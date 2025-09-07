"""
Enhanced minimal version of the backend app that provides core functionality
without pandas/numpy dependencies for stable deployment.
Version: 2.1.1 - Updated signature paths to prioritize build directory (August 18, 2025)
"""
from flask import Flask, request, jsonify, send_file, render_template_string, send_from_directory, after_this_request
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
import sqlalchemy as sa
from datetime import datetime, timedelta
import os
import sys
import json
import uuid
import tempfile
import base64
import mimetypes
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
from werkzeug.utils import secure_filename
from jinja2 import Template
from threading import Thread
import signal
import threading

# Load environment variables - prioritize container environment over .env files
try:
    from dotenv import load_dotenv
    
    # In production (Docker), don't load .env files as variables come from container
    if os.environ.get('FLASK_ENV') == 'production':
        print("🐳 Production environment detected - using container environment variables")
        print(f"  - PORT: {os.environ.get('PORT', 'not set')}")
        print(f"  - DATABASE_URL: {'configured' if os.environ.get('DATABASE_URL') else 'not configured'}")
        print(f"  - ADMIN_PASSWORD: {'configured' if os.environ.get('ADMIN_PASSWORD') else 'not configured'}")
        print(f"  - EMAIL_HOST: {os.environ.get('EMAIL_HOST', 'not set')}")
        
        # Validate critical environment variables in production
        missing_vars = []
        if not os.environ.get('DATABASE_URL'):
            missing_vars.append('DATABASE_URL')
        if not os.environ.get('ADMIN_PASSWORD'):
            missing_vars.append('ADMIN_PASSWORD')
            
        if missing_vars:
            print(f"❌ CRITICAL: Missing environment variables: {', '.join(missing_vars)}")
            print("   Application may fail to start properly")
        else:
            print("✅ All critical environment variables are configured")
    else:
        # Development environment - try to load .env file
        env_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), '.env')
        if os.path.exists(env_path):
            load_dotenv(env_path)
            print(f"✅ Development - Environment variables loaded from {env_path}")
        else:
            load_dotenv()  # Load from current directory
            print("✅ Development - Environment variables loaded from .env file")
            
except ImportError:
    print("⚠️ python-dotenv not installed, using system environment variables only")
except Exception as e:
    print(f"⚠️ Failed to load .env file: {e} - using system environment variables")

# Optional dependencies with graceful fallback
def generate_pdf_with_timeout(html, config, options, timeout=30):
    """Generate PDF with timeout to prevent hanging"""
    result = {"pdf": None, "error": None}
    
    def pdf_worker():
        try:
            result["pdf"] = pdfkit.from_string(html, False, configuration=config, options=options)
        except Exception as e:
            result["error"] = str(e)
    
    # Start PDF generation in a separate thread
    thread = threading.Thread(target=pdf_worker)
    thread.daemon = True
    thread.start()
    
    # Wait for completion or timeout
    thread.join(timeout)
    
    if thread.is_alive():
        # Thread is still running - timeout occurred
        raise TimeoutError(f"PDF generation timed out after {timeout} seconds")
    
    if result["error"]:
        raise Exception(result["error"])
    
    if result["pdf"] is None:
        raise Exception("PDF generation failed without error message")
    
    return result["pdf"]

try:
    import pdfkit
    
    # Configure wkhtmltopdf path - different for Windows vs Linux/Production
    if os.name == 'nt':  # Windows
        WKHTMLTOPDF_PATH = r'C:\Users\USER\Documents\html2pdf\wkhtmltox\bin\wkhtmltopdf.exe'
    else:  # Linux/Production - try multiple possible paths
        possible_paths = [
            '/usr/local/bin/wkhtmltopdf',  # From GitHub release
            '/usr/bin/wkhtmltopdf',        # From package manager
            'wkhtmltopdf'                  # From PATH
        ]
        WKHTMLTOPDF_PATH = None
        for path in possible_paths:
            if os.path.exists(path) or path == 'wkhtmltopdf':
                WKHTMLTOPDF_PATH = path
                break
    
    # Test if the wkhtmltopdf executable exists and works
    if WKHTMLTOPDF_PATH and WKHTMLTOPDF_PATH != 'wkhtmltopdf':
        if os.path.exists(WKHTMLTOPDF_PATH):
            # Configure pdfkit to use the specific path
            config = pdfkit.configuration(wkhtmltopdf=WKHTMLTOPDF_PATH)
            PDF_CONFIG = config
            PDF_GENERATION_AVAILABLE = True
            print(f"✅ PDF generation available with wkhtmltopdf at: {WKHTMLTOPDF_PATH}")
        else:
            WKHTMLTOPDF_PATH = None
    
    if not WKHTMLTOPDF_PATH:
        # Try default path (in case it's in PATH)
        try:
            config = pdfkit.configuration()
            PDF_CONFIG = config
            PDF_GENERATION_AVAILABLE = True
            print("✅ PDF generation available (using default wkhtmltopdf from PATH)")
        except Exception as e:
            PDF_CONFIG = None
            PDF_GENERATION_AVAILABLE = False
            print(f"⚠️  wkhtmltopdf not found in any location: {e}")
            print("   PDF generation will be disabled")
            
except ImportError as e:
    print(f"⚠️  PDF generation not available: {e}")
    print("   Continuing without PDF generation capability...")
    pdfkit = None
    PDF_CONFIG = None
    PDF_GENERATION_AVAILABLE = False

# Initialize Flask app
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

# Configure static folder for frontend files
# Try multiple possible paths for the frontend build
possible_frontend_paths = [
    'frontend/build',           # From root directory
    '../frontend/build',        # From backend directory  
    './frontend/build',         # Current directory variant
    '/app/frontend/build',      # Docker absolute path
    'build',                    # Direct build folder
]

static_folder = None
FRONTEND_BUILD_FOLDER = None

print(f"Current working directory: {os.getcwd()}")
for path in possible_frontend_paths:
    abs_path = os.path.abspath(path)
    index_exists = os.path.exists(os.path.join(path, 'index.html'))
    print(f"Checking path: {path} (absolute: {abs_path}) - index.html exists: {index_exists}")
    
    if os.path.exists(path) and index_exists:
        static_folder = abs_path  # Use absolute path
        FRONTEND_BUILD_FOLDER = abs_path  # Use absolute path
        print(f"✓ Selected frontend build at: {path} (absolute: {abs_path})")
        break

if not static_folder:
    print("Warning: Frontend build not found. Available files:")
    for root, dirs, files in os.walk('.'):
        if 'index.html' in files:
            print(f"  Found index.html in: {root}")
        if 'build' in dirs:
            print(f"  Found build directory in: {root}")
    # Fallback to static if frontend build doesn't exist
    static_folder = 'static' if os.path.exists('static') else None
    FRONTEND_BUILD_FOLDER = static_folder

# Configure database connection with enhanced error handling
DATABASE_URL = os.environ.get('DATABASE_URL', 'sqlite:///mdcan_certificates.db')

print(f"🔗 Configuring database connection...")

# Handle Digital Ocean managed database URL format
if DATABASE_URL.startswith('postgres://'):
    DATABASE_URL = DATABASE_URL.replace('postgres://', 'postgresql://', 1)
    print("🔧 Converted postgres:// to postgresql:// for compatibility")

# For Digital Ocean PostgreSQL, ensure proper SSL configuration
if 'postgresql://' in DATABASE_URL:
    if 'sslmode' not in DATABASE_URL:
        separator = '&' if '?' in DATABASE_URL else '?'
        DATABASE_URL = f"{DATABASE_URL}{separator}sslmode=require"
        print("🔒 Added SSL requirement to PostgreSQL connection")
    
    # Ensure we're using the correct SSL mode for DigitalOcean
    if 'sslmode=prefer' in DATABASE_URL:
        DATABASE_URL = DATABASE_URL.replace('sslmode=prefer', 'sslmode=require')
        print("🔒 Upgraded SSL mode from 'prefer' to 'require' for DigitalOcean")

print(f"Database URL configured (sanitized): {DATABASE_URL.split('@')[0] if '@' in DATABASE_URL else 'local'}@***")

app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE_URL
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Enhanced database connection configuration for DigitalOcean
pool_size = int(os.environ.get('DB_POOL_SIZE', 2))  # Reduced for smaller instances
max_overflow = int(os.environ.get('DB_MAX_OVERFLOW', 3))

engine_options = {
    'pool_pre_ping': True,
    'pool_recycle': 300,
    'pool_size': pool_size,
    'max_overflow': max_overflow,
    'pool_timeout': 30,
    'connect_args': {}
}

# Add SSL configuration for PostgreSQL connections
if 'postgresql://' in DATABASE_URL:
    print("🐘 Using PostgreSQL with SSL configuration")
    engine_options['connect_args'] = {
        'sslmode': 'require',
        'connect_timeout': 30
    }
    
app.config['SQLALCHEMY_ENGINE_OPTIONS'] = engine_options

# Initialize database with error handling
try:
    db = SQLAlchemy(app)
    print("✅ SQLAlchemy initialized successfully")
except Exception as e:
    print(f"❌ Failed to initialize SQLAlchemy: {e}")
    raise

# Define database models
class Participant(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), nullable=False)
    role = db.Column(db.String(50), default='Attendee')
    cert_type = db.Column(db.String(50), default='participation')
    registration_number = db.Column(db.String(50), unique=True)
    phone = db.Column(db.String(20))
    gender = db.Column(db.String(10))
    specialty = db.Column(db.String(100))
    state = db.Column(db.String(50))
    hospital = db.Column(db.String(100))
    cert_sent = db.Column(db.Boolean, default=False)
    cert_sent_date = db.Column(db.DateTime)
    certificate_id = db.Column(db.String(50), unique=True)
    date_registered = db.Column(db.DateTime, default=datetime.utcnow)
    registration_status = db.Column(db.String(20), default='Pending')
    registration_fee_paid = db.Column(db.Boolean, default=False)
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'email': self.email,
            'role': self.role,
            'cert_type': self.cert_type,
            'registration_number': self.registration_number,
            'phone': self.phone,
            'gender': self.gender,
            'specialty': self.specialty,
            'state': self.state,
            'hospital': self.hospital,
            'cert_sent': self.cert_sent,
            'cert_sent_date': self.cert_sent_date.isoformat() if self.cert_sent_date else None,
            'certificate_id': self.certificate_id,
            'date_registered': self.date_registered.isoformat() if self.date_registered else None,
            'registration_status': self.registration_status,
            'registration_fee_paid': self.registration_fee_paid
        }
        
