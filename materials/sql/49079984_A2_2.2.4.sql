-- Index the same normalized domain expression used in the queries.
CREATE INDEX IDX_MEMBER_DOMAIN
ON MEMBERS (LOWER(SPLIT_PART(email, '@', 2)));
