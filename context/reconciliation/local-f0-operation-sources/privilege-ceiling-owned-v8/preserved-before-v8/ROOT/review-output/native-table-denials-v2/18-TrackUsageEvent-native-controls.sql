-- PRIVILEGED NATIVE SHAPE CONTROL ONLY; all target USER triggers temporarily bypassed.
-- FK/CHECK/UNIQUE/internal RI triggers remain active. Roll back every mutation and trigger DDL.
BEGIN;
SET LOCAL search_path=pg_catalog;
SET LOCAL log_statement='none';
SET LOCAL log_min_error_statement='panic';
ALTER TABLE "app"."track_usage_events" DISABLE TRIGGER "owner_commit";
ALTER TABLE "app"."track_usage_events" DISABLE TRIGGER "physical_guard";
ALTER TABLE "app"."track_usage_events" DISABLE TRIGGER "usage_adapter_gate";
SAVEPOINT native_control;
WITH changed AS (INSERT INTO "app"."track_usage_events"("id","user_id","subscription_id","entitlement_grant_id","entitlement_id","track","type","customer_profile_id","candidate_profile_id","professional_profile_id","target_type","target_id","quantity","occurred_at","metadata","semantic_effect_key","source_revision","source_owner","source_id","accepted_at","period_start","period_end","effect_receipt_id","mutation_transaction_id") VALUES ('3835c36c-c4cf-50ed-aa80-3b4ece03819a'::pg_catalog.uuid,'abaf80af-839b-5916-be61-0897713ba118'::pg_catalog.uuid,NULL::pg_catalog.uuid,NULL::pg_catalog.uuid,NULL::pg_catalog.uuid,'customer'::app.account_track,'job_application_submitted'::app.track_usage_event_type,NULL::pg_catalog.uuid,NULL::pg_catalog.uuid,NULL::pg_catalog.uuid,NULL::pg_catalog.text,NULL::pg_catalog.uuid,'1'::pg_catalog.int4,'2026-11-17T00:00:00Z'::pg_catalog.timestamptz,NULL::pg_catalog.jsonb,'native-acl-83db25918bf6fc61a926aa37'::pg_catalog.text,'0'::pg_catalog.int8,'native-acl-c86d16edabfa887aee2a0bfc'::pg_catalog.text,'native-acl-b78caf2c8739bd294f2702b1'::pg_catalog.text,'2026-11-17T00:00:00Z'::pg_catalog.timestamptz,'2026-11-17T00:00:00Z'::pg_catalog.timestamptz,'2026-11-18T00:00:00Z'::pg_catalog.timestamptz,'a7790c32-dbe2-5d48-8a37-3359b38b6c7d'::pg_catalog.uuid,'native-acl-setup-transaction'::pg_catalog.text) RETURNING 1) SELECT count(*)=1 AS native_insert_one FROM changed;
ROLLBACK TO SAVEPOINT native_control;
WITH changed AS (UPDATE "app"."track_usage_events" SET "id"='9d0f416e-fab9-5a36-a967-17bb956916d1'::pg_catalog.uuid WHERE "id"='9d0f416e-fab9-5a36-a967-17bb956916d1'::pg_catalog.uuid RETURNING 1) SELECT count(*)=1 AS native_update_one FROM changed;
ROLLBACK TO SAVEPOINT native_control;
WITH changed AS (DELETE FROM "app"."track_usage_events" WHERE "id"='9d0f416e-fab9-5a36-a967-17bb956916d1'::pg_catalog.uuid RETURNING 1) SELECT count(*)=1 AS native_delete_one FROM changed;
ROLLBACK TO SAVEPOINT native_control;
ROLLBACK;
SELECT jsonb_build_object('control','native-control-TrackUsageEvent','all_declared_user_triggers_restored',NOT EXISTS(SELECT 1 FROM (VALUES ('app.track_usage_events','owner_commit','O'),('app.track_usage_events','physical_guard','O'),('app.track_usage_events','usage_adapter_gate','O')) e(table_name,name,enabled) LEFT JOIN pg_trigger t ON t.tgrelid=to_regclass(e.table_name) AND t.tgname=e.name WHERE t.oid IS NULL OR t.tgisinternal OR t.tgenabled::text IS DISTINCT FROM e.enabled));
