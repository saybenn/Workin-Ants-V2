-- PRIVILEGED NATIVE SHAPE CONTROL ONLY; all target USER triggers temporarily bypassed.
-- FK/CHECK/UNIQUE/internal RI triggers remain active. Roll back every mutation and trigger DDL.
BEGIN;
SET LOCAL search_path=pg_catalog;
SET LOCAL log_statement='none';
SET LOCAL log_min_error_statement='panic';
ALTER TABLE "app"."professional_profiles" DISABLE TRIGGER "physical_guard";
SAVEPOINT native_control;
WITH changed AS (INSERT INTO "app"."professional_profiles"("id","user_id","slug","headline","bio","website_url","city","state","country","status","rating_average","rating_count","stripe_account_id","stripe_ready","onboarding_complete_at","default_currency","created_at","updated_at","suspended_for_moderation_at","trust_score","verified_at","verification_expires_at","revision","privacy_generation","mutation_transaction_id") VALUES ('0c7f83e1-adc3-5fb0-8708-154f305e63f1'::pg_catalog.uuid,'e977b287-136e-5889-be22-7a37ef15f6dc'::pg_catalog.uuid,'native-acl-84284f85c57d4cebf29384eb'::pg_catalog.text,NULL::pg_catalog.text,NULL::pg_catalog.text,NULL::pg_catalog.text,NULL::pg_catalog.text,NULL::pg_catalog.text,NULL::pg_catalog.text,'draft'::app.profile_status,NULL::pg_catalog.float8,'0'::pg_catalog.int4,NULL::pg_catalog.text,false,NULL::pg_catalog.timestamptz,NULL::pg_catalog.text,'2026-11-17T00:00:00Z'::pg_catalog.timestamptz,'2026-11-17T00:00:00Z'::pg_catalog.timestamptz,NULL::pg_catalog.timestamptz,NULL::pg_catalog.int4,NULL::pg_catalog.timestamptz,NULL::pg_catalog.timestamptz,'0'::pg_catalog.int8,'0'::pg_catalog.int8,'native-acl-setup-transaction'::pg_catalog.text) RETURNING 1) SELECT count(*)=1 AS native_insert_one FROM changed;
ROLLBACK TO SAVEPOINT native_control;
WITH changed AS (UPDATE "app"."professional_profiles" SET "id"='4f372302-b4cb-5520-a037-0766f14b3323'::pg_catalog.uuid WHERE "id"='4f372302-b4cb-5520-a037-0766f14b3323'::pg_catalog.uuid RETURNING 1) SELECT count(*)=1 AS native_update_one FROM changed;
ROLLBACK TO SAVEPOINT native_control;
WITH changed AS (DELETE FROM "app"."professional_profiles" WHERE "id"='4f372302-b4cb-5520-a037-0766f14b3323'::pg_catalog.uuid RETURNING 1) SELECT count(*)=1 AS native_delete_one FROM changed;
ROLLBACK TO SAVEPOINT native_control;
ROLLBACK;
SELECT jsonb_build_object('control','native-control-ProfessionalProfile','all_declared_user_triggers_restored',NOT EXISTS(SELECT 1 FROM (VALUES ('app.professional_profiles','physical_guard','O')) e(table_name,name,enabled) LEFT JOIN pg_trigger t ON t.tgrelid=to_regclass(e.table_name) AND t.tgname=e.name WHERE t.oid IS NULL OR t.tgisinternal OR t.tgenabled::text IS DISTINCT FROM e.enabled));
