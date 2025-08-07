@echo off
SETLOCAL EnableDelayedExpansion

REM Docker Compose Deployment Script for MDCAN BDM 2025 Certificate Platform

echo ==================================
echo MDCAN BDM 2025 Certificate Platform
echo Docker Compose Deployment Script
echo ==================================

REM Check if Docker and Docker Compose are installed
WHERE docker >nul 2>nul
IF %ERRORLEVEL% NEQ 0 (
    echo Docker is not installed. Please install Docker first.
    exit /b 1
)

WHERE docker-compose >nul 2>nul
IF %ERRORLEVEL% NEQ 0 (
    echo Docker Compose is not installed. Please install Docker Compose first.
    exit /b 1
)

REM Parse command line arguments
IF "%1"=="" (
    GOTO :usage
) ELSE IF "%1"=="dev" (
    GOTO :deploy_dev
) ELSE IF "%1"=="prod" (
    GOTO :deploy_prod
) ELSE IF "%1"=="stop" (
    GOTO :stop_all
) ELSE IF "%1"=="logs-dev" (
    GOTO :logs_dev
) ELSE IF "%1"=="logs-prod" (
    GOTO :logs_prod
) ELSE (
    GOTO :usage
)

:deploy_dev
echo Deploying in DEVELOPMENT mode...
docker-compose up -d
echo Development deployment completed. Access the application at:
echo - Frontend: http://localhost:3000
echo - Backend API: http://localhost:5000
GOTO :eof

:deploy_prod
echo Deploying in PRODUCTION mode...

REM Check if .env file exists, otherwise create it
IF NOT EXIST .env (
    echo Creating .env file with default values...
    (
        echo DB_USER=postgres
        echo DB_PASSWORD=natiss_natiss
        echo DB_NAME=mdcan042_db
        echo EMAIL_HOST=smtp.gmail.com
        echo EMAIL_PORT=587
        echo EMAIL_USER=sylvia4douglas@gmail.com
        echo EMAIL_PASSWORD=your-app-password
        echo EMAIL_FROM=MDCAN BDM 2025 ^<sylvia4douglas@gmail.com^>
        echo PORT=5000
    ) > .env
    echo .env file created. Please update with your actual values.
)

docker-compose -f docker-compose.prod.yml up -d
echo Production deployment completed. Access the application at:
echo - Application: http://localhost:5000
GOTO :eof

:stop_all
echo Stopping all containers...
docker-compose down
docker-compose -f docker-compose.prod.yml down
echo All containers stopped.
GOTO :eof

:logs_dev
echo Viewing development logs...
docker-compose logs -f
GOTO :eof

:logs_prod
echo Viewing production logs...
docker-compose -f docker-compose.prod.yml logs -f
GOTO :eof

:usage
echo Usage: %0 {dev^|prod^|stop^|logs-dev^|logs-prod}
echo.
echo Options:
echo   dev        Deploy in development mode (separate frontend and backend)
echo   prod       Deploy in production mode (combined frontend and backend)
echo   stop       Stop all containers
echo   logs-dev   View development logs
echo   logs-prod  View production logs
exit /b 1

:eof
ENDLOCAL
