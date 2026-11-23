BEGIN;
SET LOCAL search_path=pg_catalog;
UPDATE "platform_private"."identity_service_receipt" SET "security_generation"=0::pg_catalog.int8 WHERE "id"='0cc77e3b-9355-5288-8212-1c03eb3388b7'::pg_catalog.uuid RETURNING 1;
ROLLBACK;
