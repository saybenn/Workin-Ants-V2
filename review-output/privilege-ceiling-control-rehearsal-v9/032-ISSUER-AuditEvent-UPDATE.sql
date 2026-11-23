-- Fresh actual authenticated role connection; no context handle/bind or fixture bypass. Stop/close on unexpected output.
BEGIN;
SET LOCAL search_path=pg_catalog;
UPDATE "app"."audit_events" SET "id"='65210591-87ce-5a46-a627-19800deeeb64'::pg_catalog.uuid WHERE "id"='65210591-87ce-5a46-a627-19800deeeb64'::pg_catalog.uuid RETURNING 1;
ROLLBACK;
