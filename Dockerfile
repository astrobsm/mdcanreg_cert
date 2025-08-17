FROM python:3.11-slim

WORKDIR /app

# Install essential system dependencies only
RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq-dev \
    gcc \
    curl \
    wget \
    && rm -rf /var/lib/apt/lists/*

# Create a dummy wkhtmltopdf that fails gracefully
RUN echo '#!/bin/bash' > /usr/local/bin/wkhtmltopdf && \
    echo 'echo "Error: wkhtmltopdf not available in this container - PDF generation disabled"' >> /usr/local/bin/wkhtmltopdf && \
    echo 'exit 1' >> /usr/local/bin/wkhtmltopdf && \
    chmod +x /usr/local/bin/wkhtmltopdf

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt && \
    echo "📦 Dependencies installed successfully" && \
    python -c "import flask; import flask_sqlalchemy; import psycopg2; print('✅ Critical dependencies verified')"

# Copy application files
COPY . .

# Make startup script executable
RUN chmod +x startup_check.sh

# Set Python environment with explicit environment variables
ENV PYTHONPATH="/app:/app/backend"
ENV PYTHONUNBUFFERED=1
ENV FLASK_ENV=production
ENV PORT=8080

# Add debug logging for environment variables during build
RUN echo "🔧 Environment Configuration Check:" && \
    echo "  - PYTHONPATH: ${PYTHONPATH}" && \
    echo "  - PORT: ${PORT}" && \
    echo "  - FLASK_ENV: ${FLASK_ENV}" && \
    echo "  - Build completed successfully"

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

EXPOSE 8080

HEALTHCHECK --interval=30s --timeout=10s --start-period=15s --retries=5 \
    CMD curl -f http://localhost:${PORT:-8080}/health || curl -f http://127.0.0.1:${PORT:-8080}/health || exit 1

CMD ["sh", "-c", "./startup_check.sh && echo '🚀 MDCAN BDM 2025 - STARTING APPLICATION' && echo 'Binding: 0.0.0.0:'${PORT:-8080} && echo 'Environment: production' && echo 'DATABASE_URL:' ${DATABASE_URL:0:30}... && echo 'Starting gunicorn...' && exec gunicorn --config gunicorn.conf.py wsgi:application"]
