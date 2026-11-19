-- Fresh actual authenticated role connection; no context handle/bind or fixture bypass. Stop/close on unexpected output.
BEGIN;
SET LOCAL search_path=pg_catalog;
UPDATE "app"."track_usage_counters" SET "id"='d184a890-2be0-5d50-ad54-1297d6724531'::pg_catalog.uuid WHERE "id"='d184a890-2be0-5d50-ad54-1297d6724531'::pg_catalog.uuid RETURNING 1;
ROLLBACK;
