-- Fresh actual authenticated role connection; no context handle/bind or fixture bypass. Stop/close on unexpected output.
BEGIN;
SET LOCAL search_path=pg_catalog;
INSERT INTO "app"."privacy_owner_receipt"("id","instruction_id","generation","disposition","execution_receipt_ref","legal_basis_ref","artifact_digest","artifact_version","result_schema_version","created_at","mutation_transaction_id") VALUES ('b8e464ac-4f69-5a12-93ed-ef77883ab596'::pg_catalog.uuid,'b1994733-021a-5612-97af-e1a5f9a9936e'::pg_catalog.uuid,'0'::pg_catalog.int8,'completed'::app.privacy_disposition_kind,'native-acl-23bcd4f66dfeddd2f8fc31f9'::pg_catalog.text,NULL::pg_catalog.text,NULL::pg_catalog.bpchar,NULL::pg_catalog.text,'1'::pg_catalog.text,'2026-11-17T00:00:00Z'::pg_catalog.timestamptz,'native-acl-setup-transaction'::pg_catalog.text);
ROLLBACK;
