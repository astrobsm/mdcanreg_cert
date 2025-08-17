#!/bin/bash
# Simple startup script with extensive logging for Digital Ocean debugging

echo "🚀 MDCAN BDM 2025 - Startup Script Begin"
echo "Timestamp: $(date)"
echo "Working Directory: $(pwd)"
echo "User: $(whoami)"
echo "Python Version: $(python --version)"

echo "📁 Directory Contents:"
ls -la

echo "🔍 Critical Files Check:"
echo "  wsgi.py exists: $(test -f wsgi.py && echo 'YES' || echo 'NO')"
echo "  app.py exists: $(test -f app.py && echo 'YES' || echo 'NO')"
echo "  backend/ exists: $(test -d backend && echo 'YES' || echo 'NO')"
echo "  requirements.txt exists: $(test -f requirements.txt && echo 'YES' || echo 'NO')"

echo "🌍 Environment Variables:"
echo "  PORT: ${PORT:-'not set'}"
echo "  DATABASE_URL: $(test -n "$DATABASE_URL" && echo 'configured' || echo 'not set')"
echo "  SECRET_KEY: $(test -n "$SECRET_KEY" && echo 'configured' || echo 'not set')"

echo "🐍 Python Path:"
export PYTHONPATH="/app:/app/backend"
echo "  PYTHONPATH: $PYTHONPATH"

echo "🧪 Quick Import Test:"
python -c "
try:
    import flask
    print('  ✅ Flask import: OK')
except Exception as e:
    print(f'  ❌ Flask import: FAILED - {e}')

try:
    import backend.minimal_app
    print('  ✅ Backend import: OK')
except Exception as e:
    print(f'  ❌ Backend import: FAILED - {e}')
"

echo "🚦 Starting Application..."
echo "Attempting: gunicorn --bind 0.0.0.0:8080 --workers 1 --timeout 120 --log-level info wsgi:application"

# Start the application
exec gunicorn --bind 0.0.0.0:8080 --workers 1 --timeout 120 --log-level info --access-logfile - --error-logfile - wsgi:application
