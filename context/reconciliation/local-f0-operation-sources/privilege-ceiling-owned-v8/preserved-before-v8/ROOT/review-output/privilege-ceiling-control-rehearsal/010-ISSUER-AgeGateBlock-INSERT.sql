-- Fresh actual authenticated role connection; no context handle/bind or fixture bypass. Stop/close on unexpected output.
BEGIN;
SET LOCAL search_path=pg_catalog;
INSERT INTO "app"."age_gate_blocks"("id","ip_hash","device_hash","reason","blocked_until","created_at","mutation_transaction_id") VALUES ('f8705b6f-7b00-566c-bf9a-a2a8bd04e379'::pg_catalog.uuid,NULL::pg_catalog.text,NULL::pg_catalog.text,'native-acl-1e14c72660f68b4bf4998e00'::pg_catalog.text,'2026-11-17T00:00:00Z'::pg_catalog.timestamptz,'2026-11-17T00:00:00Z'::pg_catalog.timestamptz,'native-acl-setup-transaction'::pg_catalog.text);
ROLLBACK;
