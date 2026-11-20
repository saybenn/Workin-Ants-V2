"""Restore resource composition; all external process/network boundaries mocked."""
import ast
import copy
from contextlib import redirect_stdout
import hashlib
import io
import json
from pathlib import Path
import runpy
import subprocess
import tempfile
import types
import unittest
from unittest.mock import Mock, patch

TASK = Path(__file__).resolve().parent
BASE = runpy.run_path(str(TASK / 'check_local_f0_restore_operation_resource_mount_v2.py'))
ROOT = BASE['ROOT']
CANARY = BASE['CANARY']


class RestoreResourceMountV2Tests(unittest.TestCase):
    setUp = BASE['RestoreOperationTests'].setUp
    valid_resource = BASE['RestoreOperationTests'].valid_resource

    def test_default_API_omission_and_old_inspector_only_mutant(self):
        old = TASK / 'local_f0_restore_operation_steps_safety_sql_v1.py'
        node = next(n for n in ast.parse(old.read_bytes()).body if isinstance(n, ast.FunctionDef) and n.name == 'inspect_restore')
        for kind, count in (('source', 2), ('target', 1)):
            self.n = BASE['namespace']()
            name, value, _ = self.valid_resource(kind)
            value['State']['Running'] = False
            command = Mock(side_effect=AssertionError('NO_NONRUNNING_EXEC'))
            self.n['docker'] = command
            self.assertEqual(len(value['Mounts']), count)
            self.n['inspect_restore'](name, kind, running=False)
            self.assertEqual(self.n['report']['restore_resource_inspection_checks'][-1]['mount_counts']['tmpfs_api'], 0)
            exec(compile(ast.Module(body=[node], type_ignores=[]), str(old), 'exec'), self.n)
            with self.assertRaises(self.n['Stop']) as stopped:
                self.n['inspect_restore'](name, kind, running=False)
            self.assertEqual(stopped.exception.code, 'RESTORE_MOUNT_SET')
            command.assert_not_called()

    def test_each_profile_optional_API_and_strict_host_tmpfs(self):
        for kind in ('source', 'target'):
            for optional in (False, True):
                for mode in ('mode=0700', 'mode=700'):
                    name, value, _ = self.valid_resource(kind)
                    value['HostConfig']['Tmpfs']['/run/wa-secrets'] = 'rw,nosuid,noexec,nodev,' + mode
                    if optional:
                        value['Mounts'].append({'Type': 'tmpfs', 'Destination': '/run/wa-secrets', 'RW': True})
                    self.n['inspect_restore'](name, kind)
                    self.assertTrue(self.n['report']['restore_resource_kernel_checks'][-1]['confirmed'])
            for options in ('', None, True, 'rw,noexec,nosuid,mode=700',
                            'rw,noexec,nosuid,nodev,mode=777', 'rw,noexec,nosuid,nodev,mode=700,',
                            'rw,noexec,nosuid,nodev,mode=700,rw', 'rw,noexec,nosuid,nodev,mode=700,mode=0700',
                            'rw,noexec,nosuid,nodev,mode=700,ro', 'rw,noexec,nosuid,nodev,mode=700,exec',
                            'rw,noexec,nosuid,nodev,mode=700,suid', 'rw,noexec,nosuid,nodev,mode=700,dev'):
                name, value, _ = self.valid_resource(kind)
                value['State']['Running'] = False
                value['HostConfig']['Tmpfs']['/run/wa-secrets'] = options
                self.n['docker'] = Mock(side_effect=AssertionError('NO_BAD_CONFIG_EXEC'))
                with self.subTest(kind=kind, options=options), self.assertRaises(self.n['Stop']):
                    self.n['inspect_restore'](name, kind, running=False)
                self.n['docker'].assert_not_called()

    def test_staging_and_stopped_source_never_get_secret_probe(self):
        for tmpfs in (None, {}):
            name, value, _ = self.valid_resource('staging')
            value['HostConfig']['Tmpfs'] = tmpfs
            self.n['docker'] = Mock(side_effect=AssertionError('STAGING_HAS_NO_SECRET_PROBE'))
            self.n['inspect_restore'](name, 'staging')
            self.n['docker'].assert_not_called()
        for tmpfs in (False, '', [], {'/run/wa-secrets': 'rw,nosuid,noexec,nodev,mode=700'}):
            name, value, _ = self.valid_resource('staging')
            value['HostConfig']['Tmpfs'] = tmpfs
            with self.assertRaises(self.n['Stop']): self.n['inspect_restore'](name, 'staging')
        name, value, _ = self.valid_resource('source')
        value['State']['Running'] = False
        self.n['docker'] = Mock(side_effect=AssertionError('STOPPED_SOURCE_EXEC_FORBIDDEN'))
        self.n['inspect_restore'](name, 'source', running=False)
        self.n['docker'].assert_not_called()

    def test_closed_profile_identity_and_mount_purposes(self):
        for kind in ('source', 'staging', 'target'):
            for change in ('unknown-kind', 'foreign-name', 'foreign-cid', 'duplicate-data', 'extra-bind',
                           'bad-tmpfs', 'links', 'wrong-volume-name'):
                name, value, volume = self.valid_resource(kind)
                value['State']['Running'] = False
                actual_kind = kind
                if change == 'unknown-kind': actual_kind = 'foreign'
                elif change == 'foreign-name': name = 'unrelated'
                elif change == 'foreign-cid': value['Id'] = 'f' * 64
                elif change == 'duplicate-data': value['Mounts'].append(copy.deepcopy(value['Mounts'][0]))
                elif change == 'extra-bind': value['Mounts'].append({'Type': 'bind', 'Source': CANARY, 'Destination': '/outside', 'RW': False})
                elif change == 'bad-tmpfs': value['Mounts'].append({'Type': 'tmpfs', 'Destination': '/run/wa-secrets', 'RW': False})
                elif change == 'links': value['HostConfig']['Links'] = ['/foreign:/foreign']
                else: volume['Name'] = 'unrelated'
                self.n['docker'] = Mock(side_effect=AssertionError('BAD_PROFILE_EXEC_FORBIDDEN'))
                with self.subTest(kind=kind, change=change), self.assertRaises(self.n['Stop']):
                    self.n['inspect_restore'](name, actual_kind, running=False)
                self.n['docker'].assert_not_called()
                self.assertNotIn(CANARY, json.dumps(self.n['report']))

    def kernel_model(self, args, input=None, timeout=60, rows=None, stat='directory:700:0:0'):
        self.assertEqual(args[-3:], ['sh', '-ceu', self.n['RESTORE_SECRET_TMPFS_SCRIPT']])
        self.assertIn(args[2], (self.n['created_containers']['source'], self.n['created_containers']['target']))
        self.assertIsNone(input)
        self.assertEqual(timeout, 30)
        script = args[-1]
        for fixed in ('done < /proc/mounts', '[ "$count" -eq 1 ]', 'set -f', 'export LC_ALL=C',
                      "stat -c '%F:%a:%u:%g' -- /run/wa-secrets", "'directory:700:0:0'", 'ro|exec|suid|dev'):
            self.assertIn(fixed, script)
        for flag in ('rw', 'noexec', 'nosuid', 'nodev'):
            self.assertIn('[ "$seen_' + flag + '" -eq 1 ]', script)
        rows = rows if rows is not None else [('/run/wa-secrets', 'tmpfs', 'rw,nosuid,nodev,noexec,relatime,size=64m,mode=700')]
        chosen = [r for r in rows if r[0] == '/run/wa-secrets']
        good = len(chosen) == 1
        if good:
            _, filesystem, options = chosen[0]
            tokens = options.split(',')
            good = filesystem == 'tmpfs' and all(tokens.count(f) == 1 for f in ('rw', 'noexec', 'nosuid', 'nodev'))
            good = good and all(tokens) and not any(f in tokens for f in ('ro', 'exec', 'suid', 'dev'))
        good = good and stat == 'directory:700:0:0'
        return types.SimpleNamespace(returncode=0 if good else 24,
            stdout=self.n['RESTORE_SECRET_TMPFS_TOKEN'] + '\n' if good else '', stderr='')

    def test_fixed_kernel_source_and_model_vectors_for_both_database_targets(self):
        bad_rows = [[], [('/elsewhere', 'tmpfs', 'rw,noexec,nosuid,nodev')],
                    [('/run/wa-secrets', 'ext4', 'rw,noexec,nosuid,nodev')]]
        for options in ('rw,nosuid,nodev', 'rw,noexec,nodev', 'rw,noexec,nosuid', 'ro,noexec,nosuid,nodev',
                        'rw,noexec,nosuid,nodev,exec', 'rw,noexec,nosuid,nodev,suid',
                        'rw,noexec,nosuid,nodev,dev', 'rw,rw,noexec,nosuid,nodev', 'rw,,noexec,nosuid,nodev'):
            bad_rows.append([('/run/wa-secrets', 'tmpfs', options)])
        bad_rows.append([('/run/wa-secrets', 'tmpfs', 'rw,noexec,nosuid,nodev')] * 2)
        for kind in ('source', 'target'):
            name, _, _ = self.valid_resource(kind)
            self.n['docker'] = self.kernel_model
            self.n['inspect_restore'](name, kind)
            for rows in bad_rows:
                self.n['docker'] = lambda args, input=None, timeout=60, rows=rows: self.kernel_model(args, input, timeout, rows)
                with self.assertRaises(self.n['Stop']): self.n['inspect_restore'](name, kind)
            for stat in ('regular file:700:0:0', 'symbolic link:700:0:0', 'directory:777:0:0',
                         'directory:700:999:0', 'directory:700:0:999', CANARY):
                self.n['docker'] = lambda args, input=None, timeout=60, stat=stat: self.kernel_model(args, input, timeout, stat=stat)
                with self.assertRaises(self.n['Stop']): self.n['inspect_restore'](name, kind)
            self.assertNotIn(CANARY, json.dumps(self.n['report']))

    def test_strict_kernel_transport_result_and_sanitized_failures(self):
        for kind in ('source', 'target'):
            name, _, _ = self.valid_resource(kind)
            n = self.n; token = n['RESTORE_SECRET_TMPFS_TOKEN'] + '\n'
            bad = [types.SimpleNamespace(returncode=c, stdout=token, stderr='') for c in (False, True, 0.0, 3)]
            bad += [types.SimpleNamespace(returncode=0, stdout=s, stderr='') for s in (token.rstrip(), token + '\n', CANARY, token.encode())]
            bad += [types.SimpleNamespace(returncode=0, stdout=token, stderr=s) for s in (CANARY, None)]
            bad += [subprocess.TimeoutExpired(CANARY, 30, output=CANARY, stderr=CANARY), UnicodeError(CANARY), RuntimeError(CANARY)]
            for value in bad:
                n['docker'] = Mock(side_effect=value) if isinstance(value, BaseException) else Mock(return_value=value)
                with self.assertRaises(n['Stop']) as stopped: n['inspect_restore'](name, kind)
                self.assertEqual(stopped.exception.code, 'RESTORE_SECRET_TMPFS_KERNEL_UNCONFIRMED')
                self.assertFalse(n['report']['restore_resource_kernel_checks'][-1]['confirmed'])
                self.assertNotIn(CANARY, json.dumps(n['report']))
            n['docker'] = Mock()
            with self.assertRaises(n['Stop']): n['verify_running_restore_secret_tmpfs'](name, kind, 'f' * 64)
            n['docker'].assert_not_called()

    def creation_world(self, bad_kind=None):
        temp = tempfile.TemporaryDirectory(prefix='offline-restore-resource-v2-', dir=TASK)
        self.addCleanup(temp.cleanup)
        n = BASE['namespace'](); self.n = n
        out = Path(temp.name) / 'out'; out.mkdir()
        n.update(OUT=out, PRIVATE=out / 'private', ARCHIVE=out / 'private/restore01-base.tar',
            created_containers={}, created_volumes={}, attempted_containers=set(), attempted_volumes=set(),
            passwords={}, all_secrets=[], secret_paths=[], bootstrap_attempted=set(), bootstrapped=set(),
            finalization_attempted=set(), finalized=set(), save=lambda: None, event=lambda *a, **k: None)
        n['report']['image'] = {'image_id': n['IMAGE'].split('@')[1]}
        n['report']['restore'].update(postgres_os_identity=[999, 998], source_system_identifier_sha256='9' * 64)
        containers = {}; volumes = {}; trace = []
        ids = {'source': 'a' * 64, 'stage': 'b' * 64, 'target': 'c' * 64}
        labels = {'workinants.rehearsal': n['LABEL'], 'workinants.rehearsal.run': n['RUN_ID']}

        def command(args, input=None, timeout=60):
            if args[0] == 'powershell.exe':
                trace.append('DACL'); return types.SimpleNamespace(returncode=0, stdout='OWNER_ONLY_VERIFIED\n', stderr='')
            self.assertEqual(args[:3], ['docker', '--context', 'desktop-linux'])
            p = args[3:]; code = 0; stdout = ''
            if p == ['container', 'ls', '-a', '--format', '{{.Names}}']: stdout = '\n'.join(containers)
            elif p == ['volume', 'ls', '--format', '{{.Name}}']: stdout = '\n'.join(volumes)
            elif p[:2] == ['volume', 'create']:
                name = p[-1]; volumes[name] = {'Name': name, 'CreatedAt': 'TIME-' + name, 'Labels': labels, 'Driver': 'local', 'Options': {}, 'Scope': 'local'}
                trace.append('VOLUME:' + name)
            elif p[:2] == ['container', 'create']:
                name = p[p.index('--name') + 1]
                staging = name == 'stage'
                mount_strings = [p[i + 1] for i, x in enumerate(p) if x == '--mount']
                mounts = []
                for text in mount_strings:
                    items = dict(x.split('=', 1) for x in text.split(',') if '=' in x)
                    mount = {'Type': items['type'], 'Destination': items['dst'], 'RW': 'readonly' not in text.split(',')}
                    mount['Name' if items['type'] == 'volume' else 'Source'] = items['src']
                    mounts.append(mount)
                tmpfs = {} if staging else {'/run/wa-secrets': 'rw,nosuid,noexec,nodev,mode=0700'}
                containers[name] = {'Id': ids[name], 'Name': '/' + name, 'Config': {'Image': n['IMAGE'], 'Labels': labels},
                    'Image': n['report']['image']['image_id'], 'Platform': 'linux', 'State': {'Running': False},
                    'HostConfig': {'NetworkMode': 'none', 'PortBindings': {}, 'Privileged': False, 'PidMode': '',
                        'IpcMode': 'private', 'Devices': [], 'CapAdd': [], 'Links': None, 'Tmpfs': tmpfs},
                    'NetworkSettings': {'Ports': {}}, 'Mounts': mounts}
                trace.append('CREATE:' + name)
            elif p[:2] == ['container', 'inspect']:
                name = p[2]; code = 0 if name in containers else 1
                if code == 0:
                    value = containers[name]; trace.append(('RUNNING:' if value['State']['Running'] else 'NOT_RUNNING:') + name)
                    stdout = json.dumps([value])
            elif p[:2] == ['volume', 'inspect']:
                code = 0 if p[2] in volumes else 1
                if code == 0: stdout = json.dumps([volumes[p[2]]])
            elif p[:2] == ['container', 'start']:
                name = next(k for k, v in containers.items() if v['Id'] == p[2]); containers[name]['State']['Running'] = True
                trace.append('START:' + name)
            elif p[:2] == ['container', 'stop']:
                self.assertEqual(p[2:4], ['--time', '30']); name = next(k for k, v in containers.items() if v['Id'] == p[4])
                containers[name]['State']['Running'] = False; trace.append('STOP:' + name)
            elif p[:3] == ['container', 'rm', '-f']:
                name = next(k for k, v in containers.items() if v['Id'] == p[3]); containers.pop(name); trace.append('REMOVE:' + name)
            elif p[:2] == ['volume', 'rm']: volumes.pop(p[2]); trace.append('REMOVE_VOLUME:' + p[2])
            elif p[:2] == ['exec', '-i'] and p[-1] == n['RESTORE_SECRET_TMPFS_SCRIPT']:
                self.assertEqual(p[3:5], ['sh', '-ceu']); self.assertIsNone(input); self.assertEqual(timeout, 30)
                name = next(k for k, v in containers.items() if v['Id'] == p[2]); self.assertIn(name, ('source', 'target'))
                trace.append('KERNEL:' + name); code = 24 if name == bad_kind else 0
                stdout = '' if code else n['RESTORE_SECRET_TMPFS_TOKEN'] + '\n'
            elif p[0] == 'exec' and p[1] in ids.values():
                name = next(k for k, v in ids.items() if v == p[1]); tool = p[2]
                if tool == 'pg_isready': trace.append('READY:' + name)
                elif tool == 'find': trace.append('EMPTY_DATA')
                elif tool == 'sha256sum': stdout = hashlib.sha256(n['ARCHIVE'].read_bytes()).hexdigest() + '  /run/restore01-base.tar\n'; trace.append('ARCHIVE_HASH')
                elif tool == 'tar': trace.append('EXTRACT')
                elif tool == 'pg_verifybackup': trace.append('VERIFY_BACKUP')
                elif tool == 'sh':
                    self.assertIn('chown -R 999:998', p[-1]); self.assertIn('chmod 700', p[-1]); trace.append('PGDATA_READY')
                else: raise AssertionError('UNMODELED_TOOL')
            elif p[:2] == ['exec', '-i'] and p[2] in ids.values() and p[3:5] == ['sh', '-ceu']:
                name = next(k for k, v in ids.items() if v == p[2])
                if 'cat > /run/wa-secrets/pgpass' in p[-1]: trace.append('PGPASS:' + name); stdout = '600:0:0\n'
                elif 'pg_hba.conf' in p[-1]: self.assertEqual(name, 'stage'); trace.append('HBA_STAGE')
                else: raise AssertionError('UNMODELED_PRIVATE_WRITE')
            elif p[0] == 'exec' and 'psql' in p:
                self.assertIsInstance(input, str)
                if input.startswith('SELECT pg_read_file('): stdout = 't\n'; trace.append('VERIFY_HBA')
                elif input.startswith('SELECT jsonb_build_object('):
                    stdout = json.dumps({'version': 170011, 'safe': True, 'auth': 'scram-sha-256:postgres', 'primary': True, 'system_identifier_sha256': '9' * 64}) + '\n'; trace.append('ADMIN_IDENTITY')
                else: raise AssertionError('UNMODELED_SQL')
            else: raise AssertionError('UNMODELED_COMMAND_BOUNDARY')
            return types.SimpleNamespace(returncode=code, stdout=stdout, stderr='')

        n['command'] = command
        n['MANIFEST'] = {'packet_files_sha256': {path: hashlib.sha256((ROOT / path).read_bytes()).hexdigest() for path in n['HELPER_FILES']}}
        n['WORKER'] = n['load_reviewed_helper']('scripts/sql-review/run-worker-control-rehearsal.py')
        return n, trace, containers, volumes

    def source_created(self, bad_kind=None):
        n, trace, containers, volumes = self.creation_world(bad_kind)
        with patch.object(n['secrets'], 'token_hex', side_effect=[CANARY + str(i) for i in range(6)]): n['create_resources']()
        return n, trace, containers, volumes

    def test_actual_Core_source_order_and_exact_cleanup(self):
        n, trace, containers, volumes = self.source_created()
        self.assertLess(trace.index('NOT_RUNNING:source'), trace.index('START:source'))
        self.assertLess(trace.index('START:source'), trace.index('KERNEL:source'))
        self.assertLess(trace.index('KERNEL:source'), trace.index('READY:source'))
        self.assertLess(trace.index('READY:source'), trace.index('PGPASS:source'))
        self.assertEqual(len(containers['source']['Mounts']), 2)
        n['cleanup'](); self.assertFalse(containers); self.assertFalse(volumes); self.assertFalse(n['PRIVATE'].exists())

    def test_actual_stage_restore_has_separate_target_proof_and_PGDATA_checks(self):
        n, trace, containers, volumes = self.source_created()
        n['ARCHIVE'].write_bytes(BASE['archive_bytes'](n['source_text']('source-backup.pg_hba.conf')))
        n['secret_paths'].append(n['ARCHIVE'])
        metadata = n['validate_backup_archive'](n['ARCHIVE'])
        n['stage_restore'](metadata)
        self.assertLess(trace.index('STOP:source'), trace.index('CREATE:stage'))
        self.assertLess(trace.index('VERIFY_BACKUP'), trace.index('PGDATA_READY'))
        self.assertLess(trace.index('PGDATA_READY'), trace.index('HBA_STAGE'))
        self.assertLess(trace.index('REMOVE:stage'), trace.index('CREATE:target'))
        self.assertLess(trace.index('START:target'), trace.index('KERNEL:target'))
        self.assertLess(trace.index('KERNEL:target'), trace.index('PGPASS:target'))
        self.assertLess(trace.index('PGPASS:target'), trace.index('ADMIN_IDENTITY'))
        self.assertNotIn('KERNEL:stage', trace)
        self.assertEqual(len(containers['target']['Mounts']), 1)
        self.assertEqual([r['kind'] for r in n['report']['restore_resource_kernel_checks']], ['source', 'target'])
        n['cleanup'](); self.assertFalse(containers); self.assertFalse(volumes); self.assertFalse(n['PRIVATE'].exists())

    def test_actual_target_failure_cannot_reuse_source_proof_and_cleanup_keeps_primary(self):
        n, trace, containers, volumes = self.source_created(bad_kind='target')
        n['ARCHIVE'].write_bytes(BASE['archive_bytes'](n['source_text']('source-backup.pg_hba.conf')))
        n['secret_paths'].append(n['ARCHIVE'])
        metadata = n['validate_backup_archive'](n['ARCHIVE'])
        with self.assertRaises(n['Stop']) as stopped: n['stage_restore'](metadata)
        self.assertEqual(stopped.exception.code, 'RESTORE_SECRET_TMPFS_KERNEL_UNCONFIRMED')
        self.assertNotIn('PGPASS:target', trace); self.assertNotIn('ADMIN_IDENTITY', trace)
        records = n['report']['restore_resource_kernel_checks']
        self.assertTrue(records[0]['confirmed']); self.assertFalse(records[-1]['confirmed'])
        n['record_failure'](stopped.exception.stage, stopped.exception.code, primary=True)
        primary = copy.deepcopy(n['report']['primary_failure'])
        n['save'] = Mock(side_effect=OSError(CANARY))
        with self.assertRaises(n['Stop']): n['cleanup']()
        self.assertFalse(containers); self.assertFalse(volumes); self.assertFalse(n['PRIVATE'].exists())
        self.assertEqual(n['report']['primary_failure'], primary)
        self.assertFalse(n['evidence_is_complete']())
        self.assertNotIn(CANARY, json.dumps(n['report']))

    def test_actual_source_failure_stops_before_first_private_write_under_IO(self):
        n, trace, containers, volumes = self.creation_world(bad_kind='source')
        def save():
            if 'KERNEL:source' in trace: raise OSError(CANARY)
        n['save'] = save
        with patch.object(n['secrets'], 'token_hex', side_effect=[CANARY + str(i) for i in range(6)]), self.assertRaises(BaseException):
            n['create_resources']()
        self.assertNotIn('READY:source', trace); self.assertNotIn('PGPASS:source', trace)
        with self.assertRaises(n['Stop']): n['cleanup']()
        self.assertFalse(containers); self.assertFalse(volumes); self.assertFalse(n['PRIVATE'].exists())
        self.assertNotIn(CANARY, json.dumps(n['report']))


if __name__ == '__main__':
    unittest.main(verbosity=2)
