import ast,collections,copy,difflib,hashlib,importlib.util,json,os,pathlib,sys,threading,time
from types import MappingProxyType
P=pathlib.Path(__file__).resolve().parent
sys.dont_write_bytecode=True
EDGES=[]
def guard(event,args):
 if event.startswith(('subprocess.','socket.')) or event in ('os.system','os.posix_spawn','os.spawn','os.exec'):
  EDGES.append(event);raise AssertionError('FORBIDDEN_BOUNDARY')
sys.addaudithook(guard)
started=time.monotonic();RESULT=[]
def ok(name,details=None):
 RESULT.append({'name':name,'status':'PASS',**({'details':details} if details is not None else {})})
 print(name,flush=True)
def reject(name,fn,code):
 try:fn()
 except M.EvidenceFailure as ex:
  assert str(ex)==code,(name,str(ex),code);ok(name,{'safe_code':str(ex)});return
 raise AssertionError(name+'_ACCEPTED')
raw=(P/'scripts/local_f0_privilege485517b0_evidence.py').read_bytes()
tree=ast.parse(raw)
imports={x.name.split('.')[0] for n in ast.walk(tree) if isinstance(n,ast.Import) for x in n.names}|{n.module.split('.')[0] for n in ast.walk(tree) if isinstance(n,ast.ImportFrom)}
assert imports<={'pathlib','types','ast','copy','hashlib','io','json','math','os','re','stat','tarfile'}
assert not any(isinstance(n,ast.Call) and isinstance(n.func,ast.Name) and n.func.id in {'exec','eval','compile','__import__'} for n in ast.walk(tree))
loader=importlib.util.spec_from_file_location('independent_new_reader',P/'scripts/local_f0_privilege485517b0_evidence.py');M=importlib.util.module_from_spec(loader);loader.loader.exec_module(M)
ok('new_reader_stdlib_only_no_dynamic_source_execution')
blobs=M._capture(P);spec=M.doc(blobs[M.SPEC]);execution=M.doc(blobs[M.DERIVED]);old=M.doc(blobs[M.ARCHIVE+'/prior687-assertion-evidence.json'])
assert set(M.PINS)==set(blobs) and len(blobs)==519
assert len(spec['source455_sha256'])==455 and len(spec['preserved56_sha256'])==56 and len(spec['six_history_sha256'])==6
assert len(set(M.PINS)-set(spec['closed_existing511_sha256']))==8
assert [k for k in M.PINS if k.endswith(('.tar','.tar.gz','.zip'))]==[M.ASSET+'/public-source-only-seven-files.tar.gz']
ok('independent_exact519_union_and_only_public_seven_file_tar')
assert M.encoded(M.expected_record(blobs))==blobs[M.DERIVED]
assert M.encoded(M.expected_record(dict(reversed(list(blobs.items())))))==blobs[M.DERIVED]
ok('binary_derived_reproduction_including_reversed_input_map')
assert len(execution['claims'])==44 and collections.Counter(c['status'] for c in execution['claims'])=={'PASS':41,'PARTIAL':3}
assert set((r['case_id'],r['assertion_id']) for r in execution['claims'])==set(M.MAXIMA)
assert execution['limits']['post_behavior_oracle_or_ledger_rerun'] is False
assert not any(c['case_id']=='P0C-TABLE-DatabaseActionGrant-DENY' for c in execution['claims'])
rows=[M._expected_row(c,i) for i,c in enumerate(execution['claims'])]
batch=M.prepare_batch(P)
def fork():
 b=copy.copy(batch);b._QualificationBatch__seen=set();b._QualificationBatch__failed=None;b._QualificationBatch__finalized=False;return b
