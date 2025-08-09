# MDCAN BDM 2025 Certificate Platform

## Project Overview

This is a full-stack certificate generation platform for the MDCAN BDM 14th - 2025 conference.

### Key Features
- Certificate generation for participants and service contributors
- Email delivery system with SMTP integration
- PostgreSQL database for participant management
- React.js frontend with responsive design
- Docker containerization for easy deployment

### Technology Stack
- **Frontend**: React.js, JavaScript (no TypeScript)
- **Backend**: Python Flask with SQLAlchemy
- **Database**: PostgreSQL with optimized indexes
- **Deployment**: Digital Ocean App Platform
- **Containerization**: Docker with multi-stage builds

### Project Structure
```
/
├── backend/                 # Flask backend application
│   ├── app.py              # Main Flask application
│   ├── minimal_app.py      # Lightweight version for deployment
│   ├── database.py         # Database models and connection
│   └── requirements.txt    # Python dependencies
├── frontend/               # React frontend application
│   ├── src/                # React source code
│   ├── public/             # Static assets
│   └── package.json        # Node.js dependencies
├── digital_ocean_app.py    # Digital Ocean deployment entry point
├── Dockerfile              # Container configuration
├── requirements.txt        # Root-level Python dependencies
└── .do/app.yaml           # Digital Ocean App Platform spec

## Quick Start

### Local Development
1. **Backend Setup**:
   ```bash
   cd backend
   pip install -r requirements.txt
   python app.py
   ```

2. **Frontend Setup**:
   ```bash
   cd frontend
   npm install
   npm start
   ```

3. **Database Setup**:
   - Set up PostgreSQL database
   - Configure DATABASE_URL environment variable
   - Run database migrations

### Digital Ocean Deployment

1. **Using App Spec** (Recommended):
   - Create new app from GitHub repository
   - Import app spec from `.do/app.yaml`
   - Configure environment variables
   - Deploy

2. **Manual Configuration**:
   - Repository: `astrobsm/mdcanreg_cert`
   - Dockerfile: Use root-level Dockerfile
   - Run command: `gunicorn --bind 0.0.0.0:${PORT:-8080} digital_ocean_app:app`

### Environment Variables
```
DATABASE_URL=postgresql://username:password@host:port/dbname
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USER=your_email@gmail.com
EMAIL_PASSWORD=your_app_password
EMAIL_FROM=MDCAN BDM 2025 <your_email@gmail.com>
```

### Certificate Types

1. **Certificate of Participation**
   - For conference attendees
   - Text: "participated in the MDCAN BDM 14th – 2025 held in Enugu on 1st – 6th September, 2025"

2. **Acknowledgement of Service**  
   - For volunteers, organizers, and staff
   - Text: "exceptional service towards the successful hosting of the MDCAN BDM 14th – 2025 on 1st – 6th September 2025"

Both certificates include signatures of Prof. Aminu Mohammed (MDCAN President) and Prof. Appolos Ndukuba (LOC Chairman).

### Development Guidelines
- Use JavaScript (not TypeScript) for React components
- Follow React functional component patterns with hooks
- Use Flask best practices for API development
- Ensure proper error handling for email and PDF generation
- Maintain responsive design for all devices
- Include proper validation for form inputs

### Troubleshooting

**Common Issues:**
1. **Port Binding**: App must bind to port 8080 for Digital Ocean
2. **Database Connection**: Verify DATABASE_URL format and accessibility
3. **Email Sending**: Check SMTP credentials and Gmail app password
4. **PDF Generation**: Ensure wkhtmltopdf is installed in container

**Health Checks:**
- App includes `/health` endpoint for monitoring
- Use `digital_ocean_app.py` for deployment reliability

### Support
For technical issues or questions, refer to:
- Application logs in Digital Ocean dashboard
- Database health check endpoints
- Email delivery status in application

## License
This project is proprietary software developed for MDCAN BDM 14th - 2025.
