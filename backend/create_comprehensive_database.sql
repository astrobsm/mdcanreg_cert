-- Comprehensive Database Creation Script for MDCAN BDM 2025 Certificate Platform
-- Created on August 5, 2025

-- Connect to PostgreSQL and create database if it doesn't exist
CREATE DATABASE IF NOT EXISTS mdcan042_db;

-- Connect to the database
\c mdcan042_db;

-- Enable UUID extension for certificate numbers
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Drop tables if they exist (for clean setup)
DROP TABLE IF EXISTS certificate_logs CASCADE;
DROP TABLE IF EXISTS session_registrations CASCADE;
DROP TABLE IF EXISTS notifications CASCADE;
DROP TABLE IF EXISTS conference_programs CASCADE;
DROP TABLE IF EXISTS participants CASCADE;
DROP TABLE IF EXISTS system_settings CASCADE;

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
    push_subscription TEXT,
    
    -- Certificate information
    certificate_type VARCHAR(30) NOT NULL DEFAULT 'participation',
    certificate_status VARCHAR(20) NOT NULL DEFAULT 'pending',
    certificate_number VARCHAR(50) UNIQUE,
    certificate_sent_at TIMESTAMP,
    
    -- Metadata
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    created_by VARCHAR(100) DEFAULT 'system',
    
    -- Additional fields for tracking
    registration_source VARCHAR(50) DEFAULT 'manual',
    event_attendance BOOLEAN DEFAULT TRUE,
    special_recognition TEXT,
    
    -- Constraints
    CONSTRAINT valid_certificate_type CHECK (certificate_type IN ('participation', 'service')),
    CONSTRAINT valid_certificate_status CHECK (certificate_status IN ('pending', 'sent', 'failed', 'resent')),
    CONSTRAINT valid_registration_type CHECK (registration_type IN ('participant', 'speaker', 'organizer', 'sponsor', 'volunteer')),
    CONSTRAINT valid_registration_status CHECK (registration_status IN ('registered', 'confirmed', 'attended', 'cancelled'))
);

-- Create conference_programs table
CREATE TABLE conference_programs (
    id SERIAL PRIMARY KEY,
    title VARCHAR(250) NOT NULL,
    description TEXT,
    program_type VARCHAR(50) NOT NULL,
    
    -- Scheduling
    start_time TIMESTAMP NOT NULL,
    end_time TIMESTAMP NOT NULL,
    venue VARCHAR(200),
    capacity INTEGER,
    
    -- Content details
    speaker_name VARCHAR(150),
    speaker_bio TEXT,
    speaker_photo_url VARCHAR(500),
    
    -- Program status
    status VARCHAR(20) NOT NULL DEFAULT 'scheduled',
    is_mandatory BOOLEAN DEFAULT FALSE,
    requires_registration BOOLEAN DEFAULT FALSE,
    
    -- Notification settings
    notification_sent BOOLEAN DEFAULT FALSE,
    reminder_minutes INTEGER DEFAULT 30,
    
    -- Metadata
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    created_by VARCHAR(100) DEFAULT 'admin',
    
    -- Constraints
    CONSTRAINT valid_program_type CHECK (program_type IN ('session', 'workshop', 'keynote', 'break', 'social', 'networking')),
    CONSTRAINT valid_program_status CHECK (status IN ('scheduled', 'ongoing', 'completed', 'cancelled'))
);

-- Create session_registrations table
CREATE TABLE session_registrations (
    id SERIAL PRIMARY KEY,
    participant_id INTEGER NOT NULL REFERENCES participants(id),
    program_id INTEGER NOT NULL REFERENCES conference_programs(id),
    
    -- Registration details
    registered_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    attendance_status VARCHAR(20) DEFAULT 'registered',
    
    -- Feedback (post-session)
    rating INTEGER,
    feedback TEXT,
    
    -- Constraints
    CONSTRAINT unique_participant_program UNIQUE (participant_id, program_id),
    CONSTRAINT valid_attendance_status CHECK (attendance_status IN ('registered', 'attended', 'absent', 'cancelled')),
    CONSTRAINT valid_rating CHECK (rating BETWEEN 1 AND 5)
);

-- Create notifications table
CREATE TABLE notifications (
    id SERIAL PRIMARY KEY,
    
    -- Notification content
    title VARCHAR(200) NOT NULL,
    message TEXT NOT NULL,
    notification_type VARCHAR(50) NOT NULL,
    
    -- Targeting
    target_audience VARCHAR(50) DEFAULT 'all',
    target_program_id INTEGER REFERENCES conference_programs(id),
    
    -- Scheduling
    scheduled_time TIMESTAMP NOT NULL,
    sent_at TIMESTAMP,
    
    -- Delivery channels
    send_email BOOLEAN DEFAULT TRUE,
    send_push BOOLEAN DEFAULT TRUE,
    send_sms BOOLEAN DEFAULT FALSE,
    
    -- Status
    status VARCHAR(20) DEFAULT 'scheduled',
    delivery_stats TEXT,
    
    -- Metadata
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    created_by VARCHAR(100) DEFAULT 'admin',
    
    -- Constraints
    CONSTRAINT valid_notification_type CHECK (notification_type IN ('program_reminder', 'general_announcement', 'emergency', 'welcome', 'certificate_ready')),
    CONSTRAINT valid_target_audience CHECK (target_audience IN ('all', 'participants', 'speakers', 'organizers', 'specific_program')),
    CONSTRAINT valid_notification_status CHECK (status IN ('scheduled', 'sent', 'failed', 'cancelled'))
);

