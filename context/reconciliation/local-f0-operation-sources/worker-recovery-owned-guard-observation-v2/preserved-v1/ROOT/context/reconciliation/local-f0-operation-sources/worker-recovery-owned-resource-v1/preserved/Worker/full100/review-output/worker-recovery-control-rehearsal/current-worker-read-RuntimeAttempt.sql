SELECT 'WA_WR_BEFORE_CURRENT_WORKER_READ_RUNTIMEATTEMPT';
SELECT jsonb_build_object('target_count',(SELECT count(*) FROM platform.runtime_attempt WHERE id='c211ac77-7fca-54ba-a2c4-54bcc1258e0c'),'foreign_count',(SELECT count(*) FROM platform.runtime_attempt WHERE id='bb6b4b90-adb3-56a3-938a-8f8e73f37de6'));
SELECT 'WA_WR_AFTER_CURRENT_WORKER_READ_RUNTIMEATTEMPT';
COMMIT;
