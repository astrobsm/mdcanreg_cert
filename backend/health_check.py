"""
Simple API health check endpoint for MDCAN BDM 2025 Certificate Platform
"""

from flask import jsonify
import sqlalchemy as sa
from datetime import datetime

@app.route('/api/health', methods=['GET'])
def health_check():
    """API health check endpoint"""
    try:
        # Check database connection
        db_status = "ok"
        db_error = None
        postgres_version = None
        
        try:
            with db.engine.connect() as conn:
                # Simple query to check database connection
                result = conn.execute(sa.text("SELECT version();"))
                postgres_version = result.scalar()
        except Exception as e:
            db_status = "error"
            db_error = str(e)
        
        # Get system information
        tables = []
        try:
            if db_status == "ok":
                with db.engine.connect() as conn:
                    # Get list of tables
                    inspector = sa.inspect(db.engine)
                    tables = inspector.get_table_names()
        except Exception as e:
            pass
        
        return jsonify({
            "status": "ok",
            "timestamp": datetime.utcnow().isoformat(),
            "api_version": "1.0.0",
            "database": {
                "status": db_status,
                "error": db_error,
                "version": postgres_version,
                "tables": tables
            },
            "environment": "development" if app.debug else "production"
        })
    except Exception as e:
        return jsonify({
            "status": "error",
            "timestamp": datetime.utcnow().isoformat(),
            "error": str(e)
        }), 500
