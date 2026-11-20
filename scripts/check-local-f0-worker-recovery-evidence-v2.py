"""Focused actual closed-data tests. All writes use temporary private clones.

This does not perform the required future unmocked Root full-ledger build.
"""
from pathlib import Path
from copy import deepcopy
from collections import Counter
from contextlib import ExitStack,redirect_stdout
from unittest.mock import patch
import ast,hashlib,importlib.util,io,json,os,runpy,shutil,socket,subprocess,sys,tempfile,unittest

ROOT=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('worker_under_test',ROOT/'scripts/local_f0_worker_recovery_evidence_v2.py')
M=importlib.util.module_from_spec(spec);spec.loader.exec_module(M)
data=lambda v:(json.dumps(v,indent=2,ensure_ascii=False,allow_nan=False)+'\n').encode()
forbidden=lambda *a,**k:(_ for _ in()).throw(AssertionError('PROCESS_OR_NETWORK_FORBIDDEN'))

class WorkerEvidenceTests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.temp=tempfile.TemporaryDirectory(prefix='wa-worker-evidence-');cls.root=Path(cls.temp.name)
  cls.blobs={n:(ROOT/n).read_bytes()for n in M.PINS}
  for n,b in cls.blobs.items():
   p=cls.root/n;p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(b)
  cls.execution=M.doc(cls.blobs[M.DERIVED]);cls.baseline=M.doc(cls.blobs[M.BASELINE])
  current_raw=(ROOT/(M.ARCHIVE+'/current656-before-worker.json')).read_bytes()
  assert M.sh(current_raw)=='50ea0011abb0f30730a5c4f3ff7f3dd56a13b664378ec7254646835b042c4d61'
  cls.current=M.doc(current_raw)
  cls.proposed=M.propose_ledger_delta(cls.current,cls.execution,cls.baseline)
  cls.rows={(r['case_id'],r['assertion_id']):r for r in cls.proposed['assertions']}
  cls.module_hash=M.sh((ROOT/'scripts/local_f0_worker_recovery_evidence_v2.py').read_bytes())
 @classmethod
 def tearDownClass(cls):
  assert M.sh((ROOT/'scripts/local_f0_worker_recovery_evidence_v2.py').read_bytes())==cls.module_hash
  cls.temp.cleanup()
 def setUp(self):
  self.stack=ExitStack();self.stack.enter_context(patch.object(subprocess,'run',forbidden));self.stack.enter_context(patch.object(subprocess,'Popen',forbidden));self.stack.enter_context(patch.object(socket,'socket',forbidden));self.touched=[]
 def tearDown(self):
  self.stack.close()
  for n in self.touched:(self.root/n).write_bytes(self.blobs[n])
 def change(self,n,raw):
  if n not in self.touched:self.touched.append(n)
  (self.root/n).write_bytes(raw)
 def check_claims(self,batch):
  for key in M.LEDGER_CHANGES:
   row=self.rows[key];self.assertTrue(batch.validate_claim(*key,row['status'],self.execution,self.root,json_pointer=row['json_pointer'],ledger_row=row))
 def mutate(self,callback):
  b=dict(self.blobs);c=M.doc(b[M.A+'/evidence/worker-recovery-component/worker-recovery-results.json']);o=M.doc(b[M.A+'/evidence/run-evidence.json']);r=M.doc(b[M.REC]);callback(c,o,r)
  cp=M.A+'/evidence/worker-recovery-component/worker-recovery-results.json';b[cp]=data(c)
  o['worker_recovery']['component_report_sha256']=M.digest(c);ref=o['worker_recovery']['component_report_reference'];ref['artifact_sha256']=M.sh(b[cp]);ref['bytes']=len(b[cp])
  s=M.doc(b[M.A+'/evidence/worker-recovery-component-result.json']);s['component_report_sha256']=M.digest(c);b[M.A+'/evidence/worker-recovery-component-result.json']=data(s)
  b[M.A+'/evidence/run-evidence.json']=data(o);r['raw_child_file_sha256']=M.sh(b[cp]);r['raw_child_canonical_sha256']=M.digest(c);r['raw_evidence_sha256']=M.sh(b[M.A+'/evidence/run-evidence.json'])
  cleanup_path=M.A+'/independent-cleanup.json';cleanup=M.doc(b[cleanup_path]);cleanup['run_evidence_sha256']=r['raw_evidence_sha256'];b[cleanup_path]=data(cleanup);r['independent_cleanup_sha256']=M.sh(b[cleanup_path])
  for n in r['assets_sha256']:r['assets_sha256'][n]=M.sh(b[n])
  b[M.REC]=data(r);return b
 def test_01_real654_batch16_final_all_inputs(self):
  self.assertEqual(len(M.PINS),654);self.assertEqual(sum(map(len,self.blobs.values())),M.MEASURED_BYTES)
  self.assertLessEqual(M.MEASURED_BYTES,M.MAX_BUNDLE_BYTES)
  self.assertEqual(M.validate_bundle(self.blobs),M.canonical(self.execution))
  batch=M.prepare_batch(self.root);self.check_claims(batch)
  with self.assertRaises(M.EvidenceFailure):batch.require_finalized()
  self.assertTrue(batch.verify_unchanged());self.assertTrue(batch.require_finalized())
 def test_02_standalone_and_old_lease_corroboration(self):
  key=next(k for k in M.CLOSED_CLAIMS if k not in M.LEDGER_CHANGES);claim=self.execution['claims'][M.CLOSED_CLAIMS[key]]
  self.assertEqual(claim['status'],'PARTIAL');self.assertEqual(self.rows[key],claim['prior_evidence'])
  # Corroboration is independently admissible but is never a changing batch row.
  row=M._expected_ledger_row(claim,M.PINS[M.DERIVED])
  self.assertTrue(M.validate_claim(*key,'PARTIAL',self.execution,self.root,json_pointer=row['json_pointer'],ledger_row=row))
 def test_03_rebase656_preserves_install_every_old_row_and_execution(self):
  self.assertEqual(len(self.current['assertions']),656);self.assertEqual(len(self.proposed['assertions']),671)
  self.assertEqual(Counter(r['status']for r in self.proposed['assertions']),{'PASS':638,'PARTIAL':33})
  changed=set(M.LEDGER_CHANGES)
  for old in self.current['assertions']:
   key=old['case_id'],old['assertion_id']
   if key not in changed:self.assertEqual(self.rows[key],old)
  upgrade=next(c for c in self.execution['claims']if c['action'].startswith('UPGRADE'))
  self.assertEqual(self.rows[upgrade['case_id'],upgrade['assertion_id']]['previous_evidence'],upgrade['prior_evidence'])
  self.assertEqual(self.proposed['executions'][:-1],self.current['executions'])
  current=deepcopy(self.current);extra={'case_id':'UNRELATED-INSTALL-FUTURE','assertion_id':'new','status':'PASS','opaque_preserved':{'number':7}}
  current['assertions'].append(extra);current['executions'].append({'unrelated_future_install':True})
  result=M.propose_ledger_delta(current,self.execution,self.baseline)
  self.assertIn(extra,result['assertions']);self.assertEqual(result['executions'][:-1],current['executions'])
 def test_04_delta_refuses_existing_pass_divergent_history_duplicates(self):
  for kind in('already_pass','old_row','missing','duplicate','execution'):
   with self.subTest(kind=kind):
    current=deepcopy(self.current)
    if kind=='already_pass':current['assertions'].append(deepcopy(self.rows[M.LEDGER_CHANGES[0]]))
    if kind=='old_row':
     key=next((c['case_id'],c['assertion_id'])for c in self.execution['claims']if c['action'].startswith('UPGRADE'));next(r for r in current['assertions']if(r['case_id'],r['assertion_id'])==key)['status']='PASS'
    elif kind=='missing':current['assertions'].pop(0)
    elif kind=='duplicate':current['assertions'].append(deepcopy(current['assertions'][0]))
    elif kind=='execution':current['executions'][0]['changed']='CANARY'
    with self.assertRaises((M.EvidenceFailure,KeyError)):M.propose_ledger_delta(current,self.execution,self.baseline)
 def test_05_bad_caps_pointer_prior_history_and_sticky_batch(self):
  # Reuse real closed admission; each failed API must stay poisoned.
  for kind in('status','pointer','history','duplicate','unknown','boolean'):
   with self.subTest(kind=kind):
    key=next(k for k in M.LEDGER_CHANGES if k[1]=='control.concurrent_fence');row=deepcopy(self.rows[key]);status=row['status'];pointer=row['json_pointer']
    if kind=='status':status='PARTIAL'
    elif kind=='pointer':pointer='/claims/00'
    elif kind=='history':row['previous_evidence']['status']='PASS'
    elif kind=='unknown':key=('UNLISTED','UNLISTED')
    elif kind=='boolean':status=True
    if kind in('history','duplicate'):
     batch=M.prepare_batch(self.root)
     if kind=='duplicate':batch.validate_claim(*key,status,self.execution,self.root,json_pointer=pointer,ledger_row=row)
     with self.assertRaises(M.EvidenceFailure):batch.validate_claim(*key,status,self.execution,self.root,json_pointer=pointer,ledger_row=row)
     with self.assertRaises(M.EvidenceFailure):batch.verify_unchanged()
    else:
     with self.assertRaises(M.EvidenceFailure):M.validate_claim(*key,status,self.execution,self.root,json_pointer=pointer,ledger_row=row)
 def test_06_final_drift_unrelated_input_sticky_after_restore(self):
  batch=M.prepare_batch(self.root);self.check_claims(batch);name=next(n for n in M.PINS if n.endswith('README.md'))
  raw=self.blobs[name];self.change(name,raw+b'\nCANARY')
  with self.assertRaises(M.EvidenceFailure):batch.verify_unchanged()
  self.change(name,raw)
  with self.assertRaises(M.EvidenceFailure):batch.verify_unchanged()
  with self.assertRaises(M.EvidenceFailure):batch.require_finalized()
 def test_07_missing_unrelated_input_refuses_admission(self):
  name=next(n for n in M.PINS if n.endswith('README.md'));path=self.root/name;raw=path.read_bytes();path.unlink()
  try:
   with self.assertRaises(M.EvidenceFailure):M.prepare_batch(self.root)
  finally:path.write_bytes(raw)
 def test_08_semantic_rehashed_clock_commit_effect_and_role_mutants(self):
  # Positive reseal control proves that structural rehashing itself is admitted.
  M._audit_semantics(self.mutate(lambda c,o,r:None))
  variants=[]
  for field in('new_reclaim_commit_before_old_action','old_current_unrevoked_unexpired_grant','actual_clock_expiry','effect_link_retained','original_tuple_retained'):
   variants.append((field,lambda c,o,r,f=field:next(x for x in c['operations']if x['stage']=='ACTUAL_RECLAIM_ORDERING').__setitem__(f,False)))
  variants.extend([('wrong_role',lambda c,o,r:next(x for x in c['operations']if x['stage']=='RESTRICTED_TRANSACTION').__setitem__('login','postgres')),('no_issuer_commit',lambda c,o,r:next(x for x in c['operations']if x['stage']=='RESTRICTED_TRANSACTION').__setitem__('issuer_committed',False)),('no_effect_checkpoint',lambda c,o,r:next(x for x in c['operations']if x['stage']=='GENUINE_LEASED_CHECKPOINT').__setitem__('work_still_leased_with_exact_committed_effect_inbox',False))])
  for name,callback in variants:
   with self.subTest(name=name),self.assertRaises(Exception):M._audit_semantics(self.mutate(callback))
 def test_09_semantic_typed42_counts_diagnostic_and_closure(self):
  M._audit_semantics(self.mutate(lambda c,o,r:None))
  variants=[]
  for value in(False,42.0,None):variants.append(('tabletype',lambda c,o,r,v=value:c['results'][0].__setitem__('tables_observed',v)))
  for value in(False,0.0,None):variants.append(('oldcount',lambda c,o,r,v=value:next(x for x in c['operations']if x['stage']=='ACTUAL_RECLAIM_ORDERING').__setitem__('old_protected_change_count',v)))
  variants.extend([('line',lambda c,o,r:c['results'][16]['source_guard'].__setitem__('source_body_line',8)),('state',lambda c,o,r:c['results'][16]['source_guard'].__setitem__('sqlstate','42501')),('body',lambda c,o,r:c['results'][16]['source_guard'].__setitem__('source_body_sha256','0'*64)),('global',lambda c,o,r:next(x for x in c['operations']if x['stage']=='GLOBAL_BACKEND_CLOSURE').__setitem__('other_clients_zero',False)),('terminal',lambda c,o,r:c['results'][0].__setitem__('connections_closed_before_terminal_observers',False)),('IO',lambda c,o,r:o.__setitem__('persistence_failure',True))])
  for name,callback in variants:
   with self.subTest(name=name),self.assertRaises(Exception):M._audit_semantics(self.mutate(callback))
 def test_10_native_oracle_ledger_cleanup_source_and42_coherence(self):
  names=['catalog-comparison.json','oracle-evidence.json','ledger-evidence.json','independent-cleanup.json']
  for name in names:
   b=dict(self.blobs);path=M.A+('/'if name=='independent-cleanup.json'else'/evidence/')+name;value=M.doc(b[path])
   if name=='catalog-comparison.json':value['check_counts']={'PASS':True}
   elif name=='oracle-evidence.json':value['results']['expression_count']=False
   elif name=='ledger-evidence.json':value['connection_closed_before_observation']=False
   else:value['private_directory_absent']=False
   b[path]=data(value)
   with self.subTest(name=name),self.assertRaises(Exception):M._audit_semantics(b)
  b=dict(self.blobs);p='review-output/worker-recovery-control-rehearsal/fixtures.json';f=M.doc(b[p]);f['worker_acl_rows'].pop();b[p]=data(f)
  with self.assertRaises(Exception):M._audit_semantics(b)
  # Changed SQL bytes fail even if the source-path name and data receipt remain.
  p=next(n for n in M.PINS if n.endswith('.sql'));b=dict(self.blobs);b[p]+=b'-- CANARY'
  with self.assertRaises(M.EvidenceFailure):M.validate_bundle(b)
 def test_11_duplicate_nonfinite_json_and_fixed_errors(self):
  for raw in(b'{"x":1,"x":2}',b'{"x":NaN}',b'{"x":Infinity}'):
   with self.assertRaises(M.EvidenceFailure):M.doc(raw)
  self.assertNotEqual(M.canonical(False),M.canonical(0));self.assertNotEqual(M.canonical(1),M.canonical(1.0))
  name=next(iter(M.PINS));self.change(name,b'CANARY_SENSITIVE')
  with self.assertRaises(M.EvidenceFailure)as got:M.prepare_batch(self.root)
  self.assertNotIn('CANARY',str(got.exception))
 def test_12_read_same_size_mtime_restored_race_and_old_reader_tripwire(self):
  root=self.root/'reader-race';root.mkdir(exist_ok=True);path=root/'small.json';original=b'{"value":"AAAA"}';changed=b'{"value":"BBBB"}';path.write_bytes(original);wanted=M.sh(original)
  oldstat=path.stat();real_open=Path.open;fired=[]
  class Reader:
   def __init__(self,reader):self.reader=reader
   def __enter__(self):self.reader.__enter__();return self
   def __exit__(self,*args):return self.reader.__exit__(*args)
   def fileno(self):return self.reader.fileno()
   def read(self,*args):
    raw=self.reader.read(*args)
    if not fired:
     fired.append(True)
     with real_open(path,'wb')as writer:writer.write(changed)
     os.utime(path,ns=(oldstat.st_atime_ns,oldstat.st_mtime_ns))
    return raw
  def hooked(p,*a,**k):
   reader=real_open(p,*a,**k);return Reader(reader)if p==path and a and a[0]=='rb'else reader
  with patch.object(Path,'open',hooked),self.assertRaises(M.EvidenceFailure):M._read(root,'small.json',wanted)
  self.assertEqual(path.read_bytes(),changed)
  # Old reader alone: no post-read identity/fresh closed reread. Same race is accepted.
  path.write_bytes(original);oldstat=path.stat();fired.clear()
  def old_reader():
   before=path.stat()
   with path.open('rb')as reader:raw=reader.read()
   self.assertEqual(len(raw),before.st_size);self.assertEqual(M.sh(raw),wanted);return raw
  with patch.object(Path,'open',hooked):self.assertEqual(old_reader(),original)
  self.assertNotEqual(path.read_bytes(),original)
 def test_13_closed_reader_ast_matches_reviewed_install_and_builder_additive(self):
  def node(source,name):return ast.dump(next(n for n in ast.parse(source).body if isinstance(n,ast.FunctionDef)and n.name==name),include_attributes=False)
  ours=(ROOT/'scripts/local_f0_worker_recovery_evidence_v2.py').read_text();install=(ROOT/'scripts/local_f0_install_evidence.py').read_text();self.assertEqual(node(ours,'_read'),node(install,'_read'))
  basis=(ROOT/(M.ARCHIVE+'/builder-before-c997.py.txt')).read_bytes();self.assertEqual(M.sh(basis),'c99712e7836f65dd8c4ad97b73d9f1e5e29f64abc8e52af4040acec26289d80a')
  new=(ROOT/'scripts/prepare-local-f0-status.py').read_text();old=basis.decode()
  for dispatcher in('install_batch.validate_claim','scoped_read_batch.validate_claim','native_complete_batch.validate_claim'):
   self.assertEqual(new.count(dispatcher),old.count(dispatcher))
  self.assertIn('ledger_row=row',new);self.assertIn('worker_recovery_batch.require_finalized()',new)
 def test_14_private_actual_cli_worker16_real_inventory_no_factory_patching(self):
  root=self.root/'private-cli';root.mkdir(exist_ok=True)
  for n,b in self.blobs.items():
   p=root/n;p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(b)
  inventory=M.doc(self.blobs['context/reconciliation/local-f0-assertions.json'])
  for name,wanted in inventory['source_provenance']['files_sha256'].items():
   raw=(ROOT/name).read_bytes();self.assertEqual(M.sh(raw),wanted)
   p=root/name;p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(raw)
  for name in('prepare-local-f0-status.py','local_f0_worker_recovery_evidence_v2.py','local_f0_migration_evidence.py','local_f0_catalog_evidence.py','local_f0_restricted_evidence.py','local_f0_native_prefix_evidence.py','local_f0_owner_lease_evidence.py','local_f0_native_complete_evidence.py','local_f0_scoped_read_evidence.py','local_f0_install_evidence.py'):
   p=root/'scripts'/name;p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes((ROOT/'scripts'/name).read_bytes())
  ledger=deepcopy(self.proposed);ledger['assertions']=[self.rows[k]for k in M.LEDGER_CHANGES];(root/'context/reconciliation/local-f0-assertion-evidence.json').write_bytes(data(ledger))
  imported=[n for n in sys.modules if n.startswith('local_f0_')];saved={n:sys.modules.pop(n)for n in imported};oldpath=list(sys.path)
  try:
   sys.path.insert(0,str(root/'scripts'));output=io.StringIO()
   with redirect_stdout(output):runpy.run_path(str(root/'scripts/prepare-local-f0-status.py'),run_name='__main__')
   result=M.doc((root/'context/reconciliation/local-f0-qualification-status.json').read_bytes())
   self.assertEqual(result['assertion_status_counts']['PASS'],13);self.assertEqual(result['assertion_status_counts']['PARTIAL'],3)
   self.assertEqual(result['case_status_counts']['PASS'],0)
   before=(root/'context/reconciliation/local-f0-qualification-status.json').read_bytes()
   first=next(iter(M.PINS));(root/first).write_bytes(b'CANARY_CHANGED_PIN')
   with redirect_stdout(output),self.assertRaises(AssertionError):runpy.run_path(str(root/'scripts/prepare-local-f0-status.py'),run_name='__main__')
   self.assertEqual((root/'context/reconciliation/local-f0-qualification-status.json').read_bytes(),before)
  finally:
   sys.path[:]=oldpath
   for n in list(sys.modules):
    if n.startswith('local_f0_'):sys.modules.pop(n)
   sys.modules.update(saved)

