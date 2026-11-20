BEGIN;
SET LOCAL search_path=pg_catalog;
INSERT INTO "platform_private"."identity_service_receipt"("id","service_principal","previous_generation","previous_receipt_id","security_generation","transition","revoked_at","identity_authorization_ref","mutation_transaction_id") VALUES ('41cea104-04e5-549a-9f97-bb31aec29914'::pg_catalog.uuid,'local-acl-fixture-not-an-authorized-adapter'::pg_catalog.text,NULL::pg_catalog.int8,NULL::pg_catalog.uuid,0::pg_catalog.int8,'bootstrap'::pg_catalog.text,NULL::pg_catalog.timestamptz,'native-acl-18608e11574f3fde68d41cbc'::pg_catalog.text,'native-acl-setup-transaction'::pg_catalog.text);
ROLLBACK;
