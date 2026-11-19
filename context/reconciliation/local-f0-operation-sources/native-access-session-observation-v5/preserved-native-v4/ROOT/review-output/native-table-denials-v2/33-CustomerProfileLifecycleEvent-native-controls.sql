-- PRIVILEGED NATIVE SHAPE CONTROL ONLY; all target USER triggers temporarily bypassed.
-- FK/CHECK/UNIQUE/internal RI triggers remain active. Roll back every mutation and trigger DDL.
BEGIN;
SET LOCAL search_path=pg_catalog;
SET LOCAL log_statement='none';
SET LOCAL log_min_error_statement='panic';
ALTER TABLE "app"."customer_profile_lifecycle_event" DISABLE TRIGGER "exact_customer_history";
ALTER TABLE "app"."customer_profile_lifecycle_event" DISABLE TRIGGER "physical_guard";
SAVEPOINT native_control;
WITH changed AS (INSERT INTO "app"."customer_profile_lifecycle_event"("id","customer_profile_id","command_receipt_id","source_revision","from_status","to_status","name","actor_user_id","created_at","mutation_transaction_id") VALUES ('1cf8e5b9-ae62-5655-9aa6-d2f267f4217f'::pg_catalog.uuid,'e633cfaa-85bd-598b-b9be-a089640093c8'::pg_catalog.uuid,'99214d11-13b4-5c8b-80d9-4e648a8c094b'::pg_catalog.uuid,'0'::pg_catalog.int8,NULL::app.profile_status,'active'::app.profile_status,'customer.lifecycle_changed.v1'::pg_catalog.text,'7ab4c614-56b1-5919-a94a-4900b857fa94'::pg_catalog.uuid,'2026-11-17T00:00:00Z'::pg_catalog.timestamptz,'native-acl-setup-transaction'::pg_catalog.text) RETURNING 1) SELECT count(*)=1 AS native_insert_one FROM changed;
ROLLBACK TO SAVEPOINT native_control;
WITH changed AS (UPDATE "app"."customer_profile_lifecycle_event" SET "id"='3191d0af-0ac2-5bc3-8835-d97ea3f8a30e'::pg_catalog.uuid WHERE "id"='3191d0af-0ac2-5bc3-8835-d97ea3f8a30e'::pg_catalog.uuid RETURNING 1) SELECT count(*)=1 AS native_update_one FROM changed;
ROLLBACK TO SAVEPOINT native_control;
WITH changed AS (DELETE FROM "app"."customer_profile_lifecycle_event" WHERE "id"='3191d0af-0ac2-5bc3-8835-d97ea3f8a30e'::pg_catalog.uuid RETURNING 1) SELECT count(*)=1 AS native_delete_one FROM changed;
ROLLBACK TO SAVEPOINT native_control;
ROLLBACK;
SELECT jsonb_build_object('control','native-control-CustomerProfileLifecycleEvent','all_declared_user_triggers_restored',NOT EXISTS(SELECT 1 FROM (VALUES ('app.customer_profile_lifecycle_event','exact_customer_history','O'),('app.customer_profile_lifecycle_event','physical_guard','O')) e(table_name,name,enabled) LEFT JOIN pg_trigger t ON t.tgrelid=to_regclass(e.table_name) AND t.tgname=e.name WHERE t.oid IS NULL OR t.tgisinternal OR t.tgenabled::text IS DISTINCT FROM e.enabled));
