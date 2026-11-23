-- Fresh actual authenticated role connection; no context handle/bind or fixture bypass. Stop/close on unexpected output.
BEGIN;
SET LOCAL search_path=pg_catalog;
UPDATE "platform"."runtime_reservation" SET "id"='5718446a-8390-5069-acee-07cafa3a2d4d'::pg_catalog.uuid WHERE "id"='5718446a-8390-5069-acee-07cafa3a2d4d'::pg_catalog.uuid RETURNING 1;
ROLLBACK;
