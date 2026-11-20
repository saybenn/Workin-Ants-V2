-- Fresh actual authenticated role connection; no context handle/bind or fixture bypass. Stop/close on unexpected output.
BEGIN;
SET LOCAL search_path=pg_catalog;
DELETE FROM "app"."consent_logs" WHERE "id"='4448a52e-880c-55d6-8523-06a4c4252d12'::pg_catalog.uuid RETURNING 1;
ROLLBACK;
