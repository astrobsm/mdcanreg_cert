# MDCAN BDM 2025 Certificate Platform Dockerfile
# Multi-stage build for optimized production deployment

# Stage 1: Build the React frontend
FROM node:16 AS frontend-build
WORKDIR /app/frontend
COPY frontend/package*.json ./
RUN npm install
COPY frontend/ ./
RUN npm run build

# Stage 2: Set up the Python environment
FROM python:3.9-slim
WORKDIR /app

# Install system dependencies including wkhtmltopdf for PDF generation
RUN apt-get update && apt-get install -y --no-install-recommends \
    wkhtmltopdf \
    libpq-dev \
    gcc \
    g++ \
    python3-dev \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Copy backend requirements and install dependencies
COPY backend/requirements.txt .

# Completely reinstall numpy and pandas with compatible versions
# First uninstall any existing versions
RUN pip uninstall -y numpy pandas
# Install specific versions with binary compatibility
RUN pip install --no-cache-dir numpy==1.21.6
RUN pip install --no-cache-dir pandas==1.3.5
# Install schedule package explicitly
RUN pip install --no-cache-dir schedule==1.2.0
# Install other requirements but skip numpy and pandas
RUN grep -v "numpy\|pandas" requirements.txt > filtered_requirements.txt
RUN pip install --no-cache-dir -r filtered_requirements.txt

# Copy backend code - ensure it goes into a proper backend directory
COPY backend/ ./backend/

# Create an empty __init__.py to make the backend directory a proper package
RUN touch backend/__init__.py

# Copy the entry point and fallback app
COPY app.py .
COPY fallback_app.py .
COPY do_app.py .
COPY docker_startup.sh .

# Make the startup script executable
RUN chmod +x docker_startup.sh

# Make sure minimal_app.py exists in backend directory
RUN test -f backend/minimal_app.py || echo "Minimal app not found in backend directory"

# Copy built frontend from previous stage
COPY --from=frontend-build /app/frontend/build ./frontend/build

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV PORT=8080
ENV FLASK_ENV=production
ENV FLASK_APP=do_app.py

# Expose the port (this is just for documentation - it doesn't actually publish the port)
EXPOSE 8080

# Use our startup script that properly handles the PORT environment variable
CMD ["./docker_startup.sh"]
