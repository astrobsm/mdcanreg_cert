@echo off
echo Opening certificate text test page...
start http://localhost:8080/certificate-text-test

echo.
echo You can test certificate generation by clicking the buttons on the test page
echo or by visiting these URLs directly:
echo.
echo PDF Certificates (requires wkhtmltopdf):
echo http://localhost:8080/api/generate-test-certificate/participation
echo http://localhost:8080/api/generate-test-certificate/service
echo.
echo HTML Certificates (fallback option):
echo http://localhost:8080/api/generate-test-certificate-html/participation
echo http://localhost:8080/api/generate-test-certificate-html/service
echo.
echo Please check if the certificate text has been updated correctly.
echo.
echo If PDF generation fails, run setup-wkhtmltopdf.bat to install the required PDF tool.
pause
