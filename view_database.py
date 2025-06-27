import sqlite3
import os
from datetime import datetime

def view_database():
    db_path = 'instance/smarthire.db'
    
    if not os.path.exists(db_path):
        print(f"Database file not found at: {db_path}")
        return
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Get all table names
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cursor.fetchall()
        
        print("=" * 60)
        print("SMARTHIRE DATABASE CONTENTS")
        print("=" * 60)
        print(f"Database location: {os.path.abspath(db_path)}")
        print(f"Total tables: {len(tables)}")
        print("=" * 60)
        
        for table in tables:
            table_name = table[0]
            print(f"\n📋 TABLE: {table_name.upper()}")
            print("-" * 40)
            
            # Get table schema
            cursor.execute(f"PRAGMA table_info({table_name});")
            columns = cursor.fetchall()
            column_names = [col[1] for col in columns]
            
            # Get all data from table
            cursor.execute(f"SELECT * FROM {table_name};")
            rows = cursor.fetchall()
            
            if not rows:
                print("   (No data found)")
                continue
            
            # Print column headers
            print("   Columns:", " | ".join(column_names))
            print("   " + "-" * (len(" | ".join(column_names)) + 10))
            
            # Print data rows
            for i, row in enumerate(rows, 1):
                formatted_row = []
                for j, value in enumerate(row):
                    if value is None:
                        formatted_row.append("NULL")
                    elif isinstance(value, str) and len(value) > 50:
                        formatted_row.append(f"{value[:47]}...")
                    else:
                        formatted_row.append(str(value))
                
                print(f"   {i:2d}. {' | '.join(formatted_row)}")
            
            print(f"   Total rows: {len(rows)}")
        
        conn.close()
        print("\n" + "=" * 60)
        print("Database viewing completed!")
        print("=" * 60)
        
    except Exception as e:
        print(f"Error reading database: {e}")

if __name__ == "__main__":
    view_database() 