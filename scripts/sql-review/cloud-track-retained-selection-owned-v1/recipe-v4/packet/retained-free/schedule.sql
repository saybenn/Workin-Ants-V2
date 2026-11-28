-- Actual bound wa_app_runtime; issuer already committed.
INSERT INTO platform.runtime_work_item ("id","outbox_message_id","handler_name","semantic_work_key","state","fence","attempt_count") VALUES ('771e9030-3d83-5d15-873e-6bfa3bf4f389','add755d4-036e-5130-83f0-6ff538c68cc1','assignDefaultFreeTrack.v1','customer_buyer_profile/c30510f5-b27a-5296-8749-c248c4d4724a/default-free-enrollment/v1','pending',0,0);
SELECT 'WA_WORKER_SCHEDULE_READY';
COMMIT;
