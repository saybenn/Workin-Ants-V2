"""Validate the Cloud CSP plan without starting a service."""

import json
from pathlib import Path, PurePosixPath
import subprocess
import tempfile
from types import SimpleNamespace
import unittest
from unittest.mock import patch

import cloud_host
import operate
import prepare
import source7
from cloud_host import probe_literals


RUN = "d546522f-cf32-4d59-a8e6-61b5b1aabb09"
FIXTURE = "5f8afdbe-1292-4f11-848a-9f7a62d344e1"


class Preparation(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.blobs = prepare.closed_files(prepare.ROOT)
        cls.daemon = prepare.parse(cls.blobs[f"{prepare.CAPABILITY}/result.json"])["daemon"]

    def test_frozen_program_remains_closed(self):
        controller = operate.controller(self.blobs)
        self.assertEqual(controller._SAFETY_FINALIZER_SHA,
                         "afd6d11cb19d8e1cc0c5996221935877fe9b93a0672b25d2718343813c9c6e98")
        self.assertEqual(controller.APPLICATION_SHA, source7.INITIAL_SHA)
        for coordinate in ("main", "bootstrap_all", "verify_catalog_packet", "catalog_experiment",
                           "csp_experiment", "finalize", "cleanup"):
            self.assertTrue(callable(getattr(controller, coordinate)))

    def test_generated_node_runtime_has_distinct_cloud_gate_and_deploy_only(self):
        files = source7.render_runtime(prepare.ROOT)
        self.assertEqual(set(files), {source7.CONFIG, source7.GUARD, source7.RUNNER})
        guard, runner = files[source7.GUARD].decode(), files[source7.RUNNER].decode()
        for sentinel in ('"CLOUD_CSP_DEPLOY_ONLY"', '"PATCHED_EFFECT_VERSION"', "hashStableTool"):
            self.assertIn(sentinel, guard)
        self.assertIn("verifyBootstrapAbsent()", guard)
        self.assertIn('"HOST_SECRET_MOUNT_DENIED"', guard)
        self.assertIn(source7.OPERATION_FLAG, runner)
        for text in (guard, runner):
            for legacy in ("npipe", "desktop-linux", "resolve-rolled-back", "--execute-reviewed-local-f0"):
                self.assertNotIn(legacy, text)

    def model_plan(self):
        inputs = prepare.parse(self.blobs[prepare.CLOSURE])
        tools = {
            "files_sha256": inputs["tools_files_sha256"], "file_sizes": inputs["tools_file_sizes"],
            "archive_sha256": inputs["archive_sha256"], "node_version": inputs["node_version"],
            "prisma_version": inputs["prisma_version"], "engine_commit": inputs["engine_commit"],
        }
        model = {**source7.shared(prepare.ROOT), "inspect_tools": lambda *_: tools}
        archive = Path("/workspace/scratch/offline-model/pinned-prisma-tools-cloud-v2.tar.gz")
        with patch.object(source7, "shared", return_value=model), patch.object(
            prepare, "check_committed", return_value=("2" * 40, "3" * 40),
        ):
            return prepare.build(prepare.ROOT, RUN, FIXTURE, self.daemon, archive)

    def test_matches_artifact_scope_and_new_identities(self):
        folder, plan, files = self.model_plan()
        inputs = prepare.parse(self.blobs[prepare.CLOSURE])
        self.assertEqual(folder, prepare.SCRATCH / f"wa-cloud-f0-csp-{RUN}")
        self.assertEqual(plan["runtime"], "NOT_RUN")
        self.assertTrue(plan["review_status"].startswith("PENDING"))
        self.assertIn("FRESH_OPERATIONAL_REVIEW_REQUIRED", plan["platform_gate"])
        self.assertEqual(len(files), 21)
        self.assertEqual(files[f"source7/{source7.MIGRATION_FILE}"], self.blobs[source7.APPLICATION])
        self.assertEqual(plan["generated_files_sha256"], {path: prepare.sha(data) for path, data in files.items()})
        child = json.loads(files["child/fixtures.json"])
        self.assertEqual(child["fixture_run_id"], FIXTURE)
        self.assertEqual(child["assertion_id"], "control.stale_predecessor")
        self.assertIn(b'ORDER BY table_name COLLATE "C"', files["child/full42-state-observe.sql"])
        nested = json.loads(files["migration-manifest.json"])
        self.assertEqual(nested["daemon"], self.daemon)
        self.assertEqual(nested["target"]["bootstrap_container_path"], "/run/wa-secrets/bootstrap-password")
        self.assertNotIn("bootstrap_secret_host_path", nested["target"])
        self.assertEqual(nested["source"]["integrated_sql_sha256"], source7.INITIAL_SHA)
        self.assertEqual(nested["tools"]["archive_sha256"], inputs["archive_sha256"])

    def test_refuses_historical_and_repeated_ids_before_build(self):
        for run, fixture in ((RUN, RUN), (RUN, prepare.HISTORICAL_FIXTURE), (prepare.HISTORICAL_RUN, FIXTURE)):
            with self.assertRaisesRegex(ValueError, "CSP_DISTINCT_NEW_RUNS_REQUIRED"):
                prepare.build(prepare.ROOT, run, fixture, self.daemon, None)

    def test_receipt_binds_exact_packet_and_each_scope(self):
        plan = {"run_id": RUN, "author": prepare.AUTHOR, "source_commit": "a" * 40, "packet_sha256": "b" * 64}
        raw = prepare.encode(plan)
        receipt = {
            "schema": operate.REVIEW, "decision": operate.DECISION, "plan_sha256": prepare.sha(raw),
            "source_commit": plan["source_commit"], "packet_sha256": plan["packet_sha256"],
            "run_id": RUN, "reviewer": "Offline separate reviewer model",
            "scopes": dict.fromkeys(prepare.REVIEW_SCOPES, "APPROVED"), "findings": [],
        }
        self.assertEqual(operate.read_review(prepare.encode(receipt), plan, raw), receipt)
        for mutation in (
            {"reviewer": prepare.AUTHOR}, {"scopes": {"source": "APPROVED"}},
            {"plan_sha256": "0" * 64}, {"findings": ["unresolved"]}, {"run_id": prepare.HISTORICAL_RUN},
        ):
            with self.assertRaises(ValueError):
                operate.read_review(prepare.encode({**receipt, **mutation}), plan, raw)

    def test_alias_paths_and_duplicate_json_reject(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            prepare.write_new(root / "original", b"known")
            (root / "alias").symlink_to(root / "original")
            with self.assertRaisesRegex(ValueError, "CSP_SOURCE_PATH_ALIAS"):
                prepare.stable_file(root / "alias")
        with self.assertRaisesRegex(ValueError, "CSP_JSON_DUPLICATE_FIELD"):
            prepare.parse(b'{"run_id":"first","run_id":"second"}')

    def test_proven_no_bind_literals_and_execute_without_review(self):
        literals = probe_literals(self.blobs[f"{prepare.PROFILE}/probe.py"])
        self.assertIn("0:0:600:1", literals["START_CONTROL"])
        self.assertIn('mv -T -- "$root/bootstrap-pending" "$root/bootstrap-password"', literals["WRITE_BOOTSTRAP"])
        self.assertIn(b"cloud-private-mount-and-loopback", literals["KERNEL_PROBE"])
        with patch("sys.argv", ["operate.py", "--plan", "missing", "--execute-reviewed-cloud-csp"]), patch.object(
            subprocess, "Popen", side_effect=AssertionError("PROCESS_FORBIDDEN"),
        ), patch.object(operate, "verify_plan", side_effect=AssertionError("SOURCE_LOAD_FORBIDDEN")):
            self.assertEqual(operate.main(), 1)

    def test_modeled_bootstrap_runs_only_after_both_resource_checks(self):
        folder, plan, assets = self.model_plan()
        probe = probe_literals(self.blobs[f"{prepare.PROFILE}/probe.py"])
        profile = prepare.parse(self.blobs[f"{prepare.PROFILE}/profile.json"])
        docker = SimpleNamespace(profile=profile, argv=lambda *args: ["MODELED", *args],
                                 env={}, observe=lambda: self.daemon)
        host = operate.controller(self.blobs)
        cid = "d" * 64
        disk = {"CreatedAt": "2026-11-28T03:39:01Z"}
        checked = []
        prepared = {}
        volume = plan["target"]["volume_name"]
        bootstrap = plan["target"]["bootstrap_container_path"]
        copied = {rel.removeprefix("source7/"): data for rel, data in assets.items() if rel.startswith("source7/")}
        dirs = {str(parent) for rel in copied for parent in PurePosixPath(cloud_host.COPIED_SOURCE, rel).parents
                if str(parent).startswith(cloud_host.COPIED_SOURCE)}

        def command(args, payload, _timeout, **_options):
            args = args[1:]
            if args[:2] == ["volume", "create"]:
                return host.Result(0, (volume + "\n").encode(), b"")
            if args[:2] == ["container", "create"]:
                self.assertEqual(args.count("--mount"), 1)
                self.assertIn("type=volume,src=" + volume + ",dst=/var/lib/postgresql/data", args)
                self.assertIn("--tmpfs", args)
                self.assertNotIn("type=bind", " ".join(args))
                self.assertIsNone(payload)
                prepared.update(Entrypoint=["/bin/sh"], Cmd=args[args.index(source7.IMAGE) + 1:],
                                Env=[arg for arg in args if arg.startswith("POSTGRES_")])
                return host.Result(0, (cid + "\n").encode(), b"")
            if args[:2] == ["container", "start"] or args[0] == "exec" and "pg_isready" in args:
                return host.Result(0, b"", b"")
            if payload == probe["KERNEL_PROBE"]:
                if "kernel" not in checked:
                    self.assertEqual(checked, [False, True])
                    checked.append("kernel")
                return host.Result(0, b"cloud-private-mount-and-loopback\n", b"")
            if probe["WRITE_BOOTSTRAP"] in args:
                self.assertEqual(checked, [False, True, "kernel"])
                self.assertRegex(payload, rb"^[a-f0-9]{64}\n$")
                checked.append("stdin-only")
                return host.Result(0, b"", b"")
            if "/proc/1/comm" in args:
                return host.Result(0, b"postgres\n", b"")
            if args[-2:] == ["--", bootstrap]:
                checked.append("removed")
                return host.Result(0, b"", b"")
            if args[-1] == bootstrap:
                self.assertIn("removed", checked)
                checked.append("bootstrap-absent")
                return host.Result(0, b"", b"")
            if "pgpass" in args[-1]:
                self.assertIn("bootstrap-absent", checked)
                self.assertEqual(len(payload.splitlines()), 6)
                return host.Result(0, b"0:0:600:1\n", b"")
            if "/usr/bin/find" in args:
                rows = [f"d|{directory}|4096|0|0|755|2\n" for directory in sorted(dirs)]
                rows.extend(f"f|{cloud_host.COPIED_SOURCE}/{name}|{len(raw)}|0|0|444|1\n"
                            for name, raw in sorted(copied.items()))
                return host.Result(0, "".join(rows).encode(), b"")
            if "/usr/bin/sha256sum" in args:
                self.assertEqual(len(payload.splitlines()), 8)
                self.assertIn(source7.RUNNER.encode(), payload)
                return host.Result(1, b"", b"")
            if cloud_host.COPIED_NODE in args:
                raise AssertionError("Altered copied source must prevent Node dispatch")
            raise AssertionError("Unexpected modeled Docker action")

        host.binary_process = command
        guard = SimpleNamespace(verify_volume=lambda *_: disk["CreatedAt"],
                                verify_container=lambda *args: checked.append(args[-1]))
        host = cloud_host.bind(host, plan, assets, self.blobs, guard, docker, folder, prepare.encode(plan), "f" * 64)
        host.inventory = lambda: (set(), set())
        host.inspect_volume = lambda _: disk
        host.inspect_container = lambda _: {"Config": prepared, "Image": "modeled-image"}
        host.report["image"] = {"image_id": "modeled-image"}
        host.save = lambda: None
        host.event = lambda *_, **_fields: None
        host.create_resources()
        self.assertEqual(checked, [False, True, "kernel", "stdin-only", "removed", "bootstrap-absent"])
        self.assertEqual(host.secret_paths, [])
        with self.assertRaisesRegex(host.Stop, "CSP_CLOUD_COPIED_RUNTIME_CHANGED"):
            host.migrate(host.TARGETS[0], "deploy", "MODELED")
        self.assertNotIn("migration_attempted", host.report)


if __name__ == "__main__":
    unittest.main()
