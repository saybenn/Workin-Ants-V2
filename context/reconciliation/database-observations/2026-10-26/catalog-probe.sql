-- P0-C manual schema-only probe. PREPARED, NOT EXECUTED OR QUALIFIED.
-- Run only after the steward verifies the isolated development target.
-- No application-row reads, credentials, function bodies, migration or DDL.
-- Catalog visibility is role-dependent; omissions are gaps, not proof of denial.
BEGIN TRANSACTION ISOLATION LEVEL REPEATABLE READ READ ONLY;
SET LOCAL statement_timeout = '30s';
SET LOCAL lock_timeout = '3s';

WITH namespaces AS (
  SELECT oid, nspname, nspowner, nspacl
  FROM pg_namespace
  WHERE nspname <> 'information_schema' AND nspname !~ '^pg_'
), relations AS (
  SELECT c.*, n.nspname
  FROM pg_class c JOIN namespaces n ON n.oid = c.relnamespace
  WHERE c.relkind IN ('r', 'p', 'v', 'm', 'S', 'f')
)
SELECT jsonb_build_object(
  'probe_version', 'P0-C-2026-10-26-v1',
  'collected_at', current_timestamp,
  'transaction_read_only', current_setting('transaction_read_only'),
  'database', current_database(),
  'collector_role', current_user,
  'postgres_version', current_setting('server_version'),
  'postgres_version_num', current_setting('server_version_num'),
  'limits', jsonb_build_array(
    'Database name is not provider/project identity; supply isolation evidence separately.',
    'No application-row emptiness proof or migration-ledger contents collected.',
    'Function bodies and view definitions require separate protected review.',
    'Provider API exposure, backups, actual role behavior and adoption are not proven.'
  ),
  'extensions', COALESCE((
    SELECT jsonb_agg(jsonb_build_object('name', e.extname, 'version', e.extversion,
      'schema', n.nspname, 'owner', pg_get_userbyid(e.extowner)) ORDER BY e.extname)
    FROM pg_extension e JOIN pg_namespace n ON n.oid = e.extnamespace
  ), '[]'::jsonb),
  'namespaces', COALESCE((
    SELECT jsonb_agg(jsonb_build_object('schema', nspname,
      'owner', pg_get_userbyid(nspowner), 'acl', nspacl::text) ORDER BY nspname)
    FROM namespaces
  ), '[]'::jsonb),
  'relations', COALESCE((
    SELECT jsonb_agg(jsonb_build_object('schema', nspname, 'name', relname,
      'kind', relkind, 'owner', pg_get_userbyid(relowner),
      'rls_enabled', relrowsecurity, 'rls_forced', relforcerowsecurity,
      'acl', relacl::text, 'options', reloptions) ORDER BY nspname, relname)
    FROM relations
  ), '[]'::jsonb),
  'columns', COALESCE((
    SELECT jsonb_agg(jsonb_build_object('schema', c.nspname, 'relation', c.relname,
      'column', a.attname, 'position', a.attnum, 'type', format_type(a.atttypid, a.atttypmod),
      'not_null', a.attnotnull, 'identity', a.attidentity, 'generated', a.attgenerated,
      'default', pg_get_expr(d.adbin, d.adrelid)) ORDER BY c.nspname, c.relname, a.attnum)
    FROM relations c JOIN pg_attribute a ON a.attrelid = c.oid
    LEFT JOIN pg_attrdef d ON d.adrelid = c.oid AND d.adnum = a.attnum
    WHERE a.attnum > 0 AND NOT a.attisdropped
  ), '[]'::jsonb),
  'constraints', COALESCE((
    SELECT jsonb_agg(jsonb_build_object('schema', c.nspname, 'relation', c.relname,
      'name', k.conname, 'kind', k.contype, 'definition', pg_get_constraintdef(k.oid, true),
      'validated', k.convalidated, 'deferrable', k.condeferrable, 'deferred', k.condeferred)
      ORDER BY c.nspname, c.relname, k.conname)
    FROM pg_constraint k JOIN relations c ON c.oid = k.conrelid
  ), '[]'::jsonb),
  'indexes', COALESCE((
    SELECT jsonb_agg(jsonb_build_object('schema', c.nspname, 'relation', c.relname,
      'name', i.relname, 'definition', pg_get_indexdef(x.indexrelid),
      'valid', x.indisvalid, 'ready', x.indisready) ORDER BY c.nspname, c.relname, i.relname)
    FROM pg_index x JOIN relations c ON c.oid = x.indrelid
    JOIN pg_class i ON i.oid = x.indexrelid
  ), '[]'::jsonb),
  'enums', COALESCE((
    SELECT jsonb_agg(jsonb_build_object('schema', n.nspname, 'type', t.typname,
      'label', e.enumlabel, 'sort_order', e.enumsortorder) ORDER BY n.nspname, t.typname, e.enumsortorder)
    FROM pg_enum e JOIN pg_type t ON t.oid = e.enumtypid
    JOIN namespaces n ON n.oid = t.typnamespace
  ), '[]'::jsonb),
  'policies', COALESCE((
    SELECT jsonb_agg(jsonb_build_object('schema', schemaname, 'relation', tablename,
      'name', policyname, 'permissive', permissive, 'roles', roles, 'command', cmd,
      'using', qual, 'check', with_check) ORDER BY schemaname, tablename, policyname)
    FROM pg_policies WHERE schemaname IN (SELECT nspname FROM namespaces)
  ), '[]'::jsonb),
  'functions', COALESCE((
    SELECT jsonb_agg(jsonb_build_object('schema', n.nspname, 'name', p.proname,
      'arguments', pg_get_function_identity_arguments(p.oid), 'kind', p.prokind,
      'owner', pg_get_userbyid(p.proowner), 'security_definer', p.prosecdef,
      'leakproof', p.proleakproof, 'volatility', p.provolatile, 'acl', p.proacl::text,
      'search_path_settings', ARRAY(SELECT v FROM unnest(p.proconfig) v WHERE v LIKE 'search_path=%'),
      'body_change_fingerprint_md5', md5(p.prosrc)) ORDER BY n.nspname, p.proname, p.oid)
    FROM pg_proc p JOIN namespaces n ON n.oid = p.pronamespace
  ), '[]'::jsonb),
  'triggers', COALESCE((
    SELECT jsonb_agg(jsonb_build_object('schema', c.nspname, 'relation', c.relname,
      'name', t.tgname, 'enabled', t.tgenabled, 'definition', pg_get_triggerdef(t.oid, true))
      ORDER BY c.nspname, c.relname, t.tgname)
    FROM pg_trigger t JOIN relations c ON c.oid = t.tgrelid WHERE NOT t.tgisinternal
  ), '[]'::jsonb),
  'roles', COALESCE((
    SELECT jsonb_agg(jsonb_build_object('name', rolname, 'superuser', rolsuper,
      'inherit', rolinherit, 'create_role', rolcreaterole, 'create_database', rolcreatedb,
      'can_login', rolcanlogin, 'bypass_rls', rolbypassrls) ORDER BY rolname)
    FROM pg_roles
  ), '[]'::jsonb),
  'role_membership', COALESCE((
    SELECT jsonb_agg(jsonb_build_object('role', pg_get_userbyid(roleid),
      'member', pg_get_userbyid(member), 'grantor', pg_get_userbyid(grantor),
      'admin_option', admin_option) ORDER BY roleid, member)
    FROM pg_auth_members
  ), '[]'::jsonb),
  'default_privileges', COALESCE((
    SELECT jsonb_agg(jsonb_build_object('owner', pg_get_userbyid(d.defaclrole),
      'schema', n.nspname, 'kind', d.defaclobjtype, 'acl', d.defaclacl::text)
      ORDER BY d.defaclrole, d.defaclnamespace, d.defaclobjtype)
    FROM pg_default_acl d LEFT JOIN pg_namespace n ON n.oid = d.defaclnamespace
  ), '[]'::jsonb),
  'migration_ledger_relations', COALESCE((
    SELECT jsonb_agg(jsonb_build_object('schema', nspname, 'name', relname) ORDER BY nspname)
    FROM relations WHERE relname = '_prisma_migrations'
  ), '[]'::jsonb)
) AS provenance_catalog;

ROLLBACK;
