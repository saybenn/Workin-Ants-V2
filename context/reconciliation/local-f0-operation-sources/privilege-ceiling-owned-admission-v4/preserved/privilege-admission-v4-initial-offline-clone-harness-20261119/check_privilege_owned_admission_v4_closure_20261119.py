"""AdmissionV4: actual preparation map, real source loader, all processes mocked.
No plans() pin factory is used. Synthetic native assets are offline-only.
"""
from pathlib import Path
from copy import deepcopy
from contextlib import ExitStack,redirect_stdout,redirect_stderr
from unittest.mock import patch,Mock
from types import SimpleNamespace
import ast,hashlib,io,json,runpy,shutil,socket,subprocess,tempfile,unittest,uuid
TASK=Path(__file__).resolve().parent;ROOT=TASK/'workinants-correction-pass'
CORE='execute_local_f0_privilege_ceiling_admission_v4_20261119.py'
STEPS='local_f0_privilege_ceiling_admission_v4_operation_steps.py'
PREP='prepare_local_f0_privilege_ceiling_admission_v4_plan.py'
PIN='pin_local_f0_privilege_ceiling_admission_v4_plan_20261119.py'
CHECK='check_local_f0_privilege_ceiling_admission_v4_operation.py'
COOR='scripts/sql-review/run-privilege-ceiling-control-rehearsal.py'
REVIEW='context/reconciliation/local-f0-privilege-ceiling-owned-admission-v4-source-validation.json'
PACKET='review-output/privilege-ceiling-control-rehearsal'
README=PACKET+'/README.md'
BASE=TASK/'local-f0-catalog-v4-plan-23bd8979/operation-manifest.json'
sha=lambda raw:hashlib.sha256(raw).hexdigest()
aggregate=lambda m:sha(''.join(k+'\0'+m[k]+'\n'for k in sorted(m)).encode())
encoded=lambda v:(json.dumps(v,indent=2)+'\n').encode()
CANARY='SECRET_CANARY_ADMISSION_MUST_NEVER_EXPORT'

