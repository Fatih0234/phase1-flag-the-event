-- Migration: Add bike classification columns to events table
-- Date: 2026-01-16
-- Description: Adds columns to store bike event classification results from LLM

-- Add bike classification columns
ALTER TABLE events ADD COLUMN IF NOT EXISTS bike_related BOOLEAN;
ALTER TABLE events ADD COLUMN IF NOT EXISTS bike_confidence DECIMAL(3,2);
ALTER TABLE events ADD COLUMN IF NOT EXISTS bike_evidence TEXT[];
ALTER TABLE events ADD COLUMN IF NOT EXISTS bike_reasoning TEXT;

-- Create index for efficient querying of bike-related events
CREATE INDEX IF NOT EXISTS idx_events_bike_related ON events(bike_related) WHERE bike_related IS TRUE;

-- Create index for querying uncertain events (NULL bike_related)
CREATE INDEX IF NOT EXISTS idx_events_bike_uncertain ON events(bike_related) WHERE bike_related IS NULL;

-- Add comments for documentation
COMMENT ON COLUMN events.bike_related IS 'TRUE if bike-related, FALSE if not, NULL if uncertain or not classified';
COMMENT ON COLUMN events.bike_confidence IS 'Confidence score from LLM (0.0-1.0)';
COMMENT ON COLUMN events.bike_evidence IS 'Array of evidence quotes from event description';
COMMENT ON COLUMN events.bike_reasoning IS 'LLM reasoning for classification';
