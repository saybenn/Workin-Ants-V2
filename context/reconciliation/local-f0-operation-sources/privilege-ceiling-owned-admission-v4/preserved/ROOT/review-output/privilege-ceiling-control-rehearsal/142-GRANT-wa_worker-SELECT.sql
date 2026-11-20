-- Fresh actual authenticated role connection; no context handle/bind or fixture bypass. Stop/close on unexpected output.
BEGIN;
SET LOCAL search_path=pg_catalog;
SELECT count("id") FROM "platform"."database_action_grant" WHERE "id"='f1597749-8f18-5ade-87b5-e4a3dd56107c'::pg_catalog.uuid;
ROLLBACK;
