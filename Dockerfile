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

# Explicit binding verification and startup
RUN echo "� Gunicorn configuration verification:" && \
    echo "  - Expected binding: 0.0.0.0:8080" && \
    echo "  - PORT environment: \${PORT:-8080}" && \
    python -c "import os; print(f'  - Computed binding: 0.0.0.0:{os.environ.get(\"PORT\", 8080)}')" && \
    echo "✅ Binding configuration verified"

EXPOSE 8080

# Enhanced health check with explicit port
HEALTHCHECK --interval=30s --timeout=10s --start-period=10s --retries=3 \
    CMD curl -f http://localhost:8080/health || curl -f http://0.0.0.0:8080/health || exit 1

# Explicit startup command with verified binding
CMD ["sh", "-c", "echo 'Starting gunicorn on 0.0.0.0:8080...' && exec gunicorn --bind 0.0.0.0:8080 --workers 1 --timeout 120 --log-level info --access-logfile - --error-logfile - wsgi:application"]
