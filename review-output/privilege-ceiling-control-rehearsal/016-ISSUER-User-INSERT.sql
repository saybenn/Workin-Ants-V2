-- Fresh actual authenticated role connection; no context handle/bind or fixture bypass. Stop/close on unexpected output.
BEGIN;
SET LOCAL search_path=pg_catalog;
INSERT INTO "app"."users"("id","email","handle","display_name","avatar_url","bio","city","state","country","is_public","created_at","updated_at","privacy_erased_at","privacy_erasure_status","revision","privacy_generation","mutation_transaction_id") VALUES ('a8c56c34-5761-593a-adee-d138ed81a5fe'::pg_catalog.uuid,NULL::pg_catalog.text,NULL::pg_catalog.text,NULL::pg_catalog.text,NULL::pg_catalog.text,NULL::pg_catalog.text,NULL::pg_catalog.text,NULL::pg_catalog.text,NULL::pg_catalog.text,true,'2026-11-17T00:00:00Z'::pg_catalog.timestamptz,'2026-11-17T00:00:00Z'::pg_catalog.timestamptz,NULL::pg_catalog.timestamptz,NULL::pg_catalog.text,'0'::pg_catalog.int8,'0'::pg_catalog.int8,'native-acl-setup-transaction'::pg_catalog.text);
ROLLBACK;
