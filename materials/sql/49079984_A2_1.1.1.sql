CREATE VIEW V_BUSIEST_BAYS AS
WITH collection_counts AS (
    SELECT
        m.body_type,
        s.station_id,
        s.station_name,
        COUNT(*) AS collections
    FROM BOOKING_EVENTS e
    JOIN VEHICLES v
        ON v.vehicle_id = e.vehicle_id
    JOIN MODELS m
        ON m.model_code = v.model_code
    JOIN STATIONS s
        ON s.station_id = v.station_id
    WHERE e.event_type = 'Collect'
    GROUP BY
        m.body_type,
        s.station_id,
        s.station_name
),
ranked_stations AS (
    SELECT *,
        ROW_NUMBER() OVER (
            PARTITION BY body_type
            ORDER BY collections DESC, station_id
        ) AS rn
    FROM collection_counts
)
SELECT body_type, station_name, collections
FROM ranked_stations
WHERE rn = 1
ORDER BY collections DESC, body_type;