-- PRIVILEGED NATIVE SHAPE CONTROL ONLY; all target USER triggers temporarily bypassed.
-- FK/CHECK/UNIQUE/internal RI triggers remain active. Roll back every mutation and trigger DDL.
BEGIN;
SET LOCAL search_path=pg_catalog;
SET LOCAL log_statement='none';
SET LOCAL log_min_error_statement='panic';
ALTER TABLE "app"."track_usage_reservation" DISABLE TRIGGER "owner_commit";
ALTER TABLE "app"."track_usage_reservation" DISABLE TRIGGER "physical_guard";
ALTER TABLE "app"."track_usage_reservation" DISABLE TRIGGER "usage_adapter_gate";
SAVEPOINT native_control;
WITH changed AS (INSERT INTO "app"."track_usage_reservation"("id","user_id","entitlement_id","period_start","period_end","quantity","semantic_key","reservation_id","accepted_source_owner","accepted_source_id","accepted_at","created_at","revision","mutation_transaction_id") VALUES ('20f6adb6-de11-5de9-955f-8d763f174a22'::pg_catalog.uuid,'56b17d64-3042-5f49-9d93-f4bb3cf2b8ee'::pg_catalog.uuid,'af6f8282-1305-5231-becf-c4d857810f62'::pg_catalog.uuid,'2026-11-17T00:00:00Z'::pg_catalog.timestamptz,'2026-11-18T00:00:00Z'::pg_catalog.timestamptz,'1'::pg_catalog.int4,'native-acl-687aa6bd5af40db02ab64ae2'::pg_catalog.text,'c9e71d89-df4e-5cf9-a553-72816a6a1c9e'::pg_catalog.uuid,'native-acl-0315e82b5ced53617eb392e1'::pg_catalog.text,NULL::pg_catalog.text,NULL::pg_catalog.timestamptz,'2026-11-17T00:00:00Z'::pg_catalog.timestamptz,'0'::pg_catalog.int8,'native-acl-setup-transaction'::pg_catalog.text) RETURNING 1) SELECT count(*)=1 AS native_insert_one FROM changed;
ROLLBACK TO SAVEPOINT native_control;
WITH changed AS (UPDATE "app"."track_usage_reservation" SET "id"='58f70189-e0ea-5faa-b3fa-68680f71b133'::pg_catalog.uuid WHERE "id"='58f70189-e0ea-5faa-b3fa-68680f71b133'::pg_catalog.uuid RETURNING 1) SELECT count(*)=1 AS native_update_one FROM changed;
ROLLBACK TO SAVEPOINT native_control;
WITH changed AS (DELETE FROM "app"."track_usage_reservation" WHERE "id"='58f70189-e0ea-5faa-b3fa-68680f71b133'::pg_catalog.uuid RETURNING 1) SELECT count(*)=1 AS native_delete_one FROM changed;
ROLLBACK TO SAVEPOINT native_control;
ROLLBACK;
SELECT jsonb_build_object('control','native-control-TrackUsageReservation','all_declared_user_triggers_restored',NOT EXISTS(SELECT 1 FROM (VALUES ('app.track_usage_reservation','owner_commit','O'),('app.track_usage_reservation','physical_guard','O'),('app.track_usage_reservation','usage_adapter_gate','O')) e(table_name,name,enabled) LEFT JOIN pg_trigger t ON t.tgrelid=to_regclass(e.table_name) AND t.tgname=e.name WHERE t.oid IS NULL OR t.tgisinternal OR t.tgenabled::text IS DISTINCT FROM e.enabled));
