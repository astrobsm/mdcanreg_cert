-- MDCAN BDM 2025 Certificate Platform Database Setup
-- Run this script in Digital Ocean Database Console
-- This creates all required tables for the certificate platform

-- Drop existing tables if they exist (for clean setup)
DROP TABLE IF EXISTS participants CASCADE;

-- Create participants table
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

-- Create indexes for better performance
CREATE INDEX idx_participants_email ON participants(email);
CREATE INDEX idx_participants_registration_type ON participants(registration_type);
CREATE INDEX idx_participants_cert_sent ON participants(cert_sent);
CREATE INDEX idx_participants_date_registered ON participants(date_registered);

-- Grant necessary permissions to mdcanconfreg user
GRANT SELECT, INSERT, UPDATE, DELETE ON participants TO mdcanconfreg;
GRANT USAGE, SELECT ON SEQUENCE participants_id_seq TO mdcanconfreg;

-- Create conference_programs table (for program management)
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

-- Grant permissions for conference_programs
GRANT SELECT, INSERT, UPDATE, DELETE ON conference_programs TO mdcanconfreg;
GRANT USAGE, SELECT ON SEQUENCE conference_programs_id_seq TO mdcanconfreg;

-- Create notifications table (for system notifications)
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

-- Grant permissions for notifications
GRANT SELECT, INSERT, UPDATE, DELETE ON notifications TO mdcanconfreg;
GRANT USAGE, SELECT ON SEQUENCE notifications_id_seq TO mdcanconfreg;

-- Verify tables were created successfully
SELECT 
    table_name,
    (SELECT COUNT(*) FROM information_schema.columns WHERE table_name = t.table_name) as column_count
FROM information_schema.tables t
WHERE table_schema = 'public' 
AND table_type = 'BASE TABLE'
AND table_name IN ('participants', 'conference_programs', 'notifications')
ORDER BY table_name;
