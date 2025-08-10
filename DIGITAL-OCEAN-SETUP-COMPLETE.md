# Digital Ocean Database Setup - Complete Solution

## Issue Summary
The Digital Ocean backend deployment needs database tables created, but the application user `mdcanconfreg` lacks CREATE TABLE permissions in the managed PostgreSQL database.

## Solution Options

### Option 1: Database Console Setup (Recommended)
Access your Digital Ocean database console and run this SQL:

```sql
-- Create the main participant table
CREATE TABLE IF NOT EXISTS participant (
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

-- Create additional tables for full functionality
CREATE TABLE IF NOT EXISTS participants (
    id SERIAL PRIMARY KEY,
    name VARCHAR(150) NOT NULL,
    email VARCHAR(150) NOT NULL UNIQUE,
    organization VARCHAR(250),
    position VARCHAR(150),
    phone_number VARCHAR(20),
    registration_type VARCHAR(50) NOT NULL DEFAULT 'participant',
    registration_status VARCHAR(20) NOT NULL DEFAULT 'registered',
    registration_fee_paid BOOLEAN DEFAULT FALSE,
    payment_reference VARCHAR(100),
    dietary_requirements TEXT,
    special_needs TEXT,
    emergency_contact_name VARCHAR(150),
    emergency_contact_phone VARCHAR(20),
    email_notifications BOOLEAN DEFAULT TRUE,
    sms_notifications BOOLEAN DEFAULT FALSE,
    push_notifications BOOLEAN DEFAULT TRUE,
    cert_type VARCHAR(50) DEFAULT 'participation',
    cert_sent BOOLEAN DEFAULT FALSE,
    cert_sent_date TIMESTAMP,
    certificate_id VARCHAR(50) UNIQUE,
    date_registered TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    evidence_file_path VARCHAR(500)
);

-- Grant permissions to application user
GRANT SELECT, INSERT, UPDATE, DELETE ON participant TO mdcanconfreg;
GRANT USAGE, SELECT ON SEQUENCE participant_id_seq TO mdcanconfreg;
GRANT SELECT, INSERT, UPDATE, DELETE ON participants TO mdcanconfreg;
GRANT USAGE, SELECT ON SEQUENCE participants_id_seq TO mdcanconfreg;
```

### Option 2: Production Endpoint (When Deployment Completes)
Once the latest deployment is live, use this endpoint:

```powershell
Invoke-WebRequest -Uri "https://mdcanbdm042-2025-tdlv8.ondigitalocean.app/api/setup-production" -Method POST -Body @{secret="mdcansetup2025"} -ContentType "application/x-www-form-urlencoded"
```

### Option 3: Direct Database Connection
If you have the correct hostname, use the setup script with proper connection details.

## Database Connection Details
- Database: `defaultdb`
- User: `mdcanconfreg`
- Password: `[REDACTED - See Digital Ocean Database Console]`
- Port: `25060`
- SSL Mode: `require`

## Current Status
✅ **Backend Code**: Updated with `/api/register` endpoint  
✅ **Frontend Config**: Points to Digital Ocean backend  
⏳ **Deployment**: Latest code is being deployed  
❌ **Database Tables**: Need manual creation  

## Testing After Setup
Once tables are created, test registration:

```powershell
# Test the register endpoint
Invoke-WebRequest -Uri "https://mdcanbdm042-2025-tdlv8.ondigitalocean.app/api/register" -Method POST -Body @{
    name="John Doe"
    email="john@example.com"
    phone="08012345678"
    organization="Test Hospital"
} -ContentType "application/x-www-form-urlencoded"

# Check if participant was created
Invoke-WebRequest -Uri "https://mdcanbdm042-2025-tdlv8.ondigitalocean.app/api/participants" -Method GET
```

## Next Steps
1. **Create database tables** using Option 1 (recommended)
2. **Wait for deployment** to complete (5-10 minutes)
3. **Test registration** using the frontend or API
4. **Verify certificate generation** works properly

The platform will be fully operational once the database tables are created!
