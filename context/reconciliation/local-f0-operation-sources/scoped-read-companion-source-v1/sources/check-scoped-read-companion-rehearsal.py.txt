"""Environment-free source, parser and byte-reproduction checks."""
import ast
import importlib.util
import json
from pathlib import Path
import socket
import subprocess
import sys
import unittest
from unittest.mock import patch

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'scripts'))
import scoped_read_companion_protocol as protocol
spec=importlib.util.spec_from_file_location('scoped_prepare',ROOT/'scripts/prepare-scoped-read-companion-rehearsal.py')
prepare=importlib.util.module_from_spec(spec);spec.loader.exec_module(prepare)

class SourceChecks(unittest.TestCase):
 @classmethod
 def setUpClass(cls):cls.files,cls.packet=prepare.build()
 def setUp(self):
  for name in ('run','Popen','check_call','check_output','call'):
   guard=patch.object(subprocess,name,side_effect=AssertionError('NO_PROCESS'));guard.start();self.addCleanup(guard.stop)
  guard=patch.object(socket,'create_connection',side_effect=AssertionError('NO_NETWORK'));guard.start();self.addCleanup(guard.stop)
 def test_exact_six_assertions_and_71_protocols(self):
  self.assertEqual(len(self.packet['selected_assertions']),6);self.assertEqual(len(self.packet['cases']),71)
  self.assertEqual({x['case_id'] for x in self.packet['selected_assertions']},{'P0C-TABLE-'+m+'-ALLOW' for m,_ in protocol.SPECS})
  self.assertTrue(all(x['assertion_id']=='positive.wa_app_runtime.select' and x['status']=='NOT_RUN' for x in self.packet['selected_assertions']))
 def test_all_SQL_parses_under_pinned_parser(self):
  import pglast
  self.assertEqual(pglast.__version__,'v7.21')
  for name,text in self.files.items():
   if name.endswith('.sql'):
    with self.subTest(name=name):self.assertTrue(pglast.parse_sql(text))
 def test_build_is_byte_reproducible_and_matches_output(self):
  files,packet=prepare.build();self.assertEqual(files,self.files);self.assertEqual(packet,self.packet)
  self.assertEqual({p.name for p in prepare.OUT.iterdir()},set(files))
  for name,text in files.items():self.assertEqual((prepare.OUT/name).read_bytes(),text.encode())
 def test_eight_owner_only_bypasses_flush_before_DDL(self):
  text=self.files['existing-scoped-read-fixtures.sql'];self.assertEqual(text.count('INSERT INTO '),16)
  self.assertEqual([line.split()[2] for line in text.splitlines() if 'DISABLE TRIGGER' in line],list(protocol.FIXTURE_TABLES))
  self.assertEqual([line.split()[2] for line in text.splitlines() if 'ENABLE TRIGGER' in line],list(reversed(protocol.FIXTURE_TABLES)))
  self.assertLess(text.rfind('INSERT INTO'),text.index('SET CONSTRAINTS ALL IMMEDIATE;'));self.assertLess(text.index('SET CONSTRAINTS ALL IMMEDIATE;'),text.index('ENABLE TRIGGER'))
  self.assertNotIn('DISABLE TRIGGER ALL',text);self.assertNotIn('DISABLE ROW LEVEL',text);self.assertNotIn('CREATE FUNCTION',text)
 def test_principal_generations_and_SQL_NULL_metadata(self):
  text=self.files['existing-scoped-read-fixtures.sql'];self.assertIn("'"+prepare.SECURITY[1]+"','"+prepare.USERS[1]+"',clock_timestamp(),0,1",text)
  events=[line for line in text.splitlines() if line.startswith('INSERT INTO app.audit_events')];self.assertEqual(len(events),2);self.assertTrue(all(',NULL);' in x for x in events));self.assertNotIn("'null'",text)
 def test_all42_state_and_no_work_or_enrollment_facts(self):
  self.assertEqual(len(self.packet['expected_counts']),42);self.assertEqual(sum(self.packet['expected_counts'].values()),16)
  for table,count in self.packet['expected_counts'].items():self.assertEqual(count,2 if table in protocol.FIXTURE_TABLES else 0)
  self.assertEqual(len(self.packet['worker_acl_ceiling_rows']),32)
 def test_finite_caps_every_actual_policy_column_and_revision(self):
  acl=json.loads((ROOT/'context/reconciliation/foundation-sql-draft-access.json').read_bytes())
  for model,_ in protocol.SPECS:
   case=next(c for c in self.packet['cases'] if c['model']==model and c['variant']=='positive-root');g=self.packet['grants'][case['grant']]
   self.assertEqual(g['allowed_fields'],prepare.capabilities(acl,model,self.packet['ids'][model]));self.assertFalse(any('*' in x for x in g['allowed_fields']))
 def test_wrong_purpose_and_other_root_change_exactly_one_field(self):
  for model,_ in protocol.SPECS:
   base=self.packet['grants'][model.lower()+'-positive-root']
   for variant,field in [('wrong-purpose','purpose'),('wrong-action','action'),('wrong-owner','owner_module_id'),('other-existing-root','target_id')]:
    changed=self.packet['grants'][model.lower()+'-'+variant];self.assertEqual({k for k in base if base[k]!=changed[k]},{'template_id',field})
 def test_cross_model_tokens_are_complete_without_invented_edges(self):
  acl=json.loads((ROOT/'context/reconciliation/foundation-sql-draft-access.json').read_bytes())
  for model,_ in protocol.SPECS:
   g=self.packet['grants'][model.lower()+'-cross-model-complete-caps'];wanted=prepare.capabilities(acl,model,self.packet['ids'][model])+prepare.capabilities(acl,'User',prepare.USERS)+prepare.capabilities(acl,'UserSecurityProfile',prepare.SECURITY)
   self.assertEqual(g['allowed_fields'],sorted(wanted));self.assertEqual(self.files[model.lower()+'-cross-model-complete-caps.sql'].count('SELECT count(*)'),6)
 def test_current_B_is_legitimate_contrast_not_subject_denial(self):
  for model,_ in protocol.SPECS:
   a=self.packet['grants'][model.lower()+'-principal-generation-mismatch'];b=self.packet['grants'][model.lower()+'-principalB-current-control']
   self.assertEqual({k for k in a if a[k]!=b[k]},{'template_id','security_generation'});self.assertEqual(b['principal_user_id'],prepare.USERS[1]);self.assertEqual(b['security_generation'],'1')
 def test_UserRole_composite_key_and_revision_negatives(self):
  for case in self.packet['cases']:
   if case['model']=='UserRole':self.assertIn("user_id::text||':'||role::text=",self.files[case['sql']])
  for model in ('UserRole','AuthProviderAccount'):
   for variant in ('missing-revision-capability','wrong-source-generation'):self.assertIn(model.lower()+'-'+variant,self.packet['grants'])
 def test_module_graph_is_admitted_before_compile(self):
  source=(ROOT/'scripts/sql-review/run-scoped-read-companion-rehearsal.py').read_text();tree=ast.parse(source)
  function=next(n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name=='load_inputs')
  calls=[n for n in ast.walk(function) if isinstance(n,ast.Call) and isinstance(n.func,ast.Name)]
  closed=next(n for n in calls if n.func.id=='need' and any(isinstance(s,ast.Constant) and s.value=='HELPER_SOURCE_CLOSURE' for s in ast.walk(n)))
  self.assertTrue(all(n.lineno>closed.lineno for n in calls if n.func.id=='compiled'));self.assertTrue(set(prepare.HELPERS)<=set(self.packet['source_files_sha256']))
 def test_packet_digest_and_source_SHA(self):
  self.assertEqual(protocol.digest({k:self.packet[k] for k in ('source_files_sha256','prepared_files_sha256')}),self.packet['source_only_packet_sha256'])
  self.assertEqual(self.packet['source_files_sha256'][prepare.APPLICATION],protocol.APPLICATION_SHA)
  for name,h in self.packet['source_files_sha256'].items():self.assertEqual(protocol.sha((ROOT/name).read_bytes()),h)

if __name__=='__main__':unittest.main(verbosity=2)
