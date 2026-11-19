-- PRIVILEGED NATIVE SHAPE CONTROL ONLY; all target USER triggers temporarily bypassed.
-- FK/CHECK/UNIQUE/internal RI triggers remain active. Roll back every mutation and trigger DDL.
BEGIN;
SET LOCAL search_path=pg_catalog;
SET LOCAL log_statement='none';
SET LOCAL log_min_error_statement='panic';
ALTER TABLE "platform"."runtime_effect_receipt" DISABLE TRIGGER "effect_fence";
ALTER TABLE "platform"."runtime_effect_receipt" DISABLE TRIGGER "physical_guard";
SAVEPOINT native_control;
WITH changed AS (INSERT INTO "platform"."runtime_effect_receipt"("id","command_receipt_id","owner_module_id","operation","subject_scope","semantic_effect_key","fingerprint","state","source_revision","fence","result_schema_id","result_hash","committed_at","created_at","mutation_transaction_id") VALUES ('6020a7ca-64ff-539c-9d87-e042c1c0043a'::pg_catalog.uuid,NULL::pg_catalog.uuid,'customer_buyer_profile'::pg_catalog.text,'SH-004.v1'::pg_catalog.text,'CustomerProfile:e652b295-f63f-5db7-8fc4-744d46113cb7'::pg_catalog.text,'native-acl-6608f9407b025e4e3e50f164'::pg_catalog.text,'6f7e6c0c393baa39de15e57523b2f69cfca51d41b77c0a4d28796b808afab53c'::pg_catalog.bpchar,'pending'::platform.runtime_receipt_state,NULL::pg_catalog.int8,'0'::pg_catalog.int8,'SH-004.v1#/$defs/response'::pg_catalog.text,NULL::pg_catalog.bpchar,NULL::pg_catalog.timestamptz,'2026-11-17T00:00:00Z'::pg_catalog.timestamptz,'native-acl-setup-transaction'::pg_catalog.text) RETURNING 1) SELECT count(*)=1 AS native_insert_one FROM changed;
ROLLBACK TO SAVEPOINT native_control;
WITH changed AS (UPDATE "platform"."runtime_effect_receipt" SET "id"='577c76bc-cb91-5fc6-9d88-48f0016bcc95'::pg_catalog.uuid WHERE "id"='577c76bc-cb91-5fc6-9d88-48f0016bcc95'::pg_catalog.uuid RETURNING 1) SELECT count(*)=1 AS native_update_one FROM changed;
ROLLBACK TO SAVEPOINT native_control;
WITH changed AS (DELETE FROM "platform"."runtime_effect_receipt" WHERE "id"='577c76bc-cb91-5fc6-9d88-48f0016bcc95'::pg_catalog.uuid RETURNING 1) SELECT count(*)=1 AS native_delete_one FROM changed;
ROLLBACK TO SAVEPOINT native_control;
ROLLBACK;
SELECT jsonb_build_object('control','native-control-RuntimeEffectReceipt','all_declared_user_triggers_restored',NOT EXISTS(SELECT 1 FROM (VALUES ('platform.runtime_effect_receipt','effect_fence','O'),('platform.runtime_effect_receipt','physical_guard','O')) e(table_name,name,enabled) LEFT JOIN pg_trigger t ON t.tgrelid=to_regclass(e.table_name) AND t.tgname=e.name WHERE t.oid IS NULL OR t.tgisinternal OR t.tgenabled::text IS DISTINCT FROM e.enabled));
