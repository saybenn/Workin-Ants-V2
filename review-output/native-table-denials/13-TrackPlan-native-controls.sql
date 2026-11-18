-- PRIVILEGED NATIVE SHAPE CONTROL ONLY; all target USER triggers temporarily bypassed.
-- FK/CHECK/UNIQUE/internal RI triggers remain active. Roll back every mutation and trigger DDL.
BEGIN;
SET LOCAL search_path=pg_catalog;
SET LOCAL log_statement='none';
SET LOCAL log_min_error_statement='panic';
ALTER TABLE "app"."track_plans" DISABLE TRIGGER "owner_commit";
ALTER TABLE "app"."track_plans" DISABLE TRIGGER "physical_guard";
SAVEPOINT native_control;
WITH changed AS (INSERT INTO "app"."track_plans"("id","track","key","name","status","billing_model","monthly_price_cents","currency","description","display_order","metadata","created_at","updated_at","revision","version","content_hash","mutation_transaction_id") VALUES ('76d1bd22-e0b1-50e1-9230-a5a5a4431dda'::pg_catalog.uuid,'customer'::app.account_track,'native-acl-cb9e989e721ca22ec1b24a51'::pg_catalog.text,'native-acl-278201d68e5a7a2320b51369'::pg_catalog.text,'draft'::app.track_plan_status,'free'::app.track_billing_model,NULL::pg_catalog.int4,'usd'::pg_catalog.text,NULL::pg_catalog.text,'0'::pg_catalog.int4,NULL::pg_catalog.jsonb,'2026-11-17T00:00:00Z'::pg_catalog.timestamptz,'2026-11-17T00:00:00Z'::pg_catalog.timestamptz,'0'::pg_catalog.int8,'native-acl-65385e59eba8f23103185c80'::pg_catalog.text,'fe14f407608ed335efbfbc50d6da1a25561a799ce5ccd68f3e1f7ffff45f64c5'::pg_catalog.bpchar,'native-acl-setup-transaction'::pg_catalog.text) RETURNING 1) SELECT count(*)=1 AS native_insert_one FROM changed;
ROLLBACK TO SAVEPOINT native_control;
WITH changed AS (UPDATE "app"."track_plans" SET "id"='4fac45ec-3ff4-59f9-8575-5615dde242fb'::pg_catalog.uuid WHERE "id"='4fac45ec-3ff4-59f9-8575-5615dde242fb'::pg_catalog.uuid RETURNING 1) SELECT count(*)=1 AS native_update_one FROM changed;
ROLLBACK TO SAVEPOINT native_control;
WITH changed AS (DELETE FROM "app"."track_plans" WHERE "id"='4fac45ec-3ff4-59f9-8575-5615dde242fb'::pg_catalog.uuid RETURNING 1) SELECT count(*)=1 AS native_delete_one FROM changed;
ROLLBACK TO SAVEPOINT native_control;
ROLLBACK;
SELECT jsonb_build_object('control','native-control-TrackPlan','all_declared_user_triggers_restored',NOT EXISTS(SELECT 1 FROM (VALUES ('app.track_plans','owner_commit','O'),('app.track_plans','physical_guard','O')) e(table_name,name,enabled) LEFT JOIN pg_trigger t ON t.tgrelid=to_regclass(e.table_name) AND t.tgname=e.name WHERE t.oid IS NULL OR t.tgisinternal OR t.tgenabled::text IS DISTINCT FROM e.enabled));
