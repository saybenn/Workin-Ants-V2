-- Synthetic upstream authorization only; actual separate Identity SQL login.
BEGIN;
INSERT INTO platform_private.identity_service_receipt (id,service_principal,previous_generation,previous_receipt_id,security_generation,transition,identity_authorization_ref) VALUES ('4bea96c4-5749-5093-b120-82aba41e7c40','ctx01-control-synthetic.v1',1,'7133a084-53bf-5f89-9159-f9baf185751c',2,'recover','restore01-synthetic-recover.v1');
UPDATE platform_private.identity_service_authorization a SET security_generation=r.security_generation,identity_receipt_id=r.id,revoked_at=r.revoked_at FROM platform_private.identity_service_receipt r WHERE a.service_principal='ctx01-control-synthetic.v1' AND r.id='4bea96c4-5749-5093-b120-82aba41e7c40';
SELECT 'WA_RESTORE01_IDENTITY_READY';
COMMIT;
