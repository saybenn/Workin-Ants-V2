"""Offline real preparer/pinner checks on a source-bound exclusive TASK clone.

Only cloned validation is projected approved for tests. Live gates stay PENDING.
All real process/network/DB boundaries are forbidden; Git is a byte transport.
"""
from contextlib import ExitStack
from copy import deepcopy
import hashlib
import json
from pathlib import Path
import runpy
import shutil
import subprocess
import sys
import tempfile
import time
import types
import unittest
from unittest.mock import patch,Mock

TASK=Path(__file__).resolve().parent;ROOT=TASK/'workinants-correction-pass'
PREP='prepare_local_f0_scoped_reads_owned_resource_v1_plan.py'
PIN='pin_local_f0_scoped_reads_owned_resource_v1_plan_20261119.py'
BASELINE=TASK/'local-f0-catalog-v4-plan-23bd8979/operation-manifest.json'
RUN='92763468-9cad-4bee-beb4-1733224a51fb'

def sha(raw):return hashlib.sha256(raw).hexdigest()
def encoded(v):return (json.dumps(v,indent=2,allow_nan=False)+'\n').encode()
def audit(event,args):
 if event in {'subprocess.Popen','os.system','os.posix_spawn','os.spawn','socket.connect','socket.connect_ex','socket.bind','socket.getaddrinfo'}:raise AssertionError('ACTUAL_PROCESS_NETWORK_FORBIDDEN')

def clone_fixture(destination):
 """Return real-source clone and APIs, with live PENDING metadata preserved.

 The destination must be a fresh exclusive TASK directory. Both source graph
 and copied five are byte checked. The 113900903-byte tooling cache is copied,
 never executed. Baseline path fields are rebound inside the clone only.
 """
 destination=Path(destination).resolve();assert destination.is_relative_to(TASK.resolve()) and not destination.exists()
 destination.mkdir();clone_root=destination/'workinants-correction-pass';clone_root.mkdir()
 prep=runpy.run_path(str(TASK/PREP));baseline=json.loads(BASELINE.read_bytes())
 packet=json.loads((ROOT/prep['FIXTURES']).read_bytes())
 external={name:sha((TASK/name).read_bytes()) for name in prep['EXTERNAL_FILES']}
 pins=prep['source_inventory'](baseline['packet_files_sha256'],packet,external)
 for name,wanted in pins.items():
  raw=(ROOT/name).read_bytes();assert sha(raw)==wanted
  target=clone_root/name;target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(raw)
 # These two ignored package-data files are admitted separately by the real
 # tool-data verifier against catalog metadata and the complete tool archive.
 # They are not Git/source packet entries and are never executable fixtures.
 tool_data=baseline['catalog']['tool_source_files_sha256']
 for name,wanted in tool_data.items():
  raw=(ROOT/name).read_bytes();assert sha(raw)==wanted
  target=clone_root/name;target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(raw)
 owner=json.loads((ROOT/prep['OWNER_VALIDATION']).read_bytes())
 for name,wanted in {**external,**owner['operator_sources_sha256']}.items():
  raw=(TASK/name).read_bytes();assert sha(raw)==wanted;(destination/name).write_bytes(raw)
 tools=destination/'pinned-prisma-tools.tar.gz';shutil.copyfile(baseline['tool_archive'],tools)
 assert sha(tools.read_bytes())==prep['TOOL_ARCHIVE_SHA']
 nested_entry=baseline['migration_targets']['ok'];nested=(Path(nested_entry['manifest_path'])).read_bytes()
 assert sha(nested)==nested_entry['manifest_sha256']
 nested_path=destination/'baseline-nested.json';nested_path.write_bytes(nested)
 baseline['migration_targets']['ok']['manifest_path']=str(nested_path)
 baseline['tool_archive']=str(tools);baseline_path=destination/'baseline.json';baseline_path.write_bytes(encoded(baseline))
 return {'TASK':destination,'ROOT':clone_root,'baseline':baseline_path,'baseline_sha256':sha(baseline_path.read_bytes()),
  'prepare':runpy.run_path(str(destination/PREP)),'pin':runpy.run_path(str(destination/PIN)),'source_pins':pins,'tool_data':dict(tool_data),'external':external}

def approve_clone(fixture):
 """Test-only metadata projection; this function cannot edit a live gate."""
 root=fixture['ROOT'];task=fixture['TASK'];assert root.parent==task and task!=TASK and task.is_relative_to(TASK)
 prep=fixture['prepare'];path=root/prep['OWNED_VALIDATION'];record=json.loads(path.read_bytes())
 review_path=prep['OWNED_ARCHIVE']+'/reviews/OFFLINE-CLONE-TEST-ONLY-source-review.json'
 review=encoded({'schema':'workinants.offline-test-only-review-projection.v1','source_only_mock':True,'live_source_approval':False,'runtime_approval':False})
 (root/review_path).write_bytes(review);record['archive_files_sha256'][review_path]=sha(review)
 for gate in ('independent_safety_sql_review','independent_owned_resource_review'):
  record[gate]={'decision':'SOURCE_APPROVED','path':review_path,'sha256':sha(review),'operator_sources_sha256':fixture['external'],'test_only':True}
 path.write_bytes(encoded(record))

