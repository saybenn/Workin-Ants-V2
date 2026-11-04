-- SQL-03/04/05/07/08/09/12/14/16: F0 only. Never run in this assignment.
-- This source fragment is assembled after structure/functions and before atomic guards.

ALTER TABLE platform.owner_mutation_evidence ADD CONSTRAINT evidence_identity
 CHECK (evidence_schema_id='urn:workinants:database-review:owner-evidence:v1#/$defs/'||aggregate_kind AND evidence_schema_version='1'
 AND evidence_body->>'schema'='database-owner-evidence.v1' AND evidence_body->>'model'=aggregate_kind
 AND evidence_body->>'owner'=owner_module_id AND evidence_body->>'decisionRef'=decision_ref
 AND length(decision_ref)>0 AND committed_revision>=0
 AND (previous_revision IS NULL OR committed_revision=previous_revision+1));
-- Review SQL storage digest codec: SHA-256 over PostgreSQL 17 jsonb::text UTF-8.
-- Wire serializers must implement this exact storage codec or use a reviewed
-- separate wire digest; equality with an unspecified JSON encoding is not assumed.
ALTER TABLE platform.owner_mutation_evidence ADD CONSTRAINT evidence_storage_digest CHECK
 (evidence_digest=encode(sha256(convert_to(evidence_body::text,'UTF8')),'hex'));
ALTER TABLE platform.runtime_outbox_message ADD CONSTRAINT payload_storage_digest CHECK
 (payload_hash=encode(sha256(convert_to(payload::text,'UTF8')),'hex'));
ALTER TABLE platform.runtime_command_receipt ADD CONSTRAINT result_storage_digest CHECK
 (result_body IS NULL OR (result_digest IS NOT NULL AND result_digest=encode(sha256(convert_to(result_body::text,'UTF8')),'hex')));

CREATE FUNCTION platform_private.message_json_guard() RETURNS trigger
LANGUAGE plpgsql SECURITY INVOKER SET search_path=pg_catalog AS $wa$
BEGIN
 IF NEW.kind='event' AND NEW.name='customer.lifecycle_changed.v1'
  AND NEW.payload_schema_id='urn:workin-ants:types:v1#/$defs/EventPayload_customer_lifecycle_changed_v1'
  AND NEW.schema_version='1' AND NEW.producer_owner='customer_buyer_profile'
  AND platform_private.json_customer_event(NEW.payload)
  AND NEW.payload->>'customerProfileId'=NEW.aggregate_id
  AND NEW.payload->>'lifecycleRevision'=NEW.source_revision::text THEN RETURN NEW; END IF;
 IF NEW.kind='command' AND NEW.name='assignDefaultFreeTrack.v1'
  AND NEW.payload_schema_id='urn:workinants:database-review:foundation-payloads:v1#/$defs/assignDefaultFreeTrackCustomerCommand'
  AND NEW.schema_version='1' AND NEW.producer_owner='customer_buyer_profile'
  AND platform_private.json_track_command(NEW.payload)
  AND NEW.payload->>'customerProfileId'=NEW.aggregate_id
  AND NEW.payload->>'sourceCreationRevision'=NEW.source_revision::text
  AND NEW.payload->>'sourceCreationReceipt'=NEW.command_receipt_id::text THEN RETURN NEW; END IF;
 RAISE EXCEPTION 'unregistered or incoherent F0 message';
END $wa$;
CREATE TRIGGER message_json BEFORE INSERT ON platform.runtime_outbox_message
 FOR EACH ROW EXECUTE FUNCTION platform_private.message_json_guard();

ALTER TABLE platform.runtime_command_receipt ADD CONSTRAINT result_json_boundary CHECK (
 result_body IS NULL OR (
  (operation='SH-004.v1' AND result_schema_id='SH-004.v1#/$defs/response'
   AND platform_private.json_sh004_result(result_body)) OR
  (operation='SH-114.v1' AND result_schema_id='SH-114.v1#/$defs/response'
   AND platform_private.json_sh114_result(result_body)) OR
  (operation='assignDefaultFreeTrack.v1'
   AND result_schema_id='urn:workinants:database-review:foundation-payloads:v1#/$defs/assignDefaultFreeTrackCustomerResult'
   AND platform_private.json_track_result(result_body))
 ));
ALTER TABLE platform.runtime_command_receipt ADD CONSTRAINT committed_result CHECK
 (state<>'committed' OR (result_digest IS NOT NULL AND
  (operation NOT IN ('SH-004.v1','SH-114.v1','assignDefaultFreeTrack.v1') OR result_body IS NOT NULL)));
ALTER TABLE platform.runtime_outbox_message ADD CONSTRAINT source_message_revision CHECK
 (source_revision>=0 AND source_generation>=0 AND ordinal>=0 AND aggregate_kind='CustomerProfile');

