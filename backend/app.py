from flask import Flask, request, jsonify, send_file, render_template_string, send_from_directory, after_this_request
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
import sqlalchemy as sa
from datetime import datetime, timedelta
import os
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
import pdfkit
from jinja2 import Template
import tempfile
import uuid
import pandas as pd
from werkzeug.utils import secure_filename
import json
from threading import Timer
import schedule
import time
from apscheduler.schedulers.background import BackgroundScheduler
import base64
import mimetypes

app = Flask(__name__, 
            static_folder='../frontend/build/static',
            static_url_path='/static')
# Configure CORS with specific settings for production
CORS(app, resources={r"/api/*": {"origins": "*"}}, supports_credentials=True)

# Add security headers for production
@app.after_request
def add_security_headers(response):
    # Only use HTTPS in production
    if os.environ.get('FLASK_ENV') != 'development':
        response.headers['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains'
    response.headers['X-Content-Type-Options'] = 'nosniff'
    response.headers['X-Frame-Options'] = 'SAMEORIGIN'
    response.headers['X-XSS-Protection'] = '1; mode=block'
    return response

# Route to serve the direct certificate test page
@app.route('/certificate-test')
def certificate_test():
    with open('../direct-certificate-test.html', 'r') as f:
        content = f.read()
    return content

# Route to test certificate text
@app.route('/certificate-text-test')
def certificate_text_test():
    return send_from_directory('static', 'certificate-text-test.html')

# Test endpoint to check if signatures are available
@app.route('/test_signatures')
def test_signatures():
    base_dir = os.getcwd()
    results = {"signatures_found": {}, "directories_checked": []}
    
    # Define signature files to check
    files_to_check = {
        "president_signature": ["president-signature.png", "president_signature.png"], 
        "chairman_signature": ["chairman-signature.png", "chairman_signature.png"],
        "mdcan_logo": ["mdcan-logo.png", "mdcan_logo.jpeg", "logo-mdcan.png"],
        "coalcity_logo": ["coalcity-logo.png", "coal_city_logo.png"]
    }
    
    # Define directories to check
    directories = [
        os.path.join(base_dir, 'static'),
        os.path.join(base_dir, 'public'),
        os.path.join(base_dir, 'frontend', 'public'),
        os.path.join(base_dir, 'backend', 'static'),
        os.path.join(base_dir)
    ]
    
    # Check each directory
    for directory in directories:
        if os.path.exists(directory):
            results["directories_checked"].append({"path": directory, "exists": True})
            
            # Check for each file in this directory
            for file_type, file_options in files_to_check.items():
                for file_option in file_options:
                    file_path = os.path.join(directory, file_option)
                    if os.path.exists(file_path):
                        if file_type not in results["signatures_found"]:
                            results["signatures_found"][file_type] = []
                        results["signatures_found"][file_type].append(file_path)
        else:
            results["directories_checked"].append({"path": directory, "exists": False})
    
    return jsonify(results)

# Endpoint to serve static assets with better debugging
@app.route('/serve_asset/<path:filename>')
def serve_asset(filename):
    try:
        # Log the requested file
        print(f"Requested asset: {filename}")
        
        # Define possible directories to look for the file
        base_dir = os.getcwd()
        print(f"Current working directory: {base_dir}")
        
        possible_directories = [
            os.path.join(base_dir, 'static'),
            os.path.join(base_dir, 'public'),
            os.path.join(base_dir, 'frontend', 'public'),
            os.path.join(base_dir, 'backend', 'static'),
            os.path.join(base_dir)
        ]
        
        # For specific file types, use known correct files if available
        file_basename = os.path.basename(filename).lower()
        if file_basename in ['president-signature.png', 'president_signature.png']:
            static_path = os.path.join(base_dir, 'backend', 'static', 'president-signature.png')
            public_path = os.path.join(base_dir, 'frontend', 'public', 'president-signature-placeholder.jpg')
            
            if os.path.exists(static_path):
                print(f"Found exact signature in static: {static_path}")
                file_path = static_path
                mime_type = 'image/png'
                response = send_file(file_path, mimetype=mime_type)
                response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
                response.headers['Pragma'] = 'no-cache'
                response.headers['Expires'] = '0'
                return response
            elif os.path.exists(public_path):
                print(f"Using president placeholder: {public_path}")
                file_path = public_path
                mime_type = 'image/jpeg'
                response = send_file(file_path, mimetype=mime_type)
                response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
                response.headers['Pragma'] = 'no-cache'
                response.headers['Expires'] = '0'
                return response
        
        elif file_basename in ['chairman-signature.png', 'chairman_signature.png']:
            static_path = os.path.join(base_dir, 'backend', 'static', 'chairman-signature.png')
            public_path = os.path.join(base_dir, 'frontend', 'public', 'chairman-signature-placeholder.png')
            
            if os.path.exists(static_path):
                print(f"Found exact signature in static: {static_path}")
                file_path = static_path
                mime_type = 'image/png'
                response = send_file(file_path, mimetype=mime_type)
                response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
                response.headers['Pragma'] = 'no-cache'
                response.headers['Expires'] = '0'
                return response
            elif os.path.exists(public_path):
                print(f"Using chairman placeholder: {public_path}")
                file_path = public_path
                mime_type = 'image/png'
                response = send_file(file_path, mimetype=mime_type)
                response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
                response.headers['Pragma'] = 'no-cache'
                response.headers['Expires'] = '0'
                return response
                
        elif file_basename in ['mdcan-logo.png', 'mdcan_logo.jpeg', 'mdcan_logo.png']:
            static_path = os.path.join(base_dir, 'backend', 'static', 'mdcan-logo.png')
            public_path = os.path.join(base_dir, 'frontend', 'public', 'logo-mdcan.jpeg')
            
            if os.path.exists(static_path):
                print(f"Found exact logo in static: {static_path}")
                file_path = static_path
                mime_type = 'image/png'
                response = send_file(file_path, mimetype=mime_type)
                response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
                response.headers['Pragma'] = 'no-cache'
                response.headers['Expires'] = '0'
                return response
            elif os.path.exists(public_path):
                print(f"Using logo from public: {public_path}")
                file_path = public_path
                mime_type = 'image/jpeg'
                response = send_file(file_path, mimetype=mime_type)
                response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
                response.headers['Pragma'] = 'no-cache'
                response.headers['Expires'] = '0'
                return response
                
        elif file_basename in ['coalcity-logo.png', 'coal_city_logo.png']:
            static_path = os.path.join(base_dir, 'backend', 'static', 'coalcity-logo.png')
            public_path = os.path.join(base_dir, 'frontend', 'public', 'coal_city_logo.png')
            
            if os.path.exists(static_path):
                print(f"Found exact logo in static: {static_path}")
                file_path = static_path
                mime_type = 'image/png'
                response = send_file(file_path, mimetype=mime_type)
                response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
                response.headers['Pragma'] = 'no-cache'
                response.headers['Expires'] = '0'
                return response
            elif os.path.exists(public_path):
                print(f"Using logo from public: {public_path}")
                file_path = public_path
                mime_type = 'image/png'
                response = send_file(file_path, mimetype=mime_type)
                response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
                response.headers['Pragma'] = 'no-cache'
                response.headers['Expires'] = '0'
                return response
        
        # Standard file search across directories
        for directory in possible_directories:
            file_path = os.path.join(directory, filename)
            if os.path.exists(file_path):
                print(f"Serving asset from: {file_path}")
                
                # Get the MIME type for proper response
                mime_type, _ = mimetypes.guess_type(file_path)
                if mime_type is None:
                    mime_type = 'application/octet-stream'
                
                print(f"File MIME type: {mime_type}")
                
                # Set proper cache control to prevent caching issues
                response = send_file(file_path, mimetype=mime_type)
                response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
                response.headers['Pragma'] = 'no-cache'
                response.headers['Expires'] = '0'
                return response
        
        # Try common variations of the filename if not found directly
        name, ext = os.path.splitext(filename)
        variations = [
            filename,
            name.lower() + ext.lower(),
            name.replace('-', '_') + ext,
            name.replace('_', '-') + ext
        ]
        
        # Check all variations
        for variation in variations:
            if variation == filename:
                continue  # Skip the original filename as we already checked it
                
            for directory in possible_directories:
                file_path = os.path.join(directory, variation)
                if os.path.exists(file_path):
                    print(f"Serving asset (variation) from: {file_path}")
                    
                    # Get the MIME type for proper response
                    mime_type, _ = mimetypes.guess_type(file_path)
                    if mime_type is None:
                        mime_type = 'application/octet-stream'
                    
                    print(f"File MIME type: {mime_type}")
                    
                    # Set proper cache control to prevent caching issues
                    response = send_file(file_path, mimetype=mime_type)
                    response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
                    response.headers['Pragma'] = 'no-cache'
                    response.headers['Expires'] = '0'
                    return response
        
        # If file not found, serve a default image based on the requested file type
        if 'signature' in filename.lower():
            # Serve a default signature image
            print(f"Serving default signature for: {filename}")
            response = jsonify({
                "error": "Signature file not found",
                "requested": filename,
                "message": "The requested signature image was not found. Using a placeholder instead."
            })
            return response, 404
        elif 'logo' in filename.lower():
            # Serve a default logo image
            print(f"Serving default logo for: {filename}")
            response = jsonify({
                "error": "Logo file not found",
                "requested": filename,
                "message": "The requested logo image was not found. Using a placeholder instead."
            })
            return response, 404
        else:
            # Default case for unknown file types
            print(f"Asset not found: {filename}")
            return "File not found", 404
    
    except Exception as e:
        print(f"Error serving asset: {str(e)}")
        return str(e), 500

# Initialize scheduler for program notifications
scheduler = BackgroundScheduler()
scheduler.start()

# Database configuration
# PostgreSQL configuration
DATABASE_URL = os.environ.get('DATABASE_URL', 'postgresql://postgres:natiss_natiss@localhost/mdcan042_db')
if DATABASE_URL.startswith('postgres://'):
    DATABASE_URL = DATABASE_URL.replace('postgres://', 'postgresql://', 1)

app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE_URL
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Development SQLite fallback (comment out for production)
# app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///mdcan_certificates.db'
# app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Email configuration
EMAIL_HOST = os.environ.get('EMAIL_HOST', 'smtp.gmail.com')
EMAIL_PORT = int(os.environ.get('EMAIL_PORT', 587))
EMAIL_USER = os.environ.get('EMAIL_USER', 'sylvia4douglas@gmail.com')
EMAIL_PASSWORD = os.environ.get('EMAIL_PASSWORD', 'your-app-password')
EMAIL_FROM = os.environ.get('EMAIL_FROM', 'MDCAN BDM 2025 <sylvia4douglas@gmail.com>')

# File upload configuration
UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'uploads')
BROCHURE_FOLDER = os.path.join(UPLOAD_FOLDER, 'brochures')
MEDIA_FOLDER = os.path.join(UPLOAD_FOLDER, 'media')
ANNOUNCEMENT_FOLDER = os.path.join(UPLOAD_FOLDER, 'announcements')
PAYMENT_PROOF_FOLDER = os.path.join(UPLOAD_FOLDER, 'payment_proofs')

# Create upload directories if they don't exist
for folder in [UPLOAD_FOLDER, BROCHURE_FOLDER, MEDIA_FOLDER, ANNOUNCEMENT_FOLDER, PAYMENT_PROOF_FOLDER]:
    os.makedirs(folder, exist_ok=True)

# Allowed file extensions
ALLOWED_BROCHURE_EXTENSIONS = {'pdf', 'docx', 'doc'}
ALLOWED_MEDIA_EXTENSIONS = {'jpg', 'jpeg', 'png', 'gif', 'mp4', 'avi', 'mov'}
MAX_CONTENT_LENGTH = 50 * 1024 * 1024  # 50MB max upload size

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = MAX_CONTENT_LENGTH

db = SQLAlchemy(app)

class Participant(db.Model):
    __tablename__ = 'participants'
    
    # Primary key
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    
    # Personal information (required)
    name = db.Column(db.String(150), nullable=False, index=True)
    email = db.Column(db.String(150), nullable=False, unique=True, index=True)
    
    # Professional information (optional)
    organization = db.Column(db.String(250))
    position = db.Column(db.String(150))
    phone_number = db.Column(db.String(20))
    
    # Registration information
    registration_type = db.Column(db.String(50), nullable=False, default='participant', index=True)  # participant, speaker, organizer, sponsor
    registration_status = db.Column(db.String(20), nullable=False, default='registered', index=True)  # registered, confirmed, attended, cancelled
    registration_fee_paid = db.Column(db.Boolean, default=False)
    payment_reference = db.Column(db.String(100))
    
    # Additional registration fields
    dietary_requirements = db.Column(db.Text)
    special_needs = db.Column(db.Text)
    emergency_contact_name = db.Column(db.String(150))
    emergency_contact_phone = db.Column(db.String(20))
    
    # Notification preferences
    email_notifications = db.Column(db.Boolean, default=True)
    sms_notifications = db.Column(db.Boolean, default=False)
    push_notifications = db.Column(db.Boolean, default=True)
    push_subscription = db.Column(db.Text)  # Web push subscription data
    
    # Certificate information
    certificate_type = db.Column(db.String(30), nullable=False, default='participation', index=True)
    certificate_status = db.Column(db.String(20), nullable=False, default='pending', index=True)
    certificate_number = db.Column(db.String(50), unique=True)
    certificate_sent_at = db.Column(db.DateTime)
    
    # Metadata
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow, index=True)
    updated_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
    created_by = db.Column(db.String(100), default='system')
    
    # Additional fields for tracking
    registration_source = db.Column(db.String(50), default='manual')  # manual, bulk_upload, api, online
    event_attendance = db.Column(db.Boolean, default=True)
    special_recognition = db.Column(db.Text)
    first_attendance_date = db.Column(db.DateTime)
    last_attendance_date = db.Column(db.DateTime)
    materials_provided = db.Column(db.Boolean, default=False)
    materials_provided_date = db.Column(db.DateTime)
    materials_provided_by = db.Column(db.String(100))
    
    # Relationships
    session_registrations = db.relationship('SessionRegistration', backref='participant', lazy=True)
    
    # Constraints
    __table_args__ = (
        db.CheckConstraint(certificate_type.in_(['participation', 'service']), name='valid_certificate_type'),
        db.CheckConstraint(certificate_status.in_(['pending', 'sent', 'failed', 'resent']), name='valid_certificate_status'),
        db.CheckConstraint(registration_type.in_(['participant', 'speaker', 'organizer', 'sponsor', 'volunteer']), name='valid_registration_type'),
        db.CheckConstraint(registration_status.in_(['registered', 'confirmed', 'attended', 'cancelled']), name='valid_registration_status'),
        db.Index('idx_email_status', 'email', 'certificate_status'),
        db.Index('idx_created_type', 'created_at', 'certificate_type'),
        db.Index('idx_registration_type_status', 'registration_type', 'registration_status'),
    )

    def __init__(self, **kwargs):
        super(Participant, self).__init__(**kwargs)
        if not self.certificate_number:
            self.certificate_number = self.generate_certificate_number()

    def generate_certificate_number(self):
        """Generate unique certificate number"""
        from datetime import datetime
        timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
        import random
        random_suffix = random.randint(1000, 9999)
        return f"MDCAN-BDM-2025-{timestamp}-{random_suffix}"

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'email': self.email,
            'organization': self.organization,
            'position': self.position,
            'phone_number': self.phone_number,
            'registration_type': self.registration_type,
            'registration_status': self.registration_status,
            'registration_fee_paid': self.registration_fee_paid,
            'payment_reference': self.payment_reference,
            'dietary_requirements': self.dietary_requirements,
            'special_needs': self.special_needs,
            'emergency_contact_name': self.emergency_contact_name,
            'emergency_contact_phone': self.emergency_contact_phone,
            'email_notifications': self.email_notifications,
            'sms_notifications': self.sms_notifications,
            'push_notifications': self.push_notifications,
            'push_subscription': self.push_subscription,
            'certificate_type': self.certificate_type,
            'certificate_status': self.certificate_status,
            'certificate_number': self.certificate_number,
            'certificate_sent_at': self.certificate_sent_at.isoformat() if self.certificate_sent_at else None,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat(),
            'registration_source': self.registration_source,
            'event_attendance': self.event_attendance,
            'special_recognition': self.special_recognition,
            'first_attendance_date': self.first_attendance_date.isoformat() if self.first_attendance_date else None,
            'last_attendance_date': self.last_attendance_date.isoformat() if self.last_attendance_date else None,
            'materials_provided': self.materials_provided,
            'materials_provided_date': self.materials_provided_date.isoformat() if self.materials_provided_date else None,
            'materials_provided_by': self.materials_provided_by
        }

    def __repr__(self):
        return f'<Participant {self.name} ({self.email})>'


