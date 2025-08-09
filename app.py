"""
Entry point for MDCAN BDM 2025 Certificate Platform
Compatible with both app:app and main:app deployment patterns
"""

from digital_ocean_app import app

if __name__ == "__main__":
    import os
    # Use $PORT environment variable with fallback to 8080
    port = int(os.environ.get('PORT', 8080))
    print(f"🚀 Starting MDCAN BDM 2025 server on 0.0.0.0:{port}")
    print(f"PORT environment variable: {os.environ.get('PORT', 'not set, using default 8080')}")
    app.run(host='0.0.0.0', port=port, debug=False)
