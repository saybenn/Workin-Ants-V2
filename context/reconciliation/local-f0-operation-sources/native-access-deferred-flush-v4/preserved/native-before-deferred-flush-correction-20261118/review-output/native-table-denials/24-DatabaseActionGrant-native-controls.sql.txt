-- PRIVILEGED NATIVE SHAPE CONTROL ONLY; all target USER triggers temporarily bypassed.
-- FK/CHECK/UNIQUE/internal RI triggers remain active. Roll back every mutation and trigger DDL.
BEGIN;
SET LOCAL search_path=pg_catalog;
SET LOCAL log_statement='none';
SET LOCAL log_min_error_statement='panic';
ALTER TABLE "platform"."database_action_grant" DISABLE TRIGGER "grant_guard";
SAVEPOINT native_control;
WITH changed AS (INSERT INTO "platform"."database_action_grant"("id","token_hash","issuer_service","principal_user_id","service_principal","database_login_role","owner_module_id","action","purpose","target_kind","target_id","allowed_fields","policy_version","security_generation","source_generation","backend_pid","transaction_id","expires_at","revoked_at","created_at","mutation_transaction_id") VALUES ('fec38b1a-0fe8-53d1-8d7c-d35fe2f2395b'::pg_catalog.uuid,'bdd9b81fc6b5ddde47ddc697ae7ec5a3a8968b35ba1772234033307c164c1172'::pg_catalog.bpchar,'wa_context_issuer'::pg_catalog.text,'f1988915-fa22-5261-9f79-d3ddeba4e6cc'::pg_catalog.uuid,NULL::pg_catalog.text,'wa_app_runtime'::pg_catalog.text,'customer_buyer_profile'::pg_catalog.text,'SH-004.v1'::pg_catalog.text,'provision'::pg_catalog.text,'CustomerProfile'::pg_catalog.text,'70851609-6661-5892-968d-a963468e40e3'::pg_catalog.text,NULL::pg_catalog.text[],'native-acl-fixture.v1'::pg_catalog.text,'0'::pg_catalog.int8,'0'::pg_catalog.int8,'0'::pg_catalog.int4,'inert-native-acl-fixture'::pg_catalog.text,'2026-11-17T00:00:00Z'::pg_catalog.timestamptz,'2026-11-17T00:00:00Z'::pg_catalog.timestamptz,'2026-11-17T00:00:00Z'::pg_catalog.timestamptz,'native-acl-setup-transaction'::pg_catalog.text) RETURNING 1) SELECT count(*)=1 AS native_insert_one FROM changed;
ROLLBACK TO SAVEPOINT native_control;
WITH changed AS (UPDATE "platform"."database_action_grant" SET "id"='bdc1cb43-7041-5bc5-bc31-08140c7f28c1'::pg_catalog.uuid WHERE "id"='bdc1cb43-7041-5bc5-bc31-08140c7f28c1'::pg_catalog.uuid RETURNING 1) SELECT count(*)=1 AS native_update_one FROM changed;
ROLLBACK TO SAVEPOINT native_control;
WITH changed AS (DELETE FROM "platform"."database_action_grant" WHERE "id"='bdc1cb43-7041-5bc5-bc31-08140c7f28c1'::pg_catalog.uuid RETURNING 1) SELECT count(*)=1 AS native_delete_one FROM changed;
ROLLBACK TO SAVEPOINT native_control;
ROLLBACK;
SELECT jsonb_build_object('control','native-control-DatabaseActionGrant','all_declared_user_triggers_restored',NOT EXISTS(SELECT 1 FROM (VALUES ('platform.database_action_grant','grant_guard','O')) e(table_name,name,enabled) LEFT JOIN pg_trigger t ON t.tgrelid=to_regclass(e.table_name) AND t.tgname=e.name WHERE t.oid IS NULL OR t.tgisinternal OR t.tgenabled::text IS DISTINCT FROM e.enabled));
