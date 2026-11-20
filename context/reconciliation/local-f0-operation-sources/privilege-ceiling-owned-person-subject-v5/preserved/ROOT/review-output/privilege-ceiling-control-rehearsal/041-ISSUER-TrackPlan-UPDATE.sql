-- Fresh actual authenticated role connection; no context handle/bind or fixture bypass. Stop/close on unexpected output.
BEGIN;
SET LOCAL search_path=pg_catalog;
UPDATE "app"."track_plans" SET "id"='4fac45ec-3ff4-59f9-8575-5615dde242fb'::pg_catalog.uuid WHERE "id"='4fac45ec-3ff4-59f9-8575-5615dde242fb'::pg_catalog.uuid RETURNING 1;
ROLLBACK;
