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
WITH ledger AS (
 SELECT c.*,n.nspname,am.amname FROM pg_class c
 JOIN pg_namespace n ON n.oid=c.relnamespace
 LEFT JOIN pg_am am ON am.oid=c.relam
 WHERE n.nspname='public' AND c.relname='_prisma_migrations'
), column_rows AS (
 SELECT a.attname AS name,a.attnum AS ordinal,tn.nspname||'.'||t.typname AS type,
  a.atttypmod AS typmod,NOT a.attnotnull AS nullable,a.attndims AS array_dimensions,
  a.attidentity AS identity,a.attgenerated AS generated,
  a.attcollation=t.typcollation AS collation_is_type_default,
  a.attstorage=t.typstorage AS storage_is_type_default,
  a.attcompression AS compression,a.attislocal AS is_local,a.attinhcount AS inherited_count,
  CASE WHEN d.adbin IS NOT NULL THEN encode(sha256(convert_to(pg_get_expr(d.adbin,d.adrelid,false),'UTF8')),'hex') END AS default_sha256
 FROM ledger l JOIN pg_attribute a ON a.attrelid=l.oid
 JOIN pg_type t ON t.oid=a.atttypid JOIN pg_namespace tn ON tn.oid=t.typnamespace
 LEFT JOIN pg_attrdef d ON d.adrelid=a.attrelid AND d.adnum=a.attnum
 WHERE a.attnum>0 AND NOT a.attisdropped
), constraint_rows AS (
 SELECT c.conname AS name,c.contype AS kind,c.condeferrable AS deferrable,
  c.condeferred AS initially_deferred,c.convalidated AS validated,c.connoinherit AS no_inherit,
  COALESCE((SELECT jsonb_agg(a.attname ORDER BY k.ordinality)
   FROM unnest(c.conkey) WITH ORDINALITY k(attnum,ordinality)
   JOIN pg_attribute a ON a.attrelid=c.conrelid AND a.attnum=k.attnum),'[]') AS columns,
  CASE WHEN c.conindid<>0 THEN n.nspname||'.'||i.relname END AS index_name,
  c.confrelid=0 AS no_referenced_relation,c.conbin IS NULL AS no_expression
 FROM ledger l JOIN pg_constraint c ON c.conrelid=l.oid
 LEFT JOIN pg_class i ON i.oid=c.conindid LEFT JOIN pg_namespace n ON n.oid=i.relnamespace
), index_rows AS (
 SELECT ns.nspname||'.'||ic.relname AS object,pg_get_userbyid(ic.relowner) AS owner,
  am.amname AS access_method,ic.relpersistence AS persistence,ic.relacl IS NULL AS no_index_acl,
  ic.reloptions IS NULL AS no_options,ic.reltablespace=0 AS default_tablespace,
  i.indisunique AS unique,i.indisprimary AS primary,i.indisvalid AS valid,i.indisready AS ready,
  i.indislive AS live,i.indimmediate AS immediate,i.indisclustered AS clustered,
  i.indisreplident AS replica_identity,i.indnullsnotdistinct AS nulls_not_distinct,
  i.indnkeyatts AS key_count,i.indnatts AS total_count,
  i.indexprs IS NULL AS no_expressions,i.indpred IS NULL AS no_predicate,
  COALESCE((SELECT jsonb_agg(jsonb_build_object('position',k.ordinality,'column',a.attname,
   'included',k.ordinality>i.indnkeyatts,'opclass',onsp.nspname||'.'||op.opcname,
   'opclass_default',op.opcdefault,'collation_is_type_default',co.collation_oid IS NOT DISTINCT FROM a.attcollation,
   'descending',(opt.options::integer & 1)=1,'nulls_first',(opt.options::integer & 2)=2) ORDER BY k.ordinality)
   FROM unnest(i.indkey::smallint[]) WITH ORDINALITY k(attnum,ordinality)
   LEFT JOIN pg_attribute a ON a.attrelid=i.indrelid AND a.attnum=k.attnum
   LEFT JOIN LATERAL unnest(i.indclass::oid[]) WITH ORDINALITY oc(opclass_oid,ordinality) ON oc.ordinality=k.ordinality
   LEFT JOIN pg_opclass op ON op.oid=oc.opclass_oid LEFT JOIN pg_namespace onsp ON onsp.oid=op.opcnamespace
   LEFT JOIN LATERAL unnest(i.indcollation::oid[]) WITH ORDINALITY co(collation_oid,ordinality) ON co.ordinality=k.ordinality
   LEFT JOIN LATERAL unnest(i.indoption::smallint[]) WITH ORDINALITY opt(options,ordinality) ON opt.ordinality=k.ordinality),'[]') AS keys
 FROM ledger l JOIN pg_index i ON i.indrelid=l.oid JOIN pg_class ic ON ic.oid=i.indexrelid
 JOIN pg_namespace ns ON ns.oid=ic.relnamespace JOIN pg_am am ON am.oid=ic.relam
), table_acl_rows AS (
 SELECT CASE WHEN a.grantee=0 THEN 'PUBLIC' ELSE pg_get_userbyid(a.grantee) END AS grantee,
  pg_get_userbyid(a.grantor) AS grantor,a.privilege_type AS privilege,a.is_grantable AS grant_option
 FROM ledger l CROSS JOIN LATERAL aclexplode(COALESCE(l.relacl,acldefault('r',l.relowner))) a
), column_acl_rows AS (
 SELECT att.attname AS column,CASE WHEN a.grantee=0 THEN 'PUBLIC' ELSE pg_get_userbyid(a.grantee) END AS grantee,
  pg_get_userbyid(a.grantor) AS grantor,a.privilege_type AS privilege,a.is_grantable AS grant_option
 FROM ledger l JOIN pg_attribute att ON att.attrelid=l.oid AND att.attnum>0 AND NOT att.attisdropped
 CROSS JOIN LATERAL aclexplode(att.attacl) a
), safe_history_rows AS (
 SELECT encode(sha256(convert_to(migration_name,'UTF8')),'hex') AS name_sha256,
  encode(sha256(convert_to(checksum,'UTF8')),'hex') AS checksum_sha256,
  checksum ~ '^[0-9a-f]{64}$' AS checksum_format_valid,
  id ~ '^[0-9a-f]{8}-[0-9a-f]{4}-4[0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$' AS id_is_uuid_v4,
  started_at IS NOT NULL AS started,finished_at IS NOT NULL AS finished,rolled_back_at IS NOT NULL AS rolled_back,
  (finished_at IS NULL OR finished_at>=started_at) AND (rolled_back_at IS NULL OR rolled_back_at>=started_at) AS time_order_valid,
  applied_steps_count AS steps,CASE WHEN logs IS NULL THEN 'NULL' WHEN logs='' THEN 'EMPTY' ELSE 'NONEMPTY' END AS logs_state
 FROM ONLY public._prisma_migrations
)
SELECT jsonb_build_object(
 'format','workinants.prisma-ledger-native.v1','server_version_num',current_setting('server_version_num')::integer,
 'database',current_database(),'read_only',current_setting('transaction_read_only')='on',
 'isolation',current_setting('transaction_isolation'),'collected_as',current_user,'session_user',session_user,
 'collector_is_superuser',(SELECT rolsuper FROM pg_roles WHERE rolname=current_user),
 'relations',COALESCE((SELECT jsonb_agg(jsonb_build_object('object','public._prisma_migrations',
  'kind',relkind,'owner',pg_get_userbyid(relowner),'persistence',relpersistence,'access_method',amname,
  'rls',relrowsecurity,'force_rls',relforcerowsecurity,'replica_identity',relreplident,
  'no_options',reloptions IS NULL,'default_tablespace',reltablespace=0,'not_partition',NOT relispartition,
  'no_inheritance',NOT EXISTS(SELECT 1 FROM pg_inherits i WHERE i.inhrelid=ledger.oid OR i.inhparent=ledger.oid))) FROM ledger),'[]'),
 'columns',COALESCE((SELECT jsonb_agg(to_jsonb(c) ORDER BY ordinal) FROM column_rows c),'[]'),
 'constraints',COALESCE((SELECT jsonb_agg(to_jsonb(c) ORDER BY name) FROM constraint_rows c),'[]'),
 'indexes',COALESCE((SELECT jsonb_agg(to_jsonb(i) ORDER BY object) FROM index_rows i),'[]'),
 'table_acl',COALESCE((SELECT jsonb_agg(to_jsonb(a) ORDER BY grantee,grantor,privilege,grant_option) FROM table_acl_rows a),'[]'),
 'column_acl',COALESCE((SELECT jsonb_agg(to_jsonb(a) ORDER BY a.column,a.grantee,a.grantor,a.privilege,a.grant_option) FROM column_acl_rows a),'[]'),
 'triggers_count',(SELECT count(*) FROM pg_trigger t JOIN ledger l ON l.oid=t.tgrelid),
 'policies_count',(SELECT count(*) FROM pg_policy p JOIN ledger l ON l.oid=p.polrelid),
 'rules_count',(SELECT count(*) FROM pg_rewrite r JOIN ledger l ON l.oid=r.ev_class),
 'history',COALESCE((SELECT jsonb_agg(to_jsonb(h) ORDER BY name_sha256,checksum_sha256,finished,rolled_back,steps,logs_state) FROM safe_history_rows h),'[]'),
 'history_ids_unique',(SELECT count(*)=count(DISTINCT id) FROM ONLY public._prisma_migrations)
);
COMMIT;
