"""
Kalki Know — authentication helpers.
Users stored in kalki.db (users table). Session kept in session.json.
"""

import os
import json
import sqlite3
import hashlib

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "kalki.db")
SESSION_FILE = os.path.join(BASE_DIR, "session.json")
USERS_TABLE = "users"

ROLES = [
    "Student",
    "Ayurveda Practitioner",
    "Community Contributor",
    "Researcher",
    "Forest Officer",
    "General Public",
]


def init_users_table():
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute(f"""
        CREATE TABLE IF NOT EXISTS {USERS_TABLE} (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            role TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    conn.commit()
    conn.close()


def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode("utf-8")).hexdigest()


def create_user(username, email, password, role):
    username = username.strip()
    email = email.strip().lower()
    if not username or not email or not password:
        return False, "All fields are required."
    if len(password) < 8:
        return False, "Password must be at least 8 characters."

    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    try:
        cur.execute(f"""
            INSERT INTO {USERS_TABLE} (username, email, password_hash, role)
            VALUES (?, ?, ?, ?)
        """, (username, email, hash_password(password), role))
        conn.commit()
    except sqlite3.IntegrityError as e:
        conn.close()
        if "username" in str(e):
            return False, "That username is already taken."
        if "email" in str(e):
            return False, "That email is already registered."
        return False, "Could not create account."
    conn.close()
    return True, "Account created."


def verify_login(username, password):
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    cur.execute(f"""
        SELECT * FROM {USERS_TABLE}
        WHERE username = ? AND password_hash = ?
        LIMIT 1
    """, (username.strip(), hash_password(password)))
    row = cur.fetchone()
    conn.close()
    return dict(row) if row else None


def update_user(user_id, email=None, role=None, password=None):
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    if email is not None:
        cur.execute(f"UPDATE {USERS_TABLE} SET email = ? WHERE id = ?", (email.strip().lower(), user_id))
    if role is not None:
        cur.execute(f"UPDATE {USERS_TABLE} SET role = ? WHERE id = ?", (role, user_id))
    if password:
        cur.execute(f"UPDATE {USERS_TABLE} SET password_hash = ? WHERE id = ?", (hash_password(password), user_id))
    conn.commit()
    conn.close()


def save_session(user):
    with open(SESSION_FILE, "w", encoding="utf-8") as f:
        json.dump({
            "id": user["id"],
            "username": user["username"],
            "email": user["email"],
            "role": user["role"],
        }, f)


def load_session():
    if not os.path.exists(SESSION_FILE):
        return None
    try:
        with open(SESSION_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return None


def clear_session():
    if os.path.exists(SESSION_FILE):
        try:
            os.remove(SESSION_FILE)
        except Exception:
            pass


init_users_table()