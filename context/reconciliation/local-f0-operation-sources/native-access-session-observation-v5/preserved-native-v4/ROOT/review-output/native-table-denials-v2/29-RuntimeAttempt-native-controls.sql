-- PRIVILEGED NATIVE SHAPE CONTROL ONLY; all target USER triggers temporarily bypassed.
-- FK/CHECK/UNIQUE/internal RI triggers remain active. Roll back every mutation and trigger DDL.
BEGIN;
SET LOCAL search_path=pg_catalog;
SET LOCAL log_statement='none';
SET LOCAL log_min_error_statement='panic';
ALTER TABLE "platform"."runtime_attempt" DISABLE TRIGGER "attempt_transition";
ALTER TABLE "platform"."runtime_attempt" DISABLE TRIGGER "physical_guard";
SAVEPOINT native_control;
WITH changed AS (INSERT INTO "platform"."runtime_attempt"("id","work_item_id","attempt_number","fence","worker_id","result","reason_code","started_at","finished_at","created_at","mutation_transaction_id") VALUES ('7a4b6ed3-963b-5c35-8bac-c724d8aeef2f'::pg_catalog.uuid,'27117d68-88a6-5e89-9caa-32ac2306382b'::pg_catalog.uuid,'1'::pg_catalog.int4,'1'::pg_catalog.int8,'native-acl-bf6d3781eaed0f74522e1984'::pg_catalog.text,'pending'::platform.runtime_receipt_state,'native-acl-7a9d130cd58cbef36ae8b30b'::pg_catalog.text,'2026-11-17T00:00:00Z'::pg_catalog.timestamptz,'2026-11-18T00:00:00Z'::pg_catalog.timestamptz,'2026-11-17T00:00:00Z'::pg_catalog.timestamptz,'native-acl-setup-transaction'::pg_catalog.text) RETURNING 1) SELECT count(*)=1 AS native_insert_one FROM changed;
ROLLBACK TO SAVEPOINT native_control;
WITH changed AS (UPDATE "platform"."runtime_attempt" SET "id"='2ddf2791-91ad-5d9d-bdb5-2eaf43a142fe'::pg_catalog.uuid WHERE "id"='2ddf2791-91ad-5d9d-bdb5-2eaf43a142fe'::pg_catalog.uuid RETURNING 1) SELECT count(*)=1 AS native_update_one FROM changed;
ROLLBACK TO SAVEPOINT native_control;
WITH changed AS (DELETE FROM "platform"."runtime_attempt" WHERE "id"='2ddf2791-91ad-5d9d-bdb5-2eaf43a142fe'::pg_catalog.uuid RETURNING 1) SELECT count(*)=1 AS native_delete_one FROM changed;
ROLLBACK TO SAVEPOINT native_control;
ROLLBACK;
SELECT jsonb_build_object('control','native-control-RuntimeAttempt','all_declared_user_triggers_restored',NOT EXISTS(SELECT 1 FROM (VALUES ('platform.runtime_attempt','attempt_transition','O'),('platform.runtime_attempt','physical_guard','O')) e(table_name,name,enabled) LEFT JOIN pg_trigger t ON t.tgrelid=to_regclass(e.table_name) AND t.tgname=e.name WHERE t.oid IS NULL OR t.tgisinternal OR t.tgenabled::text IS DISTINCT FROM e.enabled));
