"""Offline-only projection-aware transport mocks. No Docker/database execution."""
from contextlib import redirect_stdout
from copy import deepcopy
import importlib.util
import io
import json
from pathlib import Path
import re
import runpy
import socket
import subprocess
import tempfile
import types
import unittest
from unittest.mock import patch,Mock
import owner_read_control_protocol as P

ROOT=Path(__file__).resolve().parents[1];TASK=ROOT.parent
M=runpy.run_path(str(ROOT/'scripts/sql-review/run-owner-read-control-rehearsal.py'))
spec=importlib.util.spec_from_file_location('_owner_read_mock_generator',ROOT/'scripts/prepare-owner-read-control-rehearsal.py');G=importlib.util.module_from_spec(spec);spec.loader.exec_module(G)
CANARY='PRIVATE_CONTEXT_LEASE_ROW_OR_STDERR_CANARY_DO_NOT_EXPORT'
CID='a'*64

class Transport:
 """Interpret emitted SQL projections and admitted caps, never case.expected."""
 def __init__(self,packet,protocol,context):
  self.packet=packet;self.protocol=protocol;self.context=context;self.events=[];self.coordinator=None;self.sessions=0;self.seeded=False;self.claimed=False;self.failure_case=None;self.close_failure=False;self.mutate_projection=False;self.owner_bypass=False;self.lease_expired=False;self.expire_lease_case=None;self.expire_grant_case=None;self.grant_expired=False
  self.acl=json.loads((ROOT/'context/reconciliation/foundation-sql-draft-access.json').read_bytes())
 def raw(self,args,**options):
  self.events.append(('subprocess.run',options.get('input','')));text=options['input'];c=self.coordinator
  if "'other_clients'" in text:value={'other_clients':0}
  elif "'issuer_owned'" in text and ' UNION ALL ' in text or "'issuer_owned'" in text and 'FROM (SELECT (' in text:
   value={'count':text.count(' FROM platform.database_action_grant g WHERE g.id='),'exact':True,'issuer_owned':True,'unrevoked':True,'unexpired':not self.grant_expired}
  elif text==c.text('complete-state-observe.sql'):
   value={table:{'count':count if self.seeded else 0,'rows_sha256':('b' if self.claimed and table=='platform.runtime_work_item' else 'a')*64} for table,count in self.packet['expected_counts'].items()}
  elif text==c.text('grant-count-observe.sql'):return types.SimpleNamespace(returncode=0,stdout=str(len(c.instances)),stderr='')
  elif text==c.text('fixture-trigger-restore-observe.sql'):value=self.packet['expected_trigger_contract']['observer_expected']
  elif "'exact_live_lease'" in text:value={'work_count':1,'exact_live_lease':self.claimed and not self.lease_expired,'attempts':0,'effects':0,'enrollments':0}
  elif text.startswith('--') and 'workinants.native-catalog.v1' in text or 'workinants.native-catalog.v1' in text:value={**c.native,**({'owner_commit_disabled':True} if self.owner_bypass else {})}
  elif text.startswith('SELECT current_setting(') or text.startswith('SELECT NOT EXISTS('):return types.SimpleNamespace(returncode=0,stdout='t',stderr='')
  else:raise AssertionError('UNREGISTERED_MOCK_SQL_BOUNDARY')
  return types.SimpleNamespace(returncode=0,stdout=json.dumps(value),stderr='')
 def session(self,role,coordinator):
  outer=self;self.coordinator=coordinator;self.sessions+=1;sequence=self.sessions
  class Session:
   def __init__(self):self.role=role;self.closed=False;self.active=False;self.process=types.SimpleNamespace(returncode=None,poll=lambda:self.process.returncode);self.backend=None;self.bound=None
   def begin(self,isolation):outer.events.append((role,'begin'));self.active=True;self.isolation=isolation
   def capture(self):
    self.backend={'login':role,'current_user':role,'database':'wa_p0c_rehearsal','isolation':self.isolation,'pid':str(4000+sequence),'xid':str(10000+sequence),'started':'2026-11-18 12:00:00+00','clock':'2026-11-18 12:00:00+00'};outer.events.append((role,'capture'));return self.backend
   def call(self,text):
    outer.events.append((role,'call',text))
    if text.startswith('INSERT INTO platform.database_action_grant '):return [json.dumps({'created_at':'2026-11-18T12:00:00.001+00:00'})],True,''
    if text.startswith('SELECT pg_current_xact_id()'):return ['t'],True,''
    if text.startswith('SELECT platform_private.bind_request_context('):
     secret=re.search(r"\('([^']+)'\)",text)[1];self.bound=next(x for x in coordinator.instances.values() if x['secret']==secret);return [],True,''
    if text.startswith('SET LOCAL wa.lease_secret='):return [],True,''
    if not text.startswith("SELECT 'WA_OR_BEFORE_"):
     if 'ALTER TABLE app.consent_presentation DISABLE TRIGGER owner_commit;' in text:outer.owner_bypass=True
     if 'ALTER TABLE app.consent_presentation ENABLE TRIGGER owner_commit;' in text:outer.owner_bypass=False
     markers=re.findall(r"SELECT '(WA_[A-Z0-9_]+)';",text);return markers,True,''
    case_name=coordinator.evidence.value['current_case'];before=P.marker(case_name,'BEFORE');after=P.marker(case_name,'AFTER')
    if case_name==outer.expire_lease_case:outer.lease_expired=True
    if case_name==outer.expire_grant_case:outer.grant_expired=True
    if case_name==outer.failure_case:self.process.returncode=3;return [before],False,CANARY
    if 'UPDATE platform.runtime_work_item SET' in text:outer.claimed=True;return [before,json.dumps({'claimed':1}),after],True,''
    if "'inserted_fixture'" in text:
     if case_name.endswith('-1') and 'fixture-consentlog' in case_name:outer.seeded=True
     literal=int(re.search(r"'inserted_fixture',([0-9]+)",text)[1]);return [before,json.dumps({'inserted_fixture':literal}),after],True,''
    if case_name in P.DIAGNOSTICS:
     state,message,function=P.DIAGNOSTICS[case_name];error='ERROR:  '+state+': '+message+'\n'
     if function:
      body=re.search(r'CREATE FUNCTION platform_private\.'+function+r'\(\).*?AS (\$[a-z_0-9]*\$)(.*?)\1;',coordinator.application,re.S)[2];line=next(i for i,t in enumerate(body.split('\n'),1) if 'RAISE EXCEPTION '+P.quote(message) in t)
      error+='CONTEXT:  PL/pgSQL function platform_private.'+function+'() line '+str(line)+' at RAISE\nLOCATION:  exec_stmt_raise, pl_exec.c:3911\n'
     else:error+='LOCATION:  ExecWithCheckOptions, execMain.c:2231\n'
     self.process.returncode=3;return [before],False,error
    if 'WITH changed AS (UPDATE ' in text:return [before,json.dumps({'modified':0}),after],True,''
    # Parse exact table, row key and label projections from actual emitted SQL.
    projections=re.findall(r"'([^']+)',\(SELECT count\(\*\) FROM ([a-z_]+\.[a-z_]+) WHERE id='([0-9a-f-]+)'\)",text)
    if not projections:raise AssertionError('ACTUAL_SQL_PROJECTION_CHANGED')
    values=self.bound['values'];literal=lambda key:values[key][1:-1].replace("''", "'")
    caps=re.findall(r"'((?:[^']|'')*)'",values['allowed_fields']);root_model=literal('target_kind');root_id=literal('target_id');action=literal('action');purpose=literal('purpose');owner=literal('owner_module_id')
    allowed=any((m,a,p)==(root_model,action,purpose) and outer.packet['models'][m]['owner']==owner for _,m,a,p in P.SCOPE_SPECS)
    worker=role=='wa_worker';allowed=allowed or worker and (action,purpose,root_model)==('assignDefaultFreeTrack.v1','default_free_enrollment','RuntimeWorkItem') and outer.claimed
    result={}
    for label,table,key in projections:
     model=next(m for m,meta in outer.packet['models'].items() if meta['object']==table);fields=next(row['fields'] for row in outer.acl if (row['role'],row['model'],row['operation'])==(role,model,'SELECT'))
     good=allowed and all(model+'/'+key+'/SELECT/'+f in caps for f in fields)
     if model in P.REVISION_MODELS:good=good and model+'/'+key+'/revision/0' in caps
     if model==root_model:good=good and key==root_id and values['source_generation']=='0'
     elif not worker:
      relation='presentation' if model=='ConsentPresentation' else 'contentRevision';good=good and root_model in ('ConsentLog','ConsentPresentation') and root_model+'/'+root_id+'/'+relation+'/'+key in caps
     result[label]=int(bool(good))
    if outer.mutate_projection:result[next(iter(result))]+=1
    return [before,json.dumps(result),after],True,''
   def close(self):
    outer.events.append((role,'close'))
    if outer.close_failure and role=='wa_app_runtime':raise M['HeldFailure']('MOCK_BACKEND_CLOSURE_UNCONFIRMED')
    self.closed=True;self.active=False
    if self.process.returncode is None:self.process.returncode=0
    return self.process.returncode
  return Session()

