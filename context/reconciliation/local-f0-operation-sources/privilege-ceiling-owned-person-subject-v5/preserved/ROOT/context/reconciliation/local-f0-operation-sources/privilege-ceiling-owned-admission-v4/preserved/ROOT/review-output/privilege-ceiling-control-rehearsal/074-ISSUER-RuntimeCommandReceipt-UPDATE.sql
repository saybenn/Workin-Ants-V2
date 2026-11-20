-- Fresh actual authenticated role connection; no context handle/bind or fixture bypass. Stop/close on unexpected output.
BEGIN;
SET LOCAL search_path=pg_catalog;
UPDATE "platform"."runtime_command_receipt" SET "id"='1e3ceb0a-4063-5b5a-b018-1e9fefef9c61'::pg_catalog.uuid WHERE "id"='1e3ceb0a-4063-5b5a-b018-1e9fefef9c61'::pg_catalog.uuid RETURNING 1;
ROLLBACK;
