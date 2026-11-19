-- PRIVILEGED NATIVE SHAPE CONTROL ONLY; all target USER triggers temporarily bypassed.
-- FK/CHECK/UNIQUE/internal RI triggers remain active. Roll back every mutation and trigger DDL.
BEGIN;
SET LOCAL search_path=pg_catalog;
SET LOCAL log_statement='none';
SET LOCAL log_min_error_statement='panic';
ALTER TABLE "app"."users" DISABLE TRIGGER "owner_commit";
ALTER TABLE "app"."users" DISABLE TRIGGER "physical_guard";
SAVEPOINT native_control;
WITH changed AS (INSERT INTO "app"."users"("id","email","handle","display_name","avatar_url","bio","city","state","country","is_public","created_at","updated_at","privacy_erased_at","privacy_erasure_status","revision","privacy_generation","mutation_transaction_id") VALUES ('a8c56c34-5761-593a-adee-d138ed81a5fe'::pg_catalog.uuid,NULL::pg_catalog.text,NULL::pg_catalog.text,NULL::pg_catalog.text,NULL::pg_catalog.text,NULL::pg_catalog.text,NULL::pg_catalog.text,NULL::pg_catalog.text,NULL::pg_catalog.text,true,'2026-11-17T00:00:00Z'::pg_catalog.timestamptz,'2026-11-17T00:00:00Z'::pg_catalog.timestamptz,NULL::pg_catalog.timestamptz,NULL::pg_catalog.text,'0'::pg_catalog.int8,'0'::pg_catalog.int8,'native-acl-setup-transaction'::pg_catalog.text) RETURNING 1) SELECT count(*)=1 AS native_insert_one FROM changed;
ROLLBACK TO SAVEPOINT native_control;
WITH changed AS (UPDATE "app"."users" SET "id"='f7cb6f1f-f721-5562-aad6-85fd9ca958c5'::pg_catalog.uuid WHERE "id"='f7cb6f1f-f721-5562-aad6-85fd9ca958c5'::pg_catalog.uuid RETURNING 1) SELECT count(*)=1 AS native_update_one FROM changed;
ROLLBACK TO SAVEPOINT native_control;
WITH changed AS (DELETE FROM "app"."users" WHERE "id"='f7cb6f1f-f721-5562-aad6-85fd9ca958c5'::pg_catalog.uuid RETURNING 1) SELECT count(*)=1 AS native_delete_one FROM changed;
ROLLBACK TO SAVEPOINT native_control;
ROLLBACK;
SELECT jsonb_build_object('control','native-control-User','all_declared_user_triggers_restored',NOT EXISTS(SELECT 1 FROM (VALUES ('app.users','owner_commit','O'),('app.users','physical_guard','O')) e(table_name,name,enabled) LEFT JOIN pg_trigger t ON t.tgrelid=to_regclass(e.table_name) AND t.tgname=e.name WHERE t.oid IS NULL OR t.tgisinternal OR t.tgenabled::text IS DISTINCT FROM e.enabled));
