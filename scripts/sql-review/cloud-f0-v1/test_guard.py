"""Focused offline checks for literal review, isolation, and cleanup guards."""

import copy
from pathlib import Path
from subprocess import CompletedProcess
import tempfile
import unittest
from unittest import mock

from guard import ROOT, Docker, Stop, encode, parse, private_file, safe_refusal, sha256, stable_file, verify_container, verify_volume
from probe import APPROVALS, REVIEW_SCHEMA, Probe, read_review, refusal, target_for, write_new


RUN_ID = "202a1448-b989-40a0-a872-860be6aa95e5"
CID = "3" * 64


class CloudGuardTests(unittest.TestCase):
    def setUp(self):
        folder = self.enterContext(tempfile.TemporaryDirectory())
        self.packet = Path(folder).resolve()
        self.profile = parse((ROOT / "scripts/sql-review/cloud-f0-v1/profile.json").read_bytes())
        self.target = target_for(self.packet, RUN_ID)
        self.volume = {"Name": self.target["volume"], "CreatedAt": "synthetic",
                       "Labels": self.target["labels"], "Driver": "local", "Scope": "local",
                       "Mountpoint": "/var/lib/docker/test-data", "Options": None}
        profile = self.profile
        self.metadata = {
            "Id": CID, "Name": "/" + self.target["container"], "Image": "test-image", "Platform": "linux",
            "Config": {"Image": profile["database_image"], "Labels": self.target["labels"]},
            "State": {"Running": False}, "NetworkSettings": {"Ports": {"5432/tcp": None}, "Networks": {"none": {}}},
            "HostConfig": {
                "NetworkMode": "none", "PublishAllPorts": False, "Privileged": False, "PidMode": "",
                "IpcMode": "private", "RestartPolicy": {"Name": "no"}, "LogConfig": {"Type": "none"},
                "Tmpfs": {profile["credential_tmpfs"]: profile["credential_tmpfs_options"]},
            },
            "Mounts": [
                {"Type": "volume", "Source": self.volume["Mountpoint"], "Name": self.volume["Name"],
                 "Destination": profile["data_mount"], "Driver": "local", "RW": True},
            ],
        }

    def container(self, metadata):
        verify_container(metadata, self.profile, self.target, self.volume, CID, "test-image", running=False)

    def test_exact_container_and_no_host_bind_inventory(self):
        self.container(self.metadata)
        for category, key, value in (
            ("HostConfig", "NetworkMode", "bridge"), ("HostConfig", "Privileged", True),
            ("HostConfig", "PortBindings", {"5432/tcp": [{"HostPort": "5432"}]}),
            ("HostConfig", "Tmpfs", {"/run/wa-secrets": "rw,mode=0777"}),
            ("NetworkSettings", "Networks", {"none": {}, "other": {}}),
            ("Config", "Labels", {}), ("State", "Running", True),
        ):
            with self.subTest(category=category, key=key):
                variant = copy.deepcopy(self.metadata)
                variant[category][key] = value
                with self.assertRaises(Stop):
                    self.container(variant)
        for key, value in (("Name", "unknown"), ("RW", False), ("Source", "/other")):
            variant = copy.deepcopy(self.metadata)
            variant["Mounts"][0][key] = value
            with self.assertRaises(Stop):
                self.container(variant)
        variant = copy.deepcopy(self.metadata)
        variant["Mounts"].append({"Type": "bind", "Destination": "/run/bootstrap-password", "RW": False})
        with self.assertRaisesRegex(Stop, "MOUNT_INVENTORY_MISMATCH"):
            self.container(variant)

    def test_cleanup_refuses_recreated_volume(self):
        self.assertEqual(verify_volume(self.volume, self.target), "synthetic")
        with self.assertRaisesRegex(Stop, "VOLUME_IDENTITY_MISMATCH"):
            verify_volume(self.volume, self.target, "earlier")

    def test_literal_approval_binds_exact_manifest(self):
        manifest = b"reviewed synthetic plan"
        path = self.packet / "review.json"
        approval = {"schema": REVIEW_SCHEMA, "decision": "APPROVE", "reviewer": "independent/test",
                    "manifest_sha256": sha256(manifest), "checks": APPROVALS}
        write_new(path, encode(approval))
        self.assertEqual(read_review(path, manifest)[0], "independent/test")
        with self.assertRaisesRegex(Stop, "EXACT_LITERAL_REVIEW_REQUIRED"):
            read_review(path, manifest + b" changed")
        with self.assertRaisesRegex(Stop, "DUPLICATE_JSON_KEYS"):
            parse(b'{"decision":"PENDING","decision":"APPROVE"}')

    def test_host_private_file_aliases_and_modes_refuse(self):
        path = self.packet / "bootstrap"
        write_new(path, b"fake")
        private_file(path)
        alias = self.packet / "alias"
        alias.symlink_to(path)
        with self.assertRaises(Stop):
            stable_file(alias)
        with self.assertRaises(FileExistsError):
            write_new(path, b"overwrite")
        path.chmod(0o644)
        with self.assertRaisesRegex(Stop, "PRIVATE_FILE_MODE_OR_OWNER"):
            private_file(path)

    def test_private_absence_check_still_runs_after_resource_error(self):
        manifest = {"target": self.target}
        probe = Probe(manifest, self.profile, self.packet, None, {})
        with mock.patch.object(probe, "cleanup_resources", side_effect=Stop("MANIFEST_DAEMON_DRIFT")):
            with self.assertRaisesRegex(Stop, "CLEANUP_UNCONFIRMED"):
                probe.cleanup()
        self.assertEqual(probe.report["cleanup_steps"]["private_files"], "CONFIRMED")
        private = Path(self.target["private_host_path"])
        private.mkdir(mode=0o700)
        with self.assertRaisesRegex(Stop, "PRIVATE_SECRET_ABSENCE_UNCONFIRMED"):
            probe.cleanup_private()

    def test_only_loopback_wrong_password_diagnostic_admitted(self):
        self.assertFalse(refusal(b"connection refused", "postgres"))
        expected = (b'psql: error: connection to server at "127.0.0.1", port 5432 failed: '
                    b'FATAL:  password authentication failed for user "postgres"\n')
        self.assertTrue(refusal(expected, "postgres"))
        self.assertFalse(refusal(expected, "other"))
        self.assertFalse(refusal(expected.replace(b"127.0.0.1", b"10.0.0.1"), "postgres"))

    def test_interrupted_docker_command_latches_remote_uncertainty(self):
        docker = object.__new__(Docker)
        docker.argv = lambda *_: ["does-not-run"]
        docker.env = {}
        docker.remote_unknown = False
        with mock.patch("guard.subprocess.run", side_effect=Stop("OPERATOR_INTERRUPTED")):
            with self.assertRaisesRegex(Stop, "OPERATOR_INTERRUPTED"):
                docker.run("exec", CID, "psql")
        self.assertTrue(docker.remote_unknown)

    def test_failure_classification_excludes_secret_output(self):
        result = CompletedProcess(["not retained"], 125, b"unused canary",
                                  b"error mounting secret-DO-NOT-RETAIN to destination")
        self.assertEqual(safe_refusal(result, "FIRST_START"), {
            "operation": "FIRST_START", "exit_code": 125, "diagnostic": "OCI_MOUNT_FAILURE",
        })
        result = CompletedProcess([], 42, b"SECRET_TMPFS_KERNEL_FLAGS\n", b"")
        self.assertEqual(safe_refusal(result, "KERNEL_ISOLATION")["diagnostic"], "SECRET_TMPFS_KERNEL_FLAGS")
        result.returncode = 125
        self.assertEqual(safe_refusal(result, "KERNEL_ISOLATION")["diagnostic"], "UNLISTED")


if __name__ == "__main__":
    unittest.main()
