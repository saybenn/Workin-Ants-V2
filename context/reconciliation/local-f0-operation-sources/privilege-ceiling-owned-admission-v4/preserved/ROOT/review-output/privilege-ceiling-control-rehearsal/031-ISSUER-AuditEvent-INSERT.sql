-- Fresh actual authenticated role connection; no context handle/bind or fixture bypass. Stop/close on unexpected output.
BEGIN;
SET LOCAL search_path=pg_catalog;
INSERT INTO "app"."audit_events"("id","actor_user_id","entity_type","entity_id","action","metadata","created_at","mutation_transaction_id") VALUES ('720818b0-aefd-5f64-90c1-d889551cf3c3'::pg_catalog.uuid,NULL::pg_catalog.uuid,'native-acl-2b66dc96de6efcd8c79b48d5'::pg_catalog.text,NULL::pg_catalog.uuid,'native-acl-12e263fae5932d68fae5d736'::pg_catalog.text,NULL::pg_catalog.jsonb,'2026-11-17T00:00:00Z'::pg_catalog.timestamptz,'native-acl-setup-transaction'::pg_catalog.text);
ROLLBACK;
