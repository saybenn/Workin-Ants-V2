"""Assemble authorized review SQL only; no database libraries, subprocesses or network."""
from pathlib import Path
import json,re,runpy,hashlib,shutil
R=Path(__file__).resolve().parents[1]
O=R/'review-output'; C=R/'context/reconciliation'
def read(p): return (R/p).read_text(encoding='utf8')
def write(p,s): (R/p).parent.mkdir(parents=True,exist_ok=True); (R/p).write_text(s,encoding='utf8',newline='\n')
def dump(p,x): write(p,json.dumps(x,indent=2,ensure_ascii=False)+'\n')
def sha(p): return hashlib.sha256((R/p).read_bytes()).hexdigest()
def q(x): return '"'+x.replace('"','""')+'"'
def lit(x): return "'"+str(x).replace("'","''")+"'"
def arr(xs): return 'ARRAY['+','.join(map(lit,xs))+']::text[]'
P=runpy.run_path(str(R/'scripts/prepare-database-candidate.py'))
blocks=P['parse'](read('prisma/review/foundation-candidate.prisma'))
A=json.loads(read('context/reconciliation/database-candidate-access-matrix.json'))
models={}
for name,b in blocks.items():
 if b['kind']!='model':continue
 fs=[f for f in P['fields'](b['body']) if f['type'].rstrip('?[]') not in blocks or blocks[f['type'].rstrip('?[]')]['kind']=='enum']
 cols={f['name']:(re.search(r'@map\("([^"]+)"\)',f['attributes']).group(1) if '@map(' in f['attributes'] else f['name']) for f in fs}
 row=next(x for x in A['objects'] if x.get('model')==name and x['kind']=='table')
 models[name]={'fields':fs,'columns':cols,'object':row['object'],'owner':row['business_owner'],'access':row,'pk':['userId','role'] if name=='UserRole' else ['id']}
assert len(models)==40
def obj(n):return '.'.join(map(q,models[n]['object'].split('.')))
def col(n,f):return q(models[n]['columns'][f])
def key(n,row):return " || ':' || ".join(f"({row}->>{lit(models[n]['columns'][f])})" for f in models[n]['pk'])
raw=read('review-output/foundation-structure.sql')
# P0-C-03A explicitly authorizes nullable first-write predecessor and two CAS
# columns. Fresh raw SQL must match that revised source; fingerprints are checked
# independently in the drafting validator, not frozen to superseded source bytes.
assert sha('prisma.foundation-review.config.ts')=='ad7578e0d4c3a6fa5d350c7193a3ebc7909ba31677321e6f6095b192fa533117'
assert len(re.findall(r'CREATE TABLE ',raw))==40

bootstrap='''-- P0-C-03 REVIEW DRAFT ONLY. NOT EXECUTION-APPROVED. PostgreSQL 17.
-- Separate environment authority must run any future bootstrap; no credentials here.
-- Deliberately not idempotent: existing roles/namespaces require inspection, not takeover.
BEGIN;
CREATE ROLE wa_schema_owner NOLOGIN NOINHERIT NOBYPASSRLS NOSUPERUSER NOCREATEDB NOCREATEROLE NOREPLICATION;
CREATE ROLE wa_migrator LOGIN NOINHERIT NOBYPASSRLS NOSUPERUSER NOCREATEDB NOCREATEROLE NOREPLICATION;
CREATE ROLE wa_context_issuer LOGIN NOINHERIT NOBYPASSRLS NOSUPERUSER NOCREATEDB NOCREATEROLE NOREPLICATION;
CREATE ROLE wa_app_runtime LOGIN NOINHERIT NOBYPASSRLS NOSUPERUSER NOCREATEDB NOCREATEROLE NOREPLICATION;
CREATE ROLE wa_worker LOGIN NOINHERIT NOBYPASSRLS NOSUPERUSER NOCREATEDB NOCREATEROLE NOREPLICATION;
CREATE ROLE wa_private_helper_owner NOLOGIN NOINHERIT NOBYPASSRLS NOSUPERUSER NOCREATEDB NOCREATEROLE NOREPLICATION;
CREATE ROLE wa_customer_verifier NOLOGIN NOINHERIT NOBYPASSRLS NOSUPERUSER NOCREATEDB NOCREATEROLE NOREPLICATION;
CREATE ROLE wa_track_verifier NOLOGIN NOINHERIT NOBYPASSRLS NOSUPERUSER NOCREATEDB NOCREATEROLE NOREPLICATION;
CREATE ROLE wa_identity_service_authority LOGIN NOINHERIT NOBYPASSRLS NOSUPERUSER NOCREATEDB NOCREATEROLE NOREPLICATION;
-- Privacy executor remains unprovisioned; support_operation is an action, not a role.
GRANT wa_schema_owner TO wa_migrator WITH ADMIN FALSE, INHERIT FALSE, SET TRUE;
-- Ownership transfers require temporary membership; app/worker receive none.
GRANT wa_private_helper_owner,wa_customer_verifier,wa_track_verifier TO wa_schema_owner WITH ADMIN FALSE, INHERIT FALSE, SET TRUE;
CREATE SCHEMA app AUTHORIZATION wa_schema_owner;
CREATE SCHEMA platform AUTHORIZATION wa_schema_owner;
CREATE SCHEMA platform_private AUTHORIZATION wa_schema_owner;
REVOKE ALL ON SCHEMA app,platform,platform_private FROM PUBLIC;
GRANT USAGE ON SCHEMA app,platform,platform_private TO wa_app_runtime,wa_worker;
GRANT USAGE ON SCHEMA app,platform,platform_private TO wa_context_issuer,wa_private_helper_owner;
GRANT USAGE ON SCHEMA app,platform,platform_private TO wa_customer_verifier,wa_track_verifier;
GRANT USAGE ON SCHEMA platform_private TO wa_identity_service_authority;
-- Prisma ledger exception: only migrator may create its private metadata in public.
-- No ledger is created and no migrate execution configuration is activated here.
GRANT USAGE,CREATE ON SCHEMA public TO wa_migrator;
ALTER DEFAULT PRIVILEGES FOR ROLE wa_migrator REVOKE ALL ON TABLES FROM PUBLIC;
ALTER DEFAULT PRIVILEGES FOR ROLE wa_schema_owner REVOKE EXECUTE ON FUNCTIONS FROM PUBLIC;
ALTER DEFAULT PRIVILEGES FOR ROLE wa_private_helper_owner REVOKE EXECUTE ON FUNCTIONS FROM PUBLIC;
ALTER DEFAULT PRIVILEGES FOR ROLE wa_customer_verifier REVOKE EXECUTE ON FUNCTIONS FROM PUBLIC;
ALTER DEFAULT PRIVILEGES FOR ROLE wa_track_verifier REVOKE EXECUTE ON FUNCTIONS FROM PUBLIC;
ALTER DEFAULT PRIVILEGES FOR ROLE wa_schema_owner REVOKE USAGE ON TYPES FROM PUBLIC;
ALTER DEFAULT PRIVILEGES FOR ROLE wa_schema_owner IN SCHEMA app,platform,platform_private REVOKE ALL ON TABLES FROM PUBLIC;
ALTER DEFAULT PRIVILEGES FOR ROLE wa_schema_owner IN SCHEMA app,platform,platform_private REVOKE ALL ON SEQUENCES FROM PUBLIC;
COMMIT;
'''
write('review-output/foundation-bootstrap.review.sql',bootstrap)
write('review-output/foundation-bootstrap-finalize.review.sql',read('scripts/sql-review/foundation-bootstrap-finalize.sql'))
sql=['''-- P0-C-03 REVIEW DRAFT ONLY. NOT EXECUTION-APPROVED. Posture D.
-- Future order: separate bootstrap, then one application migration transaction.
-- No migration directory/config/ledger is activated by these review artifacts.
BEGIN;
SET LOCAL ROLE wa_schema_owner;
SET LOCAL search_path = pg_catalog;
''',re.sub(r'-- CreateSchema\s+CREATE SCHEMA IF NOT EXISTS "(?:app|platform)";\s*','',raw)]
def emit(s):sql.append(s.strip()+'\n')
def fn(name,args,returns,body,lang='plpgsql',definer=False,vol='VOLATILE'):
 emit(f'CREATE FUNCTION platform_private.{name}({args}) RETURNS {returns}\nLANGUAGE {lang} {vol} SECURITY '+('DEFINER' if definer else 'INVOKER')+'\nSET search_path = pg_catalog\nAS $wa$\n'+body.strip()+'\n$wa$;')

