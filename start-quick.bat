@echo off
SETLOCAL EnableDelayedExpansion

echo ====================================================
echo MDCAN BDM 2025 Certificate Platform - Quick Start
echo ====================================================
echo.

REM Check if Docker is available and preferred
WHERE docker >nul 2>nul
SET DOCKER_AVAILABLE=%ERRORLEVEL%

IF %DOCKER_AVAILABLE% EQU 0 (
    echo Docker is available on this system.
    
    :docker_choice
    SET /P USE_DOCKER="Would you like to use Docker for development? (y/n): "
    
    IF /I "!USE_DOCKER!"=="y" (
        GOTO start_docker
    ) ELSE IF /I "!USE_DOCKER!"=="n" (
        GOTO start_traditional
    ) ELSE (
        echo Invalid choice. Please enter 'y' or 'n'.
        GOTO docker_choice
    )
) ELSE (
    echo Docker is not available. Using traditional setup.
    GOTO start_traditional
IF EXIST deploy.bat (
    call deploy.bat dev
) ELSE (
    echo deploy.bat script not found.
    echo Falling back to direct docker-compose command...
    docker-compose up -d
)

echo.
echo Docker containers started! Access the application at:
echo - Frontend: http://localhost:3000
echo - Backend API: http://localhost:5000
echo.
echo To view logs, run: deploy.bat logs-dev
echo To stop containers, run: deploy.bat stop
GOTO end

:start_traditional
echo.
echo Starting frontend and backend servers traditionally...
echo.

REM Start backend server
echo Starting backend server...
START "MDCAN Backend" cmd /c "cd backend && python app.py"

REM Wait a bit for backend to initialize
timeout /t 5 /nobreak > nul

REM Start frontend server
echo Starting frontend server...
START "MDCAN Frontend" cmd /c "cd frontend && npm start"

echo.
echo Servers started! Access the application at:
echo - Frontend: http://localhost:3000
echo - Backend API: http://localhost:5000
echo.
echo NOTE: To stop the servers, close the command prompt windows or press Ctrl+C in each window.

:end
echo.
echo ====================================================
echo API Testing Tool Available: open api-test-tool.html in your browser
echo ====================================================
echo.

ENDLOCAL
echo Press Ctrl+C to stop the server
echo.

python app.py
