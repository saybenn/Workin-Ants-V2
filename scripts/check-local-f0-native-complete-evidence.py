"""Offline actual closed520 admission and private rehashed semantic mutations."""
import ast
from contextlib import ExitStack,contextmanager
from copy import deepcopy
import hashlib
import json
import os
from pathlib import Path
import runpy
import socket
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'scripts'))
import local_f0_native_complete_evidence as A
CANARY='PRIVATE_PASSWORD_HANDLE_STDERR_STATEMENT_CANARY_51a'

@contextmanager
def forbidden():
    with ExitStack()as stack:
        for name in ('run','Popen','call','check_call','check_output'):stack.enter_context(patch.object(subprocess,name,side_effect=AssertionError('FORBIDDEN_PROCESS')))
        stack.enter_context(patch.object(os,'system',side_effect=AssertionError('FORBIDDEN_PROCESS')))
        stack.enter_context(patch.object(socket,'socket',side_effect=AssertionError('FORBIDDEN_NETWORK')))
        stack.enter_context(patch.object(socket,'create_connection',side_effect=AssertionError('FORBIDDEN_NETWORK')))
        stack.enter_context(patch('builtins.exec',side_effect=AssertionError('FORBIDDEN_PROJECT_EXEC')))
        stack.enter_context(patch('builtins.eval',side_effect=AssertionError('FORBIDDEN_PROJECT_EXEC')))
        yield


class NativeCompleteTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        with forbidden():cls.blobs={name:A.read(ROOT,name,wanted)for name,wanted in A.PINS.items()}
        cls.documents={}
        def doc(name):
            if name not in cls.documents:cls.documents[name]=A.document(cls.blobs[name])
            return cls.documents[name]
        cls.execution=doc(A.DERIVED);cls.child=doc(A.ASSET_BASE+'/evidence/native-denials/native-denial-results.json')
        cls.packet=doc(A.PACKET_PATH);cls.native=doc(A.ASSET_BASE+'/evidence/native-before.json');cls.models={v['model']:v for v in doc(A.MODEL_PATH)};cls.contract=doc(A.CONTRACT)
        cls.names=[A.RECORD,A.ASSET_BASE+'/evidence/run-evidence.json',A.ASSET_BASE+'/evidence/native-denials/native-denial-results.json',A.ASSET_BASE+'/manifest/operation-manifest.json',A.ASSET_BASE+'/evidence/native-before.json',A.ASSET_BASE+'/evidence/authentication-ok/authentication-results-ok.json',A.ASSET_BASE+'/evidence/provider-preinstall-proof.json',A.ASSET_BASE+'/evidence/native-access-attestation.json',A.ASSET_BASE+'/evidence/native-deny-run-plan.json',A.ASSET_BASE+'/independent-cleanup.json',A.ASSET_BASE+'/evidence/oracle-evidence.json',A.ASSET_BASE+'/evidence/catalog-comparison.json',A.ASSET_BASE+'/evidence/ledger-evidence.json',A.CONTRACT]
        cls.wrapper_docs=[doc(name)for name in cls.names]
        cls.proposal=doc(A.ARCHIVE+'/exact520-proposal.json');cls.inventory=doc(A.INVENTORY)
        cls.newkeys=[(row['case_id'],row['assertion_id'])for row in cls.proposal['rows']if row['proposed_action']=='PROPOSE_NEW_PASS_AFTER_REVIEWED_FAIL_CLOSED_PARSER']
    def semantic_child(self,value):
        with forbidden():return A.validate_component(value,self.packet,self.native,self.models,self.contract,self.blobs)
    def semantic_wrapper(self,docs):
        with forbidden():return A.validate_wrapper(*docs,self.blobs)
    def private_rehashed(self,value):
        """Mutants cross a real closed-byte/hash/strict JSON boundary first."""
        with tempfile.TemporaryDirectory(prefix='native-complete-private-mutant-')as directory:
            root=Path(directory).resolve();raw=(json.dumps(value,indent=2,allow_nan=False)+'\n').encode();path=root/'mutant.json';path.write_bytes(raw)
            with forbidden():closed=A.read(root,'mutant.json',hashlib.sha256(raw).hexdigest());self.assertEqual(closed,raw);return A.document(closed)
    @contextmanager
    def changed_file(self,relative,replacement,preserve_mtime=False):
        path=ROOT/relative;old=path.read_bytes();times=path.stat()
        try:
            path.write_bytes(replacement)
            if preserve_mtime:os.utime(path,ns=(times.st_atime_ns,times.st_mtime_ns))
            yield
        finally:path.write_bytes(old);os.utime(path,ns=(times.st_atime_ns,times.st_mtime_ns))
    def claim(self,batch,key):
        return batch.validate_claim(*key,'PASS',self.execution,ROOT,json_pointer='/claims/'+str(A.CLOSED_CLAIMS[key]))
    def test_golden_all520_exact_claims_closed_readers_and_only303_inputs(self):
        opened=[];actual=Path.open
        def tracked(path,*args,**kwargs):
            mode=args[0]if args else kwargs.get('mode','r')
            self.assertEqual(mode,'rb');self.assertIn(path.relative_to(ROOT).as_posix(),A.PINS)
            handle=actual(path,*args,**kwargs);opened.append(handle);return handle
        with patch.object(Path,'open',tracked),forbidden():
            batch=A.prepare_batch(ROOT,all520=True)
            self.assertTrue(all(handle.closed for handle in opened))
            for key in A.CLOSED_CLAIMS:self.assertTrue(self.claim(batch,key))
            self.assertTrue(batch.verify_unchanged());self.assertTrue(batch.require_finalized())
        self.assertEqual(len(opened),2*len(A.PINS));self.assertEqual(len(A.PINS),303);self.assertTrue(all(handle.closed for handle in opened))
    def test_standalone_admission_is_fresh_and_finally_rechecked(self):
        key=self.newkeys[0]
        with forbidden():self.assertTrue(A.validate_claim(*key,'PASS',self.execution,ROOT,json_pointer='/claims/'+str(A.CLOSED_CLAIMS[key])))
    def test_unsupported_RLS_blocked_business_vectors_positive_and_statuses(self):
        pairs=[('P0C-UNKNOWN','control.any'),('P0C-TABLE-ConsentLog-DENY','denial.wa_context_issuer.source_business_write'),('P0C-TABLE-ConsentLog-ALLOW','positive.wa_app_runtime.select'),('P0C-PRIV-01','control.issuer_ceiling'),('P0C-TABLE-DatabaseActionGrant-DENY','denial.wa_context_issuer.insert')]
        rls=next(row for row in self.child['facets']if row['status']=='PASS_EXISTING_ROW_EMPTY_ONLY');pairs.append((rls['case_id'],'denial.'+rls['role']+'.'+rls['verb'].lower()))
        for key in pairs:
            with self.subTest(key=key),forbidden(),self.assertRaises(A.EvidenceFailure):A.validate_claim(*key,'PASS',self.execution,ROOT,json_pointer='/claims/0')
        for status in ('PARTIAL','FAILED','NOT_RUN','PASS_WHOLE_CASE',True,1,None):
            with self.subTest(status=status),forbidden(),self.assertRaises(A.EvidenceFailure):A.validate_claim(*self.newkeys[0],status,self.execution,ROOT,json_pointer='/claims/0')
    def test_bad_pointer_and_forged_execution_are_not_cached_authority(self):
        with forbidden():
            for pointer in ('/claims/00','/claims/-1','/claims/9999','/claims/0/status','/source_record','claims/0'):
                with self.subTest(pointer=pointer),self.assertRaises(A.EvidenceFailure):A.validate_claim(*self.newkeys[0],'PASS',self.execution,ROOT,json_pointer=pointer)
        for field,value in (('run_id','wrong'),('source_commit','0'*40),('source_tree','0'*40),('packet_sha256','0'*64),('actual_result','PASS')):
            changed=deepcopy(self.execution);changed[field]=value
            with self.subTest(field=field),forbidden():
                batch=A.QualificationBatch(ROOT,_single=self.newkeys[0])
                with self.assertRaises(A.EvidenceFailure):batch.validate_claim(*self.newkeys[0],'PASS',changed,ROOT,json_pointer='/claims/'+str(A.CLOSED_CLAIMS[self.newkeys[0]]))
                with self.assertRaises(A.EvidenceFailure):batch.require_finalized()
    def test_partial_batch_and_omitted_or_noop_final_verify_cannot_finalize(self):
        with forbidden():
            batch=A.prepare_batch(ROOT);self.claim(batch,self.newkeys[0])
            with self.assertRaisesRegex(A.EvidenceFailure,'INCOMPLETE_BATCH'):batch.verify_unchanged()
            with self.assertRaises(A.EvidenceFailure):batch.require_finalized()
            batch=A.prepare_batch(ROOT)
            for key in self.newkeys:self.claim(batch,key)
            with self.assertRaisesRegex(A.EvidenceFailure,'FINAL_BYTE_BARRIER_REQUIRED'):batch.require_finalized()
            with patch.object(batch,'verify_unchanged',return_value=True):
                batch.verify_unchanged()
                with self.assertRaisesRegex(A.EvidenceFailure,'FINAL_BYTE_BARRIER_REQUIRED'):batch.require_finalized()
    def test_first_middle_last_and_prefinal_drift_abort_without_new_output(self):
        raw=(ROOT/A.SQL).read_bytes();changed=raw[:-1]+(b' 'if raw[-1:]!=b' 'else b'\n');self.assertEqual(len(raw),len(changed))
        for position in (0,len(self.newkeys)//2,len(self.newkeys)-1,len(self.newkeys)):
            with self.subTest(position=position),tempfile.TemporaryDirectory(prefix='native-complete-no-output-')as directory,forbidden():
                batch=A.prepare_batch(ROOT);output=Path(directory)/'status.json'
                for key in self.newkeys[:position]:self.claim(batch,key)
                with self.changed_file(A.SQL,changed,preserve_mtime=True):
                    for key in self.newkeys[position:]:self.claim(batch,key)
                    with self.assertRaises(A.EvidenceFailure):
                        batch.verify_unchanged();batch.require_finalized();output.write_text('UNREACHABLE_NEW_PASS')
                    self.assertFalse(output.exists())
                with self.assertRaises(A.EvidenceFailure):batch.require_finalized()
    def test_pin_and_read_failures_never_export_canary(self):
        with self.changed_file(A.RECORD,CANARY.encode()),forbidden(),self.assertRaises(A.EvidenceFailure)as error:A.prepare_batch(ROOT)
        self.assertNotIn(CANARY,str(error.exception))
        with patch.object(Path,'open',side_effect=OSError(CANARY)),forbidden(),self.assertRaises(A.EvidenceFailure)as error:A.prepare_batch(ROOT)
        self.assertEqual(str(error.exception),'NATIVE_COMPLETE_EVIDENCE_REJECTED')
    def test_source_paths_size_symlinks_and_strict_JSON(self):
        for name in ('../outside','/absolute','C:/outside','x\\outside','./file','x//file','x/../file'):
            with self.subTest(name=name),self.assertRaises(A.EvidenceFailure):A.read(ROOT,name,'0'*64)
        for raw in (b'{"x":1,"x":2}',b'{"x":NaN}',b'{"x":Infinity}'):
            with self.subTest(raw=raw),self.assertRaises(A.EvidenceFailure):A.document(raw)
        with patch.object(Path,'is_symlink',return_value=True),self.assertRaises(A.EvidenceFailure):A.read(ROOT,A.SQL,A.PINS[A.SQL])
    def test_same_closed_bytes_are_parsed_not_a_second_file_read(self):
        original=Path.read_text
        with patch.object(Path,'read_text',side_effect=AssertionError('UNVERIFIED_SECOND_READ')),forbidden():
            batch=A.prepare_batch(ROOT)
            for key in self.newkeys:self.claim(batch,key)
            batch.verify_unchanged();batch.require_finalized()
    def test_module_is_stdlib_readonly_and_builder_barrier_precedes_return(self):
        tree=ast.parse((ROOT/'scripts/local_f0_native_complete_evidence.py').read_bytes());forbidden_names={'exec','eval','compile','__import__','Popen','run','socket','connect','write_text','write_bytes','system'}
        imports={alias.name for node in ast.walk(tree)if isinstance(node,ast.Import)for alias in node.names}|{node.module for node in ast.walk(tree)if isinstance(node,ast.ImportFrom)}
        self.assertEqual(imports,{'hashlib','json','pathlib','re','collections','types'})
        for node in ast.walk(tree):
            if isinstance(node,ast.Call):self.assertNotIn(node.func.id if isinstance(node.func,ast.Name)else node.func.attr if isinstance(node.func,ast.Attribute)else '',forbidden_names)
        tree=ast.parse((ROOT/'scripts/prepare-local-f0-status.py').read_bytes());build=next(n for n in tree.body if isinstance(n,ast.FunctionDef)and n.name=='build');calls=[n for n in ast.walk(build)if isinstance(n,ast.Call)and isinstance(n.func,ast.Attribute)and n.func.attr in ('verify_unchanged','require_finalized')]
        self.assertEqual([node.func.attr for node in sorted(calls,key=lambda n:n.lineno)],['verify_unchanged','require_finalized']);self.assertLess(max(n.lineno for n in calls),next(n.lineno for n in build.body if isinstance(n,ast.Return)))
    def test_actual_builder_entrypoint_admission_failure_writes_no_status(self):
        # Keep the test repeatable after a status has already been generated.
        # The exact builder bytes run in a fresh minimal private root; failure
        # occurs during Native admission before any legacy validator is needed.
        with tempfile.TemporaryDirectory(prefix='native-complete-builder-failure-')as directory:
            isolated=Path(directory);(isolated/'scripts').mkdir();rec=isolated/'context/reconciliation';rec.mkdir(parents=True)
            builder=isolated/'scripts/prepare-local-f0-status.py';builder.write_bytes((ROOT/'scripts/prepare-local-f0-status.py').read_bytes())
            for filename in('local-f0-assertions.json','local-f0-assertion-evidence.json'):(rec/filename).write_bytes((ROOT/'context/reconciliation'/filename).read_bytes())
            output=rec/'local-f0-qualification-status.json';self.assertFalse(output.exists())
            with patch.object(A,'prepare_batch',side_effect=A.EvidenceFailure('NATIVE_COMPLETE_PIN_DRIFT')):
                with self.assertRaisesRegex(AssertionError,'NATIVE_COMPLETE_PIN_DRIFT'):runpy.run_path(str(builder),run_name='__main__')
            self.assertFalse(output.exists())
    def test_semantic_child_closure_SQL_role_statement_and_context_mutants(self):
        mutations=[lambda c:c['operations'][0].update(closed_before_observers=False),lambda c:c['operations'][0].update(actual_login_context_absent=False),lambda c:c['operations'][0].update(role='wa_app_runtime'),lambda c:c['operations'][2].update(source_sql_sha256='0'*64),lambda c:c['operations'][0]['session_after_close'].update(readers_finished=False),lambda c:c['operations'][0]['session_after_close'].update(backend_absence_confirmed=False),lambda c:c['operations'][0]['session_after_capture'].update(backend_tuple_present=False),lambda c:c.update(current_case=None),lambda c:c.update(current_probe=None),lambda c:c.update(status='STOPPED_PARTIAL_EVIDENCE_PRESERVED'),lambda c:c['operations'][0].update(raw_stderr=CANARY),lambda c:c['operations'][0]['session_after_close'].update(raw_handle=CANARY),lambda c:c['operations'][0]['fingerprint_checks'].update(unknown=True)]
        for index,mutate in enumerate(mutations):
            value=deepcopy(self.child);mutate(value)
            with self.subTest(index=index),self.assertRaises(A.EvidenceFailure):self.semantic_child(self.private_rehashed(value))
    def test_semantic_exact42501_gates_flags_and_privileges(self):
        mutations=[lambda c:c['facets'][0]['diagnostic'].update(sqlstate='P0001'),lambda c:c['facets'][0]['diagnostic'].update(observed_gate='TABLE'),lambda c:c['facets'][0]['diagnostic'].update(selected_column_isolation_claimed=True),lambda c:c['facets'][0]['diagnostic'].update(source_position_verified=False),lambda c:c['operations'][2]['source_native_privilege_projection'].update(schema_usage=True),lambda c:c['operations'][2]['source_native_privilege_projection'].update(required_permission_missing=False),lambda c:c['facets'][0].update(whole_case_promoted=True)]
        for index,mutate in enumerate(mutations):
            value=deepcopy(self.child);mutate(value)
            with self.subTest(index=index),self.assertRaises(A.EvidenceFailure):self.semantic_child(self.private_rehashed(value))
    def test_semantic_all42_fingerprints205_counts100_guards_and_controls(self):
        def forged_everywhere(c):
            c['native_fact_projection'][0]['rows_sha256']='0'*64
            for op in c['operations']:op['data_projection'][0]['rows_sha256']='0'*64
            c['current']['data_projection'][0]['rows_sha256']='0'*64
        mutations=[forged_everywhere,lambda c:c['native_fact_projection'][0].update(row_count=True),lambda c:c['operations'][0].update(all_100_trigger_functions_restored=False),lambda c:c['operations'][0]['fingerprint_checks'].update(source_name_order=False),lambda c:c['native_controls'][0].update(rollback_and_restoration_proven=False),lambda c:c['native_controls'][0].update(update_controls_one=1.0),lambda c:c['selected_cases'][0].update(status='PASS'),lambda c:next(row for row in c['facets']if row['status']=='NOT_RUN').update(status='PASS_OBSERVED_NATIVE_GATE_ONLY')]
        for index,mutate in enumerate(mutations):
            value=deepcopy(self.child);mutate(value)
            with self.subTest(index=index),self.assertRaises((A.EvidenceFailure,KeyError)):self.semantic_child(self.private_rehashed(value))
    def test_semantic_wrapper_run_CID_auth_provider_finalizer_native_oracle_ledger_cleanup(self):
        mutations=[lambda d:d[0].update(run_id='wrong'),lambda d:d[0].update(source_commit='0'*40),lambda d:d[2]['resource'].update(container_id='0'*64),lambda d:d[5]['authentication'][0].update(wrong_password_exit_code=True),lambda d:d[5]['effective_hba_selections'][0].update(method='trust'),lambda d:d[6].update(canonical_install_removed_all_nine=False),lambda d:next(iter(d[1]['targets'].values()))['finalization_observation'].update(grantor='wa_migrator'),lambda d:d[11]['check_counts'].update(PASS=29089.0),lambda d:d[10]['results'].update(expression_count=416.0),lambda d:d[1]['ledger_comparison']['checks'][0].update(status='FAIL'),lambda d:d[12]['observation']['history'][0].update(steps=True),lambda d:d[4]['triggers'][0].update(enabled='D'),lambda d:d[4]['functions'][0].update(body_sha256='0'*64),lambda d:d[9].update(private_directory_absent=False),lambda d:d[2]['resource']['labels'].update({'workinants.rehearsal.run':'wrong'}),lambda d:d[1]['public_baseline_verification'].update(learned_post_install_baseline=True),lambda d:d[1]['ledger_comparison']['checks'][0].update(expected_sha256=True,actual_sha256=True),lambda d:d[2]['authentication_comparisons'].update(unknown=True)]
        for index,mutate in enumerate(mutations):
            docs=deepcopy(self.wrapper_docs);mutate(docs)
            with self.subTest(index=index),self.assertRaises(A.EvidenceFailure):self.semantic_wrapper(self.private_rehashed(docs))
    def test_semantic_mapping_RLS_pointer_requirement_and_whole_case_mutants(self):
        mutations=[lambda v:v['claims'][0].update(whole_case_promoted=True),lambda v:v['claims'][0].update(expected_assertion_sha256='0'*64),lambda v:v['claims'][0].update(complete_source_assertion_sha256='0'*64),lambda v:v['claims'][0]['component'].update(facet_json_pointer='/facets/12'),lambda v:v['claims'][0]['component'].update(operation_json_pointer='/operations/99999'),lambda v:v['claims'][0].update(assertion_id='denial.wa_context_issuer.source_business_write')]
        for index,mutate in enumerate(mutations):
            value=deepcopy(self.execution);mutate(value)
            with self.subTest(index=index),self.assertRaises(A.EvidenceFailure):A.validate_links(self.private_rehashed(value),self.proposal,self.inventory,self.child)
    def test_ledger_only388_append_old259_and132_corroborations_unchanged(self):
        old=json.loads((ROOT/A.ARCHIVE/'preserved/assertion-evidence.before259.json').read_bytes());new=json.loads((ROOT/'context/reconciliation/local-f0-assertion-evidence.json').read_bytes())
        self.assertEqual(len(old['assertions']),259);self.assertEqual(len(new['assertions']),647);self.assertEqual(new['assertions'][:259],old['assertions']);self.assertTrue(all(row['status']=='PASS'for row in new['assertions'][259:]))
        self.assertEqual(len({(r['case_id'],r['assertion_id'])for r in old['assertions']}&set(A.CLOSED_CLAIMS)),132)
        self.assertFalse(any('source_business_write'in row['assertion_id']for row in new['assertions'][259:]))

if __name__=='__main__':unittest.main(verbosity=2)
