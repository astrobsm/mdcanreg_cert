@echo off
echo ===============================
echo Installing wkhtmltopdf for PDF certificate generation
echo ===============================

:: Check if wkhtmltopdf is already installed
where wkhtmltopdf >nul 2>nul
if %ERRORLEVEL% == 0 (
    echo wkhtmltopdf is already installed
    wkhtmltopdf --version
    goto :end
)

echo wkhtmltopdf not found. Installing...

:: Create downloads directory if it doesn't exist
if not exist "%~dp0downloads" mkdir "%~dp0downloads"

:: Set the version and URL
set WKHTMLTOPDF_VERSION=0.12.6
set WKHTMLTOPDF_URL=https://github.com/wkhtmltopdf/packaging/releases/download/0.12.6-1/wkhtmltox-0.12.6-1.msvc2015-win64.exe

:: Download the installer
echo Downloading wkhtmltopdf...
powershell -Command "& {Invoke-WebRequest -Uri '%WKHTMLTOPDF_URL%' -OutFile '%~dp0downloads\wkhtmltopdf-installer.exe'}"

:: Run the installer
echo Installing wkhtmltopdf...
start /wait %~dp0downloads\wkhtmltopdf-installer.exe /S

:: Verify installation
echo Verifying installation...
where wkhtmltopdf >nul 2>nul
if %ERRORLEVEL% == 0 (
    echo wkhtmltopdf installation successful!
    wkhtmltopdf --version
) else (
    echo wkhtmltopdf installation failed.
    echo Please install manually from: https://wkhtmltopdf.org/downloads.html
    echo After installation, restart your computer or restart the backend server.
)

:end
echo ===============================
echo Updating PATH variable to include wkhtmltopdf...
echo ===============================

:: Common installation paths
set "PATHS_TO_CHECK=C:\Program Files\wkhtmltopdf\bin;C:\Program Files (x86)\wkhtmltopdf\bin"

:: Check each path and add to PATH if it exists and is not already in PATH
for %%p in (%PATHS_TO_CHECK%) do (
    if exist "%%p" (
        echo Found wkhtmltopdf in: %%p
        echo Adding to current PATH
        set "PATH=%%p;%PATH%"
    )
)

echo ===============================
echo Setup completed.
echo ===============================

echo Press any key to exit...
pause > nul