# Additional exact-topology/projection tests; no production factory is replaced.
def actual_live_root():
 live=ROOT if(ROOT/'node_modules').is_junction()else ROOT.parent.parent/'workinants-correction-pass'
 assert(live/'node_modules').is_junction();return live

def test_15_actual_junction_original_strict_reader_still_rejects(self):
 live=actual_live_root()
 for original,snapshot in M.METADATA_SNAPSHOTS:
  with self.subTest(original=original):
   self.assertEqual(M.sh((live/original).read_bytes()),M.ORIGINAL_PINS[original])
   self.assertFalse((live/original).resolve(strict=True).is_relative_to(live.resolve(strict=True)))
   with self.assertRaisesRegex(M.EvidenceFailure,'^PATH_ESCAPE$'):M._read(live,original,M.ORIGINAL_PINS[original])

def test_16_real_physical654_no_original_node_reads_and_finalization(self):
 logical=M._project_logical_inputs(self.blobs);self.assertEqual(set(logical),set(M.ORIGINAL_PINS));self.assertEqual(len(logical),654)
 real=Path.open;originals={self.root/name for name,_ in M.METADATA_SNAPSHOTS}
 def guarded(path,*a,**k):
  if path in originals:raise AssertionError('ORIGINAL_NODE_READ_FORBIDDEN')
  return real(path,*a,**k)
 with patch.object(Path,'open',guarded):
  batch=M.prepare_batch(self.root);self.check_claims(batch);self.assertTrue(batch.verify_unchanged());self.assertTrue(batch.require_finalized())

