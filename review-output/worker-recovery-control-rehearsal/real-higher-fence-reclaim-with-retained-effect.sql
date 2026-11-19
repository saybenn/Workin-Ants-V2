SELECT 'WA_WR_BEFORE_REAL_HIGHER_FENCE_RECLAIM_WITH_RETAINED_EFFECT';
WITH changed AS (UPDATE platform.runtime_work_item SET state='leased',fence=fence+1,attempt_count=attempt_count+1,lease_token_hash=encode(sha256(decode(current_setting('wa.lease_secret'),'hex')),'hex'),lease_expires_at=clock_timestamp()+interval '300 seconds' WHERE id='7ce05560-4c08-5c4b-a975-9d521f2d2864' AND fence=1 AND state='leased' RETURNING id) SELECT jsonb_build_object('changed',count(*)) FROM changed;
SELECT 'WA_WR_AFTER_REAL_HIGHER_FENCE_RECLAIM_WITH_RETAINED_EFFECT';
COMMIT;
