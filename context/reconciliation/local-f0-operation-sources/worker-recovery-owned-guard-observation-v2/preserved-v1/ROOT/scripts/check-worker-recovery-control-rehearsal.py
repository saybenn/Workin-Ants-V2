"""Environment-free source admission, exact21 scope, SQL parse/reproduction."""
import ast
import importlib.util
import json
from pathlib import Path
import socket
import subprocess
import sys
import unittest
from unittest.mock import patch

ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'scripts'))
import worker_recovery_control_protocol as P
spec=importlib.util.spec_from_file_location('worker_recovery_prepare',ROOT/'scripts/prepare-worker-recovery-control-rehearsal.py');G=importlib.util.module_from_spec(spec);spec.loader.exec_module(G)

class SourceTests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):cls.files,cls.packet=G.build()
 def setUp(self):
  for name in ('run','Popen','call','check_call','check_output'):
   p=patch.object(subprocess,name,side_effect=AssertionError('NO_PROCESS'));p.start();self.addCleanup(p.stop)
  p=patch.object(socket,'create_connection',side_effect=AssertionError('NO_NETWORK'));p.start();self.addCleanup(p.stop)
 def test_exact21_and13_PASS4_PARTIAL_ceilings_NOT_RUN(self):
  self.assertEqual(tuple(c['name'] for c in self.packet['cases']),P.CASE_NAMES);self.assertEqual(len(P.CASE_NAMES),21)
  self.assertEqual(len(self.packet['assertion_ceilings']),17);self.assertEqual(sum(r['maximum_after_actual_evidence_and_review']=='PASS' for r in self.packet['assertion_ceilings']),13)
  self.assertTrue(all(c['status']=='NOT_RUN' for c in self.packet['cases']+self.packet['assertion_ceilings']));self.assertFalse(self.packet['finite_caps']['worker_loop'])
 def test_pinned_parser_all_SQL(self):
  import pglast
  self.assertEqual(pglast.__version__,'v7.21')
  for name,text in self.files.items():
   if name.endswith('.sql'):
    with self.subTest(file=name):self.assertTrue(pglast.parse_sql(text))
 def test_byte_reproduction_and_exact_artifact_set(self):
  files,packet=G.build();self.assertEqual(files,self.files);self.assertEqual(packet,self.packet);self.assertEqual(set(files),{p.name for p in G.OUT.iterdir()})
  for name,text in files.items():self.assertEqual((G.OUT/name).read_bytes(),text.encode())
 def test_distinct_ABC_roots_shared_catalog_identity_only(self):
  for key in ('work','command','effect','attempt','inbox','subscription','selection','grant','enrollment'):self.assertEqual(len({self.packet['roots'][label]['ids'][key] for label in 'ABC'}),3)
  for key in ('plan','definition','benefit','identity-bootstrap'):self.assertEqual(len({self.packet['roots'][label]['ids'][key] for label in 'ABC'}),1)
 def test_fixture_bypass_exact_five_flush_before_restore_no_business_seeds(self):
  body=self.files['independent-fixtures.sql'];self.assertEqual(body.count('INSERT INTO '),9);self.assertEqual(body.count('DISABLE TRIGGER owner_commit;'),5);self.assertEqual(body.count('ENABLE TRIGGER owner_commit;'),5)
  self.assertLess(body.rfind('INSERT INTO '),body.index('SET CONSTRAINTS ALL IMMEDIATE;'));self.assertLess(body.index('SET CONSTRAINTS ALL IMMEDIATE;'),body.index('ENABLE TRIGGER'))
  for forbidden in ('INSERT INTO platform.runtime_','INSERT INTO app.customer_profiles','DISABLE TRIGGER physical_guard','DISABLE ROW LEVEL','CREATE FUNCTION'):self.assertNotIn(forbidden,body)
 def test_first_actual_group_pending_then_committed_exact_existing_codec_and_leased(self):
  body=self.files[P.CASE_NAMES[0]+'.sql'];self.assertIn("'pending',0,'"+P.RESULT_SCHEMA+"','1',NULL,NULL",body);self.assertIn("UPDATE platform.runtime_command_receipt SET state='committed'",body)
  self.assertIn("result_body=",body);self.assertIn('::jsonb::text',body);self.assertIn('missing_exact_inbox_rejects',body);self.assertIn('exact_inbox_matches_before_link',body);self.assertIn("'still_leased'",body)
  self.assertNotIn("SET state='completed'",body);self.assertIn('SET CONSTRAINTS ALL IMMEDIATE;',body)
 def test_claim_predecessor_caps_and_current_processing_effect_fence_distinct(self):
  roots=self.packet['roots'];work=roots['A']['ids']['work'];effect=roots['A']['ids']['effect'];claim=self.packet['grants']['A-reclaim'];processing=self.packet['grants']['A-process2']
  self.assertEqual(claim['source_generation'],'1');self.assertIn('RuntimeWorkItem/'+work+'/revision/1',claim['allowed_fields']);self.assertNotIn('RuntimeWorkItem/'+work+'/revision/2',claim['allowed_fields'])
  self.assertEqual(processing['source_generation'],'2');self.assertIn('RuntimeWorkItem/'+work+'/revision/2',processing['allowed_fields']);self.assertIn('RuntimeEffectReceipt/'+effect+'/revision/1',processing['allowed_fields'])
  stale=self.packet['grants']['A-processing-old-generation'];self.assertEqual(stale['source_generation'],'1');self.assertIn('RuntimeWorkItem/'+work+'/revision/2',stale['allowed_fields'])
 def test_audit_attempt_count_exactly_three_and_second_attempt2(self):
  self.assertEqual(self.packet['final_expected_counts']['platform.runtime_attempt'],3);body=self.files[P.CASE_NAMES[15]+'.sql'];self.assertIn("'"+self.packet['attempt2']+"'",body);self.assertIn(',2,2,',body)
 def test_all42_and_frozen_worker32_source5ae(self):
  self.assertEqual(len(self.packet['final_expected_counts']),42);self.assertEqual(len(self.packet['worker_acl_rows']),32);self.assertEqual(self.packet['source_files_sha256']['review-output/foundation-application.review.sql'],P.APPLICATION_SHA)
  self.assertEqual(self.packet['final_expected_counts']['app.track_subscriptions'],2);self.assertEqual(self.packet['final_expected_counts']['platform.runtime_effect_receipt'],2)
 def test_case20_reaches_terminal_trigger_in_same_transaction_then_errors(self):
  body=self.files[P.CASE_NAMES[19]+'.sql'];self.assertLess(body.index("SET state='completed'"),body.index('WA_WR_TEMPORARILY_COMPLETED'));self.assertLess(body.index('WA_WR_TEMPORARILY_COMPLETED'),body.index('SET attempt_count=attempt_count+1'))
 def test_NO_paid_reservation_followup_or_new_role_or_result_alias(self):
  for body in [v for k,v in self.files.items() if k.endswith('.sql')]:
   for bad in ('CREATE ROLE','ALTER ROLE','INSERT INTO platform.runtime_reservation','DISABLE TRIGGER ALL','provider=\'stripe\''):self.assertNotIn(bad,body)
 def test_source_digest_current_bytes_and_helper_graph(self):
  self.assertEqual(self.packet['source_only_packet_sha256'],P.digest({k:self.packet[k] for k in ('source_files_sha256','prepared_files_sha256')}))
  for name,wanted in self.packet['source_files_sha256'].items():self.assertEqual(P.sha((ROOT/name).read_bytes()),wanted)
  self.assertTrue(set(G.HELPERS)<=set(self.packet['source_files_sha256']))
 def test_all_remapped_grants_closed_sorted_and_native_field_tokens(self):
  for grant in self.packet['grants'].values():
   fields=grant['allowed_fields'];self.assertEqual(fields,sorted(set(fields)));self.assertLessEqual(len(fields),1024);self.assertFalse(any('*' in f for f in fields));self.assertIn(grant['database_login_role'],('wa_app_runtime','wa_worker'))
 def test_new_python_sources_parse_without_importing_or_processes(self):
  for name in G.NEW:ast.parse((ROOT/name).read_bytes(),filename=name)

if __name__=='__main__':unittest.main(verbosity=2)
