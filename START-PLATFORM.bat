@echo off
title MDCAN BDM 2025 Certificate Platform
color 0A

echo.
echo ================================================================
echo                MDCAN BDM 2025 Certificate Platform
echo                     Complete Startup Script
echo ================================================================
echo.

REM Set error handling
setlocal EnableDelayedExpansion

REM Change to the correct directory
cd /d "%~dp0"

echo [INFO] Starting in directory: %CD%
echo.

REM Function to check if a process is running on a port
:check_port
netstat -an | find "LISTENING" | find ":8080" >nul
if %ERRORLEVEL% equ 0 (
    echo [WARNING] Port 8080 is already in use!
    echo [INFO] Stopping any existing Flask processes...
    taskkill /F /IM python.exe >nul 2>&1
    timeout /t 2 >nul
)

REM Check if this is first time setup
echo [STEP 1/6] Checking environment setup...
if not exist "frontend\node_modules" (
    echo [INFO] First time setup detected - installing dependencies...
    goto :first_time_setup
) else (
    echo [INFO] Environment already configured
)

REM Check if build exists
echo [STEP 2/6] Checking React build...
if not exist "frontend\build" (
    echo [INFO] Building React application...
    cd frontend
    call npm run build
    if !ERRORLEVEL! neq 0 (
        echo [ERROR] Failed to build React application
        pause
        exit /b 1
    )
    cd ..
    echo [SUCCESS] React build completed
) else (
    echo [INFO] React build exists
)

REM Check backend environment
echo [STEP 3/6] Checking backend configuration...
if not exist "backend\.env" (
    echo [ERROR] Backend .env file not found!
    echo [INFO] Creating .env from template...
    cd backend
    copy .env.example .env >nul
    echo [WARNING] Please configure your .env file with actual credentials
    cd ..
    pause
    exit /b 1
) else (
    echo [INFO] Backend configuration found
)

REM Check database connection
echo [STEP 4/6] Checking database connection...
cd backend
python -c "
import psycopg2
import os
from dotenv import load_dotenv
load_dotenv()
try:
    conn = psycopg2.connect(
        host='localhost',
        database='bdmcertificate_db',
        user='postgres',
        password='natiss_natiss'
    )
    conn.close()
    print('[SUCCESS] Database connection verified')
except Exception as e:
    print(f'[ERROR] Database connection failed: {e}')
    print('[INFO] Attempting to create database...')
    exit(1)
" 2>nul
if !ERRORLEVEL! neq 0 (
    echo [INFO] Creating database...
    python init_db.py
    if !ERRORLEVEL! neq 0 (
        echo [ERROR] Failed to create database
        cd ..
        pause
        exit /b 1
    )
)
cd ..

REM Start the application
echo [STEP 5/6] Starting Flask backend server...
cd backend
start "MDCAN Certificate Backend" cmd /k "title MDCAN Backend Server && echo Starting MDCAN Certificate Platform Backend... && echo Server will be available at http://localhost:8080 && echo. && python app.py"

REM Wait for server to start
echo [INFO] Waiting for server to initialize...
timeout /t 5 >nul

REM Check if server started successfully
echo [STEP 6/6] Verifying server startup...
:check_server
ping 127.0.0.1 -n 1 >nul 2>&1
if !ERRORLEVEL! neq 0 (
    timeout /t 1 >nul
    goto :check_server
)

REM Try to connect to the server
powershell -Command "try { $response = Invoke-WebRequest -Uri 'http://localhost:8080/api/health' -TimeoutSec 10; if ($response.StatusCode -eq 200) { exit 0 } else { exit 1 } } catch { exit 1 }" >nul 2>&1
if !ERRORLEVEL! equ 0 (
    echo [SUCCESS] Server is running and responding
) else (
    echo [INFO] Server is starting up (this may take a moment)...
)

cd ..

echo.
echo ================================================================
echo                    🎉 STARTUP COMPLETE! 🎉
echo ================================================================
echo.
echo ✅ MDCAN BDM 2025 Certificate Platform is now running!
echo.
echo 🌐 Access your application at:
echo    http://localhost:8080
echo.
echo 📊 API Health Check:
echo    http://localhost:8080/api/health
echo.
echo 📈 Statistics Dashboard:
echo    http://localhost:8080/api/stats
echo.
echo 🖥️  Backend server is running in a separate window
echo    (Close that window to stop the server)
echo.
echo 📧 Email Configuration:
echo    Make sure your Gmail app password is configured in backend\.env
echo.
echo 🗄️  Database: PostgreSQL (bdmcertificate_db)
echo    Username: postgres
echo.
echo ================================================================
echo.

REM Open the application in default browser
echo [INFO] Opening application in your default browser...
timeout /t 2 >nul
start http://localhost:8080

echo.
echo 💡 USEFUL COMMANDS:
echo    - Press Ctrl+C in the backend window to stop the server
echo    - Run this script again to restart the platform
echo    - Check backend\.env for email configuration
echo.
echo 🎓 Ready to generate and send certificates!
echo.
echo Press any key to close this window...
pause >nul
exit /b 0

:first_time_setup
echo.
echo ================================================================
echo                    FIRST TIME SETUP
echo ================================================================
echo.

echo [1/4] Installing frontend dependencies...
cd frontend
call npm install
if !ERRORLEVEL! neq 0 (
    echo [ERROR] Failed to install frontend dependencies
    cd ..
    pause
    exit /b 1
)

echo [2/4] Building React application...
call npm run build
if !ERRORLEVEL! neq 0 (
    echo [ERROR] Failed to build React application
    cd ..
    pause
    exit /b 1
)

cd ..
echo [3/4] Installing backend dependencies...
cd backend
call pip install -r requirements.txt
if !ERRORLEVEL! neq 0 (
    echo [ERROR] Failed to install backend dependencies
    cd ..
    pause
    exit /b 1
)

echo [4/4] Setting up configuration...
if exist ".env" (
    echo [INFO] .env file already exists
) else (
    echo [INFO] Creating .env file from template...
    copy .env.example .env >nul
    echo.
    echo ⚠️  IMPORTANT: Please edit backend\.env file with your actual:
    echo    - Gmail app password (replace placeholder)
    echo    - Database credentials (if different)
    echo.
)

echo [INFO] Initializing database...
python init_db.py
if !ERRORLEVEL! neq 0 (
    echo [ERROR] Failed to initialize database
    cd ..
    pause
    exit /b 1
)

cd ..
echo.
echo ================================================================
echo                   ✅ SETUP COMPLETE!
echo ================================================================
echo.
echo Now continuing with application startup...
echo.
goto :check_port