# Literal schema compilation, no runtime schema registry or arbitrary JSON escape.
emit(read('scripts/sql-review/foundation-service-authority.sql'))
registry={}
for p in ['contracts/shared/types.v1.schema.json','contracts/shared/SH-004.v1.schema.json','contracts/shared/SH-114.v1.schema.json','contracts/database-review/foundation-payloads.v1.schema.json','contracts/database-review/owner-mutation-evidence.v1.schema.json']:
 j=json.loads(read(p));registry[p]=j;registry[j['$id']]=j
def expr(s,v,root,depth=0):
 assert depth<30
 if '$ref' in s:
  url,_,fragment=s['$ref'].partition('#');d=registry[url] if url else root
  z=d
  for k in fragment.strip('/').split('/') if fragment else []:z=z[k]
  return expr(z,v,d,depth+1)
 if 'const' in s:return f'({v} = {lit(json.dumps(s["const"]))}::jsonb)'
 if 'enum' in s:return '('+' OR '.join(f'{v} = {lit(json.dumps(z))}::jsonb' for z in s['enum'])+')'
 if 'anyOf' in s or 'oneOf' in s:
  es=[expr(z,v,root,depth+1) for z in s.get('anyOf',s.get('oneOf'))]
  return '('+(' OR '.join(es) if 'anyOf' in s else ' + '.join(f'CASE WHEN COALESCE({e},false) THEN 1 ELSE 0 END' for e in es)+' = 1')+')'
 t=s.get('type'); nullable=isinstance(t,list) and 'null' in t
 if isinstance(t,list):t=next(z for z in t if z!='null')
 es=[f'jsonb_typeof({v}) = {lit("number" if t in ("integer","number") else t)}']
 if t=='object':
  assert s.get('additionalProperties') is False, s
  props=s.get('properties',{});required=s.get('required',[])
  es += [f'{v} ?& {arr(required)}',f'({v} - {arr(props)}) = \'{{}}\'::jsonb']
  for k,z in props.items():es.append(f'(NOT ({v} ? {lit(k)}) OR {expr(z,f"({v}->{lit(k)})",root,depth+1)})')
 elif t=='string':
  text=f'({v} #>> \'{{}}\')'
  if 'minLength' in s:es.append(f'length({text}) >= {s["minLength"]}')
  if 'maxLength' in s:es.append(f'length({text}) <= {s["maxLength"]}')
  if 'pattern' in s:es.append(f'{text} ~ {lit(s["pattern"])}')
  if s.get('format')=='uuid':es.append(f'{text} ~ \'^[0-9a-fA-F]{{8}}-[0-9a-fA-F]{{4}}-[0-9a-fA-F]{{4}}-[0-9a-fA-F]{{4}}-[0-9a-fA-F]{{12}}$\'')
  elif s.get('format')=='date-time':es.append(f'platform_private.json_datetime({text})')
  elif s.get('format'):raise ValueError(s)
 elif t in ('integer','number'):
  if t=='integer':es.append(f'({v} #>> \'{{}}\') ~ \'^-?[0-9]+$\'')
  for k,op in [('minimum','>='),('maximum','<=')]:
   if k in s:es.append(f'({v} #>> \'{{}}\')::numeric {op} {s[k]}')
 elif t not in ('null','boolean'):raise ValueError(s)
 z='('+' AND '.join(es)+')'
 return f'({v} = \'null\'::jsonb OR {z})' if nullable else z
fn('json_datetime','v text','boolean', '''BEGIN
 IF v IS NULL OR v !~ '^\\d{4}-\\d{2}-\\d{2}T\\d{2}:\\d{2}:\\d{2}(\\.\\d+)?(Z|[+-]\\d{2}:\\d{2})$' THEN RETURN false; END IF;
 PERFORM v::timestamptz; RETURN true;
 EXCEPTION WHEN invalid_datetime_format OR datetime_field_overflow THEN RETURN false;
END;''',vol='IMMUTABLE')
for n in models:
 root=registry['contracts/database-review/owner-mutation-evidence.v1.schema.json']
 fn('json_evidence_'+n.lower(),'v jsonb','boolean','SELECT COALESCE('+expr(root['$defs'][n],'v',root)+',false);','sql',vol='IMMUTABLE')
for n,path,definition in [('customer_event','contracts/shared/types.v1.schema.json','EventPayload_customer_lifecycle_changed_v1'),('track_command','contracts/database-review/foundation-payloads.v1.schema.json','assignDefaultFreeTrackCustomerCommand'),('track_result','contracts/database-review/foundation-payloads.v1.schema.json','assignDefaultFreeTrackCustomerResult'),('sh004_result','contracts/shared/SH-004.v1.schema.json','response'),('sh114_result','contracts/shared/SH-114.v1.schema.json','response')]:
 root=registry[path];fn('json_'+n,'v jsonb','boolean','SELECT COALESCE('+expr(root['$defs'][definition],'v',root)+',false);','sql',vol='IMMUTABLE')

