BEGIN;
INSERT INTO platform_private.identity_service_receipt ("id","service_principal","security_generation","transition","identity_authorization_ref","previous_generation","previous_receipt_id") VALUES ('cbc2f31e-df67-5f92-a56a-7911ac553332','lease-revoke-app.v1',2,'revoke','synthetic-lease-revoke-app-revoke.v1',1,'6d56079c-e0a3-50b0-b97a-63e9a8d75987');
UPDATE platform_private.identity_service_authorization SET security_generation=2,identity_receipt_id='cbc2f31e-df67-5f92-a56a-7911ac553332',revoked_at=(SELECT revoked_at FROM platform_private.identity_service_receipt WHERE id='cbc2f31e-df67-5f92-a56a-7911ac553332') WHERE service_principal='lease-revoke-app.v1' AND security_generation=1 AND identity_receipt_id='6d56079c-e0a3-50b0-b97a-63e9a8d75987';
COMMIT;
