# MDCAN BDM 2025 Certificate Platform - Deployment Guide

This document provides streamlined instructions for deploying the MDCAN BDM 2025 Certificate Platform to Digital Ocean or other hosting environments.

## Preparation Steps

1. Run the verification script to ensure all functionality is working:
   ```
   verify_deployment_readiness.bat
   ```

2. If the main app fails but the minimal app passes, you can use the minimal app for deployment which has all the same functionality but without dependency issues.

## Deployment Options

### Option 1: Deploy using Docker (Recommended)

1. Make sure Docker is installed on your deployment server.

2. Build the Docker image:
   ```
   docker build -t mdcan-certificate-platform .
   ```

3. Run the container:
   ```
   docker run -d -p 80:5000 -e DATABASE_URL=your_database_url -e EMAIL_HOST=your_smtp_server -e EMAIL_PORT=587 -e EMAIL_USER=your_email -e EMAIL_PASSWORD=your_password -e EMAIL_FROM="MDCAN BDM 2025 <noreply@mdcan.org>" mdcan-certificate-platform
   ```

### Option 2: Deploy to Digital Ocean App Platform

1. Push your code to GitHub.

2. Connect your GitHub repository to Digital Ocean App Platform.

3. Configure the following environment variables:
   - `DATABASE_URL`: Your PostgreSQL database URL
   - `EMAIL_HOST`: SMTP server address
   - `EMAIL_PORT`: SMTP port (usually 587)
   - `EMAIL_USER`: SMTP username
   - `EMAIL_PASSWORD`: SMTP password
   - `EMAIL_FROM`: From email address for certificates

4. Deploy the application.

## Database Setup

1. Create a PostgreSQL database on Digital Ocean or your preferred provider.

2. Update the `DATABASE_URL` environment variable to point to your database.

3. The application will automatically create the required tables on first run.

## Email Configuration

For certificate sending functionality to work, configure these environment variables:
- `EMAIL_HOST`: Your SMTP server (e.g., smtp.gmail.com)
- `EMAIL_PORT`: SMTP port (typically 587 for TLS)
- `EMAIL_USER`: Your email username
- `EMAIL_PASSWORD`: Your email password
- `EMAIL_FROM`: Sender email address shown to recipients

## Troubleshooting

If you encounter issues during deployment:

1. Check the application logs to identify the specific error.

2. Verify database connectivity and email settings.

3. Try deploying the minimal app (`backend/minimal_app.py`) which has fewer dependencies.

4. Make sure all required environment variables are set correctly.

## Special Considerations for Digital Ocean

When deploying to Digital Ocean App Platform:

1. Specify the correct build command:
   ```
   pip install -r backend/requirements.txt
   ```

2. Specify the run command:
   ```
   gunicorn --bind 0.0.0.0:$PORT app:app
   ```

3. Add the `requirements.txt` file in the app root directory pointing to the backend requirements.

For more detailed deployment instructions, refer to the `DIGITAL-OCEAN-DEPLOYMENT.md` file.