def test_17_nested_tools_and_closure_data_must_agree(self):
 logical=M._project_logical_inputs(self.blobs);original=M.METADATA_SNAPSHOTS[0][0]
 for name,container in((M.A+'/manifest/migration-ok.json','tools'),('context/reconciliation/local-f0-tooling/prisma-tools-closure.json',None)):
  for value in('0'*64,False,None):
   with self.subTest(name=name,value=value):
    changed=dict(logical);document=M.doc(changed[name]);mapping=document['tools']['files_sha256']if container else document['tools_files_sha256'];mapping[original]=value;changed[name]=data(document)
    with self.assertRaisesRegex(M.EvidenceFailure,'REVIEWED_TOOL_METADATA_BINDING'):M._verify_metadata_binding(changed)

def test_18_alias_source_mutants_cannot_create_a_caller_override(self):
 source=(ROOT/'scripts/local_f0_worker_recovery_evidence_v2.py').read_text();literal='METADATA_SNAPSHOTS='+repr(M.METADATA_SNAPSHOTS)
 self.assertEqual(source.count(literal),1);logical=M._project_logical_inputs(self.blobs);a,b=M.METADATA_SNAPSHOTS
 for aliases in((a,a),(a,(b[0],a[1])),(a,(b[0],'../outside.json')),(a,b,('OTHER','OTHER')),((a[0]+'-changed',a[1]),b)):
  with self.subTest(aliases=aliases):
   namespace={'__name__':'_confined_alias_source_mutant'};exec(compile(source.replace(literal,'METADATA_SNAPSHOTS='+repr(aliases),1),'<alias-mutant>','exec'),namespace)
   mapping=dict(aliases);physical={mapping.get(k,k):v for k,v in logical.items()}
   with self.assertRaisesRegex(namespace['EvidenceFailure'],'EXACT_FIXED_METADATA_PROJECTION'):namespace['_project_logical_inputs'](physical)
 self.assertEqual(len(M.METADATA_SNAPSHOTS),2);self.assertIs(type(M.METADATA_SNAPSHOTS),tuple)