CREATE FUNCTION platform_private.command_state_guard() RETURNS trigger
LANGUAGE plpgsql SECURITY INVOKER SET search_path=pg_catalog AS $wa$
BEGIN
 IF TG_OP='UPDATE' AND (OLD.state IN ('committed','denied','fenced_noncommit')
  OR (to_jsonb(NEW)-ARRAY['state','source_revision','result_digest','result_body','mutation_transaction_id'])
   IS DISTINCT FROM (to_jsonb(OLD)-ARRAY['state','source_revision','result_digest','result_body','mutation_transaction_id']))
 THEN RAISE EXCEPTION 'terminal receipt or semantic identity immutable'; END IF;
 RETURN NEW;
END $wa$;
CREATE TRIGGER command_state BEFORE UPDATE ON platform.runtime_command_receipt
 FOR EACH ROW EXECUTE FUNCTION platform_private.command_state_guard();

ALTER TABLE app.consent_content_revision ADD CONSTRAINT exact_content_hash CHECK
 (content_hash=encode(sha256(convert_to(content_text,'UTF8')),'hex') AND
  (review_state<>'legal_approved' OR NULLIF(legal_approval_ref,'') IS NOT NULL));
ALTER TABLE app.consent_presentation ADD CONSTRAINT exact_rendered_hash CHECK
 (rendered_hash=encode(sha256(convert_to(rendered_text,'UTF8')),'hex'));
CREATE FUNCTION platform_private.consent_guard() RETURNS trigger
LANGUAGE plpgsql SECURITY INVOKER SET search_path=pg_catalog AS $wa$
DECLARE p app.consent_presentation; c app.consent_content_revision; a app.consent_logs;
BEGIN
 IF NOT platform_private.context_subject(NEW.user_id) THEN RAISE EXCEPTION 'accepting subject is not current principal' USING ERRCODE='42501'; END IF;
 IF TG_TABLE_NAME='consent_logs' THEN
  SELECT * INTO STRICT p FROM app.consent_presentation WHERE id=NEW.presentation_id;
  SELECT * INTO STRICT c FROM app.consent_content_revision WHERE id=p.content_revision_id;
  IF p.user_id<>NEW.user_id OR p.content_revision_id<>NEW.content_revision_id
   OR c.type<>NEW.type OR c.version<>NEW.version OR p.rendered_hash<>NEW.presentation_hash
   OR p.action_owner<>NEW.action_owner OR p.action<>NEW.action
   OR p.context_owner<>NEW.context_owner OR p.context_kind<>NEW.context_kind
   OR p.context_id IS DISTINCT FROM NEW.context_id
   OR NEW.accepted_at<p.created_at OR NEW.accepted_at<c.effective_from
   OR (c.effective_until IS NOT NULL AND NEW.accepted_at>=c.effective_until)
   OR c.review_state='draft' OR NULLIF(NEW.acceptance_key,'') IS NULL
  THEN RAISE EXCEPTION 'exact consent binding required'; END IF;
  -- Actual rendering, affirmative acceptance and production legal applicability
  -- are trusted Consent-owner code obligations, never inferred from these hashes.
 ELSIF TG_TABLE_NAME='consent_disposition' THEN
  SELECT * INTO STRICT p FROM app.consent_presentation WHERE id=NEW.presentation_id;
  IF p.user_id<>NEW.user_id THEN RAISE EXCEPTION 'foreign consent subject'; END IF;
  IF NEW.proof_id IS NOT NULL THEN
   SELECT * INTO STRICT a FROM app.consent_logs WHERE id=NEW.proof_id;
   IF a.user_id<>NEW.user_id OR a.presentation_id<>NEW.presentation_id THEN RAISE EXCEPTION 'foreign proof'; END IF;
  ELSIF NEW.kind<>'declined' THEN RAISE EXCEPTION 'withdrawal/supersession needs original proof'; END IF;
 END IF;
 RETURN NEW;
END $wa$;
CREATE TRIGGER consent_proof BEFORE INSERT ON app.consent_logs
 FOR EACH ROW EXECUTE FUNCTION platform_private.consent_guard();
CREATE TRIGGER consent_disposition BEFORE INSERT ON app.consent_disposition
 FOR EACH ROW EXECUTE FUNCTION platform_private.consent_guard();
CREATE TRIGGER consent_presentation_subject BEFORE INSERT ON app.consent_presentation
 FOR EACH ROW EXECUTE FUNCTION platform_private.consent_guard();

