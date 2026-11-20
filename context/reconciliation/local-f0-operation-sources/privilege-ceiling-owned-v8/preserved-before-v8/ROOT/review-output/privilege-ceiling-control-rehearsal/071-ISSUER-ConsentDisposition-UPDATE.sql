-- Fresh actual authenticated role connection; no context handle/bind or fixture bypass. Stop/close on unexpected output.
BEGIN;
SET LOCAL search_path=pg_catalog;
UPDATE "app"."consent_disposition" SET "id"='a2fbc48e-33b3-532e-9e7a-4a7a8ac1dccd'::pg_catalog.uuid WHERE "id"='a2fbc48e-33b3-532e-9e7a-4a7a8ac1dccd'::pg_catalog.uuid RETURNING 1;
ROLLBACK;