class ConferenceProgram(db.Model):
    __tablename__ = 'conference_programs'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    title = db.Column(db.String(250), nullable=False, index=True)
    description = db.Column(db.Text)
    program_type = db.Column(db.String(50), nullable=False, index=True)  # session, workshop, keynote, break, social
    
    # Scheduling
    start_time = db.Column(db.DateTime, nullable=False, index=True)
    end_time = db.Column(db.DateTime, nullable=False, index=True)
    venue = db.Column(db.String(200))
    capacity = db.Column(db.Integer)
    
    # Content details
    speaker_name = db.Column(db.String(150))
    speaker_bio = db.Column(db.Text)
    speaker_photo_url = db.Column(db.String(500))
    
    # Program status
    status = db.Column(db.String(20), nullable=False, default='scheduled', index=True)  # scheduled, ongoing, completed, cancelled
    is_mandatory = db.Column(db.Boolean, default=False)
    requires_registration = db.Column(db.Boolean, default=False)
    
    # Notification settings
    notification_sent = db.Column(db.Boolean, default=False)
    reminder_minutes = db.Column(db.Integer, default=30)  # Minutes before start to send reminder
    
    # Metadata
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
    created_by = db.Column(db.String(100), default='admin')
    
    # Relationships
    sessions = db.relationship('SessionRegistration', backref='program', lazy=True)
    
    # Constraints
    __table_args__ = (
        db.CheckConstraint(program_type.in_(['session', 'workshop', 'keynote', 'break', 'social', 'networking']), name='valid_program_type'),
        db.CheckConstraint(status.in_(['scheduled', 'ongoing', 'completed', 'cancelled']), name='valid_program_status'),
        db.Index('idx_start_time_type', 'start_time', 'program_type'),
        db.Index('idx_status_mandatory', 'status', 'is_mandatory'),
    )
    
    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'description': self.description,
            'program_type': self.program_type,
            'start_time': self.start_time.isoformat(),
            'end_time': self.end_time.isoformat(),
            'venue': self.venue,
            'capacity': self.capacity,
            'speaker_name': self.speaker_name,
            'speaker_bio': self.speaker_bio,
            'speaker_photo_url': self.speaker_photo_url,
            'status': self.status,
            'is_mandatory': self.is_mandatory,
            'requires_registration': self.requires_registration,
            'notification_sent': self.notification_sent,
            'reminder_minutes': self.reminder_minutes,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat(),
            'registration_count': len(self.sessions) if self.sessions else 0
        }

    def __repr__(self):
        return f'<ConferenceProgram {self.title}>'


class SessionRegistration(db.Model):
    __tablename__ = 'session_registrations'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    participant_id = db.Column(db.Integer, db.ForeignKey('participants.id'), nullable=False, index=True)
    program_id = db.Column(db.Integer, db.ForeignKey('conference_programs.id'), nullable=False, index=True)
    
    # Registration details
    registered_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    attendance_status = db.Column(db.String(20), default='registered', index=True)  # registered, attended, absent, cancelled
    
    # Feedback (post-session)
    rating = db.Column(db.Integer)  # 1-5 rating
    feedback = db.Column(db.Text)
    
    # Constraints
    __table_args__ = (
        db.UniqueConstraint('participant_id', 'program_id', name='unique_participant_program'),
        db.CheckConstraint(attendance_status.in_(['registered', 'attended', 'absent', 'cancelled']), name='valid_attendance_status'),
        db.CheckConstraint(rating.between(1, 5), name='valid_rating'),
    )
    
    def to_dict(self):
        return {
            'id': self.id,
            'participant_id': self.participant_id,
            'program_id': self.program_id,
            'registered_at': self.registered_at.isoformat(),
            'attendance_status': self.attendance_status,
            'rating': self.rating,
            'feedback': self.feedback,
            'participant_name': self.participant.name if self.participant else None,
            'program_title': self.program.title if self.program else None
        }


class Notification(db.Model):
    __tablename__ = 'notifications'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    
    # Notification content
    title = db.Column(db.String(200), nullable=False)
    message = db.Column(db.Text, nullable=False)
    notification_type = db.Column(db.String(50), nullable=False, index=True)  # program_reminder, general_announcement, emergency, welcome
    
    # Targeting
    target_audience = db.Column(db.String(50), default='all')  # all, participants, speakers, organizers, specific_program
    target_program_id = db.Column(db.Integer, db.ForeignKey('conference_programs.id'), nullable=True)
    
    # Scheduling
    scheduled_time = db.Column(db.DateTime, nullable=False, index=True)
    sent_at = db.Column(db.DateTime)
    
    # Delivery channels
    send_email = db.Column(db.Boolean, default=True)
    send_push = db.Column(db.Boolean, default=True)
    send_sms = db.Column(db.Boolean, default=False)
    
    # Status
    status = db.Column(db.String(20), default='scheduled', index=True)  # scheduled, sent, failed, cancelled
    delivery_stats = db.Column(db.Text)  # JSON with delivery statistics
    
    # Metadata
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    created_by = db.Column(db.String(100), default='admin')
    
    # Relationships
    target_program = db.relationship('ConferenceProgram', backref='notifications')
    
    # Constraints
    __table_args__ = (
        db.CheckConstraint(notification_type.in_(['program_reminder', 'general_announcement', 'emergency', 'welcome', 'certificate_ready']), name='valid_notification_type'),
        db.CheckConstraint(target_audience.in_(['all', 'participants', 'speakers', 'organizers', 'specific_program']), name='valid_target_audience'),
        db.CheckConstraint(status.in_(['scheduled', 'sent', 'failed', 'cancelled']), name='valid_notification_status'),
    )
    
    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'message': self.message,
            'notification_type': self.notification_type,
            'target_audience': self.target_audience,
            'target_program_id': self.target_program_id,
            'scheduled_time': self.scheduled_time.isoformat(),
            'sent_at': self.sent_at.isoformat() if self.sent_at else None,
            'send_email': self.send_email,
            'send_push': self.send_push,
            'send_sms': self.send_sms,
            'status': self.status,
            'delivery_stats': json.loads(self.delivery_stats) if self.delivery_stats else {},
            'created_at': self.created_at.isoformat(),
            'program_title': self.target_program.title if self.target_program else None
        }


class CertificateLog(db.Model):
    __tablename__ = 'certificate_logs'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    participant_id = db.Column(db.Integer, db.ForeignKey('participants.id'), nullable=False, index=True)
    action = db.Column(db.String(50), nullable=False)  # sent, failed, resent, downloaded
    status = db.Column(db.String(20), nullable=False)  # success, failed
    error_message = db.Column(db.Text)
    email_subject = db.Column(db.String(200))
    email_body_preview = db.Column(db.Text)
    timestamp = db.Column(db.DateTime, nullable=False, default=datetime.utcnow, index=True)
    ip_address = db.Column(db.String(45))
    user_agent = db.Column(db.String(500))
    
    # Relationship
    participant = db.relationship('Participant', backref=db.backref('certificate_logs', lazy=True))
    
    def to_dict(self):
        return {
            'id': self.id,
            'participant_id': self.participant_id,
            'action': self.action,
            'status': self.status,
            'error_message': self.error_message,
            'timestamp': self.timestamp.isoformat(),
            'participant_name': self.participant.name if self.participant else None
        }


class SystemSettings(db.Model):
    __tablename__ = 'system_settings'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    key = db.Column(db.String(100), nullable=False, unique=True, index=True)
    value = db.Column(db.Text)
    description = db.Column(db.String(500))
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    @staticmethod
    def get_setting(key, default_value=None):
        setting = SystemSettings.query.filter_by(key=key).first()
        return setting.value if setting else default_value
    
    @staticmethod
    def set_setting(key, value, description=None):
        setting = SystemSettings.query.filter_by(key=key).first()
        
        
class ConferenceMaterial(db.Model):
    __tablename__ = 'conference_materials'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    material_type = db.Column(db.String(50), nullable=False, index=True)  # brochure, video, image, other
    file_path = db.Column(db.String(500), nullable=False)
    file_size = db.Column(db.Integer)  # in bytes
    file_extension = db.Column(db.String(10))
    is_published = db.Column(db.Boolean, default=True)
    download_count = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    created_by = db.Column(db.String(100), default='admin')
    
    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'description': self.description,
            'material_type': self.material_type,
            'file_path': self.file_path,
            'file_size': self.file_size,
            'file_extension': self.file_extension,
            'is_published': self.is_published,
            'download_count': self.download_count,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'created_by': self.created_by,
            'download_url': f'/api/materials/{self.id}/download'
        }


class Announcement(db.Model):
    __tablename__ = 'announcements'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    title = db.Column(db.String(200), nullable=False)
    content = db.Column(db.Text, nullable=False)
    priority = db.Column(db.String(20), default='normal')  # high, normal, low
    attachment_path = db.Column(db.String(500))
    is_published = db.Column(db.Boolean, default=True)
    view_count = db.Column(db.Integer, default=0)
    notify_participants = db.Column(db.Boolean, default=True)
    notification_sent = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    published_at = db.Column(db.DateTime)
    created_by = db.Column(db.String(100), default='admin')
    
    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'content': self.content,
            'priority': self.priority,
            'has_attachment': bool(self.attachment_path),
            'is_published': self.is_published,
            'view_count': self.view_count,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'published_at': self.published_at.isoformat() if self.published_at else None,
            'created_by': self.created_by,
            'attachment_url': f'/api/announcements/{self.id}/attachment' if self.attachment_path else None
        }


class CheckIn(db.Model):
    __tablename__ = 'check_ins'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    participant_id = db.Column(db.Integer, db.ForeignKey('participants.id'), nullable=False, index=True)
    check_in_time = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    check_in_day = db.Column(db.Integer, nullable=False)  # 1-6 for conference days
    materials_received = db.Column(db.Boolean, default=False)
    verified_by = db.Column(db.String(100))
    verification_method = db.Column(db.String(50), default='manual')  # manual, qr, id
    notes = db.Column(db.Text)
    ip_address = db.Column(db.String(45))
    
    # Relationship
    participant = db.relationship('Participant', backref=db.backref('check_ins', lazy=True))
    
    # Constraints
    __table_args__ = (
        db.UniqueConstraint('participant_id', 'check_in_day', name='unique_participant_day_check_in'),
        db.CheckConstraint(check_in_day.between(1, 6), name='valid_conference_day'),
    )
    
    def to_dict(self):
        return {
            'id': self.id,
            'participant_id': self.participant_id,
            'participant_name': self.participant.name if self.participant else None,
            'participant_email': self.participant.email if self.participant else None,
            'check_in_time': self.check_in_time.isoformat() if self.check_in_time else None,
            'check_in_day': self.check_in_day,
            'materials_received': self.materials_received,
            'verified_by': self.verified_by,
            'verification_method': self.verification_method,
            'notes': self.notes
        }
        if setting:
            setting.value = value
            setting.updated_at = datetime.utcnow()
        else:
            setting = SystemSettings(key=key, value=value, description=description)
            db.session.add(setting)
        db.session.commit()
        return setting

