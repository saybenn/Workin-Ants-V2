-- PRIVILEGED NATIVE SHAPE CONTROL ONLY; all target USER triggers temporarily bypassed.
-- FK/CHECK/UNIQUE/internal RI triggers remain active. Roll back every mutation and trigger DDL.
BEGIN;
SET LOCAL search_path=pg_catalog;
SET LOCAL log_statement='none';
SET LOCAL log_min_error_statement='panic';
ALTER TABLE "app"."audit_events" DISABLE TRIGGER "owner_commit";
ALTER TABLE "app"."audit_events" DISABLE TRIGGER "physical_guard";
SAVEPOINT native_control;
WITH changed AS (INSERT INTO "app"."audit_events"("id","actor_user_id","entity_type","entity_id","action","metadata","created_at","mutation_transaction_id") VALUES ('720818b0-aefd-5f64-90c1-d889551cf3c3'::pg_catalog.uuid,NULL::pg_catalog.uuid,'native-acl-2b66dc96de6efcd8c79b48d5'::pg_catalog.text,NULL::pg_catalog.uuid,'native-acl-12e263fae5932d68fae5d736'::pg_catalog.text,NULL::pg_catalog.jsonb,'2026-11-17T00:00:00Z'::pg_catalog.timestamptz,'native-acl-setup-transaction'::pg_catalog.text) RETURNING 1) SELECT count(*)=1 AS native_insert_one FROM changed;
ROLLBACK TO SAVEPOINT native_control;
WITH changed AS (UPDATE "app"."audit_events" SET "id"='65210591-87ce-5a46-a627-19800deeeb64'::pg_catalog.uuid WHERE "id"='65210591-87ce-5a46-a627-19800deeeb64'::pg_catalog.uuid RETURNING 1) SELECT count(*)=1 AS native_update_one FROM changed;
ROLLBACK TO SAVEPOINT native_control;
WITH changed AS (DELETE FROM "app"."audit_events" WHERE "id"='65210591-87ce-5a46-a627-19800deeeb64'::pg_catalog.uuid RETURNING 1) SELECT count(*)=1 AS native_delete_one FROM changed;
ROLLBACK TO SAVEPOINT native_control;
ROLLBACK;
SELECT jsonb_build_object('control','native-control-AuditEvent','all_declared_user_triggers_restored',NOT EXISTS(SELECT 1 FROM (VALUES ('app.audit_events','owner_commit','O'),('app.audit_events','physical_guard','O')) e(table_name,name,enabled) LEFT JOIN pg_trigger t ON t.tgrelid=to_regclass(e.table_name) AND t.tgname=e.name WHERE t.oid IS NULL OR t.tgisinternal OR t.tgenabled::text IS DISTINCT FROM e.enabled));
