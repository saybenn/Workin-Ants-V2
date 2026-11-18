-- P0C-CATALOG-01 collector SOURCE ONLY until independently reviewed for a run.
-- PostgreSQL 17. No application rows, ledger rows, passwords, raw SQL/function
-- bodies, backend handles or unrestricted diagnostics are selected.
-- Output one JSON value with psql --no-psqlrc --quiet --tuples-only --no-align.
-- Expressions/definitions are SHA-256 only. A hash mismatch that cannot be
-- resolved from approved source remains INCOMPLETE, never assumed equivalent.
BEGIN READ ONLY;
SET LOCAL search_path = pg_catalog;
WITH
namespaces AS (
 SELECT oid,nspname,nspowner,nspacl FROM pg_namespace
 WHERE nspname IN ('app','platform','platform_private')
),
wa_roles AS (SELECT * FROM pg_roles WHERE left(rolname,3)='wa_'),
-- Exact REL_17_11 bootstrap pg_proc identities; no runtime OIDs are exported.
release_trigger_functions(name,oid) AS (VALUES
 ('unique_key_recheck',1250::oid),('RI_FKey_check_ins',1644::oid),('RI_FKey_check_upd',1645::oid),
 ('RI_FKey_cascade_del',1646::oid),('RI_FKey_cascade_upd',1647::oid),
 ('RI_FKey_restrict_del',1648::oid),('RI_FKey_restrict_upd',1649::oid),
 ('RI_FKey_setnull_del',1650::oid),('RI_FKey_setnull_upd',1651::oid),
 ('RI_FKey_setdefault_del',1652::oid),('RI_FKey_setdefault_upd',1653::oid),
 ('RI_FKey_noaction_del',1654::oid),('RI_FKey_noaction_upd',1655::oid)),
