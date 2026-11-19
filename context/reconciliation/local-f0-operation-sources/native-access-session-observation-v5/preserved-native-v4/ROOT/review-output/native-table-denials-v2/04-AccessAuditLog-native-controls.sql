-- PRIVILEGED NATIVE SHAPE CONTROL ONLY; all target USER triggers temporarily bypassed.
-- FK/CHECK/UNIQUE/internal RI triggers remain active. Roll back every mutation and trigger DDL.
BEGIN;
SET LOCAL search_path=pg_catalog;
SET LOCAL log_statement='none';
SET LOCAL log_min_error_statement='panic';
ALTER TABLE "app"."access_audit_logs" DISABLE TRIGGER "owner_commit";
ALTER TABLE "app"."access_audit_logs" DISABLE TRIGGER "physical_guard";
SAVEPOINT native_control;
WITH changed AS (INSERT INTO "app"."access_audit_logs"("id","actor_user_id","target_type","target_id","action","sensitivity","access_decision","request_id","ip_hash","user_agent","previous_hash","entry_hash","created_at","mutation_transaction_id") VALUES ('0c07261b-bf9d-5379-a267-2c18fc6631e2'::pg_catalog.uuid,NULL::pg_catalog.uuid,'native-acl-138114460a6c2972fec68c65'::pg_catalog.text,'3685b557-69e8-5940-8f5f-0aff8a33223a'::pg_catalog.uuid,'file_read'::app.access_audit_action,'normal'::app.data_sensitivity,NULL::app.healthcare_access_decision,NULL::pg_catalog.text,NULL::pg_catalog.text,NULL::pg_catalog.text,NULL::pg_catalog.text,NULL::pg_catalog.text,'2026-11-17T00:00:00Z'::pg_catalog.timestamptz,'native-acl-setup-transaction'::pg_catalog.text) RETURNING 1) SELECT count(*)=1 AS native_insert_one FROM changed;
ROLLBACK TO SAVEPOINT native_control;
WITH changed AS (UPDATE "app"."access_audit_logs" SET "id"='2591049c-35d4-5206-b07d-4725ebffe6bd'::pg_catalog.uuid WHERE "id"='2591049c-35d4-5206-b07d-4725ebffe6bd'::pg_catalog.uuid RETURNING 1) SELECT count(*)=1 AS native_update_one FROM changed;
ROLLBACK TO SAVEPOINT native_control;
WITH changed AS (DELETE FROM "app"."access_audit_logs" WHERE "id"='2591049c-35d4-5206-b07d-4725ebffe6bd'::pg_catalog.uuid RETURNING 1) SELECT count(*)=1 AS native_delete_one FROM changed;
ROLLBACK TO SAVEPOINT native_control;
ROLLBACK;
SELECT jsonb_build_object('control','native-control-AccessAuditLog','all_declared_user_triggers_restored',NOT EXISTS(SELECT 1 FROM (VALUES ('app.access_audit_logs','owner_commit','O'),('app.access_audit_logs','physical_guard','O')) e(table_name,name,enabled) LEFT JOIN pg_trigger t ON t.tgrelid=to_regclass(e.table_name) AND t.tgname=e.name WHERE t.oid IS NULL OR t.tgisinternal OR t.tgenabled::text IS DISTINCT FROM e.enabled));
