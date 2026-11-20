-- Separate actual Identity service login; exact previous receipt, fixture-only upstream authorization.
BEGIN;
INSERT INTO platform_private.identity_service_receipt ("id","service_principal","previous_generation","previous_receipt_id","security_generation","transition","revoked_at","identity_authorization_ref") VALUES ('ae69ab21-e762-59e7-8f4f-8137bb1eba68','worker-control-fixture.v1',1,'78b8e11a-2733-5b86-a90c-5474243581dd',2,'revoke',clock_timestamp(),'synthetic-worker-fixture-revoke.v1');
UPDATE platform_private.identity_service_authorization SET security_generation=2,identity_receipt_id='ae69ab21-e762-59e7-8f4f-8137bb1eba68',revoked_at=(SELECT revoked_at FROM platform_private.identity_service_receipt WHERE id='ae69ab21-e762-59e7-8f4f-8137bb1eba68') WHERE service_principal='worker-control-fixture.v1' AND security_generation=1 AND identity_receipt_id='78b8e11a-2733-5b86-a90c-5474243581dd';
COMMIT;
