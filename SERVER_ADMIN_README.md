# SmartHire Server Administration Panel

A comprehensive server-side administration panel for managing the SmartHire job and internship portal. This panel provides full control over the database, users, and system settings.

## Features

### 🔐 **Authentication & Security**
- Secure server admin login system
- Role-based access control
- Session management
- Password protection

### 📊 **Dashboard & Analytics**
- Real-time system statistics
- Recent activity monitoring
- User registration trends
- Job posting analytics

### 👥 **User Management**
- **Students**: Add, edit, delete, search, and manage student accounts
- **Administrators**: Full CRUD operations for admin accounts
- **Approval System**: Approve/reject admin registrations
- **Status Management**: Manage user verification and approval status

### 💼 **Content Management**
- **Jobs**: Create, edit, delete, and approve job postings
- **Internships**: Manage internship opportunities
- **Applications**: View and manage job/internship applications
- **Competitions**: Manage competitions and events

### 🗄️ **Database Operations**
- **Export**: Export entire database to Excel format
- **Backup**: Create database backups with timestamps
- **Search**: Advanced search functionality across all tables
- **Bulk Operations**: Perform bulk actions on multiple records

### ⚙️ **System Settings**
- Maintenance mode toggle
- Registration controls
- Email notification settings
- System configuration

## Installation & Setup

### Prerequisites
- Python 3.8 or higher
- Access to the main SmartHire database
- Required Python packages (see requirements.txt)

### 1. Install Dependencies
```bash
pip install -r server_requirements.txt
```

### 2. Database Setup
The server admin panel uses the same database as the main SmartHire application. Ensure the main app is running and the database exists.

### 3. Create Server Admin Account
```bash
python -c "
from app import app, db, ServerAdmin
with app.app_context():
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
    print('Server admin created: admin/admin123')
"
```

### 4. Run the Server Admin Panel
```bash
python server_admin_panel.py
```

The panel will be available at: `http://localhost:5001`

## Usage Guide

### 🔑 **Login**
- Username: `admin`
- Password: `admin123`
- **Important**: Change the default password after first login

### 📋 **Managing Students**
1. Navigate to "Students" in the sidebar
2. Use search to find specific students
3. Click "Add New Student" to create accounts
4. Use edit/delete buttons for existing students
5. Manage verification status

### 👔 **Managing Administrators**
1. Go to "Admins" section
2. Approve pending admin registrations
3. Edit admin details and permissions
4. Suspend or delete admin accounts
5. Monitor admin activity

### 💼 **Job Management**
1. Access "Jobs" section
2. Review pending job postings
3. Approve or reject jobs
4. Edit job details
5. Monitor job statistics

### 📊 **Database Operations**
1. **Export**: Click "Export Database" to download Excel file
2. **Backup**: Use "Backup Database" for data safety
3. **Search**: Use search bars to find specific records
4. **Bulk Actions**: Select multiple records for bulk operations

### ⚙️ **System Settings**
1. Access "Settings" section
2. Toggle maintenance mode
3. Control user registration
4. Manage email notifications
5. Configure system parameters

## API Endpoints

### Authentication
- `POST /login` - Server admin login
- `GET /logout` - Logout

### Dashboard
- `GET /dashboard` - Main dashboard with statistics

### Students Management
- `GET /api/students` - Get all students
- `POST /api/students` - Create new student
- `PUT /api/students` - Update student
- `DELETE /api/students?id=<id>` - Delete student

### Administrators Management
- `GET /api/admins` - Get all admins
- `POST /api/admins` - Create new admin
- `PUT /api/admins` - Update admin
- `DELETE /api/admins?id=<id>` - Delete admin

### Jobs Management
- `GET /api/jobs` - Get all jobs
- `POST /api/jobs` - Create new job
- `PUT /api/jobs` - Update job
- `DELETE /api/jobs?id=<id>` - Delete job

### Database Operations
- `GET /export/database` - Export database to Excel
- `GET /backup/database` - Create database backup

## Security Considerations

### 🔒 **Access Control**
- Server admin panel runs on a separate port (5001)
- Requires server admin credentials
- Session-based authentication
- Automatic logout on inactivity

### 🛡️ **Data Protection**
- All database operations are logged
- Backup functionality for data safety
- Input validation and sanitization
- SQL injection protection

### 🔐 **Best Practices**
1. **Change Default Password**: Immediately change admin password
2. **Regular Backups**: Schedule regular database backups
3. **Monitor Access**: Keep track of admin panel access
4. **Update Regularly**: Keep dependencies updated
5. **Secure Network**: Run on secure, private network

## File Structure

```
server_admin_panel/
├── server_admin_panel.py          # Main application
├── server_requirements.txt        # Python dependencies
├── server_templates/              # HTML templates
│   ├── server_login.html         # Login page
│   ├── server_dashboard.html     # Main dashboard
│   ├── manage_students.html      # Student management
│   ├── manage_admins.html        # Admin management
│   ├── manage_jobs.html          # Job management
│   ├── manage_internships.html   # Internship management
│   ├── manage_applications.html  # Application management
│   └── system_settings.html      # System settings
├── backups/                       # Database backups
├── server_uploads/                # File uploads
└── SERVER_ADMIN_README.md         # This file
```

## Troubleshooting

### Common Issues

1. **Database Connection Error**
   - Ensure main SmartHire app is running
   - Check database file path
   - Verify database permissions

2. **Login Issues**
   - Verify server admin credentials
   - Check if admin account exists
   - Clear browser cache and cookies

3. **Export/Backup Failures**
   - Check file permissions
   - Ensure sufficient disk space
   - Verify pandas/openpyxl installation

4. **Template Errors**
   - Check template file paths
   - Verify Jinja2 syntax
   - Clear browser cache

### Support

For technical support or issues:
1. Check the main SmartHire application logs
2. Verify database integrity
3. Review server admin panel logs
4. Contact system administrator

## License

This server administration panel is part of the SmartHire project and follows the same licensing terms.

---

**⚠️ Security Notice**: This is a powerful administrative tool. Use with caution and ensure proper access controls are in place. Only authorized personnel should have access to this panel. 