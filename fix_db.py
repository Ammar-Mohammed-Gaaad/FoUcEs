import sqlite3
import os

db_path = 'src/fakarni.db'
if os.path.exists(db_path):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("UPDATE learning_profiles SET goals = '' WHERE goals IS NULL")
    conn.commit()
    print(f"✅ Database cleaned: {cursor.rowcount} rows updated.")
    conn.close()
else:
    print("❌ DB file not found.")