emit('''-- SQL-01/02/06: only the issuer and SELECT-only private helper can read grants.
ALTER TABLE platform.database_action_grant ENABLE ROW LEVEL SECURITY;
ALTER TABLE platform.database_action_grant FORCE ROW LEVEL SECURITY;
GRANT SELECT,INSERT ON platform.database_action_grant TO wa_context_issuer;
GRANT UPDATE(revoked_at) ON platform.database_action_grant TO wa_context_issuer;
GRANT SELECT ON platform.database_action_grant TO wa_private_helper_owner;
CREATE POLICY grant_issuer_select ON platform.database_action_grant FOR SELECT TO wa_context_issuer USING (issuer_service = session_user::text);
CREATE POLICY grant_issuer_insert ON platform.database_action_grant FOR INSERT TO wa_context_issuer WITH CHECK (issuer_service = session_user::text);
CREATE POLICY grant_issuer_revoke ON platform.database_action_grant FOR UPDATE TO wa_context_issuer USING (issuer_service = session_user::text) WITH CHECK (issuer_service = session_user::text);
CREATE POLICY grant_helper_read ON platform.database_action_grant FOR SELECT TO wa_private_helper_owner USING (database_login_role = session_user::text AND backend_pid = pg_backend_pid() AND transaction_id = pg_current_xact_id()::text);
GRANT SELECT(user_id,security_generation) ON app.user_security_profiles TO wa_private_helper_owner;
CREATE POLICY security_helper_read ON app.user_security_profiles FOR SELECT TO wa_private_helper_owner USING (true);
-- Minimal Identity columns only; this nonrecursive leaf policy exposes no source body.
''')
fn('bound_grant','take_action_lock boolean DEFAULT true','platform.database_action_grant','''
DECLARE g platform.database_action_grant; handle text;
BEGIN
 IF current_setting('transaction_isolation') <> 'read committed' THEN RETURN NULL; END IF;
 handle := current_setting('wa.context_hash',true);
 IF handle IS NULL OR handle !~ '^[0-9a-f]{64}$' THEN RETURN NULL; END IF;
 IF take_action_lock THEN
  -- Bind takes no lock: a separately committed revocation can win before action.
  PERFORM pg_advisory_xact_lock_shared(hashtextextended('grant:'||handle,0));
 END IF;
 SELECT * INTO g FROM platform.database_action_grant WHERE token_hash=handle
  AND database_login_role=session_user::text AND backend_pid=pg_backend_pid()
  AND transaction_id=pg_current_xact_id()::text AND revoked_at IS NULL
  AND expires_at > clock_timestamp();
 IF NOT FOUND THEN RETURN NULL; END IF;
 IF g.principal_user_id IS NULL THEN
  IF take_action_lock THEN
   PERFORM pg_advisory_xact_lock_shared(hashtextextended('service:'||g.service_principal,0));
  END IF;
  IF NOT EXISTS (SELECT 1 FROM platform_private.identity_service_authorization a
   WHERE a.service_principal=g.service_principal AND a.security_generation=g.security_generation AND a.revoked_at IS NULL)
  THEN RETURN NULL; END IF;
  RETURN g;
 END IF;
 IF take_action_lock THEN
  PERFORM pg_advisory_xact_lock_shared(hashtextextended('identity:'||g.principal_user_id::text,0));
 END IF;
 IF NOT EXISTS (SELECT 1 FROM app.user_security_profiles s WHERE s.user_id=g.principal_user_id
  AND s.security_generation=g.security_generation) THEN RETURN NULL; END IF;
 RETURN g;
END;''',definer=True)
fn('bind_request_context','secret text','void','''
DECLARE g platform.database_action_grant;
BEGIN
 IF secret IS NULL OR secret !~ '^[0-9a-f]{64}$' THEN RAISE EXCEPTION 'invalid context' USING ERRCODE='42501'; END IF;
 PERFORM set_config('wa.context_hash',encode(sha256(decode(secret,'hex')),'hex'),true);
 g:=platform_private.bound_grant(false);
 IF g.id IS NULL THEN RAISE EXCEPTION 'invalid, stale or unsupported context' USING ERRCODE='42501'; END IF;
END;''',definer=True)
fn('context_allows','owner_id text, action_name text, target_kind text, target_id text, purpose_name text','boolean','''
DECLARE g platform.database_action_grant;
BEGIN
 g:=platform_private.bound_grant(true);
 RETURN COALESCE(g.id IS NOT NULL AND g.owner_module_id=owner_id AND g.action=action_name
  AND g.target_kind=target_kind AND g.target_id=target_id AND g.purpose=purpose_name,false);
END;''',definer=True)
scope_policy=json.loads(read('context/reconciliation/foundation-sql-scope-policy.json'))
scope_body=["DECLARE g platform.database_action_grant; BEGIN", "g:=platform_private.bound_grant(true); IF g.id IS NULL THEN RETURN false; END IF;",
 "IF model_name=g.target_kind AND row_key<>g.target_id THEN RETURN false; END IF;"]
for registration in scope_policy['domain_scopes']:
 owner,action,purpose,root_kind=[registration[k] for k in ['owner','action','purpose','root_kind']]
 children=" OR model_name='CustomerProfileLifecycleEvent'" if root_kind=='CustomerProfile' else ''
 # A Consent proof needs exact immutable presentation/content reads. Admission
 # stays SELECT-only and requires a root-to-child token in addition to the
 # ordinary per-row/column capabilities enforced by row_allowed.
 for model,relationship in registration.get('related_reads',{}).items():
  binding=f"{lit(root_kind+'/')}||g.target_id||{lit('/'+relationship+'/')}||row_key=ANY(g.allowed_fields)"
  children+=f" OR (verb='SELECT' AND model_name={lit(model)} AND {binding})"
 scope_body.append(f"IF verb=ANY({arr(registration['verbs'])}) AND (model_name={lit(root_kind)}{children} OR model_name IN ('OwnerMutationEvidence','RuntimeCommandReceipt','RuntimeOutboxMessage','RuntimeEffectReceipt')) AND platform_private.context_allows({lit(owner)},{lit(action)},{lit(root_kind)},g.target_id,{lit(purpose)}) THEN RETURN true; END IF;")
