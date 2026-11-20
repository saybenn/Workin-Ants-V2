SELECT 'WA_WR_BEFORE_FRESH_HOLDER_RECOGNIZES_ORIGINAL_LOWER_FENCE_EFFECT';
SELECT jsonb_build_object('original_effect_matches',platform_private.worker_effect_matches('7ce05560-4c08-5c4b-a975-9d521f2d2864','9c6eecb1-9227-57ae-ad26-af67b16fb2dc',true));
INSERT INTO platform.runtime_attempt (id,work_item_id,attempt_number,fence,worker_id,result,reason_code,started_at,finished_at) VALUES ('20b82bf8-e623-55f7-b4bc-365a7d3e6fbb','7ce05560-4c08-5c4b-a975-9d521f2d2864',2,2,'worker-recovery-core-fixture.v1','committed','synthetic-retained-effect-recognized',clock_timestamp()-interval '1 millisecond',clock_timestamp());
SELECT 'WA_WR_AFTER_FRESH_HOLDER_RECOGNIZES_ORIGINAL_LOWER_FENCE_EFFECT';
COMMIT;
