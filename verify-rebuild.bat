@echo off
echo ===================================
echo MDCAN BDM 2025 Certificate Platform
echo Verification Script
echo ===================================

echo.
echo Step 1: Checking frontend build...
if exist "build\index.html" (
    echo [OK] Frontend build exists
) else (
    echo [ERROR] Frontend build not found
)

echo.
echo Step 2: Checking backend files...
if exist "backend\optimized_app.py" (
    echo [OK] Optimized backend file exists
) else (
    echo [ERROR] Optimized backend file not found
)

echo.
echo Step 3: Checking database configuration...
if exist "backend\database.py" (
    echo [OK] Database configuration exists
) else (
    echo [ERROR] Database configuration not found
)

echo.
echo Step 4: Checking for running services...
netstat -ano | findstr :5000
if %ERRORLEVEL% EQU 0 (
    echo [OK] Backend service is running on port 5000
) else (
    echo [WARNING] Backend service not detected on port 5000
)

echo.
echo Step 5: Checking for environment files...
if exist ".env.production.local" (
    echo [OK] Production environment file exists
) else (
    echo [WARNING] Production environment file not found
)

echo.
echo Verification complete!
echo If all checks passed, the application has been successfully rebuilt.
echo.
echo ===================================
pause
