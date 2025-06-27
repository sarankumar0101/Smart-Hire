import sqlite3
import os

def delete_user():
    db_path = 'instance/smarthire.db'
    
    if not os.path.exists(db_path):
        print("Database file not found!")
        return
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Delete the specific user
        email = 'saranseethini27@gmail.com'
        
        # Delete from student table
        cursor.execute("DELETE FROM student WHERE email = ?", (email,))
        student_deleted = cursor.rowcount
        
        # Delete from administrator table
        cursor.execute("DELETE FROM administrator WHERE email = ?", (email,))
        admin_deleted = cursor.rowcount
        
        # Delete related applications
        cursor.execute("DELETE FROM application WHERE student_id IN (SELECT id FROM student WHERE email = ?)", (email,))
        
        # Delete related resume analyses
        cursor.execute("DELETE FROM resume_analysis WHERE student_id IN (SELECT id FROM student WHERE email = ?)", (email,))
        
        conn.commit()
        conn.close()
        
        if student_deleted > 0 or admin_deleted > 0:
            print(f"User {email} deleted successfully!")
            print(f"Deleted from student table: {student_deleted}")
            print(f"Deleted from administrator table: {admin_deleted}")
        else:
            print(f"User {email} not found in database!")
            
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    delete_user() 