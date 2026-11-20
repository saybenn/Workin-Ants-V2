SELECT 'WA_WR_BEFORE_B_CLAIM';
WITH changed AS (UPDATE platform.runtime_work_item SET state='leased',fence=fence+1,attempt_count=attempt_count+1,lease_token_hash=encode(sha256(decode(current_setting('wa.lease_secret'),'hex')),'hex'),lease_expires_at=clock_timestamp()+interval '300 seconds' WHERE id='bd16c4aa-52bd-50f6-950e-c55e501f2b21' AND fence=0 AND state='pending' RETURNING id) SELECT jsonb_build_object('changed',count(*)) FROM changed;
SELECT 'WA_WR_AFTER_B_CLAIM';
COMMIT;
