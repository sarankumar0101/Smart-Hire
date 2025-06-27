from flask import Flask, render_template, request, jsonify, redirect, url_for, session, send_from_directory
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, timedelta
import random
import smtplib
import ssl
import re
import os
from werkzeug.utils import secure_filename
import secrets
import string
import requests

app = Flask(__name__)
app.secret_key = 'supersecretkey123'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///smarthire.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size
# Session configuration
app.config['PERMANENT_SESSION_LIFETIME'] = 30 * 24 * 60 * 60  # 30 days for "Remember Me"
app.config['SESSION_COOKIE_SECURE'] = False  # Set to True in production with HTTPS
app.config['SESSION_COOKIE_HTTPONLY'] = True
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'
CORS(app)

# Create uploads directory if it doesn't exist
if not os.path.exists(app.config['UPLOAD_FOLDER']):
    os.makedirs(app.config['UPLOAD_FOLDER'])

# Allowed file extensions for resumes
ALLOWED_EXTENSIONS = {'pdf', 'doc', 'docx', 'txt'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

db = SQLAlchemy(app)

# The /analyze route is already using the Gemini REST API via requests, so no further changes needed there.

otp_store = {}
password_reset_tokens = {}  # Store reset tokens with expiration
password_reset_otps = {}    # Store OTPs for password reset

# Database Models
class Student(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(50), nullable=False)
    last_name = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    date_of_birth = db.Column(db.Date, nullable=False)
    college = db.Column(db.String(100), nullable=False)
    course = db.Column(db.String(50), nullable=False)
    graduation_year = db.Column(db.String(10), nullable=False)
    current_year = db.Column(db.String(20), nullable=False)
    roll_number = db.Column(db.String(20), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    is_verified = db.Column(db.Boolean, default=False)
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

class Administrator(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    full_name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    organization = db.Column(db.String(100), nullable=False)
    designation = db.Column(db.String(50), nullable=False)
    org_website = db.Column(db.String(200))
    purpose = db.Column(db.String(100), nullable=False)
    admin_code = db.Column(db.String(50))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    is_verified = db.Column(db.Boolean, default=False)
    is_approved = db.Column(db.Boolean, default=False)  # Server admin approval
    admin_level = db.Column(db.String(20), default='regular')  # regular, server_admin
    status = db.Column(db.String(20), default='pending')  # pending, approved, rejected, suspended
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

class ServerAdmin(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    full_name = db.Column(db.String(100), nullable=False)
    role = db.Column(db.String(50), default='server_admin')  # server_admin, super_admin
    permissions = db.Column(db.Text)  # JSON string of permissions
    last_login = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    is_active = db.Column(db.Boolean, default=True)
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

class Job(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    company = db.Column(db.String(100), nullable=False)
    location = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=False)
    requirements = db.Column(db.Text)
    salary_range = db.Column(db.String(50))
    job_type = db.Column(db.String(20), nullable=False)  # Full-time, Part-time, Internship
    posted_by = db.Column(db.Integer, db.ForeignKey('administrator.id'), nullable=False)
    posted_at = db.Column(db.DateTime, default=datetime.utcnow)
    is_active = db.Column(db.Boolean, default=True)
    is_approved = db.Column(db.Boolean, default=False)  # Server admin approval
    status = db.Column(db.String(20), default='pending')  # pending, approved, rejected, flagged
    flagged_reason = db.Column(db.Text)  # Reason if flagged as suspicious
    reviewed_by = db.Column(db.Integer, db.ForeignKey('server_admin.id'))
    reviewed_at = db.Column(db.DateTime)
    
    administrator = db.relationship('Administrator', backref=db.backref('jobs', lazy=True))
    reviewer = db.relationship('ServerAdmin', backref=db.backref('reviewed_jobs', lazy=True))

class Internship(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    company = db.Column(db.String(100), nullable=False)
    location = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=False)
    requirements = db.Column(db.Text)
    duration = db.Column(db.String(50))  # e.g., "3 months", "6 months"
    stipend = db.Column(db.String(50))   # e.g., "₹15,000/month", "Unpaid"
    internship_type = db.Column(db.String(20), nullable=False)  # Summer, Winter, Year-round
    posted_by = db.Column(db.Integer, db.ForeignKey('administrator.id'), nullable=False)
    posted_at = db.Column(db.DateTime, default=datetime.utcnow)
    is_active = db.Column(db.Boolean, default=True)
    is_approved = db.Column(db.Boolean, default=False)  # Server admin approval
    status = db.Column(db.String(20), default='pending')  # pending, approved, rejected, flagged
    flagged_reason = db.Column(db.Text)  # Reason if flagged as suspicious
    reviewed_by = db.Column(db.Integer, db.ForeignKey('server_admin.id'))
    reviewed_at = db.Column(db.DateTime)
    
    administrator = db.relationship('Administrator', backref=db.backref('internships', lazy=True))
    reviewer = db.relationship('ServerAdmin', backref=db.backref('reviewed_internships', lazy=True))

class ResumeAnalysis(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('student.id'), nullable=False)
    original_content = db.Column(db.Text, nullable=False)
    strengths = db.Column(db.Text)
    weaknesses = db.Column(db.Text)
    suggestions = db.Column(db.Text)
    grammar_issues = db.Column(db.Text)
    analyzed_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    student = db.relationship('Student', backref=db.backref('resume_analyses', lazy=True))

class Application(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('student.id'), nullable=False)
    job_id = db.Column(db.Integer, db.ForeignKey('job.id'), nullable=True)
    internship_id = db.Column(db.Integer, db.ForeignKey('internship.id'), nullable=True)
    applied_at = db.Column(db.DateTime, default=datetime.utcnow)
    status = db.Column(db.String(20), default='Pending')  # Pending, Accepted, Rejected
    cover_letter = db.Column(db.Text)
    resume_filename = db.Column(db.String(255))
    
    # Additional form fields
    phone_number = db.Column(db.String(20))
    current_cgpa = db.Column(db.String(10))
    skills = db.Column(db.Text)
    experience = db.Column(db.Text)
    projects = db.Column(db.Text)
    why_interested = db.Column(db.Text)
    availability = db.Column(db.String(100))
    
    student = db.relationship('Student', backref=db.backref('applications', lazy=True))
    job = db.relationship('Job', backref=db.backref('applications', lazy=True))
    internship = db.relationship('Internship', backref=db.backref('applications', lazy=True))

class Competition(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    organizer = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=False)
    category = db.Column(db.String(50), nullable=False)  # e.g., "Programming", "Design", "Business", "Science"
    prize_pool = db.Column(db.String(100))  # e.g., "₹50,000", "Internship Opportunity"
    deadline = db.Column(db.DateTime, nullable=False)
    start_date = db.Column(db.DateTime, nullable=False)
    end_date = db.Column(db.DateTime, nullable=False)
    max_participants = db.Column(db.Integer)
    current_participants = db.Column(db.Integer, default=0)
    eligibility = db.Column(db.Text)  # Who can participate
    rules = db.Column(db.Text)
    posted_by = db.Column(db.Integer, db.ForeignKey('administrator.id'), nullable=False)
    posted_at = db.Column(db.DateTime, default=datetime.utcnow)
    is_active = db.Column(db.Boolean, default=True)
    
    administrator = db.relationship('Administrator', backref=db.backref('competitions', lazy=True))

class CompetitionParticipant(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    competition_id = db.Column(db.Integer, db.ForeignKey('competition.id'), nullable=False)
    student_id = db.Column(db.Integer, db.ForeignKey('student.id'), nullable=False)
    registered_at = db.Column(db.DateTime, default=datetime.utcnow)
    status = db.Column(db.String(20), default='Registered')  # Registered, Submitted, Won, Lost
    
    competition = db.relationship('Competition', backref=db.backref('participants', lazy=True))
    student = db.relationship('Student', backref=db.backref('competition_participations', lazy=True))

# Create database tables
with app.app_context():
    db.create_all()

@app.route('/')
def home():
    return render_template('Index.html')

@app.route('/internships')
def internships():
    internships = Internship.query.filter_by(is_active=True).order_by(Internship.posted_at.desc()).all()
    return render_template('internships.html', internships=internships)

@app.route('/jobs')
def jobs():
    jobs = Job.query.filter_by(is_active=True).order_by(Job.posted_at.desc()).all()
    return render_template('jobs.html', jobs=jobs)

@app.route('/resume_tools')
def resume_tools():
    if 'user_id' not in session or session.get('user_type') != 'student':
        return redirect(url_for('login', next=request.path))
    return render_template('resume_tools.html')

@app.route('/student_dashboard')
def student_dashboard():
    if 'user_id' not in session or session.get('user_type') != 'student':
        return redirect(url_for('login', next=request.path))
    return render_template('student_dashboard.html')

@app.route('/admin_dashboard')
def admin_dashboard():
    if 'user_id' not in session or session.get('user_type') != 'admin':
        return redirect(url_for('login', next=request.path))
    return render_template('admin_dashboard.html')

@app.route('/resume_modifier')
def resume_modifier():
    return render_template('resume_modifier.html')

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/login')
def login():
    next_url = request.args.get('next', '')
    return render_template('login.html', next=next_url)

@app.route('/Register')
def register():
    return render_template('Register.html')

@app.route('/register_student.html')
def register_student():
    return render_template('register_student.html')

@app.route('/register_administrator.html')
def register_administrator():
    return render_template('register_administrator.html')

@app.route('/login_submit', methods=['POST'])
def login_submit():
    email = request.form.get('email')
    password = request.form.get('password')
    role = request.form.get('role', 'student')
    next_url = request.args.get('next') or request.form.get('next')
    remember_me = request.form.get('remember_me') == 'true'
    
    if not email or not password:
        return jsonify({'success': False, 'message': 'Email and password are required'}), 400
    
    try:
        if role == 'student':
            user = Student.query.filter_by(email=email).first()
            if user and user.check_password(password):
                session['user_id'] = user.id
                session['user_type'] = 'student'
                session['user_email'] = user.email
                session['user_name'] = f"{user.first_name} {user.last_name}"
                
                # Set session permanence based on "Remember Me"
                if remember_me:
                    session.permanent = True
                else:
                    session.permanent = False
                
                redirect_url = next_url or url_for('student_dashboard')
                return jsonify({'success': True, 'redirect': redirect_url})
            else:
                return jsonify({'success': False, 'message': 'Invalid email or password'}), 401
        else:  # admin
            user = Administrator.query.filter_by(email=email).first()
            if user and user.check_password(password):
                session['user_id'] = user.id
                session['user_type'] = 'admin'
                session['user_email'] = user.email
                session['user_name'] = user.full_name
                
                # Set session permanence based on "Remember Me"
                if remember_me:
                    session.permanent = True
                else:
                    session.permanent = False
                
                redirect_url = next_url or url_for('admin_dashboard')
                return jsonify({'success': True, 'redirect': redirect_url})
            else:
                return jsonify({'success': False, 'message': 'Invalid email or password'}), 401
        
    except Exception as e:
        return jsonify({'success': False, 'message': f'Login failed. Error: {str(e)}'}), 500

@app.route('/logout')
def logout():
    session.pop('user', None)
    session.pop('user_id', None)
    session.pop('user_type', None)
    session.pop('user_email', None)
    session.pop('user_name', None)
    return redirect(url_for('login'))

@app.route('/send_otp', methods=['POST'])
def send_otp():
    data = request.json
    email = data['email']
    otp = str(random.randint(1000, 9999))
    otp_store[email] = otp

    try:
        sender_email = "smarthire2k25@gmail.com"
        sender_password = "hwqd hzpv srus akig"
        message = f"Subject: SmartHire OTP Verification\n\nYour OTP is: {otp}"

        context = ssl.create_default_context()
        with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=context) as server:
            server.login(sender_email, sender_password)
            server.sendmail(sender_email, email, message)

        return jsonify({"status": "success", "message": "OTP sent successfully"})
    except Exception as e:
        return jsonify({"status": "error", "message": f"Email send failed: {str(e)}"})

@app.route('/verify_otp', methods=['POST'])
def verify_otp():
    data = request.json
    email = data.get('email')
    otp = data.get('otp')
    if otp_store.get(email) == otp:
        return jsonify({"status": "success", "message": "OTP verified successfully"})
    else:
        return jsonify({"status": "fail", "message": "Invalid OTP"})

def send_application_status_email(student_email, student_name, job_title, company_name, status, job_details=None):
    """Send email notification to student about application status, including job/internship details if accepted."""
    try:
        sender_email = "smarthire2k25@gmail.com"
        sender_password = "hwqd hzpv srus akig"
        
        if status == 'Accepted':
            subject = "Congratulations! You've been shortlisted for further interview"
            message = f"""Subject: {subject}

Dear {student_name},

We are pleased to inform you that your application for the position of "{job_title}" at {company_name} has been accepted!

Job Details:
{job_details if job_details else ''}

You have been shortlisted for the further interview process. Our team will contact you soon with the next steps.

Best regards,
SmartHire Team
"""
        else:
            subject = "Application Status Update"
            message = f"""Subject: {subject}

Dear {student_name},

Thank you for your interest in the position of "{job_title}" at {company_name}.

After careful review of your application, we regret to inform you that we will not be moving forward with your application at this time.

We encourage you to apply for other opportunities that match your skills and experience.

Best regards,
SmartHire Team
"""

        context = ssl.create_default_context()
        with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=context) as server:
            server.login(sender_email, sender_password)
            server.sendmail(sender_email, student_email, message)

        return True
    except Exception as e:
        print(f"Error sending email: {e}")
        return False

@app.route('/analyze', methods=['POST'])
def analyze_resume():
    try:
        if 'user_id' not in session or session.get('user_type') != 'student':
            return jsonify({"error": "Authentication required"}), 401
            
        uploaded_file = request.files.get('resume')
        if not uploaded_file:
            return jsonify({"error": "No file uploaded"}), 400

        content = uploaded_file.read().decode('utf-8', errors='ignore')
        if not content.strip():
            return jsonify({"error": "Uploaded file is empty or not readable"}), 400

        prompt = f"""
        Analyze the following resume content and provide:
        - Strengths
        - Weaknesses
        - Suggestions for improvement
        - Grammar Issues
        - Vocabulary Mistakes (such as repeated words, weak word choices, or inappropriate vocabulary for a professional resume)

        Respond with bullet points under each category.

        Resume:
        {content}
        """

        # Gemini REST API call
        url = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key=AIzaSyB0_1qrv04YNN8n2R6iH5SuwEgj6r0Or2k"
        headers = {"Content-Type": "application/json"}
        data = {
            "contents": [
                {
                    "parts": [
                        {"text": prompt}
                    ]
                }
            ]
        }
        response = requests.post(url, headers=headers, json=data)
        if response.status_code != 200:
            return jsonify({"error": f"Gemini API error: {response.text}"}), 500

        result = response.json()
        # Extract the generated text
        try:
            result_text = result["candidates"][0]["content"]["parts"][0]["text"]
        except Exception:
            return jsonify({"error": "Failed to parse Gemini API response"}), 500

        def extract_section(title):
            match = re.search(rf"{title}.*?:\s*(.*?)(?=\n\S|\Z)", result_text, re.IGNORECASE | re.DOTALL)
            if match:
                return [line.strip("•- \n") for line in match.group(1).split('\n') if line.strip()]
            return []

        strengths = extract_section("Strengths")
        weaknesses = extract_section("Weaknesses")
        suggestions = extract_section("Suggestions")
        grammar = extract_section("Grammar Issues")
        vocab = extract_section("Vocabulary Mistakes")
        
        # Store analysis in database
        analysis = ResumeAnalysis(
            student_id=session['user_id'],
            original_content=content,
            strengths='\n'.join(strengths) if strengths else '',
            weaknesses='\n'.join(weaknesses) if weaknesses else '',
            suggestions='\n'.join(suggestions) if suggestions else '',
            grammar_issues='\n'.join(grammar) if grammar else ''
        )
        
        db.session.add(analysis)
        db.session.commit()

        return jsonify({
            "strengths": strengths,
            "weaknesses": weaknesses,
            "suggestions": suggestions,
            "grammar": grammar,
            "vocab": vocab
        })

    except Exception as e:
        print("⚠️ Error during analysis:", e)
        return jsonify({"error": str(e)}), 500

@app.route('/register_student_submit', methods=['POST'])
def register_student_submit():
    try:
        # Get form data
        first_name = request.form.get('firstName')
        last_name = request.form.get('lastName')
        email = request.form.get('email')
        password = request.form.get('password')
        date_of_birth = request.form.get('dob')
        college = request.form.get('college')
        course = request.form.get('course')
        graduation_year = request.form.get('graduation')
        current_year = request.form.get('year')
        roll_number = request.form.get('roll')
        
        # Check if email already exists
        if Student.query.filter_by(email=email).first():
            return jsonify({"status": "error", "message": "Email already registered"})
        
        # Create new student
        student = Student(
            first_name=first_name,
            last_name=last_name,
            email=email,
            date_of_birth=datetime.strptime(date_of_birth, '%Y-%m-%d').date(),
            college=college,
            course=course,
            graduation_year=graduation_year,
            current_year=current_year,
            roll_number=roll_number,
            is_verified=True
        )
        student.set_password(password)
        
        db.session.add(student)
        db.session.commit()
        
        return jsonify({
            "status": "success", 
            "message": "Registration successful!",
            "redirect": "/login"
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({"status": "error", "message": f"Registration failed: {str(e)}"})

@app.route('/register_administrator_submit', methods=['POST'])
def register_administrator_submit():
    try:
        # Get form data
        full_name = request.form.get('fullName')
        email = request.form.get('email')
        password = request.form.get('password')
        organization = request.form.get('organization')
        designation = request.form.get('designation')
        org_website = request.form.get('orgWebsite')
        purpose = request.form.get('purpose')
        admin_code = request.form.get('adminCode')
        
        # Check if email already exists
        if Administrator.query.filter_by(email=email).first():
            return "Email already registered"
        
        # Create new administrator
        admin = Administrator(
            full_name=full_name,
            email=email,
            organization=organization,
            designation=designation,
            org_website=org_website,
            purpose=purpose,
            admin_code=admin_code,
            is_verified=True
        )
        admin.set_password(password)
        
        db.session.add(admin)
        db.session.commit()
        
        return "Registration successful! You can now login."
        
    except Exception as e:
        db.session.rollback()
        return f"Registration failed: {str(e)}"

@app.route('/post_job', methods=['GET', 'POST'])
def post_job():
    if 'user_id' not in session or session.get('user_type') != 'admin':
        return redirect(url_for('login', next=request.path))
    
    if request.method == 'POST':
        try:
            # Check if admin is approved
            admin = Administrator.query.get(session['user_id'])
            if not admin or not admin.is_approved:
                return jsonify({"status": "error", "message": "Your account is not approved yet. Please contact the system administrator."})
            
            job = Job(
                title=request.form.get('title'),
                company=request.form.get('company'),
                location=request.form.get('location'),
                description=request.form.get('description'),
                requirements=request.form.get('requirements'),
                salary_range=request.form.get('salary_range'),
                job_type=request.form.get('job_type'),
                posted_by=session['user_id'],
                is_approved=True,  # Auto-approve jobs from approved admins
                status='approved'
            )
            db.session.add(job)
            db.session.commit()
            return jsonify({"status": "success", "message": "Job posted successfully!"})
        except Exception as e:
            db.session.rollback()
            return jsonify({"status": "error", "message": str(e)})
    
    return render_template('post_job.html')

@app.route('/post_internship', methods=['GET', 'POST'])
def post_internship():
    if 'user_id' not in session or session.get('user_type') != 'admin':
        return redirect(url_for('login', next=request.path))
    
    if request.method == 'POST':
        try:
            # Check if admin is approved
            admin = Administrator.query.get(session['user_id'])
            if not admin or not admin.is_approved:
                return jsonify({"status": "error", "message": "Your account is not approved yet. Please contact the system administrator."})
            
            internship = Internship(
                title=request.form.get('title'),
                company=request.form.get('company'),
                location=request.form.get('location'),
                description=request.form.get('description'),
                requirements=request.form.get('requirements'),
                duration=request.form.get('duration'),
                stipend=request.form.get('stipend'),
                internship_type=request.form.get('internship_type'),
                posted_by=session['user_id'],
                is_approved=True,  # Auto-approve internships from approved admins
                status='approved'
            )
            db.session.add(internship)
            db.session.commit()
            return jsonify({"status": "success", "message": "Internship posted successfully!"})
        except Exception as e:
            db.session.rollback()
            return jsonify({"status": "error", "message": str(e)})
    
    return render_template('post_internship.html')

@app.route('/apply_job/<int:job_id>', methods=['POST'])
def apply_job(job_id):
    if 'user_id' not in session or session.get('user_type') != 'student':
        return jsonify({"error": "Authentication required"}), 401
    
    try:
        # Check if already applied
        existing_application = Application.query.filter_by(
            student_id=session['user_id'], 
            job_id=job_id
        ).first()
        
        if existing_application:
            return jsonify({"error": "You have already applied for this job"}), 400
        
        # Handle file upload
        resume_filename = None
        if 'resume' in request.files:
            file = request.files['resume']
            if file and file.filename != '' and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                # Add timestamp to make filename unique
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                resume_filename = f"{session['user_id']}_{timestamp}_{filename}"
                file.save(os.path.join(app.config['UPLOAD_FOLDER'], resume_filename))
        
        # Create application with all form data
        application = Application(
            student_id=session['user_id'],
            job_id=job_id,
            cover_letter=request.form.get('cover_letter', ''),
            resume_filename=resume_filename,
            phone_number=request.form.get('phone_number', ''),
            current_cgpa=request.form.get('current_cgpa', ''),
            skills=request.form.get('skills', ''),
            experience=request.form.get('experience', ''),
            projects=request.form.get('projects', ''),
            why_interested=request.form.get('why_interested', ''),
            availability=request.form.get('availability', '')
        )
        
        db.session.add(application)
        db.session.commit()
        
        return jsonify({"status": "success", "message": "Application submitted successfully!"})
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500

@app.route('/apply_internship/<int:internship_id>', methods=['POST'])
def apply_internship(internship_id):
    if 'user_id' not in session or session.get('user_type') != 'student':
        return jsonify({"error": "Authentication required"}), 401
    
    try:
        # Check if already applied
        existing_application = Application.query.filter_by(
            student_id=session['user_id'], 
            internship_id=internship_id
        ).first()
        
        if existing_application:
            return jsonify({"error": "You have already applied for this internship"}), 400
        
        # Handle file upload
        resume_filename = None
        if 'resume' in request.files:
            file = request.files['resume']
            if file and file.filename != '' and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                # Add timestamp to make filename unique
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                resume_filename = f"{session['user_id']}_{timestamp}_{filename}"
                file.save(os.path.join(app.config['UPLOAD_FOLDER'], resume_filename))
        
        # Create application with all form data
        application = Application(
            student_id=session['user_id'],
            internship_id=internship_id,
            cover_letter=request.form.get('cover_letter', ''),
            resume_filename=resume_filename,
            phone_number=request.form.get('phone_number', ''),
            current_cgpa=request.form.get('current_cgpa', ''),
            skills=request.form.get('skills', ''),
            experience=request.form.get('experience', ''),
            projects=request.form.get('projects', ''),
            why_interested=request.form.get('why_interested', ''),
            availability=request.form.get('availability', '')
        )
        
        db.session.add(application)
        db.session.commit()
        
        return jsonify({"status": "success", "message": "Application submitted successfully!"})
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500

@app.route('/my_applications')
def my_applications():
    if 'user_id' not in session or session.get('user_type') != 'student':
        return redirect(url_for('login', next=request.path))
    
    applications = Application.query.filter_by(student_id=session['user_id']).all()
    return render_template('my_applications.html', applications=applications)

@app.route('/manage_applications')
def manage_applications():
    if 'user_id' not in session or session.get('user_type') != 'admin':
        return redirect(url_for('login', next=request.path))
    
    # Get applications for jobs and internships posted by this admin
    job_applications = Application.query.join(Job).filter(
        Job.posted_by == session['user_id']
    ).all()
    
    internship_applications = Application.query.join(Internship).filter(
        Internship.posted_by == session['user_id']
    ).all()
    
    return render_template('manage_applications.html', 
                         job_applications=job_applications,
                         internship_applications=internship_applications)

@app.route('/application_form')
def application_form():
    if 'user_id' not in session or session.get('user_type') != 'student':
        return redirect(url_for('login', next=request.full_path))
    return render_template('application_form.html')

@app.route('/update_application_status/<int:application_id>', methods=['POST'])
def update_application_status(application_id):
    if 'user_id' not in session or session.get('user_type') != 'admin':
        return jsonify({"error": "Authentication required"}), 401
    
    try:
        application = Application.query.get_or_404(application_id)
        new_status = request.form.get('status')
        
        # Verify the job/internship belongs to this admin
        if application.job_id and application.job.posted_by != session['user_id']:
            return jsonify({"error": "Unauthorized"}), 403
        if application.internship_id and application.internship.posted_by != session['user_id']:
            return jsonify({"error": "Unauthorized"}), 403
        
        # Update status
        application.status = new_status
        db.session.commit()
        
        # Send email notification
        student = application.student
        if application.job_id:
            job = application.job
            job_details = f"""
Title: {job.title}
Company: {job.company}
Location: {job.location}
Description: {job.description}
Requirements: {job.requirements}
Salary Range: {job.salary_range}
Job Type: {job.job_type}
"""
            job_title = job.title
            company_name = job.company
        else:
            internship = application.internship
            job_details = f"""
Title: {internship.title}
Company: {internship.company}
Location: {internship.location}
Description: {internship.description}
Requirements: {internship.requirements}
Duration: {internship.duration}
Stipend: {internship.stipend}
Internship Type: {internship.internship_type}
"""
            job_title = internship.title
            company_name = internship.company
        
        student_name = f"{student.first_name} {student.last_name}"
        send_application_status_email(student.email, student_name, job_title, company_name, new_status, job_details)
        
        return jsonify({"status": "success", "message": "Application status updated and email sent!"})
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500

@app.route('/download_resume/<path:filename>')
def download_resume(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename, as_attachment=True)

@app.route('/api/check-auth', methods=['GET'])
def check_auth():
    """API endpoint to check if user is authenticated"""
    if 'user_id' in session:
        return jsonify({
            'authenticated': True,
            'user_id': session['user_id'],
            'user_type': session['user_type'],
            'user_email': session['user_email'],
            'user_name': session['user_name']
        })
    else:
        return jsonify({'authenticated': False}), 401

@app.route('/api/logout', methods=['POST'])
def api_logout():
    """API endpoint to logout user"""
    session.clear()
    return jsonify({'message': 'Logged out successfully'})

@app.route('/server_admin/login', methods=['GET', 'POST'])
def server_admin_login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        remember_me = request.form.get('remember_me') == 'true'
        
        if not username or not password:
            return "Login failed. Please provide username and password."
        
        try:
            admin = ServerAdmin.query.filter_by(username=username, is_active=True).first()
            if admin and admin.check_password(password):
                session['server_admin_id'] = admin.id
                session['server_admin_username'] = admin.username
                session['server_admin_role'] = admin.role
                session['user_type'] = 'server_admin'
                
                # Update last login
                admin.last_login = datetime.utcnow()
                db.session.commit()
                
                # Set session permanence based on "Remember Me"
                if remember_me:
                    session.permanent = True
                else:
                    session.permanent = False
                
                return redirect(url_for('server_admin_dashboard'))
            
            return "Login failed. Invalid username or password."
        except Exception as e:
            return f"Login failed. Error: {str(e)}"
    
    return render_template('server_admin_login.html')

@app.route('/server_admin/dashboard')
def server_admin_dashboard():
    if 'server_admin_id' not in session:
        return redirect(url_for('server_admin_login'))
    
    # Get statistics
    total_students = Student.query.count()
    total_admins = Administrator.query.count()
    pending_admins = Administrator.query.filter_by(status='pending').count()
    pending_jobs = Job.query.filter_by(status='pending').count()
    pending_internships = Internship.query.filter_by(status='pending').count()
    flagged_jobs = Job.query.filter_by(status='flagged').count()
    flagged_internships = Internship.query.filter_by(status='flagged').count()
    
    # Recent activities
    recent_admins = Administrator.query.order_by(Administrator.created_at.desc()).limit(5).all()
    recent_jobs = Job.query.order_by(Job.posted_at.desc()).limit(5).all()
    recent_internships = Internship.query.order_by(Internship.posted_at.desc()).limit(5).all()
    
    return render_template('server_admin_dashboard.html',
                         total_students=total_students,
                         total_admins=total_admins,
                         pending_admins=pending_admins,
                         pending_jobs=pending_jobs,
                         pending_internships=pending_internships,
                         flagged_jobs=flagged_jobs,
                         flagged_internships=flagged_internships,
                         recent_admins=recent_admins,
                         recent_jobs=recent_jobs,
                         recent_internships=recent_internships)

@app.route('/server_admin/admins')
def server_admin_manage_admins():
    if 'server_admin_id' not in session:
        return redirect(url_for('server_admin_login'))
    
    status_filter = request.args.get('status', 'all')
    if status_filter == 'all':
        admins = Administrator.query.order_by(Administrator.created_at.desc()).all()
    else:
        admins = Administrator.query.filter_by(status=status_filter).order_by(Administrator.created_at.desc()).all()
    
    return render_template('server_admin_manage_admins.html', admins=admins, status_filter=status_filter)

@app.route('/server_admin/admin/<int:admin_id>/approve', methods=['POST'])
def server_admin_approve_admin(admin_id):
    if 'server_admin_id' not in session:
        return jsonify({"error": "Unauthorized"}), 401
    
    try:
        admin = Administrator.query.get_or_404(admin_id)
        admin.status = 'approved'
        admin.is_approved = True
        admin.is_verified = True
        db.session.commit()
        
        return jsonify({"status": "success", "message": "Admin approved successfully"})
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500

@app.route('/server_admin/admin/<int:admin_id>/reject', methods=['POST'])
def server_admin_reject_admin(admin_id):
    if 'server_admin_id' not in session:
        return jsonify({"error": "Unauthorized"}), 401
    
    try:
        admin = Administrator.query.get_or_404(admin_id)
        admin.status = 'rejected'
        admin.is_approved = False
        db.session.commit()
        
        return jsonify({"status": "success", "message": "Admin rejected successfully"})
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500

@app.route('/server_admin/admin/<int:admin_id>/suspend', methods=['POST'])
def server_admin_suspend_admin(admin_id):
    if 'server_admin_id' not in session:
        return jsonify({"error": "Unauthorized"}), 401
    
    try:
        admin = Administrator.query.get_or_404(admin_id)
        admin.status = 'suspended'
        admin.is_approved = False
        db.session.commit()
        
        return jsonify({"status": "success", "message": "Admin suspended successfully"})
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500

@app.route('/server_admin/jobs')
def server_admin_manage_jobs():
    if 'server_admin_id' not in session:
        return redirect(url_for('server_admin_login'))
    
    status_filter = request.args.get('status', 'all')
    if status_filter == 'all':
        jobs = Job.query.order_by(Job.posted_at.desc()).all()
    else:
        jobs = Job.query.filter_by(status=status_filter).order_by(Job.posted_at.desc()).all()
    
    return render_template('server_admin_manage_jobs.html', jobs=jobs, status_filter=status_filter)

@app.route('/server_admin/internships')
def server_admin_manage_internships():
    if 'server_admin_id' not in session:
        return redirect(url_for('server_admin_login'))
    
    status_filter = request.args.get('status', 'all')
    if status_filter == 'all':
        internships = Internship.query.order_by(Internship.posted_at.desc()).all()
    else:
        internships = Internship.query.filter_by(status=status_filter).order_by(Internship.posted_at.desc()).all()
    
    return render_template('server_admin_manage_internships.html', internships=internships, status_filter=status_filter)

@app.route('/server_admin/job/<int:job_id>/approve', methods=['POST'])
def server_admin_approve_job(job_id):
    if 'server_admin_id' not in session:
        return jsonify({"error": "Unauthorized"}), 401
    
    try:
        job = Job.query.get_or_404(job_id)
        job.status = 'approved'
        job.is_approved = True
        job.reviewed_by = session['server_admin_id']
        job.reviewed_at = datetime.utcnow()
        db.session.commit()
        
        return jsonify({"status": "success", "message": "Job approved successfully"})
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500

@app.route('/server_admin/job/<int:job_id>/reject', methods=['POST'])
def server_admin_reject_job(job_id):
    if 'server_admin_id' not in session:
        return jsonify({"error": "Unauthorized"}), 401
    
    try:
        job = Job.query.get_or_404(job_id)
        job.status = 'rejected'
        job.is_approved = False
        job.reviewed_by = session['server_admin_id']
        job.reviewed_at = datetime.utcnow()
        db.session.commit()
        
        return jsonify({"status": "success", "message": "Job rejected successfully"})
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500

@app.route('/server_admin/job/<int:job_id>/flag', methods=['POST'])
def server_admin_flag_job(job_id):
    if 'server_admin_id' not in session:
        return jsonify({"error": "Unauthorized"}), 401
    
    try:
        job = Job.query.get_or_404(job_id)
        job.status = 'flagged'
        job.flagged_reason = request.form.get('reason', 'Suspicious content detected')
        job.reviewed_by = session['server_admin_id']
        job.reviewed_at = datetime.utcnow()
        db.session.commit()
        
        return jsonify({"status": "success", "message": "Job flagged successfully"})
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500

@app.route('/server_admin/internship/<int:internship_id>/approve', methods=['POST'])
def server_admin_approve_internship(internship_id):
    if 'server_admin_id' not in session:
        return jsonify({"error": "Unauthorized"}), 401
    
    try:
        internship = Internship.query.get_or_404(internship_id)
        internship.status = 'approved'
        internship.is_approved = True
        internship.reviewed_by = session['server_admin_id']
        internship.reviewed_at = datetime.utcnow()
        db.session.commit()
        
        return jsonify({"status": "success", "message": "Internship approved successfully"})
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500

@app.route('/server_admin/internship/<int:internship_id>/reject', methods=['POST'])
def server_admin_reject_internship(internship_id):
    if 'server_admin_id' not in session:
        return jsonify({"error": "Unauthorized"}), 401
    
    try:
        internship = Internship.query.get_or_404(internship_id)
        internship.status = 'rejected'
        internship.is_approved = False
        internship.reviewed_by = session['server_admin_id']
        internship.reviewed_at = datetime.utcnow()
        db.session.commit()
        
        return jsonify({"status": "success", "message": "Internship rejected successfully"})
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500

@app.route('/server_admin/internship/<int:internship_id>/flag', methods=['POST'])
def server_admin_flag_internship(internship_id):
    if 'server_admin_id' not in session:
        return jsonify({"error": "Unauthorized"}), 401
    
    try:
        internship = Internship.query.get_or_404(internship_id)
        internship.status = 'flagged'
        internship.flagged_reason = request.form.get('reason', 'Suspicious content detected')
        internship.reviewed_by = session['server_admin_id']
        internship.reviewed_at = datetime.utcnow()
        db.session.commit()
        
        return jsonify({"status": "success", "message": "Internship flagged successfully"})
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500

@app.route('/server_admin/logout')
def server_admin_logout():
    session.pop('server_admin_id', None)
    session.pop('server_admin_username', None)
    session.pop('server_admin_role', None)
    return redirect(url_for('server_admin_login'))

@app.route('/competitions')
def competitions():
    competitions = Competition.query.filter_by(is_active=True).order_by(Competition.posted_at.desc()).all()
    return render_template('competitions.html', competitions=competitions)

@app.route('/post_competition', methods=['GET', 'POST'])
def post_competition():
    if 'user_id' not in session or session.get('user_type') != 'admin':
        return redirect(url_for('login'))
    
    if request.method == 'POST':
        try:
            competition = Competition(
                title=request.form.get('title'),
                organizer=request.form.get('organizer'),
                description=request.form.get('description'),
                category=request.form.get('category'),
                prize_pool=request.form.get('prize_pool'),
                deadline=datetime.strptime(request.form.get('deadline'), '%Y-%m-%dT%H:%M'),
                start_date=datetime.strptime(request.form.get('start_date'), '%Y-%m-%dT%H:%M'),
                end_date=datetime.strptime(request.form.get('end_date'), '%Y-%m-%dT%H:%M'),
                max_participants=int(request.form.get('max_participants')) if request.form.get('max_participants') else None,
                eligibility=request.form.get('eligibility'),
                rules=request.form.get('rules'),
                posted_by=session['user_id']
            )
            db.session.add(competition)
            db.session.commit()
            return jsonify({'success': True, 'message': 'Competition posted successfully'})
        except Exception as e:
            return jsonify({'success': False, 'message': f'Error: {str(e)}'})
    
    return render_template('post_competition.html')

@app.route('/register_competition/<int:competition_id>', methods=['POST'])
def register_competition(competition_id):
    if 'user_id' not in session or session.get('user_type') != 'student':
        return jsonify({'success': False, 'message': 'Unauthorized'}), 401
    
    try:
        competition = Competition.query.get_or_404(competition_id)
        
        # Check if already registered
        existing_participation = CompetitionParticipant.query.filter_by(
            competition_id=competition_id,
            student_id=session['user_id']
        ).first()
        
        if existing_participation:
            return jsonify({'success': False, 'message': 'You are already registered for this competition'})
        
        # Check if competition is full
        if competition.max_participants and competition.current_participants >= competition.max_participants:
            return jsonify({'success': False, 'message': 'Competition is full'})
        
        # Check if deadline has passed
        if datetime.utcnow() > competition.deadline:
            return jsonify({'success': False, 'message': 'Registration deadline has passed'})
        
        # Register the student
        participation = CompetitionParticipant(
            competition_id=competition_id,
            student_id=session['user_id']
        )
        db.session.add(participation)
        
        # Update participant count
        competition.current_participants += 1
        
        db.session.commit()
        return jsonify({'success': True, 'message': 'Successfully registered for competition'})
        
    except Exception as e:
        return jsonify({'success': False, 'message': f'Error: {str(e)}'})

@app.route('/my_competitions')
def my_competitions():
    if 'user_id' not in session or session.get('user_type') != 'student':
        return redirect(url_for('login'))
    
    participations = CompetitionParticipant.query.filter_by(student_id=session['user_id']).all()
    return render_template('my_competitions.html', participations=participations)

@app.route('/manage_competitions')
def manage_competitions():
    if 'user_id' not in session or session.get('user_type') != 'admin':
        return redirect(url_for('login'))
    
    competitions = Competition.query.filter_by(posted_by=session['user_id']).all()
    return render_template('manage_competitions.html', competitions=competitions)

@app.route('/view_applicants')
def view_applicants_redirect():
    """Redirect old view_applicants route to manage_applications"""
    return redirect(url_for('manage_applications'))

@app.route('/api/application/<int:application_id>')
def get_application_details(application_id):
    if 'user_id' not in session or session.get('user_type') != 'admin':
        return jsonify({"error": "Unauthorized"}), 401
    
    try:
        application = Application.query.get_or_404(application_id)
        
        # Verify the job/internship belongs to this admin
        if application.job_id and application.job.posted_by != session['user_id']:
            return jsonify({"error": "Unauthorized"}), 403
        if application.internship_id and application.internship.posted_by != session['user_id']:
            return jsonify({"error": "Unauthorized"}), 403
        
        # Prepare application data
        app_data = {
            'id': application.id,
            'student_name': f"{application.student.first_name} {application.student.last_name}",
            'student_email': application.student.email,
            'student_college': application.student.college,
            'student_course': application.student.course,
            'applied_at': application.applied_at.strftime('%B %d, %Y at %I:%M %p'),
            'status': application.status,
            'cover_letter': application.cover_letter,
            'phone_number': application.phone_number,
            'current_cgpa': application.current_cgpa,
            'skills': application.skills,
            'experience': application.experience,
            'projects': application.projects,
            'why_interested': application.why_interested,
            'availability': application.availability,
            'resume_filename': application.resume_filename,
            'type': 'job' if application.job_id else 'internship'
        }
        
        if application.job_id:
            app_data['position'] = application.job.title
            app_data['company'] = application.job.company
        else:
            app_data['position'] = application.internship.title
            app_data['company'] = application.internship.company
        
        return jsonify(app_data)
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/forgot_password', methods=['GET', 'POST'])
def forgot_password():
    if request.method == 'POST':
        email = request.form.get('email')
        user_type = request.form.get('user_type', 'student')
        
        if not email:
            return jsonify({'success': False, 'message': 'Email is required'}), 400
        
        try:
            # Check if user exists
            if user_type == 'student':
                user = Student.query.filter_by(email=email).first()
            else:
                user = Administrator.query.filter_by(email=email).first()
            
            if not user:
                return jsonify({'success': False, 'message': 'No account found with this email address'}), 404
            
            # Generate OTP
            otp = ''.join(secrets.choice(string.digits) for _ in range(6))
            password_reset_otps[email] = {
                'otp': otp,
                'user_type': user_type,
                'user_id': user.id,
                'expires_at': datetime.utcnow() + timedelta(minutes=10)
            }
            
            # Send OTP email
            try:
                sender_email = "smarthire2k25@gmail.com"
                sender_password = "hwqd hzpv srus akig"
                
                subject = "SmartHire - Password Reset OTP"
                message = f"""
Subject: {subject}

Dear User,

You have requested to reset your password for your SmartHire account.

Your OTP (One-Time Password) is: {otp}

This OTP will expire in 10 minutes.

If you did not request this password reset, please ignore this email.

Best regards,
SmartHire Team
                """
                
                context = ssl.create_default_context()
                with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=context) as server:
                    server.login(sender_email, sender_password)
                    server.sendmail(sender_email, email, message)
                
                return jsonify({
                    'success': True, 
                    'message': 'OTP sent to your email address. Please check your inbox.'
                })
                
            except Exception as e:
                return jsonify({'success': False, 'message': f'Failed to send email: {str(e)}'}), 500
                
        except Exception as e:
            return jsonify({'success': False, 'message': f'Error: {str(e)}'}), 500
    
    return render_template('forgot_password.html')

@app.route('/verify_reset_otp', methods=['POST'])
def verify_reset_otp():
    email = request.form.get('email')
    otp = request.form.get('otp')
    
    if not email or not otp:
        return jsonify({'success': False, 'message': 'Email and OTP are required'}), 400
    
    # Check if OTP exists and is valid
    if email not in password_reset_otps:
        return jsonify({'success': False, 'message': 'Invalid or expired OTP'}), 400
    
    reset_data = password_reset_otps[email]
    
    # Check if OTP has expired
    if datetime.utcnow() > reset_data['expires_at']:
        del password_reset_otps[email]
        return jsonify({'success': False, 'message': 'OTP has expired. Please request a new one.'}), 400
    
    # Verify OTP
    if reset_data['otp'] != otp:
        return jsonify({'success': False, 'message': 'Invalid OTP'}), 400
    
    # Generate reset token
    reset_token = secrets.token_urlsafe(32)
    password_reset_tokens[reset_token] = {
        'email': email,
        'user_type': reset_data['user_type'],
        'user_id': reset_data['user_id'],
        'expires_at': datetime.utcnow() + timedelta(minutes=30)
    }
    
    # Remove OTP after successful verification
    del password_reset_otps[email]
    
    return jsonify({
        'success': True, 
        'message': 'OTP verified successfully',
        'reset_token': reset_token
    })

@app.route('/reset_password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    if request.method == 'POST':
        new_password = request.form.get('new_password')
        confirm_password = request.form.get('confirm_password')
        
        if not new_password or not confirm_password:
            return jsonify({'success': False, 'message': 'Both password fields are required'}), 400
        
        if new_password != confirm_password:
            return jsonify({'success': False, 'message': 'Passwords do not match'}), 400
        
        if len(new_password) < 6:
            return jsonify({'success': False, 'message': 'Password must be at least 6 characters long'}), 400
        
        # Verify reset token
        if token not in password_reset_tokens:
            return jsonify({'success': False, 'message': 'Invalid or expired reset token'}), 400
        
        reset_data = password_reset_tokens[token]
        
        # Check if token has expired
        if datetime.utcnow() > reset_data['expires_at']:
            del password_reset_tokens[token]
            return jsonify({'success': False, 'message': 'Reset token has expired. Please request a new password reset.'}), 400
        
        try:
            # Update password in database
            if reset_data['user_type'] == 'student':
                user = Student.query.get(reset_data['user_id'])
            else:
                user = Administrator.query.get(reset_data['user_id'])
            
            if not user:
                return jsonify({'success': False, 'message': 'User not found'}), 404
            
            user.set_password(new_password)
            db.session.commit()
            
            # Remove reset token after successful password change
            del password_reset_tokens[token]
            
            return jsonify({
                'success': True, 
                'message': 'Password updated successfully! You can now login with your new password.',
                'redirect': '/login'
            })
            
        except Exception as e:
            db.session.rollback()
            return jsonify({'success': False, 'message': f'Error updating password: {str(e)}'}), 500
    
    # GET request - show reset password form
    if token not in password_reset_tokens:
        return render_template('reset_password_expired.html')
    
    reset_data = password_reset_tokens[token]
    if datetime.utcnow() > reset_data['expires_at']:
        del password_reset_tokens[token]
        return render_template('reset_password_expired.html')
    
    return render_template('reset_password.html', token=token)

@app.route('/resume_builder')
def resume_builder():
    if 'user_id' not in session or session.get('user_type') != 'student':
        return redirect(url_for('login', next=request.path))
    return render_template('resume_builder.html')

@app.route('/resume_builder/template/<int:template_id>')
def resume_template(template_id):
    if 'user_id' not in session or session.get('user_type') != 'student':
        return redirect(url_for('login', next=request.path))
    
    # Map template IDs to actual template files
    template_mapping = {
        1: 'Resume1.html', 2: 'Resume2.html', 3: 'Resume3.html', 4: 'Resume4.html', 5: 'Resume5.html',
        6: 'Resume6.html', 7: 'Resume7.html', 8: 'Resume8.html', 9: 'Resume9.html', 10: 'Resume10.html',
        11: 'Resume11.html', 12: 'Resume12.html', 13: 'Resume13.html', 14: 'Resume14.html', 15: 'Resume15.html',
        16: 'Resume16.html', 17: 'Resume17.html', 18: 'Resume18.html', 19: 'Resume19.html', 20: 'Resume20.html',
        21: 'Resume21.html', 22: 'Resume22.html', 23: 'Resume23.html', 24: 'Resume24.html', 25: 'Resume25.html',
        26: 'Resume26.html', 27: 'Resume27.html', 28: 'Resume28.html', 29: 'Resume29.html', 30: 'Resume30.html',
        31: 'Resume31.html', 32: 'Resume32.html', 33: 'Resume33.html', 34: 'Resume34.html', 35: 'Resume35.html',
        36: 'Resume36.html', 37: 'Resume37.html', 38: 'Resume38.html', 39: 'Resume39.html', 40: 'Resume40.html',
        41: 'Resume41.html', 42: 'Resume42.html', 43: 'Resume43.html', 44: 'Resume44.html', 45: 'Resume45.html',
        46: 'Resume46.html', 47: 'Resume47.html', 48: 'Resume48.html', 49: 'Resume49.html', 50: 'Resume50.html'
    }
    
    if template_id not in template_mapping:
        return redirect(url_for('resume_builder'))
    
    template_file = template_mapping[template_id]
    return render_template(f'resume_templates/{template_file}')

@app.route('/api/save_resume', methods=['POST'])
def save_resume():
    if 'user_id' not in session or session.get('user_type') != 'student':
        return jsonify({"error": "Authentication required"}), 401
    
    try:
        data = request.json
        resume_data = {
            'student_id': session['user_id'],
            'template_id': data.get('template_id'),
            'resume_content': data.get('content'),
            'created_at': datetime.utcnow()
        }
        
        # Here you could save to database if you want to store user resumes
        # For now, we'll just return success
        return jsonify({"status": "success", "message": "Resume saved successfully!"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
