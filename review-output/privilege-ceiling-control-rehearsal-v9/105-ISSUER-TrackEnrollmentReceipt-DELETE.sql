-- Fresh actual authenticated role connection; no context handle/bind or fixture bypass. Stop/close on unexpected output.
BEGIN;
SET LOCAL search_path=pg_catalog;
DELETE FROM "app"."track_enrollment_receipt" WHERE "id"='9eeefad7-2b05-550e-aaec-72f267ac473c'::pg_catalog.uuid RETURNING 1;
ROLLBACK;
