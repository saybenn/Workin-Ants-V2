BEGIN;
INSERT INTO platform_private.identity_service_receipt ("id","service_principal","security_generation","transition","identity_authorization_ref","previous_generation","previous_receipt_id","revoked_at") VALUES ('933908f3-aabf-5697-ad70-a277050ca5a7','lease-revoke-app.v1',3,'recover','synthetic-lease-revoke-app-recover.v1',2,'cbc2f31e-df67-5f92-a56a-7911ac553332',NULL);
UPDATE platform_private.identity_service_authorization SET security_generation=3,identity_receipt_id='933908f3-aabf-5697-ad70-a277050ca5a7',revoked_at=(SELECT revoked_at FROM platform_private.identity_service_receipt WHERE id='933908f3-aabf-5697-ad70-a277050ca5a7') WHERE service_principal='lease-revoke-app.v1' AND security_generation=2 AND identity_receipt_id='cbc2f31e-df67-5f92-a56a-7911ac553332';
COMMIT;
