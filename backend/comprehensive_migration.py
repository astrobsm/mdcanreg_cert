import os
import psycopg2
from psycopg2 import sql
import time

def run_migration():
    # Get database URL from environment or use default
    DATABASE_URL = os.environ.get('DATABASE_URL', 'postgresql://postgres:natiss_natiss@localhost/bdmcertificate_db')
    if DATABASE_URL.startswith('postgres://'):
        DATABASE_URL = DATABASE_URL.replace('postgres://', 'postgresql://', 1)
    
    print(f"Using database URL: {DATABASE_URL}")
    print("Connecting to database...")
    
    # List of all columns that should be in the participants table
    required_columns = [
        ('registration_status', 'VARCHAR(50) DEFAULT \'pending\''),
        ('registration_fee_paid', 'BOOLEAN DEFAULT FALSE'),
        ('payment_reference', 'VARCHAR(100)'),
        ('dietary_requirements', 'TEXT'),
        ('special_needs', 'TEXT'),
        ('emergency_contact_name', 'VARCHAR(100)'),
        ('emergency_contact_phone', 'VARCHAR(50)'),
        ('email_notifications', 'BOOLEAN DEFAULT TRUE'),
        ('sms_notifications', 'BOOLEAN DEFAULT FALSE'),
        ('push_notifications', 'BOOLEAN DEFAULT FALSE'),
        ('push_subscription', 'TEXT'),
        ('certificate_type', 'VARCHAR(50)'),
        ('certificate_status', 'VARCHAR(50) DEFAULT \'not_issued\''),
        ('certificate_number', 'VARCHAR(100)'),
        ('certificate_sent_at', 'TIMESTAMP'),
        ('created_by', 'VARCHAR(100)'),
        ('registration_source', 'VARCHAR(50) DEFAULT \'website\''),
        ('event_attendance', 'BOOLEAN DEFAULT FALSE'),
        ('special_recognition', 'TEXT'),
        ('first_attendance_date', 'TIMESTAMP'),
        ('last_attendance_date', 'TIMESTAMP'),
        ('materials_provided', 'BOOLEAN DEFAULT FALSE'),
        ('materials_provided_date', 'TIMESTAMP'),
        ('materials_provided_by', 'VARCHAR(100)'),
    ]
    
    # Add retry logic for database connection
    max_retries = 3
    retry_count = 0
    
    while retry_count < max_retries:
        try:
            connection = psycopg2.connect(DATABASE_URL)
            connection.autocommit = True
            cursor = connection.cursor()
            
            # First, ensure the participants table exists
            cursor.execute("""
                SELECT EXISTS (
                    SELECT FROM information_schema.tables 
                    WHERE table_name = 'participants'
                );
            """)
            
            if not cursor.fetchone()[0]:
                print("Creating participants table...")
                cursor.execute("""
                    CREATE TABLE participants (
                        id SERIAL PRIMARY KEY,
                        name VARCHAR(100) NOT NULL,
                        email VARCHAR(100) UNIQUE NOT NULL,
                        organization VARCHAR(100),
                        position VARCHAR(100),
                        phone_number VARCHAR(50),
                        registration_type VARCHAR(50),
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    );
                """)
                print("Participants table created successfully!")
            
            # Check for each column and add if it doesn't exist
            for column_name, column_type in required_columns:
                cursor.execute("""
                    SELECT column_name 
                    FROM information_schema.columns 
                    WHERE table_name='participants' AND column_name=%s;
                """, (column_name,))
                
                if cursor.fetchone() is None:
                    print(f"Adding {column_name} column to participants table...")
                    # Add the column if it doesn't exist
                    cursor.execute(sql.SQL("""
                        ALTER TABLE participants 
                        ADD COLUMN {} {};
                    """).format(sql.Identifier(column_name), sql.SQL(column_type)))
                    print(f"Column '{column_name}' added successfully!")
                else:
                    print(f"Column '{column_name}' already exists.")
            
            # Close connection
            cursor.close()
            connection.close()
            print("Database migration completed successfully.")
            print("Database connection closed.")
            return True
            
        except Exception as e:
            print(f"Error during migration (attempt {retry_count + 1}/{max_retries}): {e}")
            retry_count += 1
            if retry_count < max_retries:
                sleep_time = 2 ** retry_count  # Exponential backoff
                print(f"Retrying in {sleep_time} seconds...")
                time.sleep(sleep_time)
            else:
                print("Maximum retry attempts reached. Migration failed.")
                return False

if __name__ == "__main__":
    run_migration()
