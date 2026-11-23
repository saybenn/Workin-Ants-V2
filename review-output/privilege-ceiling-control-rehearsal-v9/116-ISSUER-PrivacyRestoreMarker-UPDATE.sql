-- Fresh actual authenticated role connection; no context handle/bind or fixture bypass. Stop/close on unexpected output.
BEGIN;
SET LOCAL search_path=pg_catalog;
UPDATE "app"."privacy_restore_marker" SET "id"='f4f64db4-e460-5f50-ae58-2bd58d17811c'::pg_catalog.uuid WHERE "id"='f4f64db4-e460-5f50-ae58-2bd58d17811c'::pg_catalog.uuid RETURNING 1;
ROLLBACK;
