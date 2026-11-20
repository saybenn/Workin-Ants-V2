SELECT jsonb_build_object('read13_marker','G9-AB'::text,'position','BEFORE'::text);
INSERT INTO platform.runtime_reservation (command_receipt_id,effect_receipt_id,expires_at,fence,id,owner_module_id,quantity,resource_key,resource_kind,semantic_key,state) VALUES ('7282489a-b97c-5bc4-8a52-dd343c7d4646',NULL,NULL,0,'570f8ca0-0d41-5478-bd07-c1c145304abf','customer_buyer_profile',1,'76b7a107-ed42-5471-9d24-946e10c38a4f','CustomerProfile','read13-0b7c519e-68be-4c44-ac42-83adcfe0def4-A-customer-provision-v1','active');
INSERT INTO platform.runtime_reservation (command_receipt_id,effect_receipt_id,expires_at,fence,id,owner_module_id,quantity,resource_key,resource_kind,semantic_key,state) VALUES ('6d1b5813-44bc-5ece-9c35-db327f128bd7',NULL,NULL,0,'ca735678-2cbb-56ff-ae43-2afe000df153','customer_buyer_profile',1,'fdb9d7da-2124-5a29-a0d5-ca2e1a3ecc22','CustomerProfile','read13-0b7c519e-68be-4c44-ac42-83adcfe0def4-B-customer-provision-v1','active');
SET CONSTRAINTS ALL IMMEDIATE;
SELECT jsonb_build_object('read13_marker','G9-AB'::text,'position','AFTER'::text);
COMMIT;
