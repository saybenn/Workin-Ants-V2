#!/usr/bin/env python3
"""Offline P0-C-03 SQL source checks. Never imports a database driver or executes SQL.

Requires isolated pinned pglast==7.21 (PostgreSQL 17 parser) on PYTHONPATH.
Parsing is not SQL execution, installation, name resolution or runtime proof.
"""
import json,re,hashlib,sys,runpy
from pathlib import Path
from pglast import parse_sql,parse_plpgsql,__version__
from pglast import ast
ROOT=Path(__file__).resolve().parents[1]
def checks(root=ROOT,verify_fingerprints=True):
 errors=[];stats={};functions={};tables={};triggers=[];actual_acl=[];owners={};policies=[];function_acl=set();helper_acl=[]
 def need(ok,msg):
  if not ok:errors.append(msg)
 def data(p):return json.loads((root/p).read_text(encoding='utf8'))
 manifest=data('context/reconciliation/foundation-sql-draft-manifest.json')
 need(__version__=='v7.21','parser version not pinned 7.21')
 for k in ['execution_approved','database_contacted','sql_executed','adopted','runtime_qualified']:
  need(manifest.get(k) is False,'unsafe stage claim: '+k)
 need(manifest.get('database_posture')=='D','posture changed')
 if verify_fingerprints:
  for path,expected in (manifest['preserved_reviewed_inputs_sha256']|manifest.get('revised_inputs_sha256',{})|manifest['outputs_sha256']|manifest.get('draft_source_sha256',{})).items():
   need(hashlib.sha256((root/path).read_bytes()).hexdigest()==expected,'reviewed input/output changed: '+path)
 for path in ['prisma/foundation/migrations','prisma.foundation.config.ts']:
  need(not (root/path).exists(),'migration path activated: '+path)
 for path in ['review-output/foundation-bootstrap.review.sql','review-output/foundation-structure.sql','review-output/foundation-application.review.sql','review-output/foundation-bootstrap-finalize.review.sql']:
  s=(root/path).read_text(encoding='utf8');ss=parse_sql(s);pc=0;sc=0
  for item in ss:
   st=item.stmt
   if isinstance(st,ast.CreateStmt):
    columns={v.colname for v in st.tableElts if isinstance(v,ast.ColumnDef)}
    tables[(st.relation.schemaname,st.relation.relname)]=columns
   if isinstance(st,ast.CreateFunctionStmt):
    start=item.stmt_location;end=start+item.stmt_len if item.stmt_len else len(s);chunk=s[start:end]
    name='.'.join(x.sval for x in st.funcname)
    opts={x.defname:x.arg for x in st.options}
    funcs=opts['as'][0].sval
    need('search_path' in chunk and 'pg_catalog' in chunk,'unpinned function search path: '+name)
    if opts['language'].sval=='plpgsql':
     try:parse_plpgsql(chunk);pc+=1
     except Exception as exc:errors.append('PL/pgSQL syntax '+name+': '+str(exc))
    elif opts['language'].sval=='sql':
     try:parse_sql(funcs);sc+=1
     except Exception as exc:errors.append('SQL body syntax '+name+': '+str(exc))
    need(name not in functions or path.endswith('foundation-structure.sql'),'duplicate function '+name)
    functions[name]=(st,funcs,chunk)
   if isinstance(st,ast.CreateTrigStmt):triggers.append(st)
   if isinstance(st,ast.AlterOwnerStmt) and st.objectType.name=='OBJECT_FUNCTION':owners['.'.join(x.sval for x in st.object.objname)]=st.newowner.rolename
   if isinstance(st,ast.CreatePolicyStmt):policies.append(st)
   if isinstance(st,ast.GrantStmt) and st.is_grant and st.objtype.name=='OBJECT_TABLE' and st.objects:
    for ob in st.objects:
     for role in st.grantees:
      if role.rolename=='wa_private_helper_owner':
       for priv in st.privileges or []:helper_acl.append((ob.schemaname+'.'+ob.relname,priv.priv_name.upper(),tuple(sorted(x.sval for x in priv.cols or []))))
      if role.rolename in ['wa_app_runtime','wa_worker']:
       need(not st.grant_option,'runtime grant option')
       for priv in st.privileges or []:
        actual_acl.append((ob.schemaname+'.'+ob.relname,role.rolename,priv.priv_name.upper(),tuple(sorted(x.sval for x in priv.cols or []))))
       need(bool(st.privileges),'whole table ALL privilege')
   if isinstance(st,ast.GrantStmt) and st.objtype.name=='OBJECT_FUNCTION':
    for role in st.grantees:
     need(not(st.is_grant and role.roletype.name=='ROLESPEC_PUBLIC'),'PUBLIC function execute grant')
     if role.rolename in ['wa_app_runtime','wa_worker']:
      need(not (st.is_grant and not st.objects),'blanket function grant')
      for ob in st.objects or []:
       if isinstance(ob,ast.ObjectWithArgs):
        signature='.'.join(x.sval for x in ob.objname)
        if st.is_grant:function_acl.add((role.rolename,signature))
        else:function_acl.discard((role.rolename,signature))
   if isinstance(st,ast.AlterTableStmt):
    if st.relation:
     key=(st.relation.schemaname,st.relation.relname)
     need(key in tables,'ALTER before table: '+str(key))
   if isinstance(st,ast.DoStmt):
    try:parse_plpgsql(s[item.stmt_location:item.stmt_location+item.stmt_len]+';');pc+=1
    except Exception as exc:errors.append('DO syntax: '+str(exc))
  stats[path]={'sql_statements':len(ss),'plpgsql_bodies_parsed':pc,'sql_bodies_parsed':sc}
 application=(root/'review-output/foundation-application.review.sql').read_text(encoding='utf8')
 bootstrap=(root/'review-output/foundation-bootstrap.review.sql').read_text(encoding='utf8')
 modelrows=data('context/reconciliation/foundation-sql-draft-models.json')
 access=data('context/reconciliation/foundation-sql-draft-access.json')
 need(len(modelrows)==40,'wrong foundation cut')
 need(set(tables)=={tuple(r['object'].split('.')) for r in modelrows}|{('platform_private','identity_service_authorization'),('platform_private','identity_service_receipt')},'unregistered physical table')
 for r in modelrows:
  sch,tab=r['object'].split('.');cols=tables[(sch,tab)]
  need(set(r['fields'].values())==cols,'actual column mismatch '+r['model'])
  ob='"'+sch+'"."'+tab+'"'
  if r['model']!='DatabaseActionGrant':
   need('ALTER TABLE '+ob+' ENABLE ROW LEVEL SECURITY;' in application,'RLS missing '+ob)
   need('ALTER TABLE '+ob+' FORCE ROW LEVEL SECURITY;' in application,'FORCE RLS missing '+ob)
   need('platform_private.guard_'+r['model'].lower()+'()' in application,'write guard missing '+ob)
  if r['atomic_guard']:need('platform_private.commit_'+r['model'].lower()+'()' in application,'atomic guard missing '+ob)
 for t in triggers:
  fn='.'.join(x.sval for x in t.funcname)
  need(fn in functions,'trigger function not found '+fn)
  need((t.relation.schemaname,t.relation.relname) in tables,'trigger table not found')
 # Column privileges are parsed from actual SQL, compared with independently
 # approved worker field sets. A coherent generator/map mutation is not enough.
 matrix=data('context/reconciliation/database-candidate-access-matrix.json')
 approved={r['model']:r for r in matrix['objects'] if r['kind']=='table'}
 expected_acl=[]
 for r in access:
  m=next(x for x in modelrows if x['model']==r['model']);ob='"'+m['object'].replace('.','"."')+'"'
  need(set(r['columns'])<=tables[tuple(m['object'].split('.'))],'ACL nonexistent column '+r['model'])
  needle='GRANT '+r['operation']+' ('+','.join('"'+c+'"' for c in r['columns'])+') ON '+ob+' TO '+r['role']+';'
  expected_acl.append((m['object'],r['role'],r['operation'],tuple(sorted(r['columns']))))
  need(needle in application,'ACL evidence differs from SQL '+str(r))
  if r['role']=='wa_worker' and r['model'].startswith('Track'):
   allowed=[x for x in approved[r['model']]['operations_by_role']['wa_worker'] if isinstance(x,dict) and x['operation']==r['operation']]
   need(len(allowed)==1 and set(r['fields'])==set(allowed[0]['columns']),'Track worker privilege broadening '+r['model'])
  need(r['operation']!='DELETE','direct deletion grant')
 need(sorted(expected_acl)==sorted(actual_acl),'actual SQL ACL exceeds or differs from declared exact role/column map')
 need(sorted(helper_acl)==sorted([('platform.database_action_grant','SELECT',()),('app.user_security_profiles','SELECT',('security_generation','user_id')),('platform_private.identity_service_authorization','SELECT',('revoked_at','security_generation','service_principal'))]),'helper read/write surface broadened')
 for p in policies:
  if any(r.rolename in ['wa_app_runtime','wa_worker'] for r in p.roles):
   text=json.dumps(p())
   need('row_allowed' in text,'runtime policy without protected row context: '+p.policy_name)
   if p.cmd_name=='update':need(p.qual is not None and p.with_check is not None,'UPDATE needs USING and WITH CHECK')
 for model in ['TrackUsageEvent','TrackUsageCounter','TrackUsageReservation']:
  need(not any(r['role']=='wa_worker' and r['model']==model for r in access),'worker usage permission '+model)
 need('REVOKE EXECUTE ON FUNCTION platform_private.bound_grant(boolean) FROM wa_app_runtime,wa_worker;' in application,'raw grant helper exposed')
 need(not any(n=='platform_private.bound_grant' for r,n in function_acl),'effective raw grant helper execute granted')
 need(not re.search(r'GRANT\s+(?:SELECT|INSERT|UPDATE|DELETE|ALL).*database_action_grant.*TO wa_(?:app_runtime|worker)',application),'direct grant table exposed')
 need('GRANT wa_schema_owner TO wa_migrator' in bootstrap,'migrator SET ROLE path missing')
 need(not re.search(r'GRANT wa_(?:schema_owner|context_issuer|private_helper_owner) TO wa_(?:app_runtime|worker)',bootstrap),'runtime privileged membership')
 finalize=(root/'review-output/foundation-bootstrap-finalize.review.sql').read_text();need('GRANTED BY CURRENT_USER' in finalize and 'original bootstrap grantor' in finalize and 'temporary installation membership remains' in finalize,'authorized success/failure membership cleanup missing');need('REVOKE wa_private_helper_owner FROM wa_schema_owner;' not in application,'ADMIN FALSE owner attempts membership cleanup')
 need('ALTER DEFAULT PRIVILEGES FOR ROLE wa_schema_owner REVOKE EXECUTE ON FUNCTIONS FROM PUBLIC;' in bootstrap,'default PUBLIC function execute')
 for name,(node,body,chunk) in functions.items():
  if any(o.defname=='security' and o.arg.boolval for o in node.options):
   need(name.split('.')[-1] in ['bound_grant','bind_request_context','context_allows','protected_scope','row_allowed','worker_track_allowed','context_subject','context_subject_owner','command_context_allows','customer_current_for_track','worker_lease_valid','worker_effect_matches','track_atomic_valid','worker_evidence_source_matches'],'unexpected DEFINER '+name)
   need(not re.search(r'(?:^|[;\n])\s*(?:INSERT|UPDATE|DELETE|EXECUTE)\b',re.sub(r'--[^\n]*','',body),re.I),'DEFINER writes/dynamic SQL '+name)
   expected_owner='wa_customer_verifier' if name.endswith('.customer_current_for_track') else 'wa_track_verifier' if name.split('.')[-1] in ['worker_track_allowed','worker_lease_valid','worker_effect_matches','track_atomic_valid','worker_evidence_source_matches'] else 'wa_private_helper_owner';need(owners.get(name)==expected_owner,'DEFINER owner not narrow helper: '+name)
  # Offline composite variable column checks; this is not full catalog resolution.
  for var,sch,tab in re.findall(r'\b(\w+)\s+(app|platform)\.(\w+)\b',chunk):
   need((sch,tab) in tables,'unknown composite type '+sch+'.'+tab)
   for field in re.findall(r'\b'+re.escape(var)+r'\."?(\w+)"?',body):
    need(field in tables.get((sch,tab),set()),'unknown '+var+' column '+field+' in '+name)
  for called in re.findall(r'platform_private\.(\w+)\s*\(',body):need('platform_private.'+called in functions,'unknown private function '+called)
  if name.split('.')[-1].startswith('guard_') or name.endswith('.grant_guard'):
   need('NEW.mutation_transaction_id:=pg_current_xact_id()::text;' in body,'missing server mutation stamp '+name)
 # Semantic security assertions independent of assembler.
 binding=functions['platform_private.bound_grant'][1]
 for fragment in ['database_login_role=session_user::text','backend_pid=pg_backend_pid()','transaction_id=pg_current_xact_id()::text','revoked_at IS NULL','expires_at > clock_timestamp()','s.security_generation=g.security_generation']:
  need(fragment in binding,'missing bind/currentness predicate '+fragment)
 need('platform_private.identity_service_authorization a' in binding and 'a.security_generation=g.security_generation AND a.revoked_at IS NULL' in binding,'service currentness has no independent Identity source')
 need('bound_grant(false)' in functions['platform_private.bind_request_context'][1],'bind locks before CTX02 revocation')
 need("COALESCE(model_name||'/'||row_key||'/'||verb||'/'||f = ANY(g.allowed_fields),false)" in functions['platform_private.row_allowed'][1],'nullable capability membership can authorize absent field')
 need('array_position(NEW.allowed_fields,NULL) IS NOT NULL' in functions['platform_private.grant_guard'][1],'NULL capability element admitted')
 need('context_id IS DISTINCT FROM NEW.context_id' in application,'nullable Consent context not exact')
 need('committed_revision=previous_revision+1' in application,'evidence revision gap')
 need('mutation_transaction_id=pg_current_xact_id()::text' in application,'transaction-stamp proof missing')
 need('DEFERRABLE INITIALLY DEFERRED' in application,'deferred atomic guards missing')
 need("e.state<>'fenced_noncommit'" in application and "e.command_receipt_id IS DISTINCT FROM NEW.command_receipt_id" in application and "e.operation<>c.operation" in application,'unsafe unknown reservation release');need("OLD.state='unknown' AND NEW.state IN ('unknown','committed','released')" in application,'uncertain reservation can return to active')
 control=data('context/reconciliation/foundation-sql-draft-controls.json')
 need({r['id'] for r in control['requirements']}=={'SQL-'+str(n).zfill(2) for n in range(1,19)},'18 SQL map incomplete')
 replay=data('context/reconciliation/foundation-sql-draft-replay-map.json')
 ids=data('context/reconciliation/database-candidate-corrections-first-replay-selection.json')['first_p0c_replay']['ids']
 need(len(replay['tests'])==94 and {r['id'] for r in replay['tests']}==set(ids),'94 replay mapping incomplete')
 need(all(r['status']=='NOT_RUN' and r['controls'] for r in replay['tests']),'false replay claim or unmapped test')
 correction=runpy.run_path(str(ROOT/'scripts/check-foundation-sql-corrections.py'))['inspect'](root)
 errors.extend(correction['errors'])
 return {'status':'PASS' if not errors else 'FAIL','scope':'OFFLINE_SOURCE_AND_PARSER_ONLY','database_contacted':False,'sql_executed':False,'catalog_parity_verified':False,'runtime_tests':'NOT_RUN','parser':__version__,'stats':stats,'errors':errors}
if __name__=='__main__':
 result=checks();print(json.dumps(result,indent=2));sys.exit(bool(result['errors']))
