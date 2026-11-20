"""Real initialized source admission on a clone; no runtime/network execution."""
from pathlib import Path
from contextlib import redirect_stdout
from copy import deepcopy
import builtins,hashlib,io,json,runpy,subprocess,tempfile,types,unittest
from unittest.mock import patch
TASK=Path(__file__).resolve().parent;ROOT=TASK/'workinants-correction-pass'
HELP=runpy.run_path(str(TASK/'check_sixread_owned_resource_v1_preparer_pinner_20261119.py'))
CORE='execute_local_f0_scoped_reads_owned_resource_v1_20261119.py';STEPS='local_f0_scoped_reads_owned_resource_v1_operation_steps.py'
def sha(raw):return hashlib.sha256(raw).hexdigest()
def runtime_git(root,args,**options):
 if args[:4]==['git','-c','core.longpaths=true','rev-parse']:
  value='b'*40 if args[4]=='HEAD'else'c'*40
  return types.SimpleNamespace(returncode=0,stdout=value+'\n',stderr='')
 if args[:4]==['git','-c','core.longpaths=true','show']:
  commit,name=args[4].split(':',1);assert commit=='b'*40
  return types.SimpleNamespace(returncode=0,stdout=(root/name).read_bytes(),stderr=b'')
 raise AssertionError('ONLY_MOCKED_READ_ONLY_SOURCE_GIT_BOUNDARY')
class AdmissionTests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.temp=tempfile.TemporaryDirectory(prefix='sixread-owned-whole-source-',dir=TASK);cls.fixture=HELP['clone_fixture'](Path(cls.temp.name)/'clone');HELP['approve_clone'](cls.fixture)
  cls.path,_=HELP['prepare_fixture'](cls.fixture,'94763468-9cad-4bee-beb4-1733224a51fb');world=HELP['GitWorld'](cls.fixture['ROOT'])
  with patch.object(subprocess,'run',side_effect=world.run):cls.fixture['pin']['pin'](cls.path)
  value=json.loads(cls.path.read_bytes());value['review_status']='APPROVED_LOCAL_F0_SCOPED_READ_COMPANION_OWNED_RESOURCE_V1_ATTEMPT';cls.path.write_bytes(HELP['encoded'](value))
 @classmethod
 def tearDownClass(cls):cls.temp.cleanup()
 def setUp(self):
  self.n=runpy.run_path(str(self.fixture['TASK']/CORE))['launch'].__globals__;self.n['initialize'](self.path);exec(compile((self.fixture['TASK']/STEPS).read_bytes(),str(self.fixture['TASK']/STEPS),'exec'),self.n)
  self.n['OUT'].mkdir(exist_ok=True);self.git=lambda args,**options:runtime_git(self.fixture['ROOT'],args,**options)
 def test_01_actual_complete_verifier_current_committed_catalog16_helpers7_and_source7(self):
  with patch.object(subprocess,'run',side_effect=self.git),redirect_stdout(io.StringIO()):self.n['verify_scoped_read_packet']()
  self.assertTrue(self.n['SCOPED_STATE']['tools_verified_before_compile']);self.assertEqual(len(self.n['HELPERS']),7);self.assertEqual(len(self.n['SCOPED_FIXTURES']['cases']),71)
  self.assertEqual(len(self.n['SCOPED_FIXTURES']['prepared_files_sha256']),76);self.assertEqual(len(self.n['CATALOG']['pins']),16);self.assertEqual(self.n['report']['source_verification']['files_sha256'],self.n['MANIFEST']['packet_files_sha256'])
 def test_02_missing_actual_helpers_or_historical_snapshot_reject_before_project_compile(self):
  for name in('scripts/sql-review/run-context-control-rehearsal.py','scripts/sql-review/run-first-rehearsal.py','scripts/sql-review/run-scoped-read-companion-rehearsal.py',self.n['OWNED_ARCHIVE']+'/'+CORE+'.txt'):
   original=self.n['MANIFEST']['packet_files_sha256'].pop(name)
   try:
    with patch.object(builtins,'compile',side_effect=AssertionError('NO_PROJECT_COMPILE')),self.assertRaises(self.n['Stop']):self.n['verify_scoped_read_packet']()
   finally:self.n['MANIFEST']['packet_files_sha256'][name]=original
 def test_03_physical_snapshot_and_raw_link_source_refused_before_compile(self):
  name=self.n['OWNED_ARCHIVE']+'/'+CORE+'.txt';path=self.fixture['ROOT']/name;raw=path.read_bytes();path.write_bytes(b'OLD_HELD_SNAPSHOT_NOT_EXECUTABLE')
  try:
   with patch.object(builtins,'compile',side_effect=AssertionError('NO_PROJECT_COMPILE')),self.assertRaises(self.n['Stop']):self.n['verify_scoped_read_packet']()
  finally:path.write_bytes(raw)
  physical=self.fixture['TASK']/CORE;actual=Path.is_symlink
  with patch.object(Path,'is_symlink',lambda p:p==physical or actual(p)),patch.object(builtins,'compile',side_effect=AssertionError('NO_PROJECT_COMPILE')),self.assertRaises(self.n['Stop']):self.n['verify_scoped_read_packet']()
 def test_04_source_member_extra_and_stale_history_stop_before_compile(self):
  target=self.n['MANIFEST']['migration_targets']['ok'];target['source_files_sha256']['unlisted.py']='a'*64
  try:
   with patch.object(builtins,'compile',side_effect=AssertionError('NO_PROJECT_COMPILE')),self.assertRaises(self.n['Stop']):self.n['verify_scoped_read_packet']()
  finally:target['source_files_sha256'].pop('unlisted.py')
  history=Path(target['source_snapshot'])/'prisma/foundation/history-manifest.json';raw=history.read_bytes();value=json.loads(raw);value['run_id']='550e8400-e29b-41d4-a716-446655440000';history.write_bytes(HELP['encoded'](value))
  try:
   with patch.object(builtins,'compile',side_effect=AssertionError('NO_PROJECT_COMPILE')),self.assertRaises(self.n['Stop']):self.n['verify_scoped_read_packet']()
  finally:history.write_bytes(raw)
 def test_05_second_source_read_drift_cannot_use_cached_old_bytes(self):
  finalizer=self.fixture['ROOT']/'review-output/foundation-bootstrap-finalize.review.sql';actual=Path.read_bytes;reads=[]
  def read(path):
   if path==finalizer:
    reads.append(1)
    if len(reads)>1:return b'SECOND_READ_SOURCE_MUTANT'
   return actual(path)
  with patch.object(Path,'read_bytes',read),patch.object(subprocess,'run',side_effect=self.git),patch.object(builtins,'compile',side_effect=AssertionError('NO_PROJECT_COMPILE')),self.assertRaises(self.n['Stop']):self.n['verify_scoped_read_packet']()
  self.assertGreaterEqual(len(reads),2)
if __name__=='__main__':
 import sys
 sys.addaudithook(HELP['audit']);unittest.main(verbosity=2)
