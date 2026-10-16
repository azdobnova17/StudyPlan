import os
import re
import time as clock
from datetime import date, time, timedelta
from functools import lru_cache
from pathlib import Path

from argon2 import PasswordHasher
from argon2.exceptions import InvalidHashError, VerificationError

from sqlalchemy import (
    BigInteger,
    CheckConstraint,
    Column,
    ForeignKey,
    Index,
    Integer,
    MetaData,
    String,
    Table,
    case,
    create_engine,
    delete,
    event,
    insert,
    select,
    update
)

from sqlalchemy.engine import make_url
from sqlalchemy.exc import IntegrityError, SQLAlchemyError


DB_PATH = Path(__file__).with_name("studyplan.db")

DatabaseError = SQLAlchemyError

_database_url = None
_metadata = MetaData()

_hasher = PasswordHasher(
    time_cost=2,
    memory_cost=19456,
    parallelism=1
)

_dummy_hash = _hasher.hash(os.urandom(32).hex())

_login_error = (
    "Неверный логин или пароль. "
    "После 5 ошибок вход блокируется на 15 минут."
)

_users = Table(
    "studyplan_users",
    _metadata,
    Column("id", Integer, primary_key=True),
    Column(
        "username",
        String(32),
        nullable=False,
        unique=True
    ),
    Column("name", String(100), nullable=False),
    Column("password_hash", String(255), nullable=False),
    Column(
        "failed_attempts",
        Integer,
        nullable=False,
        default=0
    ),
    Column(
        "blocked_until",
        BigInteger,
        nullable=False,
        default=0
    )
)

_tasks = Table(
    "studyplan_personal_tasks",
    _metadata,
    Column("id", Integer, primary_key=True),
    Column(
        "user_id",
        Integer,
        ForeignKey("studyplan_users.id"),
        nullable=False
    ),
    Column("title", String(200), nullable=False),
    Column("subject", String(100), nullable=False),
    Column("due", String(10), nullable=False),
    Column("done", Integer, nullable=False, default=0),
    CheckConstraint("done IN (0, 1)"),
    CheckConstraint("length(trim(title)) > 0"),
    CheckConstraint("length(trim(subject)) > 0")
)

_lessons = Table(
    "studyplan_personal_lessons",
    _metadata,
    Column("id", Integer, primary_key=True),
    Column(
        "user_id",
        Integer,
        ForeignKey("studyplan_users.id"),
        nullable=False
    ),
    Column("subject", String(100), nullable=False),
    Column("weekday", Integer, nullable=False),
    Column("start", String(5), nullable=False),
    Column("end", String(5), nullable=False),
    Column("room", String(80), nullable=False, default=""),
    CheckConstraint("weekday BETWEEN 1 AND 7"),
    CheckConstraint('"end" > start'),
    CheckConstraint("length(trim(subject)) > 0")
)

Index(
    "studyplan_tasks_owner_due",
    _tasks.c.user_id,
    _tasks.c.due
)

Index(
    "studyplan_lessons_owner_day",
    _lessons.c.user_id,
    _lessons.c.weekday
)


def _normalize_url(value):
    if not value:
        return f"sqlite:///{DB_PATH}"

    parsed = make_url(value.strip())

    if parsed.drivername in ("postgres", "postgresql"):
        parsed = parsed.set(
            drivername="postgresql+psycopg"
        )

    if parsed.drivername not in (
        "sqlite",
        "sqlite+pysqlite",
        "postgresql+psycopg"
    ):
        raise ValueError(
            "Для проекта поддерживаются SQLite и PostgreSQL."
        )

    return parsed.render_as_string(hide_password=False)


@lru_cache(maxsize=4)
def _engine_for(url):
    options = {"pool_pre_ping": True}

    if make_url(url).get_backend_name() == "sqlite":
        options["connect_args"] = {
            "check_same_thread": False,
            "timeout": 20
        }
    else:
        options["connect_args"] = {
            "connect_timeout": 10
        }

    engine = create_engine(url, **options)

    if engine.dialect.name == "sqlite":
        @event.listens_for(engine, "connect")
        def enable_foreign_keys(connection, record):
            cursor = connection.cursor()
            cursor.execute("PRAGMA foreign_keys = ON")
            cursor.execute("PRAGMA busy_timeout = 20000")
            cursor.close()

    return engine


def _engine():
    url = _database_url or _normalize_url(
        os.environ.get("DATABASE_URL")
    )

    return _engine_for(url)


@lru_cache(maxsize=4)
def _initialize(url):
    _metadata.create_all(_engine_for(url))


