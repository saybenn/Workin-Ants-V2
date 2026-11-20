SELECT 'WA_AW2_BEFORE_GENUINE_PENDING_SCHEDULE';
WITH changed AS (INSERT INTO platform.runtime_work_item (id,outbox_message_id,handler_name,semantic_work_key,state,fence,attempt_count) VALUES ('530db9d1-b945-53ec-bb0c-6d91c914b5fc','6be93914-5cc2-5cc0-a5b6-0906f8b4add1','assignDefaultFreeTrack.v1','customer_buyer_profile/cdfa190f-3235-5c98-b217-bf27a5d03d66/default-free-enrollment/v1','pending',0,0) RETURNING id) SELECT jsonb_build_object('scheduled',count(*)) FROM changed;
SET CONSTRAINTS ALL IMMEDIATE;
SELECT 'WA_AW2_AFTER_GENUINE_PENDING_SCHEDULE';
COMMIT;