for c,r in zip(execution['claims'],rows):assert batch.validate_claim(c['case_id'],c['assertion_id'],c['status'],execution,P,json_pointer=r['json_pointer'],ledger_row=r)
racebatch=copy.copy(batch);racebatch._QualificationBatch__seen=set(batch._QualificationBatch__seen)
assert batch.verify_unchanged() and batch.require_finalized()
ok('actual_constructor_complete44_once_and_actual_final519_barrier')
b=fork();r=rows[0];reject('omitted44_is_sticky',b.verify_unchanged,'COMPLETE44_BATCH_REQUIRED');reject('sticky_failure_cannot_recover',lambda:b.validate_claim(r['case_id'],r['assertion_id'],r['status'],execution,json_pointer=r['json_pointer'],ledger_row=r),'COMPLETE44_BATCH_REQUIRED')
b=fork();assert b.validate_claim(r['case_id'],r['assertion_id'],r['status'],execution,json_pointer=r['json_pointer'],ledger_row=r)
reject('duplicate44_rejected',lambda:b.validate_claim(r['case_id'],r['assertion_id'],r['status'],execution,json_pointer=r['json_pointer'],ledger_row=r),'EXACT_UNSEEN44')
b=fork();changed=copy.deepcopy(r);changed['qualification_limit']='unsupported extra scope'
reject('entire_row_equality_rejects_scope_rewrite',lambda:b.validate_claim(r['case_id'],r['assertion_id'],r['status'],execution,json_pointer=r['json_pointer'],ledger_row=changed),'EXACT_EXECUTION_FULL_LEDGER_ROW')
b=fork();reject('numeric_pointer_alias_rejected',lambda:b.validate_claim(r['case_id'],r['assertion_id'],r['status'],execution,json_pointer='/claims/00',ledger_row=r),'EXACT_STATUS_POINTER')
delta=M.propose_ledger_delta(old,execution)
assert len(delta['assertions'])==730 and len(delta['executions'])==15
assert all(delta['assertions'][i]==v for i,v in enumerate(old['assertions']) if i!=70)
assert delta['executions'][:14]==old['executions']
assert delta['assertions'][70]['previous_evidence']==old['assertions'][70] and delta['assertions'][70]['status']=='PARTIAL'
assert len([r for r in old['assertions'] if r['case_id']=='P0C-RESTORE-01'])==3
assert [r for r in delta['assertions'] if r['case_id']=='P0C-RESTORE-01']==[r for r in old['assertions'] if r['case_id']=='P0C-RESTORE-01']
ok('pure43_plus1_delta_all686_and14_and_Restore3_preserved_no_builder_run')
base=(P/M.ARCHIVE/'prior-builder7a2.py.txt').read_bytes();proposal=(P/'builder-proposal/FINAL/prepare-local-f0-status.py.PROPOSAL').read_bytes()
a=base.decode().splitlines(True);b=proposal.decode().splitlines(True);ops=difflib.SequenceMatcher(None,a,b,autojunk=False).get_opcodes()
assert sum(j2-j1 for tag,i1,i2,j1,j2 in ops if tag=='insert')==12
assert all(tag in ('equal','insert') for tag,*_ in ops)
recovered=''.join(line for tag,i1,i2,j1,j2 in ops if tag=='equal' for line in b[j1:j2]).encode()
assert recovered==base and ast.dump(ast.parse(recovered))==ast.dump(ast.parse(base))
ok('builder12_additions_zero_removals_exact_previous_AST_recovered')
parent=M.doc(blobs[M.ASSET+'/evidence/run-evidence.json']);child=M.doc(blobs[M.ASSET+'/evidence/privilege-ceiling-component/privilege-ceiling-results.json']);fixture=M.doc(blobs[M.FIXTURE+'/fixtures.json']);migration=M.doc(blobs[M.ASSET+'/manifest/ok-migration-manifest.json'])
policy,native=M._native(blobs,spec,fixture,parent,migration)
cp=M.ASSET+'/evidence/privilege-ceiling-component/privilege-ceiling-results.json';pp=M.ASSET+'/evidence/run-evidence.json';sp=M.ASSET+'/evidence/privilege-ceiling-component-result.json'
def envelope(mut):
 b=dict(blobs);objects={p:M.doc(b[p]) for p in spec['sanitized_json_frames']};mut(objects)
 ch=objects[cp];objects[sp]['component_report_sha256']=M.digest(ch);objects[pp]['privilege_ceiling']['component_report_sha256']=M.digest(ch)
 for p,v in objects.items():
  if p!=M.REC:b[p]=blobs[p] if M.canonical(v)==M.canonical(M.doc(blobs[p])) else M.encoded(v)
 objects[pp]['privilege_ceiling']['component_report_reference'].update(artifact_sha256=M.sh(b[cp]),bytes=len(b[cp]));b[pp]=M.encoded(objects[pp])
 n=objects[M.REC];n['raw_parent']['sha256']=M.sh(b[pp]);n['raw_child']['sha256']=M.sh(b[cp]);n['assets_sha256']={p:M.sh(b[p]) for p in n['assets_sha256']};b[M.REC]=M.encoded(n)
 s=copy.deepcopy(spec);s['preserved56_sha256']={p:M.sh(b[p]) for p in s['preserved56_sha256']};s['closed_existing511_sha256']={**s['source455_sha256'],**s['preserved56_sha256']};b[M.SPEC]=M.encoded(s)
 return b,MappingProxyType({p:M.sh(v) for p,v in b.items()})
