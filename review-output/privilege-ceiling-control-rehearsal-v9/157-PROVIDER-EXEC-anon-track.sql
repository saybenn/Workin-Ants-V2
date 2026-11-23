BEGIN;
SELECT platform_private.worker_lease_valid(NULL::uuid,NULL::uuid,false);
ROLLBACK;