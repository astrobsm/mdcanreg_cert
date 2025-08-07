"""
Database optimization script for MDCAN BDM 2025 Certificate Platform
Creates indexes for frequently accessed columns and optimizes the database
"""

import os
import sys
import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT

# Database connection parameters
DB_NAME = os.environ.get('DB_NAME', 'mdcan042_db')
DB_USER = os.environ.get('DB_USER', 'postgres')
DB_PASSWORD = os.environ.get('DB_PASSWORD', 'natiss_natiss')
DB_HOST = os.environ.get('DB_HOST', 'localhost')
DB_PORT = os.environ.get('DB_PORT', '5432')

def connect_to_database():
    """Connect to the PostgreSQL database"""
    try:
        conn = psycopg2.connect(
            dbname=DB_NAME,
            user=DB_USER,
            password=DB_PASSWORD,
            host=DB_HOST,
            port=DB_PORT
        )
        conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        return conn
    except Exception as e:
        print(f"Error connecting to database: {str(e)}")
        sys.exit(1)

def optimize_database():
    """Run optimization operations on the database"""
    conn = connect_to_database()
    cursor = conn.cursor()
    
    try:
        print("Starting database optimization...")
        
        # Create indexes for frequently accessed columns
        indexes = [
            # Participants table indexes
            "CREATE INDEX IF NOT EXISTS idx_participant_email ON participants(email)",
            "CREATE INDEX IF NOT EXISTS idx_participant_registration_status ON participants(registration_status)",
            "CREATE INDEX IF NOT EXISTS idx_participant_certificate_status ON participants(certificate_status)",
            "CREATE INDEX IF NOT EXISTS idx_participant_created_at ON participants(created_at)",
            
            # Programs table indexes
            "CREATE INDEX IF NOT EXISTS idx_program_date ON programs(program_date)",
            "CREATE INDEX IF NOT EXISTS idx_program_status ON programs(status)",
            
            # Notifications table indexes
            "CREATE INDEX IF NOT EXISTS idx_notification_sent_at ON notifications(sent_at)",
            "CREATE INDEX IF NOT EXISTS idx_notification_recipient_type ON notifications(recipient_type)",
            
            # Attendance table indexes
            "CREATE INDEX IF NOT EXISTS idx_attendance_participant_id ON attendance(participant_id)",
            "CREATE INDEX IF NOT EXISTS idx_attendance_program_id ON attendance(program_id)",
            "CREATE INDEX IF NOT EXISTS idx_attendance_checkin_time ON attendance(checkin_time)",
            
            # Composite indexes for common queries
            "CREATE INDEX IF NOT EXISTS idx_participant_reg_cert_status ON participants(registration_status, certificate_status)",
            "CREATE INDEX IF NOT EXISTS idx_attendance_participant_program ON attendance(participant_id, program_id)"
        ]
        
        for index_query in indexes:
            print(f"Creating index: {index_query}")
            cursor.execute(index_query)
        
        # Analyze tables for query optimization
        tables = ["participants", "programs", "notifications", "attendance"]
        for table in tables:
            print(f"Analyzing table: {table}")
            cursor.execute(f"ANALYZE {table}")
        
        # Vacuum database to reclaim space and update statistics
        print("Vacuuming database...")
        old_isolation_level = conn.isolation_level
        conn.set_isolation_level(0)
        cursor.execute("VACUUM ANALYZE")
        conn.set_isolation_level(old_isolation_level)
        
        print("Database optimization completed successfully!")
        
    except Exception as e:
        print(f"Error during database optimization: {str(e)}")
    finally:
        cursor.close()
        conn.close()

if __name__ == "__main__":
    optimize_database()
