@echo off
title MDCAN BDM 2025 Certificate Platform [OPTIMIZED]
color 0A

echo.
echo ================================================================
echo                MDCAN BDM 2025 Certificate Platform
echo                 Optimized Platform Startup Script
echo ================================================================
echo.

REM Change to the correct directory
cd /d "%~dp0"

echo [INFO] Starting in directory: %CD%
echo.

REM Check for existing processes
echo [STEP 1/5] Checking for existing processes...
taskkill /F /IM python.exe >nul 2>&1
echo [INFO] Cleared any existing Python processes

REM Build in development mode to avoid minification errors
echo [STEP 2/5] Building frontend in development mode...
set "REACT_APP_DISABLE_MINIFICATION=true"
set "GENERATE_SOURCEMAP=true"
set "BABEL_ENV=production"
set "NODE_ENV=development"
call npm run build
echo [SUCCESS] Frontend built in development mode to avoid minification errors

REM Copy build to frontend/build directory
echo [STEP 3/5] Copying build to frontend/build...
xcopy /E /Y build\* frontend\build\
echo [SUCCESS] Build copied successfully

REM Start optimized backend
echo [STEP 4/5] Starting optimized backend...
start cmd /k "cd backend && python optimized_app.py"
echo [SUCCESS] Backend started with optimizations (Flask 2.x compatible)

REM Start frontend server
echo [STEP 5/5] Starting frontend server...
start cmd /k "npm start"
echo [SUCCESS] Frontend server started

echo.
echo ================================================================
echo                 MDCAN BDM 2025 Platform is READY
echo.
echo      Frontend: http://localhost:3000
echo      Backend API: http://localhost:5000
echo.
echo      All optimizations have been applied.
echo      The application is now running in debug mode to avoid minification errors.
echo ================================================================
echo.
pause
