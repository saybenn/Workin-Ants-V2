-- Fresh actual authenticated role connection; no context handle/bind or fixture bypass. Stop/close on unexpected output.
BEGIN;
SET LOCAL search_path=pg_catalog;
INSERT INTO "app"."age_gate_attempts"("id","user_id","ip_hash","device_hash","region","result","birth_year","age_band","blocked_until","created_at","mutation_transaction_id") VALUES ('d37e8c18-7364-5c1a-bd05-924d6630a173'::pg_catalog.uuid,NULL::pg_catalog.uuid,NULL::pg_catalog.text,NULL::pg_catalog.text,NULL::pg_catalog.text,'allowed'::app.age_gate_result,NULL::pg_catalog.int4,NULL::pg_catalog.text,NULL::pg_catalog.timestamptz,'2026-11-17T00:00:00Z'::pg_catalog.timestamptz,'native-acl-setup-transaction'::pg_catalog.text);
ROLLBACK;
