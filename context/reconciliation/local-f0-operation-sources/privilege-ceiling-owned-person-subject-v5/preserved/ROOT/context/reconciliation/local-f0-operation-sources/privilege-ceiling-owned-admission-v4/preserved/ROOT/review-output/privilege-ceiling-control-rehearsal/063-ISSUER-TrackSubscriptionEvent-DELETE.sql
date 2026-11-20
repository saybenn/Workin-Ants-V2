-- Fresh actual authenticated role connection; no context handle/bind or fixture bypass. Stop/close on unexpected output.
BEGIN;
SET LOCAL search_path=pg_catalog;
DELETE FROM "app"."track_subscription_events" WHERE "id"='477ab2c9-2e2e-58ca-bd5e-9bf1963c1d11'::pg_catalog.uuid RETURNING 1;
ROLLBACK;
