-- PRIVILEGED NATIVE SHAPE CONTROL ONLY; all target USER triggers temporarily bypassed.
-- FK/CHECK/UNIQUE/internal RI triggers remain active. Roll back every mutation and trigger DDL.
BEGIN;
SET LOCAL search_path=pg_catalog;
SET LOCAL log_statement='none';
SET LOCAL log_min_error_statement='panic';
ALTER TABLE "app"."track_base_selection" DISABLE TRIGGER "enrollment_commit";
ALTER TABLE "app"."track_base_selection" DISABLE TRIGGER "owner_commit";
ALTER TABLE "app"."track_base_selection" DISABLE TRIGGER "physical_guard";
ALTER TABLE "app"."track_base_selection" DISABLE TRIGGER "selection_binding";
SAVEPOINT native_control;
WITH changed AS (INSERT INTO "app"."track_base_selection"("id","user_id","track","customer_profile_id","candidate_profile_id","professional_profile_id","subscription_id","revision","source_generation","created_at","mutation_transaction_id") VALUES ('d97eeaca-8261-5e52-b2ba-1fc901133343'::pg_catalog.uuid,'b9bb35cc-27ae-5e38-98d5-d1e35c2bfa7f'::pg_catalog.uuid,'customer'::app.account_track,NULL::pg_catalog.uuid,NULL::pg_catalog.uuid,NULL::pg_catalog.uuid,'001261ce-759d-5711-9198-557895541b3b'::pg_catalog.uuid,'0'::pg_catalog.int8,'0'::pg_catalog.int8,'2026-11-17T00:00:00Z'::pg_catalog.timestamptz,'native-acl-setup-transaction'::pg_catalog.text) RETURNING 1) SELECT count(*)=1 AS native_insert_one FROM changed;
ROLLBACK TO SAVEPOINT native_control;
WITH changed AS (UPDATE "app"."track_base_selection" SET "id"='f997b61e-4875-5865-81ad-b8285ac1cef0'::pg_catalog.uuid WHERE "id"='f997b61e-4875-5865-81ad-b8285ac1cef0'::pg_catalog.uuid RETURNING 1) SELECT count(*)=1 AS native_update_one FROM changed;
ROLLBACK TO SAVEPOINT native_control;
WITH changed AS (DELETE FROM "app"."track_base_selection" WHERE "id"='f997b61e-4875-5865-81ad-b8285ac1cef0'::pg_catalog.uuid RETURNING 1) SELECT count(*)=1 AS native_delete_one FROM changed;
ROLLBACK TO SAVEPOINT native_control;
ROLLBACK;
SELECT jsonb_build_object('control','native-control-TrackBaseSelection','all_declared_user_triggers_restored',NOT EXISTS(SELECT 1 FROM (VALUES ('app.track_base_selection','enrollment_commit','O'),('app.track_base_selection','owner_commit','O'),('app.track_base_selection','physical_guard','O'),('app.track_base_selection','selection_binding','O')) e(table_name,name,enabled) LEFT JOIN pg_trigger t ON t.tgrelid=to_regclass(e.table_name) AND t.tgname=e.name WHERE t.oid IS NULL OR t.tgisinternal OR t.tgenabled::text IS DISTINCT FROM e.enabled));
