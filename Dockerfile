FROM python:3.10-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq5 \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy application files
COPY . .

# Set environment variables
ENV PYTHONPATH="/app:/app/backend"
ENV PYTHONUNBUFFERED=1
ENV FLASK_ENV=production

# Create frontend build directory if it doesn't exist
RUN mkdir -p frontend/build && \
    echo '<!DOCTYPE html><html><head><title>MDCAN BDM 2025</title></head><body><h1>Loading...</h1></body></html>' > frontend/build/index.html

EXPOSE 8080

# Health check with generous timeout
HEALTHCHECK --interval=30s --timeout=15s --start-period=120s --retries=3 \
    CMD curl -f http://localhost:8080/health || exit 1

# Start command using environment PORT variable
CMD gunicorn --bind 0.0.0.0:${PORT:-8080} --workers 2 --timeout 120 --access-logfile - --error-logfile - wsgi:application
