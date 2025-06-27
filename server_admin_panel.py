from flask import Flask, render_template, request, jsonify, redirect, url_for, session, flash
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, timedelta
import os
import json
import pandas as pd
from werkzeug.utils import secure_filename
import sqlite3

app = Flask(__name__, template_folder='server_templates')
app.secret_key = 'server_admin_secret_key_2025'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///smarthire.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['UPLOAD_FOLDER'] = 'server_uploads'

# Create uploads directory if it doesn't exist
if not os.path.exists(app.config['UPLOAD_FOLDER']):
    os.makedirs(app.config['UPLOAD_FOLDER'])

db = SQLAlchemy(app)

# Import models from main app
import sys
sys.path.append('.')
from app import Student, Administrator, ServerAdmin, Job, Internship, Application, Competition, CompetitionParticipant, ResumeAnalysis

# Server Admin Authentication
def require_server_admin(f):
    def decorated_function(*args, **kwargs):
        if 'server_admin_id' not in session:
            return redirect(url_for('server_login'))
        return f(*args, **kwargs)
    decorated_function.__name__ = f.__name__
    return decorated_function

@app.route('/')
def index():
    if 'server_admin_id' in session:
        return redirect(url_for('dashboard'))
    return redirect(url_for('server_login'))

@app.route('/login', methods=['GET', 'POST'])
def server_login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        admin = ServerAdmin.query.filter_by(username=username, is_active=True).first()
        if admin and admin.check_password(password):
            session['server_admin_id'] = admin.id
            session['server_admin_username'] = admin.username
            session['server_admin_role'] = admin.role
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid credentials', 'error')
    
    return render_template('server_login.html')

@app.route('/logout')
def server_logout():
    session.clear()
    return redirect(url_for('server_login'))

@app.route('/dashboard')
@require_server_admin
def dashboard():
    # Get statistics
    stats = {
        'total_students': Student.query.count(),
        'total_admins': Administrator.query.count(),
        'total_jobs': Job.query.count(),
        'total_internships': Internship.query.count(),
        'total_applications': Application.query.count(),
        'pending_admins': Administrator.query.filter_by(status='pending').count(),
        'pending_jobs': Job.query.filter_by(status='pending').count(),
        'pending_internships': Internship.query.filter_by(status='pending').count(),
        'active_jobs': Job.query.filter_by(is_active=True).count(),
        'active_internships': Internship.query.filter_by(is_active=True).count()
    }
    
    # Recent activities
    recent_students = Student.query.order_by(Student.created_at.desc()).limit(5).all()
    recent_admins = Administrator.query.order_by(Administrator.created_at.desc()).limit(5).all()
    recent_jobs = Job.query.order_by(Job.posted_at.desc()).limit(5).all()
    
    return render_template('server_dashboard.html', stats=stats, 
                         recent_students=recent_students,
                         recent_admins=recent_admins,
                         recent_jobs=recent_jobs)

# Database Management Routes
@app.route('/database/students')
@require_server_admin
def manage_students():
    students = Student.query.order_by(Student.created_at.desc()).all()
    return render_template('manage_students.html', students=students)

@app.route('/database/admins')
@require_server_admin
def manage_admins():
    admins = Administrator.query.order_by(Administrator.created_at.desc()).all()
    return render_template('manage_admins.html', admins=admins)

@app.route('/database/jobs')
@require_server_admin
def manage_jobs():
    jobs = Job.query.order_by(Job.posted_at.desc()).all()
    return render_template('manage_jobs.html', jobs=jobs)

@app.route('/database/internships')
@require_server_admin
def manage_internships():
    internships = Internship.query.order_by(Internship.posted_at.desc()).all()
    return render_template('manage_internships.html', internships=internships)

@app.route('/database/applications')
@require_server_admin
def manage_applications():
    applications = Application.query.order_by(Application.applied_at.desc()).all()
    return render_template('manage_applications.html', applications=applications)

