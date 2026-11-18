"""Environment-free selected owner-read source, parser and reproduction checks."""
from copy import deepcopy
import hashlib
import importlib.util
import json
from pathlib import Path
import re
import subprocess
import socket
import unittest
from unittest.mock import patch
from pglast import parse_sql
import owner_read_control_protocol as P

ROOT=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('_owner_read_prepare',ROOT/'scripts/prepare-owner-read-control-rehearsal.py')
G=importlib.util.module_from_spec(spec);spec.loader.exec_module(G)

class SourceTests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):cls.files,cls.packet=G.build()
 def setUp(self):
  for name in ('run','Popen','call','check_call','check_output'):
   guard=patch.object(subprocess,name,side_effect=AssertionError('PROCESS_FORBIDDEN'));guard.start();self.addCleanup(guard.stop)
  guard=patch.object(socket,'create_connection',side_effect=AssertionError('NETWORK_FORBIDDEN'));guard.start();self.addCleanup(guard.stop)
 def test_canonical_source_and_32_worker_rows(self):
  self.assertEqual(self.packet['source_files_sha256'][G.APPLICATION],P.APPLICATION_SHA);self.assertEqual(len(self.packet['worker_acl_ceiling_rows']),32)
  self.assertTrue(all(c['status']=='NOT_RUN' for c in self.packet['cases']));self.assertFalse(self.packet['database_contacted']);self.assertFalse(self.packet['sql_executed'])
 def test_finite_unique_case_order_and_no_global_scope(self):
  names=[c['name'] for c in self.packet['cases']];self.assertEqual(len(names),len(set(names)));self.assertEqual(len(names),self.packet['finite_caps']['case_count'])
  worker=[c['actual_login']=='wa_worker' for c in self.packet['cases']];self.assertEqual(worker,sorted(worker))
  self.assertEqual({self.packet['grants'][n]['target_kind'] for n in ('professional-query','candidate-query','user-actor')},{'ProfessionalProfile','CandidateProfile','User'})
 def test_every_emitted_sql_parses_without_database(self):
  self.assertGreater(len([n for n in self.files if n.endswith('.sql')]),90)
  for name,text in self.files.items():
   if name.endswith('.sql'):
    with self.subTest(name=name):self.assertGreater(len(parse_sql(text)),0)
 def test_byte_reproduction_and_digest_recipe(self):
  files,packet=G.build();self.assertEqual(files,self.files)
  self.assertEqual(P.digest({k:packet[k] for k in ('source_files_sha256','prepared_files_sha256')}),packet['source_only_packet_sha256'])
  if G.OUT.exists():
   self.assertEqual({p.name for p in G.OUT.iterdir()},set(files))
   for name,value in files.items():self.assertEqual((G.OUT/name).read_bytes(),value.encode())
 def test_all_caps_are_finite_and_canonical(self):
  for name,grant in self.packet['grants'].items():
   with self.subTest(name=name):
    fields=grant['allowed_fields'];self.assertEqual(fields,sorted(set(fields)));self.assertLessEqual(len(fields),1024);self.assertFalse(any('*' in f for f in fields));self.assertTrue(fields)
 def test_existing_rows_and_root_negatives_are_not_empty_source(self):
  for model,ids in self.packet['ids'].items():self.assertEqual(len(ids),2);self.assertNotEqual(ids[0],ids[1])
  cases={c['name']:c for c in self.packet['cases']}
  for name,model,_,_ in P.SCOPE_SPECS:
   self.assertEqual(cases[name]['expected']['root'],1);self.assertEqual(cases[name+'-wrong-root']['expected']['root'],0);self.assertEqual(cases[name+'-wrong-root']['expected']['foreign'],1)
 def test_only_real_owner_triggers_bypassed_no_function_or_physical_override(self):
  app=(ROOT/G.APPLICATION).read_text();seed=self.files['existing-read-fixtures.sql'];tables=self.packet['fixture_bypasses']['existing_read_owner_commit_only']
  self.assertNotIn('app.professional_profiles',tables);self.assertNotIn('app.candidate_profiles',tables)
  for table in tables:
   pattern=r'CREATE CONSTRAINT TRIGGER owner_commit AFTER INSERT OR UPDATE ON "'+table.replace('.','"."')+'"'
   self.assertRegex(app,pattern);self.assertEqual(seed.count('ALTER TABLE '+table+' DISABLE TRIGGER owner_commit;'),1);self.assertEqual(seed.count('ALTER TABLE '+table+' ENABLE TRIGGER owner_commit;'),1)
  for name,text in self.files.items():
   if name.endswith('.sql'):
    self.assertNotIn('DISABLE TRIGGER ALL',text);self.assertNotIn('DISABLE TRIGGER physical_guard',text);self.assertNotIn('CREATE OR REPLACE FUNCTION',text)
 def test_consent_fixture_uses_guarded_app_and_complete_prerequisite_caps(self):
  self.assertEqual(len(self.packet['fixture_operations']),4)
  for case in self.packet['fixture_operations']:
   grant=self.packet['grants'][case['grant']];self.assertEqual(grant['database_login_role'],'wa_app_runtime');self.assertEqual(grant['owner_module_id'],'consent_disclosure')
   self.assertIn(grant['action'],('SH-007.v1','recordConsentPresentation.v1'));self.assertIn('clock_timestamp()',self.files[case['sql']]) if case['model']=='ConsentLog' else None
   self.assertTrue(any('/contentRevision/' in f for f in grant['allowed_fields']))
  self.assertNotIn('DISABLE TRIGGER consent_',self.files['consent-owner-fixture-open.sql'])
 def test_related_controls_keep_existing_child_caps(self):
  for name in ('consent-presentation','consent-proof'):
   base=self.packet['grants'][name];bad=self.packet['grants'][name+'-missing-relation']
   child=[f for f in base['allowed_fields'] if '/SELECT/' in f and not f.startswith(base['target_kind']+'/')]
   self.assertTrue(child);self.assertTrue(set(child)<=set(bad['allowed_fields']))
   self.assertFalse(any('/contentRevision/' in f or '/presentation/' in f for f in bad['allowed_fields']))
 def test_worker_catalog_has_real_claim_currentness_and_plan_preconditions(self):
  seed=self.files['existing-read-fixtures.sql'];self.assertIn("'customer'",seed);self.assertIn("'active'",seed);self.assertIn("'free'",seed)
  for stem in ('plan','definition','benefit'):
   g=self.packet['grants'][stem+'-worker'];self.assertEqual(g['source_generation'],'1');self.assertEqual(g['action'],'assignDefaultFreeTrack.v1');self.assertTrue(any('/version/' in f for f in g['allowed_fields']));self.assertTrue(any('/contentHash/' in f for f in g['allowed_fields']));self.assertTrue(any(f.startswith('CustomerProfile/') for f in g['allowed_fields']))
  claim=self.files['worker-read-fixture-claim.sql'];self.assertIn('fence=fence+1',claim);self.assertIn("current_setting('wa.lease_secret')",claim);self.assertIn('RETURNING id',claim)
 def test_pure_purpose_update_caps_are_complete_but_no_owner_write_claim(self):
  for stem in ('user-actor','security-actor','plan-app'):
   g=self.packet['grants'][stem+'-write-denied'];self.assertTrue(any('/UPDATE/@row' in f for f in g['allowed_fields']));self.assertTrue(any('/UPDATE/revision' in f for f in g['allowed_fields']))
   case=next(c for c in self.packet['cases'] if c['name']==stem+'-write-denied');self.assertEqual(case['expected'],{'modified':0})
 def test_query_insert_uses_exact_fresh_root_and_native_guard(self):
  for name in ('content-query-insert','presentation-query-insert'):
   g=self.packet['grants'][name];self.assertIn(G.quote(g['target_id']),self.files[name+'.sql']);self.assertTrue(any('/'+g['target_id']+'/INSERT/' in f for f in g['allowed_fields']));self.assertIn(g['action'],('SH-009.v1','SH-010.v1'))
 def test_privacy_gate_has_otherwise_matching_owner_scope(self):
  g=self.packet['grants']['privacy-completion-gate'];self.assertEqual((g['owner_module_id'],g['action'],g['purpose'],g['target_kind']),('privacy_data_erasure','SH-049.v1','owner:orchestrateWorkflowSteps','PrivacyRequest'))
  self.assertTrue(any('/UPDATE/completedAt' in f for f in g['allowed_fields']));self.assertIn('revision=revision+1',self.files['privacy-completion-gate.sql'])
 def test_counts_hashes_cover_all_non_grant_application_relations(self):
  expected=self.packet['expected_counts'];self.assertEqual(len(expected),41);self.assertNotIn('platform.database_action_grant',expected)
  self.assertEqual(expected['app.track_enrollment_receipt'],0);self.assertEqual(expected['platform.runtime_attempt'],0);self.assertEqual(expected['app.consent_presentation'],2)
  query=self.files['complete-state-observe.sql'];self.assertIn('COLLATE "C"',query);self.assertEqual(query.count("'rows_sha256'"),41)

if __name__=='__main__':unittest.main(verbosity=2)
