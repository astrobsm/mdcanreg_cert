FROM node:18-slim AS frontend-builder

# Build the React frontend
WORKDIR /app/frontend
COPY frontend/package*.json ./
RUN npm ci --only=production
COPY frontend/ ./
RUN npm run build

# Python backend stage
FROM python:3.10-slim

WORKDIR /app

# Install system dependencies including wkhtmltopdf for PDF generation
# Using official wkhtmltopdf with comprehensive dependency resolution
RUN apt-get update && apt-get install -y --no-install-recommends \
    # Basic system dependencies
    libpq5 \
    curl \
    wget \
    ca-certificates \
    gnupg \
    lsb-release \
    # X11 and graphics dependencies for wkhtmltopdf
    xvfb \
    libfontconfig1 \
    libxrender1 \
    libxtst6 \
    libxi6 \
    libx11-6 \
    libxext6 \
    # Font packages
    fontconfig \
    fonts-dejavu-core \
    xfonts-75dpi \
    xfonts-base \
    fonts-liberation \
    # Image and compression libraries
    libjpeg62-turbo \
    libpng16-16 \
    # SSL/TLS libraries (use available version)
    libssl3 \
    # Additional dependencies that wkhtmltopdf might need
    libqt5core5a \
    libqt5gui5 \
    libqt5widgets5 \
    libqt5network5 \
    libqt5printsupport5 \
    && rm -rf /var/lib/apt/lists/* \
    # Download and install wkhtmltopdf from official releases
    && wget -q https://github.com/wkhtmltopdf/packaging/releases/download/0.12.6.1-2/wkhtmltox_0.12.6.1-2.bullseye_amd64.deb \
    && apt-get update \
    && apt-get install -f -y ./wkhtmltox_0.12.6.1-2.bullseye_amd64.deb \
    && rm wkhtmltox_0.12.6.1-2.bullseye_amd64.deb \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean

# Verify wkhtmltopdf installation
RUN which wkhtmltopdf && wkhtmltopdf --version

# Copy and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy application files
COPY . .

# Copy the built frontend from the builder stage
COPY --from=frontend-builder /app/frontend/build ./frontend/build

# Set environment variables
ENV PYTHONPATH="/app:/app/backend"
ENV PYTHONUNBUFFERED=1
ENV FLASK_ENV=production
ENV ENABLE_PDF_GENERATION=true

# Verify frontend build exists
RUN ls -la frontend/build/ && \
    echo "Frontend build directory contents:" && \
    find frontend/build -type f -name "*.html" -o -name "*.js" -o -name "*.css" | head -10

EXPOSE 8080

# Health check with dynamic port
HEALTHCHECK --interval=30s --timeout=15s --start-period=120s --retries=3 \
    CMD curl -f http://localhost:${PORT:-8080}/health || exit 1

# Start command using gunicorn configuration file
CMD ["gunicorn", "--config", "gunicorn.conf.py", "wsgi:application"]
