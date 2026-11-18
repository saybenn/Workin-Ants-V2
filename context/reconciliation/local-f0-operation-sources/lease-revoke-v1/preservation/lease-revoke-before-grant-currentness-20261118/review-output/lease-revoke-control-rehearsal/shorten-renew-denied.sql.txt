SELECT 'WA_LR_BEFORE_SHORTEN_RENEW_DENIED';
WITH changed AS (UPDATE platform.runtime_work_item SET lease_expires_at=lease_expires_at-interval '1 second' WHERE id='b3c6b69b-8f03-5406-88e6-b2434ee6c797'::uuid RETURNING 1) SELECT jsonb_build_object('changed',count(*)) FROM changed;
SELECT 'WA_LR_AFTER_SHORTEN_RENEW_DENIED';
COMMIT;
