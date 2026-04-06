import sqlite3
import os

# -*- coding: utf-8 -*-
DB_PATH = os.path.join(os.path.dirname(__file__), "fakarni.db")

conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()

cursor.execute("PRAGMA table_info(tasks)")
existing = [row[1] for row in cursor.fetchall()]
print("Existing columns:", existing)

migrations = [
    ("parent_id",   "ALTER TABLE tasks ADD COLUMN parent_id INTEGER"),
    ("task_type",   "ALTER TABLE tasks ADD COLUMN task_type TEXT DEFAULT 'task'"),
    ("is_archived", "ALTER TABLE tasks ADD COLUMN is_archived INTEGER DEFAULT 0"),
]

for col_name, sql in migrations:
    if col_name not in existing:
        try:
            cursor.execute(sql)
            print("Added column:", col_name)
        except Exception as e:
            print("Could not add", col_name, ":", e)
    else:
        print("Column already exists:", col_name)

conn.commit()
conn.close()
print("Migration done! Database is safe and updated.")
