"""Environment-free tests. No Docker, database, tool download or migration write."""
from contextlib import redirect_stdout
from copy import deepcopy
import hashlib
import io
import json
from pathlib import Path
import runpy
from types import SimpleNamespace
import unittest

ROOT = Path(__file__).resolve().parents[1]
prepare = runpy.run_path(str(ROOT / "scripts/prepare-local-f0-history.py"))
launcher = runpy.run_path(str(ROOT / "scripts/sql-review/run-local-f0-migrate.py"))


def encoded(value):
    return json.dumps(value, separators=(",", ":")).encode("utf8")


def fixture():
    source = ("BEGIN;\nSET LOCAL ROLE wa_schema_owner;\n" +
              "".join("CREATE TABLE app.fixture_%d (id text);\n" % index for index in range(42)) +
              "RESET ROLE;\nCOMMIT;\n").encode("utf8")
    schema = b"offline schema fixture"
    run = "12345678-1234-1234-1234-123456789abc"
    manifest = {"schema": "workinants.local-f0-run.v1", "run_id": run,
                "purpose": "LOCAL_F0_MIGRATION_REHEARSAL",
                "target": {"container_name": "wa-p0c-offline", "volume_name": "wa-p0c-offline-data",
                           "bootstrap_secret_host_path": str(ROOT.parent / "local-f0-secrets-offline" / "bootstrap-password"),
                           "database": "wa_p0c_rehearsal", "image": prepare["IMAGE"], "network": "none",
                           "labels": {"workinants.rehearsal": "p0c-local-f0", "workinants.rehearsal.run": run}},
                "source": {"integrated_sql_sha256": hashlib.sha256(source).hexdigest(),
                           "foundation_schema_sha256": hashlib.sha256(schema).hexdigest(),
                           "runtime_files_sha256": {path: hashlib.sha256(path.encode("utf8")).hexdigest() for path in prepare["RUNTIME_FILES"]}},
                "migration": {"id": "20261117000000_local_f0_initial", "history": prepare["HISTORY"]},
                "tools": {"node_version": "v24.22.1", "prisma_version": "7.10.1",
                          "engine_commit": "d1b3f377ca835d73fd50954a5e22128b9ebdd6b8",
                          "files_sha256": {path: "a" * 64 for path in ("node/bin/node", "schema-engine",
                              "node_modules/prisma/build/index.js", "node_modules/prisma/build/cli.js",
                              "node_modules/prisma/config.js", "node_modules/prisma/package.json")}}}
    context = {"Name": "desktop-linux", "Endpoints": {"docker": {"Host": launcher["ENDPOINT"]}}}
    container = {"Id": "b" * 64, "Image": "sha256:" + "f" * 64, "Name": "/wa-p0c-offline", "Platform": "linux",
                 "Config": {"Image": manifest["target"]["image"], "Labels": deepcopy(manifest["target"]["labels"])},
                 "State": {"Running": True}, "HostConfig": {"NetworkMode": "none", "PortBindings": {},
                     "Privileged": False, "PidMode": "", "IpcMode": "private", "Devices": [], "CapAdd": [],
                     "Tmpfs": {"/run/wa-secrets": "rw,noexec,nosuid,nodev,mode=0700,size=16m"}},
                 "NetworkSettings": {"Ports": {"5432/tcp": None}},
                 "Mounts": [{"Type": "volume", "Name": "wa-p0c-offline-data", "Destination": "/var/lib/postgresql/data", "RW": True},
                            {"Type": "bind", "Source": manifest["target"]["bootstrap_secret_host_path"], "Destination": "/run/bootstrap-password", "RW": False}]}
    volume = {"Name": "wa-p0c-offline-data", "Driver": "local", "Options": None, "Scope": "local",
              "Labels": deepcopy(manifest["target"]["labels"])}
    runtime = {path: path.encode("utf8") for path in prepare["RUNTIME_FILES"]}
    return manifest, source, schema, runtime, context, container, volume


