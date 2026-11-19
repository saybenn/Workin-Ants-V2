-- Fresh actual authenticated role connection; no context handle/bind or fixture bypass. Stop/close on unexpected output.
BEGIN;
SET LOCAL search_path=pg_catalog;
DELETE FROM "app"."auth_provider_accounts" WHERE "id"='fdb2647d-da3c-5f81-bcde-5d6f83108ef1'::pg_catalog.uuid RETURNING 1;
ROLLBACK;
