-- PRIVILEGED NATIVE SHAPE CONTROL ONLY; all target USER triggers temporarily bypassed.
-- FK/CHECK/UNIQUE/internal RI triggers remain active. Roll back every mutation and trigger DDL.
BEGIN;
SET LOCAL search_path=pg_catalog;
SET LOCAL log_statement='none';
SET LOCAL log_min_error_statement='panic';
ALTER TABLE "platform"."owner_mutation_evidence" DISABLE TRIGGER "exact_evidence_source";
ALTER TABLE "platform"."owner_mutation_evidence" DISABLE TRIGGER "infrastructure_commit";
ALTER TABLE "platform"."owner_mutation_evidence" DISABLE TRIGGER "physical_guard";
SAVEPOINT native_control;
WITH changed AS (INSERT INTO "platform"."owner_mutation_evidence"("id","command_receipt_id","owner_module_id","aggregate_kind","aggregate_id","previous_revision","committed_revision","action","decision_ref","evidence_schema_id","evidence_schema_version","evidence_digest","created_at","evidence_body","mutation_transaction_id") VALUES ('38c3a564-7ff6-5cf1-8ee8-85e01da13775'::pg_catalog.uuid,'d0c6ddd2-8a58-522b-aeb7-ce60304058b3'::pg_catalog.uuid,'customer_buyer_profile'::pg_catalog.text,'CustomerProfile'::pg_catalog.text,'95dd2ef9-62ab-5df0-994f-668d52f017d7'::pg_catalog.text,NULL::pg_catalog.int8,'0'::pg_catalog.int8,'SH-004.v1'::pg_catalog.text,'native-acl-fact-not-owner-proof'::pg_catalog.text,'urn:workinants:database-review:owner-evidence:v1#/$defs/CustomerProfile'::pg_catalog.text,'1'::pg_catalog.text,encode(sha256(convert_to('{"schema":"database-owner-evidence.v1","owner":"customer_buyer_profile","model":"CustomerProfile","primaryKey":{"id":"95dd2ef9-62ab-5df0-994f-668d52f017d7"},"prior":null,"committed":{"id":"95dd2ef9-62ab-5df0-994f-668d52f017d7","userId":"eef35384-2706-5385-8408-3478494d445d","status":"active","revision":"0","privacyGeneration":"0"},"decisionRef":"native-acl-fact-not-owner-proof"}'::jsonb::text,'UTF8')),'hex'),'2026-11-17T00:00:00Z'::pg_catalog.timestamptz,'{"schema":"database-owner-evidence.v1","owner":"customer_buyer_profile","model":"CustomerProfile","primaryKey":{"id":"95dd2ef9-62ab-5df0-994f-668d52f017d7"},"prior":null,"committed":{"id":"95dd2ef9-62ab-5df0-994f-668d52f017d7","userId":"eef35384-2706-5385-8408-3478494d445d","status":"active","revision":"0","privacyGeneration":"0"},"decisionRef":"native-acl-fact-not-owner-proof"}'::pg_catalog.jsonb,'native-acl-setup-transaction'::pg_catalog.text) RETURNING 1) SELECT count(*)=1 AS native_insert_one FROM changed;
ROLLBACK TO SAVEPOINT native_control;
WITH changed AS (UPDATE "platform"."owner_mutation_evidence" SET "id"='c5cf03a7-ebee-5a21-b1bb-35033da4fe45'::pg_catalog.uuid WHERE "id"='c5cf03a7-ebee-5a21-b1bb-35033da4fe45'::pg_catalog.uuid RETURNING 1) SELECT count(*)=1 AS native_update_one FROM changed;
ROLLBACK TO SAVEPOINT native_control;
WITH changed AS (DELETE FROM "platform"."owner_mutation_evidence" WHERE "id"='c5cf03a7-ebee-5a21-b1bb-35033da4fe45'::pg_catalog.uuid RETURNING 1) SELECT count(*)=1 AS native_delete_one FROM changed;
ROLLBACK TO SAVEPOINT native_control;
ROLLBACK;
SELECT jsonb_build_object('control','native-control-OwnerMutationEvidence','all_declared_user_triggers_restored',NOT EXISTS(SELECT 1 FROM (VALUES ('platform.owner_mutation_evidence','exact_evidence_source','O'),('platform.owner_mutation_evidence','infrastructure_commit','O'),('platform.owner_mutation_evidence','physical_guard','O')) e(table_name,name,enabled) LEFT JOIN pg_trigger t ON t.tgrelid=to_regclass(e.table_name) AND t.tgname=e.name WHERE t.oid IS NULL OR t.tgisinternal OR t.tgenabled::text IS DISTINCT FROM e.enabled));
