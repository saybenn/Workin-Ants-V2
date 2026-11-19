-- Fresh actual authenticated role connection; no context handle/bind or fixture bypass. Stop/close on unexpected output.
BEGIN;
SET LOCAL search_path=pg_catalog;
UPDATE "app"."track_plan_entitlements" SET "id"='f2ff834c-834c-554b-b6fa-f18de37789c0'::pg_catalog.uuid WHERE "id"='f2ff834c-834c-554b-b6fa-f18de37789c0'::pg_catalog.uuid RETURNING 1;
ROLLBACK;
