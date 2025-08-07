# MDCAN BDM 2025 Certificate Platform - Deployment Guide

## Local Development

### Frontend (React)
1. Install dependencies: `npm install`
2. Start development server: `npm start`
3. Access at `http://localhost:3000`

### Backend (Python Flask)
1. Navigate to backend: `cd backend`
2. Create virtual environment: `python -m venv venv`
3. Activate environment: `venv\Scripts\activate` (Windows) or `source venv/bin/activate` (Mac/Linux)
4. Install dependencies: `pip install -r requirements.txt`
5. Install wkhtmltopdf from https://wkhtmltopdf.org/downloads.html
6. Copy `.env.example` to `.env` and configure
7. Run server: `python app.py`

## Deployment to Vercel

### Prerequisites
- Vercel account
- PostgreSQL database (recommended: Vercel Postgres)
- Email service (Gmail with App Password recommended)

### Steps
1. Install Vercel CLI: `npm install -g vercel`
2. Login to Vercel: `vercel login`
3. Set up environment variables in Vercel dashboard:
   - `DATABASE_URL`: Your PostgreSQL connection string
   - `EMAIL_HOST`: smtp.gmail.com
   - `EMAIL_PORT`: 587
   - `EMAIL_USER`: your-email@gmail.com
   - `EMAIL_PASSWORD`: your-app-password
   - `EMAIL_FROM`: MDCAN BDM 2025 <your-email@gmail.com>

4. Deploy: `vercel`

### Database Setup
1. Create PostgreSQL database
2. Update `DATABASE_URL` environment variable
3. The application will automatically create required tables

### Signature Images
1. Add `president-signature.png` to the `public` directory
2. Add `chairman-signature.png` to the `public` directory
3. Images should be approximately 200x60 pixels with transparent background

## Configuration

### Email Setup (Gmail)
1. Enable 2-factor authentication on your Gmail account
2. Generate an App Password:
   - Go to Google Account settings
   - Security → App passwords
   - Generate password for "Mail"
3. Use the app password in `EMAIL_PASSWORD` environment variable

### Database Schema
The application uses these tables:
- `participant`: Stores participant information and certificate status

### Environment Variables
- `DATABASE_URL`: PostgreSQL connection string
- `EMAIL_HOST`: SMTP server (default: smtp.gmail.com)
- `EMAIL_PORT`: SMTP port (default: 587)
- `EMAIL_USER`: Email username
- `EMAIL_PASSWORD`: Email password/app password
- `EMAIL_FROM`: From email address

## Production Considerations

1. **Security**: Use environment variables for all sensitive data
2. **Database**: Use a managed PostgreSQL service
3. **Email**: Use a reliable email service provider
4. **File Storage**: Signature images should be served from a CDN
5. **Error Handling**: Monitor for failed certificate deliveries
6. **Backup**: Regular database backups for participant data

## Troubleshooting

### Common Issues
1. **PDF Generation Fails**: Ensure wkhtmltopdf is installed and accessible
2. **Email Delivery Fails**: Check email credentials and app password
3. **Database Connection**: Verify DATABASE_URL format and credentials
4. **Signature Images Not Showing**: Check file paths and permissions

### Error Logs
- Frontend errors: Browser console
- Backend errors: Terminal/server logs
- Email delivery: Check email service logs
