SELECT 'WA_AW2_BEFORE_PENDING_WORK_NEXT_ATTEMPT_UPDATE';
WITH changed AS (UPDATE platform.runtime_work_item SET next_attempt_at=clock_timestamp()+interval '120 seconds' WHERE id='530db9d1-b945-53ec-bb0c-6d91c914b5fc' AND state='pending' AND fence=0 AND attempt_count=0 AND next_attempt_at IS NULL AND lease_token_hash IS NULL AND lease_expires_at IS NULL AND effect_receipt_id IS NULL RETURNING next_attempt_at) SELECT jsonb_build_object('changed',count(*),'server_not_before_future',coalesce(bool_and(next_attempt_at>clock_timestamp() AND next_attempt_at<=clock_timestamp()+interval '120 seconds'),false)) FROM changed;
SET CONSTRAINTS ALL IMMEDIATE;
SELECT 'WA_AW2_AFTER_PENDING_WORK_NEXT_ATTEMPT_UPDATE';
COMMIT;
