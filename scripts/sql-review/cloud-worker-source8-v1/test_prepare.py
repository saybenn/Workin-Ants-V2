"""Exercise only the published bytes, typed responses and effective Worker frames."""

import json
from pathlib import Path
import socket
import subprocess
import unittest
from unittest.mock import patch

import prepare


class WorkerSource8(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.root = prepare.ROOT
        cls.source = prepare.common(cls.root)
        cls.application = (cls.root / prepare.INITIAL).read_bytes()
        cls.fixture = cls.source.unique_json((cls.root / prepare.FIXTURE).read_bytes())
        cls.proof, cls.protocol = prepare.build()

    def test_immutable_packet_and_held_boundary(self):
        run = subprocess.run
        seen = []

        def git_only(args, **options):
            self.assertEqual(args, ["git", "-C", str(self.root), "cat-file", "--batch"])
            self.assertEqual(options["env"]["GIT_NO_LAZY_FETCH"], "1")
            seen.append(args)
            return run(args, **options)

        with patch.object(subprocess, "run", side_effect=git_only), patch.object(
            socket.socket, "connect", side_effect=AssertionError("NETWORK_FORBIDDEN"),
        ):
            reproduced, _ = prepare.build()
        self.assertEqual(reproduced, self.proof)
        self.assertEqual(len(seen), 4)
        self.assertEqual(len(self.proof["published_worker_files_sha256"]), 100)
        self.assertEqual(len(self.proof["sql_files_sha256"]), 40)
        self.assertEqual(len(self.proof["ordered_cases"]), 21)
        self.assertEqual(self.proof["runtime"], "NOT_RUN")
        self.assertEqual(self.proof["assertion_promotions"], 0)
        self.assertEqual(len(self.fixture["worker_acl_rows"]), 32)
        seam = self.proof["owning_transport_seam"]
        self.assertEqual(seam["previous_target_reuse"], "DENIED")
        self.assertEqual(seam["maximum_live_worker_sessions"], 2)
        self.assertEqual(seam["unknown_transport_or_backend_closure"], "HOLD_AND_CLEANUP")

    def test_guard_receipts_report_exact_effective_bodies(self):
        historic = self.source.module(self.root, prepare.PROTOCOL, (self.root / prepare.PROTOCOL).read_bytes())
        for case in self.fixture["cases"]:
            name = case["name"]
            if name not in self.proof["effective_guard_frames"]:
                continue
            with self.subTest(case=name):
                wanted = self.proof["effective_guard_frames"][name]
                stderr = self.stderr(name)
                rows = [json.dumps(row) if type(row) is dict else row for row in case["expected_records"]]
                original = historic.verdict(case, 3, rows, False, stderr, self.application.decode())
                effective = self.protocol.verdict(case, 3, rows, False, stderr, self.application.decode())
                old_hash = prepare.OLD_FRAME[0] if wanted["source"] == prepare.APPEND else prepare.TRACK_FRAME
                self.assertEqual(original["source_guard"]["source_body_sha256"], old_hash)
                self.assertEqual(effective["source_guard"], {
                    **original["source_guard"], "source_body_sha256": wanted["body_sha256"],
                })
                observed = self.protocol.operation_observation(
                    case, 3, rows, False, stderr, self.application.decode(),
                    result_received=True, client_exit_received=True,
                )
                self.assertEqual(observed["source_guard"], effective["source_guard"])

    def stderr(self, name, line=None):
        state, message, function = self.protocol.DIAGNOSTICS[name]
        raise_line = prepare.SOURCE_LINES[name] if line is None else line
        return (f"ERROR:  {state}: {message}\n"
                f"CONTEXT:  PL/pgSQL function platform_private.{function}() line {raise_line} at RAISE\n"
                "LOCATION:  exec_stmt_raise, pl_exec.c:3900\n")

    def test_mismatched_or_extra_diagnostics_remain_discarded(self):
        name = "nonnull-effect-relink-denied"
        valid = self.stderr(name)
        bad = [self.stderr(name, line=7), valid.replace("P0001", "42501"),
               valid.replace("runtime_transition", "track_binding"), valid + "extra-private-value\n"]
        for text in bad:
            with self.subTest(text=text):
                receipt = self.protocol.diagnostic(name, text, self.application.decode())
                self.assertFalse(receipt["matched"])
                self.assertIsNone(receipt["source_body_sha256"])
                self.assertEqual(receipt["classification"], "UNLISTED_DISCARDED")
                self.assertNotIn("extra-private-value", json.dumps(receipt))

    def test_altered_append_cannot_supply_effective_frame(self):
        native = self.source.unique_json((self.root / prepare.EXPECTED).read_bytes())
        append = (self.root / prepare.APPEND).read_bytes()
        mutated = append.replace(b"terminal work/regressive attempt", b"terminal work/regressive CASE", 1)
        self.assertNotEqual(mutated, append)
        with self.assertRaisesRegex(self.source.Held, "WORKER_EFFECTIVE_BODY_IDENTITY"):
            prepare.effective_protocol(self.source, self.protocol, self.application, mutated, native)

    def test_same_owner_cleanup_remains_required(self):
        steps = (self.root / self.source.STEPS).read_bytes()
        operation = (self.root / prepare.TWO_OWNER).read_bytes()
        muted = steps.replace(b"try:cleanup()", b"try:save()", 1)
        self.assertNotEqual(muted, steps)
        with self.assertRaisesRegex(self.source.Held, "WORKER_FRESH_OWNER_INSERTION"):
            prepare.owning_seam(self.source, operation, muted)


if __name__ == "__main__":
    unittest.main()