scope_body.append("IF model_name IN ('RuntimeWorkItem','RuntimeAttempt','RuntimeOutboxMessage','RuntimeCommandReceipt','RuntimeEffectReceipt','RuntimeInboxReceipt','OwnerMutationEvidence','TrackPlan','TrackEntitlementDefinition','TrackPlanEntitlement','TrackSubscription','TrackEntitlementGrant','TrackBaseSelection','TrackSubscriptionEvent','TrackEnrollmentReceipt') AND platform_private.context_allows('track_subscription_entitlement','assignDefaultFreeTrack.v1','RuntimeWorkItem',g.target_id,'default_free_enrollment') THEN RETURN true; END IF;")
for registration in scope_policy['runtime_work_scopes']:
 scope_body.append(f"IF model_name='RuntimeWorkItem' AND platform_private.context_allows({lit(registration['owner'])},{lit(registration['action'])},'RuntimeWorkItem',row_key,{lit(registration['purpose'])}) THEN RETURN true; END IF;")
scope_body.append("IF model_name IN ('RuntimeReservation','RuntimeEffectReceipt','RuntimeCommandReceipt') AND platform_private.context_allows(g.owner_module_id,'runtime.reservation.v1','RuntimeReservation',g.target_id,'reservation') THEN RETURN true; END IF;")
scope_body+=['RETURN false; END;']
fn('protected_scope','model_name text, row_key text, verb text','boolean','\n'.join(scope_body),definer=True)
fn('row_allowed','owner_id text, model_name text, row_key text, verb text, field_names text[], row_revision text DEFAULT NULL, row_transaction text DEFAULT NULL','boolean','''
DECLARE g platform.database_action_grant; f text; authorized_revision text:=row_revision;
BEGIN
 g:=platform_private.bound_grant(true);
 IF g.id IS NULL OR verb NOT IN ('SELECT','INSERT','UPDATE') THEN RETURN false; END IF;
 IF NOT platform_private.protected_scope(model_name,row_key,verb) THEN RETURN false; END IF;
 IF g.owner_module_id<>owner_id AND NOT (owner_id='platform_integration_owner'
  AND model_name IN ('RuntimeWorkItem','RuntimeAttempt'))
  AND NOT (session_user::text='wa_worker' AND g.owner_module_id='track_subscription_entitlement' AND model_name='RuntimeOutboxMessage') THEN RETURN false; END IF;
 -- SQL transport convention: issuer-authorized finite model/key/verb/field tokens.
 -- No wildcard. Every role-visible SELECT column must be authorized together.
 FOREACH f IN ARRAY field_names LOOP
  IF NOT COALESCE(model_name||'/'||row_key||'/'||verb||'/'||f = ANY(g.allowed_fields),false) THEN RETURN false; END IF;
 END LOOP;
 IF row_revision IS NOT NULL AND row_transaction=pg_current_xact_id()::text AND row_revision::bigint>0
  AND NOT COALESCE(model_name||'/'||row_key||'/revision/'||row_revision=ANY(g.allowed_fields),false)
  AND COALESCE(model_name||'/'||row_key||'/revision/'||(row_revision::bigint-1)::text=ANY(g.allowed_fields),false)
 THEN authorized_revision:=(row_revision::bigint-1)::text; END IF;
 IF row_revision IS NOT NULL AND NOT COALESCE
  (model_name||'/'||row_key||'/revision/'||authorized_revision = ANY(g.allowed_fields),false) THEN RETURN false; END IF;
 IF row_revision IS NOT NULL AND g.target_kind=model_name AND g.target_id=row_key
  AND g.source_generation::text<>authorized_revision THEN RETURN false; END IF;
 RETURN true;
END;''',definer=True)
fn('context_subject_owner','subject_user_id uuid, source_owner text','boolean','''
DECLARE g platform.database_action_grant;
BEGIN
 g:=platform_private.bound_grant(true);
 RETURN COALESCE(g.principal_user_id=subject_user_id AND g.owner_module_id=source_owner,false);
END;''',definer=True)
fn('command_context_allows','source_owner text, operation_name text, subject_scope text','boolean','''
DECLARE g platform.database_action_grant;
BEGIN
 g:=platform_private.bound_grant(true);
 IF g.id IS NULL OR g.owner_module_id<>source_owner THEN RETURN false; END IF;
 IF session_user::text='wa_worker' AND g.action='assignDefaultFreeTrack.v1' THEN RETURN operation_name=g.action; END IF;
 RETURN operation_name=g.action AND subject_scope=g.target_kind||':'||g.target_id;
END;''',definer=True)
global_contexts=scope_policy['registered_global_consent_contexts']
global_expr=' OR '.join('('+ ' AND '.join(f'{k}={lit(v)}' for k,v in context.items()) +')' for context in global_contexts) or 'false'
fn('global_context_registered','action_owner text, action_name text, context_owner text, context_kind text','boolean','SELECT '+global_expr+';','sql',vol='IMMUTABLE')
fn('context_subject','subject_user_id uuid','boolean','''
DECLARE g platform.database_action_grant;
BEGIN
 g:=platform_private.bound_grant(true);
 RETURN COALESCE(g.principal_user_id=subject_user_id AND g.owner_module_id='consent_disclosure',false);
END;''',definer=True)
fn('grant_guard','','trigger','''
BEGIN
 IF TG_OP='DELETE' THEN RAISE EXCEPTION 'grant delete denied' USING ERRCODE='42501'; END IF;
 IF TG_OP='UPDATE' THEN
  IF (to_jsonb(NEW)-ARRAY['revoked_at','mutation_transaction_id']) IS DISTINCT FROM
     (to_jsonb(OLD)-ARRAY['revoked_at','mutation_transaction_id']) OR OLD.revoked_at IS NOT NULL
     OR NEW.revoked_at IS NULL THEN RAISE EXCEPTION 'immutable grant'; END IF;
  PERFORM pg_advisory_xact_lock(hashtextextended('grant:'||OLD.token_hash::text,0));
  NEW.revoked_at:=clock_timestamp();
 ELSE
  IF NEW.issuer_service<>session_user::text OR NEW.database_login_role NOT IN ('wa_app_runtime','wa_worker')
   OR (NEW.principal_user_id IS NULL)=(NEW.service_principal IS NULL)
   OR NEW.backend_pid<=0 OR NEW.transaction_id !~ '^[0-9]+$'
   OR NEW.token_hash !~ '^[0-9a-f]{64}$' OR NEW.expires_at<=clock_timestamp()
   OR NEW.security_generation<0 OR NEW.source_generation<0 OR cardinality(NEW.allowed_fields)=0
   OR array_position(NEW.allowed_fields,NULL) IS NOT NULL OR array_ndims(NEW.allowed_fields)<>1
   OR NEW.revoked_at IS NOT NULL OR NEW.policy_version='' OR NEW.action='' OR NEW.purpose=''
   OR NEW.target_kind='' OR NEW.target_id='' THEN RAISE EXCEPTION 'invalid grant'; END IF;
  NEW.created_at:=clock_timestamp();
 END IF;
 NEW.mutation_transaction_id:=pg_current_xact_id()::text;
 RETURN NEW;
END;''')
emit('CREATE TRIGGER grant_guard BEFORE INSERT OR UPDATE OR DELETE ON platform.database_action_grant FOR EACH ROW EXECUTE FUNCTION platform_private.grant_guard();')

