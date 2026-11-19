-- Fresh actual authenticated role connection; no context handle/bind or fixture bypass. Stop/close on unexpected output.
BEGIN;
SET LOCAL search_path=pg_catalog;
DELETE FROM "app"."track_usage_events" WHERE "id"='9d0f416e-fab9-5a36-a967-17bb956916d1'::pg_catalog.uuid RETURNING 1;
ROLLBACK;
