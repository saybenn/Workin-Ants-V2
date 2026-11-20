SELECT 'WA_WR_BEFORE_CURRENT_WORKER_READ_RUNTIMEEFFECTRECEIPT';
SELECT jsonb_build_object('target_count',(SELECT count(*) FROM platform.runtime_effect_receipt WHERE id='9c6eecb1-9227-57ae-ad26-af67b16fb2dc'),'foreign_count',(SELECT count(*) FROM platform.runtime_effect_receipt WHERE id='c29de844-e0cd-5e7c-b5bc-4f7c11b1de2e'));
SELECT 'WA_WR_AFTER_CURRENT_WORKER_READ_RUNTIMEEFFECTRECEIPT';
COMMIT;
