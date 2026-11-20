BEGIN;
SET LOCAL search_path=pg_catalog;
UPDATE "platform_private"."identity_service_authorization" SET "security_generation"=0::pg_catalog.int8 WHERE "service_principal"='local-acl-fixture-not-an-authorized-adapter'::pg_catalog.text RETURNING 1;
ROLLBACK;
