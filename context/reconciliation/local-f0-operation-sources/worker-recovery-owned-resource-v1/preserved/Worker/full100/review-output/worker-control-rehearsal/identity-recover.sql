-- Separate actual Identity service login; exact previous receipt, fixture-only upstream authorization.
BEGIN;
INSERT INTO platform_private.identity_service_receipt ("id","service_principal","previous_generation","previous_receipt_id","security_generation","transition","revoked_at","identity_authorization_ref") VALUES ('1e74ff3d-38ac-5d8f-bc91-52202ba1d4dc','worker-control-fixture.v1',2,'ae69ab21-e762-59e7-8f4f-8137bb1eba68',3,'recover',NULL,'synthetic-worker-fixture-recover.v1');
UPDATE platform_private.identity_service_authorization SET security_generation=3,identity_receipt_id='1e74ff3d-38ac-5d8f-bc91-52202ba1d4dc',revoked_at=(SELECT revoked_at FROM platform_private.identity_service_receipt WHERE id='1e74ff3d-38ac-5d8f-bc91-52202ba1d4dc') WHERE service_principal='worker-control-fixture.v1' AND security_generation=2 AND identity_receipt_id='ae69ab21-e762-59e7-8f4f-8137bb1eba68';
COMMIT;
