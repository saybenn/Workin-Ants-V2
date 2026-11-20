SELECT 'WA_WR_BEFORE_CURRENT_WORKER_READ_RUNTIMEOUTBOXMESSAGE';
SELECT jsonb_build_object('target_count',(SELECT count(*) FROM platform.runtime_outbox_message WHERE id='9c3b8f32-d0bb-5efa-aef9-0bf64edc8d81'),'foreign_count',(SELECT count(*) FROM platform.runtime_outbox_message WHERE id='380420fc-4dba-57c6-8242-30d4f0b044b1'));
SELECT 'WA_WR_AFTER_CURRENT_WORKER_READ_RUNTIMEOUTBOXMESSAGE';
COMMIT;
