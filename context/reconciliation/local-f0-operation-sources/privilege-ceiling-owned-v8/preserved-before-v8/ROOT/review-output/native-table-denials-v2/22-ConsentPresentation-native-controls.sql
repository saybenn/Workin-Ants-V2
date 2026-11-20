-- PRIVILEGED NATIVE SHAPE CONTROL ONLY; all target USER triggers temporarily bypassed.
-- FK/CHECK/UNIQUE/internal RI triggers remain active. Roll back every mutation and trigger DDL.
BEGIN;
SET LOCAL search_path=pg_catalog;
SET LOCAL log_statement='none';
SET LOCAL log_min_error_statement='panic';
ALTER TABLE "app"."consent_presentation" DISABLE TRIGGER "consent_presentation_subject";
ALTER TABLE "app"."consent_presentation" DISABLE TRIGGER "owner_commit";
ALTER TABLE "app"."consent_presentation" DISABLE TRIGGER "physical_guard";
SAVEPOINT native_control;
WITH changed AS (INSERT INTO "app"."consent_presentation"("id","content_revision_id","user_id","action_owner","action","render_version","rendered_text","rendered_hash","context_owner","context_kind","context_id","created_at","mutation_transaction_id") VALUES ('47fa88b1-37d7-5b39-b193-0c905afa8171'::pg_catalog.uuid,'2da448e0-0389-5f59-a9ec-baf3e429c909'::pg_catalog.uuid,'92148209-85bf-5420-b6ed-59655eb15467'::pg_catalog.uuid,'native-acl-fc5905575c0b037cc3d9bae3'::pg_catalog.text,'native-acl-e66fc98b56b8f82afc37f59d'::pg_catalog.text,'native-acl-26ca96eab7761ad5a87ba0b8'::pg_catalog.text,'synthetic local ACL fact; not legal approval or rendered acceptance'::pg_catalog.text,encode(sha256(convert_to('synthetic local ACL fact; not legal approval or rendered acceptance','UTF8')),'hex'),'native-acl-044842076678b704a0ac1203'::pg_catalog.text,'native-acl-09deeaff906fe03301ce493c'::pg_catalog.text,NULL::pg_catalog.text,'2026-11-17T00:00:00Z'::pg_catalog.timestamptz,'native-acl-setup-transaction'::pg_catalog.text) RETURNING 1) SELECT count(*)=1 AS native_insert_one FROM changed;
ROLLBACK TO SAVEPOINT native_control;
WITH changed AS (UPDATE "app"."consent_presentation" SET "id"='00f918b5-5bf0-5e33-91f0-58baddd61daf'::pg_catalog.uuid WHERE "id"='00f918b5-5bf0-5e33-91f0-58baddd61daf'::pg_catalog.uuid RETURNING 1) SELECT count(*)=1 AS native_update_one FROM changed;
ROLLBACK TO SAVEPOINT native_control;
WITH changed AS (DELETE FROM "app"."consent_presentation" WHERE "id"='00f918b5-5bf0-5e33-91f0-58baddd61daf'::pg_catalog.uuid RETURNING 1) SELECT count(*)=1 AS native_delete_one FROM changed;
ROLLBACK TO SAVEPOINT native_control;
ROLLBACK;
SELECT jsonb_build_object('control','native-control-ConsentPresentation','all_declared_user_triggers_restored',NOT EXISTS(SELECT 1 FROM (VALUES ('app.consent_presentation','consent_presentation_subject','O'),('app.consent_presentation','owner_commit','O'),('app.consent_presentation','physical_guard','O')) e(table_name,name,enabled) LEFT JOIN pg_trigger t ON t.tgrelid=to_regclass(e.table_name) AND t.tgname=e.name WHERE t.oid IS NULL OR t.tgisinternal OR t.tgenabled::text IS DISTINCT FROM e.enabled));
