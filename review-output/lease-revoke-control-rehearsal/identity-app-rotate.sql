BEGIN;
INSERT INTO platform_private.identity_service_receipt ("id","service_principal","security_generation","transition","identity_authorization_ref","previous_generation","previous_receipt_id","revoked_at") VALUES ('6d56079c-e0a3-50b0-b97a-63e9a8d75987','lease-revoke-app.v1',1,'rotate','synthetic-lease-revoke-app-rotate.v1',0,'75e54933-ec50-5d11-8594-7d636430aff5',NULL);
UPDATE platform_private.identity_service_authorization SET security_generation=1,identity_receipt_id='6d56079c-e0a3-50b0-b97a-63e9a8d75987',revoked_at=(SELECT revoked_at FROM platform_private.identity_service_receipt WHERE id='6d56079c-e0a3-50b0-b97a-63e9a8d75987') WHERE service_principal='lease-revoke-app.v1' AND security_generation=0 AND identity_receipt_id='75e54933-ec50-5d11-8594-7d636430aff5';
COMMIT;