class CoordinatorTests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):cls.files,cls.packet=G.build();cls.application=(ROOT/G.APPLICATION).read_text()
 def setUp(self):
  self.guards=[]
  for name in ('run','Popen','call','check_call','check_output'):
   guard=patch.object(subprocess,name,side_effect=AssertionError('UNMOCKED_PROCESS_FORBIDDEN'));guard.start();self.addCleanup(guard.stop)
  guard=patch.object(socket,'create_connection',side_effect=AssertionError('NETWORK_FORBIDDEN'));guard.start();self.addCleanup(guard.stop)
  self.temp=tempfile.TemporaryDirectory(prefix='owner-read-offline-',dir=TASK);self.addCleanup(self.temp.cleanup);self.base=Path(self.temp.name);self.packetdir=self.base/'packet';self.packetdir.mkdir()
  for name,value in self.files.items():(self.packetdir/name).write_text(value,encoding='utf8',newline='\n')
  self.patch=patch.dict(M['coordinate'].__globals__,PACKET=self.packetdir);self.patch.start();self.addCleanup(self.patch.stop)
  self.context=M['compiled']((ROOT/M['CONTEXT']).read_bytes(),M['CONTEXT']);blobs={p:(ROOT/p).read_bytes() for p in M['HELPERS']};self.context['load_helpers'](blobs)
  self.native={'format':'workinants.native-catalog.v1','server_version_num':170011,'read_only':True,'collected_as':'postgres','collector_is_superuser':True}
  self.plan={'run_id':'550e8400-e29b-41d4-a716-446655440000','source_commit':'b'*40,'source_tree':'c'*40,'packet_sha256':'d'*64,'reviewed_packet_sha256':P.sha(self.files['fixtures.json'].encode()),'reviewed_content_sha256':self.packet['source_only_packet_sha256'],'immutable_container_id':CID,'packet_files_sha256':{p:P.sha((ROOT/p).read_bytes()) for p in M['HELPERS']+(M['COLLECTOR'],)}}
  self.evidence=M['Evidence'](self.base/'evidence',self.plan,self.packet)
  self.transport=Transport(self.packet,P.__dict__,self.context);klass=M['coordinator_type'](self.context)
  self.coordinator=klass(self.plan,deepcopy(self.packet),self.native,{},self.evidence,P.__dict__,session_factory=self.transport.session);self.transport.coordinator=self.coordinator
  self.run_patch=patch.object(subprocess,'run',side_effect=self.transport.raw);self.run_patch.start();self.addCleanup(self.run_patch.stop)
 def case(self,name):return deepcopy(next(c for c in self.packet['cases'] if c['name']==name))
 def test_source_and_generator_import_help_do_not_contact_processes(self):
  with redirect_stdout(io.StringIO()),self.assertRaises(SystemExit) as found:M['main'](['--help'])
  self.assertEqual(found.exception.code,0)
  with redirect_stdout(io.StringIO()):self.assertEqual(M['main']([]),1)
 def test_actual_tuple_issuer_commit_and_close_precede_bind_and_observation(self):
  case=self.case('professional-query');value=self.coordinator.bound(case);self.assertEqual(value['counts'],{'root':1,'foreign':0})
  events=self.transport.events;issuer_close=events.index(('wa_context_issuer','close'));app_capture=events.index(('wa_app_runtime','capture'))
  bind=next(i for i,v in enumerate(events) if len(v)>2 and v[1]=='call' and v[2].startswith('SELECT platform_private.bind_request_context('));self.assertLess(app_capture,issuer_close);self.assertLess(issuer_close,bind)
  app_close=events.index(('wa_app_runtime','close'));observe=next(i for i,v in enumerate(events) if v[0]=='subprocess.run' and "'other_clients'" in v[1]);self.assertLess(app_close,observe)
 def test_all_generated_read_variants_use_actual_capability_and_projection_results(self):
  self.transport.claimed=True;self.coordinator.lease_secret='1'*64
  for case in self.packet['cases']:
   if case['kind']!='read' or case['name'].endswith('-write-denied'):continue
   with self.subTest(case=case['name']):self.assertEqual(self.coordinator.bound(case,lease=case['actual_login']=='wa_worker') ['counts'],case['expected'])
 def test_projection_regression_rejects_changed_actual_count(self):
  case=self.case('professional-query');path=self.packetdir/case['sql'];text=path.read_text();first,foreign=self.packet['ids']['ProfessionalProfile']
  # Change the actual second projection to read the authorized root again.
  # A mock copied from case.expected would miss this regression.
  text=text.replace("WHERE id="+P.quote(foreign),"WHERE id="+P.quote(first));path.write_text(text);self.coordinator.packet['prepared_files_sha256'][case['sql']]=P.sha(path.read_bytes())
  with self.assertRaises(P.HeldFailure):self.coordinator.bound(self.case('professional-query'))
  self.assertTrue(next(v for v in self.evidence.value['operations'] if v['stage']=='BOUND_OPERATION')['operation_closed'])
 def test_removed_actual_projection_is_not_filled_from_expected(self):
  case=self.case('professional-query');path=self.packetdir/case['sql'];text=path.read_text().replace("'root',(SELECT count(*)", "'root',(SELECT count(*)+1",1);path.write_text(text);self.coordinator.packet['prepared_files_sha256'][case['sql']]=P.sha(path.read_bytes())
  with self.assertRaises(P.HeldFailure):self.coordinator.bound(case)
 def test_missing_or_float_counts_reject(self):
  case=self.case('professional-query');before=P.marker(case['name'],'BEFORE');after=P.marker(case['name'],'AFTER')
  for value in ({'root':True,'foreign':0},{'root':1.0,'foreign':0},{'root':1},{'root':1,'foreign':0,'extra':CANARY}):
   with self.assertRaises(P.HeldFailure):P.verdict(case,0,[before,json.dumps(value),after],True,'',self.application)
 def test_exact_privacy_and_RLS_diagnostics_pass_with_source_frame(self):
  for name in P.DIAGNOSTICS:
   with self.subTest(name=name):self.assertTrue(self.coordinator.bound(self.case(name))['expected_guard']['matched'])
 def test_unrelated_sqlstates_messages_frames_and_extra_text_reject(self):
  case=self.case('privacy-completion-gate');before=P.marker(case['name'],'BEFORE')
  for stderr in ('ERROR:  P0001: unrelated\n','ERROR:  42501: unrelated\n','ERROR:  0A000: request completion requires qualified full owner accounting\n',CANARY+'\nERROR:  0A000: request completion requires qualified full owner accounting\n'):
   with self.assertRaises(P.HeldFailure):P.verdict(case,3,[before],False,stderr,self.application)
 def test_exact_pg17_colon_location_passes_and_old_comma_or_private_tail_rejects(self):
  for name in P.DIAGNOSTICS:
   case=self.case(name);before=P.marker(name,'BEFORE');state,message,function=P.DIAGNOSTICS[name];text='ERROR:  '+state+': '+message+'\n'
   if function:
    body=re.search(r'CREATE FUNCTION platform_private\.'+function+r'\(\).*?AS (\$[a-z_0-9]*\$)(.*?)\1;',self.application,re.S)[2];line=next(i for i,value in enumerate(body.split('\n'),1) if 'RAISE EXCEPTION '+P.quote(message) in value);text+='CONTEXT:  PL/pgSQL function platform_private.'+function+'() line '+str(line)+' at RAISE\n';location='LOCATION:  exec_stmt_raise, pl_exec.c:3911\n'
   else:location='LOCATION:  ExecWithCheckOptions, execMain.c:2231\n'
   self.assertTrue(P.verdict(case,3,[before],False,text+location,self.application)['expected_guard']['matched'])
   for bad in (location.replace('.c:', '.c, '),location+CANARY,location.replace('.c:', '.c:'+CANARY)):
    with self.assertRaises(P.HeldFailure):P.verdict(case,3,[before],False,text+bad,self.application)
 def test_complete_state_boolean_count_or_changed_hash_reject(self):
  self.transport.seeded=True;baseline=self.coordinator.state();case=self.case('professional-query');result=self.coordinator.bound(case)
  bad=deepcopy(baseline);bad['app.users']['rows_sha256']='f'*64
  with self.assertRaises(M['HeldFailure']):self.coordinator.after(case,bad,result)
 def test_close_failure_prevents_privileged_rollback_observation(self):
  self.transport.close_failure=True
  with self.assertRaises(M['HeldFailure']):self.coordinator.bound(self.case('professional-query'))
  self.assertFalse(any(v[0]=='subprocess.run' and "'other_clients'" in v[1] for v in self.transport.events))
 def test_hash_verified_sql_same_bytes_and_second_read_drift_reject(self):
  case=self.case('professional-query');path=self.packetdir/case['sql'];original=path.read_bytes()
  with patch.object(Path,'read_text',side_effect=AssertionError('SECOND_READ_FORBIDDEN')):self.assertEqual(self.coordinator.text(case['sql']),original.decode())
  path.write_bytes(CANARY.encode())
  with self.assertRaises(M['HeldFailure']):self.coordinator.bound(case)
  self.assertNotIn(CANARY,json.dumps(self.evidence.value));self.assertTrue(any(v==('wa_app_runtime','close') for v in self.transport.events))
 def test_fixture_order_preserves_physical_guards_and_always_restores_owner_bypass(self):
  self.coordinator.setup();self.assertFalse(self.coordinator.bypass_open);self.assertTrue(self.evidence.value['fixture_owner_bypass_restored'])
  calls=[v[2] for v in self.transport.events if len(v)>2 and v[1]=='call'];self.assertFalse(any('DISABLE TRIGGER physical_guard' in t for t in calls))
  opened=next(i for i,t in enumerate(calls) if 'ALTER TABLE app.consent_presentation DISABLE TRIGGER owner_commit' in t);first=next(i for i,t in enumerate(calls) if 'WA_OR_BEFORE_FIXTURE_CONSENTPRESENTATION_0' in t);closed=next(i for i,t in enumerate(calls) if 'ALTER TABLE app.consent_presentation ENABLE TRIGGER owner_commit' in t);self.assertLess(opened,first);self.assertLess(first,closed)
 def test_lease_prerequisite_is_actual_claim_and_changes_only_work_fingerprint(self):
  self.transport.seeded=True;baseline=self.coordinator.state();after=self.coordinator.claim_for_catalog(baseline);self.assertNotEqual(after['platform.runtime_work_item'],baseline['platform.runtime_work_item'])
  self.assertEqual({k:v for k,v in after.items() if k!='platform.runtime_work_item'},{k:v for k,v in baseline.items() if k!='platform.runtime_work_item'})
  self.assertNotIn(self.coordinator.lease_secret,json.dumps(self.evidence.value))
 def test_incremental_evidence_preserves_completed_cases_without_secrets(self):
  self.transport.seeded=True;baseline=self.coordinator.state();case=self.case('professional-query');result=self.coordinator.bound(case);self.coordinator.after(case,baseline,result)
  self.transport.failure_case='professional-result'
  with self.assertRaises(P.HeldFailure):self.coordinator.bound(self.case('professional-result'))
  retained=json.loads(self.evidence.path.read_bytes());self.assertEqual(len(retained['results']),1);self.assertNotIn(CANARY,json.dumps(retained))
  for value in self.coordinator.instances.values():self.assertNotIn(value['secret'],json.dumps(retained));self.assertNotIn(value['id'],json.dumps(retained))
 def test_full_mocked_pipeline_covers_all_cases_and_all_21_field_issuance(self):
  c=self.coordinator;host=self.context['HOST'];c.target={'target':{'container_name':'mock','volume_name':'mock-data','image':'pinned'}}
  host['docker_json']=lambda args,process:{};host['inspect_live']=lambda *a:{'container_id':CID};host['verify_image']=lambda *a:None
  self.context['API']['authentication_preflight']=lambda evidence,container:evidence.value['authentication'].append({'status':'MOCK_PASS'})
  c.execute();self.assertEqual(len(self.evidence.value['results']),len(self.packet['cases']));self.assertEqual(self.evidence.value['status'],'PASS_FINITE_OWNER_READ_SQL_SUBSET_ONLY')
  self.assertEqual(len(c.instances),len(self.packet['cases'])+7);self.assertTrue(self.evidence.value['fixture_owner_bypass_restored']);self.assertTrue(self.transport.claimed)
  for value in c.instances.values():self.assertEqual(len(value['values']),21)
 def test_outer_stop_preserves_partial_results_and_does_not_run_later_cases(self):
  c=self.coordinator;self.transport.seeded=True;self.transport.failure_case='professional-result'
  def execute():
   baseline=c.state()
   for name in ('professional-query','professional-result','candidate-query'):
    case=self.case(name);result=c.bound(case);c.after(case,baseline,result)
  c.execute=execute
  def factory(*args):c.evidence=args[4];return c
  namespace=M['coordinate'].__globals__
  with patch.dict(namespace,load_inputs=lambda plan:(self.packet,self.native,{},P.__dict__,self.context),coordinator_type=lambda context:factory):result=M['coordinate'](self.plan,self.base/'outer-evidence')
  self.assertEqual(result['status'],'STOPPED_PARTIAL_EVIDENCE_PRESERVED');self.assertTrue(result['subsequent_cases_stopped']);self.assertEqual(len(result['results']),1)
  self.assertNotIn(CANARY,json.dumps(result));self.assertFalse(any(len(v)>2 and 'WA_OR_BEFORE_CANDIDATE_QUERY' in v[2] for v in self.transport.events));self.assertTrue(result['source_packet_unchanged_after'])
 def outer(self):
  c=self.coordinator
  def factory(*args):c.evidence=args[4];return c
  with patch.dict(M['coordinate'].__globals__,load_inputs=lambda plan:(self.packet,self.native,{},P.__dict__,self.context),coordinator_type=lambda context:factory):return M['coordinate'](self.plan,self.base/'stopped-outer-evidence')
 def enable_resource_auth_mocks(self):
  self.coordinator.target={'target':{'container_name':'mock','volume_name':'mock-data','image':'pinned'}};host=self.context['HOST'];host['docker_json']=lambda args,process:{};host['inspect_live']=lambda *args:{'container_id':CID};host['verify_image']=lambda *args:None;self.context['API']['authentication_preflight']=lambda evidence,container:evidence.value['authentication'].append({'status':'MOCK_PASS'})
 def test_committed_open_then_verification_failure_closes_restores_exact_two_and_stops(self):
  c=self.coordinator;original=c.fixture_commit
  def committed_then_failed(name,label):
   original(name,label)
   if name=='consent-owner-fixture-open.sql':raise M['HeldFailure']('MOCK_POST_COMMIT_ACK_VERIFICATION_FAILURE')
  c.fixture_commit=committed_then_failed;c.execute=lambda:c.setup();result=self.outer()
  self.assertTrue(result['subsequent_cases_stopped']);self.assertEqual(result['results'],[]);self.assertTrue(result['fixture_owner_bypass_restored']);self.assertFalse(c.bypass_open);self.assertFalse(self.transport.owner_bypass)
  calls=[(i,v[2]) for i,v in enumerate(self.transport.events) if len(v)>2 and v[1]=='call'];opened=next(i for i,text in calls if 'ALTER TABLE app.consent_presentation DISABLE TRIGGER owner_commit;' in text);restored=next(i for i,text in calls if 'ALTER TABLE app.consent_presentation ENABLE TRIGGER owner_commit;' in text)
  self.assertLess(opened,restored);self.assertTrue(any(v==('postgres','close') for v in self.transport.events[opened+1:restored]));self.assertTrue(any(v[0]=='subprocess.run' and "'other_clients'" in v[1] for v in self.transport.events[opened+1:restored]));self.assertFalse(any('WA_OR_BEFORE_FIXTURE_CONSENTPRESENTATION_0' in text for _,text in calls));self.assertTrue(any(v.get('stage')=='FINALLY_EXACT_TRIGGER_FUNCTION_ACL_PARITY' for v in result['operations']))
 def test_expired_lease_during_zero_negative_stops_without_qualifying_it_or_later_cases(self):
  c=self.coordinator;self.enable_resource_auth_mocks();c.packet['cases']=[self.case(name) for name in ('professional-query','plan-worker','plan-worker-wrong-purpose','plan-worker-missing-field')];self.transport.expire_lease_case='plan-worker-wrong-purpose';result=self.outer()
  self.assertEqual([r['case'] for r in result['results']],['professional-query','plan-worker']);self.assertTrue(result['subsequent_cases_stopped']);self.assertTrue(any(x['code']=='EXACT_ACTUAL_LEASE_PREIMAGE_FENCE_CURRENTNESS' for x in result['unexpected']));self.assertFalse(any(len(v)>2 and 'WA_OR_BEFORE_PLAN_WORKER_MISSING_FIELD' in v[2] for v in self.transport.events));self.assertNotIn(c.lease_secret,json.dumps(result));self.assertNotIn(CANARY,json.dumps(result))
 def test_just_used_grant_expiry_after_zero_result_stops_before_verdict(self):
  c=self.coordinator;self.transport.seeded=True;self.transport.expire_grant_case='professional-query-missing-field'
  def execute():
   baseline=c.state()
   for name in ('professional-query','professional-query-missing-field','candidate-query'):
    case=self.case(name);value=c.bound(case);c.after(case,baseline,value)
  c.execute=execute;result=self.outer();self.assertEqual([r['case'] for r in result['results']],['professional-query']);self.assertTrue(result['subsequent_cases_stopped']);self.assertTrue(any(x['code']=='IMMUTABLE_21_FIELD_ISSUER_RETENTION' for x in result['unexpected']));self.assertFalse(any(len(v)>2 and 'WA_OR_BEFORE_CANDIDATE_QUERY' in v[2] for v in self.transport.events));self.assertNotIn(CANARY,json.dumps(result))
 def admitted_plan(self):
  plan=deepcopy(self.plan);pins={p:P.sha((ROOT/p).read_bytes()) for p in self.packet['source_files_sha256']}
  for name,text in self.files.items():pins['review-output/owner-read-control-rehearsal/'+name]=P.sha(text.encode())
  plan.update(schema='workinants.owner-read-run.v1',scope='REVIEWED_SELECTED94_OWNER_READ_SQL_SUBSET_ONLY',packet_files_sha256=pins,packet_sha256=P.sha(''.join(p+'\0'+pins[p]+'\n' for p in sorted(pins)).encode()),target_manifest={'reviewed':'mock'},scenario_names=[c['name'] for c in self.packet['cases']])
  comparison={'format':'workinants.catalog-comparison.v1','status':'PASS','source_expected_sha256':M['EXPECTED_CATALOG'],'native_snapshot_sha256':P.digest(self.native),'findings':[],'check_counts':{'PASS':29089}}
  native=self.base/'native.json';native.write_text(json.dumps(self.native));compare=self.base/'comparison.json';compare.write_text(json.dumps(comparison))
  plan['native_snapshot']={'path':str(native),'sha256':P.sha(native.read_bytes())};plan['native_comparison']={'path':str(compare),'sha256':P.sha(compare.read_bytes())}
  attestation={'schema':'workinants.owner-read-native-attestation.v1','run_id':plan['run_id'],'container_id':CID,'source_commit':plan['source_commit'],'source_tree':plan['source_tree'],'packet_sha256':plan['packet_sha256'],'collector_sha256':pins[M['COLLECTOR']],'source_expected_sha256':M['EXPECTED_CATALOG'],'native_snapshot_sha256':P.digest(self.native),'native_comparison_file_sha256':plan['native_comparison']['sha256'],'original_grantor_finalized':True,'operation_backends_absent':True,'comparison_status':'PASS'}
  path=self.base/'attestation.json';path.write_text(json.dumps(attestation));plan['native_attestation']={'path':str(path),'sha256':P.sha(path.read_bytes())};return plan
 def source_redirect(self,relative):
  if relative.startswith('review-output/owner-read-control-rehearsal/'):return self.packetdir/relative.split('/')[-1]
  return ROOT/relative
 def test_source_gate_rejects_packet_drift_before_helper_code_or_process(self):
  plan=self.admitted_plan();plan['packet_files_sha256'][M['PROTOCOL']]='0'*64;plan['packet_sha256']=P.sha(''.join(p+'\0'+plan['packet_files_sha256'][p]+'\n' for p in sorted(plan['packet_files_sha256'])).encode())
  execute=Mock(side_effect=AssertionError('UNVERIFIED_HELPER_EXECUTION'))
  with patch.dict(M['load_inputs'].__globals__,source_path=self.source_redirect,compiled=execute),self.assertRaises(M['HeldFailure']):M['load_inputs'](plan)
  execute.assert_not_called();self.assertEqual(self.transport.events,[])
 def test_source_gate_rejects_forged_same_run_native_attestation_before_import(self):
  plan=self.admitted_plan();path=Path(plan['native_attestation']['path']);value=json.loads(path.read_bytes());value['container_id']='f'*64;path.write_text(json.dumps(value));plan['native_attestation']['sha256']=P.sha(path.read_bytes());execute=Mock(side_effect=AssertionError('UNREVIEWED_HELPER'))
  with patch.dict(M['load_inputs'].__globals__,source_path=self.source_redirect,compiled=execute),self.assertRaises(M['HeldFailure']):M['load_inputs'](plan)
  execute.assert_not_called();self.assertEqual(self.transport.events,[])
 def test_source_gate_genuine_bytes_pass_without_read_text_second_read(self):
  plan=self.admitted_plan();original=M['compiled']
  def admitted_compiled(raw,relative):
   result=original(raw,relative)
   if relative==M['CONTEXT']:
    loader=result['load_helpers']
    def load(blobs):
     loader(blobs);result['HOST']['validate_manifest']=lambda target:{'run_id':plan['run_id'],'source':{'integrated_sql_sha256':P.APPLICATION_SHA}}
    result['load_helpers']=load
   return result
  with patch.dict(M['load_inputs'].__globals__,source_path=self.source_redirect,compiled=admitted_compiled),patch.object(Path,'read_text',side_effect=AssertionError('SECOND_READ_FORBIDDEN')):value=M['load_inputs'](plan)
  self.assertEqual(value[0]['source_only_packet_sha256'],self.packet['source_only_packet_sha256']);self.assertEqual(self.transport.events,[])

if __name__=='__main__':unittest.main(verbosity=2)
