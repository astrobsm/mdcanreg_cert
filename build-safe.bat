@echo off
echo ===================================
echo MDCAN BDM 2025 Certificate Platform
echo Safe Build Script
echo ===================================

echo.
echo Step 1: Setting environment variables for safe build...
set "INLINE_RUNTIME_CHUNK=false"
set "GENERATE_SOURCEMAP=false"
set "REACT_APP_DISABLE_MINIFICATION=true"

echo.
echo Step 2: Building React application with safety options...
call npm run build

echo.
echo Step 3: Copying build to backend static folder...
xcopy /E /Y build\* frontend\build\

echo.
echo Safe build complete!
echo.
echo ===================================
pause
