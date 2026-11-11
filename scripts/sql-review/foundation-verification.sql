-- DRAFT-02: fixed Boolean ports. Read maxima are emitted from the separate
-- foundation-sql-verifier-access.json register, never granted to the worker.
CREATE FUNCTION platform_private.lease_secret_matches(expected_hash text) RETURNS boolean
LANGUAGE sql VOLATILE SECURITY INVOKER SET search_path=pg_catalog AS $wa$
 SELECT CASE WHEN current_setting('wa.lease_secret',true) ~ '^[0-9a-f]{64}$'
  THEN encode(sha256(decode(current_setting('wa.lease_secret',true),'hex')),'hex')=expected_hash
  ELSE false END;
$wa$;

CREATE FUNCTION platform_private.customer_current_for_track(customer_id uuid, user_id uuid, creation_revision bigint, privacy_generation bigint, creation_receipt uuid) RETURNS boolean
LANGUAGE plpgsql VOLATILE SECURITY DEFINER SET search_path=pg_catalog AS $wa$
DECLARE g platform.database_action_grant; c record;
BEGIN
 g:=platform_private.bound_grant(true);
 IF g.id IS NULL OR session_user::text<>'wa_worker' OR g.service_principal IS NULL
  OR NOT platform_private.context_allows('track_subscription_entitlement','assignDefaultFreeTrack.v1','RuntimeWorkItem',g.target_id,'default_free_enrollment')
 THEN RETURN false; END IF;
 PERFORM pg_advisory_xact_lock_shared(hashtextextended('source:CustomerProfile:'||customer_id::text,0));
 SELECT p.id,p.user_id,p.status,p.archived_at,p.revision,p.privacy_generation INTO c FROM app.customer_profiles p WHERE p.id=customer_id;
 RETURN COALESCE(c.id IS NOT NULL AND c.user_id=user_id AND c.status='active' AND c.archived_at IS NULL
  AND c.privacy_generation=privacy_generation AND creation_revision=0
  AND 'CustomerProfile/'||customer_id::text||'/revision/'||c.revision::text=ANY(g.allowed_fields)
  AND EXISTS(SELECT 1 FROM app.customer_profile_lifecycle_event h WHERE h.customer_profile_id=customer_id
   AND h.source_revision=creation_revision AND h.command_receipt_id=creation_receipt
   AND h.actor_user_id=user_id AND h.from_status IS NULL AND h.to_status='active'),false);
END $wa$;

CREATE FUNCTION platform_private.worker_lease_valid(work_id uuid, effect_id uuid DEFAULT NULL, allow_completed boolean DEFAULT false) RETURNS boolean
LANGUAGE plpgsql VOLATILE SECURITY DEFINER SET search_path=pg_catalog AS $wa$
DECLARE g platform.database_action_grant; w record;
BEGIN
 g:=platform_private.bound_grant(true);
 IF g.id IS NULL OR session_user::text<>'wa_worker' OR g.service_principal IS NULL
  OR NOT platform_private.context_allows('track_subscription_entitlement','assignDefaultFreeTrack.v1','RuntimeWorkItem',work_id::text,'default_free_enrollment')
 THEN RETURN false; END IF;
 SELECT j.id,j.handler_name,j.state,j.fence,j.lease_token_hash,j.lease_expires_at,j.effect_receipt_id,j.mutation_transaction_id INTO w
  FROM platform.runtime_work_item j WHERE j.id=work_id;
 RETURN COALESCE(w.id IS NOT NULL AND w.handler_name='assignDefaultFreeTrack.v1'
  AND (w.state='leased' OR (allow_completed AND w.state='completed' AND w.mutation_transaction_id=pg_current_xact_id()::text))
  AND w.fence=g.source_generation AND w.fence::text=current_setting('wa.fence',true)
  AND w.lease_expires_at>clock_timestamp() AND platform_private.lease_secret_matches(w.lease_token_hash::text)
  AND (effect_id IS NULL OR w.effect_receipt_id=effect_id),false);
END $wa$;

