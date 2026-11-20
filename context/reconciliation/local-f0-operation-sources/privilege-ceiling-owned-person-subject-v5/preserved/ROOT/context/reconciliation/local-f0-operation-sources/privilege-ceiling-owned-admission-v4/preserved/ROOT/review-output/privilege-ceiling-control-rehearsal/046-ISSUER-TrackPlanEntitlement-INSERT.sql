-- Fresh actual authenticated role connection; no context handle/bind or fixture bypass. Stop/close on unexpected output.
BEGIN;
SET LOCAL search_path=pg_catalog;
INSERT INTO "app"."track_plan_entitlements"("id","plan_id","entitlement_id","value_type","boolean_value","int_value","decimal_value","string_value","json_value","usage_period","created_at","updated_at","revision","mutation_transaction_id") VALUES ('7ebd7dd6-7c9c-5146-bed4-2693f8babd78'::pg_catalog.uuid,'8792f072-01e0-5070-b577-e34a2b13e476'::pg_catalog.uuid,'e51f149d-b600-5bfa-8910-7ace0d153be0'::pg_catalog.uuid,'boolean'::app.track_entitlement_value_type,true,NULL::pg_catalog.int4,NULL::pg_catalog.float8,NULL::pg_catalog.text,NULL::pg_catalog.jsonb,NULL::app.track_usage_period,'2026-11-17T00:00:00Z'::pg_catalog.timestamptz,'2026-11-17T00:00:00Z'::pg_catalog.timestamptz,'0'::pg_catalog.int8,'native-acl-setup-transaction'::pg_catalog.text);
ROLLBACK;
