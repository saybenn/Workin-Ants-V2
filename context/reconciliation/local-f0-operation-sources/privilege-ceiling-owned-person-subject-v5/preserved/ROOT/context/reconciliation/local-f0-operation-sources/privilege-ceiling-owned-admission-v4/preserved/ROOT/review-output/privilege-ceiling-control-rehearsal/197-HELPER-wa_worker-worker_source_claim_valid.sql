BEGIN;
SELECT platform_private.worker_source_claim_valid('CustomerProfile','{}'::jsonb);
ROLLBACK;
