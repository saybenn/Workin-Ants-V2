-- PRIVILEGED NATIVE SHAPE CONTROL ONLY; all target USER triggers temporarily bypassed.
-- FK/CHECK/UNIQUE/internal RI triggers remain active. Roll back every mutation and trigger DDL.
BEGIN;
SET LOCAL search_path=pg_catalog;
SET LOCAL log_statement='none';
SET LOCAL log_min_error_statement='panic';
ALTER TABLE "app"."user_security_profiles" DISABLE TRIGGER "owner_commit";
ALTER TABLE "app"."user_security_profiles" DISABLE TRIGGER "physical_guard";
SAVEPOINT native_control;
WITH changed AS (INSERT INTO "app"."user_security_profiles"("id","user_id","security_tier","phone_number_encrypted","phone_number_hash","phone_verified_at","phone_last_changed_at","passkeys_enabled","sms_mfa_enabled","backup_password_configured","sensitive_action_mfa_required","last_step_up_at","last_sensitive_action_at","locked_until","lock_reason","created_at","updated_at","revision","security_generation","mutation_transaction_id") VALUES ('13aa9b2f-5ef3-53f6-a183-70e3f8e00d11'::pg_catalog.uuid,'f10db05c-76a4-56d3-ae8f-2340aa037a6a'::pg_catalog.uuid,'standard'::app.user_security_tier,NULL::pg_catalog.text,NULL::pg_catalog.text,NULL::pg_catalog.timestamptz,NULL::pg_catalog.timestamptz,false,false,false,true,NULL::pg_catalog.timestamptz,NULL::pg_catalog.timestamptz,NULL::pg_catalog.timestamptz,NULL::pg_catalog.text,'2026-11-17T00:00:00Z'::pg_catalog.timestamptz,'2026-11-17T00:00:00Z'::pg_catalog.timestamptz,'0'::pg_catalog.int8,'0'::pg_catalog.int8,'native-acl-setup-transaction'::pg_catalog.text) RETURNING 1) SELECT count(*)=1 AS native_insert_one FROM changed;
ROLLBACK TO SAVEPOINT native_control;
WITH changed AS (UPDATE "app"."user_security_profiles" SET "id"='678f9096-36e2-5cfd-a884-850c82d28332'::pg_catalog.uuid WHERE "id"='678f9096-36e2-5cfd-a884-850c82d28332'::pg_catalog.uuid RETURNING 1) SELECT count(*)=1 AS native_update_one FROM changed;
ROLLBACK TO SAVEPOINT native_control;
WITH changed AS (DELETE FROM "app"."user_security_profiles" WHERE "id"='678f9096-36e2-5cfd-a884-850c82d28332'::pg_catalog.uuid RETURNING 1) SELECT count(*)=1 AS native_delete_one FROM changed;
ROLLBACK TO SAVEPOINT native_control;
ROLLBACK;
SELECT jsonb_build_object('control','native-control-UserSecurityProfile','all_declared_user_triggers_restored',NOT EXISTS(SELECT 1 FROM (VALUES ('app.user_security_profiles','owner_commit','O'),('app.user_security_profiles','physical_guard','O')) e(table_name,name,enabled) LEFT JOIN pg_trigger t ON t.tgrelid=to_regclass(e.table_name) AND t.tgname=e.name WHERE t.oid IS NULL OR t.tgisinternal OR t.tgenabled::text IS DISTINCT FROM e.enabled));
