-- Connection 1: use the original open transaction after Connection 2 commits.
-- Do not reconnect or start a new transaction before running these statements.
\set ON_ERROR_STOP off

-- Attempt to collect the same vehicle for a different member.
INSERT INTO BOOKING_EVENTS
    (member_id, vehicle_id, event_type, event_time, amount)
VALUES
    (1, 'VEH-0004', 'Collect', NOW(), NULL);

-- After the expected trigger error, COMMIT ends the failed transaction as ROLLBACK.
COMMIT;

-- Check the latest recorded events after the transaction has ended.
SELECT event_id, member_id, vehicle_id, event_type, event_time, amount
FROM BOOKING_EVENTS
WHERE vehicle_id = 'VEH-0004'
ORDER BY event_time DESC, event_id DESC
LIMIT 3;
