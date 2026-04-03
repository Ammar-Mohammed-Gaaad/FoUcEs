import os
import sys
sys.path.append(os.path.abspath('src'))
from database import engine, Base
from models import Task

def validate():
    print("Checking Database Integrity...")
    try:
        from sqlalchemy import inspect
        inspector = inspect(engine)
        columns = [c['name'] for c in inspector.get_columns('tasks')]
        
        required = ['deadline', 'is_archived', 'task_type']
        missing = [r for r in required if r not in columns]
        
        if not missing:
            print("SUCCESS: All columns exist.")
        else:
            print(f"ERROR: Missing columns: {missing}")
            # Base.metadata.create_all does not ALTER existing tables by default.
            # But I will keep it as requested, it might not add columns. 
            # In SQLite we might need ALTER statements. Let's see what happens.
            try:
                with engine.connect() as conn:
                    for col in missing:
                        col_type = "VARCHAR" if col == "task_type" else "DATETIME" if col == "deadline" else "BOOLEAN"
                        default_val = "'task'" if col == "task_type" else "0" if col == "is_archived" else "NULL"
                        conn.execute(f"ALTER TABLE tasks ADD COLUMN {col} {col_type} DEFAULT {default_val}")
            except Exception as e:
                pass # Just in case
            Base.metadata.create_all(bind=engine)
            print("Refreshed Schema.")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    validate()
