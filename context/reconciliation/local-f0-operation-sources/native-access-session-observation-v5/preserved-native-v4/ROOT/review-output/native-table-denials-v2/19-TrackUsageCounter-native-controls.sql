-- PRIVILEGED NATIVE SHAPE CONTROL ONLY; all target USER triggers temporarily bypassed.
-- FK/CHECK/UNIQUE/internal RI triggers remain active. Roll back every mutation and trigger DDL.
BEGIN;
SET LOCAL search_path=pg_catalog;
SET LOCAL log_statement='none';
SET LOCAL log_min_error_statement='panic';
ALTER TABLE "app"."track_usage_counters" DISABLE TRIGGER "owner_commit";
ALTER TABLE "app"."track_usage_counters" DISABLE TRIGGER "physical_guard";
ALTER TABLE "app"."track_usage_counters" DISABLE TRIGGER "usage_adapter_gate";
SAVEPOINT native_control;
WITH changed AS (INSERT INTO "app"."track_usage_counters"("id","user_id","subscription_id","entitlement_grant_id","entitlement_id","track","period","customer_profile_id","candidate_profile_id","professional_profile_id","period_start","period_end","used_quantity","limit_quantity","updated_at","created_at","revision","source_revision","mutation_transaction_id") VALUES ('3f196875-2bdb-58d9-adf9-bb6bb9c6e9b7'::pg_catalog.uuid,'3d42e555-dadf-5e69-9029-316de7bde869'::pg_catalog.uuid,NULL::pg_catalog.uuid,NULL::pg_catalog.uuid,'6ac8d6cf-7f8f-5a11-bc83-4e59c894d704'::pg_catalog.uuid,'customer'::app.account_track,'once'::app.track_usage_period,NULL::pg_catalog.uuid,NULL::pg_catalog.uuid,NULL::pg_catalog.uuid,'2026-11-17T00:00:00Z'::pg_catalog.timestamptz,'2026-11-18T00:00:00Z'::pg_catalog.timestamptz,'0'::pg_catalog.int4,NULL::pg_catalog.int4,'2026-11-17T00:00:00Z'::pg_catalog.timestamptz,'2026-11-17T00:00:00Z'::pg_catalog.timestamptz,'0'::pg_catalog.int8,'0'::pg_catalog.int8,'native-acl-setup-transaction'::pg_catalog.text) RETURNING 1) SELECT count(*)=1 AS native_insert_one FROM changed;
ROLLBACK TO SAVEPOINT native_control;
WITH changed AS (UPDATE "app"."track_usage_counters" SET "id"='d184a890-2be0-5d50-ad54-1297d6724531'::pg_catalog.uuid WHERE "id"='d184a890-2be0-5d50-ad54-1297d6724531'::pg_catalog.uuid RETURNING 1) SELECT count(*)=1 AS native_update_one FROM changed;
ROLLBACK TO SAVEPOINT native_control;
WITH changed AS (DELETE FROM "app"."track_usage_counters" WHERE "id"='d184a890-2be0-5d50-ad54-1297d6724531'::pg_catalog.uuid RETURNING 1) SELECT count(*)=1 AS native_delete_one FROM changed;
ROLLBACK TO SAVEPOINT native_control;
ROLLBACK;
SELECT jsonb_build_object('control','native-control-TrackUsageCounter','all_declared_user_triggers_restored',NOT EXISTS(SELECT 1 FROM (VALUES ('app.track_usage_counters','owner_commit','O'),('app.track_usage_counters','physical_guard','O'),('app.track_usage_counters','usage_adapter_gate','O')) e(table_name,name,enabled) LEFT JOIN pg_trigger t ON t.tgrelid=to_regclass(e.table_name) AND t.tgname=e.name WHERE t.oid IS NULL OR t.tgisinternal OR t.tgenabled::text IS DISTINCT FROM e.enabled));
