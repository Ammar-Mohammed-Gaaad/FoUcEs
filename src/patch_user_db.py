import sqlite3

def patch():
    # تأكد من مسار ملف الداتا بيز بتاعك
    db_path = "fakarni.db" # أو المسار اللي شغال عليه
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        print("Adding missing columns to User table...")
        
        try:
            cursor.execute("ALTER TABLE users ADD COLUMN job_title TEXT")
            print("Column 'job_title' added.")
        except sqlite3.OperationalError:
            print("Column 'job_title' already exists.")

        try:
            cursor.execute("ALTER TABLE users ADD COLUMN bio TEXT")
            print("Column 'bio' added.")
        except sqlite3.OperationalError:
            print("Column 'bio' already exists.")
            
        conn.commit()
        conn.close()
        print("Database patched successfully!")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    patch()
