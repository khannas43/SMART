-- Fix application_events table
-- Run this if the table was not created due to syntax error

-- Drop table if exists (to recreate)
DROP TABLE IF EXISTS application.application_events CASCADE;

-- Create application_events table
CREATE TABLE application.application_events (
    event_id BIGSERIAL PRIMARY KEY,
    application_id INTEGER REFERENCES application.applications(application_id) ON DELETE CASCADE,
    
    -- Event Details
    event_type VARCHAR(100) NOT NULL,
    -- APPLICATION_DRAFT_CREATED, APPLICATION_SUBMITTED, APPLICATION_REJECTED_BY_DEPT_VALIDATION,
    -- APPLICATION_ACCEPTED_BY_DEPT, APPLICATION_STATUS_UPDATED, etc.
    
    event_data JSONB NOT NULL, -- Event payload
    event_status VARCHAR(50) DEFAULT 'pending', -- pending, published, failed
    
    -- Timestamps
    event_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,
    published_at TIMESTAMP,
    
    -- Consumer Tracking (optional, for event streaming)
    consumed_by TEXT[] -- List of consumer IDs that have processed this event
);

-- Create indexes
CREATE INDEX idx_app_events_type ON application.application_events(event_type);
CREATE INDEX idx_app_events_application ON application.application_events(application_id);
CREATE INDEX idx_app_events_timestamp ON application.application_events(event_timestamp);
CREATE INDEX idx_app_events_status ON application.application_events(event_status) WHERE event_status = 'pending';

-- Add comment
COMMENT ON TABLE application.application_events IS 'Event log for downstream integration';

