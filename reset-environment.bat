@echo off
echo ========================================
echo MDCAN BDM 2025 Certificate Platform
echo Environment Reset
echo ========================================
echo.

echo This will clean up the development environment.
echo.
set /p confirm="Are you sure you want to reset? (y/N): "
if /i not "%confirm%"=="y" (
    echo Reset cancelled.
    pause
    exit /b 0
)

echo.
echo Cleaning up environment...

REM Clean frontend
if exist "frontend\node_modules" (
    echo Removing frontend dependencies...
    rmdir /s /q "frontend\node_modules"
)

if exist "frontend\build" (
    echo Removing frontend build...
    rmdir /s /q "frontend\build"
)

REM Clean backend cache
if exist "backend\__pycache__" (
    echo Removing Python cache...
    rmdir /s /q "backend\__pycache__"
)

REM Remove .env file (but keep the example)
if exist "backend\.env" (
    echo Removing .env file...
    del "backend\.env"
)

echo.
echo ========================================
echo RESET COMPLETE!
echo ========================================
echo.
echo Run start-development.bat to set up the environment again.
echo.

pause
