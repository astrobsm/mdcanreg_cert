@echo off
title MDCAN BDM 2025 Certificate Platform - Clean Reset
color 0C

echo.
echo ================================================================
echo                MDCAN BDM 2025 Certificate Platform
echo                     Clean Reset Script
echo ================================================================
echo.

REM Kill all relevant processes
echo [STEP 1/3] Stopping all running processes...
taskkill /F /IM node.exe >nul 2>&1
taskkill /F /IM python.exe >nul 2>&1
taskkill /F /IM npm.exe >nul 2>&1
taskkill /F /IM cmd.exe /FI "WINDOWTITLE eq *Certificate*" >nul 2>&1
echo [SUCCESS] All processes terminated

REM Clean up build directories
echo [STEP 2/3] Cleaning up build directories...
if exist "build" (
    echo [INFO] Removing build directory...
    rmdir /S /Q build
)
if exist "frontend\build" (
    echo [INFO] Removing frontend\build directory...
    rmdir /S /Q frontend\build
)
echo [SUCCESS] Build directories cleaned

REM Set development environment variables
echo [STEP 3/3] Setting up development environment...
set "REACT_APP_DISABLE_MINIFICATION=true"
set "GENERATE_SOURCEMAP=true"
set "BABEL_ENV=development"
set "NODE_ENV=development"
echo [SUCCESS] Environment variables set for development

echo.
echo ================================================================
echo           MDCAN BDM 2025 Platform Clean Reset Complete
echo.
echo    Your environment has been reset. You can now start the
echo    platform in development mode using:
echo.
echo    start-dev-mode.bat
echo.
echo ================================================================
echo.
pause
