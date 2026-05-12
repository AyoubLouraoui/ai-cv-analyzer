import sqlite3
import json

conn = sqlite3.connect("users.db", check_same_thread=False)

cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE,
    email TEXT UNIQUE,
    password TEXT
)
""")

conn.commit()

cursor.execute("""
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

conn.commit()

try:
    cursor.execute("ALTER TABLE cv_uploads ADD COLUMN cv_text TEXT")
    conn.commit()
except sqlite3.OperationalError:
    pass

cursor.execute("""
CREATE TABLE IF NOT EXISTS user_activity (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT,
    action TEXT,
    details TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
""")

conn.commit()


def add_user(username, email, password):

    cursor.execute(
        "INSERT INTO users (username, email, password) VALUES (?, ?, ?)",
        (username, email, password)
    )

    conn.commit()


def get_user(username):

    cursor.execute(
        "SELECT * FROM users WHERE username=?",
        (username,)
    )

    return cursor.fetchone()


def get_user_by_email(email):

    cursor.execute(
        "SELECT * FROM users WHERE email=?",
        (email,)
    )

    return cursor.fetchone()


def get_all_users():

    cursor.execute(
        "SELECT id, username, email FROM users ORDER BY id DESC"
    )

    return cursor.fetchall()


def update_user(user_id, username, email):

    cursor.execute(
        "UPDATE users SET username=?, email=? WHERE id=?",
        (username, email, user_id)
    )

    conn.commit()


def delete_user(user_id):

    cursor.execute(
        "DELETE FROM users WHERE id=?",
        (user_id,)
    )

    conn.commit()


def add_cv_upload(username, filename, cv_text, skills, best_career, best_score):

    cursor.execute(
        """
        INSERT INTO cv_uploads (username, filename, cv_text, skills, best_career, best_score)
        VALUES (?, ?, ?, ?, ?, ?)
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

    conn.commit()


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

    cursor.execute(
        """
        INSERT INTO user_activity (username, action, details)
        VALUES (?, ?, ?)
        """,
        (username, action, details)
    )

    conn.commit()


def get_all_user_activity():

    cursor.execute(
        """
        SELECT id, username, action, details, created_at
        FROM user_activity
        ORDER BY created_at DESC
        """
    )

    return cursor.fetchall()
