-- PRIVILEGED NATIVE SHAPE CONTROL ONLY; all target USER triggers temporarily bypassed.
-- FK/CHECK/UNIQUE/internal RI triggers remain active. Roll back every mutation and trigger DDL.
BEGIN;
SET LOCAL search_path=pg_catalog;
SET LOCAL log_statement='none';
SET LOCAL log_min_error_statement='panic';
ALTER TABLE "app"."track_entitlement_grants" DISABLE TRIGGER "enrollment_commit";
ALTER TABLE "app"."track_entitlement_grants" DISABLE TRIGGER "grant_binding";
ALTER TABLE "app"."track_entitlement_grants" DISABLE TRIGGER "owner_commit";
ALTER TABLE "app"."track_entitlement_grants" DISABLE TRIGGER "physical_guard";
SAVEPOINT native_control;
WITH changed AS (INSERT INTO "app"."track_entitlement_grants"("id","user_id","subscription_id","entitlement_id","track","customer_profile_id","candidate_profile_id","professional_profile_id","status","value_type","boolean_value","int_value","decimal_value","string_value","json_value","starts_at","expires_at","revoked_at","revoke_reason","source_plan_id","source_event_id","created_at","updated_at","revision","mutation_transaction_id") VALUES ('edf112c9-bd08-5ab3-b03a-6d952ff2caa6'::pg_catalog.uuid,'e0a1ea56-9279-5548-b949-8c2cae567ec8'::pg_catalog.uuid,NULL::pg_catalog.uuid,'39019043-4e9b-554a-8d18-0bbd7eac22a3'::pg_catalog.uuid,'customer'::app.account_track,NULL::pg_catalog.uuid,NULL::pg_catalog.uuid,NULL::pg_catalog.uuid,'active'::app.track_entitlement_grant_status,'boolean'::app.track_entitlement_value_type,true,NULL::pg_catalog.int4,NULL::pg_catalog.float8,NULL::pg_catalog.text,NULL::pg_catalog.jsonb,NULL::pg_catalog.timestamptz,NULL::pg_catalog.timestamptz,NULL::pg_catalog.timestamptz,NULL::pg_catalog.text,NULL::pg_catalog.uuid,NULL::pg_catalog.uuid,'2026-11-17T00:00:00Z'::pg_catalog.timestamptz,'2026-11-17T00:00:00Z'::pg_catalog.timestamptz,'0'::pg_catalog.int8,'native-acl-setup-transaction'::pg_catalog.text) RETURNING 1) SELECT count(*)=1 AS native_insert_one FROM changed;
ROLLBACK TO SAVEPOINT native_control;
WITH changed AS (UPDATE "app"."track_entitlement_grants" SET "id"='a366bf4f-e520-5cb0-b3cf-a77afdbf3f21'::pg_catalog.uuid WHERE "id"='a366bf4f-e520-5cb0-b3cf-a77afdbf3f21'::pg_catalog.uuid RETURNING 1) SELECT count(*)=1 AS native_update_one FROM changed;
ROLLBACK TO SAVEPOINT native_control;
WITH changed AS (DELETE FROM "app"."track_entitlement_grants" WHERE "id"='a366bf4f-e520-5cb0-b3cf-a77afdbf3f21'::pg_catalog.uuid RETURNING 1) SELECT count(*)=1 AS native_delete_one FROM changed;
ROLLBACK TO SAVEPOINT native_control;
ROLLBACK;
SELECT jsonb_build_object('control','native-control-TrackEntitlementGrant','all_declared_user_triggers_restored',NOT EXISTS(SELECT 1 FROM (VALUES ('app.track_entitlement_grants','enrollment_commit','O'),('app.track_entitlement_grants','grant_binding','O'),('app.track_entitlement_grants','owner_commit','O'),('app.track_entitlement_grants','physical_guard','O')) e(table_name,name,enabled) LEFT JOIN pg_trigger t ON t.tgrelid=to_regclass(e.table_name) AND t.tgname=e.name WHERE t.oid IS NULL OR t.tgisinternal OR t.tgenabled::text IS DISTINCT FROM e.enabled));
