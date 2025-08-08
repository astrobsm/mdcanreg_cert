@echo off
echo ==============================================================
echo MDCAN BDM 2025 Certificate Platform - Verification Script
echo ==============================================================
echo.
echo This script will verify that the application is ready for deployment
echo by testing all critical endpoints in both the main and minimal apps.
echo.
echo Press any key to continue...
pause > nul

REM Make sure virtual environment is activated if it exists
if exist venv\Scripts\activate.bat (
    call venv\Scripts\activate.bat
)

REM Check if requests module is installed
python -c "import requests" 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo Installing requests module...
    pip install requests
)

echo.
echo Running verification against the main app...
echo.
start /B cmd /c "cd backend && python app.py"
timeout /t 5 /nobreak > nul
python verify_app_readiness.py http://localhost:5000
set MAIN_APP_RESULT=%ERRORLEVEL%
taskkill /F /IM python.exe /T > nul 2>&1

echo.
echo Running verification against the minimal app...
echo.
start /B cmd /c "cd backend && python minimal_app.py"
timeout /t 5 /nobreak > nul
python verify_app_readiness.py http://localhost:5000
set MINIMAL_APP_RESULT=%ERRORLEVEL%
taskkill /F /IM python.exe /T > nul 2>&1

echo.
echo ==============================================================
echo Verification Results
echo ==============================================================

if %MAIN_APP_RESULT% EQU 0 (
    echo Main app: PASSED ✅
) else (
    echo Main app: FAILED ❌ - Some endpoints did not pass verification
)

if %MINIMAL_APP_RESULT% EQU 0 (
    echo Minimal app: PASSED ✅
) else (
    echo Minimal app: FAILED ❌ - Some endpoints did not pass verification
)

echo.
if %MAIN_APP_RESULT% EQU 0 (
    echo The main app is ready for deployment!
) else if %MINIMAL_APP_RESULT% EQU 0 (
    echo The minimal app is ready for deployment! The main app still needs fixes.
) else (
    echo Neither app is fully ready for deployment. Please check the logs for details.
)

echo.
echo Press any key to exit...
pause > nul
