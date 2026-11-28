"""Offline regression tests for the exact known-work owner and pipe framing."""

from contextlib import nullcontext
from copy import deepcopy
import json
import os
from pathlib import Path
import re
import subprocess
import sys
from tempfile import TemporaryDirectory
import time
from types import SimpleNamespace
import unittest
from unittest.mock import Mock, patch

import node_session
import run


ROOT = Path(os.environ.get("WA_KNOWN_WORK_TEST_ROOT", "/workspace/Workin-Ants-Phase0-cloud"))
LOCAL = r'''
import json, sys, time
mode = sys.argv[1]
if mode == 'entry':
    print(json.dumps({'schema':'workinants.p0d-known-work-node.v1','phase':'ENTRY','sequence':0,'status':'STOPPED',
                      'code':'DRIVER_IDENTITY','pools_closed':True,'outcome_unconfirmed':False}), flush=True)
    sys.exit(1)
outcomes = {'SOURCE':'created','SCHEDULE':'scheduled','REPLAY':'already_scheduled','CLAIM':'claimed',
            'LIVE_RECLAIM':'unavailable','RENEW':'renewed','COPIED_HASH_RENEW':'unavailable',
            'RECLAIM':'claimed','STALE_RENEW':'unavailable'}
leases = {'CLAIM':(1,18000),'RENEW':(1,26000),'RECLAIM':(2,18000)}
for index, line in enumerate(sys.stdin):
    data = json.loads(line)
    phase = data['phase']
    value = {'schema':'workinants.p0d-known-work-node.v1','phase':phase,'sequence':index,'pools_closed':True}
    if mode == 'hang':
        time.sleep(30)
    if mode == 'stop' and phase == 'SOURCE':
        value.update(status='STOPPED',code='OWNER_COMMIT_UNCONFIRMED',outcome_unconfirmed=True)
        print(json.dumps(value), flush=True)
        sys.exit(1)
    if phase == 'INIT':
        value['status'] = 'READY'
    elif phase == 'FINISH':
        assert sys.stdin.read() == ''
        value.update(status='PASS',assertion_promotions=0)
        print(json.dumps(value), flush=True)
        sys.exit(0)
    else:
        lease = None
        if phase in leases:
            fence,offset = leases[phase]
            lease = {'fence':fence,'deadline_ms':data['server_ms']+offset,'lease_digest_sha256':'d'*64}
        value.update(status='PHASE_PASS',outcome=outcomes[phase],lease=lease)
    if mode == 'stderr':
        print('unretained fixture diagnostic', file=sys.stderr, flush=True)
    if mode == 'blank':
        print('', flush=True)
    print(json.dumps(value) + ('\r' if mode == 'crlf' else '\t' if mode == 'tab' else ''), flush=True)
    print('WA_P0D_WORK_ACK|'+phase, flush=True)
'''


