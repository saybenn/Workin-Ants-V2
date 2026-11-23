BEGIN;
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
COMMIT;
