BEGIN;
INSERT INTO platform_private.identity_service_receipt ("id","service_principal","security_generation","transition","identity_authorization_ref","revoked_at") VALUES ('f23ed33a-575b-5ecd-95bd-2f573a7004a6','lease-revoke-worker.v1',0,'bootstrap','synthetic-lease-revoke-worker-bootstrap.v1',NULL);
INSERT INTO platform_private.identity_service_authorization ("service_principal","security_generation","identity_receipt_id") VALUES ('lease-revoke-worker.v1',0,'f23ed33a-575b-5ecd-95bd-2f573a7004a6');
COMMIT;
