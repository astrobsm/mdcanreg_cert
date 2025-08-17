FROM python:3.11-slim

WORKDIR /app

# Install system dependencies for PDF generation and PostgreSQL
RUN apt-get update && apt-get install -y --no-install-recommends \
    wget \
    xvfb \
    libpq-dev \
    gcc \
    libx11-6 \
    libxext6 \
    libxrender1 \
    libxtst6 \
    libxi6 \
    fontconfig \
    libfontconfig1 \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Install wkhtmltopdf from the official source
RUN wget -q https://github.com/wkhtmltopdf/packaging/releases/download/0.12.6.1-2/wkhtmltox_0.12.6.1-2.bullseye_amd64.deb \
    && dpkg -i wkhtmltox_0.12.6.1-2.bullseye_amd64.deb || true \
    && apt-get update && apt-get install -f -y \
    && rm wkhtmltox_0.12.6.1-2.bullseye_amd64.deb \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy all application files
COPY . .

# Set Python path to include current directory and backend
ENV PYTHONPATH="/app:/app/backend:$PYTHONPATH"

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

# Set Python path to include the app directory
ENV PYTHONPATH=/app

# Use environment variable for port binding with proper working directory
WORKDIR /app
CMD ["gunicorn", "--bind", "0.0.0.0:8080", "--workers", "1", "--timeout", "120", "--log-level", "info", "wsgi:application"]
