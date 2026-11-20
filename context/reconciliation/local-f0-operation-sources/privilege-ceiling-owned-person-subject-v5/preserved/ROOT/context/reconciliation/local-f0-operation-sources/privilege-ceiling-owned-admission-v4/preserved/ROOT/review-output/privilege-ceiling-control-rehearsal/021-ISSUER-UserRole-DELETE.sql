-- Fresh actual authenticated role connection; no context handle/bind or fixture bypass. Stop/close on unexpected output.
BEGIN;
SET LOCAL search_path=pg_catalog;
DELETE FROM "app"."user_roles" WHERE "user_id"='989b90a6-604e-5f8b-942d-c0f563355004'::pg_catalog.uuid AND "role"='user'::app.platform_role RETURNING 1;
ROLLBACK;
