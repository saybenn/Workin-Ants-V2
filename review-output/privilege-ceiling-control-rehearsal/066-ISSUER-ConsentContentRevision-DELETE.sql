-- Fresh actual authenticated role connection; no context handle/bind or fixture bypass. Stop/close on unexpected output.
BEGIN;
SET LOCAL search_path=pg_catalog;
DELETE FROM "app"."consent_content_revision" WHERE "id"='059a8b87-99cc-59ea-ab6d-13561ca909dd'::pg_catalog.uuid RETURNING 1;
ROLLBACK;
