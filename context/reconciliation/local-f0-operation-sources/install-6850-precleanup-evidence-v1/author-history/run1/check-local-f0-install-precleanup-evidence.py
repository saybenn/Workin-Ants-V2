"""Actual closed graph/API tests. All service/process/network calls forbidden."""
import ast,copy,hashlib,io,json,os,runpy,socket,stat,subprocess,sys,tempfile,types,unittest
from pathlib import Path
from unittest.mock import patch
ROOT=Path(__file__).resolve().parents[1];TASK=ROOT.parent
SOURCE=ROOT/'scripts/local_f0_install_precleanup_evidence.py'
CANARY='PRIVATE_PASSWORD_SQL_HANDLE_CANARY_6850'

def legacy_read_for_tripwire(root,relative,wanted):
    need(type(relative)is str and relative and not Path(relative).is_absolute()and ':'not in relative and '\\'not in relative and all(x not in('','.','..')for x in relative.split('/')),'RELATIVE_PATH')
    path=root/relative
    need(not any(x.is_symlink()for x in(path,*path.parents)if x.is_relative_to(root)),'SYMLINK')
    need(path.resolve(strict=True).is_relative_to(root),'PATH_ESCAPE')
    before=path.stat();need(stat.S_ISREG(before.st_mode)and before.st_nlink==1 and 0<=before.st_size<=8*1024*1024,'REGULAR_SINGLE_LINK_BOUNDED_FILE')
    with path.open('rb')as reader:raw=reader.read(8*1024*1024+1)
    after=path.stat();need(not path.is_symlink()and(before.st_dev,before.st_ino,before.st_size,before.st_mtime_ns,before.st_nlink)==(after.st_dev,after.st_ino,after.st_size,after.st_mtime_ns,after.st_nlink),'FILE_CHANGED_DURING_READ')
    need(len(raw)==before.st_size and sh(raw)==wanted,'FILE_BYTES')
    return raw

