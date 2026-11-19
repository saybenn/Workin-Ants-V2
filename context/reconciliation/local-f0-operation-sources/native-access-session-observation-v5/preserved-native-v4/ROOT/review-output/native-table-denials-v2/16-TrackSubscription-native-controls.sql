-- PRIVILEGED NATIVE SHAPE CONTROL ONLY; all target USER triggers temporarily bypassed.
-- FK/CHECK/UNIQUE/internal RI triggers remain active. Roll back every mutation and trigger DDL.
BEGIN;
SET LOCAL search_path=pg_catalog;
SET LOCAL log_statement='none';
SET LOCAL log_min_error_statement='panic';
ALTER TABLE "app"."track_subscriptions" DISABLE TRIGGER "enrollment_commit";
ALTER TABLE "app"."track_subscriptions" DISABLE TRIGGER "owner_commit";
ALTER TABLE "app"."track_subscriptions" DISABLE TRIGGER "physical_guard";
ALTER TABLE "app"."track_subscriptions" DISABLE TRIGGER "subscription_binding";
SAVEPOINT native_control;
WITH changed AS (INSERT INTO "app"."track_subscriptions"("id","user_id","plan_id","track","customer_profile_id","candidate_profile_id","professional_profile_id","status","provider","provider_customer_id","provider_subscription_id","provider_price_id","current_period_start","current_period_end","trial_ends_at","cancelled_at","ended_at","created_at","updated_at","revision","mutation_transaction_id") VALUES ('c5c2ade7-ba70-5b3b-85a4-532e517f72a9'::pg_catalog.uuid,'092ed88f-5655-5d2d-aeb4-962fbd07eb6b'::pg_catalog.uuid,'843c2ac7-6a96-5f5f-8491-204ef2d98baa'::pg_catalog.uuid,'customer'::app.account_track,NULL::pg_catalog.uuid,NULL::pg_catalog.uuid,NULL::pg_catalog.uuid,'active'::app.track_subscription_status,'none'::app.track_billing_provider,NULL::pg_catalog.text,NULL::pg_catalog.text,NULL::pg_catalog.text,NULL::pg_catalog.timestamptz,NULL::pg_catalog.timestamptz,NULL::pg_catalog.timestamptz,NULL::pg_catalog.timestamptz,NULL::pg_catalog.timestamptz,'2026-11-17T00:00:00Z'::pg_catalog.timestamptz,'2026-11-17T00:00:00Z'::pg_catalog.timestamptz,'0'::pg_catalog.int8,'native-acl-setup-transaction'::pg_catalog.text) RETURNING 1) SELECT count(*)=1 AS native_insert_one FROM changed;
ROLLBACK TO SAVEPOINT native_control;
WITH changed AS (UPDATE "app"."track_subscriptions" SET "id"='23bf79b6-6c20-594c-96a7-b07e23db9ee0'::pg_catalog.uuid WHERE "id"='23bf79b6-6c20-594c-96a7-b07e23db9ee0'::pg_catalog.uuid RETURNING 1) SELECT count(*)=1 AS native_update_one FROM changed;
ROLLBACK TO SAVEPOINT native_control;
WITH changed AS (DELETE FROM "app"."track_subscriptions" WHERE "id"='23bf79b6-6c20-594c-96a7-b07e23db9ee0'::pg_catalog.uuid RETURNING 1) SELECT count(*)=1 AS native_delete_one FROM changed;
ROLLBACK TO SAVEPOINT native_control;
ROLLBACK;
SELECT jsonb_build_object('control','native-control-TrackSubscription','all_declared_user_triggers_restored',NOT EXISTS(SELECT 1 FROM (VALUES ('app.track_subscriptions','enrollment_commit','O'),('app.track_subscriptions','owner_commit','O'),('app.track_subscriptions','physical_guard','O'),('app.track_subscriptions','subscription_binding','O')) e(table_name,name,enabled) LEFT JOIN pg_trigger t ON t.tgrelid=to_regclass(e.table_name) AND t.tgname=e.name WHERE t.oid IS NULL OR t.tgisinternal OR t.tgenabled::text IS DISTINCT FROM e.enabled));
