import sqlite3
import os

db_path = 'src/fakarni.db' if os.path.exists('src/fakarni.db') else 'fakarni.db'
conn = sqlite3.connect(db_path)

columns_to_add = [
    'ALTER TABLE tasks ADD COLUMN parent_id INTEGER REFERENCES tasks(id)',
    'ALTER TABLE tasks ADD COLUMN task_type VARCHAR DEFAULT "task"',
    'ALTER TABLE tasks ADD COLUMN is_archived BOOLEAN DEFAULT 0'
]

for col in columns_to_add:
    try:
        conn.execute(col)
        print(f"Executed: {col}")
    except Exception as e:
        print(f"Skipped: {col} -> {e}")

conn.commit()
conn.close()
