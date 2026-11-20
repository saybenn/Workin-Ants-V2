BEGIN ISOLATION LEVEL REPEATABLE READ READ ONLY;
SET LOCAL search_path=pg_catalog;
SET LOCAL TimeZone='UTC';
SET LOCAL DateStyle='ISO, YMD';
SET LOCAL extra_float_digits=3;
SET LOCAL bytea_output='hex';
WITH role_rows AS (SELECT rolname,rolsuper,rolinherit,rolcreaterole,rolcreatedb,rolcanlogin,rolreplication,rolbypassrls,rolconnlimit,rolvaliduntil,rolconfig FROM pg_roles WHERE rolname !~ '^pg_'),
members AS (SELECT member::regrole::text AS member,roleid::regrole::text AS role,grantor::regrole::text AS grantor,admin_option,inherit_option,set_option FROM pg_auth_members),
db AS (SELECT datname,datdba::regrole::text AS owner,datacl FROM pg_database WHERE datname=current_database())
SELECT jsonb_build_object('role_attributes_sha256',(SELECT encode(sha256(convert_to(COALESCE(jsonb_agg(to_jsonb(x) ORDER BY rolname),'[]'::jsonb)::text,'UTF8')),'hex') FROM role_rows x),
'memberships_sha256',(SELECT encode(sha256(convert_to(COALESCE(jsonb_agg(to_jsonb(x) ORDER BY to_jsonb(x)::text COLLATE "C"),'[]'::jsonb)::text,'UTF8')),'hex') FROM members x),
'database_authority_sha256',(SELECT encode(sha256(convert_to(to_jsonb(db)::text,'UTF8')),'hex') FROM db),
'all_six_have_scram',(SELECT count(*)=6 AND bool_and(rolpassword LIKE 'SCRAM-SHA-256$%') FROM pg_authid WHERE rolname=ANY(ARRAY['postgres','wa_migrator','wa_context_issuer','wa_identity_service_authority','wa_app_runtime','wa_worker'])),
'temporary_memberships',(SELECT count(*) FROM pg_auth_members WHERE member='wa_schema_owner'::regrole AND roleid IN ('wa_private_helper_owner'::regrole,'wa_customer_verifier'::regrole,'wa_track_verifier'::regrole)),
'permanent_migrator_edge',(SELECT count(*)=1 AND bool_and(roleid='wa_schema_owner'::regrole AND grantor='postgres'::regrole AND NOT admin_option AND NOT inherit_option AND set_option) FROM pg_auth_members WHERE member='wa_migrator'::regrole),
'leaf_create_false',NOT EXISTS(SELECT 1 FROM (VALUES('wa_private_helper_owner'),('wa_customer_verifier'),('wa_track_verifier')) l(role) CROSS JOIN (VALUES('app'),('platform'),('platform_private')) s(name) WHERE has_schema_privilege(l.role,s.name,'CREATE')));
COMMIT;
