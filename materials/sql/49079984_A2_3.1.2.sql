-- Report the execution plan for Statement A.
EXPLAIN (ANALYZE, BUFFERS)
SELECT v.vehicle_id
FROM VEHICLES v
WHERE NOT EXISTS (
    SELECT 1
    FROM BOOKING_EVENTS e
    WHERE e.vehicle_id = v.vehicle_id
      AND e.event_type = 'Collect'
)
ORDER BY v.vehicle_id;

-- Report the execution plan for Statement B.
EXPLAIN (ANALYZE, BUFFERS)
SELECT v.vehicle_id
FROM VEHICLES v
LEFT JOIN BOOKING_EVENTS e
    ON e.vehicle_id = v.vehicle_id
   AND e.event_type = 'Collect'
WHERE e.vehicle_id IS NULL
ORDER BY v.vehicle_id;
