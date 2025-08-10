#!/usr/bin/env python3
"""
Digital Ocean Database Setup Script
Connects directly to the Digital Ocean PostgreSQL database and creates required tables
"""

import psycopg2
import sys
from datetime import datetime

# Digital Ocean Database Configuration
DB_CONFIG = {
    'host': 'YOUR_DB_HOST',
    'port': 25060,
    'database': 'defaultdb',
    'user': 'mdcanconfreg',
    'password': 'YOUR_DB_PASSWORD',
    'sslmode': 'require'
}

def create_connection():
    """Create a connection to the Digital Ocean PostgreSQL database"""
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        print("✅ Successfully connected to Digital Ocean database")
        return conn
    except Exception as e:
        print(f"❌ Failed to connect to database: {e}")
        return None

def setup_database(conn):
    """Create all required tables for the MDCAN platform"""
    cursor = conn.cursor()
    
    try:
        print("🔧 Starting database setup...")
        
        # Drop existing tables if they exist
        print("Dropping existing tables...")
        cursor.execute("DROP TABLE IF EXISTS participants CASCADE;")
        cursor.execute("DROP TABLE IF EXISTS conference_programs CASCADE;")
        cursor.execute("DROP TABLE IF EXISTS notifications CASCADE;")
        
        # Create participants table
        print("Creating participants table...")
        create_participants_sql = """
        CREATE TABLE participants (
            id SERIAL PRIMARY KEY,
            
            -- Personal information (required)
            name VARCHAR(150) NOT NULL,
            email VARCHAR(150) NOT NULL UNIQUE,
            
            -- Professional information (optional)
            organization VARCHAR(250),
            position VARCHAR(150),
            phone_number VARCHAR(20),
            
            -- Registration information
            registration_type VARCHAR(50) NOT NULL DEFAULT 'participant',
            registration_status VARCHAR(20) NOT NULL DEFAULT 'registered',
            registration_fee_paid BOOLEAN DEFAULT FALSE,
            payment_reference VARCHAR(100),
            
            -- Additional registration fields
            dietary_requirements TEXT,
            special_needs TEXT,
            emergency_contact_name VARCHAR(150),
            emergency_contact_phone VARCHAR(20),
            
            -- Notification preferences
            email_notifications BOOLEAN DEFAULT TRUE,
            sms_notifications BOOLEAN DEFAULT FALSE,
            push_notifications BOOLEAN DEFAULT TRUE,
            
            -- Certificate information
            cert_type VARCHAR(50) DEFAULT 'participation',
            cert_sent BOOLEAN DEFAULT FALSE,
            cert_sent_date TIMESTAMP,
            certificate_id VARCHAR(50) UNIQUE,
            
            -- Metadata
            date_registered TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            
            -- File upload path
            evidence_file_path VARCHAR(500)
        );
        """
        cursor.execute(create_participants_sql)
        
        # Create indexes for better performance
        print("Creating indexes...")
        cursor.execute("CREATE INDEX idx_participants_email ON participants(email);")
        cursor.execute("CREATE INDEX idx_participants_registration_type ON participants(registration_type);")
        cursor.execute("CREATE INDEX idx_participants_cert_sent ON participants(cert_sent);")
        cursor.execute("CREATE INDEX idx_participants_date_registered ON participants(date_registered);")
        
        # Create conference_programs table
        print("Creating conference_programs table...")
        create_programs_sql = """
        CREATE TABLE conference_programs (
            id SERIAL PRIMARY KEY,
            title VARCHAR(200) NOT NULL,
            description TEXT,
            start_datetime TIMESTAMP NOT NULL,
            end_datetime TIMESTAMP NOT NULL,
            location VARCHAR(150),
            speaker VARCHAR(150),
            session_type VARCHAR(50) DEFAULT 'presentation',
            capacity INTEGER DEFAULT 100,
            is_active BOOLEAN DEFAULT TRUE,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        """
        cursor.execute(create_programs_sql)
        
        # Create notifications table
        print("Creating notifications table...")
        create_notifications_sql = """
        CREATE TABLE notifications (
            id SERIAL PRIMARY KEY,
            title VARCHAR(150) NOT NULL,
            message TEXT NOT NULL,
            notification_type VARCHAR(50) DEFAULT 'info',
            target_audience VARCHAR(50) DEFAULT 'all',
            is_active BOOLEAN DEFAULT TRUE,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            expires_at TIMESTAMP
        );
        """
        cursor.execute(create_notifications_sql)
        
        # Create legacy participant table for backward compatibility
        print("Creating legacy participant table...")
        create_legacy_sql = """
        CREATE TABLE participant (
            id SERIAL PRIMARY KEY,
            name VARCHAR(100) NOT NULL,
            email VARCHAR(100) NOT NULL,
            role VARCHAR(50) DEFAULT 'Attendee',
            cert_type VARCHAR(50) DEFAULT 'participation',
            registration_number VARCHAR(50),
            phone VARCHAR(20),
            gender VARCHAR(10),
            specialty VARCHAR(100),
            state VARCHAR(50),
            hospital VARCHAR(100),
            cert_sent BOOLEAN DEFAULT FALSE,
            cert_sent_date TIMESTAMP,
            certificate_id VARCHAR(50),
            date_registered TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            registration_status VARCHAR(20) DEFAULT 'Pending',
            registration_fee_paid BOOLEAN DEFAULT FALSE
        );
        """
        cursor.execute(create_legacy_sql)
        
        # Commit all changes
        conn.commit()
        print("✅ All tables created successfully!")
        
        # Verify tables were created
        print("\n🔍 Verifying table creation...")
        cursor.execute("""
            SELECT table_name, 
                   (SELECT COUNT(*) FROM information_schema.columns WHERE table_name = t.table_name) as column_count
            FROM information_schema.tables t
            WHERE table_schema = 'public' 
            AND table_type = 'BASE TABLE'
            AND table_name IN ('participants', 'conference_programs', 'notifications', 'participant')
            ORDER BY table_name;
        """)
        
        tables = cursor.fetchall()
        if tables:
            print("Created tables:")
            for table_name, column_count in tables:
                print(f"  ✅ {table_name} ({column_count} columns)")
        else:
            print("❌ No tables found!")
            
        return True
        
    except Exception as e:
        print(f"❌ Error during database setup: {e}")
        conn.rollback()
        return False
    finally:
        cursor.close()

def main():
    """Main function to run the database setup"""
    print("🚀 MDCAN BDM 2025 - Digital Ocean Database Setup")
    print("=" * 50)
    
    # Connect to database
    conn = create_connection()
    if not conn:
        sys.exit(1)
    
    try:
        # Setup database
        success = setup_database(conn)
        
        if success:
            print("\n" + "=" * 50)
            print("✅ Database setup completed successfully!")
            print("The Digital Ocean backend should now work with registration.")
            print("Test registration at: https://mdcanbdm042-2025-tdlv8.ondigitalocean.app")
        else:
            print("\n" + "=" * 50)
            print("❌ Database setup failed!")
            sys.exit(1)
            
    finally:
        conn.close()
        print("🔐 Database connection closed.")

if __name__ == "__main__":
    main()
