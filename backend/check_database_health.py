"""
Script to check database health and model registration for MDCAN BDM 2025 Certificate Platform
"""

from app import app, db, Participant, ConferenceProgram, SessionRegistration, Notification, CertificateLog, SystemSettings
import sqlalchemy as sa

def check_database_health():
    """Check database health and model registration"""
    with app.app_context():
        try:
            # Check database connection
            with db.engine.connect() as conn:
                conn.execute(sa.text("SELECT 1"))
            print("✅ Database connection successful!")
            
            # Check if all tables exist
            inspector = sa.inspect(db.engine)
            table_names = inspector.get_table_names()
            expected_tables = ['participants', 'conference_programs', 'session_registrations', 
                              'notifications', 'certificate_logs', 'system_settings']
            
            missing_tables = [table for table in expected_tables if table not in table_names]
            if missing_tables:
                print(f"❌ Missing tables: {', '.join(missing_tables)}")
            else:
                print("✅ All expected tables exist!")
            
            # Check model counts
            participant_count = Participant.query.count()
            program_count = ConferenceProgram.query.count()
            session_count = SessionRegistration.query.count()
            notification_count = Notification.query.count()
            log_count = CertificateLog.query.count()
            setting_count = SystemSettings.query.count()
            
            print(f"📊 Database Statistics:")
            print(f"  - Participants: {participant_count}")
            print(f"  - Conference Programs: {program_count}")
            print(f"  - Session Registrations: {session_count}")
            print(f"  - Notifications: {notification_count}")
            print(f"  - Certificate Logs: {log_count}")
            print(f"  - System Settings: {setting_count}")
            
            # Check if system settings are initialized
            settings = SystemSettings.query.all()
            if settings:
                print("✅ System settings are initialized")
                for setting in settings:
                    print(f"  - {setting.key}: {setting.value}")
            else:
                print("❌ System settings are not initialized")
            
            print("✅ Database health check completed successfully!")
            
        except Exception as e:
            print(f"❌ Error checking database health: {str(e)}")

if __name__ == "__main__":
    check_database_health()
