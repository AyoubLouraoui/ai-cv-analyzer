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
    skills TEXT,
    best_career TEXT,
    best_score REAL,
    uploaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
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


def add_cv_upload(username, filename, skills, best_career, best_score):

    cursor.execute(
        """
        INSERT INTO cv_uploads (username, filename, skills, best_career, best_score)
        VALUES (?, ?, ?, ?, ?)
        """,
        (
            username,
            filename,
            json.dumps(skills),
            best_career,
            best_score
        )
    )

    conn.commit()


def get_all_cv_uploads():

    cursor.execute(
        """
        SELECT id, username, filename, skills, best_career, best_score, uploaded_at
        FROM cv_uploads
        ORDER BY uploaded_at DESC
        """
    )

    return cursor.fetchall()
