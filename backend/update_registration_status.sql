-- More comprehensive update of registration_status column
-- This will ensure existing participants have the correct status based on payment status

-- Make sure column exists with non-null constraint
ALTER TABLE participants 
  ALTER COLUMN registration_status SET NOT NULL,
  ALTER COLUMN registration_status SET DEFAULT 'pending';

-- Update registration status based on payment status
UPDATE participants 
SET registration_status = 
  CASE 
    WHEN registration_fee_paid = true THEN 'confirmed'
    ELSE 'pending'
  END
WHERE registration_status = 'registered' OR registration_status IS NULL;

-- Set special status for speakers and organizers
UPDATE participants
SET registration_status = 'confirmed'
WHERE registration_type IN ('speaker', 'organizer', 'sponsor', 'staff');
