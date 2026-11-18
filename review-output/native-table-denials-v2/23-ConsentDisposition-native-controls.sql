-- PRIVILEGED NATIVE SHAPE CONTROL ONLY; all target USER triggers temporarily bypassed.
-- FK/CHECK/UNIQUE/internal RI triggers remain active. Roll back every mutation and trigger DDL.
BEGIN;
SET LOCAL search_path=pg_catalog;
SET LOCAL log_statement='none';
SET LOCAL log_min_error_statement='panic';
ALTER TABLE "app"."consent_disposition" DISABLE TRIGGER "consent_disposition";
ALTER TABLE "app"."consent_disposition" DISABLE TRIGGER "owner_commit";
ALTER TABLE "app"."consent_disposition" DISABLE TRIGGER "physical_guard";
SAVEPOINT native_control;
WITH changed AS (INSERT INTO "app"."consent_disposition"("id","proof_id","user_id","presentation_id","kind","semantic_key","fingerprint","created_at","mutation_transaction_id") VALUES ('78a5bb8b-8263-5624-99ac-b10ec69ca2c5'::pg_catalog.uuid,NULL::pg_catalog.uuid,'9e02328e-6e6a-581b-b747-4cf9398f8720'::pg_catalog.uuid,'72a60a96-4104-5ca0-b38a-00df941b0960'::pg_catalog.uuid,'declined'::app.consent_disposition_kind,'native-acl-370b93ffca102d8b169fab10'::pg_catalog.text,'cb02b66e426445c8e390c3fa8493257cc429c424c2ead9aaaf19e2417449a2b3'::pg_catalog.bpchar,'2026-11-17T00:00:00Z'::pg_catalog.timestamptz,'native-acl-setup-transaction'::pg_catalog.text) RETURNING 1) SELECT count(*)=1 AS native_insert_one FROM changed;
ROLLBACK TO SAVEPOINT native_control;
WITH changed AS (UPDATE "app"."consent_disposition" SET "id"='a2fbc48e-33b3-532e-9e7a-4a7a8ac1dccd'::pg_catalog.uuid WHERE "id"='a2fbc48e-33b3-532e-9e7a-4a7a8ac1dccd'::pg_catalog.uuid RETURNING 1) SELECT count(*)=1 AS native_update_one FROM changed;
ROLLBACK TO SAVEPOINT native_control;
WITH changed AS (DELETE FROM "app"."consent_disposition" WHERE "id"='a2fbc48e-33b3-532e-9e7a-4a7a8ac1dccd'::pg_catalog.uuid RETURNING 1) SELECT count(*)=1 AS native_delete_one FROM changed;
ROLLBACK TO SAVEPOINT native_control;
ROLLBACK;
SELECT jsonb_build_object('control','native-control-ConsentDisposition','all_declared_user_triggers_restored',NOT EXISTS(SELECT 1 FROM (VALUES ('app.consent_disposition','consent_disposition','O'),('app.consent_disposition','owner_commit','O'),('app.consent_disposition','physical_guard','O')) e(table_name,name,enabled) LEFT JOIN pg_trigger t ON t.tgrelid=to_regclass(e.table_name) AND t.tgname=e.name WHERE t.oid IS NULL OR t.tgisinternal OR t.tgenabled::text IS DISTINCT FROM e.enabled));
