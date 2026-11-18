-- PRIVILEGED NATIVE SHAPE CONTROL ONLY; all target USER triggers temporarily bypassed.
-- FK/CHECK/UNIQUE/internal RI triggers remain active. Roll back every mutation and trigger DDL.
BEGIN;
SET LOCAL search_path=pg_catalog;
SET LOCAL log_statement='none';
SET LOCAL log_min_error_statement='panic';
ALTER TABLE "platform"."runtime_reservation" DISABLE TRIGGER "physical_guard";
ALTER TABLE "platform"."runtime_reservation" DISABLE TRIGGER "reservation_transition";
SAVEPOINT native_control;
WITH changed AS (INSERT INTO "platform"."runtime_reservation"("id","command_receipt_id","owner_module_id","resource_kind","resource_key","semantic_key","quantity","state","fence","effect_receipt_id","expires_at","created_at","mutation_transaction_id") VALUES ('40082c51-d89e-53b7-b1c7-064ec1a0d00c'::pg_catalog.uuid,'47150589-716b-544d-89e7-5a804984408e'::pg_catalog.uuid,'native-acl-97df153815ca3721f74a2622'::pg_catalog.text,'native-acl-59e3c7e281ea7c4cbaaa6b95'::pg_catalog.text,'native-acl-9f086fcffb004912799c80b9'::pg_catalog.text,'native-acl-89844b35199ab822d0b4a073'::pg_catalog.text,'1'::pg_catalog.int4,'active'::platform.runtime_reservation_state,'0'::pg_catalog.int8,NULL::pg_catalog.uuid,NULL::pg_catalog.timestamptz,'2026-11-17T00:00:00Z'::pg_catalog.timestamptz,'native-acl-setup-transaction'::pg_catalog.text) RETURNING 1) SELECT count(*)=1 AS native_insert_one FROM changed;
ROLLBACK TO SAVEPOINT native_control;
WITH changed AS (UPDATE "platform"."runtime_reservation" SET "id"='5718446a-8390-5069-acee-07cafa3a2d4d'::pg_catalog.uuid WHERE "id"='5718446a-8390-5069-acee-07cafa3a2d4d'::pg_catalog.uuid RETURNING 1) SELECT count(*)=1 AS native_update_one FROM changed;
ROLLBACK TO SAVEPOINT native_control;
WITH changed AS (DELETE FROM "platform"."runtime_reservation" WHERE "id"='5718446a-8390-5069-acee-07cafa3a2d4d'::pg_catalog.uuid RETURNING 1) SELECT count(*)=1 AS native_delete_one FROM changed;
ROLLBACK TO SAVEPOINT native_control;
ROLLBACK;
SELECT jsonb_build_object('control','native-control-RuntimeReservation','all_declared_user_triggers_restored',NOT EXISTS(SELECT 1 FROM (VALUES ('platform.runtime_reservation','physical_guard','O'),('platform.runtime_reservation','reservation_transition','O')) e(table_name,name,enabled) LEFT JOIN pg_trigger t ON t.tgrelid=to_regclass(e.table_name) AND t.tgname=e.name WHERE t.oid IS NULL OR t.tgisinternal OR t.tgenabled::text IS DISTINCT FROM e.enabled));
