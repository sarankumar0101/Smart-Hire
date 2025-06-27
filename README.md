# SmartHire - Job Portal with Resume Analysis

A comprehensive job portal platform that connects students with employers, featuring AI-powered resume analysis and job application management.

## Features

### For Students
- **User Registration & Authentication**: Secure student registration with email verification
- **Resume Analysis**: AI-powered resume analysis using OpenAI GPT-3.5
- **Job Browsing**: Browse and search available job opportunities
- **Job Applications**: Apply to jobs with optional cover letters
- **Application Tracking**: Track application status and history
- **Dashboard**: Personalized student dashboard

### For Administrators/Employers
- **Administrator Registration**: Secure registration for employers and administrators
- **Job Posting**: Create and manage job listings
- **Application Management**: Review and manage job applications
- **Dashboard**: Administrative dashboard for job management

## Database Schema

The application uses SQLite with the following database models:

### 1. Student Table
```sql
- id (Primary Key)
- first_name (String, 50 chars)
- last_name (String, 50 chars)
- email (String, 120 chars, Unique)
- password_hash (String, 255 chars)
- date_of_birth (Date)
- college (String, 100 chars)
- course (String, 50 chars)
- graduation_year (String, 10 chars)
- current_year (String, 20 chars)
- roll_number (String, 20 chars)
- created_at (DateTime)
- is_verified (Boolean)
```

### 2. Administrator Table
```sql
- id (Primary Key)
- full_name (String, 100 chars)
- email (String, 120 chars, Unique)
- password_hash (String, 255 chars)
- organization (String, 100 chars)
- designation (String, 50 chars)
- org_website (String, 200 chars, Optional)
- purpose (String, 100 chars)
- admin_code (String, 50 chars, Optional)
- created_at (DateTime)
- is_verified (Boolean)
```

### 3. Job Table
```sql
- id (Primary Key)
- title (String, 100 chars)
- company (String, 100 chars)
- location (String, 100 chars)
- description (Text)
- requirements (Text, Optional)
- salary_range (String, 50 chars, Optional)
- job_type (String, 20 chars) - Full-time, Part-time, Internship, Contract
- posted_by (Foreign Key to Administrator)
- posted_at (DateTime)
- is_active (Boolean)
```

### 4. ResumeAnalysis Table
```sql
- id (Primary Key)
- student_id (Foreign Key to Student)
- original_content (Text)
- strengths (Text, Optional)
- weaknesses (Text, Optional)
- suggestions (Text, Optional)
- grammar_issues (Text, Optional)
- analyzed_at (DateTime)
```

### 5. Application Table
```sql
- id (Primary Key)
- student_id (Foreign Key to Student)
- job_id (Foreign Key to Job)
- applied_at (DateTime)
- status (String, 20 chars) - Pending, Accepted, Rejected
- cover_letter (Text, Optional)
```

## Installation & Setup

### Prerequisites
- Python 3.7 or higher
- pip (Python package installer)

### Step 1: Clone the Repository
```bash
git clone <repository-url>
cd duplicate
```

### Step 2: Install Dependencies
```bash
pip install -r requirements.txt
```

### Step 3: Environment Setup
Create a `.env` file in the root directory with your OpenAI API key:
```
OPENAI_API_KEY=your_openai_api_key_here
```

### Step 4: Database Initialization
The database will be automatically created when you run the application for the first time. The SQLite database file (`smarthire.db`) will be created in the root directory.

### Step 5: Run the Application
```bash
python app.py
```

The application will be available at `http://localhost:5000`

## Usage

### Student Registration
1. Navigate to `/register_student.html`
2. Fill in all required fields
3. Verify email with OTP
4. Complete registration

### Administrator Registration
1. Navigate to `/register_administrator.html`
2. Fill in organization details
3. Verify email with OTP
4. Complete registration

### Job Posting (Administrators)
1. Login as administrator
2. Navigate to `/post_job`
3. Fill in job details
4. Submit job posting

### Job Application (Students)
1. Login as student
2. Browse jobs at `/jobs`
3. Click "Apply Now" on desired job
4. Submit application with optional cover letter

### Resume Analysis (Students)
1. Login as student
2. Navigate to `/resume_tools`
3. Upload resume file
4. Receive AI-powered analysis

## API Endpoints

### Authentication
- `POST /login_submit` - User login
- `POST /register_student_submit` - Student registration
- `POST /register_administrator_submit` - Administrator registration
- `GET /logout` - User logout

### Job Management
- `GET /jobs` - View all active jobs
- `POST /post_job` - Post new job (Admin only)
- `POST /apply_job/<job_id>` - Apply for job (Student only)

### Resume Analysis
- `POST /analyze` - Analyze resume with AI (Student only)

### Application Management
- `GET /my_applications` - View student's applications
- `GET /manage_applications` - Manage applications (Admin only)
- `POST /update_application_status/<application_id>` - Update application status (Admin only)

### OTP Verification
- `POST /send_otp` - Send OTP to email
- `POST /verify_otp` - Verify OTP

## Security Features

- **Password Hashing**: All passwords are hashed using Werkzeug's security functions
- **Session Management**: Secure session handling with Flask sessions
- **Email Verification**: OTP-based email verification for registration
- **Authentication Required**: Protected routes require user authentication
- **Role-based Access**: Different access levels for students and administrators

## Database Operations

### Creating Tables
Tables are automatically created when the application starts:
```python
with app.app_context():
    db.create_all()
```

### Adding Records
```python
# Example: Adding a new student
student = Student(
    first_name="John",
    last_name="Doe",
    email="john@example.com",
    # ... other fields
)
student.set_password("secure_password")
db.session.add(student)
db.session.commit()
```

### Querying Records
```python
# Example: Finding a student by email
student = Student.query.filter_by(email="john@example.com").first()

# Example: Getting all active jobs
jobs = Job.query.filter_by(is_active=True).all()
```

## File Structure
```
duplicate/
├── app.py                          # Main Flask application
├── requirements.txt                # Python dependencies
├── smarthire.db                   # SQLite database (created automatically)
├── static/                        # Static files (CSS, images)
├── templates/                     # HTML templates
│   ├── Index.html
│   ├── login.html
│   ├── register_student.html
│   ├── register_administrator.html
│   ├── student_dashboard.html
│   ├── admin_dashboard.html
│   ├── jobs.html
│   ├── post_job.html
│   └── ...
└── README.md                      # This file
```

## Troubleshooting

### Common Issues

1. **Database not created**: Ensure you have write permissions in the project directory
2. **OpenAI API errors**: Verify your API key is correct and has sufficient credits
3. **Email sending fails**: Check your email credentials in the app.py file
4. **Import errors**: Make sure all dependencies are installed with `pip install -r requirements.txt`

### Database Reset
To reset the database, simply delete the `smarthire.db` file and restart the application.

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## License

This project is licensed under the MIT License. 