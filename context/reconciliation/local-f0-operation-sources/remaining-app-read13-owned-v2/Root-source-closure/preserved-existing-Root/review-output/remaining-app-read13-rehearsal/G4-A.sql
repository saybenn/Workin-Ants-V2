SELECT jsonb_build_object('read13_marker','G4-A'::text,'position','BEFORE'::text);
INSERT INTO platform.runtime_work_item (attempt_count,effect_receipt_id,fence,handler_name,id,lease_expires_at,lease_token_hash,next_attempt_at,outbox_message_id,semantic_work_key,state) VALUES (0,NULL,0,'assignDefaultFreeTrack.v1','724f3bda-c6d6-570a-8dcb-60ff70f82902',NULL,NULL,NULL,'422bb5cb-5fad-5bb4-9c0e-1ad67229d5dd','customer_buyer_profile/76b7a107-ed42-5471-9d24-946e10c38a4f/default-free-enrollment/v1','pending');
SET CONSTRAINTS ALL IMMEDIATE;
SELECT jsonb_build_object('read13_marker','G4-A'::text,'position','AFTER'::text);
COMMIT;
