import sqlite3
import os

DB_PATH = os.path.join("GroupProjectSE", "database", "plant_history.db")

def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def initialize_db():
    conn = get_db()
    cur = conn.cursor()

    # USERS TABLE (accounts)
    cur.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            role TEXT NOT NULL
        )
    ''')

    # HISTORY TABLE (with user_id)
    cur.execute('''
        CREATE TABLE IF NOT EXISTS history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            image_path TEXT NOT NULL,
            predicted_class TEXT NOT NULL,
            confidence REAL NOT NULL,
            description TEXT,
            timestamp TEXT NOT NULL,
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
    ''')

    conn.commit()
    conn.close()

# Initialize database when module imports
initialize_db()
