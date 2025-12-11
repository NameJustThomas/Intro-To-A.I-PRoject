-- Fix is_on_time column type from boolean to integer
-- Created: 2025-12-11

-- Drop default first
ALTER TABLE attendance_logs ALTER COLUMN is_on_time DROP DEFAULT;

-- Convert boolean to integer (true -> 1, false -> 0)
ALTER TABLE attendance_logs ALTER COLUMN is_on_time TYPE INTEGER USING CASE WHEN is_on_time THEN 1 ELSE 0 END;

-- Set default back
ALTER TABLE attendance_logs ALTER COLUMN is_on_time SET DEFAULT 1;

