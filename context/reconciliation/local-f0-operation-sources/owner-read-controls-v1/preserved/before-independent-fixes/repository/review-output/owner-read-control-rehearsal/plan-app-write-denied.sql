SELECT 'WA_OR_BEFORE_PLAN_APP_WRITE_DENIED';
WITH changed AS (UPDATE app.track_plans SET name='forbidden read-purpose update',revision=revision+1 WHERE id='e017a25c-8213-5033-ab00-2537cd02a524' RETURNING id) SELECT jsonb_build_object('modified',count(*)) FROM changed;
SELECT 'WA_OR_AFTER_PLAN_APP_WRITE_DENIED';
COMMIT;
