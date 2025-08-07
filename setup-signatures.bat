@echo off
echo ======================================================
echo MDCAN BDM 2025 Certificate - Signature Setup
echo ======================================================
echo.
echo This script will set up signature files for certificate generation.
echo.

REM Create directories if they don't exist
if not exist "public" mkdir public
if not exist "backend\static" mkdir backend\static

REM Copy signature files from frontend/public to public
echo Copying signature files to public directory...
copy /Y "frontend\public\president-signature-placeholder.jpg" "public\president-signature.png"
copy /Y "frontend\public\chairman-signature-placeholder.png" "public\chairman-signature.png"
copy /Y "frontend\public\logo-mdcan.jpeg" "public\mdcan-logo.png"
copy /Y "frontend\public\coal_city_logo.png" "public\coalcity-logo.png"

REM Copy signature files to backend/static
echo Copying signature files to backend/static directory...
copy /Y "frontend\public\president-signature-placeholder.jpg" "backend\static\president-signature.png"
copy /Y "frontend\public\chairman-signature-placeholder.png" "backend\static\chairman-signature.png"
copy /Y "frontend\public\logo-mdcan.jpeg" "backend\static\mdcan-logo.png"
copy /Y "frontend\public\coal_city_logo.png" "backend\static\coalcity-logo.png"

echo.
echo Signature files setup complete!
echo.
echo ======================================================
