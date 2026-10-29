-- Execute the labelled sections in order in two independent connections.
-- Do not execute this entire file in a single connection.
-- The deadlock victim may differ on a rerun.

-- Connection 1: record the initial odometers.
SELECT vehicle_id, odometer
FROM VEHICLES
WHERE vehicle_id IN ('VEH-0401', 'VEH-0501')
ORDER BY vehicle_id;

-- Connection 1: begin and update the first vehicle.
BEGIN;
UPDATE VEHICLES
SET odometer = odometer + 10
WHERE vehicle_id = 'VEH-0401'
RETURNING vehicle_id, odometer;

-- Connection 2: begin and update the other vehicle first.
BEGIN;
UPDATE VEHICLES
SET odometer = odometer + 20
WHERE vehicle_id = 'VEH-0501'
RETURNING vehicle_id, odometer;

-- Connection 1: this statement waits for Connection 2.
UPDATE VEHICLES
SET odometer = odometer + 10
WHERE vehicle_id = 'VEH-0501'
RETURNING vehicle_id, odometer;

-- Connection 2: this statement completes the wait-for cycle.
UPDATE VEHICLES
SET odometer = odometer + 20
WHERE vehicle_id = 'VEH-0401'
RETURNING vehicle_id, odometer;

-- Connection 2: COMMIT reported ROLLBACK in the recorded run.
COMMIT;

-- Connection 1: commit and report the final odometers.
COMMIT;
SELECT vehicle_id, odometer
FROM VEHICLES
WHERE vehicle_id IN ('VEH-0401', 'VEH-0501')
ORDER BY vehicle_id;
