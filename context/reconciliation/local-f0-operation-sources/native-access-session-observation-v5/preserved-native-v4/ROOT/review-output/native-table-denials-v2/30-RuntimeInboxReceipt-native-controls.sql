-- PRIVILEGED NATIVE SHAPE CONTROL ONLY; all target USER triggers temporarily bypassed.
-- FK/CHECK/UNIQUE/internal RI triggers remain active. Roll back every mutation and trigger DDL.
BEGIN;
SET LOCAL search_path=pg_catalog;
SET LOCAL log_statement='none';
SET LOCAL log_min_error_statement='panic';
ALTER TABLE "platform"."runtime_inbox_receipt" DISABLE TRIGGER "infrastructure_commit";
ALTER TABLE "platform"."runtime_inbox_receipt" DISABLE TRIGGER "physical_guard";
SAVEPOINT native_control;
WITH changed AS (INSERT INTO "platform"."runtime_inbox_receipt"("id","outbox_message_id","consumer_owner","handler_name","payload_hash","effect_receipt_id","created_at","mutation_transaction_id") VALUES ('004c342a-2c6b-5039-9cdb-64e3c48e436d'::pg_catalog.uuid,'2302eb70-7637-5f00-b124-70a788511c59'::pg_catalog.uuid,'native-acl-6ce2b16eb9bb465ef2cb3bad'::pg_catalog.text,'native-acl-92c98a20ccbd16ba8ce3d690'::pg_catalog.text,'123ee97377e0e4978da53826169d71f6f4037d2b8ea135569ef3b150ad380fc6'::pg_catalog.bpchar,'e348c3f0-82b0-5c4a-9ee0-7d08c4566f80'::pg_catalog.uuid,'2026-11-17T00:00:00Z'::pg_catalog.timestamptz,'native-acl-setup-transaction'::pg_catalog.text) RETURNING 1) SELECT count(*)=1 AS native_insert_one FROM changed;
ROLLBACK TO SAVEPOINT native_control;
WITH changed AS (UPDATE "platform"."runtime_inbox_receipt" SET "id"='7fdfecc1-b021-5567-9f7c-ccebebe0145b'::pg_catalog.uuid WHERE "id"='7fdfecc1-b021-5567-9f7c-ccebebe0145b'::pg_catalog.uuid RETURNING 1) SELECT count(*)=1 AS native_update_one FROM changed;
ROLLBACK TO SAVEPOINT native_control;
WITH changed AS (DELETE FROM "platform"."runtime_inbox_receipt" WHERE "id"='7fdfecc1-b021-5567-9f7c-ccebebe0145b'::pg_catalog.uuid RETURNING 1) SELECT count(*)=1 AS native_delete_one FROM changed;
ROLLBACK TO SAVEPOINT native_control;
ROLLBACK;
SELECT jsonb_build_object('control','native-control-RuntimeInboxReceipt','all_declared_user_triggers_restored',NOT EXISTS(SELECT 1 FROM (VALUES ('platform.runtime_inbox_receipt','infrastructure_commit','O'),('platform.runtime_inbox_receipt','physical_guard','O')) e(table_name,name,enabled) LEFT JOIN pg_trigger t ON t.tgrelid=to_regclass(e.table_name) AND t.tgname=e.name WHERE t.oid IS NULL OR t.tgisinternal OR t.tgenabled::text IS DISTINCT FROM e.enabled));
