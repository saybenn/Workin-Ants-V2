-- Actual bound wa_app_runtime; issuer already committed.
INSERT INTO platform.runtime_work_item ("id","outbox_message_id","handler_name","semantic_work_key","state","fence","attempt_count") VALUES ('0733d5c9-e95e-5c48-a176-60e6bf6a2220','a2d80749-774a-55be-af38-56fbd9ac799c','assignDefaultFreeTrack.v1','customer_buyer_profile/b32b7f93-fed4-59c7-8721-14d72dd661fa/default-free-enrollment/v1','pending',0,0);
SELECT 'WA_WORKER_SCHEDULE_READY';
COMMIT;
