-- Fresh actual authenticated role connection; no context handle/bind or fixture bypass. Stop/close on unexpected output.
BEGIN;
SET LOCAL search_path=pg_catalog;
INSERT INTO "app"."track_entitlement_definitions"("id","key","label","description","value_type","track","is_active","created_at","updated_at","revision","mutation_transaction_id") VALUES ('fa8238ce-4f3b-5ada-a572-bd8c500ed246'::pg_catalog.uuid,'native-acl-8df20f644de7f69e9fe1d743'::pg_catalog.text,'native-acl-5dba482680970c6074406df4'::pg_catalog.text,NULL::pg_catalog.text,'boolean'::app.track_entitlement_value_type,NULL::app.account_track,true,'2026-11-17T00:00:00Z'::pg_catalog.timestamptz,'2026-11-17T00:00:00Z'::pg_catalog.timestamptz,'0'::pg_catalog.int8,'native-acl-setup-transaction'::pg_catalog.text);
ROLLBACK;
