-- Separate actual Identity service login; exact previous receipt, fixture-only upstream authorization.
BEGIN;
INSERT INTO platform_private.identity_service_receipt ("id","service_principal","previous_generation","previous_receipt_id","security_generation","transition","revoked_at","identity_authorization_ref") VALUES ('78b8e11a-2733-5b86-a90c-5474243581dd','worker-control-fixture.v1',0,'51352ebe-dac3-5d57-8a44-f1bbc30c680e',1,'rotate',NULL,'synthetic-worker-fixture-rotate.v1');
UPDATE platform_private.identity_service_authorization SET security_generation=1,identity_receipt_id='78b8e11a-2733-5b86-a90c-5474243581dd',revoked_at=(SELECT revoked_at FROM platform_private.identity_service_receipt WHERE id='78b8e11a-2733-5b86-a90c-5474243581dd') WHERE service_principal='worker-control-fixture.v1' AND security_generation=0 AND identity_receipt_id='51352ebe-dac3-5d57-8a44-f1bbc30c680e';
COMMIT;
