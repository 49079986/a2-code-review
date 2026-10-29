-- Retrieve the busiest station for each body type after creating the index.
SELECT * FROM V_BUSIEST_BAYS;

-- Compare this plan with the plan recorded in Q1.1 before creating the index.
EXPLAIN (ANALYZE, BUFFERS)
SELECT * FROM V_BUSIEST_BAYS;