CREATE FUNCTION platform_private.worker_effect_matches(work_id uuid, effect_id uuid, require_link boolean DEFAULT true) RETURNS boolean
LANGUAGE plpgsql VOLATILE SECURITY DEFINER SET search_path=pg_catalog AS $wa$
DECLARE g platform.database_action_grant; w record; e record; c record; o record;
BEGIN
 g:=platform_private.bound_grant(true);
 IF g.id IS NULL OR NOT platform_private.worker_lease_valid(work_id,NULL,true) THEN RETURN false; END IF;
 SELECT j.id,j.outbox_message_id,j.effect_receipt_id,j.handler_name,j.semantic_work_key,j.fence INTO w FROM platform.runtime_work_item j WHERE j.id=work_id;
 SELECT m.id,m.aggregate_id,m.payload_hash,m.payload,m.source_revision,m.source_generation,m.command_receipt_id,m.producer_owner FROM platform.runtime_outbox_message m WHERE m.id=w.outbox_message_id INTO o;
 -- Fixed Outbox branch validates the canonical creation command and returns
 -- before the Effect branch; this does not recurse through effect matching.
 IF NOT platform_private.worker_track_allowed('RuntimeOutboxMessage',jsonb_build_object('id',o.id,'producer_owner',o.producer_owner),'SELECT') THEN RETURN false; END IF;
 IF NOT platform_private.customer_current_for_track(o.aggregate_id::uuid,(o.payload->>'userId')::uuid,o.source_revision,o.source_generation,o.command_receipt_id) THEN RETURN false; END IF;
 SELECT r.id,r.command_receipt_id,r.owner_module_id,r.operation,r.subject_scope,r.semantic_effect_key,r.fingerprint,r.fence,r.state,r.mutation_transaction_id INTO e
  FROM platform.runtime_effect_receipt r WHERE r.id=effect_id;
 SELECT r.id,r.owner_module_id,r.operation,r.subject_scope,r.semantic_key,r.fingerprint,r.state,r.mutation_transaction_id INTO c
  FROM platform.runtime_command_receipt r WHERE r.id=e.command_receipt_id;
 IF NOT platform_private.worker_row_capabilities('RuntimeEffectReceipt',to_jsonb(e),'SELECT')
  OR NOT platform_private.worker_row_capabilities('RuntimeCommandReceipt',to_jsonb(c),'SELECT') THEN RETURN false; END IF;
 RETURN COALESCE((NOT require_link OR w.effect_receipt_id=e.id) AND e.id IS NOT NULL
  AND 'RuntimeWorkItem/'||w.id::text||'/effect/'||e.id::text=ANY(g.allowed_fields)
  AND 'RuntimeWorkItem/'||w.id::text||'/command/'||c.id::text=ANY(g.allowed_fields)
  AND e.owner_module_id='track_subscription_entitlement' AND c.owner_module_id=e.owner_module_id
  AND e.operation=w.handler_name AND c.operation=e.operation AND e.state='committed' AND c.state='committed'
  AND e.subject_scope='CustomerProfile:'||o.aggregate_id AND c.subject_scope=e.subject_scope
  AND e.semantic_effect_key=w.semantic_work_key AND c.semantic_key=e.semantic_effect_key
  AND e.fingerprint=o.payload_hash AND c.fingerprint=e.fingerprint AND e.fence<=w.fence
  AND e.mutation_transaction_id=c.mutation_transaction_id
  AND EXISTS(SELECT 1 FROM platform.runtime_inbox_receipt i WHERE i.outbox_message_id=o.id
   AND i.effect_receipt_id=e.id AND i.consumer_owner=e.owner_module_id AND i.handler_name=e.operation
   AND i.payload_hash=o.payload_hash AND i.mutation_transaction_id=e.mutation_transaction_id),false);
END $wa$;

CREATE FUNCTION platform_private.worker_track_allowed(model_name text, row_value jsonb, verb text) RETURNS boolean
LANGUAGE plpgsql VOLATILE SECURITY DEFINER SET search_path=pg_catalog AS $wa$
DECLARE g platform.database_action_grant; w record; o record; p record; s record;
 u uuid; customer uuid; expected_effect text; scope text; row_id uuid; expected_command text;
