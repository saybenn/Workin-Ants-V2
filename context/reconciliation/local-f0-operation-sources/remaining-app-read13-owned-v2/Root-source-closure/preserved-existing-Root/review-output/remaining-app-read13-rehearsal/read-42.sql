SELECT jsonb_build_object('read13_marker','RuntimeWorkItem/unbound'::text,'position','BEFORE'::text);
SELECT jsonb_build_object('model','RuntimeWorkItem','ids',coalesce(jsonb_agg(observed.id::text ORDER BY observed.id::text COLLATE "C"),'[]'::jsonb)) FROM (SELECT id,outbox_message_id,handler_name,semantic_work_key,state,fence,lease_token_hash,lease_expires_at,attempt_count,next_attempt_at,effect_receipt_id,created_at,mutation_transaction_id FROM platform.runtime_work_item WHERE id IN ('724f3bda-c6d6-570a-8dcb-60ff70f82902'::uuid,'3662e35d-1a1d-5769-89cb-7bfefd5b1e80'::uuid)) observed;
SET CONSTRAINTS ALL IMMEDIATE;
SELECT jsonb_build_object('read13_marker','RuntimeWorkItem/unbound'::text,'position','AFTER'::text);