-- Create certificate_logs table
CREATE TABLE certificate_logs (
    id SERIAL PRIMARY KEY,
    participant_id INTEGER NOT NULL REFERENCES participants(id),
    action VARCHAR(50) NOT NULL,
    status VARCHAR(20) NOT NULL,
    error_message TEXT,
    email_subject VARCHAR(200),
    email_body_preview TEXT,
    timestamp TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    ip_address VARCHAR(45),
    user_agent VARCHAR(500)
);

-- Create system_settings table
CREATE TABLE system_settings (
    id SERIAL PRIMARY KEY,
    key VARCHAR(100) NOT NULL UNIQUE,
    value TEXT,
    description VARCHAR(500),
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- Create indexes for better performance
-- Participants table indexes
CREATE INDEX idx_participants_name ON participants(name);
CREATE INDEX idx_participants_email ON participants(email);
CREATE INDEX idx_participants_certificate_type ON participants(certificate_type);
CREATE INDEX idx_participants_certificate_status ON participants(certificate_status);
CREATE INDEX idx_participants_created_at ON participants(created_at);
CREATE INDEX idx_participants_registration_type ON participants(registration_type);
CREATE INDEX idx_participants_registration_status ON participants(registration_status);
CREATE INDEX idx_participants_email_status ON participants(email, certificate_status);
CREATE INDEX idx_participants_created_type ON participants(created_at, certificate_type);
CREATE INDEX idx_participants_registration_type_status ON participants(registration_type, registration_status);

-- Conference programs table indexes
CREATE INDEX idx_conference_programs_title ON conference_programs(title);
CREATE INDEX idx_conference_programs_program_type ON conference_programs(program_type);
CREATE INDEX idx_conference_programs_start_time ON conference_programs(start_time);
CREATE INDEX idx_conference_programs_end_time ON conference_programs(end_time);
CREATE INDEX idx_conference_programs_status ON conference_programs(status);
CREATE INDEX idx_conference_programs_start_time_type ON conference_programs(start_time, program_type);
CREATE INDEX idx_conference_programs_status_mandatory ON conference_programs(status, is_mandatory);

-- Session registrations table indexes
CREATE INDEX idx_session_registrations_participant_id ON session_registrations(participant_id);
CREATE INDEX idx_session_registrations_program_id ON session_registrations(program_id);
CREATE INDEX idx_session_registrations_attendance_status ON session_registrations(attendance_status);
CREATE INDEX idx_session_registrations_participant_program ON session_registrations(participant_id, program_id);

-- Notifications table indexes
CREATE INDEX idx_notifications_notification_type ON notifications(notification_type);
CREATE INDEX idx_notifications_scheduled_time ON notifications(scheduled_time);
CREATE INDEX idx_notifications_sent_at ON notifications(sent_at);
CREATE INDEX idx_notifications_status ON notifications(status);
CREATE INDEX idx_notifications_target_audience ON notifications(target_audience);

-- Certificate logs table indexes
CREATE INDEX idx_certificate_logs_participant_id ON certificate_logs(participant_id);
CREATE INDEX idx_certificate_logs_timestamp ON certificate_logs(timestamp);
CREATE INDEX idx_certificate_logs_action_status ON certificate_logs(action, status);

-- System settings table indexes
CREATE INDEX idx_system_settings_key ON system_settings(key);

-- Insert default system settings
INSERT INTO system_settings (key, value, description) VALUES
('email_enabled', 'true', 'Enable/disable email sending'),
('certificate_template_version', '1.0', 'Current certificate template version'),
('max_bulk_upload_size', '1000', 'Maximum number of records in bulk upload'),
('conference_name', 'MDCAN BDM 14th – 2025', 'Conference name for certificates'),
('conference_date', 'September 1st – 6th, 2025', 'Conference date for certificates'),
('conference_location', 'Enugu', 'Conference location for certificates'),
('certificate_signature_president', 'Prof. Aminu Mohammed', 'Name of MDCAN President for signature'),
('certificate_signature_chairman', 'Prof. Appolos Ndukuba', 'Name of LOC Chairman for signature'),
('registration_early_bird_end_date', '2025-07-15', 'Early bird registration end date'),
('registration_regular_end_date', '2025-08-15', 'Regular registration end date'),
('registration_fee_early_bird', '30000', 'Early bird registration fee'),
('registration_fee_regular', '50000', 'Regular registration fee'),
('registration_fee_late', '70000', 'Late registration fee'),
('program_display_days', '7', 'Number of days to display in program schedule')
ON CONFLICT (key) DO UPDATE SET 
    value = EXCLUDED.value,
    description = EXCLUDED.description,
    updated_at = CURRENT_TIMESTAMP;

-- Create a function to automatically update the updated_at timestamp
CREATE OR REPLACE FUNCTION update_modified_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Create triggers to automatically update the updated_at timestamp
CREATE TRIGGER update_participants_modtime
    BEFORE UPDATE ON participants
    FOR EACH ROW
    EXECUTE FUNCTION update_modified_column();

CREATE TRIGGER update_conference_programs_modtime
    BEFORE UPDATE ON conference_programs
    FOR EACH ROW
    EXECUTE FUNCTION update_modified_column();

CREATE TRIGGER update_system_settings_modtime
    BEFORE UPDATE ON system_settings
    FOR EACH ROW
    EXECUTE FUNCTION update_modified_column();

-- Grant permissions
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO postgres;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO postgres;

-- Analyze tables for better query optimization
ANALYZE;
