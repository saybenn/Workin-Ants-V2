-- Fresh actual authenticated role connection; no context handle/bind or fixture bypass. Stop/close on unexpected output.
BEGIN;
SET LOCAL search_path=pg_catalog;
DELETE FROM "platform"."database_action_grant" WHERE "id"='bdc1cb43-7041-5bc5-bc31-08140c7f28c1'::pg_catalog.uuid RETURNING 1;
ROLLBACK;
