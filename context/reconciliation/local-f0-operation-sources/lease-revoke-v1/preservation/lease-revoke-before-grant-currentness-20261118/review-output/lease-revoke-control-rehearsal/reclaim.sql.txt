SELECT 'WA_LR_BEFORE_CONCURRENT_RECLAIM_STALE_HOLDER';
WITH changed AS (UPDATE platform.runtime_work_item SET state='leased',fence=fence+1,attempt_count=attempt_count+1,lease_token_hash=encode(sha256(decode(current_setting('wa.lease_secret'),'hex')),'hex'),lease_expires_at=clock_timestamp()+interval '90 seconds' WHERE id='b3c6b69b-8f03-5406-88e6-b2434ee6c797'::uuid RETURNING 1) SELECT jsonb_build_object('changed',count(*)) FROM changed;
SELECT 'WA_LR_AFTER_CONCURRENT_RECLAIM_STALE_HOLDER';
COMMIT;
