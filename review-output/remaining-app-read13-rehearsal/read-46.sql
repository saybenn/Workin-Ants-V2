SELECT jsonb_build_object('read13_marker','RuntimeWorkItem/root'::text,'position','BEFORE'::text);
SELECT jsonb_build_object('model','RuntimeWorkItem','ids',coalesce(jsonb_agg(observed.id::text ORDER BY observed.id::text COLLATE "C"),'[]'::jsonb)) FROM (SELECT id,outbox_message_id,handler_name,semantic_work_key,state,fence,lease_token_hash,lease_expires_at,attempt_count,next_attempt_at,effect_receipt_id,created_at,mutation_transaction_id FROM platform.runtime_work_item WHERE id IN ('77edf1fe-81d6-5738-ac45-6303875a18dc'::uuid,'a6ad9981-5a97-59ba-856b-02c6c3cb783b'::uuid)) observed;
SET CONSTRAINTS ALL IMMEDIATE;
SELECT jsonb_build_object('read13_marker','RuntimeWorkItem/root'::text,'position','AFTER'::text);
