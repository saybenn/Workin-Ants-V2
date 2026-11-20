-- Actual bound wa_worker; 256-bit preimage is runtime memory only, never a stored hash used as secret.
UPDATE platform.runtime_work_item SET state='leased',fence=fence+1,attempt_count=attempt_count+1,lease_token_hash=encode(sha256(decode(current_setting('wa.lease_secret'),'hex')),'hex'),lease_expires_at=clock_timestamp()+interval '2 minutes' WHERE id='0733d5c9-e95e-5c48-a176-60e6bf6a2220' AND fence=0 AND state='pending';
SELECT 'WA_WORKER_CLAIM_READY';
COMMIT;
