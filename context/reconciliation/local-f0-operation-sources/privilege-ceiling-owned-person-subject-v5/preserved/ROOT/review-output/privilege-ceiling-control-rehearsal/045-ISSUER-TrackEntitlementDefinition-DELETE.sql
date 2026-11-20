-- Fresh actual authenticated role connection; no context handle/bind or fixture bypass. Stop/close on unexpected output.
BEGIN;
SET LOCAL search_path=pg_catalog;
DELETE FROM "app"."track_entitlement_definitions" WHERE "id"='cafe3d92-23ad-5f61-9f18-2f21e3e65900'::pg_catalog.uuid RETURNING 1;
ROLLBACK;
