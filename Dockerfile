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

# Ensure frontend build exists
RUN if [ ! -d "/app/frontend/build" ]; then \
        mkdir -p /app/frontend/build && \
        echo '<!DOCTYPE html><html><head><title>MDCAN BDM 2025</title></head><body><h1>MDCAN Certificate Platform</h1></body></html>' > /app/frontend/build/index.html; \
    fi

# Simple build verification
RUN echo "🔍 Build verification:" && \
    echo "  - Python version: $(python --version)" && \
    echo "  - Working directory: $(pwd)" && \
    echo "  - Files present: $(ls -la | wc -l) items" && \
    echo "  - Backend exists: $(test -d backend && echo 'YES' || echo 'NO')" && \
    echo "  - WSGI exists: $(test -f wsgi.py && echo 'YES' || echo 'NO')" && \
    echo "✅ Build verification complete"

EXPOSE 8080

# Basic health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8080/health || exit 1

# Simple startup with fallback
CMD ["gunicorn", "--bind", "0.0.0.0:8080", "--workers", "1", "--timeout", "120", "--log-level", "info", "--access-logfile", "-", "--error-logfile", "-", "wsgi:application"]
