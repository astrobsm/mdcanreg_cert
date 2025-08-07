@echo off
REM MDCAN BDM 2025 Certificate Platform - Database Setup Script
REM This script sets up PostgreSQL database and initializes the application

echo ========================================
echo MDCAN BDM 2025 Certificate Platform
echo Database Setup Script
echo ========================================
echo.

echo Step 1: Installing Python dependencies...
pip install -r requirements.txt
if %errorlevel% neq 0 (
    echo ERROR: Failed to install Python dependencies
    pause
    exit /b 1
)
echo ✅ Python dependencies installed successfully!
echo.

echo Step 2: Setting up environment variables...
if not exist .env (
    copy .env.example .env
    echo ✅ .env file created from template
    echo ⚠️  Please edit .env file with your actual email password
) else (
    echo ℹ️  .env file already exists
)
echo.

echo Step 3: Creating PostgreSQL database...
echo Please ensure PostgreSQL is running and accessible with:
echo   Host: localhost
echo   User: postgres  
echo   Password: natiss_natiss
echo.
pause

python init_db.py
if %errorlevel% neq 0 (
    echo ERROR: Database initialization failed
    echo.
    echo Please ensure:
    echo 1. PostgreSQL is installed and running
    echo 2. User 'postgres' exists with password 'natiss_natiss'
    echo 3. PostgreSQL is accessible on localhost:5432
    pause
    exit /b 1
)

echo.
echo ========================================
echo ✅ Setup completed successfully!
echo ========================================
echo.
echo Database Information:
echo   Database: bdmcertificate_db
echo   Host: localhost
echo   User: postgres
echo   Password: natiss_natiss
echo.
echo To start the application:
echo   python app.py
echo.
echo The application will be available at:
echo   http://localhost:5000
echo.
echo Next steps:
echo 1. Edit .env file with your Gmail app password
echo 2. Replace placeholder images in ../frontend/public/
echo 3. Run 'python app.py' to start the server
echo.
pause