# Full physical ACL and per-operation RLS, generated only from reviewed matrix.
acl=[]
immutable={'RuntimeOutboxMessage','RuntimeEffectReceipt','RuntimeAttempt','RuntimeInboxReceipt','OwnerMutationEvidence'}
for n,m in models.items():
 if n=='DatabaseActionGrant':continue
 fields=m['columns']; object_=obj(n)
 emit(f'-- SQL-01/02: {n}\nALTER TABLE {object_} ENABLE ROW LEVEL SECURITY;\nALTER TABLE {object_} FORCE ROW LEVEL SECURITY;')
 for role in ['wa_app_runtime','wa_worker']:
  ops=m['access']['operations_by_role'][role]
  if role=='wa_app_runtime':
   verbs={x.split('_')[0] for x in ops if x.startswith(('SELECT_','INSERT_','UPDATE_'))}
   if n in immutable:verbs.discard('UPDATE')
   opcols={v:list(fields) for v in verbs}
   if 'INSERT' in opcols:opcols['INSERT']=[f for f in fields if f not in ['mutationTransactionId','createdAt']]
   if 'UPDATE' in opcols:
    foreign={f['name'] for f in m['fields'] if f['name'].endswith('Id') and f['name']!='avatarMediaId'}
    opcols['UPDATE']=[f for f in fields if f not in set(m['pk'])|foreign|{'createdAt','mutationTransactionId'}]
  else:
   opcols={}
   for x in ops:
    if isinstance(x,dict):opcols[x['operation']]=x['columns']
    elif x.startswith(('SELECT_','INSERT_','UPDATE_')):
     v=x.split('_')[0];opcols[v]=[f for f in fields if f not in (['mutationTransactionId','createdAt'] if v=='INSERT' else [])]
   if n in immutable:opcols.pop('UPDATE',None)
  for verb,fs in sorted(opcols.items()):
   if not fs:continue
   acl.append({'model':n,'role':role,'operation':verb,'fields':fs,'columns':[fields[f] for f in fs]})
   emit(f'GRANT {verb} ('+','.join(q(fields[f]) for f in fs)+f') ON {object_} TO {role};')
   rk=" || ':' || ".join(q(fields[f])+'::text' for f in m['pk'])
   version=next((f for f in ['revision','fence','generation'] if f in fields),None)
   rv=q(fields[version])+'::text' if version else 'NULL::text'
   # INSERT new revision must be zero; mutable existing version in USING checked on old row.
   ownerfield={'RuntimeCommandReceipt':'ownerModuleId','OwnerMutationEvidence':'ownerModuleId','RuntimeEffectReceipt':'ownerModuleId','RuntimeReservation':'ownerModuleId','RuntimeOutboxMessage':'producerOwner','RuntimeInboxReceipt':'consumerOwner'}.get(n)
   ownerexpr=q(fields[ownerfield]) if ownerfield else lit(m['owner'])
   guard=f'platform_private.row_allowed({ownerexpr},{lit(n)},{rk},{lit(verb)},{arr(["@row"] if verb=="UPDATE" else fs)},{rv if verb=="SELECT" else "NULL::text"},{q(fields["mutationTransactionId"])}::text)'
   if role=='wa_worker':
    # A narrow UPDATE column grant is not a complete source identity. Pass the
    # fixed SELECT/verb union to the Boolean verifier without changing the ACL.
    verifier_fields=[f for f in fields if f in set(opcols.get('SELECT',[]))|set(fs)]
    guard+=f' AND platform_private.worker_track_allowed({lit(n)},jsonb_build_object('+','.join(v for f in verifier_fields for v in [lit(fields[f]),q(fields[f])])+f'),{lit(verb)})'
   pname=q('p_'+role.removeprefix('wa_')+'_'+verb.lower())
   if verb=='SELECT':clause='USING ('+guard+')'
   elif verb=='INSERT':clause='WITH CHECK ('+guard+')'
   else:clause='USING ('+guard+') WITH CHECK ('+guard+')'
   # Track helper defined below before policies are installed.
   statement=f'CREATE POLICY {pname} ON {object_} FOR {verb} TO {role} {clause};'
   m.setdefault('policies',[]).append(statement)
dump('context/reconciliation/foundation-sql-draft-access.json',acl)

verifier_access=json.loads(read('context/reconciliation/foundation-sql-verifier-access.json'))
for role,profile in verifier_access['roles'].items():
 enum_types=set()
 for table,columns in profile['columns'].items():
  emit(f'GRANT SELECT ('+','.join(q(c) for c in columns)+f') ON {table} TO {role};')
  emit(f'CREATE POLICY {q("leaf_"+role)} ON {table} FOR SELECT TO {role} USING (true);')
  model=next(m for m in models.values() if m['object']==table)
  for field in model['fields']:
   typename=field['type'].rstrip('?[]')
   if model['columns'][field['name']] in columns and typename in blocks and blocks[typename]['kind']=='enum':enum_types.add(typename)
 for typename in sorted(enum_types):
  definition=blocks[typename]['body']; native=re.search(r'@@map\("([^"]+)"\)',definition).group(1); schema=re.search(r'@@schema\("([^"]+)"\)',definition).group(1)
  emit(f'GRANT USAGE ON TYPE {q(schema)}.{q(native)} TO {role};')
emit(read('scripts/sql-review/foundation-verification.sql'))
for m in models.values():
 for statement in m.get('policies',[]):emit(statement)

