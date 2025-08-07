@echo off
echo ===================================
echo MDCAN BDM 2025 Certificate Platform
echo Complete Rebuild Script
echo ===================================

echo.
echo Step 1: Building frontend application...
call npm run build

echo.
echo Step 2: Copying build to backend static folder...
xcopy /E /Y build\* frontend\build\

echo.
echo Step 3: Ensuring backend dependencies are installed...
cd backend
pip install -r requirements.txt
cd ..

echo.
echo Step 4: Starting optimized backend application...
start python backend\optimized_app.py

echo.
echo Rebuild complete!
echo The application has been rebuilt and the optimized backend is running.
echo.
echo ===================================
pause
