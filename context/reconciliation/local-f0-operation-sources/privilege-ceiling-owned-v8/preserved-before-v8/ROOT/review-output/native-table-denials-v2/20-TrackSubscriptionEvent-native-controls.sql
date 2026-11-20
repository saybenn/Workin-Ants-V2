-- PRIVILEGED NATIVE SHAPE CONTROL ONLY; all target USER triggers temporarily bypassed.
-- FK/CHECK/UNIQUE/internal RI triggers remain active. Roll back every mutation and trigger DDL.
BEGIN;
SET LOCAL search_path=pg_catalog;
SET LOCAL log_statement='none';
SET LOCAL log_min_error_statement='panic';
ALTER TABLE "app"."track_subscription_events" DISABLE TRIGGER "enrollment_commit";
ALTER TABLE "app"."track_subscription_events" DISABLE TRIGGER "physical_guard";
SAVEPOINT native_control;
WITH changed AS (INSERT INTO "app"."track_subscription_events"("id","subscription_id","plan_id","user_id","name","from_status","to_status","provider","provider_event_id","metadata","created_at","mutation_transaction_id") VALUES ('b7cd8849-e7a6-59ef-9948-7c1448cf52d6'::pg_catalog.uuid,NULL::pg_catalog.uuid,NULL::pg_catalog.uuid,'e2be55a6-0aa0-58fb-8d45-735624b37743'::pg_catalog.uuid,'native-acl-78154aca25752e8b72f3bb14'::pg_catalog.text,NULL::app.track_subscription_status,NULL::app.track_subscription_status,NULL::app.track_billing_provider,NULL::pg_catalog.text,NULL::pg_catalog.jsonb,'2026-11-17T00:00:00Z'::pg_catalog.timestamptz,'native-acl-setup-transaction'::pg_catalog.text) RETURNING 1) SELECT count(*)=1 AS native_insert_one FROM changed;
ROLLBACK TO SAVEPOINT native_control;
WITH changed AS (UPDATE "app"."track_subscription_events" SET "id"='477ab2c9-2e2e-58ca-bd5e-9bf1963c1d11'::pg_catalog.uuid WHERE "id"='477ab2c9-2e2e-58ca-bd5e-9bf1963c1d11'::pg_catalog.uuid RETURNING 1) SELECT count(*)=1 AS native_update_one FROM changed;
ROLLBACK TO SAVEPOINT native_control;
WITH changed AS (DELETE FROM "app"."track_subscription_events" WHERE "id"='477ab2c9-2e2e-58ca-bd5e-9bf1963c1d11'::pg_catalog.uuid RETURNING 1) SELECT count(*)=1 AS native_delete_one FROM changed;
ROLLBACK TO SAVEPOINT native_control;
ROLLBACK;
SELECT jsonb_build_object('control','native-control-TrackSubscriptionEvent','all_declared_user_triggers_restored',NOT EXISTS(SELECT 1 FROM (VALUES ('app.track_subscription_events','enrollment_commit','O'),('app.track_subscription_events','physical_guard','O')) e(table_name,name,enabled) LEFT JOIN pg_trigger t ON t.tgrelid=to_regclass(e.table_name) AND t.tgname=e.name WHERE t.oid IS NULL OR t.tgisinternal OR t.tgenabled::text IS DISTINCT FROM e.enabled));