# Generic physical guards: exact field checks and immutable owning FKs/keys.
for n,m in models.items():
 if n=='DatabaseActionGrant':continue
 fs=m['columns']; pk=m['pk']; immutable_row=m['access']['retained_evidence']=='IMMUTABLE_EVIDENCE_OR_RECEIPT' or n in immutable
 owning=set(pk)|{f for f in fs if f.endswith('Id') and f not in ['avatarMediaId','subscriptionId']}
 # Reassignment of subscription is restricted to TrackBaseSelection only.
 if n!='TrackBaseSelection' and 'subscriptionId' in fs:owning.add('subscriptionId')
 owning|={f for f in ['createdAt','track','sourceOwner','sourceId','semanticKey','semanticEffectKey','fingerprint','ownerModuleId','operation','subjectScope','handlerName','semanticWorkKey','resourceKind','resourceKey'] if f in fs}
 if n=='RuntimeReservation':owning.add('quantity')
 if n in ['RuntimeWorkItem','RuntimeReservation']:owning.discard('effectReceiptId') # one protected outcome link, checked by transition guard
 body=['DECLARE n jsonb:=to_jsonb(NEW); o jsonb; changed text[];','BEGIN'," IF TG_OP='DELETE' THEN RAISE EXCEPTION 'direct deletion denied' USING ERRCODE='42501'; END IF;",' IF TG_OP=\'UPDATE\' THEN','  o:=to_jsonb(OLD);']
 if immutable_row:body.append("  RAISE EXCEPTION 'immutable evidence or receipt';")
 else:
  if not m['object'].startswith('platform.') and 'revision' not in fs:
   body.append("  RAISE EXCEPTION 'DRAFT-03: mutable source requires reviewed CAS version';")
  body.append('  IF '+ ' OR '.join(f'NEW.{q(fs[f])} IS DISTINCT FROM OLD.{q(fs[f])}' for f in sorted(owning)) + " THEN RAISE EXCEPTION 'immutable identity or ownership'; END IF;")
  if 'revision' in fs:body.append("  IF NEW.revision<>OLD.revision+1 THEN RAISE EXCEPTION 'CAS revision must increment once'; END IF;")
  for f in ['privacyGeneration','securityGeneration','sourceGeneration','instructionGeneration','generation','fence']:
   if f in fs:body.append(f"  IF NEW.{q(fs[f])}<OLD.{q(fs[f])} THEN RAISE EXCEPTION 'generation/fence regression'; END IF;")
  body.append("  SELECT COALESCE(array_agg(key),ARRAY[]::text[]) INTO changed FROM jsonb_each(n) WHERE value IS DISTINCT FROM o->key AND key<>'mutation_transaction_id';")
  body.append('  IF NOT platform_private.row_allowed('+','.join([lit(m['owner']),lit(n),key(n,'n'),"'UPDATE'",'ARRAY['] ) if False else '')
  # field-to-column translation fixed at generation, not caller selectable.
  changes='ARRAY['+','.join(f'CASE WHEN {lit(fs[f])}=ANY(changed) THEN {lit(f)} END' for f in fs)+']::text[]'
  version=next((f for f in ['revision','fence','generation'] if f in fs),None)
  of={'RuntimeCommandReceipt':'ownerModuleId','OwnerMutationEvidence':'ownerModuleId','RuntimeEffectReceipt':'ownerModuleId','RuntimeReservation':'ownerModuleId','RuntimeOutboxMessage':'producerOwner','RuntimeInboxReceipt':'consumerOwner'}.get(n)
  oe=f'n->>{lit(fs[of])}' if of else lit(m['owner'])
  body.append(f'  IF NOT platform_private.row_allowed({oe},{lit(n)},{key(n,"n")},\'UPDATE\',array_remove({changes},NULL),'+('OLD.'+q(fs[version])+'::text' if version else 'NULL::text')+") THEN RAISE EXCEPTION 'field or CAS scope denied' USING ERRCODE='42501'; END IF;")
 body.extend([' ELSE'])
 if 'revision' in fs:body.append("  IF NEW.revision<>0 THEN RAISE EXCEPTION 'initial revision must be zero'; END IF;")
 if 'createdAt' in fs:body.append(f'  NEW.{q(fs["createdAt"])}:=clock_timestamp();')
 body.append(' END IF;')
 if n in ['CustomerProfile','TrackPlan']:
  body.insert(2,f" PERFORM pg_advisory_xact_lock(hashtextextended('source:{n}:'||NEW.id::text,0));")
 if n=='CustomerProfile':body.append(" IF NOT platform_private.context_subject_owner(NEW.user_id,'customer_buyer_profile') THEN RAISE EXCEPTION 'foreign Customer principal'; END IF;")
 if n=='ConsentPresentation':body.append(" IF NOT platform_private.context_subject_owner(NEW.user_id,'consent_disclosure') THEN RAISE EXCEPTION 'foreign Consent presentation principal'; END IF;")
 if 'updatedAt' in fs:body.append(f' NEW.{q(fs["updatedAt"])}:=clock_timestamp();')
 if n=='UserSecurityProfile':body.append(" PERFORM pg_advisory_xact_lock(hashtextextended('identity:'||NEW.user_id::text,0));")
 body+=[' NEW.mutation_transaction_id:=pg_current_xact_id()::text;',' RETURN NEW;','END;']
 fn('guard_'+n.lower(),'','trigger','\n'.join(body))
 emit(f'CREATE TRIGGER physical_guard BEFORE INSERT OR UPDATE OR DELETE ON {obj(n)} FOR EACH ROW EXECUTE FUNCTION platform_private.guard_{n.lower()}();')
 # Explicit JSON NULL admission; SQL NULL only, not JSON null.
 for f in m['fields']:
  if f['type'].rstrip('?')=='Json' and n not in ['OwnerMutationEvidence','RuntimeCommandReceipt','RuntimeOutboxMessage']:
   emit(f'ALTER TABLE {obj(n)} ADD CONSTRAINT {q("f0_null_"+fs[f["name"]])} CHECK ({q(fs[f["name"]])} IS NULL);')
 for f in ['revision','privacyGeneration','securityGeneration','sourceGeneration','instructionGeneration','generation','fence','attemptCount']:
  if f in fs:emit(f'ALTER TABLE {obj(n)} ADD CONSTRAINT {q("nonnegative_"+fs[f])} CHECK ({q(fs[f])} >= 0);')
 for f in m['fields']:
  if '@db.Char(64)' in f['attributes']:emit(f'ALTER TABLE {obj(n)} ADD CONSTRAINT {q("hash_"+fs[f["name"]])} CHECK ({q(fs[f["name"]])} ~ \'^[0-9a-f]{{64}}$\');')
 for start,end in [('periodStart','periodEnd'),('currentPeriodStart','currentPeriodEnd'),('startedAt','finishedAt'),('effectiveFrom','effectiveUntil'),('startsAt','expiresAt')]:
  if start in fs and end in fs:emit(f'ALTER TABLE {obj(n)} ADD CONSTRAINT {q("ordered_"+fs[end])} CHECK ({col(n,end)} IS NULL OR ({col(n,start)} IS NOT NULL AND {col(n,end)} > {col(n,start)}));')

