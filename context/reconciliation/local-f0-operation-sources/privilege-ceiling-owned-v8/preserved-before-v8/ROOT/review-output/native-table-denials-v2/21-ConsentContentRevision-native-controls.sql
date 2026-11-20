-- PRIVILEGED NATIVE SHAPE CONTROL ONLY; all target USER triggers temporarily bypassed.
-- FK/CHECK/UNIQUE/internal RI triggers remain active. Roll back every mutation and trigger DDL.
BEGIN;
SET LOCAL search_path=pg_catalog;
SET LOCAL log_statement='none';
SET LOCAL log_min_error_statement='panic';
ALTER TABLE "app"."consent_content_revision" DISABLE TRIGGER "owner_commit";
ALTER TABLE "app"."consent_content_revision" DISABLE TRIGGER "physical_guard";
SAVEPOINT native_control;
WITH changed AS (INSERT INTO "app"."consent_content_revision"("id","type","version","locale","jurisdiction_scope","content_text","content_hash","review_state","legal_approval_ref","effective_from","effective_until","created_at","mutation_transaction_id") VALUES ('d640544f-9c62-5098-b760-5c8b0ed7dd64'::pg_catalog.uuid,'terms'::app.consent_type,'native-acl-67dcd56c90f48ff1f24da2f2'::pg_catalog.text,'native-acl-5b04f12493cc23835b38c1a3'::pg_catalog.text,'native-acl-8bf7db35d7ef8e82dd402a1b'::pg_catalog.text,'synthetic local ACL fact; not legal approval or rendered acceptance'::pg_catalog.text,encode(sha256(convert_to('synthetic local ACL fact; not legal approval or rendered acceptance','UTF8')),'hex'),'draft'::app.review_policy_state,NULL::pg_catalog.text,'2026-11-17T00:00:00Z'::pg_catalog.timestamptz,NULL::pg_catalog.timestamptz,'2026-11-17T00:00:00Z'::pg_catalog.timestamptz,'native-acl-setup-transaction'::pg_catalog.text) RETURNING 1) SELECT count(*)=1 AS native_insert_one FROM changed;
ROLLBACK TO SAVEPOINT native_control;
WITH changed AS (UPDATE "app"."consent_content_revision" SET "id"='059a8b87-99cc-59ea-ab6d-13561ca909dd'::pg_catalog.uuid WHERE "id"='059a8b87-99cc-59ea-ab6d-13561ca909dd'::pg_catalog.uuid RETURNING 1) SELECT count(*)=1 AS native_update_one FROM changed;
ROLLBACK TO SAVEPOINT native_control;
WITH changed AS (DELETE FROM "app"."consent_content_revision" WHERE "id"='059a8b87-99cc-59ea-ab6d-13561ca909dd'::pg_catalog.uuid RETURNING 1) SELECT count(*)=1 AS native_delete_one FROM changed;
ROLLBACK TO SAVEPOINT native_control;
ROLLBACK;
SELECT jsonb_build_object('control','native-control-ConsentContentRevision','all_declared_user_triggers_restored',NOT EXISTS(SELECT 1 FROM (VALUES ('app.consent_content_revision','owner_commit','O'),('app.consent_content_revision','physical_guard','O')) e(table_name,name,enabled) LEFT JOIN pg_trigger t ON t.tgrelid=to_regclass(e.table_name) AND t.tgname=e.name WHERE t.oid IS NULL OR t.tgisinternal OR t.tgenabled::text IS DISTINCT FROM e.enabled));
