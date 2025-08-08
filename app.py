"""
Entry point for the MDCAN BDM 2025 Certificate Platform.
This file helps with Digital Ocean deployment by ensuring the app module is correctly loaded.
"""
import os
import sys
import logging

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Add current directory to path to ensure imports work
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)
    logger.info(f"Added {current_dir} to sys.path")

# Print current directory structure for debugging
logger.info(f"Current directory: {os.getcwd()}")
logger.info(f"Directory contents: {os.listdir('.')}")
if os.path.exists('backend'):
    logger.info(f"Backend directory contents: {os.listdir('backend')}")
else:
    logger.info("Backend directory not found")

# Try to import the main app, but fall back to a minimal app if there are issues
try:
    logger.info("Attempting to import main application...")
    
    # First try to import pandas and numpy to catch any compatibility issues early
    try:
        logger.info("Checking numpy and pandas compatibility...")
        import numpy
        logger.info(f"Numpy version: {numpy.__version__}")
        import pandas
        logger.info(f"Pandas version: {pandas.__version__}")
        
        # Check for schedule package
        try:
            import schedule
            logger.info(f"Schedule version: {schedule.__version__}")
        except ImportError:
            logger.warning("Schedule package not found, installing...")
            import subprocess
            subprocess.check_call([sys.executable, "-m", "pip", "install", "schedule"])
            import schedule
            logger.info(f"Schedule installed and imported, version: {schedule.__version__}")
    except ValueError as ve:
        if "numpy.dtype size changed" in str(ve):
            logger.error("Binary incompatibility between numpy and pandas detected")
            logger.error(f"Error: {str(ve)}")
            raise ImportError(f"Binary incompatibility between numpy and pandas: {str(ve)}")
        else:
            logger.error(f"ValueError in numpy/pandas import: {str(ve)}")
            raise
    except Exception as e:
        logger.error(f"Error importing numpy or pandas: {str(e)}")
        raise
        
    # Try multiple import paths to be more robust
    try:
        # Import Flask app from the backend/app.py file (standard path)
        # Use importlib to avoid circular imports
        import importlib.util
        import importlib
        
        # First check if backend module is available
        if importlib.util.find_spec("backend") is not None:
            logger.info("Backend module found, attempting to import app")
            # Import the backend app module
            backend_app = importlib.import_module("backend.app")
            # Get the app object from the module
            application = getattr(backend_app, "app")
            logger.info("Main application imported successfully from backend.app.")
        else:
            logger.warning("Backend module not found, trying direct import")
            # Try alternative import using spec
            spec = importlib.util.spec_from_file_location("backend_app", os.path.join(current_dir, "backend", "app.py"))
            backend_app = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(backend_app)
            application = backend_app.app
            logger.info("Main application imported successfully using spec loader.")
    except ImportError as e:
        logger.warning(f"Failed to import from backend.app: {e}")
        # Try alternative import path
        sys.path.insert(0, os.path.join(current_dir, 'backend'))
        try:
            # Rename the import to avoid conflict with the current module
            import app as backend_app
            application = backend_app.app
            logger.info("Main application imported successfully from direct app import.")
        except ImportError as ie:
            logger.error(f"All import methods failed: {ie}")
            raise
    
    # Alias the application as 'app' for Gunicorn
    app = application
    
except Exception as e:
    logger.error(f"Error importing main application: {str(e)}")
    logger.error(f"Exception type: {type(e).__name__}")
    logger.error(f"Exception traceback: {sys.exc_info()}")
    
    # Try the minimal backend app first
    try:
        logger.info("Trying minimal backend app...")
        from backend.minimal_app import app as minimal_app
        logger.info("Minimal backend app loaded successfully.")
        # Successfully loaded minimal app, continue with this app
        app = minimal_app
        
        # Add a route to indicate we're running the minimal app
        from flask import jsonify
        @app.route('/api/status')
        def enhanced_status():
            """Enhanced status endpoint to show we're running in minimal mode"""
            return jsonify({
                "status": "ok",
                "mode": "minimal",
                "message": "Running minimal app with full API functionality",
                "version": "minimal",
                "available_endpoints": [
                    "/api/health",
                    "/api/test", 
                    "/api/participants",
                    "/api/certificates/{id}",
                    "/api/send-certificate/{id}",
                    "/api/statistics",
                    "/api/bulk/participants"
                ],
                "environment": {
                    "python_version": sys.version,
                    "database_url": bool(os.environ.get('DATABASE_URL')),
                    "email_configured": bool(os.environ.get('EMAIL_HOST'))
                }
            })
    except Exception as minimal_error:
        logger.error(f"Error loading minimal backend app: {str(minimal_error)}")
        
        logger.info("Falling back to minimal application...")
        
        # Import the fallback minimal app
        try:
            from fallback_app import app
            logger.info("Fallback application loaded successfully.")
        except Exception as fallback_error:
            logger.error(f"Error loading fallback app: {str(fallback_error)}")
            
            # If even the fallback app fails, create a super minimal app
            from flask import Flask, jsonify
            app = Flask(__name__)
            
            @app.route('/')
            def emergency_home():
                return jsonify({
                    "status": "degraded",
                    "message": "Emergency Fallback Mode",
                    "error": str(e),
                    "exception_type": str(type(e).__name__),
                    "path_info": {
                        "cwd": os.getcwd(),
                        "sys_path": sys.path
                    }
                })
            
            @app.route('/debug')
            def debug_info():
                """Return debug information to help diagnose deployment issues."""
                return jsonify({
                    "status": "debug",
                    "environment": dict(os.environ),
                    "directory_structure": {
                        "root": os.listdir("."),
                        "backend_exists": os.path.exists("backend"),
                        "backend_contents": os.listdir("backend") if os.path.exists("backend") else "N/A"
                    },
                    "python_info": {
                        "version": sys.version,
                        "path": sys.path
                    }
                })
            
            logger.info("Emergency minimal application created.")

# Direct execution (for local testing)
if __name__ == "__main__":
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port)
