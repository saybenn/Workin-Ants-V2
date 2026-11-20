-- Fresh actual authenticated role connection; no context handle/bind or fixture bypass. Stop/close on unexpected output.
BEGIN;
SET LOCAL search_path=pg_catalog;
UPDATE "app"."customer_profiles" SET "id"='97816ece-41af-5a37-993b-c703e390543a'::pg_catalog.uuid WHERE "id"='97816ece-41af-5a37-993b-c703e390543a'::pg_catalog.uuid RETURNING 1;
ROLLBACK;
