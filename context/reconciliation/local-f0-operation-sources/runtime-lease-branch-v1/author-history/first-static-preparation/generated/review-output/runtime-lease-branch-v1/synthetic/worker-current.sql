BEGIN ISOLATION LEVEL READ COMMITTED;
SELECT set_config('wa.lease_secret',repeat('a',64),true) IS NOT NULL;
SELECT set_config('wa.fence','7',true)='7';
SELECT 'LEASE_V1_BEFORE';
UPDATE wa_lease_branch_v1_repro.work SET state='pending',lease_token_hash=NULL,lease_expires_at=NULL WHERE id=2 RETURNING id,state,fence,attempt_count;
SELECT 'LEASE_V1_AFTER';
COMMIT;