-- SQL-08: Customer source event and both outbox kinds must describe the same write.
CREATE FUNCTION platform_private.customer_atomic() RETURNS trigger
LANGUAGE plpgsql SECURITY INVOKER SET search_path=pg_catalog AS $wa$
DECLARE e platform.owner_mutation_evidence; h app.customer_profile_lifecycle_event;
BEGIN
 SELECT * INTO STRICT e FROM platform.owner_mutation_evidence WHERE aggregate_kind='CustomerProfile'
  AND aggregate_id=NEW.id::text AND committed_revision=NEW.revision
  AND mutation_transaction_id=pg_current_xact_id()::text;
 SELECT * INTO STRICT h FROM app.customer_profile_lifecycle_event WHERE customer_profile_id=NEW.id
  AND source_revision=NEW.revision AND command_receipt_id=e.command_receipt_id
  AND mutation_transaction_id=e.mutation_transaction_id;
 IF h.to_status<>NEW.status OR h.actor_user_id<>NEW.user_id
  OR h.from_status IS DISTINCT FROM (CASE WHEN TG_OP='INSERT' THEN NULL::app.profile_status ELSE OLD.status END)
  OR NOT EXISTS(SELECT 1 FROM platform.runtime_outbox_message o WHERE o.command_receipt_id=e.command_receipt_id
    AND o.aggregate_kind='CustomerProfile' AND o.aggregate_id=NEW.id::text
    AND o.source_revision=NEW.revision AND o.source_generation=NEW.privacy_generation
    AND o.name='customer.lifecycle_changed.v1' AND o.kind='event'
    AND o.payload->>'userId'=NEW.user_id::text AND o.payload->>'safeState'=NEW.status::text
    AND o.mutation_transaction_id=e.mutation_transaction_id)
 THEN RAISE EXCEPTION 'missing atomic Customer lifecycle fact'; END IF;
 IF TG_OP='INSERT' AND NOT EXISTS(SELECT 1 FROM platform.runtime_outbox_message o
   WHERE o.command_receipt_id=e.command_receipt_id AND o.name='assignDefaultFreeTrack.v1' AND o.kind='command'
    AND o.aggregate_id=NEW.id::text AND o.source_revision=NEW.revision
    AND o.source_generation=NEW.privacy_generation AND o.payload->>'userId'=NEW.user_id::text
    AND o.mutation_transaction_id=e.mutation_transaction_id)
 THEN RAISE EXCEPTION 'missing durable default-Free intent'; END IF;
 RETURN NULL;
END $wa$;
CREATE CONSTRAINT TRIGGER customer_atomic AFTER INSERT OR UPDATE ON app.customer_profiles
 DEFERRABLE INITIALLY DEFERRED FOR EACH ROW EXECUTE FUNCTION platform_private.customer_atomic();

-- SQL-09: unknown never releases by clock expiry; durable noncommit is necessary.
ALTER TABLE platform.runtime_reservation ADD CONSTRAINT positive_reservation CHECK (quantity>0);
ALTER TABLE platform.runtime_attempt ADD CONSTRAINT attempt_order CHECK (attempt_number>0 AND fence>0);
ALTER TABLE platform.runtime_work_item ADD CONSTRAINT lease_shape CHECK
 ((state='leased' AND lease_token_hash IS NOT NULL AND lease_expires_at IS NOT NULL AND fence>0)
  OR (state<>'leased' AND lease_token_hash IS NULL AND lease_expires_at IS NULL));
CREATE FUNCTION platform_private.runtime_transition() RETURNS trigger
LANGUAGE plpgsql SECURITY INVOKER SET search_path=pg_catalog AS $wa$
DECLARE w platform.runtime_work_item; e platform.runtime_effect_receipt;
BEGIN
 IF TG_TABLE_NAME='runtime_work_item' THEN
  IF TG_OP='UPDATE' THEN
   IF OLD.state='completed' OR NEW.attempt_count<OLD.attempt_count THEN RAISE EXCEPTION 'terminal work/regressive attempt'; END IF;
   IF NEW.state='leased' AND (OLD.state<>'leased' OR NEW.lease_token_hash IS DISTINCT FROM OLD.lease_token_hash) THEN
    IF NEW.fence<>OLD.fence+1 OR NEW.attempt_count<>OLD.attempt_count+1
     OR (OLD.state='leased' AND OLD.lease_expires_at>clock_timestamp())
    THEN RAISE EXCEPTION 'invalid claim/reclaim'; END IF;
   ELSIF NEW.fence<>OLD.fence THEN RAISE EXCEPTION 'fence may change only on claim'; END IF;
   IF OLD.state='leased' AND NEW.state<>'leased' AND (OLD.lease_expires_at<=clock_timestamp()
    OR current_setting('wa.lease_hash',true) IS DISTINCT FROM OLD.lease_token_hash::text
    OR current_setting('wa.fence',true) IS DISTINCT FROM OLD.fence::text)
   THEN RAISE EXCEPTION 'expired or foreign worker'; END IF;
  END IF;
  IF NEW.state='completed' THEN
   SELECT * INTO STRICT e FROM platform.runtime_effect_receipt WHERE id=NEW.effect_receipt_id;
   IF e.state<>'committed' OR e.fence<>NEW.fence THEN RAISE EXCEPTION 'completion without current committed effect'; END IF;
  END IF;
 ELSIF TG_TABLE_NAME='runtime_attempt' THEN
  SELECT * INTO STRICT w FROM platform.runtime_work_item WHERE id=NEW.work_item_id;
  IF w.fence<>NEW.fence OR NEW.attempt_number<>w.attempt_count THEN RAISE EXCEPTION 'stale attempt'; END IF;
 ELSIF TG_TABLE_NAME='runtime_reservation' AND TG_OP='UPDATE' THEN
  IF OLD.state IN ('committed','released') THEN RAISE EXCEPTION 'terminal reservation'; END IF;
  IF NEW.state='released' AND OLD.state='unknown' AND NOT EXISTS
   (SELECT 1 FROM platform.runtime_effect_receipt r WHERE r.id=NEW.effect_receipt_id
    AND r.state='fenced_noncommit' AND r.fence>=OLD.fence)
  THEN RAISE EXCEPTION 'unknown needs durable fenced noncommit'; END IF;
 END IF;
 RETURN NEW;
