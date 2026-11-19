SELECT 'WA_WR_BEFORE_CURRENT_WORKER_READ_TRACKBASESELECTION';
SELECT jsonb_build_object('target_count',(SELECT count(*) FROM app.track_base_selection WHERE id='748589ea-c892-5dbd-aac7-6118cd855832'),'foreign_count',(SELECT count(*) FROM app.track_base_selection WHERE id='cef4d2f2-6cd9-57d1-be42-947e3abf7f7f'));
SELECT 'WA_WR_AFTER_CURRENT_WORKER_READ_TRACKBASESELECTION';
COMMIT;
