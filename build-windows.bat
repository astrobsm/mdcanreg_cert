@echo off
echo ===================================
echo MDCAN BDM 2025 Certificate Platform
echo Windows-Compatible Safe Build
echo ===================================

echo.
echo Step 1: Setting environment variables for Windows...
set "REACT_APP_DISABLE_MINIFICATION=true"
set "GENERATE_SOURCEMAP=true"
set "BABEL_ENV=production"
set "NODE_ENV=development"

echo.
echo Step 2: Building React application with development settings...
call npm run build

echo.
echo Step 3: Copying build to backend static folder...
xcopy /E /Y build\* frontend\build\

echo.
echo Build complete with development settings!
echo The application is now built with debugging enabled.
echo.
echo ===================================
pause