BEGIN
 g:=platform_private.bound_grant(true);
 IF g.id IS NULL OR session_user::text<>'wa_worker' OR g.service_principal IS NULL OR verb NOT IN ('SELECT','INSERT','UPDATE') THEN RETURN false; END IF;
 IF NOT platform_private.worker_row_capabilities(model_name,row_value,verb) THEN RETURN false; END IF;
 -- Claims inspect/update only their exact queued job. They cannot create effects.
 IF model_name='RuntimeWorkItem' AND g.action IN ('runtime.claim_work.v1','runtime.renew_work.v1') THEN
  RETURN platform_private.context_allows('platform_integration_owner',g.action,'RuntimeWorkItem',row_value->>'id',
   CASE WHEN g.action='runtime.claim_work.v1' THEN 'work.claim' ELSE 'work.renew' END);
 END IF;
 IF NOT platform_private.worker_lease_valid(g.target_id::uuid,NULL,true) THEN RETURN false; END IF;
 SELECT j.id,j.outbox_message_id,j.semantic_work_key,j.effect_receipt_id,j.fence INTO w FROM platform.runtime_work_item j WHERE j.id=g.target_id::uuid;
 SELECT m.id,m.command_receipt_id,m.kind,m.name,m.producer_owner,m.aggregate_kind,m.aggregate_id,m.source_revision,m.source_generation,m.payload,m.payload_hash INTO o
  FROM platform.runtime_outbox_message m WHERE m.id=w.outbox_message_id;
 IF o.id IS NULL OR o.kind<>'command' OR o.name<>'assignDefaultFreeTrack.v1'
  OR o.producer_owner<>'customer_buyer_profile' OR o.aggregate_kind<>'CustomerProfile'
  OR o.source_revision<>0 OR o.payload->>'sourceCreationReceipt'<>o.command_receipt_id::text
 THEN RETURN false; END IF;
 u:=(o.payload->>'userId')::uuid;customer:=o.aggregate_id::uuid;
 IF NOT platform_private.customer_current_for_track(customer,u,o.source_revision,o.source_generation,o.command_receipt_id) THEN RETURN false; END IF;
 scope:='CustomerProfile:'||customer::text;
 expected_effect:='customer_buyer_profile/'||customer::text||'/default-free-enrollment/v1';
 IF w.semantic_work_key<>expected_effect THEN RETURN false; END IF;
 IF model_name='RuntimeWorkItem' THEN
  RETURN COALESCE(row_value->>'id'=w.id::text AND verb IN ('SELECT','UPDATE'),false);
 ELSIF model_name='RuntimeOutboxMessage' THEN RETURN verb='SELECT' AND row_value->>'id'=o.id::text;
 ELSIF model_name='RuntimeAttempt' THEN
  RETURN COALESCE(row_value->>'work_item_id'=w.id::text AND (row_value->>'fence')::bigint=w.fence
   AND row_value->>'worker_id'=g.service_principal AND verb IN ('SELECT','INSERT'),false);
 ELSIF model_name='RuntimeCommandReceipt' THEN
  RETURN COALESCE(('RuntimeWorkItem/'||w.id::text||'/command/'||(row_value->>'id'))=ANY(g.allowed_fields)
   AND row_value->>'owner_module_id'='track_subscription_entitlement' AND row_value->>'operation'='assignDefaultFreeTrack.v1'
   AND row_value->>'subject_scope'=scope AND row_value->>'semantic_key'=expected_effect AND row_value->>'fingerprint'=o.payload_hash::text,false);
 ELSIF model_name='RuntimeEffectReceipt' THEN
  RETURN COALESCE(('RuntimeWorkItem/'||w.id::text||'/effect/'||(row_value->>'id'))=ANY(g.allowed_fields)
   AND ('RuntimeWorkItem/'||w.id::text||'/command/'||(row_value->>'command_receipt_id'))=ANY(g.allowed_fields)
   AND row_value->>'owner_module_id'='track_subscription_entitlement' AND row_value->>'operation'='assignDefaultFreeTrack.v1'
   AND row_value->>'subject_scope'=scope AND row_value->>'semantic_effect_key'=expected_effect
   AND row_value->>'fingerprint'=o.payload_hash::text
   AND ((row_value->>'fence')::bigint=w.fence OR
    (verb='SELECT' AND platform_private.worker_effect_matches(w.id,(row_value->>'id')::uuid,true))),false);
 ELSIF model_name='RuntimeInboxReceipt' THEN
  RETURN COALESCE(row_value->>'outbox_message_id'=o.id::text AND row_value->>'consumer_owner'='track_subscription_entitlement'
   AND row_value->>'handler_name'='assignDefaultFreeTrack.v1' AND row_value->>'payload_hash'=o.payload_hash::text
   AND ('RuntimeWorkItem/'||w.id::text||'/effect/'||(row_value->>'effect_receipt_id'))=ANY(g.allowed_fields),false);
 ELSIF model_name='OwnerMutationEvidence' THEN
  RETURN COALESCE(row_value->>'owner_module_id'='track_subscription_entitlement'
   AND row_value->>'aggregate_kind' IN ('TrackSubscription','TrackEntitlementGrant','TrackBaseSelection','TrackSubscriptionEvent','TrackEnrollmentReceipt')
   AND row_value->'evidence_body'->'committed'->>'userId'=u::text,false);
 END IF;
 IF NOT model_name LIKE 'Track%' THEN RETURN false; END IF;
 -- Only a current, explicitly approved catalog revision may create Free access.
 IF model_name='TrackPlan' THEN row_id:=(row_value->>'id')::uuid;
 ELSE
  SELECT b.plan_id INTO row_id FROM app.track_base_selection a JOIN app.track_subscriptions b ON b.id=a.subscription_id
   WHERE a.user_id=u AND a.track='customer' AND a.customer_profile_id=customer;
  IF verb='INSERT' AND model_name='TrackSubscription' THEN row_id:=(row_value->>'plan_id')::uuid;
  ELSIF model_name='TrackPlanEntitlement' THEN row_id:=(row_value->>'plan_id')::uuid;
  ELSIF model_name='TrackEntitlementGrant' AND verb='INSERT' THEN row_id:=(row_value->>'source_plan_id')::uuid;
  END IF;
 END IF;
 IF row_id IS NOT NULL THEN
  PERFORM pg_advisory_xact_lock_shared(hashtextextended('source:TrackPlan:'||row_id::text,0));
  SELECT x.id,x.track,x.status,x.billing_model,x.version,x.content_hash,x.revision INTO p FROM app.track_plans x WHERE x.id=row_id;
 END IF;
 IF model_name IN ('TrackPlan','TrackPlanEntitlement','TrackEntitlementDefinition') THEN
  IF verb<>'SELECT' THEN RETURN false; END IF;
  IF model_name='TrackEntitlementDefinition' THEN
   RETURN EXISTS(SELECT 1 FROM app.track_plan_entitlements b JOIN app.track_plans q ON q.id=b.plan_id
    WHERE b.entitlement_id=(row_value->>'id')::uuid AND q.track='customer'
     AND 'TrackPlan/'||q.id::text||'/revision/'||q.revision::text=ANY(g.allowed_fields)
     AND 'TrackPlan/'||q.id::text||'/version/'||q.version=ANY(g.allowed_fields)
     AND 'TrackPlan/'||q.id::text||'/contentHash/'||q.content_hash::text=ANY(g.allowed_fields)
     AND q.status='active' AND q.billing_model='free');
  END IF;
  RETURN COALESCE(p.id IS NOT NULL AND p.track='customer'
   AND 'TrackPlan/'||p.id::text||'/revision/'||p.revision::text=ANY(g.allowed_fields)
   AND 'TrackPlan/'||p.id::text||'/version/'||p.version=ANY(g.allowed_fields)
   AND 'TrackPlan/'||p.id::text||'/contentHash/'||p.content_hash::text=ANY(g.allowed_fields),false);
 END IF;
 IF model_name='TrackEnrollmentReceipt' THEN
  RETURN COALESCE(row_value->>'user_id'=u::text AND row_value->>'profile_id'=customer::text
   AND row_value->>'source_owner'='customer_buyer_profile' AND row_value->>'track'='customer'
   AND row_value->>'source_creation_revision'=o.source_revision::text AND row_value->>'semantic_key'=expected_effect
   AND ('RuntimeWorkItem/'||w.id::text||'/effect/'||(row_value->>'effect_receipt_id'))=ANY(g.allowed_fields),false);
 END IF;
 IF row_value->>'user_id' IS DISTINCT FROM u::text THEN RETURN false; END IF;
 IF model_name='TrackSubscriptionEvent' THEN
  RETURN verb='INSERT' AND row_value->>'from_status' IS NULL AND row_value->>'provider'='none';
 END IF;
 IF row_value->>'track' IS DISTINCT FROM 'customer' OR row_value->>'customer_profile_id' IS DISTINCT FROM customer::text
  OR row_value->>'candidate_profile_id' IS NOT NULL OR row_value->>'professional_profile_id' IS NOT NULL THEN RETURN false; END IF;
 IF model_name='TrackSubscription' THEN
  IF verb='SELECT' THEN RETURN EXISTS(SELECT 1 FROM app.track_base_selection b WHERE b.user_id=u AND b.track='customer' AND b.subscription_id=(row_value->>'id')::uuid)
    OR EXISTS(SELECT 1 FROM app.track_subscriptions a WHERE a.id=(row_value->>'id')::uuid AND a.mutation_transaction_id=pg_current_xact_id()::text); END IF;
  IF verb<>'INSERT' OR p.id IS NULL OR p.status<>'active' OR p.billing_model<>'free' OR p.track<>'customer'
   OR row_value->>'provider'<>'none' OR row_value->>'status'<>'active'
   OR NOT ('TrackPlan/'||p.id::text||'/revision/'||p.revision::text=ANY(g.allowed_fields))
   OR NOT ('TrackPlan/'||p.id::text||'/version/'||p.version=ANY(g.allowed_fields))
   OR NOT ('TrackPlan/'||p.id::text||'/contentHash/'||p.content_hash::text=ANY(g.allowed_fields)) THEN RETURN false; END IF;
  PERFORM pg_advisory_xact_lock(hashtextextended('track:'||u::text||':customer',0));
  RETURN NOT EXISTS(SELECT 1 FROM app.track_base_selection b JOIN app.track_subscriptions a ON a.id=b.subscription_id
   WHERE b.user_id=u AND b.track='customer' AND a.status IN ('active','trialing') AND a.ended_at IS NULL
    AND (a.current_period_end IS NULL OR a.current_period_end>clock_timestamp()));
 END IF;
 RETURN model_name IN ('TrackBaseSelection','TrackEntitlementGrant') AND verb IN ('SELECT','INSERT','UPDATE');
