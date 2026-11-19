-- PRIVILEGED NATIVE SHAPE CONTROL ONLY; all target USER triggers temporarily bypassed.
-- FK/CHECK/UNIQUE/internal RI triggers remain active. Roll back every mutation and trigger DDL.
BEGIN;
SET LOCAL search_path=pg_catalog;
SET LOCAL log_statement='none';
SET LOCAL log_min_error_statement='panic';
ALTER TABLE "app"."auth_provider_accounts" DISABLE TRIGGER "owner_commit";
ALTER TABLE "app"."auth_provider_accounts" DISABLE TRIGGER "physical_guard";
SAVEPOINT native_control;
WITH changed AS (INSERT INTO "app"."auth_provider_accounts"("id","user_id","security_profile_id","provider_type","provider_user_id","provider_account_id","email","email_verified_at","status","linked_at","last_used_at","revoked_at","created_at","updated_at","revision","mutation_transaction_id") VALUES ('a1fc15e5-8658-5c91-8a52-118e450c3b41'::pg_catalog.uuid,'e2abf164-e83b-55dc-b398-486d0008a19e'::pg_catalog.uuid,NULL::pg_catalog.uuid,'email_password'::app.auth_provider_type,NULL::pg_catalog.text,NULL::pg_catalog.text,NULL::pg_catalog.text,NULL::pg_catalog.timestamptz,'active'::app.auth_credential_status,'2026-11-17T00:00:00Z'::pg_catalog.timestamptz,NULL::pg_catalog.timestamptz,NULL::pg_catalog.timestamptz,'2026-11-17T00:00:00Z'::pg_catalog.timestamptz,'2026-11-17T00:00:00Z'::pg_catalog.timestamptz,'0'::pg_catalog.int8,'native-acl-setup-transaction'::pg_catalog.text) RETURNING 1) SELECT count(*)=1 AS native_insert_one FROM changed;
ROLLBACK TO SAVEPOINT native_control;
WITH changed AS (UPDATE "app"."auth_provider_accounts" SET "id"='fdb2647d-da3c-5f81-bcde-5d6f83108ef1'::pg_catalog.uuid WHERE "id"='fdb2647d-da3c-5f81-bcde-5d6f83108ef1'::pg_catalog.uuid RETURNING 1) SELECT count(*)=1 AS native_update_one FROM changed;
ROLLBACK TO SAVEPOINT native_control;
WITH changed AS (DELETE FROM "app"."auth_provider_accounts" WHERE "id"='fdb2647d-da3c-5f81-bcde-5d6f83108ef1'::pg_catalog.uuid RETURNING 1) SELECT count(*)=1 AS native_delete_one FROM changed;
ROLLBACK TO SAVEPOINT native_control;
ROLLBACK;
SELECT jsonb_build_object('control','native-control-AuthProviderAccount','all_declared_user_triggers_restored',NOT EXISTS(SELECT 1 FROM (VALUES ('app.auth_provider_accounts','owner_commit','O'),('app.auth_provider_accounts','physical_guard','O')) e(table_name,name,enabled) LEFT JOIN pg_trigger t ON t.tgrelid=to_regclass(e.table_name) AND t.tgname=e.name WHERE t.oid IS NULL OR t.tgisinternal OR t.tgenabled::text IS DISTINCT FROM e.enabled));