class Offline(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.smoke = run.load_smoke(ROOT)
        cls.renewal, cls.modules = cls.smoke.mechanism()
        cls.S = cls.modules[0].S
        cls.assets = {}
        _, _, cls.validator = run.capture_child(ROOT, cls.assets, cls.S)
        cls.bridge = node_session.session_type(cls.S.pinned(ROOT, node_session.APP_PIPE, node_session.APP_PIPE_SHA),
                                               ROOT, cls.S, cls.validator)
        cls.Owner = run.owner_type(ROOT, cls.smoke, cls.renewal, cls.modules, cls.validator)

    def model(self, mode):
        args_seen = []
        owner = SimpleNamespace(resources=SimpleNamespace(cid="c" * 64), program=SimpleNamespace(
            all_secrets=["f" * 64], _required_safety_first_exception=Mock()), report={"stage": "MODELED"})

        def popen(args, **options):
            args_seen.append(args)
            self.assertEqual(args, ["exec", "-i", "--user", "65534:65534", owner.resources.cid, "/usr/bin/env", "-i",
                                   node_session.NODE, f"{node_session.REMOTE}/{node_session.ENTRY}", node_session.DRIVER])
            return subprocess.Popen([sys.executable, "-I", "-c", LOCAL, mode], **options)

        owner.transport = SimpleNamespace(unknown=False, io=SimpleNamespace(Popen=popen))
        owner.docker = SimpleNamespace(argv=lambda *args: list(args), remote_unknown=False)
        owner.check_socket = Mock()

        def sticky():
            owner.transport.unknown = owner.docker.remote_unknown = True

        owner.sticky = sticky
        return owner, args_seen

    def start(self, mode):
        owner, argv = self.model(mode)
        bridge = self.bridge(owner)

        def cleanup():
            try:
                bridge.terminate_unconfirmed()
            except BaseException:
                pass

        self.addCleanup(cleanup)
        self.assertEqual(len(argv), 1)
        return bridge, owner

    def test_identity_pinned_phase_acks_and_final_eof(self):
        bridge, owner = self.start("pass")
        for phase in run.PHASES:
            server = 1770000009000 if phase in self.validator.CLOCK_OFFSETS else None
            payload = b'{"phase":"INIT"}\n' if phase == "INIT" else self.validator.phase_message(phase, server)
            value = bridge.advance(phase, payload, server)
            self.assertEqual(value["phase"], phase)
        self.assertTrue(bridge.closed)
        self.assertEqual(bridge.process.poll(), 0)
        self.assertFalse(bridge.readers)
        self.assertFalse(owner.transport.unknown)

    def test_actual_exit_one_preserves_closed_typed_receipt(self):
        bridge, owner = self.start("stop")
        bridge.advance("INIT", b'{"phase":"INIT"}\n')
        value = bridge.advance("SOURCE", self.validator.phase_message("SOURCE"))
        self.assertEqual(value["code"], "OWNER_COMMIT_UNCONFIRMED")
        self.assertTrue(value["outcome_unconfirmed"])
        self.assertTrue(bridge.closed)
        pump_advance = Mock(return_value=value)
        runner = self.Owner.__new__(self.Owner)
        runner.report = {"stage": "MODELED", "known_work": {"phases": {"SOURCE": {}}}}
        runner.program = SimpleNamespace(save=Mock(), write_safe=Mock(return_value={"sha256": "b" * 64}),
                                         _required_safety_first_exception=Mock())
        runner.transport, runner.docker = owner.transport, owner.docker
        runner.closed = Mock(return_value=nullcontext())
        with self.assertRaisesRegex(self.S.Held, run.STOP):
            runner.invoke(SimpleNamespace(advance=pump_advance), "SOURCE", b"{}\n")
        self.assertTrue(owner.transport.unknown)
        self.assertTrue(owner.docker.remote_unknown)
        self.assertEqual(runner.report["known_work"]["phases"]["SOURCE"]["status"], "CHILD_TERMINAL_STOP")
        self.assertIs(runner.program.write_safe.call_args.args[1], value)

    def test_pre_init_closed_entry_diagnosis(self):
        bridge, owner = self.start("entry")
        self.assertEqual(bridge.process.wait(timeout=2), 1)
        result = bridge.advance("INIT", b'{"phase":"INIT"}\n')
        self.assertEqual((result["phase"], result["code"]), ("ENTRY", "DRIVER_IDENTITY"))
        self.assertTrue(bridge.closed)
        self.assertFalse(owner.transport.unknown)

    def test_blank_record_stderr_and_nonprintable_ascii_fail_sticky(self):
        for mode in ("blank", "stderr", "crlf", "tab"):
            with self.subTest(mode=mode):
                bridge, owner = self.start(mode)
                with self.assertRaisesRegex(RuntimeError, node_session.BRIDGE):
                    bridge.advance("INIT", b'{"phase":"INIT"}\n')
                self.assertTrue(owner.transport.unknown)
                self.assertTrue(all(pipe.closed for pipe in (bridge.process.stdin, bridge.process.stdout, bridge.process.stderr)))

    def test_persistable_filenames_and_unacknowledged_terminal_pass(self):
        for phase in run.PHASES:
            for kind in ("node", "readback", "observation"):
                self.assertTrue(re.fullmatch(r"[a-z0-9-]{1,80}\.json", run.phase_file(phase, kind)))
        runner = self.Owner.__new__(self.Owner)
        runner.report = {"stage": "MODELED", "known_work": {"phases": {"FINISH": {}}}}
        runner.program = SimpleNamespace(save=Mock(), write_safe=Mock())
        runner.closed = Mock(return_value=nullcontext())
        runner.invoke(SimpleNamespace(advance=Mock(return_value={"status": "PASS"})), "FINISH", b"{}\n")
        self.assertEqual(runner.report["known_work"]["phases"]["FINISH"]["status"], "CHILD_TERMINAL_PASS_PENDING_OBSERVATION")

    def test_absolute_deadline_aborts_exchange_and_observer(self):
        with patch.object(node_session, "SESSION_SECONDS", 0.12):
            bridge, owner = self.start("hang")
        start = time.monotonic()
        with self.assertRaisesRegex(RuntimeError, node_session.DEADLINE):
            bridge.advance("INIT", b'{"phase":"INIT"}\n')
        self.assertLess(time.monotonic() - start, 2)
        self.assertTrue(owner.transport.unknown)
        self.assertIsNotNone(bridge.process.poll())
        runner = self.Owner.__new__(self.Owner)
        runner.active_node = bridge
        with self.assertRaisesRegex(RuntimeError, node_session.DEADLINE):
            runner.exact_container_exec("never-dispatched", timeout=30)

    def test_changed_full42_requires_exact_count_and_hash_delta(self):
        fixture = json.loads(self.assets[run.APP_FIXTURE])
        tables = fixture["setup_expected_counts"]
        empty = {name: {"count": 0, "rows_sha256": self.S.sha(b"[]")} for name in tables}
        run.full42(empty, tables, self.S)
        run.compare42(empty, None, "UNBORN", self.S)
        seed = deepcopy(empty)
        for name, delta in run.SEED_DELTA.items():
            seed[name] = {"count": delta, "rows_sha256": "a" * 64}
        run.compare42(seed, empty, "SEEDED", self.S)
        run.compare42(seed, seed, "INIT", self.S)
        source = deepcopy(seed)
        for name, delta in run.CHECKPOINT_DELTAS["SOURCE"].items():
            source[name] = {"count": delta, "rows_sha256": "b" * 64}
        run.compare42(source, seed, "SOURCE", self.S)
        for name, value in (("app.users", {"count": 2, "rows_sha256": "c" * 64}),
                            ("platform.runtime_outbox_message", {"count": 1, "rows_sha256": "b" * 64})):
            drift = deepcopy(source)
            drift[name] = value
            with self.assertRaisesRegex(self.S.Held, run.STATE):
                run.compare42(drift, seed, "SOURCE", self.S)

    def test_pinned_smoke_load_accepts_cold_atime_change(self):
        with TemporaryDirectory() as directory:
            root = Path(directory).resolve()
            path = root / run.SMOKE
            path.parent.mkdir(parents=True)
            path.write_bytes((ROOT / run.SMOKE).read_bytes())
            os.utime(path, ns=(1000, time.time_ns()))
            self.assertEqual(run.load_smoke(root).ENTRY_SHA, run.ENTRY_SHA)
    def test_missing_global_proof_latches_uncertainty(self):
        runner = self.Owner.__new__(self.Owner)
        runner.report = {"known_work": {"closure_probes": {}}}
        runner.program = SimpleNamespace(_RequiredSafetyBoundary=lambda *args: nullcontext())
        runner.name = "no_real_target"
        runner.sticky = Mock()
        with self.assertRaisesRegex(self.S.Held, run.CLOSE):
            with runner.closed("MODELED"):
                pass
        runner.sticky.assert_called_once()
        self.assertIs(runner.report["known_work"]["closure_probes"]["MODELED"], False)

    def test_closed_projection_persists_before_expected_delta_refusal(self):
        fixture = json.loads(self.assets[run.APP_FIXTURE])
        tables = fixture["setup_expected_counts"]
        empty = {name: {"count": 0, "rows_sha256": self.S.sha(b"[]")} for name in tables}
        drift = deepcopy(empty)
        drift["app.customer_profiles"] = {"count": 1, "rows_sha256": "b" * 64}
        projection = {**dict.fromkeys(run.WORK_COUNT_FIELDS, 0), "work": None, "server_ms": 1770000000000,
                      "source_count": 0, "source_distinct_xids": 0, "source_xid": None}
        grants = {"count": 0, "distinct_hashes": 0, "grants": []}
        runner = self.Owner.__new__(self.Owner)
        runner.report = {"known_work": {"checkpoints": {}}}
        runner.program = SimpleNamespace(save=Mock(), write_safe=Mock())
        runner.closed = Mock(side_effect=lambda *args: nullcontext())
        runner.closed_record = Mock(side_effect=[drift, projection, grants])
        with self.assertRaisesRegex(self.S.Held, run.STATE):
            runner.observe("INIT", tables, {"full42": empty, "scope": projection, "grants": grants}, {})
        runner.program.write_safe.assert_called_once()
        path, report = runner.program.write_safe.call_args.args
        self.assertEqual(path, "known-work-init-readback.json")
        self.assertEqual(report["scope"], projection)
        self.assertEqual(report["grants"], grants)
        self.assertEqual(report["full42"], drift)

    def test_reclaim_reprobes_server_expiration_and_live_reserve(self):
        runner = self.Owner.__new__(self.Owner)
        runner.stage = Mock()
        runner.closed = Mock(side_effect=lambda *args: nullcontext())
        runner.active_node = SimpleNamespace(limit=Mock())
        now = 1770000000000
        scope = {**dict.fromkeys(run.WORK_COUNT_FIELDS, 0), "work_total": 1, "server_ms": now, "source_count": 6,
                 "source_distinct_xids": 1, "source_xid": "11", "work": {
                     "count": 1, "identity_exact": True, "state": "leased", "fence": 1, "attempt": 1, "deadline_ms": now + 1000,
                     "lease_digest_sha256": "a" * 64, "mutation_xid": "12", "row_sha256": "b" * 64,
                     "without_deadline_xid_sha256": "c" * 64, "identity_sha256": "d" * 64}}
        runner.closed_record = Mock(side_effect=[scope, {**scope, "server_ms": now + 1250}])
        with patch.object(run.time, "sleep") as sleep:
            self.assertEqual(runner.clock("RECLAIM", {"scope": scope}), (now, now + 1250))
        sleep.assert_called_once_with(1.25)
        runner.active_node.limit.assert_called_once_with(2.25)
        runner.closed_record = Mock(return_value=scope)
        with self.assertRaisesRegex(self.S.Held, run.CLOCK):
            runner.clock("RENEW", {"scope": scope})


if __name__ == "__main__":
    unittest.main()