# Certificate HTML template
CERTIFICATE_HTML = """
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <style>
        @page {
            size: A4 landscape;
            margin: 0.3in;
        }
        body {
            font-family: 'Times New Roman', serif;
            margin: 0;
            padding: 0;
            background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
        }
        .certificate-container {
            position: relative;
            border: 8px solid #d4af37;
            border-image: linear-gradient(45deg, #d4af37, #ffd700, #b8860b) 1;
            padding: 50px 40px;
            min-height: 480px;
            background: white url('/certificate_background.png') center/cover no-repeat,
                        linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
            background-blend-mode: overlay;
            background-image: 
                url('/certificate_background.png'),
                radial-gradient(circle at 20% 20%, rgba(212, 175, 55, 0.05) 0%, transparent 50%),
                radial-gradient(circle at 80% 80%, rgba(212, 175, 55, 0.05) 0%, transparent 50%);
            display: flex;
            flex-direction: column;
            justify-content: space-between;
            box-shadow: 0 0 30px rgba(0,0,0,0.1);
        }
        .header-section {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 30px;
            position: relative;
        }
        .logo {
            width: 80px;
            height: 80px;
            object-fit: contain;
        }
        .golden-seal {
            position: absolute;
            top: -20px;
            right: 50%;
            transform: translateX(50%);
            width: 120px;
            height: 120px;
            background: radial-gradient(circle, #ffd700 0%, #d4af37 70%, #b8860b 100%);
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            box-shadow: 0 0 20px rgba(212, 175, 55, 0.5);
            z-index: 10;
        }
        .seal-text {
            font-size: 12px;
            font-weight: bold;
            color: #8b4513;
            text-align: center;
            line-height: 1.2;
        }
        .certificate-title {
            font-size: 42px;
            font-weight: bold;
            color: #1a365d;
            margin: 40px 0 30px 0;
            text-align: center;
            text-transform: uppercase;
            letter-spacing: 4px;
            text-shadow: 2px 2px 4px rgba(0,0,0,0.1);
            background: linear-gradient(45deg, #1a365d, #2d5aa0);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
        }
        .certificate-text {
            font-size: 22px;
            line-height: 1.8;
            margin: 18px 0;
            color: #2d3748;
            text-align: center;
            font-weight: 400;
        }
        .participant-name {
            font-size: 36px;
            font-weight: bold;
            color: #c53030;
            margin: 35px 0;
            text-align: center;
            text-decoration: underline;
            text-decoration-color: #d4af37;
            text-decoration-thickness: 3px;
            font-family: 'Times New Roman', serif;
            text-shadow: 1px 1px 3px rgba(0,0,0,0.1);
        }
        .event-name {
            font-size: 32px;
            font-weight: bold;
            margin: 30px 0;
            color: #1a365d;
            text-align: center;
            background: linear-gradient(45deg, #1a365d, #d4af37);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
        }
        .signatures {
            display: flex;
            justify-content: space-around;
            margin-top: 60px;
            position: relative;
        }
        .signature {
            text-align: center;
            width: 280px;
            position: relative;
        }
        .signature-image {
            height: 70px;
            margin-bottom: 15px;
            filter: drop-shadow(0 2px 4px rgba(0,0,0,0.2));
        }
        .signature-line {
            border-bottom: 3px solid #d4af37;
            width: 220px;
            margin: 15px auto;
            position: relative;
        }
        .signature-line::after {
            content: '';
            position: absolute;
            bottom: -6px;
            left: 50%;
            transform: translateX(-50%);
            width: 180px;
            height: 1px;
            background: #b8860b;
        }
        .signature-name {
            font-weight: bold;
            font-size: 18px;
            margin-top: 15px;
            color: #1a365d;
            text-shadow: 1px 1px 2px rgba(0,0,0,0.05);
        }
        .signature-title {
            font-size: 16px;
            margin-top: 8px;
            color: #4a5568;
            font-style: italic;
        }
        .decorative-border {
            position: absolute;
            top: 20px;
            left: 20px;
            right: 20px;
            bottom: 20px;
            border: 2px solid #d4af37;
            border-radius: 15px;
            opacity: 0.3;
            pointer-events: none;
        }
        .corner-ornament {
            position: absolute;
            width: 40px;
            height: 40px;
            background: radial-gradient(circle, #d4af37 0%, #b8860b 100%);
            border-radius: 50%;
        }
        .corner-ornament.top-left {
            top: 10px;
            left: 10px;
        }
        .corner-ornament.top-right {
            top: 10px;
            right: 10px;
        }
        .corner-ornament.bottom-left {
            bottom: 10px;
            left: 10px;
        }
        .corner-ornament.bottom-right {
            bottom: 10px;
            right: 10px;
        }
        .conference-details {
            background: linear-gradient(90deg, rgba(212, 175, 55, 0.1) 0%, rgba(255, 215, 0, 0.1) 50%, rgba(212, 175, 55, 0.1) 100%);
            padding: 15px;
            border-radius: 10px;
            margin: 20px 0;
            border: 1px solid rgba(212, 175, 55, 0.3);
        }
        
        /* Responsive styles for PDF output */
        @media print {
            .certificate-container {
                padding: 40px 30px;
            }
            
            .golden-seal {
                width: 100px;
                height: 100px;
            }
            
            .certificate-title {
                font-size: 36px;
                margin: 30px 0 20px 0;
            }
            
            .certificate-text {
                font-size: 18px;
                margin: 15px 0;
            }
            
            .participant-name {
                font-size: 30px;
                margin: 25px 0;
            }
            
            .event-name {
                font-size: 28px;
                margin: 20px 0;
            }
            
            .signatures {
                margin-top: 40px;
            }
            
            .signature {
                width: 240px;
            }
            
            .signature-image {
                height: 60px;
            }
            
            .signature-line {
                width: 180px;
            }
            
            .signature-name {
                font-size: 16px;
            }
            
            .signature-title {
                font-size: 14px;
            }
        }
    </style>
</head>
<body>
    <div class="certificate-container">
        <div class="decorative-border"></div>
        <div class="corner-ornament top-left"></div>
        <div class="corner-ornament top-right"></div>
        <div class="corner-ornament bottom-left"></div>
        <div class="corner-ornament bottom-right"></div>
        
        <!-- Headers section to ensure proper display -->
        <div class="header-section">
            <img src="/serve_asset/{{ mdcan_logo.split('/')[-1] if mdcan_logo and '/' in mdcan_logo else 'mdcan-logo.png' }}" alt="MDCAN Logo" class="logo" onerror="this.src='data:image/png;base64,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';" />
            <div class="golden-seal">
                <div class="seal-text">
                    MDCAN<br>
                    BDM<br>
                    2025
                </div>
            </div>
            <img src="/serve_asset/{{ coalcity_logo.split('/')[-1] if coalcity_logo and '/' in coalcity_logo else 'coalcity-logo.png' }}" alt="Coal City Logo" class="logo" onerror="this.src='data:image/png;base64,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';" />
        </div>
        
        <div>
            <div class="certificate-title">
                {{ certificate_title }}
            </div>
            
            {{ certificate_content }}
        </div>
        
        <div class="signatures">
            <div class="signature">
                <img src="/serve_asset/{{ president_signature.split('/')[-1] if president_signature and '/' in president_signature else 'president-signature.png' }}" alt="President Signature" class="signature-image" onerror="this.src='data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAMgAAABkCAYAAADDhn8LAAAABGdBTUEAALGPC/xhBQAAACBjSFJNAAB6JgAAgIQAAPoAAACA6AAAdTAAAOpgAAA6mAAAF3CculE8AAAABmJLR0QA/wD/AP+gvaeTAAAAB3RJTUUH5AgGBzkfIayKcQAAD7JJREFUeNrtnWuMHVUdwH/33t3d7ba7pW0WodDAAwNIeARqAgSrVQxVo6KJwfjhYYJRCBSaGBLxkwTPh4nxAw9jhBg/mKhIeIQYCPIIGAiBQHgqSKGU0gJt6WO33fvww5mVYblz5szMndk7e39/srbdO/fMmfM/v3me/zkzDTHGGGOMMcYYY4wxxhhjTNVY1JBM3Xrjv4ErgeOAd4LcHNPBUmAz8CAwNiJmtRBsBnYBHxGl2jGX0S0/B74LLBv0RHUQbUPX+ZbEa6FtwPQQzWsATgeWAZsGPWdFYFGjieDmGOFGYDQJUhEmgKuBY/r9oYMYQRY3pPf4MvAKcEOD3DQhq4EjgeMHeeFKK5DZZu/xTcA1jcaOBrmJQhw6PW0e9MRlFRgwMXcQNQdRA5YA36CeGsF6xPm0V1Oe19I0vQG4DDAqgjFmXEv/UuBy4GXgD8ArKqSN6Pb9KvAR4EQdcTqOeS3z92eBLWUMSdOmMLMi/d+3gW8BvwX+DNyvwprNEexz7V2muwl8yHjmF4E/AbtLs0KlaBrfbk3zTeAK4B7gXuCf6g+tRXoaLWnMTQg6w9QW+cJCF48Z9P/OKXvnKEUIEjYtXfZF4HJgDfBn4FbgWeCIBgLdDONTfS1JpjFxv9S3wAFsUiGcDJwGfBq4BfgfcA5wlf7/I8Bx+vcTwEeB9wOPq8CeT9N0R4OZJtCLkEcH/d9zhPZFGlON5BT8IvE4cCHwAeCXwOPADcB9wKeA3eg0TKeoaXJ0XDTCa4OeiDkwEu2LtPcU0fZ1VPEO4AbE3xhR4Ryj/+8AD9HS8jK6k/+yQU9KzrzQoL0lw/+9A7gNcbTHgNOBi4CzgXe1HffsoH/4HGIPwv1g0D95LbAA/YhXVBhfAY4a9MQMiIcVQ0fAn2tPxqAnqpAsQafXK4OemErxoP57FvC2QU9MkRmJNrVaqh+zgK4nMPrRmEHUAp4JNJjdLtBCMQO8MeiJKAOjMYLUgGPR6Pd29Qm6CWTYmAEeS9P01UH/iLIwDOG+MXS0+Biwmo4TPMM+5mBJdWq1edA/osyMDPqHR3I+sBRZUDYp2Wa1ue/i+OUlTdP/AMOxPLpvDINAFgAvAb8CltPZTFZk+yFzz6s6WA+FMArJMPggNcSp/h1wAXBqg1zlCjNbS5rmDLAPWEQneyjE3oWGQiBtfgc8BfxU/+5XAEVfWdlYpqtSFiB7PJaqu9BtNz+T9HUYI54FeDXwEeCPwNeA0/QDioztrC9i7uGmXEKnBxlTgbweR7E9wEPD5HgPq0AAXgA+B1xIZxPYbANPYw44VZ5QBZLnV4yYn/FCt8EO3VQDWzTNmIqkBdyjTfhudZYztcIWdnrpNYI04sBrrLY84SrHfBvLB8nLDHBLmubjmtYYdNdpRBs6/VJ0GsQJ5FU9x3w0yb3Ip0CK0Pj7jNk1aZq+WsB5R7VqkrX3BVowD6BNLZMq0Ng6lE2aZoF5XZKmeZORGEEsWYZUyzrdeoH5E8hSFUh7L3iodUu7EF0XR5S/MJr6PL3O84S6Cb1qAIcQdcXAMsYO+JxpmmYnqg0cqJD3AEtVFMezuLNLXfPH1Ny5AliDrN95UHdY+FZlhpZVmqZP2wOo51wdONt3vOb50c7jzwQ+DlypPwk6y3jfCHwHuEttmI28q7zVhU7TdHeapjtTkzQgT9NW3Yg2ioiZ1ehQ33aO6c51IrWY8+5J07y9g9a1oO+2+kQZ1Z+4qA7nWYA2Ke8EXqITh/1mAQvZ5cC9zO1yVnR3eZH6QX3tFLrR8P6EiONeZCH3o8DjNGZrklWu6P9F+vDdmqab9L2LrXGd0rjzjXQYdZ3nt8CFwHfonkq9P+bztOkdbJN0NaLR1QVs6HEW6hh9/DQiDsxCr2huBm7Ncy+NfZLmWUDC/j3RgbmKzkbyOzStpdpMPINsN/m1cQ0zZvfD9k+Bm7kPqDIeZmF8G9nHPa1+wunM7pZ1jxq6mZuQr45nz2Nb9aOuInkZeSxbU/u5h5hbm9B+iBiui6E5r1Ixsw49Pw38DAlmLvQI/SxkZT6JvF4+Q5xzHsMBBLPXh+r7SxHn/LQMf88TzjQ/l6Rp/haxb+16FeKkN+mc4xVHk8UaRLO15PWtcLUjrg0a7XtGv7tTm9CL6WyPuRgJdrbR1yGb4e5Bgs1jPp9kCXKxS5B5/j1i/yNZ5xnzpTX/v0SfK+mELpYAf6DzZPWdGVotPcZZkPYDXkbm55QMaa2mc/8PIfY/QyeOchURQe1R5EYO9VwJHdFu0uZfqHAWxlw0r0BcL9iGD3kvoDmPuG6gmx3oK0C3sJLXA96vgj5Vv7+7wXRnr2jqXIaZfXSayh9CfLF12qx5D/A15ObubFCbCv1u+lTKH9CIX8z8TWkLdGGa5gmx/5BZOJkFoukcoXVdRWTr6YwuB1UYW7Vl8CSzH2P5F+BC/Z1rkABt2SJeYjBNLJiJVf2GvIllpPrXnBq6UYXxZeCPTUm7S8w2yBTXXISzr5j1LQZP9BCmxwfZCnyOTnj01h7Ht5vADyIbnK7U41NdrXh22dzU6SRN8+ZUBNmkTfON2Moa6jj+GnE2T0c+vwZpvbYjLHnE0NSbeVdNZ/HGvLkv3x6QGx1JE5/C9YKz9fElOum7hNLaQoJgJmRDFcJ0iEp4LoRpZBfSLI5hP+Y+NuXwQY49G9HmN5J/RHXNw7QJ+jTmfV6q87lLjz1FzTkOMdM1yjRPvVxTnB0aE7lR0QsUyQbt+LGmea9BbsYlDOmSQYAW4ib8BlnvfqcpjnZUbQzJyL4I+K4e+wLSPVxBp78CUlY0Uyaz1d1Hp4Jm+QWbkJjJTUj0C7qEIfOJqS4lTdMXEHczNiZiqheAv2kUZy3wBHLPy3VwXEznHifUvKnA36MHr9fH4+qDPYhk7qNq3hPqa96OjGJH6bkTFV6qs58r/7wKPEAe3yMuZKqBu/R3X4XkIj6DBGuPQpZ6/BpZoXpnTB6PISbM0qcZQzfLNs91SH+bPGUgWfO2G/gm8HtVlJ3e4x5B7kEv5c/sSLtc0aJGpD6P1Wl9XYuYdCMS9j0G6Uf/KLKF4yFtcU4OSOk3wPsQXye2frR1s09k3QUb6qzPSmdTivXfEEf+JWbbdCNxZqtk5NeQy5Z/6HU9rT9krX42Ip0Ojwdeir3vSZdIV1Hhm0e6n5p2Qmc/v3FG3wt9fCVYRGpvX0Fsc2wF/zFtQp3K7OU7XcPxKlRbTUhNtP/bsXMWOzpZFkNSJrN1JjJyfVajhL3m+FFkpcGu2Is0sX5IWQbPxZq+5S7vZPr79PkLkC6EWVYL9CJPk3QXsAE4MKB5n9Bm3Sn6erHy3qFmbGdMCDbG9p8Fm08t43M5nXXMQz9qeXwQVDQTGk39WsSE+dYPJQS5h/PQl19lHDxcxymT2fI16cZL/L6ePKl5s1ij1mwK6IuIQJ7RZzpnE4rNO6HXH9M0X6Rr7Vio4HbSDes29JnODZLEi9KhszZoKhL3PYa5+40ZnuHJeT7bVPgMOZ2RGBkPfI6NKnwOxUjnIfXJXkLuZ38ofU4Vx2tq77PeIOO9DfX5Q5LWmctN0c0hj2YMg0LOZUsbIkKCeVlyEpvmT5A13fP2JjHTpQ11wF/Q1+5Bopw3IAOPre5rjGn2OD8+TdPNaZrbG3QieLMFN52maa+8E9qkvU8/uzdwTN7r2C6aZQsB26yRYuLLSE/hCe3tVZQ8a2O2Ix0O30J3zMVMVwsxc0YXfOyc+w5mwi6iUznX0M/D+JYBJTqHGbM70QL6A/LsnDwnL3b27FHka5vfGZBz/qDmb6ky3NRRV5lYr4vYtTmJQzwNYLKAXefKwiywW9P83VQzOb3ik6VPPxGNY7+NbFMvM9PuXLJ0/QJ5ZN2ekvSATkNdIH3mDiLOuYwdMw8hO+Bjo+T9XKhvFCpyhHKZrbJTNsHYeKgziPqYwvyQIZpbp+q5T0Tnr9d1+znXgPIgofNs16WZ/Vf4vG+uXNGHrJ+9jLj53A58NcNnYS04C7PrwNYjS1xiNqwVxb4/oDf6FsR5fh8S5T8N2dUxhgTNXo2J9IUKowYZBd6k91uCnFmEVJFD1DzH7DySt6DwWFbCZnMfsl0l62r2fpz7wP6dCeAeROR3Z0w3NHN1B/Bg2qcgXa7v3aRpvqnXuo/ObxhB1ixdisR3rHlzPnDNpCrmMp2fPG2rSXQh4ooMaSa9rlPr8vzePmYXzXU9QvZOzNZXzBN+XYmMBrcDdw86vyvWWb+W3jvQQ+Y6sVdRQB8dArM1Ct1tVQp7ZfGpWuhYk+mU8TSy67xTgbKfuIXUV5EgEsiiurxdLrMuKuzU5X4akU2KMtPvcZr3Lx1MN8mO1zQ//BDTTDW9uxHz3Ia0lx8veFQrRQRMh8FslbXwbHwXnVXZrsJ5EokVbFMLjEA3svEE5pZt9vO+bWPL56lkEHbK7NB9iK93FRIx/QRzQ6V9CbJQ0dZht8fGhGKvb0eUwXQDYjazLpqz+5Qe18KJTK8H6fhsLc/5Ys7l+r69QtbGFKbDe4ZAOz2PuI5rYyGG8VJZzVbVr9+vvY5lKdNpVpWjzOv2K2yQjR8Hu2MxPthrtCqTQIbBbFU9r9BtLrOUO/QGz/XGlT2iOVfCKrORbBdRtpHUVf52Xp0FkrWw+j1fUXH1tS/8TRnfzCTKVLghu6iGpVKEFHCz4I76kqZAitSMaRLnM3Rfu9cnVaQixo5AVb9+lpvfbXZj2W5YDPDaNgYyfp4yRb/iyHKDitAfvmgkOd/Xy16dBS1WU2w3OXa1sO+6Nv05P+Uz32jS7/d7hflDW5DdfhfPnkiKg6MJ57XyCtl1/tgi6nUfIed14bq/rhy2K8Cc/SfHtewpnU31/YuYO4p0u+l53c6Y81lvjq1DXZ5VqfZrkQjgB4AzGTKB5HHa54v5hqVJEcNcx7GXQ+vy3rjP+t1aUMeYmvwqO+j7XLdNOzfXGGOMMcYYY4wxxhhjjDFyeD8BxFYp2NQpAAAAAElFTkSuQmCC';" />
                <div class="signature-line"></div>
                <div class="signature-name">Prof. Appolos Ndukuba</div>
                <div class="signature-title">LOC Chairman</div>
            </div>
            
            <div class="signature">
                <img src="/serve_asset/{{ chairman_signature.split('/')[-1] if chairman_signature and '/' in chairman_signature else 'chairman-signature.png' }}" alt="Chairman Signature" class="signature-image" onerror="this.src='data:image/png;base64,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';" />
                <div class="signature-line"></div>
                <div class="signature-name">Dr. Augustine Duru</div>
                <div class="signature-title">LOC Secretary<br>MDCAN Sec. Gen.</div>
            </div>
        </div>
    </div>
</body>
</html>
"""

PARTICIPATION_CONTENT = """
<div class="certificate-text">
    This is to certify that
</div>

<div class="participant-name">
    {{ participant_name }}
</div>

<div class="certificate-text">
    participated in the
</div>

<div class="conference-details">
    <div class="event-name">
        14th Biennial Delegates' Meeting and SCIENTIFIC Conference
    </div>
    
    <div class="certificate-text">
        OF MEDICAL AND DENTAL CONSULTANTS'ASSOCIATION OF NIGERIA
    </div>
    
    <div class="certificate-text">
        HELD AT INTERNATIONAL CONFERENCE CENTRE ENUGU FROM 1st–6th September, 2025
    </div>
</div>
"""

SERVICE_CONTENT = """
<div class="certificate-text">
    This is to acknowledge and appreciate
</div>

<div class="certificate-text">
    the exceptional service of
</div>

<div class="participant-name">
    {{ participant_name }}
</div>

<div class="certificate-text">
    towards the successful hosting of the
</div>

<div class="conference-details">
    <div class="event-name">
        14th Biennial Delegates' Meeting and SCIENTIFIC Conference
    </div>
    
    <div class="certificate-text">
        OF MEDICAL AND DENTAL CONSULTANTS'ASSOCIATION OF NIGERIA
    </div>
    
    <div class="certificate-text">
        HELD AT INTERNATIONAL CONFERENCE CENTRE ENUGU FROM 1st–6th September, 2025
    </div>
</div>
"""