for name,mut,code in [
 ('rehashed_HBA_trust_cannot_bypass_source_auth',lambda d:d[pp]['effective_hba_selections'][0].update(method='trust'),'TWELVE_EFFECTIVE_SCRAM_HBA_RULES'),
 ('rehashed_raw_control_promotion_rejected',lambda d:d[cp]['selected_controls'][0].update(status='PASS'),'RAW_FIVE_CONTROLS_SOURCE_NOT_PROMOTED'),
 ('rehashed_cleanup_unrelated_change_rejected',lambda d:d[pp]['cleanup_summary'].update(unrelated_resources_changed=True),'CLEANUP_EXACT_BOUNDARIES'),
 ('rehashed_stale_current_operation_rejected',lambda d:d[cp].update(current=copy.deepcopy(d[cp]['operations'][0])),'EXACT_ALLOWLISTED_JSON_FRAME')]:
 altered,pins=envelope(mut);prior=M.PINS
 try:M.PINS=pins;reject(name,lambda:M.validate_bundle(altered),code)
 finally:M.PINS=prior
altered=dict(blobs);n=copy.deepcopy(native);n['nonowner_acl']=n['nonowner_acl'][1:];altered[M.ASSET+'/evidence/native-before.json']=M.encoded(n)
reject('native_ACL_missing_independently_source_derived',lambda:M._native(altered,spec,fixture,parent,migration),'COMPLETE_SOURCE_NONOWNER_ACL')
altered=dict(blobs);n=copy.deepcopy(native);n['memberships'][0]['grantor']='wa_migrator';altered[M.ASSET+'/evidence/native-before.json']=M.encoded(n)
reject('original_bootstrap_grantor_is_not_migrator',lambda:M._native(altered,spec,fixture,parent,migration),'ORIGINAL_GRANTOR_PERMANENT_EDGE')
altered=dict(blobs);n=copy.deepcopy(native);n['roles'][0]['rolsuper']=not n['roles'][0]['rolsuper'];altered[M.ASSET+'/evidence/privilege-ceiling-native-final.json']=M.encoded(n)
reject('fresh_post200_native_must_match_no_post_oracle_fiction',lambda:M._native(altered,spec,fixture,parent,migration),'BASELINE_PREREQUISITES_AND_FINAL_NATIVE_EQUAL')
canary='INDEPENDENT_SECRET_CANARY_NO_EXPOSURE'
for i,raw in enumerate((b'{"x":1,"x":2}',b'{"x":NaN}',b'{"x":Infinity}',b'"\xff"')):
 try:M.doc(raw)
 except M.EvidenceFailure as e:assert canary not in str(e)
 else:raise AssertionError('JSON_ACCEPTED')
