-- Fresh actual authenticated role connection; no context handle/bind or fixture bypass. Stop/close on unexpected output.
BEGIN;
SET LOCAL search_path=pg_catalog;
DELETE FROM "app"."users" WHERE "id"='f7cb6f1f-f721-5562-aad6-85fd9ca958c5'::pg_catalog.uuid RETURNING 1;
ROLLBACK;
