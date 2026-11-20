-- Fresh actual authenticated role connection; no context handle/bind or fixture bypass. Stop/close on unexpected output.
BEGIN;
SET LOCAL search_path=pg_catalog;
UPDATE "platform"."runtime_attempt" SET "id"='2ddf2791-91ad-5d9d-bdb5-2eaf43a142fe'::pg_catalog.uuid WHERE "id"='2ddf2791-91ad-5d9d-bdb5-2eaf43a142fe'::pg_catalog.uuid RETURNING 1;
ROLLBACK;
