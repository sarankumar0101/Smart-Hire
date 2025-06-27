import sqlite3
import pandas as pd
import os
from datetime import datetime

def export_database_to_excel():
    db_path = 'instance/smarthire.db'
    excel_path = 'smarthire_database.xlsx'
    
    if not os.path.exists(db_path):
        print(f"Database file not found at: {db_path}")
        return
    
    try:
        # Connect to database
        conn = sqlite3.connect(db_path)
        
        # Get all table names
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cursor.fetchall()
        
        print("=" * 60)
        print("EXPORTING DATABASE TO EXCEL")
        print("=" * 60)
        print(f"Database: {os.path.abspath(db_path)}")
        print(f"Excel file: {os.path.abspath(excel_path)}")
        print(f"Tables found: {len(tables)}")
        print("=" * 60)
        
        # Create Excel writer
        with pd.ExcelWriter(excel_path, engine='openpyxl') as writer:
            
            # Export each table to a separate sheet
            for table in tables:
                table_name = table[0]
                print(f"Exporting table: {table_name}")
                
                # Read table data
                df = pd.read_sql_query(f"SELECT * FROM {table_name}", conn)
                
                # Write to Excel sheet
                df.to_excel(writer, sheet_name=table_name, index=False)
                
                # Auto-adjust column widths
                worksheet = writer.sheets[table_name]
                for column in worksheet.columns:
                    max_length = 0
                    column_letter = column[0].column_letter
                    
                    for cell in column:
                        try:
                            if len(str(cell.value)) > max_length:
                                max_length = len(str(cell.value))
                        except:
                            pass
                    
                    adjusted_width = min(max_length + 2, 50)  # Max width of 50
                    worksheet.column_dimensions[column_letter].width = adjusted_width
                
                print(f"  ✓ {table_name}: {len(df)} rows exported")
        
        conn.close()
        
        print("\n" + "=" * 60)
        print("EXPORT COMPLETED SUCCESSFULLY!")
        print("=" * 60)
        print(f"Excel file created: {os.path.abspath(excel_path)}")
        print(f"Tables exported: {len(tables)}")
        print("\nYou can now open this Excel file anytime to view your database!")
        print("=" * 60)
        
        # Create a summary file
        create_summary_file(tables, excel_path)
        
    except Exception as e:
        print(f"Error exporting database: {e}")

def create_summary_file(tables, excel_path):
    """Create a summary text file with database information"""
    summary_path = 'database_summary.txt'
    
    try:
        with open(summary_path, 'w', encoding='utf-8') as f:
            f.write("=" * 60 + "\n")
            f.write("SMARTHIRE DATABASE SUMMARY\n")
            f.write("=" * 60 + "\n")
            f.write(f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"Database location: instance/smarthire.db\n")
            f.write(f"Excel file: {excel_path}\n")
            f.write(f"Total tables: {len(tables)}\n")
            f.write("=" * 60 + "\n\n")
            
            for table in tables:
                f.write(f"Table: {table[0].upper()}\n")
                f.write("-" * 40 + "\n")
                
                # Get table info
                conn = sqlite3.connect('instance/smarthire.db')
                cursor = conn.cursor()
                
                # Get row count
                cursor.execute(f"SELECT COUNT(*) FROM {table[0]}")
                row_count = cursor.fetchone()[0]
                
                # Get column info
                cursor.execute(f"PRAGMA table_info({table[0]})")
                columns = cursor.fetchall()
                
                f.write(f"Records: {row_count}\n")
                f.write(f"Columns: {len(columns)}\n")
                f.write("Column names:\n")
                for col in columns:
                    f.write(f"  - {col[1]} ({col[2]})\n")
                f.write("\n")
                
                conn.close()
        
        print(f"Summary file created: {summary_path}")
        
    except Exception as e:
        print(f"Error creating summary file: {e}")

def auto_export():
    """Function to automatically export database - can be called anytime"""
    export_database_to_excel()

if __name__ == "__main__":
    export_database_to_excel() 