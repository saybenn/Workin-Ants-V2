-- Fresh actual authenticated role connection; no context handle/bind or fixture bypass. Stop/close on unexpected output.
BEGIN;
SET LOCAL search_path=pg_catalog;
DELETE FROM "app"."candidate_profiles" WHERE "id"='c7c63525-4c7e-5b01-8e1f-da6e61dac15b'::pg_catalog.uuid RETURNING 1;
ROLLBACK;