END $wa$;
CREATE TRIGGER work_transition BEFORE INSERT OR UPDATE ON platform.runtime_work_item FOR EACH ROW EXECUTE FUNCTION platform_private.runtime_transition();
CREATE TRIGGER attempt_transition BEFORE INSERT ON platform.runtime_attempt FOR EACH ROW EXECUTE FUNCTION platform_private.runtime_transition();
CREATE TRIGGER reservation_transition BEFORE UPDATE ON platform.runtime_reservation FOR EACH ROW EXECUTE FUNCTION platform_private.runtime_transition();

-- Effect insertion must match the still-current protected work lease, not an
-- arbitrary fence copied from an old message or an untrusted GUC alone.
CREATE FUNCTION platform_private.effect_fence_guard() RETURNS trigger
LANGUAGE plpgsql SECURITY INVOKER SET search_path=pg_catalog AS $wa$
DECLARE w platform.runtime_work_item;
BEGIN
 IF session_user::text='wa_worker' THEN
  SELECT * INTO STRICT w FROM platform.runtime_work_item WHERE effect_receipt_id=NEW.id;
  IF w.state<>'leased' OR w.fence<>NEW.fence OR w.lease_expires_at<=clock_timestamp()
   OR current_setting('wa.lease_hash',true) IS DISTINCT FROM w.lease_token_hash::text
   OR current_setting('wa.fence',true) IS DISTINCT FROM w.fence::text
  THEN RAISE EXCEPTION 'stale worker effect'; END IF;
 END IF;
 RETURN NULL;
END $wa$;
CREATE CONSTRAINT TRIGGER effect_fence AFTER INSERT ON platform.runtime_effect_receipt
 DEFERRABLE INITIALLY DEFERRED FOR EACH ROW EXECUTE FUNCTION platform_private.effect_fence_guard();

-- Locked current selection is authoritative. Catalog retirement alone does not
-- invalidate an already valid selected subscription.
CREATE FUNCTION platform_private.track_enrollment_commit() RETURNS trigger
LANGUAGE plpgsql SECURITY INVOKER SET search_path=pg_catalog AS $wa$
DECLARE s app.track_subscriptions; old_s app.track_subscriptions; p app.track_plans;
 sel app.track_base_selection; e platform.runtime_effect_receipt;
