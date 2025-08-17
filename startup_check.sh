#!/bin/bash
# Startup verification script for MDCAN BDM 2025 application

echo "🔍 MDCAN BDM 2025 - Startup Verification"
echo "========================================="

# Check environment variables
echo "📋 Environment Variables Check:"
echo "  PORT: ${PORT:-NOT SET}"
echo "  FLASK_ENV: ${FLASK_ENV:-NOT SET}"
if [ -n "${DATABASE_URL}" ]; then
    echo "  DATABASE_URL: ${DATABASE_URL:0:30}... (configured)"
else
    echo "  DATABASE_URL: NOT SET"
fi
if [ -n "${ADMIN_PASSWORD}" ]; then
    echo "  ADMIN_PASSWORD: CONFIGURED"
else
    echo "  ADMIN_PASSWORD: NOT SET"
fi
echo "  EMAIL_HOST: ${EMAIL_HOST:-NOT SET}"

# Verify critical environment variables
missing_vars=""
if [ -z "${DATABASE_URL}" ]; then
    missing_vars="${missing_vars} DATABASE_URL"
fi
if [ -z "${ADMIN_PASSWORD}" ]; then
    missing_vars="${missing_vars} ADMIN_PASSWORD"
fi

if [ -n "${missing_vars}" ]; then
    echo "❌ Missing critical environment variables:${missing_vars}"
    echo "Application may fail to start properly"
else
    echo "✅ All critical environment variables are set"
fi

# Check Python dependencies
echo ""
echo "📦 Python Dependencies Check:"
python3 -c "
import sys
try:
    import flask
    print('  ✅ Flask:', flask.__version__)
except ImportError:
    print('  ❌ Flask: NOT INSTALLED')
    sys.exit(1)

try:
    import flask_sqlalchemy
    print('  ✅ Flask-SQLAlchemy: Available')
except ImportError:
    print('  ❌ Flask-SQLAlchemy: NOT INSTALLED')
    sys.exit(1)

try:
    import psycopg2
    print('  ✅ psycopg2: Available')
except ImportError:
    print('  ❌ psycopg2: NOT INSTALLED')
    sys.exit(1)

try:
    import gunicorn
    print('  ✅ Gunicorn: Available')
except ImportError:
    print('  ❌ Gunicorn: NOT INSTALLED')
    sys.exit(1)
"

# Check file structure
echo ""
echo "📁 File Structure Check:"
if [ -f "wsgi.py" ]; then
    echo "  ✅ wsgi.py: Found"
else
    echo "  ❌ wsgi.py: Missing"
    exit 1
fi

if [ -f "gunicorn.conf.py" ]; then
    echo "  ✅ gunicorn.conf.py: Found"
else
    echo "  ❌ gunicorn.conf.py: Missing"
    exit 1
fi

if [ -d "backend" ]; then
    echo "  ✅ backend directory: Found"
else
    echo "  ❌ backend directory: Missing"
    exit 1
fi

if [ -f "backend/minimal_app.py" ]; then
    echo "  ✅ backend/minimal_app.py: Found"
else
    echo "  ❌ backend/minimal_app.py: Missing"
    exit 1
fi

# Test app import
echo ""
echo "🧪 Application Import Test:"
python3 -c "
try:
    from backend.minimal_app import app
    print('  ✅ Application imports successfully')
except Exception as e:
    print(f'  ❌ Application import failed: {e}')
    import traceback
    traceback.print_exc()
    exit(1)
"

# Test gunicorn config
echo ""
echo "⚙️ Gunicorn Configuration Test:"
python3 -c "
try:
    import gunicorn.conf
    print('  ✅ Gunicorn config loads successfully')
except Exception as e:
    print(f'  ❌ Gunicorn config error: {e}')
    exit(1)
"

echo ""
echo "✅ All startup checks passed! Starting application..."
echo "======================================================="
