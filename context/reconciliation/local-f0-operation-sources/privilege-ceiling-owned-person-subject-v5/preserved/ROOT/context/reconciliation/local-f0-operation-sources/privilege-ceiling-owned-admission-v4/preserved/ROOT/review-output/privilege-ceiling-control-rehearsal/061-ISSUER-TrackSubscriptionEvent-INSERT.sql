-- Fresh actual authenticated role connection; no context handle/bind or fixture bypass. Stop/close on unexpected output.
BEGIN;
SET LOCAL search_path=pg_catalog;
INSERT INTO "app"."track_subscription_events"("id","subscription_id","plan_id","user_id","name","from_status","to_status","provider","provider_event_id","metadata","created_at","mutation_transaction_id") VALUES ('b7cd8849-e7a6-59ef-9948-7c1448cf52d6'::pg_catalog.uuid,NULL::pg_catalog.uuid,NULL::pg_catalog.uuid,'e2be55a6-0aa0-58fb-8d45-735624b37743'::pg_catalog.uuid,'native-acl-78154aca25752e8b72f3bb14'::pg_catalog.text,NULL::app.track_subscription_status,NULL::app.track_subscription_status,NULL::app.track_billing_provider,NULL::pg_catalog.text,NULL::pg_catalog.jsonb,'2026-11-17T00:00:00Z'::pg_catalog.timestamptz,'native-acl-setup-transaction'::pg_catalog.text);
ROLLBACK;
