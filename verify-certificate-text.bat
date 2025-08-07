@echo off
echo ===================================
echo MDCAN BDM Certificate Text Verifier
echo ===================================
echo.
echo This tool will help you verify the certificate text changes.
echo.

REM Check if the backend server is running
powershell -Command "& {try { $response = Invoke-WebRequest -Uri 'http://localhost:8080/api/health' -UseBasicParsing; if ($response.StatusCode -eq 200) { Write-Host 'Backend server is running.' -ForegroundColor Green } else { Write-Host 'Backend server appears to be running but returned status code:' $response.StatusCode -ForegroundColor Yellow } } catch { Write-Host 'Backend server is not running. Please start it first.' -ForegroundColor Red; exit 1 }}"

echo.
echo 1. Opening certificate preview page in your browser...
start http://localhost:8080/certificate-text-test
echo.

echo 2. Generating a simple HTML certificate preview (no wkhtmltopdf needed)...
echo.
echo   Certificate text has been updated to:
echo.
echo   "14th Biennial Delegates' Meeting and SCIENTIFIC Conference"
echo   "OF MEDICAL AND DENTAL CONSULTANTS'ASSOCIATION OF NIGERIA"
echo   "HELD AT INTERNATIONAL CONFERENCE CENTRE ENUGU FROM 1st-6th September, 2025"
echo.
echo   HTML Certificate URLs:
echo   - http://localhost:8080/certificate-text-test
echo.

echo 3. If you want to generate PDF certificates, you need wkhtmltopdf installed.
echo    Run setup-wkhtmltopdf.bat to install it.
echo.

pause
