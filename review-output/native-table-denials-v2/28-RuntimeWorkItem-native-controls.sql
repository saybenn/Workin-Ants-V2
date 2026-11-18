-- PRIVILEGED NATIVE SHAPE CONTROL ONLY; all target USER triggers temporarily bypassed.
-- FK/CHECK/UNIQUE/internal RI triggers remain active. Roll back every mutation and trigger DDL.
BEGIN;
SET LOCAL search_path=pg_catalog;
SET LOCAL log_statement='none';
SET LOCAL log_min_error_statement='panic';
ALTER TABLE "platform"."runtime_work_item" DISABLE TRIGGER "physical_guard";
ALTER TABLE "platform"."runtime_work_item" DISABLE TRIGGER "work_transition";
SAVEPOINT native_control;
WITH changed AS (INSERT INTO "platform"."runtime_work_item"("id","outbox_message_id","handler_name","semantic_work_key","state","fence","lease_token_hash","lease_expires_at","attempt_count","next_attempt_at","effect_receipt_id","created_at","mutation_transaction_id") VALUES ('aac01dd8-1e65-55ef-a70e-9de3ce8bdffb'::pg_catalog.uuid,'482d72fd-d770-5efb-b262-4d0d936c99d7'::pg_catalog.uuid,'native-acl-9a2b3b8c4c8543e073f452f1'::pg_catalog.text,'native-acl-529dd6c10e06c77f5f124776'::pg_catalog.text,'pending'::platform.runtime_work_state,'0'::pg_catalog.int8,NULL::pg_catalog.bpchar,NULL::pg_catalog.timestamptz,'0'::pg_catalog.int4,NULL::pg_catalog.timestamptz,NULL::pg_catalog.uuid,'2026-11-17T00:00:00Z'::pg_catalog.timestamptz,'native-acl-setup-transaction'::pg_catalog.text) RETURNING 1) SELECT count(*)=1 AS native_insert_one FROM changed;
ROLLBACK TO SAVEPOINT native_control;
WITH changed AS (UPDATE "platform"."runtime_work_item" SET "id"='87f1066d-9bf1-5809-a1da-ffd96c766ad4'::pg_catalog.uuid WHERE "id"='87f1066d-9bf1-5809-a1da-ffd96c766ad4'::pg_catalog.uuid RETURNING 1) SELECT count(*)=1 AS native_update_one FROM changed;
ROLLBACK TO SAVEPOINT native_control;
WITH changed AS (DELETE FROM "platform"."runtime_work_item" WHERE "id"='87f1066d-9bf1-5809-a1da-ffd96c766ad4'::pg_catalog.uuid RETURNING 1) SELECT count(*)=1 AS native_delete_one FROM changed;
ROLLBACK TO SAVEPOINT native_control;
ROLLBACK;
SELECT jsonb_build_object('control','native-control-RuntimeWorkItem','all_declared_user_triggers_restored',NOT EXISTS(SELECT 1 FROM (VALUES ('platform.runtime_work_item','physical_guard','O'),('platform.runtime_work_item','work_transition','O')) e(table_name,name,enabled) LEFT JOIN pg_trigger t ON t.tgrelid=to_regclass(e.table_name) AND t.tgname=e.name WHERE t.oid IS NULL OR t.tgisinternal OR t.tgenabled::text IS DISTINCT FROM e.enabled));
