SELECT 'WA_WR_BEFORE_TERMINAL_WORK_TRIGGER_DENIAL_ROLLS_BACK_COMPLETION';
WITH changed AS (UPDATE platform.runtime_work_item SET state='completed' WHERE id='7ce05560-4c08-5c4b-a975-9d521f2d2864' AND state='leased' AND fence=2 AND effect_receipt_id='9c6eecb1-9227-57ae-ad26-af67b16fb2dc' RETURNING id) SELECT jsonb_build_object('changed',count(*)) FROM changed;
SELECT 'WA_WR_TEMPORARILY_COMPLETED';
UPDATE platform.runtime_work_item SET attempt_count=attempt_count+1 WHERE id='7ce05560-4c08-5c4b-a975-9d521f2d2864';
SELECT 'WA_WR_AFTER_TERMINAL_WORK_TRIGGER_DENIAL_ROLLS_BACK_COMPLETION';
COMMIT;
