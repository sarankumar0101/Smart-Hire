import sqlite3
import os

def check_schema():
    db_path = 'instance/smarthire.db'
    
    if not os.path.exists(db_path):
        print("Database file not found!")
        return
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Check student table schema
        cursor.execute("PRAGMA table_info(student)")
        student_columns = cursor.fetchall()
        print("Student table schema:")
        for col in student_columns:
            print(f"  {col[1]} ({col[2]}) - NOT NULL: {col[3]} - DEFAULT: {col[4]}")
        
        print("\n" + "="*50 + "\n")
        
        # Check administrator table schema
        cursor.execute("PRAGMA table_info(administrator)")
        admin_columns = cursor.fetchall()
        print("Administrator table schema:")
        for col in admin_columns:
            print(f"  {col[1]} ({col[2]}) - NOT NULL: {col[3]} - DEFAULT: {col[4]}")
        
        conn.close()
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    check_schema() 