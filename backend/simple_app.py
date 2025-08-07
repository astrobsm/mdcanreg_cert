"""
Simple database optimization script for MDCAN BDM 2025 Certificate Platform
"""

import sqlalchemy
from app import app, db

def optimize_database():
    """Optimize the database by analyzing tables and creating additional indexes if needed"""
    with app.app_context():
        try:
            # Connect to the database
            with db.engine.connect() as conn:
                # Analyze tables for better query planning
                conn.execute(sqlalchemy.text('ANALYZE participants;'))
                conn.execute(sqlalchemy.text('ANALYZE certificate_logs;'))
                conn.execute(sqlalchemy.text('ANALYZE system_settings;'))
                conn.commit()
                
                # Create additional indexes if they don't exist
                conn.execute(sqlalchemy.text('''
                    CREATE INDEX IF NOT EXISTS idx_participants_email_status 
                    ON participants(email, certificate_status);
                '''))
                conn.execute(sqlalchemy.text('''
                    CREATE INDEX IF NOT EXISTS idx_participants_created_type 
                    ON participants(created_at, certificate_type);
                '''))
                conn.execute(sqlalchemy.text('''
                    CREATE INDEX IF NOT EXISTS idx_participants_registration_combined 
                    ON participants(registration_type, registration_status);
                '''))
                conn.execute(sqlalchemy.text('''
                    CREATE INDEX IF NOT EXISTS idx_certificate_logs_action_status 
                    ON certificate_logs(action, status);
                '''))
                conn.commit()
                
            print("✅ Database optimization completed successfully!")
            print("Tables analyzed and additional indexes created.")
        except Exception as e:
            print(f"❌ Error optimizing database: {e}")

if __name__ == "__main__":
    optimize_database()
