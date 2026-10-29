-- Run every section in the same Query Tool connection.
-- Keep IDX_EVENT_TYPE_TIME from Q2.1 in place.

-- Setting 1: allow index, index-only, bitmap, and sequential scans.
SET enable_indexscan = on;
SET enable_indexonlyscan = on;
SET enable_bitmapscan = on;
SET enable_seqscan = on;

-- Plan C1: Query C under Setting 1.
EXPLAIN (ANALYZE, BUFFERS)
SELECT * FROM BOOKING_EVENTS WHERE event_type < 'Collect';

-- Plan D1: Query D under Setting 1.
EXPLAIN (ANALYZE, BUFFERS)
SELECT * FROM BOOKING_EVENTS WHERE event_type >= 'Collect';

-- Setting 2: allow index access and suppress sequential scans.
SET enable_indexscan = on;
SET enable_indexonlyscan = on;
SET enable_bitmapscan = on;
SET enable_seqscan = off;

-- Plan C2: Query C under Setting 2.
EXPLAIN (ANALYZE, BUFFERS)
SELECT * FROM BOOKING_EVENTS WHERE event_type < 'Collect';

-- Plan D2: Query D under Setting 2.
EXPLAIN (ANALYZE, BUFFERS)
SELECT * FROM BOOKING_EVENTS WHERE event_type >= 'Collect';

-- Setting 3: suppress all three index access types and allow sequential scans.
SET enable_indexscan = off;
SET enable_indexonlyscan = off;
SET enable_bitmapscan = off;
SET enable_seqscan = on;

-- Plan C3: Query C under Setting 3.
EXPLAIN (ANALYZE, BUFFERS)
SELECT * FROM BOOKING_EVENTS WHERE event_type < 'Collect';

-- Plan D3: Query D under Setting 3.
EXPLAIN (ANALYZE, BUFFERS)
SELECT * FROM BOOKING_EVENTS WHERE event_type >= 'Collect';

-- Restore all four scan settings before proceeding to another question.
SET enable_indexscan = on;
SET enable_indexonlyscan = on;
SET enable_bitmapscan = on;
SET enable_seqscan = on;
