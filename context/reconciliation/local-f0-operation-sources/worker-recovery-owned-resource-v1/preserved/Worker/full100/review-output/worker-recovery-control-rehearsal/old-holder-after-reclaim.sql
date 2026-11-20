SELECT 'WA_WR_BEFORE_OLD_HOLDER_AFTER_RECLAIM';
SELECT jsonb_build_object('lease_valid',platform_private.worker_lease_valid('7ce05560-4c08-5c4b-a975-9d521f2d2864',NULL,true));
WITH changed AS (UPDATE platform.runtime_work_item SET state=state WHERE id='7ce05560-4c08-5c4b-a975-9d521f2d2864' RETURNING id) SELECT jsonb_build_object('changed',count(*)) FROM changed;
SELECT 'WA_WR_AFTER_OLD_HOLDER_AFTER_RECLAIM';
COMMIT;
