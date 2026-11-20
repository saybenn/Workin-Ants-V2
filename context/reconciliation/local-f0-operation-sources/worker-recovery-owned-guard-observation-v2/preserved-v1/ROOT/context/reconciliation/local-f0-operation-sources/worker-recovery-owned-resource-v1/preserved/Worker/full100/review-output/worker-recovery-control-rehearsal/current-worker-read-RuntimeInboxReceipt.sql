SELECT 'WA_WR_BEFORE_CURRENT_WORKER_READ_RUNTIMEINBOXRECEIPT';
SELECT jsonb_build_object('target_count',(SELECT count(*) FROM platform.runtime_inbox_receipt WHERE id='0f7891d4-591d-5482-861b-43f8322959c1'),'foreign_count',(SELECT count(*) FROM platform.runtime_inbox_receipt WHERE id='14808e33-b12d-5a3d-ac1e-933890dcc929'));
SELECT 'WA_WR_AFTER_CURRENT_WORKER_READ_RUNTIMEINBOXRECEIPT';
COMMIT;