class HistoryTests(unittest.TestCase):
    def plan(self, manifest, source, schema, runtime):
        return prepare["prepare_plan"](manifest, encoded(manifest), source, schema, runtime,
                                       manifest["source"]["integrated_sql_sha256"])

    def test_exact_integrated_migration_is_only_a_byte_plan(self):
        manifest, source, schema, runtime, *_ = fixture()
        files, provenance = self.plan(manifest, source, schema, runtime)
        self.assertEqual(len(files), 2)
        migration = prepare["HISTORY"] + "/" + manifest["migration"]["id"] + "/migration.sql"
        self.assertEqual(files[migration], source)
        self.assertFalse(provenance["database_contacted"])
        self.assertFalse(provenance["ledger_created_or_modified"])
        self.assertFalse(provenance["raw_structure_applied_separately"])
        self.assertEqual(provenance["run_manifest_sha256"], hashlib.sha256(encoded(manifest)).hexdigest())

    def test_no_explicit_source_hash_refuses(self):
        manifest, source, schema, runtime, *_ = fixture()
        with self.assertRaises(prepare["HeldFailure"]):
            prepare["prepare_plan"](manifest, encoded(manifest), source, schema, runtime, None)

    def test_manifest_and_sources_must_match_exactly(self):
        original = fixture()
        for kind in ("source", "schema", "runtime", "runtime_drift", "manifest_bytes"):
            with self.subTest(kind=kind):
                manifest, source, schema, runtime, *_ = deepcopy(original)
                raw = encoded(manifest)
                if kind == "source": source += b"changed"
                if kind == "schema": schema += b"changed"
                if kind == "runtime": runtime.pop(next(iter(runtime)))
                if kind == "runtime_drift": runtime[next(iter(runtime))] = b"changed"
                if kind == "manifest_bytes": raw = encoded({**manifest, "purpose": "OTHER"})
                with self.assertRaises(prepare["HeldFailure"]):
                    prepare["prepare_plan"](manifest, raw, source, schema, runtime, manifest["source"]["integrated_sql_sha256"])

    def test_rejects_other_target_history_tools_and_unknown_fields(self):
        for path, value in (("target.image", "postgres:latest"), ("target.network", "bridge"),
                            ("target.database", "production"), ("target.container_name", "unknown"),
                            ("target.volume_name", "wa-p0c-../escape"), ("target.labels", {}),
                            ("migration.history", "prisma/migrations"), ("migration.id", "../escape"),
                            ("tools.prisma_version", "7.10.2"), ("tools.node_version", "v24.18.1"),
                            ("tools.engine_commit", "other"), ("source.integrated_sql_sha256", "bad"),
                            ("source.runtime_files_sha256", {}),
                            ("tools.files_sha256", {"../bad": "a" * 64}), ("password", "CANARY")):
            with self.subTest(path=path):
                manifest, *_ = fixture()
                parent = manifest
                keys = path.split(".")
                for key in keys[:-1]: parent = parent[key]
                parent[keys[-1]] = value
                with self.assertRaises(prepare["HeldFailure"]): prepare["validate_manifest"](manifest)

    def test_bootstrap_secret_path_is_absolute_task_owned_and_external(self):
        for value in ("relative", "\\\\server\\share\\secret", "D:\\unowned\\secret", str(ROOT / "secret"),
                      str(ROOT.parent / "secrets" / ".." / "secret"), str(ROOT.parent / "secrets" / "secret:stream"),
                      str(ROOT.parent / "secrets" / "secret.")):
            with self.subTest(value=value):
                self.assert_held_path(value)

    def assert_held_path(self, value):
        with self.assertRaises(prepare["HeldFailure"]): prepare["validate_bootstrap_secret_path"](value)

    def test_bootstrap_and_wrong_cut_refuse_even_with_matching_hash(self):
        for replacement in (b"CREATE ROLE forbidden;\n", b"CREATE DATABASE forbidden;\n", b"BEGIN;\n"):
            manifest, source, schema, runtime, *_ = fixture()
            source = replacement + source
            manifest["source"]["integrated_sql_sha256"] = hashlib.sha256(source).hexdigest()
            with self.assertRaises(prepare["HeldFailure"]): self.plan(manifest, source, schema, runtime)
        manifest, source, schema, runtime, *_ = fixture()
        source = source.replace(b"CREATE TABLE app.fixture_41 (id text);\n", b"")
        manifest["source"]["integrated_sql_sha256"] = hashlib.sha256(source).hexdigest()
        with self.assertRaises(prepare["HeldFailure"]): self.plan(manifest, source, schema, runtime)


