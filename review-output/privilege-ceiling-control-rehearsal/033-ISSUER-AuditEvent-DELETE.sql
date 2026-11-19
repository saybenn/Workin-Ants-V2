-- Fresh actual authenticated role connection; no context handle/bind or fixture bypass. Stop/close on unexpected output.
BEGIN;
SET LOCAL search_path=pg_catalog;
DELETE FROM "app"."audit_events" WHERE "id"='65210591-87ce-5a46-a627-19800deeeb64'::pg_catalog.uuid RETURNING 1;
ROLLBACK;
