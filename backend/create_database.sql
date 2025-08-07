-- MDCAN BDM 2025 Certificate Platform Database Creation Script
-- PostgreSQL Database: bdmcertificate_db
-- User: postgres
-- Password: natiss_natiss

-- Connect to PostgreSQL as superuser and create database
-- Run this with: psql -U postgres -h localhost

-- Create database
CREATE DATABASE bdmcertificate_db
    WITH 
    OWNER = postgres
    ENCODING = 'UTF8'
    LC_COLLATE = 'English_United States.1252'
    LC_CTYPE = 'English_United States.1252'
    TABLESPACE = pg_default
    CONNECTION LIMIT = -1;

-- Grant privileges
GRANT ALL ON DATABASE bdmcertificate_db TO postgres;

-- Connect to the new database
\c bdmcertificate_db;

-- Create extensions if needed
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- The tables will be created automatically by SQLAlchemy when the Flask app runs
-- But here's the equivalent SQL for reference:

/*
-- Participants table
CREATE TABLE participants (
    id SERIAL PRIMARY KEY,
    name VARCHAR(150) NOT NULL,
    email VARCHAR(150) NOT NULL UNIQUE,
    organization VARCHAR(250),
    position VARCHAR(150),
    phone_number VARCHAR(20),
    certificate_type VARCHAR(30) NOT NULL DEFAULT 'participation',
    certificate_status VARCHAR(20) NOT NULL DEFAULT 'pending',
    certificate_number VARCHAR(50) UNIQUE,
    certificate_sent_at TIMESTAMP,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    created_by VARCHAR(100) DEFAULT 'system',
    registration_source VARCHAR(50) DEFAULT 'manual',
    event_attendance BOOLEAN DEFAULT TRUE,
    special_recognition TEXT,
    
    CONSTRAINT valid_certificate_type CHECK (certificate_type IN ('participation', 'service')),
    CONSTRAINT valid_certificate_status CHECK (certificate_status IN ('pending', 'sent', 'failed', 'resent'))
);

-- Indexes for participants table
CREATE INDEX idx_participants_name ON participants(name);
CREATE INDEX idx_participants_email ON participants(email);
CREATE INDEX idx_participants_certificate_type ON participants(certificate_type);
CREATE INDEX idx_participants_certificate_status ON participants(certificate_status);
CREATE INDEX idx_participants_created_at ON participants(created_at);
CREATE INDEX idx_participants_email_status ON participants(email, certificate_status);
CREATE INDEX idx_participants_created_type ON participants(created_at, certificate_type);

-- Certificate logs table
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

-- Indexes for certificate_logs table
CREATE INDEX idx_certificate_logs_participant_id ON certificate_logs(participant_id);
CREATE INDEX idx_certificate_logs_timestamp ON certificate_logs(timestamp);

-- System settings table
CREATE TABLE system_settings (
    id SERIAL PRIMARY KEY,
    key VARCHAR(100) NOT NULL UNIQUE,
    value TEXT,
    description VARCHAR(500),
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- Index for system_settings table
CREATE INDEX idx_system_settings_key ON system_settings(key);

-- Insert default system settings
INSERT INTO system_settings (key, value, description) VALUES
('email_enabled', 'true', 'Enable/disable email sending'),
('certificate_template_version', '1.0', 'Current certificate template version'),
('max_bulk_upload_size', '1000', 'Maximum number of records in bulk upload'),
('conference_name', 'MDCAN BDM 14th – 2025', 'Conference name for certificates'),
('conference_date', '1st – 6th September, 2025', 'Conference date for certificates'),
('conference_location', 'Enugu', 'Conference location'),
('president_name', 'Prof. Aminu Mohammed', 'MDCAN President name'),
('chairman_name', 'Prof. Appolos Ndukuba', 'LOC Chairman name');
*/

-- Create a function to update the updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

-- This trigger will be applied automatically by SQLAlchemy
-- CREATE TRIGGER update_participants_updated_at BEFORE UPDATE ON participants FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
-- CREATE TRIGGER update_system_settings_updated_at BEFORE UPDATE ON system_settings FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
