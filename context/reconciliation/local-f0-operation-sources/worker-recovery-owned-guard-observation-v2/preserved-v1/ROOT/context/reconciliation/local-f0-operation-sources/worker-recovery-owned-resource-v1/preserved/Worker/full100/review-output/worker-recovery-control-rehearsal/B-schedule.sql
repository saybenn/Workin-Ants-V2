-- Actual bound wa_app_runtime; issuer already committed.
INSERT INTO platform.runtime_work_item ("id","outbox_message_id","handler_name","semantic_work_key","state","fence","attempt_count") VALUES ('bd16c4aa-52bd-50f6-950e-c55e501f2b21','380420fc-4dba-57c6-8242-30d4f0b044b1','assignDefaultFreeTrack.v1','customer_buyer_profile/c3f5fa23-f064-5509-8e30-adf9855a53d9/default-free-enrollment/v1','pending',0,0);
SELECT 'WA_WORKER_SCHEDULE_READY';
COMMIT;
