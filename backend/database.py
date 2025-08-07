"""
Optimized database connection configuration for Flask-SQLAlchemy
Implements connection pooling and retry mechanisms
"""

from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import create_engine, exc
from sqlalchemy.pool import QueuePool
import time
import os
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class OptimizedDatabase:
    """Database connection manager with optimization features"""
    
    def __init__(self, app=None):
        self.db = SQLAlchemy()
        self.engine = None
        if app is not None:
            self.init_app(app)
    
    def init_app(self, app):
        """Initialize the database with the Flask app"""
        # Get database URL from environment or use default
        DATABASE_URL = os.environ.get('DATABASE_URL', 'postgresql://postgres:natiss_natiss@localhost/bdmcertificate_db')
        if DATABASE_URL.startswith('postgres://'):
            DATABASE_URL = DATABASE_URL.replace('postgres://', 'postgresql://', 1)
        
        # Configure SQLAlchemy
        app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE_URL
        app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
        
        # Performance optimizations
        app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {
            # Connection pool settings
            'pool_size': 10,  # Default number of connections to maintain
            'max_overflow': 20,  # Allow up to this many extra connections when pool is fully used
            'pool_timeout': 30,  # Seconds to wait before giving up on getting a connection
            'pool_recycle': 1800,  # Recycle connections after 30 minutes to prevent stale connections
            'pool_pre_ping': True,  # Check connection validity before using from pool
            
            # Performance settings
            'echo': False,  # Set to True in dev mode to log all SQL
            'echo_pool': False,  # Set to True to log pool checkouts
            
            # PostgreSQL specific optimizations
            'connect_args': {
                'connect_timeout': 10,  # Connection timeout in seconds
                'application_name': 'MDCAN Certificate Platform',  # Identify app in pg_stat_activity
                'options': '-c statement_timeout=30000'  # 30 second query timeout
            }
        }
        
        # Initialize SQLAlchemy with app
        self.db.init_app(app)
        
        # Create a standalone engine for background operations
        self.engine = create_engine(
            DATABASE_URL,
            poolclass=QueuePool,
            pool_size=5,
            max_overflow=10,
            pool_timeout=30,
            pool_recycle=1800
        )
        
        logger.info("Database connection initialized with optimized settings")
    
    def get_engine(self):
        """Get SQLAlchemy engine for raw operations"""
        return self.engine
    
    def execute_with_retry(self, query, params=None, max_retries=3, retry_delay=0.5):
        """Execute a query with retry mechanism for transient errors"""
        retries = 0
        last_error = None
        
        while retries < max_retries:
            try:
                with self.engine.connect() as conn:
                    if params:
                        result = conn.execute(query, params)
                    else:
                        result = conn.execute(query)
                    return result
            except (exc.OperationalError, exc.InterfaceError) as e:
                last_error = e
                retries += 1
                if retries < max_retries:
                    logger.warning(f"Database error, retrying ({retries}/{max_retries}): {str(e)}")
                    time.sleep(retry_delay * retries)  # Exponential backoff
                else:
                    logger.error(f"Database error after {max_retries} retries: {str(e)}")
                    raise
        
        if last_error:
            raise last_error

# Create a singleton instance
db_manager = OptimizedDatabase()
