"""
Modified app.py to use the optimized database connection
This patch file can be applied to your existing app.py
"""

from flask import Flask, request, jsonify, send_file, render_template_string
from flask_cors import CORS
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
from database import db_manager  # Import our optimized database manager

app = Flask(__name__, 
            static_folder='../frontend/build/static',
            static_url_path='/static')
CORS(app)

# Initialize scheduler for program notifications
scheduler = BackgroundScheduler(
    job_defaults={
        'coalesce': True,  # Combine multiple executions of the same job
        'max_instances': 3  # Limit concurrent instances of the same job
    }
)
scheduler.start()

# Initialize the optimized database
db_manager.init_app(app)
db = db_manager.db  # Get the SQLAlchemy instance

# Email configuration with environment variables
EMAIL_HOST = os.environ.get('EMAIL_HOST', 'smtp.gmail.com')
EMAIL_PORT = int(os.environ.get('EMAIL_PORT', 587))
EMAIL_USER = os.environ.get('EMAIL_USER', 'sylvia4douglas@gmail.com')
EMAIL_PASSWORD = os.environ.get('EMAIL_PASSWORD', 'your-app-password')
EMAIL_FROM = os.environ.get('EMAIL_FROM', 'MDCAN BDM 2025 <sylvia4douglas@gmail.com>')

# Create the database tables - using Flask 2.x+ compatible approach
with app.app_context():
    db.create_all()

# Add performance monitoring
@app.before_request
def before_request():
    request.start_time = time.time()

@app.after_request
def after_request(response):
    # Calculate request duration
    duration = time.time() - getattr(request, 'start_time', time.time())
    
    # Log slow requests (more than 500ms)
    if duration > 0.5:
        app.logger.warning(f"Slow request: {request.path} took {duration:.2f}s")
    
    # Add security headers
    response.headers['X-Content-Type-Options'] = 'nosniff'
    response.headers['X-Frame-Options'] = 'DENY'
    response.headers['X-XSS-Protection'] = '1; mode=block'
    
    # Add cache control headers for static assets
    if request.path.startswith('/static'):
        response.headers['Cache-Control'] = 'public, max-age=31536000'
    else:
        response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, max-age=0'
    
    return response

# API rate limiting
request_counts = {}
@app.before_request
def limit_request_rates():
    # Simple rate limiting - could be replaced with a Redis-based solution
    if request.endpoint == 'api_route':  # Adjust for your actual API endpoints
        ip = request.remote_addr
        current_time = time.time()
        
        # Clean up old requests
        for ip_addr in list(request_counts.keys()):
            if current_time - request_counts[ip_addr]['timestamp'] > 60:
                del request_counts[ip_addr]
        
        # Check current IP
        if ip in request_counts:
            if current_time - request_counts[ip]['timestamp'] < 60:
                request_counts[ip]['count'] += 1
                if request_counts[ip]['count'] > 60:  # 60 requests per minute
                    return jsonify({"error": "Rate limit exceeded"}), 429
            else:
                request_counts[ip] = {'count': 1, 'timestamp': current_time}
        else:
            request_counts[ip] = {'count': 1, 'timestamp': current_time}

# Add a health check endpoint
@app.route('/api/health', methods=['GET'])
def health_check():
    try:
        # Check database connection
        engine = db_manager.get_engine()
        with engine.connect() as conn:
            conn.execute("SELECT 1")
        
        return jsonify({
            "status": "healthy",
            "project": "MDCAN BDM 2025 Certificate Platform",
            "timestamp": datetime.utcnow().isoformat(),
            "version": "2.0.0",
            "database": "connected",
            "environment": "optimized"
        })
    except Exception as e:
        app.logger.error(f"Health check failed: {str(e)}")
        return jsonify({
            "status": "unhealthy",
            "project": "MDCAN BDM 2025 Certificate Platform",
            "error": str(e),
            "timestamp": datetime.utcnow().isoformat()
        }), 500

