FROM python:3.11-slim

WORKDIR /app

# Install minimal system dependencies for DigitalOcean deployment
RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq5 \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better Docker layer caching
COPY requirements.txt .

# Install Python dependencies (optimized for DigitalOcean)
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy application files
COPY . .

# Set essential environment variables for DigitalOcean
ENV PYTHONPATH="/app:/app/backend"
ENV PYTHONUNBUFFERED=1
ENV FLASK_ENV=production
ENV PORT=8080

# Create basic frontend directory structure (if needed)
RUN mkdir -p frontend/build/static && \
    echo '<!DOCTYPE html><html><head><title>MDCAN BDM 2025</title></head><body><h1>Loading...</h1></body></html>' > frontend/build/index.html

EXPOSE 8080

# Simple health check (no startup script dependency)
HEALTHCHECK --interval=30s --timeout=10s --start-period=30s --retries=3 \
    CMD curl -f http://localhost:8080/health || exit 1

# Direct start command (no startup script to avoid complexity)
CMD ["gunicorn", "--config", "gunicorn.conf.py", "wsgi:application"]
