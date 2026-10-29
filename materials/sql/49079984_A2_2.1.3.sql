-- Count incidents and sum their charges for March 2026.
SELECT COUNT(*), SUM(amount)
FROM BOOKING_EVENTS
WHERE event_type = 'Incident'
  AND event_time >= TIMESTAMP '2026-03-01'
  AND event_time < TIMESTAMP '2026-04-01';

-- Report the execution plan for the March incidents query.
EXPLAIN (ANALYZE, BUFFERS)
SELECT COUNT(*), SUM(amount)
FROM BOOKING_EVENTS
WHERE event_type = 'Incident'
  AND event_time >= TIMESTAMP '2026-03-01'
  AND event_time < TIMESTAMP '2026-04-01';
