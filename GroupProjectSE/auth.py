from flask_login import UserMixin
import sqlite3
import os

DB_PATH = os.path.join("GroupProjectSE", "database", "plant_history.db")

class User(UserMixin):
    def __init__(self, id, username, password, role):
        self.id = id
        self.username = username
        self.password = password
        self.role = role

def get_user_by_username(username):
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("SELECT id, username, password, role FROM users WHERE username = ?", (username,))
    row = cur.fetchone()
    conn.close()

    if row:
        return User(*row)
    return None

def get_user_by_id(id):
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("SELECT id, username, password, role FROM users WHERE id = ?", (id,))
    row = cur.fetchone()
    conn.close()

    if row:
        return User(*row)
    return None
