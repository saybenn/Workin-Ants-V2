-- Actual separate wa_identity_service_authority login; synthetic authorization prerequisite only.
BEGIN;
INSERT INTO platform_private.identity_service_receipt ("id","service_principal","security_generation","transition","identity_authorization_ref") VALUES ('51352ebe-dac3-5d57-8a44-f1bbc30c680e','worker-control-fixture.v1',0,'bootstrap','synthetic-worker-fixture-authorization.v1');
INSERT INTO platform_private.identity_service_authorization ("service_principal","security_generation","identity_receipt_id") VALUES ('worker-control-fixture.v1',0,'51352ebe-dac3-5d57-8a44-f1bbc30c680e');
COMMIT;
