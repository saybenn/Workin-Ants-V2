-- Separate actual wa_identity_service_authority; fixture-only upstream authorization.
BEGIN;
INSERT INTO platform_private.identity_service_receipt ("id","service_principal","security_generation","transition","identity_authorization_ref") VALUES ('9f6b0fa9-7a6f-52a6-8297-6ea55cbf6c0f','ctx01-control-synthetic.v1',0,'bootstrap','ctx01-synthetic-bootstrap.v1');
INSERT INTO platform_private.identity_service_authorization ("service_principal","security_generation","identity_receipt_id") VALUES ('ctx01-control-synthetic.v1',0,'9f6b0fa9-7a6f-52a6-8297-6ea55cbf6c0f');
COMMIT;