def init_db(database_url=None):
    global _database_url

    _database_url = _normalize_url(
        database_url or os.environ.get("DATABASE_URL")
    )

    _initialize(_database_url)


def storage_is_local():
    return _engine().dialect.name == "sqlite"


def _text(value, label, maximum):
    value = value.strip() if isinstance(value, str) else ""

    if not value:
        raise ValueError(f"Заполни поле «{label}».")

    if len(value) > maximum:
        raise ValueError(
            f"Поле «{label}» должно содержать "
            f"не больше {maximum} символов."
        )

    return value


def _username(value):
    value = (
        value.strip().lower()
        if isinstance(value, str)
        else ""
    )

    if not re.fullmatch(r"[a-z0-9_]{3,32}", value):
        raise ValueError(
            "Логин: от 3 до 32 латинских букв, "
            "цифр или знаков _."
        )

    return value


def _owner_id(value):
    if type(value) is not int or value <= 0:
        raise ValueError("Сначала войди в свой аккаунт.")

    return value


def _public_user(row):
    return {
        "id": row["id"],
        "username": row["username"],
        "name": row["name"]
    }


def create_user(username, password, name):
    username = _username(username)
    name = _text(name, "Имя", 100)

    if (
        not isinstance(password, str)
        or not 12 <= len(password) <= 128
    ):
        raise ValueError(
            "Пароль должен содержать от 12 до 128 символов."
        )

    if not password.strip():
        raise ValueError(
            "Пароль не может состоять только из пробелов."
        )

    password_hash = _hasher.hash(password)

    try:
        with _engine().begin() as connection:
            result = connection.execute(
                insert(_users).values(
                    username=username,
                    name=name,
                    password_hash=password_hash,
                    failed_attempts=0,
                    blocked_until=0
                )
            )

            user_id = result.inserted_primary_key[0]
    except IntegrityError:
        raise ValueError(
            "Этот логин уже занят. Выбери другой."
        ) from None

    return {
        "id": user_id,
        "username": username,
        "name": name
    }


def authenticate(username, password):
    try:
        username = _username(username)
    except ValueError:
        raise ValueError(_login_error) from None

    if (
        not isinstance(password, str)
        or not 1 <= len(password) <= 128
    ):
        raise ValueError(_login_error)

    now = int(clock.time())
    authenticated = None

    with _engine().begin() as connection:
        row = connection.execute(
            select(_users)
            .where(_users.c.username == username)
            .with_for_update()
        ).mappings().first()

        encoded = (
            row["password_hash"]
            if row
            else _dummy_hash
        )

        try:
            valid = _hasher.verify(encoded, password)
        except (VerificationError, InvalidHashError):
            valid = False

        if row and row["blocked_until"] <= now:
            if valid:
                values = {
                    "failed_attempts": 0,
                    "blocked_until": 0
                }

                if _hasher.check_needs_rehash(encoded):
                    values["password_hash"] = _hasher.hash(
                        password
                    )

                connection.execute(
                    update(_users)
                    .where(_users.c.id == row["id"])
                    .values(**values)
                )

                authenticated = _public_user(row)
            else:
                failures = case(
                    (_users.c.blocked_until > 0, 1),
                    else_=_users.c.failed_attempts + 1
                )

                connection.execute(
                    update(_users)
                    .where(_users.c.id == row["id"])
                    .values(
                        failed_attempts=failures,
                        blocked_until=case(
                            (failures >= 5, now + 900),
                            else_=0
                        )
                    )
                )

    if authenticated is None:
        raise ValueError(_login_error)

    return authenticated


def get_user(user_id):
    user_id = _owner_id(user_id)

    with _engine().connect() as connection:
        row = connection.execute(
            select(
                _users.c.id,
                _users.c.username,
                _users.c.name
            ).where(_users.c.id == user_id)
        ).mappings().first()

    return dict(row) if row else None


def validate_task(title, subject, due):
    title = _text(title, "Название задания", 200)
    subject = _text(subject, "Предмет", 100)

    if type(due) is not date:
        raise ValueError("Укажи срок сдачи.")

    return {
        "title": title,
        "subject": subject,
        "due": due.isoformat()
    }


def add_task(user_id, title, subject, due):
    user_id = _owner_id(user_id)
    values = validate_task(title, subject, due)

    with _engine().begin() as connection:
        result = connection.execute(
            insert(_tasks).values(
                user_id=user_id,
                done=0,
                **values
            )
        )

        return result.inserted_primary_key[0]


