-- PRIVILEGED NATIVE SHAPE CONTROL ONLY; all target USER triggers temporarily bypassed.
-- FK/CHECK/UNIQUE/internal RI triggers remain active. Roll back every mutation and trigger DDL.
BEGIN;
SET LOCAL search_path=pg_catalog;
SET LOCAL log_statement='none';
SET LOCAL log_min_error_statement='panic';
ALTER TABLE "app"."user_roles" DISABLE TRIGGER "owner_commit";
ALTER TABLE "app"."user_roles" DISABLE TRIGGER "physical_guard";
SAVEPOINT native_control;
WITH changed AS (INSERT INTO "app"."user_roles"("user_id","role","created_at","revision","mutation_transaction_id") VALUES ('c09f00d1-6d76-5c9f-b9af-2e779a5bcbcf'::pg_catalog.uuid,'user'::app.platform_role,'2026-11-17T00:00:00Z'::pg_catalog.timestamptz,'0'::pg_catalog.int8,'native-acl-setup-transaction'::pg_catalog.text) RETURNING 1) SELECT count(*)=1 AS native_insert_one FROM changed;
ROLLBACK TO SAVEPOINT native_control;
WITH changed AS (UPDATE "app"."user_roles" SET "user_id"='989b90a6-604e-5f8b-942d-c0f563355004'::pg_catalog.uuid WHERE "user_id"='989b90a6-604e-5f8b-942d-c0f563355004'::pg_catalog.uuid AND "role"='user'::app.platform_role RETURNING 1) SELECT count(*)=1 AS native_update_one FROM changed;
ROLLBACK TO SAVEPOINT native_control;
WITH changed AS (DELETE FROM "app"."user_roles" WHERE "user_id"='989b90a6-604e-5f8b-942d-c0f563355004'::pg_catalog.uuid AND "role"='user'::app.platform_role RETURNING 1) SELECT count(*)=1 AS native_delete_one FROM changed;
ROLLBACK TO SAVEPOINT native_control;
ROLLBACK;
SELECT jsonb_build_object('control','native-control-UserRole','all_declared_user_triggers_restored',NOT EXISTS(SELECT 1 FROM (VALUES ('app.user_roles','owner_commit','O'),('app.user_roles','physical_guard','O')) e(table_name,name,enabled) LEFT JOIN pg_trigger t ON t.tgrelid=to_regclass(e.table_name) AND t.tgname=e.name WHERE t.oid IS NULL OR t.tgisinternal OR t.tgenabled::text IS DISTINCT FROM e.enabled));
