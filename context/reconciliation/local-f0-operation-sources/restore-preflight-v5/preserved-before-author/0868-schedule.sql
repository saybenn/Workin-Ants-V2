-- Actual bound wa_app_runtime; separate issuer has committed.
INSERT INTO platform.runtime_work_item ("id","outbox_message_id","handler_name","semantic_work_key","state","fence","attempt_count") VALUES ('927e6a91-e9f9-5a6a-88c0-2c6b7402e5f7','73c0bd05-54fe-5bee-acb1-17b64224f16a','assignDefaultFreeTrack.v1','customer_buyer_profile/bbe23c0b-ee0e-57f8-a60e-8333fe8650e2/default-free-enrollment/v1','pending',0,0);
SELECT 'WA_CTX01_SCHEDULE_READY';
COMMIT;
