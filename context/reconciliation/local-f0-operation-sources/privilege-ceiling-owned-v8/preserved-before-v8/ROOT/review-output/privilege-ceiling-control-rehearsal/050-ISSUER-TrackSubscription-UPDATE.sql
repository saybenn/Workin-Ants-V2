-- Fresh actual authenticated role connection; no context handle/bind or fixture bypass. Stop/close on unexpected output.
BEGIN;
SET LOCAL search_path=pg_catalog;
UPDATE "app"."track_subscriptions" SET "id"='23bf79b6-6c20-594c-96a7-b07e23db9ee0'::pg_catalog.uuid WHERE "id"='23bf79b6-6c20-594c-96a7-b07e23db9ee0'::pg_catalog.uuid RETURNING 1;
ROLLBACK;
