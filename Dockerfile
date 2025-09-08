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
RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq5 \
    curl \
    wget \
    xvfb \
    libfontconfig1 \
    libxrender1 \
    libxtst6 \
    libxi6 \
    fontconfig \
    libjpeg62-turbo \
    libssl1.1 \
    xfonts-75dpi \
    xfonts-base \
    libpng16-16 \
    libjpeg-turbo8 \
    && wget -q https://github.com/wkhtmltopdf/packaging/releases/download/0.12.6.1-2/wkhtmltox_0.12.6.1-2.bullseye_amd64.deb \
    && dpkg -i wkhtmltox_0.12.6.1-2.bullseye_amd64.deb || apt-get install -f -y \
    && rm wkhtmltox_0.12.6.1-2.bullseye_amd64.deb \
    && rm -rf /var/lib/apt/lists/*

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
