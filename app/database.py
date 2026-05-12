import sqlite3

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