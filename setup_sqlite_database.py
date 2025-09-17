#!/usr/bin/env python3
"""
SQLite Database Setup Script for SmartHire
This script creates the database and all tables for the SmartHire application.
"""

import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def create_database():
    """Create the SQLite database if it doesn't exist."""
    
    try:
        # Import Flask app and create tables
        from app import app, db
        
        with app.app_context():
            # Create all tables (this will also create the database file if it doesn't exist)
            db.create_all()
            print("✅ Database and all tables created successfully")
            
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
        print(f"❌ Error creating database: {e}")
        return False
    
    return True

def main():
    """Main function to set up the database."""
    print("🚀 Setting up SQLite database for SmartHire...")
    print("=" * 50)
    
    # Create database and tables
    if create_database():
        print("✅ Database setup completed")
    else:
        print("❌ Database setup failed")
        return
    
    print("=" * 50)
    print("🎉 SQLite database setup completed successfully!")
    print("\n📝 Next steps:")
    print("1. Update your .env file with the correct DATABASE_URL (sqlite:///smarthire.db)")
    print("2. Change the default admin password")
    print("3. Run your Flask application: python app.py")
    print("\n📁 Database file location: smarthire.db")

if __name__ == "__main__":
    main() 