# Ensure the database is created (useful for SQLite)
with app.app_context():
    try:
        print("🔗 Testing database connection...")
        # Test database connection first with timeout
        with db.engine.connect() as connection:
            result = connection.execute(sa.text('SELECT 1'))
            print("✅ Database connection successful")
        
        # Create tables if connection is successful
        print("📋 Creating database tables...")
        db.create_all()
        print("✅ Database tables created successfully")
        
        # Test a simple query to ensure everything works
        participant_count = db.session.query(Participant).count()
        print(f"✅ Database operational - {participant_count} participants registered")
        
    except Exception as e:
        print(f"❌ Database initialization error: {e}")
        print("⚠️ Application will start but database functionality may be limited")
        # Log the full stack trace for debugging
        import traceback
        print(f"Full error trace: {traceback.format_exc()}")
        # Don't fail the entire application if database is not available yet

# Email configuration
EMAIL_HOST = os.environ.get('EMAIL_HOST')
EMAIL_PORT = int(os.environ.get('EMAIL_PORT', 587))
EMAIL_USER = os.environ.get('EMAIL_USER')
EMAIL_PASSWORD = os.environ.get('EMAIL_PASSWORD')
EMAIL_FROM = os.environ.get('EMAIL_FROM', 'MDCAN BDM 2025 <noreply@mdcan.org>')

# Certificate template configuration
CERT_EVENT_TEXT = "MEDICAL AND DENTAL CONSULTANTS' ASSOCIATION OF NIGERIA 14th Biennial Delegates' Meeting and SCIENTIFIC Conference on 1st–6th September, 2025"
CERT_SERVICE_TEXT = "the successful hosting of the MEDICAL AND DENTAL CONSULTANTS' ASSOCIATION OF NIGERIA 14th Biennial Delegates' Meeting and SCIENTIFIC Conference on 1st–6th September, 2025"

# Helper function to load and encode signature files
def load_signature_file(filename):
    """Load signature file and return base64 encoded string with proper MIME type"""
    try:
        # Try multiple possible paths for the signature files - prioritize build directory for transparent versions
        static_dir = os.path.join(os.path.dirname(__file__), 'static')
        possible_paths = [
            os.path.join(static_dir, filename),  # Absolute path to backend/static
            filename
        ]
        for path in possible_paths:
            if os.path.exists(path):
                try:
                    with open(path, 'rb') as f:
                        image_data = f.read()
                        # Determine MIME type
                        if filename.lower().endswith('.png'):
                            mime_type = 'image/png'
                        elif filename.lower().endswith(('.jpg', '.jpeg')):
                            mime_type = 'image/jpeg'
                        else:
                            mime_type = 'image/png'  # Default
                        encoded = base64.b64encode(image_data).decode('utf-8')
                        print(f"Loaded signature file: {path} ({len(image_data)} bytes, {mime_type})")
                        return f"data:{mime_type};base64,{encoded}"
                except Exception as e:
                    print(f"Error reading signature file {path}: {e}")
        print(f"Signature file {filename} not found or unreadable in backend/static. Returning empty string.")
        # Optionally, return a placeholder transparent PNG if file is missing
        return ""
        
        for path in possible_paths:
            if os.path.exists(path):
                with open(path, 'rb') as f:
                    image_data = f.read()
                    # Determine MIME type
                    if filename.lower().endswith('.png'):
                        mime_type = 'image/png'
                    elif filename.lower().endswith(('.jpg', '.jpeg')):
                        mime_type = 'image/jpeg'
                    else:
                        mime_type = 'image/png'  # Default
                    
                    encoded = base64.b64encode(image_data).decode('utf-8')
                    print(f"Loaded signature file: {path} ({len(image_data)} bytes, {mime_type})")
                    return f"data:{mime_type};base64,{encoded}"
        
        print(f"Warning: Signature file {filename} not found in any of the expected paths")
        return ""
    except Exception as e:
        print(f"Error loading signature file {filename}: {e}")
        return ""

# Load signature files at startup - using specific paths for better versions
def load_signature_from_path(file_path):
    """Load signature file from specific path"""
    try:
        if os.path.exists(file_path):
            with open(file_path, 'rb') as f:
                image_data = f.read()
                if file_path.lower().endswith('.png'):
                    mime_type = 'image/png'
                elif file_path.lower().endswith(('.jpg', '.jpeg')):
                    mime_type = 'image/jpeg'
                else:
                    mime_type = 'image/png'
                encoded = base64.b64encode(image_data).decode('utf-8')
                print(f"Loaded signature from: {file_path} ({len(image_data)} bytes, {mime_type})")
                return encoded  # Return just the base64 string without data URL prefix
        print(f"Warning: Signature file not found at {file_path}")
        return ""
    except Exception as e:
        print(f"Error loading signature from {file_path}: {e}")
        return ""

# Load signatures from build directory for president and secretary, static for chairman
build_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'build')
static_dir = os.path.join(os.path.dirname(__file__), 'static')
PRESIDENT_SIGNATURE = load_signature_from_path(os.path.join(build_dir, 'president-signature.png'))
CHAIRMAN_SIGNATURE = load_signature_from_path(os.path.join(static_dir, 'chairman-signature.png'))
SECRETARY_SIGNATURE = load_signature_from_path(os.path.join(build_dir, 'Dr_Augustine_Duru_signature.png'))

# Load logo file
MDCAN_LOGO = load_signature_file('logo-mdcan.jpeg')

print(f"Signatures loaded - President: {'✓' if PRESIDENT_SIGNATURE else '✗'}, Chairman: {'✓' if CHAIRMAN_SIGNATURE else '✗'}, Secretary: {'✓' if SECRETARY_SIGNATURE else '✗'}")
print(f"Logo loaded: {'✓' if MDCAN_LOGO else '✗'}")

# Certificate templates
PARTICIPATION_CERTIFICATE_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>Certificate of Participation</title>
    <style>
        body {
            font-family: 'Arial', sans-serif;
            text-align: center;
            margin: 0;
            padding: 0;
            background-color: white;
        }
        .certificate {
            width: 210mm;
            height: 297mm;
            margin: 0 auto;
            padding: 20mm;
            border: 10px solid #00205b;
            position: relative;
            background: white;
        }
        .header {
            font-size: 36px;
            font-weight: bold;
            color: #00205b;
            margin-bottom: 20px;
            text-decoration: underline;
        }
        .content {
            font-size: 24px;
            margin: 30px 0;
            line-height: 1.5;
        }
        .name {
            font-size: 36px;
            font-weight: bold;
            color: #ac0036;
            margin: 20px 0;
        }
        .footer {
            font-size: 18px;
            position: absolute;
            bottom: 40mm;
            width: 80%;
            left: 10%;
        }
        .signature {
            display: inline-block;
            margin: 0 30px;
        }
        .signature img {
            max-height: 60px;
            background: transparent !important;
            border: none;
            opacity: 1;
        }
        .signature-name {
            font-weight: bold;
            margin-top: 10px;
        }
        .signature-title {
            font-style: italic;
        }
        .logo {
            position: absolute;
            top: 20mm;
            left: 20mm;
            max-width: 80px;
        }
        .certificate-id {
            position: absolute;
            bottom: 10mm;
            right: 20mm;
            font-size: 12px;
            color: #666;
        }
    </style>
</head>
<body>
    <div class="certificate">
        <img src="data:image/png;base64,{{ logo }}" class="logo" alt="MDCAN Logo">
        
        <div class="header">CERTIFICATE OF PARTICIPATION</div>
        
        <div class="content">
            This is to certify that
        </div>
        
        <div class="name">{{ name }}</div>
        
        <div class="content">
            participated in the {{ event_text }}
        </div>
        
        <div class="footer">
            <div class="signature">
                <img src="data:image/png;base64,{{ president_signature }}" alt="President's Signature">
                <div class="signature-name">Prof. Aminu Mohammed</div>
                <div class="signature-title">MDCAN President</div>
            </div>
            
            <div class="signature">
                <img src="data:image/png;base64,{{ chairman_signature }}" alt="Chairman's Signature">
                <div class="signature-name">Prof. Appolos Ndukuba</div>
                <div class="signature-title">LOC Chairman</div>
            </div>
        </div>
        
        <div class="certificate-id">Certificate ID: {{ certificate_id }}</div>
    </div>
</body>
</html>
"""

SERVICE_CERTIFICATE_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>Acknowledgement of Service</title>
    <style>
        body {
            font-family: 'Arial', sans-serif;
            text-align: center;
            margin: 0;
            padding: 0;
            background-color: white;
        }
        .certificate {
            width: 210mm;
            height: 297mm;
            margin: 0 auto;
            padding: 20mm;
            border: 10px solid #00205b;
            position: relative;
            background: white;
        }
        .header {
            font-size: 36px;
            font-weight: bold;
            color: #00205b;
            margin-bottom: 20px;
            text-decoration: underline;
        }
        .content {
            font-size: 24px;
            margin: 30px 0;
            line-height: 1.5;
        }
        .name {
            font-size: 36px;
            font-weight: bold;
            color: #ac0036;
            margin: 20px 0;
        }
        .footer {
            font-size: 18px;
            position: absolute;
            bottom: 40mm;
            width: 80%;
            left: 10%;
        }
        .signature {
            display: inline-block;
            margin: 0 30px;
        }
        .signature img {
            max-height: 60px;
            background: transparent !important;
            border: none;
            opacity: 1;
        }
        .signature-name {
            font-weight: bold;
            margin-top: 10px;
        }
        .signature-title {
            font-style: italic;
        }
        .logo {
            position: absolute;
            top: 20mm;
            left: 20mm;
            max-width: 80px;
        }
        .certificate-id {
            position: absolute;
            bottom: 10mm;
            right: 20mm;
            font-size: 12px;
            color: #666;
        }
    </style>
</head>
<body>
    <div class="certificate">
        <img src="data:image/png;base64,{{ logo }}" class="logo" alt="MDCAN Logo">
        
        <div class="header">ACKNOWLEDGEMENT OF SERVICE</div>
        
        <div class="content">
            This is to acknowledge and appreciate the exceptional service of
        </div>
        
        <div class="name">{{ name }}</div>
        
        <div class="content">
            towards {{ service_text }}
        </div>
        
        <div class="footer">
            <div class="signature">
                <img src="data:image/png;base64,{{ chairman_signature }}" alt="Chairman's Signature">
                <div class="signature-name">Prof. Appolos Ndukuba</div>
                <div class="signature-title">LOC Chairman</div>
            </div>
            
            <div class="signature">
                {% if secretary_signature %}
                <img src="data:image/png;base64,{{ secretary_signature }}" alt="Secretary's Signature">
                {% else %}
                <div class="signature-missing">Secretary's Signature Not Available</div>
                {% endif %}
                <div class="signature-name">Dr. Augustine Duru</div>
                <div class="signature-title">LOC Secretary<br/>MDCAN Sec. Gen.</div>
            </div>
        </div>
        
        <div class="certificate-id">Certificate ID: {{ certificate_id }}</div>
    </div>
</body>
</html>
"""

@app.route('/test-simple')
def test_simple():
    """Simple test route to verify routing is working"""
    return "MDCAN BDM 2025 - Route Test Working!"

