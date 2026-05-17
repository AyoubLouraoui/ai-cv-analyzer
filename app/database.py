import json
import os
import sqlite3
import threading


def get_secret(name, default=None):
    try:
        import streamlit as st

        return st.secrets.get(name, os.getenv(name, default))
    except Exception:
        return os.getenv(name, default)


DATABASE_URL = get_secret("DATABASE_URL")
IS_POSTGRES = bool(DATABASE_URL)
_DB_LOCK = threading.Lock()

if IS_POSTGRES:
    import psycopg2

    conn = psycopg2.connect(DATABASE_URL, sslmode="require")
    conn.autocommit = True
else:
    conn = sqlite3.connect("users.db", check_same_thread=False)

def placeholder(index=1):
    return "%s" if IS_POSTGRES else "?"


def execute(query, params=(), fetch=None):
    with _DB_LOCK:
        cursor = conn.cursor()

        try:
            cursor.execute(query, params)

            if fetch == "one":
                return cursor.fetchone()

            if fetch == "all":
                return cursor.fetchall()

            if not IS_POSTGRES:
                conn.commit()

            return None
        finally:
            cursor.close()


def ignore_duplicate_column_error(error):
    if IS_POSTGRES:
        return getattr(error, "pgcode", None) == "42701"

    return isinstance(error, sqlite3.OperationalError) and "duplicate column" in str(error).lower()


def add_column_if_missing(table, column, definition):
    try:
        execute(f"ALTER TABLE {table} ADD COLUMN {column} {definition}")
    except Exception as error:
        if not ignore_duplicate_column_error(error):
            raise


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

        add_column_if_missing("users", "email", "TEXT UNIQUE")
        add_column_if_missing("users", "password", "TEXT")
        add_column_if_missing("users", "social_provider", "TEXT")
        add_column_if_missing("users", "social_sub", "TEXT")
        add_column_if_missing("users", "profile_image", "TEXT")
        add_column_if_missing("users", "password_created", "INTEGER")
        add_column_if_missing("users", "password_created_at", "TIMESTAMP")
        add_column_if_missing("users", "is_admin", "INTEGER DEFAULT 0")

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

        add_column_if_missing("cv_uploads", "cv_text", "TEXT")

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

        add_column_if_missing("users", "email", "TEXT")
        add_column_if_missing("users", "password", "TEXT")
        add_column_if_missing("users", "social_provider", "TEXT")
        add_column_if_missing("users", "social_sub", "TEXT")
        add_column_if_missing("users", "profile_image", "TEXT")
        add_column_if_missing("users", "password_created", "INTEGER")
        add_column_if_missing("users", "password_created_at", "TEXT")
        add_column_if_missing("users", "is_admin", "INTEGER DEFAULT 0")

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

        add_column_if_missing("cv_uploads", "cv_text", "TEXT")

        execute("""
        CREATE TABLE IF NOT EXISTS user_activity (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT,
            action TEXT,
            details TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """)


def backfill_password_created():
    execute(
        """
        UPDATE users
        SET password_created = 1
        WHERE password_created IS NULL
          AND password IS NOT NULL
          AND (social_provider IS NULL OR social_provider = '')
        """
    )
    execute(
        """
        UPDATE users
        SET password_created = 0
        WHERE password_created IS NULL
        """
    )


init_db()
backfill_password_created()


def add_user(username, email, password):
    p = placeholder()
    password_created = 1 if password else 0
    password_created_at = "CURRENT_TIMESTAMP" if password else "NULL"

    execute(
        f"INSERT INTO users (username, email, password, password_created, password_created_at) VALUES ({p}, {p}, {p}, {p}, {password_created_at})",
        (username, email, password, password_created)
    )


def get_user(username):
    p = placeholder()

    return execute(
        f"SELECT id, username, email, password, social_provider, social_sub, profile_image, password_created, password_created_at, is_admin FROM users WHERE username={p}",
        (username,),
        fetch="one"
    )


def get_user_by_email(email):
    p = placeholder()

    return execute(
        f"SELECT id, username, email, password, social_provider, social_sub, profile_image, password_created, password_created_at, is_admin FROM users WHERE email={p}",
        (email,),
        fetch="one"
    )


def get_user_by_social_identity(provider, social_sub):
    p = placeholder()

    return execute(
        f"""
        SELECT id, username, email, password, social_provider, social_sub, profile_image, password_created, password_created_at, is_admin
        FROM users
        WHERE social_provider={p} AND social_sub={p}
        """,
        (provider, social_sub),
        fetch="one"
    )


def update_user_social_identity(username, provider, social_sub):
    p = placeholder()

    execute(
        f"UPDATE users SET social_provider={p}, social_sub={p} WHERE username={p}",
        (provider, social_sub, username)
    )


def update_user_account_credentials(username, email, password=None):
    p = placeholder()

    if password is None:
        execute(
            f"UPDATE users SET email={p} WHERE username={p}",
            (email, username)
        )
    else:
        execute(
            f"UPDATE users SET email={p}, password={p}, password_created=1, password_created_at=CURRENT_TIMESTAMP WHERE username={p}",
            (email, password, username)
        )


def update_user_profile_image(username, profile_image):
    p = placeholder()

    execute(
        f"UPDATE users SET profile_image={p} WHERE username={p}",
        (profile_image, username)
    )


def get_all_users():
    return execute(
        """
        SELECT id, username, email, password, social_provider, social_sub, profile_image, password_created, password_created_at, is_admin
        FROM users
        ORDER BY id DESC
        """,
        fetch="all"
    )


def set_user_admin(user_id, is_admin):
    p = placeholder()

    execute(
        f"UPDATE users SET is_admin={p} WHERE id={p}",
        (1 if is_admin else 0, user_id)
    )


def update_user(user_id, username, email):
    p = placeholder()

    execute(
        f"UPDATE users SET username={p}, email={p} WHERE id={p}",
        (username, email, user_id)
    )


def update_user_password(user_id, password):
    p = placeholder()

    execute(
        f"UPDATE users SET password={p}, password_created=1, password_created_at=CURRENT_TIMESTAMP WHERE id={p}",
        (password, user_id)
    )


def clear_user_social_identity(user_id):
    p = placeholder()

    execute(
        f"UPDATE users SET social_provider=NULL, social_sub=NULL WHERE id={p}",
        (user_id,)
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
    return execute(
        """
        SELECT id, username, filename, cv_text, skills, best_career, best_score, uploaded_at
        FROM cv_uploads
        ORDER BY uploaded_at DESC
        """,
        fetch="all"
    )


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
    return execute(
        """
        SELECT id, username, action, details, created_at
        FROM user_activity
        ORDER BY created_at DESC, id DESC
        """,
        fetch="all"
    )


def get_database_backend():
    return "PostgreSQL" if IS_POSTGRES else "SQLite"


def is_persistent_database():
    return IS_POSTGRES
