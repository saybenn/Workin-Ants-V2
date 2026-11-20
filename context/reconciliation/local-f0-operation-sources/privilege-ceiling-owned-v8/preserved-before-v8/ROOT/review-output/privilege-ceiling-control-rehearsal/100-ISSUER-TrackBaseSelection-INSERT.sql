-- Fresh actual authenticated role connection; no context handle/bind or fixture bypass. Stop/close on unexpected output.
BEGIN;
SET LOCAL search_path=pg_catalog;
INSERT INTO "app"."track_base_selection"("id","user_id","track","customer_profile_id","candidate_profile_id","professional_profile_id","subscription_id","revision","source_generation","created_at","mutation_transaction_id") VALUES ('d97eeaca-8261-5e52-b2ba-1fc901133343'::pg_catalog.uuid,'b9bb35cc-27ae-5e38-98d5-d1e35c2bfa7f'::pg_catalog.uuid,'customer'::app.account_track,NULL::pg_catalog.uuid,NULL::pg_catalog.uuid,NULL::pg_catalog.uuid,'001261ce-759d-5711-9198-557895541b3b'::pg_catalog.uuid,'0'::pg_catalog.int8,'0'::pg_catalog.int8,'2026-11-17T00:00:00Z'::pg_catalog.timestamptz,'native-acl-setup-transaction'::pg_catalog.text);
ROLLBACK;
