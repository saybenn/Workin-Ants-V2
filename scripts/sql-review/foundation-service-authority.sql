-- P0-C-03A/DRAFT-01. Private Identity source, not a permission-policy catalog.
-- Identity's separately credentialed transition port verifies its canonical
-- authorization receipt before this transaction. Issuer/app/worker cannot write it.
CREATE TABLE platform_private.identity_service_receipt (
 id uuid PRIMARY KEY,
 service_principal text NOT NULL,
 previous_generation bigint,
 previous_receipt_id uuid REFERENCES platform_private.identity_service_receipt(id) ON DELETE RESTRICT ON UPDATE RESTRICT,
 security_generation bigint NOT NULL CHECK (security_generation>=0),
 transition text NOT NULL CHECK (transition IN ('bootstrap','rotate','revoke','recover')),
 revoked_at timestamptz,
 identity_authorization_ref text NOT NULL CHECK (length(identity_authorization_ref)>0),
 mutation_transaction_id text NOT NULL DEFAULT pg_current_xact_id()::text,
 UNIQUE(service_principal,security_generation,id),
 CHECK ((previous_generation IS NULL AND previous_receipt_id IS NULL AND security_generation=0 AND transition='bootstrap')
     OR (previous_generation IS NOT NULL AND previous_receipt_id IS NOT NULL AND security_generation=previous_generation+1 AND transition<>'bootstrap')),
 CHECK ((transition='revoke')=(revoked_at IS NOT NULL))
);
CREATE TABLE platform_private.identity_service_authorization (
 service_principal text PRIMARY KEY CHECK (length(service_principal)>0),
 security_generation bigint NOT NULL CHECK (security_generation>=0),
 revoked_at timestamptz,
 identity_receipt_id uuid NOT NULL UNIQUE,
 mutation_transaction_id text NOT NULL DEFAULT pg_current_xact_id()::text,
 FOREIGN KEY(service_principal,security_generation,identity_receipt_id)
  REFERENCES platform_private.identity_service_receipt(service_principal,security_generation,id) ON DELETE RESTRICT ON UPDATE RESTRICT
);
ALTER TABLE platform_private.identity_service_receipt ENABLE ROW LEVEL SECURITY;
ALTER TABLE platform_private.identity_service_receipt FORCE ROW LEVEL SECURITY;
ALTER TABLE platform_private.identity_service_authorization ENABLE ROW LEVEL SECURITY;
ALTER TABLE platform_private.identity_service_authorization FORCE ROW LEVEL SECURITY;
GRANT SELECT,INSERT ON platform_private.identity_service_receipt TO wa_identity_service_authority;
GRANT SELECT,INSERT,UPDATE ON platform_private.identity_service_authorization TO wa_identity_service_authority;
GRANT SELECT(service_principal,security_generation,revoked_at) ON platform_private.identity_service_authorization TO wa_private_helper_owner;
CREATE POLICY identity_receipt_owner ON platform_private.identity_service_receipt TO wa_identity_service_authority USING (true) WITH CHECK (true);
CREATE POLICY identity_service_owner ON platform_private.identity_service_authorization TO wa_identity_service_authority USING (true) WITH CHECK (true);
CREATE POLICY identity_service_leaf ON platform_private.identity_service_authorization FOR SELECT TO wa_private_helper_owner USING (true);

CREATE FUNCTION platform_private.identity_service_guard() RETURNS trigger
LANGUAGE plpgsql SECURITY INVOKER SET search_path=pg_catalog AS $wa$
DECLARE r platform_private.identity_service_receipt; old_authority platform_private.identity_service_authorization;
BEGIN
 IF session_user::text<>'wa_identity_service_authority' OR TG_OP='DELETE' THEN
  RAISE EXCEPTION 'Identity service authority required' USING ERRCODE='42501'; END IF;
 PERFORM pg_advisory_xact_lock(hashtextextended('service:'||NEW.service_principal,0));
 IF TG_TABLE_NAME='identity_service_receipt' THEN
  IF TG_OP<>'INSERT' THEN RAISE EXCEPTION 'immutable Identity receipt'; END IF;
  SELECT * INTO old_authority FROM platform_private.identity_service_authorization WHERE service_principal=NEW.service_principal;
  IF FOUND THEN
   IF NEW.previous_generation IS DISTINCT FROM old_authority.security_generation
    OR NEW.previous_receipt_id IS DISTINCT FROM old_authority.identity_receipt_id
    OR NEW.security_generation<>old_authority.security_generation+1
    OR (old_authority.revoked_at IS NOT NULL AND NEW.transition<>'recover')
    OR (old_authority.revoked_at IS NULL AND NEW.transition NOT IN ('rotate','revoke'))
   THEN RAISE EXCEPTION 'stale or unsupported Identity transition'; END IF;
  ELSIF NEW.transition<>'bootstrap' OR NEW.previous_generation IS NOT NULL OR NEW.security_generation<>0 THEN
   RAISE EXCEPTION 'service bootstrap must have no predecessor';
  END IF;
  IF NEW.transition='revoke' THEN NEW.revoked_at:=clock_timestamp(); ELSE NEW.revoked_at:=NULL; END IF;
 ELSE
  IF TG_OP='UPDATE' AND (NEW.service_principal<>OLD.service_principal OR NEW.security_generation<>OLD.security_generation+1) THEN
   RAISE EXCEPTION 'service generation must advance once'; END IF;
  SELECT * INTO STRICT r FROM platform_private.identity_service_receipt WHERE id=NEW.identity_receipt_id;
  IF r.service_principal<>NEW.service_principal OR r.security_generation<>NEW.security_generation
   OR r.revoked_at IS DISTINCT FROM NEW.revoked_at OR r.mutation_transaction_id<>pg_current_xact_id()::text
   OR r.previous_generation IS DISTINCT FROM (CASE WHEN TG_OP='UPDATE' THEN OLD.security_generation ELSE NULL::bigint END)
   OR r.previous_receipt_id IS DISTINCT FROM (CASE WHEN TG_OP='UPDATE' THEN OLD.identity_receipt_id ELSE NULL::uuid END)
  THEN RAISE EXCEPTION 'exact current Identity receipt required'; END IF;
 END IF;
 NEW.mutation_transaction_id:=pg_current_xact_id()::text;
 RETURN NEW;
END $wa$;
CREATE TRIGGER identity_service_write BEFORE INSERT OR UPDATE OR DELETE ON platform_private.identity_service_authorization FOR EACH ROW EXECUTE FUNCTION platform_private.identity_service_guard();
CREATE TRIGGER identity_receipt_write BEFORE INSERT OR UPDATE OR DELETE ON platform_private.identity_service_receipt FOR EACH ROW EXECUTE FUNCTION platform_private.identity_service_guard();
CREATE FUNCTION platform_private.identity_receipt_commit() RETURNS trigger
LANGUAGE plpgsql SECURITY INVOKER SET search_path=pg_catalog AS $wa$
BEGIN
 IF NOT EXISTS(SELECT 1 FROM platform_private.identity_service_authorization a WHERE a.service_principal=NEW.service_principal
  AND a.security_generation=NEW.security_generation AND a.identity_receipt_id=NEW.id
  AND a.mutation_transaction_id=NEW.mutation_transaction_id) THEN RAISE EXCEPTION 'orphan Identity authorization receipt'; END IF;
 RETURN NULL;
END $wa$;
CREATE CONSTRAINT TRIGGER identity_receipt_atomic AFTER INSERT ON platform_private.identity_service_receipt DEFERRABLE INITIALLY DEFERRED FOR EACH ROW EXECUTE FUNCTION platform_private.identity_receipt_commit();
