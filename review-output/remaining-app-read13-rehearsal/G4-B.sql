SELECT jsonb_build_object('read13_marker','G4-B'::text,'position','BEFORE'::text);
INSERT INTO platform.runtime_work_item (attempt_count,effect_receipt_id,fence,handler_name,id,lease_expires_at,lease_token_hash,next_attempt_at,outbox_message_id,semantic_work_key,state) VALUES (0,NULL,0,'assignDefaultFreeTrack.v1','a6ad9981-5a97-59ba-856b-02c6c3cb783b',NULL,NULL,NULL,'3b01e420-d726-5fec-8833-a35fabe7fdb4','customer_buyer_profile/9d6a8241-8c72-5540-b494-55dca1468442/default-free-enrollment/v1','pending');
SET CONSTRAINTS ALL IMMEDIATE;
SELECT jsonb_build_object('read13_marker','G4-B'::text,'position','AFTER'::text);
COMMIT;