BEGIN
 IF session_user::text<>'wa_worker' THEN RETURN NULL; END IF;
 IF TG_TABLE_NAME='track_base_selection' THEN
  SELECT * INTO STRICT s FROM app.track_subscriptions WHERE id=NEW.subscription_id;
  SELECT * INTO STRICT p FROM app.track_plans WHERE id=s.plan_id;
  IF s.mutation_transaction_id<>NEW.mutation_transaction_id OR p.status<>'active' OR p.billing_model<>'free'
   OR s.provider<>'none' OR s.status<>'active' OR s.customer_profile_id<>NEW.customer_profile_id
  THEN RAISE EXCEPTION 'not same new approved Free enrollment'; END IF;
  IF TG_OP='UPDATE' THEN
   SELECT * INTO STRICT old_s FROM app.track_subscriptions WHERE id=OLD.subscription_id;
   IF old_s.status IN ('active','trialing') AND old_s.ended_at IS NULL
    AND (old_s.current_period_end IS NULL OR old_s.current_period_end>clock_timestamp())
   THEN RAISE EXCEPTION 'preserve valid existing Free or paid selection'; END IF;
  END IF;
  IF NOT EXISTS(SELECT 1 FROM app.track_enrollment_receipt r WHERE r.selection_id=NEW.id
   AND r.selection_revision=NEW.revision AND r.mutation_transaction_id=NEW.mutation_transaction_id)
  THEN RAISE EXCEPTION 'missing atomic enrollment receipt'; END IF;
 ELSIF TG_TABLE_NAME='track_subscriptions' THEN
  IF NOT EXISTS(SELECT 1 FROM app.track_base_selection b WHERE b.subscription_id=NEW.id
    AND b.mutation_transaction_id=NEW.mutation_transaction_id)
   OR NOT EXISTS(SELECT 1 FROM app.track_subscription_events h WHERE h.subscription_id=NEW.id
    AND h.mutation_transaction_id=NEW.mutation_transaction_id AND h.user_id=NEW.user_id
    AND h.plan_id=NEW.plan_id AND h.to_status=NEW.status AND h.from_status IS NULL)
  THEN RAISE EXCEPTION 'orphan Free enrollment/history'; END IF;
 ELSIF TG_TABLE_NAME='track_entitlement_grants' THEN
  SELECT * INTO STRICT s FROM app.track_subscriptions WHERE id=NEW.subscription_id;
  IF s.mutation_transaction_id<>NEW.mutation_transaction_id OR NEW.source_plan_id IS DISTINCT FROM s.plan_id
   OR NOT EXISTS(SELECT 1 FROM app.track_plan_entitlements b JOIN app.track_entitlement_definitions d ON d.id=b.entitlement_id
    WHERE b.plan_id=s.plan_id AND b.entitlement_id=NEW.entitlement_id AND d.is_active
     AND (d.track IS NULL OR d.track='customer') AND d.value_type=NEW.value_type AND b.value_type=NEW.value_type
     AND b.boolean_value IS NOT DISTINCT FROM NEW.boolean_value AND b.int_value IS NOT DISTINCT FROM NEW.int_value
     AND b.decimal_value IS NOT DISTINCT FROM NEW.decimal_value AND b.string_value IS NOT DISTINCT FROM NEW.string_value)
  THEN RAISE EXCEPTION 'not exact approved Free benefits'; END IF;
 ELSIF TG_TABLE_NAME='track_subscription_events' THEN
  SELECT * INTO STRICT s FROM app.track_subscriptions WHERE id=NEW.subscription_id;
  IF s.mutation_transaction_id<>NEW.mutation_transaction_id OR s.user_id<>NEW.user_id OR s.plan_id IS DISTINCT FROM NEW.plan_id
   OR NEW.from_status IS NOT NULL OR NEW.to_status IS DISTINCT FROM s.status OR NEW.provider IS DISTINCT FROM 'none'::app.track_billing_provider
  THEN RAISE EXCEPTION 'replay must not append new enrollment history'; END IF;
 ELSIF TG_TABLE_NAME='track_enrollment_receipt' THEN
  SELECT * INTO STRICT sel FROM app.track_base_selection WHERE id=NEW.selection_id;
  SELECT * INTO STRICT e FROM platform.runtime_effect_receipt WHERE id=NEW.effect_receipt_id;
  IF NEW.track<>'customer' OR NEW.source_owner<>'customer_buyer_profile'
   OR sel.user_id<>NEW.user_id OR sel.track<>NEW.track OR sel.customer_profile_id<>NEW.profile_id
   OR sel.revision<>NEW.selection_revision OR e.state<>'committed'
   OR e.mutation_transaction_id<>NEW.mutation_transaction_id
   OR NOT EXISTS(SELECT 1 FROM platform.runtime_inbox_receipt i WHERE i.effect_receipt_id=e.id
    AND i.handler_name='assignDefaultFreeTrack.v1' AND i.mutation_transaction_id=e.mutation_transaction_id)
  THEN RAISE EXCEPTION 'incoherent atomic enrollment/inbox/effect'; END IF;
 END IF;
 RETURN NULL;
END $wa$;
CREATE CONSTRAINT TRIGGER enrollment_commit AFTER INSERT OR UPDATE ON app.track_base_selection DEFERRABLE INITIALLY DEFERRED FOR EACH ROW EXECUTE FUNCTION platform_private.track_enrollment_commit();
CREATE CONSTRAINT TRIGGER enrollment_commit AFTER INSERT ON app.track_subscriptions DEFERRABLE INITIALLY DEFERRED FOR EACH ROW EXECUTE FUNCTION platform_private.track_enrollment_commit();
CREATE CONSTRAINT TRIGGER enrollment_commit AFTER INSERT ON app.track_entitlement_grants DEFERRABLE INITIALLY DEFERRED FOR EACH ROW EXECUTE FUNCTION platform_private.track_enrollment_commit();
CREATE CONSTRAINT TRIGGER enrollment_commit AFTER INSERT ON app.track_subscription_events DEFERRABLE INITIALLY DEFERRED FOR EACH ROW EXECUTE FUNCTION platform_private.track_enrollment_commit();
CREATE CONSTRAINT TRIGGER enrollment_commit AFTER INSERT ON app.track_enrollment_receipt DEFERRABLE INITIALLY DEFERRED FOR EACH ROW EXECUTE FUNCTION platform_private.track_enrollment_commit();

