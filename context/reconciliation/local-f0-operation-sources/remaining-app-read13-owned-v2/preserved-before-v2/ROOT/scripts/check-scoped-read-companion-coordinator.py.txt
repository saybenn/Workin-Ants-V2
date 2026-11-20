"""Projection-aware transport mocks; every process/network boundary is mocked."""
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
import sys
import tempfile
import types
import unittest
from unittest.mock import patch,Mock

ROOT=Path(__file__).resolve().parents[1];TASK=ROOT.parent
sys.path.insert(0,str(ROOT/'scripts'))
import scoped_read_companion_protocol as P
M=runpy.run_path(str(ROOT/'scripts/sql-review/run-scoped-read-companion-rehearsal.py'))
spec=importlib.util.spec_from_file_location('scoped_mock_generator',ROOT/'scripts/prepare-scoped-read-companion-rehearsal.py');G=importlib.util.module_from_spec(spec);spec.loader.exec_module(G)
CANARY='PRIVATE_ROW_PASSWORD_HANDLE_OR_STDERR_CANARY'
CID='a'*64

class Transport:
 """Derive visibility from actual SQL, scopes and caps; never case.expected."""
 def __init__(self,packet):
  self.packet=packet;self.events=[];self.coordinator=None;self.sequence=0;self.seeded=False;self.expired=False;self.expire_case=None;self.failure_case=None;self.close_failure=False;self.other_clients=0;self.disabled_owner=False;self.native_mutant=None
  self.acl=json.loads((ROOT/'context/reconciliation/foundation-sql-draft-access.json').read_bytes())
 def raw(self,args,**options):
  text=options['input'];self.events.append(('raw',text));c=self.coordinator
  if "'other_clients'" in text:value={'other_clients':self.other_clients}
  elif "'issuer_owned'" in text:value={'count':text.count(' FROM platform.database_action_grant g WHERE g.id='),'exact':True,'issuer_owned':True,'unrevoked':True,'unexpired':not self.expired}
  elif text==c.text('complete-state-observe.sql'):
   value={t:{'count':len(c.instances) if t=='platform.database_action_grant' else count if self.seeded else 0,'rows_sha256':('b' if t=='platform.database_action_grant' and c.instances else 'a')*64} for t,count in self.packet['expected_counts'].items()}
  elif text==c.text('fixture-coherence-observe.sql'):value={'users':2,'coherent':self.seeded}
  elif text==c.text('exact-trigger-observe.sql'):value={'owner_count':8,'physical_count':8,'all_enabled':True}
  elif 'workinants.native-catalog.v1' in text:
   value=deepcopy(c.native)
   if self.disabled_owner:
    for row in value['triggers']:
     if row['name']=='owner_commit':row['enabled']='D'
   if self.native_mutant:self.native_mutant(value)
  elif text.startswith('SELECT current_setting(') or text.startswith('SELECT NOT EXISTS('):return types.SimpleNamespace(returncode=0,stdout='t',stderr='')
  else:raise AssertionError('UNREGISTERED_SQL_BOUNDARY')
  return types.SimpleNamespace(returncode=0,stdout=json.dumps(value),stderr='')
 def session(self,role,c):
  outer=self;self.coordinator=c;self.sequence+=1;sequence=self.sequence
  class Session:
   def __init__(self):self.closed=False;self.role=role;self.active=False;self.bound=None;self.process=types.SimpleNamespace(returncode=None,poll=lambda:self.process.returncode)
   def begin(self,isolation):self.active=True;self.isolation=isolation;outer.events.append((role,'begin'))
   def capture(self):
    self.backend={'login':role,'current_user':role,'database':'wa_p0c_rehearsal','isolation':self.isolation,'pid':str(4000+sequence),'xid':str(10000+sequence),'started':'2026-11-19 12:00:00+00','clock':'2026-11-19 12:00:00+00'};outer.events.append((role,'capture'));return self.backend
   def call(self,text):
    outer.events.append((role,'call',text))
    if text.startswith('INSERT INTO platform.database_action_grant '):return [json.dumps({'created_at':'2026-11-19T12:00:00.001+00:00'})],True,''
    if text.startswith('SELECT pg_current_xact_id()'):return ['t'],True,''
    if text.startswith("SELECT 'WA_SRC_BIND_"):return re.findall(r"SELECT '([^']+)';",text),True,''
    if text.startswith('SELECT platform_private.bind_request_context('):
     secret=re.search(r"\('([^']+)'\)",text)[1];self.bound=next(v for v in c.instances.values() if v['secret']==secret);v=self.bound['values']
     if v['principal_user_id'].startswith(P.quote(G.USERS[1])) and v['security_generation']=='0':
      self.process.returncode=3;body=re.search(r'CREATE FUNCTION platform_private\.bind_request_context\(secret text\).*?AS\s+(\$[a-z_0-9]*\$)(.*?)\1;',c.application,re.S)[2];line=next(i for i,x in enumerate(body.split('\n'),1) if "RAISE EXCEPTION 'invalid, stale or unsupported context'" in x)
      return [],False,'ERROR:  42501: invalid, stale or unsupported context\nCONTEXT:  PL/pgSQL function platform_private.bind_request_context(text) line '+str(line)+' at RAISE\nLOCATION:  exec_stmt_raise, pl_exec.c:3911\n'
     return [],True,''
    if not text.startswith("SELECT 'WA_SRC_BEFORE_"):
     if 'DISABLE TRIGGER owner_commit;' in text:outer.seeded=True
     if text.count('ENABLE TRIGGER owner_commit;')==8:outer.disabled_owner=False
     return [],True,''
    name=c.evidence.value['current_case'];before=P.marker(name,'BEFORE');after=P.marker(name,'AFTER')
    if name==outer.expire_case:outer.expired=True
    if name==outer.failure_case:self.process.returncode=3;return [before],False,CANARY
    projections=re.findall(r"'([^']+)',\(SELECT count\(\*\) FROM ([a-z_]+\.[a-z_]+) WHERE (?:id=|user_id::text\|\|':'\|\|role::text=)'([0-9a-z:-]+)'\)",text)
    if not projections:raise M['HeldFailure']('ACTUAL_SQL_PROJECTION_CHANGED')
    v=self.bound['values'];literal=lambda key:re.match(r"'((?:[^']|'')*)'",v[key])[1].replace("''","'")
    caps=re.findall(r"'((?:[^']|'')*)'",v['allowed_fields']);root=literal('target_kind');root_id=literal('target_id');owner=literal('owner_module_id');purpose=literal('purpose');action=literal('action')
    registered=root in dict(P.SPECS) and owner==outer.packet['models'][root]['owner'] and action=='SH-003.v1' and purpose=='owner:queryOwnerFacts';result={}
    for label,table,key in projections:
     model=next(m for m,meta in outer.packet['models'].items() if meta['object']==table);fields=next(x['fields'] for x in outer.acl if (x['role'],x['model'],x['operation'])==('wa_app_runtime',model,'SELECT'))
     visible=outer.seeded and registered and model==root and key==root_id and all(model+'/'+key+'/SELECT/'+f in caps for f in fields)
     if model in P.REVISION_MODELS:visible=visible and model+'/'+key+'/revision/0' in caps and v['source_generation']=='0'
     result[label]=int(bool(visible))
    return [before,json.dumps(result),after],True,''
   def close(self):
    outer.events.append((role,'close'))
    if outer.close_failure and role=='wa_app_runtime':raise M['HeldFailure']('MOCK_CLOSURE_UNCONFIRMED')
    self.closed=True;self.active=False
    if self.process.returncode is None:self.process.returncode=0
    return self.process.returncode
  return Session()

