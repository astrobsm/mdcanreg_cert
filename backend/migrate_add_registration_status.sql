-- Migration: Add registration_status column to participants table
ALTER TABLE participants ADD COLUMN IF NOT EXISTS registration_status VARCHAR(50);
