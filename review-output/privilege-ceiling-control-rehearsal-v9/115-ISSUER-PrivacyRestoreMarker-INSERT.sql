-- Fresh actual authenticated role connection; no context handle/bind or fixture bypass. Stop/close on unexpected output.
BEGIN;
SET LOCAL search_path=pg_catalog;
INSERT INTO "app"."privacy_restore_marker"("id","owner_module_id","target_kind","source_id","generation","action","source_receipt_id","restore_point_ref","applied_at","created_at","revision","mutation_transaction_id") VALUES ('297f8698-4f61-5bca-95f8-14e79087aa2b'::pg_catalog.uuid,'native-acl-4fe861dcb302e5fc89a6e135'::pg_catalog.text,'native-acl-521ca14dd2674eb02a0c8620'::pg_catalog.text,'native-acl-08f2af72a944fb0ff950beab'::pg_catalog.text,'0'::pg_catalog.int8,'export'::app.privacy_action_kind,'5a843917-ae56-5739-8771-e703108ef221'::pg_catalog.uuid,NULL::pg_catalog.text,NULL::pg_catalog.timestamptz,'2026-11-17T00:00:00Z'::pg_catalog.timestamptz,'0'::pg_catalog.int8,'native-acl-setup-transaction'::pg_catalog.text);
ROLLBACK;
