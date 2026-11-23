-- Fresh actual authenticated role connection; no context handle/bind or fixture bypass. Stop/close on unexpected output.
BEGIN;
SET LOCAL search_path=pg_catalog;
DELETE FROM "app"."privacy_requests" WHERE "id"='a429a294-38dc-55fd-971b-b97ec04ef5cf'::pg_catalog.uuid RETURNING 1;
ROLLBACK;
