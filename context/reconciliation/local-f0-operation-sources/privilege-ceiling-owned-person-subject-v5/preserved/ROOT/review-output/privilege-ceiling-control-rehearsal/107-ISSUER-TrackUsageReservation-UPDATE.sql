-- Fresh actual authenticated role connection; no context handle/bind or fixture bypass. Stop/close on unexpected output.
BEGIN;
SET LOCAL search_path=pg_catalog;
UPDATE "app"."track_usage_reservation" SET "id"='58f70189-e0ea-5faa-b3fa-68680f71b133'::pg_catalog.uuid WHERE "id"='58f70189-e0ea-5faa-b3fa-68680f71b133'::pg_catalog.uuid RETURNING 1;
ROLLBACK;
