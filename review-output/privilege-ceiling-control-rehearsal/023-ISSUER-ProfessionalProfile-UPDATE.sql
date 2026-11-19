-- Fresh actual authenticated role connection; no context handle/bind or fixture bypass. Stop/close on unexpected output.
BEGIN;
SET LOCAL search_path=pg_catalog;
UPDATE "app"."professional_profiles" SET "id"='4f372302-b4cb-5520-a037-0766f14b3323'::pg_catalog.uuid WHERE "id"='4f372302-b4cb-5520-a037-0766f14b3323'::pg_catalog.uuid RETURNING 1;
ROLLBACK;