def test_19_missing_or_wrong_snapshot_has_no_live_fallback(self):
 original,snapshot=M.METADATA_SNAPSHOTS[0];path=self.root/snapshot;raw=path.read_bytes();path.unlink()
 try:
  with self.assertRaises(M.EvidenceFailure):M.prepare_batch(self.root)
 finally:path.write_bytes(raw)
 changed=dict(self.blobs);changed[snapshot]=b'CANARY_DIFFERENT_SNAPSHOT'
 with self.assertRaises(M.EvidenceFailure):M.validate_bundle(changed)
 missing=dict(self.blobs);missing[original]=missing.pop(snapshot)
 with self.assertRaises(M.EvidenceFailure):M.validate_bundle(missing)

def test_20_snapshot_race_and_late_drift_remain_sticky(self):
 _,snapshot=M.METADATA_SNAPSHOTS[0];path=self.root/snapshot;original=self.blobs[snapshot];changed=bytes((original[0]^1,))+original[1:];before=path.stat();real_open=Path.open;fired=[]
 class Reader:
  def __init__(self,reader):self.reader=reader
  def __enter__(self):self.reader.__enter__();return self
  def __exit__(self,*args):return self.reader.__exit__(*args)
  def fileno(self):return self.reader.fileno()
  def read(self,*args):
   raw=self.reader.read(*args)
   if not fired:
    fired.append(True)
    with real_open(path,'wb')as writer:writer.write(changed)
    os.utime(path,ns=(before.st_atime_ns,before.st_mtime_ns))
   return raw
 def hooked(p,*a,**k):
  reader=real_open(p,*a,**k);return Reader(reader)if p==path and a and a[0]=='rb'else reader
 self.touched.append(snapshot)
 with patch.object(Path,'open',hooked),self.assertRaises(M.EvidenceFailure):M._read(self.root,snapshot,M.PINS[snapshot])
 path.write_bytes(original);batch=M.prepare_batch(self.root);self.check_claims(batch);self.change(snapshot,changed)
 with self.assertRaises(M.EvidenceFailure):batch.verify_unchanged()
 self.change(snapshot,original)
 with self.assertRaises(M.EvidenceFailure):batch.verify_unchanged()
 with self.assertRaises(M.EvidenceFailure):batch.require_finalized()

