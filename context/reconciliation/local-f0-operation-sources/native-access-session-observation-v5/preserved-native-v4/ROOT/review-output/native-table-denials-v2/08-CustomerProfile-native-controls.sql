-- PRIVILEGED NATIVE SHAPE CONTROL ONLY; all target USER triggers temporarily bypassed.
-- FK/CHECK/UNIQUE/internal RI triggers remain active. Roll back every mutation and trigger DDL.
BEGIN;
SET LOCAL search_path=pg_catalog;
SET LOCAL log_statement='none';
SET LOCAL log_min_error_statement='panic';
ALTER TABLE "app"."customer_profiles" DISABLE TRIGGER "customer_atomic";
ALTER TABLE "app"."customer_profiles" DISABLE TRIGGER "owner_commit";
ALTER TABLE "app"."customer_profiles" DISABLE TRIGGER "physical_guard";
SAVEPOINT native_control;
WITH changed AS (INSERT INTO "app"."customer_profiles"("id","user_id","status","display_name","avatar_media_id","city","state","country","created_at","updated_at","archived_at","revision","privacy_generation","mutation_transaction_id") VALUES ('bab9586f-2605-534e-a027-d79b44b29213'::pg_catalog.uuid,'501fb57b-3601-55e5-a7f2-768b7c0dbf04'::pg_catalog.uuid,'active'::app.profile_status,NULL::pg_catalog.text,NULL::pg_catalog.uuid,NULL::pg_catalog.text,NULL::pg_catalog.text,NULL::pg_catalog.text,'2026-11-17T00:00:00Z'::pg_catalog.timestamptz,'2026-11-17T00:00:00Z'::pg_catalog.timestamptz,NULL::pg_catalog.timestamptz,'0'::pg_catalog.int8,'0'::pg_catalog.int8,'native-acl-setup-transaction'::pg_catalog.text) RETURNING 1) SELECT count(*)=1 AS native_insert_one FROM changed;
ROLLBACK TO SAVEPOINT native_control;
WITH changed AS (UPDATE "app"."customer_profiles" SET "id"='97816ece-41af-5a37-993b-c703e390543a'::pg_catalog.uuid WHERE "id"='97816ece-41af-5a37-993b-c703e390543a'::pg_catalog.uuid RETURNING 1) SELECT count(*)=1 AS native_update_one FROM changed;
ROLLBACK TO SAVEPOINT native_control;
WITH changed AS (DELETE FROM "app"."customer_profiles" WHERE "id"='97816ece-41af-5a37-993b-c703e390543a'::pg_catalog.uuid RETURNING 1) SELECT count(*)=1 AS native_delete_one FROM changed;
ROLLBACK TO SAVEPOINT native_control;
ROLLBACK;
SELECT jsonb_build_object('control','native-control-CustomerProfile','all_declared_user_triggers_restored',NOT EXISTS(SELECT 1 FROM (VALUES ('app.customer_profiles','customer_atomic','O'),('app.customer_profiles','owner_commit','O'),('app.customer_profiles','physical_guard','O')) e(table_name,name,enabled) LEFT JOIN pg_trigger t ON t.tgrelid=to_regclass(e.table_name) AND t.tgname=e.name WHERE t.oid IS NULL OR t.tgisinternal OR t.tgenabled::text IS DISTINCT FROM e.enabled));
