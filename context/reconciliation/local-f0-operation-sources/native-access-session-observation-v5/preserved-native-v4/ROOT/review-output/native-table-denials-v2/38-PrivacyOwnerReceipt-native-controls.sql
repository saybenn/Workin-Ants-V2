-- PRIVILEGED NATIVE SHAPE CONTROL ONLY; all target USER triggers temporarily bypassed.
-- FK/CHECK/UNIQUE/internal RI triggers remain active. Roll back every mutation and trigger DDL.
BEGIN;
SET LOCAL search_path=pg_catalog;
SET LOCAL log_statement='none';
SET LOCAL log_min_error_statement='panic';
ALTER TABLE "app"."privacy_owner_receipt" DISABLE TRIGGER "owner_commit";
ALTER TABLE "app"."privacy_owner_receipt" DISABLE TRIGGER "physical_guard";
ALTER TABLE "app"."privacy_owner_receipt" DISABLE TRIGGER "privacy_receipt";
SAVEPOINT native_control;
WITH changed AS (INSERT INTO "app"."privacy_owner_receipt"("id","instruction_id","generation","disposition","execution_receipt_ref","legal_basis_ref","artifact_digest","artifact_version","result_schema_version","created_at","mutation_transaction_id") VALUES ('b8e464ac-4f69-5a12-93ed-ef77883ab596'::pg_catalog.uuid,'b1994733-021a-5612-97af-e1a5f9a9936e'::pg_catalog.uuid,'0'::pg_catalog.int8,'completed'::app.privacy_disposition_kind,'native-acl-23bcd4f66dfeddd2f8fc31f9'::pg_catalog.text,NULL::pg_catalog.text,NULL::pg_catalog.bpchar,NULL::pg_catalog.text,'1'::pg_catalog.text,'2026-11-17T00:00:00Z'::pg_catalog.timestamptz,'native-acl-setup-transaction'::pg_catalog.text) RETURNING 1) SELECT count(*)=1 AS native_insert_one FROM changed;
ROLLBACK TO SAVEPOINT native_control;
WITH changed AS (UPDATE "app"."privacy_owner_receipt" SET "id"='fb76abbb-ce1f-5804-a623-66325639cb1c'::pg_catalog.uuid WHERE "id"='fb76abbb-ce1f-5804-a623-66325639cb1c'::pg_catalog.uuid RETURNING 1) SELECT count(*)=1 AS native_update_one FROM changed;
ROLLBACK TO SAVEPOINT native_control;
WITH changed AS (DELETE FROM "app"."privacy_owner_receipt" WHERE "id"='fb76abbb-ce1f-5804-a623-66325639cb1c'::pg_catalog.uuid RETURNING 1) SELECT count(*)=1 AS native_delete_one FROM changed;
ROLLBACK TO SAVEPOINT native_control;
ROLLBACK;
SELECT jsonb_build_object('control','native-control-PrivacyOwnerReceipt','all_declared_user_triggers_restored',NOT EXISTS(SELECT 1 FROM (VALUES ('app.privacy_owner_receipt','owner_commit','O'),('app.privacy_owner_receipt','physical_guard','O'),('app.privacy_owner_receipt','privacy_receipt','O')) e(table_name,name,enabled) LEFT JOIN pg_trigger t ON t.tgrelid=to_regclass(e.table_name) AND t.tgname=e.name WHERE t.oid IS NULL OR t.tgisinternal OR t.tgenabled::text IS DISTINCT FROM e.enabled));
