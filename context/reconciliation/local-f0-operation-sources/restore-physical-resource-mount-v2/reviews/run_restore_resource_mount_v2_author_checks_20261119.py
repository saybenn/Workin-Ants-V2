"""Offline source author checks; all real process/network and old-root writes forbidden."""
import contextlib
import datetime
import hashlib
import io
import json
import os
from pathlib import Path
import runpy
import sys
import time
import types
import unittest

sys.dont_write_bytecode = True
TASK = Path(__file__).resolve().parent
ROOT = TASK / 'workinants-correction-pass'
DENIALS = []


def audit(event, args):
    if event in ('subprocess.Popen', 'os.system', 'os.spawn', 'socket.connect', 'socket.bind', 'socket.getaddrinfo'):
        DENIALS.append(event)
        raise RuntimeError('ACTUAL_PROCESS_NETWORK_FORBIDDEN')
    if event == 'open' and isinstance(args[0], (str, bytes, os.PathLike)):
        path = Path(args[0]).absolute()
        mode, flags = args[1], args[2]
        writing = (isinstance(mode, str) and any(c in mode for c in 'wax+')) or (
            isinstance(flags, int) and flags & (os.O_WRONLY | os.O_RDWR | os.O_CREAT | os.O_TRUNC | os.O_APPEND))
        if writing and path.is_relative_to(ROOT):
            DENIALS.append('ACTUAL_ROOT_WRITE')
            raise RuntimeError('ACTUAL_ROOT_WRITE_FORBIDDEN')


def main():
    sys.addaudithook(audit)
    suites = (
        ('check_local_f0_restore_operation_resource_mount_v2.py', 64),
        ('check_restore_resource_mount_v2_resources_20261119.py', 10),
        ('check_restore_resource_mount_v2_source_gates_20261119.py', 4),
        ('check_restore_resource_mount_v2_safety_composed_20261119.py', 23))
    results = []
    for filename, expected in suites:
        namespace = runpy.run_path(str(TASK / filename), run_name='_offline_restore_resource_author')
        module = types.ModuleType('_offline_restore_resource_author')
        module.__dict__.update(namespace)
        suite = unittest.defaultTestLoader.loadTestsFromModule(module)
        log = io.StringIO()
        output = io.StringIO()
        started = time.monotonic()
        with contextlib.redirect_stdout(output), contextlib.redirect_stderr(output):
            result = unittest.TextTestRunner(stream=log, verbosity=2).run(suite)
        entry = {'suite': filename, 'tests': result.testsRun, 'expected_tests': expected,
                 'seconds': round(time.monotonic() - started, 3),
                 'passed': result.wasSuccessful() and result.testsRun == expected,
                 'failures': len(result.failures), 'errors': len(result.errors),
                 'test_output': log.getvalue(),
                 'safe_output_sha256': hashlib.sha256(output.getvalue().encode()).hexdigest()}
        results.append(entry)
        print(json.dumps({k: v for k, v in entry.items() if k != 'test_output'}), flush=True)
    record = {'schema': 'workinants.restore-resource-mount-v2-author-offline-checks.v1',
              'author': '/root/install_outer_review',
              'recorded_at_utc': datetime.datetime.now(datetime.timezone.utc).isoformat(),
              'results': results, 'tests': sum(r['tests'] for r in results), 'audit_denials': DENIALS,
              'status': 'PASS' if all(r['passed'] for r in results) and not DENIALS else 'FAIL',
              'actual_process_database_shell_kernel_network_Git': 'FORBIDDEN_NOT_RUN',
              'actual_ROOT_write_or_metadata_mutations_during_tests': False,
              'synthetic_inputs_only': True}
    suffix = sys.argv[1] if len(sys.argv) > 1 else 'run1'
    assert suffix.replace('_', '').isalnum()
    destination = TASK / ('restore_resource_mount_v2_author_checks_' + suffix + '_20261119.json')
    with destination.open('x', encoding='utf-8', newline='\n') as handle:
        handle.write(json.dumps(record, indent=2, ensure_ascii=True) + '\n')
    print(json.dumps({'path': str(destination), 'sha256': hashlib.sha256(destination.read_bytes()).hexdigest(),
                      'status': record['status'], 'tests': record['tests']}), flush=True)
    return 0 if record['status'] == 'PASS' else 1


if __name__ == '__main__':
    raise SystemExit(main())
