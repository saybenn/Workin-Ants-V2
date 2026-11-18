-- Synthetic upstream authorization only; actual separate Identity SQL login.
BEGIN;
INSERT INTO platform_private.identity_service_receipt (id,service_principal,previous_generation,previous_receipt_id,security_generation,transition,identity_authorization_ref) VALUES ('7133a084-53bf-5f89-9159-f9baf185751c','ctx01-control-synthetic.v1',0,'9f6b0fa9-7a6f-52a6-8297-6ea55cbf6c0f',1,'revoke','restore01-synthetic-revoke.v1');
UPDATE platform_private.identity_service_authorization a SET security_generation=r.security_generation,identity_receipt_id=r.id,revoked_at=r.revoked_at FROM platform_private.identity_service_receipt r WHERE a.service_principal='ctx01-control-synthetic.v1' AND r.id='7133a084-53bf-5f89-9159-f9baf185751c';
SELECT 'WA_RESTORE01_IDENTITY_READY';
COMMIT;
