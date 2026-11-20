SELECT 'WA_WR_BEFORE_ORIGINAL_EFFECT_COMPLETES_ONCE_WITHOUT_REENROLLMENT';
SELECT jsonb_build_object('original_effect_matches',platform_private.worker_effect_matches('7ce05560-4c08-5c4b-a975-9d521f2d2864','9c6eecb1-9227-57ae-ad26-af67b16fb2dc',true));
WITH changed AS (UPDATE platform.runtime_work_item SET state='completed' WHERE id='7ce05560-4c08-5c4b-a975-9d521f2d2864' AND state='leased' AND fence=2 AND effect_receipt_id='9c6eecb1-9227-57ae-ad26-af67b16fb2dc' RETURNING id) SELECT jsonb_build_object('changed',count(*)) FROM changed;
SELECT 'WA_WR_AFTER_ORIGINAL_EFFECT_COMPLETES_ONCE_WITHOUT_REENROLLMENT';
COMMIT;
