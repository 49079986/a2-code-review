-- Create a composite index with event_type as the leading column.
CREATE INDEX IDX_EVENT_TYPE_TIME
ON BOOKING_EVENTS (event_type, event_time);
