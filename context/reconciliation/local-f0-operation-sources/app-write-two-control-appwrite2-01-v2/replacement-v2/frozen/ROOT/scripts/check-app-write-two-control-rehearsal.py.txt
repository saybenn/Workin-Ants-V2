"""Environment-free source, schema, parsing and byte-reproduction checks."""
import ast
from copy import deepcopy
import importlib.util
import json
from pathlib import Path
import runpy
import socket
import subprocess
import sys
import unittest
from unittest.mock import patch
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'scripts'))
import app_write_two_control_protocol as P
spec=importlib.util.spec_from_file_location('app_write_two_prepare',ROOT/'scripts/prepare-app-write-two-control-rehearsal.py');G=importlib.util.module_from_spec(spec);spec.loader.exec_module(G)

class SourceTests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):cls.files,cls.packet=G.build()
 def setUp(self):
  for name in ('run','Popen','call','check_call','check_output'):
   mock=patch.object(subprocess,name,side_effect=AssertionError('PROCESS_FORBIDDEN'));mock.start();self.addCleanup(mock.stop)
  mock=patch.object(socket,'create_connection',side_effect=AssertionError('NETWORK_FORBIDDEN'));mock.start();self.addCleanup(mock.stop)
 def test_exact_two_claims_14_finite_protocols_all_NOT_RUN(self):
  self.assertEqual(tuple(c['name'] for c in self.packet['cases']),P.CASE_NAMES);self.assertEqual(len(P.CASE_NAMES),14);self.assertEqual(self.packet['finite_caps']['grant_instances_max'],15)
  self.assertEqual(tuple(c['case_id']+'|'+c['assertion_id'] for c in self.packet['claim_ceilings']),P.CLAIMS)
  self.assertTrue(all(c['status']=='NOT_RUN' for c in self.packet['cases']+self.packet['claim_ceilings']));self.assertFalse(self.packet['sql_executed']);self.assertFalse(self.packet['database_contacted']);self.assertEqual(self.packet['database_posture'],'D')
 def test_parse_every_SQL_with_exact_offline_parser(self):
  import pglast
  self.assertEqual(pglast.__version__,'v7.21')
  for name,sql in self.files.items():
   if name.endswith('.sql'):
    with self.subTest(file=name):self.assertTrue(pglast.parse_sql(sql))
 def test_exact_bytes_reproduced_and_closed_artifact_set(self):
  files,packet=G.build();self.assertEqual(files,self.files);self.assertEqual(packet,self.packet);self.assertEqual(set(files),{p.name for p in G.OUT.iterdir()})
  for name,raw in files.items():self.assertEqual((G.OUT/name).read_bytes(),raw.encode())
 def test_only_two_user_prerequisite_bypasses_flush_before_restore(self):
  sql=self.files['independent-user-fixtures.sql'];self.assertEqual(sql.count('INSERT INTO '),4);self.assertEqual(sql.count('DISABLE TRIGGER owner_commit;'),2);self.assertEqual(sql.count('ENABLE TRIGGER owner_commit;'),2)
  self.assertLess(sql.rfind('INSERT INTO '),sql.index('SET CONSTRAINTS ALL IMMEDIATE;'));self.assertLess(sql.index('SET CONSTRAINTS ALL IMMEDIATE;'),sql.index('ENABLE TRIGGER'))
  for text in ('DISABLE TRIGGER physical_guard','DISABLE ROW LEVEL','INSERT INTO platform.','INSERT INTO app.customer_profiles','CREATE FUNCTION'):self.assertNotIn(text,sql)
 def test_genuine_sh004_recipe_six_rows_and_server_storage_codec(self):
  sql=self.files['genuine-sh004-effect-insert.sql'];self.assertEqual(sql.count('INSERT INTO '),7);self.assertIn("'SH-004.v1#/$defs/response'",sql);self.assertIn('::jsonb::text',sql);self.assertIn('SET CONSTRAINTS ALL IMMEDIATE;',sql)
  source=self.packet['source_customer'];receipt=source['fixture_values']['response']['value']['receipt'];self.assertEqual(receipt['fingerprint'],P.sha(('synthetic-intent:'+source['semantic_key']).encode()));self.assertEqual(source['fixture_values']['response']['requestId'],'app-write-two-genuine-sh004')
 def test_effect_uses_actual_stored_command_result_never_arbitrary_digest(self):
  sql=self.files['genuine-sh004-effect-insert.sql'];self.assertIn("result_schema_id,result_digest,clock_timestamp() FROM platform.runtime_command_receipt",sql);self.assertIn("state='committed' AND result_schema_id='SH-004.v1#/$defs/response'",sql)
  observe=self.files['effect-coherence-observe.sql'];self.assertIn('e.result_hash=q.result_digest',observe);self.assertIn('e.mutation_transaction_id=q.mutation_transaction_id',observe);self.assertIn('q.result_body::text',observe)
 def test_pending_work_only_mutates_next_attempt_with_actual_future_and_count(self):
  from pglast import ast as pg,parse_sql
  sql=self.files['pending-work-next-attempt-update.sql'];node=next(x.stmt.withClause.ctes[0].ctequery for x in parse_sql(sql) if isinstance(x.stmt,pg.SelectStmt) and x.stmt.withClause)
  self.assertEqual([t.name for t in node.targetList],['next_attempt_at']);self.assertIn("interval '120 seconds'",sql);self.assertIn("next_attempt_at IS NULL",sql);self.assertIn("'changed',count(*)",sql);self.assertIn("lease_token_hash IS NULL",sql);self.assertIn("effect_receipt_id IS NULL",sql)
 def test_capabilities_are_exact_app_acl_with_control_mutations(self):
  grants=self.packet['grants'];self.assertEqual(grants['update']['service_principal'],None);self.assertEqual(grants['update']['principal_user_id'],self.packet['ids']['user'])
  for g in grants.values():self.assertEqual(g['allowed_fields'],sorted(set(g['allowed_fields'])));self.assertTrue(all('*' not in f for f in g['allowed_fields']));self.assertEqual(g['database_login_role'],'wa_app_runtime')
  root=self.packet['ids']['work'];self.assertIn('RuntimeWorkItem/'+root+'/UPDATE/nextAttemptAt',grants['update']['allowed_fields']);self.assertNotIn('RuntimeWorkItem/'+root+'/UPDATE/nextAttemptAt',grants['work-missing-update-field']['allowed_fields'])
 def test_paired_existing_customer_read_differs_only_in_root_revision_token(self):
  first,second=(self.packet['cases'][i] for i in (6,7));self.assertEqual(first['name'],'customer-existing-complete-revision-read');self.assertEqual(second['name'],'customer-existing-missing-revision-read');self.assertEqual(self.packet['cases'][5]['name'],'genuine-sh004-effect-insert')
  a,b=(self.packet['grants'][c['grant']] for c in (first,second));self.assertEqual({k:v for k,v in a.items() if k not in ('allowed_fields','template_id')},{k:v for k,v in b.items() if k not in ('allowed_fields','template_id')});root=self.packet['ids']['CustomerProfile'];self.assertEqual(set(a['allowed_fields'])-set(b['allowed_fields']),{'CustomerProfile/'+root+'/revision/0'});self.assertFalse(set(b['allowed_fields'])-set(a['allowed_fields']));self.assertEqual(len(a['allowed_fields']),15);self.assertEqual(len(b['allowed_fields']),14)
  for row in (first,second):self.assertEqual(row['kind'],'read-support');self.assertIsNone(row['claim']);self.assertIsNone(row['diagnostic']);self.assertEqual(row['allowed_changed_tables'],[]);self.assertFalse(row['positive'])
  self.assertEqual(self.files[first['sql']].splitlines()[1:-2],self.files[second['sql']].splitlines()[1:-2]);self.assertEqual(first['expected_records'][1],{'existing_customer':1});self.assertEqual(second['expected_records'][1],{'existing_customer':0});self.assertNotIn('effect-missing-root-revision.sql',self.files);self.assertNotIn('effect-missing-root-revision',P.CASE_NAMES)
 def test_canonical_and_worker32_unchanged_and_all_source_bytes_pinned(self):
  self.assertEqual(self.packet['source_files_sha256']['review-output/foundation-application.review.sql'],P.APPLICATION_SHA);self.assertEqual(len(self.packet['worker_acl_rows']),32)
  for name,wanted in self.packet['source_files_sha256'].items():self.assertEqual(P.sha((ROOT/name).read_bytes()),wanted)
 def test_complete42_counts_no_Track_inbox_attempt_or_identity_success_seeds(self):
  for key in ('setup_expected_counts','committed_expected_counts','scheduled_expected_counts'):
   counts=self.packet[key];self.assertEqual(len(counts),42);self.assertTrue(all(type(n) is int and n>=0 for n in counts.values()))
   for table in ('app.track_enrollment_receipt','app.track_subscriptions','platform.runtime_inbox_receipt','platform.runtime_attempt','platform_private.identity_service_authorization'):self.assertEqual(counts[table],0)
  self.assertEqual(self.packet['scheduled_expected_counts']['platform.runtime_work_item'],1)
 def test_no_nonexistent_result_guard_or_other28_write_claims(self):
  self.assertEqual(sum(c['claim'] is not None for c in self.packet['cases']),2);self.assertIn('App Effect has no canonical result-link guard',' '.join(self.packet['scope_limits']))
  self.assertTrue(all(c['diagnostic'] is None or 'result' not in c['diagnostic']['message'] for c in self.packet['cases']))
 def test_restoration_allows_only_two_owner_enableflags(self):
  baseline={'triggers':[{'table_name':t,'name':'owner_commit','enabled':'O','internal':False,'definition':'exact','function':'fixed'} for t in P.FIXTURE_TABLES],'function_body':'original'};actual=deepcopy(baseline);actual['triggers'][0]['enabled']='D';self.assertEqual(P.restoration_identity(baseline,actual)['disabled_owner_triggers'],1)
  for change in ('function','foreign','A','R'):
   bad=deepcopy(actual)
   if change=='function':bad['function_body']='changed'
   elif change=='foreign':bad['triggers'].append({'table_name':'app.foreign','name':'owner_commit','enabled':'D'})
   else:bad['triggers'][0]['enabled']=change
   with self.assertRaises(P.HeldFailure):P.restoration_identity(baseline,bad)
 def test_import_and_help_are_dormant(self):
  import io
  from contextlib import redirect_stdout
  module=runpy.run_path(str(ROOT/G.NEW[2]));
  with redirect_stdout(io.StringIO()),self.assertRaises(SystemExit) as result:module['main'](['--help'])
  self.assertEqual(result.exception.code,0)
  with redirect_stdout(io.StringIO()):self.assertEqual(module['main']([]),1)
if __name__=='__main__':unittest.main(verbosity=2)
