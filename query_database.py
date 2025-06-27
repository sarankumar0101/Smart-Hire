import sqlite3
import os

def query_database():
    db_path = 'instance/smarthire.db'
    
    if not os.path.exists(db_path):
        print(f"Database file not found at: {db_path}")
        return
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        print("=" * 60)
        print("SMARTHIRE DATABASE QUERY TOOL")
        print("=" * 60)
        print("Available tables: student, administrator, job, resume_analysis, application")
        print("Type 'quit' to exit")
        print("=" * 60)
        
        while True:
            query = input("\nEnter SQL query: ").strip()
            
            if query.lower() == 'quit':
                break
            
            if not query:
                continue
            
            try:
                cursor.execute(query)
                
                # Check if it's a SELECT query
                if query.strip().upper().startswith('SELECT'):
                    rows = cursor.fetchall()
                    
                    if rows:
                        # Get column names
                        column_names = [description[0] for description in cursor.description]
                        
                        # Print headers
                        print("\nResults:")
                        print("-" * 80)
                        print(" | ".join(f"{col:15}" for col in column_names))
                        print("-" * 80)
                        
                        # Print data
                        for row in rows:
                            formatted_row = []
                            for value in row:
                                if value is None:
                                    formatted_row.append("NULL".ljust(15))
                                elif isinstance(value, str) and len(value) > 12:
                                    formatted_row.append(f"{value[:12]}...".ljust(15))
                                else:
                                    formatted_row.append(str(value).ljust(15))
                            print(" | ".join(formatted_row))
                        
                        print(f"\nTotal rows: {len(rows)}")
                    else:
                        print("No results found.")
                else:
                    # For non-SELECT queries (INSERT, UPDATE, DELETE)
                    conn.commit()
                    print(f"Query executed successfully. Rows affected: {cursor.rowcount}")
                    
            except Exception as e:
                print(f"Error executing query: {e}")
        
        conn.close()
        print("\nDatabase connection closed.")
        
    except Exception as e:
        print(f"Error connecting to database: {e}")

if __name__ == "__main__":
    query_database() 