SELECT 'WA_SRC_BEFORE_AGEGATEBLOCK_MISSING_PRIMARY_FIELD';
SELECT jsonb_build_object('root',(SELECT count(*) FROM app.age_gate_blocks WHERE id='966acdc1-5960-59ce-a11f-087556336be7'),'foreign',(SELECT count(*) FROM app.age_gate_blocks WHERE id='ff81a7a1-da2a-5cdd-af0d-d0fe55091448'));
SELECT 'WA_SRC_AFTER_AGEGATEBLOCK_MISSING_PRIMARY_FIELD';
COMMIT;
