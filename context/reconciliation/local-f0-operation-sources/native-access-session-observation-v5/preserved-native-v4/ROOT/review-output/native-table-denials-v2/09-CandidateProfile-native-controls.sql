-- PRIVILEGED NATIVE SHAPE CONTROL ONLY; all target USER triggers temporarily bypassed.
-- FK/CHECK/UNIQUE/internal RI triggers remain active. Roll back every mutation and trigger DDL.
BEGIN;
SET LOCAL search_path=pg_catalog;
SET LOCAL log_statement='none';
SET LOCAL log_min_error_statement='panic';
ALTER TABLE "app"."candidate_profiles" DISABLE TRIGGER "physical_guard";
SAVEPOINT native_control;
WITH changed AS (INSERT INTO "app"."candidate_profiles"("id","user_id","headline","portfolio_url","availability","city","state","country","status","is_visible","created_at","updated_at","trust_score","verified_at","verification_expires_at","revision","privacy_generation","discovery_preference_revision","discovery_enabled_at","mutation_transaction_id") VALUES ('8a073045-711c-5621-9c3f-bb93ed591b32'::pg_catalog.uuid,'751ef8a8-890a-5be5-a1e8-b72534887166'::pg_catalog.uuid,NULL::pg_catalog.text,NULL::pg_catalog.text,NULL::pg_catalog.text,NULL::pg_catalog.text,NULL::pg_catalog.text,NULL::pg_catalog.text,'draft'::app.profile_status,false,'2026-11-17T00:00:00Z'::pg_catalog.timestamptz,'2026-11-17T00:00:00Z'::pg_catalog.timestamptz,NULL::pg_catalog.int4,NULL::pg_catalog.timestamptz,NULL::pg_catalog.timestamptz,'0'::pg_catalog.int8,'0'::pg_catalog.int8,'0'::pg_catalog.int8,NULL::pg_catalog.timestamptz,'native-acl-setup-transaction'::pg_catalog.text) RETURNING 1) SELECT count(*)=1 AS native_insert_one FROM changed;
ROLLBACK TO SAVEPOINT native_control;
WITH changed AS (UPDATE "app"."candidate_profiles" SET "id"='c7c63525-4c7e-5b01-8e1f-da6e61dac15b'::pg_catalog.uuid WHERE "id"='c7c63525-4c7e-5b01-8e1f-da6e61dac15b'::pg_catalog.uuid RETURNING 1) SELECT count(*)=1 AS native_update_one FROM changed;
ROLLBACK TO SAVEPOINT native_control;
WITH changed AS (DELETE FROM "app"."candidate_profiles" WHERE "id"='c7c63525-4c7e-5b01-8e1f-da6e61dac15b'::pg_catalog.uuid RETURNING 1) SELECT count(*)=1 AS native_delete_one FROM changed;
ROLLBACK TO SAVEPOINT native_control;
ROLLBACK;
SELECT jsonb_build_object('control','native-control-CandidateProfile','all_declared_user_triggers_restored',NOT EXISTS(SELECT 1 FROM (VALUES ('app.candidate_profiles','physical_guard','O')) e(table_name,name,enabled) LEFT JOIN pg_trigger t ON t.tgrelid=to_regclass(e.table_name) AND t.tgname=e.name WHERE t.oid IS NULL OR t.tgisinternal OR t.tgenabled::text IS DISTINCT FROM e.enabled));