class LauncherTests(unittest.TestCase):
    def test_observed_desktop_translation_matches_only_exact_manifest_path(self):
        from pathlib import PureWindowsPath
        manifest,*_,context,container,volume=fixture()
        expected=manifest['target']['bootstrap_secret_host_path'];windows=PureWindowsPath(expected)
        desktop='/run/desktop/mnt/host/'+windows.drive[0].lower()+'/'+'/'.join(windows.parts[1:])
        container['Mounts'][1]['Source']=desktop
        self.assertNotEqual(desktop,expected)  # Restores the previous exact-equality mismatch.
        launcher['inspect_live'](manifest,context,container,volume)
        self.assertEqual(launcher['bootstrap_source_comparison'](desktop,expected),(False,True))
        from unittest.mock import patch
        with patch.dict(launcher['inspect_live'].__globals__,bootstrap_source_comparison=lambda actual,planned:(actual==planned,False)):
            with self.assertRaises(Exception) as caught:launcher['inspect_live'](manifest,context,container,volume)
            self.assertEqual(caught.exception.code,'EXACT_PRIVATE_MOUNTS_REQUIRED')
        for value in (desktop+'/extra',desktop.replace('/run/desktop/mnt/host/','/unapproved/'),desktop.replace('/c/','/d/',1),desktop+'CANARY',expected+'CANARY'):
            with self.subTest(value=value):
                container['Mounts'][1]['Source']=value
                with self.assertRaises(Exception) as caught:launcher['inspect_live'](manifest,context,container,volume)
                checks=launcher['mount_failure_comparison'](caught.exception)
                self.assertEqual(set(checks),set(launcher['MOUNT_CHECKS']))
                self.assertTrue(all(type(v) is bool for v in checks.values()))
                self.assertFalse(checks['bootstrap_source']);self.assertNotIn('CANARY',json.dumps(checks))

    def assert_held(self, function):
        # Launcher imports its own runpy class, so identify the fixed error code.
        with self.assertRaises(Exception) as caught: function()
        self.assertTrue(hasattr(caught.exception, "code"))

    def test_realistic_unpublished_expose_is_allowed(self):
        manifest, *_, context, container, volume = fixture()
        observed = launcher["inspect_live"](manifest, context, container, volume)
        self.assertEqual(observed["container_id"], container["Id"])
        self.assertFalse(observed["published_ports"])

    def test_runtime_metadata_guards(self):
        mutations = [
            lambda m, c, t, v: c["Endpoints"]["docker"].update(Host="ssh://remote"),
            lambda m, c, t, v: t.update(Name="/unowned"),
            lambda m, c, t, v: t["Config"].update(Image="postgres:latest"),
            lambda m, c, t, v: t["Config"].update(Labels={}),
            lambda m, c, t, v: t["State"].update(Running=False),
            lambda m, c, t, v: t["HostConfig"].update(NetworkMode="bridge"),
            lambda m, c, t, v: t["HostConfig"].update(PortBindings={"5432/tcp": [{"HostPort": "5432"}]}),
            lambda m, c, t, v: t["NetworkSettings"].update(Ports={"5432/tcp": [{"HostPort": "5432"}]}),
            lambda m, c, t, v: t["HostConfig"].update(Privileged=True),
            lambda m, c, t, v: t["HostConfig"].update(IpcMode="host"),
            lambda m, c, t, v: t["HostConfig"].update(IpcMode="container:" + "a" * 64),
            lambda m, c, t, v: t["HostConfig"].update(Tmpfs={}),
            lambda m, c, t, v: t["Mounts"].append({"Type": "bind", "Source": "/", "Destination": "/host"}),
            lambda m, c, t, v: t["Mounts"][0].update(Name="other-volume"),
            lambda m, c, t, v: t["Mounts"][1].update(Source="C:\\wrong\\secret"),
            lambda m, c, t, v: t["Mounts"][1].update(Destination="/run/other-secret"),
            lambda m, c, t, v: t["Mounts"][1].update(RW=True),
            lambda m, c, t, v: t["Mounts"].append(deepcopy(t["Mounts"][1])),
            lambda m, c, t, v: t["Mounts"].append({"Type": "tmpfs", "Destination": "/unapproved"}),
            lambda m, c, t, v: v.update(Labels={}),
            lambda m, c, t, v: v.update(Driver="unknown"),
        ]
        for index, mutate in enumerate(mutations):
            with self.subTest(index=index):
                manifest, *_, context, container, volume = fixture()
                mutate(manifest, context, container, volume)
                self.assert_held(lambda: launcher["inspect_live"](manifest, context, container, volume))

    def test_coordinator_mocked_all_processes_and_exact_immutable_id(self):
        manifest, _, _, runtime, context, container, volume = fixture()
        calls = []
        image = {"Id": container["Image"], "Os": "linux", "Architecture": "amd64", "RepoDigests": [manifest["target"]["image"]]}
        observations = iter((context, container, volume, image))
        def process(arguments, **kwargs):
            calls.append((arguments, kwargs))
            if "exec" not in arguments:
                return SimpleNamespace(returncode=0, stdout=json.dumps([next(observations)]), stderr="")
            if "/usr/bin/sha256sum" in arguments:
                self.assertEqual(arguments[4], container["Id"])
                hashes = {launcher["TOOLS_ROOT"] + "/node/bin/node": manifest["tools"]["files_sha256"]["node/bin/node"],
                          **{launcher["SOURCE_ROOT"] + "/" + name: hashlib.sha256(raw).hexdigest() for name, raw in runtime.items()}}
                return SimpleNamespace(returncode=0, stdout="".join(hashes[path] + "  " + path + "\n" for path in arguments[7:]), stderr="")
            self.assertEqual(arguments[5], container["Id"])
            self.assertNotIn("CANARY", json.dumps(arguments))
            self.assertNotIn("env", kwargs)
            attestation = json.loads(kwargs["input"])
            value = {"schema": "workinants.local-f0-migrate-result.v1", "operation": "deploy",
                     "status": "CLI_COMPLETED_REQUIRES_INDEPENDENT_LEDGER_CATALOG_CHECKS", "exit_code": 0,
                     "prisma_codes": [], "sqlstates": [], "no_pending_message_observed": False,
                     "raw_output_discarded": True, "database_qualification_claimed": False,
                     "run_id": manifest["run_id"], "container_id": container["Id"],
                     "source_sql_sha256": manifest["source"]["integrated_sql_sha256"],
                     "attestation_sha256": hashlib.sha256(kwargs["input"].encode("utf8")).hexdigest()}
            self.assertEqual(attestation["observed"]["container_id"], container["Id"])
            return SimpleNamespace(returncode=0, stdout=json.dumps(value), stderr="CANARY discarded")
        value = launcher["coordinate"](encoded(manifest), "deploy", process=process, runtime_sources=runtime)
        self.assertEqual(len(calls), 6)
        self.assertEqual(value["exit_code"], 0)
        self.assertNotIn("CANARY", json.dumps(value))

    def test_no_execution_without_opt_in(self):
        def forbidden(*args, **kwargs): self.fail("process called before explicit execution")
        output = io.StringIO()
        with redirect_stdout(output):
            self.assertEqual(launcher["main"]([], process=forbidden), 1)
        self.assertIn("EXPLICIT_EXECUTION_REQUIRED", output.getvalue())

    def test_actual_image_and_entrypoint_drift_refuse_before_copied_code(self):
        manifest, _, _, runtime, context, container, volume = fixture()
        image = {"Id": container["Image"], "Os": "linux", "Architecture": "amd64", "RepoDigests": [manifest["target"]["image"]]}
        launcher["verify_image"](manifest, container, image)
        for key, value in (("Id", "sha256:" + "e" * 64), ("Os", "windows"), ("Architecture", "arm64"), ("RepoDigests", [])):
            self.assert_held(lambda: launcher["verify_image"](manifest, container, {**image, key: value}))
        observed = launcher["inspect_live"](manifest, context, container, volume)
        def mismatch(*args, **kwargs): return SimpleNamespace(returncode=0, stdout="CANARY malformed digest output", stderr="")
        self.assert_held(lambda: launcher["copied_entrypoint_preflight"](manifest, observed, runtime, mismatch))
        changed = {**runtime, next(iter(runtime)): b"changed host JS"}
        def forbidden(*args, **kwargs): self.fail("process called before reviewed runtime equality")
        self.assert_held(lambda: launcher["copied_entrypoint_preflight"](manifest, observed, changed, forbidden))

    def test_no_raw_exception_output(self):
        self.assert_held(lambda: launcher["unique_json"]('{"key":1,"key":2}'))
        manifest, *_, context, container, volume = fixture()
        def process(*args, **kwargs): raise RuntimeError("CANARY postgresql://password@host")
        # No filesystem input for this pure function, so no real tool can run.
        with self.assertRaises(RuntimeError): launcher["coordinate"](encoded(manifest), "deploy", process=process)

    def test_recovery_requires_bound_reviewed_evidence(self):
        manifest, *_, context, container, volume = fixture()
        observed = launcher["inspect_live"](manifest, context, container, volume)
        proof = {"schema": "workinants.local-f0-reviewed-rollback.v1", "run_id": manifest["run_id"],
                 "container_id": container["Id"], "migration_id": manifest["migration"]["id"],
                 "source_sql_sha256": manifest["source"]["integrated_sql_sha256"],
                 "disposition": "REVIEWED_FOR_STANDARD_RESOLVE_ROLLED_BACK", "backend_closed": True,
                 "application_transaction_rolled_back": True, "application_object_count": 0,
                 "failed_migration_rows": 1, "finished_migration_rows": 0, "rolled_back_migration_rows": 0,
                 "failed_row_checksum": manifest["source"]["integrated_sql_sha256"],
                 "catalog_evidence_sha256": "c" * 64, "ledger_evidence_sha256": "d" * 64}
        launcher["validate_rollback"](proof, manifest, observed)
        for key, value in (("application_object_count", 1), ("backend_closed", False),
                           ("failed_migration_rows", True), ("finished_migration_rows", 1),
                           ("failed_row_checksum", "f" * 64), ("container_id", "e" * 64)):
            wrong = {**proof, key: value}
            self.assert_held(lambda: launcher["validate_rollback"](wrong, manifest, observed))


if __name__ == "__main__":
    unittest.main(verbosity=2)