-- SQL-12: typed Track bindings and value arms. No product Track path is activated.
CREATE FUNCTION platform_private.track_binding() RETURNS trigger
LANGUAGE plpgsql SECURITY INVOKER SET search_path=pg_catalog AS $wa$
DECLARE v jsonb:=to_jsonb(NEW); u uuid; plan app.track_plans; sub app.track_subscriptions;
BEGIN
 IF v ? 'customer_profile_id' THEN
  IF num_nonnulls(v->>'customer_profile_id',v->>'candidate_profile_id',v->>'professional_profile_id')<>1
   OR ((v->>'track'='customer') IS DISTINCT FROM (v->>'customer_profile_id' IS NOT NULL))
   OR ((v->>'track'='candidate') IS DISTINCT FROM (v->>'candidate_profile_id' IS NOT NULL))
   OR ((v->>'track'='professional') IS DISTINCT FROM (v->>'professional_profile_id' IS NOT NULL))
  THEN RAISE EXCEPTION 'exact typed Track profile required'; END IF;
  IF v->>'track'='customer' THEN
   SELECT user_id INTO STRICT u FROM app.customer_profiles WHERE id=(v->>'customer_profile_id')::uuid;
  ELSIF v->>'track'='candidate' THEN
   SELECT user_id INTO STRICT u FROM app.candidate_profiles WHERE id=(v->>'candidate_profile_id')::uuid;
  ELSE SELECT user_id INTO STRICT u FROM app.professional_profiles WHERE id=(v->>'professional_profile_id')::uuid;
  END IF;
  IF u::text IS DISTINCT FROM v->>'user_id' THEN RAISE EXCEPTION 'foreign Track owner'; END IF;
 END IF;
 IF TG_TABLE_NAME='track_subscriptions' THEN
  SELECT * INTO STRICT plan FROM app.track_plans WHERE id=NEW.plan_id;
  IF plan.track<>NEW.track THEN RAISE EXCEPTION 'foreign plan track'; END IF;
  IF plan.billing_model='free' AND (NEW.provider<>'none' OR NEW.provider_customer_id IS NOT NULL
   OR NEW.provider_subscription_id IS NOT NULL OR NEW.provider_price_id IS NOT NULL)
  THEN RAISE EXCEPTION 'Free must be provider-neutral'; END IF;
 ELSIF TG_TABLE_NAME='track_base_selection' THEN
  PERFORM pg_advisory_xact_lock(hashtextextended('track:'||NEW.user_id::text||':'||NEW.track::text,0));
  SELECT * INTO STRICT sub FROM app.track_subscriptions WHERE id=NEW.subscription_id;
  IF sub.user_id<>NEW.user_id OR sub.track<>NEW.track OR sub.customer_profile_id IS DISTINCT FROM NEW.customer_profile_id
   OR sub.candidate_profile_id IS DISTINCT FROM NEW.candidate_profile_id
   OR sub.professional_profile_id IS DISTINCT FROM NEW.professional_profile_id
  THEN RAISE EXCEPTION 'foreign base selection'; END IF;
 ELSIF TG_TABLE_NAME='track_entitlement_grants' AND NEW.subscription_id IS NOT NULL THEN
  SELECT * INTO STRICT sub FROM app.track_subscriptions WHERE id=NEW.subscription_id;
  IF sub.user_id<>NEW.user_id OR sub.track<>NEW.track OR sub.customer_profile_id IS DISTINCT FROM NEW.customer_profile_id
   OR sub.candidate_profile_id IS DISTINCT FROM NEW.candidate_profile_id
   OR sub.professional_profile_id IS DISTINCT FROM NEW.professional_profile_id
  THEN RAISE EXCEPTION 'foreign entitlement grant'; END IF;
 END IF;
 RETURN NEW;
END $wa$;
CREATE TRIGGER subscription_binding BEFORE INSERT OR UPDATE ON app.track_subscriptions FOR EACH ROW EXECUTE FUNCTION platform_private.track_binding();
CREATE TRIGGER grant_binding BEFORE INSERT OR UPDATE ON app.track_entitlement_grants FOR EACH ROW EXECUTE FUNCTION platform_private.track_binding();
CREATE TRIGGER selection_binding BEFORE INSERT OR UPDATE ON app.track_base_selection FOR EACH ROW EXECUTE FUNCTION platform_private.track_binding();

ALTER TABLE app.track_plan_entitlements ADD CONSTRAINT typed_plan_value CHECK
 ((value_type='boolean' AND boolean_value IS NOT NULL AND int_value IS NULL AND decimal_value IS NULL AND string_value IS NULL)
 OR (value_type IN ('integer','percent_bps','money_cents') AND int_value IS NOT NULL AND boolean_value IS NULL AND decimal_value IS NULL AND string_value IS NULL)
 OR (value_type='decimal' AND decimal_value IS NOT NULL AND int_value IS NULL AND boolean_value IS NULL AND string_value IS NULL)
 OR (value_type='string' AND string_value IS NOT NULL AND int_value IS NULL AND decimal_value IS NULL AND boolean_value IS NULL));
