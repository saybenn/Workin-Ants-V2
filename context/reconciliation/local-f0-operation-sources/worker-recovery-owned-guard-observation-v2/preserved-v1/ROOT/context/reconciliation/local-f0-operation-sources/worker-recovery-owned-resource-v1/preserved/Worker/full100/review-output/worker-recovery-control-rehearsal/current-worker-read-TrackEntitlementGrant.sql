SELECT 'WA_WR_BEFORE_CURRENT_WORKER_READ_TRACKENTITLEMENTGRANT';
SELECT jsonb_build_object('target_count',(SELECT count(*) FROM app.track_entitlement_grants WHERE id='c0f420f8-536a-592c-823c-3bdedc161867'),'foreign_count',(SELECT count(*) FROM app.track_entitlement_grants WHERE id='735ec337-a191-577f-a787-d774b8e0a32a'));
SELECT 'WA_WR_AFTER_CURRENT_WORKER_READ_TRACKENTITLEMENTGRANT';
COMMIT;
