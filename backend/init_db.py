"""
Database initialization script for MDCAN BDM 2025 Certificate Platform
Creates the PostgreSQL database and tables with proper constraints and indexes.
"""

import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
import sys
import os

# Database configuration
DB_HOST = 'localhost'
DB_USER = 'postgres'
DB_PASSWORD = 'natiss_natiss'
DB_NAME = 'mdcan042_db'

def create_database():
    """Create the PostgreSQL database if it doesn't exist"""
    try:
        # Connect to PostgreSQL server (not to a specific database)
        conn = psycopg2.connect(
            host=DB_HOST,
            user=DB_USER,
            password=DB_PASSWORD,
            database='postgres'  # Connect to default postgres database
        )
        conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        cursor = conn.cursor()
        
        # Check if database exists
        cursor.execute(f"SELECT 1 FROM pg_database WHERE datname = '{DB_NAME}'")
        exists = cursor.fetchone()
        
        if not exists:
            # Create database
            cursor.execute(f'CREATE DATABASE "{DB_NAME}"')
            print(f"✅ Database '{DB_NAME}' created successfully!")
        else:
            print(f"ℹ️  Database '{DB_NAME}' already exists.")
        
        cursor.close()
        conn.close()
        return True
        
    except psycopg2.Error as e:
        print(f"❌ Error creating database: {e}")
        return False

def initialize_tables():
    """Initialize database tables using SQLAlchemy"""
    try:
        # Import the Flask app to initialize tables
        sys.path.append(os.path.dirname(os.path.abspath(__file__)))
        from app import app, db, SystemSettings
        
        with app.app_context():
            # Create all tables
            db.create_all()
            print("✅ Database tables created successfully!")
            
            # Insert default system settings
            default_settings = [
                ('email_enabled', 'true', 'Enable/disable email sending'),
                ('certificate_template_version', '1.0', 'Current certificate template version'),
                ('max_bulk_upload_size', '1000', 'Maximum number of records in bulk upload'),
                ('conference_name', 'MDCAN BDM 14th – 2025', 'Conference name for certificates'),
                ('conference_date', '1st – 6th September, 2025', 'Conference date for certificates'),
                ('conference_location', 'Enugu', 'Conference location'),
                ('president_name', 'Prof. Aminu Mohammed', 'MDCAN President name'),
                ('chairman_name', 'Prof. Appolos Ndukuba', 'LOC Chairman name'),
            ]
            
            for key, value, description in default_settings:
                existing = SystemSettings.query.filter_by(key=key).first()
                if not existing:
                    setting = SystemSettings(key=key, value=value, description=description)
                    db.session.add(setting)
            
            db.session.commit()
            print("✅ Default system settings initialized!")
            
        return True
        
    except Exception as e:
        print(f"❌ Error initializing tables: {e}")
        return False

def main():
    print("🚀 Initializing MDCAN BDM 2025 Certificate Database...")
    print(f"Database: {DB_NAME}")
    print(f"Host: {DB_HOST}")
    print(f"User: {DB_USER}")
    print()
    
    # Step 1: Create database
    if not create_database():
        print("❌ Failed to create database. Exiting.")
        sys.exit(1)
    
    # Step 2: Initialize tables
    if not initialize_tables():
        print("❌ Failed to initialize tables. Exiting.")
        sys.exit(1)
    
    print()
    print("🎉 Database initialization completed successfully!")
    print()
    print("Next steps:")
    print("1. Update your .env file with the database credentials")
    print("2. Start the Flask application: python app.py")
    print("3. Access the application at: http://localhost:5000")

if __name__ == '__main__':
    main()
