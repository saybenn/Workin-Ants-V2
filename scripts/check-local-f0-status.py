"""Offline evidence-binding mutations. Never invokes a process or database."""
import json
from pathlib import Path
import runpy
import unittest
from unittest.mock import patch
ROOT=Path(__file__).resolve().parents[1]
build=runpy.run_path(str(ROOT/'scripts/prepare-local-f0-status.py'))['build']

class StatusTests(unittest.TestCase):
    def test_recorded_subset_does_not_promote_compound_cases(self):
        result=build();self.assertEqual(result['selected_cases'],94)
        self.assertEqual(result['assertion_status_counts']['PASS'],15)
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

if __name__=='__main__':unittest.main(verbosity=2)
