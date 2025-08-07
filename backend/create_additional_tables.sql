-- Create certificate_logs table
CREATE TABLE IF NOT EXISTS certificate_logs (
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
CREATE INDEX IF NOT EXISTS idx_certificate_logs_participant_id ON certificate_logs(participant_id);
CREATE INDEX IF NOT EXISTS idx_certificate_logs_timestamp ON certificate_logs(timestamp);

-- Create system_settings table
CREATE TABLE IF NOT EXISTS system_settings (
    id SERIAL PRIMARY KEY,
    key VARCHAR(100) NOT NULL UNIQUE,
    value TEXT,
    description VARCHAR(500),
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- Index for system_settings table
CREATE INDEX IF NOT EXISTS idx_system_settings_key ON system_settings(key);

-- Insert default system settings
INSERT INTO system_settings (key, value, description) VALUES
('email_enabled', 'true', 'Enable/disable email sending'),
('certificate_template_version', '1.0', 'Current certificate template version'),
('max_bulk_upload_size', '1000', 'Maximum number of records in bulk upload'),
('conference_name', 'MDCAN BDM 14th – 2025', 'Conference name for certificates'),
('conference_date', 'September 1st – 6th, 2025', 'Conference date for certificates'),
('conference_location', 'Enugu', 'Conference location for certificates'),
('certificate_signature_president', 'Prof. Aminu Mohammed', 'Name of MDCAN President for signature'),
('certificate_signature_chairman', 'Prof. Appolos Ndukuba', 'Name of LOC Chairman for signature')
ON CONFLICT (key) DO NOTHING;
