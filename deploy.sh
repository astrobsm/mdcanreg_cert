#!/bin/bash

# Docker Compose Deployment Script for MDCAN BDM 2025 Certificate Platform

set -e

# Display banner
echo "=================================="
echo "MDCAN BDM 2025 Certificate Platform"
echo "Docker Compose Deployment Script"
echo "=================================="

# Check if Docker and Docker Compose are installed
if ! command -v docker &> /dev/null; then
    echo "Docker is not installed. Please install Docker first."
    exit 1
fi

if ! command -v docker-compose &> /dev/null; then
    echo "Docker Compose is not installed. Please install Docker Compose first."
    exit 1
fi

# Function to deploy in development mode
deploy_dev() {
    echo "Deploying in DEVELOPMENT mode..."
    docker-compose up -d
    echo "Development deployment completed. Access the application at:"
    echo "- Frontend: http://localhost:3000"
    echo "- Backend API: http://localhost:5000"
}

# Function to deploy in production mode
deploy_prod() {
    echo "Deploying in PRODUCTION mode..."
    
    # Check if .env file exists, otherwise create it
    if [ ! -f .env ]; then
        echo "Creating .env file with default values..."
        cat > .env << EOF
DB_USER=postgres
DB_PASSWORD=natiss_natiss
DB_NAME=mdcan042_db
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USER=sylvia4douglas@gmail.com
EMAIL_PASSWORD=your-app-password
EMAIL_FROM=MDCAN BDM 2025 <sylvia4douglas@gmail.com>
PORT=5000
EOF
        echo ".env file created. Please update with your actual values."
    fi
    
    docker-compose -f docker-compose.prod.yml up -d
    echo "Production deployment completed. Access the application at:"
    echo "- Application: http://localhost:5000"
}

# Function to stop all containers
stop_all() {
    echo "Stopping all containers..."
    docker-compose down
    docker-compose -f docker-compose.prod.yml down
    echo "All containers stopped."
}

# Function to view logs
view_logs() {
    if [ "$1" == "dev" ]; then
        echo "Viewing development logs..."
        docker-compose logs -f
    else
        echo "Viewing production logs..."
        docker-compose -f docker-compose.prod.yml logs -f
    fi
}

# Main script execution
case "$1" in
    dev)
        deploy_dev
        ;;
    prod)
        deploy_prod
        ;;
    stop)
        stop_all
        ;;
    logs-dev)
        view_logs dev
        ;;
    logs-prod)
        view_logs prod
        ;;
    *)
        echo "Usage: $0 {dev|prod|stop|logs-dev|logs-prod}"
        echo ""
        echo "Options:"
        echo "  dev        Deploy in development mode (separate frontend and backend)"
        echo "  prod       Deploy in production mode (combined frontend and backend)"
        echo "  stop       Stop all containers"
        echo "  logs-dev   View development logs"
        echo "  logs-prod  View production logs"
        exit 1
esac

exit 0
