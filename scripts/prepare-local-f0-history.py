"""Prepare one reviewed initial F0 migration; never connect or invoke a tool.

No migration file is written without --prepare-reviewed-history, an explicit
integrated-source checksum and a valid planned local run manifest. Existing
history is never replaced. Failed-history/recovery experiments keep their own
immutable snapshots; this helper does not edit any applied migration or ledger.
"""
import argparse
import hashlib
import json
from pathlib import Path, PureWindowsPath
import re

ROOT = Path(__file__).resolve().parents[1]
SOURCE = "review-output/foundation-application.review.sql"
SCHEMA = "prisma/review/foundation-candidate.prisma"
HISTORY = "prisma/foundation/migrations"
IMAGE = "docker.io/library/postgres:17.11@sha256:996e9dc583ba9f0265a2c75547a9c95fb22c251e394749cab205a0a00e1856a1"
RUNTIME_FILES = (
    "prisma.local-f0.config.mjs",
    "scripts/sql-review/local-f0-migrate-guard.mjs",
    "scripts/sql-review/local-f0-migrate-runner.mjs",
)
SHA = re.compile(r"[0-9a-f]{64}")
MIGRATION = re.compile(r"[0-9]{14}_[a-z][a-z0-9_]{0,79}")


class HeldFailure(Exception):
    def __init__(self, code):
        self.code = code
        super().__init__(code)


def require(condition, code):
    if not condition:
        raise HeldFailure(code)


def digest(value):
    return hashlib.sha256(value).hexdigest()


def validate_bootstrap_secret_path(value):
    # Metadata only: the setup owner separately verifies the actual file's DACL,
    # content transport and exact cleanup. No secret file is opened here.
    require(type(value) is str and re.fullmatch(r'[A-Za-z]:\\[^\x00-\x1f<>"|?*]+', value) and
            "/" not in value and ":" not in value[2:] and
            all(part and part not in (".", "..") and not part.endswith((" ", ".")) for part in value[3:].split("\\")),
            "ABSOLUTE_WINDOWS_SECRET_PATH_REQUIRED")
    path = PureWindowsPath(value)
    task = PureWindowsPath(str(ROOT.parent))
    checkout = PureWindowsPath(str(ROOT))
    require(path.is_absolute() and path.is_relative_to(task) and not path.is_relative_to(checkout) and
            len(path.parts) >= len(task.parts) + 2, "TASK_OWNED_EXTERNAL_SECRET_PATH_REQUIRED")
    return value


def validate_manifest(manifest):
    require(type(manifest) is dict and manifest.get("schema") == "workinants.local-f0-run.v1", "MANIFEST_SCHEMA")
    require(set(manifest) == {"schema", "run_id", "purpose", "target", "source", "migration", "tools"}, "MANIFEST_FIELDS")
    run = manifest.get("run_id")
    require(type(run) is str and re.fullmatch(r"[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}", run), "RUN_ID")
    require(manifest.get("purpose") == "LOCAL_F0_MIGRATION_REHEARSAL", "MANIFEST_PURPOSE")
    target = manifest.get("target", {})
    require(type(target) is dict and set(target) == {"container_name", "volume_name", "database", "image", "network", "labels", "bootstrap_secret_host_path"}, "TARGET_FIELDS")
    validate_bootstrap_secret_path(target["bootstrap_secret_host_path"])
    for key in ("container_name", "volume_name"):
        value = target.get(key)
        require(type(value) is str and re.fullmatch(r"wa-p0c-[a-z0-9][a-z0-9-]{0,110}", value), "RESOURCE_NAME")
    require(target.get("database") == "wa_p0c_rehearsal" and target.get("image") == IMAGE, "LOCAL_TARGET")
    require(target.get("network") == "none", "PRIVATE_NETWORK_REQUIRED")
    require(target.get("labels") == {"workinants.rehearsal": "p0c-local-f0", "workinants.rehearsal.run": run}, "RUN_LABELS")
    source = manifest.get("source", {})
    require(type(source) is dict and set(source) == {"integrated_sql_sha256", "foundation_schema_sha256", "runtime_files_sha256"}, "SOURCE_FIELDS")
    require(all(type(source.get(k)) is str and SHA.fullmatch(source[k])
                for k in ("integrated_sql_sha256", "foundation_schema_sha256")), "SOURCE_HASHES")
    runtime_hashes = source["runtime_files_sha256"]
    require(type(runtime_hashes) is dict and set(runtime_hashes) == set(RUNTIME_FILES) and
            all(type(value) is str and SHA.fullmatch(value) for value in runtime_hashes.values()), "REVIEWED_RUNTIME_HASHES")
    migration = manifest.get("migration", {})
    require(type(migration) is dict and set(migration) == {"id", "history"}, "MIGRATION_FIELDS")
    require(type(migration.get("id")) is str and MIGRATION.fullmatch(migration["id"]), "MIGRATION_ID")
    require(migration.get("history") == HISTORY, "SINGLE_HISTORY_ONLY")
    tools = manifest.get("tools", {})
    require(type(tools) is dict and set(tools) == {"node_version", "prisma_version", "engine_commit", "files_sha256"}, "TOOL_FIELDS")
    require(tools.get("node_version") == "v24.22.1" and tools.get("prisma_version") == "7.10.1", "PINNED_TOOLCHAIN")
    require(tools.get("engine_commit") == "d1b3f377ca835d73fd50954a5e22128b9ebdd6b8", "PINNED_ENGINE")
    files = tools.get("files_sha256", {})
    require(type(files) is dict and all(k in files for k in (
        "node/bin/node", "schema-engine", "node_modules/prisma/build/index.js", "node_modules/prisma/build/cli.js", "node_modules/prisma/config.js", "node_modules/prisma/package.json",
    )), "TOOL_FILE_MAP")
    require(all(type(k) is str and not k.startswith(("/", "\\")) and "\\" not in k and
                all(part not in ("", ".", "..") for part in k.split("/")) and
                type(v) is str and SHA.fullmatch(v) for k, v in files.items()), "TOOL_FILE_MAP")
    return manifest


