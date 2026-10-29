-- Report the domain-count query plan after creating the expression index.
EXPLAIN (ANALYZE, BUFFERS)
SELECT LOWER(SPLIT_PART(email, '@', 2)) AS provider_domain,
       COUNT(*) AS member_count
FROM MEMBERS
GROUP BY LOWER(SPLIT_PART(email, '@', 2))
ORDER BY member_count DESC, provider_domain;

-- Report the selective lookup plan for a rare provider domain.
EXPLAIN (ANALYZE, BUFFERS)
SELECT member_id, member_name, email
FROM MEMBERS
WHERE LOWER(SPLIT_PART(email, '@', 2)) = 'exemail.com.au';
