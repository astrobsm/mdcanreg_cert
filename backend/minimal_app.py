"""
Enhanced minimal version of the backend app that provides core functionality
without pandas/numpy dependencies for stable deployment.
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
import pdfkit
from jinja2 import Template
from threading import Thread

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

# Configure database connection
DATABASE_URL = os.environ.get('DATABASE_URL', 'sqlite:///mdcan_certificates.db')
if DATABASE_URL.startswith('postgres://'):
    DATABASE_URL = DATABASE_URL.replace('postgres://', 'postgresql://', 1)

app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE_URL
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {
    'pool_pre_ping': True,
    'pool_recycle': 300
}

# Initialize database
db = SQLAlchemy(app)

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
        db.create_all()
        print("Database tables created successfully")
    except Exception as e:
        print(f"Error creating database tables: {e}")

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
        # Try multiple possible paths for the signature files
        possible_paths = [
            f'frontend/public/{filename}',
            f'backend/static/{filename}',
            f'../frontend/public/{filename}',
            f'./frontend/public/{filename}',
            f'/app/frontend/public/{filename}',
            f'/app/backend/static/{filename}',
            f'public/{filename}',
            f'static/{filename}',
            filename
        ]
        
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

# Load signature files at startup
PRESIDENT_SIGNATURE = load_signature_file('president-signature.jpg')
CHAIRMAN_SIGNATURE = load_signature_file('chairman-signature.png') 
SECRETARY_SIGNATURE = load_signature_file('Dr_Augustine_Duru_signature.jpg')

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
                <img src="data:image/jpeg;base64,{{ president_signature }}" alt="President's Signature">
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
                <img src="data:image/jpeg;base64,{{ secretary_signature }}" alt="Secretary's Signature">
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
    """Health check endpoint"""
    return jsonify({"status": "ok"})

@app.route('/health')
def health_check():
    """Health check endpoint for Digital Ocean"""
    return jsonify({"status": "healthy"})

@app.route('/static/<path:filename>')
def serve_static_assets(filename):
    """Serve static assets for production deployment"""
    try:
        # Try to serve from the frontend build static directory
        static_path = os.path.join(FRONTEND_BUILD_FOLDER, 'static', filename)
        if os.path.exists(static_path):
            return send_file(static_path)
        
        # Fallback to project root static
        root_static_path = os.path.join(os.getcwd(), 'static', filename)
        if os.path.exists(root_static_path):
            return send_file(root_static_path)
            
        return "File not found", 404
    except Exception as e:
        return f"Error serving static file: {str(e)}", 500

@app.route('/<filename>')
def serve_static_files(filename):
    """Serve signature files and other static assets"""
    # Define the files that should be served directly
    static_files = [
        'president-signature.jpg',
        'chairman-signature.png', 
        'Dr_Augustine_Duru_signature.jpg',
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
            pdf = pdfkit.from_string(html, False)
        except Exception as e:
            # For environments where wkhtmltopdf might not be available
            return jsonify({
                "status": "error",
                "message": f"Error generating PDF: {str(e)}. HTML version returned instead.",
                "html": html
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

# Email certificate function
@app.route('/api/send-certificate/<int:participant_id>', methods=['POST'])
def send_certificate(participant_id):
    try:
        participant = Participant.query.get(participant_id)
        if not participant:
            return jsonify({
                "status": "error",
                "message": "Participant not found"
            }), 404
            
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
            pdf = pdfkit.from_string(html, False)
        except Exception as e:
            return jsonify({
                "status": "error",
                "message": f"Error generating PDF: {str(e)}"
            }), 500
            
        # Create a temporary file for the PDF
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.pdf')
        temp_file.write(pdf)
        temp_file.close()
        
        # Check if email configuration is available
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
                server = smtplib.SMTP(EMAIL_HOST, EMAIL_PORT)
                server.starttls()
                server.login(EMAIL_USER, EMAIL_PASSWORD)
                server.send_message(msg)
                server.quit()
                
                # Update participant record
                with app.app_context():
                    participant.cert_sent = True
                    participant.cert_sent_date = datetime.utcnow()
                    db.session.commit()
            except Exception as e:
                print(f"Error sending email: {e}")
            finally:
                # Clean up temp file
                try:
                    os.unlink(temp_file.name)
                except:
                    pass
                    
        # Start email thread
        email_thread = Thread(target=send_email_task)
        email_thread.start()
        
        return jsonify({
            "status": "success",
            "message": "Certificate has been queued for sending"
        })
    except Exception as e:
        # Clean up temp file if it exists
        try:
            os.unlink(temp_file.name)
        except:
            pass
            
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500

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

@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def serve_react(path):
    """Serve the React frontend"""
    try:
        print(f"=== SERVE_REACT DEBUG START ===")
        print(f"Route requested: '{path}'")
        print(f"static_folder: {static_folder}")
        print(f"FRONTEND_BUILD_FOLDER: {FRONTEND_BUILD_FOLDER}")
        
        # Handle API routes - return 404 if specific route not found
        if path and path.startswith('api/'):
            print(f"API route requested: {path} - route not found")
            return jsonify({"error": "API endpoint not found", "path": path}), 404
        
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

# Initialize the application
if __name__ == "__main__":
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
