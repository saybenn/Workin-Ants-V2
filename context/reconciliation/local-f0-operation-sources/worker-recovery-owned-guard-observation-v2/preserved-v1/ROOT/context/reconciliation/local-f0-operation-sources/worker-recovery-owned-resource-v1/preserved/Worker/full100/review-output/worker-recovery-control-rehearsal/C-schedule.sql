-- Actual bound wa_app_runtime; issuer already committed.
INSERT INTO platform.runtime_work_item ("id","outbox_message_id","handler_name","semantic_work_key","state","fence","attempt_count") VALUES ('fe698747-d296-5435-9b12-050bc8f8339b','d5eb5e25-5254-52b6-9309-cb9ff22950fb','assignDefaultFreeTrack.v1','customer_buyer_profile/73292b10-226f-5588-920d-cb9421f6e358/default-free-enrollment/v1','pending',0,0);
SELECT 'WA_WORKER_SCHEDULE_READY';
COMMIT;
