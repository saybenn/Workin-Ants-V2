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
        self.assertEqual(result['assertion_status_counts'],{'PASS':615,'PARTIAL':32,'FAILED':0,'DEPENDENCY_BLOCKED':32,'NOT_RUN':348,'UNRESOLVED_SOURCE':7})
        self.assertEqual({c['id'] for c in result['cases'] if c['status']=='PASS'},{'P0C-UNIQUE-01','P0C-TABLE-DatabaseActionGrant-ALLOW','P0C-TABLE-ProfessionalProfile-ALLOW','P0C-TABLE-CandidateProfile-ALLOW'})
        self.assertEqual(len(restricted_calls),70)
        self.assertEqual(len(migration_calls),7)
        self.assertNotIn('PASS_LOCAL_RESTRICTED_CONTROL_PACKETS_ONLY',migration_calls)
        self.assertEqual(len(native_calls),132)
        self.assertEqual(len(self.owner_lease_calls),21)
        self.assertEqual(len(self.native_complete_calls),388)
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
    def test_partial_migration_claim_cannot_be_promoted(self):
        original=Path.read_text
        def changed(path,*args,**kwargs):
            text=original(path,*args,**kwargs)
            if path.name=='local-f0-assertion-evidence.json':
                value=json.loads(text);next(r for r in value['assertions'] if r['assertion_id']=='control.intended_failure')['status']='PASS';return json.dumps(value)
            return text
        with patch.object(Path,'read_text',changed),self.assertRaisesRegex(AssertionError,'MIGRATION_CLAIM_NOT_SUPPORTED'):build()
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
        self.assertEqual(result['assertion_status_counts']['PASS'],615)

if __name__=='__main__':unittest.main(verbosity=2)
