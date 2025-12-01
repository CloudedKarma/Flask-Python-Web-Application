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

    cur.execute('''
        CREATE TABLE IF NOT EXISTS history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            image_path TEXT NOT NULL,
            predicted_class TEXT NOT NULL,
            confidence REAL NOT NULL,
            description TEXT,
            timestamp TEXT NOT NULL
        )
    ''')

    conn.commit()
    conn.close()

# Run on import (ensures DB exists)
initialize_db()
