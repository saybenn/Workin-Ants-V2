-- Fresh actual authenticated role connection; no context handle/bind or fixture bypass. Stop/close on unexpected output.
BEGIN;
SET LOCAL search_path=pg_catalog;
UPDATE "app"."customer_profile_lifecycle_event" SET "id"='3191d0af-0ac2-5bc3-8835-d97ea3f8a30e'::pg_catalog.uuid WHERE "id"='3191d0af-0ac2-5bc3-8835-d97ea3f8a30e'::pg_catalog.uuid RETURNING 1;
ROLLBACK;
