-- Fresh actual authenticated role connection; no context handle/bind or fixture bypass. Stop/close on unexpected output.
BEGIN;
SET LOCAL search_path=pg_catalog;
UPDATE "app"."auth_provider_accounts" SET "id"='fdb2647d-da3c-5f81-bcde-5d6f83108ef1'::pg_catalog.uuid WHERE "id"='fdb2647d-da3c-5f81-bcde-5d6f83108ef1'::pg_catalog.uuid RETURNING 1;
ROLLBACK;
