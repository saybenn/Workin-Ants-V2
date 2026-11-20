-- Fresh actual authenticated role connection; no context handle/bind or fixture bypass. Stop/close on unexpected output.
BEGIN;
SET LOCAL search_path=pg_catalog;
INSERT INTO "platform"."runtime_attempt"("id","work_item_id","attempt_number","fence","worker_id","result","reason_code","started_at","finished_at","created_at","mutation_transaction_id") VALUES ('7a4b6ed3-963b-5c35-8bac-c724d8aeef2f'::pg_catalog.uuid,'27117d68-88a6-5e89-9caa-32ac2306382b'::pg_catalog.uuid,'1'::pg_catalog.int4,'1'::pg_catalog.int8,'native-acl-bf6d3781eaed0f74522e1984'::pg_catalog.text,'pending'::platform.runtime_receipt_state,'native-acl-7a9d130cd58cbef36ae8b30b'::pg_catalog.text,'2026-11-17T00:00:00Z'::pg_catalog.timestamptz,'2026-11-18T00:00:00Z'::pg_catalog.timestamptz,'2026-11-17T00:00:00Z'::pg_catalog.timestamptz,'native-acl-setup-transaction'::pg_catalog.text);
ROLLBACK;