def generate_certificate_pdf(participant_name, certificate_type='participation'):
    """Generate a PDF certificate for the participant"""
    try:
        # Get base directory and potential signature file locations
        base_dir = os.getcwd()
        print(f"Current working directory: {base_dir}")
        print(f"Generating {certificate_type} certificate for: {participant_name}")
        print(f"Using certificate template: {'PARTICIPATION_CONTENT' if certificate_type == 'participation' else 'SERVICE_CONTENT'}")
        
        possible_directories = [
            os.path.join(base_dir, 'frontend', 'public'),
            os.path.join(base_dir, 'public'),
            os.path.join(base_dir, 'backend', 'static'),
            os.path.join(base_dir)
        ]
        
        # Check if directories exist
        for directory in possible_directories:
            if os.path.exists(directory):
                print(f"Directory exists: {directory}")
            else:
                print(f"Directory does not exist: {directory}")
        
        # Define file basenames
        president_file_options = ['president-signature.png', 'president-signature-placeholder.jpg', 'president-signature.jpg']
        chairman_file_options = ['chairman-signature.png', 'chairman-signature-placeholder.png', 'Dr. Augustine Duru.jpg']
        mdcan_logo_options = ['mdcan-logo.png', 'mdcan_logo.jpeg', 'logo-mdcan.jpeg']
        coalcity_logo_options = ['coalcity-logo.png', 'coal_city_logo.png']
        
        # Function to find first existing file from options in directories
        def find_file(file_options, directories):
            for directory in possible_directories:
                for file_option in file_options:
                    file_path = os.path.join(directory, file_option)
                    if os.path.exists(file_path):
                        print(f"Found file: {file_path}")
                        return file_path
            
            # If no file found, use a direct reference to frontend/public
            for file_option in file_options:
                direct_path = os.path.join(base_dir, 'frontend', 'public', file_option)
                if os.path.exists(direct_path):
                    print(f"Found direct file: {direct_path}")
                    return direct_path
            
            # Return the first option (even if not found) as fallback
            fallback = os.path.join(possible_directories[0], file_options[0])
            print(f"Using fallback path: {fallback}")
            return fallback
        
        # Find signature files
        president_signature = find_file(president_file_options, possible_directories)
        chairman_signature = find_file(chairman_file_options, possible_directories)
        mdcan_logo = find_file(mdcan_logo_options, possible_directories)
        coalcity_logo = find_file(coalcity_logo_options, possible_directories)
        
        # Log paths for debugging
        print(f"Using files for certificate generation:")
        print(f"President signature: {president_signature}")
        print(f"Chairman signature: {chairman_signature}")
        print(f"MDCAN logo: {mdcan_logo}")
        print(f"Coal City logo: {coalcity_logo}")
        
        # Determine certificate title and content
        if certificate_type == 'service':
            certificate_title = 'ACKNOWLEDGEMENT OF SERVICE'
            print("Using SERVICE_CONTENT template:")
            print(SERVICE_CONTENT)
            content_template = Template(SERVICE_CONTENT)
        else:
            certificate_title = 'CERTIFICATE OF PARTICIPATION'
            print("Using PARTICIPATION_CONTENT template:")
            print(PARTICIPATION_CONTENT)
            content_template = Template(PARTICIPATION_CONTENT)
        
        # Generate content
        certificate_content = content_template.render(participant_name=participant_name)
        
        # Log signature paths for debugging
        print(f"MDCAN logo path: {mdcan_logo}")
        print(f"Coal City logo path: {coalcity_logo}")
        print(f"President signature path: {president_signature}")
        print(f"Chairman signature path: {chairman_signature}")
        
        # Create HTML from template
        template = Template(CERTIFICATE_HTML)
        html_content = template.render(
            certificate_title=certificate_title,
            certificate_content=certificate_content,
            participant_name=participant_name,
            president_signature=president_signature,
            chairman_signature=chairman_signature,
            mdcan_logo=mdcan_logo,
            coalcity_logo=coalcity_logo
        )
        
        # Generate PDF
        options = {
            'page-size': 'A4',
            'orientation': 'Landscape',
            'margin-top': '0.3in',
            'margin-right': '0.3in',
            'margin-bottom': '0.3in',
            'margin-left': '0.3in',
            'encoding': "UTF-8",
            'no-outline': None,
            'enable-local-file-access': None,
            'print-media-type': None,
            'disable-smart-shrinking': None
        }
        
        try:
            # Create temporary file
            temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.pdf')
            
            # Try to find wkhtmltopdf in common locations
            wkhtmltopdf_paths = [
                r'C:\Program Files\wkhtmltopdf\bin\wkhtmltopdf.exe',
                r'C:\Program Files (x86)\wkhtmltopdf\bin\wkhtmltopdf.exe',
                r'C:\wkhtmltopdf\bin\wkhtmltopdf.exe',
                '/usr/bin/wkhtmltopdf',
                '/usr/local/bin/wkhtmltopdf'
            ]
            
            # Check if any of the paths exist
            wkhtmltopdf_path = None
            for path in wkhtmltopdf_paths:
                if os.path.exists(path):
                    wkhtmltopdf_path = path
                    print(f"Found wkhtmltopdf at: {path}")
                    break
            
            if wkhtmltopdf_path:
                # Use the found path
                config = pdfkit.configuration(wkhtmltopdf=wkhtmltopdf_path)
                pdfkit.from_string(html_content, temp_file.name, options=options, configuration=config)
            else:
                # Try default installation
                pdfkit.from_string(html_content, temp_file.name, options=options)
            
            return temp_file.name
        except Exception as e:
            print(f"Error in PDF generation: {e}")
            
            # Alternative: Save HTML and notify
            html_file = tempfile.NamedTemporaryFile(delete=False, suffix='.html')
            with open(html_file.name, 'w', encoding='utf-8') as f:
                f.write(html_content)
            
            print(f"HTML file saved as fallback: {html_file.name}")
            
            # Return None to indicate failure in PDF generation
            return None
        
    except Exception as e:
        print(f"Error generating certificate PDF: {e}")
        return None

