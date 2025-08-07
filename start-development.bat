@echo off
echo ========================================
echo MDCAN BDM 2025 Certificate Platform
echo Development Environment Startup
echo ========================================
echo.

REM Check if this is the first run by looking for node_modules
if not exist "frontend\node_modules" (
    echo First time setup detected...
    call :setup
) else (
    echo Environment already set up. Starting servers...
)

echo.
echo Starting development servers...
call :start_servers

pause
exit /b

:setup
echo.
echo ========================================
echo FIRST TIME SETUP
echo ========================================
echo.

echo [1/4] Installing frontend dependencies...
cd frontend
call npm install
if %ERRORLEVEL% neq 0 (
    echo ERROR: Failed to install frontend dependencies
    pause
    exit /b 1
)

echo [2/4] Building React application...
call npm run build
if %ERRORLEVEL% neq 0 (
    echo ERROR: Failed to build React application
    pause
    exit /b 1
)

cd ..
echo [3/4] Installing backend dependencies...
cd backend
call pip install -r requirements.txt
if %ERRORLEVEL% neq 0 (
    echo ERROR: Failed to install backend dependencies
    pause
    exit /b 1
)

echo [4/4] Setting up database...
if exist ".env" (
    echo .env file exists, skipping database setup...
    echo Please ensure your database is configured correctly.
) else (
    echo Creating .env file from template...
    copy .env.example .env
    echo.
    echo IMPORTANT: Please edit backend\.env file with your actual:
    echo - Gmail app password
    echo - Database credentials if different
    echo.
    echo Setting up database...
    call python init_db.py
)

cd ..
echo.
echo ========================================
echo SETUP COMPLETE!
echo ========================================
echo.
goto :eof

:start_servers
echo.
echo Starting Flask backend server...
cd backend
start "MDCAN Backend Server" cmd /k "python app.py"
echo Backend server starting at http://localhost:5000
echo.
echo ========================================
echo APPLICATION READY!
echo ========================================
echo.
echo Your certificate platform is running at:
echo http://localhost:8080
echo.
echo Backend server is running in a separate window.
echo Close that window to stop the server.
echo.
cd ..
goto :eof
