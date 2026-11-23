-- Fresh actual authenticated role connection; no context handle/bind or fixture bypass. Stop/close on unexpected output.
BEGIN;
SET LOCAL search_path=pg_catalog;
DELETE FROM "app"."privacy_owner_receipt" WHERE "id"='fb76abbb-ce1f-5804-a623-66325639cb1c'::pg_catalog.uuid RETURNING 1;
ROLLBACK;