def test_21_only_projection_changes_and_real_old_import_tripwire(self):
 live=actual_live_root();old_raw=(live/'scripts/local_f0_worker_recovery_evidence.py').read_bytes();self.assertEqual(M.sh(old_raw),'3685e0a7534cff29d91b2a8ac68368d0acde42331877a819b81de12f682c1bff')
 def definitions(raw):return{n.name:ast.dump(n,include_attributes=False)for n in ast.parse(raw).body if isinstance(n,(ast.FunctionDef,ast.ClassDef))}
 old=definitions(old_raw);new=definitions((ROOT/'scripts/local_f0_worker_recovery_evidence_v2.py').read_bytes())
 self.assertEqual(set(new)-set(old),{'_verify_metadata_binding','_project_logical_inputs'})
 self.assertEqual({n for n in old if old[n]!=new[n]},{'validate_bundle'})
 self.assertEqual(M.ORIGINAL_PINS,{n:M.PINS[dict(M.METADATA_SNAPSHOTS).get(n,n)]for n in M.ORIGINAL_PINS})
 basis=(ROOT/(M.ARCHIVE+'/current-snapshots/prepare-local-f0-status.py.txt')).read_bytes();builder=(ROOT/'scripts/prepare-local-f0-status.py').read_bytes()
 self.assertEqual(builder.replace(b'from local_f0_worker_recovery_evidence_v2 import',b'from local_f0_worker_recovery_evidence import'),basis)
 root=self.root/'old-import-real-cli';root.mkdir(exist_ok=True)
 for n,b in self.blobs.items():p=root/n;p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(b)
 inventory=M.doc(self.blobs['context/reconciliation/local-f0-assertions.json'])
 for n,w in inventory['source_provenance']['files_sha256'].items():
  raw=(ROOT/n).read_bytes();self.assertEqual(M.sh(raw),w);p=root/n;p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(raw)
 scripts=('prepare-local-f0-status.py','local_f0_worker_recovery_evidence_v2.py','local_f0_migration_evidence.py','local_f0_catalog_evidence.py','local_f0_restricted_evidence.py','local_f0_native_prefix_evidence.py','local_f0_owner_lease_evidence.py','local_f0_native_complete_evidence.py','local_f0_scoped_read_evidence.py','local_f0_install_evidence.py')
 for n in scripts:p=root/'scripts'/n;p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes((ROOT/'scripts'/n).read_bytes())
 # Live accepted V1 source is used only as a restoration mutant, not a proof.
 (root/'scripts/local_f0_worker_recovery_evidence.py').write_bytes(old_raw)
 for original,snapshot in M.METADATA_SNAPSHOTS:
  p=root/original;p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(self.blobs[snapshot])
 ledger=deepcopy(self.proposed);ledger['assertions']=[self.rows[k]for k in M.LEDGER_CHANGES];(root/'context/reconciliation/local-f0-assertion-evidence.json').write_bytes(data(ledger))
 script=root/'scripts/prepare-local-f0-status.py';script.write_bytes(builder.replace(b'from local_f0_worker_recovery_evidence_v2 import',b'from local_f0_worker_recovery_evidence import'))
 real_resolve=Path.resolve
 def observed_junction_projection(path,*a,**k):
  if path.is_relative_to(root/'node_modules'):return real_resolve(live/path.relative_to(root),*a,**k)
  return real_resolve(path,*a,**k)
 saved={n:sys.modules.pop(n)for n in list(sys.modules)if n.startswith('local_f0_')};oldpath=list(sys.path)
 try:
  sys.path.insert(0,str(root/'scripts'))
  with patch.object(Path,'resolve',observed_junction_projection),redirect_stdout(io.StringIO()),self.assertRaisesRegex(AssertionError,'PATH_ESCAPE'):
   runpy.run_path(str(script),run_name='__main__')
  self.assertFalse((root/'context/reconciliation/local-f0-qualification-status.json').exists())
 finally:
  sys.path[:]=oldpath
  for n in list(sys.modules):
   if n.startswith('local_f0_'):sys.modules.pop(n)
  sys.modules.update(saved)

for _fn in(test_15_actual_junction_original_strict_reader_still_rejects,test_16_real_physical654_no_original_node_reads_and_finalization,test_17_nested_tools_and_closure_data_must_agree,test_18_alias_source_mutants_cannot_create_a_caller_override,test_19_missing_or_wrong_snapshot_has_no_live_fallback,test_20_snapshot_race_and_late_drift_remain_sticky,test_21_only_projection_changes_and_real_old_import_tripwire):setattr(WorkerEvidenceTests,_fn.__name__,_fn)

if __name__=='__main__':unittest.main(verbosity=2)
