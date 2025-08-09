"""
Main entry point for MDCAN BDM 2025 Certificate Platform
Simple wrapper around digital_ocean_app for cleaner deployment configuration
"""

from digital_ocean_app import app

if __name__ == "__main__":
    import os
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port, debug=False)
