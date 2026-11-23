"""Offline evidence-binding mutations. Never invokes a process or database."""
import hashlib,json
from pathlib import Path
import runpy
import unittest
from unittest.mock import patch
ROOT=Path(__file__).resolve().parents[1]
build=runpy.run_path(str(ROOT/'scripts/prepare-local-f0-status.py'))['build']

class StatusTests(unittest.TestCase):
    def setUp(self):
        # Native prefix bytes/132 claims and their mutations have a dedicated
        # real-data suite. These existing tests isolate legacy evidence and
        # dispatcher behavior, avoiding repeated 182-source/25-asset hashing.
        links=json.loads((ROOT/'context/reconciliation/local-f0-native-495976-exact132-links.json').read_text())['links']
        allowed={(row['case_id'],row['assertion_id']) for row in links}
        def admitted_native_boundary(case_id,assertion_id,status,execution,root,json_pointer=None):
            self.assertIn((case_id,assertion_id),allowed)
            self.assertEqual(status,'PASS')
            self.assertEqual(execution['actual_result'],'STOPPED_ATTEMPT_PRESERVED')
            self.assertEqual(json_pointer,'/actual_outcomes')
            return True
        boundary=patch.dict(build.__globals__,validate_native_prefix_claim=admitted_native_boundary)
        boundary.start();self.addCleanup(boundary.stop)
        # The new adapter has a real-data/closed28 tamper suite. Isolate its
        # boundary here while exercising the existing legacy mutations.
        from local_f0_owner_lease_evidence import CLOSED_CLAIMS, FAMILIES
        self.owner_lease_calls=[]
        def admitted_owner_lease_boundary(case_id,assertion_id,status,execution,root,json_pointer=None):
            self.assertIn((case_id,assertion_id),CLOSED_CLAIMS)
            family,index,cap=CLOSED_CLAIMS[(case_id,assertion_id)]
            self.assertEqual(status,cap)
            self.assertEqual(json_pointer,'/claims/'+str(index))
            self.assertEqual(execution['actual_result'],FAMILIES[family]['actual_result'])
            self.owner_lease_calls.append((case_id,assertion_id,status))
            return True
        new_boundary=patch.dict(build.__globals__,validate_owner_lease_claim=admitted_owner_lease_boundary)
        new_boundary.start();self.addCleanup(new_boundary.stop)
        # Only the new closed520 dispatcher is isolated here. Its independent
        # real-data/byte-barrier/semantic-mutation suite remains mandatory.
        from local_f0_native_complete_evidence import CLOSED_CLAIMS as NATIVE520
        derived=json.loads((ROOT/'context/reconciliation/local-f0-native-1110fa4-4c894dba-qualified-evidence.json').read_bytes())
        ledger=json.loads((ROOT/'context/reconciliation/local-f0-assertion-evidence.json').read_text())
        expected={(row['case_id'],row['assertion_id']) for row in ledger['assertions'] if row['evidence_path']=='context/reconciliation/local-f0-native-1110fa4-4c894dba-qualified-evidence.json'}
        self.assertEqual(len(expected),388)
        self.native_complete_calls=[];test=self
        class ClosedNativeBoundary:
            def __init__(self):self.seen=set();self.finalized=False
            def validate_claim(self,case,assertion,status,execution,root,json_pointer=None):
                key=(case,assertion);test.assertIn(key,expected);test.assertIn(key,NATIVE520);test.assertEqual(status,'PASS')
                test.assertEqual(json_pointer,'/claims/'+str(NATIVE520[key]));test.assertEqual(execution,derived)
                self.seen.add(key);test.native_complete_calls.append(key);return True
            def verify_unchanged(self):test.assertEqual(self.seen,expected);self.finalized=True;return True
            def require_finalized(self):test.assertTrue(self.finalized);return True
        def complete_boundary(root):test.assertEqual(root,ROOT);return ClosedNativeBoundary()
        boundary520=patch.dict(build.__globals__,prepare_native_complete_batch=complete_boundary)
        boundary520.start();self.addCleanup(boundary520.stop)
        # The six-read adapter has its separate real403-input/race suite and
        # an actual unmocked653-row CLI build. Isolate only this dispatcher
        # boundary while checking the legacy mutations below.
        six_path='context/reconciliation/local-f0-six-read-5f189aa-c662f807-qualified-evidence.json'
        six_derived=json.loads((ROOT/six_path).read_bytes())
        six_expected={(row['case_id'],row['assertion_id']):row['json_pointer'] for row in ledger['assertions'] if row['evidence_path']==six_path}
        self.assertEqual(len(six_expected),6);self.scoped_read_calls=[]
        class ClosedScopedBoundary:
            def __init__(self):self.seen=set();self.finalized=False
            def validate_claim(self,case,assertion,status,execution,root,json_pointer=None):
                key=(case,assertion);test.assertIn(key,six_expected);test.assertEqual(status,'PASS')
                test.assertEqual(root,ROOT);test.assertEqual(json_pointer,six_expected[key]);test.assertEqual(execution,six_derived)
                self.seen.add(key);test.scoped_read_calls.append(key);return True
            def verify_unchanged(self):test.assertEqual(self.seen,set(six_expected));self.finalized=True;return True
            def require_finalized(self):test.assertTrue(self.finalized);return True
        def scoped_boundary(root):test.assertEqual(root,ROOT);return ClosedScopedBoundary()
        boundary6=patch.dict(build.__globals__,prepare_scoped_read_batch=scoped_boundary)
        boundary6.start();self.addCleanup(boundary6.stop)
        # The actual656 CLI used the real closed446-input installation reader.
        # Its separate semantic/race suite and independent4 checks remain the
        # reader proof; isolate only this exact dispatcher boundary here.
        install_path='context/reconciliation/local-f0-install-5f189aa-4b35e08b-qualified-evidence.json'
        install_derived=json.loads((ROOT/install_path).read_bytes())
        install_expected={(row['case_id'],row['assertion_id']):(row['json_pointer'],row['status']) for row in ledger['assertions'] if row['evidence_path']==install_path}
        # Four current old-source links plus the exact superseded PARTIAL
        # complete the unchanged five-claim historical batch.
        replacement=next(row for row in ledger['assertions'] if row['evidence_path']=='context/reconciliation/local-f0-install-0ff2a91-6850ee4c-precleanup-qualified-evidence.json')
        historical=replacement['previous_evidence']
        self.assertEqual(historical['status'],'PARTIAL')
        install_expected[(historical['case_id'],historical['assertion_id'])]=(historical['json_pointer'],historical['status'])
        self.assertEqual(len(install_expected),5);self.install_calls=[]
        class ClosedInstallBoundary:
            def __init__(self):self.seen=set();self.finalized=False
            def validate_claim(self,case,assertion,status,execution,root,json_pointer=None):
                key=(case,assertion);test.assertIn(key,install_expected)
                pointer,ceiling=install_expected[key];test.assertEqual(status,ceiling,'INSTALL_CLAIM_STATUS_CEILING')
                test.assertEqual(root,ROOT);test.assertEqual(json_pointer,pointer);test.assertEqual(execution,install_derived)
                self.seen.add(key);test.install_calls.append(key);return True
            def verify_unchanged(self):test.assertEqual(self.seen,set(install_expected));self.finalized=True;return True
            def require_finalized(self):test.assertTrue(self.finalized);return True
        def install_boundary(root):test.assertEqual(root,ROOT);return ClosedInstallBoundary()
        boundary5=patch.dict(build.__globals__,prepare_install_batch=install_boundary)
        boundary5.start();self.addCleanup(boundary5.stop)
        # Worker has a separate real654-input suite and an accepted actual
        # complete671 CLI build. These legacy evidence mutations isolate only
        # its exact sixteen-row dispatch; the production reader is unchanged.
        worker_path='context/reconciliation/local-f0-worker-5f189aa-b42c35d5-qualified-evidence.json'
        worker_derived=json.loads((ROOT/worker_path).read_bytes())
        worker_rows={(row['case_id'],row['assertion_id']):row for row in ledger['assertions'] if row['evidence_path']==worker_path}
        self.assertEqual(len(worker_rows),16);self.worker_recovery_calls=[]
        class ClosedWorkerBoundary:
            def __init__(self):self.seen=set();self.finalized=False
            def validate_claim(self,case,assertion,status,execution,root,json_pointer=None,ledger_row=None):
                key=(case,assertion);test.assertIn(key,worker_rows);wanted=worker_rows[key]
                test.assertEqual(status,wanted['status'],'WORKER_CLAIM_STATUS_CEILING')
                test.assertEqual(root,ROOT);test.assertEqual(json_pointer,wanted['json_pointer'])
                test.assertEqual(execution,worker_derived);test.assertEqual(ledger_row,wanted)
                self.seen.add(key);test.worker_recovery_calls.append(key);return True
            def verify_unchanged(self):test.assertEqual(self.seen,set(worker_rows));self.finalized=True;return True
            def require_finalized(self):test.assertTrue(self.finalized);return True
        def worker_boundary(root):test.assertEqual(root,ROOT);return ClosedWorkerBoundary()
        boundary16=patch.dict(build.__globals__,prepare_worker_recovery_batch=worker_boundary)
        boundary16.start();self.addCleanup(boundary16.stop)
        # Real reader suites, the independent historical-bridge regression
        # and corrected unmocked684 build are recorded separately. These
        # legacy mutations exercise only the exact new dispatch boundaries.
        self.read1161_calls=[];self.install_precleanup_calls=[]
        class ClosedNewBoundary:
            def __init__(self,path,require_row,calls):
                self.rows={(r['case_id'],r['assertion_id']):r for r in ledger['assertions'] if r['evidence_path']==path}
                self.derived=json.loads((ROOT/path).read_bytes())
                self.require_row=require_row;self.calls=calls;self.seen=set();self.finalized=False
            def validate_claim(self,case,assertion,status,execution,root,json_pointer=None,ledger_row=None):
                key=(case,assertion);test.assertIn(key,self.rows);wanted=self.rows[key]
                test.assertEqual(status,'PASS');test.assertEqual(root,ROOT)
                test.assertEqual(json_pointer,wanted['json_pointer']);test.assertEqual(execution,self.derived)
                if self.require_row:test.assertEqual(ledger_row,wanted)
                test.assertNotIn(key,self.seen);self.seen.add(key);self.calls.append(key);return True
            def verify_unchanged(self):test.assertEqual(self.seen,set(self.rows));self.finalized=True;return True
            def require_finalized(self):test.assertTrue(self.finalized);return True
        def read1161_boundary(root):
            test.assertEqual(root,ROOT)
            return ClosedNewBoundary('context/reconciliation/local-f0-read13-0ff2a91-116153b2-qualified-evidence.json',True,self.read1161_calls)
        def precleanup_boundary(root):
            test.assertEqual(root,ROOT)
            return ClosedNewBoundary('context/reconciliation/local-f0-install-0ff2a91-6850ee4c-precleanup-qualified-evidence.json',False,self.install_precleanup_calls)
        new_dispatch=patch.dict(build.__globals__,prepare_read1161_batch=read1161_boundary,prepare_install_precleanup_batch=precleanup_boundary)
        new_dispatch.start();self.addCleanup(new_dispatch.stop)
        # The exact-three reader has independent domain/race checks and the
        # real full687 build. Isolate its dispatch during legacy mutations.
        restore_path='context/reconciliation/local-f0-restore-249e681-04731001-qualified-evidence.json'
        restore_derived=json.loads((ROOT/restore_path).read_bytes())
        restore_rows={(r['case_id'],r['assertion_id']):r for r in ledger['assertions'] if r['evidence_path']==restore_path}
        restore_caps={'control.real_backup':'PASS','control.restored_parity':'PASS','control.restored_authority':'PARTIAL'}
        self.assertEqual(len(restore_rows),3);self.assertEqual({key[0] for key in restore_rows},{'P0C-RESTORE-01'})
        self.assertEqual({key[1]:r['status'] for key,r in restore_rows.items()},restore_caps)
        self.restore047_calls=[]
        class ClosedRestoreBoundary:
            def __init__(self):self.seen=set();self.finalized=False
            def validate_claim(self,case,assertion,status,execution,root,json_pointer=None,ledger_row=None):
                key=(case,assertion);test.assertIn(key,restore_rows);wanted=restore_rows[key]
                test.assertEqual(status,restore_caps[assertion]);test.assertEqual(root,ROOT)
                test.assertEqual(json_pointer,wanted['json_pointer']);test.assertEqual(execution,restore_derived)
                test.assertEqual(ledger_row,wanted);test.assertNotIn(key,self.seen)
                self.seen.add(key);test.restore047_calls.append(key);return True
            def verify_unchanged(self):test.assertEqual(self.seen,set(restore_rows));self.finalized=True;return True
            def require_finalized(self):test.assertTrue(self.finalized);return True
        def restore_boundary(root):test.assertEqual(root,ROOT);return ClosedRestoreBoundary()
        restore_dispatch=patch.dict(build.__globals__,prepare_restore047_batch=restore_boundary)
        restore_dispatch.start();self.addCleanup(restore_dispatch.stop)
    def test_recorded_subset_does_not_promote_compound_cases(self):
        namespace=build.__globals__;restricted=namespace['validate_restricted_claim'];migration=namespace['validate_claim'];native=namespace['validate_native_prefix_claim']
        restricted_calls=[];migration_calls=[];native_calls=[]
        def restricted_dispatch(*args,**kwargs):
            restricted_calls.append((args[0],args[1],args[2],kwargs.get('json_pointer')))
            return restricted(*args,**kwargs)
        def migration_dispatch(*args,**kwargs):
            migration_calls.append(args[3]['actual_result'])
            return migration(*args,**kwargs)
        def native_dispatch(*args,**kwargs):
            native_calls.append((args[0],args[1],args[3]['actual_result']))
            return native(*args,**kwargs)
        with patch.dict(namespace,validate_restricted_claim=restricted_dispatch,validate_claim=migration_dispatch,validate_native_prefix_claim=native_dispatch):result=build()
        self.assertEqual(result['selected_cases'],94)
        self.assertEqual(result['assertion_status_counts'],{'PASS':654,'PARTIAL':33,'FAILED':0,'DEPENDENCY_BLOCKED':32,'NOT_RUN':308,'UNRESOLVED_SOURCE':7})
        self.assertEqual(result['case_status_counts'],{'PASS':8,'PARTIAL':80,'FAILED':0,'DEPENDENCY_BLOCKED':0,'NOT_RUN':6})
        self.assertEqual({c['id'] for c in result['cases'] if c['status']=='PASS'},{'P0C-UNIQUE-01','P0C-TABLE-DatabaseActionGrant-ALLOW','P0C-TABLE-ProfessionalProfile-ALLOW','P0C-TABLE-CandidateProfile-ALLOW','P0C-INSTALL-01','P0C-INSTALL-02','P0C-TABLE-OwnerMutationEvidence-ALLOW','P0C-TABLE-CustomerProfileLifecycleEvent-ALLOW'})
        self.assertEqual(len(restricted_calls),70)
        self.assertEqual(len(migration_calls),5)
        self.assertNotIn('PASS_LOCAL_RESTRICTED_CONTROL_PACKETS_ONLY',migration_calls)
        self.assertEqual(len(native_calls),132)
        self.assertEqual(len(self.owner_lease_calls),20)
        self.assertEqual(len(self.native_complete_calls),388)
        self.assertEqual(len(self.scoped_read_calls),6)
        self.assertEqual(len(self.install_calls),5)
        self.assertEqual(len(self.worker_recovery_calls),16)
        self.assertEqual(len(self.read1161_calls),13)
        self.assertEqual(len(self.install_precleanup_calls),1)
        self.assertEqual(len(self.restore047_calls),3)
        self.assertTrue(all(row[2]=='STOPPED_ATTEMPT_PRESERVED' for row in native_calls))
        self.assertNotIn('STOPPED_ATTEMPT_PRESERVED',migration_calls)
        catalog=next(c for c in result['cases'] if c['id']=='P0C-CATALOG-01')
        self.assertEqual(catalog['status'],'PARTIAL')
        self.assertEqual(next(a for a in catalog['assertions'] if a['id']=='vector.CATALOG-LEAVES.adversarial')['status'],'NOT_RUN')
        customer=next(c for c in result['cases'] if c['id']=='P0C-TABLE-CustomerProfile-ALLOW')
        self.assertEqual(next(a for a in customer['assertions'] if a['id']=='positive.wa_app_runtime.update')['status'],'NOT_RUN')
        self.assertFalse(any(c['status']=='PASS' and 'Privacy' in c['id'] for c in result['cases']))
    def test_changed_current_sql_does_not_reuse_stale_inventory(self):
        original=Path.read_bytes
        def changed(path):
            data=original(path)
            return data+b'\n-- source changed\n' if path.name=='foundation-application.review.sql' else data
        with patch.object(Path,'read_bytes',changed),self.assertRaisesRegex(AssertionError,'Inventory source changed'):build()
    def test_pointer_and_execution_identities_fail_closed(self):
        original=Path.read_text
        for field,value in [('json_pointer','/coordinator/no_such_observation'),('run_id','00000000-0000-0000-0000-000000000000'),('source_commit','0'*40),('source_tree','0'*40),('packet_sha256','0'*64),('expected_assertion_sha256','0'*64)]:
            with self.subTest(field=field):
                def changed(path,*args,**kwargs):
                    data=original(path,*args,**kwargs)
                    if path.name=='local-f0-assertion-evidence.json':
                        ledger=json.loads(data);ledger['assertions'][0][field]=value;return json.dumps(ledger)
                    return data
                with patch.object(Path,'read_text',changed),self.assertRaises(AssertionError):build()
    def test_small_pass_record_cannot_promote_unexercised_cas(self):
        original=Path.read_text
        inventory=json.loads(original(ROOT/'context/reconciliation/local-f0-assertions.json'))
        assertion=next(a for c in inventory['cases'] if c['id']=='P0C-CAS-01' for a in c['assertions'] if a['id']=='control.concurrent_customer_update')
        def changed(path,*args,**kwargs):
            text=original(path,*args,**kwargs)
            if path.name=='local-f0-assertion-evidence.json':
                value=json.loads(text);row=value['assertions'][0];row.update(case_id='P0C-CAS-01',assertion_id=assertion['id'],expected_assertion_sha256=hashlib.sha256(assertion['expected_assertion'].encode()).hexdigest());return json.dumps(value)
            return text
        with patch.object(Path,'read_text',changed),self.assertRaisesRegex(AssertionError,'Unsupported small-rehearsal assertion'):build()
    def test_catalog_reference_cannot_point_to_unrelated_existing_dictionary(self):
        original=Path.read_text
        def changed(path,*args,**kwargs):
            text=original(path,*args,**kwargs)
            if path.name=='local-f0-assertion-evidence.json':
                value=json.loads(text)
                next(r for r in value['assertions'] if r['case_id']=='P0C-CATALOG-01' and r['assertion_id']=='control.visibility')['json_pointer']='/sanitized_report/limits'
                return json.dumps(value)
            return text
        with patch.object(Path,'read_text',changed),self.assertRaisesRegex(AssertionError,'Catalog evidence pointer'):build()
    def test_restricted_reference_cannot_point_to_unrelated_existing_dictionary(self):
        original=Path.read_text
        def changed(path,*args,**kwargs):
            text=original(path,*args,**kwargs)
            if path.name=='local-f0-assertion-evidence.json':
                value=json.loads(text);next(r for r in value['assertions'] if r['case_id']=='P0C-TABLE-CustomerProfile-ALLOW' and r['assertion_id']=='positive.wa_app_runtime.select')['json_pointer']='/sanitized_report/limits';return json.dumps(value)
            return text
        with patch.object(Path,'read_text',changed),self.assertRaisesRegex(AssertionError,'RESTRICTED_PROOF_POINTER'):build()
    def test_restricted_partial_cannot_be_promoted(self):
        original=Path.read_text
        def changed(path,*args,**kwargs):
            text=original(path,*args,**kwargs)
            if path.name=='local-f0-assertion-evidence.json':
                value=json.loads(text);next(r for r in value['assertions'] if r['case_id']=='P0C-EVIDENCE-01' and r['assertion_id']=='control.closed_codec')['status']='PASS';return json.dumps(value)
            return text
        with patch.object(Path,'read_text',changed),self.assertRaisesRegex(AssertionError,'RESTRICTED_CLAIM_NOT_SUPPORTED'):build()
    def test_restricted_record_cannot_promote_unlisted_case(self):
        original=Path.read_text
        inventory=json.loads(original(ROOT/'context/reconciliation/local-f0-assertions.json'))
        assertion=next(a for c in inventory['cases'] if c['id']=='P0C-TABLE-ConsentLog-ALLOW' for a in c['assertions'] if a['id']=='positive.wa_app_runtime.insert')
        def changed(path,*args,**kwargs):
            text=original(path,*args,**kwargs)
            if path.name=='local-f0-assertion-evidence.json':
                value=json.loads(text);row=next(r for r in value['assertions'] if r['run_id']=='f161d454-13dd-453f-a9ee-6e92f95ea8d6');row.update(case_id='P0C-TABLE-ConsentLog-ALLOW',assertion_id=assertion['id'],status='PASS',expected_assertion_sha256=hashlib.sha256(assertion['expected_assertion'].encode()).hexdigest());return json.dumps(value)
            return text
        with patch.object(Path,'read_text',changed),self.assertRaisesRegex(AssertionError,'RESTRICTED_CLAIM_NOT_SUPPORTED'):build()
    def test_restricted_record_kind_cannot_fall_back_to_migration(self):
        records=build.__globals__['EVIDENCE_RECORDS'];path='context/reconciliation/local-f0-restricted-b8f6b10-f161d454-execution.json'
        changed={**records,path:(records[path][0],'PASS_GENUINE_FIRST_NOOP_FAILURE_REVIEWED_RESOLVE_SAME_CHECKSUM_RETRY')}
        with patch.dict(build.__globals__,EVIDENCE_RECORDS=changed),self.assertRaisesRegex(AssertionError,'Execution evidence kind changed'):build()
    def test_superseded_missing_phase_partial_cannot_be_rewritten_as_pass(self):
        original=Path.read_text
        def changed(path,*args,**kwargs):
            text=original(path,*args,**kwargs)
            if path.name=='local-f0-assertion-evidence.json':
                value=json.loads(text);next(r for r in value['assertions'] if r['case_id']=='P0C-INSTALL-02' and r['assertion_id']=='vector.FUNCTION-ACL-FAILURE-CLEANUP.adversarial')['previous_evidence']['status']='PASS';return json.dumps(value)
            return text
        with patch.object(Path,'read_text',changed),self.assertRaisesRegex(AssertionError,'HISTORICAL_INSTALL_EMBEDDED_HISTORY'):build()
    def test_unreviewed_evidence_path_is_not_read(self):
        original=Path.read_text
        def changed(path,*args,**kwargs):
            text=original(path,*args,**kwargs)
            if path.name=='local-f0-assertion-evidence.json':
                value=json.loads(text);value['assertions'][0]['evidence_path']='../SECRET_CANARY';return json.dumps(value)
            return text
        with patch.object(Path,'read_text',changed),self.assertRaisesRegex(AssertionError,'Unsupported execution evidence path'):build()
    def test_approved_small_pair_cannot_use_forged_empty_pass_record(self):
        original_text,original_bytes=Path.read_text,Path.read_bytes
        old=json.loads(original_text(ROOT/'context/reconciliation/local-f0-small-rehearsal-0623028-execution.json'))
        forged={key:old[key] for key in ('run_id','source_commit','source_tree','packet_sha256')}
        forged.update(actual_result='PASS_FIRST01_THROUGH_FIRST10_SUBSET_ONLY',empty_observation={})
        raw=json.dumps(forged).encode();digest=hashlib.sha256(raw).hexdigest()
        def changed_bytes(path):return raw if path.name=='local-f0-small-rehearsal-0623028-execution.json' else original_bytes(path)
        def changed_text(path,*args,**kwargs):
            text=original_text(path,*args,**kwargs)
            if path.name=='local-f0-small-rehearsal-0623028-execution.json':return raw.decode()
            if path.name=='local-f0-assertion-evidence.json':
                value=json.loads(text)
                for row in value['assertions']:
                    if row['source_commit']==old['source_commit']:row.update(evidence_sha256=digest,json_pointer='/empty_observation')
                return json.dumps(value)
            return text
        with patch.object(Path,'read_text',changed_text),patch.object(Path,'read_bytes',changed_bytes),self.assertRaisesRegex(AssertionError,'independently reviewed record'):build()
    def test_parses_exact_hashed_bytes_without_second_file_read(self):
        original=Path.read_text
        def second_read_trap(path,*args,**kwargs):
            if path.name in ('local-f0-small-rehearsal-0623028-execution.json','local-f0-migration-6b8910d-execution.json','local-f0-catalog-b9703d7-23bd8979-execution.json','local-f0-restricted-b8f6b10-f161d454-execution.json','local-f0-native-access-0a29cf6-495976eb-execution.json','local-f0-owner-da5ad66-72934689-qualified-evidence.json','local-f0-lease-da5ad66-a560e05b-qualified-evidence.json','local-f0-native-1110fa4-4c894dba-qualified-evidence.json'):raise RuntimeError('UNVERIFIED_SECOND_READ')
            return original(path,*args,**kwargs)
        with patch.object(Path,'read_text',second_read_trap):result=build()
        self.assertEqual(result['assertion_status_counts']['PASS'],654)

if __name__=='__main__':unittest.main(verbosity=2)
