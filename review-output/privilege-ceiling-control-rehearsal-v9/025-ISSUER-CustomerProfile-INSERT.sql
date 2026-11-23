-- Fresh actual authenticated role connection; no context handle/bind or fixture bypass. Stop/close on unexpected output.
BEGIN;
SET LOCAL search_path=pg_catalog;
INSERT INTO "app"."customer_profiles"("id","user_id","status","display_name","avatar_media_id","city","state","country","created_at","updated_at","archived_at","revision","privacy_generation","mutation_transaction_id") VALUES ('bab9586f-2605-534e-a027-d79b44b29213'::pg_catalog.uuid,'501fb57b-3601-55e5-a7f2-768b7c0dbf04'::pg_catalog.uuid,'active'::app.profile_status,NULL::pg_catalog.text,NULL::pg_catalog.uuid,NULL::pg_catalog.text,NULL::pg_catalog.text,NULL::pg_catalog.text,'2026-11-17T00:00:00Z'::pg_catalog.timestamptz,'2026-11-17T00:00:00Z'::pg_catalog.timestamptz,NULL::pg_catalog.timestamptz,'0'::pg_catalog.int8,'0'::pg_catalog.int8,'native-acl-setup-transaction'::pg_catalog.text);
ROLLBACK;
