"""Build the source-only Cloud v2 Customer rollback fixture packet."""

import argparse
import hashlib
import json
from pathlib import Path
from types import ModuleType


ROOT = Path(__file__).resolve().parents[3]
SELF = "scripts/sql-review/cloud-customer-stale-predecessor-v2/prepare.py"
PARENT = "scripts/prepare-customer-stale-predecessor-v1.py"
PARENT_SHA = "8e8f37b5292fa377da509cc9a4f5380a25fc3f5291a84e9e5c344e782272ec61"
PROTOCOL = "scripts/customer_stale_predecessor_v1_protocol.py"
PROTOCOL_SHA = "865f91ba0d82c77a12b8c2da92c4ae489d8029e33bf18c81ce784f6ad4b26115"
SNAPSHOT = "full42-state-observe.sql"
AGGREGATE = "SELECT jsonb_agg(jsonb_build_object('table',table_name,'count',row_count,'sha256',row_sha)"
PARENT_PREFIX = AGGREGATE + " ORDER BY table_name) FROM ("
CLOUD_PREFIX = AGGREGATE + ' ORDER BY table_name COLLATE "C") FROM ('


def sha(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def load_parent(root: Path) -> ModuleType:
    path = root / PARENT
    raw = path.read_bytes()
    if sha(raw) != PARENT_SHA:
        raise ValueError("CSP_CLOUD_V2_PARENT_GENERATOR_CHANGED")
    parent = ModuleType("_workinants_csp_v1_generator")
    parent.__file__ = str(path)
    exec(compile(raw, str(path), "exec"), parent.__dict__)
    return parent


def build(root: Path, fixture_run_id: str) -> tuple[dict[str, str], dict]:
    """Return SQL and metadata without creating a process or opening a database."""
    root = Path(root).resolve()
    if sha((root / PROTOCOL).read_bytes()) != PROTOCOL_SHA:
        raise ValueError("CSP_CLOUD_V2_STRICT_VALIDATOR_CHANGED")

    parent = load_parent(root)
    files, packet = parent.build(root, fixture_run_id)
    # Fresh UUIDs can change the order of capabilities within a model.
    grant = packet["baseline"]["grant"]
    grant["allowed_fields"] = sorted(grant["allowed_fields"])
    observer = files[SNAPSHOT]
    if not observer.startswith(PARENT_PREFIX) or observer.count(PARENT_PREFIX) != 1:
        raise ValueError("CSP_CLOUD_V2_UNRECOGNIZED_SNAPSHOT")
    files[SNAPSHOT] = CLOUD_PREFIX + observer[len(PARENT_PREFIX):]

    packet["source_files_sha256"][SELF] = sha((root / SELF).read_bytes())
    packet["prepared_files_sha256"][SNAPSHOT] = sha(files[SNAPSHOT].encode("utf-8"))
    content = {key: packet[key] for key in ("source_files_sha256", "prepared_files_sha256")}
    packet["content_sha256"] = sha(
        json.dumps(content, sort_keys=True, separators=(",", ":")).encode("utf-8")
    )
    files["fixtures.json"] = parent.encoded(packet).decode("utf-8")
    return files, packet


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--fixture-run-id", required=True)
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args(argv)
    files, packet = build(ROOT, args.fixture_run_id)

    args.output.mkdir()
    for name, contents in sorted(files.items()):
        with (args.output / name).open("xb") as output:
            output.write(contents.encode("utf-8"))
    print(
        json.dumps(
            {
                "schema": "workinants.cloud-customer-stale-predecessor-v2-preparation.v1",
                "status": "SOURCE_PREPARED_NOT_EXECUTED",
                "fixture_run_id": packet["fixture_run_id"],
                "fixtures_sha256": sha(files["fixtures.json"].encode("utf-8")),
                "snapshot_sha256": packet["prepared_files_sha256"][SNAPSHOT],
                "content_sha256": packet["content_sha256"],
                "files": len(files),
            },
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
