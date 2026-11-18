SELECT 'WA_OR_BEFORE_WORKER_READ_FIXTURE_CLAIM';
WITH changed AS (UPDATE platform.runtime_work_item SET state='leased',fence=fence+1,attempt_count=attempt_count+1,lease_token_hash=encode(sha256(decode(current_setting('wa.lease_secret'),'hex')),'hex'),lease_expires_at=clock_timestamp()+interval '300 seconds' WHERE id='927e6a91-e9f9-5a6a-88c0-2c6b7402e5f7' RETURNING id) SELECT jsonb_build_object('claimed',count(*)) FROM changed;
SELECT 'WA_OR_AFTER_WORKER_READ_FIXTURE_CLAIM';
COMMIT;
