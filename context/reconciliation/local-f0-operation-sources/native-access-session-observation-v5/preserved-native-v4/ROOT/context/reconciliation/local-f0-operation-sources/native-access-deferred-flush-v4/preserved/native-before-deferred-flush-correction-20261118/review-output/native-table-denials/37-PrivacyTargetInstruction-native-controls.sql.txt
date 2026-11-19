-- PRIVILEGED NATIVE SHAPE CONTROL ONLY; all target USER triggers temporarily bypassed.
-- FK/CHECK/UNIQUE/internal RI triggers remain active. Roll back every mutation and trigger DDL.
BEGIN;
SET LOCAL search_path=pg_catalog;
SET LOCAL log_statement='none';
SET LOCAL log_min_error_statement='panic';
ALTER TABLE "app"."privacy_target_instruction" DISABLE TRIGGER "owner_commit";
ALTER TABLE "app"."privacy_target_instruction" DISABLE TRIGGER "physical_guard";
ALTER TABLE "app"."privacy_target_instruction" DISABLE TRIGGER "privacy_instruction";
SAVEPOINT native_control;
WITH changed AS (INSERT INTO "app"."privacy_target_instruction"("id","privacy_request_id","owner_module_id","target_kind","source_id","source_revision","action","generation","field_map_version","executor_version","descriptor_hash","created_at","mutation_transaction_id") VALUES ('ca0193c4-33ab-56e2-952f-3da3cdf2ea7d'::pg_catalog.uuid,'62f84254-e777-5815-971c-be00730a4656'::pg_catalog.uuid,'native-acl-9135cfb11db7cc3b5cc5d76f'::pg_catalog.text,'native-acl-1b8b89ce924014ee3b28f1d7'::pg_catalog.text,'native-acl-8f620165bca26b343a5f3b1f'::pg_catalog.text,'native-acl-23a2259062eb1bbeac6f47ea'::pg_catalog.text,'export'::app.privacy_action_kind,'0'::pg_catalog.int8,'native-acl-85e7eeacb5246b20767e98f1'::pg_catalog.text,'native-acl-cf98e4a1b961bd6ead0d7e8d'::pg_catalog.text,'f5f946bfb65d40c202bd075fdcb671481cf5862143fa4ed81b4c49d664b3bd92'::pg_catalog.bpchar,'2026-11-17T00:00:00Z'::pg_catalog.timestamptz,'native-acl-setup-transaction'::pg_catalog.text) RETURNING 1) SELECT count(*)=1 AS native_insert_one FROM changed;
ROLLBACK TO SAVEPOINT native_control;
WITH changed AS (UPDATE "app"."privacy_target_instruction" SET "id"='bfa56011-5fe0-5101-9c6d-924081a37cb7'::pg_catalog.uuid WHERE "id"='bfa56011-5fe0-5101-9c6d-924081a37cb7'::pg_catalog.uuid RETURNING 1) SELECT count(*)=1 AS native_update_one FROM changed;
ROLLBACK TO SAVEPOINT native_control;
WITH changed AS (DELETE FROM "app"."privacy_target_instruction" WHERE "id"='bfa56011-5fe0-5101-9c6d-924081a37cb7'::pg_catalog.uuid RETURNING 1) SELECT count(*)=1 AS native_delete_one FROM changed;
ROLLBACK TO SAVEPOINT native_control;
ROLLBACK;
SELECT jsonb_build_object('control','native-control-PrivacyTargetInstruction','all_declared_user_triggers_restored',NOT EXISTS(SELECT 1 FROM (VALUES ('app.privacy_target_instruction','owner_commit','O'),('app.privacy_target_instruction','physical_guard','O'),('app.privacy_target_instruction','privacy_instruction','O')) e(table_name,name,enabled) LEFT JOIN pg_trigger t ON t.tgrelid=to_regclass(e.table_name) AND t.tgname=e.name WHERE t.oid IS NULL OR t.tgisinternal OR t.tgenabled::text IS DISTINCT FROM e.enabled));
