@echo off
echo =========echo Starting Flask backend server...
cd backend
start "MDCAN Backend Server" cmd /k "python app.py"
echo Backend server starting at http://localhost:8080===========================
echo MDCAN BDM 2025 Certificate Platform
echo Development Mode with Hot Reload
echo ========================================
echo.

REM Check if setup is complete
if not exist "frontend\node_modules" (
    echo ERROR: Frontend dependencies not installed!
    echo Please run start-development.bat first
    pause
    exit /b 1
)

if not exist "backend\.env" (
    echo ERROR: Backend not configured!
    echo Please run start-development.bat first
    pause
    exit /b 1
)

echo Starting servers in development mode...
echo.

echo [1/2] Starting Flask backend server...
cd backend
start "MDCAN Backend Server" cmd /k "python app.py"
echo Backend server starting at http://localhost:5000

echo [2/2] Starting React development server...
cd ..\frontend
start "MDCAN Frontend Dev Server" cmd /k "npm start"
echo Frontend dev server starting at http://localhost:3000

cd ..
echo.
echo ========================================
echo DEVELOPMENT SERVERS STARTED!
echo ========================================
echo.
echo Backend (API): http://localhost:8080
echo Frontend (Dev): http://localhost:3000
echo.
echo Both servers are running in separate windows.
echo Close those windows to stop the servers.
echo.
echo For production mode, use start-quick.bat instead.
echo.

pause
