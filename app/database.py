import json
import os
import sqlite3


def get_secret(name, default=None):
    try:
        import streamlit as st

        return st.secrets.get(name, os.getenv(name, default))
    except Exception:
        return os.getenv(name, default)


DATABASE_URL = get_secret("DATABASE_URL")
IS_POSTGRES = bool(DATABASE_URL)

if IS_POSTGRES:
    import psycopg2
    from psycopg2.extras import Json

    conn = psycopg2.connect(DATABASE_URL, sslmode="require")
    conn.autocommit = True
else:
    conn = sqlite3.connect("users.db", check_same_thread=False)

cursor = conn.cursor()


def placeholder(index=1):
    return "%s" if IS_POSTGRES else "?"


def execute(query, params=()):
    cursor.execute(query, params)

    if not IS_POSTGRES:
        conn.commit()


def init_db():
    if IS_POSTGRES:
        execute("""
        CREATE TABLE IF NOT EXISTS users (
            id SERIAL PRIMARY KEY,
            username TEXT UNIQUE,
            email TEXT UNIQUE,
            password TEXT
        )
        """)

        execute("""
        CREATE TABLE IF NOT EXISTS cv_uploads (
            id SERIAL PRIMARY KEY,
            username TEXT,
            filename TEXT,
            cv_text TEXT,
            skills TEXT,
            best_career TEXT,
            best_score REAL,
            uploaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """)

        execute("""
        CREATE TABLE IF NOT EXISTS user_activity (
            id SERIAL PRIMARY KEY,
            username TEXT,
            action TEXT,
            details TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """)
    else:
        execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE,
            email TEXT UNIQUE,
            password TEXT
        )
        """)

        execute("""
        CREATE TABLE IF NOT EXISTS cv_uploads (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT,
            filename TEXT,
            cv_text TEXT,
            skills TEXT,
            best_career TEXT,
            best_score REAL,
            uploaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """)

        try:
            execute("ALTER TABLE cv_uploads ADD COLUMN cv_text TEXT")
        except sqlite3.OperationalError:
            pass

        execute("""
        CREATE TABLE IF NOT EXISTS user_activity (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT,
            action TEXT,
            details TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """)


init_db()


def add_user(username, email, password):
    p = placeholder()

    execute(
        f"INSERT INTO users (username, email, password) VALUES ({p}, {p}, {p})",
        (username, email, password)
    )


def get_user(username):
    p = placeholder()

    cursor.execute(
        f"SELECT * FROM users WHERE username={p}",
        (username,)
    )

    return cursor.fetchone()


def get_user_by_email(email):
    p = placeholder()

    cursor.execute(
        f"SELECT * FROM users WHERE email={p}",
        (email,)
    )

    return cursor.fetchone()


def get_all_users():
    cursor.execute(
        "SELECT id, username, email FROM users ORDER BY id DESC"
    )

    return cursor.fetchall()


def update_user(user_id, username, email):
    p = placeholder()

    execute(
        f"UPDATE users SET username={p}, email={p} WHERE id={p}",
        (username, email, user_id)
    )


def delete_user(user_id):
    p = placeholder()

    execute(
        f"DELETE FROM users WHERE id={p}",
        (user_id,)
    )


def add_cv_upload(username, filename, cv_text, skills, best_career, best_score):
    p = placeholder()

    execute(
        f"""
        INSERT INTO cv_uploads (username, filename, cv_text, skills, best_career, best_score)
        VALUES ({p}, {p}, {p}, {p}, {p}, {p})
        """,
        (
            username,
            filename,
            cv_text,
            json.dumps(skills),
            best_career,
            best_score
        )
    )


def get_all_cv_uploads():
    cursor.execute(
        """
        SELECT id, username, filename, cv_text, skills, best_career, best_score, uploaded_at
        FROM cv_uploads
        ORDER BY uploaded_at DESC
        """
    )

    return cursor.fetchall()


def add_user_activity(username, action, details=""):
    p = placeholder()

    execute(
        f"""
        INSERT INTO user_activity (username, action, details)
        VALUES ({p}, {p}, {p})
        """,
        (username, action, details)
    )


def get_all_user_activity():
    cursor.execute(
        """
        SELECT id, username, action, details, created_at
        FROM user_activity
        ORDER BY created_at DESC
        """
    )

    return cursor.fetchall()
