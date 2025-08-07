import os
import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
from dotenv import load_dotenv
import sys

# Load environment variables
load_dotenv()

# Get database URL from environment
database_url = os.getenv('DATABASE_URL')

if not database_url:
    print("❌ DATABASE_URL environment variable not set")
    sys.exit(1)

try:
    # Connect to the database
    print(f"Connecting to database...")
    conn = psycopg2.connect(database_url)
    conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
    cursor = conn.cursor()
    
    print(f"Connection established successfully.")
    
    # Read the migration SQL file
    with open('migrate_add_missing_columns.sql', 'r') as f:
        migration_sql = f.read()
    
    # Execute the migration
    print(f"Executing migration...")
    cursor.execute(migration_sql)
    
    # Close the connection
    cursor.close()
    conn.close()
    
    print("✅ Migration completed successfully")
    
except Exception as e:
    print(f"❌ Error during migration: {e}")
    sys.exit(1)
