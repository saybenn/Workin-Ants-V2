SELECT jsonb_build_object('read13_marker','G4-B'::text,'position','BEFORE'::text);
INSERT INTO platform.runtime_work_item (attempt_count,effect_receipt_id,fence,handler_name,id,lease_expires_at,lease_token_hash,next_attempt_at,outbox_message_id,semantic_work_key,state) VALUES (0,NULL,0,'assignDefaultFreeTrack.v1','3662e35d-1a1d-5769-89cb-7bfefd5b1e80',NULL,NULL,NULL,'68b8ace5-8aff-5fac-8906-3a10ea333e2c','customer_buyer_profile/fdb9d7da-2124-5a29-a0d5-ca2e1a3ecc22/default-free-enrollment/v1','pending');
SET CONSTRAINTS ALL IMMEDIATE;
SELECT jsonb_build_object('read13_marker','G4-B'::text,'position','AFTER'::text);
COMMIT;