def prepare_fixture(fixture,run=RUN):
 output=fixture['prepare']['prepare'](fixture['baseline'],fixture['baseline_sha256'],run)
 return Path(output['operation_manifest']),output

class GitWorld:
 def __init__(self,root,mutate_blob=False):self.root=root;self.mutate_blob=mutate_blob;self.calls=[]
 def run(self,args,**options):
  prefix=['git','--no-optional-locks','-c','core.longpaths=true'];assert args[:4]==prefix
  command=tuple(args[4:]);self.calls.append(command)
  assert options['cwd']==self.root and options['shell'] is False
  if command==('rev-parse','HEAD'):raw=('b'*40+'\n').encode()
  elif command==('rev-parse','HEAD^{tree}'):raw=('c'*40+'\n').encode()
  elif command==('cat-file','--batch'):
   rows=[]
   for index,line in enumerate(options['input'].decode().splitlines()):
    commit,name=line.split(':',1);assert commit=='b'*40;body=(self.root/name).read_bytes()
    if self.mutate_blob and index==0:body=b'OFFLINE_COMMITTED_BLOB_MUTANT'
    rows.extend([('0'*40+' blob '+str(len(body))+'\n').encode(),body,b'\n'])
   raw=b''.join(rows)
  else:raise AssertionError('NON_READ_ONLY_GIT_COMMAND')
  return types.SimpleNamespace(returncode=0,stdout=raw,stderr=b'')

