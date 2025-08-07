@echo off
REM Comprehensive Database Setup Script for MDCAN BDM 2025 Certificate Platform
REM Created on August 5, 2025

echo ========================================================================
echo        MDCAN BDM 2025 Certificate Platform Database Setup
echo ========================================================================
echo.

REM Set database connection parameters
set DB_HOST=localhost
set DB_PORT=5432
set DB_USER=postgres
set DB_PASSWORD=natiss_natiss
set DB_NAME=mdcan042_db

echo Database Parameters:
echo - Host: %DB_HOST%
echo - Port: %DB_PORT%
echo - Database: %DB_NAME%
echo - User: %DB_USER%
echo.

echo Step 1: Creating comprehensive database with all tables...
psql -h %DB_HOST% -p %DB_PORT% -U %DB_USER% -f backend\create_comprehensive_database.sql
if %ERRORLEVEL% neq 0 (
    echo Error creating database. Please check the error message above.
    goto :error
)

echo.
echo Step 2: Verifying database tables...
psql -h %DB_HOST% -p %DB_PORT% -U %DB_USER% -d %DB_NAME% -c "\dt"
if %ERRORLEVEL% neq 0 (
    echo Error verifying database tables. Please check the error message above.
    goto :error
)

echo.
echo Step 3: Setting environment variable for the application...
set DATABASE_URL=postgresql://%DB_USER%:%DB_PASSWORD%@%DB_HOST%:%DB_PORT%/%DB_NAME%
echo DATABASE_URL set to %DATABASE_URL%

echo.
echo ========================================================================
echo        Database setup completed successfully!
echo ========================================================================
echo.
echo To start the Flask application, run:
echo   cd backend
echo   set DATABASE_URL=%DATABASE_URL%
echo   python app.py
echo.
echo To start the React frontend, run:
echo   cd frontend
echo   npm start
echo.

goto :end

:error
echo.
echo ========================================================================
echo        Database setup failed! Please fix the errors and try again.
echo ========================================================================
echo.
exit /b 1

:end
