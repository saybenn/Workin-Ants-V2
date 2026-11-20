-- PRIVILEGED NATIVE SHAPE CONTROL ONLY; all target USER triggers temporarily bypassed.
-- FK/CHECK/UNIQUE/internal RI triggers remain active. Roll back every mutation and trigger DDL.
BEGIN;
SET LOCAL search_path=pg_catalog;
SET LOCAL log_statement='none';
SET LOCAL log_min_error_statement='panic';
ALTER TABLE "platform"."runtime_outbox_message" DISABLE TRIGGER "exact_customer_message";
ALTER TABLE "platform"."runtime_outbox_message" DISABLE TRIGGER "infrastructure_commit";
ALTER TABLE "platform"."runtime_outbox_message" DISABLE TRIGGER "message_json";
ALTER TABLE "platform"."runtime_outbox_message" DISABLE TRIGGER "physical_guard";
SAVEPOINT native_control;
WITH changed AS (INSERT INTO "platform"."runtime_outbox_message"("id","command_receipt_id","kind","producer_owner","aggregate_kind","aggregate_id","source_revision","source_generation","ordinal","name","schema_version","payload_schema_id","payload_hash","payload","correlation_id","causation_id","correction_of_id","occurred_at","effective_at","created_at","mutation_transaction_id") VALUES ('f01a3687-c15e-5979-a621-0ffc9c676661'::pg_catalog.uuid,'680df6b2-70b0-531a-bd10-e2091d75cc69'::pg_catalog.uuid,'event'::platform.runtime_message_kind,'customer_buyer_profile'::pg_catalog.text,'CustomerProfile'::pg_catalog.text,'936ed859-5c55-5d84-88fe-b3dd8b4ccc33'::pg_catalog.text,'0'::pg_catalog.int8,'0'::pg_catalog.int8,'0'::pg_catalog.int4,'customer.lifecycle_changed.v1'::pg_catalog.text,'1'::pg_catalog.text,'urn:workin-ants:types:v1#/$defs/EventPayload_customer_lifecycle_changed_v1'::pg_catalog.text,encode(sha256(convert_to('{"eventName":"customer.lifecycle_changed.v1","customerProfileId":"936ed859-5c55-5d84-88fe-b3dd8b4ccc33","userId":"a4bdb6c1-1f86-5f04-bc72-6bac9feffe46","lifecycleRevision":"0","safeState":"active"}'::jsonb::text,'UTF8')),'hex'),'{"eventName":"customer.lifecycle_changed.v1","customerProfileId":"936ed859-5c55-5d84-88fe-b3dd8b4ccc33","userId":"a4bdb6c1-1f86-5f04-bc72-6bac9feffe46","lifecycleRevision":"0","safeState":"active"}'::pg_catalog.jsonb,'native-acl-c597b8b98c2a07ea51bf0b63'::pg_catalog.text,'680df6b2-70b0-531a-bd10-e2091d75cc69'::pg_catalog.text,NULL::pg_catalog.uuid,'2026-11-17T00:00:00Z'::pg_catalog.timestamptz,'2026-11-17T00:00:00Z'::pg_catalog.timestamptz,'2026-11-17T00:00:00Z'::pg_catalog.timestamptz,'native-acl-setup-transaction'::pg_catalog.text) RETURNING 1) SELECT count(*)=1 AS native_insert_one FROM changed;
ROLLBACK TO SAVEPOINT native_control;
WITH changed AS (UPDATE "platform"."runtime_outbox_message" SET "id"='f5b2dce7-397b-5aa6-8b52-040f3fc4adcc'::pg_catalog.uuid WHERE "id"='f5b2dce7-397b-5aa6-8b52-040f3fc4adcc'::pg_catalog.uuid RETURNING 1) SELECT count(*)=1 AS native_update_one FROM changed;
ROLLBACK TO SAVEPOINT native_control;
WITH changed AS (DELETE FROM "platform"."runtime_outbox_message" WHERE "id"='f5b2dce7-397b-5aa6-8b52-040f3fc4adcc'::pg_catalog.uuid RETURNING 1) SELECT count(*)=1 AS native_delete_one FROM changed;
ROLLBACK TO SAVEPOINT native_control;
ROLLBACK;
SELECT jsonb_build_object('control','native-control-RuntimeOutboxMessage','all_declared_user_triggers_restored',NOT EXISTS(SELECT 1 FROM (VALUES ('platform.runtime_outbox_message','exact_customer_message','O'),('platform.runtime_outbox_message','infrastructure_commit','O'),('platform.runtime_outbox_message','message_json','O'),('platform.runtime_outbox_message','physical_guard','O')) e(table_name,name,enabled) LEFT JOIN pg_trigger t ON t.tgrelid=to_regclass(e.table_name) AND t.tgname=e.name WHERE t.oid IS NULL OR t.tgisinternal OR t.tgenabled::text IS DISTINCT FROM e.enabled));
