-- Fresh actual authenticated role connection; no context handle/bind or fixture bypass. Stop/close on unexpected output.
BEGIN;
SET LOCAL search_path=pg_catalog;
INSERT INTO "app"."consent_disposition"("id","proof_id","user_id","presentation_id","kind","semantic_key","fingerprint","created_at","mutation_transaction_id") VALUES ('78a5bb8b-8263-5624-99ac-b10ec69ca2c5'::pg_catalog.uuid,NULL::pg_catalog.uuid,'9e02328e-6e6a-581b-b747-4cf9398f8720'::pg_catalog.uuid,'72a60a96-4104-5ca0-b38a-00df941b0960'::pg_catalog.uuid,'declined'::app.consent_disposition_kind,'native-acl-370b93ffca102d8b169fab10'::pg_catalog.text,'cb02b66e426445c8e390c3fa8493257cc429c424c2ead9aaaf19e2417449a2b3'::pg_catalog.bpchar,'2026-11-17T00:00:00Z'::pg_catalog.timestamptz,'native-acl-setup-transaction'::pg_catalog.text);
ROLLBACK;
