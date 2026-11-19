-- Fresh actual authenticated role connection; no context handle/bind or fixture bypass. Stop/close on unexpected output.
BEGIN;
SET LOCAL search_path=pg_catalog;
DELETE FROM "platform"."runtime_outbox_message" WHERE "id"='f5b2dce7-397b-5aa6-8b52-040f3fc4adcc'::pg_catalog.uuid RETURNING 1;
ROLLBACK;
