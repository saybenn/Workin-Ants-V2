SELECT 'WA_OR_BEFORE_PLAN_APP_WRONG_ACTION';
SELECT jsonb_build_object('root',(SELECT count(*) FROM app.track_plans WHERE id='e017a25c-8213-5033-ab00-2537cd02a524'),'foreign',(SELECT count(*) FROM app.track_plans WHERE id='c6c7ef29-9020-5562-9289-9e39930ff595'));
SELECT 'WA_OR_AFTER_PLAN_APP_WRONG_ACTION';
COMMIT;