@app.route('/api/health')
def health():
    """Comprehensive health check endpoint with deployment status"""
    try:
        # Test database connection
        db_status = "unknown"
        try:
            with app.app_context():
                db.session.execute(sa.text("SELECT 1"))
                db_status = "connected"
        except Exception:
            db_status = "disconnected"
        
        health_data = {
            "status": "ok",
            "service": "MDCAN BDM 2025 Certificate Platform",
            "timestamp": datetime.utcnow().isoformat(),
            "database": db_status,
            "environment": os.environ.get('FLASK_ENV', 'development'),
            "port": os.environ.get('PORT', '8080'),
            "pdf_generation": globals().get('PDF_GENERATION_AVAILABLE', False),
            "frontend_build": bool(FRONTEND_BUILD_FOLDER and os.path.exists(FRONTEND_BUILD_FOLDER)),
            "deployment": "DIGITAL_OCEAN_TARGETED_FIXES_v3"
        }
        
        return jsonify(health_data), 200
        
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": str(e),
            "timestamp": datetime.utcnow().isoformat()
        }), 500

@app.route('/health')
def health_check():
    """Enhanced health check endpoint for Digital Ocean load balancer"""
    try:
        # Test database connectivity
        db_status = "unknown"
        try:
            # Simple database query to test connection
            with app.app_context():
                db.session.execute(sa.text('SELECT 1'))
                db_status = "connected"
        except Exception as db_e:
            db_status = f"error: {str(db_e)[:50]}"
        
        # Check environment variables
        env_check = {
            "port": os.environ.get('PORT', 'not set'),
            "database_configured": bool(os.environ.get('DATABASE_URL')),
            "admin_configured": bool(os.environ.get('ADMIN_PASSWORD'))
        }
        
        # Basic imports test
        try:
            import flask
            import sqlalchemy
            import psycopg2
            import gunicorn
            
            return jsonify({
                "status": "healthy",
                "timestamp": datetime.utcnow().isoformat(),
                "service": "mdcan-bdm-2025",
                "database": db_status,
                "environment": env_check,
                "python_version": sys.version.split()[0],
                "flask_version": flask.__version__
            }), 200
            
        except ImportError as ie:
            return jsonify({
                "status": "unhealthy",
                "message": f"Missing dependencies: {ie}",
                "database": db_status,
                "environment": env_check
            }), 503
            
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": str(e),
            "timestamp": datetime.utcnow().isoformat()
        }), 500

@app.route('/static/<path:filename>')
def serve_static_assets(filename):
    """Serve static assets for production deployment"""
    try:
        print(f"🔍 Requesting static file: {filename}")
        
        # Try to serve from the frontend build static directory
        if FRONTEND_BUILD_FOLDER:
            static_path = os.path.join(FRONTEND_BUILD_FOLDER, 'static', filename)
            print(f"🔍 Checking static path: {static_path}")
            
            if os.path.exists(static_path):
                print(f"✅ Found static file: {static_path}")
                # Set proper MIME type
                mimetype = mimetypes.guess_type(static_path)[0]
                return send_file(static_path, mimetype=mimetype)
        
        # Fallback to project root static
        root_static_path = os.path.join(os.getcwd(), 'static', filename)
        if os.path.exists(root_static_path):
            print(f"✅ Found fallback static file: {root_static_path}")
            mimetype = mimetypes.guess_type(root_static_path)[0]
            return send_file(root_static_path, mimetype=mimetype)
            
        print(f"❌ Static file not found: {filename}")
        return "Static file not found", 404
        
    except Exception as e:
        print(f"❌ Error serving static file {filename}: {str(e)}")
        return f"Error serving static file: {str(e)}", 500

@app.route('/<filename>')
def serve_static_files(filename):
    """Serve signature files and other static assets"""
    # Define the files that should be served directly
    static_files = [
        'president-signature.png',
        'chairman-signature.png', 
        'Dr_Augustine_Duru_signature.png',
        'logo-mdcan.jpeg',
        'certificate_background.png'
    ]
    
    if filename in static_files:
        # Get the current working directory (should be project root)
        project_root = os.getcwd()
        
        # Try to serve from frontend/public first
        frontend_public_path = os.path.join(project_root, 'frontend', 'public', filename)
        if os.path.exists(frontend_public_path):
            return send_file(frontend_public_path)
        
        # Try to serve from build directory
        build_path = os.path.join(project_root, 'build', filename)
        if os.path.exists(build_path):
            return send_file(build_path)
            
        # Try frontend/build directory
        frontend_build_path = os.path.join(project_root, 'frontend', 'build', filename)
        if os.path.exists(frontend_build_path):
            return send_file(frontend_build_path)
    
    # If not a static file we serve, let the catch-all handle it
    return serve_react(filename)

@app.route('/api/test')
def test():
    """Test endpoint"""
    return jsonify({
        "status": "ok",
        "message": "Backend API is working",
        "version": "minimal"
    })

@app.route('/api/status')
def status():
    """System status endpoint"""
    return jsonify({
        "status": "ok",
        "version": "minimal",
        "environment": {
            "python_version": sys.version,
            "flask_version": getattr(Flask, '__version__', 'unknown'),
            "database_connected": bool(os.environ.get('DATABASE_URL')),
            "email_configured": bool(os.environ.get('EMAIL_HOST')),
            "static_folder": static_folder
        }
    })

@app.route('/api/create-tables')
def create_all_tables():
    """Force create all database tables"""
    try:
        # Drop and recreate tables for a clean setup
        db.drop_all()
        db.create_all()
        
        # Verify table creation by checking the participant table specifically
        with db.engine.connect() as connection:
            # Check if participant table exists
            result = connection.execute(sa.text("""
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_schema = 'public' 
                AND table_type = 'BASE TABLE'
            """))
            tables = [row[0] for row in result.fetchall()]
            
            # Try to query the participant table to ensure it's working
            if 'participant' in tables:
                count_result = connection.execute(sa.text("SELECT COUNT(*) FROM participant"))
                participant_count = count_result.fetchone()[0]
            else:
                participant_count = "Table not found"
        
        return jsonify({
            "status": "success",
            "message": "All database tables created successfully",
            "tables_created": tables,
            "participant_table_status": "exists" if 'participant' in tables else "missing",
            "participant_count": participant_count,
            "timestamp": datetime.utcnow().isoformat()
        })
        
    except Exception as e:
        import traceback
        return jsonify({
            "status": "error",
            "message": f"Failed to create tables: {str(e)}",
            "traceback": traceback.format_exc(),
            "timestamp": datetime.utcnow().isoformat()
        }), 500

@app.route('/api/check-permissions')
def check_permissions():
    """Check database permissions and schemas"""
    try:
        with db.engine.connect() as connection:
            # Check current user
            user_result = connection.execute(sa.text("SELECT current_user, current_database()"))
            user_info = user_result.fetchone()
            
            # Check available schemas
            schema_result = connection.execute(sa.text("""
                SELECT schema_name 
                FROM information_schema.schemata 
                WHERE schema_name NOT IN ('information_schema', 'pg_catalog', 'pg_toast')
            """))
            schemas = [row[0] for row in schema_result.fetchall()]
            
            # Check permissions on public schema
            perms_result = connection.execute(sa.text("""
                SELECT 
                    has_schema_privilege(current_user, 'public', 'CREATE') as can_create,
                    has_schema_privilege(current_user, 'public', 'USAGE') as can_use
            """))
            permissions = perms_result.fetchone()
            
            # Check if we own any schemas
            owned_result = connection.execute(sa.text("""
                SELECT schema_name 
                FROM information_schema.schemata 
                WHERE schema_owner = current_user
            """))
            owned_schemas = [row[0] for row in owned_result.fetchall()]
        
        return jsonify({
            "status": "success",
            "current_user": user_info[0] if user_info else None,
            "current_database": user_info[1] if user_info else None,
            "available_schemas": schemas,
            "public_schema_permissions": {
                "can_create": permissions[0] if permissions else False,
                "can_use": permissions[1] if permissions else False
            },
            "owned_schemas": owned_schemas,
            "timestamp": datetime.utcnow().isoformat()
        })
        
    except Exception as e:
        import traceback
        return jsonify({
            "status": "error",
            "message": f"Permission check failed: {str(e)}",
            "traceback": traceback.format_exc(),
            "timestamp": datetime.utcnow().isoformat()
        }), 500

@app.route('/api/create-table-now')
def create_table_now():
    """Create participant table immediately"""
    try:
        # Simple CREATE TABLE statement
        sql = """
        CREATE TABLE IF NOT EXISTS participant (
            id SERIAL PRIMARY KEY,
            name VARCHAR(100) NOT NULL,
            email VARCHAR(100) NOT NULL,
            role VARCHAR(50) DEFAULT 'Attendee',
            cert_type VARCHAR(50) DEFAULT 'participation',
            registration_number VARCHAR(50),
            phone VARCHAR(20),
            gender VARCHAR(10),
            specialty VARCHAR(100),
            state VARCHAR(50),
            hospital VARCHAR(100),
            cert_sent BOOLEAN DEFAULT FALSE,
            cert_sent_date TIMESTAMP,
            certificate_id VARCHAR(50),
            date_registered TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            registration_status VARCHAR(20) DEFAULT 'Pending',
            registration_fee_paid BOOLEAN DEFAULT FALSE
        )
        """
        
        # Execute with autocommit
        connection = db.engine.connect()
        trans = connection.begin()
        try:
            connection.execute(sa.text(sql))
            trans.commit()
            success = True
            message = "Table created successfully"
        except Exception as e:
            trans.rollback()
            success = False
            message = f"Failed to create table: {str(e)}"
        finally:
            connection.close()
        
        return jsonify({
            "status": "success" if success else "error",
            "message": message,
            "timestamp": datetime.utcnow().isoformat()
        })
        
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": f"Endpoint error: {str(e)}",
            "timestamp": datetime.utcnow().isoformat()
        }), 500

@app.route('/api/force-create')
def force_create_tables():
    """Force create tables using SQLAlchemy"""
    try:
        # Force table creation using SQLAlchemy in app context
        with app.app_context():
            db.create_all()
        
        return jsonify({
            "status": "success",
            "message": "SQLAlchemy create_all() executed successfully",
            "timestamp": datetime.utcnow().isoformat()
        })
        
    except Exception as e:
        import traceback
        return jsonify({
            "status": "error", 
            "message": f"SQLAlchemy create_all failed: {str(e)}",
            "traceback": traceback.format_exc(),
            "timestamp": datetime.utcnow().isoformat()
        }), 500