type_names AS (
 SELECT n.nspname||'.'||t.typname AS object,
  CASE WHEN t.typcategory='A' AND t.typelem<>0
   THEN en.nspname||'.'||e.typname||'[]' ELSE n.nspname||'.'||t.typname END AS identity,
  t.*,n.nspname
 FROM pg_type t JOIN pg_namespace n ON n.oid=t.typnamespace
 LEFT JOIN pg_type e ON e.oid=t.typelem
 LEFT JOIN pg_namespace en ON en.oid=e.typnamespace
),
relations AS (
 SELECT c.*,n.nspname,n.nspname||'.'||c.relname AS object
 FROM pg_class c JOIN namespaces n ON n.oid=c.relnamespace
 WHERE c.relkind IN ('r','p','v','m','S','f')
),
functions AS (
 SELECT p.*,n.nspname,n.nspname||'.'||p.proname AS object,
  n.nspname||'.'||p.proname||'('||COALESCE((
   SELECT string_agg(t.identity,',' ORDER BY a.ordinality)
   FROM unnest(p.proargtypes::oid[]) WITH ORDINALITY a(type_oid,ordinality)
   JOIN type_names t ON t.oid=a.type_oid),'')||')' AS identity
 FROM pg_proc p JOIN namespaces n ON n.oid=p.pronamespace
),
columns AS (
 SELECT r.object AS table_name,a.attname AS name,a.attnum AS ordinal,
  t.identity AS type,a.atttypmod AS typmod,a.attndims AS array_dimensions,
  NOT a.attnotnull AS nullable,a.attidentity AS identity,a.attgenerated AS generated,
  a.attcollation=t.typcollation AS collation_is_type_default,
  a.attstorage=t.typstorage AS storage_is_type_default,a.attcompression AS compression,
  a.attislocal AS is_local,a.attinhcount AS inherited_count,
  CASE WHEN d.adbin IS NOT NULL THEN encode(sha256(convert_to(pg_get_expr(d.adbin,d.adrelid,false),'UTF8')),'hex') END AS default_sha256
 FROM relations r JOIN pg_attribute a ON a.attrelid=r.oid
 JOIN type_names t ON t.oid=a.atttypid
 LEFT JOIN pg_attrdef d ON d.adrelid=a.attrelid AND d.adnum=a.attnum
 WHERE a.attnum>0 AND NOT a.attisdropped
),
constraints AS (
 SELECT r.object AS table_name,c.conname AS name,c.contype AS kind,
  c.condeferrable AS deferrable,c.condeferred AS initially_deferred,
  c.convalidated AS validated,c.connoinherit AS no_inherit,
  COALESCE((SELECT jsonb_agg(a.attname ORDER BY k.ordinality)
   FROM unnest(c.conkey) WITH ORDINALITY k(attnum,ordinality)
   JOIN pg_attribute a ON a.attrelid=c.conrelid AND a.attnum=k.attnum),'[]') AS columns,
  CASE WHEN c.confrelid<>0 THEN pn.nspname||'.'||pc.relname END AS references,
  COALESCE((SELECT jsonb_agg(a.attname ORDER BY k.ordinality)
   FROM unnest(c.confkey) WITH ORDINALITY k(attnum,ordinality)
   JOIN pg_attribute a ON a.attrelid=c.confrelid AND a.attnum=k.attnum),'[]') AS referenced_columns,
  c.confmatchtype AS match,c.confupdtype AS update_action,c.confdeltype AS delete_action,
  CASE WHEN c.conbin IS NOT NULL THEN encode(sha256(convert_to(pg_get_expr(c.conbin,c.conrelid,false),'UTF8')),'hex') END AS expression_sha256,
  encode(sha256(convert_to(pg_get_constraintdef(c.oid,false),'UTF8')),'hex') AS definition_sha256,
  c.conindid<>0 AS has_index,
  CASE WHEN c.contype='f' AND c.conindid<>0 THEN ins.nspname||'.'||ic.relname END AS referenced_unique_index,
  CASE WHEN ic.oid IS NOT NULL AND c.contype IN ('p','u','x') THEN ins.nspname||'.'||ic.relname END AS index_name
 FROM pg_constraint c JOIN relations r ON r.oid=c.conrelid
 LEFT JOIN pg_class pc ON pc.oid=c.confrelid LEFT JOIN pg_namespace pn ON pn.oid=pc.relnamespace
 LEFT JOIN pg_class ic ON ic.oid=c.conindid LEFT JOIN pg_namespace ins ON ins.oid=ic.relnamespace
),
indexes AS (
 SELECT ns.nspname||'.'||ic.relname AS object,r.object AS table_name,
  pg_get_userbyid(ic.relowner) AS owner,am.amname AS access_method,
  i.indisunique AS unique,i.indisprimary AS primary,i.indisvalid AS valid,
  i.indisready AS ready,i.indislive AS live,i.indimmediate AS immediate,
  i.indisclustered AS clustered,i.indisreplident AS replica_identity,
  i.indnullsnotdistinct AS nulls_not_distinct,i.indnkeyatts AS key_count,
  COALESCE((SELECT jsonb_agg(jsonb_build_object(
   'position',k.ordinality,'column',a.attname,'included',k.ordinality>i.indnkeyatts,
   'expression_sha256',CASE WHEN k.attnum=0 THEN encode(sha256(convert_to(pg_get_indexdef(i.indexrelid,k.ordinality::integer,false),'UTF8')),'hex') END,
   'opclass',onsp.nspname||'.'||opc.opcname,'opclass_default',opc.opcdefault,
   'collation_is_type_default',co.colloid IS NOT DISTINCT FROM a.attcollation,
   'descending',(opt.option_value::integer & 1)=1,
   'nulls_first',(opt.option_value::integer & 2)=2) ORDER BY k.ordinality)
   FROM unnest(i.indkey::smallint[]) WITH ORDINALITY k(attnum,ordinality)
   LEFT JOIN pg_attribute a ON a.attrelid=i.indrelid AND a.attnum=k.attnum
   LEFT JOIN LATERAL unnest(i.indclass::oid[]) WITH ORDINALITY op(opclass_oid,ordinality) ON op.ordinality=k.ordinality
   LEFT JOIN pg_opclass opc ON opc.oid=op.opclass_oid LEFT JOIN pg_namespace onsp ON onsp.oid=opc.opcnamespace
   LEFT JOIN LATERAL unnest(i.indcollation::oid[]) WITH ORDINALITY co(colloid,ordinality) ON co.ordinality=k.ordinality
   LEFT JOIN LATERAL unnest(i.indoption::smallint[]) WITH ORDINALITY opt(option_value,ordinality) ON opt.ordinality=k.ordinality),'[]') AS keys,
  CASE WHEN i.indpred IS NOT NULL THEN encode(sha256(convert_to(pg_get_expr(i.indpred,i.indrelid,false),'UTF8')),'hex') END AS predicate_sha256,
  encode(sha256(convert_to(pg_get_indexdef(i.indexrelid),'UTF8')),'hex') AS definition_sha256
 FROM pg_index i JOIN relations r ON r.oid=i.indrelid
 JOIN pg_class ic ON ic.oid=i.indexrelid JOIN pg_namespace ns ON ns.oid=ic.relnamespace
 JOIN pg_am am ON am.oid=ic.relam
),
function_rows AS (
 SELECT f.identity AS object,f.object AS name,pg_get_userbyid(f.proowner) AS owner,
  l.lanname AS language,rt.identity AS return_type,f.proretset AS returns_set,
  f.prosecdef AS security_definer,f.proisstrict AS strict,f.proleakproof AS leakproof,
  f.provolatile AS volatility,f.proparallel AS parallel,f.prokind AS kind,
  f.procost AS cost,f.prorows AS rows,COALESCE(to_jsonb(f.proconfig),'[]') AS settings,
  f.provariadic<>0 AS variadic,f.prosupport<>0 AS support_function,
  f.pronargdefaults AS default_count,
  CASE WHEN f.proargdefaults IS NOT NULL THEN encode(sha256(convert_to(pg_get_expr(f.proargdefaults,0,false),'UTF8')),'hex') END AS defaults_sha256,
  encode(sha256(convert_to(f.prosrc,'UTF8')),'hex') AS body_sha256,
  COALESCE((SELECT jsonb_agg(jsonb_build_object('name',f.proargnames[a.ordinality],
   'mode',COALESCE(f.proargmodes[a.ordinality],'i'::"char"),'type',t.identity) ORDER BY a.ordinality)
   FROM unnest(COALESCE(f.proallargtypes,f.proargtypes::oid[])) WITH ORDINALITY a(type_oid,ordinality)
   JOIN type_names t ON t.oid=a.type_oid),'[]') AS parameters
 FROM functions f JOIN pg_language l ON l.oid=f.prolang JOIN type_names rt ON rt.oid=f.prorettype
),
trigger_dependency_edges AS (
 SELECT t.oid AS trigger_oid,'trigger_to'::text AS direction,d.refclassid AS target_class,d.refobjid AS target_oid,
  d.deptype,d.objsubid,d.refobjsubid
 FROM pg_trigger t JOIN relations r ON r.oid=t.tgrelid
 JOIN pg_depend d ON d.classid='pg_trigger'::regclass AND d.objid=t.oid
 UNION ALL
 SELECT t.oid,'to_trigger',d.classid,d.objid,d.deptype,d.objsubid,d.refobjsubid
 FROM pg_trigger t JOIN relations r ON r.oid=t.tgrelid
 JOIN pg_depend d ON d.refclassid='pg_trigger'::regclass AND d.refobjid=t.oid
),
trigger_dependency_rows AS (
 SELECT e.trigger_oid,jsonb_agg(jsonb_build_object('direction',e.direction,
  'class',CASE e.target_class WHEN 'pg_proc'::regclass THEN 'function' WHEN 'pg_class'::regclass THEN 'relation'
   WHEN 'pg_constraint'::regclass THEN 'constraint' ELSE 'unsupported' END,
  'object',CASE e.target_class
   WHEN 'pg_proc'::regclass THEN pn.nspname||'.'||p.proname||'('||COALESCE((
    SELECT string_agg(t.identity,',' ORDER BY a.ordinality) FROM unnest(p.proargtypes::oid[]) WITH ORDINALITY a(type_oid,ordinality)
    JOIN type_names t ON t.oid=a.type_oid),'')||')'
   WHEN 'pg_class'::regclass THEN rn.nspname||'.'||rc.relname
   WHEN 'pg_constraint'::regclass THEN cn.nspname||'.'||cr.relname||'/'||c.conname ELSE NULL END,
  'dependency_type',e.deptype,'object_subid',e.objsubid,'referenced_subid',e.refobjsubid)
  ORDER BY e.direction,e.target_class,e.target_oid,e.deptype,e.objsubid,e.refobjsubid) AS dependencies
 FROM trigger_dependency_edges e
 LEFT JOIN pg_proc p ON e.target_class='pg_proc'::regclass AND p.oid=e.target_oid LEFT JOIN pg_namespace pn ON pn.oid=p.pronamespace
 LEFT JOIN pg_class rc ON e.target_class='pg_class'::regclass AND rc.oid=e.target_oid LEFT JOIN pg_namespace rn ON rn.oid=rc.relnamespace
 LEFT JOIN pg_constraint c ON e.target_class='pg_constraint'::regclass AND c.oid=e.target_oid
 LEFT JOIN pg_class cr ON cr.oid=c.conrelid LEFT JOIN pg_namespace cn ON cn.oid=cr.relnamespace
 GROUP BY e.trigger_oid
),
trigger_rows AS (
 SELECT r.object AS table_name,t.tgname AS name,t.tgisinternal AS internal,
  t.tgtype AS type_bits,t.tgenabled AS enabled,t.tgconstraint<>0 AS constraint,
  t.tgdeferrable AS deferrable,t.tginitdeferred AS initially_deferred,
  fn.nspname||'.'||p.proname AS function,
  fn.nspname||'.'||p.proname||'('||COALESCE((SELECT string_agg(ty.identity,',' ORDER BY a.ordinality)
   FROM unnest(p.proargtypes::oid[]) WITH ORDINALITY a(type_oid,ordinality) JOIN type_names ty ON ty.oid=a.type_oid),'')||')' AS function_identity,
  EXISTS(SELECT 1 FROM release_trigger_functions b WHERE b.oid=p.oid AND b.name=p.proname
   AND fn.nspname='pg_catalog' AND p.pronargs=0 AND p.prokind='f' AND p.prorettype='trigger'::regtype
   AND p.prolang=(SELECT oid FROM pg_language WHERE lanname='internal') AND p.prosrc=p.proname) AS function_release_builtin,
  t.tgnargs AS argument_count,
  encode(sha256(t.tgargs),'hex') AS arguments_sha256,
  CASE WHEN t.tgqual IS NOT NULL THEN encode(sha256(convert_to(pg_get_expr(t.tgqual,t.tgrelid,false),'UTF8')),'hex') END AS when_sha256,
  c.conname AS constraint_name,
  CASE WHEN cr.oid IS NOT NULL THEN cn.nspname||'.'||cr.relname END AS constraint_table,
  t.tgconstrrelid<>0 AS has_constraint_relation,
  CASE WHEN t.tgconstrrelid<>0 THEN rrn.nspname||'.'||rr.relname END AS referenced_table,
  t.tgconstrindid<>0 AS has_constraint_index,
  CASE WHEN t.tgconstrindid<>0 THEN rin.nspname||'.'||ri.relname END AS constraint_index,
  COALESCE(dep.dependencies,'[]'::jsonb) AS dependencies
 FROM pg_trigger t JOIN relations r ON r.oid=t.tgrelid
 JOIN pg_proc p ON p.oid=t.tgfoid JOIN pg_namespace fn ON fn.oid=p.pronamespace
 LEFT JOIN pg_constraint c ON c.oid=t.tgconstraint
 LEFT JOIN pg_class cr ON cr.oid=c.conrelid LEFT JOIN pg_namespace cn ON cn.oid=cr.relnamespace
 LEFT JOIN pg_class rr ON rr.oid=t.tgconstrrelid LEFT JOIN pg_namespace rrn ON rrn.oid=rr.relnamespace
 LEFT JOIN pg_class ri ON ri.oid=t.tgconstrindid LEFT JOIN pg_namespace rin ON rin.oid=ri.relnamespace
 LEFT JOIN trigger_dependency_rows dep ON dep.trigger_oid=t.oid
),
policy_rows AS (
 SELECT r.object AS table_name,p.polname AS name,p.polcmd AS command,p.polpermissive AS permissive,
  (SELECT jsonb_agg(CASE WHEN x=0 THEN 'PUBLIC' ELSE pg_get_userbyid(x) END ORDER BY x)
   FROM unnest(p.polroles) x) AS roles,
  CASE WHEN p.polqual IS NOT NULL THEN encode(sha256(convert_to(pg_get_expr(p.polqual,p.polrelid,false),'UTF8')),'hex') END AS using_sha256,
  CASE WHEN p.polwithcheck IS NOT NULL THEN encode(sha256(convert_to(pg_get_expr(p.polwithcheck,p.polrelid,false),'UTF8')),'hex') END AS with_check_sha256
 FROM pg_policy p JOIN relations r ON r.oid=p.polrelid
),
acl_objects AS (
 SELECT 'SCHEMA'::text AS kind,n.nspname::text AS object,n.nspowner AS owner,NULL::text AS column,
  COALESCE(n.nspacl,acldefault('n',n.nspowner)) AS acl FROM namespaces n
 UNION ALL SELECT CASE WHEN r.relkind='S' THEN 'SEQUENCE' ELSE 'TABLE' END,r.object,r.relowner,NULL,
  COALESCE(r.relacl,acldefault(CASE WHEN r.relkind='S' THEN 's'::"char" ELSE 'r'::"char" END,r.relowner)) FROM relations r
 UNION ALL SELECT 'TABLE',r.object,r.relowner,a.attname,a.attacl FROM relations r
  JOIN pg_attribute a ON a.attrelid=r.oid WHERE a.attnum>0 AND NOT a.attisdropped AND a.attacl IS NOT NULL
 UNION ALL SELECT 'FUNCTION',f.identity,f.proowner,NULL,COALESCE(f.proacl,acldefault('f',f.proowner)) FROM functions f
 UNION ALL SELECT 'TYPE',t.object,t.typowner,NULL,COALESCE(t.typacl,acldefault('T',t.typowner)) FROM type_names t
  JOIN namespaces n ON n.oid=t.typnamespace WHERE t.typtype='e'
),
acl_rows AS (
 SELECT o.kind,o.object,o.column,CASE WHEN a.grantee=0 THEN 'PUBLIC' ELSE pg_get_userbyid(a.grantee) END AS grantee,
  pg_get_userbyid(a.grantor) AS grantor,a.privilege_type AS privilege,a.is_grantable AS grant_option
 FROM acl_objects o CROSS JOIN LATERAL aclexplode(o.acl) a WHERE a.grantee<>o.owner
),
owner_acl_rows AS (
 SELECT o.kind,o.object,o.column,pg_get_userbyid(a.grantee) AS grantee,
  pg_get_userbyid(a.grantor) AS grantor,a.privilege_type AS privilege,a.is_grantable AS grant_option
 FROM acl_objects o CROSS JOIN LATERAL aclexplode(o.acl) a WHERE a.grantee=o.owner
),
generated_type_acl AS (
 SELECT t.object,CASE WHEN a.grantee=0 THEN 'PUBLIC' ELSE pg_get_userbyid(a.grantee) END AS grantee,
  pg_get_userbyid(a.grantor) AS grantor,a.privilege_type AS privilege,a.is_grantable AS grant_option
 FROM type_names t JOIN namespaces n ON n.oid=t.typnamespace
 CROSS JOIN LATERAL aclexplode(COALESCE(t.typacl,acldefault('T',t.typowner))) a
 WHERE t.typtype<>'e'
),
default_slots AS (
 SELECT r.oid AS creator_oid,r.rolname AS creator,s.schema,k.kind,k.code,
  CASE WHEN s.schema='*' THEN COALESCE(d.defaclacl,acldefault(CASE WHEN k.code='S' THEN 's'::"char" ELSE k.code END,r.oid)) ELSE d.defaclacl END AS acl
 FROM wa_roles r CROSS JOIN (VALUES ('*'),('app'),('platform'),('platform_private')) s(schema)
 CROSS JOIN (VALUES ('TABLE','r'::"char"),('SEQUENCE','S'::"char"),('FUNCTION','f'::"char"),('TYPE','T'::"char"),('SCHEMA','n'::"char")) k(kind,code)
 LEFT JOIN pg_namespace n ON n.nspname=s.schema
 LEFT JOIN pg_default_acl d ON d.defaclrole=r.oid AND d.defaclobjtype=k.code
  AND d.defaclnamespace=CASE WHEN s.schema='*' THEN 0 ELSE n.oid END
 WHERE k.kind<>'SCHEMA' OR s.schema='*'
),
default_rows AS (
 SELECT d.creator,d.schema,d.kind,COALESCE((SELECT jsonb_agg(jsonb_build_object(
  'grantee',CASE WHEN a.grantee=0 THEN 'PUBLIC' ELSE pg_get_userbyid(a.grantee) END,
  'grantor',pg_get_userbyid(a.grantor),'privilege',a.privilege_type,'grant_option',a.is_grantable)
  ORDER BY a.grantee,a.privilege_type,a.grantor) FROM aclexplode(CASE WHEN cardinality(d.acl)>0 THEN d.acl ELSE NULL::aclitem[] END) a WHERE a.grantee<>d.creator_oid),'[]') AS entries
 FROM default_slots d
)
SELECT jsonb_build_object(
 'format','workinants.native-catalog.v1','server_version_num',current_setting('server_version_num')::integer,
 'read_only',current_setting('transaction_read_only')='on','collected_as',current_user,
 'collector_is_superuser',(SELECT rolsuper FROM pg_roles WHERE rolname=current_user),
 'public_schema_owner',(SELECT pg_get_userbyid(nspowner) FROM pg_namespace WHERE nspname='public'),
 'schemas',COALESCE((SELECT jsonb_agg(jsonb_build_object('object',nspname,'owner',pg_get_userbyid(nspowner)) ORDER BY nspname) FROM namespaces),'[]'),
 'roles',COALESCE((SELECT jsonb_agg(jsonb_build_object('name',rolname,'rolsuper',rolsuper,'rolinherit',rolinherit,'rolcreaterole',rolcreaterole,
  'rolcreatedb',rolcreatedb,'rolcanlogin',rolcanlogin,'rolreplication',rolreplication,'rolbypassrls',rolbypassrls,
  'rolconnlimit',rolconnlimit,'rolvaliduntil',rolvaliduntil,'rolconfig',rolconfig) ORDER BY rolname) FROM wa_roles),'[]'),
 'memberships',COALESCE((SELECT jsonb_agg(jsonb_build_object('role',pg_get_userbyid(m.roleid),'member',pg_get_userbyid(m.member),
  'grantor',pg_get_userbyid(m.grantor),'admin',m.admin_option,'inherit',m.inherit_option,'set',m.set_option) ORDER BY m.roleid,m.member,m.grantor)
  FROM pg_auth_members m WHERE m.roleid IN (SELECT oid FROM wa_roles) OR m.member IN (SELECT oid FROM wa_roles)),'[]'),
 'relations',COALESCE((SELECT jsonb_agg(jsonb_build_object('object',object,'kind',relkind,'owner',pg_get_userbyid(relowner),
  'persistence',relpersistence,'rls',relrowsecurity,'force_rls',relforcerowsecurity,'replica_identity',relreplident) ORDER BY object) FROM relations),'[]'),
 'columns',COALESCE((SELECT jsonb_agg(to_jsonb(c) ORDER BY table_name,ordinal) FROM columns c),'[]'),
 'types',COALESCE((SELECT jsonb_agg(jsonb_build_object('object',t.object,'owner',pg_get_userbyid(t.typowner),'kind',t.typtype,
  'category',t.typcategory,'element',e.object,'relation',CASE WHEN c.oid IS NOT NULL THEN n.nspname||'.'||c.relname END) ORDER BY t.object)
  FROM type_names t JOIN namespaces ns ON ns.oid=t.typnamespace LEFT JOIN type_names e ON e.oid=t.typelem
  LEFT JOIN pg_class c ON c.oid=t.typrelid LEFT JOIN pg_namespace n ON n.oid=c.relnamespace),'[]'),
 'enums',COALESCE((SELECT jsonb_agg(jsonb_build_object('object',t.object,'owner',pg_get_userbyid(t.typowner),
  'labels',(SELECT jsonb_agg(e.enumlabel ORDER BY e.enumsortorder) FROM pg_enum e WHERE e.enumtypid=t.oid)) ORDER BY t.object)
  FROM type_names t JOIN namespaces n ON n.oid=t.typnamespace WHERE t.typtype='e'),'[]'),
 'constraints',COALESCE((SELECT jsonb_agg(to_jsonb(c) ORDER BY table_name,name) FROM constraints c),'[]'),
 'indexes',COALESCE((SELECT jsonb_agg(to_jsonb(i) ORDER BY object) FROM indexes i),'[]'),
 'functions',COALESCE((SELECT jsonb_agg(to_jsonb(f) ORDER BY object) FROM function_rows f),'[]'),
 'triggers',COALESCE((SELECT jsonb_agg(to_jsonb(t) ORDER BY table_name,name) FROM trigger_rows t),'[]'),
 'policies',COALESCE((SELECT jsonb_agg(to_jsonb(p) ORDER BY table_name,name) FROM policy_rows p),'[]'),
 'nonowner_acl',COALESCE((SELECT jsonb_agg(to_jsonb(a) ORDER BY a.kind,a.object,a.grantee,a.privilege,a.column) FROM acl_rows a),'[]'),
 'owner_acl',COALESCE((SELECT jsonb_agg(to_jsonb(a) ORDER BY a.kind,a.object,a.privilege,a.column) FROM owner_acl_rows a),'[]'),
 'generated_type_acl',COALESCE((SELECT jsonb_agg(to_jsonb(a) ORDER BY a.object,a.grantee,a.privilege) FROM generated_type_acl a),'[]'),
 'default_acl',COALESCE((SELECT jsonb_agg(to_jsonb(d) ORDER BY creator,schema,kind) FROM default_rows d),'[]'),
 'default_acl_outside_registered_schemas',COALESCE((SELECT jsonb_agg(jsonb_build_object('creator',pg_get_userbyid(d.defaclrole),'schema',n.nspname,'kind',d.defaclobjtype)
  ORDER BY d.defaclrole,d.defaclnamespace,d.defaclobjtype) FROM pg_default_acl d JOIN pg_namespace n ON n.oid=d.defaclnamespace
  WHERE d.defaclrole IN (SELECT oid FROM wa_roles) AND n.nspname NOT IN ('app','platform','platform_private')),'[]'),
 'extensions',COALESCE((SELECT jsonb_agg(jsonb_build_object('name',e.extname,'version',e.extversion,'schema',n.nspname,'owner',pg_get_userbyid(e.extowner)) ORDER BY e.extname)
  FROM pg_extension e JOIN pg_namespace n ON n.oid=e.extnamespace),'[]'),
 'public_owned_relations',COALESCE((SELECT jsonb_agg(jsonb_build_object('object','public.'||c.relname,'kind',c.relkind,'owner',pg_get_userbyid(c.relowner),
  'rls',c.relrowsecurity,'force_rls',c.relforcerowsecurity,
  'nonowner_acl',COALESCE((SELECT jsonb_agg(jsonb_build_object('grantee',CASE WHEN a.grantee=0 THEN 'PUBLIC' ELSE pg_get_userbyid(a.grantee) END,
   'grantor',pg_get_userbyid(a.grantor),'privilege',a.privilege_type,'grant_option',a.is_grantable))
   FROM aclexplode(COALESCE(c.relacl,acldefault('r',c.relowner))) a WHERE a.grantee<>c.relowner),'[]')) ORDER BY c.relname)
  FROM pg_class c JOIN pg_namespace n ON n.oid=c.relnamespace
  WHERE n.nspname='public' AND c.relkind IN ('r','p','v','m','S','f')),'[]'),
 'public_schema_acl',COALESCE((SELECT jsonb_agg(jsonb_build_object(
  'grantee',CASE WHEN a.grantee=0 THEN 'PUBLIC' ELSE pg_get_userbyid(a.grantee) END,
  'grantor',pg_get_userbyid(a.grantor),'privilege',a.privilege_type,'grant_option',a.is_grantable)
  ORDER BY a.grantee,a.privilege_type,a.grantor)
  FROM pg_namespace n CROSS JOIN LATERAL aclexplode(COALESCE(n.nspacl,acldefault('n',n.nspowner))) a
  WHERE n.nspname='public'),'[]'),
 'public_wa_schema_acl',COALESCE((SELECT jsonb_agg(jsonb_build_object('grantee',pg_get_userbyid(a.grantee),'grantor',pg_get_userbyid(a.grantor),
  'privilege',a.privilege_type,'grant_option',a.is_grantable) ORDER BY a.grantee,a.privilege_type)
  FROM pg_namespace n CROSS JOIN LATERAL aclexplode(COALESCE(n.nspacl,acldefault('n',n.nspowner))) a
  WHERE n.nspname='public' AND a.grantee IN (SELECT oid FROM wa_roles)),'[]')
);
COMMIT;
