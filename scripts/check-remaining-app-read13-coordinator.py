"""Actual CTX Session and SQL-projection mocks; no Postgres/runtime claims."""
from copy import deepcopy
import ast as python_ast
from datetime import datetime,timedelta,timezone
import importlib.util
import inspect
import json
from pathlib import Path
import re
import runpy
import socket
import subprocess
import sys
import tempfile
import types
import unittest
from unittest.mock import patch
from pglast import ast,parse_sql
from pglast.stream import RawStream
ROOT=Path(__file__).resolve().parents[1];TASK=ROOT.parent;sys.path.insert(0,str(ROOT/'scripts'))
import remaining_app_read13_protocol as P
M=runpy.run_path(str(ROOT/'scripts/sql-review/run-remaining-app-read13-rehearsal.py'))
spec=importlib.util.spec_from_file_location('read13_generator',ROOT/'scripts/prepare-remaining-app-read13-rehearsal.py');G=importlib.util.module_from_spec(spec);spec.loader.exec_module(G)
# Only the old offline pipe/ACK machinery and SQL expression engine are reused.
# No production factory, coordinator, Session, qualifier or proof is replaced.
for relative,wanted in G.OFFLINE_ONLY_INPUTS.items():P.need(P.sha((ROOT/relative).read_bytes())==wanted,'OFFLINE_SUPPORT_SOURCE_DRIFT')
OLD=runpy.run_path(str(ROOT/'scripts/check-app-write-two-control-coordinator.py'))
CID='a'*64;CANARY='READ13_PRIVATE_PASSWORD_SECRET_STDERR_CANARY'
OFFLINE_NATIVE='context/reconciliation/local-f0-run-assets/1110fa4-native-4c894dba/evidence/native-before.json'