END $wa$;

CREATE FUNCTION platform_private.track_atomic_valid(table_name text, n jsonb, prior_value jsonb) RETURNS boolean
LANGUAGE plpgsql VOLATILE SECURITY DEFINER SET search_path=pg_catalog AS $wa$
DECLARE g platform.database_action_grant; s record; old_s record; p record; sel record; e record; o record; w record; model_name text;
BEGIN
 g:=platform_private.bound_grant(true);
 IF g.id IS NULL OR NOT platform_private.worker_lease_valid(g.target_id::uuid,NULL,true) THEN RETURN false; END IF;
 model_name:=CASE table_name WHEN 'track_base_selection' THEN 'TrackBaseSelection' WHEN 'track_subscriptions' THEN 'TrackSubscription'
  WHEN 'track_entitlement_grants' THEN 'TrackEntitlementGrant' WHEN 'track_subscription_events' THEN 'TrackSubscriptionEvent'
  WHEN 'track_enrollment_receipt' THEN 'TrackEnrollmentReceipt' ELSE NULL END;
 IF model_name IS NULL OR NOT platform_private.worker_source_claim_valid(model_name,n) THEN RETURN false; END IF;
 SELECT j.id,j.outbox_message_id,j.effect_receipt_id,j.fence INTO w FROM platform.runtime_work_item j WHERE j.id=g.target_id::uuid;
 SELECT m.id,m.command_receipt_id,m.aggregate_id,m.source_revision,m.source_generation,m.payload_hash,m.payload INTO o FROM platform.runtime_outbox_message m WHERE m.id=w.outbox_message_id;
 IF NOT platform_private.customer_current_for_track(o.aggregate_id::uuid,(o.payload->>'userId')::uuid,o.source_revision,o.source_generation,o.command_receipt_id) THEN RETURN false; END IF;
 IF table_name='track_base_selection' THEN
  IF (n->>'revision')::bigint=0 AND prior_value IS NOT NULL THEN RETURN false; END IF;
  IF (n->>'revision')::bigint>0 AND (prior_value IS NULL OR NOT EXISTS(
   SELECT 1 FROM platform.owner_mutation_evidence v WHERE v.owner_module_id='track_subscription_entitlement' AND v.aggregate_kind='TrackBaseSelection' AND v.aggregate_id=n->>'id'
    AND v.committed_revision=(n->>'revision')::bigint AND v.previous_revision=v.committed_revision-1
    AND v.mutation_transaction_id=pg_current_xact_id()::text
    AND v.evidence_body->'prior'->>'id'=prior_value->>'id'
    AND v.evidence_body->'prior'->>'revision'=prior_value->>'revision'
    AND v.evidence_body->'prior'->>'subscriptionId'=prior_value->>'subscription_id'
    AND v.evidence_body->'prior'->>'userId'=prior_value->>'user_id'
    AND v.evidence_body->'prior'->>'customerProfileId'=prior_value->>'customer_profile_id')) THEN RETURN false; END IF;
  SELECT a.id,a.user_id,a.plan_id,a.track,a.customer_profile_id,a.status,a.provider,a.mutation_transaction_id INTO s FROM app.track_subscriptions a WHERE a.id=(n->>'subscription_id')::uuid;
  SELECT q.id,q.track,q.status,q.billing_model,q.revision,q.version,q.content_hash INTO p FROM app.track_plans q WHERE q.id=s.plan_id;
  IF NOT platform_private.worker_source_row_valid('TrackSubscription',s.id::text)
   OR s.mutation_transaction_id IS DISTINCT FROM pg_current_xact_id()::text OR p.track<>'customer' OR p.status<>'active' OR p.billing_model<>'free'
   OR s.provider<>'none' OR s.status<>'active' OR s.customer_profile_id::text IS DISTINCT FROM n->>'customer_profile_id'
   OR NOT ('TrackPlan/'||p.id::text||'/revision/'||p.revision::text=ANY(g.allowed_fields))
   OR NOT ('TrackPlan/'||p.id::text||'/version/'||p.version=ANY(g.allowed_fields))
   OR NOT ('TrackPlan/'||p.id::text||'/contentHash/'||p.content_hash::text=ANY(g.allowed_fields)) THEN RETURN false; END IF;
  IF prior_value IS NOT NULL THEN
   SELECT a.id,a.user_id,a.customer_profile_id,a.track,a.status,a.ended_at,a.current_period_end,a.revision,a.mutation_transaction_id INTO old_s FROM app.track_subscriptions a WHERE a.id=(prior_value->>'subscription_id')::uuid;
   IF old_s.id IS NULL OR old_s.user_id::text<>o.payload->>'userId' OR old_s.customer_profile_id::text<>o.aggregate_id OR old_s.track<>'customer'
    OR NOT platform_private.worker_row_capabilities('TrackSubscription',to_jsonb(old_s),'SELECT') THEN RETURN false; END IF;
   IF old_s.status IN ('active','trialing') AND old_s.ended_at IS NULL AND (old_s.current_period_end IS NULL OR old_s.current_period_end>clock_timestamp()) THEN RETURN false; END IF;
  END IF;
  RETURN EXISTS(SELECT 1 FROM app.track_enrollment_receipt r WHERE r.selection_id=(n->>'id')::uuid AND r.selection_revision=(n->>'revision')::bigint
   AND platform_private.worker_source_row_valid('TrackEnrollmentReceipt',r.id::text)
   AND r.effect_receipt_id=w.effect_receipt_id AND r.mutation_transaction_id=n->>'mutation_transaction_id');
 ELSIF table_name='track_subscriptions' THEN
  RETURN EXISTS(SELECT 1 FROM app.track_base_selection b WHERE b.subscription_id=(n->>'id')::uuid AND b.mutation_transaction_id=n->>'mutation_transaction_id')
   AND EXISTS(SELECT 1 FROM app.track_subscription_events h WHERE h.subscription_id=(n->>'id')::uuid AND h.user_id::text=n->>'user_id'
    AND h.plan_id::text=n->>'plan_id' AND h.to_status::text=n->>'status' AND h.from_status IS NULL AND h.mutation_transaction_id=n->>'mutation_transaction_id'
    AND platform_private.worker_source_row_valid('TrackSubscriptionEvent',h.id::text))
   AND EXISTS(SELECT 1 FROM app.track_base_selection b WHERE b.subscription_id=(n->>'id')::uuid AND platform_private.worker_source_row_valid('TrackBaseSelection',b.id::text));
 ELSIF table_name='track_entitlement_grants' THEN
  SELECT a.id,a.plan_id,a.mutation_transaction_id INTO s FROM app.track_subscriptions a WHERE a.id=(n->>'subscription_id')::uuid;
  RETURN COALESCE(platform_private.worker_source_row_valid('TrackSubscription',s.id::text) AND s.mutation_transaction_id=pg_current_xact_id()::text AND s.plan_id::text=n->>'source_plan_id'
   AND EXISTS(SELECT 1 FROM app.track_plan_entitlements b JOIN app.track_entitlement_definitions d ON d.id=b.entitlement_id
    WHERE b.plan_id=s.plan_id AND b.entitlement_id=(n->>'entitlement_id')::uuid AND d.is_active AND (d.track IS NULL OR d.track='customer')
     AND d.value_type::text=n->>'value_type' AND b.value_type::text=n->>'value_type'
     AND COALESCE(to_jsonb(b.boolean_value),'null'::jsonb) IS NOT DISTINCT FROM n->'boolean_value' AND COALESCE(to_jsonb(b.int_value),'null'::jsonb) IS NOT DISTINCT FROM n->'int_value'
     AND COALESCE(to_jsonb(b.decimal_value),'null'::jsonb) IS NOT DISTINCT FROM n->'decimal_value' AND COALESCE(to_jsonb(b.string_value),'null'::jsonb) IS NOT DISTINCT FROM n->'string_value'),false);
 ELSIF table_name='track_subscription_events' THEN
  SELECT a.id,a.user_id,a.plan_id,a.status,a.mutation_transaction_id INTO s FROM app.track_subscriptions a WHERE a.id=(n->>'subscription_id')::uuid;
  RETURN COALESCE(platform_private.worker_source_row_valid('TrackSubscription',s.id::text) AND s.mutation_transaction_id=pg_current_xact_id()::text AND s.user_id::text=n->>'user_id' AND s.plan_id::text=n->>'plan_id'
   AND n->>'from_status' IS NULL AND n->>'to_status'=s.status::text AND n->>'provider'='none',false);
 ELSIF table_name='track_enrollment_receipt' THEN
  SELECT b.id,b.user_id,b.track,b.customer_profile_id,b.revision INTO sel FROM app.track_base_selection b WHERE b.id=(n->>'selection_id')::uuid;
  SELECT r.id,r.owner_module_id,r.operation,r.command_receipt_id,r.subject_scope,r.semantic_effect_key,r.fingerprint,r.fence,r.state,r.mutation_transaction_id INTO e
   FROM platform.runtime_effect_receipt r WHERE r.id=(n->>'effect_receipt_id')::uuid;
  RETURN COALESCE(n->>'track'='customer' AND n->>'source_owner'='customer_buyer_profile'
   AND platform_private.worker_source_row_valid('TrackBaseSelection',sel.id::text) AND platform_private.worker_effect_matches(w.id,e.id,true)
   AND sel.user_id::text=n->>'user_id' AND sel.customer_profile_id::text=n->>'profile_id'
   AND n->>'profile_id'=o.aggregate_id AND n->>'source_creation_revision'=o.source_revision::text
   AND sel.revision::text=n->>'selection_revision' AND e.state='committed' AND e.fence=w.fence AND e.id=w.effect_receipt_id
   AND e.owner_module_id='track_subscription_entitlement' AND e.operation='assignDefaultFreeTrack.v1'
   AND e.subject_scope='CustomerProfile:'||o.aggregate_id AND e.semantic_effect_key=n->>'semantic_key'
   AND e.fingerprint=o.payload_hash AND e.mutation_transaction_id=n->>'mutation_transaction_id'
   AND EXISTS(SELECT 1 FROM platform.runtime_inbox_receipt i WHERE i.effect_receipt_id=e.id AND i.outbox_message_id=o.id
    AND i.handler_name='assignDefaultFreeTrack.v1' AND i.consumer_owner='track_subscription_entitlement'
    AND i.payload_hash=o.payload_hash AND i.mutation_transaction_id=e.mutation_transaction_id),false);
 END IF;
 RETURN false;
END $wa$;
