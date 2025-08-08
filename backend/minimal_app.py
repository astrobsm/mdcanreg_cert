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
if os.path.exists('frontend/build'):
    FRONTEND_BUILD_FOLDER = 'frontend/build'
    static_folder = 'frontend/build'
elif os.path.exists('../frontend/build'):
    FRONTEND_BUILD_FOLDER = '../frontend/build'
    static_folder = '../frontend/build'
else:
    # Fallback to backend/static if frontend build doesn't exist
    FRONTEND_BUILD_FOLDER = 'static' if os.path.exists('static') else None
    static_folder = 'static' if os.path.exists('static') else None

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
CERT_EVENT_TEXT = "MDCAN BDM 14th – 2025 held in Enugu on 1st – 6th September, 2025"
CERT_SERVICE_TEXT = "the successful hosting of the MDCAN BDM 14th – 2025 on 1st – 6th September 2025"

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

@app.route('/api/health')
def health():
    """Health check endpoint"""
    return jsonify({"status": "ok"})

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
                president_signature="", # Base64 encoded signature would go here
                chairman_signature="", # Base64 encoded signature would go here
                logo="" # Base64 encoded logo would go here
            )
        else:
            # Default to participation certificate
            html = render_template_string(
                PARTICIPATION_CERTIFICATE_TEMPLATE,
                name=participant.name,
                event_text=CERT_EVENT_TEXT,
                certificate_id=participant.certificate_id,
                president_signature="", # Base64 encoded signature would go here
                chairman_signature="", # Base64 encoded signature would go here
                logo="" # Base64 encoded logo would go here
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

# Serve the React frontend
@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def serve_react(path):
    """Serve the React frontend"""
    if not path or path == '/':
        if static_folder and os.path.exists(os.path.join(static_folder, 'index.html')):
            return send_from_directory(static_folder, 'index.html')
        return jsonify({
            "status": "ok",
            "message": "MDCAN BDM 2025 Certificate Platform - Minimal Backend",
            "frontend": "Not available in minimal mode",
            "environment": {
                "DATABASE_URL": bool(os.environ.get('DATABASE_URL')),
                "EMAIL_HOST": bool(os.environ.get('EMAIL_HOST'))
            }
        })
    
    if static_folder and os.path.exists(os.path.join(static_folder, path)):
        return send_from_directory(static_folder, path)
    
    # For API routes, let them fall through to other handlers
    if path.startswith('api/'):
        return None
    
    # For React router routes, return index.html
    if static_folder and os.path.exists(os.path.join(static_folder, 'index.html')):
        return send_from_directory(static_folder, 'index.html')
    
    # Return 404 for other paths
    return jsonify({"error": "Path not found"}), 404

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
                president_signature="", # Base64 encoded signature would go here
                chairman_signature="", # Base64 encoded signature would go here
                logo="" # Base64 encoded logo would go here
            )
        else:
            # Default to participation certificate
            html = render_template_string(
                PARTICIPATION_CERTIFICATE_TEMPLATE,
                name=participant.name,
                event_text=CERT_EVENT_TEXT,
                certificate_id=participant.certificate_id,
                president_signature="", # Base64 encoded signature would go here
                chairman_signature="", # Base64 encoded signature would go here
                logo="" # Base64 encoded logo would go here
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

# Initialize the application
if __name__ == "__main__":
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
