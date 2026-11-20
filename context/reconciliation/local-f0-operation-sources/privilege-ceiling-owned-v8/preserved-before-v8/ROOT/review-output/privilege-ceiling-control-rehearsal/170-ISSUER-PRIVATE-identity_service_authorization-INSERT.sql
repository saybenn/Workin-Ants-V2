BEGIN;
SET LOCAL search_path=pg_catalog;
INSERT INTO "platform_private"."identity_service_authorization"("service_principal","security_generation","revoked_at","identity_receipt_id","mutation_transaction_id") VALUES ('privilege-ceiling-source-native-candidate.v1'::pg_catalog.text,0::pg_catalog.int8,'2026-11-17T00:00:00Z'::pg_catalog.timestamptz,'0cc77e3b-9355-5288-8212-1c03eb3388b7'::pg_catalog.uuid,'native-acl-setup-transaction'::pg_catalog.text);
ROLLBACK;
