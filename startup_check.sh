#!/bin/bash
# Startup verification script for MDCAN BDM 2025 application

echo "🔍 MDCAN BDM 2025 - Startup Verification"
echo "========================================="

# Check environment variables
echo "📋 Environment Variables Check:"
echo "  PORT: ${PORT:-NOT SET}"
echo "  FLASK_ENV: ${FLASK_ENV:-NOT SET}"
echo "  DATABASE_URL: ${DATABASE_URL:0:30}..."
echo "  ADMIN_PASSWORD: ${ADMIN_PASSWORD:+CONFIGURED}"
echo "  EMAIL_HOST: ${EMAIL_HOST:-NOT SET}"

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