# CRUD Operations for Students
@app.route('/api/students', methods=['GET', 'POST', 'PUT', 'DELETE'])
@require_server_admin
def api_students():
    if request.method == 'GET':
        students = Student.query.all()
        return jsonify([{
            'id': s.id,
            'first_name': s.first_name,
            'last_name': s.last_name,
            'email': s.email,
            'college': s.college,
            'course': s.course,
            'graduation_year': s.graduation_year,
            'current_year': s.current_year,
            'roll_number': s.roll_number,
            'is_verified': s.is_verified,
            'created_at': s.created_at.strftime('%Y-%m-%d %H:%M:%S')
        } for s in students])
    
    elif request.method == 'POST':
        data = request.json
        try:
            student = Student(
                first_name=data['first_name'],
                last_name=data['last_name'],
                email=data['email'],
                date_of_birth=datetime.strptime(data['date_of_birth'], '%Y-%m-%d').date(),
                college=data['college'],
                course=data['course'],
                graduation_year=data['graduation_year'],
                current_year=data['current_year'],
                roll_number=data['roll_number'],
                is_verified=data.get('is_verified', True)
            )
            student.set_password(data['password'])
            db.session.add(student)
            db.session.commit()
            return jsonify({'success': True, 'message': 'Student created successfully'})
        except Exception as e:
            db.session.rollback()
            return jsonify({'success': False, 'message': str(e)})
    
    elif request.method == 'PUT':
        data = request.json
        try:
            student = Student.query.get(data['id'])
            if student:
                student.first_name = data['first_name']
                student.last_name = data['last_name']
                student.email = data['email']
                student.college = data['college']
                student.course = data['course']
                student.graduation_year = data['graduation_year']
                student.current_year = data['current_year']
                student.roll_number = data['roll_number']
                student.is_verified = data.get('is_verified', True)
                if data.get('password'):
                    student.set_password(data['password'])
                db.session.commit()
                return jsonify({'success': True, 'message': 'Student updated successfully'})
            return jsonify({'success': False, 'message': 'Student not found'})
        except Exception as e:
            db.session.rollback()
            return jsonify({'success': False, 'message': str(e)})
    
    elif request.method == 'DELETE':
        student_id = request.args.get('id')
        try:
            student = Student.query.get(student_id)
            if student:
                db.session.delete(student)
                db.session.commit()
                return jsonify({'success': True, 'message': 'Student deleted successfully'})
            return jsonify({'success': False, 'message': 'Student not found'})
        except Exception as e:
            db.session.rollback()
            return jsonify({'success': False, 'message': str(e)})

# CRUD Operations for Admins
@app.route('/api/admins', methods=['GET', 'POST', 'PUT', 'DELETE'])
@require_server_admin
def api_admins():
    if request.method == 'GET':
        admins = Administrator.query.all()
        return jsonify([{
            'id': a.id,
            'full_name': a.full_name,
            'email': a.email,
            'organization': a.organization,
            'designation': a.designation,
            'org_website': a.org_website,
            'purpose': a.purpose,
            'admin_code': a.admin_code,
            'is_verified': a.is_verified,
            'is_approved': a.is_approved,
            'status': a.status,
            'created_at': a.created_at.strftime('%Y-%m-%d %H:%M:%S')
        } for a in admins])
    
    elif request.method == 'POST':
        data = request.json
        try:
            admin = Administrator(
                full_name=data['full_name'],
                email=data['email'],
                organization=data['organization'],
                designation=data['designation'],
                org_website=data.get('org_website', ''),
                purpose=data['purpose'],
                admin_code=data.get('admin_code', ''),
                is_verified=data.get('is_verified', True),
                is_approved=data.get('is_approved', True),
                status=data.get('status', 'approved')
            )
            admin.set_password(data['password'])
            db.session.add(admin)
            db.session.commit()
            return jsonify({'success': True, 'message': 'Admin created successfully'})
        except Exception as e:
            db.session.rollback()
            return jsonify({'success': False, 'message': str(e)})
    
    elif request.method == 'PUT':
        data = request.json
        try:
            admin = Administrator.query.get(data['id'])
            if admin:
                admin.full_name = data['full_name']
                admin.email = data['email']
                admin.organization = data['organization']
                admin.designation = data['designation']
                admin.org_website = data.get('org_website', '')
                admin.purpose = data['purpose']
                admin.admin_code = data.get('admin_code', '')
                admin.is_verified = data.get('is_verified', True)
                admin.is_approved = data.get('is_approved', True)
                admin.status = data.get('status', 'approved')
                if data.get('password'):
                    admin.set_password(data['password'])
                db.session.commit()
                return jsonify({'success': True, 'message': 'Admin updated successfully'})
            return jsonify({'success': False, 'message': 'Admin not found'})
        except Exception as e:
            db.session.rollback()
            return jsonify({'success': False, 'message': str(e)})
    
    elif request.method == 'DELETE':
        admin_id = request.args.get('id')
        try:
            admin = Administrator.query.get(admin_id)
            if admin:
                db.session.delete(admin)
                db.session.commit()
                return jsonify({'success': True, 'message': 'Admin deleted successfully'})
            return jsonify({'success': False, 'message': 'Admin not found'})
        except Exception as e:
            db.session.rollback()
            return jsonify({'success': False, 'message': str(e)})

