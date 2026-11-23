BEGIN;
SET LOCAL ROLE wa_schema_owner;
CREATE OR REPLACE FUNCTION platform_private.runtime_transition() RETURNS trigger
LANGUAGE plpgsql VOLATILE CALLED ON NULL INPUT SECURITY INVOKER
PARALLEL UNSAFE COST 100 SET search_path=pg_catalog AS $wa$
DECLARE w platform.runtime_work_item; e platform.runtime_effect_receipt; c platform.runtime_command_receipt;
BEGIN
 IF TG_TABLE_NAME='runtime_work_item' THEN
  IF TG_OP='INSERT' THEN
   IF session_user::text<>'wa_app_runtime' OR NEW.state<>'pending' OR NEW.fence<>0 OR NEW.attempt_count<>0
    OR NEW.effect_receipt_id IS NOT NULL OR NOT platform_private.context_allows('platform_integration_owner','runtime.schedule_work.v1','RuntimeWorkItem',NEW.id::text,'work.schedule')
   THEN RAISE EXCEPTION 'job must enter through registered scheduler'; END IF;
  END IF;
  IF TG_OP='UPDATE' THEN
   IF OLD.state='completed' OR NEW.attempt_count<OLD.attempt_count THEN RAISE EXCEPTION 'terminal work/regressive attempt'; END IF;
   IF NEW.effect_receipt_id IS DISTINCT FROM OLD.effect_receipt_id THEN
    IF OLD.effect_receipt_id IS NOT NULL OR NEW.effect_receipt_id IS NULL OR OLD.state<>'leased'
     OR NOT platform_private.worker_effect_matches(OLD.id,NEW.effect_receipt_id,false)
    THEN RAISE EXCEPTION 'effect link must be one exact protected attachment'; END IF;
   END IF;
   IF NEW.state='leased' AND (OLD.state<>'leased' OR NEW.lease_token_hash IS DISTINCT FROM OLD.lease_token_hash) THEN
    IF session_user::text<>'wa_worker' OR NOT platform_private.context_allows('platform_integration_owner','runtime.claim_work.v1','RuntimeWorkItem',OLD.id::text,'work.claim')
     OR NEW.fence<>OLD.fence+1 OR NEW.attempt_count<>OLD.attempt_count+1
     OR NEW.lease_expires_at<=clock_timestamp()
     OR (OLD.state='leased' AND OLD.lease_expires_at>clock_timestamp())
     OR NOT platform_private.lease_secret_matches(NEW.lease_token_hash::text)
    THEN RAISE EXCEPTION 'invalid claim/reclaim'; END IF;
   ELSIF NEW.fence<>OLD.fence OR NEW.attempt_count<>OLD.attempt_count
   THEN RAISE EXCEPTION 'fence and attempt may change only on claim'; END IF;
   IF OLD.state='leased' AND NEW.lease_token_hash IS NOT DISTINCT FROM OLD.lease_token_hash AND NEW.state='leased'
    AND NEW.lease_expires_at IS DISTINCT FROM OLD.lease_expires_at THEN
    IF NOT platform_private.context_allows('platform_integration_owner','runtime.renew_work.v1','RuntimeWorkItem',OLD.id::text,'work.renew')
     OR OLD.lease_expires_at<=clock_timestamp() OR NOT platform_private.lease_secret_matches(OLD.lease_token_hash::text)
     OR NEW.lease_expires_at<=OLD.lease_expires_at OR NEW.attempt_count<>OLD.attempt_count
    THEN RAISE EXCEPTION 'renewal requires current secret and extends live lease'; END IF;
   END IF;
   IF OLD.state='leased' AND NEW.state<>'leased' THEN
    IF OLD.lease_expires_at<=clock_timestamp()
    OR NOT platform_private.lease_secret_matches(OLD.lease_token_hash::text)
    OR current_setting('wa.fence',true) IS DISTINCT FROM OLD.fence::text
    THEN RAISE EXCEPTION 'expired or foreign worker'; END IF;
   END IF;
  END IF;
  IF NEW.state='completed' THEN
   SELECT * INTO STRICT e FROM platform.runtime_effect_receipt WHERE id=NEW.effect_receipt_id;
   IF e.state<>'committed' OR e.fence>NEW.fence OR NOT platform_private.worker_effect_matches(NEW.id,e.id,false)
   THEN RAISE EXCEPTION 'completion without exact committed effect and current holder'; END IF;
  END IF;
 ELSIF TG_TABLE_NAME='runtime_attempt' THEN
  SELECT * INTO STRICT w FROM platform.runtime_work_item WHERE id=NEW.work_item_id;
  IF w.fence<>NEW.fence OR NEW.attempt_number<>w.attempt_count OR NOT platform_private.worker_lease_valid(w.id,NULL,true)
  THEN RAISE EXCEPTION 'stale attempt'; END IF;
 ELSIF TG_TABLE_NAME='runtime_reservation' AND TG_OP='INSERT' THEN
  IF NEW.state<>'active' OR NEW.effect_receipt_id IS NOT NULL
  THEN RAISE EXCEPTION 'reservation must start active without outcome'; END IF;
 ELSIF TG_TABLE_NAME='runtime_reservation' AND TG_OP='UPDATE' THEN
  IF OLD.state IN ('committed','released') THEN RAISE EXCEPTION 'terminal reservation'; END IF;
  IF NEW.effect_receipt_id IS DISTINCT FROM OLD.effect_receipt_id AND
   (OLD.effect_receipt_id IS NOT NULL OR NEW.effect_receipt_id IS NULL OR NEW.state NOT IN ('committed','released'))
  THEN RAISE EXCEPTION 'reservation outcome link attaches once at exact terminal proof'; END IF;
  IF NOT ((OLD.state='active' AND NEW.state IN ('active','unknown','committed','released'))
   OR (OLD.state='unknown' AND NEW.state IN ('unknown','committed','released')))
  THEN RAISE EXCEPTION 'unsupported reservation transition'; END IF;
  IF NEW.state IN ('committed','released') THEN
   SELECT * INTO STRICT c FROM platform.runtime_command_receipt WHERE id=NEW.command_receipt_id;
   SELECT * INTO STRICT e FROM platform.runtime_effect_receipt WHERE id=NEW.effect_receipt_id;
   IF e.command_receipt_id IS DISTINCT FROM NEW.command_receipt_id OR e.owner_module_id<>NEW.owner_module_id
    OR c.owner_module_id<>NEW.owner_module_id OR e.operation<>c.operation OR e.fingerprint<>c.fingerprint OR e.fence<>NEW.fence
    OR e.subject_scope<>'RuntimeReservation:'||NEW.id::text OR c.subject_scope<>e.subject_scope
    OR e.semantic_effect_key<>NEW.semantic_key OR c.semantic_key<>NEW.semantic_key
    OR (NEW.state='released' AND (e.state<>'fenced_noncommit' OR c.state<>'fenced_noncommit'
      OR e.mutation_transaction_id<>pg_current_xact_id()::text OR c.mutation_transaction_id<>e.mutation_transaction_id))
    OR (NEW.state='committed' AND (e.state<>'committed' OR c.state<>'committed'))
   THEN RAISE EXCEPTION 'reservation outcome needs exact command/operation/effect proof'; END IF;
  END IF;
 END IF;
 RETURN NEW;
END $wa$;
RESET ROLE;
COMMIT;
