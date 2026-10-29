-- Query A: retrieve the ordinary view results.
SELECT * FROM V_ACCOUNT_LIABILITY;

-- Query A: report the ordinary view execution plan.
EXPLAIN (ANALYZE, BUFFERS)
SELECT * FROM V_ACCOUNT_LIABILITY;

-- Query B: retrieve the materialized view results.
SELECT * FROM MV_ACCOUNT_LIABILITY;

-- Query B: report the materialized view execution plan.
EXPLAIN (ANALYZE, BUFFERS)
SELECT * FROM MV_ACCOUNT_LIABILITY;