ok('strict_duplicate_nonfinite_and_nonUTF8_JSON')
try:M._literal(b'IMPORTANT=__import__("os").system("FORBIDDEN")','IMPORTANT')
except M.EvidenceFailure as e:assert str(e)=='SOURCE_LITERAL_REJECTED'
else:raise AssertionError('LITERAL_EXECUTED')
ok('AST_literal_does_not_execute_calls')
for s in ('../canary','a//canary','C:/canary','a\\canary','/canary'):
 reject('unsafe_relative_path_'+str(len(RESULT)),lambda s=s:M._read(P,s,'0'*64),'RELATIVE_PATH')
# Actual bytes change in the final capture, triggered after a real handle read.
# A separate thread performs the filesystem write; no cached callback proof is used.
rel=next(p for p in M.PINS if p.endswith('migration_lock.toml'));target=P/rel;original=target.read_bytes();st=target.stat();modified=(b'!' if original[:1]!=b'!' else b'#')+original[1:]
original_open=pathlib.Path.open;armed=[True];thread_errors=[]
def mutate_file():
 try:
  with original_open(target,'wb') as f:f.write(modified)
  os.utime(target,ns=(st.st_atime_ns,st.st_mtime_ns))
 except Exception as ex:thread_errors.append(type(ex).__name__)
class RacedHandle:
 def __init__(self,f):self.f=f
 def __enter__(self):self.f.__enter__();return self
 def __exit__(self,*a):return self.f.__exit__(*a)
 def fileno(self):return self.f.fileno()
 def read(self,*a):
  raw=self.f.read(*a)
  if armed[0]:
   armed[0]=False;t=threading.Thread(target=mutate_file);t.start();t.join(5);assert not t.is_alive() and not thread_errors
  return raw
def racing_open(path,*a,**kw):
 stream=original_open(path,*a,**kw)
 return RacedHandle(stream) if path==target and a and a[0]=='rb' and armed[0] else stream
try:
 pathlib.Path.open=racing_open
 try:racebatch.verify_unchanged()
 except M.EvidenceFailure as e:
  racecode=str(e);assert racecode in {'HANDLE_CHANGED_DURING_READ','PATH_CHANGED_DURING_READ','FILE_CHANGED_DURING_READ','FILE_BYTES','CLOSED_READ_BYTES_CHANGED'}
 else:raise AssertionError('ACTUAL_FINAL_RACE_ACCEPTED')
finally:
 pathlib.Path.open=original_open
 with original_open(target,'wb') as f:f.write(original)
 os.utime(target,ns=(st.st_atime_ns,st.st_mtime_ns))
assert not armed[0] and target.read_bytes()==original and M.sh(original)==M.PINS[rel]
reject('sticky_actual_same_size_mtime_restored_final519_race',racebatch.require_finalized,racecode)
ok('actual_thread_mutated_private_file_restored_exact_bytes',{'target':rel,'safe_code':racecode,'same_size':True,'mtime_restored':True})
assert not EDGES
# The delivery is reviewed as frozen; no candidate source or graph bytes change.
freeze=json.loads((P/'review-freeze-manifest.json').read_bytes())
assert all(hashlib.sha256((P/p).read_bytes()).hexdigest()==h for p,h in freeze['files_sha256'].items())
ok('all626_frozen_private_bytes_reverified_after_tests')
report={'schema':'workinants.independent-reader-code-peer-tests.v1','status':'PASS','reader_sha256':hashlib.sha256((P/'scripts/local_f0_privilege485517b0_evidence.py').read_bytes()).hexdigest(),'focused_tests':len(RESULT),'results':RESULT,'seconds':round(time.monotonic()-started,3),'boundary_events':EDGES,'Root_mutated':False,'runtime':'NOT_RUN_SOURCE_ONLY','aggregate730_builder':'NOT_RUN','Posture':'D'}
(P/'independent-focused-tests.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf8')
print(json.dumps({'status':'PASS','tests':len(RESULT),'seconds':report['seconds']}))
