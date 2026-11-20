SELECT 'WA_WR_BEFORE_CURRENT_WORKER_READ_TRACKSUBSCRIPTION';
SELECT jsonb_build_object('target_count',(SELECT count(*) FROM app.track_subscriptions WHERE id='c1893860-e4fc-5586-93d7-ea5a4c41e840'),'foreign_count',(SELECT count(*) FROM app.track_subscriptions WHERE id='1000d3f0-487e-540f-92ae-d8e7afdc67c9'));
SELECT 'WA_WR_AFTER_CURRENT_WORKER_READ_TRACKSUBSCRIPTION';
COMMIT;
