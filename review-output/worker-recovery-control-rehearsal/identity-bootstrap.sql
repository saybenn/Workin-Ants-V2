-- Actual separate wa_identity_service_authority login; synthetic authorization prerequisite only.
BEGIN;
INSERT INTO platform_private.identity_service_receipt ("id","service_principal","security_generation","transition","identity_authorization_ref") VALUES ('18655009-e252-51a2-8f2d-2b6baa9d9a68','worker-recovery-core-fixture.v1',0,'bootstrap','synthetic-worker-fixture-authorization.v1');
INSERT INTO platform_private.identity_service_authorization ("service_principal","security_generation","identity_receipt_id") VALUES ('worker-recovery-core-fixture.v1',0,'18655009-e252-51a2-8f2d-2b6baa9d9a68');
COMMIT;
