BEGIN;
CREATE SCHEMA wa_lease_branch_v1_repro;
CREATE ROLE wa_lease_v1_app LOGIN NOSUPERUSER NOCREATEDB NOCREATEROLE NOINHERIT NOREPLICATION NOBYPASSRLS;
CREATE ROLE wa_lease_v1_worker LOGIN NOSUPERUSER NOCREATEDB NOCREATEROLE NOINHERIT NOREPLICATION NOBYPASSRLS;
CREATE ROLE wa_lease_v1_verifier LOGIN NOSUPERUSER NOCREATEDB NOCREATEROLE NOINHERIT NOREPLICATION NOBYPASSRLS;
GRANT USAGE ON SCHEMA wa_lease_branch_v1_repro TO wa_lease_v1_app,wa_lease_v1_worker,wa_lease_v1_verifier;
CREATE FUNCTION wa_lease_branch_v1_repro.lease_secret_matches(expected_hash text) RETURNS boolean
LANGUAGE sql VOLATILE SECURITY INVOKER SET search_path=pg_catalog AS $wa$
 SELECT CASE WHEN current_setting('wa.lease_secret',true) ~ '^[0-9a-f]{64}$'
  THEN encode(sha256(decode(current_setting('wa.lease_secret',true),'hex')),'hex')=expected_hash
  ELSE false END;
$wa$;
CREATE OR REPLACE FUNCTION wa_lease_branch_v1_repro.guard() RETURNS trigger
LANGUAGE plpgsql VOLATILE CALLED ON NULL INPUT SECURITY INVOKER
PARALLEL UNSAFE COST 100 SET search_path=pg_catalog AS $wa$
BEGIN
   IF OLD.state='leased' AND NEW.state<>'leased' AND (OLD.lease_expires_at<=clock_timestamp()
    OR NOT wa_lease_branch_v1_repro.lease_secret_matches(OLD.lease_token_hash::text)
    OR current_setting('wa.fence',true) IS DISTINCT FROM OLD.fence::text)
   THEN RAISE EXCEPTION 'expired or foreign worker'; END IF;
 RETURN NEW;
END $wa$;
REVOKE ALL ON ALL FUNCTIONS IN SCHEMA wa_lease_branch_v1_repro FROM PUBLIC;
GRANT EXECUTE ON FUNCTION wa_lease_branch_v1_repro.lease_secret_matches(text) TO wa_lease_v1_worker,wa_lease_v1_verifier;
CREATE TABLE wa_lease_branch_v1_repro.work(id integer PRIMARY KEY,state text NOT NULL,fence bigint NOT NULL,attempt_count integer NOT NULL,lease_token_hash text,lease_expires_at timestamptz,effect_receipt_id uuid,next_attempt_at timestamptz NOT NULL);
INSERT INTO wa_lease_branch_v1_repro.work VALUES(1,'pending',0,0,NULL,NULL,NULL,'2026-01-01T00:00:00Z'),(2,'leased',7,1,encode(sha256(decode(repeat('a',64),'hex')),'hex'),clock_timestamp()+interval '1 hour',NULL,'2026-01-01T00:00:00Z'),(3,'leased',7,1,encode(sha256(decode(repeat('a',64),'hex')),'hex'),clock_timestamp()-interval '1 hour',NULL,'2026-01-01T00:00:00Z'),(4,'leased',7,1,encode(sha256(decode(repeat('a',64),'hex')),'hex'),clock_timestamp()+interval '1 hour',NULL,'2026-01-01T00:00:00Z'),(5,'leased',7,1,encode(sha256(decode(repeat('a',64),'hex')),'hex'),clock_timestamp()+interval '1 hour',NULL,'2026-01-01T00:00:00Z');
CREATE TRIGGER exact_guard BEFORE UPDATE ON wa_lease_branch_v1_repro.work FOR EACH ROW EXECUTE FUNCTION wa_lease_branch_v1_repro.guard();
GRANT SELECT ON wa_lease_branch_v1_repro.work TO wa_lease_v1_app,wa_lease_v1_worker,wa_lease_v1_verifier;
GRANT UPDATE(next_attempt_at) ON wa_lease_branch_v1_repro.work TO wa_lease_v1_app;
GRANT UPDATE(state,lease_token_hash,lease_expires_at) ON wa_lease_branch_v1_repro.work TO wa_lease_v1_worker;
COMMIT;
