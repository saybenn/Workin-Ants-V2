-- Fresh actual authenticated role connection; no context handle/bind or fixture bypass. Stop/close on unexpected output.
BEGIN;
SET LOCAL search_path=pg_catalog;
DELETE FROM "platform"."runtime_effect_receipt" WHERE "id"='577c76bc-cb91-5fc6-9d88-48f0016bcc95'::pg_catalog.uuid RETURNING 1;
ROLLBACK;
