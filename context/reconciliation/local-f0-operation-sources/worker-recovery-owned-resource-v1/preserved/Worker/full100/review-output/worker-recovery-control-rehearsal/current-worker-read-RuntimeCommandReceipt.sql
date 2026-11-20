SELECT 'WA_WR_BEFORE_CURRENT_WORKER_READ_RUNTIMECOMMANDRECEIPT';
SELECT jsonb_build_object('target_count',(SELECT count(*) FROM platform.runtime_command_receipt WHERE id='e79b78bf-fa17-5263-946f-b87c9f57688c'),'foreign_count',(SELECT count(*) FROM platform.runtime_command_receipt WHERE id='c7fe92b9-2ef9-5892-bf43-794f3cf9d802'));
SELECT 'WA_WR_AFTER_CURRENT_WORKER_READ_RUNTIMECOMMANDRECEIPT';
COMMIT;