class Transport(OLD['Transport']):
 def __init__(self,packet,files):
  self.packet=packet;self.events=[];self.models=[];self.sequence=0;self.now=0.;self.rows={table:{} for table in packet['setup_expected_counts']};self.disabled=set();self.coordinator=None;self.other_clients=0;self.close_failure=False;self.issued={};self.lost_fixture_ack=False
  self.application=(ROOT/M['APPLICATION']).read_text();self.acl=json.loads((ROOT/'context/reconciliation/foundation-sql-draft-access.json').read_bytes());self.by_table={row['object']:key for key,row in packet['models'].items()};self.policies={}
  P.need(P.sha(self.application.encode())==P.APPLICATION_SHA,'CANONICAL_SQL_POLICY_SOURCE')
  for statement in parse_sql(self.application):
   policy=statement.stmt
   if not isinstance(policy,ast.CreatePolicyStmt)or not any(role.rolename=='wa_app_runtime'for role in policy.roles):continue
   expression=policy.with_check if policy.cmd_name=='insert'else policy.qual
   if isinstance(expression,ast.FuncCall)and expression.funcname[-1].sval=='row_allowed':self.policies[self.table(policy.table),policy.cmd_name.upper()]=expression
  self.baseline_sql=files;self.clock_origin=datetime(2026,11,20,12,tzinfo=timezone.utc);self.scope=[];self.fail_group=None;self.extra_projection=False;self.invalid_closure=None;self.mutate_native=None;self.grant_expression_cache={}
  body=re.search(r'CREATE FUNCTION platform_private\.protected_scope\(.*?AS\s+(\$[a-z_0-9]*\$)(.*?)\1;',self.application,re.S)[2]
  # Every modeled route is projected from an actual canonical IF expression.
  for condition in re.findall(r'^IF (.*?) THEN RETURN true; END IF;$',body,re.M):self.scope.append(parse_sql('SELECT '+condition)[0].stmt.targetList[0].val)
  assert len(self.scope)>390
 def values(self,session):
  # Cache expression parsing only, never RLS/currentness/rowset verdicts. Each
  # mock instance owns its bounded cache; every SQL expression is in the key.
  expressions=session.bound['values'];key=tuple(sorted(expressions.items()))
  if key not in self.grant_expression_cache:
   assert len(self.grant_expression_cache)<256,'FINITE_OFFLINE_EXPRESSION_CACHE'
   self.grant_expression_cache[key]={name:self.expression(parse_sql('SELECT '+value)[0].stmt.targetList[0].val,session)for name,value in expressions.items()}
  return deepcopy(self.grant_expression_cache[key])
 def expression(self,node,session=None,row=None,ctes=None):
  if isinstance(node,(tuple,list)):return [self.expression(x,session,row,ctes) for x in node]
  if isinstance(node,ast.SetToDefault):return None
  if isinstance(node,ast.ColumnRef):
   fields=[x.sval for x in node.fields];key='.'.join(fields)
   if row is not None and key in row:return row[key]
   return super().expression(node,session,row,ctes)
  if isinstance(node,ast.TypeCast):
   value=self.expression(node.arg,session,row,ctes);kind=node.typeName.names[-1].sval
   if kind in ('jsonb','json') and isinstance(value,str):return json.loads(value)
   if kind=='text' and isinstance(value,dict):return P.canonical(value)
   if kind=='interval':return ('months',int(value.split()[0])) if 'month' in value else float(value.split()[0])*(86400 if 'day' in value else 1)
   if kind=='timestamptz' and value is not None:return str(value)
   return value
  if isinstance(node,ast.A_Expr):
   left=self.expression(node.lexpr,session,row,ctes);right=self.expression(node.rexpr,session,row,ctes);op=node.name[0].sval
   if node.kind.name in ('AEXPR_OP_ANY','AEXPR_IN'):return (left in right) if op=='=' else (left not in right)
   if op in ('<>','!='):return left!=right
   if op=='||':return str(left)+str(right)
   if op=='+' and isinstance(left,str) and isinstance(right,tuple) and right[0]=='months':
    stamp=datetime.fromisoformat(left);month=stamp.month-1+right[1];return stamp.replace(year=stamp.year+month//12,month=month%12+1).isoformat()
   if op=='+' and isinstance(left,str) and isinstance(right,(float,int)):return (datetime.fromisoformat(left)+timedelta(seconds=right)).isoformat()
   if op=='-' and isinstance(left,str) and isinstance(right,(float,int)):return (datetime.fromisoformat(left)-timedelta(seconds=right)).isoformat()
  if isinstance(node,ast.FuncCall):
   name=node.funcname[-1].sval
   if name=='transaction_timestamp':return self.timestamp()
   if name=='clock_timestamp':return self.timestamp()
   if name=='to_char':return datetime.fromisoformat(self.timestamp()).strftime('%Y-%m-%dT%H:%M:%S.%fZ')
   if name=='timezone':return self.expression(node.args[1],session,row,ctes)
   if name=='date_trunc':return self.clock_origin.replace(day=1,hour=0,minute=0,second=0,microsecond=0).isoformat()
   if name=='current_setting':
    settings={'server_version_num':'170011','log_statement':'none','log_min_error_statement':'panic','password_encryption':'scram-sha-256'};key=self.expression(node.args[0],session,row,ctes);assert key in settings,'UNREGISTERED_SETTING';return settings[key]
   if name=='jsonb_build_array':return [self.expression(x,session,row,ctes) for x in node.args]
   if name=='context_allows':
    args=[self.expression(x,session,row,ctes) for x in node.args];g=self.values(session)
    return tuple(args)==tuple(g[k] for k in ('owner_module_id','action','target_kind','target_id','purpose'))
   if name=='jsonb_agg':
    values=[self.expression(node.args[0],session,r,ctes) for r in (row or {}).get('_aggregate',[])];return sorted(values) if values else None
  return super().expression(node,session,row,ctes)
 def allowed(self,session,table,row,verb,fields=None):
  if not session.bound:return False
  grant_row=self.rows['platform.database_action_grant'].get(session.bound['id']);g=self.values(session)
  if not grant_row or grant_row['revoked_at'] is not None or datetime.fromisoformat(grant_row['expires_at'])<=self.clock_origin+timedelta(seconds=self.now):return False
  model=self.by_table[table];key=row['id'];caps=g['allowed_fields']
  if model==g['target_kind'] and key!=g['target_id']:return False
  env={**{'g.'+k:v for k,v in g.items()},'model_name':model,'row_key':key,'verb':verb}
  if not any(self.expression(condition,session,env) for condition in self.scope):return False
  policy=self.policies.get((table,verb))
  if policy is None:return False
  owner=self.expression(policy.args[0],session,row)
  if owner!=g['owner_module_id'] and not(owner=='platform_integration_owner' and model in ('RuntimeWorkItem','RuntimeAttempt')):return False
  required=fields if fields is not None else self.expression(policy.args[4],session,row)
  if any(model+'/'+key+'/'+verb+'/'+f not in caps for f in required):return False
  revision=self.expression(policy.args[5],session,row)
  if revision is not None and model+'/'+key+'/revision/'+str(revision) not in caps:return False
  return revision is None or model!=g['target_kind'] or key!=g['target_id'] or str(g['source_generation'])==str(revision)
 def select(self,node,session,ctes=None):
  if node.fromClause and isinstance(node.fromClause[0],ast.RangeSubselect):
   selected=node.fromClause[0].subquery;table=self.table(selected.fromClause[0]);rows=[r for r in self.view(session,table).values() if self.visible(session,table,r) and (selected.whereClause is None or self.expression(selected.whereClause,session,r))]
   expected=self.policies[table,'SELECT'].args[4];columns=[x.val.fields[-1].sval for x in selected.targetList]
   assert len(columns)==len(self.expression(expected,session,rows[0] if rows else {})),'FULL_ROLE_VISIBLE_SELECT_PROJECTION'
   return self.expression(node.targetList[0].val,session,{'_aggregate':rows})
  return super().select(node,session,ctes)
 def statement(self,node,session):
  if isinstance(node,ast.InsertStmt):
   table=self.table(node.relation);values={col.name:self.expression(value,session) for col,value in zip(node.cols,node.selectStmt.valuesLists[0])};values['mutation_transaction_id']=session.backend['xid'];values['created_at']=self.timestamp(.001)
   if 'display_order' in values and values['display_order'] is None:values['display_order']=0
   if table=='platform.database_action_grant':values['created_at']=self.timestamp(.002);self.issued[values['id']]=values
   if session.role=='wa_app_runtime' and not self.allowed(session,table,values,'INSERT'):raise OLD['SqlFailure']('42501','new row violates row-level security policy for table "'+table.split('.')[1]+'"')
   if table in ('app.track_usage_events','app.track_usage_counters') and (table,'usage_adapter_gate') not in self.disabled:raise OLD['SqlFailure']('0A000','fixture usage adapter remains enabled')
   if table=='app.track_subscription_events' and (table,'enrollment_commit') not in self.disabled:raise OLD['SqlFailure']('42501','fixture event enrollment remains enabled')
   if values['id'] in self.view(session,table):raise OLD['SqlFailure']('23505','duplicate fixture key')
   session.pending.setdefault(table,{})[values['id']]=values
   return {'created_at':values['created_at']} if table=='platform.database_action_grant' else []
  if isinstance(node,ast.UpdateStmt):
   table=self.table(node.relation);assert table=='platform.database_action_grant' and session.role=='wa_context_issuer';changed=[]
   for key,row in self.view(session,table).items():
    if self.expression(node.whereClause,session,row):
     row['revoked_at']=self.timestamp(.003);row['mutation_transaction_id']=session.backend['xid'];session.pending.setdefault(table,{})[key]=row;changed.append(row)
   assert len(changed)==1;return {'revoked_at':changed[0]['revoked_at']}
  return super().statement(node,session)
 def commit(self,session):
  # The fixture model checks real statement rows and same-transaction group,
  # never packet.case.expected_records. It does not claim PostgreSQL behavior.
  for customer in session.pending.get('app.customer_profiles',{}).values():
   key=customer['id'];q=[r for r in session.pending.get('platform.runtime_command_receipt',{}).values() if r['subject_scope']=='CustomerProfile:'+key];h=[r for r in session.pending.get('app.customer_profile_lifecycle_event',{}).values() if r['customer_profile_id']==key];ev=[r for r in session.pending.get('platform.owner_mutation_evidence',{}).values() if r['aggregate_id']==key];out=[r for r in session.pending.get('platform.runtime_outbox_message',{}).values() if r['aggregate_id']==key]
   if not(session.flushed and len(q)==len(h)==len(ev)==1 and len(out)==2 and q[0]['state']=='committed' and {r['name'] for r in out}=={'customer.lifecycle_changed.v1','assignDefaultFreeTrack.v1'}):raise OLD['SqlFailure']('P0001','incomplete real-group model')
  for table,values in session.pending.items():self.rows[table].update(deepcopy(values))
  session.pending={};session.active=False;self.events.append(('COMMIT',session.role,session.backend['pid'],session.backend['xid']))
 def model(self,role,c):
  self.coordinator=c;self.sequence+=1;sequence=self.sequence;vm=self
  class Model:
   def __init__(self):self.closed=False;self.role=role;self.active=False;self.bound=None;self.pending={};self.flushed=False;self.process=types.SimpleNamespace(returncode=None)
   def begin(self,isolation):self.active=True;self.isolation=isolation
   def capture(self):
    if not hasattr(self,'backend'):self.backend={'login':role,'current_user':role,'database':'wa_p0c_rehearsal','isolation':self.isolation,'pid':str(5000+sequence),'xid':str(20000+sequence),'started':vm.timestamp(),'clock':vm.timestamp()}
    return deepcopy(self.backend)
   def call(self,text):
    vm.events.append(('SQL',role,text));rows=[]
    try:
     if text.startswith('SELECT pg_current_xact_id()'):return ['t'],True,''
     if text.startswith('SELECT platform_private.bind_request_context('):
      secret=re.search(r"\('([^']+)'\)",text)[1];instance=next(v for v in c.instances.values() if v['secret']==secret);self.bound=instance;g=vm.values(self);stored=vm.rows['platform.database_action_grant'][instance['id']]
      assert not any(s.role=='wa_context_issuer' and not s.closed for s in vm.models),'ISSUER_COMMIT_AND_CLOSE_BEFORE_BIND'
      if g['security_generation']!=0 or stored['revoked_at'] is not None or datetime.fromisoformat(stored['expires_at'])<=vm.clock_origin+timedelta(seconds=vm.now):raise OLD['SqlFailure']('42501','invalid, stale or unsupported context','bind_request_context')
      return [],True,''
     if vm.fail_group is not None and vm.fail_group==c.evidence.value['current_case']:raise OLD['SqlFailure']('P0001',CANARY)
     for raw in parse_sql(text):
      node=raw.stmt
      if isinstance(node,ast.TransactionStmt):
       if node.kind.name=='TRANS_STMT_COMMIT':vm.commit(self)
       else:self.pending={};self.active=False
       continue
      if isinstance(node,ast.ConstraintsSetStmt):self.flushed=True;continue
      if isinstance(node,ast.AlterTableStmt):
       identity=(vm.table(node.relation),node.cmds[0].name);assert identity in {(t['definition']['table'],t['definition']['name']) for t in c.packet['fixture_plan']['trigger_setup_allowlist']},'EXACT15_SOURCE_IDENTITIES_ONLY'
       if 'DISABLE' in RawStream()(node):vm.disabled.add(identity)
       else:vm.disabled.discard(identity)
       continue
      result=vm.statement(node,self)
      if isinstance(node,(ast.SelectStmt,ast.InsertStmt,ast.UpdateStmt)) and result is not None and (isinstance(node,ast.SelectStmt) or node.returningList):rows.append(json.dumps(result) if isinstance(result,(dict,list)) else str(result))
     return rows,True,''
    except OLD['SqlFailure'] as error:self.pending={};self.active=False;self.process.returncode=3;return rows,False,vm.diagnostic(error)
   def close(self):
    self.closed=True;self.pending={};self.active=False
    if self.process.returncode is None:self.process.returncode=0
    return self.process.returncode
  model=Model();self.models.append(model);return model
 def raw(self,args,**kwargs):
  text=kwargs.get('input','');c=self.coordinator
  if c is None:
   frame=inspect.currentframe().f_back
   while frame:
    candidate=frame.f_locals.get('self')
    if candidate is not None and type(candidate).__name__=='Coordinator' and hasattr(candidate,'instances'):c=candidate;self.coordinator=c;break
    frame=frame.f_back
  def result(value,raw=False):return types.SimpleNamespace(returncode=0,stdout=str(value) if raw else json.dumps(value),stderr='')
  if text.startswith('SELECT current_setting('):return result('t'if self.expression(parse_sql(text)[0].stmt.targetList[0].val)else'f',True)
  if text.startswith('SELECT NOT EXISTS('):
   expected="SELECT NOT EXISTS(SELECT 1 FROM pg_auth_members WHERE member='wa_schema_owner'::regrole AND roleid=ANY(ARRAY['wa_private_helper_owner'::regrole,'wa_customer_verifier'::regrole,'wa_track_verifier'::regrole])) AND NOT has_schema_privilege('wa_private_helper_owner','platform_private','CREATE') AND NOT has_schema_privilege('wa_customer_verifier','platform_private','CREATE') AND NOT has_schema_privilege('wa_track_verifier','platform_private','CREATE');"
   assert RawStream()(parse_sql(text)[0])==RawStream()(parse_sql(expected)[0]),'FINALIZATION_PREDICATE_MUTATION';return result('t',True)
  if '-U' not in args or 'PGPASSWORD' in args or 'pg_hba_file_rules' in text or 'FROM pg_authid' in text or "'auth',system_user" in text or text.startswith('SELECT count(*) FROM pg_stat_activity WHERE pid='):return super().raw(args,**kwargs)
  if "'other_clients'" in text:
   return result(self.invalid_closure if self.invalid_closure is not None else {'other_clients':sum(not x.closed for x in self.models)+self.other_clients})
  if 'workinants.native-catalog.v1' in text:
   value=deepcopy(c.native)
   for row in value['triggers']:
    if (row['table_name'],row['name']) in self.disabled:row['enabled']='D'
   if self.mutate_native:self.mutate_native(value)
   return result(value)
  if "'issuer_owned'" in text:
   ids=re.findall(r" FROM platform.database_action_grant g WHERE g.id='([^']+)'",text);stored=[self.rows['platform.database_action_grant'][key] for key in ids];exact=True
   for identity in ids:
    instance=next(v for v in c.instances.values() if v['id']==identity);expected={k:self.expression(parse_sql('SELECT '+v)[0].stmt.targetList[0].val) for k,v in instance['values'].items()};actual=self.rows['platform.database_action_grant'][identity];exact=exact and all(expected[k]==actual[k] and text.count('g.'+k+' IS NOT DISTINCT FROM (')==len(ids) for k in expected)
   return result({'count':len(ids),'exact':exact,'issuer_owned':all(v['issuer_service']=='wa_context_issuer' for v in stored),'unexpired':all(datetime.fromisoformat(v['expires_at'])>self.clock_origin+timedelta(seconds=self.now) for v in stored)})
  if text.startswith('SELECT clock_timestamp()>expires_at'):
   self.now+=3;identity=re.search(r"WHERE id='([^']+)'",text)[1];row=self.rows['platform.database_action_grant'][identity];return result('t' if self.clock_origin+timedelta(seconds=self.now)>datetime.fromisoformat(row['expires_at']) else 'f',True)
  if text==c.text('complete-state-observe.sql'):
   assert not any(not x.closed for x in self.models),'STATE_BEFORE_GLOBAL_CLOSURE'
   facts={t:{'count':len(rows),'rows_sha256':P.digest(sorted(rows.values(),key=P.canonical))} for t,rows in self.rows.items()};return result(self.project_observer(text,'complete-state-observe.sql',facts))
  if text==c.text('fixture-coherence-observe.sql'):
   assert RawStream()(parse_sql(text)[0])==RawStream()(parse_sql(self.baseline_sql['fixture-coherence-observe.sql'])[0]),'COHERENCE_SQL_PROJECTION_MUTATION'
   count=sum(len(v) for k,v in self.rows.items() if k!='platform.database_action_grant');good=count==48
   for expected in self.packet['fixture_plan']['fixture_rows']:
    actual=self.rows[expected['table']].get(expected['values']['id']);good=good and actual is not None
    if actual is None:continue
    for column,value in expected['values'].items():
     if isinstance(value,dict):
      if any(k in value for k in ('source_default_or_guard','server_value','server_expression','PG_jsonb_text_UTF8_SHA256')):continue
      if column=='result_body':good=good and actual[column]['value']['receipt']['semanticKey']==value['value']['receipt']['semanticKey'];continue
     good=good and actual.get(column)==value
   return result({'rows':count,'all_source_values_match':bool(good),'usage_source_window_sum_limit_match':bool(good and all(r.get('used_quantity',1)==1 for r in self.rows['app.track_usage_counters'].values()))})
  if "'same_actual_group_xid'" in text:
   selected=re.findall(r"SELECT mutation_transaction_id FROM ([a-z_.]+) WHERE id='([^']+)'",text);rows=[self.rows[t][identity] for t,identity in selected];xid=re.search(r"bool_and\(mutation_transaction_id='([^']+)'",text)[1];return result({'count':len(rows),'same_actual_group_xid':all(r['mutation_transaction_id']==xid for r in rows)})
  raise AssertionError('UNREGISTERED_READ13_PROCESS_BOUNDARY')

class CoordinatorTests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):cls.files,cls.packet=G.build()
 def setUp(self):
  for name in ('run','Popen','call','check_call','check_output'):
   guard=patch.object(subprocess,name,side_effect=AssertionError('UNMOCKED_PROCESS_FORBIDDEN'));guard.start();self.addCleanup(guard.stop)
  guard=patch.object(socket,'create_connection',side_effect=AssertionError('NETWORK_FORBIDDEN'));guard.start();self.addCleanup(guard.stop)
  self.temp=tempfile.TemporaryDirectory(prefix='read13-offline-',dir=TASK);self.addCleanup(self.temp.cleanup);self.directory=Path(self.temp.name);self.context=M['compiled']((ROOT/M['CONTEXT']).read_bytes(),M['CONTEXT']);self.context['load_helpers']({p:(ROOT/p).read_bytes() for p in M['HELPERS']});self.base=M['compiled']((ROOT/M['BASE']).read_bytes(),M['BASE']);self.protocol=vars(P);self.native=json.loads((ROOT/OFFLINE_NATIVE).read_bytes());self.vm=Transport(self.packet,self.files)
  guard=patch.object(subprocess,'run',side_effect=self.vm.raw);guard.start();self.addCleanup(guard.stop);guard=patch.object(subprocess,'Popen',side_effect=self.vm.popen);guard.start();self.addCleanup(guard.stop)
 def actual(self):
  pins={p:P.sha((ROOT/p).read_bytes()) for p in self.packet['source_files_sha256']};plan={'run_id':self.packet['fixture_run_id'],'immutable_container_id':CID,'source_commit':'b'*40,'source_tree':'c'*40,'packet_sha256':'d'*64,'packet_files_sha256':pins,'reviewed_packet_sha256':P.sha(self.files['fixtures.json'].encode()),'reviewed_content_sha256':self.packet['source_only_packet_sha256']}
  image=self.context['HOST']['preparation']['IMAGE'];target={'run_id':plan['run_id'],'target':{'container_name':'wa-p0c-read13-offline','volume_name':'wa-p0c-read13-offline-data','database':'wa_p0c_rehearsal','image':image,'network':'none','labels':{'workinants.rehearsal':'p0c-local-f0','workinants.rehearsal.run':plan['run_id']},'bootstrap_secret_host_path':str(self.directory/'bootstrap-password')}}
  evidence=M['Evidence'](self.directory/'evidence',plan,self.packet);coordinator=M['coordinator_type'](self.context,self.base)(plan,self.packet,self.native,target,evidence,self.protocol,{k:v for k,v in self.files.items() if k.endswith('.sql')});self.vm.coordinator=coordinator;return coordinator,evidence
 def failed_business_write(self,old_transaction=None,receipt_io=False):
  c,e=self.actual();case=next(x for x in self.packet['cases']if x['name']=='RuntimeEffectReceipt/positive/A');e.value.update(current_stage='FINITE_READ13_PROTOCOL',current_case=case['name']);ordinary=OLD['Input'].write;opened=Path.open;attempted=[]
  def write(stream,text):
   if 'SELECT 987654321;'in text:attempted.append(True);raise OSError(CANARY)
   return ordinary(stream,text)
  def opening(path,*args,**kwargs):
   if receipt_io and attempted and path==e.path.with_suffix('.json.tmp'):raise OSError(CANARY)
   return opened(path,*args,**kwargs)
  with patch.object(OLD['Input'],'write',write),patch.object(Path,'open',opening):
   if old_transaction is None:
    with self.assertRaises(OSError):c.transaction(case['name'],'wa_app_runtime','SELECT 987654321;',self.packet['grants'][case['grant']])
   else:
    with patch.object(type(c),'transaction',old_transaction),self.assertRaises(OSError):c.transaction(case['name'],'wa_app_runtime','SELECT 987654321;',self.packet['grants'][case['grant']])
  row=next(x for x in e.value['operations']if x['stage']=='ACTUAL_TRANSACTION')
  self.assertTrue(attempted);self.assertTrue(row['operation_closed']);self.assertTrue(row['global_closure_confirmed']);self.assertTrue(all(x.closed for x in self.vm.models));self.assertEqual(e.value['results'],[]);self.assertNotIn(CANARY,P.canonical(e.value))
  return c,e,row
 def assert_unreceived_business(self,row):
  self.assertEqual(row.get('observation_stage'),'BUSINESS');self.assertIs(row.get('response_received'),False);self.assertIs(row.get('response_shape_valid'),False)
  for key in('acknowledged','stderr_present','stdout_records'):self.assertIsNone(row.get(key))
 def test_business_process_write_throw_has_no_stale_bind_observation(self):
  c,e,row=self.failed_business_write();self.assert_unreceived_business(row);self.assertTrue(row['client_exit_received']);self.assertEqual(e.value['unexpected'][0]['code'],'READ13_UNEXPECTED_OPERATION_FAILURE')
 def test_original_business_failure_is_primary_before_receipt_IO(self):
  c,e,row=self.failed_business_write(receipt_io=True);self.assert_unreceived_business(row);self.assertFalse(e.value['evidence_complete']);self.assertTrue(e.failed)
  self.assertEqual(e.value['unexpected'][0]['code'],'READ13_UNEXPECTED_OPERATION_FAILURE');self.assertTrue(any(x['code']=='SANITIZED_EVIDENCE_WRITE_UNCONFIRMED'for x in e.value['unexpected']))
 def test_only_old_response_reuse_restoration_fails_new_regression(self):
  raw=(TASK/'read13-before-two-evidence-fixes-Root-preserved-20261120/ROOT/scripts/sql-review/run-remaining-app-read13-rehearsal.py').read_bytes();self.assertEqual(P.sha(raw),'5d6baaef489bfaefb97e1585cbeeb37709c207c02544580725f01abc6ea868da')
  method=next(n for n in python_ast.walk(python_ast.parse(raw))if isinstance(n,python_ast.FunctionDef)and n.name=='transaction');namespace=dict(M['coordinator_type'].__globals__)
  exec(compile(python_ast.Module(body=[method],type_ignores=[]),'<only-preserved-old-response-reuse>','exec'),namespace)
  c,e,row=self.failed_business_write(old_transaction=namespace['transaction'])
  self.assertTrue(row['acknowledged']);self.assertEqual(row['stdout_records'],0);self.assertFalse(row['stderr_present'])
  with self.assertRaises(AssertionError):self.assert_unreceived_business(row)
 def test_fixed_transaction_response_types_unknown_exit_and_secret_exclusion(self):
  for response in(None,{},(CANARY,True,''),([],1,''),([],True,{'raw':CANARY}),([],True,'')):
   value=P.transaction_observation('BUSINESS',True,response,True,99);P.validate_transaction_observation(value);self.assertIsNone(value['exit_code']);self.assertEqual(value['client_exit_class'],'OTHER');self.assertNotIn(CANARY,P.canonical(value))
   if response!=([],True,''):
    self.assertFalse(value['response_shape_valid']);self.assertIsNone(value['acknowledged']);self.assertIsNone(value['stdout_records']);self.assertIsNone(value['stderr_present'])
  for code in(True,False,0.0,-1,None):
   value=P.transaction_observation('BIND',False,None,True,code);P.validate_transaction_observation(value);self.assertEqual(value['client_exit_class'],'OTHER');self.assertIsNone(value['exit_code'])
  value=P.transaction_observation('NOT_STARTED',False,None,False,None)
  for key,bad in(('response_received',0),('response_shape_valid',1),('exit_code',False),('client_exit_class',CANARY),('observation_stage',CANARY),('acknowledged',True)):
   mutant=deepcopy(value);mutant[key]=bad
   with self.assertRaises(P.HeldFailure):P.validate_transaction_observation(mutant)
 def test_setup_commit_observation_is_business_response_and_restores(self):
  c,e=self.disabled_world();row=next(x for x in e.value['operations']if x['stage']=='ACTUAL_TRANSACTION');self.assertEqual(row['observation_stage'],'BUSINESS');self.assertTrue(row['response_received']);self.assertTrue(row['response_shape_valid']);self.assertTrue(row['client_exit_received']);self.assertEqual(row['client_exit_class'],'KNOWN');self.assertTrue(row['acknowledged']);self.assertEqual(row['stdout_records'],0);self.assertFalse(row['stderr_present']);M['finish_component'](c,e,c.plan);self.assertEqual(self.vm.disabled,set())
 def test_control_rebind_process_write_failure_has_own_fresh_stage(self):
  c,e=self.actual();case=next(x for x in self.packet['cases']if x['control']=='revoked_before_action');e.value.update(current_stage='FINITE_READ13_PROTOCOL',current_case=case['name']);ordinary=OLD['Input'].write;binds=[]
  def write(stream,text):
   if 'SELECT platform_private.bind_request_context('in text:
    binds.append(True)
    if len(binds)==2:raise OSError(CANARY)
   return ordinary(stream,text)
  with patch.object(OLD['Input'],'write',write),self.assertRaises(OSError):c.transaction(case['name'],'wa_app_runtime',self.files[case['sql']],self.packet['grants'][case['grant']],control='revoked_before_action')
  row=next(x for x in e.value['operations']if x['stage']=='ACTUAL_TRANSACTION');self.assertEqual(row['observation_stage'],'REVOKED_REBIND');self.assertFalse(row['response_received']);self.assertIsNone(row['acknowledged']);self.assertIsNone(row['stdout_records']);self.assertIsNone(row['stderr_present']);self.assertTrue(row['operation_closed']);self.assertTrue(row['global_closure_confirmed']);self.assertTrue(all(x.closed for x in self.vm.models));self.assertFalse(e.value['results']);self.assertNotIn(CANARY,P.canonical(e.value))
 def test_real_ctx_session_full_source_fixture_then82_finite_protocols(self):
  c,e=self.actual();c.execute();M['finish_component'](c,e,c.plan);self.assertEqual(e.value['status'],'PASS_FINITE_REMAINING13_APP_SELECT_SQL_SUBSET_ONLY');self.assertEqual(len(e.value['results']),82);self.assertEqual(len(c.instances),79);self.assertEqual(len({x['claim'] for x in e.value['results'] if x['claim']}),13);self.assertTrue(all(m.closed for m in self.vm.models));self.assertEqual(self.vm.disabled,set());self.assertEqual(sum(len(v) for t,v in self.vm.rows.items() if t!='platform.database_action_grant'),48);self.assertTrue(e.value['source_packet_unchanged_after']);self.assertFalse(e.failed)
 def test_pending_gate_precedes_any_compilation_or_process(self):
  c,e=self.actual();plan=dict(c.plan);plan.update(schema='workinants.remaining-app-read13-run.v1',scope='REVIEWED_REMAINING13_APP_SELECT_ONLY',scenario_names=[x['name'] for x in self.packet['cases']],native_snapshot={},native_comparison={},native_attestation={},target_manifest=c.target)
  validation={'independent_source_review':{'decision':'PENDING'}};path=self.directory/'pending.json';path.write_text(json.dumps(validation));pins=dict(plan['packet_files_sha256']);pins[M['VALIDATION']]=P.sha(path.read_bytes());plan['packet_files_sha256']=pins;plan['packet_sha256']=P.sha(''.join(k+'\0'+pins[k]+'\n' for k in sorted(pins)).encode())
  original=M['source_path']
  with patch.dict(M['load_inputs'].__globals__,source_path=lambda p:path if p==M['VALIDATION'] else original(p)),patch.dict(M['load_inputs'].__globals__,compiled=lambda *a,**k:(_ for _ in ()).throw(AssertionError('COMPILATION_FORBIDDEN'))):
   with self.assertRaises(M['HeldFailure']) as failure:M['load_inputs'](plan)
  self.assertEqual(failure.exception.code,'INDEPENDENT_READ13_SOURCE_REVIEW_REQUIRED');self.assertEqual(self.vm.models,[])
 def test_global_closure_strict_shapes_and_unconfirmed_retention(self):
  for bad in ([],{'other_clients':False},{'other_clients':0.0},{'other_clients':-1},{'other_clients':0,'CANARY':CANARY}):
   c,e=self.actual() if not hasattr(self,'one') else self.one;self.one=(c,e);self.vm.invalid_closure=bad
   with self.assertRaises(M['HeldFailure']):c.global_closure()
   row=e.value['operations'][-1];self.assertFalse(row['all_other_clients_absent']);self.assertNotIn(CANARY,P.canonical(e.value))
 def test_throwing_closure_still_records_fixed_unconfirmed(self):
  c,e=self.actual()
  with patch.object(c,'raw',side_effect=RuntimeError(CANARY)):
   with self.assertRaises(RuntimeError):c.global_closure()
  self.assertEqual(e.value['operations'][-1]['observation_completed'],False);self.assertNotIn(CANARY,P.canonical(e.value))
 def test_constructor_failure_still_attempts_global_before_verdict(self):
  c,e=self.actual();calls=[]
  with patch.object(c,'session',side_effect=RuntimeError(CANARY)),patch.object(c,'global_closure',side_effect=lambda:calls.append('global')):
   with self.assertRaises(RuntimeError):c.transaction('read','wa_app_runtime','SELECT 1;')
  self.assertEqual(calls,['global']);self.assertEqual(e.value['results'],[])
 def test_issuer_timestamp_trigger_overwrite_is_exactly_retained(self):
  c,e=self.actual();c.counts=dict.fromkeys(c.counts,0);template=next(iter(self.packet['grants'].values()));session=c.session('wa_app_runtime');session.begin('read committed');backend=session.capture()
  try:key=c.issue(template,backend);self.assertIn('.002',c.instances[key]['values']['created_at']);c.retention([key],True)
  finally:session.close();c.global_closure()
 def test_expiry_response_after_deadline_never_qualifies(self):
  c,e=self.actual();c.instances[1]={'values':{'id':"'00000000-0000-4000-8000-000000000001'::uuid"}}
  with patch.object(time_module(),'monotonic',side_effect=[0,1,46]),patch.object(subprocess,'run',return_value=types.SimpleNamespace(returncode=0,stdout='t',stderr='')):
   with self.assertRaises(M['HeldFailure']) as failure:c.wait_expired(1)
  self.assertEqual(failure.exception.code,'SERVER_EXPIRY_BUDGET_EXHAUSTED');self.assertFalse(any(r['stage']=='ACTUAL_SERVER_EXPIRY' for r in e.value['operations']))
 def test_restore_identity_rejects_unknown_disabled_guard_or_source_drift(self):
  for mutation in ('other','body','internal'):
   actual=deepcopy(self.native);row=next(t for t in actual['triggers'] if t['internal'] is (mutation=='internal'))
   if mutation=='body':row['function_body_sha256']='0'*64
   else:row['enabled']='D'
   with self.assertRaises(P.HeldFailure):P.restoration_identity(self.native,actual,self.packet['fixture_plan']['trigger_setup_allowlist'],True)
 def test_offline_cache_full_expression_tuple_and_no_mutable_alias(self):
  session=types.SimpleNamespace(bound={'values':{'source_generation':'7','security_generation':'19','allowed_fields':"ARRAY['RuntimeEffectReceipt/x/revision/0']::text[]"}})
  first=self.vm.values(session);self.assertEqual(first['source_generation'],7);first['allowed_fields'].append(CANARY)
  self.assertNotIn(CANARY,self.vm.values(session)['allowed_fields']);self.assertEqual(len(self.vm.grant_expression_cache),1)
  session.bound['values']['source_generation']='8';self.assertEqual(self.vm.values(session)['source_generation'],8);self.assertEqual(len(self.vm.grant_expression_cache),2)
  session.bound['values']['allowed_fields']="ARRAY['RuntimeEffectReceipt/x/revision/1']::text[]";self.assertEqual(self.vm.values(session)['allowed_fields'],['RuntimeEffectReceipt/x/revision/1']);self.assertEqual(len(self.vm.grant_expression_cache),3)
 def test_source_diagnostic_projection_rejects_unknown_helper_fields_or_types(self):
  text=self.vm.diagnostic(OLD['SqlFailure']('42501','invalid, stale or unsupported context','bind_request_context'));application=self.vm.application
  value=self.context['binder_diagnostic'](text,'invalid, stale or unsupported context',application);self.assertTrue(M['binder_projection'](value,application)['matched'])
  for key,wrong in [('CANARY',CANARY),('source_body_line',True),('source_body_sha256','0'*64),('sqlstate','P0001'),('classification',CANARY)]:
   bad=deepcopy(value);bad[key]=wrong
   with self.assertRaises(M['HeldFailure']):M['binder_projection'](bad,application)
 def disabled_world(self):
  c,e=self.actual();c.bypass_open=True;e.stage('EXACT15_RESTORATION_OBLIGATION_RECORDED');result=c.transaction('DISABLE_EXACT15','postgres',c.text('fixture-disable-exact15.sql').removeprefix('BEGIN;\n'));self.assertEqual(result['code'],0);self.assertEqual(len(self.vm.disabled),15);return c,e
 def test_real_finally_restores_all15_despite_persistent_report_IO(self):
  c,e=self.disabled_world();e.stop('ORIGINAL_OPERATION_STOP');original=deepcopy(e.value['unexpected'][0])
  with patch.object(Path,'open',side_effect=OSError(CANARY)):M['finish_component'](c,e,c.plan)
  self.assertEqual(self.vm.disabled,set());self.assertFalse(c.bypass_open);self.assertTrue(e.failed);self.assertFalse(e.value['evidence_complete']);self.assertEqual(e.value['unexpected'][0],original);self.assertEqual(e.value['results'],[]);self.assertNotIn(CANARY,P.canonical(e.value));self.assertTrue(all(m.closed for m in self.vm.models))
 def test_active_or_unknown_global_closure_forbids_every_restoration_DDL(self):
  c,e=self.disabled_world();e.stop('ORIGINAL_OPERATION_STOP');self.vm.other_clients=1;before=len(self.vm.events);M['finish_component'](c,e,c.plan)
  self.assertEqual(len(self.vm.disabled),15);self.assertTrue(c.bypass_open);self.assertFalse(any('ENABLE TRIGGER'in event[2]for event in self.vm.events[before:]if event[0]=='SQL'));self.assertEqual(e.value['results'],[])
 def test_native_source_identity_drift_forbids_restoration_and_discards_values(self):
  c,e=self.disabled_world();e.stop('ORIGINAL_OPERATION_STOP');self.vm.mutate_native=lambda value:value['functions'][0].update(body_sha256='0'*64);before=len(self.vm.events);M['finish_component'](c,e,c.plan)
  self.assertEqual(len(self.vm.disabled),15);self.assertFalse(any('ENABLE TRIGGER'in event[2]for event in self.vm.events[before:]if event[0]=='SQL'));self.assertEqual(e.value['unexpected'][0]['code'],'ORIGINAL_OPERATION_STOP');self.assertEqual(e.value['results'],[])
 def test_lost_disable_commit_ACK_retains_obligation_and_restores_before_stop(self):
  c,e=self.actual();self.vm.lost_fixture_ack=True
  try:c.execute()
  except BaseException as error:e.stop(M['safe_code'](error))
  else:self.fail('Lost commit ACK was accepted')
  M['finish_component'](c,e,c.plan);self.assertEqual(self.vm.disabled,set());self.assertEqual(e.value['results'],[]);self.assertTrue(e.value['fixture_owner_bypass_restored']);self.assertFalse(any(self.vm.rows[table]for table in self.vm.rows));self.assertTrue(all(m.closed for m in self.vm.models))
 def test_expression_cache_never_caches_revocation_or_expiry_decisions(self):
  c,e=self.actual();session=c.session('wa_app_runtime');session.begin('read committed');backend=session.capture()
  try:
   key=c.issue(next(iter(self.packet['grants'].values())),backend);model=self.vm.models[0];model.bound=c.instances[key];self.vm.values(model);stored=self.vm.rows['platform.database_action_grant'][c.instances[key]['id']];row={'id':self.packet['fixture_plan']['fixture_namespace']['preview_ids']['A']['Customer']}
   stored['revoked_at']=self.vm.timestamp();self.assertFalse(self.vm.allowed(model,'app.customer_profiles',row,'SELECT'));stored['revoked_at']=None;self.vm.now=1000;self.assertFalse(self.vm.allowed(model,'app.customer_profiles',row,'SELECT'))
  finally:session.close();c.global_closure()
 def test_source_policy_distinct_security19_root7_and_child_effect_fence0(self):
  # A policy-expression unit, not another fixture protocol or Identity/write
  # qualification. It projects the actual canonical SELECT policy arguments.
  read=next(r for r in self.packet['fixture_plan']['selected_reads']if r['model']=='RuntimeEffectReceipt');context=deepcopy(read['contexts']['A']);customer=context['target_id'];effect=context['expected_ids'][0]
  fields=[f.replace('CustomerProfile/'+customer+'/revision/0','CustomerProfile/'+customer+'/revision/7')for f in context['allowed_fields']]
  values={k:P.quote(context[k])for k in('owner_module_id','action','purpose','target_kind','target_id','principal_user_id')};values.update(source_generation='7',security_generation='19',allowed_fields='ARRAY['+','.join(P.quote(f)for f in fields)+']::text[]')
  identity='00000000-0000-4000-8000-000000000019';session=types.SimpleNamespace(bound={'id':identity,'values':values});self.vm.rows['platform.database_action_grant'][identity]={'revoked_at':None,'expires_at':self.vm.timestamp(300)}
  row={'id':effect,'owner_module_id':'customer_buyer_profile','fence':0,'mutation_transaction_id':'PREVIOUS_COMMITTED_XID'}
  self.assertTrue(self.vm.allowed(session,'platform.runtime_effect_receipt',row,'SELECT'))
  fields.remove('RuntimeEffectReceipt/'+effect+'/revision/0');values['allowed_fields']='ARRAY['+','.join(P.quote(f)for f in fields)+']::text[]';self.assertFalse(self.vm.allowed(session,'platform.runtime_effect_receipt',row,'SELECT'))
  fields.append('RuntimeEffectReceipt/'+effect+'/revision/0');values['allowed_fields']='ARRAY['+','.join(P.quote(f)for f in fields)+']::text[]';customer_row={'id':customer,'revision':7,'mutation_transaction_id':'PREVIOUS_COMMITTED_XID'}
  self.assertTrue(self.vm.allowed(session,'app.customer_profiles',customer_row,'SELECT'));values['source_generation']='8';self.assertFalse(self.vm.allowed(session,'app.customer_profiles',customer_row,'SELECT'));self.assertTrue(self.vm.allowed(session,'platform.runtime_effect_receipt',row,'SELECT'))

def time_module():return M['coordinate'].__globals__['time']
if __name__=='__main__':unittest.main()
