import os
import sys
import psycopg2
from psycopg2 import sql
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
from dotenv import load_dotenv

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
    
    # Get a list of all tables
    cursor.execute("SELECT table_name FROM information_schema.tables WHERE table_schema = 'public'")
    tables = cursor.fetchall()
    
    print("\n===== DATABASE TABLES =====")
    for table in tables:
        print(f"- {table[0]}")
    
    # For each table, get column information
    for table in tables:
        table_name = table[0]
        print(f"\n===== TABLE: {table_name} =====")
        
        # Get column information
        cursor.execute("""
            SELECT column_name, data_type, is_nullable, column_default
            FROM information_schema.columns
            WHERE table_schema = 'public' AND table_name = %s
            ORDER BY ordinal_position
        """, (table_name,))
        
        columns = cursor.fetchall()
        
        for column in columns:
            col_name, data_type, is_nullable, default = column
            print(f"- {col_name}: {data_type} (nullable: {is_nullable}, default: {default})")
        
        # Get index information
        cursor.execute("""
            SELECT indexname, indexdef
            FROM pg_indexes
            WHERE tablename = %s
        """, (table_name,))
        
        indexes = cursor.fetchall()
        
        if indexes:
            print("\n  Indexes:")
            for index in indexes:
                index_name, index_def = index
                print(f"  - {index_name}: {index_def}")
    
    # Check for foreign key constraints
    print("\n===== FOREIGN KEY CONSTRAINTS =====")
    cursor.execute("""
        SELECT
            tc.table_name, kcu.column_name,
            ccu.table_name AS foreign_table_name,
            ccu.column_name AS foreign_column_name
        FROM
            information_schema.table_constraints AS tc
            JOIN information_schema.key_column_usage AS kcu
              ON tc.constraint_name = kcu.constraint_name
              AND tc.table_schema = kcu.table_schema
            JOIN information_schema.constraint_column_usage AS ccu
              ON ccu.constraint_name = tc.constraint_name
              AND ccu.table_schema = tc.table_schema
        WHERE tc.constraint_type = 'FOREIGN KEY'
    """)
    
    fk_constraints = cursor.fetchall()
    
    for constraint in fk_constraints:
        table, column, ref_table, ref_column = constraint
        print(f"- {table}.{column} -> {ref_table}.{ref_column}")
    
    # Close the connection
    cursor.close()
    conn.close()
    
    print("\n✅ Database schema check completed successfully")
    
except Exception as e:
    print(f"❌ Error checking database schema: {e}")
    sys.exit(1)
