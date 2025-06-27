import sqlite3
import os
from werkzeug.security import generate_password_hash

def create_test_user():
    db_path = 'instance/smarthire.db'
    
    if not os.path.exists(db_path):
        print("Database file not found!")
        return
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Create a test student
        test_email = 'test@example.com'
        test_password = 'password123'
        password_hash = generate_password_hash(test_password)
        
        # Check if user already exists
        cursor.execute("SELECT id FROM student WHERE email = ?", (test_email,))
        if cursor.fetchone():
            print("Test user already exists!")
            conn.close()
            return
        
        cursor.execute("""
            INSERT INTO student (first_name, last_name, email, password_hash, college, course, graduation_year, current_year, is_verified)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, ('Test', 'User', test_email, password_hash, 'Test College', 'Computer Science', '2025', '3rd Year', True))
        
        conn.commit()
        conn.close()
        
        print("Test user created successfully!")
        print(f"Email: {test_email}")
        print(f"Password: {test_password}")
        print("\nYou can now test login with:")
        print("1. Valid credentials: test@example.com / password123")
        print("2. Invalid credentials: test@example.com / wrongpassword")
        print("3. Non-existent user: nonexistent@example.com / anypassword")
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    create_test_user() 