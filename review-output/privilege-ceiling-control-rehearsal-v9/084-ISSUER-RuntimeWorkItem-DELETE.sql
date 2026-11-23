-- Fresh actual authenticated role connection; no context handle/bind or fixture bypass. Stop/close on unexpected output.
BEGIN;
SET LOCAL search_path=pg_catalog;
DELETE FROM "platform"."runtime_work_item" WHERE "id"='87f1066d-9bf1-5809-a1da-ffd96c766ad4'::pg_catalog.uuid RETURNING 1;
ROLLBACK;
