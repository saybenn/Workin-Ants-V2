"""Validate the reviewed Cloud dependency successor and replay older package checks."""

from contextlib import contextmanager
import hashlib
import json
from pathlib import Path
import subprocess
from tempfile import TemporaryDirectory


CLOUD_SECURITY = "context/reconciliation/cloud-phase0-evidence/2026-11-27/p0b-requalification.json"
CLOUD_SECURITY_SHA256 = "18d8c76d4ecfe28d87d84871a7aeab68757419f84feb1faaa64250d0c4017144"
BASE_COMMIT = "532445ed1f861211978dd8b2e9ae12d4b5e6e180"
AUTHORITY = "context/reconciliation/directives/cloud-phase0-standing-authority-2026-11-27.md"
PACKAGES = {
    "package.json": (
        "6a3a1c7ef64f84eab2e4ec74843eb1c45d907e19ab7f04b222ad8d0eb42a6d85",
        "bdafbda6065b2af3457036789694f9f729c0733275550923d63f2fb4ca380a61",
    ),
    "package-lock.json": (
        "6b4e322549d6a6c14cd8542a21c1a6621a2625f88dbab5606174fd655dcdda1f",
        "89ed7e1a71409fbab67118d310ffde9f6e76d1cea65992d234bdd08d7e1bc3de",
    ),
}
COMMANDS = {"clean_install", "lint", "typecheck", "build", "http_smoke", "schema_validate",
            "runtime_security", "audit_full", "audit_production", "dependency_graph"}


def digest(raw):
    return hashlib.sha256(raw).hexdigest()


def inspect_cloud_security(root, baseline):
    path = root / CLOUD_SECURITY
    if not path.is_file():
        return {"errors": [], "approved": {}}
    errors = []
    try:
        raw_record = path.read_bytes()
        if digest(raw_record) != CLOUD_SECURITY_SHA256:
            return {"errors": ["Reviewed Cloud dependency evidence identity changed"], "approved": {}}
        record = json.loads(raw_record)
        approved = {name: successor for name, (_, successor) in PACKAGES.items()}
        if (record["schema"] != "workinants.cloud-phase0-security.v1"
                or record["starting_commit"] != BASE_COMMIT
                or record["independent_review"]["decision"] != "APPROVE"
                or record["authority"] != AUTHORITY
                or record["authority_sha256"] != "6b7904c37ebab7867f30c00e1a556c387fd3fc63115a86955594ff8dc07b56c4"
                or digest((root / AUTHORITY).read_bytes()) != record["authority_sha256"]
                or record["package_files_sha256"] != approved):
            errors.append("Cloud dependency review identity or authority mismatch")
        for name, expected in approved.items():
            if digest((root / name).read_bytes()) != expected:
                errors.append("Reviewed dependency file drift " + name)
        expected_package = json.loads((baseline / "package.json").read_bytes())
        expected_package["dependencies"]["next"] = "16.4.6"
        expected_package["devDependencies"]["eslint-config-next"] = "16.4.6"
        expected_package["overrides"] = {"@prisma/config@7.10.1": {"effect": "3.22.1"}}
        if json.loads((root / "package.json").read_bytes()) != expected_package:
            errors.append("Unapproved direct dependency or package metadata change")
        if (set(record["command_exit_codes"]) != COMMANDS
                or any(type(code) is not int or code != 0 for code in record["command_exit_codes"].values())
                or record["toolchain"] != {"node": "24.22.1", "npm": "11.9.0", "next": "16.4.6",
                                           "prisma": "7.10.1", "effect_for_prisma_config": "3.22.1"}
                or record["lifecycle_scripts_enabled"] is not True or record["database_contacted"] is not False):
            errors.append("Cloud dependency requalification incomplete or out of scope")
        for name in ("audit-full.json", "audit-production.json", "http.json", "runtime-security.json", "lock-change.json"):
            raw = (path.parent / name).read_bytes()
            if digest(raw) != record["files_sha256"][name]:
                errors.append("Cloud dependency evidence changed " + name)
            evidence = json.loads(raw)
            if name.startswith("audit-"):
                counts = evidence.get("metadata", {}).get("vulnerabilities", {})
                if (evidence.get("error") or evidence.get("vulnerabilities") != {}
                        or not counts or counts.get("total") != 0 or any(counts.values())):
                    errors.append("Cloud dependency audit has findings or incomplete output " + name)
            elif name in ("http.json", "runtime-security.json"):
                rows = evidence["tests" if name == "http.json" else "checks"]
                total = 47 if name == "http.json" else 9
                if (evidence["status"] != "PASS" or evidence["total"] != total or len(rows) != total
                        or any(row["result"] != "PASS" for row in rows)):
                    errors.append("Cloud functional qualification incomplete " + name)
        integrated = record["integration_recheck"]
        if digest((path.parent / integrated["http_artifact"]).read_bytes()) != integrated["http_sha256"]:
            errors.append("Cloud integration HTTP evidence changed")
    except (OSError, ValueError, KeyError, TypeError):
        return {"errors": ["Cloud dependency qualification evidence unavailable or malformed"], "approved": {}}
    return {"errors": errors, "approved": approved if not errors else {}}


class HistoricalPackageView:
    """Point only the two superseded dependency paths at their verified Git bytes."""

    def __init__(self, root, package_root):
        self.root = root
        self.package_root = package_root

    def __truediv__(self, path):
        return (self.package_root if path in PACKAGES else self.root) / path


@contextmanager
def historical_packages(root, git_root):
    if not (root / CLOUD_SECURITY).is_file():
        yield root
        return
    with TemporaryDirectory(prefix="workin-ants-phase0-evidence-") as directory:
        package_root = Path(directory)
        for name, (expected, _) in PACKAGES.items():
            raw = subprocess.check_output(["git", "-C", str(git_root), "show", f"{BASE_COMMIT}:{name}"],
                                          stderr=subprocess.DEVNULL, timeout=15)
            if digest(raw) != expected:
                raise ValueError("Historical dependency fingerprint mismatch")
            (package_root / name).write_bytes(raw)
        yield HistoricalPackageView(root, package_root)
