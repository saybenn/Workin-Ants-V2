-- SOURCE ONLY. Separately reviewed read-only collector for the genuine client
-- ledger exception. Requires the already-existing public._prisma_migrations;
-- absence/type/query failure stops before history. Never creates/adopts/repairs it.
-- No logs, migration names/checksums, IDs, raw timestamps or SQL bodies escape.
BEGIN ISOLATION LEVEL REPEATABLE READ READ ONLY;
SET LOCAL search_path=pg_catalog;
SET LOCAL lock_timeout='1s';
SET LOCAL statement_timeout='5s';
-- LOCK resolves/locks metadata, without SELECTing a same-named view's query.
-- No other relation can replace this name while the ACCESS SHARE lock is held.
LOCK TABLE ONLY public._prisma_migrations IN ACCESS SHARE MODE;
DO $wa_ledger_shape$
DECLARE ledger_id oid := to_regclass('public._prisma_migrations');
BEGIN
 IF current_user<>session_user OR NOT EXISTS(SELECT 1 FROM pg_roles WHERE rolname=current_user AND rolsuper)
 THEN RAISE EXCEPTION 'ledger collector requires direct superuser login' USING ERRCODE='42501'; END IF;
 IF ledger_id IS NULL OR NOT EXISTS(
  SELECT 1 FROM pg_class c JOIN pg_namespace n ON n.oid=c.relnamespace JOIN pg_am am ON am.oid=c.relam
  WHERE c.oid=ledger_id AND n.nspname='public' AND c.relname='_prisma_migrations'
   AND c.relkind='r' AND c.relpersistence='p' AND am.amname='heap' AND NOT c.relispartition
   AND pg_get_userbyid(c.relowner)='wa_migrator' AND NOT c.relrowsecurity AND NOT c.relforcerowsecurity)
 OR EXISTS(SELECT 1 FROM pg_inherits WHERE inhrelid=ledger_id OR inhparent=ledger_id)
 OR EXISTS(SELECT 1 FROM pg_rewrite WHERE ev_class=ledger_id)
 THEN RAISE EXCEPTION 'ledger collector source-safe relation required' USING ERRCODE='0A000'; END IF;
 IF EXISTS(
  WITH expected(ordinal,name,type_oid,typmod,not_null) AS (VALUES
   (1,'id','pg_catalog.varchar'::regtype,40,true),(2,'checksum','pg_catalog.varchar'::regtype,68,true),
   (3,'finished_at','pg_catalog.timestamptz'::regtype,-1,false),(4,'migration_name','pg_catalog.varchar'::regtype,259,true),
   (5,'logs','pg_catalog.text'::regtype,-1,false),(6,'rolled_back_at','pg_catalog.timestamptz'::regtype,-1,false),
   (7,'started_at','pg_catalog.timestamptz'::regtype,-1,true),(8,'applied_steps_count','pg_catalog.int4'::regtype,-1,true)),
  wanted AS (SELECT ordinal,name,type_oid::oid,typmod,not_null,0 AS dimensions,''::text AS identity,''::text AS generated,
    false AS dropped,true AS default_collation FROM expected),
  actual AS (SELECT a.attnum::integer,a.attname::text,a.atttypid,a.atttypmod,a.attnotnull,a.attndims,
    a.attidentity::text,a.attgenerated::text,a.attisdropped,a.attcollation=t.typcollation
   FROM pg_attribute a LEFT JOIN pg_type t ON t.oid=a.atttypid WHERE a.attrelid=ledger_id AND a.attnum>0)
  (SELECT * FROM wanted EXCEPT SELECT * FROM actual) UNION ALL (SELECT * FROM actual EXCEPT SELECT * FROM wanted))
 THEN RAISE EXCEPTION 'ledger collector exact builtin columns required' USING ERRCODE='0A000'; END IF;
END $wa_ledger_shape$;
SET LOCAL TimeZone='UTC'; SELECT jsonb_build_object('ids_unique',count(*)=count(DISTINCT id),'rows',COALESCE(jsonb_agg(jsonb_build_object('name_sha256',encode(sha256(convert_to(migration_name,'UTF8')),'hex'),'checksum_sha256',encode(sha256(convert_to(checksum,'UTF8')),'hex'),'finished',finished_at IS NOT NULL,'rolled_back',rolled_back_at IS NOT NULL,'steps',applied_steps_count,'logs_state',CASE WHEN logs IS NULL THEN 'NULL' WHEN logs='' THEN 'EMPTY' ELSE 'NONEMPTY' END,'immutable_sha256',encode(sha256(convert_to(jsonb_build_object('id',id,'name',migration_name,'checksum',checksum,'started',started_at,'logs',logs,'steps',applied_steps_count)::text,'UTF8')),'hex')) ORDER BY started_at,id),'[]'::jsonb)) FROM ONLY public._prisma_migrations; COMMIT;
