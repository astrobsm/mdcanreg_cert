from flask import Flask
from flask_sqlalchemy import SQLAlchemy
import os
import psycopg2

# Check if tables exist
def check_tables():
    try:
        # Connect to PostgreSQL directly
        conn = psycopg2.connect(
            host="localhost",
            database="mdcan042_db",
            user="postgres",
            password="natiss_natiss"
        )
        
        # Create a cursor
        cur = conn.cursor()
        
        # Check if participants table exists
        cur.execute("SELECT EXISTS (SELECT FROM information_schema.tables WHERE table_name = 'participants')")
        participants_exists = cur.fetchone()[0]
        
        # Check if certificate_logs table exists
        cur.execute("SELECT EXISTS (SELECT FROM information_schema.tables WHERE table_name = 'certificate_logs')")
        certificate_logs_exists = cur.fetchone()[0]
        
        # Check if system_settings table exists
        cur.execute("SELECT EXISTS (SELECT FROM information_schema.tables WHERE table_name = 'system_settings')")
        system_settings_exists = cur.fetchone()[0]
        
        print(f"Participants table exists: {participants_exists}")
        print(f"Certificate logs table exists: {certificate_logs_exists}")
        print(f"System settings table exists: {system_settings_exists}")
        
        # Close the cursor and connection
        cur.close()
        conn.close()
        
        return participants_exists and certificate_logs_exists and system_settings_exists
    except Exception as e:
        print(f"Error checking tables: {e}")
        return False

# Function to update the database connection
def update_database_connection():
    # Check if tables exist
    tables_exist = check_tables()
    
    # If tables exist, print success message
    if tables_exist:
        print("Database connection successful! All required tables exist.")
        print("To use this database in your application, update your DATABASE_URL environment variable or app.py to:")
        print("DATABASE_URL = 'postgresql://postgres:natiss_natiss@localhost/mdcan042_db'")
    else:
        print("Database connection successful, but some tables are missing.")
        print("Run the SQL scripts to create the missing tables.")

if __name__ == "__main__":
    update_database_connection()
