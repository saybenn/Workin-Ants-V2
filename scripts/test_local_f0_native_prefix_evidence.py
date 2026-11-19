"""Exact completed-prefix evidence checks; no subprocess/database boundary."""
import copy
import importlib.util
import json
from pathlib import Path
import socket
import subprocess
import unittest
from unittest.mock import patch

ROOT=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('native_prefix',ROOT/'scripts/local_f0_native_prefix_evidence.py')
adapter=importlib.util.module_from_spec(spec);spec.loader.exec_module(adapter)

class NativePrefixEvidenceTests(unittest.TestCase):
    def setUp(self):
        for name in ('run','Popen','check_output','check_call','call'):
            guard=patch.object(subprocess,name,side_effect=AssertionError('NO_PROCESS'));guard.start();self.addCleanup(guard.stop)
        guard=patch.object(socket,'create_connection',side_effect=AssertionError('NO_NETWORK'));guard.start();self.addCleanup(guard.stop)
        self.record=json.loads((ROOT/adapter.RECORD).read_bytes())
        self.links=json.loads((ROOT/adapter.LINKS).read_bytes())['links']
        self.link=self.links[0]
        self.document=json.loads((ROOT/self.link['facet_asset_path']).read_bytes())
        self.parts=[adapter.pointer(self.document,self.link[key]) for key in ('facet_json_pointer','operation_json_pointer','native_control_json_pointer')]
    def claim(self,link=None,record=None,pointer='/actual_outcomes',status='PASS'):
        link=link or self.link
        return adapter.validate_claim(link['case_id'],link['assertion_id'],status,record or self.record,ROOT,json_pointer=pointer)
    def test_all132_exact_actual_completed_provider_denials_pass(self):
        self.assertEqual(len(self.links),132)
        for link in self.links:
            with self.subTest(case=link['case_id'],assertion=link['assertion_id']):self.assertTrue(self.claim(link))
    def test_failed_operation_and_issuer_umbrella_never_qualify(self):
        for assertion in ('denial.wa_context_issuer.select','denial.wa_context_issuer.source_business_write','denial.context.foreign_runtime_context'):
            with self.assertRaises(adapter.EvidenceFailure):self.claim({'case_id':'P0C-TABLE-AuditEvent-DENY','assertion_id':assertion})
    def test_later_unexecuted_provider_case_cannot_qualify(self):
        with self.assertRaises(adapter.EvidenceFailure):self.claim({'case_id':'P0C-TABLE-UserSecurityProfile-DENY','assertion_id':'denial.anon.select'})
    def test_pointer_substitution_and_nonpass_status_reject(self):
        for pointer in ('/sanitized_report/cleanup_summary','/actual_outcomes/absent','/facets/0',None):
            with self.assertRaises(adapter.EvidenceFailure):self.claim(pointer=pointer)
        for status in ('PARTIAL','FAILED',True,1):
            with self.assertRaises(adapter.EvidenceFailure):self.claim(status=status)
    def test_changed_exact_record_rejects_without_secret_retention(self):
        record=copy.deepcopy(self.record);record['password']='SECRET_CANARY_MUST_NOT_ESCAPE'
        with self.assertRaises(adapter.EvidenceFailure) as error:self.claim(record=record)
        self.assertNotIn('SECRET_CANARY',str(error.exception))
    def test_pinned_asset_drift_rejects_before_claim(self):
        target=(ROOT/self.link['facet_asset_path']).resolve();original=Path.read_bytes
        def changed(path):return b'{"password":"SECRET_CANARY"}' if path.resolve()==target else original(path)
        with patch.object(Path,'read_bytes',changed),self.assertRaises(adapter.EvidenceFailure) as error:self.claim()
        self.assertNotIn('SECRET_CANARY',str(error.exception))
    def test_facet_requires_intended_native_diagnostic_and_position(self):
        for key,value in [('sqlstate','P0001'),('observed_gate','TABLE'),('matched',1),('source_position_verified',False),('native_location','exec_stmt_raise@pl_exec.c')]:
            parts=copy.deepcopy(self.parts);parts[0]['diagnostic'][key]=value
            with self.assertRaises(adapter.EvidenceFailure):adapter.validate_facet(self.link,*parts)
    def test_operation_requires_exact_role_and_confirmed_prior_closure(self):
        for key,value in [('role','wa_context_issuer'),('closed_before_observers',False),('closed_before_observers',1),('exit_code',True),('acknowledgement',True),('source_sql_sha256','0'*64)]:
            parts=copy.deepcopy(self.parts);parts[1][key]=value
            with self.assertRaises(adapter.EvidenceFailure):adapter.validate_facet(self.link,*parts)
    def test_valid_target_and_restored_state_are_mandatory(self):
        for target,key,value in [('control','insert_one',False),('control','update_controls_one',True),('control','rollback_and_restoration_proven',False),('observers','all_205_native_facts_unchanged',False),('observers','all_100_trigger_functions_restored',1)]:
            parts=copy.deepcopy(self.parts)
            if target=='control':parts[2][key]=value
            else:parts[0]['post_probe_observers'][key]=value
            with self.assertRaises(adapter.EvidenceFailure):adapter.validate_facet(self.link,*parts)
    def test_source_missing_privilege_projection_is_mandatory(self):
        parts=copy.deepcopy(self.parts);parts[1]['source_native_privilege_projection']['schema_usage']=True
        with self.assertRaises(adapter.EvidenceFailure):adapter.validate_facet(self.link,*parts)

if __name__=='__main__':unittest.main(verbosity=2)
