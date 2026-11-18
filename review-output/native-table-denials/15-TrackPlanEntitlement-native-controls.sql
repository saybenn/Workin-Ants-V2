-- PRIVILEGED NATIVE SHAPE CONTROL ONLY; all target USER triggers temporarily bypassed.
-- FK/CHECK/UNIQUE/internal RI triggers remain active. Roll back every mutation and trigger DDL.
BEGIN;
SET LOCAL search_path=pg_catalog;
SET LOCAL log_statement='none';
SET LOCAL log_min_error_statement='panic';
ALTER TABLE "app"."track_plan_entitlements" DISABLE TRIGGER "owner_commit";
ALTER TABLE "app"."track_plan_entitlements" DISABLE TRIGGER "physical_guard";
SAVEPOINT native_control;
WITH changed AS (INSERT INTO "app"."track_plan_entitlements"("id","plan_id","entitlement_id","value_type","boolean_value","int_value","decimal_value","string_value","json_value","usage_period","created_at","updated_at","revision","mutation_transaction_id") VALUES ('7ebd7dd6-7c9c-5146-bed4-2693f8babd78'::pg_catalog.uuid,'8792f072-01e0-5070-b577-e34a2b13e476'::pg_catalog.uuid,'e51f149d-b600-5bfa-8910-7ace0d153be0'::pg_catalog.uuid,'boolean'::app.track_entitlement_value_type,true,NULL::pg_catalog.int4,NULL::pg_catalog.float8,NULL::pg_catalog.text,NULL::pg_catalog.jsonb,NULL::app.track_usage_period,'2026-11-17T00:00:00Z'::pg_catalog.timestamptz,'2026-11-17T00:00:00Z'::pg_catalog.timestamptz,'0'::pg_catalog.int8,'native-acl-setup-transaction'::pg_catalog.text) RETURNING 1) SELECT count(*)=1 AS native_insert_one FROM changed;
ROLLBACK TO SAVEPOINT native_control;
WITH changed AS (UPDATE "app"."track_plan_entitlements" SET "id"='f2ff834c-834c-554b-b6fa-f18de37789c0'::pg_catalog.uuid WHERE "id"='f2ff834c-834c-554b-b6fa-f18de37789c0'::pg_catalog.uuid RETURNING 1) SELECT count(*)=1 AS native_update_one FROM changed;
ROLLBACK TO SAVEPOINT native_control;
WITH changed AS (DELETE FROM "app"."track_plan_entitlements" WHERE "id"='f2ff834c-834c-554b-b6fa-f18de37789c0'::pg_catalog.uuid RETURNING 1) SELECT count(*)=1 AS native_delete_one FROM changed;
ROLLBACK TO SAVEPOINT native_control;
ROLLBACK;
SELECT jsonb_build_object('control','native-control-TrackPlanEntitlement','all_declared_user_triggers_restored',NOT EXISTS(SELECT 1 FROM (VALUES ('app.track_plan_entitlements','owner_commit','O'),('app.track_plan_entitlements','physical_guard','O')) e(table_name,name,enabled) LEFT JOIN pg_trigger t ON t.tgrelid=to_regclass(e.table_name) AND t.tgname=e.name WHERE t.oid IS NULL OR t.tgisinternal OR t.tgenabled::text IS DISTINCT FROM e.enabled));