class CoordinatorTests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):cls.files,cls.packet=G.build();cls.application=(ROOT/G.APPLICATION).read_text()
 def setUp(self):
  for name in ('run','Popen','call','check_call','check_output'):
   guard=patch.object(subprocess,name,side_effect=AssertionError('NO_UNMOCKED_PROCESS'));guard.start();self.addCleanup(guard.stop)
  guard=patch.object(socket,'create_connection',side_effect=AssertionError('NO_NETWORK'));guard.start();self.addCleanup(guard.stop)
  self.temp=tempfile.TemporaryDirectory(prefix='six-read-offline-',dir=TASK);self.addCleanup(self.temp.cleanup);self.base=Path(self.temp.name);self.packetdir=self.base/'packet';self.packetdir.mkdir()
  for name,text in self.files.items():(self.packetdir/name).write_text(text,encoding='utf8',newline='\n')
  guard=patch.dict(M['coordinate'].__globals__,PACKET=self.packetdir);guard.start();self.addCleanup(guard.stop)
  self.context=M['compiled']((ROOT/M['CONTEXT']).read_bytes(),M['CONTEXT']);self.context['load_helpers']({p:(ROOT/p).read_bytes() for p in M['HELPERS']})
  self.native={'format':'workinants.native-catalog.v1','server_version_num':170011,'read_only':True,'collected_as':'postgres','collector_is_superuser':True,'functions':[{'object':'synthetic.function()','body_sha256':'e'*64}],'triggers':[{'table_name':table,'name':'owner_commit','enabled':'O','internal':False,'function_identity':'synthetic.commit_'+str(i)+'()','definition_sha256':'c'*64} for i,table in enumerate(P.FIXTURE_TABLES)]+[{'table_name':'app.users','name':'physical_guard','enabled':'O','internal':False,'function_identity':'synthetic.physical()'}]}
  self.plan={'run_id':'550e8400-e29b-41d4-a716-446655440000','source_commit':'b'*40,'source_tree':'c'*40,'packet_sha256':'d'*64,'reviewed_packet_sha256':P.sha(self.files['fixtures.json'].encode()),'reviewed_content_sha256':self.packet['source_only_packet_sha256'],'immutable_container_id':CID,'packet_files_sha256':{p:P.sha((ROOT/p).read_bytes()) for p in M['HELPERS']+(M['COLLECTOR'],)}}
  self.evidence=M['Evidence'](self.base/'evidence',self.plan,self.packet);self.transport=Transport(self.packet);self.coordinator=M['coordinator_type'](self.context)(self.plan,deepcopy(self.packet),self.native,{},self.evidence,P.__dict__,session_factory=self.transport.session);self.transport.coordinator=self.coordinator
  guard=patch.object(subprocess,'run',side_effect=self.transport.raw);guard.start();self.addCleanup(guard.stop)
 def case(self,name):return deepcopy(next(c for c in self.packet['cases'] if c['name']==name))
 def enable_preflight(self):
  self.coordinator.target={'target':{'container_name':'mock','volume_name':'mock-data','image':'pinned'}};host=self.context['HOST'];host['docker_json']=lambda *a:{};host['inspect_live']=lambda *a:{'container_id':CID};host['verify_image']=lambda *a:None;self.context['API']['authentication_preflight']=lambda evidence,container:evidence.value['authentication'].append({'status':'MOCK_PASS'})
 def outer(self,label='outer-evidence'):
  c=self.coordinator
  def factory(*args):c.evidence=args[4];return c
  with patch.dict(M['coordinate'].__globals__,load_inputs=lambda plan:(self.packet,self.native,{},P.__dict__,self.context),coordinator_type=lambda context:factory):return M['coordinate'](self.plan,self.base/label)
 def test_full_mock_pipeline71_and_exact21_issuer_fields(self):
  self.enable_preflight();self.coordinator.execute();self.assertEqual(len(self.evidence.value['results']),71);self.assertEqual(len(self.coordinator.instances),71)
  self.assertTrue(all(len(x['values'])==21 for x in self.coordinator.instances.values()));self.assertTrue(self.evidence.value['fixture_owner_bypass_restored'])
 def test_all_variants_use_actual_projection_caps_and_generation(self):
  self.transport.seeded=True
  for case in self.packet['cases']:
   with self.subTest(case=case['name']):self.assertEqual(self.coordinator.bound(case)['counts'],case['expected'])
 def test_actual_issuer_close_before_binding_and_app_close_before_observing(self):
  self.transport.seeded=True;self.coordinator.bound(self.case('agegateattempt-positive-root'));e=self.transport.events
  issuer=e.index(('wa_context_issuer','close'));bind=next(i for i,x in enumerate(e) if len(x)>2 and x[2].startswith('SELECT platform_private.bind_request_context('));self.assertLess(issuer,bind)
  app=e.index(('wa_app_runtime','close'));closure=next(i for i,x in enumerate(e) if x[0]=='raw' and "'other_clients'" in x[1]);self.assertLess(app,closure)
 def test_changed_second_projection_does_not_copy_expected(self):
  self.transport.seeded=True;case=self.case('agegateattempt-positive-root');p=self.packetdir/case['sql'];a,b=self.packet['ids'][case['model']];p.write_text(p.read_text().replace("id='"+b+"'","id='"+a+"'"));self.coordinator.packet['prepared_files_sha256'][case['sql']]=P.sha(p.read_bytes())
  with self.assertRaises(P.HeldFailure):self.coordinator.bound(case)
 def test_missing_actual_projection_rejects(self):
  self.transport.seeded=True;case=self.case('agegateattempt-positive-root');p=self.packetdir/case['sql'];p.write_text(p.read_text().replace('SELECT count(*)','SELECT count(*)+1'));self.coordinator.packet['prepared_files_sha256'][case['sql']]=P.sha(p.read_bytes())
  with self.assertRaises(M['HeldFailure']):self.coordinator.bound(case)
 def test_typed_counts_duplicate_json_and_markers_reject(self):
  case=self.case('agegateattempt-positive-root');a=P.marker(case['name'],'BEFORE');b=P.marker(case['name'],'AFTER')
  for raw in ('{"root":true,"foreign":0}','{"root":1.0,"foreign":0}','{"root":1,"root":1,"foreign":0}','{"root":1}',CANARY):
   with self.assertRaises(P.HeldFailure):P.verdict(case,0,[a,raw,b],True,'',self.application)
  with self.assertRaises(P.HeldFailure):P.verdict(case,0,[a,'{"root":1,"foreign":0}'],True,'',self.application)
 def test_exact_binder_source_colon_and_generic_diagnostics_reject(self):
  self.transport.seeded=True;case=self.case('agegateattempt-principal-generation-mismatch');proof=self.coordinator.bound(case)['diagnostic'];self.assertTrue(proof['matched'])
  for text in ('ERROR:  42501: unrelated\n','ERROR:  P0001: unrelated\n',CANARY):
   with self.assertRaises(P.HeldFailure):P.verdict(case,3,[],False,text,self.application)
  body=re.search(r'CREATE FUNCTION platform_private\.bind_request_context\(secret text\).*?AS\s+(\$[a-z_0-9]*\$)(.*?)\1;',self.application,re.S)[2];line=next(i for i,x in enumerate(body.split('\n'),1) if "RAISE EXCEPTION 'invalid, stale or unsupported context'" in x);good='ERROR:  42501: invalid, stale or unsupported context\nCONTEXT:  PL/pgSQL function platform_private.bind_request_context(text) line '+str(line)+' at RAISE\nLOCATION:  exec_stmt_raise, pl_exec.c:3911\n'
  for text in (good.replace('.c:', '.c, '),good+CANARY,good.replace('line '+str(line),'line 1')):
   with self.assertRaises(P.HeldFailure):P.verdict(case,3,[],False,text,self.application)
 def test_current_B_control_passes_after_stale_generation_denial(self):
  self.transport.seeded=True;self.assertIsNone(self.coordinator.bound(self.case('auditEvent'.lower()+'-principal-generation-mismatch'))['counts']);self.assertEqual(self.coordinator.bound(self.case('auditevent-principalB-current-control'))['counts'],{'root':1,'foreign':0})
 def test_just_used_grant_expiry_stops_zero_negative_and_later_cases(self):
  self.enable_preflight();self.coordinator.packet['cases']=[self.case('agegateattempt-positive-root'),self.case('agegateattempt-wrong-purpose'),self.case('agegateattempt-wrong-action')];self.transport.expire_case='agegateattempt-wrong-purpose';result=self.outer()
  self.assertEqual([x['case'] for x in result['results']],['agegateattempt-positive-root']);self.assertTrue(result['subsequent_cases_stopped']);self.assertFalse(any(len(x)>2 and 'WA_SRC_BEFORE_AGEGATEATTEMPT_WRONG_ACTION' in x[2] for x in self.transport.events))
 def test_unexpected_failure_preserves_partial_and_no_private_output(self):
  self.enable_preflight();self.coordinator.packet['cases']=self.packet['cases'][:3];self.transport.failure_case='agegateattempt-wrong-purpose';result=self.outer();self.assertEqual(len(result['results']),1);self.assertTrue(result['subsequent_cases_stopped']);self.assertNotIn(CANARY,json.dumps(result))
  for v in self.coordinator.instances.values():self.assertNotIn(v['secret'],json.dumps(result));self.assertNotIn(v['token_hash'],json.dumps(result));self.assertNotIn(v['id'],json.dumps(result))
 def test_committed_fixture_lost_ACK_restores_exact_eight_after_closure(self):
  c=self.coordinator;old=c.fixture_commit
  def failure(name,label):
   old(name,label)
   if name=='existing-scoped-read-fixtures.sql':raise M['HeldFailure']('MOCK_COMMITTED_ACK_LOST')
  c.fixture_commit=failure;c.execute=lambda:c.setup();result=self.outer();self.assertTrue(result['fixture_owner_bypass_restored']);self.assertEqual(result['results'],[])
  restores=[x[2] for x in self.transport.events if len(x)>2 and 'ENABLE TRIGGER owner_commit' in x[2]];self.assertEqual(len(restores),2);self.assertNotIn('DISABLE TRIGGER',restores[-1]);self.assertEqual(restores[-1].count('ENABLE TRIGGER owner_commit'),8)
 def test_persistence_failure_still_closes_restores_native_and_postchecks(self):
  c=self.coordinator
  def execute():
   c.bypass_open=True;c.evidence.stage('WRITE_FAILURE')
  c.execute=execute;old=Path.replace
  def failed(path,target):
   if str(path).endswith('scoped-read-companion-results.json.tmp'):raise OSError(CANARY)
   return old(path,target)
  # Construct the evidence first, then fail every subsequent atomic write.
  cls=M['Evidence'];original_save=cls.save;counter={'n':0}
  def save(e):
   counter['n']+=1
   if counter['n']==1:return original_save(e)
   with patch.object(Path,'replace',failed):return original_save(e)
  with patch.object(cls,'save',save):result=self.outer()
  self.assertFalse(result['evidence_complete']);self.assertTrue(result['subsequent_cases_stopped']);self.assertTrue(result['fixture_owner_bypass_restored']);self.assertTrue(result['source_packet_unchanged_after']);self.assertTrue(any(x.get('stage')=='FINALLY_FULL_NATIVE_PARITY' for x in result['operations']));self.assertNotIn(CANARY,json.dumps(result))
 def test_close_failure_prevents_verdict_and_further_cases(self):
  self.transport.seeded=True;self.transport.close_failure=True
  with self.assertRaises(M['HeldFailure']):self.coordinator.bound(self.case('agegateattempt-positive-root'))
  self.assertEqual(self.evidence.value['results'],[]);self.assertFalse(next(x for x in self.evidence.value['operations'] if x['stage']=='BOUND_OPERATION')['operation_closed'])
 def test_SQL_same_verified_read_and_drift_reject(self):
  self.transport.seeded=True;case=self.case('agegateattempt-positive-root');p=self.packetdir/case['sql'];raw=p.read_bytes()
  with patch.object(Path,'read_text',side_effect=AssertionError('SECOND_READ')):self.assertEqual(self.coordinator.text(case['sql']),raw.decode())
  p.write_bytes(CANARY.encode())
  with self.assertRaises(M['HeldFailure']):self.coordinator.bound(case)
  self.assertNotIn(CANARY,json.dumps(self.evidence.value))
 def admitted_plan(self):
  plan=deepcopy(self.plan);pins={p:P.sha((ROOT/p).read_bytes()) for p in self.packet['source_files_sha256']}
  for name,text in self.files.items():pins['review-output/scoped-read-companion-rehearsal/'+name]=P.sha(text.encode())
  plan.update(schema='workinants.scoped-read-companion-run.v1',scope='REVIEWED_SELECTED94_SCOPED_READ_COMPANION_SQL_SUBSET_ONLY',packet_files_sha256=pins,packet_sha256=P.sha(''.join(p+'\0'+pins[p]+'\n' for p in sorted(pins)).encode()),scenario_names=[c['name'] for c in self.packet['cases']])
  # Real pure target validator, with finite metadata only; no source helper mocked.
  history=self.context['HOST']['preparation'];plan['target_manifest']={'schema':'workinants.local-f0-run.v1','run_id':plan['run_id'],'purpose':'LOCAL_F0_MIGRATION_REHEARSAL','target':{'container_name':'wa-p0c-source-only-sixread','volume_name':'wa-p0c-source-only-sixread-data','database':'wa_p0c_rehearsal','image':history['IMAGE'],'network':'none','labels':{'workinants.rehearsal':'p0c-local-f0','workinants.rehearsal.run':plan['run_id']},'bootstrap_secret_host_path':str(self.base/'bootstrap-password')},'source':{'integrated_sql_sha256':P.APPLICATION_SHA,'foundation_schema_sha256':'f'*64,'runtime_files_sha256':{p:'a'*64 for p in history['RUNTIME_FILES']}},'migration':{'id':'20261117000100_f0_local_initial','history':history['HISTORY']},'tools':{'node_version':'v24.22.1','prisma_version':'7.10.1','engine_commit':'d1b3f377ca835d73fd50954a5e22128b9ebdd6b8','files_sha256':{p:'a'*64 for p in ('node/bin/node','schema-engine','node_modules/prisma/build/index.js','node_modules/prisma/build/cli.js','node_modules/prisma/config.js','node_modules/prisma/package.json')}}}
  comparison={'format':'workinants.catalog-comparison.v1','status':'PASS','source_expected_sha256':M['EXPECTED_CATALOG'],'native_snapshot_sha256':P.digest(self.native),'findings':[],'check_counts':{'PASS':29089}}
  for name,value in [('native_snapshot',self.native),('native_comparison',comparison)]:
   p=self.base/(name+'.json');p.write_text(json.dumps(value));plan[name]={'path':str(p),'sha256':P.sha(p.read_bytes())}
  attestation={'schema':'workinants.scoped-read-companion-native-attestation.v1','run_id':plan['run_id'],'container_id':CID,'source_commit':plan['source_commit'],'source_tree':plan['source_tree'],'packet_sha256':plan['packet_sha256'],'collector_sha256':pins[M['COLLECTOR']],'source_expected_sha256':M['EXPECTED_CATALOG'],'native_snapshot_sha256':P.digest(self.native),'native_comparison_file_sha256':plan['native_comparison']['sha256'],'original_grantor_finalized':True,'operation_backends_absent':True,'comparison_status':'PASS'}
  p=self.base/'attestation.json';p.write_text(json.dumps(attestation));plan['native_attestation']={'path':str(p),'sha256':P.sha(p.read_bytes())};return plan
 def source_redirect(self,relative):return self.packetdir/relative.split('/')[-1] if relative.startswith('review-output/scoped-read-companion-rehearsal/') else ROOT/relative
 def test_whole_actual_load_inputs_real_graph_and_target_validator(self):
  plan=self.admitted_plan()
  with patch.dict(M['load_inputs'].__globals__,source_path=self.source_redirect),patch.object(Path,'read_text',side_effect=AssertionError('SECOND_READ')):value=M['load_inputs'](plan)
  self.assertEqual(value[0]['source_only_packet_sha256'],self.packet['source_only_packet_sha256']);self.assertEqual(self.transport.events,[])
 def test_missing_helper_and_historical_folder_reject_before_compile(self):
  for old,new in [(M['HELPERS'][1],None),(M['HELPERS'][1],'historical/run-first-rehearsal.py')]:
   plan=self.admitted_plan();h=plan['packet_files_sha256'].pop(old)
   if new:plan['packet_files_sha256'][new]=h
   plan['packet_sha256']=P.sha(''.join(p+'\0'+plan['packet_files_sha256'][p]+'\n' for p in sorted(plan['packet_files_sha256'])).encode());compiled=Mock(side_effect=AssertionError('UNADMITTED_COMPILE'))
   with patch.dict(M['load_inputs'].__globals__,source_path=self.source_redirect,compiled=compiled),self.assertRaises(M['HeldFailure']):M['load_inputs'](plan)
   compiled.assert_not_called()
 def test_second_fixture_read_mutation_rejects_before_compile_without_echo(self):
  plan=self.admitted_plan();p=self.packetdir/'fixtures.json';old=Path.read_bytes;reads={'n':0};compiled=Mock(side_effect=AssertionError('UNADMITTED_COMPILE'))
  def read(path):
   if path==p:
    reads['n']+=1
    if reads['n']==2:return CANARY.encode()
   return old(path)
  with patch.dict(M['load_inputs'].__globals__,source_path=self.source_redirect,compiled=compiled),patch.object(Path,'read_bytes',read),self.assertRaises(M['HeldFailure']) as error:M['load_inputs'](plan)
  compiled.assert_not_called();self.assertNotIn(CANARY,str(error.exception))
 def test_forged_native_CID_rejects_before_compile(self):
  plan=self.admitted_plan();p=Path(plan['native_attestation']['path']);d=json.loads(p.read_bytes());d['container_id']='f'*64;p.write_text(json.dumps(d));plan['native_attestation']['sha256']=P.sha(p.read_bytes());compiled=Mock(side_effect=AssertionError('UNADMITTED_COMPILE'))
  with patch.dict(M['load_inputs'].__globals__,source_path=self.source_redirect,compiled=compiled),self.assertRaises(M['HeldFailure']):M['load_inputs'](plan)
  compiled.assert_not_called()
 def test_import_help_and_missing_authorization_are_dormant(self):
  with redirect_stdout(io.StringIO()),self.assertRaises(SystemExit) as error:M['main'](['--help'])
  self.assertEqual(error.exception.code,0)
  with redirect_stdout(io.StringIO()):self.assertEqual(M['main']([]),1)
 def test_arbitrary_exception_code_never_enters_retained_metadata(self):
  error=M['HeldFailure'](CANARY);self.assertEqual(M['safe_code'](error),'UNEXPECTED_OPERATION_FAILURE')
  self.assertEqual(M['safe_code'](M['HeldFailure']('IMMUTABLE_21_FIELD_ISSUER_RETENTION')),'IMMUTABLE_21_FIELD_ISSUER_RETENTION')
 def test_independent_global_absence_allows_only_cleanup_after_close_uncertainty(self):
  c=self.coordinator;self.transport.close_failure=True;self.transport.seeded=True;c.bypass_open=True;c.execute=lambda:c.bound(self.case('agegateattempt-positive-root'));result=self.outer()
  self.assertEqual(result['results'],[]);self.assertTrue(result['subsequent_cases_stopped']);self.assertTrue(result['fixture_owner_bypass_restored']);self.assertTrue(any(x['code']=='OPERATION_CLOSURE_UNCONFIRMED' for x in result['unexpected']))
  self.assertTrue(any(len(x)>2 and x[2].count('ENABLE TRIGGER owner_commit')==8 for x in self.transport.events))
 def test_unconfirmed_global_absence_prevents_restoration_SQL_and_business_observers(self):
  c=self.coordinator;c.bypass_open=True;self.transport.other_clients=1
  def failure():raise M['HeldFailure']('UNEXPECTED_OPERATION_FAILURE')
  c.execute=failure;result=self.outer();self.assertTrue(result['subsequent_cases_stopped']);self.assertFalse(result['fixture_owner_bypass_restored']);self.assertTrue(result['source_packet_unchanged_after'])
  self.assertFalse(any(len(x)>2 and 'ENABLE TRIGGER owner_commit' in x[2] for x in self.transport.events));self.assertFalse(any(x[0]=='raw' and x[1]==c.text('complete-state-observe.sql') for x in self.transport.events))
 def test_exact_eight_disabled_identity_gate_precedes_restore_DDL(self):
  c=self.coordinator;c.bypass_open=True;self.transport.disabled_owner=True
  def failure():raise M['HeldFailure']('UNEXPECTED_OPERATION_FAILURE')
  c.execute=failure;result=self.outer();self.assertTrue(result['fixture_owner_bypass_restored']);self.assertTrue(result['subsequent_cases_stopped']);self.assertEqual(result['results'],[])
  gate=next(i for i,x in enumerate(result['operations']) if x['stage']=='PRE_RESTORATION_EXACT_NATIVE_IDENTITY');restore=next(i for i,x in enumerate(result['operations']) if x['stage']=='FINALLY_EXACT_EIGHT_RESTORE');self.assertLess(gate,restore);self.assertEqual(result['operations'][gate]['disabled_owner_triggers'],8)
 def test_pre_restore_function_foreign_trigger_definition_and_state_mutants_reject(self):
  mutants=[lambda n:n['functions'][0].update(body_sha256='f'*64),lambda n:n['triggers'][-1].update(enabled='D'),lambda n:n['triggers'][0].update(definition_sha256='f'*64),lambda n:n['triggers'][0].update(enabled='A'),lambda n:n['triggers'][0].update(enabled='R'),lambda n:n['triggers'][0].update(table_name='app.unlisted'),lambda n:n.update(unlisted_catalog_fact=True)]
  c=self.coordinator
  def failure():raise M['HeldFailure']('UNEXPECTED_OPERATION_FAILURE')
  c.execute=failure
  for index,mutation in enumerate(mutants):
   actual=deepcopy(self.native);mutation(actual)
   with self.assertRaises(P.HeldFailure):P.restoration_identity(self.native,actual)
   c.bypass_open=True;self.transport.native_mutant=mutation;start=len(self.transport.events);result=self.outer('mutant-'+str(index));self.assertFalse(result['fixture_owner_bypass_restored']);self.assertTrue(c.bypass_open);self.assertFalse(any(len(x)>2 and 'ENABLE TRIGGER owner_commit;' in x[2] for x in self.transport.events[start:]));self.assertTrue(result['subsequent_cases_stopped']);gate=next(x for x in result['operations'] if x['stage']=='PRE_RESTORATION_EXACT_NATIVE_IDENTITY');self.assertFalse(gate['comparison_passed']);self.assertIn(gate['failed_check'],('RESTORATION_FULL_NATIVE_IDENTITY_DRIFT','RESTORATION_ONLY_OWNER_O_OR_D','RESTORATION_EXACT_EIGHT_IDENTITIES'))

if __name__=='__main__':unittest.main(verbosity=2)
