-- Connection 1: keep this connection and its transaction open after this file.
\set ECHO all
\pset pager off
\timing on

-- Identify the connection used for this experiment.
SELECT pg_backend_pid() AS session_pid,
       current_database() AS database_name;

BEGIN;
SAVEPOINT collect_attempt;
SHOW transaction_isolation;

-- Find each vehicle's latest event before checking whether it is a Return.
WITH latest_events AS (
    SELECT DISTINCT ON (vehicle_id)
        vehicle_id, event_id, member_id, event_type, event_time
    FROM BOOKING_EVENTS
    ORDER BY vehicle_id, event_time DESC, event_id DESC
)
SELECT vehicle_id, event_id, member_id, event_type, event_time
FROM latest_events
WHERE vehicle_id = 'VEH-0004'
  AND event_type = 'Return'
ORDER BY vehicle_id
LIMIT 1;

-- The availability check is fixed to the vehicle selected in the recorded run.
-- Leave this transaction open.
-- Continue with Q4.1 (2) in Connection 2 before returning to Connection 1.