ALTER TABLE app.track_entitlement_grants ADD CONSTRAINT typed_grant_value CHECK
 ((value_type='boolean' AND boolean_value IS NOT NULL AND int_value IS NULL AND decimal_value IS NULL AND string_value IS NULL)
 OR (value_type IN ('integer','percent_bps','money_cents') AND int_value IS NOT NULL AND boolean_value IS NULL AND decimal_value IS NULL AND string_value IS NULL)
 OR (value_type='decimal' AND decimal_value IS NOT NULL AND int_value IS NULL AND boolean_value IS NULL AND string_value IS NULL)
 OR (value_type='string' AND string_value IS NOT NULL AND int_value IS NULL AND decimal_value IS NULL AND boolean_value IS NULL));
ALTER TABLE app.track_plan_entitlements ADD CONSTRAINT plan_value_bounds CHECK
 ((value_type<>'percent_bps' OR int_value BETWEEN 0 AND 10000) AND (value_type<>'money_cents' OR int_value>=0)
 AND (decimal_value IS NULL OR decimal_value NOT IN ('NaN'::float8,'Infinity'::float8,'-Infinity'::float8)));
ALTER TABLE app.track_entitlement_grants ADD CONSTRAINT grant_value_bounds CHECK
 ((value_type<>'percent_bps' OR int_value BETWEEN 0 AND 10000) AND (value_type<>'money_cents' OR int_value>=0)
 AND (decimal_value IS NULL OR decimal_value NOT IN ('NaN'::float8,'Infinity'::float8,'-Infinity'::float8)));
ALTER TABLE app.track_usage_events ADD CONSTRAINT usage_window CHECK (quantity>0 AND accepted_at>=period_start AND accepted_at<period_end);
ALTER TABLE app.track_usage_reservation ADD CONSTRAINT usage_reservation_window CHECK (quantity>0 AND
 (accepted_at IS NULL OR (accepted_at>=period_start AND accepted_at<period_end)));
ALTER TABLE app.track_usage_counters ADD CONSTRAINT counter_bounds CHECK (used_quantity>=0 AND (limit_quantity IS NULL OR limit_quantity>=0));
-- Quota period calculation and event-derived counter reconciliation are owner-code
-- dependencies. In this draft direct usage mutation is blocked until qualified.
CREATE FUNCTION platform_private.block_usage_mutation() RETURNS trigger
LANGUAGE plpgsql SECURITY INVOKER SET search_path=pg_catalog AS $wa$
BEGIN RAISE EXCEPTION 'usage mutation requires separately qualified period/reconciliation owner adapter' USING ERRCODE='0A000'; END $wa$;
CREATE TRIGGER usage_adapter_gate BEFORE INSERT OR UPDATE ON app.track_usage_events FOR EACH ROW EXECUTE FUNCTION platform_private.block_usage_mutation();
CREATE TRIGGER usage_adapter_gate BEFORE INSERT OR UPDATE ON app.track_usage_counters FOR EACH ROW EXECUTE FUNCTION platform_private.block_usage_mutation();
CREATE TRIGGER usage_adapter_gate BEFORE INSERT OR UPDATE ON app.track_usage_reservation FOR EACH ROW EXECUTE FUNCTION platform_private.block_usage_mutation();

-- SQL-14: versioned owner instructions, receipts and restoration markers.
ALTER TABLE app.privacy_owner_receipt ADD CONSTRAINT retained_basis CHECK
 (disposition<>'retained' OR NULLIF(legal_basis_ref,'') IS NOT NULL);
CREATE FUNCTION platform_private.privacy_guard() RETURNS trigger
LANGUAGE plpgsql SECURITY INVOKER SET search_path=pg_catalog AS $wa$
DECLARE i app.privacy_target_instruction; r app.privacy_requests; p app.privacy_owner_receipt;
BEGIN
 IF TG_TABLE_NAME='privacy_target_instruction' THEN
  SELECT * INTO STRICT r FROM app.privacy_requests WHERE id=NEW.privacy_request_id;
  IF r.verified_at IS NULL OR r.status NOT IN ('verified','processing')
   OR r.instruction_generation<>NEW.generation OR NEW.field_map_version='' OR NEW.executor_version=''
  THEN RAISE EXCEPTION 'unverified or stale privacy instruction'; END IF;
 ELSIF TG_TABLE_NAME='privacy_owner_receipt' THEN
  SELECT * INTO STRICT i FROM app.privacy_target_instruction WHERE id=NEW.instruction_id;
  SELECT * INTO STRICT r FROM app.privacy_requests WHERE id=i.privacy_request_id;
  IF i.generation<>NEW.generation OR r.instruction_generation<>NEW.generation OR r.verified_at IS NULL
  THEN RAISE EXCEPTION 'stale privacy disposition'; END IF;
  IF NEW.disposition='completed' THEN
   RAISE EXCEPTION 'completed execution needs qualified owner field-map and exact-byte/provider evidence' USING ERRCODE='0A000';
  END IF;
 ELSIF TG_TABLE_NAME='privacy_restore_marker' THEN
  SELECT * INTO STRICT p FROM app.privacy_owner_receipt WHERE id=NEW.source_receipt_id;
  SELECT * INTO STRICT i FROM app.privacy_target_instruction WHERE id=p.instruction_id;
  IF NEW.generation<>i.generation OR NEW.owner_module_id<>i.owner_module_id
   OR NEW.target_kind<>i.target_kind OR NEW.source_id<>i.source_id OR NEW.action<>i.action
   OR p.disposition NOT IN ('completed','retained') THEN RAISE EXCEPTION 'incoherent restore marker'; END IF;
 ELSIF TG_TABLE_NAME='privacy_requests' THEN
  IF TG_OP='UPDATE' AND NEW.requested_at IS DISTINCT FROM OLD.requested_at THEN RAISE EXCEPTION 'request origin immutable'; END IF;
  IF NEW.status IN ('completed','partially_completed') OR NEW.completed_at IS NOT NULL THEN
   RAISE EXCEPTION 'request completion requires qualified full owner accounting' USING ERRCODE='0A000';
  END IF;
 END IF;
 RETURN NEW;
