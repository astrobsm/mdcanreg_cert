FROM python:3.11-slim

WORKDIR /app

# Install system dependencies for PDF generation and PostgreSQL
RUN apt-get update && apt-get install -y --no-install-recommends \
    wkhtmltopdf \
    libpq-dev \
    gcc \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy all application files
COPY . .

# Ensure the frontend build directory exists and has the right structure
RUN ls -la /app/
RUN if [ -d "/app/frontend/build" ]; then \
        echo "Frontend build found"; \
        ls -la /app/frontend/build/; \
    else \
        echo "Frontend build not found"; \
        mkdir -p /app/frontend/build; \
        echo '<!DOCTYPE html><html><head><title>MDCAN BDM 2025</title></head><body><h1>Frontend build missing</h1></body></html>' > /app/frontend/build/index.html; \
    fi

EXPOSE 8080

# Use environment variable for port binding
CMD ["sh", "-c", "gunicorn --bind 0.0.0.0:${PORT:-8080} --workers 1 --timeout 120 --log-level info app:app"]
