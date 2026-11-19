-- Fixed PostgreSQL17.11 collector compatibility controls, no application rows.
-- Caught diagnostic text stays in a local variable and is never exported.
BEGIN READ ONLY;
SET LOCAL search_path = pg_catalog;
DO $acl_preflight$
DECLARE
  rejected boolean := false;
  primary_message text;
  observed_count integer;
  sequence_privileges text[];
  owner_only boolean;
BEGIN
  BEGIN
    PERFORM 1 FROM aclexplode('{}'::aclitem[]);
  EXCEPTION WHEN SQLSTATE '22023' THEN
    GET STACKED DIAGNOSTICS primary_message = MESSAGE_TEXT;
    IF primary_message = 'ACL arrays must be one-dimensional' THEN
      rejected := true;
    ELSE
      RAISE;
    END IF;
  END;
  IF NOT rejected THEN
    RAISE EXCEPTION 'catalog ACL dimension control did not reject';
  END IF;
  SELECT count(*) INTO observed_count FROM aclexplode(NULL::aclitem[]);
  IF observed_count <> 0 THEN
    RAISE EXCEPTION 'catalog ACL NULL control returned rows';
  END IF;
  SELECT count(*) INTO observed_count
    FROM aclexplode(CASE WHEN cardinality('{}'::aclitem[]) > 0
      THEN '{}'::aclitem[] ELSE NULL::aclitem[] END);
  IF observed_count <> 0 THEN
    RAISE EXCEPTION 'catalog ACL empty control returned rows';
  END IF;
  SELECT array_agg(a.privilege_type ORDER BY a.privilege_type),
    bool_and(a.grantee=r.oid AND a.grantor=r.oid AND NOT a.is_grantable)
    INTO sequence_privileges,owner_only
    FROM pg_roles r CROSS JOIN LATERAL aclexplode(acldefault('s',r.oid)) a
    WHERE r.rolname=current_user;
  IF sequence_privileges IS DISTINCT FROM ARRAY['SELECT','UPDATE','USAGE']::text[]
    OR owner_only IS DISTINCT FROM true THEN
    RAISE EXCEPTION 'catalog sequence default control mismatch';
  END IF;
END
$acl_preflight$;
SELECT jsonb_build_object(
  'format','workinants.catalog-acl-preflight.v1',
  'server_version_num',current_setting('server_version_num')::integer,
  'read_only',current_setting('transaction_read_only')='on',
  'collected_as',current_user,
  'collector_is_superuser',(SELECT rolsuper FROM pg_roles WHERE rolname=current_user),
  'old_zero_dimensional_acl_rejected_exactly',true,
  'null_acl_has_zero_rows',true,
  'empty_acl_guard_has_zero_rows',true,
  'sequence_default_has_exact_owner_privileges',true);
ROLLBACK;
