-- Fresh actual authenticated role connection; no context handle/bind or fixture bypass. Stop/close on unexpected output.
BEGIN;
SET LOCAL search_path=pg_catalog;
INSERT INTO "platform"."runtime_inbox_receipt"("id","outbox_message_id","consumer_owner","handler_name","payload_hash","effect_receipt_id","created_at","mutation_transaction_id") VALUES ('004c342a-2c6b-5039-9cdb-64e3c48e436d'::pg_catalog.uuid,'2302eb70-7637-5f00-b124-70a788511c59'::pg_catalog.uuid,'native-acl-6ce2b16eb9bb465ef2cb3bad'::pg_catalog.text,'native-acl-92c98a20ccbd16ba8ce3d690'::pg_catalog.text,'123ee97377e0e4978da53826169d71f6f4037d2b8ea135569ef3b150ad380fc6'::pg_catalog.bpchar,'e348c3f0-82b0-5c4a-9ee0-7d08c4566f80'::pg_catalog.uuid,'2026-11-17T00:00:00Z'::pg_catalog.timestamptz,'native-acl-setup-transaction'::pg_catalog.text);
ROLLBACK;
