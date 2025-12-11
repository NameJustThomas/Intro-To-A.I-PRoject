-- Add location fields for GPS tracking
-- Created: 2025-12-04

-- Add latitude and longitude to stores
ALTER TABLE stores 
ADD COLUMN IF NOT EXISTS latitude FLOAT,
ADD COLUMN IF NOT EXISTS longitude FLOAT;

-- Add latitude and longitude to attendance_logs
ALTER TABLE attendance_logs 
ADD COLUMN IF NOT EXISTS latitude FLOAT,
ADD COLUMN IF NOT EXISTS longitude FLOAT,
ADD COLUMN IF NOT EXISTS location_validated BOOLEAN DEFAULT false,
ADD COLUMN IF NOT EXISTS distance_from_store FLOAT;