# Hand-authored relational/domain controls live in a source template, copied verbatim.
emit(read('scripts/sql-review/foundation-invariants.sql'))

# Each business mutation has exact source snapshots and current-transaction receipt/evidence.
# Infrastructure uses its specialized FK/semantic guards; it does not recurse into evidence.
domain=[];reverse_cases=[];worker_reverse_cases=[]
for n,m in models.items():
 if n=='DatabaseActionGrant' or m['object'].startswith('platform.'):continue
 if n in ['ProfessionalProfile','CandidateProfile','CustomerProfileLifecycleEvent','TrackSubscriptionEvent','TrackEnrollmentReceipt']:continue
 domain.append(n);fs=m['columns'];ed=registry['contracts/database-review/owner-mutation-evidence.v1.schema.json']['$defs'][n]
 snap=ed['properties']['committed']['properties']
 def snapshot(row):
  values=[]
  for f in snap:
   values += [lit(f),f'to_jsonb({row}.{q(fs[f])}'+('::text' if models[n]['fields'][list(fs).index(f)]['type'].rstrip('?') == 'BigInt' else '')+')']
  return 'jsonb_build_object('+','.join(values)+')'
 pkjson='jsonb_build_object('+','.join(v for f in m['pk'] for v in [lit(f),f'NEW.{q(fs[f])}'])+')'
 reverse_case=f'''WHEN {lit(n)} THEN
  SELECT EXISTS(SELECT 1 FROM {obj(n)} s WHERE {key(n,'to_jsonb(s)')}=NEW.aggregate_id
   AND s.mutation_transaction_id=NEW.mutation_transaction_id
   AND {snapshot('s')}=NEW.evidence_body->'committed'
   AND {('s.revision' if 'revision' in fs else '0::bigint')}=NEW.committed_revision) INTO matches;'''
 if n in ['TrackSubscription','TrackEntitlementGrant','TrackBaseSelection']:
  # Worker keeps its original direct columns. The fixed read-only port gets
  # only the exact snapshot/identity fields needed for these three branches.
  identity_fields=['id','userId','track','customerProfileId','candidateProfileId','professionalProfileId']
  identity_json='jsonb_build_object('+','.join(v for f in identity_fields for v in [lit(fs[f]),f's.{q(fs[f])}'])+')'
  worker_reverse_cases.append(f'''WHEN {lit(n)} THEN
  RETURN EXISTS(SELECT 1 FROM {obj(n)} s WHERE s.{q(fs['id'])}::text=aggregate_id
   AND s.mutation_transaction_id=source_transaction AND s.revision=committed_revision
   AND {snapshot('s')}=committed_value
   AND platform_private.worker_track_allowed({lit(n)},{identity_json},'SELECT'));''')
  reverse_case=f'''WHEN {lit(n)} THEN
  IF session_user::text='wa_worker' THEN
   matches:=platform_private.worker_evidence_source_matches(NEW.aggregate_kind,NEW.aggregate_id,NEW.committed_revision,NEW.mutation_transaction_id,NEW.evidence_body->'committed');
  ELSE
   {reverse_case.split('THEN',1)[1].strip()}
  END IF;'''
 reverse_cases.append(reverse_case)
 newrev='NEW.revision' if 'revision' in fs else '0::bigint'
 oldrev='OLD.revision' if 'revision' in fs else '0::bigint'
 fn('commit_'+n.lower(),'','trigger',f'''
DECLARE e platform.owner_mutation_evidence; prior_value jsonb;
BEGIN
 prior_value:=CASE WHEN TG_OP='UPDATE' THEN {snapshot('OLD')} ELSE 'null'::jsonb END;
 SELECT * INTO e FROM platform.owner_mutation_evidence WHERE aggregate_kind={lit(n)}
  AND aggregate_id={key(n,'to_jsonb(NEW)')} AND committed_revision={newrev}
  AND owner_module_id={lit(m['owner'])} AND mutation_transaction_id=pg_current_xact_id()::text;
 IF NOT FOUND OR e.evidence_body->'primaryKey' IS DISTINCT FROM {pkjson}
  OR e.evidence_body->'committed' IS DISTINCT FROM {snapshot('NEW')}
  OR COALESCE(e.evidence_body->'prior','null'::jsonb) IS DISTINCT FROM prior_value
  OR e.previous_revision IS DISTINCT FROM (CASE WHEN TG_OP='UPDATE' THEN {oldrev} ELSE NULL::bigint END)
  OR e.decision_ref IS DISTINCT FROM e.evidence_body->>'decisionRef'
  OR NOT platform_private.json_evidence_{n.lower()}(e.evidence_body)
  OR NOT EXISTS(SELECT 1 FROM platform.runtime_command_receipt c WHERE c.id=e.command_receipt_id
   AND c.mutation_transaction_id=e.mutation_transaction_id AND c.owner_module_id=e.owner_module_id
   AND c.state='committed' AND c.operation=e.action {"AND c.source_revision=e.committed_revision" if n=="CustomerProfile" else ""})
 THEN RAISE EXCEPTION 'missing exact atomic owner proof for {n}'; END IF;
 RETURN NULL;
END;''')
 emit(f'CREATE CONSTRAINT TRIGGER owner_commit AFTER INSERT OR UPDATE ON {obj(n)} DEFERRABLE INITIALLY DEFERRED FOR EACH ROW EXECUTE FUNCTION platform_private.commit_{n.lower()}();')
fn('worker_evidence_source_matches','model_name text, aggregate_id text, committed_revision bigint, source_transaction text, committed_value jsonb','boolean','''
DECLARE g platform.database_action_grant;
BEGIN
 g:=platform_private.bound_grant(true);
 IF g.id IS NULL OR session_user::text<>'wa_worker' OR g.service_principal IS NULL
  OR source_transaction IS DISTINCT FROM pg_current_xact_id()::text
  OR NOT platform_private.worker_lease_valid(g.target_id::uuid,NULL,true)
 THEN RETURN false; END IF;
 CASE model_name
'''+ '\n'.join(worker_reverse_cases)+'''
 ELSE RETURN false;
 END CASE;
END;''',definer=True)
fn('evidence_source_commit','','trigger', '''DECLARE matches boolean:=false;
BEGIN
 CASE NEW.aggregate_kind
'''+ '\n'.join(reverse_cases)+'''
 ELSE RAISE EXCEPTION 'unsupported source or recursive evidence bootstrap';
 END CASE;
 IF NOT matches THEN RAISE EXCEPTION 'orphan or invented source evidence'; END IF;
 RETURN NULL;
END;''')
emit('CREATE CONSTRAINT TRIGGER exact_evidence_source AFTER INSERT ON platform.owner_mutation_evidence DEFERRABLE INITIALLY DEFERRED FOR EACH ROW EXECUTE FUNCTION platform_private.evidence_source_commit();')
emit('ALTER TABLE platform.owner_mutation_evidence ADD CONSTRAINT closed_evidence_json CHECK (CASE aggregate_kind '+ ' '.join(f'WHEN {lit(n)} THEN platform_private.json_evidence_{n.lower()}(evidence_body)' for n in domain)+' ELSE false END);')

