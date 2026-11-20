"""Real new Restore source/pinner graph using isolated synthetic review clones."""
import ast
import copy
from contextlib import redirect_stdout
import hashlib
import io
import json
from pathlib import Path
import runpy
import tempfile
import unittest
from unittest.mock import Mock,patch

TASK = Path(__file__).resolve().parent
BASE = runpy.run_path(str(TASK / 'check_local_f0_restore_operation_bound_evidence_v3.py'))
CANARY = BASE['CANARY']
ROOT = BASE['ROOT']


class RestoreBoundEvidenceSourceGateTests(unittest.TestCase):
    setUp = BASE['RestoreOperationTests'].setUp
    full_fixture = BASE['RuntimeClosureTests'].full_fixture

    def test_actual_initializer_and_whole_verifier_populate_all_resource_globals(self):
        with tempfile.TemporaryDirectory(prefix='offline-restore-v2-initialize-', dir=TASK) as directory:
            n, master, path, root, prep = self.full_fixture(Path(directory))
            self.assertEqual(n['created_containers'], {})
            self.assertEqual(n['created_volumes'], {})
            n['verify_restore_packet']()
            stem = 'wa-p0c-' + master['run_id'][:8] + '-restore-'
            self.assertEqual(n['RESOURCE_CONTAINERS'], (stem+'source', stem+'staging', stem+'target'))
            self.assertEqual(n['RESOURCE_VOLUMES'], (stem+'source-data', stem+'target-data'))
            self.assertEqual((n['SOURCE'], n['STAGING'], n['RESTORED']), n['RESOURCE_CONTAINERS'])
            self.assertEqual(n['_SAFETY_IO_PROFILE'], 'COMMON')
            self.assertEqual(n['_SAFETY_SQL_PROFILE'], 'STANDARD')
            self.assertEqual(len(n['ROLES']), 6)
            self.assertFalse(Path(master['evidence_directory']).exists())

    def fixture(self, decision):
        temp = tempfile.TemporaryDirectory(prefix='offline-restore-v2-gate-', dir=TASK)
        self.addCleanup(temp.cleanup)
        n, master, path, root, prep = self.full_fixture(Path(temp.name))
        pin = runpy.run_path(str(TASK / 'pin_local_f0_restore_plan_20261119_bound_evidence_v3.py'))
        g = pin['validate_filesystem'].__globals__
        g['ROOT'] = root
        g['TASK'] = TASK
        validation = root / g['VALIDATION']
        value = json.loads((ROOT / g['VALIDATION']).read_bytes())
        # Preparation closes the source inventory; the real pinner then admits
        # its own current validation/archive files. Supply that real filesystem
        # layer in the isolated clone instead of manufacturing prepared entries.
        for name, wanted in value['archive_files_sha256'].items():
            destination = root / name
            destination.parent.mkdir(parents=True, exist_ok=True)
            body = (ROOT / name).read_bytes()
            self.assertEqual(hashlib.sha256(body).hexdigest(), wanted)
            destination.write_bytes(body)
        validation.parent.mkdir(parents=True, exist_ok=True)
        value['independent_bound_evidence_review'] = {'decision': decision, 'scope': 'OFFLINE_EXPLICIT_ISOLATED_TEST_ONLY'}
        if decision=='SOURCE_APPROVED':
            peer=g['SOURCE_ROOT']+'/reviews/offline-bound-evidence-review.json';body=b'{"decision":"SOURCE_APPROVED","scope":"ISOLATED_TEST_ONLY"}\n';target=root/peer;target.write_bytes(body)
            value['independent_bound_evidence_review'].update(path=peer,sha256=hashlib.sha256(body).hexdigest(),exact_five_sha256=value['all_five_sources_sha256'])
        value['archive_files_sha256']={p.relative_to(root).as_posix():hashlib.sha256(p.read_bytes()).hexdigest() for p in (root/g['SOURCE_ROOT']).rglob('*') if p.is_file()}
        value['archive_files_aggregate_sha256']=g['aggregate'](value['archive_files_sha256'])
        validation.write_text(json.dumps(value, indent=2) + '\n', encoding='utf-8')
        master.update(source_commit='TO_BE_PINNED', source_tree='TO_BE_PINNED', packet_sha256='TO_BE_PINNED', packet_files_sha256={})
        path.write_text(json.dumps(master, indent=2) + '\n', encoding='utf-8')
        return n, master, path, root, pin, g

    def test_actual_pinner_full_current_and_committed_graph_keeps_execution_pending(self):
        n, master, path, root, pin, g = self.fixture('SOURCE_APPROVED')
        original = path.read_bytes()
        _, raw, _, files = pin['validate_filesystem'](path)
        self.assertEqual(raw, original)
        self.assertTrue(all(hashlib.sha256((root / name).read_bytes()).hexdigest() == h for name, h in files.items()))
        calls = []
        def git(*args):
            calls.append(args)
            if args == ('rev-parse', 'HEAD'): return ('a' * 40 + '\n').encode()
            if args == ('rev-parse', 'HEAD^{tree}'): return ('b' * 40 + '\n').encode()
            self.assertEqual(args[0], 'show')
            self.assertTrue(args[1].startswith('a' * 40 + ':'))
            return (root / args[1].split(':', 1)[1]).read_bytes()
        g['git_read'] = git
        result = pin['pin'](path)
        value = json.loads(path.read_bytes())
        self.assertEqual(value['review_status'], 'PENDING_OPERATIONAL_REVIEW')
        self.assertEqual(value['packet_files_sha256'], files)
        self.assertEqual(path.with_name('operation-manifest-before-source-pin.json').read_bytes(), original)
        self.assertFalse(Path(master['evidence_directory']).exists())
        self.assertFalse(result['runtime_approved'])
        self.assertEqual(len(calls), len(files) + 3)
        self.assertEqual(len(master['restore']['external_files_sha256']), 4)
        self.assertIn(g['VALIDATION'], files)
        self.assertIn(g['SOURCE_ROOT'] + '/' + g['SELF'] + '.txt', files)

    def test_explicit_PENDING_new_review_blocks_actual_pinner_and_runtime_before_process(self):
        n, master, path, root, pin, g = self.fixture('PENDING_OFFLINE_TEST_ONLY')
        g['git_read'] = Mock(side_effect=AssertionError('NO_GIT_FOR_PENDING_REVIEW'))
        with self.assertRaisesRegex(g['Held'], 'BOUND_EVIDENCE_REVIEW_REQUIRED'):
            pin['pin'](path)
        g['git_read'].assert_not_called()
        actual = BASE['namespace']()['verify_common_packet']
        master['review_status'] = 'APPROVED_LOCAL_F0_RESTORE_ATTEMPT'
        master['packet_files_sha256'] = dict(master['prepared_source_file_inventory_sha256'])
        master['packet_files_sha256'][g['VALIDATION']] = hashlib.sha256((root / g['VALIDATION']).read_bytes()).hexdigest()
        n.update(MANIFEST=master, ROOT=root, command=Mock(side_effect=AssertionError('NO_PROCESS_FOR_PENDING_REVIEW')))
        actual.__globals__.update(n)
        with self.assertRaises(n['Stop']) as stopped:
            actual()
        self.assertEqual(stopped.exception.code, 'BOUND_EVIDENCE_REVIEW_REQUIRED')
        n['command'].assert_not_called()
        self.assertFalse(Path(master['evidence_directory']).exists())

    def test_missing_physical_fifth_snapshot_and_bad_committed_blob_stop_without_pin(self):
        n, master, path, root, pin, g = self.fixture('SOURCE_APPROVED')
        snapshot = root / g['SOURCE_ROOT'] / (g['SELF'] + '.txt')
        body = snapshot.read_bytes(); snapshot.unlink()
        g['git_read'] = Mock(side_effect=AssertionError('NO_GIT_BEFORE_PHYSICAL_FIFTH'))
        with self.assertRaises(g['Held']): pin['pin'](path)
        g['git_read'].assert_not_called()
        snapshot.write_bytes(body)
        original = path.read_bytes()
        def bad_git(*args, input=None):
            if args == ('rev-parse', 'HEAD'): return ('a' * 40).encode()
            if args == ('rev-parse', 'HEAD^{tree}'): return ('b' * 40).encode()
            return ('f' * 40 + ' blob ' + str(len(CANARY)) + '\n' + CANARY + '\n').encode()
        g['git_read'] = bad_git
        with self.assertRaises(g['Held']): pin['pin'](path)
        self.assertEqual(path.read_bytes(), original)
        self.assertFalse(path.with_name('operation-manifest-before-source-pin.json').exists())



    def test_actual_core_launch_initializes_and_pending_bound_gate_stops_before_helpers(self):
        n,master,path,root,pin,g=self.fixture('PENDING_OFFLINE_TEST_ONLY');actual_validation=json.loads((ROOT/g['VALIDATION']).read_bytes());files=dict(master['prepared_source_file_inventory_sha256']);files.update(actual_validation['archive_files_sha256']);files[g['VALIDATION']]=hashlib.sha256((ROOT/g['VALIDATION']).read_bytes()).hexdigest();master.update(source_commit='a'*40,source_tree='b'*40,packet_files_sha256=files,packet_sha256=g['aggregate'](files),review_status='APPROVED_LOCAL_F0_RESTORE_ATTEMPT');path.write_text(json.dumps(master));focused=runpy.run_path(str(TASK/'check_restore_bound_evidence_v3_focused_20261119.py'));world=focused['World'](n);world.present_c.clear();world.present_v.clear();original_compile=compile;compiled=[]
        def guarded(source,filename,*args,**kwargs):
            compiled.append(str(filename))
            if str(filename).startswith(str(ROOT/'scripts')):raise AssertionError('NO_HELPER_BEFORE_BOUND_SOURCE_REVIEW')
            return original_compile(source,filename,*args,**kwargs)
        with patch.object(BASE['subprocess'],'run',side_effect=world.run),patch('builtins.compile',guarded),redirect_stdout(io.StringIO()) as output:code=n['launch'](['--execute-reviewed-restore','--manifest',str(path)])
        self.assertEqual(code,1);self.assertEqual(n['report']['primary_failure']['code'],'BOUND_EVIDENCE_REVIEW_REQUIRED');self.assertEqual(n['created_containers'],{});self.assertEqual(n['created_volumes'],{});self.assertFalse(world.processes);self.assertFalse(any(x[0]=='global_zero' for x in world.events));self.assertEqual(compiled,[str(TASK/'local_f0_restore_operation_steps_bound_evidence_v3.py')]);self.assertNotIn(CANARY,output.getvalue())

    def test_new_five_scope_old_recipe_and_archive_are_exact(self):
        R=ROOT;pres=json.loads((TASK/'restore_bound_evidence_v3_before_author_preservation_20261119.json').read_bytes())
        for path,h in pres['files_sha256'].items():self.assertEqual(hashlib.sha256(Path(path).read_bytes()).hexdigest(),h,path)
        def funcs(raw):return {n.name:ast.dump(n,include_attributes=False) for n in ast.parse(raw).body if isinstance(n,(ast.FunctionDef,ast.ClassDef))}
        coreold=funcs((TASK/'execute_local_f0_restore_20261119_resource_mount_v2.py').read_text());corenew=funcs((TASK/'execute_local_f0_restore_20261119_bound_evidence_v3.py').read_text().replace('_bound_evidence_v3.py','_resource_mount_v2.py'));self.assertEqual(coreold,corenew)
        old=funcs((TASK/'local_f0_restore_operation_steps_resource_mount_v2.py').read_bytes());new=funcs((TASK/'local_f0_restore_operation_steps_bound_evidence_v3.py').read_bytes());self.assertEqual(set(new)-set(old),{'bound_source_metadata','bound_diagnostic','bound_outcome'})
        for name in set(old)-{'bound_operation','verify_common_packet'}:self.assertEqual(old[name],new[name],name)
        for prefix in ('prepare_local_f0_restore_plan','pin_local_f0_restore_plan_20261119'):
            old=funcs((TASK/(prefix+'_resource_mount_v2.py')).read_text());new=funcs((TASK/(prefix+'_bound_evidence_v3.py')).read_text().replace('_bound_evidence_v3.py','_resource_mount_v2.py'))
            for name in set(old)-({'validate_filesystem'} if prefix.startswith('pin') else set()):self.assertEqual(old[name],new[name],name)
        v=json.loads((R/'context/reconciliation/local-f0-restore-bound-evidence-v3-source-validation.json').read_bytes());self.assertEqual(v['independent_bound_evidence_review'],{'decision':'PENDING'});actual={p.relative_to(R).as_posix():hashlib.sha256(p.read_bytes()).hexdigest() for p in (R/v['source_root']).rglob('*') if p.is_file()};self.assertEqual(v['archive_files_sha256'],actual)
        for name,h in v['all_five_sources_sha256'].items():self.assertEqual((TASK/name).read_bytes(),(R/v['source_root']/(name+'.txt')).read_bytes());self.assertEqual(hashlib.sha256((TASK/name).read_bytes()).hexdigest(),h)

if __name__ == '__main__':
    unittest.main(verbosity=2)
