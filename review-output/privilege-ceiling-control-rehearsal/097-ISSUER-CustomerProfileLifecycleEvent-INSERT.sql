-- Fresh actual authenticated role connection; no context handle/bind or fixture bypass. Stop/close on unexpected output.
BEGIN;
SET LOCAL search_path=pg_catalog;
INSERT INTO "app"."customer_profile_lifecycle_event"("id","customer_profile_id","command_receipt_id","source_revision","from_status","to_status","name","actor_user_id","created_at","mutation_transaction_id") VALUES ('1cf8e5b9-ae62-5655-9aa6-d2f267f4217f'::pg_catalog.uuid,'e633cfaa-85bd-598b-b9be-a089640093c8'::pg_catalog.uuid,'99214d11-13b4-5c8b-80d9-4e648a8c094b'::pg_catalog.uuid,'0'::pg_catalog.int8,NULL::app.profile_status,'active'::app.profile_status,'customer.lifecycle_changed.v1'::pg_catalog.text,'7ab4c614-56b1-5919-a94a-4900b857fa94'::pg_catalog.uuid,'2026-11-17T00:00:00Z'::pg_catalog.timestamptz,'native-acl-setup-transaction'::pg_catalog.text);
ROLLBACK;
