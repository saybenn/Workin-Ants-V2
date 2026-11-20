-- Fresh actual authenticated role connection; no context handle/bind or fixture bypass. Stop/close on unexpected output.
BEGIN;
SET LOCAL search_path=pg_catalog;
UPDATE "app"."access_audit_logs" SET "id"='2591049c-35d4-5206-b07d-4725ebffe6bd'::pg_catalog.uuid WHERE "id"='2591049c-35d4-5206-b07d-4725ebffe6bd'::pg_catalog.uuid RETURNING 1;
ROLLBACK;
