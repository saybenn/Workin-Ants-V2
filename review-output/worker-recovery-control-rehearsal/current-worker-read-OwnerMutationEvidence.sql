SELECT 'WA_WR_BEFORE_CURRENT_WORKER_READ_OWNERMUTATIONEVIDENCE';
SELECT jsonb_build_object('target_count',(SELECT count(*) FROM platform.owner_mutation_evidence WHERE id='28c407fb-268a-5920-8c86-ea9ce249a38f'),'foreign_count',(SELECT count(*) FROM platform.owner_mutation_evidence WHERE id='e8b0b375-03a8-5672-83a5-2f31a4590d70'));
SELECT 'WA_WR_AFTER_CURRENT_WORKER_READ_OWNERMUTATIONEVIDENCE';
COMMIT;
