#!/usr/bin/env python3
"""
SmartHire Server Admin Panel Setup Script
This script sets up the server admin panel and creates the necessary directories and admin account.
"""

import os
import sys
from pathlib import Path

def create_directories():
    """Create necessary directories for the server admin panel."""
    directories = [
        'server_templates',
        'backups',
        'server_uploads'
    ]
    
    for directory in directories:
        Path(directory).mkdir(exist_ok=True)
        print(f"✓ Created directory: {directory}")

def create_server_admin():
    """Create the initial server admin account."""
    try:
        # Import from main app
        sys.path.append('.')
        from app import app, db, ServerAdmin
        
        with app.app_context():
            # Check if server admin already exists
            existing_admin = ServerAdmin.query.filter_by(username='admin').first()
            if existing_admin:
                print("✓ Server admin account already exists")
                return
            
            # Create server admin
            admin = ServerAdmin(
                username='admin',
                email='admin@smarthire.com',
                full_name='System Administrator',
                role='server_admin',
                permissions='all',
                is_active=True
            )
            admin.set_password('admin123')
            
            db.session.add(admin)
            db.session.commit()
            print("✓ Server admin account created successfully")
            print("  Username: admin")
            print("  Password: admin123")
            print("  ⚠️  IMPORTANT: Change the password after first login!")
            
    except ImportError as e:
        print(f"✗ Error: Could not import from main app: {e}")
        print("  Make sure the main SmartHire app is in the same directory")
        return False
    except Exception as e:
        print(f"✗ Error creating server admin: {e}")
        return False
    
    return True

def check_dependencies():
    """Check if required packages are installed."""
    required_packages = [
        'flask',
        'flask_sqlalchemy',
        'flask_cors',
        'pandas',
        'openpyxl'
    ]
    
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package.replace('-', '_'))
            print(f"✓ {package}")
        except ImportError:
            missing_packages.append(package)
            print(f"✗ {package} (missing)")
    
    if missing_packages:
        print(f"\n⚠️  Missing packages: {', '.join(missing_packages)}")
        print("Install them using: pip install -r server_requirements.txt")
        return False
    
    return True

def main():
    """Main setup function."""
    print("🚀 SmartHire Server Admin Panel Setup")
    print("=" * 50)
    
    # Check dependencies
    print("\n📦 Checking dependencies...")
    if not check_dependencies():
        print("\n❌ Setup failed: Missing dependencies")
        return
    
    # Create directories
    print("\n📁 Creating directories...")
    create_directories()
    
    # Create server admin
    print("\n👤 Creating server admin account...")
    if not create_server_admin():
        print("\n❌ Setup failed: Could not create admin account")
        return
    
    print("\n✅ Setup completed successfully!")
    print("\n🎯 Next steps:")
    print("1. Run the server admin panel: python server_admin_panel.py")
    print("2. Access the panel at: http://localhost:5001")
    print("3. Login with: admin / admin123")
    print("4. Change the default password immediately")
    print("\n📚 For more information, see: SERVER_ADMIN_README.md")

if __name__ == '__main__':
    main() 