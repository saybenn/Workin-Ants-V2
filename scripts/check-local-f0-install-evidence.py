"""Focused real-data INSTALL adapter checks; every mutation is TASK-private.

The real Root full builder and ledger/status installation require later review.
These tests never execute archived runtime/source, SQL, processes or networks.
"""
import ast,collections,contextlib,hashlib,io,json,math,os,runpy,socket,subprocess,sys,tempfile,types,unittest
from copy import deepcopy
from pathlib import Path
from unittest.mock import patch
import local_f0_install_evidence as E

ROOT=Path(__file__).resolve().parents[1]
DRAFT=ROOT.parent
TASK=DRAFT.parent

def data(value):return (json.dumps(value,indent=2,allow_nan=False)+'\n').encode()
def blocked(*args,**kwargs):raise AssertionError('PROCESS_OR_NETWORK_NOT_ALLOWED')

class InstallEvidenceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.original_pins=dict(E.PINS)
        cls.original={n:(ROOT/n).read_bytes()for n in E.PINS}
        cls.execution=json.loads(cls.original[E.DERIVED])
        cls.temp=tempfile.TemporaryDirectory(prefix='install4b35-adapter-',dir=TASK/'test-tmp')
        cls.root=Path(cls.temp.name)/'root'
        for n,raw in cls.original.items():
            p=cls.root/n;p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(raw)
        cls.boundaries=[patch.object(subprocess,'run',blocked),patch.object(subprocess,'Popen',blocked),patch.object(socket,'socket',blocked),patch.object(socket,'create_connection',blocked)]
        for boundary in cls.boundaries:boundary.start()

    @classmethod
    def tearDownClass(cls):
        E.PINS=cls.original_pins
        for boundary in reversed(cls.boundaries):boundary.stop()
        cls.temp.cleanup()

    def setUp(self):
        E.PINS=dict(self.original_pins)
        for n,raw in self.original.items():
            p=self.root/n
            if not p.exists()or p.read_bytes()!=raw:
                if p.is_symlink():p.unlink()
                p.write_bytes(raw)

    def prepare(self):return E.prepare_batch(self.root)
    def admit(self,batch):
        for key in E.LEDGER_CHANGES:batch.validate_claim(*key,E.CLAIM_STATUSES[key],deepcopy(self.execution),self.root,json_pointer='/claims/'+str(E.CLOSED_CLAIMS[key]))
    def finish(self,batch):
        self.admit(batch);batch.verify_unchanged();return batch.require_finalized()

    def semantic(self,name,mutate):
        """Rehash only private fixture bytes; no runtime factory or verdict patch."""
        blobs=dict(self.original);value=json.loads(blobs[name]);mutate(value);blobs[name]=data(value)
        record=json.loads(blobs[E.REC])
        if name in record['assets_sha256']:
            record['assets_sha256'][name]=E.sha(blobs[name]);blobs[E.REC]=data(record)
        derived=json.loads(blobs[E.DERIVED]);derived['source_record']['sha256']=E.sha(blobs[E.REC]);blobs[E.DERIVED]=data(derived)
        E.PINS={n:E.sha(raw)for n,raw in blobs.items()}
        return blobs

    def test_01_exact17_requirements_and_preserved653_provenance(self):
        self.assertEqual(E.validate_bundle(dict(self.original)),E.canonical(self.execution))
        self.assertEqual(len(E.CLOSED_CLAIMS),17);self.assertEqual(len(E.LEDGER_CHANGES),5)
        self.assertEqual(collections.Counter(x['status']for x in self.execution['claims']),{'PASS':16,'PARTIAL':1})
        before=json.loads(self.original[E.ARCHIVE+'/prior653-ledger.json'])
        proposed=json.loads((DRAFT/'proposed-ledger.base653-to656.json').read_bytes())
        lookup={(x['case_id'],x['assertion_id']):x for x in proposed['assertions']}
        upgrades=[]
        for row in before['assertions']:
            key=(row['case_id'],row['assertion_id'])
            if key in E.LEDGER_CHANGES:
                self.assertEqual(row['status'],'PARTIAL');self.assertEqual(lookup[key]['status'],'PASS');self.assertEqual(lookup[key]['previous_evidence'],row);self.assertEqual(lookup[key]['previous_evidence_sha256'],E.sha(E.canonical(row).encode()));upgrades.append(key)
            else:self.assertEqual(lookup[key],row)
        self.assertEqual(len(upgrades),2);self.assertEqual(len(proposed['assertions']),656)
        self.assertEqual(proposed['executions'][:-1],before['executions'])
        self.assertEqual(before['assertions'][647:],proposed['assertions'][647:653])

    def test_02_actual_five_batch_and_required_final_barrier(self):
        batch=self.prepare()
        with self.assertRaises(E.EvidenceFailure):batch.require_finalized()
        self.assertTrue(self.finish(batch))
        with self.assertRaises(E.EvidenceFailure):batch.verify_unchanged()

    def test_03_closed_claim_status_pointer_and_safe_forged_record(self):
        # Invalid calls reject before any file admission. Full legitimate batch
        # is actual in test02; each of the17 closed contracts is checked here.
        for key,index in E.CLOSED_CLAIMS.items():
            for bad_status in ('FAILED','NOT_RUN',True,1,'PASS'if E.CLAIM_STATUSES[key]=='PARTIAL'else'PARTIAL'):
                with self.subTest(key=key,status=bad_status),self.assertRaises(E.EvidenceFailure):E.validate_claim(*key,bad_status,self.execution,self.root,json_pointer='/claims/'+str(index))
        key=E.LEDGER_CHANGES[0]
        for bad in('/claims/00','/claims/-1','/claims/0/status','/results/0',None):
            with self.assertRaises(E.EvidenceFailure):E.validate_claim(*key,E.CLAIM_STATUSES[key],self.execution,self.root,json_pointer=bad)
        for bad in [('P0C-INSTALL-01','vector.INSTALL.positive'),('P0C-RLS-01','control.visibility'),('P0C-INSTALL-02','whole_case')]:
            with self.assertRaises(E.EvidenceFailure):E.validate_claim(*bad,'PASS',self.execution,self.root,json_pointer='/claims/0')
        batch=self.prepare();forged=deepcopy(self.execution);forged['source_tree']='SECRET-CANARY-NEVER-RETAIN'
        with self.assertRaises(E.EvidenceFailure)as caught:batch.validate_claim(*key,E.CLAIM_STATUSES[key],forged,self.root,json_pointer='/claims/'+str(E.CLOSED_CLAIMS[key]))
        self.assertNotIn('SECRET-CANARY',str(caught.exception))
        with self.assertRaises(E.EvidenceFailure):batch.verify_unchanged()

    def test_04_missing_duplicate_and_sticky_batch(self):
        batch=self.prepare();key=E.LEDGER_CHANGES[0];args=(*key,E.CLAIM_STATUSES[key],self.execution,self.root)
        batch.validate_claim(*args,json_pointer='/claims/'+str(E.CLOSED_CLAIMS[key]))
        with self.assertRaises(E.EvidenceFailure):batch.validate_claim(*args,json_pointer='/claims/'+str(E.CLOSED_CLAIMS[key]))
        with self.assertRaises(E.EvidenceFailure):batch.verify_unchanged()
        batch=self.prepare()
        with self.assertRaises(E.EvidenceFailure):batch.verify_unchanged()
        with self.assertRaises(E.EvidenceFailure):batch.require_finalized()

    def test_05_strict_json_path_size_link_and_windows_descriptor(self):
        for raw in (b'{"a":1,"a":2}',b'{"a":NaN}',b'{"a":Infinity}',b'{"a":1e999}',b'not-json-SECRET-CANARY'):
            with self.assertRaises(Exception):E.doc(raw)
        self.assertEqual(E.doc(b'{"elapsed_seconds":2.648}'),{'elapsed_seconds':2.648})
        for name in('../escape','a\\b','C:/absolute','/absolute','x//a'):
            with self.assertRaises(E.EvidenceFailure):E._read(self.root,name,'0'*64)
        keys=('st_mode','st_dev','st_ino','st_size','st_mtime_ns','st_nlink','st_ctime_ns');original=os.fstat
        def offset(fd):
            s=original(fd);return types.SimpleNamespace(**{k:getattr(s,k)+(1000000000 if k=='st_ctime_ns'else 0)for k in keys})
        with patch.object(os,'fstat',offset):self.assertEqual(E._read(self.root,E.DERIVED,E.PINS[E.DERIVED]),self.original[E.DERIVED])
        def wrong_inode(fd):
            s=original(fd);return types.SimpleNamespace(**{k:getattr(s,k)+(1 if k=='st_ino'else 0)for k in keys})
        with patch.object(os,'fstat',wrong_inode),self.assertRaises(E.EvidenceFailure):E._read(self.root,E.DERIVED,E.PINS[E.DERIVED])
        path=self.root/E.DERIVED;link=path.with_name('private-hard-link.json')
        try:os.link(path,link)
        except OSError:pass
        else:
            try:
                with self.assertRaises(E.EvidenceFailure):E._read(self.root,E.DERIVED,E.PINS[E.DERIVED])
            finally:link.unlink()
        huge=path.with_name('private-oversize.json');huge.write_bytes(b'x'*(8*1024*1024+1))
        try:
            with self.assertRaises(E.EvidenceFailure):E._read(self.root,huge.relative_to(self.root).as_posix(),E.sha(huge.read_bytes()))
        finally:huge.unlink()

    def test_06_rehashed_actual_failure_auth_closure_and_cleanup_mutants(self):
        child=E.B+'/evidence/install-controls/install-controls-results.json'
        mutations=[lambda x:x.update(status='IN_PROGRESS'),lambda x:x.update(source_tree='0'*40),lambda x:x['targets']['canonical']['auth_wa_app_runtime'].update(wrong_password='NOT_RUN'),lambda x:x['targets']['canonical']['settings'].update(no_error_statements=False),lambda x:x['targets']['canonical']['original_cleanup'].update(temporary_memberships=False),lambda x:x['targets']['canonical']['wrong_grantor'].update(sqlstate='42501'),lambda x:x['targets']['canonical']['wrong_grantor'].update(source_line=7),lambda x:x['targets']['canonical']['activation_gate_held'].update(database_password_sql_executed=True),lambda x:x['targets']['canonical']['BEFORE_INSTALL_RUNTIME_INACTIVE'].update(all_null_verifiers=False),lambda x:x['targets']['late_function_grant']['failure_verdict'].update(primary_sqlstate='P0001'),lambda x:x['targets']['late_function_grant']['failure_verdict']['delta'].update(secondary_25p02=True),lambda x:x['targets']['late_function_grant']['ledger']['rows'][0].update(logs_state='NONNULL'),lambda x:x['targets']['late_function_grant']['inventory'].update(functions=1),lambda x:x['targets']['division_failure']['ledger']['rows'][0].update(immutable_sha256='0'*64),lambda x:x['targets']['division_failure']['ledger']['rows'][1].update(steps=True),lambda x:x['targets']['division_failure']['recovery_result'].update(failed_row_retained_unchanged=False)]
        for index,mutate in enumerate(mutations):
            with self.subTest(index=index),self.assertRaises(E.EvidenceFailure):E.validate_bundle(self.semantic(child,mutate))
        def closure(x):next(v for k,v in x['targets']['canonical'].items()if k.startswith('closure_')).update(all_other_clients_absent=False)
        with self.assertRaises(E.EvidenceFailure):E.validate_bundle(self.semantic(child,closure))
        parent=E.B+'/evidence/run-evidence.json'
        for mutate in [lambda x:x.update(evidence_complete=False),lambda x:x['targets']['wa-p0c-4b35e08b-install-good'].update(container_id='0'*64),lambda x:x['targets']['wa-p0c-4b35e08b-install-good'].update(network_mode='bridge'),lambda x:x['backend_closures'][0].update(other_clients_zero=False),lambda x:x['cleanup_summary'].update(private_directory_absent=False)]:
            with self.assertRaises(E.EvidenceFailure):E.validate_bundle(self.semantic(parent,mutate))

    def test_07_rehashed_partial_upgrades_exact_pointers_and_limits(self):
        changes=[lambda x:x['claims'].pop(),lambda x:x['claims'].append(deepcopy(x['claims'][0])),lambda x:x['claims'].__setitem__(0,deepcopy(x['claims'][1])),lambda x:x['claims'][0].update(assertion_id='whole_case'),lambda x:x['limits'].update(whole_case_promoted=True),lambda x:x['limits'].update(failure_precleanup_activation_phase='PASS')]
        partial=next(i for i,x in enumerate(self.execution['claims'])if x['status']=='PARTIAL')
        changes.extend([lambda x:x['claims'][partial].update(status='PASS'),lambda x:x['claims'][partial].update(missing_required_piece=None)])
        upgrade=next(i for i,x in enumerate(self.execution['claims'])if x['action']=='PROPOSE_PARTIAL_TO_PASS_WITH_PRIOR_PROVENANCE_RETAINED')
        changes.extend([lambda x:x['claims'][upgrade].update(prior_evidence=None),lambda x:x['claims'][upgrade]['prior_evidence'].update(source_commit='0'*40),lambda x:x['claims'][upgrade]['mapping'].update(json_pointer='/rows/0')])
        for index,mutate in enumerate(changes):
            with self.subTest(index=index),self.assertRaises(E.EvidenceFailure):E.validate_bundle(self.semantic(E.DERIVED,mutate))

    def test_08_actual_source_native312_and_nonname_semantics(self):
        expected=json.loads(self.original['review-output/native-catalog/expected.json'])['expected'];native=json.loads(self.original[E.B+'/evidence/canonical-native-before.json'])
        view,names=E.semantic_view(native,expected);self.assertEqual(len(names),312)
        self.assertEqual(E.sha(E.canonical(view).encode()),'534d6edf382bf324664d272e66e28e16d3da79ab9411693c722bec9bff4aae06')
        for field,value in [('enabled','D'),('type_bits',True),('internal',False),('argument_count',1),('function_release_builtin',False),('constraint_index','wrong'),('dependencies',[]),('deferrable',True)]:
            changed=deepcopy(native);next(x for x in changed['triggers']if x['internal']).update({field:value})
            with self.subTest(field=field),self.assertRaises(E.EvidenceFailure):E.semantic_view(changed,expected)
        bad=deepcopy(expected)
        next(x for t in bad['tables'].values()for x in t['constraints']if x['kind']=='FOREIGN')['delete_action']='c'
        with self.assertRaises(E.EvidenceFailure):E.semantic_view(native,bad)
        native['triggers'].append(deepcopy(native['triggers'][0]))
        with self.assertRaises(E.EvidenceFailure):E.semantic_view(native,expected)

    def test_09_full_native_count_oracle_and_ledger_mutants(self):
        for suffix,mutate in [('canonical-catalog-comparison.json',lambda x:x['check_counts'].update(PASS=29089.0)),('canonical-oracle-results.json',lambda x:x.update(expression_count=True)),('canonical-ledger-comparison.json',lambda x:x['checks'][0].update(status='FAIL')),('recovered-ledger-comparison.json',lambda x:x['checks'].pop()),('canonical-catalog-comparison.json',lambda x:x.update(native_snapshot_sha256='0'*64))]:
            with self.subTest(suffix=suffix),self.assertRaises(E.EvidenceFailure):E.validate_bundle(self.semantic(E.B+'/evidence/'+suffix,mutate))

    def test_10_source_five_packet_hash_approval_and_deadline_changes(self):
        # Fixed closed hashes are the admission gate for all source and evidence.
        for name in ('review-output/foundation-application.review.sql','context/reconciliation/local-f0-install-controls-owned-parity-v4-source-validation.json',E.B+'/evidence/install-controls/independent-recovery-approval.json',E.B+'/Catalog-explicit-actual-approval-receipt.json'):
            blobs=dict(self.original);blobs[name]+=b' '
            with self.subTest(name=name),self.assertRaises(E.EvidenceFailure)as caught:E.validate_bundle(blobs)
            self.assertEqual(str(caught.exception),'CAPTURED_HASHES')
        for mutate in [lambda x:x.update(original_deadline_monotonic=185785.187),lambda x:x.update(remaining_seconds_after_publication=math.inf),lambda x:x['approval'].update(container_id='0'*64),lambda x:x['approval'].update(decision='APPROVED_UNBOUNDED')]:
            if mutate.__code__.co_consts and math.inf in mutate.__code__.co_consts:continue
            try:blobs=self.semantic(E.B+'/Catalog-explicit-actual-approval-receipt.json',mutate)
            except ValueError:continue
            with self.assertRaises(E.EvidenceFailure):E.validate_bundle(blobs)

    def race(self,old_reader=None,freeze_metadata=False):
        target=self.root/E.DERIVED;original=self.original[E.DERIVED];target.write_bytes(original)
        changed=original.replace(b'"status": "PASS"',b'"status": "FAIL"',1);self.assertNotEqual(changed,original);self.assertEqual(len(changed),len(original))
        before=target.stat();factory=E.prepare_batch;batch=factory(self.root);self.admit(batch)
        opening=Path.open;lstat0=Path.lstat;fstat0=os.fstat;handles=[];target_fds=set();template=[];mutated=[]
        class Reader:
            def __init__(self,reader):self.reader=reader;handles.append(reader);target_fds.add(reader.fileno());template.append(fstat0(reader.fileno()))
            def __enter__(self):self.reader.__enter__();return self
            def __exit__(self,*args):target_fds.discard(self.reader.fileno());return self.reader.__exit__(*args)
            def __getattr__(self,name):return getattr(self.reader,name)
            def read(reader,size=-1):
                value=reader.reader.read(size)
                if not mutated:
                    with opening(target,'wb')as writer:writer.write(changed);writer.flush();os.fsync(writer.fileno())
                    os.utime(target,ns=(before.st_atime_ns,before.st_mtime_ns));mutated.append(True)
                return value
        def hook(path,*args,**kwargs):
            reader=opening(path,*args,**kwargs);mode=args[0]if args else kwargs.get('mode','r')
            return Reader(reader)if path==target and mode=='rb'else reader
        failure=None;barrier=False;finalized=False
        with patch.object(Path,'open',hook),contextlib.ExitStack()as stack:
            if old_reader is not None:stack.enter_context(patch.object(E,'_read',old_reader))
            if freeze_metadata:
                stack.enter_context(patch.object(Path,'lstat',lambda path,*a,**k:before if path==target else lstat0(path,*a,**k)))
                stack.enter_context(patch.object(os,'fstat',lambda fd:template[0]if fd in target_fds else fstat0(fd)))
            try:barrier=batch.verify_unchanged();finalized=batch.require_finalized()
            except E.EvidenceFailure as error:failure=str(error)
        self.assertTrue(mutated);self.assertTrue(all(h.closed for h in handles));self.assertIs(E.prepare_batch,factory);self.assertEqual(E.PINS,self.original_pins)
        after=target.stat();self.assertEqual((before.st_ino,before.st_size,before.st_mtime_ns,before.st_nlink),(after.st_ino,after.st_size,after.st_mtime_ns,after.st_nlink))
        self.assertNotEqual(E.sha(target.read_bytes()),E.PINS[E.DERIVED])
        return {'rejected':failure is not None,'failure':failure,'barrier':barrier,'finalized':finalized}

    def test_11_actual_factory_final_read_race_and_only_old_reader_tripwire(self):
        fixed=self.race();self.assertTrue(fixed['rejected']);self.assertFalse(fixed['finalized'])
        # Source-sensitive mutation restores only the known defective one-read
        # implementation. No PINS, expected hash, factory, or proof replacement.
        fixture=ROOT/E.ARCHIVE/'test-fixtures/original-defective-reader.py.txt'
        raw=fixture.read_bytes();self.assertEqual(E.sha(raw),'1e24bf2ba9ee4d15d498c75abf77f7e1f17b909c46f7e5efc4cd493249520593')
        function=next(n for n in ast.parse(raw).body if isinstance(n,ast.FunctionDef)and n.name=='_read');namespace=dict(vars(E))
        exec(compile(ast.Module(body=[function],type_ignores=[]),'<original-reader-only-restoration>','exec'),namespace)
        old_read=namespace['_read']
        old=self.race(old_reader=old_read);self.assertFalse(old['rejected']);self.assertTrue(old['barrier']);self.assertTrue(old['finalized'])

    def test_12_fresh_closed_reread_rejects_stable_metadata(self):
        outcome=self.race(freeze_metadata=True);self.assertTrue(outcome['rejected']);self.assertEqual(outcome['failure'],'FILE_BYTES');self.assertFalse(outcome['finalized'])

    def install_ledger(self):
        proposed=json.loads((DRAFT/'proposed-ledger.base653-to656.json').read_bytes())
        return {'executions':[],'assertions':[x for x in proposed['assertions']if x.get('evidence_path')==E.DERIVED]}

    def test_13_actual_private_dispatcher_partial_ceiling_and_no_output_on_drift(self):
        rec=self.root/'context/reconciliation';(rec/'local-f0-assertion-evidence.json').write_bytes(data(self.install_ledger()))
        # Only the new closed five-row dispatcher is exercised. Legacy records
        # are absent, so their validators are not mocked or promoted.
        builder=self.root/'scripts/prepare-local-f0-status.py';builder.write_bytes((ROOT/'scripts/prepare-local-f0-status.py').read_bytes());output=rec/'local-f0-qualification-status.json'
        inventory=json.loads((rec/'local-f0-assertions.json').read_bytes())
        for name in inventory['source_provenance']['files_sha256']:
            p=self.root/name
            if not p.exists():p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes((ROOT/name).read_bytes())
        with patch('sys.stdout',io.StringIO()):runpy.run_path(str(builder),run_name='__main__')
        status=json.loads(output.read_bytes());self.assertEqual(status['assertion_status_counts']['PASS'],4);self.assertEqual(status['assertion_status_counts']['PARTIAL'],1);output.unlink()
        verify=E.QualificationBatch.verify_unchanged
        def drift(batch):
            p=self.root/E.REC;p.write_bytes(p.read_bytes()+b' ');return verify(batch)
        with patch.object(E.QualificationBatch,'verify_unchanged',drift),patch('sys.stdout',io.StringIO()),self.assertRaises(AssertionError):runpy.run_path(str(builder),run_name='__main__')
        self.assertFalse(output.exists())

    def test_14_pure_boundaries_exact_read_graph_and_source_scope(self):
        tree=ast.parse((ROOT/'scripts/local_f0_install_evidence.py').read_bytes())
        imports={x.name.split('.')[0]for n in ast.walk(tree)if isinstance(n,ast.Import)for x in n.names}|{n.module.split('.')[0]for n in ast.walk(tree)if isinstance(n,ast.ImportFrom)}
        self.assertLessEqual(imports,{'ast','pathlib','types','hashlib','json','math','os','re','stat'})
        self.assertFalse(any(isinstance(n,ast.Call)and isinstance(n.func,ast.Name)and n.func.id in {'exec','eval','compile','__import__'}for n in ast.walk(tree)))
        handles=[];seen=[];opening=Path.open
        def hook(path,*args,**kwargs):
            name=path.relative_to(self.root).as_posix();self.assertIn(name,E.PINS);self.assertTrue(all(h.closed for h in handles));seen.append(name);reader=opening(path,*args,**kwargs);handles.append(reader);return reader
        with patch.object(Path,'open',hook):self.assertTrue(self.finish(self.prepare()))
        self.assertEqual(collections.Counter(seen),collections.Counter({n:4 for n in E.PINS}));self.assertTrue(all(h.closed for h in handles))

if __name__=='__main__':unittest.main()
