-- PRIVILEGED NATIVE SHAPE CONTROL ONLY; all target USER triggers temporarily bypassed.
-- FK/CHECK/UNIQUE/internal RI triggers remain active. Roll back every mutation and trigger DDL.
BEGIN;
SET LOCAL search_path=pg_catalog;
SET LOCAL log_statement='none';
SET LOCAL log_min_error_statement='panic';
ALTER TABLE "app"."privacy_restore_marker" DISABLE TRIGGER "owner_commit";
ALTER TABLE "app"."privacy_restore_marker" DISABLE TRIGGER "physical_guard";
ALTER TABLE "app"."privacy_restore_marker" DISABLE TRIGGER "privacy_restore";
SAVEPOINT native_control;
WITH changed AS (INSERT INTO "app"."privacy_restore_marker"("id","owner_module_id","target_kind","source_id","generation","action","source_receipt_id","restore_point_ref","applied_at","created_at","revision","mutation_transaction_id") VALUES ('297f8698-4f61-5bca-95f8-14e79087aa2b'::pg_catalog.uuid,'native-acl-4fe861dcb302e5fc89a6e135'::pg_catalog.text,'native-acl-521ca14dd2674eb02a0c8620'::pg_catalog.text,'native-acl-08f2af72a944fb0ff950beab'::pg_catalog.text,'0'::pg_catalog.int8,'export'::app.privacy_action_kind,'5a843917-ae56-5739-8771-e703108ef221'::pg_catalog.uuid,NULL::pg_catalog.text,NULL::pg_catalog.timestamptz,'2026-11-17T00:00:00Z'::pg_catalog.timestamptz,'0'::pg_catalog.int8,'native-acl-setup-transaction'::pg_catalog.text) RETURNING 1) SELECT count(*)=1 AS native_insert_one FROM changed;
ROLLBACK TO SAVEPOINT native_control;
WITH changed AS (UPDATE "app"."privacy_restore_marker" SET "id"='f4f64db4-e460-5f50-ae58-2bd58d17811c'::pg_catalog.uuid WHERE "id"='f4f64db4-e460-5f50-ae58-2bd58d17811c'::pg_catalog.uuid RETURNING 1) SELECT count(*)=1 AS native_update_one FROM changed;
ROLLBACK TO SAVEPOINT native_control;
WITH changed AS (DELETE FROM "app"."privacy_restore_marker" WHERE "id"='f4f64db4-e460-5f50-ae58-2bd58d17811c'::pg_catalog.uuid RETURNING 1) SELECT count(*)=1 AS native_delete_one FROM changed;
ROLLBACK TO SAVEPOINT native_control;
ROLLBACK;
SELECT jsonb_build_object('control','native-control-PrivacyRestoreMarker','all_declared_user_triggers_restored',NOT EXISTS(SELECT 1 FROM (VALUES ('app.privacy_restore_marker','owner_commit','O'),('app.privacy_restore_marker','physical_guard','O'),('app.privacy_restore_marker','privacy_restore','O')) e(table_name,name,enabled) LEFT JOIN pg_trigger t ON t.tgrelid=to_regclass(e.table_name) AND t.tgname=e.name WHERE t.oid IS NULL OR t.tgisinternal OR t.tgenabled::text IS DISTINCT FROM e.enabled));
