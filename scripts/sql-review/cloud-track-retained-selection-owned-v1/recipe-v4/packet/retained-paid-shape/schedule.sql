-- Actual bound wa_app_runtime; issuer already committed.
INSERT INTO platform.runtime_work_item ("id","outbox_message_id","handler_name","semantic_work_key","state","fence","attempt_count") VALUES ('92533181-a521-5ea7-a17b-60c58661ee6f','36ec5ebd-4379-5885-9349-aea52771af7e','assignDefaultFreeTrack.v1','customer_buyer_profile/aa50ee27-b66d-5fa9-b5f4-5144848088c9/default-free-enrollment/v1','pending',0,0);
SELECT 'WA_WORKER_SCHEDULE_READY';
COMMIT;
