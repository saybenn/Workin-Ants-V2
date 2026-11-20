-- Fresh actual authenticated role connection; no context handle/bind or fixture bypass. Stop/close on unexpected output.
BEGIN;
SET LOCAL search_path=pg_catalog;
INSERT INTO "app"."access_audit_logs"("id","actor_user_id","target_type","target_id","action","sensitivity","access_decision","request_id","ip_hash","user_agent","previous_hash","entry_hash","created_at","mutation_transaction_id") VALUES ('0c07261b-bf9d-5379-a267-2c18fc6631e2'::pg_catalog.uuid,NULL::pg_catalog.uuid,'native-acl-138114460a6c2972fec68c65'::pg_catalog.text,'3685b557-69e8-5940-8f5f-0aff8a33223a'::pg_catalog.uuid,'file_read'::app.access_audit_action,'normal'::app.data_sensitivity,NULL::app.healthcare_access_decision,NULL::pg_catalog.text,NULL::pg_catalog.text,NULL::pg_catalog.text,NULL::pg_catalog.text,NULL::pg_catalog.text,'2026-11-17T00:00:00Z'::pg_catalog.timestamptz,'native-acl-setup-transaction'::pg_catalog.text);
ROLLBACK;