class PreparerPinnerTests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.temporary=tempfile.TemporaryDirectory(prefix='sixread-owned-admission-',dir=TASK)
  cls.base=Path(cls.temporary.name).resolve();assert cls.base.is_relative_to(TASK.resolve())
  cls.fixture=clone_fixture(cls.base/'clone');cls.prep=cls.fixture['prepare'];cls.pin=cls.fixture['pin']
 @classmethod
 def tearDownClass(cls):cls.temporary.cleanup()
 def test_01_both_modules_are_dormant_with_process_network_forbidden(self):
  with patch.object(subprocess,'run',side_effect=AssertionError('NO_IMPORT_PROCESS')),patch.object(subprocess,'Popen',side_effect=AssertionError('NO_IMPORT_PROCESS')):
   self.assertTrue(callable(runpy.run_path(str(TASK/PREP))['prepare']));self.assertTrue(callable(runpy.run_path(str(TASK/PIN))['pin']))
 def test_02_real_preparation_with_pending_gates_and_pinner_rejects_before_git(self):
  path,out=prepare_fixture(self.fixture);value=json.loads(path.read_bytes())
  self.assertEqual(out['status'],'SOURCE_PREPARED_NOT_EXECUTED');self.assertFalse(out['database_contacted']);self.assertFalse(out['resources_created'])
  self.assertEqual(out['source_files'],7);self.assertEqual(value['review_status'],'PENDING_OPERATIONAL_REVIEW')
  self.assertEqual(value['source_commit'],'TO_BE_PINNED');self.assertEqual(value['packet_files_sha256'],{})
  self.assertFalse(Path(value['evidence_directory']).exists());self.assertEqual(len(value['migration_targets']),1)
  cfg=value['scoped_read'];self.assertEqual(cfg['fixtures_sha256'],self.prep['FIXTURES_SHA'])
  self.assertNotIn('context/reconciliation/local-f0-scoped-read-operation-source-validation.json',value['prepared_source_file_inventory_sha256'])
  with patch.object(subprocess,'run') as git,self.assertRaises(self.pin['Held']) as failure:self.pin['pin'](path)
  self.assertEqual(str(failure.exception),'SAFETY_SQL_REVIEW_REQUIRED');git.assert_not_called()
  self.__class__.pending_manifest=path
 def test_03_exact_tool_member_set_and_versions_checked_by_both_actual_methods(self):
  baseline=json.loads(self.fixture['baseline'].read_bytes());nested=json.loads(Path(baseline['migration_targets']['ok']['manifest_path']).read_bytes())
  for module in (self.prep,self.pin):
   actual=module['verify_tools'](baseline['tool_archive'],baseline['tool_archive_sha256'],nested['tools']);self.assertEqual(actual['file_count'],10300)
   bad=deepcopy(nested['tools']);bad['node_version']='v0.0.0'
   with self.assertRaises((self.prep['Refused'],self.pin['Held'])) as failure:module['verify_tools'](baseline['tool_archive'],baseline['tool_archive_sha256'],bad)
   self.assertEqual(str(failure.exception),'EXACT_TOOL_VERSIONS')
 def test_02a_owned_resource_gate_independently_pending_blocks_before_git(self):
  path=self.fixture['ROOT']/self.prep['OWNED_VALIDATION'];original=path.read_bytes();record=json.loads(original)
  record['independent_safety_sql_review']['decision']='SOURCE_APPROVED';path.write_bytes(encoded(record))
  try:
   manifest,out=prepare_fixture(self.fixture,'94763468-9cad-4bee-beb4-1733224a51fb')
   with patch.object(subprocess,'run') as git,self.assertRaises(self.pin['Held']) as failure:self.pin['pin'](manifest)
   self.assertEqual(str(failure.exception),'OWNED_RESOURCE_REVIEW_REQUIRED');git.assert_not_called()
  finally:path.write_bytes(original)
 def test_04_duplicate_and_nonfinite_json_rejected_by_both_actual_decoders(self):
  for module in (self.prep,self.pin):
   for raw in ('{"a":1,"a":2}','{"a":NaN}'):
    with self.assertRaises((self.prep['Refused'],self.pin['Held'])):module['decoded'](raw)
 def test_05_raw_source_link_refusal_before_alias_resolution(self):
  path=self.fixture['ROOT']/'scripts/prepare-local-f0-history.py';original=Path.is_symlink
  def projected(p):return True if p==path else original(p)
  for module,name in ((self.prep,'source'),(self.pin,'read_source')):
   with patch.object(Path,'is_symlink',projected),self.assertRaises((self.prep['Refused'],self.pin['Held'])) as failure:module[name]('scripts/prepare-local-f0-history.py',self.prep['HISTORY_SHA'])
   self.assertEqual(str(failure.exception),'SOURCE_SYMLINK_REFUSED')
 def test_06_clone_only_approved_preparation_and_missing_actual_CTX_helper_reject(self):
  approve_clone(self.fixture);path,out=prepare_fixture(self.fixture,'93763468-9cad-4bee-beb4-1733224a51fb');original=path.read_bytes();value=json.loads(original)
  value['prepared_source_file_inventory_sha256'].pop('scripts/sql-review/run-context-control-rehearsal.py');path.write_bytes(encoded(value))
  try:
   with patch.object(subprocess,'run') as git,self.assertRaises(self.pin['Held']) as failure:self.pin['pin'](path)
   self.assertEqual(str(failure.exception),'RUNTIME_CLOSURE_MISSING');git.assert_not_called()
  finally:path.write_bytes(original)
  self.__class__.approved_manifest=path
 def test_07_current_source_drift_rejects_before_git(self):
  source=self.fixture['ROOT']/'scripts/sql-review/run-context-control-rehearsal.py';original=source.read_bytes();source.write_bytes(original+b'\n# OFFLINE_CURRENT_SOURCE_MUTANT\n')
  try:
   with patch.object(subprocess,'run') as git,self.assertRaises(self.pin['Held']) as failure:self.pin['pin'](self.approved_manifest)
   self.assertEqual(str(failure.exception),'CURRENT_SOURCE_HASH_MISMATCH');git.assert_not_called()
  finally:source.write_bytes(original)
 def test_08_real_pinner_committed_blob_mutant_rejects_without_manifest_write(self):
  path=self.approved_manifest;original=path.read_bytes();world=GitWorld(self.fixture['ROOT'],mutate_blob=True)
  with patch.object(subprocess,'run',side_effect=world.run),self.assertRaises(self.pin['Held']) as failure:self.pin['pin'](path)
  self.assertEqual(str(failure.exception),'COMMITTED_SOURCE_HASH_MISMATCH');self.assertEqual(path.read_bytes(),original)
  self.assertFalse(path.with_name('operation-manifest-before-source-pin.json').exists())
 def test_09_real_pinner_full_current_committed_packet_stays_operational_pending(self):
  path=self.approved_manifest;original=path.read_bytes();world=GitWorld(self.fixture['ROOT'])
  with patch.object(subprocess,'run',side_effect=world.run):out=self.pin['pin'](path)
  value=json.loads(path.read_bytes());self.assertEqual(out['status'],'SOURCE_PINNED_PENDING_OPERATIONAL_REVIEW')
  self.assertEqual(value['source_commit'],'b'*40);self.assertEqual(value['source_tree'],'c'*40)
  self.assertEqual(value['packet_files_sha256'],value['prepared_source_file_inventory_sha256']);self.assertEqual(value['packet_sha256'],self.pin['aggregate'](value['packet_files_sha256']))
  self.assertEqual(value['review_status'],'PENDING_OPERATIONAL_REVIEW');self.assertFalse(out['runtime_approved']);self.assertFalse(out['git_mutated'])
  self.assertEqual(path.with_name('operation-manifest-before-source-pin.json').read_bytes(),original)
  self.assertEqual(world.calls,[('rev-parse','HEAD'),('rev-parse','HEAD^{tree}'),('cat-file','--batch'),('rev-parse','HEAD')])

if __name__=='__main__':
 sys.addaudithook(audit);unittest.main()
