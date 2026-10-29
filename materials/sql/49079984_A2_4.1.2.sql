-- Connection 2: run this file while Connection 1 remains in its open transaction.
\set ECHO all
\connect assignment2
\pset pager off
\timing on

-- Identify the independent connection used for the reservation.
SELECT pg_backend_pid() AS session_pid,
       current_database() AS database_name;

BEGIN;
SHOW transaction_isolation;

-- Check the same vehicle selected by Connection 1.
SELECT *
FROM (
    SELECT vehicle_id, event_id, member_id, event_type, event_time
    FROM BOOKING_EVENTS
    WHERE vehicle_id = 'VEH-0004'
    ORDER BY event_time DESC, event_id DESC
    LIMIT 1
) AS latest_event
WHERE event_type = 'Return';

-- Reserve the vehicle for member 2 three days in the future.
INSERT INTO BOOKING_EVENTS
    (member_id, vehicle_id, event_type, event_time, amount)
VALUES
    (2, 'VEH-0004', 'Reserve', NOW() + INTERVAL '3 days', NULL)
RETURNING event_id, member_id, vehicle_id, event_type, event_time;

COMMIT;

-- Return to Connection 1 only after this COMMIT succeeds.