# CRUD Operations for Jobs
@app.route('/api/jobs', methods=['GET', 'POST', 'PUT', 'DELETE'])
@require_server_admin
def api_jobs():
    if request.method == 'GET':
        jobs = Job.query.all()
        return jsonify([{
            'id': j.id,
            'title': j.title,
            'company': j.company,
            'location': j.location,
            'description': j.description,
            'requirements': j.requirements,
            'salary_range': j.salary_range,
            'job_type': j.job_type,
            'posted_by': j.posted_by,
            'is_active': j.is_active,
            'is_approved': j.is_approved,
            'status': j.status,
            'posted_at': j.posted_at.strftime('%Y-%m-%d %H:%M:%S')
        } for j in jobs])
    
    elif request.method == 'POST':
        data = request.json
        try:
            job = Job(
                title=data['title'],
                company=data['company'],
                location=data['location'],
                description=data['description'],
                requirements=data.get('requirements', ''),
                salary_range=data.get('salary_range', ''),
                job_type=data['job_type'],
                posted_by=data['posted_by'],
                is_active=data.get('is_active', True),
                is_approved=data.get('is_approved', True),
                status=data.get('status', 'approved')
            )
            db.session.add(job)
            db.session.commit()
            return jsonify({'success': True, 'message': 'Job created successfully'})
        except Exception as e:
            db.session.rollback()
            return jsonify({'success': False, 'message': str(e)})
    
    elif request.method == 'PUT':
        data = request.json
        try:
            job = Job.query.get(data['id'])
            if job:
                job.title = data['title']
                job.company = data['company']
                job.location = data['location']
                job.description = data['description']
                job.requirements = data.get('requirements', '')
                job.salary_range = data.get('salary_range', '')
                job.job_type = data['job_type']
                job.is_active = data.get('is_active', True)
                job.is_approved = data.get('is_approved', True)
                job.status = data.get('status', 'approved')
                db.session.commit()
                return jsonify({'success': True, 'message': 'Job updated successfully'})
            return jsonify({'success': False, 'message': 'Job not found'})
        except Exception as e:
            db.session.rollback()
            return jsonify({'success': False, 'message': str(e)})
    
    elif request.method == 'DELETE':
        job_id = request.args.get('id')
        try:
            job = Job.query.get(job_id)
            if job:
                db.session.delete(job)
                db.session.commit()
                return jsonify({'success': True, 'message': 'Job deleted successfully'})
            return jsonify({'success': False, 'message': 'Job not found'})
        except Exception as e:
            db.session.rollback()
            return jsonify({'success': False, 'message': str(e)})

# Database Export/Import
@app.route('/export/database')
@require_server_admin
def export_database():
    try:
        # Export all tables to Excel
        with pd.ExcelWriter('database_export.xlsx', engine='openpyxl') as writer:
            # Students
            students_data = pd.read_sql_query('SELECT * FROM student', db.engine)
            students_data.to_excel(writer, sheet_name='Students', index=False)
            
            # Administrators
            admins_data = pd.read_sql_query('SELECT * FROM administrator', db.engine)
            admins_data.to_excel(writer, sheet_name='Administrators', index=False)
            
            # Jobs
            jobs_data = pd.read_sql_query('SELECT * FROM job', db.engine)
            jobs_data.to_excel(writer, sheet_name='Jobs', index=False)
            
            # Internships
            internships_data = pd.read_sql_query('SELECT * FROM internship', db.engine)
            internships_data.to_excel(writer, sheet_name='Internships', index=False)
            
            # Applications
            applications_data = pd.read_sql_query('SELECT * FROM application', db.engine)
            applications_data.to_excel(writer, sheet_name='Applications', index=False)
            
            # Competitions
            competitions_data = pd.read_sql_query('SELECT * FROM competition', db.engine)
            competitions_data.to_excel(writer, sheet_name='Competitions', index=False)
        
        return jsonify({'success': True, 'message': 'Database exported successfully to database_export.xlsx'})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})

@app.route('/backup/database')
@require_server_admin
def backup_database():
    try:
        import shutil
        from datetime import datetime
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        backup_filename = f'smarthire_backup_{timestamp}.db'
        
        shutil.copy2('instance/smarthire.db', f'backups/{backup_filename}')
        
        return jsonify({'success': True, 'message': f'Database backed up as {backup_filename}'})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})

# System Settings
@app.route('/settings')
@require_server_admin
def system_settings():
    return render_template('system_settings.html')

@app.route('/api/settings', methods=['GET', 'POST'])
@require_server_admin
def api_settings():
    if request.method == 'GET':
        # Return current system settings
        return jsonify({
            'maintenance_mode': False,
            'registration_enabled': True,
            'job_posting_enabled': True,
            'email_notifications': True
        })
    
    elif request.method == 'POST':
        # Update system settings
        data = request.json
        # Here you would save settings to a config file or database
        return jsonify({'success': True, 'message': 'Settings updated successfully'})

if __name__ == '__main__':
    # Create backups directory
    if not os.path.exists('backups'):
        os.makedirs('backups')
    
    app.run(debug=True, port=5001) 