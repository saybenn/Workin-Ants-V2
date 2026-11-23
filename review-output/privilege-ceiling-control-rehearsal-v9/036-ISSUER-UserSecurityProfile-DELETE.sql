-- Fresh actual authenticated role connection; no context handle/bind or fixture bypass. Stop/close on unexpected output.
BEGIN;
SET LOCAL search_path=pg_catalog;
DELETE FROM "app"."user_security_profiles" WHERE "id"='678f9096-36e2-5cfd-a884-850c82d28332'::pg_catalog.uuid RETURNING 1;
ROLLBACK;
