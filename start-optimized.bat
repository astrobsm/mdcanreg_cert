@echo off
echo ===================================
echo MDCAN BDM 2025 Certificate Platform
echo Rebuild and Start Script
echo ===================================

echo.
echo Step 1: Building frontend with optimizations...
call npm run build

echo.
echo Step 2: Starting optimized backend...
cd backend
start python optimized_app.py
cd ..

echo.
echo Build and start complete!
echo.
echo Frontend: http://localhost:3000
echo Backend API: http://localhost:5000
echo.
echo ===================================