class Checks(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        ns=runpy.run_path(str(SOURCE));cls.m=ns['prepare_batch'].__globals__;cls.E=cls.m['EvidenceFailure'];cls.blobs=cls.m['_capture'](ROOT);cls.derived=cls.m['_doc'](cls.blobs[cls.m['DERIVED']]);cls.child=cls.m['_doc'](cls.blobs[cls.m['B']+'/evidence/install-controls/install-controls-results.json'])
        cls.source_before=hashlib.sha256(SOURCE.read_bytes()).hexdigest()
    def setUp(self):
        for name in('run','Popen','check_output','call','check_call'):
            g=patch.object(subprocess,name,side_effect=AssertionError('PROCESS_FORBIDDEN'));g.start();self.addCleanup(g.stop)
        for name in('socket','create_connection'):
            g=patch.object(socket,name,side_effect=AssertionError('NETWORK_FORBIDDEN'));g.start();self.addCleanup(g.stop)
    def safe_reject(self,call):
        with self.assertRaises(self.E)as caught:call()
        self.assertNotIn(CANARY,str(caught.exception));return str(caught.exception)
    def phase(self,variant='late_function_grant',mutate=None):
        target=copy.deepcopy(self.child['targets'][variant]);rows=target['failed_precleanup_activation'];closures=target['failed_precleanup_closures']
        if mutate:mutate(rows,closures,target)
        return self.m['_phase'](rows,closures,variant,self.m['CIDS'][variant],target['cli_'+variant+'_deploy'])
    def rebinding(self,path,mutate):
        """In-memory byte/hash-consistent mutants; no golden verdict factory."""
        m=self.m;blobs=dict(self.blobs);assets=dict(m['ASSET_PINS']);changes={};pins=dict(m['PINS'])
        def encode(v):return(json.dumps(v,sort_keys=True,indent=2,allow_nan=False)+'\n').encode()
        def replace(value):
            if type(value)is str:return changes.get(value,value)
            if type(value)is dict:return{k:replace(v)for k,v in value.items()}
            if type(value)is list:return[replace(v)for v in value]
            return value
        v=m['_doc'](blobs[path]);mutate(v);blobs[path]=encode(v);changes[pins[path]]=m['sh'](blobs[path]);pins[path]=m['sh'](blobs[path])
        if path in assets:assets[path]=pins[path]
        rpath=m['B']+'/evidence/run-evidence.json'
        if path!=rpath:
            r=replace(m['_doc'](blobs[rpath]))
            childpath=m['B']+'/evidence/install-controls/install-controls-results.json'
            if path==childpath:r['install']['coordinator_reference']['bytes']=len(blobs[childpath])
            blobs[rpath]=encode(r);changes[pins[rpath]]=m['sh'](blobs[rpath]);pins[rpath]=m['sh'](blobs[rpath]);assets[rpath]=pins[rpath]
        rec=replace(m['_doc'](blobs[m['REC']]));rec['assets_sha256']=assets;blobs[m['REC']]=encode(rec);changes[pins[m['REC']]]=m['sh'](blobs[m['REC']]);pins[m['REC']]=m['sh'](blobs[m['REC']])
        d=replace(m['_doc'](blobs[m['DERIVED']]));blobs[m['DERIVED']]=encode(d);pins[m['DERIVED']]=m['sh'](blobs[m['DERIVED']]);pieces=replace(copy.deepcopy(m['EVIDENCE_PIECES']))
        return blobs,{'PINS':pins,'ASSET_PINS':assets,'EVIDENCE_PIECES':pieces}
    def test_01_real409_public_batch_oneclaim_and_final_byte_barrier(self):
        b=self.m['prepare_batch'](ROOT);self.assertTrue(b.validate_claim(*self.m['CLAIM'],'PASS',self.derived,ROOT,json_pointer='/claims/0'));self.assertTrue(b.verify_unchanged());self.assertTrue(b.require_finalized())
    def test_02_runtime_code_is_closed_stdlib_and_has_no_execution_boundary(self):
        tree=ast.parse(SOURCE.read_bytes());allowed={'hashlib','json','math','os','re','stat','pathlib','types'}
        for node in ast.walk(tree):
            if isinstance(node,ast.Import):self.assertTrue(all(x.name in allowed for x in node.names))
            if isinstance(node,ast.ImportFrom):self.assertIn(node.module,allowed)
            if isinstance(node,ast.Call)and isinstance(node.func,ast.Name):self.assertNotIn(node.func.id,{'exec','eval','compile','__import__'})
        self.assertEqual(len(self.m['PINS']),409);self.assertEqual(len(self.m['SOURCE_PINS']),291)
    def test_03_only_exact_claim_status_pointer_and_no_forged_proof_dict(self):
        for args in[('P0C-INSTALL-01',self.m['CLAIM'][1],'PASS','/claims/0'),(*self.m['CLAIM'],'PARTIAL','/claims/0'),(*self.m['CLAIM'],'PASS','/limits'),(*self.m['CLAIM'],'PASS','/claims/00')]:
            self.safe_reject(lambda args=args:self.m['validate_claim'](*args[:3],self.derived,ROOT,json_pointer=args[3]))
        bad=copy.deepcopy(self.derived);bad['claims'][0]['status']='PARTIAL';p=self.m['DERIVED'];blobs=dict(self.blobs);blobs[p]=(json.dumps(bad)+'\n').encode()
        with patch.dict(self.m,{'PINS':{**self.m['PINS'],p:self.m['sh'](blobs[p])}}):self.safe_reject(lambda:self.m['_validate_bundle'](blobs))
    def test_04_json_duplicate_nonfinite_overflow_and_safe_errors(self):
        for raw in[b'{"a":1,"a":2}',b'{"a":NaN}',b'{"a":Infinity}',b'{"a":1e999}',('{'+CANARY).encode()]:self.safe_reject(lambda raw=raw:self.m['_doc'](raw))
        self.assertEqual(self.m['_doc'](b'{"a":1.25}'),{'a':1.25})
    def test_05_both_actual10_15_precleanup_phases_pass(self):
        self.phase('division_failure');self.phase('late_function_grant')
    def test_06_phase_semantic_scope_authority_roles_and_type_mutants(self):
        mutations=[lambda r,c,t:r.pop(),lambda r,c,t:c.pop(),lambda r,c,t:r[0].update(sequence=True),lambda r,c,t:r[1]['facts'].update(activated=True),lambda r,c,t:r[2]['facts'].update(database_password_sql_executed=True),lambda r,c,t:r[3]['facts'].update(all_null_verifiers=False),lambda r,c,t:r[4]['facts'].update(role='wa_worker'),lambda r,c,t:r[7]['facts'].update(exit_code=True),lambda r,c,t:r[8]['facts'].update(temporary_memberships=0),lambda r,c,t:r[8]['facts'].update(leaf_create=True),lambda r,c,t:r[9]['facts'].update(original_finalization_not_yet_run=False),lambda r,c,t:r[0]['identity'].update(container_id='f'*64),lambda r,c,t:r[0]['facts'].update(intended_primary_sqlstate='42501'if t['failed_precleanup_activation'][0]['identity']['variant']=='division_failure'else'22012'),lambda r,c,t:r[0]['facts']['diagnostic_delta'].update(malformed=1),lambda r,c,t:c[0]['proof'].update(all_other_clients_absent=False),lambda r,c,t:c[0].update(stage='AFTER_CLEANUP'),lambda r,c,t:r[2]['facts'].update(unknown=CANARY)]
        for v in('division_failure','late_function_grant'):
            for mutate in mutations:
                with self.subTest(v=v,mutate=mutate):self.safe_reject(lambda:self.phase(v,mutate))
    def test_07_actual_cli_type_identity_closed_and_fixed_diagnostic_mutants(self):
        base=self.child['targets']['late_function_grant']['cli_late_function_grant_deploy'];cid=self.m['CIDS']['late_function_grant'];sql=self.m['SQL']['late_function_grant']
        for mutate in[lambda x:x.update(exit_code=True),lambda x:x.update(container_id='e'*64),lambda x:x.update(raw_output_discarded=False),lambda x:x['diagnostic_format'].update(raw_stderr=CANARY),lambda x:x['diagnostic_format'].update(text_valid=1),lambda x:x.update(sqlstates=[CANARY])]:
            v=copy.deepcopy(base);mutate(v);self.safe_reject(lambda:self.m['_cli'](v,cid,sql))
    def test_08_byte_consistent_phase_mutant_and_phase_only_omission_tripwire(self):
        p=self.m['B']+'/evidence/install-controls/install-controls-results.json';blobs,pins=self.rebinding(p,lambda x:x['targets']['late_function_grant']['failed_precleanup_activation'][1]['facts'].update(activated=True))
        with patch.dict(self.m,pins):
            self.assertEqual(self.safe_reject(lambda:self.m['_validate_bundle'](blobs)),'PHASE_GATE_FALSE')
            with patch.dict(self.m,{'_phase':lambda *a,**k:None}):self.assertIsInstance(self.m['_validate_bundle'](blobs),str)
    def test_09_byte_consistent_parent_IO_and_unknown_child_fields_reject(self):
        for path,mutate in[(self.m['B']+'/evidence/run-evidence.json',lambda x:x.update(persistence_failure=True)),(self.m['B']+'/evidence/install-controls/install-controls-results.json',lambda x:x.update(extra=CANARY))]:
            blobs,pins=self.rebinding(path,mutate)
            with patch.dict(self.m,pins):self.safe_reject(lambda:self.m['_validate_bundle'](blobs))
    def test_10_byte_consistent_native_counts_and_normalization_mutants(self):
        for n,mutate in[('canonical-catalog-comparison.json',lambda x:x['check_counts'].update(PASS=29089.0)),('recovered-catalog-comparison.json',lambda x:x['check_counts'].update(PASS=29089)),('install-semantic-parity.json',lambda x:x.update(only_validated_internal_name_equality_omitted=False))]:
            blobs,pins=self.rebinding(self.m['B']+'/evidence/'+n,mutate)
            with patch.dict(self.m,pins):self.safe_reject(lambda:self.m['_validate_bundle'](blobs))
    def test_11_original_deadline_review_scope_and_preserved_prior_row_reject(self):
        receipt=self.m['_doc'](self.blobs[self.m['ARCHIVE']+'/Catalog-explicit-recovery-decision-receipt.json'])
        for field,value in[('original_review_deadline_monotonic',213728.921),('remaining_seconds_after_publication',0),('remaining_seconds_after_publication',221),('all_read_handles_closed',False)]:
            blobs=dict(self.blobs);p=self.m['ARCHIVE']+'/Catalog-explicit-recovery-decision-receipt.json';bad=copy.deepcopy(receipt);bad[field]=value;blobs[p]=(json.dumps(bad)+'\n').encode()
            with patch.dict(self.m,{'PINS':{**self.m['PINS'],p:self.m['sh'](blobs[p])}}):self.safe_reject(lambda:self.m['_validate_bundle'](blobs))
    def test_12_source_pin_rebinding_cannot_hide_source_drift(self):
        p=next(iter(self.m['SOURCE_PINS']));blobs=dict(self.blobs);blobs[p]+=b' ';pins={**self.m['PINS'],p:self.m['sh'](blobs[p])}
        with patch.dict(self.m,{'PINS':pins}):self.assertEqual(self.safe_reject(lambda:self.m['_validate_bundle'](blobs)),'EXACT_SOURCE_PIN_LINKAGE')
    def reader_race(self,old=False,metadata_stable=False):
        with tempfile.TemporaryDirectory(prefix='read-race-',dir=TASK)as temp:
            root=Path(temp).resolve();self.assertTrue(root.is_relative_to(TASK.resolve()));p=root/'fixed.json';gold=b'{"value":1}\n';bad=b'{"value":2}\n';p.write_bytes(gold);before=p.stat();opening=Path.open;fired=[]
            class Handle:
                def __init__(self,h):self.h=h
                def __enter__(self):return self
                def __exit__(self,*a):return self.h.__exit__(*a)
                def fileno(self):return self.h.fileno()
                def read(self,*a):
                    value=self.h.read(*a)
                    if not fired:
                        fired.append(True)
                        with opening(p,'wb')as w:w.write(bad)
                        os.utime(p,ns=(before.st_atime_ns,before.st_mtime_ns))
                    return value
            def opened(path,*a,**k):
                h=opening(path,*a,**k);return Handle(h)if path==p and a and a[0]=='rb'else h
            reader=self.m['_read']
            if old:
                legacy_read_for_tripwire.__globals__.update(need=self.m['need'],sh=self.m['sh']);reader=legacy_read_for_tripwire
            with patch.object(Path,'open',opened):
                if metadata_stable:
                    with patch.object(Path,'lstat',return_value=before),patch.object(os,'fstat',return_value=before):return reader(root,'fixed.json',self.m['sh'](gold))
                return reader(root,'fixed.json',self.m['sh'](gold))
    def test_13_actual_inflight_reader_race_and_old_reader_only_tripwire(self):
        self.safe_reject(lambda:self.reader_race());self.assertEqual(self.reader_race(old=True),b'{"value":1}\n')
    def test_14_fresh_closed_bytes_reject_metadata_stable_race(self):self.safe_reject(lambda:self.reader_race(metadata_stable=True))
    def test_15_windows_cross_API_ctime_valid_and_fstat_identity_reject(self):
        with tempfile.TemporaryDirectory(prefix='read-metadata-',dir=TASK)as temp:
            root=Path(temp).resolve();self.assertTrue(root.is_relative_to(TASK.resolve()));p=root/'x';p.write_bytes(b'x');st=p.stat();values={k:getattr(st,k)for k in('st_mode','st_dev','st_ino','st_size','st_mtime_ns','st_nlink','st_ctime_ns')};values['st_ctime_ns']+=999999
            with patch.object(os,'fstat',return_value=types.SimpleNamespace(**values)):self.assertEqual(self.m['_read'](root,'x',self.m['sh'](b'x')),b'x')
            values['st_ino']+=1
            with patch.object(os,'fstat',return_value=types.SimpleNamespace(**values)):self.safe_reject(lambda:self.m['_read'](root,'x',self.m['sh'](b'x')))
    def test_16_paths_bounds_nlink_and_reader_IO_are_safe(self):
        with tempfile.TemporaryDirectory(prefix='read-bounds-',dir=TASK)as temp:
            root=Path(temp).resolve();self.assertTrue(root.is_relative_to(TASK.resolve()));p=root/'x';p.write_bytes(b'x')
            for name in('../x','x/../x','C:/x','x\\y',''):
                self.safe_reject(lambda name=name:self.m['_read'](root,name,'0'*64))
            st=p.stat();values={k:getattr(st,k)for k in('st_mode','st_dev','st_ino','st_size','st_mtime_ns','st_nlink','st_ctime_ns')};values['st_nlink']=2
            with patch.object(Path,'lstat',return_value=types.SimpleNamespace(**values)):self.safe_reject(lambda:self.m['_read'](root,'x','0'*64))
        with patch.object(Path,'open',side_effect=OSError(CANARY)):self.safe_reject(lambda:self.m['prepare_batch'](ROOT))
    def test_17_actual_batch_final_race_rejects_and_latches(self):
        b=self.m['prepare_batch'](ROOT);b.validate_claim(*self.m['CLAIM'],'PASS',self.derived,ROOT,json_pointer='/claims/0');p=ROOT/self.m['DERIVED'];raw=p.read_bytes();st=p.stat();bad=raw[:-1]+b' '
        try:
            p.write_bytes(bad);os.utime(p,ns=(st.st_atime_ns,st.st_mtime_ns));self.safe_reject(b.verify_unchanged);p.write_bytes(raw);self.safe_reject(b.require_finalized);self.safe_reject(b.verify_unchanged)
        finally:p.write_bytes(raw)
    def test_18_actual_private_INSTALL_only_CLI_dispatch_and_final_barrier(self):
        integration=json.loads((TASK/'private-integration-proposal.json').read_bytes());candidate=json.loads(Path(integration['candidate_ledger']).read_bytes());row=integration['private_replacement_row']
        with tempfile.TemporaryDirectory(prefix='private-install-dispatch-',dir=TASK)as temp:
            root=Path(temp).resolve();self.assertTrue(root.is_relative_to(TASK.resolve()))
            for n,raw in self.blobs.items():p=root/n;p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(raw)
            names=[*integration['existing_import_files_sha256'],'scripts/prepare-local-f0-status.py']
            for n in names:p=root/n;p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes((ROOT/n).read_bytes())
            ledger=root/'context/reconciliation/local-f0-assertion-evidence.json';ledger.write_text(json.dumps({'assertions':[row],'executions':candidate['executions'][-1:]}),encoding='utf8')
            output=io.StringIO();before=set(sys.modules);sys.path.insert(0,str(root/'scripts'))
            try:
                with contextlib_redirect(output):runpy.run_path(str(root/'scripts/prepare-local-f0-status.py'),run_name='__main__')
                result=json.loads((root/'context/reconciliation/local-f0-qualification-status.json').read_bytes());self.assertEqual(result['assertion_status_counts']['PASS'],1);self.assertEqual(result['case_status_counts']['PASS'],0)
            finally:
                sys.path.pop(0)
                for name in set(sys.modules)-before:
                    if name.startswith('local_f0_'):sys.modules.pop(name,None)
        self.assertNotIn(CANARY,output.getvalue())
    def test_19_actual_public_final_read_race_and_only_legacy_reader_restoration(self):
        target=ROOT/next(reversed(self.m['PINS']));raw=target.read_bytes();bad=raw[:-1]+(b' 'if raw[-1:]!=b' 'else b'\n');before=target.stat();opening=Path.open
        for legacy in(False,True):
            with self.subTest(legacy=legacy):
                batch=self.m['prepare_batch'](ROOT);batch.validate_claim(*self.m['CLAIM'],'PASS',self.derived,ROOT,json_pointer='/claims/0');fired=[]
                class Handle:
                    def __init__(self,h):self.h=h
                    def __enter__(self):return self
                    def __exit__(self,*a):return self.h.__exit__(*a)
                    def fileno(self):return self.h.fileno()
                    def read(self,*a):
                        v=self.h.read(*a)
                        if not fired:
                            fired.append(True)
                            with opening(target,'wb')as w:w.write(bad)
                            os.utime(target,ns=(before.st_atime_ns,before.st_mtime_ns))
                        return v
                def opened(path,*a,**k):
                    h=opening(path,*a,**k);return Handle(h)if path==target and a and a[0]=='rb'else h
                try:
                    legacy_read_for_tripwire.__globals__.update(need=self.m['need'],sh=self.m['sh'])
                    with patch.object(Path,'open',opened),patch.dict(self.m,{'_read':legacy_read_for_tripwire}if legacy else{}):
                        if legacy:self.assertTrue(batch.verify_unchanged());self.assertTrue(batch.require_finalized())
                        else:self.safe_reject(batch.verify_unchanged);self.safe_reject(batch.require_finalized)
                    self.assertTrue(fired);self.assertNotEqual(hashlib.sha256(target.read_bytes()).hexdigest(),self.m['PINS'][target.relative_to(ROOT).as_posix()])
                finally:target.write_bytes(raw)
    def test_20_tripwire_legacy_function_matches_exact_preserved_old_AST(self):
        text=(ROOT/self.m['ARCHIVE']/'known-held-read-only-function.py.txt').read_text(encoding='utf8');old=ast.parse(text).body[0];new=next(n for n in ast.parse(Path(__file__).read_bytes()).body if isinstance(n,ast.FunctionDef)and n.name=='legacy_read_for_tripwire');new.name='_read';self.assertEqual(ast.dump(new,include_attributes=False),ast.dump(old,include_attributes=False))
    @classmethod
    def tearDownClass(cls):
        assert hashlib.sha256(SOURCE.read_bytes()).hexdigest()==cls.source_before
        assert all(hashlib.sha256((ROOT/n).read_bytes()).hexdigest()==h for n,h in cls.m['PINS'].items())

def contextlib_redirect(stream):
    from contextlib import redirect_stdout
    return redirect_stdout(stream)

if __name__=='__main__':unittest.main()
