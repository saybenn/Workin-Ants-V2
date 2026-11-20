-- Actual bound wa_app_runtime; issuer already committed.
INSERT INTO platform.runtime_work_item ("id","outbox_message_id","handler_name","semantic_work_key","state","fence","attempt_count") VALUES ('7ce05560-4c08-5c4b-a975-9d521f2d2864','9c3b8f32-d0bb-5efa-aef9-0bf64edc8d81','assignDefaultFreeTrack.v1','customer_buyer_profile/51b0eaff-9164-508e-9cd9-c8fc679af06a/default-free-enrollment/v1','pending',0,0);
SELECT 'WA_WORKER_SCHEDULE_READY';
COMMIT;
