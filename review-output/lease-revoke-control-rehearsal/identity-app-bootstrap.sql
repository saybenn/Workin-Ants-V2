BEGIN;
INSERT INTO platform_private.identity_service_receipt ("id","service_principal","security_generation","transition","identity_authorization_ref","revoked_at") VALUES ('75e54933-ec50-5d11-8594-7d636430aff5','lease-revoke-app.v1',0,'bootstrap','synthetic-lease-revoke-app-bootstrap.v1',NULL);
INSERT INTO platform_private.identity_service_authorization ("service_principal","security_generation","identity_receipt_id") VALUES ('lease-revoke-app.v1',0,'75e54933-ec50-5d11-8594-7d636430aff5');
COMMIT;