def update_task(user_id, task_id, title, subject, due):
    user_id = _owner_id(user_id)
    values = validate_task(title, subject, due)

    with _engine().begin() as connection:
        result = connection.execute(
            update(_tasks)
            .where(
                _tasks.c.id == task_id,
                _tasks.c.user_id == user_id
            )
            .values(**values)
        )

        if result.rowcount != 1:
            raise ValueError(
                "Задание не найдено в твоем аккаунте."
            )


def delete_task(user_id, task_id):
    user_id = _owner_id(user_id)

    with _engine().begin() as connection:
        result = connection.execute(
            delete(_tasks).where(
                _tasks.c.id == task_id,
                _tasks.c.user_id == user_id
            )
        )

        if result.rowcount != 1:
            raise ValueError(
                "Задание не найдено в твоем аккаунте."
            )


def get_tasks(user_id):
    user_id = _owner_id(user_id)

    with _engine().connect() as connection:
        rows = connection.execute(
            select(_tasks)
            .where(_tasks.c.user_id == user_id)
            .order_by(_tasks.c.due, _tasks.c.id)
        ).mappings().all()

    return [dict(row) for row in rows]


def set_task_done(user_id, task_id, done):
    user_id = _owner_id(user_id)

    if type(done) is not bool:
        raise ValueError("Выбери статус задания.")

    with _engine().begin() as connection:
        result = connection.execute(
            update(_tasks)
            .where(
                _tasks.c.id == task_id,
                _tasks.c.user_id == user_id
            )
            .values(done=int(done))
        )

        if result.rowcount != 1:
            raise ValueError(
                "Задание не найдено в твоем аккаунте."
            )


def validate_lesson(subject, weekday, start, end, room):
    subject = _text(subject, "Предмет", 100)
    room = room.strip() if isinstance(room, str) else ""

    if len(room) > 80:
        raise ValueError(
            "Аудитория: не больше 80 символов."
        )

    if type(weekday) is not int or weekday not in range(1, 8):
        raise ValueError("Выбери день недели.")

    if not isinstance(start, time) or not isinstance(end, time):
        raise ValueError(
            "Укажи время начала и окончания занятия."
        )

    start_text = start.strftime("%H:%M")
    end_text = end.strftime("%H:%M")

    if end_text <= start_text:
        raise ValueError(
            "Время окончания должно быть позже времени начала."
        )

    return {
        "subject": subject,
        "weekday": weekday,
        "start": start_text,
        "end": end_text,
        "room": room
    }


def add_lesson(user_id, subject, weekday, start, end, room):
    user_id = _owner_id(user_id)

    values = validate_lesson(
        subject,
        weekday,
        start,
        end,
        room
    )

    with _engine().begin() as connection:
        result = connection.execute(
            insert(_lessons).values(
                user_id=user_id,
                **values
            )
        )

        return result.inserted_primary_key[0]


def update_lesson(
    user_id,
    lesson_id,
    subject,
    weekday,
    start,
    end,
    room
):
    user_id = _owner_id(user_id)

    values = validate_lesson(
        subject,
        weekday,
        start,
        end,
        room
    )

    with _engine().begin() as connection:
        result = connection.execute(
            update(_lessons)
            .where(
                _lessons.c.id == lesson_id,
                _lessons.c.user_id == user_id
            )
            .values(**values)
        )

        if result.rowcount != 1:
            raise ValueError(
                "Занятие не найдено в твоем аккаунте."
            )


def delete_lesson(user_id, lesson_id):
    user_id = _owner_id(user_id)

    with _engine().begin() as connection:
        result = connection.execute(
            delete(_lessons).where(
                _lessons.c.id == lesson_id,
                _lessons.c.user_id == user_id
            )
        )

        if result.rowcount != 1:
            raise ValueError(
                "Занятие не найдено в твоем аккаунте."
            )


def get_lessons(user_id):
    user_id = _owner_id(user_id)

    with _engine().connect() as connection:
        rows = connection.execute(
            select(_lessons)
            .where(_lessons.c.user_id == user_id)
            .order_by(
                _lessons.c.weekday,
                _lessons.c.start,
                _lessons.c.id
            )
        ).mappings().all()

    return [dict(row) for row in rows]


def get_upcoming_tasks(user_id, today):
    last_day = today + timedelta(days=6)

    return [
        task
        for task in get_tasks(user_id)
        if not task["done"]
        and today.isoformat() <= task["due"] <= last_day.isoformat()
    ]


def get_overdue_tasks(user_id, today):
    return [
        task
        for task in get_tasks(user_id)
        if not task["done"]
        and task["due"] < today.isoformat()
    ]