"""Offline source and dispatch regressions for the Cloud TWO handoff."""

import copy
from pathlib import Path
import tempfile
from types import SimpleNamespace
import unittest
from unittest import mock
import uuid

import bridge
import packet
import sources


class PacketTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.blobs, cls.reviews = sources.historical_sources(sources.ROOT)
        cls.validator = bridge.result_validator(sources.ROOT, cls.blobs)

    def test_historical_receipt_is_not_a_cloud_approval(self):
        self.assertEqual(len(self.blobs), 435)
        self.assertEqual(len(self.reviews), 3)
        peer = next(self.blobs[name] for name in self.blobs
                    if name.endswith("/Root-successor-admission-20261124/independent-code-source-review.json"))
        with self.assertRaisesRegex(sources.Held, "JSON_NUMBER"):
            sources.unique_json(peer)
        projected = sources.unique_json(peer, historical=True)
        self.assertTrue(projected["independent_of_source_author"])
        self.assertFalse(projected["decisions"]["runtime_authorization"])
        self.assertEqual(projected["runtime"], "NOT_RUN")

    def test_only_exact_nonauthor_typed_receipt_admitted(self):
        bindings = {"packet_sha256": "a" * 64, "commit": "b" * 40}
        approval = {"schema": packet.SOURCE_REVIEW, "decision": "APPROVE",
                    "reviewer": "independent/reviewer", "source_author": "author",
                    "bindings": bindings, "scopes": packet.SOURCE_SCOPES}
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "review.json"
            packet.write_new(path, sources.encode(approval))
            review, digest = packet.read_review(path, schema=packet.SOURCE_REVIEW,
                                                bindings=bindings, scopes=packet.SOURCE_SCOPES)
            self.assertEqual(review, approval)
            self.assertEqual(digest, sources.sha(path.read_bytes()))
            with self.assertRaisesRegex(sources.Held, "FRESH_TYPED_REVIEW_REQUIRED"):
                packet.read_review(path, schema=packet.LITERAL_REVIEW, bindings=bindings, scopes=packet.SOURCE_SCOPES)
            path.write_bytes(sources.encode({**approval, "reviewer": "author"}))
            with self.assertRaisesRegex(sources.Held, "FRESH_TYPED_REVIEW_REQUIRED"):
                packet.read_review(path, schema=packet.SOURCE_REVIEW, bindings=bindings, scopes=packet.SOURCE_SCOPES)

    def test_closed_native_assets_reproduce_without_database(self):
        outputs = sources.reproduce_native(sources.ROOT, self.blobs)
        self.assertEqual(len(outputs), 6)
        self.assertIn("expected.json", outputs)
        self.assertIn("expression-oracle.sql", outputs)

    def test_exact_historical_git_bytes_and_claimed_worktree_drift(self):
        identity = sources.verify_committed(sources.ROOT, self.blobs)
        self.assertRegex(identity["commit"], r"^[0-9a-f]{40}$")
        self.assertRegex(identity["tree"], r"^[0-9a-f]{40}$")
        with self.assertRaisesRegex(sources.Held, "GIT_BATCH_HEADER"):
            sources.verify_committed(sources.ROOT, {sources.STEPS: self.blobs[sources.STEPS] + b"\n"})

    def case(self):
        inner = SimpleNamespace(
            SCHEMA="schema.prisma", HISTORY_MANIFEST="hist/manifest.json",
            HISTORY="hist/migrations", ORDERED=[{"path": "hist/migrations/first.sql", "sha256": sources.sha(b"test1")},
                                              {"path": "hist/migrations/second.sql", "sha256": sources.sha(b"test2")}],
            RUNTIME=["config.mjs", "guard.mjs", "runner.mjs"], BASE="fake/runner", OP_ARG="--test-only",
            attest=lambda manifest, observed, operation: sources.encode({"operation": operation}),
        )
        files = {
            inner.SCHEMA: b"schema", inner.HISTORY_MANIFEST: b"manifest",
            f"{inner.HISTORY}/migration_lock.toml": b"lock",
            inner.ORDERED[0]["path"]: b"test1", inner.ORDERED[1]["path"]: b"test2",
            **{path: path.encode() for path in inner.RUNTIME},
        }
        manifest = {
            "run_id": str(uuid.uuid4()), "tools": {"files_sha256": {"node/bin/node": "a" * 64}},
            "source": {**dict.fromkeys(("initial_sql_sha256", "append_sql_sha256", "ordered_history_sha256",
                                       "effective_expected_sha256"), "a" * 64),
                       "runtime_files_sha256": {name: sources.sha(files[name]) for name in inner.RUNTIME}},
        }
        observed = {"container_id": "b" * 64, "daemon": {"daemon_id": "synthetic-daemon"}}
        paths = bridge.copied_paths(inner, manifest, files)
        commands, raw = bridge.required_execs(inner, manifest, files, observed, "deploy")
        result = {
            "schema": bridge.CLOUD_RESULT, "operation": "deploy",
            "status": "CLI_COMPLETED_REQUIRES_INDEPENDENT_LEDGER_CATALOG_CHECKS",
            "exit_code": 0, "prisma_codes": [], "sqlstates": [], "no_pending_message_observed": True,
            "raw_output_discarded": True, "database_qualification_claimed": False,
            "run_id": manifest["run_id"], "container_id": observed["container_id"],
            "daemon_id": observed["daemon"]["daemon_id"], "attestation_sha256": sources.sha(raw),
            **{k: v for k, v in manifest["source"].items() if k.endswith("_sha256") and type(v) is str},
            "diagnostic_format": dict.fromkeys(self.validator.DIAGNOSTIC_FLAGS, False)
            | {"text_valid": True, "headers_valid": True},
        }
        return inner, manifest, files, observed, paths, commands, result

    def test_relative_commands_and_valid_receipt(self):
        inner, manifest, files, observed, paths, commands, result = self.case()
        calls, uncertainty, post = [], [], []

        def process(command, payload, timeout):
            calls.append((command, timeout))
            self.assertEqual(command, commands[len(calls) - 1])
            if len(calls) == 1:
                out = "".join(f"{value}  {name}\n" for name, value in {
                    **{name: sources.sha(body) for name, body in paths.items()},
                    bridge.NODE: manifest["tools"]["files_sha256"]["node/bin/node"],
                }.items()).encode()
            elif len(calls) == 2:
                out = "".join(f"{len(paths[name])}\n" for name in sorted(paths)).encode()
            else:
                self.assertEqual(command[5:8], ("/usr/bin/env", "-i", bridge.NODE))
                self.assertEqual(sources.sha(payload), result["attestation_sha256"])
                out = sources.encode(result)
            return SimpleNamespace(returncode=0, stdout=out, stderr=b"")

        actual = bridge.migrate(inner, self.validator, manifest, files, observed, "deploy",
                                process=process, latch_unknown=lambda: uncertainty.append(True),
                                post_source_check=lambda: post.append(True))
        self.assertEqual(actual, result)
        self.assertEqual([timeout for _, timeout in calls], [30, 30, 150])
        self.assertEqual(uncertainty, [])
        self.assertEqual(post, [True])

    def test_runner_receipt_wrong_daemon_and_private_output_refuse(self):
        inner, manifest, files, observed, _, _, result = self.case()
        _, raw = bridge.required_execs(inner, manifest, files, observed, "deploy")
        for modified in (
            {**result, "daemon_id": "unrelated"},
            {**result, "attestation_sha256": "0" * 64},
            {**result, "billing_detail": "example"},
        ):
            with self.assertRaises(ValueError if "billing_detail" in modified else sources.Held):
                bridge.validate_receipt(SimpleNamespace(returncode=0, stdout=sources.encode(modified), stderr=b""),
                                        self.validator, manifest, observed, "deploy", raw)

    def test_inner_failure_is_sticky_after_outer_dispatch(self):
        inner, manifest, files, observed, _, _, result = self.case()
        result = copy.deepcopy(result)
        result.update(exit_code=None, status="CLI_CLOSURE_UNCONFIRMED_STOP_AND_CLEAN_EXACT_RESOURCE",
                      no_pending_message_observed=False)
        uncertainty = []
        with mock.patch.object(bridge, "verify_source_copy"), mock.patch.object(bridge, "verify_source_lengths"):
            with self.assertRaisesRegex(sources.Held, "REPORTED_INNER_CLI_CLOSURE_UNCONFIRMED"):
                bridge.migrate(
                    inner, self.validator, manifest, files, observed, "deploy",
                    process=lambda *args: SimpleNamespace(returncode=1, stdout=sources.encode(result), stderr=b""),
                    latch_unknown=lambda: uncertainty.append(True), post_source_check=self.fail,
                )
        self.assertEqual(uncertainty, [True])


if __name__ == "__main__":
    unittest.main()
