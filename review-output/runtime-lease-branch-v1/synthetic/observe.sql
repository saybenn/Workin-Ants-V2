BEGIN READ ONLY;
SELECT jsonb_build_object(
'rows',(SELECT jsonb_agg(jsonb_build_object('id',id,'state',state,'fence',fence,'attempt_count',attempt_count,'lease_fields_null',lease_token_hash IS NULL AND lease_expires_at IS NULL,'effect_absent',effect_receipt_id IS NULL,'next_attempt_at',next_attempt_at) ORDER BY id) FROM wa_lease_branch_v1_repro.work),
'app_helper_execute',has_function_privilege('wa_lease_v1_app','wa_lease_branch_v1_repro.lease_secret_matches(text)','EXECUTE'),
'worker_helper_execute',has_function_privilege('wa_lease_v1_worker','wa_lease_branch_v1_repro.lease_secret_matches(text)','EXECUTE'),
'verifier_helper_execute',has_function_privilege('wa_lease_v1_verifier','wa_lease_branch_v1_repro.lease_secret_matches(text)','EXECUTE'),
'trigger_enabled',(SELECT tgenabled='O' FROM pg_trigger WHERE tgrelid='wa_lease_branch_v1_repro.work'::regclass AND tgname='exact_guard'));
ROLLBACK;
