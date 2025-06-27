import sqlite3
import os
from werkzeug.security import generate_password_hash

def manage_database():
    db_path = 'instance/smarthire.db'
    
    if not os.path.exists(db_path):
        print("Database file not found!")
        return
    
    while True:
        print("\n=== SmartHire Database Manager ===")
        print("1. View all students")
        print("2. View all administrators")
        print("3. Delete a student")
        print("4. Delete an administrator")
        print("5. Add a test student")
        print("6. Add a test administrator")
        print("7. Clear all data")
        print("8. Export to Excel")
        print("9. Exit")
        
        choice = input("\nEnter your choice (1-9): ")
        
        try:
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            
            if choice == '1':
                cursor.execute("SELECT id, email, first_name, last_name, college, course FROM student")
                students = cursor.fetchall()
                print(f"\nTotal students: {len(students)}")
                for student in students:
                    print(f"ID: {student[0]} | {student[2]} {student[3]} | {student[1]} | {student[4]} - {student[5]}")
            
            elif choice == '2':
                cursor.execute("SELECT id, email, full_name, organization, designation FROM administrator")
                admins = cursor.fetchall()
                print(f"\nTotal administrators: {len(admins)}")
                for admin in admins:
                    print(f"ID: {admin[0]} | {admin[2]} | {admin[1]} | {admin[3]} - {admin[4]}")
            
            elif choice == '3':
                email = input("Enter student email to delete: ")
                cursor.execute("DELETE FROM student WHERE email = ?", (email,))
                if cursor.rowcount > 0:
                    conn.commit()
                    print(f"Student with email {email} deleted successfully!")
                else:
                    print("Student not found!")
            
            elif choice == '4':
                email = input("Enter administrator email to delete: ")
                cursor.execute("DELETE FROM administrator WHERE email = ?", (email,))
                if cursor.rowcount > 0:
                    conn.commit()
                    print(f"Administrator with email {email} deleted successfully!")
                else:
                    print("Administrator not found!")
            
            elif choice == '5':
                first_name = input("First name: ")
                last_name = input("Last name: ")
                email = input("Email: ")
                password = input("Password: ")
                college = input("College: ")
                course = input("Course: ")
                graduation_year = input("Graduation year: ")
                current_year = input("Current year: ")
                
                password_hash = generate_password_hash(password)
                cursor.execute("""
                    INSERT INTO student (first_name, last_name, email, password_hash, college, course, graduation_year, current_year, is_verified)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (first_name, last_name, email, password_hash, college, course, graduation_year, current_year, True))
                conn.commit()
                print("Test student added successfully!")
            
            elif choice == '6':
                full_name = input("Full name: ")
                email = input("Email: ")
                password = input("Password: ")
                organization = input("Organization: ")
                designation = input("Designation: ")
                purpose = input("Purpose: ")
                
                password_hash = generate_password_hash(password)
                cursor.execute("""
                    INSERT INTO administrator (full_name, email, password_hash, organization, designation, purpose, is_verified)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                """, (full_name, email, password_hash, organization, designation, purpose, True))
                conn.commit()
                print("Test administrator added successfully!")
            
            elif choice == '7':
                confirm = input("Are you sure you want to clear ALL data? (yes/no): ")
                if confirm.lower() == 'yes':
                    cursor.execute("DELETE FROM application")
                    cursor.execute("DELETE FROM resume_analysis")
                    cursor.execute("DELETE FROM job")
                    cursor.execute("DELETE FROM internship")
                    cursor.execute("DELETE FROM student")
                    cursor.execute("DELETE FROM administrator")
                    conn.commit()
                    print("All data cleared successfully!")
                else:
                    print("Operation cancelled.")
            
            elif choice == '8':
                import pandas as pd
                cursor.execute("SELECT * FROM student")
                students = cursor.fetchall()
                cursor.execute("SELECT * FROM administrator")
                admins = cursor.fetchall()
                
                # Get column names
                cursor.execute("PRAGMA table_info(student)")
                student_columns = [col[1] for col in cursor.fetchall()]
                cursor.execute("PRAGMA table_info(administrator)")
                admin_columns = [col[1] for col in cursor.fetchall()]
                
                # Create DataFrames
                df_students = pd.DataFrame(students, columns=student_columns)
                df_admins = pd.DataFrame(admins, columns=admin_columns)
                
                # Export to Excel
                with pd.ExcelWriter('smarthire_database_export.xlsx') as writer:
                    df_students.to_excel(writer, sheet_name='Students', index=False)
                    df_admins.to_excel(writer, sheet_name='Administrators', index=False)
                
                print("Data exported to smarthire_database_export.xlsx")
            
            elif choice == '9':
                print("Goodbye!")
                break
            
            else:
                print("Invalid choice!")
            
            conn.close()
            
        except Exception as e:
            print(f"Error: {e}")
            if 'conn' in locals():
                conn.close()

if __name__ == "__main__":
    manage_database() 