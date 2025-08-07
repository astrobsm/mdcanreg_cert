-- Create participants table
CREATE TABLE IF NOT EXISTS participants (
    id SERIAL PRIMARY KEY,
    name VARCHAR(150) NOT NULL,
    email VARCHAR(150) NOT NULL UNIQUE,
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
    CONSTRAINT valid_registration_type CHECK (registration_type IN ('participant', 'speaker', 'organizer', 'sponsor')),
    CONSTRAINT valid_registration_status CHECK (registration_status IN ('registered', 'confirmed', 'attended', 'cancelled'))
);

-- Indexes for participants table
CREATE INDEX IF NOT EXISTS idx_participants_name ON participants(name);
CREATE INDEX IF NOT EXISTS idx_participants_email ON participants(email);
CREATE INDEX IF NOT EXISTS idx_participants_certificate_type ON participants(certificate_type);
CREATE INDEX IF NOT EXISTS idx_participants_certificate_status ON participants(certificate_status);
CREATE INDEX IF NOT EXISTS idx_participants_created_at ON participants(created_at);
CREATE INDEX IF NOT EXISTS idx_participants_registration_type ON participants(registration_type);
CREATE INDEX IF NOT EXISTS idx_participants_registration_status ON participants(registration_status);
