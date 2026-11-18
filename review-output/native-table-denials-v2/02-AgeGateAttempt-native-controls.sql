-- PRIVILEGED NATIVE SHAPE CONTROL ONLY; all target USER triggers temporarily bypassed.
-- FK/CHECK/UNIQUE/internal RI triggers remain active. Roll back every mutation and trigger DDL.
BEGIN;
SET LOCAL search_path=pg_catalog;
SET LOCAL log_statement='none';
SET LOCAL log_min_error_statement='panic';
ALTER TABLE "app"."age_gate_attempts" DISABLE TRIGGER "owner_commit";
ALTER TABLE "app"."age_gate_attempts" DISABLE TRIGGER "physical_guard";
SAVEPOINT native_control;
WITH changed AS (INSERT INTO "app"."age_gate_attempts"("id","user_id","ip_hash","device_hash","region","result","birth_year","age_band","blocked_until","created_at","mutation_transaction_id") VALUES ('d37e8c18-7364-5c1a-bd05-924d6630a173'::pg_catalog.uuid,NULL::pg_catalog.uuid,NULL::pg_catalog.text,NULL::pg_catalog.text,NULL::pg_catalog.text,'allowed'::app.age_gate_result,NULL::pg_catalog.int4,NULL::pg_catalog.text,NULL::pg_catalog.timestamptz,'2026-11-17T00:00:00Z'::pg_catalog.timestamptz,'native-acl-setup-transaction'::pg_catalog.text) RETURNING 1) SELECT count(*)=1 AS native_insert_one FROM changed;
ROLLBACK TO SAVEPOINT native_control;
WITH changed AS (UPDATE "app"."age_gate_attempts" SET "id"='fed3a5b0-1787-53de-8605-28dd0e1a2220'::pg_catalog.uuid WHERE "id"='fed3a5b0-1787-53de-8605-28dd0e1a2220'::pg_catalog.uuid RETURNING 1) SELECT count(*)=1 AS native_update_one FROM changed;
ROLLBACK TO SAVEPOINT native_control;
WITH changed AS (DELETE FROM "app"."age_gate_attempts" WHERE "id"='fed3a5b0-1787-53de-8605-28dd0e1a2220'::pg_catalog.uuid RETURNING 1) SELECT count(*)=1 AS native_delete_one FROM changed;
ROLLBACK TO SAVEPOINT native_control;
ROLLBACK;
SELECT jsonb_build_object('control','native-control-AgeGateAttempt','all_declared_user_triggers_restored',NOT EXISTS(SELECT 1 FROM (VALUES ('app.age_gate_attempts','owner_commit','O'),('app.age_gate_attempts','physical_guard','O')) e(table_name,name,enabled) LEFT JOIN pg_trigger t ON t.tgrelid=to_regclass(e.table_name) AND t.tgname=e.name WHERE t.oid IS NULL OR t.tgisinternal OR t.tgenabled::text IS DISTINCT FROM e.enabled));
