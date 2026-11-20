-- Fresh actual authenticated role connection; no context handle/bind or fixture bypass. Stop/close on unexpected output.
BEGIN;
SET LOCAL search_path=pg_catalog;
DELETE FROM "app"."professional_profiles" WHERE "id"='4f372302-b4cb-5520-a037-0766f14b3323'::pg_catalog.uuid RETURNING 1;
ROLLBACK;
