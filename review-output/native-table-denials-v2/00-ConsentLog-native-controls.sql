-- PRIVILEGED NATIVE SHAPE CONTROL ONLY; all target USER triggers temporarily bypassed.
-- FK/CHECK/UNIQUE/internal RI triggers remain active. Roll back every mutation and trigger DDL.
BEGIN;
SET LOCAL search_path=pg_catalog;
SET LOCAL log_statement='none';
SET LOCAL log_min_error_statement='panic';
ALTER TABLE "app"."consent_logs" DISABLE TRIGGER "consent_proof";
ALTER TABLE "app"."consent_logs" DISABLE TRIGGER "owner_commit";
ALTER TABLE "app"."consent_logs" DISABLE TRIGGER "physical_guard";
SAVEPOINT native_control;
WITH changed AS (INSERT INTO "app"."consent_logs"("id","user_id","type","version","accepted_at","ip_hash","user_agent","created_at","acceptance_key","fingerprint","action_owner","action","context_kind","context_id","context_owner","presentation_hash","content_revision_id","presentation_id","mutation_transaction_id") VALUES ('d35039cb-0bdd-563f-9f03-543542c0a3b5'::pg_catalog.uuid,'02e05a8c-6db1-5843-aa4c-2c9407e5919e'::pg_catalog.uuid,'terms'::app.consent_type,'native-acl-c4bdb99be2b4fbf606c8b1d0'::pg_catalog.text,'2026-11-17T00:00:00Z'::pg_catalog.timestamptz,NULL::pg_catalog.text,NULL::pg_catalog.text,'2026-11-17T00:00:00Z'::pg_catalog.timestamptz,'native-acl-bc1f5adece767c21b96a34af'::pg_catalog.text,'c14bed8de0ddd7adcfa2f7cc108663af3f8b8fa099c163e3b20f916275811f9e'::pg_catalog.bpchar,'native-acl-2625b2f1e336c2cb10d62b76'::pg_catalog.text,'native-acl-4038836990a4a3419d74ac30'::pg_catalog.text,'native-acl-64b6b78a3ffecdbaca2964e5'::pg_catalog.text,NULL::pg_catalog.text,'native-acl-52eabcb778c5dee3ce7cd5c7'::pg_catalog.text,'4b976adeaa66491926266fa75706a018babdfb5c3adc07abdb429e47b982cbf6'::pg_catalog.bpchar,'54303263-941c-542b-a57d-b74a58cf7c4e'::pg_catalog.uuid,'2e2a1144-dafd-597f-99fb-92ace6aa6d6d'::pg_catalog.uuid,'native-acl-setup-transaction'::pg_catalog.text) RETURNING 1) SELECT count(*)=1 AS native_insert_one FROM changed;
ROLLBACK TO SAVEPOINT native_control;
WITH changed AS (UPDATE "app"."consent_logs" SET "id"='4448a52e-880c-55d6-8523-06a4c4252d12'::pg_catalog.uuid WHERE "id"='4448a52e-880c-55d6-8523-06a4c4252d12'::pg_catalog.uuid RETURNING 1) SELECT count(*)=1 AS native_update_one FROM changed;
ROLLBACK TO SAVEPOINT native_control;
WITH changed AS (DELETE FROM "app"."consent_logs" WHERE "id"='4448a52e-880c-55d6-8523-06a4c4252d12'::pg_catalog.uuid RETURNING 1) SELECT count(*)=1 AS native_delete_one FROM changed;
ROLLBACK TO SAVEPOINT native_control;
ROLLBACK;
SELECT jsonb_build_object('control','native-control-ConsentLog','all_declared_user_triggers_restored',NOT EXISTS(SELECT 1 FROM (VALUES ('app.consent_logs','consent_proof','O'),('app.consent_logs','owner_commit','O'),('app.consent_logs','physical_guard','O')) e(table_name,name,enabled) LEFT JOIN pg_trigger t ON t.tgrelid=to_regclass(e.table_name) AND t.tgname=e.name WHERE t.oid IS NULL OR t.tgisinternal OR t.tgenabled::text IS DISTINCT FROM e.enabled));
