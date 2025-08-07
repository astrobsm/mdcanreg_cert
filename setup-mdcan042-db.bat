@echo off
REM MDCAN Certificate Platform Database Setup Script

echo Setting up MDCAN Certificate Platform Database...

REM Create environment variable for the new database
set DATABASE_URL=postgresql://postgres:natiss_natiss@localhost/mdcan042_db

echo DATABASE_URL set to %DATABASE_URL%

echo Starting Flask application with the new database...
echo.
echo Please start your Flask application with the following commands:
echo cd backend
echo set DATABASE_URL=postgresql://postgres:natiss_natiss@localhost/mdcan042_db
echo python app.py
echo.
echo Setup complete!
