-- PRIVILEGED NATIVE SHAPE CONTROL ONLY; all target USER triggers temporarily bypassed.
-- FK/CHECK/UNIQUE/internal RI triggers remain active. Roll back every mutation and trigger DDL.
BEGIN;
SET LOCAL search_path=pg_catalog;
SET LOCAL log_statement='none';
SET LOCAL log_min_error_statement='panic';
ALTER TABLE "app"."privacy_requests" DISABLE TRIGGER "owner_commit";
ALTER TABLE "app"."privacy_requests" DISABLE TRIGGER "physical_guard";
ALTER TABLE "app"."privacy_requests" DISABLE TRIGGER "privacy_request";
SAVEPOINT native_control;
WITH changed AS (INSERT INTO "app"."privacy_requests"("id","user_id","type","status","requested_at","verified_at","due_at","completed_at","rejection_reason","admin_note","created_at","updated_at","revision","privacy_generation","instruction_generation","mutation_transaction_id") VALUES ('a4dfc700-cae1-5d9f-b604-b420d170a3e3'::pg_catalog.uuid,'a3b8fb0a-7da4-513b-972b-2ce3e165fdf6'::pg_catalog.uuid,'access'::app.privacy_request_type,'submitted'::app.privacy_request_status,'2026-11-17T00:00:00Z'::pg_catalog.timestamptz,NULL::pg_catalog.timestamptz,NULL::pg_catalog.timestamptz,NULL::pg_catalog.timestamptz,NULL::pg_catalog.text,NULL::pg_catalog.text,'2026-11-17T00:00:00Z'::pg_catalog.timestamptz,'2026-11-17T00:00:00Z'::pg_catalog.timestamptz,'0'::pg_catalog.int8,'0'::pg_catalog.int8,'0'::pg_catalog.int8,'native-acl-setup-transaction'::pg_catalog.text) RETURNING 1) SELECT count(*)=1 AS native_insert_one FROM changed;
ROLLBACK TO SAVEPOINT native_control;
WITH changed AS (UPDATE "app"."privacy_requests" SET "id"='a429a294-38dc-55fd-971b-b97ec04ef5cf'::pg_catalog.uuid WHERE "id"='a429a294-38dc-55fd-971b-b97ec04ef5cf'::pg_catalog.uuid RETURNING 1) SELECT count(*)=1 AS native_update_one FROM changed;
ROLLBACK TO SAVEPOINT native_control;
WITH changed AS (DELETE FROM "app"."privacy_requests" WHERE "id"='a429a294-38dc-55fd-971b-b97ec04ef5cf'::pg_catalog.uuid RETURNING 1) SELECT count(*)=1 AS native_delete_one FROM changed;
ROLLBACK TO SAVEPOINT native_control;
ROLLBACK;
SELECT jsonb_build_object('control','native-control-PrivacyRequest','all_declared_user_triggers_restored',NOT EXISTS(SELECT 1 FROM (VALUES ('app.privacy_requests','owner_commit','O'),('app.privacy_requests','physical_guard','O'),('app.privacy_requests','privacy_request','O')) e(table_name,name,enabled) LEFT JOIN pg_trigger t ON t.tgrelid=to_regclass(e.table_name) AND t.tgname=e.name WHERE t.oid IS NULL OR t.tgisinternal OR t.tgenabled::text IS DISTINCT FROM e.enabled));
