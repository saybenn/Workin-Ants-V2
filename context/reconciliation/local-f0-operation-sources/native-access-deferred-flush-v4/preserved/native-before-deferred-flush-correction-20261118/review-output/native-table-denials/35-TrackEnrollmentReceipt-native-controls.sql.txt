-- PRIVILEGED NATIVE SHAPE CONTROL ONLY; all target USER triggers temporarily bypassed.
-- FK/CHECK/UNIQUE/internal RI triggers remain active. Roll back every mutation and trigger DDL.
BEGIN;
SET LOCAL search_path=pg_catalog;
SET LOCAL log_statement='none';
SET LOCAL log_min_error_statement='panic';
ALTER TABLE "app"."track_enrollment_receipt" DISABLE TRIGGER "enrollment_commit";
ALTER TABLE "app"."track_enrollment_receipt" DISABLE TRIGGER "physical_guard";
SAVEPOINT native_control;
WITH changed AS (INSERT INTO "app"."track_enrollment_receipt"("id","user_id","track","profile_id","source_owner","source_creation_revision","selection_id","selection_revision","semantic_key","fingerprint","result_code","effect_receipt_id","created_at","mutation_transaction_id") VALUES ('f25adf2f-592e-5ba7-abd5-92c08764b700'::pg_catalog.uuid,'c97555c4-e85d-53e5-8435-9979588fd1ae'::pg_catalog.uuid,'customer'::app.account_track,'54aed17a-a385-50e8-83c2-50acc1ae86e3'::pg_catalog.uuid,'native-acl-3008810452ea9cf8eef97079'::pg_catalog.text,'0'::pg_catalog.int8,'7417e1d4-9d74-5e40-8190-1247cfc96fa0'::pg_catalog.uuid,'0'::pg_catalog.int8,'native-acl-a7609f2f517edf99adae2b86'::pg_catalog.text,'8341c7a4ccde287f5bce578ee1433d3800cf28cd2a230a8ee89327a7cba7acbf'::pg_catalog.bpchar,'native-acl-4a0d0588967e310265db5257'::pg_catalog.text,'022f3d1b-86b8-5ecd-8d40-c4e271e3b025'::pg_catalog.uuid,'2026-11-17T00:00:00Z'::pg_catalog.timestamptz,'native-acl-setup-transaction'::pg_catalog.text) RETURNING 1) SELECT count(*)=1 AS native_insert_one FROM changed;
ROLLBACK TO SAVEPOINT native_control;
WITH changed AS (UPDATE "app"."track_enrollment_receipt" SET "id"='9eeefad7-2b05-550e-aaec-72f267ac473c'::pg_catalog.uuid WHERE "id"='9eeefad7-2b05-550e-aaec-72f267ac473c'::pg_catalog.uuid RETURNING 1) SELECT count(*)=1 AS native_update_one FROM changed;
ROLLBACK TO SAVEPOINT native_control;
WITH changed AS (DELETE FROM "app"."track_enrollment_receipt" WHERE "id"='9eeefad7-2b05-550e-aaec-72f267ac473c'::pg_catalog.uuid RETURNING 1) SELECT count(*)=1 AS native_delete_one FROM changed;
ROLLBACK TO SAVEPOINT native_control;
ROLLBACK;
SELECT jsonb_build_object('control','native-control-TrackEnrollmentReceipt','all_declared_user_triggers_restored',NOT EXISTS(SELECT 1 FROM (VALUES ('app.track_enrollment_receipt','enrollment_commit','O'),('app.track_enrollment_receipt','physical_guard','O')) e(table_name,name,enabled) LEFT JOIN pg_trigger t ON t.tgrelid=to_regclass(e.table_name) AND t.tgname=e.name WHERE t.oid IS NULL OR t.tgisinternal OR t.tgenabled::text IS DISTINCT FROM e.enabled));
