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
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Copy backend requirements and install dependencies
COPY backend/requirements.txt .

# Install numpy and pandas first to ensure compatibility
RUN pip install --no-cache-dir numpy==1.24.3
RUN pip install --no-cache-dir pandas==1.5.3
RUN pip install --no-cache-dir -r requirements.txt

# Copy backend code - ensure it goes into a proper backend directory
COPY backend/ ./backend/

# Create an empty __init__.py to make the backend directory a proper package
RUN touch backend/__init__.py

# Copy the entry point and fallback app
COPY app.py .
COPY fallback_app.py .

# Copy built frontend from previous stage
COPY --from=frontend-build /app/frontend/build ./frontend/build

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV PORT=8080
ENV FLASK_ENV=production
ENV FLASK_APP=app.py

# Expose the port
EXPOSE 8080

# Run gunicorn with optimized settings and detailed error logging
CMD ["gunicorn", "--bind", "0.0.0.0:8080", "--workers", "2", "--timeout", "120", "--log-level", "debug", "--capture-output", "--enable-stdio-inheritance", "app:app"]