@app.route('/api/db-test')
def db_test():
    """Simple database test endpoint - v3"""
    try:
        # Test database connection
        with db.engine.connect() as connection:
            result = connection.execute(sa.text('SELECT 1 as test')).fetchone()
            test_value = result[0] if result else None
            
            # Test if participant table exists
            try:
                table_check = connection.execute(sa.text("""
                    SELECT EXISTS (
                        SELECT FROM information_schema.tables 
                        WHERE table_name = 'participant'
                    )
                """)).fetchone()[0]
                
                if table_check:
                    # If table exists, try to count records
                    count_result = connection.execute(sa.text("SELECT COUNT(*) FROM participant")).fetchone()[0]
                    table_status = f"Table exists with {count_result} records"
                else:
                    table_status = "Table does not exist"
            except Exception as e:
                table_status = f"Error checking table: {str(e)}"
        
        return jsonify({
            "status": "ok",
            "message": "Database connection successful",
            "test_query_result": test_value,
            "participant_table_status": table_status,
            "timestamp": datetime.utcnow().isoformat(),
            "database_url_configured": bool(os.environ.get('DATABASE_URL'))
        })
    except Exception as e:
        import traceback
        return jsonify({
            "status": "error",
            "message": f"Database connection failed: {str(e)}",
            "traceback": traceback.format_exc(),
            "database_url_configured": bool(os.environ.get('DATABASE_URL'))
        }), 500

@app.route('/api/ssl-test')
def ssl_test():
    """Test SSL database connection and configuration"""
    try:
        # Get database URL
        database_url = os.environ.get('DATABASE_URL', '')
        is_postgres = 'postgresql://' in database_url
        
        if not is_postgres:
            return jsonify({
                "status": "info",
                "message": "SSL test not applicable - not using PostgreSQL",
                "database_type": "SQLite or other",
                "ssl_required": False
            })
        
        # Test SSL connection
        with db.engine.connect() as connection:
            # Get SSL status
            try:
                ssl_result = connection.execute(sa.text("SELECT ssl_is_used()")).fetchone()
                ssl_active = ssl_result[0] if ssl_result else False
            except:
                ssl_active = "Unknown"
            
            # Get connection info
            try:
                version_result = connection.execute(sa.text("SELECT version()")).fetchone()
                db_version = version_result[0] if version_result else "Unknown"
            except:
                db_version = "Unknown"
            
            # Get current user
            try:
                user_result = connection.execute(sa.text("SELECT current_user")).fetchone()
                current_user = user_result[0] if user_result else "Unknown"
            except:
                current_user = "Unknown"
        
        return jsonify({
            "status": "success",
            "message": "SSL connection test completed",
            "ssl_active": ssl_active,
            "database_version": db_version,
            "current_user": current_user,
            "sslmode_in_url": "sslmode=require" in database_url,
            "ssl_configured": bool(app.config['SQLALCHEMY_ENGINE_OPTIONS'].get('connect_args', {}).get('sslmode')),
            "timestamp": datetime.utcnow().isoformat()
        })
        
    except Exception as e:
        import traceback
        return jsonify({
            "status": "error",
            "message": f"SSL test failed: {str(e)}",
            "traceback": traceback.format_exc(),
            "timestamp": datetime.utcnow().isoformat()
        }), 500

@app.route('/api/table-test')
def test_table_exists():
    """Test if participant table exists"""
    try:
        # Try a simple query to see if table exists
        with db.engine.connect() as connection:
            result = connection.execute(sa.text("SELECT EXISTS (SELECT FROM information_schema.tables WHERE table_name = 'participant')"))
            table_exists = result.fetchone()[0]
            
            # If table doesn't exist, try to create it using SQLAlchemy
            if not table_exists:
                # Force creation in the database context
                with app.app_context():
                    db.create_all()
                
                # Check again
                result = connection.execute(sa.text("SELECT EXISTS (SELECT FROM information_schema.tables WHERE table_name = 'participant')"))
                table_exists_after = result.fetchone()[0]
                
                return jsonify({
                    "status": "attempted_creation",
                    "table_existed_before": table_exists,
                    "table_exists_after": table_exists_after,
                    "message": "Attempted to create tables"
                })
            else:
                return jsonify({
                    "status": "exists",
                    "table_exists": table_exists,
                    "message": "Participant table already exists"
                })
        
    except Exception as e:
        import traceback
        return jsonify({
            "status": "error",
            "message": f"Table test failed: {str(e)}",
            "traceback": traceback.format_exc()
        }), 500

@app.route('/api/setup-db')
def setup_database():
    """Set up database tables manually using SQL DDL"""
    try:
        # Step 1: Drop existing table if it exists
        drop_sql = "DROP TABLE IF EXISTS participant CASCADE"
        
        # Step 2: Create the participant table
        create_sql = """
        CREATE TABLE participant (
            id SERIAL PRIMARY KEY,
            name VARCHAR(100) NOT NULL,
            email VARCHAR(100) NOT NULL,
            role VARCHAR(50) DEFAULT 'Attendee',
            cert_type VARCHAR(50) DEFAULT 'participation',
            registration_number VARCHAR(50),
            phone VARCHAR(20),
            gender VARCHAR(10),
            specialty VARCHAR(100),
            state VARCHAR(50),
            hospital VARCHAR(100),
            cert_sent BOOLEAN DEFAULT FALSE,
            cert_sent_date TIMESTAMP,
            certificate_id VARCHAR(50),
            date_registered TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            registration_status VARCHAR(20) DEFAULT 'Pending',
            registration_fee_paid BOOLEAN DEFAULT FALSE
        )
        """
        
        execution_log = []
        
        # Execute in a transaction
        with db.engine.begin() as connection:
            # Drop table
            connection.execute(sa.text(drop_sql))
            execution_log.append("Dropped existing participant table")
            
            # Create table
            connection.execute(sa.text(create_sql))
            execution_log.append("Created participant table")
        
        # Verify the table was created
        with db.engine.connect() as connection:
            # Check if table exists
            result = connection.execute(sa.text("""
                SELECT EXISTS (
                    SELECT FROM information_schema.tables 
                    WHERE table_name = 'participant'
                )
            """))
            table_exists = result.fetchone()[0]
            
            if table_exists:
                # Get column info
                result = connection.execute(sa.text("""
                    SELECT column_name, data_type 
                    FROM information_schema.columns 
                    WHERE table_name = 'participant' 
                    ORDER BY ordinal_position
                """))
                columns = [f"{row[0]} ({row[1]})" for row in result.fetchall()]
                execution_log.append(f"Verified table structure: {len(columns)} columns")
            else:
                execution_log.append("ERROR: Table was not created")
        
        return jsonify({
            "status": "success" if table_exists else "error",
            "message": "Database setup completed" if table_exists else "Table creation failed",
            "table_exists": table_exists,
            "columns": columns if table_exists else [],
            "execution_log": execution_log,
            "timestamp": datetime.utcnow().isoformat()
        })
        
    except Exception as e:
        import traceback
        return jsonify({
            "status": "error",
            "message": f"Database setup failed: {str(e)}",
            "traceback": traceback.format_exc(),
            "execution_log": execution_log if 'execution_log' in locals() else [],
            "timestamp": datetime.utcnow().isoformat()
        }), 500

@app.route('/api/setup-production', methods=['POST'])
def setup_production_database():
    """Special endpoint to setup production database with proper permissions"""
    try:
        # Get the secret key from request to prevent unauthorized access
        secret = request.form.get('secret') or request.json.get('secret') if request.is_json else None
        
        if secret != 'mdcansetup2025':
            return jsonify({
                "status": "error",
                "message": "Unauthorized access"
            }), 403
        
        execution_log = []
        
        # Create the participant table with IF NOT EXISTS to avoid permission errors
        create_sql = """
        CREATE TABLE IF NOT EXISTS participant (
            id SERIAL PRIMARY KEY,
            name VARCHAR(100) NOT NULL,
            email VARCHAR(100) NOT NULL,
            role VARCHAR(50) DEFAULT 'Attendee',
            cert_type VARCHAR(50) DEFAULT 'participation',
            registration_number VARCHAR(50),
            phone VARCHAR(20),
            gender VARCHAR(10),
            specialty VARCHAR(100),
            state VARCHAR(50),
            hospital VARCHAR(100),
            cert_sent BOOLEAN DEFAULT FALSE,
            cert_sent_date TIMESTAMP,
            certificate_id VARCHAR(50),
            date_registered TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            registration_status VARCHAR(20) DEFAULT 'Pending',
            registration_fee_paid BOOLEAN DEFAULT FALSE
        )
        """
        
        # Execute using database connection
        with db.engine.connect() as connection:
            # Try to create the table
            try:
                connection.execute(sa.text(create_sql))
                connection.commit()
                execution_log.append("✅ Participant table created successfully")
            except Exception as create_error:
                # If table creation fails, check if table already exists
                try:
                    result = connection.execute(sa.text("SELECT COUNT(*) FROM participant"))
                    count = result.fetchone()[0]
                    execution_log.append(f"ℹ️ Table already exists with {count} records")
                except:
                    execution_log.append(f"❌ Table creation failed: {str(create_error)}")
                    raise create_error
            
            # Verify table structure
            try:
                result = connection.execute(sa.text("""
                    SELECT column_name, data_type 
                    FROM information_schema.columns 
                    WHERE table_name = 'participant' 
                    ORDER BY ordinal_position
                """))
                columns = [f"{row[0]} ({row[1]})" for row in result.fetchall()]
                execution_log.append(f"✅ Table structure verified: {len(columns)} columns")
            except Exception as verify_error:
                execution_log.append(f"⚠️ Table verification failed: {str(verify_error)}")
        
        return jsonify({
            "status": "success",
            "message": "Production database setup completed successfully",
            "execution_log": execution_log,
            "table_columns": columns if 'columns' in locals() else [],
            "timestamp": datetime.utcnow().isoformat()
        })
        
    except Exception as e:
        import traceback
        return jsonify({
            "status": "error",
            "message": f"Production database setup failed: {str(e)}",
            "traceback": traceback.format_exc(),
            "execution_log": execution_log if 'execution_log' in locals() else [],
            "timestamp": datetime.utcnow().isoformat()
        }), 500

@app.route('/api/init-database', methods=['GET', 'POST'])
def init_database():
    """Initialize database tables"""
    try:
        # Check if database connection works
        with db.engine.connect() as connection:
            connection.execute(sa.text('SELECT 1'))
        
        # Create all tables
        db.create_all()
        
        # Verify tables were created
        from sqlalchemy import inspect
        inspector = inspect(db.engine)
        tables = inspector.get_table_names()
        
        return jsonify({
            "status": "success",
            "message": "Database tables created successfully",
            "tables_created": tables,
            "database_url": bool(os.environ.get('DATABASE_URL'))
        })
        
    except Exception as e:
        import traceback
        return jsonify({
            "status": "error",
            "message": f"Failed to initialize database: {str(e)}",
            "traceback": traceback.format_exc(),
            "database_url": bool(os.environ.get('DATABASE_URL'))
        }), 500
