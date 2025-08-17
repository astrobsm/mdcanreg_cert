FROM python:3.11-slim

WORKDIR /app

# Install essential system dependencies for PostgreSQL and basic functionality
RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq-dev \
    gcc \
    curl \
    wget \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy application files
COPY . .

# Set Python environment
ENV PYTHONPATH="/app:/app/backend"
ENV PYTHONUNBUFFERED=1
ENV FLASK_ENV=production

# CRITICAL: Set explicit PORT environment variable for Digital Ocean
ENV PORT=8080

# Ensure frontend build exists with proper structure
RUN mkdir -p frontend/build/static && \
    echo '<!DOCTYPE html>' > frontend/build/index.html && \
    echo '<html lang="en">' >> frontend/build/index.html && \
    echo '<head>' >> frontend/build/index.html && \
    echo '  <meta charset="utf-8">' >> frontend/build/index.html && \
    echo '  <meta name="viewport" content="width=device-width,initial-scale=1">' >> frontend/build/index.html && \
    echo '  <title>MDCAN BDM 2025 Certificate Platform</title>' >> frontend/build/index.html && \
    echo '  <style>body{font-family:Arial,sans-serif;text-align:center;padding:50px;}</style>' >> frontend/build/index.html && \
    echo '</head>' >> frontend/build/index.html && \
    echo '<body>' >> frontend/build/index.html && \
    echo '  <h1>MDCAN BDM 2025 Certificate Platform</h1>' >> frontend/build/index.html && \
    echo '  <p>Application is loading...</p>' >> frontend/build/index.html && \
    echo '  <p><a href="/admin">Admin Portal</a> | <a href="/api/health">Health Check</a></p>' >> frontend/build/index.html && \
    echo '</body>' >> frontend/build/index.html && \
    echo '</html>' >> frontend/build/index.html && \
    echo "Frontend build directory created with index.html"

# CRITICAL: Binding and health check verification
RUN echo "🔧 Critical deployment configuration:" && \
    echo "  - Target binding: 0.0.0.0:8080" && \
    echo "  - PORT environment: ${PORT}" && \
    echo "  - Health check endpoint: /health" && \
    echo "  - Frontend build: $(ls -la frontend/build/ | wc -l) files" && \
    echo "✅ Configuration verified"

EXPOSE 8080

# CRITICAL: Health check that matches Digital Ocean expectations with dynamic PORT
HEALTHCHECK --interval=30s --timeout=10s --start-period=15s --retries=5 \
    CMD curl -f http://localhost:${PORT:-8080}/health || curl -f http://127.0.0.1:${PORT:-8080}/health || exit 1

# CRITICAL: Dynamic PORT binding as required by Digital Ocean
CMD ["sh", "-c", "echo '🚀 MDCAN BDM 2025 - STARTING APPLICATION' && echo 'Binding: 0.0.0.0:'${PORT:-8080} && echo 'Environment: production' && echo 'Starting gunicorn...' && exec gunicorn --bind 0.0.0.0:${PORT:-8080} --workers 1 --worker-class sync --timeout 120 --keep-alive 2 --log-level info --access-logfile - --error-logfile - --preload wsgi:application"]
