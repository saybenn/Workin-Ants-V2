-- REVIEW ONLY. Run in a separate connection as the ORIGINAL bootstrap grantor,
-- after either application success or failure; never as wa_schema_owner/migrator.
-- No runtime credentials are activated until this independent cleanup verifies.
BEGIN;
DO $cleanup$
DECLARE principal oid:=current_user::regrole; owner_role oid:='wa_schema_owner'::regrole;
BEGIN
 IF EXISTS(SELECT 1 FROM pg_auth_members m WHERE m.member=owner_role
  AND m.roleid IN ('wa_private_helper_owner'::regrole,'wa_customer_verifier'::regrole,'wa_track_verifier'::regrole)
  AND m.grantor<>principal) THEN RAISE EXCEPTION 'cleanup requires original bootstrap grantor'; END IF;
END $cleanup$;
REVOKE wa_private_helper_owner,wa_customer_verifier,wa_track_verifier FROM wa_schema_owner GRANTED BY CURRENT_USER;
DO $verify$
BEGIN
 IF EXISTS(SELECT 1 FROM pg_auth_members WHERE member='wa_schema_owner'::regrole
  AND roleid IN ('wa_private_helper_owner'::regrole,'wa_customer_verifier'::regrole,'wa_track_verifier'::regrole))
 THEN RAISE EXCEPTION 'temporary installation membership remains'; END IF;
 IF has_schema_privilege('wa_private_helper_owner','platform_private','CREATE')
  OR has_schema_privilege('wa_customer_verifier','platform_private','CREATE')
  OR has_schema_privilege('wa_track_verifier','platform_private','CREATE')
 THEN RAISE EXCEPTION 'temporary function creation authority remains'; END IF;
END $verify$;
COMMIT;
