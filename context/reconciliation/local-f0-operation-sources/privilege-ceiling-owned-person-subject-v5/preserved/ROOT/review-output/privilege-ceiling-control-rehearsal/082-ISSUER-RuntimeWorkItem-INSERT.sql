-- Fresh actual authenticated role connection; no context handle/bind or fixture bypass. Stop/close on unexpected output.
BEGIN;
SET LOCAL search_path=pg_catalog;
INSERT INTO "platform"."runtime_work_item"("id","outbox_message_id","handler_name","semantic_work_key","state","fence","lease_token_hash","lease_expires_at","attempt_count","next_attempt_at","effect_receipt_id","created_at","mutation_transaction_id") VALUES ('aac01dd8-1e65-55ef-a70e-9de3ce8bdffb'::pg_catalog.uuid,'482d72fd-d770-5efb-b262-4d0d936c99d7'::pg_catalog.uuid,'native-acl-9a2b3b8c4c8543e073f452f1'::pg_catalog.text,'native-acl-529dd6c10e06c77f5f124776'::pg_catalog.text,'pending'::platform.runtime_work_state,'0'::pg_catalog.int8,NULL::pg_catalog.bpchar,NULL::pg_catalog.timestamptz,'0'::pg_catalog.int4,NULL::pg_catalog.timestamptz,NULL::pg_catalog.uuid,'2026-11-17T00:00:00Z'::pg_catalog.timestamptz,'native-acl-setup-transaction'::pg_catalog.text);
ROLLBACK;
