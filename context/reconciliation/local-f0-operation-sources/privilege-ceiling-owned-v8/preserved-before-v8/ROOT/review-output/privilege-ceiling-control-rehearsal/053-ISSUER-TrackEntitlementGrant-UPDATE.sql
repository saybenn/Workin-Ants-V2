-- Fresh actual authenticated role connection; no context handle/bind or fixture bypass. Stop/close on unexpected output.
BEGIN;
SET LOCAL search_path=pg_catalog;
UPDATE "app"."track_entitlement_grants" SET "id"='a366bf4f-e520-5cb0-b3cf-a77afdbf3f21'::pg_catalog.uuid WHERE "id"='a366bf4f-e520-5cb0-b3cf-a77afdbf3f21'::pg_catalog.uuid RETURNING 1;
ROLLBACK;
