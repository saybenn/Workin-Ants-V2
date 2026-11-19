-- PRIVILEGED NATIVE SHAPE CONTROL ONLY; all target USER triggers temporarily bypassed.
-- FK/CHECK/UNIQUE/internal RI triggers remain active. Roll back every mutation and trigger DDL.
BEGIN;
SET LOCAL search_path=pg_catalog;
SET LOCAL log_statement='none';
SET LOCAL log_min_error_statement='panic';
ALTER TABLE "app"."track_entitlement_definitions" DISABLE TRIGGER "owner_commit";
ALTER TABLE "app"."track_entitlement_definitions" DISABLE TRIGGER "physical_guard";
SAVEPOINT native_control;
WITH changed AS (INSERT INTO "app"."track_entitlement_definitions"("id","key","label","description","value_type","track","is_active","created_at","updated_at","revision","mutation_transaction_id") VALUES ('fa8238ce-4f3b-5ada-a572-bd8c500ed246'::pg_catalog.uuid,'native-acl-8df20f644de7f69e9fe1d743'::pg_catalog.text,'native-acl-5dba482680970c6074406df4'::pg_catalog.text,NULL::pg_catalog.text,'boolean'::app.track_entitlement_value_type,NULL::app.account_track,true,'2026-11-17T00:00:00Z'::pg_catalog.timestamptz,'2026-11-17T00:00:00Z'::pg_catalog.timestamptz,'0'::pg_catalog.int8,'native-acl-setup-transaction'::pg_catalog.text) RETURNING 1) SELECT count(*)=1 AS native_insert_one FROM changed;
ROLLBACK TO SAVEPOINT native_control;
WITH changed AS (UPDATE "app"."track_entitlement_definitions" SET "id"='cafe3d92-23ad-5f61-9f18-2f21e3e65900'::pg_catalog.uuid WHERE "id"='cafe3d92-23ad-5f61-9f18-2f21e3e65900'::pg_catalog.uuid RETURNING 1) SELECT count(*)=1 AS native_update_one FROM changed;
ROLLBACK TO SAVEPOINT native_control;
WITH changed AS (DELETE FROM "app"."track_entitlement_definitions" WHERE "id"='cafe3d92-23ad-5f61-9f18-2f21e3e65900'::pg_catalog.uuid RETURNING 1) SELECT count(*)=1 AS native_delete_one FROM changed;
ROLLBACK TO SAVEPOINT native_control;
ROLLBACK;
SELECT jsonb_build_object('control','native-control-TrackEntitlementDefinition','all_declared_user_triggers_restored',NOT EXISTS(SELECT 1 FROM (VALUES ('app.track_entitlement_definitions','owner_commit','O'),('app.track_entitlement_definitions','physical_guard','O')) e(table_name,name,enabled) LEFT JOIN pg_trigger t ON t.tgrelid=to_regclass(e.table_name) AND t.tgname=e.name WHERE t.oid IS NULL OR t.tgisinternal OR t.tgenabled::text IS DISTINCT FROM e.enabled));
