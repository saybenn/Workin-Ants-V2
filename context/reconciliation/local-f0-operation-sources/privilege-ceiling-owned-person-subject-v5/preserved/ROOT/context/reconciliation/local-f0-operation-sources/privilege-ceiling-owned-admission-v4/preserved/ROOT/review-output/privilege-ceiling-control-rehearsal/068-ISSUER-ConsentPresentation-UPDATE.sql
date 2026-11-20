-- Fresh actual authenticated role connection; no context handle/bind or fixture bypass. Stop/close on unexpected output.
BEGIN;
SET LOCAL search_path=pg_catalog;
UPDATE "app"."consent_presentation" SET "id"='00f918b5-5bf0-5e33-91f0-58baddd61daf'::pg_catalog.uuid WHERE "id"='00f918b5-5bf0-5e33-91f0-58baddd61daf'::pg_catalog.uuid RETURNING 1;
ROLLBACK;
