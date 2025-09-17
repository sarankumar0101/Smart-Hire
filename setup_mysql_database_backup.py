#!/usr/bin/env python3
"""
MySQL Database Setup Script for SmartHire
This script creates the database and all tables for the SmartHire application.
"""

import pymysql
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def create_database():
    """Create the MySQL database if it doesn't exist."""
    
    # Get database configuration from environment
    database_url = os.environ.get('DATABASE_URL', 'mysql+pymysql://root:password@localhost/smarthire')
    
    # Parse the database URL
    if database_url.startswith('mysql+pymysql://'):
        # Remove the mysql+pymysql:// prefix
        connection_string = database_url.replace('mysql+pymysql://', '')
        
        # Split into user:pass@host:port/database
        if '@' in connection_string:
            auth_part, rest = connection_string.split('@', 1)
            if ':' in auth_part:
                username, password = auth_part.split(':', 1)
            else:
                username = auth_part
                password = ''
            
            if '/' in rest:
                host_port, database_name = rest.split('/', 1)
                if ':' in host_port:
                    host, port = host_port.split(':', 1)
                    port = int(port)
                else:
                    host = host_port
                    port = 3306
            else:
                host = rest
                port = 3306
                database_name = 'smarthire'
        else:
            print("Invalid database URL format")
            return False
    else:
        print("Invalid database URL format")
        return False
    
    try:
        # Connect to MySQL server (without specifying database)
        connection = pymysql.connect(
            host=host,
            port=port,
            user=username,
            password=password,
            charset='utf8mb4'
        )
        
        cursor = connection.cursor()
        
        # Create database if it doesn't exist
        cursor.execute(f"CREATE DATABASE IF NOT EXISTS `{database_name}` CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci")
        print(f"✅ Database '{database_name}' created successfully or already exists")
        
        cursor.close()
        connection.close()
        
        return True
        
    except Exception as e:
        print(f"❌ Error creating database: {e}")
        return False

def create_tables():
    """Create all tables using Flask-SQLAlchemy."""
    
    try:
        # Import Flask app and create tables
        from app import app, db
        
        with app.app_context():
            # Create all tables
            db.create_all()
            print("✅ All tables created successfully")
            
            # Create a default server admin if none exists
            from app import ServerAdmin
            
            existing_admin = ServerAdmin.query.filter_by(username='admin').first()
            if not existing_admin:
                admin = ServerAdmin(
                    username='admin',
                    email='admin@smarthire.com',
                    full_name='System Administrator',
                    role='super_admin',
                    is_active=True
                )
                admin.set_password('admin123')  # Change this password!
                
                db.session.add(admin)
                db.session.commit()
                print("✅ Default server admin created (username: admin, password: admin123)")
            else:
                print("ℹ️  Server admin already exists")
                
    except Exception as e:
        print(f"❌ Error creating tables: {e}")
        return False
    
    return True

def main():
    """Main function to set up the database."""
    print("🚀 Setting up MySQL database for SmartHire...")
    print("=" * 50)
    
    # Step 1: Create database
    if create_database():
        print("✅ Database creation completed")
    else:
        print("❌ Database creation failed")
        return
    
    # Step 2: Create tables
    if create_tables():
        print("✅ Table creation completed")
    else:
        print("❌ Table creation failed")
        return
    
    print("=" * 50)
    print("🎉 MySQL database setup completed successfully!")
    print("\n📝 Next steps:")
    print("1. Update your .env file with the correct DATABASE_URL")
    print("2. Change the default admin password")
    print("3. Run your Flask application: python app.py")

if __name__ == "__main__":
    main() 