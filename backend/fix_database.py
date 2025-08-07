from app import app, db, Participant, CertificateLog
import sqlalchemy

with app.app_context():
    try:
        # Create all tables
        db.create_all()
        print("✅ Created all database tables successfully")
        
        # Check participants table
        participant_count = Participant.query.count()
        print(f"✅ Participant count: {participant_count}")
        
        # Check certificate_logs table
        try:
            log_count = CertificateLog.query.count()
            print(f"✅ Certificate log count: {log_count}")
        except Exception as log_error:
            print(f"❌ Error checking certificate logs: {str(log_error)}")
            
        print("✅ Database fix completed successfully!")
    except Exception as e:
        print(f"❌ Error: {str(e)}")
