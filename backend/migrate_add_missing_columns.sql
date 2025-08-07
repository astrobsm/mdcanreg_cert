-- Add missing columns to participants table
ALTER TABLE participants ADD COLUMN IF NOT EXISTS first_attendance_date TIMESTAMP;
ALTER TABLE participants ADD COLUMN IF NOT EXISTS last_attendance_date TIMESTAMP;
ALTER TABLE participants ADD COLUMN IF NOT EXISTS materials_provided BOOLEAN DEFAULT FALSE;
ALTER TABLE participants ADD COLUMN IF NOT EXISTS materials_provided_date TIMESTAMP;
ALTER TABLE participants ADD COLUMN IF NOT EXISTS materials_provided_by VARCHAR(255);
