-- Fresh actual authenticated role connection; no context handle/bind or fixture bypass. Stop/close on unexpected output.
BEGIN;
SET LOCAL search_path=pg_catalog;
DELETE FROM "app"."access_audit_logs" WHERE "id"='2591049c-35d4-5206-b07d-4725ebffe6bd'::pg_catalog.uuid RETURNING 1;
ROLLBACK;
