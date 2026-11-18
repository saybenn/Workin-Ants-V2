SELECT 'WA_OR_BEFORE_BENEFIT_APP_WRONG_ROOT';
SELECT jsonb_build_object('root',(SELECT count(*) FROM app.track_plan_entitlements WHERE id='b8e5e9af-7638-5ab9-81e2-6ad0b298b8c5'),'foreign',(SELECT count(*) FROM app.track_plan_entitlements WHERE id='9ed8c635-91e3-5c15-8064-7c90c1d9f365'));
SELECT 'WA_OR_AFTER_BENEFIT_APP_WRONG_ROOT';
COMMIT;
