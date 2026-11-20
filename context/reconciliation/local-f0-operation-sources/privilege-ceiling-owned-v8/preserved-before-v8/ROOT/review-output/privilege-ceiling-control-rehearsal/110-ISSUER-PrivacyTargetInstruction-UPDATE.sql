-- Fresh actual authenticated role connection; no context handle/bind or fixture bypass. Stop/close on unexpected output.
BEGIN;
SET LOCAL search_path=pg_catalog;
UPDATE "app"."privacy_target_instruction" SET "id"='bfa56011-5fe0-5101-9c6d-924081a37cb7'::pg_catalog.uuid WHERE "id"='bfa56011-5fe0-5101-9c6d-924081a37cb7'::pg_catalog.uuid RETURNING 1;
ROLLBACK;