def prepare_plan(manifest, manifest_bytes, source, schema, runtime_files, expected_hash):
    validate_manifest(manifest)
    require(json.loads(manifest_bytes.decode("utf8")) == manifest, "RAW_MANIFEST_MISMATCH")
    require(type(expected_hash) is str and SHA.fullmatch(expected_hash), "EXPLICIT_SOURCE_HASH_REQUIRED")
    require(digest(source) == expected_hash == manifest["source"]["integrated_sql_sha256"], "SOURCE_HASH_MISMATCH")
    require(digest(schema) == manifest["source"]["foundation_schema_sha256"], "SCHEMA_HASH_MISMATCH")
    text = source.decode("utf8")
    require(len(re.findall(r"(?m)^BEGIN;\s*$", text)) == 1 and
            "SET LOCAL ROLE wa_schema_owner;" in text and
            re.search(r"RESET ROLE;\s*COMMIT;\s*$", text), "INTEGRATED_TRANSACTION_REQUIRED")
    require(not re.search(r"\bCREATE\s+ROLE\b|\bALTER\s+ROLE\b|\bCREATE\s+DATABASE\b", text, re.I), "BOOTSTRAP_OUTSIDE_HISTORY")
    require(len(re.findall(r"(?m)^CREATE TABLE ", text)) == 42, "EXACT_F0_CUT_REQUIRED")
    require(set(runtime_files) == set(RUNTIME_FILES), "RUNTIME_SOURCE_FILES")
    require({path: digest(value) for path, value in runtime_files.items()} == manifest["source"]["runtime_files_sha256"], "REVIEWED_RUNTIME_DRIFT")
    migration = manifest["migration"]["id"]
    files = {
        HISTORY + "/migration_lock.toml": b'provider = "postgresql"\n',
        HISTORY + "/" + migration + "/migration.sql": source,
    }
    provenance = {
        "schema": "workinants.local-f0-history.v1",
        "scope": "PROVISIONAL_LOCAL_REHEARSAL_ONLY_NOT_HOSTED_ADOPTION",
        "run_id": manifest["run_id"], "run_manifest_sha256": digest(manifest_bytes),
        "migration_id": migration, "migrations": HISTORY, "source": SOURCE,
        "source_sql_sha256": expected_hash, "foundation_schema": SCHEMA,
        "files_sha256": {**{path: digest(value) for path, value in files.items()},
                         SCHEMA: digest(schema),
                         **{path: digest(value) for path, value in sorted(runtime_files.items())}},
        "database_contacted": False, "ledger_created_or_modified": False,
        "raw_structure_applied_separately": False,
        "applied_history_rule": "Applied checksums are immutable. Recovery requires independently verified catalog/ledger evidence and the reviewed standard command, never direct ledger writes.",
    }
    return files, provenance


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--prepare-reviewed-history", action="store_true")
    parser.add_argument("--run-manifest", type=Path)
    parser.add_argument("--source-sha256")
    args = parser.parse_args(argv)
    if not args.prepare_reviewed_history:
        parser.error("No writes performed: explicit reviewed-history preparation is required")
    try:
        require(args.run_manifest is not None, "RUN_MANIFEST_REQUIRED")
        raw = args.run_manifest.read_bytes()
        manifest = json.loads(raw.decode("utf8"))
        files, provenance = prepare_plan(manifest, raw, (ROOT / SOURCE).read_bytes(),
                                        (ROOT / SCHEMA).read_bytes(),
                                        {path: (ROOT / path).read_bytes() for path in RUNTIME_FILES},
                                        args.source_sha256)
        history = ROOT / HISTORY
        require(not history.exists(), "HISTORY_ALREADY_EXISTS_NO_REWRITE")
        require(not (ROOT / "prisma/foundation/history-manifest.json").exists(), "HISTORY_MANIFEST_EXISTS")
        # Reserve the history directory exclusively; never patch an existing one.
        history.mkdir(parents=True, exist_ok=False)
        for path, content in files.items():
            destination = ROOT / path
            destination.parent.mkdir(parents=True, exist_ok=True)
            with destination.open("xb") as file:
                file.write(content)
        with (ROOT / "prisma/foundation/history-manifest.json").open("x", encoding="utf8", newline="\n") as file:
            file.write(json.dumps(provenance, indent=2) + "\n")
        print(json.dumps({"status": "PREPARED_NOT_EXECUTED", "migration": provenance["migration_id"],
                          "source_sha256": provenance["source_sql_sha256"]}))
        return 0
    except Exception as error:
        print(json.dumps({"status": "REFUSED_OR_INCOMPLETE_PREPARATION",
                          "code": error.code if isinstance(error, HeldFailure) else "INVALID_INPUT_OR_IO"}))
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
