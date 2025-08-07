# Local Testing Guide

This guide provides step-by-step instructions for setting up and testing the MDCAN BDM 2025 Certificate Platform locally.

## Setup Options

You have two main options for local testing:

1. **Traditional Setup**: Separate frontend and backend installations
2. **Docker Compose Setup**: Containerized development environment (recommended)

## Option 1: Traditional Setup

### Step 1: Set Up the Backend

1. Navigate to the backend directory:
   ```
   cd backend
   ```

2. Create a virtual environment:
   ```
   # Windows
   python -m venv venv
   venv\Scripts\activate

   # macOS/Linux
   python -m venv venv
   source venv/bin/activate
   ```

3. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

4. Set up the PostgreSQL database:
   ```
   # Windows (using psql CLI)
   psql -U postgres -f create_comprehensive_database.sql

   # Alternative: Run the setup script
   setup-database.bat
   ```

5. Start the backend server:
   ```
   python app.py
   
   # Or use the provided batch file
   cd ..
   start-backend.bat
   ```

### Step 2: Set Up the Frontend

1. Navigate to the frontend directory:
   ```
   cd frontend
   ```

2. Install dependencies:
   ```
   npm install
   ```

3. Start the development server:
   ```
   npm start
   
   # Or use the provided batch file from the project root
   cd ..
   start-frontend.bat
   ```

4. Access the application at:
   - Frontend: http://localhost:3000
   - Backend API: http://localhost:5000

## Option 2: Docker Compose Setup (Recommended)

### Prerequisites

- Docker Desktop installed and running
- Docker Compose installed

### Step 1: Set Up Environment Variables

1. Copy the example environment file:
   ```
   copy .env.example .env
   ```

2. Update the environment variables as needed, particularly:
   - `EMAIL_USER` and `EMAIL_PASSWORD` for your email provider
   - `EMAIL_FROM` to match your sending address

### Step 2: Start the Development Environment

1. Run the deployment script:
   ```
   # Windows
   deploy.bat dev

   # Linux/macOS
   ./deploy.sh dev
   ```

2. This will start:
   - PostgreSQL database on port 5432
   - Backend Flask server on port 5000
   - Frontend development server on port 3000

3. Access the application at:
   - Frontend: http://localhost:3000
   - Backend API: http://localhost:5000

### Step 3: View Logs (Optional)

To view the logs from the running containers:

```
# Windows
deploy.bat logs-dev

# Linux/macOS
./deploy.sh logs-dev
```

## Testing the Platform

### 1. Register a Participant

1. Go to http://localhost:3000
2. Navigate to the Registration tab
3. Fill out the registration form with:
   - Name: Test User
   - Email: test@example.com
   - Certificate Type: Certificate of Participation
4. Click Submit
5. Verify the success message

### 2. Check the Participants List

1. Navigate to the Participants tab
2. Verify that your test user appears in the list

### 3. Test Certificate Generation

1. Find your test user in the participants list
2. Click on "Generate Certificate"
3. Verify that the certificate is generated and displayed

### 4. Test Email Functionality

1. Find your test user in the participants list
2. Click on "Send Certificate"
3. Verify that the success message appears
4. Check your email inbox for the certificate (may be in spam folder)

## Troubleshooting

### Database Connection Issues

1. Verify PostgreSQL is running:
   ```
   # Windows
   sc query postgresql
   
   # Docker
   docker ps | grep postgres
   ```

2. Check database connectivity:
   ```
   cd backend
   python check_db_connection.py
   ```

### Email Sending Issues

1. Verify your email credentials in `.env`
2. For Gmail, ensure you:
   - Have 2-factor authentication enabled
   - Have generated an App Password
   - Have allowed less secure apps (if using a regular password)

### Frontend-Backend Connection Issues

1. Check that the frontend is configured to connect to http://localhost:5000
2. Verify CORS settings in `backend/app.py`
3. Check the browser console for any connection errors

## Stopping the Environment

### Traditional Setup

1. Stop the frontend: Press Ctrl+C in the frontend terminal
2. Stop the backend: Press Ctrl+C in the backend terminal

### Docker Compose Setup

```
# Windows
deploy.bat stop

# Linux/macOS
./deploy.sh stop
```

This will stop all running containers.
