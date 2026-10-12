import sqlite3
from datetime import timedelta
from pathlib import Path


DB_PATH = Path(__file__).with_name("studyplan.db")


def connect():
    connection = sqlite3.connect(DB_PATH)
    connection.row_factory = sqlite3.Row
    connection.execute("PRAGMA foreign_keys = ON")
    return connection


def init_db():
    connection = connect()

    try:
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


def get_subject_id(connection, subject):
    connection.execute(
        "INSERT OR IGNORE INTO subjects (name) VALUES (?)",
        (subject,)
    )

    return connection.execute(
        "SELECT id FROM subjects WHERE name = ?",
        (subject,)
    ).fetchone()["id"]


def add_task(title, subject, due):
    title = title.strip()
    subject = subject.strip()

    if not title:
        raise ValueError("Введи название задания.")

    if not subject:
        raise ValueError("Введи название предмета.")

    if due is None:
        raise ValueError("Укажи срок сдачи.")

    connection = connect()

    try:
        subject_id = get_subject_id(connection, subject)

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
    connection = connect()

    try:
        return connection.execute("""
            SELECT
                tasks.id,
                tasks.title,
                subjects.name AS subject,
                tasks.due,
                tasks.done
            FROM tasks
            JOIN subjects ON tasks.subject_id = subjects.id
            ORDER BY tasks.due, tasks.id
        """).fetchall()
    finally:
        connection.close()


def set_task_done(task_id, done):
    connection = connect()

    try:
        result = connection.execute(
            "UPDATE tasks SET done = ? WHERE id = ?",
            (int(done), task_id)
        )

        if result.rowcount == 0:
            raise ValueError("Задание не найдено.")

        connection.commit()
    finally:
        connection.close()


def add_lesson(subject, weekday, start, end, room):
    subject = subject.strip()
    room = room.strip()

    if not subject:
        raise ValueError("Введи название предмета.")

    if weekday not in range(1, 8):
        raise ValueError("Выбери день недели.")

    if start is None or end is None:
        raise ValueError(
            "Укажи время начала и окончания занятия."
        )

    start_text = start.strftime("%H:%M")
    end_text = end.strftime("%H:%M")

    if end_text <= start_text:
        raise ValueError(
            "Время окончания должно быть позже времени начала."
        )

    connection = connect()

    try:
        subject_id = get_subject_id(connection, subject)

        connection.execute(
            """
            INSERT INTO lessons (
                subject_id,
                weekday,
                start,
                end,
                room
            )
            VALUES (?, ?, ?, ?, ?)
            """,
            (
                subject_id,
                weekday,
                start_text,
                end_text,
                room
            )
        )

        connection.commit()
    finally:
        connection.close()


def get_lessons():
    connection = connect()

    try:
        return connection.execute("""
            SELECT
                lessons.id,
                subjects.name AS subject,
                lessons.weekday,
                lessons.start,
                lessons.end,
                lessons.room
            FROM lessons
            JOIN subjects ON lessons.subject_id = subjects.id
            ORDER BY lessons.weekday, lessons.start, lessons.id
        """).fetchall()
    finally:
        connection.close()


def get_upcoming_tasks(today):
    last_day = today + timedelta(days=6)

    return [
        task
        for task in get_tasks()
        if not task["done"]
        and today.isoformat() <= task["due"] <= last_day.isoformat()
    ]


def get_overdue_tasks(today):
    return [
        task
        for task in get_tasks()
        if not task["done"]
        and task["due"] < today.isoformat()
    ]