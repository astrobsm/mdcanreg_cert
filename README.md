# MDCAN 14th Biennial Delegates' Meeting and SCIENTIFIC Conference

A full-stack web application that automatically generates and emails certificates of participation for the MDCAN 14th Biennial Delegates' Meeting and SCIENTIFIC Conference.

## Features

- **Participant Management**: Add and manage conference participants
- **Dual Certificate Types**: 
  - Certificate of Participation (for attendees)
  - Acknowledgement of Service (for volunteers/organizers)
- **Automatic Certificate Generation**: Generate PDF certificates with participant names and appropriate content
- **Email Integration**: Automatically send certificates to participants' email addresses
- **Digital Signatures**: Include signatures of Prof. Aminu Mohammed (MDCAN President) and Prof. Appolos Ndukuba (LOC Chairman)
- **Status Tracking**: Track certificate delivery status for each participant
- **Bulk Operations**: Send certificates to all participants at once
- **Certificate Preview**: Preview both certificate types before sending
- **Responsive Design**: Optimized for desktop, tablet, and mobile devices

## Tech Stack

- **Frontend**: React.js with Create React App
- **Backend**: Python Flask
- **Database**: PostgreSQL
- **PDF Generation**: pdfkit with wkhtmltopdf
- **Email**: SMTP (Gmail supported)
- **Deployment**: Docker, Digital Ocean, Vercel

## Setup Instructions

### Prerequisites

1. Node.js (v14 or higher)
2. Python 3.8+
3. PostgreSQL database
4. wkhtmltopdf (for PDF generation)
5. Docker and Docker Compose (for containerized deployment, optional)

### Traditional Setup

#### Frontend Setup

1. Install Node.js dependencies:
```bash
cd frontend
npm install
```

2. Start the development server:
```bash
npm start
```

The frontend will run on `http://localhost:3000`

#### Backend Setup

1. Navigate to the backend directory:
```bash
cd backend
```

2. Create a virtual environment:
```bash
python -m venv venv
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate
```

3. Install Python dependencies:
```bash
pip install -r requirements.txt
```

4. Install wkhtmltopdf:
   - **Windows**: Download from https://wkhtmltopdf.org/downloads.html
   - **macOS**: `brew install wkhtmltopdf`
   - **Ubuntu/Debian**: `sudo apt-get install wkhtmltopdf`

5. Set up environment variables:
```bash
cp .env.example .env
```

Edit the `.env` file with your configuration:
- Database URL
- Email settings (Gmail recommended)

6. Initialize the database:
```bash
python app.py
```

The backend will run on `http://localhost:5000`

### Docker Compose Setup (Recommended)

We provide Docker Compose configuration for both development and production environments:

#### Development Setup

Run the following command to start the development environment:

```bash
# On Windows
deploy.bat dev

# On Linux/macOS
./deploy.sh dev
```

This will start:
- PostgreSQL database on port 5432
- Backend Flask server on port 5000
- Frontend development server on port 3000

#### Production Setup

For production deployment:

```bash
# On Windows
deploy.bat prod

# On Linux/macOS
./deploy.sh prod
```

This will build and start:
- PostgreSQL database
- Combined frontend and backend application on port 5000

#### Other Commands

```bash
# Stop all containers
deploy.bat stop  # or ./deploy.sh stop

# View development logs
deploy.bat logs-dev  # or ./deploy.sh logs-dev

# View production logs
deploy.bat logs-prod  # or ./deploy.sh logs-prod
```

### Database Setup

1. Create a PostgreSQL database named `mdcan_certificates`
2. Update the `DATABASE_URL` in your `.env` file
3. The application will automatically create the required tables

### Email Configuration

For Gmail, you'll need to:
1. Enable 2-factor authentication
2. Generate an App Password
3. Use the App Password in the `EMAIL_PASSWORD` field

### Signature Images

Place the signature images in the `public` directory:
- `public/president-signature.png` - Prof. Aminu Mohammed's signature
- `public/chairman-signature.png` - Prof. Appolos Ndukuba's signature

## Deployment

For detailed deployment instructions, see:
- [DOCKER-COMPOSE-DEPLOYMENT.md](DOCKER-COMPOSE-DEPLOYMENT.md) - Deploy using Docker Compose on Digital Ocean
- [DIGITAL-OCEAN-DEPLOYMENT.md](DIGITAL-OCEAN-DEPLOYMENT.md) - Deploy directly on Digital Ocean

### Deployment to Vercel

1. Install Vercel CLI:
```bash
npm i -g vercel
```

2. Login to Vercel:
```bash
vercel login
```

3. Set environment variables in Vercel dashboard:
   - `DATABASE_URL`
   - `EMAIL_HOST`
   - `EMAIL_PORT`
   - `EMAIL_USER`
   - `EMAIL_PASSWORD`
   - `EMAIL_FROM`

4. Deploy:
```bash
vercel
```

## Usage

1. **Add Participants**: Use the "Add Participant" tab to add participant details and select certificate type
2. **View Participants**: Check the "Participants List" tab to see all registered participants with their certificate types
3. **Preview Certificate**: Use the "Certificate Preview" tab to see how both certificate types will look
4. **Send Certificates**: 
   - Send individual certificates using the "Send Certificate" button
   - Send all certificates at once using "Send All Certificates"

## Certificate Types

### Certificate of Participation
For conference attendees who participated in the event:
- **Title**: "CERTIFICATE OF PARTICIPATION"
- **Content**: "This is to certify that [Name] participated in the MDCAN BDM 14th – 2025 held in Enugu on 1st – 6th September, 2025"

### Acknowledgement of Service  
For volunteers, organizers, and staff who contributed to the conference:
- **Title**: "ACKNOWLEDGEMENT OF SERVICE"
- **Content**: "This is to acknowledge and appreciate the exceptional service of [Name] towards the successful hosting of the MDCAN BDM 14th – 2025 on 1st – 6th September 2025"

Both certificate types include signatures of Prof. Aminu Mohammed (MDCAN President) and Prof. Appolos Ndukuba (LOC Chairman).

## Environment Variables

| Variable | Description | Example |
|----------|-------------|---------|
| `DATABASE_URL` | PostgreSQL connection string | `postgresql://username:password@localhost/mdcan_certificates` |
| `EMAIL_HOST` | SMTP server host | `smtp.gmail.com` |
| `EMAIL_PORT` | SMTP server port | `587` |
| `EMAIL_USER` | Email username | `your-email@gmail.com` |
| `EMAIL_PASSWORD` | Email password/app password | `your-app-password` |
| `EMAIL_FROM` | From email address | `MDCAN BDM 2025 <your-email@gmail.com>` |

## Support

For issues or questions, please contact the development team or create an issue in the project repository.

## License

This project is created for the MDCAN BDM 14th - 2025 conference.
