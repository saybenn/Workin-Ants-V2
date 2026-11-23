BEGIN TRANSACTION ISOLATION LEVEL REPEATABLE READ READ ONLY;
DO $wa_history_fingerprints$
BEGIN
 IF current_setting('server_version_num')<>'170011'
 OR current_database()<>'wa_p0c_rehearsal' OR current_user<>'postgres'
 OR current_setting('transaction_read_only')<>'on'
 OR NOT (SELECT rolsuper FROM pg_roles WHERE rolname=current_user)
 OR NOT EXISTS(SELECT 1 FROM pg_class c JOIN pg_namespace n ON n.oid=c.relnamespace
   WHERE n.nspname='public' AND c.relname='_prisma_migrations' AND c.relkind='r'
    AND c.relowner='wa_migrator'::regrole AND NOT c.relrowsecurity AND NOT c.relforcerowsecurity)
 OR (SELECT count(*) FROM pg_attribute WHERE attrelid='public._prisma_migrations'::regclass
     AND attnum>0 AND NOT attisdropped)<>8
 THEN RAISE EXCEPTION 'exact local source ledger fingerprint context required' USING ERRCODE='0A000'; END IF;
END
$wa_history_fingerprints$;
SELECT jsonb_build_object(
 'schema','workinants.runtime-lease-history-fingerprints.v1',
 'server_version_num',current_setting('server_version_num')::integer,
 'database',current_database(),'collected_as',current_user,
 'collector_is_superuser',(SELECT rolsuper FROM pg_roles WHERE rolname=current_user),
 'read_only',current_setting('transaction_read_only')='on',
 'history_count',(SELECT count(*) FROM ONLY public._prisma_migrations),
 'rows',(SELECT jsonb_agg(row_data ORDER BY name_sha256,checksum_sha256)
  FROM (SELECT encode(sha256(convert_to(m.migration_name,'UTF8')),'hex') AS name_sha256,
    encode(sha256(convert_to(m.checksum,'UTF8')),'hex') AS checksum_sha256,
    jsonb_build_object('name_sha256',encode(sha256(convert_to(m.migration_name,'UTF8')),'hex'),
      'checksum_sha256',encode(sha256(convert_to(m.checksum,'UTF8')),'hex'),
      'row_sha256',encode(sha256(convert_to(to_jsonb(m)::text,'UTF8')),'hex')) AS row_data
   FROM ONLY public._prisma_migrations m) exact_rows));
ROLLBACK;
