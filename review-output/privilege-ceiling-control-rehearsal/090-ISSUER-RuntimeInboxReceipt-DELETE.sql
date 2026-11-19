-- Fresh actual authenticated role connection; no context handle/bind or fixture bypass. Stop/close on unexpected output.
BEGIN;
SET LOCAL search_path=pg_catalog;
DELETE FROM "platform"."runtime_inbox_receipt" WHERE "id"='7fdfecc1-b021-5567-9f7c-ccebebe0145b'::pg_catalog.uuid RETURNING 1;
ROLLBACK;