# Explicit final privileges for all functions; no inherited PUBLIC execute window survives COMMIT.
emit('REVOKE ALL ON ALL FUNCTIONS IN SCHEMA platform_private FROM PUBLIC;')
for n in models:emit(f'GRANT EXECUTE ON FUNCTION platform_private.json_evidence_{n.lower()}(jsonb) TO wa_app_runtime,wa_worker;')
for n in ['customer_event','track_command','track_result','sh004_result','sh114_result']:emit(f'GRANT EXECUTE ON FUNCTION platform_private.json_{n}(jsonb) TO wa_app_runtime,wa_worker;')
for sig in ['json_datetime(text)','bind_request_context(text)','context_allows(text,text,text,text,text)','row_allowed(text,text,text,text,text[],text,text)','context_subject(uuid)','context_subject_owner(uuid,text)','command_context_allows(text,text,text)','global_context_registered(text,text,text,text)']:
 emit(f'GRANT EXECUTE ON FUNCTION platform_private.{sig} TO wa_app_runtime,wa_worker;')
emit('REVOKE EXECUTE ON FUNCTION platform_private.bound_grant(boolean) FROM wa_app_runtime,wa_worker;')
# Trigger functions cannot be called as ordinary SQL; private helper surface is bounded below.
for sig in ['bound_grant(boolean)','bind_request_context(text)','context_allows(text,text,text,text,text)','protected_scope(text,text,text)','row_allowed(text,text,text,text,text[],text,text)','context_subject(uuid)','context_subject_owner(uuid,text)','command_context_allows(text,text,text)']:
 emit(f'GRANT CREATE ON SCHEMA platform_private TO wa_private_helper_owner;\nALTER FUNCTION platform_private.{sig} OWNER TO wa_private_helper_owner;')
for role,signatures in {
 'wa_customer_verifier':['customer_current_for_track(uuid,uuid,bigint,bigint,uuid)'],
 'wa_track_verifier':['worker_track_allowed(text,jsonb,text)','worker_lease_valid(uuid,uuid,boolean)','worker_effect_matches(uuid,uuid,boolean)','track_atomic_valid(text,jsonb,jsonb)','worker_evidence_source_matches(text,text,bigint,text,jsonb)']}.items():
 for sig in signatures:
  emit(f'GRANT CREATE ON SCHEMA platform_private TO {role};\nALTER FUNCTION platform_private.{sig} OWNER TO {role};')
 emit(f'REVOKE CREATE ON SCHEMA platform_private FROM {role};')
emit('''GRANT EXECUTE ON FUNCTION platform_private.bound_grant(boolean),platform_private.context_allows(text,text,text,text,text) TO wa_customer_verifier,wa_track_verifier;
GRANT EXECUTE ON FUNCTION platform_private.customer_current_for_track(uuid,uuid,bigint,bigint,uuid) TO wa_track_verifier;
GRANT EXECUTE ON FUNCTION platform_private.worker_track_allowed(text,jsonb,text),platform_private.worker_lease_valid(uuid,uuid,boolean),platform_private.worker_effect_matches(uuid,uuid,boolean),platform_private.track_atomic_valid(text,jsonb,jsonb),platform_private.worker_evidence_source_matches(text,text,bigint,text,jsonb) TO wa_worker;
GRANT EXECUTE ON FUNCTION platform_private.lease_secret_matches(text) TO wa_track_verifier,wa_worker;
REVOKE CREATE ON SCHEMA platform_private FROM wa_private_helper_owner;
-- Separate original bootstrap grantor must run foundation-bootstrap-finalize.review.sql
-- after success OR failure. wa_schema_owner has ADMIN FALSE and cannot do that cleanup.
-- Helper may call its own functions and pure JSON predicates only; no business DML.
-- Owned context functions need no grant of arbitrary application functions.
-- Issuer invokes only grant trigger automatically; no context discovery endpoints.
REVOKE ALL ON ALL TABLES IN SCHEMA app,platform FROM PUBLIC;
REVOKE ALL ON ALL SEQUENCES IN SCHEMA app,platform FROM PUBLIC;
-- Managed browser/service roles are untouched; revoke application grants if present.
DO $roles$ DECLARE r text; BEGIN
 FOREACH r IN ARRAY ARRAY['anon','authenticated','service_role'] LOOP
  IF EXISTS (SELECT 1 FROM pg_roles WHERE rolname=r) THEN
   EXECUTE format('REVOKE ALL ON ALL TABLES IN SCHEMA app,platform FROM %I',r);
   EXECUTE format('REVOKE ALL ON SCHEMA app,platform,platform_private FROM %I',r);
   EXECUTE format('REVOKE ALL ON ALL FUNCTIONS IN SCHEMA platform_private FROM %I',r);
  END IF;
 END LOOP;
END $roles$;
RESET ROLE;
COMMIT;
''')
# Enum USAGE is explicit, before function/table runtime access.
enumgrant=[]
for name,b in blocks.items():
 if b['kind']=='enum':
  native=re.search(r'@@map\("([^"]+)"\)',b['body']).group(1);schema=re.search(r'@@schema\("([^"]+)"\)',b['body']).group(1)
  enumgrant.append(f'REVOKE ALL ON TYPE {q(schema)}.{q(native)} FROM PUBLIC;\nGRANT USAGE ON TYPE {q(schema)}.{q(native)} TO wa_app_runtime,wa_worker,wa_context_issuer,wa_private_helper_owner;')
sql.insert(2,'\n'.join(enumgrant)+'\n')
write('review-output/foundation-application.review.sql','\n'.join(sql))
dump('context/reconciliation/foundation-sql-draft-models.json',[{'model':n,'object':m['object'],'owner':m['owner'],'fields':m['columns'],'pk':m['pk'],'atomic_guard':n in domain} for n,m in models.items()])
print('Wrote application review SQL, bootstrap, 40-model metadata and exact ACL map')
