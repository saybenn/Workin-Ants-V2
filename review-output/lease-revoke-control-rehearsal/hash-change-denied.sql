SELECT 'WA_LR_BEFORE_HASH_CHANGE_DENIED';
WITH changed AS (UPDATE platform.runtime_work_item SET lease_token_hash=encode(sha256(decode(current_setting('wa.lease_secret'),'hex')),'hex') WHERE id='b3c6b69b-8f03-5406-88e6-b2434ee6c797'::uuid RETURNING 1) SELECT jsonb_build_object('changed',count(*)) FROM changed;
SELECT 'WA_LR_AFTER_HASH_CHANGE_DENIED';
COMMIT;
