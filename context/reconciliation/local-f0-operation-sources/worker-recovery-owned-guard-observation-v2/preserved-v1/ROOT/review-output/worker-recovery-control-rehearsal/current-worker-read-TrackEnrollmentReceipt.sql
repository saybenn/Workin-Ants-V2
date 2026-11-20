SELECT 'WA_WR_BEFORE_CURRENT_WORKER_READ_TRACKENROLLMENTRECEIPT';
SELECT jsonb_build_object('target_count',(SELECT count(*) FROM app.track_enrollment_receipt WHERE id='69e01c0f-448a-5dfa-94b3-37096908e4d3'),'foreign_count',(SELECT count(*) FROM app.track_enrollment_receipt WHERE id='be2aa578-598a-5aae-9ffb-6caea3f701ea'));
SELECT 'WA_WR_AFTER_CURRENT_WORKER_READ_TRACKENROLLMENTRECEIPT';
COMMIT;
