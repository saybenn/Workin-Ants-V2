BEGIN ISOLATION LEVEL READ COMMITTED;
SELECT 'LEASE_V1_BEFORE';
UPDATE wa_lease_branch_v1_repro.work SET next_attempt_at='2026-01-02T00:00:00Z' WHERE id=1 RETURNING jsonb_build_object('id',id,'state',state,'fence',fence,'attempt_count',attempt_count,'lease_fields_null',lease_token_hash IS NULL AND lease_expires_at IS NULL,'effect_absent',effect_receipt_id IS NULL,'next_attempt_at',next_attempt_at);
SELECT 'LEASE_V1_AFTER';
COMMIT;
