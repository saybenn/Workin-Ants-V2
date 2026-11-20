-- Fresh actual authenticated role connection; no context handle/bind or fixture bypass. Stop/close on unexpected output.
BEGIN;
SET LOCAL search_path=pg_catalog;
INSERT INTO "platform"."runtime_reservation"("id","command_receipt_id","owner_module_id","resource_kind","resource_key","semantic_key","quantity","state","fence","effect_receipt_id","expires_at","created_at","mutation_transaction_id") VALUES ('40082c51-d89e-53b7-b1c7-064ec1a0d00c'::pg_catalog.uuid,'47150589-716b-544d-89e7-5a804984408e'::pg_catalog.uuid,'native-acl-97df153815ca3721f74a2622'::pg_catalog.text,'native-acl-59e3c7e281ea7c4cbaaa6b95'::pg_catalog.text,'native-acl-9f086fcffb004912799c80b9'::pg_catalog.text,'native-acl-89844b35199ab822d0b4a073'::pg_catalog.text,'1'::pg_catalog.int4,'active'::platform.runtime_reservation_state,'0'::pg_catalog.int8,NULL::pg_catalog.uuid,NULL::pg_catalog.timestamptz,'2026-11-17T00:00:00Z'::pg_catalog.timestamptz,'native-acl-setup-transaction'::pg_catalog.text);
ROLLBACK;
