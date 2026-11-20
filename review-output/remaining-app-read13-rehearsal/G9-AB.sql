SELECT jsonb_build_object('read13_marker','G9-AB'::text,'position','BEFORE'::text);
INSERT INTO platform.runtime_reservation (command_receipt_id,effect_receipt_id,expires_at,fence,id,owner_module_id,quantity,resource_key,resource_kind,semantic_key,state) VALUES ('7f470f9d-ffe1-5c29-ab7c-a48e3ea5a58d',NULL,NULL,0,'86f9e299-8b77-5a44-9524-818666ece211','customer_buyer_profile',1,'d4fd559a-4273-5e9b-9c4d-4a66e0760626','CustomerProfile','read13-d848e852-f857-4c03-8288-4893e2e8aa0c-A-customer-provision-v1','active');
INSERT INTO platform.runtime_reservation (command_receipt_id,effect_receipt_id,expires_at,fence,id,owner_module_id,quantity,resource_key,resource_kind,semantic_key,state) VALUES ('98626faf-d1ae-5f4d-8ed6-5c4d9168d251',NULL,NULL,0,'09be5411-0338-5038-8d04-12fabeb066df','customer_buyer_profile',1,'9d6a8241-8c72-5540-b494-55dca1468442','CustomerProfile','read13-d848e852-f857-4c03-8288-4893e2e8aa0c-B-customer-provision-v1','active');
SET CONSTRAINTS ALL IMMEDIATE;
SELECT jsonb_build_object('read13_marker','G9-AB'::text,'position','AFTER'::text);
COMMIT;
