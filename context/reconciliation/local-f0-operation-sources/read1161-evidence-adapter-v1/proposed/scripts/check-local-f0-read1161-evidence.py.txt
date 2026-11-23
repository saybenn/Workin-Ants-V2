"""Pure private candidate tests; no database, process, network or archived code."""
import ast,copy,hashlib,importlib.util,io,json,os,runpy,socket,subprocess,sys,tempfile,unittest
from pathlib import Path
from types import MappingProxyType,SimpleNamespace
from unittest.mock import patch

ROOT=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('read1161_evidence_candidate',ROOT/'scripts/local_f0_read1161_evidence.py')
M=importlib.util.module_from_spec(spec);spec.loader.exec_module(M)
CHILD=M.ASSET+'/evidence/read13-component/remaining-app-read13-results.json'
OUTER=M.ASSET+'/evidence/run-evidence.json'

class EvidenceTests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.guards=[patch.object(subprocess,'run',side_effect=AssertionError('PROCESS_FORBIDDEN')),patch.object(subprocess,'Popen',side_effect=AssertionError('PROCESS_FORBIDDEN')),patch.object(socket,'socket',side_effect=AssertionError('NETWORK_FORBIDDEN')),patch.object(os,'system',side_effect=AssertionError('PROCESS_FORBIDDEN'))]
  for guard in cls.guards:guard.start()
  cls.blobs={p:(ROOT/p).read_bytes()for p in M.PINS}
  cls.child=M.doc(cls.blobs[CHILD]);cls.fixture=M.doc(cls.blobs[M.FIXTURE]);cls.application=cls.blobs['review-output/foundation-application.review.sql'].decode();cls.execution=M.doc(cls.blobs[M.DERIVED])
 @classmethod
 def tearDownClass(cls):
  for guard in reversed(cls.guards):guard.stop()
 def reject_child(self,change,code):
  child=copy.deepcopy(self.child);change(child)
  # Serialise + parse real producer shape. Update the fingerprint so the
  # refusal must come from actual semantic predicates, not stale bytes.
  blobs=dict(self.blobs);blobs[CHILD]=(json.dumps(child,ensure_ascii=False)+'\n').encode()
  pins=dict(M.PINS);pins[CHILD]=M.sh(blobs[CHILD])
  with patch.object(M,'PINS',MappingProxyType(pins)):
   with self.assertRaisesRegex(M.EvidenceFailure,'^'+code+'$'):M.validate_bundle(blobs)
 def test_golden_real_closed_semantics(self):
  self.assertEqual(M.validate_bundle(self.blobs),M.canonical(self.execution))
  M._validate_order(self.child['operations'],self.fixture)
 def test_actual_role_issuer_and_closure_mutants(self):
  self.reject_child(lambda c:c['results'][0].update(actual_login='postgres'),'READ13_TYPED_CASE_FIELDS')
  def issuer(c):next(x for x in c['operations']if x['stage']=='SEPARATE_ISSUER_COMMIT')['issuer_committed']=False
  self.reject_child(issuer,'READ13_79_SEPARATE_ISSUER_COMMITS')
  self.reject_child(lambda c:c['operations'][0].update(all_other_clients_absent=False),'READ13_GLOBAL_ALL_CLIENT_PROOFS')
 def test_currentness_and_source_frame_mutants(self):
  def expiry(c):next(x for x in c['operations']if x['stage']=='ACTUAL_SERVER_EXPIRY')['late_response_accepted']=True
  self.reject_child(expiry,'READ13_ACTUAL_BOUNDED_EXPIRY')
  def frame(c):next(x for x in c['results']if x.get('guard_diagnostic'))['guard_diagnostic']['source_body_sha256']='0'*64
  self.reject_child(frame,'READ13_BIND_SOURCE_FRAME')
 def test_complete42_coherence_and_source_guard_mutants(self):
  self.reject_child(lambda c:c['results'][0]['after_tables'].pop('platform.runtime_work_item'),'READ13_COMPLETE42_SOURCE_LINK')
  def coherence(c):next(x for x in c['operations']if x['stage']=='EXACT48_SOURCE_COHERENCE')['adapter_or_write_qualification']=True
  self.reject_child(coherence,'READ13_SOURCE_COHERENCE_SCOPE')
  def guard(c):next(x for x in c['operations']if x['stage']=='ALL100_GUARDS_RESTORED')['internal312_identities_unchanged']=False
  self.reject_child(guard,'READ13_EXACT_TRIGGER_IDENTITIES')
 def test_typed_count_bool_float_and_canary_exclusion(self):
  for invalid in (True,42.0,None,'CANARY_PRIVATE'):
   with self.subTest(invalid=type(invalid).__name__):
    self.reject_child(lambda c:c['results'][0].update(tables_observed=invalid),'READ13_TYPED_CASE_FIELDS')
  self.reject_child(lambda c:c['results'][0].update(raw_stderr='CANARY_PRIVATE'),'READ13_READ_RESULT_FIELDS')
 def test_source_order_including_issuer_and_retention(self):
  c=copy.deepcopy(self.child);ops=c['operations'];a=next(i for i,r in enumerate(ops)if r['stage']=='ACTUAL_TRANSACTION'and r['actual_login']=='wa_app_runtime');ops[a],ops[a+1]=ops[a+1],ops[a]
  with self.assertRaisesRegex(M.EvidenceFailure,'EXACT1149_SOURCE_APPEND_ORDER'):M._validate_order(ops,self.fixture)
  c=copy.deepcopy(self.child);r=next(x for x in c['operations']if x['stage']=='EXACT21_GRANT_RETENTION');r['unexpired_required']=False
  with self.assertRaisesRegex(M.EvidenceFailure,'EXACT1149_SOURCE_APPEND_ORDER'):M._validate_order(c['operations'],self.fixture)
 def test_typed_native_counts_and_unclosed_postproof(self):
  for invalid in (True,29089.0):
   b=dict(self.blobs);p=M.ASSET+'/evidence/catalog-comparison.json';d=M.doc(b[p]);d['check_counts']['PASS']=invalid;b[p]=json.dumps(d).encode()
   with self.assertRaisesRegex(M.EvidenceFailure,'STRICT_NATIVE_29089'):M._validate_qualifiers(b,M.doc(b[OUTER]))
  b=dict(self.blobs);d=M.doc(b[OUTER]);d['read13']['component_closure_confirmed']=False;b[OUTER]=json.dumps(d).encode()
  with self.assertRaisesRegex(M.EvidenceFailure,'PARENT_CHILD_CLOSED_SAME_BYTES'):M._audit_semantics(b)
 def test_exact_claim_pointer_and_old_identity(self):
  for field,value,code in [('run_id','95321-stopped','DERIVED_EXPLICIT_IDENTITY_ALIAS'),('raw_run_id',M.RUN,'DERIVED_EXPLICIT_IDENTITY_ALIAS')]:
   b=dict(self.blobs);e=copy.deepcopy(self.execution);e[field]=value;b[M.DERIVED]=json.dumps(e).encode();pins=dict(M.PINS);pins[M.DERIVED]=M.sh(b[M.DERIVED])
   with patch.object(M,'PINS',MappingProxyType(pins)):
    with self.assertRaises(M.EvidenceFailure):M.validate_bundle(b)
 def test_pure_delta_preserves_every_unrelated_row_and_execution(self):
  old=M.doc(self.blobs[M.BASELINE]);current=copy.deepcopy(old)
  current['assertions'].append({'case_id':'UNRELATED_FUTURE_INSTALL','assertion_id':'preserve','status':'PARTIAL','history':{'all':'kept'}})
  current['executions'].append({'evidence_path':'unrelated/INSTALL.json','run_id':'new'})
  new=M.propose_ledger_delta(current,self.execution)
  self.assertEqual(new['assertions'][:-13],current['assertions']);self.assertEqual(new['executions'][:-1],current['executions']);self.assertEqual(len(new['assertions']),685)
  with self.assertRaisesRegex(M.EvidenceFailure,'PRESERVE_EXISTING_ROWS'):M.propose_ledger_delta(new,self.execution)
 def test_json_duplicate_nonfinite_depth_and_size(self):
  for raw in (b'{"same":1,"same":2}',b'{"n":NaN}',b'{"n":Infinity}',b'['*50+b'0'+b']'*50,b' '* (8*1024*1024+1)):
   with self.assertRaises(M.EvidenceFailure):M.doc(raw)
 def test_independent_inventory_sources_are_closed_without_execution(self):
  spec=M.doc(self.blobs[M.SPEC]);inputs=spec['independent_assertion_mapping_inputs_sha256'];self.assertEqual(len(inputs),6)
  for p,h in inputs.items():self.assertEqual(M.sh(self.blobs[p]),h);self.assertIn(p,M.PINS)
  b=dict(self.blobs);p=next(iter(inputs));b[p]=b[p]+b'\n'
  with self.assertRaisesRegex(M.EvidenceFailure,'ALL_DECLARED_ASSERTION_MAPPING_INPUTS'):M._claims(b)
 def test_reader_regular_missing_escape_and_multilink(self):
  with tempfile.TemporaryDirectory()as td:
   r=Path(td).resolve();p=r/'file.json';p.write_bytes(b'{"ok":true}');h=M.sh(p.read_bytes())
   self.assertEqual(M._read(r,'file.json',h),p.read_bytes())
   for path in ('../file.json','/file.json','C:/file.json','x\\y','./file.json'):
    with self.assertRaises(M.EvidenceFailure):M._read(r,path,h)
   with self.assertRaises((M.EvidenceFailure,OSError)):M._read(r,'missing',h)
   actual=p.lstat();metadata=SimpleNamespace(**{k:getattr(actual,k)for k in ('st_mode','st_dev','st_ino','st_size','st_mtime_ns','st_ctime_ns','st_nlink')});metadata.st_nlink=2
   # Creating real hardlinks is denied (WinError5) by this app sandbox; the
   # preserved failed fixture records that limit. Project only its stat result.
   with patch.object(Path,'lstat',return_value=metadata):
    with self.assertRaisesRegex(M.EvidenceFailure,'REGULAR_SINGLE_LINK_BOUNDED_FILE'):M._read(r,'file.json',h)
 def test_reader_same_size_mtime_race_and_old_reader_tripwire(self):
  # Real regular-file read, real rewrite. The wrapper only triggers timing;
  # all producer reader APIs/fstat/hash rules execute unchanged.
  source=(ROOT/'scripts/local_f0_read1161_evidence.py').read_text();tree=ast.parse(source);node=next(n for n in tree.body if isinstance(n,ast.FunctionDef)and n.name=='_read');reader='\n'.join(source.splitlines()[node.lineno-1:node.end_lineno])
  old=reader.replace("and after_handle.st_ctime_ns==opened.st_ctime_ns",'').replace("and after_path.st_ctime_ns==before.st_ctime_ns",'').replace("need((identity,before.st_ctime_ns)==expected,'FILE_CHANGED_DURING_READ')","need(identity==expected[0],'FILE_CHANGED_DURING_READ')")
  old=old[:old.index('    checked,_=closed_read(identity)')]+"    return raw\n"
  namespace=dict(M.__dict__);exec(compile(old,'<old-reader-only-tripwire>','exec'),namespace);old_reader=namespace['_read']
  with tempfile.TemporaryDirectory()as td:
   r=Path(td).resolve();p=r/'data';good=b'{"a":1}';bad=b'{"a":2}';original_open=Path.open
   def run(reader):
    p.write_bytes(good);st=p.stat();done=[False]
    class Wrapped:
     def __init__(self,fh):self.fh=fh
     def __enter__(self):self.fh.__enter__();return self
     def __exit__(self,*a):return self.fh.__exit__(*a)
     def fileno(self):return self.fh.fileno()
     def read(self,*a):
      value=self.fh.read(*a)
      if not done[0]:
       done[0]=True
       with original_open(p,'wb')as w:w.write(bad)
       os.utime(p,ns=(st.st_atime_ns,st.st_mtime_ns))
      return value
    def opening(path,*a,**kw):
     fh=original_open(path,*a,**kw)
     return Wrapped(fh)if path==p and a and a[0]=='rb'else fh
    with patch.object(Path,'open',opening):return reader(r,'data',M.sh(good))
   with self.assertRaises(M.EvidenceFailure):run(M._read)
   self.assertEqual(run(old_reader),good);self.assertEqual(p.read_bytes(),bad)
 def test_real_batch_complete13_final_all_input_barrier(self):
  b=M.prepare_batch(ROOT)
  with self.assertRaisesRegex(M.EvidenceFailure,'FINAL_FRESH_BYTE_BARRIER_REQUIRED'):b.require_finalized()
  for i,c in enumerate(self.execution['claims']):self.assertTrue(b.validate_claim(c['case_id'],c['assertion_id'],'PASS',self.execution,ROOT,'/claims/'+str(i),M._expected_row(c,M.PINS[M.DERIVED],i)))
  self.assertTrue(b.verify_unchanged());self.assertTrue(b.require_finalized())
 def test_batch_wrong_pointer_sticky_and_incomplete(self):
  # Constructor still uses actual closed bytes + semantic parser; only repeated
  # filesystem capture is replaced with a previously captured immutable graph.
  with patch.object(M,'_capture',return_value=dict(self.blobs)):
   b=M.prepare_batch(ROOT);c=self.execution['claims'][0];row=M._expected_row(c,M.PINS[M.DERIVED],0)
   with self.assertRaisesRegex(M.EvidenceFailure,'STATUS_AND_POINTER'):b.validate_claim(c['case_id'],c['assertion_id'],'PASS',self.execution,ROOT,'/claims/01',row)
   with self.assertRaisesRegex(M.EvidenceFailure,'STATUS_AND_POINTER'):b.verify_unchanged()
   b=M.prepare_batch(ROOT)
   with self.assertRaisesRegex(M.EvidenceFailure,'COMPLETE13_BATCH_REQUIRED'):b.verify_unchanged()
 def test_final_barrier_same_size_change_and_unknown_field(self):
  with patch.object(M,'_capture',return_value=dict(self.blobs)):
   b=M.prepare_batch(ROOT)
   for i,c in enumerate(self.execution['claims']):b.validate_claim(c['case_id'],c['assertion_id'],'PASS',self.execution,ROOT,'/claims/'+str(i),M._expected_row(c,M.PINS[M.DERIVED],i))
  p=M.AR+'/before-builder.py.txt'
  # It is intentionally not a runtime input: choose a real source bytes path.
  p='review-output/foundation-application.review.sql';path=ROOT/p;good=path.read_bytes();st=path.stat()
  try:
   bad=good.replace(b'CREATE',b'create',1);self.assertEqual(len(bad),len(good));path.write_bytes(bad);os.utime(path,ns=(st.st_atime_ns,st.st_mtime_ns))
   with self.assertRaises(M.EvidenceFailure):b.verify_unchanged()
   with self.assertRaises(M.EvidenceFailure):b.require_finalized()
  finally:path.write_bytes(good)
 def test_reader_ast_exact_reviewed_worker_v2_and_builder_additive(self):
  # Reader source retained locally as data for AST comparison, never imported.
  worker=ROOT/M.AR/'before-reader.py.txt'
  t=ast.parse(worker.read_bytes());old=next(n for n in t.body if isinstance(n,ast.FunctionDef)and n.name=='_read');new=next(n for n in ast.parse((ROOT/'scripts/local_f0_read1161_evidence.py').read_bytes()).body if isinstance(n,ast.FunctionDef)and n.name=='_read');self.assertEqual(ast.dump(old),ast.dump(new))
  before=(ROOT/M.AR/'before-builder.py.txt').read_text();after=(ROOT/'scripts/prepare-local-f0-status.py').read_text()
  self.assertIn('prepare_read1161_batch(ROOT)',after);self.assertIn('read1161_batch.verify_unchanged();read1161_batch.require_finalized()',after)
  self.assertIn('prepare_install_batch(ROOT)',after);self.assertIn('prepare_worker_recovery_batch(ROOT)',after)
  self.assertEqual(after.count('read1161_batch.validate_claim('),1)
 def test_private_actual_builder_dispatcher13_only(self):
  ledger_path=ROOT/'context/reconciliation/local-f0-assertion-evidence.json';status_path=ROOT/'context/reconciliation/local-f0-qualification-status.json';saved=ledger_path.read_bytes();prior_status=status_path.read_bytes()if status_path.exists()else None
  dispatcher=M.doc(saved);dispatcher['assertions']=dispatcher['assertions'][-13:];dispatcher['executions']=dispatcher['executions'][-1:]
  history=ROOT.parent/'author-check-outputs';history.mkdir(exist_ok=True)
  try:
   ledger_path.write_text(json.dumps(dispatcher,indent=2,ensure_ascii=False)+'\n',encoding='utf8',newline='\n')
   with patch.object(sys,'path',[str(ROOT/'scripts'),*sys.path]),patch('sys.stdout',new_callable=io.StringIO):runpy.run_path(str(ROOT/'scripts/prepare-local-f0-status.py'),run_name='__main__')
   raw=status_path.read_bytes();result=M.doc(raw);self.assertEqual(result['assertion_status_counts']['PASS'],13);self.assertEqual(sum(result['assertion_status_counts'].values()),1034)
   (history/'private13-actual-dispatcher-output.json').write_bytes(raw)
  finally:
   ledger_path.write_bytes(saved)
   if prior_status is not None:status_path.write_bytes(prior_status)
   elif status_path.exists():status_path.unlink()

if __name__=='__main__':unittest.main(verbosity=2)