END $wa$;
CREATE TRIGGER privacy_instruction BEFORE INSERT ON app.privacy_target_instruction FOR EACH ROW EXECUTE FUNCTION platform_private.privacy_guard();
CREATE TRIGGER privacy_receipt BEFORE INSERT ON app.privacy_owner_receipt FOR EACH ROW EXECUTE FUNCTION platform_private.privacy_guard();
CREATE TRIGGER privacy_restore BEFORE INSERT OR UPDATE ON app.privacy_restore_marker FOR EACH ROW EXECUTE FUNCTION platform_private.privacy_guard();
CREATE TRIGGER privacy_request BEFORE INSERT OR UPDATE ON app.privacy_requests FOR EACH ROW EXECUTE FUNCTION platform_private.privacy_guard();

-- SQL-08/09 nonrecursive infrastructure roots: FK/semantic/txn guards, not evidence-of-evidence.
CREATE FUNCTION platform_private.infrastructure_atomic() RETURNS trigger
LANGUAGE plpgsql SECURITY INVOKER SET search_path=pg_catalog AS $wa$
DECLARE c platform.runtime_command_receipt; o platform.runtime_outbox_message; e platform.runtime_effect_receipt; w platform.runtime_work_item;
BEGIN
 IF TG_TABLE_NAME IN ('owner_mutation_evidence','runtime_outbox_message') THEN
  SELECT * INTO STRICT c FROM platform.runtime_command_receipt WHERE id=NEW.command_receipt_id;
  IF c.state<>'committed' OR c.mutation_transaction_id<>NEW.mutation_transaction_id THEN RAISE EXCEPTION 'foreign transaction command'; END IF;
  IF TG_TABLE_NAME='owner_mutation_evidence' AND (c.owner_module_id<>NEW.owner_module_id OR c.operation<>NEW.action)
   THEN RAISE EXCEPTION 'foreign owner command'; END IF;
 ELSIF TG_TABLE_NAME='runtime_inbox_receipt' THEN
  SELECT * INTO STRICT o FROM platform.runtime_outbox_message WHERE id=NEW.outbox_message_id;
  SELECT * INTO STRICT e FROM platform.runtime_effect_receipt WHERE id=NEW.effect_receipt_id;
  SELECT * INTO STRICT w FROM platform.runtime_work_item WHERE outbox_message_id=o.id AND handler_name=NEW.handler_name;
  IF o.payload_hash<>NEW.payload_hash OR e.owner_module_id<>NEW.consumer_owner OR e.state<>'committed'
   OR e.mutation_transaction_id<>NEW.mutation_transaction_id OR e.fence<>w.fence
   OR w.state<>'leased' OR w.lease_expires_at<=clock_timestamp()
   OR current_setting('wa.lease_hash',true) IS DISTINCT FROM w.lease_token_hash::text
   OR current_setting('wa.fence',true) IS DISTINCT FROM w.fence::text
  THEN RAISE EXCEPTION 'stale or incoherent inbox effect'; END IF;
 END IF;
 RETURN NULL;
END $wa$;
CREATE CONSTRAINT TRIGGER infrastructure_commit AFTER INSERT ON platform.owner_mutation_evidence DEFERRABLE INITIALLY DEFERRED FOR EACH ROW EXECUTE FUNCTION platform_private.infrastructure_atomic();
CREATE CONSTRAINT TRIGGER infrastructure_commit AFTER INSERT ON platform.runtime_outbox_message DEFERRABLE INITIALLY DEFERRED FOR EACH ROW EXECUTE FUNCTION platform_private.infrastructure_atomic();
CREATE CONSTRAINT TRIGGER infrastructure_commit AFTER INSERT ON platform.runtime_inbox_receipt DEFERRABLE INITIALLY DEFERRED FOR EACH ROW EXECUTE FUNCTION platform_private.infrastructure_atomic();
