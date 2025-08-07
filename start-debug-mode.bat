@echo off
title MDCAN BDM 2025 Certificate Platform - Development Mode
color 0A

echo.
echo ================================================================
echo                MDCAN BDM 2025 Certificate Platform
echo                   Development Mode Startup
echo ================================================================
echo.

REM Change to the correct directory
cd /d "%~dp0"

echo [INFO] Starting in directory: %CD%
echo.

REM First clean up any running processes
echo [STEP 1/5] Cleaning up environment...
call clean-reset.bat
echo [SUCCESS] Environment reset

REM Start backend server
echo [STEP 2/5] Starting backend server...
start cmd /k "cd backend && python optimized_app.py"
echo [SUCCESS] Backend server started at http://localhost:5000
timeout /t 3 >nul

REM Start frontend server
echo [STEP 3/5] Starting frontend in development mode...
echo [INFO] This will run without minification to prevent runtime errors
start cmd /k "npm start"
echo [SUCCESS] Frontend development server started

echo.
echo ================================================================
echo                 MDCAN BDM 2025 Platform is READY
echo.
echo      Frontend: http://localhost:3000
echo      Backend API: http://localhost:5000
echo.
echo      Running in DEVELOPMENT MODE with optimized backend
echo      This mode avoids minification errors but is slower
echo ================================================================
echo.
pause
