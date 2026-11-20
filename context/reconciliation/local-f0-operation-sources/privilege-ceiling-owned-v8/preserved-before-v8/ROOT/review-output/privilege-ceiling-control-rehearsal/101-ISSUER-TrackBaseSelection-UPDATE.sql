-- Fresh actual authenticated role connection; no context handle/bind or fixture bypass. Stop/close on unexpected output.
BEGIN;
SET LOCAL search_path=pg_catalog;
UPDATE "app"."track_base_selection" SET "id"='f997b61e-4875-5865-81ad-b8285ac1cef0'::pg_catalog.uuid WHERE "id"='f997b61e-4875-5865-81ad-b8285ac1cef0'::pg_catalog.uuid RETURNING 1;
ROLLBACK;
