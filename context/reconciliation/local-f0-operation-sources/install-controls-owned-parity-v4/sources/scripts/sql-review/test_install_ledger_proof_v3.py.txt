"""Synthetic environment-free ledger tests; no actual runtime qualification."""
from copy import deepcopy
import hashlib
import json
from pathlib import Path
import runpy
import socket
import subprocess
import unittest
from unittest.mock import patch

ROOT=Path(__file__).resolve().parents[2]
M=runpy.run_path(str(ROOT/'scripts/sql-review/install_ledger_proof_v3.py'))
P=runpy.run_path(str(ROOT/'scripts/install_control_protocol_v2.py'))
CANARY='UNEXPORTED_INSTALL_LEDGER_PRIVATE_ERROR_CANARY'

class Tests(unittest.TestCase):
    def setUp(self):
        for method in ('run','Popen','check_output','check_call','call'):
            guard=patch.object(subprocess,method,side_effect=AssertionError('NO_PROCESS'));guard.start();self.addCleanup(guard.stop)
        guard=patch.object(socket,'create_connection',side_effect=AssertionError('NO_NETWORK'));guard.start();self.addCleanup(guard.stop)
        self.blobs={p:(ROOT/p).read_bytes() for p in M['INPUTS']};self.hashes={p:M['sha'](b) for p,b in self.blobs.items()};self.identity={'run_id':'550e8400-e29b-41d4-a716-446655440000','container_id':'b'*64,'source_commit':'c'*40,'source_tree':'d'*40,'packet_sha256':'e'*64,'target_attestation_sha256':'f'*64};self.adapter=M['make_adapter'](self.blobs,self.hashes,P,self.identity)
    def failure(self,masked=True):
        identity={k:v for k,v in self.identity.items() if k!='target_attestation_sha256'};identity['source_sql_sha256']=M['FIXED'][M['FAULT']]
        primary='WA_F0_DIAG|22012|wa_migrator|wa_p0c_rehearsal|ERROR:  division by zero\n';base='WA_F0_DIAG|28P01|wa_worker|wa_p0c_rehearsal|FATAL:  password authentication failed for user "wa_worker"\n';after=base+primary+('WA_F0_DIAG|25P02|wa_migrator|wa_p0c_rehearsal|ERROR:  '+P['ABORTED']+'\n' if masked else '')
        before=P['summarize_server'](base,'');after=P['summarize_server'](after,'');cli={'run_id':self.identity['run_id'],'container_id':self.identity['container_id'],'schema':'workinants.local-f0-migrate-result.v2','operation':'deploy','source_sql_sha256':identity['source_sql_sha256'],'exit_code':1,'status':'CLI_OUTPUT_REJECTED_STOP_AND_INSPECT','prisma_codes':[],'sqlstates':[]};row={'name_sha256':M['text_hash'](M['MIGRATION']),'checksum_sha256':M['text_hash'](identity['source_sql_sha256']),'finished':False,'rolled_back':False,'steps':0,'logs_state':'NULL' if masked else 'NONEMPTY','immutable_sha256':'1'*64};inventory=dict.fromkeys(('relations','functions','types','enums','other_clients'),0);verdict=P['failure_verdict']('division_failure',cli,inventory,{'rows':[row],'ids_unique':True},before,after,identity['source_sql_sha256']);rollback={'schema':'workinants.install-rollback-observation.v1',**identity,'failure':verdict,'failed_ledger':row,'application_inventory':inventory,'original_grantor_finalized':True,'disposition':'PENDING_INDEPENDENT_REVIEW'};approval={'schema':'workinants.install-independent-rollback-review.v1','decision':'APPROVED_STANDARD_RESOLVE_ROLLED_BACK','run_id':identity['run_id'],'container_id':identity['container_id'],'source_sql_sha256':identity['source_sql_sha256'],'proof_sha256':M['sha']((P['canonical'](rollback)+'\n').encode()),'reviewer':'/root/restricted_controls_operator'}
        retained={'rows':[dict(row,rolled_back=True),{'name_sha256':M['text_hash'](M['MIGRATION']),'checksum_sha256':M['text_hash'](M['FIXED'][M['CANONICAL']]),'finished':True,'rolled_back':False,'steps':1,'logs_state':'NULL','immutable_sha256':'2'*64}],'ids_unique':True};recovered={'schema':'workinants.local-f0-migrate-result.v2','operation':'deploy','status':'CLI_COMPLETED_REQUIRES_INDEPENDENT_LEDGER_CATALOG_CHECKS','exit_code':0,'run_id':self.identity['run_id'],'container_id':self.identity['container_id'],'source_sql_sha256':M['FIXED'][M['CANONICAL']],'attestation_sha256':self.identity['target_attestation_sha256']}
        return {'format':'workinants.install-ledger-failure-proof.v1','identity':identity,'rollback':rollback,'approval':approval,'failed_cli':cli,'server_before':before,'server_after':after,'settings':dict.fromkeys(('prefix','terse','no_statements','no_error_statements','locale','passwords','version'),True),'retained_ledger':retained,'recovered_cli':recovered}
    def registration(self,recovered=False,proof=None):
        rows=[{'path':M['CANONICAL'],'migration_name':M['MIGRATION'],'sha256':M['FIXED'][M['CANONICAL']],'state':'applied','count':1}]
        if recovered:rows.append({'path':M['FAULT'],'migration_name':M['MIGRATION'],'sha256':M['FIXED'][M['FAULT']],'state':'rolled_back','count':1})
        return self.adapter.build_registration(rows,run_id=self.identity['run_id'],target_attestation_sha256=self.identity['target_attestation_sha256'],source_expected_sha256=M['EXPECTED'],install_failure_proof=proof)
    def evidence(self,registration):
        native={'synthetic_main_catalog_identity':'TEST_ONLY'};observation={**M['schema_expectation'](),'format':M['NATIVE_FORMAT'],'server_version_num':170011,'database':'wa_p0c_rehearsal','read_only':True,'isolation':'repeatable read','collected_as':'postgres','session_user':'postgres','collector_is_superuser':True,'history_ids_unique':True,'history':deepcopy(registration['history_expected'])};evidence={'format':M['EVIDENCE_FORMAT'],'registration_sha256':M['digest'](registration),'collector_sql_sha256':M['FIXED'][M['COLLECTOR']],'run_id':self.identity['run_id'],'target_attestation_sha256':self.identity['target_attestation_sha256'],'native_catalog_before_sha256':M['digest'](native),'native_catalog_after_sha256':M['digest'](native),'observation':observation};return evidence,native
    def result(self,r,e,n):return self.adapter.compare_proof(r,e,n,bootstrap_grantor='postgres',source_expected_sha256=M['EXPECTED'])
    def test_schema_ast_matches_original_immutable_source_and_canonical_metadata(self):
        old=runpy.run_path(str(ROOT/M['OLD']));self.assertEqual(M['canonical'](M['schema_expectation']()),old['canonical'](old['schema_expectation']()));r=self.registration();e,n=self.evidence(r);self.assertEqual(self.result(r,e,n)['status'],'PASS')
    def test_retained_22012_masked_null_path_has_two_exact_rows_and_independent_review(self):
        r=self.registration(True,self.failure());e,n=self.evidence(r);self.assertEqual(len(e['observation']['history']),2);self.assertEqual(self.result(r,e,n)['status'],'PASS');self.assertFalse(r['install_failure_proof']['rollback']['failure']['P3018_claimed'])
    def test_retained_nonempty_engine_persistence_is_separate_predeclared_branch(self):
        r=self.registration(True,self.failure(False));e,n=self.evidence(r);self.assertEqual(self.result(r,e,n)['status'],'PASS');self.assertIn('NONEMPTY',[row['logs_state'] for row in r['history_expected']])
    def test_failed_row_cannot_be_dropped_or_rewritten_or_duplicated(self):
        r=self.registration(True,self.failure());e,n=self.evidence(r)
        for history in (e['observation']['history'][:1],e['observation']['history']*2,[dict(row,steps=1) for row in e['observation']['history']]):
            bad=deepcopy(e);bad['observation']['history']=history;self.assertEqual(self.result(r,bad,n)['status'],'FAIL')
    def test_retained_failed_immutable_identity_and_recovered_actual_cli_are_required(self):
        proof=self.failure();proof['retained_ledger']['rows'][0]['immutable_sha256']='0'*64
        with self.assertRaises(Exception):self.registration(True,proof)
        proof=self.failure();proof['recovered_cli']['container_id']='0'*64
        with self.assertRaises(Exception):self.registration(True,proof)
    def test_proof_cannot_move_to_a_different_actual_outer_target_or_source(self):
        for field in ('container_id','source_commit','source_tree','packet_sha256'):
            proof=self.failure();proof['identity'][field]='0'*len(proof['identity'][field])
            with self.subTest(field=field),self.assertRaises(Exception):self.registration(True,proof)
    def test_independent_review_hash_and_reviewer_are_mandatory(self):
        for field in ('proof_sha256','reviewer','decision'):
            proof=self.failure();proof['approval'][field]=CANARY
            with self.subTest(field=field),self.assertRaises(Exception):self.registration(True,proof)
    def test_primary_and_secondary_error_chain_is_rebuilt_not_asserted(self):
        for field in ('division_22012','secondary_25p02','other_migrator_error'):
            proof=self.failure();proof['server_after']['counts'][field]+=1
            with self.subTest(field=field),self.assertRaises(Exception):self.registration(True,proof)
    def test_permission_failure_cannot_stand_in_for_division(self):
        proof=self.failure();proof['server_after']['counts']['division_22012']=0;proof['server_after']['counts']['function_42501']=1
        with self.assertRaises(Exception):self.registration(True,proof)
    def test_complete_schema_acl_and_every_typed_metadata_flag_are_compared(self):
        r=self.registration();e,n=self.evidence(r)
        for key,value in [('read_only',1),('history_ids_unique',1),('server_version_num',170012),('column_acl',[CANARY]),('table_acl',[]),('columns',[])]:
            bad=deepcopy(e);bad['observation'][key]=value;result=self.result(r,bad,n);self.assertEqual(result['status'],'FAIL');self.assertNotIn(CANARY,json.dumps(result))
    def test_read_only_collector_catalog_envelope_cannot_drift(self):
        r=self.registration();e,n=self.evidence(r)
        for key in ('collector_sql_sha256','run_id','target_attestation_sha256','native_catalog_before_sha256','native_catalog_after_sha256'):
            bad=deepcopy(e);bad[key]=CANARY;result=self.result(r,bad,n);self.assertEqual(result['status'],'FAIL');self.assertNotIn(CANARY,json.dumps(result))
    def test_fixed_source_body_or_tool_metadata_drift_refuses_before_comparison(self):
        for path in (M['OLD'],M['COLLECTOR'],M['PROTOCOL'],M['ENGINE_PACKAGE']):
            blobs=dict(self.blobs);blobs[path]=CANARY.encode();hashes={p:M['sha'](b) for p,b in blobs.items()}
            with self.subTest(path=path),self.assertRaises(Exception):M['make_adapter'](blobs,hashes,P,self.identity)
    def test_parser_module_performs_no_io_or_process_calls_after_binding(self):
        with patch.object(Path,'read_bytes',side_effect=AssertionError('PURE_NO_READ')),patch.object(Path,'open',side_effect=AssertionError('PURE_NO_OPEN')):
            r=self.registration(True,self.failure());e,n=self.evidence(r);self.assertEqual(self.result(r,e,n)['status'],'PASS')

    def test_old_v2_namespace_is_not_a_v3_source_fallback(self):
        for current,old in ((M['SELF'],'scripts/sql-review/install_ledger_proof_v2.py'),(M['FAULT'],M['FAULT'].replace('rehearsal-v3/','rehearsal-v2/'))):
            blobs=dict(self.blobs);hashes=dict(self.hashes);blobs[old]=blobs.pop(current);hashes[old]=hashes.pop(current)
            with self.subTest(current=current),self.assertRaises(M['LedgerProofError']):M['make_adapter'](blobs,hashes,P,self.identity)

    def test_failed_cli_binding_and_returned_hash_maps_cannot_be_rebound(self):
        for key in ('run_id','container_id','source_sql_sha256'):
            proof=self.failure();proof['failed_cli'][key]=CANARY
            with self.subTest(key=key),self.assertRaises(Exception):self.registration(True,proof)
        first=self.registration();original=deepcopy(first['tool_source_files_sha256']);first['tool_source_files_sha256'][M['SELF']]=CANARY;self.hashes[M['SELF']]=CANARY
        second=self.registration();self.assertEqual(second['tool_source_files_sha256'],original)

if __name__=='__main__':unittest.main(verbosity=2)