def send_email_with_certificate(participant_name, participant_email, pdf_path, certificate_type='participation'):
    """Send email with certificate attachment"""
    try:
        msg = MIMEMultipart()
        msg['From'] = EMAIL_FROM
        msg['To'] = participant_email
        
        # Set subject based on certificate type
        if certificate_type == 'service':
            msg['Subject'] = "Your MDCAN BDM 14th - 2025 Acknowledgement of Service"
            certificate_name = "Acknowledgement of Service"
        else:
            msg['Subject'] = "Your MDCAN BDM 14th - 2025 Certificate of Participation"
            certificate_name = "Certificate of Participation"
        
        # Create HTML email
        html_body = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <style>
                body {{ font-family: Arial, sans-serif; margin: 0; padding: 0; background-color: #f5f5f5; }}
                .container {{ max-width: 600px; margin: 0 auto; background-color: white; padding: 30px; border-radius: 10px; box-shadow: 0 0 10px rgba(0,0,0,0.1); }}
                .header {{ text-align: center; margin-bottom: 30px; border-bottom: 2px solid #d4af37; padding-bottom: 20px; }}
                .logo {{ width: 80px; height: 80px; margin: 0 auto 20px; }}
                .title {{ color: #1a365d; font-size: 24px; font-weight: bold; margin-bottom: 10px; }}
                .subtitle {{ color: #666; font-size: 16px; }}
                .content {{ margin: 20px 0; line-height: 1.6; }}
                .certificate-info {{ background-color: #f8f9fa; padding: 15px; border-radius: 5px; margin: 15px 0; border-left: 4px solid #d4af37; }}
                .footer {{ margin-top: 30px; padding-top: 20px; border-top: 1px solid #eee; text-align: center; color: #666; font-size: 14px; }}
                .button {{ display: inline-block; background-color: #1a365d; color: white; padding: 12px 24px; text-decoration: none; border-radius: 5px; margin: 10px 0; }}
                
                /* Responsive styles */
                @media only screen and (max-width: 480px) {{
                    .container {{ padding: 20px 15px; }}
                    .title {{ font-size: 20px; }}
                    .subtitle {{ font-size: 14px; }}
                    .content {{ font-size: 14px; }}
                    .footer {{ font-size: 12px; }}
                    .button {{ padding: 10px 20px; font-size: 14px; }}
                }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <div class="title">MDCAN BDM 14th - 2025</div>
                    <div class="subtitle">Enugu • September 1-6, 2025</div>
                </div>
                
                <div class="content">
                    <p>Dear {participant_name},</p>
                    
                    <p>{"Thank you for your exceptional service and contribution to the success of" if certificate_type == 'service' else "Congratulations! Thank you for participating in"} the MDCAN BDM 14th - 2025 conference held in Enugu from 1st – 6th September, 2025.</p>
                    
                    <div class="certificate-info">
                        <p><strong>Your {certificate_name} is attached to this email.</strong></p>
                        <p>You can download and save it for your records or print it if needed.</p>
                    </div>
                    
                    <p>{"We deeply appreciate your dedication and hard work in making this conference a success." if certificate_type == 'service' else "We appreciate your valuable participation and hope you found the conference beneficial."}</p>
                    
                    <p>If you have any questions or need further assistance, please don't hesitate to contact us.</p>
                </div>
                
                <div class="footer">
                    <p><strong>MDCAN BDM 2025 Organizing Committee</strong></p>
                    <p>Prof. Appolos Ndukuba - LOC Chairman<br>
                    Dr. Augustine Duru - LOC Secretary, MDCAN Sec. Gen.</p>
                </div>
            </div>
        </body>
        </html>
        """
        
        # Add HTML body
        msg.attach(MIMEText(html_body, 'html'))
        
        # Add plain text alternative for email clients that don't support HTML
        text_body = f"""
Dear {participant_name},

{"Thank you for your exceptional service and contribution to the success of" if certificate_type == 'service' else "Congratulations! Thank you for participating in"} the MDCAN BDM 14th - 2025 conference held in Enugu from 1st – 6th September, 2025.

Please find attached your {certificate_name}.

{"We deeply appreciate your dedication and hard work in making this conference a success." if certificate_type == 'service' else "We appreciate your valuable participation and hope you found the conference beneficial."}

Best regards,
MDCAN BDM 2025 Organizing Committee

Prof. Appolos Ndukuba
LOC Chairman

Dr. Augustine Duru
LOC Secretary
MDCAN Sec. Gen.
        """
        
        msg.attach(MIMEText(text_body, 'plain'))
        
        # Attach PDF
        if pdf_path and os.path.exists(pdf_path):
            with open(pdf_path, "rb") as attachment:
                part = MIMEBase('application', 'octet-stream')
                part.set_payload(attachment.read())
                encoders.encode_base64(part)
                filename = f"MDCAN_BDM_2025_{'Service' if certificate_type == 'service' else 'Certificate'}_{participant_name.replace(' ', '_')}.pdf"
                part.add_header(
                    'Content-Disposition',
                    f'attachment; filename= "{filename}"'
                )
                msg.attach(part)
        
        # Send email
        server = smtplib.SMTP(EMAIL_HOST, EMAIL_PORT)
        server.starttls()
        server.login(EMAIL_USER, EMAIL_PASSWORD)
        text = msg.as_string()
        server.sendmail(EMAIL_FROM, participant_email, text)
        server.quit()
        
        return True
    except Exception as e:
        print(f"Error sending email: {e}")
        return False


def send_notification_email(participant_email, participant_name, subject, message):
    """Send notification email to participant"""
    try:
        msg = MIMEMultipart()
        msg['From'] = EMAIL_FROM
        msg['To'] = participant_email
        msg['Subject'] = subject
        
        # Create HTML email template
        html_body = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <style>
                body {{ font-family: Arial, sans-serif; margin: 0; padding: 0; background-color: #f5f5f5; }}
                .container {{ max-width: 600px; margin: 0 auto; background-color: white; padding: 30px; border-radius: 10px; box-shadow: 0 0 10px rgba(0,0,0,0.1); }}
                .header {{ text-align: center; margin-bottom: 30px; }}
                .logo {{ width: 80px; height: 80px; margin: 0 auto 20px; }}
                .title {{ color: #1a365d; font-size: 24px; font-weight: bold; margin-bottom: 10px; }}
                .subtitle {{ color: #666; font-size: 16px; }}
                .content {{ margin: 20px 0; line-height: 1.6; }}
                .highlight {{ background-color: #d4af37; color: white; padding: 15px; border-radius: 5px; margin: 15px 0; }}
                .footer {{ margin-top: 30px; padding-top: 20px; border-top: 1px solid #eee; text-align: center; color: #666; font-size: 14px; }}
                .button {{ display: inline-block; background-color: #1a365d; color: white; padding: 12px 24px; text-decoration: none; border-radius: 5px; margin: 10px 0; }}
                
                /* Responsive styles */
                @media only screen and (max-width: 480px) {{
                    .container {{ padding: 20px 15px; }}
                    .title {{ font-size: 20px; }}
                    .subtitle {{ font-size: 14px; }}
                    .content {{ font-size: 14px; }}
                    .footer {{ font-size: 12px; }}
                    .button {{ padding: 10px 20px; font-size: 14px; }}
                }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <div class="title">MDCAN BDM 14th - 2025</div>
                    <div class="subtitle">Enugu • September 1-6, 2025</div>
                </div>
                
                <div class="content">
                    <p>Dear {participant_name},</p>
                    
                    {message}
                    
                    <p>For more information, visit our conference portal or contact the organizing committee.</p>
                </div>
                
                <div class="footer">
                    <p><strong>MDCAN BDM 2025 Organizing Committee</strong></p>
                    <p>Prof. Appolos Ndukuba - LOC Chairman<br>
                    Dr. Augustine Duru - LOC Secretary, MDCAN Sec. Gen.</p>
                </div>
            </div>
        </body>
        </html>
        """
        
        msg.attach(MIMEText(html_body, 'html'))
        
        # Send email
        server = smtplib.SMTP(EMAIL_HOST, EMAIL_PORT)
        server.starttls()
        server.login(EMAIL_USER, EMAIL_PASSWORD)
        text = msg.as_string()
        server.sendmail(EMAIL_FROM, participant_email, text)
        server.quit()
        
        return True
    except Exception as e:
        print(f"Error sending notification email: {e}")
        return False


def send_push_notification(subscription_data, title, message):
    """Send push notification to user's device"""
    try:
        # This would integrate with a push notification service like Firebase
        # For now, we'll log the notification
        print(f"Push notification: {title} - {message}")
        return True
    except Exception as e:
        print(f"Error sending push notification: {e}")
        return False


def send_program_reminder():
    """Send reminders for upcoming programs"""
    try:
        # Use application context for database operations
        with app.app_context():
            # Get programs starting in the next hour that haven't sent reminders
            upcoming_time = datetime.utcnow() + timedelta(hours=1)
            current_time = datetime.utcnow()
            
            programs = ConferenceProgram.query.filter(
                ConferenceProgram.start_time.between(current_time, upcoming_time),
                ConferenceProgram.notification_sent == False,
                ConferenceProgram.status == 'scheduled'
            ).all()
            
            for program in programs:
                # Get participants for this program
                if program.requires_registration:
                    # Get registered participants
                    participants = db.session.query(Participant).join(SessionRegistration).filter(
                        SessionRegistration.program_id == program.id,
                        SessionRegistration.attendance_status == 'registered',
                        Participant.email_notifications == True
                    ).all()
                else:
                    # Get all participants with notifications enabled
                    participants = Participant.query.filter(
                        Participant.email_notifications == True,
                        Participant.registration_fee_paid == True  # Use registration_fee_paid instead of status
                    ).all()
                
                # Send notifications
                subject = f"Reminder: {program.title} starting soon"
                message = f"""
                <div class="highlight">
                    <strong>Upcoming Session Reminder</strong>
                </div>
                
                <p>This is a friendly reminder that the following session is starting soon:</p>
                
                <p><strong>Program:</strong> {program.title}<br>
                <strong>Time:</strong> {program.start_time.strftime('%B %d, %Y at %I:%M %p')}<br>
                <strong>Venue:</strong> {program.venue}<br>
                <strong>Speaker:</strong> {program.speaker_name if program.speaker_name else 'TBA'}</p>
                
                <p><strong>Description:</strong><br>
                {program.description}</p>
                
                <p>Please ensure you arrive on time. Looking forward to seeing you there!</p>
                """
                
                for participant in participants:
                    # Send email notification
                    if participant.email_notifications:
                        send_notification_email(participant.email, participant.name, subject, message)
                    
                    # Send push notification
                    if participant.push_notifications and participant.push_subscription:
                        send_push_notification(
                            participant.push_subscription,
                            f"MDCAN BDM 2025: {program.title}",
                            f"Starting at {program.start_time.strftime('%I:%M %p')} in {program.venue}"
                        )
                
                # Mark notification as sent
                program.notification_sent = True
                db.session.commit()
            
        return len(programs)
    except Exception as e:
        print(f"Error sending program reminders: {e}")
        return 0

# API Routes
@app.route('/api/participants', methods=['GET'])
def get_participants():
    participants = Participant.query.order_by(Participant.created_at.desc()).all()
    return jsonify([p.to_dict() for p in participants])

@app.route('/api/participants', methods=['POST'])
def add_participant():
    try:
        data = request.json
        
        # Validate required fields
        if not data.get('name') or not data.get('email'):
            return jsonify({'error': 'Name and email are required'}), 400
        
        # Check if participant already exists
        existing = Participant.query.filter_by(email=data['email']).first()
        if existing:
            return jsonify({'error': 'Participant with this email already exists'}), 400
        
        participant = Participant(
            name=data['name'].strip(),
            email=data['email'].strip().lower(),
            organization=data.get('organization', '').strip() if data.get('organization') else None,
            position=data.get('position', '').strip() if data.get('position') else None,
            phone_number=data.get('phoneNumber', '').strip() if data.get('phoneNumber') else None,
            certificate_type=data.get('certificateType', 'participation'),
            registration_source='manual',
            created_by=request.remote_addr or 'unknown'
        )
        
        db.session.add(participant)
        db.session.commit()
        
        # Log the creation
        log_entry = CertificateLog(
            participant_id=participant.id,
            action='created',
            status='success',
            ip_address=request.remote_addr,
            user_agent=request.headers.get('User-Agent', '')[:500]
        )
        db.session.add(log_entry)
        db.session.commit()
        
        return jsonify(participant.to_dict()), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Failed to add participant: {str(e)}'}), 500

@app.route('/api/send-certificate/<int:participant_id>', methods=['POST'])
def send_certificate(participant_id):
    participant = Participant.query.get_or_404(participant_id)
    
    try:
        # Generate certificate PDF
        pdf_path = generate_certificate_pdf(participant.name, participant.certificate_type)
        if not pdf_path:
            return jsonify({'error': 'Failed to generate certificate PDF'}), 500
        
        # Send email
        if send_email_with_certificate(participant.name, participant.email, pdf_path, participant.certificate_type):
            participant.certificate_status = 'sent'
            participant.certificate_sent_at = datetime.utcnow()
            db.session.commit()
            
            # Clean up temporary PDF file
            if os.path.exists(pdf_path):
                os.unlink(pdf_path)
            
            return jsonify({'message': 'Certificate sent successfully'})
        else:
            participant.certificate_status = 'failed'
            db.session.commit()
            return jsonify({'error': 'Failed to send email'}), 500
            
    except Exception as e:
        participant.certificate_status = 'failed'
        db.session.commit()
        return jsonify({'error': str(e)}), 500

@app.route('/api/send-all-certificates', methods=['POST'])
def send_all_certificates():
    participants = Participant.query.filter_by(certificate_status='pending').all()
    
    sent_count = 0
    failed_count = 0
    
    for participant in participants:
        try:
            pdf_path = generate_certificate_pdf(participant.name, participant.certificate_type)
            if pdf_path and send_email_with_certificate(participant.name, participant.email, pdf_path, participant.certificate_type):
                participant.certificate_status = 'sent'
                participant.certificate_sent_at = datetime.utcnow()
                sent_count += 1
                
                # Clean up temporary PDF file
                if os.path.exists(pdf_path):
                    os.unlink(pdf_path)
            else:
                participant.certificate_status = 'failed'
                failed_count += 1
        except Exception as e:
            print(f"Error sending certificate to {participant.name}: {e}")
            participant.certificate_status = 'failed'
            failed_count += 1
    
    db.session.commit()
    
    return jsonify({
        'message': f'Certificates sent: {sent_count}, Failed: {failed_count}',
        'sent_count': sent_count,
        'failed_count': failed_count
    })

@app.route('/api/upload-excel', methods=['POST'])
def upload_excel():
    """Upload Excel file with participant data and generate certificates"""
    try:
        if 'file' not in request.files:
            return jsonify({'error': 'No file uploaded'}), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
        
        if not file.filename.lower().endswith(('.xlsx', '.xls')):
            return jsonify({'error': 'Please upload an Excel file (.xlsx or .xls)'}), 400
        
        # Save uploaded file temporarily
        filename = secure_filename(file.filename)
        temp_path = os.path.join(tempfile.gettempdir(), filename)
        file.save(temp_path)
        
        # Read Excel file
        try:
            df = pd.read_excel(temp_path)
        except Exception as e:
            os.remove(temp_path)
            return jsonify({'error': f'Error reading Excel file: {str(e)}'}), 400
        
        # Validate required columns
        required_columns = ['name', 'email']
        missing_columns = [col for col in required_columns if col.lower() not in df.columns.str.lower()]
        if missing_columns:
            os.remove(temp_path)
            return jsonify({'error': f'Missing required columns: {", ".join(missing_columns)}'}), 400
        
        # Normalize column names
        df.columns = df.columns.str.lower()
        
        # Process each participant
        added_count = 0
        failed_count = 0
        failed_records = []
        
        for index, row in df.iterrows():
            try:
                # Extract data from row
                name = str(row['name']).strip()
                email = str(row['email']).strip()
                organization = str(row.get('organization', '')).strip() if pd.notna(row.get('organization')) else ''
                position = str(row.get('position', '')).strip() if pd.notna(row.get('position')) else ''
                
                # Determine certificate type based on role/position
                role = str(row.get('role', '')).strip().lower() if pd.notna(row.get('role')) else ''
                certificate_type = 'service' if role in ['volunteer', 'organizer', 'staff', 'committee', 'organizing committee'] else 'participation'
                
                # Skip if name or email is missing
                if not name or not email or name == 'nan' or email == 'nan':
                    failed_count += 1
                    failed_records.append({'row': index + 2, 'error': 'Missing name or email'})
                    continue
                
                # Check if participant already exists
                existing = Participant.query.filter_by(email=email).first()
                if existing:
                    failed_count += 1
                    failed_records.append({'row': index + 2, 'error': 'Email already exists'})
                    continue
                
                # Create new participant
                participant = Participant(
                    name=name,
                    email=email,
                    organization=organization,
                    position=position,
                    certificate_type=certificate_type,
                    certificate_status='pending'
                )
                
                db.session.add(participant)
                added_count += 1
                
            except Exception as e:
                failed_count += 1
                failed_records.append({'row': index + 2, 'error': str(e)})
        
        # Commit all changes
        try:
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            os.remove(temp_path)
            return jsonify({'error': f'Database error: {str(e)}'}), 500
        
        # Clean up temp file
        os.remove(temp_path)
        
        return jsonify({
            'message': f'Successfully processed {added_count} participants',
            'added_count': added_count,
            'failed_count': failed_count,
            'failed_records': failed_records[:10]  # Return first 10 failed records
        })
        
    except Exception as e:
        return jsonify({'error': f'Unexpected error: {str(e)}'}), 500

@app.route('/api/bulk-send-certificates', methods=['POST'])
def bulk_send_certificates():
    """Send certificates to all participants from uploaded Excel data"""
    try:
        # Get all participants with pending certificates
        participants = Participant.query.filter_by(certificate_status='pending').all()
        
        if not participants:
            return jsonify({'message': 'No participants with pending certificates found'}), 404
        
        sent_count = 0
        failed_count = 0
        failed_emails = []
        
        for participant in participants:
            try:
                # Generate and send certificate
                pdf_path = generate_certificate_pdf(participant.name, participant.certificate_type)
                send_certificate_email(participant.email, participant.name, pdf_path, participant.certificate_type)
                
                # Update participant status
                participant.certificate_status = 'sent'
                participant.certificate_sent_at = datetime.utcnow()
                
                sent_count += 1
                
                # Clean up PDF file
                try:
                    os.unlink(pdf_path)
                except:
                    pass
                    
            except Exception as e:
                failed_count += 1
                failed_emails.append({'email': participant.email, 'error': str(e)})
                print(f"Failed to send certificate to {participant.email}: {str(e)}")
        
        # Save changes to database
        try:
            db.session.commit()
        except Exception as e:
            print(f"Database error: {str(e)}")
        
        return jsonify({
            'message': f'Bulk certificate sending completed. Sent: {sent_count}, Failed: {failed_count}',
            'sent_count': sent_count,
            'failed_count': failed_count,
            'failed_emails': failed_emails[:10]  # Return first 10 failed emails
        })
        
    except Exception as e:
        return jsonify({'error': f'Bulk sending failed: {str(e)}'}), 500

@app.route('/api/health', methods=['GET'])
def health_check():
    try:
        # Basic health status
        health = {
            'status': 'ok', 
            'message': 'MDCAN BDM 2025 Certificate API is running',
            'version': '2.0',
            'timestamp': datetime.utcnow().isoformat(),
            'database': {
                'status': 'unknown'
            }
        }
        
        # Test database connection
        try:
            # Test basic connection
            with db.engine.connect() as conn:
                result = conn.execute(sa.text("SELECT version();"))
                postgres_version = result.scalar()
                health['database']['version'] = postgres_version
                health['database']['status'] = 'connected'
            
            # Test model queries
            try:
                participant_count = Participant.query.count()
                log_count = CertificateLog.query.count()
                health['database']['participants'] = participant_count
                health['database']['logs'] = log_count
            except Exception as model_error:
                health['database']['model_error'] = str(model_error)
                health['database']['status'] = 'schema_issue'
        except Exception as db_error:
            health['database']['status'] = 'error'
            health['database']['error'] = str(db_error)
            health['status'] = 'degraded'
        
        # Get available API endpoints
        rules = []
        for rule in app.url_map.iter_rules():
            if rule.endpoint != 'static':
                rules.append({
                    'endpoint': rule.endpoint,
                    'methods': [method for method in rule.methods if method not in ['HEAD', 'OPTIONS']],
                    'path': str(rule)
                })
        health['api'] = {
            'endpoints': len(rules),
            'endpoints_list': rules
        }
        
        # Add device detection for responsive design
        user_agent = request.headers.get('User-Agent', '')
        is_mobile = 'Mobile' in user_agent or 'Android' in user_agent or 'iPhone' in user_agent or 'iPad' in user_agent
        is_tablet = 'iPad' in user_agent or 'Tablet' in user_agent
        device_type = 'mobile' if is_mobile and not is_tablet else 'tablet' if is_tablet else 'desktop'
        
        health['client'] = {
            'device_type': device_type,
            'is_mobile': is_mobile,
            'is_tablet': is_tablet,
            'user_agent': user_agent,
            'host': request.host,
            'origin': request.headers.get('Origin', '')
        }
        
        status_code = 200 if health['status'] == 'ok' else 207  # Partial Content if degraded
        return jsonify(health), status_code
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': 'Service health check failed',
            'error': str(e),
            'timestamp': datetime.utcnow().isoformat()
        }), 500

@app.route('/api/stats', methods=['GET'])
def get_statistics():
    """Get application statistics with robust error handling for missing fields"""
    try:
        # Basic stats that should work even with schema discrepancies
        stats = {
            'participants': {
                'total': 0,
                'participation_certificates': 0,
                'service_certificates': 0,
                'certificates_sent': 0,
                'certificates_pending': 0,
                'certificates_failed': 0
            },
            'recent_activity': {
                'registrations_today': 0,
                'certificates_sent_today': 0
            },
            'system': {
                'database_type': 'PostgreSQL',
                'total_logs': 0,
                'status': 'Connected'
            }
        }
        
        # Safely try to get counts with error handling for each query
        try:
            stats['participants']['total'] = Participant.query.count()
        except Exception as e:
            print(f"Error getting participant count: {e}")
        
        try:
            stats['participants']['participation_certificates'] = Participant.query.filter_by(certificate_type='participation').count()
        except Exception as e:
            print(f"Error getting participation certificate count: {e}")
        
        try:
            stats['participants']['service_certificates'] = Participant.query.filter_by(certificate_type='service').count()
        except Exception as e:
            print(f"Error getting service certificate count: {e}")
        
        try:
            stats['participants']['certificates_sent'] = Participant.query.filter_by(certificate_status='sent').count()
        except Exception as e:
            print(f"Error getting certificates sent count: {e}")
        
        try:
            stats['participants']['certificates_pending'] = Participant.query.filter_by(certificate_status='pending').count()
        except Exception as e:
            print(f"Error getting certificates pending count: {e}")
        
        try:
            stats['participants']['certificates_failed'] = Participant.query.filter_by(certificate_status='failed').count()
        except Exception as e:
            print(f"Error getting certificates failed count: {e}")
        
        try:
            stats['recent_activity']['registrations_today'] = Participant.query.filter(
                Participant.created_at >= datetime.utcnow().date()
            ).count()
        except Exception as e:
            print(f"Error getting registrations today count: {e}")
        
        try:
            stats['recent_activity']['certificates_sent_today'] = CertificateLog.query.filter(
                CertificateLog.timestamp >= datetime.utcnow().date(),
                CertificateLog.action == 'sent',
                CertificateLog.status == 'success'
            ).count()
        except Exception as e:
            print(f"Error getting certificates sent today count: {e}")
            
        try:
            stats['system']['total_logs'] = CertificateLog.query.count()
        except Exception as e:
            print(f"Error getting total logs count: {e}")
        
        # Add database schema version and connection info
        try:
            with db.engine.connect() as conn:
                result = conn.execute(sa.text("SELECT version();"))
                version = result.scalar()
                stats['system']['database_version'] = version
        except Exception as e:
            stats['system']['database_version'] = 'Unknown'
            print(f"Error getting database version: {e}")
        
        return jsonify(stats)
    except Exception as e:
        error_message = str(e)
        print(f"Error in get_statistics: {error_message}")
        return jsonify({
            'error': f'Failed to get statistics: {error_message}',
            'system': {
                'status': 'Error',
                'message': 'Database error encountered'
            }
        }), 500


@app.route('/api/programs/reminders/trigger', methods=['GET', 'POST'])
def trigger_program_reminders():
    """Manually trigger program reminders for upcoming programs"""
    try:
        # Call the function that sends program reminders
        reminder_count = send_program_reminder()
        
        return jsonify({
            'status': 'success',
            'message': f'Successfully triggered reminders for {reminder_count} upcoming programs',
            'reminder_count': reminder_count
        })
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': f'Error sending program reminders: {str(e)}'
        }), 500


# ============================================================================
# CONFERENCE REGISTRATION APIs
# ============================================================================

@app.route('/api/register', methods=['POST'])
def register_participant():
    """Complete conference registration with all details"""
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger("register_api")
    try:
        data = request.json
        logger.info(f"Received registration data: {data}")
        # Validate required fields
        required_fields = ['name', 'email', 'phone_number']
        for field in required_fields:
            if not data.get(field):
                logger.warning(f"Missing required field: {field}")
                return jsonify({'error': f"{field.replace('_', ' ').title()} is required"}), 400
        # Check if participant already exists
        existing = Participant.query.filter_by(email=data['email']).first()
        if existing:
            logger.warning(f"Duplicate registration attempt for email: {data['email']}")
            return jsonify({'error': 'Email already registered. Please use a different email or login to update your registration.'}), 400
        # Create participant with registration details
        participant = Participant(
            name=data['name'].strip(),
            email=data['email'].strip().lower(),
            phone_number=data['phone_number'].strip(),
            organization=data.get('organization', '').strip() or None,
            position=data.get('position', '').strip() or None,
            registration_type=data.get('registration_type', 'participant'),
            registration_status='registered',
            dietary_requirements=data.get('dietary_requirements', '').strip() or None,
            special_needs=data.get('special_needs', '').strip() or None,
            emergency_contact_name=data.get('emergency_contact_name', '').strip() or None,
            emergency_contact_phone=data.get('emergency_contact_phone', '').strip() or None,
            email_notifications=data.get('email_notifications', True),
            sms_notifications=data.get('sms_notifications', False),
            push_notifications=data.get('push_notifications', True),
            registration_source='online',
            created_by='self-registration'
        )
        db.session.add(participant)
        db.session.commit()
        logger.info(f"Participant registered successfully: {participant.email}")
        # Send welcome email
        welcome_subject = "Welcome to MDCAN BDM 14th - 2025!"
        welcome_message = f"""
        <div class="highlight">
            <strong>Registration Successful!</strong>
        </div>
        <p>Thank you for registering for the MDCAN BDM 14th - 2025 conference. We're excited to have you join us in Enugu from September 1-6, 2025.</p>
        <p><strong>Your Registration Details:</strong><br>
        <strong>Name:</strong> {participant.name}<br>
        <strong>Email:</strong> {participant.email}<br>
        <strong>Registration Type:</strong> {participant.registration_type.title()}<br>
        <strong>Registration Number:</strong> {participant.certificate_number}</p>
        <p><strong>What's Next?</strong></p>
        <ul>
            <li>You'll receive updates about the conference program</li>
            <li>Payment instructions will be sent if applicable</li>
            <li>Program schedule will be available soon</li>
            <li>Your certificate will be ready after the conference</li>
        </ul>
        <p>Keep an eye on your inbox for important updates and reminders!</p>
        """
        if participant.email_notifications:
            try:
                send_notification_email(participant.email, participant.name, welcome_subject, welcome_message)
                logger.info(f"Welcome email sent to: {participant.email}")
            except Exception as email_error:
                logger.error(f"Failed to send welcome email: {email_error}")
        return jsonify({
            'message': 'Registration successful!',
            'participant': participant.to_dict(),
            'registration_number': participant.certificate_number
        }), 201
    except Exception as e:
        db.session.rollback()
        logger.error(f"Registration failed: {str(e)}", exc_info=True)
        return jsonify({'error': f'Registration failed: {str(e)}'}), 500
def update_participant(participant_id):
    """Update participant registration details"""
    try:
        participant = Participant.query.get_or_404(participant_id)
        data = request.json
        
        # Update allowed fields
        updatable_fields = [
            'name', 'phone_number', 'organization', 'position',
            'dietary_requirements', 'special_needs', 'emergency_contact_name',
            'emergency_contact_phone', 'email_notifications', 'sms_notifications',
            'push_notifications'
        ]
        
        for field in updatable_fields:
            if field in data:
                if field in ['dietary_requirements', 'special_needs', 'emergency_contact_name', 'emergency_contact_phone']:
                    setattr(participant, field, data[field].strip() if data[field] else None)
                elif field in ['email_notifications', 'sms_notifications', 'push_notifications']:
                    setattr(participant, field, bool(data[field]))
                else:
                    setattr(participant, field, data[field].strip())
        
        participant.updated_at = datetime.utcnow()
        db.session.commit()
        
        return jsonify({
            'message': 'Registration updated successfully',
            'participant': participant.to_dict()
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Update failed: {str(e)}'}), 500


@app.route('/api/participants/<participant_email>/dashboard', methods=['GET'])
def get_participant_dashboard(participant_email):
    """Get participant dashboard with registration info, schedule, and notifications"""
    try:
        participant = Participant.query.filter_by(email=participant_email).first()
        if not participant:
            return jsonify({'error': 'Participant not found'}), 404
        
        # Get registered sessions
        registered_sessions = db.session.query(SessionRegistration, ConferenceProgram).join(
            ConferenceProgram, SessionRegistration.program_id == ConferenceProgram.id
        ).filter(SessionRegistration.participant_id == participant.id).all()
        
        # Get upcoming programs (next 24 hours)
        upcoming_programs = ConferenceProgram.query.filter(
            ConferenceProgram.start_time > datetime.utcnow(),
            ConferenceProgram.start_time <= datetime.utcnow() + timedelta(hours=24),
            ConferenceProgram.status == 'scheduled'
        ).order_by(ConferenceProgram.start_time).all()
        
        # Get recent notifications for this participant
        recent_notifications = Notification.query.filter(
            Notification.status == 'sent',
            Notification.created_at >= datetime.utcnow() - timedelta(days=7)
        ).order_by(Notification.created_at.desc()).limit(5).all()
        
        dashboard_data = {
            'participant': participant.to_dict(),
            'registered_sessions': [
                {
                    'registration': reg.to_dict(),
                    'program': program.to_dict()
                } for reg, program in registered_sessions
            ],
            'upcoming_programs': [p.to_dict() for p in upcoming_programs],
            'recent_notifications': [n.to_dict() for n in recent_notifications],
            'statistics': {
                'total_registered_sessions': len(registered_sessions),
                'attended_sessions': len([r for r, p in registered_sessions if r.attendance_status == 'attended']),
                'certificate_status': participant.certificate_status
            }
        }
        
        return jsonify(dashboard_data)
        
    except Exception as e:
        return jsonify({'error': f'Failed to get dashboard: {str(e)}'}), 500


# ============================================================================
# PROGRAM MANAGEMENT APIs
# ============================================================================

@app.route('/api/programs', methods=['GET'])
def get_programs():
    """Get all conference programs with optional filtering"""
    try:
        # Get query parameters
        program_type = request.args.get('type')
        date = request.args.get('date')
        status = request.args.get('status', 'scheduled')
        
        query = ConferenceProgram.query
        
        # Apply filters
        if program_type:
            query = query.filter(ConferenceProgram.program_type == program_type)
        if status:
            query = query.filter(ConferenceProgram.status == status)
        if date:
            try:
                filter_date = datetime.strptime(date, '%Y-%m-%d').date()
                query = query.filter(db.func.date(ConferenceProgram.start_time) == filter_date)
            except ValueError:
                return jsonify({'error': 'Invalid date format. Use YYYY-MM-DD'}), 400
        
        programs = query.order_by(ConferenceProgram.start_time).all()
        
        return jsonify([p.to_dict() for p in programs])
        
    except Exception as e:
        return jsonify({'error': f'Failed to get programs: {str(e)}'}), 500


@app.route('/api/programs', methods=['POST'])
def create_program():
    """Create a new conference program/session"""
    try:
        data = request.json
        
        # Validate required fields
        required_fields = ['title', 'start_time', 'end_time', 'program_type']
        for field in required_fields:
            if not data.get(field):
                return jsonify({'error': f'{field.replace("_", " ").title()} is required'}), 400
        
        # Parse datetime strings
        try:
            start_time = datetime.fromisoformat(data['start_time'].replace('Z', '+00:00'))
            end_time = datetime.fromisoformat(data['end_time'].replace('Z', '+00:00'))
        except ValueError:
            return jsonify({'error': 'Invalid datetime format'}), 400
        
        if start_time >= end_time:
            return jsonify({'error': 'End time must be after start time'}), 400
        
        program = ConferenceProgram(
            title=data['title'].strip(),
            description=data.get('description', '').strip() or None,
            program_type=data['program_type'],
            start_time=start_time,
            end_time=end_time,
            venue=data.get('venue', '').strip() or None,
            capacity=data.get('capacity'),
            speaker_name=data.get('speaker_name', '').strip() or None,
            speaker_bio=data.get('speaker_bio', '').strip() or None,
            speaker_photo_url=data.get('speaker_photo_url', '').strip() or None,
            is_mandatory=data.get('is_mandatory', False),
            requires_registration=data.get('requires_registration', False),
            reminder_minutes=data.get('reminder_minutes', 30),
            created_by='admin'
        )
        
        db.session.add(program)
        db.session.commit()
        
        return jsonify({
            'message': 'Program created successfully',
            'program': program.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Failed to create program: {str(e)}'}), 500


@app.route('/api/programs/<int:program_id>', methods=['PUT'])
def update_program(program_id):
    """Update an existing program"""
    try:
        program = ConferenceProgram.query.get_or_404(program_id)
        data = request.json
        
        # Update allowed fields
        if 'title' in data:
            program.title = data['title'].strip()
        if 'description' in data:
            program.description = data['description'].strip() or None
        if 'venue' in data:
            program.venue = data['venue'].strip() or None
        if 'capacity' in data:
            program.capacity = data['capacity']
        if 'speaker_name' in data:
            program.speaker_name = data['speaker_name'].strip() or None
        if 'speaker_bio' in data:
            program.speaker_bio = data['speaker_bio'].strip() or None
        if 'speaker_photo_url' in data:
            program.speaker_photo_url = data['speaker_photo_url'].strip() or None
        if 'is_mandatory' in data:
            program.is_mandatory = bool(data['is_mandatory'])
        if 'requires_registration' in data:
            program.requires_registration = bool(data['requires_registration'])
        if 'reminder_minutes' in data:
            program.reminder_minutes = data['reminder_minutes']
        if 'status' in data:
            program.status = data['status']
        
        # Handle datetime updates
        if 'start_time' in data:
            try:
                program.start_time = datetime.fromisoformat(data['start_time'].replace('Z', '+00:00'))
                # Reset notification flag if time changed
                program.notification_sent = False
            except ValueError:
                return jsonify({'error': 'Invalid start_time format'}), 400
        
        if 'end_time' in data:
            try:
                program.end_time = datetime.fromisoformat(data['end_time'].replace('Z', '+00:00'))
            except ValueError:
                return jsonify({'error': 'Invalid end_time format'}), 400
        
        if program.start_time >= program.end_time:
            return jsonify({'error': 'End time must be after start time'}), 400
        
        program.updated_at = datetime.utcnow()
        db.session.commit()
        
        return jsonify({
            'message': 'Program updated successfully',
            'program': program.to_dict()
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Failed to update program: {str(e)}'}), 500


@app.route('/api/programs/<int:program_id>/register', methods=['POST'])
def register_for_program(program_id):
    """Register a participant for a specific program/session"""
    try:
        data = request.json
        participant_id = data.get('participant_id')
        
        if not participant_id:
            return jsonify({'error': 'Participant ID is required'}), 400
        
        program = ConferenceProgram.query.get_or_404(program_id)
        participant = Participant.query.get_or_404(participant_id)
        
        # Check if program requires registration
        if not program.requires_registration:
            return jsonify({'error': 'This program does not require registration'}), 400
        
        # Check capacity
        if program.capacity:
            current_registrations = SessionRegistration.query.filter_by(
                program_id=program_id,
                attendance_status='registered'
            ).count()
            if current_registrations >= program.capacity:
                return jsonify({'error': 'Program is at full capacity'}), 400
        
        # Check if already registered
        existing = SessionRegistration.query.filter_by(
            participant_id=participant_id,
            program_id=program_id
        ).first()
        
        if existing:
            return jsonify({'error': 'Already registered for this program'}), 400
        
        # Create registration
        registration = SessionRegistration(
            participant_id=participant_id,
            program_id=program_id,
            attendance_status='registered'
        )
        
        db.session.add(registration)
        db.session.commit()
        
        # Send confirmation email
        if participant.email_notifications:
            subject = f"Registration Confirmed: {program.title}"
            message = f"""
            <div class="highlight">
                <strong>Session Registration Confirmed</strong>
            </div>
            
            <p>You have successfully registered for the following session:</p>
            
            <p><strong>Program:</strong> {program.title}<br>
            <strong>Date & Time:</strong> {program.start_time.strftime('%B %d, %Y at %I:%M %p')}<br>
            <strong>Venue:</strong> {program.venue}<br>
            <strong>Speaker:</strong> {program.speaker_name if program.speaker_name else 'TBA'}</p>
            
            <p><strong>Description:</strong><br>
            {program.description}</p>
            
            <p>Please arrive on time. You will receive a reminder before the session starts.</p>
            """
            send_notification_email(participant.email, participant.name, subject, message)
        
        return jsonify({
            'message': 'Successfully registered for program',
            'registration': registration.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Registration failed: {str(e)}'}), 500


# ============================================================================
# NOTIFICATION & MESSAGING APIs
# ============================================================================

@app.route('/api/notifications', methods=['GET'])
def get_notifications():
    """Get all notifications with optional filtering"""
    try:
        status = request.args.get('status')
        notification_type = request.args.get('type')
        limit = request.args.get('limit', 50, type=int)
        
        query = Notification.query
        
        if status:
            query = query.filter(Notification.status == status)
        if notification_type:
            query = query.filter(Notification.notification_type == notification_type)
        
        notifications = query.order_by(Notification.created_at.desc()).limit(limit).all()
        
        return jsonify([n.to_dict() for n in notifications])
        
    except Exception as e:
        return jsonify({'error': f'Failed to get notifications: {str(e)}'}), 500


@app.route('/api/notifications', methods=['POST'])
def create_notification():
    """Create and schedule a new notification"""
    try:
        data = request.json
        
        # Validate required fields
        required_fields = ['title', 'message', 'notification_type', 'scheduled_time']
        for field in required_fields:
            if not data.get(field):
                return jsonify({'error': f'{field.replace("_", " ").title()} is required'}), 400
        
        # Parse scheduled time
        try:
            scheduled_time = datetime.fromisoformat(data['scheduled_time'].replace('Z', '+00:00'))
        except ValueError:
            return jsonify({'error': 'Invalid scheduled_time format'}), 400
        
        notification = Notification(
            title=data['title'].strip(),
            message=data['message'].strip(),
            notification_type=data['notification_type'],
            target_audience=data.get('target_audience', 'all'),
            target_program_id=data.get('target_program_id'),
            scheduled_time=scheduled_time,
            send_email=data.get('send_email', True),
            send_push=data.get('send_push', True),
            send_sms=data.get('send_sms', False),
            created_by='admin'
        )
        
        db.session.add(notification)
        db.session.commit()
        
        # If scheduled for immediate sending
        if scheduled_time <= datetime.utcnow():
            send_notification_now(notification.id)
        
        return jsonify({
            'message': 'Notification created successfully',
            'notification': notification.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Failed to create notification: {str(e)}'}), 500


@app.route('/api/notifications/<int:notification_id>/send', methods=['POST'])
def send_notification_now(notification_id):
    """Send a notification immediately"""
    try:
        notification = Notification.query.get_or_404(notification_id)
        
        if notification.status == 'sent':
            return jsonify({'error': 'Notification already sent'}), 400
        
        # Get target participants
        participants = []
        
        if notification.target_audience == 'all':
            participants = Participant.query.filter(
                Participant.registration_status.in_(['registered', 'confirmed'])
            ).all()
        elif notification.target_audience == 'participants':
            participants = Participant.query.filter(
                Participant.registration_type == 'participant',
                Participant.registration_status.in_(['registered', 'confirmed'])
            ).all()
        elif notification.target_audience == 'speakers':
            participants = Participant.query.filter(
                Participant.registration_type == 'speaker',
                Participant.registration_status.in_(['registered', 'confirmed'])
            ).all()
        elif notification.target_audience == 'specific_program' and notification.target_program_id:
            participants = db.session.query(Participant).join(SessionRegistration).filter(
                SessionRegistration.program_id == notification.target_program_id,
                SessionRegistration.attendance_status == 'registered'
            ).all()
        
        # Send notifications
        email_sent = 0
        push_sent = 0
        email_failed = 0
        push_failed = 0
        
        for participant in participants:
            # Send email notification
            if notification.send_email and participant.email_notifications:
                try:
                    send_notification_email(participant.email, participant.name, notification.title, notification.message)
                    email_sent += 1
                except:
                    email_failed += 1
            
            # Send push notification
            if notification.send_push and participant.push_notifications and participant.push_subscription:
                try:
                    send_push_notification(participant.push_subscription, notification.title, notification.message)
                    push_sent += 1
                except:
                    push_failed += 1
        
        # Update notification status
        notification.status = 'sent'
        notification.sent_at = datetime.utcnow()
        notification.delivery_stats = json.dumps({
            'email_sent': email_sent,
            'email_failed': email_failed,
            'push_sent': push_sent,
            'push_failed': push_failed,
            'total_recipients': len(participants)
        })
        
        db.session.commit()
        
        return jsonify({
            'message': 'Notification sent successfully',
            'statistics': {
                'email_sent': email_sent,
                'email_failed': email_failed,
                'push_sent': push_sent,
                'push_failed': push_failed,
                'total_recipients': len(participants)
            }
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Failed to send notification: {str(e)}'}), 500


@app.route('/api/push-subscription', methods=['POST'])
def save_push_subscription():
    """Save push notification subscription for a participant"""
    try:
        data = request.json
        participant_email = data.get('email')
        subscription_data = data.get('subscription')
        
        if not participant_email or not subscription_data:
            return jsonify({'error': 'Email and subscription data required'}), 400
        
        participant = Participant.query.filter_by(email=participant_email).first()
        if not participant:
            return jsonify({'error': 'Participant not found'}), 404
        
        participant.push_subscription = json.dumps(subscription_data)
        participant.push_notifications = True
        db.session.commit()
        
        return jsonify({'message': 'Push subscription saved successfully'})
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Failed to save subscription: {str(e)}'}), 500


# ============================================================================
# CERTIFICATE DOWNLOAD & MANAGEMENT APIs
# ============================================================================

@app.route('/api/participants/<participant_email>/certificate', methods=['GET'])
def download_certificate(participant_email):
    """Download certificate for a participant"""
    try:
        participant = Participant.query.filter_by(email=participant_email).first()
        if not participant:
            return jsonify({'error': 'Participant not found'}), 404
        
        # Check if participant has attended the conference
        if participant.registration_status != 'attended' and participant.event_attendance != True:
            return jsonify({'error': 'Certificate not available. Conference attendance required.'}), 403
        
        # Generate certificate PDF
        pdf_path = generate_certificate_pdf(participant.name, participant.certificate_type)
        if not pdf_path:
            return jsonify({'error': 'Failed to generate certificate'}), 500
        
        # Log the download
        log_entry = CertificateLog(
            participant_id=participant.id,
            action='downloaded',
            status='success',
            ip_address=request.remote_addr,
            user_agent=request.headers.get('User-Agent', '')[:500]
        )
        db.session.add(log_entry)
        db.session.commit()
        
        # Return PDF file
        filename = f"MDCAN_BDM_2025_{'Service' if participant.certificate_type == 'service' else 'Certificate'}_{participant.name.replace(' ', '_')}.pdf"
        
        def remove_file(response):
            try:
                os.unlink(pdf_path)
            except:
                pass
            return response
        
        return send_file(
            pdf_path,
            as_attachment=True,
            download_name=filename,
            mimetype='application/pdf'
        )
        
    except Exception as e:
        return jsonify({'error': f'Certificate download failed: {str(e)}'}), 500


@app.route('/api/participants/<participant_email>/certificate/preview', methods=['GET'])
def preview_certificate(participant_email):
    """Preview certificate for a participant"""
    try:
        participant = Participant.query.filter_by(email=participant_email).first()
        if not participant:
            return jsonify({'error': 'Participant not found'}), 404
        
        # Generate certificate PDF
        pdf_path = generate_certificate_pdf(participant.name, participant.certificate_type)
        if not pdf_path:
            return jsonify({'error': 'Failed to generate certificate preview'}), 500
        
        def remove_file(response):
            try:
                os.unlink(pdf_path)
            except:
                pass
            return response
        
        # Return PDF for inline viewing
        response = send_file(
            pdf_path,
            as_attachment=False,
            mimetype='application/pdf'
        )
        response.call_on_close(lambda: remove_file(response))
        
        return response
        
    except Exception as e:
        return jsonify({'error': f'Certificate preview failed: {str(e)}'}), 500


@app.route('/api/certificates/bulk-generate', methods=['POST'])
def bulk_generate_certificates():
    """Mark participants as attended and make certificates available"""
    try:
        data = request.json
        participant_ids = data.get('participant_ids', [])
        
        if not participant_ids:
            # Mark all confirmed participants as attended
            participants = Participant.query.filter(
                Participant.registration_status.in_(['confirmed', 'registered'])
            ).all()
        else:
            participants = Participant.query.filter(
                Participant.id.in_(participant_ids)
            ).all()
        
        updated_count = 0
        for participant in participants:
            if participant.registration_status != 'attended':
                participant.registration_status = 'attended'
                participant.event_attendance = True
                participant.certificate_status = 'pending'  # Make certificate available
                updated_count += 1
        
        db.session.commit()
        
        return jsonify({
            'message': f'Certificates made available for {updated_count} participants',
            'updated_count': updated_count
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Bulk certificate generation failed: {str(e)}'}), 500


# ============================================================================
# ATTENDANCE & SESSION MANAGEMENT APIs
# ============================================================================

@app.route('/api/programs/<int:program_id>/attendance', methods=['POST'])
def mark_attendance(program_id):
    """Mark attendance for participants in a session"""
    try:
        data = request.json
        attendance_data = data.get('attendance', [])  # [{'participant_id': 1, 'status': 'attended'}]
        
        program = ConferenceProgram.query.get_or_404(program_id)
        
        updated_count = 0
        for item in attendance_data:
            participant_id = item.get('participant_id')
            status = item.get('status', 'attended')
            
            # Find or create session registration
            registration = SessionRegistration.query.filter_by(
                participant_id=participant_id,
                program_id=program_id
            ).first()
            
            if registration:
                registration.attendance_status = status
                updated_count += 1
            else:
                # Create registration record for attendance
                registration = SessionRegistration(
                    participant_id=participant_id,
                    program_id=program_id,
                    attendance_status=status
                )
                db.session.add(registration)
                updated_count += 1
        
        db.session.commit()
        
        return jsonify({
            'message': f'Attendance marked for {updated_count} participants',
            'updated_count': updated_count
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Failed to mark attendance: {str(e)}'}), 500


@app.route('/api/participants/<int:participant_id>/sessions', methods=['GET'])
def get_participant_sessions(participant_id):
    """Get all sessions for a participant with attendance status"""
    try:
        participant = Participant.query.get_or_404(participant_id)
        
        sessions = db.session.query(SessionRegistration, ConferenceProgram).join(
            ConferenceProgram, SessionRegistration.program_id == ConferenceProgram.id
        ).filter(SessionRegistration.participant_id == participant_id).all()
        
        session_data = []
        for registration, program in sessions:
            session_data.append({
                'registration': registration.to_dict(),
                'program': program.to_dict(),
                'can_provide_feedback': (
                    registration.attendance_status == 'attended' and 
                    program.status == 'completed'
                )
            })
        
        return jsonify({
            'participant': participant.to_dict(),
            'sessions': session_data,
            'total_registered': len(sessions),
            'total_attended': len([r for r, p in sessions if r.attendance_status == 'attended'])
        })
        
    except Exception as e:
        return jsonify({'error': f'Failed to get participant sessions: {str(e)}'}), 500


@app.route('/api/sessions/<int:registration_id>/feedback', methods=['POST'])
def submit_session_feedback(registration_id):
    """Submit feedback for a session"""
    try:
        registration = SessionRegistration.query.get_or_404(registration_id)
        data = request.json
        
        # Validate participant attended the session
        if registration.attendance_status != 'attended':
            return jsonify({'error': 'Feedback can only be submitted for attended sessions'}), 400
        
        # Update feedback
        rating = data.get('rating')
        if rating is not None:
            if not (1 <= rating <= 5):
                return jsonify({'error': 'Rating must be between 1 and 5'}), 400
            registration.rating = rating
        
        if 'feedback' in data:
            registration.feedback = data['feedback'].strip() or None
        
        db.session.commit()
        
        return jsonify({
            'message': 'Feedback submitted successfully',
            'registration': registration.to_dict()
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Failed to submit feedback: {str(e)}'}), 500


# ============================================================================
# REPORTING & ANALYTICS APIs
# ============================================================================

@app.route('/api/reports/conference-summary', methods=['GET'])
def get_conference_summary():
    """Get comprehensive conference statistics and summary"""
    try:
        # Participant statistics
        total_participants = Participant.query.count()
        by_type = db.session.query(
            Participant.registration_type,
            db.func.count(Participant.id)
        ).group_by(Participant.registration_type).all()
        
        by_status = db.session.query(
            Participant.registration_status,
            db.func.count(Participant.id)
        ).group_by(Participant.registration_status).all()
        
        # Program statistics
        total_programs = ConferenceProgram.query.count()
        program_types = db.session.query(
            ConferenceProgram.program_type,
            db.func.count(ConferenceProgram.id)
        ).group_by(ConferenceProgram.program_type).all()
        
        # Session registration statistics
        total_registrations = SessionRegistration.query.count()
        attendance_stats = db.session.query(
            SessionRegistration.attendance_status,
            db.func.count(SessionRegistration.id)
        ).group_by(SessionRegistration.attendance_status).all()
        
        # Certificate statistics
        certificate_stats = db.session.query(
            Participant.certificate_status,
            db.func.count(Participant.id)
        ).group_by(Participant.certificate_status).all()
        
        # Top-rated sessions
        top_sessions = db.session.query(
            ConferenceProgram.title,
            db.func.avg(SessionRegistration.rating).label('avg_rating'),
            db.func.count(SessionRegistration.rating).label('rating_count')
        ).join(SessionRegistration).filter(
            SessionRegistration.rating.isnot(None)
        ).group_by(ConferenceProgram.id, ConferenceProgram.title).order_by(
            db.func.avg(SessionRegistration.rating).desc()
        ).limit(5).all()
        
        summary = {
            'participants': {
                'total': total_participants,
                'by_type': dict(by_type),
                'by_status': dict(by_status)
            },
            'programs': {
                'total': total_programs,
                'by_type': dict(program_types)
            },
            'sessions': {
                'total_registrations': total_registrations,
                'attendance': dict(attendance_stats)
            },
            'certificates': {
                'by_status': dict(certificate_stats)
            },
            'feedback': {
                'top_rated_sessions': [
                    {
                        'title': title,
                        'average_rating': float(avg_rating),
                        'rating_count': rating_count
                    } for title, avg_rating, rating_count in top_sessions
                ]
            }
        }
        
        return jsonify(summary)
        
    except Exception as e:
        return jsonify({'error': f'Failed to generate conference summary: {str(e)}'}), 500


@app.route('/api/reports/export/<format>', methods=['GET'])
def export_report(format):
    """Export participant and session data in various formats"""
    try:
        if format not in ['csv', 'excel']:
            return jsonify({'error': 'Supported formats: csv, excel'}), 400
        
        # Get participants with session data
        participants = Participant.query.all()
        
        # Prepare data for export
        export_data = []
        for participant in participants:
            # Get session statistics
            sessions = SessionRegistration.query.filter_by(participant_id=participant.id).all()
            attended_sessions = [s for s in sessions if s.attendance_status == 'attended']
            
            row = {
                'Name': participant.name,
                'Email': participant.email,
                'Phone': participant.phone_number,
                'Organization': participant.organization,
                'Position': participant.position,
                'Registration Type': participant.registration_type,
                'Registration Status': participant.registration_status,
                'Certificate Type': participant.certificate_type,
                'Certificate Status': participant.certificate_status,
                'Registration Date': participant.created_at.strftime('%Y-%m-%d %H:%M:%S'),
                'Total Sessions Registered': len(sessions),
                'Total Sessions Attended': len(attended_sessions),
                'Event Attendance': 'Yes' if participant.event_attendance else 'No',
                'Email Notifications': 'Yes' if participant.email_notifications else 'No'
            }
            export_data.append(row)
        
        # Create DataFrame
        df = pd.DataFrame(export_data)
        
        # Generate file
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        
        if format == 'csv':
            filename = f'mdcan_bdm_2025_participants_{timestamp}.csv'
            filepath = os.path.join(tempfile.gettempdir(), filename)
            df.to_csv(filepath, index=False)
            
            return send_file(
                filepath,
                as_attachment=True,
                download_name=filename,
                mimetype='text/csv'
            )
            
        elif format == 'excel':
            filename = f'mdcan_bdm_2025_participants_{timestamp}.xlsx'
            filepath = os.path.join(tempfile.gettempdir(), filename)
            
            with pd.ExcelWriter(filepath, engine='openpyxl') as writer:
                df.to_excel(writer, sheet_name='Participants', index=False)
                
                # Add program summary sheet
                programs = ConferenceProgram.query.all()
                program_data = [p.to_dict() for p in programs]
                program_df = pd.DataFrame(program_data)
                program_df.to_excel(writer, sheet_name='Programs', index=False)
            
            return send_file(
                filepath,
                as_attachment=True,
                download_name=filename,
                mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
            )
            
    except Exception as e:
        return jsonify({'error': f'Export failed: {str(e)}'}), 500


# ============================================================================
# STATIC FILE SERVING & FRONTEND ROUTES
# ============================================================================

# Serve React app static files
@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def serve_react_app(path):
    try:
        print(f"Requested path: {path}")
        
        # Skip static files - they're handled by Flask's built-in static serving
        if path.startswith('static/'):
            # This should not happen since static files are handled by Flask
            return jsonify({'error': 'Static file routing error'}), 404
        
        # Serve other static files (images, etc.)
        if path != "":
            static_file_path = os.path.join('../frontend/build', path)
            print(f"Checking file: {static_file_path}")
            print(f"File exists: {os.path.exists(static_file_path)}")
            if os.path.exists(static_file_path):
                print(f"Serving file: {static_file_path}")
                return send_file(static_file_path)
        
        # For root path or any other routes, serve index.html (React Router)
        index_path = '../frontend/build/index.html'
        print(f"Serving index.html: {index_path}")
        if os.path.exists(index_path):
            return send_file(index_path)
        else:
            return jsonify({'error': 'Frontend not built. Please run build script first.'}), 500
    except Exception as e:
        print(f"Error: {str(e)}")
        return jsonify({'error': f'Error serving frontend: {str(e)}'}), 500


# Serve certificate assets
@app.route('/certificate_background.png')
def serve_certificate_background():
    return send_file('../public/certificate_background.png')

@app.route('/mdcan-logo.png')
def serve_mdcan_logo():
    return send_file('../public/logo-mdcan.png')

@app.route('/coalcity-logo.png')
def serve_coalcity_logo():
    return send_file('../public/coalcity-logo.png')

@app.route('/president-signature.png')
def serve_president_signature():
    return send_file('../public/president-signature.png')

@app.route('/chairman-signature.png')
def serve_chairman_signature():
    return send_file('../public/chairman-signature.png')


# Initialize scheduler for automatic notifications
# ============================================================================
# CONFERENCE MATERIALS, ANNOUNCEMENTS & CHECK-IN APIs
# ============================================================================

def allowed_file(filename, allowed_extensions):
    """Check if a file has an allowed extension"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in allowed_extensions


def generate_unique_filename(original_filename):
    """Generate a unique filename by adding a timestamp and UUID"""
    name, ext = os.path.splitext(original_filename)
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    unique_id = str(uuid.uuid4())[:8]
    return f"{name}_{timestamp}_{unique_id}{ext}"


def get_file_details(file_path):
    """Get file details such as size and extension"""
    if os.path.exists(file_path):
        size = os.path.getsize(file_path)
        _, ext = os.path.splitext(file_path)
        return size, ext.lower().lstrip('.')
    return None, None


def send_certificate_to_checked_in_participants():
    """Automatically send certificates to participants who checked in"""
    try:
        # Get unique participants who checked in at least once
        checked_in_participants = db.session.query(Participant).join(
            CheckIn, Participant.id == CheckIn.participant_id
        ).filter(
            Participant.certificate_status == 'pending'
        ).distinct().all()
        
        sent_count = 0
        failed_count = 0
        
        for participant in checked_in_participants:
            try:
                # Generate certificate PDF
                pdf_path = generate_certificate_pdf(participant.name, participant.certificate_type)
                
                if pdf_path and send_email_with_certificate(participant.name, participant.email, pdf_path, participant.certificate_type):
                    participant.certificate_status = 'sent'
                    sent_count += 1
                    
                    # Log the successful certificate sending
                    log_entry = CertificateLog(
                        participant_id=participant.id,
                        action='sent',
                        status='success',
                        email_subject=f"Your {participant.certificate_type.title()} Certificate - MDCAN BDM 2025",
                        timestamp=datetime.utcnow()
                    )
                    db.session.add(log_entry)
                else:
                    participant.certificate_status = 'failed'
                    failed_count += 1
            except Exception as e:
                print(f"Error sending certificate to {participant.name}: {e}")
                participant.certificate_status = 'failed'
                failed_count += 1
                
                # Log the failed certificate sending
                log_entry = CertificateLog(
                    participant_id=participant.id,
                    action='sent',
                    status='failed',
                    error_message=str(e),
                    timestamp=datetime.utcnow()
                )
                db.session.add(log_entry)
        
        db.session.commit()
        return sent_count, failed_count
    except Exception as e:
        print(f"Error in bulk certificate sending: {e}")
        db.session.rollback()
        return 0, 0


@app.route('/api/materials', methods=['GET'])
def get_materials():
    """Get all conference materials with optional filtering by type"""
    try:
        material_type = request.args.get('type')
        query = ConferenceMaterial.query
        
        if material_type:
            query = query.filter_by(material_type=material_type)
        
        # Only show published materials to regular users
        if request.args.get('show_all') != 'true':
            query = query.filter_by(is_published=True)
            
        materials = query.order_by(ConferenceMaterial.created_at.desc()).all()
        return jsonify([m.to_dict() for m in materials])
    except Exception as e:
        print(f"Error getting materials: {e}")
        return jsonify({'error': f'Failed to retrieve materials: {str(e)}'}), 500


@app.route('/api/materials', methods=['POST'])
def upload_material():
    """Upload a new conference material (brochure, video, image)"""
    try:
        if 'file' not in request.files:
            return jsonify({'error': 'No file part'}), 400
            
        file = request.files['file']
        if file.filename == '':
            return jsonify({'error': 'No selected file'}), 400
            
        material_type = request.form.get('type', 'brochure')
        
        # Validate file type
        allowed_extensions = ALLOWED_BROCHURE_EXTENSIONS if material_type == 'brochure' else ALLOWED_MEDIA_EXTENSIONS
        if not allowed_file(file.filename, allowed_extensions):
            return jsonify({'error': f'File type not allowed. Allowed types: {", ".join(allowed_extensions)}'}), 400
        
        # Generate unique filename and save file
        filename = generate_unique_filename(secure_filename(file.filename))
        folder = BROCHURE_FOLDER if material_type == 'brochure' else MEDIA_FOLDER
        file_path = os.path.join(folder, filename)
        file.save(file_path)
        
        # Get file details
        file_size, file_extension = get_file_details(file_path)
        
        # Create database entry
        material = ConferenceMaterial(
            title=request.form.get('title', 'Untitled Material'),
            description=request.form.get('description', ''),
            material_type=material_type,
            file_path=os.path.relpath(file_path, UPLOAD_FOLDER),
            file_size=file_size,
            file_extension=file_extension,
            is_published=request.form.get('is_published', 'true').lower() == 'true',
            created_by=request.form.get('created_by', 'admin')
        )
        
        db.session.add(material)
        db.session.commit()
        
        return jsonify({
            'message': f'{material_type.title()} uploaded successfully',
            'material': material.to_dict()
        }), 201
    except Exception as e:
        print(f"Error uploading material: {e}")
        return jsonify({'error': f'Failed to upload material: {str(e)}'}), 500


@app.route('/api/materials/<int:material_id>', methods=['DELETE'])
def delete_material(material_id):
    """Delete a conference material"""
    try:
        material = ConferenceMaterial.query.get_or_404(material_id)
        
        # Delete the file
        file_path = os.path.join(UPLOAD_FOLDER, material.file_path)
        if os.path.exists(file_path):
            os.remove(file_path)
        
        # Delete database record
        db.session.delete(material)
        db.session.commit()
        
        return jsonify({'message': f'{material.material_type.title()} deleted successfully'})
    except Exception as e:
        db.session.rollback()
        print(f"Error deleting material: {e}")
        return jsonify({'error': f'Failed to delete material: {str(e)}'}), 500


@app.route('/api/materials/<int:material_id>/download', methods=['GET'])
def download_material(material_id):
    """Download a conference material"""
    try:
        material = ConferenceMaterial.query.get_or_404(material_id)
        
        # Increment download counter
        material.download_count += 1
        db.session.commit()
        
        # Send file
        file_path = os.path.join(UPLOAD_FOLDER, material.file_path)
        if not os.path.exists(file_path):
            return jsonify({'error': 'File not found'}), 404
            
        return send_file(
            file_path,
            as_attachment=True, 
            download_name=os.path.basename(material.file_path),
            mimetype=mimetypes.guess_type(file_path)[0]
        )
    except Exception as e:
        print(f"Error downloading material: {e}")
        return jsonify({'error': f'Failed to download material: {str(e)}'}), 500


@app.route('/api/announcements', methods=['GET'])
def get_announcements():
    """Get all announcements"""
    try:
        # Only show published announcements to regular users
        if request.args.get('show_all') != 'true':
            announcements = Announcement.query.filter_by(is_published=True).order_by(Announcement.created_at.desc()).all()
        else:
            announcements = Announcement.query.order_by(Announcement.created_at.desc()).all()
            
        return jsonify([a.to_dict() for a in announcements])
    except Exception as e:
        print(f"Error getting announcements: {e}")
        return jsonify({'error': f'Failed to retrieve announcements: {str(e)}'}), 500


@app.route('/api/announcements', methods=['POST'])
def create_announcement():
    """Create a new announcement with optional attachment"""
    try:
        data = request.form
        attachment = request.files.get('attachment')
        attachment_path = None
        
        # Handle attachment if provided
        if attachment and attachment.filename != '':
            filename = generate_unique_filename(secure_filename(attachment.filename))
            attachment_path = os.path.join(ANNOUNCEMENT_FOLDER, filename)
            attachment.save(attachment_path)
            attachment_path = os.path.relpath(attachment_path, UPLOAD_FOLDER)
        
        # Create announcement
        announcement = Announcement(
            title=data.get('title'),
            content=data.get('content'),
            priority=data.get('priority', 'normal'),
            attachment_path=attachment_path,
            is_published=data.get('is_published', 'true').lower() == 'true',
            notify_participants=data.get('notify_participants', 'true').lower() == 'true',
            created_by=data.get('created_by', 'admin')
        )
        
        if announcement.is_published:
            announcement.published_at = datetime.utcnow()
        
        db.session.add(announcement)
        db.session.commit()
        
        # Send notifications if requested
        if announcement.notify_participants and announcement.is_published:
            try:
                # Get participants who opted for notifications
                participants = Participant.query.filter_by(email_notifications=True).all()
                
                # Create notification record
                notification = Notification(
                    title=f"Announcement: {announcement.title}",
                    message=announcement.content,
                    notification_type='general_announcement',
                    target_audience='all',
                    scheduled_time=datetime.utcnow(),
                    sent_at=datetime.utcnow(),
                    send_email=True,
                    send_push=True,
                    status='sent',
                    created_by=announcement.created_by
                )
                db.session.add(notification)
                
                # Send emails to participants
                for participant in participants:
                    send_notification_email(
                        participant.email, 
                        participant.name, 
                        f"MDCAN BDM 2025 Announcement: {announcement.title}", 
                        f"""
                        <div class="highlight">
                            <strong>Important Announcement</strong>
                        </div>
                        
                        <h3>{announcement.title}</h3>
                        
                        <div style="margin: 20px 0; padding: 15px; background-color: #f5f5f5; border-left: 4px solid #1a365d; border-radius: 5px;">
                            {announcement.content}
                        </div>
                        
                        <p>{f'An attachment is available in the conference portal.' if announcement.attachment_path else ''}</p>
                        """
                    )
                
                announcement.notification_sent = True
                db.session.commit()
            except Exception as e:
                print(f"Error sending announcement notifications: {e}")
        
        return jsonify({
            'message': 'Announcement created successfully',
            'announcement': announcement.to_dict()
        }), 201
    except Exception as e:
        db.session.rollback()
        print(f"Error creating announcement: {e}")
        return jsonify({'error': f'Failed to create announcement: {str(e)}'}), 500


@app.route('/api/announcements/<int:announcement_id>/attachment', methods=['GET'])
def download_announcement_attachment(announcement_id):
    """Download an announcement attachment"""
    try:
        announcement = Announcement.query.get_or_404(announcement_id)
        
        if not announcement.attachment_path:
            return jsonify({'error': 'No attachment available'}), 404
            
        # Increment view counter
        announcement.view_count += 1
        db.session.commit()
        
        # Send file
        file_path = os.path.join(UPLOAD_FOLDER, announcement.attachment_path)
        if not os.path.exists(file_path):
            return jsonify({'error': 'Attachment file not found'}), 404
            
        return send_file(
            file_path,
            as_attachment=True, 
            download_name=os.path.basename(announcement.attachment_path),
            mimetype=mimetypes.guess_type(file_path)[0]
        )
    except Exception as e:
        print(f"Error downloading attachment: {e}")
        return jsonify({'error': f'Failed to download attachment: {str(e)}'}), 500


@app.route('/api/check-in', methods=['POST'])
def check_in_participant():
    """Check in a participant for a specific day of the conference"""
    try:
        data = request.json
        
        # Validate required fields
        if not data.get('participant_id') or not data.get('check_in_day'):
            return jsonify({'error': 'Participant ID and check-in day are required'}), 400
            
        # Validate conference day
        check_in_day = int(data.get('check_in_day'))
        if check_in_day < 1 or check_in_day > 6:
            return jsonify({'error': 'Invalid conference day. Must be between 1 and 6'}), 400
            
        # Check if participant exists
        participant = Participant.query.get(data.get('participant_id'))
        if not participant:
            return jsonify({'error': 'Participant not found'}), 404
            
        # Check if already checked in for this day
        existing_check_in = CheckIn.query.filter_by(
            participant_id=participant.id,
            check_in_day=check_in_day
        ).first()
        
        if existing_check_in:
            return jsonify({'error': 'Participant already checked in for this day', 'check_in': existing_check_in.to_dict()}), 400
            
        # Create check-in record
        check_in = CheckIn(
            participant_id=participant.id,
            check_in_day=check_in_day,
            materials_received=data.get('materials_received', False),
            verified_by=data.get('verified_by', 'admin'),
            verification_method=data.get('verification_method', 'manual'),
            notes=data.get('notes', ''),
            ip_address=request.remote_addr
        )
        
        db.session.add(check_in)
        
        # Update participant attendance status
        participant.event_attendance = True
        if participant.first_attendance_date is None:
            participant.first_attendance_date = datetime.utcnow()
        participant.last_attendance_date = datetime.utcnow()
        
        db.session.commit()
        
        # If last day of conference and automatic certificate sending is enabled
        if check_in_day == 6:
            # Schedule certificate sending at the end of the day
            # This will run in the background
            scheduler.add_job(
                func=send_certificate_to_checked_in_participants,
                trigger="date",
                run_date=datetime.utcnow() + timedelta(hours=3),
                id=f'send_certificates_{datetime.utcnow().strftime("%Y%m%d%H%M%S")}'
            )
        
        return jsonify({
            'message': f'Participant checked in successfully for day {check_in_day}',
            'check_in': check_in.to_dict()
        }), 201
    except Exception as e:
        db.session.rollback()
        print(f"Error checking in participant: {e}")
        return jsonify({'error': f'Failed to check in participant: {str(e)}'}), 500


@app.route('/api/check-in/report', methods=['GET'])
def get_check_in_report():
    """Get check-in report with statistics"""
    try:
        # Get statistics for each day
        stats = []
        for day in range(1, 7):
            day_stats = {
                'day': day,
                'date': (datetime(2025, 9, day)).strftime('%Y-%m-%d'),
                'total_checked_in': CheckIn.query.filter_by(check_in_day=day).count(),
                'materials_received': CheckIn.query.filter_by(check_in_day=day, materials_received=True).count()
            }
            stats.append(day_stats)
            
        # Get unique participants who checked in at least once
        unique_participants = db.session.query(Participant).join(
            CheckIn, Participant.id == CheckIn.participant_id
        ).distinct().count()
        
        # Get participants who never checked in
        total_participants = Participant.query.count()
        never_checked_in = total_participants - unique_participants
        
        return jsonify({
            'daily_stats': stats,
            'unique_participants': unique_participants,
            'never_checked_in': never_checked_in,
            'total_participants': total_participants,
            'check_in_percentage': round((unique_participants / total_participants * 100), 2) if total_participants > 0 else 0
        })
    except Exception as e:
        print(f"Error generating check-in report: {e}")
        return jsonify({'error': f'Failed to generate check-in report: {str(e)}'}), 500


@app.route('/api/check-in/participant/<int:participant_id>', methods=['GET'])
def get_participant_check_ins(participant_id):
    """Get all check-ins for a specific participant"""
    try:
        participant = Participant.query.get_or_404(participant_id)
        check_ins = CheckIn.query.filter_by(participant_id=participant_id).order_by(CheckIn.check_in_day).all()
        
        # Build attendance record by day
        attendance = []
        for day in range(1, 7):
            # Find if participant checked in for this day
            day_check_in = next((c for c in check_ins if c.check_in_day == day), None)
            
            attendance.append({
                'day': day,
                'date': (datetime(2025, 9, day)).strftime('%Y-%m-%d'),
                'checked_in': day_check_in is not None,
                'check_in_time': day_check_in.check_in_time.isoformat() if day_check_in else None,
                'materials_received': day_check_in.materials_received if day_check_in else False
            })
        
        return jsonify({
            'participant': participant.to_dict(),
            'attendance': attendance,
            'total_days_attended': len(check_ins),
            'has_full_attendance': len(check_ins) >= 5,  # Attended at least 5 days
            'materials_received': any(c.materials_received for c in check_ins)
        })
    except Exception as e:
        print(f"Error getting participant check-ins: {e}")
        return jsonify({'error': f'Failed to get participant check-ins: {str(e)}'}), 500


@app.route('/api/check-in/search', methods=['GET'])
def search_participants_for_check_in():
    """Search participants for check-in by name, email, or registration number"""
    try:
        query = request.args.get('q', '')
        if not query or len(query) < 3:
            return jsonify({'error': 'Search query must be at least 3 characters'}), 400
            
        # Search for matching participants
        participants = Participant.query.filter(
            (Participant.name.ilike(f'%{query}%')) | 
            (Participant.email.ilike(f'%{query}%')) | 
            (Participant.certificate_number.ilike(f'%{query}%'))
        ).limit(10).all()
        
        results = []
        for participant in participants:
            # Get check-in info for this participant
            check_ins = CheckIn.query.filter_by(participant_id=participant.id).all()
            checked_in_days = [c.check_in_day for c in check_ins]
            
            results.append({
                'participant': participant.to_dict(),
                'checked_in_days': checked_in_days,
                'has_checked_in_today': datetime.utcnow().day - 31 in checked_in_days,  # Assumes September (day-31)
                'total_days_attended': len(checked_in_days)
            })
            
        return jsonify(results)
    except Exception as e:
        print(f"Error searching participants: {e}")
        return jsonify({'error': f'Failed to search participants: {str(e)}'}), 500


@app.route('/api/send-certificates/checked-in', methods=['POST'])
def trigger_certificates_for_checked_in():
    """Manually trigger sending certificates to all checked-in participants"""
    try:
        sent_count, failed_count = send_certificate_to_checked_in_participants()
        
        return jsonify({
            'message': f'Certificate sending triggered for checked-in participants. Sent: {sent_count}, Failed: {failed_count}',
            'sent_count': sent_count,
            'failed_count': failed_count
        })
    except Exception as e:
        print(f"Error triggering certificate sending: {e}")
        return jsonify({'error': f'Failed to trigger certificate sending: {str(e)}'}), 500


def init_scheduler():
    """Initialize background scheduler for automatic notifications"""
    try:
        # Schedule reminder checks every 15 minutes
        scheduler.add_job(
            func=send_program_reminder,
            trigger="interval",
            minutes=15,
            id='program_reminders'
        )
        
        print("✅ Scheduler initialized successfully")
    except Exception as e:
        print(f"❌ Failed to initialize scheduler: {e}")


# Start scheduler when app starts
init_scheduler()

# Test endpoint to generate a certificate for testing
@app.route('/api/generate-test-certificate/<cert_type>', methods=['GET'])
def generate_test_certificate(cert_type):
    """Generate a test certificate for immediate viewing"""
    if cert_type not in ['participation', 'service']:
        return jsonify({'error': 'Invalid certificate type'}), 400
    
    # Use a fixed test name
    test_name = "Test Participant" if cert_type == 'participation' else "Test Volunteer"
    
    # Generate the certificate
    pdf_path = generate_certificate_pdf(test_name, cert_type)
    if not pdf_path:
        return jsonify({'error': 'Failed to generate test certificate'}), 500
    
    # Return PDF for inline viewing
    response = send_file(
        pdf_path,
        as_attachment=False,
        mimetype='application/pdf'
    )
    
    # Add callback to remove the file after sending
    @after_this_request
    def cleanup(response):
        try:
            os.unlink(pdf_path)
        except:
            pass
        return response
    
    return response

# HTML fallback for certificate preview when PDF generation fails
@app.route('/api/generate-test-certificate-html/<cert_type>', methods=['GET'])
def generate_test_certificate_html(cert_type):
    """Generate a test certificate in HTML format for immediate viewing"""
    if cert_type not in ['participation', 'service']:
        return jsonify({'error': 'Invalid certificate type'}), 400
    
    # Use a fixed test name
    test_name = "Test Participant" if cert_type == 'participation' else "Test Volunteer"
    
    try:
        # Get base directory and potential signature file locations
        base_dir = os.getcwd()
        
        possible_directories = [
            os.path.join(base_dir, 'frontend', 'public'),
            os.path.join(base_dir, 'public'),
            os.path.join(base_dir, 'backend', 'static'),
            os.path.join(base_dir)
        ]
        
        # Search for signature files in potential directories
        president_signature = None
        chairman_signature = None
        mdcan_logo = None
        coalcity_logo = None
        
        for directory in possible_directories:
            # Check for president signature
            president_path = os.path.join(directory, 'president-signature.png')
            if president_signature is None and os.path.exists(president_path):
                president_signature = '/serve_asset/president-signature.png'
            
            # Check for chairman signature
            chairman_path = os.path.join(directory, 'chairman-signature.png')
            if chairman_signature is None and os.path.exists(chairman_path):
                chairman_signature = '/serve_asset/chairman-signature.png'
            
            # Check for MDCAN logo
            mdcan_path = os.path.join(directory, 'mdcan-logo.png')
            if mdcan_logo is None and os.path.exists(mdcan_path):
                mdcan_logo = '/serve_asset/mdcan-logo.png'
            
            # Check for Coal City logo
            coalcity_path = os.path.join(directory, 'coalcity-logo.png')
            if coalcity_logo is None and os.path.exists(coalcity_path):
                coalcity_logo = '/serve_asset/coalcity-logo.png'
            
            # If all found, exit loop
            if president_signature and chairman_signature and mdcan_logo and coalcity_logo:
                break
        
        # Log signature paths for debugging
        print(f"MDCAN logo path: {mdcan_logo}")
        print(f"Coal City logo path: {coalcity_logo}")
        print(f"President signature path: {president_signature}")
        print(f"Chairman signature path: {chairman_signature}")
        
        # Determine certificate title and content
        if cert_type == 'service':
            certificate_title = 'ACKNOWLEDGEMENT OF SERVICE'
            content_template = Template(SERVICE_CONTENT)
        else:
            certificate_title = 'CERTIFICATE OF PARTICIPATION'
            content_template = Template(PARTICIPATION_CONTENT)
        
        # Generate content
        certificate_content = content_template.render(participant_name=test_name)
        
        # Create HTML from template
        template = Template(CERTIFICATE_HTML)
        html_content = template.render(
            certificate_title=certificate_title,
            certificate_content=certificate_content,
            participant_name=test_name,
            president_signature=president_signature,
            chairman_signature=chairman_signature,
            mdcan_logo=mdcan_logo,
            coalcity_logo=coalcity_logo
        )
        
        # Add additional styling for browser preview
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Certificate Preview - HTML Version</title>
            <style>
                body {{
                    font-family: Arial, sans-serif;
                    margin: 0;
                    padding: 0;
                }}
                .container {{
                    max-width: 1100px;
                    margin: 0 auto;
                    padding: 20px;
                }}
                .info-banner {{
                    background-color: #f8d7da;
                    color: #721c24;
                    padding: 10px 15px;
                    margin-bottom: 20px;
                    border-radius: 4px;
                    border: 1px solid #f5c6cb;
                }}
                .info-banner h3 {{
                    margin-top: 0;
                }}
                .certificate-frame {{
                    border: 1px solid #ddd;
                    padding: 20px;
                    background-color: #f9f9f9;
                }}
                .action-buttons {{
                    margin-top: 20px;
                    text-align: center;
                }}
                .action-button {{
                    background-color: #4CAF50;
                    color: white;
                    padding: 10px 15px;
                    border: none;
                    border-radius: 4px;
                    cursor: pointer;
                    font-size: 16px;
                    margin: 5px;
                    text-decoration: none;
                    display: inline-block;
                }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="info-banner">
                    <h3>Certificate HTML Preview</h3>
                    <p>This is an HTML preview of the certificate because PDF generation requires wkhtmltopdf to be installed.</p>
                    <p>To enable PDF generation, please run the <strong>setup-wkhtmltopdf.bat</strong> script in the project root directory.</p>
                </div>
                
                <div class="certificate-frame">
                    {html_content}
                </div>
                
                <div class="action-buttons">
                    <a href="/certificate-text-test" class="action-button">Back to Test Page</a>
                    <a href="/api/generate-test-certificate-html/{'service' if cert_type == 'participation' else 'participation'}" class="action-button">
                        Try {{'Service' if cert_type == 'participation' else 'Participation'}} Certificate
                    </a>
                </div>
            </div>
        </body>
        </html>
        """
        
        return html_content
    except Exception as e:
        print(f"Error generating HTML certificate: {e}")
        return jsonify({'error': f'Failed to generate HTML certificate: {str(e)}'}), 500
if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True, port=8080)