class PrivilegeAdmissionV4ClosureTests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.guard=ExitStack()
  for name in('run','Popen','call','check_call','check_output'):cls.guard.enter_context(patch.object(subprocess,name,side_effect=AssertionError('REAL_PROCESS_FORBIDDEN')))
  for owner,name in((socket,'create_connection'),(socket.socket,'connect')):cls.guard.enter_context(patch.object(owner,name,side_effect=AssertionError('NETWORK_FORBIDDEN')))
  cls.temporary=tempfile.TemporaryDirectory(prefix='priv-admission-v4-',dir=TASK);cls.task=Path(cls.temporary.name);cls.root=cls.task/'workinants-correction-pass';cls.root.mkdir()
  prep=runpy.run_path(str(TASK/PREP));result=prep['prepare'](BASE,sha(BASE.read_bytes()),str(uuid.uuid4()));first=Path(result['operation_manifest']).parent
  try:
   actual=json.loads(Path(result['operation_manifest']).read_bytes());cls.actual_inventory=deepcopy(actual['prepared_source_file_inventory_sha256'])
   for relative in cls.actual_inventory:
    dest=cls.root/relative;dest.parent.mkdir(parents=True,exist_ok=True);dest.write_bytes((ROOT/relative).read_bytes())
  finally:
   assert first.resolve().parent==TASK.resolve()and first.name.startswith('local-f0-privilege-ceiling-plan-')and not first.is_relative_to(ROOT);shutil.rmtree(first)
  for name in(CORE,STEPS,PREP,PIN,CHECK):(cls.task/name).write_bytes((TASK/name).read_bytes())
  for relative in('node_modules/@prisma/engines-version/package.json','node_modules/prisma/package.json'):
   target=cls.root/relative;target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes((ROOT/relative).read_bytes())
  # Only isolated metadata is approved, before actual prepare builds its map.
  value=json.loads((cls.root/REVIEW).read_bytes());value['independent_safety_sql_review']={'decision':'SOURCE_APPROVED','scope':'OFFLINE_TEST_ONLY_SYNTHETIC_FUTURE_APPROVAL_NOT_RUNTIME_AUTHORITY'};(cls.root/REVIEW).write_bytes(encoded(value))
  cls.baseline=cls.task/'offline-baseline.json';cls.baseline.write_bytes(BASE.read_bytes())
  cls.legacy=runpy.run_path(str(ROOT/'scripts/sql-review/test_run_privilege_ceiling_control_rehearsal.py'))
  cls.preparer=runpy.run_path(str(cls.task/PREP));cls.M=runpy.run_path(str(cls.root/COOR))
  result=cls.preparer['prepare'](cls.baseline,sha(cls.baseline.read_bytes()),cls.legacy['RUN']);cls.plan_path=Path(result['operation_manifest']);cls.unpinned=cls.plan_path.read_bytes();cls.master=json.loads(cls.unpinned)
  cls.pins=deepcopy(cls.master['prepared_source_file_inventory_sha256']);cls.target=json.loads(Path(cls.master['migration_targets']['ok']['manifest_path']).read_bytes())
  cls.pinner=runpy.run_path(str(cls.task/PIN));cls.pin_calls=[]
  def git(*args,input=None):
   cls.pin_calls.append(args)
   if args==('rev-parse','HEAD'):return b'a'*40+b'\n'
   if args==('rev-parse','HEAD^{tree}'):return b'b'*40+b'\n'
   assert args==('cat-file','--batch')
   output=b''
   for request in input.decode().splitlines():
    commit,relative=request.split(':',1);assert commit=='a'*40;raw=(cls.root/relative).read_bytes();output+=b'0'*40+b' blob '+str(len(raw)).encode()+b'\n'+raw+b'\n'
   return output
  cls.pinner['pin'].__globals__['git_read']=git;cls.pin_result=cls.pinner['pin'](cls.plan_path);cls.pinned=json.loads(cls.plan_path.read_bytes())
  assert cls.pinned['packet_files_sha256']==cls.pins
  cls.current_validation=sha((ROOT/REVIEW).read_bytes())

 @classmethod
 def tearDownClass(cls):
  try:
   assert cls.task.resolve().parent==TASK.resolve()and not cls.task.is_relative_to(ROOT);cls.temporary.cleanup()
  finally:cls.guard.close()

 def setUp(self):
  self.directory=Path(tempfile.mkdtemp(prefix='case-',dir=self.task));self.addCleanup(lambda:shutil.rmtree(self.directory))
  self.world=self.legacy['World']();self.world.target=deepcopy(self.target)
  target=self.target['target'];self.world.container['Name']='/'+target['container_name'];self.world.container['Config']['Image']=target['image'];self.world.volume['Name']=target['volume_name']
  for mount in self.world.container['Mounts']:
   if mount['Type']=='volume':mount['Name']=target['volume_name']
   elif mount['Type']=='bind':mount['Source']=target['bootstrap_secret_host_path']
  self.component=self.component_plan(self.pins)

 def component_plan(self,pins):
  M=self.M;N=self.legacy['N'];world=self.world;run=self.master['run_id'];cid=self.legacy['CID']
  def asset(name,value):
   path=self.directory/(name+'.json');path.write_bytes(encoded(value));return{'path':str(path),'sha256':sha(path.read_bytes())}
  comparison={'format':'workinants.catalog-comparison.v1','status':'PASS','source_expected_sha256':N['EXPECTED_SOURCE'],'native_snapshot_sha256':M['digest'](world.native),'check_counts':{'PASS':1},'findings':[]}
  provider={'schema':'workinants.native-deny-provider-preinstall.v1','run_id':run,'container_id':cid,'source_commit':'a'*40,'source_tree':'b'*40,'packet_sha256':N['PACKET_SHA'],'application_sql_sha256':M['APPLICATION_SHA'],'roles':N['provider_flags'](),'all_nine_schema_usage_sentinels_before_install':True,'canonical_install_removed_all_nine':True,'genuine_prisma_one_applied_migration':True,'original_grantor_finalized':True,'local_simulation_only':True,'hosted_parity_claimed':False}
  native={'schema':'workinants.native-deny-run.v1','scope':'FINITE_NATIVE_DENIAL_FACETS_ONLY','run_id':run,'source_commit':'a'*40,'source_tree':'b'*40,'packet_sha256':N['PACKET_SHA'],'source_modules_sha256':{p:pins[p]for p in N['MODULES']},'target_manifest':deepcopy(self.target),'immutable_container_id':cid,'selected_case_ids':self.legacy['NATIVE_PACKET']['selected_case_ids']}
  for key,value in(('native_snapshot',world.native),('native_comparison',comparison),('provider_preinstall_proof',provider)):native[key]=asset('OFFLINE_TEST_ONLY_'+key,value)
  value={'schema':'workinants.privilege-ceiling-run.v1','scope':'FINITE_EXISTING_PRIVILEGE_CEILINGS_ONLY','run_id':run,'source_commit':'a'*40,'source_tree':'b'*40,'packet_sha256':aggregate(pins),'packet_files_sha256':deepcopy(pins),'fixtures_sha256':self.master['privilege_ceiling']['fixtures_sha256'],'content_sha256':self.master['privilege_ceiling']['content_sha256'],'native_plan':native}
  attestation={'schema':'workinants.privilege-ceiling-native-attestation.v1','run_id':run,'container_id':cid,'source_commit':'a'*40,'source_tree':'b'*40,'operation_packet_sha256':value['packet_sha256'],'native_sql_packet_sha256':N['PACKET_SHA'],'application_sql_sha256':M['APPLICATION_SHA'],'source_expected_sha256':M['EXPECTED_NATIVE'],'native_snapshot_sha256':M['digest'](world.native),'native_comparison_file_sha256':native['native_comparison']['sha256'],'genuine_prisma_one_applied_migration':True,'original_grantor_finalized':True,'native_expression_oracle_and_private_ledger_pass':True,'all_other_client_backends_absent':True,'provider_preinstall_source_proven':True,'posture':'D','whole_case_promotion':False}
  value['prerequisite_attestation']=asset('OFFLINE_TEST_ONLY_prerequisite',attestation);return value

 def test_actual_prepare_map_has_all202_generated_bytes_and_same_source_digests(self):
  owned=json.loads((self.root/REVIEW).read_bytes());artifacts=owned['privilege_packet']['artifacts_sha256'];self.assertEqual(len(artifacts),202)
  self.assertEqual(self.pins[README],'5837f26cd959ee0addca42f319b3d67f8d8ee09828657dd793c6caeadbd416ec')
  self.assertTrue(all(self.pins[p]==h==sha((self.root/p).read_bytes())for p,h in artifacts.items()));self.assertEqual(self.master['privilege_ceiling']['fixtures_sha256'],'4ebe8b6cd7b85ff5ad8dbb79d431bb7001cf16dea72e3920138be4b5f2855e68');self.assertEqual(self.master['privilege_ceiling']['content_sha256'],'643232e4d068892b49e49122b7ce3b909bd86caa9e770aa923d7df00def1ec32')

 def test_real_unchanged_load_inputs_accepts_only_the_actual_prepare_map(self):
  before=encoded(self.component['packet_files_sha256']);loaded=self.M['load_inputs'](self.component)
  self.assertEqual(encoded(self.component['packet_files_sha256']),before);self.assertEqual(loaded[0],json.loads((self.root/PACKET/'fixtures.json').read_bytes()));self.assertEqual(set(loaded[1]),set(self.pins));self.assertEqual(len(loaded[0]['cases']),200)

 def test_exact_old604_map_reproduces_missing_README_without_factory_supplement(self):
  original=runpy.run_path(str(ROOT/COOR));old=json.loads((TASK/'local-f0-privilege-ceiling-plan-c3c6d297/operation-manifest.json').read_bytes());plan=deepcopy(self.component);plan['packet_files_sha256']=old['packet_files_sha256'];plan['packet_sha256']=aggregate(plan['packet_files_sha256']);self.assertEqual(len(plan['packet_files_sha256']),604);self.assertNotIn(README,plan['packet_files_sha256'])
  with self.assertRaises(original['Held'])as found:original['load_inputs'](plan)
  self.assertEqual(found.exception.code,'EXACT_SOURCE_PACKET_REPRODUCTION')

 def test_removed_README_rehashed_actual_map_is_still_rejected_by_real_loader(self):
  plan=deepcopy(self.component);plan['packet_files_sha256'].pop(README);plan['packet_sha256']=aggregate(plan['packet_files_sha256'])
  with self.assertRaises(self.M['Held'])as found:self.M['load_inputs'](plan)
  self.assertEqual(found.exception.code,'EXACT_SOURCE_PACKET_REPRODUCTION')

 def helper(self):
  n=runpy.run_path(str(self.task/CORE))['launch'].__globals__;n['initialize'](self.plan_path);exec(compile((self.task/STEPS).read_bytes(),str(self.task/STEPS),'exec'),n)
  return n,{p:(self.root/p).read_bytes()for p in self.pins},json.loads((self.root/REVIEW).read_bytes()),json.loads((self.root/PACKET/'fixtures.json').read_bytes())

 def test_generation_helper_rejects_missing_rehashed_or_wrong_type_artifacts(self):
  n,blobs,owned,fixture=self.helper()
  cases=[];b=deepcopy(blobs);b.pop(README);cases.append((b,deepcopy(owned),fixture));b=deepcopy(blobs);b[README]=CANARY.encode();v=deepcopy(owned);v['privilege_packet']['artifacts_sha256'][README]=sha(b[README]);cases.append((b,v,fixture));b=deepcopy(blobs);b[README]=CANARY;cases.append((b,deepcopy(owned),fixture));v=deepcopy(owned);v['privilege_packet']['artifacts_sha256'].pop(README);cases.append((deepcopy(blobs),v,fixture));v=deepcopy(owned);v['privilege_packet']['artifacts_sha256'][PACKET+'/../'+CANARY]=v['privilege_packet']['artifacts_sha256'].pop(README);cases.append((deepcopy(blobs),v,fixture));f=deepcopy(fixture);f['status']=CANARY;cases.append((deepcopy(blobs),deepcopy(owned),f))
  for b,v,f in cases:
   with self.subTest(kind=type(b.get(README)).__name__),self.assertRaises(n['Stop'])as found:n['privilege_generated_artifact_closure'](b,v,f,self.root)
   self.assertNotIn(CANARY,str(found.exception))

 def test_remove_actual_preparer_full_artifact_union_is_detected(self):
  source=(self.task/PREP).read_text();self.assertEqual(source.count(';inventory.update(artifacts)'),1);mutant=source.replace(';inventory.update(artifacts)','');n={'__name__':'_offline_old_inventory_mutant','__file__':str(self.task/PREP)};exec(compile(mutant,str(self.task/PREP),'exec'),n);run=str(uuid.uuid4())
  with self.assertRaises(n['Refused'])as found:n['prepare'](self.baseline,sha(self.baseline.read_bytes()),run)
  self.assertEqual(str(found.exception),'PRIVILEGE_GENERATED_ARTIFACT_NOT_ADMITTED');self.assertFalse((self.task/('local-f0-privilege-ceiling-plan-'+run[:8])).exists())

 def actual_entry(self,missing=False,pending=False):
  m=deepcopy(self.pinned);m['review_status']='APPROVED_LOCAL_F0_PRIVILEGE_CEILING_ATTEMPT';m['evidence_directory']=str(self.directory/'out')
  if missing:m['packet_files_sha256'].pop(README)
  pending_raw=None
  if pending:
   v=json.loads((self.root/REVIEW).read_bytes());v['independent_safety_sql_review']={'decision':'PENDING_ROOT_AND_INDEPENDENT_REVIEW'};pending_raw=encoded(v);m['packet_files_sha256'][REVIEW]=sha(pending_raw)
  m['packet_sha256']=aggregate(m['packet_files_sha256']);manifest=self.directory/'operation-manifest.json';manifest.write_bytes(encoded(m));module=runpy.run_path(str(self.task/CORE));n=module['launch'].__globals__;calls=[];project_compiles=[];actual_read=Path.read_bytes;actual_compile=compile
  def read(path):return pending_raw if pending_raw is not None and path==self.root/REVIEW else actual_read(path)
  def compile_(source,filename,*args,**kwargs):
   if str(filename).startswith(str(self.root/'scripts')):project_compiles.append(str(filename))
   return actual_compile(source,filename,*args,**kwargs)
  def process(args,**kwargs):
   if args[:3]==['git','-c','core.longpaths=true']:
    if args[3:]==['rev-parse','HEAD']:return SimpleNamespace(returncode=0,stdout='a'*40+'\n',stderr='')
    if args[3:]==['rev-parse','HEAD^{tree}']:return SimpleNamespace(returncode=0,stdout='b'*40+'\n',stderr='')
    assert args[3]=='show';return SimpleNamespace(returncode=0,stdout=read(self.root/args[4].split(':',1)[1]),stderr=b'')
   assert args[:3]==['docker','--context','desktop-linux'];tail=args[3:];calls.append(tail)
   if tail in(['ps','-a','--format','{{.Names}}'],['volume','ls','--format','{{.Name}}']):return SimpleNamespace(returncode=0,stdout='',stderr='')
   if tail==['context','inspect','desktop-linux']:raise n['Stop']('OFFLINE_RESOURCE_STAGE_REACHED')
   raise AssertionError('UNDECLARED_RESOURCE_ACTION')
  output=io.StringIO()
  with patch.object(Path,'read_bytes',read),patch('builtins.compile',compile_),patch.object(subprocess,'run',side_effect=process),redirect_stdout(output),redirect_stderr(output):code=module['launch'](['--execute-reviewed-privilege-ceilings','--manifest',str(manifest)])
  self.assertEqual(code,1);self.assertNotIn(CANARY,output.getvalue());return n,calls,project_compiles

 def test_real_initialized_entry_refuses_missing_README_before_resources_and_helpers(self):
  n,calls,compiled=self.actual_entry(missing=True);self.assertEqual(n['report']['primary_failure']['code'],'PRIVILEGE_GENERATED_ARTIFACT_NOT_ADMITTED');self.assertEqual(compiled,[]);self.assertFalse(any(c[:2]in(['container','create'],['volume','create'],['image','inspect'],['context','inspect'])for c in calls));self.assertTrue(n['report']['cleanup_actions_confirmed'])

 def test_isolated_pending_gate_precedes_new_pure_project_compilation(self):
  n,calls,compiled=self.actual_entry(pending=True);self.assertEqual(n['report']['primary_failure']['code'],'SAFETY_SQL_REVIEW_REQUIRED');self.assertEqual(compiled,[]);self.assertFalse(any(c[:2]==['context','inspect']for c in calls))

 def test_real_initialized_complete_entry_reaches_only_first_resource_boundary(self):
  n,calls,compiled=self.actual_entry();self.assertEqual(n['report']['primary_failure']['code'],'OFFLINE_RESOURCE_STAGE_REACHED');self.assertEqual(n['report']['privilege_generated_artifact_closure']['generated_artifacts'],202);self.assertTrue(compiled);self.assertFalse(any(c[:2]in(['container','create'],['volume','create'],['image','inspect'])for c in calls))

 def test_real_coordinator_SQL_projection_composition_uses_actual_preparation_map(self):
  before=encoded(self.component['packet_files_sha256']);loaded=self.M['load_inputs'](self.component);packet,blobs,protocol,native,ctx,np,nb,snapshot,api,host=loaded;memory=self.legacy['MemoryEvidence']();self.world.evidence=memory;Runner=self.M['runner_type'](native,ctx,protocol);runner=Runner(self.component,packet,blobs,np,nb,snapshot,api,host,memory)
  with patch.object(subprocess,'run',side_effect=self.world.run),patch.object(subprocess,'check_output',side_effect=self.world.check_output),patch.object(subprocess,'Popen',side_effect=lambda *a,**k:self.legacy['Process'](self.world,*a,**k)):runner.run()
  self.assertEqual(encoded(self.component['packet_files_sha256']),before);self.assertEqual((len(memory.value['results']),len(memory.value['definer_metadata']),len(memory.value['native_controls']),len(memory.value['issuer_protocols']),len(memory.value['operations'])),(200,16,40,3,244));self.assertEqual(memory.value['facets'],[]);self.assertTrue(all(p.poll()is not None for p in self.world.processes));self.assertTrue(all(r['status']=='NOT_RUN'for r in packet['control_links']))

if __name__=='__main__':unittest.main(verbosity=2)
