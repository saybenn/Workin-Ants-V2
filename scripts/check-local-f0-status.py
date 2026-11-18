"""Offline evidence-binding mutations. Never invokes a process or database."""
import hashlib,json
from pathlib import Path
import runpy
import unittest
from unittest.mock import patch
ROOT=Path(__file__).resolve().parents[1]
build=runpy.run_path(str(ROOT/'scripts/prepare-local-f0-status.py'))['build']

class StatusTests(unittest.TestCase):
    def test_recorded_subset_does_not_promote_compound_cases(self):
        result=build();self.assertEqual(result['selected_cases'],94)
        self.assertEqual(result['assertion_status_counts']['PASS'],20)
        self.assertEqual(result['assertion_status_counts']['PARTIAL'],3)
        self.assertEqual(result['case_status_counts']['PASS'],0)
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
    def test_partial_migration_claim_cannot_be_promoted(self):
        original=Path.read_text
        def changed(path,*args,**kwargs):
            text=original(path,*args,**kwargs)
            if path.name=='local-f0-assertion-evidence.json':
                value=json.loads(text);next(r for r in value['assertions'] if r['assertion_id']=='control.private_ledger')['status']='PASS';return json.dumps(value)
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
            if path.name in ('local-f0-small-rehearsal-0623028-execution.json','local-f0-migration-6b8910d-execution.json'):raise RuntimeError('UNVERIFIED_SECOND_READ')
            return original(path,*args,**kwargs)
        with patch.object(Path,'read_text',second_read_trap):result=build()
        self.assertEqual(result['assertion_status_counts']['PASS'],20)

if __name__=='__main__':unittest.main(verbosity=2)