@app.route('/api/participants/<int:id>', methods=['PUT'])
def update_participant(id):
    try:
        participant = Participant.query.get(id)
        if not participant:
            return jsonify({
                "status": "error",
                "message": "Participant not found"
            }), 404
            
        data = request.json
        
        # Update fields
        for key, value in data.items():
            if hasattr(participant, key):
                setattr(participant, key, value)
                
        db.session.commit()
        
        return jsonify({
            "status": "success",
            "message": "Participant updated successfully",
            "participant": participant.to_dict()
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500

@app.route('/api/participants/<int:id>', methods=['DELETE'])
def delete_participant(id):
    try:
        participant = Participant.query.get(id)
        if not participant:
            return jsonify({
                "status": "error",
                "message": "Participant not found"
            }), 404
            
        db.session.delete(participant)
        db.session.commit()
        
        return jsonify({
            "status": "success",
            "message": "Participant deleted successfully"
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500

# Certificate generation and retrieval
@app.route('/api/certificates/<int:participant_id>', methods=['GET'])
def generate_certificate(participant_id):
    try:
        participant = Participant.query.get(participant_id)
        if not participant:
            return jsonify({
                "status": "error",
                "message": "Participant not found"
            }), 404
            
        # Generate certificate HTML
        if participant.cert_type == 'service':
            html = render_template_string(
                SERVICE_CERTIFICATE_TEMPLATE,
                name=participant.name,
                service_text=CERT_SERVICE_TEXT,
                certificate_id=participant.certificate_id,
                chairman_signature=CHAIRMAN_SIGNATURE,
                secretary_signature=SECRETARY_SIGNATURE,
                logo=MDCAN_LOGO
            )
        else:
            # Default to participation certificate
            html = render_template_string(
                PARTICIPATION_CERTIFICATE_TEMPLATE,
                name=participant.name,
                event_text=CERT_EVENT_TEXT,
                certificate_id=participant.certificate_id,
                president_signature=PRESIDENT_SIGNATURE,
                chairman_signature=CHAIRMAN_SIGNATURE,
                logo=MDCAN_LOGO
            )
            
        # Generate PDF
        try:
            if not globals().get('PDF_GENERATION_AVAILABLE', False):
                return jsonify({
                    "status": "error",
                    "message": "PDF generation not available in this deployment. System packages may be missing.",
                    "html_preview": html[:500] + "..." if len(html) > 500 else html,
                    "available_features": ["registration", "admin_portal", "database"]
                }), 503
                
            pdf = pdfkit.from_string(html, False, configuration=PDF_CONFIG)
        except Exception as e:
            # For environments where wkhtmltopdf might not be available
            return jsonify({
                "status": "error",
                "message": f"Error generating PDF: {str(e)}. HTML version returned instead.",
                "html_preview": html[:500] + "..." if len(html) > 500 else html,
                "troubleshooting": "This may indicate missing system dependencies like wkhtmltopdf"
            }), 500
            
        # Create a temporary file to serve
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.pdf')
        temp_file.write(pdf)
        temp_file.close()
        
        @after_this_request
        def cleanup(response):
            try:
                os.unlink(temp_file.name)
            except:
                pass
            return response
            
        return send_file(
            temp_file.name, 
            mimetype='application/pdf',
            as_attachment=True,
            download_name=f"certificate_{participant.name.replace(' ', '_')}.pdf"
        )
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500

# Route definitions for specific API endpoints first, then catch-all route at the end

# API routes for participant management
@app.route('/api/participants', methods=['GET'])
def get_participants():
    try:
        participants = Participant.query.all()
        return jsonify({
            "status": "success",
            "count": len(participants),
            "participants": [p.to_dict() for p in participants]
        })
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500

@app.route('/api/participants', methods=['POST'])
def create_participant():
    try:
        data = request.json
        
        # Generate a unique registration number if not provided
        if not data.get('registration_number'):
            data['registration_number'] = f"MDCAN-{uuid.uuid4().hex[:8].upper()}"
            
        # Generate a unique certificate ID
        data['certificate_id'] = f"CERT-{uuid.uuid4().hex[:12].upper()}"
        
        new_participant = Participant(
            name=data.get('name'),
            email=data.get('email'),
            role=data.get('role', 'Attendee'),
            cert_type=data.get('cert_type', 'participation'),
            registration_number=data.get('registration_number'),
            phone=data.get('phone'),
            gender=data.get('gender'),
            specialty=data.get('specialty'),
            state=data.get('state'),
            hospital=data.get('hospital'),
            certificate_id=data.get('certificate_id'),
            registration_status=data.get('registration_status', 'Pending'),
            registration_fee_paid=data.get('registration_fee_paid', False)
        )
        
        db.session.add(new_participant)
        db.session.commit()
        
        return jsonify({
            "status": "success",
            "message": "Participant created successfully",
            "participant": new_participant.to_dict()
        }), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500

@app.route('/api/register', methods=['POST'])
def register_participant():
    """Registration endpoint that handles multipart form data"""
    try:
        # Handle both form data and JSON data
        if request.is_json:
            # Handle JSON data
            data = request.get_json()
            name = data.get('name')
            email = data.get('email')
            phone = data.get('phone')
            gender = data.get('gender')
            specialty = data.get('specialty')
            state = data.get('state')
            hospital = data.get('hospital')
            cert_type = data.get('cert_type', 'participation')
            role = data.get('role', 'Attendee')
            registration_fee_paid = data.get('registration_fee_paid', False)
            files = {}  # No files in JSON requests
        else:
            # Handle multipart form data
            form_data = request.form
            files = request.files
            
            name = form_data.get('name')
            email = form_data.get('email')
            phone = form_data.get('phone')
            gender = form_data.get('gender')
            specialty = form_data.get('specialty')
            state = form_data.get('state')
            hospital = form_data.get('hospital')
            cert_type = form_data.get('cert_type', 'participation')
            role = form_data.get('role', 'Attendee')
            registration_fee_paid = form_data.get('registration_fee_paid', 'false').lower() == 'true'
        
        # Validate required fields
        if not name or not email:
            return jsonify({
                "status": "error",
                "message": "Name and email are required"
            }), 400
        
        # Generate unique identifiers
        import uuid
        registration_number = f"MDCAN-{uuid.uuid4().hex[:8].upper()}"
        certificate_id = f"CERT-{uuid.uuid4().hex[:12].upper()}"
        
        # Try to create and save participant directly
        try:
            # Check if email already exists first
            existing_participant = Participant.query.filter_by(email=email).first()
            if existing_participant:
                return jsonify({
                    "status": "error",
                    "message": "Email already registered. Please use a different email."
                }), 400
            
            # Create new participant
            new_participant = Participant(
                name=name,
                email=email,
                phone=phone,
                gender=gender,
                specialty=specialty,
                state=state,
                hospital=hospital,
                role=role,
                cert_type=cert_type,
                registration_number=registration_number,
                certificate_id=certificate_id,
                registration_status='Pending' if not registration_fee_paid else 'Confirmed',
                registration_fee_paid=registration_fee_paid
            )
            
            db.session.add(new_participant)
            db.session.commit()
            
            return jsonify({
                "status": "success",
                "message": "Registration successful! Welcome to MDCAN BDM 2025.",
                "participant": new_participant.to_dict(),
                "registration_number": registration_number,
                "certificate_id": certificate_id,
                "whatsapp_group": {
                    "message": "Join the MDCAN BDM 2025 Conference WhatsApp group to stay updated!",
                    "link": "https://chat.whatsapp.com/E0JkGqBhM362Z2fwHyiv8k",
                    "instructions": "Click the link above to join the conference WhatsApp group for important updates, networking, and real-time conference information."
                }
            }), 201
            
        except Exception as db_error:
            db.session.rollback()
            
            # Check if it's a table missing error
            error_str = str(db_error).lower()
            if 'relation "participant" does not exist' in error_str or 'table' in error_str:
                return jsonify({
                    "status": "error",
                    "message": "Database setup incomplete. Please contact administrator.",
                    "error_code": "DB_TABLE_MISSING",
                    "details": "The participant table needs to be created."
                }), 503
            elif 'authentication' in error_str or 'password' in error_str:
                return jsonify({
                    "status": "error", 
                    "message": "Database connection issue. Please try again later.",
                    "error_code": "DB_AUTH_ERROR",
                    "details": "Database authentication needs to be configured."
                }), 503
            else:
                return jsonify({
                    "status": "error",
                    "message": f"Registration failed: {str(db_error)}",
                    "error_code": "DB_ERROR"
                }), 500

    except Exception as e:
        return jsonify({
            "status": "error", 
            "message": "An unexpected error occurred during registration.",
            "error_code": "GENERAL_ERROR",
            "details": str(e)
        }), 500

@app.route('/api/participants/<int:id>', methods=['GET'])
def get_participant(id):
    try:
        participant = Participant.query.get(id)
        if not participant:
            return jsonify({
                "status": "error",
                "message": "Participant not found"
            }), 404
            
        return jsonify({
            "status": "success",
            "participant": participant.to_dict()
        })
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500

@app.route('/api/participants/<email>/dashboard', methods=['GET'])
def get_participant_dashboard(email):
    """Get participant dashboard information by email"""
    try:
        participant = Participant.query.filter_by(email=email).first()
        if not participant:
            return jsonify({
                "status": "error",
                "message": "Participant not found"
            }), 404
            
        dashboard_data = {
            "participant": participant.to_dict(),
            "registration_status": participant.registration_status,
            "certificate_sent": participant.cert_sent,
            "registration_number": participant.registration_number,
            "certificate_id": participant.certificate_id,
            "whatsapp_group": {
                "message": "Join the MDCAN BDM 2025 Conference WhatsApp group to stay updated!",
                "link": "https://chat.whatsapp.com/E0JkGqBhM362Z2fwHyiv8k",
                "instructions": "Click the link above to join the conference WhatsApp group for important updates, networking, and real-time conference information."
            }
        }
        
        return jsonify({
            "status": "success",
            "dashboard": dashboard_data
        })
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500

def send_email(recipient_email, subject, body, attachment_path=None):
    """Send email with optional attachment"""
    try:
        if not all([EMAIL_HOST, EMAIL_PORT, EMAIL_USER, EMAIL_PASSWORD]):
            print("[EMAIL] Email configuration incomplete")
            return False
            
        msg = MIMEMultipart()
        msg['From'] = EMAIL_FROM
        msg['To'] = recipient_email
        msg['Subject'] = subject
        
        # Add body
        msg.attach(MIMEText(body, 'plain'))
        
        # Add attachment if provided
        if attachment_path and os.path.exists(attachment_path):
            with open(attachment_path, "rb") as attachment:
                part = MIMEBase("application", "octet-stream")
                part.set_payload(attachment.read())
                
            encoders.encode_base64(part)
            
            filename = os.path.basename(attachment_path)
            part.add_header(
                "Content-Disposition",
                f"attachment; filename= {filename}",
            )
            msg.attach(part)
        
        # Send email
        server = smtplib.SMTP(EMAIL_HOST, EMAIL_PORT)
        server.starttls()
        server.login(EMAIL_USER, EMAIL_PASSWORD)
        server.send_message(msg)
        server.quit()
        
        print(f"[EMAIL] Email sent successfully to {recipient_email}")
        return True
        
    except Exception as e:
        print(f"[EMAIL] Error sending email to {recipient_email}: {e}")
        return False

# Email certificate function
@app.route('/api/send-certificate/<int:participant_id>', methods=['POST'])
def send_certificate(participant_id):
    try:
        print(f"[CERTIFICATE] Starting certificate send for participant ID: {participant_id}")
        
        # Check database connection before attempting to query
        try:
            # Use session.get() instead of deprecated query.get()
            participant = db.session.get(Participant, participant_id)
        except Exception as db_error:
            print(f"[CERTIFICATE] Database connection error: {db_error}")
            return jsonify({
                "status": "error",
                "message": "Database connection unavailable. Cannot retrieve participant information.",
                "details": "The certificate generation service is temporarily unavailable due to database connectivity issues.",
                "error_type": "database_connection_error",
                "participant_id": participant_id,
                "troubleshooting": "Please check the database connection settings and try again."
            }), 503
            
        if not participant:
            print(f"[CERTIFICATE] Participant not found with ID: {participant_id}")
            return jsonify({
                "status": "error",
                "message": "Participant not found"
            }), 404
            
        print(f"[CERTIFICATE] Found participant: {participant.name} ({participant.email})")
        
        # Check certificate sending schedule
        now = datetime.now()
        current_date = now.date()
        current_time = now.time()
        
        # Allow sending today (August 18, 2025) anytime for testing
        today_allowed = datetime(2025, 8, 18).date()
        
        # Allow sending from September 5, 2025 at 5:00 PM onwards
        conference_start = datetime(2025, 9, 5, 17, 0, 0)  # September 5, 2025 at 5:00 PM
        
        # Check certificate sending schedule
        now = datetime.now()
        current_date = now.date()
        current_time = now.time()
        
        # Allow sending during August 2025 (entire month for testing)
        august_2025_start = datetime(2025, 8, 1).date()
        august_2025_end = datetime(2025, 8, 31).date()
        
        # Allow sending from September 5, 2025 at 5:00 PM onwards
        conference_start = datetime(2025, 9, 5, 17, 0, 0)  # September 5, 2025 at 5:00 PM
        
        sending_allowed = False
        restriction_message = ""
        
        if august_2025_start <= current_date <= august_2025_end:
            # August 2025 testing period
            sending_allowed = True
            print(f"[CERTIFICATE] Sending allowed - August 2025 testing period ({current_date})")
        elif now >= conference_start:
            # After conference start time
            sending_allowed = True
            print(f"[CERTIFICATE] Sending allowed - Conference period active since {conference_start}")
        else:
            # Not allowed yet
            sending_allowed = False
            restriction_message = f"Certificate sending will be available from September 5, 2025 at 5:00 PM. Current time: {now.strftime('%B %d, %Y at %I:%M %p')}"
            print(f"[CERTIFICATE] Sending restricted - {restriction_message}")
        
        if not sending_allowed:
            return jsonify({
                "status": "error",
                "message": "Certificate sending is not available at this time",
                "details": restriction_message,
                "available_from": "September 5, 2025 at 5:00 PM"
            }), 403
        
        # Check email configuration first
        if not all([EMAIL_HOST, EMAIL_PORT, EMAIL_USER, EMAIL_PASSWORD]):
            print("[CERTIFICATE] Email configuration incomplete")
            return jsonify({
                "status": "error",
                "message": "Email configuration is incomplete. Cannot send certificate.",
                "details": "Please configure EMAIL_HOST, EMAIL_USER, and EMAIL_PASSWORD environment variables.",
                "participant": {
                    "name": participant.name,
                    "email": participant.email,
                    "certificate_id": participant.certificate_id
                }
            }), 503
            
        print(f"[CERTIFICATE] Generating certificate for: {participant.name}")
        
        # Generate certificate PDF first
        if participant.cert_type == 'service':
            html = render_template_string(
                SERVICE_CERTIFICATE_TEMPLATE,
                name=participant.name,
                service_text=CERT_SERVICE_TEXT,
                certificate_id=participant.certificate_id,
                chairman_signature=CHAIRMAN_SIGNATURE,
                secretary_signature=SECRETARY_SIGNATURE,
                logo=MDCAN_LOGO
            )
        else:
            # Default to participation certificate
            html = render_template_string(
                PARTICIPATION_CERTIFICATE_TEMPLATE,
                name=participant.name,
                event_text=CERT_EVENT_TEXT,
                certificate_id=participant.certificate_id,
                president_signature=PRESIDENT_SIGNATURE,
                chairman_signature=CHAIRMAN_SIGNATURE,
                logo=MDCAN_LOGO
            )
        
        # Generate PDF
        try:
            if not globals().get('PDF_GENERATION_AVAILABLE', False):
                print("[CERTIFICATE] PDF generation not available")
                return jsonify({
                    "status": "error",
                    "message": "PDF generation not available in this deployment. System packages may be missing.",
                    "html_preview": html[:500] + "..." if len(html) > 500 else html,
                    "available_features": ["registration", "admin_portal", "database"]
                }), 503
                
            print("[CERTIFICATE] Generating PDF with pdfkit...")
            
            # PDF generation options with timeout to prevent hanging
            pdf_options = {
                'page-size': 'A4',
                'margin-top': '0.75in',
                'margin-right': '0.75in', 
                'margin-bottom': '0.75in',
                'margin-left': '0.75in',
                'encoding': "UTF-8",
                'no-outline': None,
                'enable-local-file-access': None,
                'load-error-handling': 'ignore',
                'load-media-error-handling': 'ignore',
                'javascript-delay': 1000,  # 1 second delay for JS/CSS
                'print-media-type': None
            }
            
            # Generate PDF with 30-second timeout
            pdf = generate_pdf_with_timeout(html, PDF_CONFIG, pdf_options, timeout=30)
            print(f"[CERTIFICATE] PDF generated successfully, size: {len(pdf)} bytes")
        except Exception as e:
            print(f"[CERTIFICATE] PDF generation error: {str(e)}")
            return jsonify({
                "status": "error",
                "message": f"Error generating PDF: {str(e)}",
                "troubleshooting": "This may indicate missing system dependencies like wkhtmltopdf"
            }), 500
            
        # Create a temporary file for the PDF
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.pdf')
        temp_file.write(pdf)
        temp_file.close()
        print(f"[CERTIFICATE] PDF saved to temporary file: {temp_file.name}")
        
        # Check if email configuration is available (already checked above, but for safety)
        if not all([EMAIL_HOST, EMAIL_PORT, EMAIL_USER, EMAIL_PASSWORD]):
            os.unlink(temp_file.name)
            return jsonify({
                "status": "error",
                "message": "Email configuration is incomplete"
            }), 500
            
        # Setup email message
        msg = MIMEMultipart()
        msg['From'] = EMAIL_FROM
        msg['To'] = participant.email
        msg['Subject'] = f"Your MDCAN BDM 2025 Certificate - {participant.name}"
        
        # Email body
        email_body = f"""
        Dear {participant.name},
        
        Thank you for your participation in the MDCAN BDM 14th – 2025 held in Enugu.
        
        Please find attached your {'Acknowledgement of Service' if participant.cert_type == 'service' else 'Certificate of Participation'}.
        
        Your certificate ID is: {participant.certificate_id}
        
        Best regards,
        MDCAN BDM 2025 Team
        """
        
        msg.attach(MIMEText(email_body, 'plain'))
        
        # Attach the PDF certificate
        with open(temp_file.name, "rb") as attachment:
            part = MIMEBase("application", "octet-stream")
            part.set_payload(attachment.read())
            
        encoders.encode_base64(part)
        
        filename = f"MDCAN_Certificate_{participant.name.replace(' ', '_')}.pdf"
        part.add_header(
            "Content-Disposition",
            f"attachment; filename= {filename}",
        )
        
        msg.attach(part)
        
        # Send email in a separate thread to avoid blocking
        def send_email_task():
            try:
                print(f"[EMAIL] Starting email send to {participant.email}")
                server = smtplib.SMTP(EMAIL_HOST, EMAIL_PORT)
                server.starttls()
                server.login(EMAIL_USER, EMAIL_PASSWORD)
                server.send_message(msg)
                server.quit()
                print(f"[EMAIL] Email sent successfully to {participant.email}")
                
                # Update participant record
                with app.app_context():
                    participant.cert_sent = True
                    participant.cert_sent_date = datetime.utcnow()
                    db.session.commit()
                    print(f"[EMAIL] Updated participant record for {participant.name}")
            except Exception as e:
                print(f"[EMAIL] Error sending email to {participant.email}: {e}")
            finally:
                # Clean up temp file
                try:
                    os.unlink(temp_file.name)
                    print(f"[EMAIL] Cleaned up temporary file: {temp_file.name}")
                except:
                    pass
                    
        # Start email thread
        email_thread = Thread(target=send_email_task)
        email_thread.start()
        print(f"[CERTIFICATE] Email queued for {participant.name}")
        
        return jsonify({
            "status": "success",
            "message": "Certificate has been queued for sending"
        })
    except Exception as e:
        print(f"[CERTIFICATE] Error in send_certificate: {str(e)}")
        # Clean up temp file if it exists
        try:
            if 'temp_file' in locals():
                os.unlink(temp_file.name)
                print(f"[CERTIFICATE] Cleaned up temp file after error")
        except:
            pass
            
        return jsonify({
            "status": "error",
            "message": str(e),
            "participant_id": participant_id
        }), 500

# Send all certificates endpoint
@app.route('/api/send-all-certificates', methods=['POST'])
def send_all_certificates():
    try:
        print("[BULK SEND] Starting bulk certificate send process")
        
        # Get all participants who haven't received certificates yet
        participants = Participant.query.filter_by(cert_sent=False).all()
        
        if not participants:
            return jsonify({
                "status": "info",
                "message": "No participants found who need certificates",
                "count": 0
            })
        
        print(f"[BULK SEND] Found {len(participants)} participants to send certificates to")
        
        success_count = 0
        error_count = 0
        errors = []
        
        for participant in participants:
            try:
                print(f"[BULK SEND] Processing {participant.name} ({participant.email})")
                
                # Check certificate sending schedule (same logic as individual send)
                now = datetime.now()
                current_date = now.date()
                
                # Allow sending during August 2025 (entire month for testing)
                august_2025_start = datetime(2025, 8, 1).date()
                august_2025_end = datetime(2025, 8, 31).date()
                
                # Allow sending from September 5, 2025 at 5:00 PM onwards
                conference_start = datetime(2025, 9, 5, 17, 0, 0)
                
                if not (august_2025_start <= current_date <= august_2025_end or now >= conference_start):
                    print(f"[BULK SEND] Skipping {participant.name} - outside allowed time window")
                    continue
                
                # Generate certificate based on type
                if participant.cert_type == 'service':
                    html = render_template_string(
                        SERVICE_CERTIFICATE_TEMPLATE,
                        name=participant.name,
                        service_text=CERT_SERVICE_TEXT,
                        certificate_id=participant.certificate_id,
                        chairman_signature=CHAIRMAN_SIGNATURE,
                        secretary_signature=SECRETARY_SIGNATURE,
                        logo=MDCAN_LOGO
                    )
                else:
                    html = render_template_string(
                        PARTICIPATION_CERTIFICATE_TEMPLATE,
                        name=participant.name,
                        event_text=CERT_EVENT_TEXT,
                        certificate_id=participant.certificate_id,
                        president_signature=PRESIDENT_SIGNATURE,
                        chairman_signature=CHAIRMAN_SIGNATURE,
                        logo=MDCAN_LOGO
                    )
                
                # Generate PDF
                if not globals().get('PDF_GENERATION_AVAILABLE', False):
                    print(f"[BULK SEND] PDF generation not available, skipping {participant.name}")
                    error_count += 1
                    errors.append(f"{participant.name}: PDF generation not available")
                    continue
                
                # PDF generation options
                pdf_options = {
                    'page-size': 'A4',
                    'margin-top': '0.75in',
                    'margin-right': '0.75in', 
                    'margin-bottom': '0.75in',
                    'margin-left': '0.75in',
                    'encoding': "UTF-8",
                    'no-outline': None,
                    'enable-local-file-access': None,
                    'load-error-handling': 'ignore',
                    'load-media-error-handling': 'ignore',
                    'javascript-delay': 1000,
                    'print-media-type': None
                }
                
                # Generate PDF with timeout
                pdf = generate_pdf_with_timeout(html, PDF_CONFIG, pdf_options, timeout=30)
                
                if not pdf:
                    print(f"[BULK SEND] PDF generation failed for {participant.name}")
                    error_count += 1
                    errors.append(f"{participant.name}: PDF generation failed")
                    continue
                
                # Create temporary file for email
                temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.pdf')
                temp_file.write(pdf)
                temp_file.close()
                
                # Send email with certificate
                cert_type_text = "Service" if participant.cert_type == 'service' else "Participation"
                subject = f"MDCAN BDM 14th - 2025 Certificate of {cert_type_text}"
                body = f"""
Dear {participant.name},

Please find attached your Certificate of {cert_type_text} for the MDCAN BDM 14th - 2025.

Best regards,
MDCAN BDM 2025 Organizing Committee
"""
                
                # Send email
                if send_email(participant.email, subject, body, temp_file.name):
                    participant.cert_sent = True
                    participant.cert_sent_date = datetime.utcnow()
                    db.session.commit()
                    success_count += 1
                    print(f"[BULK SEND] Successfully sent certificate to {participant.name}")
                else:
                    error_count += 1
                    errors.append(f"{participant.name}: Email sending failed")
                    print(f"[BULK SEND] Failed to send certificate to {participant.name}")
                
                # Clean up temp file
                try:
                    os.unlink(temp_file.name)
                except:
                    pass
                    
            except Exception as e:
                error_count += 1
                errors.append(f"{participant.name}: {str(e)}")
                print(f"[BULK SEND] Error processing {participant.name}: {e}")
        
        print(f"[BULK SEND] Bulk send completed. Success: {success_count}, Errors: {error_count}")
        
        return jsonify({
            "status": "success",
            "message": f"Bulk certificate send completed",
            "success_count": success_count,
            "error_count": error_count,
            "errors": errors[:10] if errors else []  # Limit error list to first 10
        })
        
    except Exception as e:
        print(f"[BULK SEND] Error in send_all_certificates: {str(e)}")
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500

# Favicon route to prevent 404 errors
@app.route('/favicon.ico')
def favicon():
    try:
        # Try to serve favicon from static directory
        return send_from_directory(
            os.path.join(app.root_path, 'static'),
            'favicon.ico',
            mimetype='image/vnd.microsoft.icon'
        )
    except:
        # If favicon doesn't exist, return a 204 No Content response
        return '', 204

# Bulk operations
@app.route('/api/bulk/participants', methods=['POST'])
def bulk_add_participants():
    try:
        data = request.json
        if not data or not isinstance(data, list):
            return jsonify({
                "status": "error",
                "message": "Invalid data format. Expected a list of participants."
            }), 400
            
        added_participants = []
        errors = []
        
        for item in data:
            try:
                # Generate a unique registration number if not provided
                if not item.get('registration_number'):
                    item['registration_number'] = f"MDCAN-{uuid.uuid4().hex[:8].upper()}"
                    
                # Generate a unique certificate ID
                item['certificate_id'] = f"CERT-{uuid.uuid4().hex[:12].upper()}"
                
                new_participant = Participant(
                    name=item.get('name'),
                    email=item.get('email'),
                    role=item.get('role', 'Attendee'),
                    cert_type=item.get('cert_type', 'participation'),
                    registration_number=item.get('registration_number'),
                    phone=item.get('phone'),
                    gender=item.get('gender'),
                    specialty=item.get('specialty'),
                    state=item.get('state'),
                    hospital=item.get('hospital'),
                    certificate_id=item.get('certificate_id'),
                    registration_status=item.get('registration_status', 'Pending'),
                    registration_fee_paid=item.get('registration_fee_paid', False)
                )
                
                db.session.add(new_participant)
                db.session.flush()
                added_participants.append(new_participant.to_dict())
            except Exception as e:
                errors.append({
                    "data": item,
                    "error": str(e)
                })
                
        db.session.commit()
        
        return jsonify({
            "status": "success",
            "message": f"Added {len(added_participants)} participants with {len(errors)} errors",
            "added": added_participants,
            "errors": errors
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500

# Statistics endpoint
@app.route('/api/debug/files')
def debug_files():
    """Debug endpoint to show available files and directories"""
    file_structure = {}
    
    try:
        # Check current working directory
        import os
        current_dir = os.getcwd()
        file_structure["current_directory"] = current_dir
        file_structure["static_folder"] = static_folder
        file_structure["frontend_build_folder"] = FRONTEND_BUILD_FOLDER
        
        # List files in current directory
        file_structure["root_files"] = []
        for item in os.listdir('.'):
            if os.path.isfile(item):
                file_structure["root_files"].append(item)
            elif os.path.isdir(item):
                file_structure[f"dir_{item}"] = []
                try:
                    for subitem in os.listdir(item)[:10]:  # Limit to first 10 items
                        file_structure[f"dir_{item}"].append(subitem)
                except:
                    file_structure[f"dir_{item}"] = ["Permission denied"]
        
        # Check specifically for frontend build
        frontend_paths_checked = []
        for path in ['frontend/build', '../frontend/build', './frontend/build', '/app/frontend/build', 'build']:
            exists = os.path.exists(path)
            has_index = os.path.exists(os.path.join(path, 'index.html')) if exists else False
            frontend_paths_checked.append({
                "path": path,
                "exists": exists,
                "has_index_html": has_index
            })
        
        file_structure["frontend_paths_checked"] = frontend_paths_checked
        
    except Exception as e:
        file_structure["error"] = str(e)
    
    return jsonify(file_structure)

@app.route('/api/statistics', methods=['GET'])
def get_statistics():
    try:
        total_participants = Participant.query.count()
        participation_certs = Participant.query.filter_by(cert_type='participation').count()
        service_certs = Participant.query.filter_by(cert_type='service').count()
        certificates_sent = Participant.query.filter_by(cert_sent=True).count()
        
        # Registration status stats
        pending_registrations = Participant.query.filter_by(registration_status='Pending').count()
        approved_registrations = Participant.query.filter_by(registration_status='Approved').count()
        rejected_registrations = Participant.query.filter_by(registration_status='Rejected').count()
        
        # Fee payment stats
        fees_paid = Participant.query.filter_by(registration_fee_paid=True).count()
        
        return jsonify({
            "status": "success",
            "statistics": {
                "total_participants": total_participants,
                "certificates": {
                    "participation": participation_certs,
                    "service": service_certs,
                    "sent": certificates_sent
                },
                "registration": {
                    "pending": pending_registrations,
                    "approved": approved_registrations,
                    "rejected": rejected_registrations
                },
                "payment": {
                    "paid": fees_paid,
                    "unpaid": total_participants - fees_paid
                }
            }
        })
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500

# Serve the React frontend - MUST be at the end to avoid route conflicts
@app.route('/catch-all-test')
def catch_all_test():
    """Test route to verify catch-all routing works"""
    return jsonify({
        "status": "success",
        "message": "Catch-all routing test successful",
        "static_folder": static_folder,
        "FRONTEND_BUILD_FOLDER": FRONTEND_BUILD_FOLDER
    })

# Handle static files from React build
@app.route('/static/<path:filename>')
def serve_static(filename):
    """Serve static files from React build"""
    try:
        if static_folder:
            static_path = os.path.join(static_folder, 'static', filename)
            print(f"Serving static file: {filename} from {static_path}")
            if os.path.exists(static_path):
                return send_from_directory(os.path.join(static_folder, 'static'), filename)
        
        print(f"Static file not found: {filename}")
        return jsonify({"error": "Static file not found", "file": filename}), 404
    except Exception as e:
        print(f"Error serving static file {filename}: {e}")
        return jsonify({"error": "Error serving static file"}), 500

# Serve React frontend for non-API routes only
@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def serve_react(path):
    """Serve the React frontend - but skip API routes entirely"""
    # Don't handle API routes at all - they should be handled by specific @app.route decorators
    if path and path.startswith('api/'):
        from flask import abort
        abort(404)  # Let Flask continue to check other routes
        
    try:
        print(f"=== SERVE_REACT DEBUG START ===")
        print(f"Route requested: '{path}'")
        print(f"static_folder: {static_folder}")
        print(f"FRONTEND_BUILD_FOLDER: {FRONTEND_BUILD_FOLDER}")
        
        # Handle specific frontend files
        if path and '.' in path:
            if static_folder and os.path.exists(os.path.join(static_folder, path)):
                print(f"Serving file: {path}")
                return send_from_directory(static_folder, path)
            else:
                print(f"File not found: {path}")
                return jsonify({"error": "File not found", "path": path}), 404
        
        # For root path or any non-API path, serve index.html
        print(f"Checking for index.html in static_folder: {static_folder}")
        
        if static_folder:
            index_path = os.path.join(static_folder, 'index.html')
            print(f"Index path: {index_path}")
            print(f"Index exists: {os.path.exists(index_path)}")
            
            if os.path.exists(index_path):
                print(f"Serving index.html from: {static_folder}")
                return send_from_directory(static_folder, 'index.html')
        
        print(f"Frontend not available - static_folder: {static_folder}")
        
        # Debugging information when frontend is not available
        debug_info = {
            "status": "debug",
            "message": "MDCAN BDM 2025 Certificate Platform - Frontend Not Available",
            "frontend_status": "Frontend build not found",
            "static_folder": static_folder,
            "FRONTEND_BUILD_FOLDER": FRONTEND_BUILD_FOLDER,
            "requested_path": path,
            "possible_paths": possible_frontend_paths,
            "environment": {
                "DATABASE_URL": bool(os.environ.get('DATABASE_URL')),
                "EMAIL_HOST": bool(os.environ.get('EMAIL_HOST'))
            }
        }
        
        print(f"=== SERVE_REACT DEBUG END ===")
        return jsonify(debug_info)
        
    except Exception as e:
        print(f"ERROR in serve_react: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({
            "error": "Server error in serve_react",
            "message": str(e),
            "path": path,
            "static_folder": static_folder
        }), 500

# ===== MISSING API ENDPOINTS =====

# Test certificate generation without email
@app.route('/api/test-certificate/<int:participant_id>', methods=['GET'])
def test_certificate(participant_id):
    """Test certificate generation without sending email"""
    try:
        print(f"[TEST-CERT] Testing certificate generation for participant ID: {participant_id}")
        
        # Use session.get() instead of deprecated query.get()
        participant = db.session.get(Participant, participant_id)
        if not participant:
            return jsonify({
                "status": "error",
                "message": "Participant not found"
            }), 404
            
        print(f"[TEST-CERT] Found participant: {participant.name}")
        
        # Check certificate generation schedule
        now = datetime.now()
        current_date = now.date()
        
        # Allow testing during August 2025 (entire month for testing)
        august_2025_start = datetime(2025, 8, 1).date()
        august_2025_end = datetime(2025, 8, 31).date()
        
        # Allow testing from September 5, 2025 at 5:00 PM onwards
        conference_start = datetime(2025, 9, 5, 17, 0, 0)  # September 5, 2025 at 5:00 PM
        
        testing_allowed = False
        
        if august_2025_start <= current_date <= august_2025_end:
            # August 2025 testing period
            testing_allowed = True
            print(f"[TEST-CERT] Testing allowed - August 2025 testing period ({current_date})")
        elif now >= conference_start:
            # After conference start time
            testing_allowed = True
            print(f"[TEST-CERT] Testing allowed - Conference period active since {conference_start}")
        else:
            # Not allowed yet
            testing_allowed = False
            restriction_message = f"Certificate generation will be available from September 5, 2025 at 5:00 PM. Current time: {now.strftime('%B %d, %Y at %I:%M %p')}"
            print(f"[TEST-CERT] Testing restricted - {restriction_message}")
        
        if not testing_allowed:
            return jsonify({
                "status": "error",
                "message": "Certificate generation is not available at this time",
                "details": f"Certificate generation will be available from September 5, 2025 at 5:00 PM. Current time: {now.strftime('%B %d, %Y at %I:%M %p')}",
                "available_from": "September 5, 2025 at 5:00 PM"
            }), 403
        
        # Generate certificate HTML
        if participant.cert_type == 'service':
            html = render_template_string(
                SERVICE_CERTIFICATE_TEMPLATE,
                name=participant.name,
                service_text=CERT_SERVICE_TEXT,
                certificate_id=participant.certificate_id,
                chairman_signature=CHAIRMAN_SIGNATURE,
                secretary_signature=SECRETARY_SIGNATURE,
                logo=MDCAN_LOGO
            )
        else:
            html = render_template_string(
                PARTICIPATION_CERTIFICATE_TEMPLATE,
                name=participant.name,
                event_text=CERT_EVENT_TEXT,
                certificate_id=participant.certificate_id,
                president_signature=PRESIDENT_SIGNATURE,
                chairman_signature=CHAIRMAN_SIGNATURE,
                logo=MDCAN_LOGO
            )
        
        # Test PDF generation
        if globals().get('PDF_GENERATION_AVAILABLE', False):
            try:
                pdf = pdfkit.from_string(html, False, configuration=PDF_CONFIG)
                print(f"[TEST-CERT] PDF generated successfully, size: {len(pdf)} bytes")
                pdf_status = "success"
                pdf_size = len(pdf)
            except Exception as e:
                print(f"[TEST-CERT] PDF generation failed: {e}")
                pdf_status = f"failed: {str(e)}"
                pdf_size = 0
        else:
            pdf_status = "unavailable"
            pdf_size = 0
        
        return jsonify({
            "status": "success",
            "participant": {
                "id": participant.id,
                "name": participant.name,
                "email": participant.email,
                "cert_type": participant.cert_type,
                "certificate_id": participant.certificate_id
            },
            "pdf_generation": {
                "status": pdf_status,
                "size_bytes": pdf_size,
                "available": globals().get('PDF_GENERATION_AVAILABLE', False)
            },
            "email_config": {
                "configured": bool(EMAIL_HOST and EMAIL_USER and EMAIL_PASSWORD),
                "host_set": bool(EMAIL_HOST),
                "user_set": bool(EMAIL_USER),
                "password_set": bool(EMAIL_PASSWORD)
            },
            "html_preview": html[:200] + "..." if len(html) > 200 else html
        })
        
    except Exception as e:
        print(f"[TEST-CERT] Error: {str(e)}")
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500

@app.route('/api/programs', methods=['GET'])
def get_programs():
    """Get all conference programs/sessions"""
    try:
        # For now, return empty array with sample structure
        # This can be expanded later when program management is implemented
        sample_programs = [
            {
                "id": 1,
                "title": "Opening Ceremony",
                "description": "Welcome and conference opening",
                "program_type": "ceremony",
                "start_time": "2025-09-01T09:00:00",
                "end_time": "2025-09-01T10:00:00",
                "venue": "Main Auditorium",
                "speaker_name": "Prof. Aminu Mohammed",
                "speaker_bio": "MDCAN President",
                "capacity": 500,
                "is_mandatory": True,
                "requires_registration": False,
                "status": "scheduled"
            }
        ]
        
        return jsonify(sample_programs), 200
        
    except Exception as e:
        print(f"Error in get_programs: {e}")
        return jsonify({"error": "Failed to fetch programs", "message": str(e)}), 500

@app.route('/api/notifications', methods=['GET'])
def get_notifications():
    """Get all notifications"""
    try:
        # For now, return empty array with sample structure
        # This can be expanded later when notification system is implemented
        sample_notifications = [
            {
                "id": 1,
                "title": "Welcome to MDCAN BDM 2025",
                "message": "Thank you for registering for the conference. Check your email for updates.",
                "type": "info",
                "priority": "normal",
                "created_at": "2025-08-17T12:00:00",
                "is_active": True,
                "target_audience": "all"
            }
        ]
        
        return jsonify(sample_notifications), 200
        
    except Exception as e:
        print(f"Error in get_notifications: {e}")
        return jsonify({"error": "Failed to fetch notifications", "message": str(e)}), 500

@app.route('/api/check-ins/day/<int:day>', methods=['GET'])
def get_check_ins(day):
    """Get check-ins for a specific day"""
    try:
        # Mock data for now - in a real app this would come from a check-in system
        check_ins = []
        
        # Try to get participants who would be checked in
        try:
            participants = Participant.query.all()
            # For demo purposes, simulate some participants being checked in
            for i, participant in enumerate(participants[:min(5, len(participants))]):
                if i % 2 == 0:  # Every other participant for variety
                    check_ins.append({
                        "id": participant.id,
                        "participant_id": participant.id,
                        "name": participant.name,
                        "email": participant.email,
                        "check_in_time": "09:00:00",
                        "day": day,
                        "status": "present"
                    })
        except Exception as db_error:
            print(f"Database query error in check-ins: {db_error}")
            # Return empty list if database query fails
            pass
        
        return jsonify({
            "day": day,
            "check_ins": check_ins,
            "total": len(check_ins)
        }), 200
        
    except Exception as e:
        print(f"Error in get_check_ins: {e}")
        return jsonify({"error": "Failed to fetch check-ins", "message": str(e)}), 500

@app.route('/api/stats', methods=['GET'])
def get_stats():
    """Get conference statistics"""
    try:
        # Get participant count from database
        total_participants = 0
        certificates_sent = 0
        certificates_pending = 0
        participation_certificates = 0
        service_certificates = 0
        certificates_failed = 0
        
        try:
            # Try to query the database
            participants = Participant.query.all()
            total_participants = len(participants)
            
            for participant in participants:
                if participant.cert_sent:
                    certificates_sent += 1
                else:
                    certificates_pending += 1
                    
                if participant.cert_type == 'participation':
                    participation_certificates += 1
                elif participant.cert_type == 'service':
                    service_certificates += 1
                    
        except Exception as db_error:
            print(f"Database query error in stats: {db_error}")
            # Return default stats if database query fails
            pass
        
        stats = {
            "participants": {
                "total": total_participants,
                "certificates_sent": certificates_sent,
                "certificates_pending": certificates_pending,
                "participation_certificates": participation_certificates,
                "service_certificates": service_certificates,
                "certificates_failed": certificates_failed
            },
            "programs": {
                "total": 10,
                "completed": 0,
                "upcoming": 10
            },
            "certificates": {
                "total": total_participants,
                "sent": certificates_sent,
                "pending": certificates_pending,
                "failed": certificates_failed
            },
            "feedback": {
                "total_responses": 0,
                "average_rating": 0.0,
                "top_rated_sessions": []
            }
        }
        
        return jsonify(stats), 200
        
    except Exception as e:
        print(f"Error in get_stats: {e}")
        return jsonify({"error": "Failed to fetch stats", "message": str(e)}), 500

# Catch-all route for React Router (must be last)
@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def serve_react_app(path):
    """Serve the React application for all non-API routes"""
    try:
        print(f"🔍 Serving React route: '{path}'")
        
        # If it's an API request that doesn't match any endpoint, return 404
        if path.startswith('api/'):
            print(f"❌ API endpoint not found: {path}")
            return jsonify({"error": "API endpoint not found"}), 404
            
        # For the root path or any other path, serve index.html
        if FRONTEND_BUILD_FOLDER and os.path.exists(FRONTEND_BUILD_FOLDER):
            index_path = os.path.join(FRONTEND_BUILD_FOLDER, 'index.html')
            print(f"🔍 Checking index.html at: {index_path}")
            
            if os.path.exists(index_path):
                print(f"✅ Serving index.html for route: '{path}'")
                return send_file(index_path)
            else:
                print(f"❌ index.html not found at: {index_path}")
                return "Frontend not built. Please run 'npm run build' in the frontend directory.", 500
        else:
            print(f"❌ Frontend build folder not found: {FRONTEND_BUILD_FOLDER}")
            return "Frontend build folder not found.", 500
            
    except Exception as e:
        print(f"❌ Error serving React app for path '{path}': {e}")
        return f"Error loading application: {str(e)}", 500

# Initialize the application
if __name__ == "__main__":
    port = int(os.environ.get('PORT', 8080))  # Use 8080 for Digital Ocean compatibility
    app.run(host='0.0.0.0', port=port, debug=False)
