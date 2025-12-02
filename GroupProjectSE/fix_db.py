import sqlite3
import os

DB_PATH = os.path.join("GroupProjectSE", "database", "plant_history.db")

conn = sqlite3.connect(DB_PATH)
cur = conn.cursor()

try:
    cur.execute("ALTER TABLE history ADD COLUMN user_id INTEGER;")
    print("Column user_id added successfully.")
except Exception as e:
    print("Error:", e)

conn.commit()
conn.close()
