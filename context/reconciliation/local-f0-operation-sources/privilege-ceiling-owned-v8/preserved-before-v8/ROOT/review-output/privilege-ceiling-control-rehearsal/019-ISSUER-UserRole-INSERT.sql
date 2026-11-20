-- Fresh actual authenticated role connection; no context handle/bind or fixture bypass. Stop/close on unexpected output.
BEGIN;
SET LOCAL search_path=pg_catalog;
INSERT INTO "app"."user_roles"("user_id","role","created_at","revision","mutation_transaction_id") VALUES ('c09f00d1-6d76-5c9f-b9af-2e779a5bcbcf'::pg_catalog.uuid,'user'::app.platform_role,'2026-11-17T00:00:00Z'::pg_catalog.timestamptz,'0'::pg_catalog.int8,'native-acl-setup-transaction'::pg_catalog.text);
ROLLBACK;
