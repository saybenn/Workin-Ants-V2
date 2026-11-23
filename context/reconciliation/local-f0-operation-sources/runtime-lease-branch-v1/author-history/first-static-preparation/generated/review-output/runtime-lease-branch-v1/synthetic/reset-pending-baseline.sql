BEGIN;
UPDATE wa_lease_branch_v1_repro.work SET next_attempt_at='2026-01-01T00:00:00Z' WHERE id=1 RETURNING id,next_attempt_at;
COMMIT;
