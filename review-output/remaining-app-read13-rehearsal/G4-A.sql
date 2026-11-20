SELECT jsonb_build_object('read13_marker','G4-A'::text,'position','BEFORE'::text);
INSERT INTO platform.runtime_work_item (attempt_count,effect_receipt_id,fence,handler_name,id,lease_expires_at,lease_token_hash,next_attempt_at,outbox_message_id,semantic_work_key,state) VALUES (0,NULL,0,'assignDefaultFreeTrack.v1','77edf1fe-81d6-5738-ac45-6303875a18dc',NULL,NULL,NULL,'9945b1b6-cd27-5b92-aaa8-f143fb7a4e9d','customer_buyer_profile/d4fd559a-4273-5e9b-9c4d-4a66e0760626/default-free-enrollment/v1','pending');
SET CONSTRAINTS ALL IMMEDIATE;
SELECT jsonb_build_object('read13_marker','G4-A'::text,'position','AFTER'::text);
COMMIT;
