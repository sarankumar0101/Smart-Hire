import sqlite3
import os

def check_database():
    db_path = 'instance/smarthire.db'
    
    if not os.path.exists(db_path):
        print("Database file not found!")
        return
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Check tables
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = cursor.fetchall()
        print("Tables in database:", [table[0] for table in tables])
        
        # Check student data
        cursor.execute("SELECT COUNT(*) FROM student")
        student_count = cursor.fetchone()[0]
        print(f"Total students: {student_count}")
        
        # Show sample student emails
        cursor.execute("SELECT email, first_name, last_name FROM student LIMIT 10")
        students = cursor.fetchall()
        print("\nSample students:")
        for student in students:
            print(f"  {student[1]} {student[2]} - {student[0]}")
        
        # Check administrator data
        cursor.execute("SELECT COUNT(*) FROM administrator")
        admin_count = cursor.fetchone()[0]
        print(f"\nTotal administrators: {admin_count}")
        
        # Show sample admin emails
        cursor.execute("SELECT email, full_name FROM administrator LIMIT 5")
        admins = cursor.fetchall()
        print("\nSample administrators:")
        for admin in admins:
            print(f"  {admin[1]} - {admin[0]}")
        
        conn.close()
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    check_database() 