import sqlite3
from pathlib import Path

# База хранится рядом с файлами проекта
DB_PATH = Path(__file__).with_name("studyplan.db")


def init_db():
    """Создает базу и таблицы, если их еще нет."""
    connection = sqlite3.connect(DB_PATH)

    try:
        connection.execute("PRAGMA foreign_keys = ON")

        connection.executescript("""
            CREATE TABLE IF NOT EXISTS subjects (
                id INTEGER PRIMARY KEY,
                name TEXT NOT NULL UNIQUE
                    CHECK(length(trim(name)) > 0)
            );

            CREATE TABLE IF NOT EXISTS tasks (
                id INTEGER PRIMARY KEY,
                title TEXT NOT NULL
                    CHECK(length(trim(title)) > 0),
                subject_id INTEGER NOT NULL
                    REFERENCES subjects(id),
                due TEXT NOT NULL,
                priority INTEGER NOT NULL DEFAULT 2
                    CHECK(priority BETWEEN 1 AND 3),
                description TEXT NOT NULL DEFAULT '',
                done INTEGER NOT NULL DEFAULT 0
                    CHECK(done IN (0, 1))
            );

            CREATE TABLE IF NOT EXISTS lessons (
                id INTEGER PRIMARY KEY,
                subject_id INTEGER NOT NULL
                    REFERENCES subjects(id),
                weekday INTEGER NOT NULL
                    CHECK(weekday BETWEEN 1 AND 7),
                start TEXT NOT NULL,
                end TEXT NOT NULL
                    CHECK(end > start),
                room TEXT NOT NULL DEFAULT ''
            );
        """)

        connection.commit()
    finally:
        connection.close()


def add_task(title, subject, due):
    """Проверяет данные и сохраняет задание."""
    title = title.strip()
    subject = subject.strip()

    if not title:
        raise ValueError("Введи название задания.")

    if not subject:
        raise ValueError("Введи название предмета.")

    if due is None:
        raise ValueError("Укажи срок сдачи.")

    connection = sqlite3.connect(DB_PATH)

    try:
        connection.execute("PRAGMA foreign_keys = ON")

        # Добавляем предмет, если его еще нет
        connection.execute(
            "INSERT OR IGNORE INTO subjects (name) VALUES (?)",
            (subject,)
        )

        # Получаем номер предмета
        subject_id = connection.execute(
            "SELECT id FROM subjects WHERE name = ?",
            (subject,)
        ).fetchone()[0]

        # Сохраняем задание
        connection.execute(
            """
            INSERT INTO tasks (title, subject_id, due)
            VALUES (?, ?, ?)
            """,
            (title, subject_id, due.isoformat())
        )

        connection.commit()
    finally:
        connection.close()


def get_tasks():
    """Возвращает задания по порядку сроков сдачи."""
    connection = sqlite3.connect(DB_PATH)

    try:
        return connection.execute(
            """
            SELECT tasks.title, subjects.name, tasks.due
            FROM tasks
            JOIN subjects ON tasks.subject_id = subjects.id
            ORDER BY tasks.due, tasks.id
            """
        ).fetchall()
    finally:
        connection.close()