# Add a stats endpoint
@app.route('/api/stats', methods=['GET'])
def get_stats():
    # This will be updated to use our models
    # Keep the original implementation for now
    pass

# Serve React app static files
@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def serve_react_app(path):
    try:
        # Skip static files - they're handled by Flask's built-in static serving
        if path.startswith('static/'):
            # This should not happen since static files are handled by Flask
            return jsonify({'error': 'Static file routing error'}), 404
        
        # Serve other static files (images, etc.)
        if path != "":
            static_file_path = os.path.join('../frontend/build', path)
            if os.path.exists(static_file_path):
                return send_file(static_file_path)
        
        # For root path or any other routes, serve index.html (React Router)
        index_path = '../frontend/build/index.html'
        if os.path.exists(index_path):
            return send_file(index_path)
        else:
            return jsonify({'error': 'Frontend not built. Please run build script first.'}), 500
    except Exception as e:
        app.logger.error(f"Error serving frontend: {str(e)}")
        return jsonify({'error': f'Error serving frontend: {str(e)}'}), 500

# Add a simple health check endpoint at the root path too
@app.route('/health', methods=['GET'])
def root_health_check():
    return jsonify({
        "status": "healthy",
        "project": "MDCAN BDM 2025 Certificate Platform",
        "application": "MDCAN BDM 2025 Certificate Platform",
        "timestamp": datetime.utcnow().isoformat(),
        "version": "2.0.0",
        "environment": "optimized"
    })

# Continue with the rest of your application code...
# Make sure to update any database operations to use the new db instance

# Now add the main routes from the original app.py
# We'll need to copy over any missing routes from app.py

# Add a route for processing participants
@app.route('/api/participants', methods=['GET', 'POST'])
def handle_participants():
    if request.method == 'GET':
        try:
            # Use optimized database access
            engine = db_manager.get_engine()
            with engine.connect() as conn:
                result = conn.execute("SELECT * FROM participants ORDER BY id DESC")
                participants = [dict(zip(result.keys(), row)) for row in result]
            return jsonify(participants)
        except Exception as e:
            app.logger.error(f"Error fetching participants: {str(e)}")
            return jsonify({"error": str(e)}), 500
    elif request.method == 'POST':
        try:
            data = request.json
            
            # Validate required fields
            required_fields = ['name', 'email', 'category']
            for field in required_fields:
                if field not in data:
                    return jsonify({"error": f"Missing required field: {field}"}), 400
            
            # Use optimized database access
            engine = db_manager.get_engine()
            with engine.connect() as conn:
                # Check if email already exists
                result = conn.execute(
                    "SELECT id FROM participants WHERE email = %s", 
                    (data['email'],)
                )
                if result.rowcount > 0:
                    return jsonify({"error": "Participant with this email already exists"}), 409
                
                # Insert new participant
                query = """
                INSERT INTO participants (name, email, category, phone, organization, 
                                          attendance_status, certificate_status, certificate_type, 
                                          registration_date, certificate_id)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                RETURNING id
                """
                
                cert_id = str(uuid.uuid4())
                now = datetime.utcnow()
                
                result = conn.execute(
                    query,
                    (
                        data['name'],
                        data['email'],
                        data['category'],
                        data.get('phone', ''),
                        data.get('organization', ''),
                        data.get('attendance_status', 'Registered'),
                        'Not Generated',
                        data.get('certificate_type', 'Attendance'),
                        now,
                        cert_id
                    )
                )
                
                new_id = result.fetchone()[0]
                
                return jsonify({
                    "id": new_id,
                    "message": "Participant added successfully",
                    "certificate_id": cert_id
                }), 201
                
        except Exception as e:
            app.logger.error(f"Error adding participant: {str(e)}")
            return jsonify({"error": str(e)}), 500

# Run the application with improved server settings
if __name__ == '__main__':
    # In production, consider using gunicorn or uwsgi instead
    app.run(host='0.0.0.0', port=5000, threaded=True)
