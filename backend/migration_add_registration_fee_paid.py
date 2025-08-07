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
    
    # Add retry logic for database connection
    max_retries = 3
    retry_count = 0
    
    while retry_count < max_retries:
        try:
            connection = psycopg2.connect(DATABASE_URL)
            connection.autocommit = True
            cursor = connection.cursor()
            
            # Check if the column already exists
            print("Checking if registration_fee_paid column exists...")
            cursor.execute("""
                SELECT column_name 
                FROM information_schema.columns 
                WHERE table_name='participants' AND column_name='registration_fee_paid';
            """)
            
            if cursor.fetchone() is None:
                print("Adding registration_fee_paid column to participants table...")
                # Add the column if it doesn't exist
                cursor.execute("""
                    ALTER TABLE participants 
                    ADD COLUMN registration_fee_paid BOOLEAN DEFAULT FALSE;
                """)
                print("Column 'registration_fee_paid' added successfully!")
            else:
                print("Column 'registration_fee_paid' already exists.")
            
            # Close connection
            cursor.close()
            connection.close()
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
