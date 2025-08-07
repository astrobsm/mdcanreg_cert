@echo off
echo ===== Setting up Signature Files =====

REM Create directories if they don't exist
if not exist "backend\static" mkdir "backend\static"
if not exist "public" mkdir "public"

echo Copying signature files from frontend/public to public and backend/static...

REM Copy all signature files from frontend/public to public and backend/static
copy /Y "frontend\public\president-signature-placeholder.jpg" "public\president-signature.png"
copy /Y "frontend\public\chairman-signature-placeholder.png" "public\chairman-signature.png"
copy /Y "frontend\public\logo-mdcan.jpeg" "public\mdcan-logo.png"
copy /Y "frontend\public\coal_city_logo.png" "public\coalcity-logo.png"

copy /Y "frontend\public\president-signature-placeholder.jpg" "backend\static\president-signature.png"
copy /Y "frontend\public\chairman-signature-placeholder.png" "backend\static\chairman-signature.png"
copy /Y "frontend\public\logo-mdcan.jpeg" "backend\static\mdcan-logo.png"
copy /Y "frontend\public\coal_city_logo.png" "backend\static\coalcity-logo.png"

echo Setting correct permissions...

REM Ensure permissions are set correctly
attrib -R "public\president-signature.png"
attrib -R "public\chairman-signature.png"
attrib -R "public\mdcan-logo.png"
attrib -R "public\coalcity-logo.png"

attrib -R "backend\static\president-signature.png"
attrib -R "backend\static\chairman-signature.png"
attrib -R "backend\static\mdcan-logo.png"
attrib -R "backend\static\coalcity-logo.png"

echo ===== Signature Files Setup Complete =====
echo Restart the backend server to ensure files are correctly served.
pause
