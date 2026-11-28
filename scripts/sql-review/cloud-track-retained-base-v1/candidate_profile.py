"""Prepare a held three-history Cloud Track packet without opening Docker."""

import argparse
from copy import deepcopy
from pathlib import Path
import re
import sys
from types import ModuleType
import uuid


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
BASE = HERE.relative_to(ROOT).as_posix()
TWO = "scripts/sql-review/cloud-two-history-owned-v2"
RETAINED = "review-output/track-retained-base-candidate-v1"
GENERATOR = "scripts/sql-review/prepare-track-retained-base-candidate.py"
REVIEW = f"{RETAINED}/independent-source-review.json"
APPEND = f"{RETAINED}/migration.sql"
EXPECTED = f"{RETAINED}/expected-catalog.json"
PRIOR = "context/reconciliation/cloud-phase0-evidence/2026-11-27/two-2f71c365"
PRIOR_RUN = "2f71c365-4c31-4000-837c-cdd72ac163ae"
CANDIDATE_COMMIT = "d25792e0524a70af763c31cc0c64605d737cc915"
CANDIDATE_SHA = "ae7b94aae1689b54d6da0b9443b2512087018270774124f2b1d012f65f6ddcdb"
CATALOG_SHA = "59a6a99a96748b72d8d639977c457857058777bf99346afb59804df926c107a9"
MIGRATION = "20261128000100_f0_track_retained_base_v1"
HISTORY = "prisma/local-f0-track-retained-base-v1/migrations"
HISTORY_MANIFEST = "prisma/local-f0-track-retained-base-v1/history-manifest.json"
TARGET_PREFIX = "wa-p0c-cloud-track-retained-"
LABEL = "p0c-cloud-f0-track-retained-base-v1"
PURPOSE = "CLOUD_F0_TRACK_RETAINED_BASE_THREE_MIGRATION_REHEARSAL"
RUN_SCHEMA = "workinants.cloud-f0-track-retained-base-run.v1"
HISTORY_SCHEMA = "workinants.cloud-f0-track-retained-base-history.v1"
ATTESTATION_SCHEMA = "workinants.cloud-f0-track-retained-base-attestation.v1"
RESULT_SCHEMA = "workinants.cloud-f0-track-retained-base-migration-result.v1"
REFUSAL_SCHEMA = "workinants.cloud-f0-track-retained-base-migration-refusal.v1"
PACKET_SCHEMA = "workinants.cloud-f0-track-retained-base-held-owner-packet.v1"
OP_ARG = "--execute-reviewed-cloud-f0-track-retained-base-v1"
APPLIED_RULE = "Three exact applied checksums immutable; no resolve/baseline/direct ledger mutation in this family."
OWN_FILES = ("candidate_profile.py", "three_proof.py", "test_profile.py", "README.md")
EXTRA_PINS = {
    GENERATOR: "8052cd4b303d14cfb9ee99cd96492bb609776a0017013cd655407caeee091a8f",
    APPEND: CANDIDATE_SHA,
    EXPECTED: "df3197e77f3d4c540417c371f8bcd4b80d9c6020c8cf03cc7a18ce23379e8359",
    REVIEW: "88dd682505df6b3d52a39c9eab9ceda75fc7dee04f35849d5596ff605c5f802d",
    f"{RETAINED}/README.md": "c3154a669bd1ac13304b8bbefa5faa2356ac771707f57a5487c1d67a14fc8a68",
    f"{RETAINED}/history/v1-migration.sql.txt": "42b149ef2d0e567ea326328f485ef21bd0b3afe30162667ef70631c338f56fba",
    f"{RETAINED}/history/v2-migration.sql.txt": "1187a0ed4468d7d576d03653af672f9133e5eab19ca9a8a3e819572e10ef7f10",
    f"{PRIOR}/acceptance.json": "9ecf3628b388ef11c504def7422bf53c1d67926820a6662d60a44dbc0fe61d76",
    f"{PRIOR}/operation.json": "ad689dc962febeeb72b5f7583598cef559d475b2fe7227d097e57558625cef30",
    f"{PRIOR}/independent-closure.json": "2aa3d5178e406f42ae617c77ffe0e72f8b472e1c42b51fccbb261e3a781f0992",
    f"{PRIOR}/evidence/two-history-results.json": "81d04362aa00e52bcb7161899cf3711c644cd7abb7237c2d1f0a33f0cb41115c",
}
PARENT_LAUNCHER_SHA = {
    "config.mjs": "12b1747089ed950ada35c6475d991949da2cc3ad21b0e756106175ff447af2d0",
    "guard.mjs": "e17b7effeba3dc172c853199e784d29715823c30c5e1f3c23e1a61eaaec710ef",
    "runner.mjs": "74a08369ac1bbecbbc7e24ac88135a5f9921c827f5d104155abb235a528fc5f2",
}
RUNTIME = tuple(f"{BASE}/{name}" for name in PARENT_LAUNCHER_SHA)
CONVERSION_CODES = {
    "EXACT_TWO_HISTORY_REQUIRED": "EXACT_THREE_HISTORY_REQUIRED",
    "EXACT_ORDERED_TWO_HISTORY": "EXACT_ORDERED_THREE_HISTORY",
    "EXACT_TWO_SOURCE_PINS": "EXACT_THREE_SOURCE_PINS",
    "EXACT_SEVEN_DECLARED_SOURCES": "EXACT_EIGHT_DECLARED_SOURCES",
    "EXACT_SOURCE8_CLOSURE": "EXACT_NINE_FILE_CLOSURE",
}
FIXED_HISTORY = (
    ("20261117000100_f0_local_initial", "5ae39abf991f9c189e367eb6ab6968b0ad50836bf4220ac27ef8c18306ac26ad"),
    ("20261120000100_f0_runtime_lease_branch_v1", "49c3345c281d8ef62355d5392d02085d5fdfa71f7193e7e0bd4264562c33cfb7"),
    (MIGRATION, CANDIDATE_SHA),
)
ORIGINAL_BOOTSTRAP = "review-output/foundation-bootstrap.review.sql"
ORIGINAL_FINALIZER = "scripts/sql-review/foundation-bootstrap-finalize.sql"
LEDGER_COLLECTOR = "scripts/sql-review/collect_prisma_ledger.sql"
FINGERPRINT_COLLECTOR = "scripts/sql-review/collect_runtime_lease_history_fingerprints_v1.sql"


def load_basis():
    import hashlib

    path = ROOT / TWO / "basis.py"
    raw = path.read_bytes()
    if hashlib.sha256(raw).hexdigest() != "e19319429a5b97fc594f91b882229f767964e4f9dd96891a9b9ebcaa9a4280af":
        raise ValueError("FIXED_TWO_BASIS_DRIFT")
    module = ModuleType("_track_retained_pinned_two_basis")
    module.__file__ = str(path)
    exec(compile(raw, str(path), "exec", dont_inherit=True), module.__dict__)
    return module


basis = load_basis()
S, P = basis.S, basis.P
INNER_SOURCE = f"{basis.INNER}/prepare.py"
INNER_PIN = "5a11134e3f2b9944dfeab1e691d9358901a9eca33495d1d6701ed400998999da"


def reviewed_parent():
    return S.module(ROOT, INNER_SOURCE, S.pinned(ROOT, INNER_SOURCE, INNER_PIN))


def qualification_basis(blobs):
    accepted, operation, audit, result, review = (S.unique_json(blobs[name]) for name in (
        f"{PRIOR}/acceptance.json", f"{PRIOR}/operation.json", f"{PRIOR}/independent-closure.json",
        f"{PRIOR}/evidence/two-history-results.json", REVIEW,
    ))
    S.require(accepted["decision"] == "ACCEPT_EXACT_DISPOSABLE_MIGRATION_MACHINERY"
              and accepted["operation_run_id"] == operation["run_id"] == audit["run_id"] == result["run_id"] == PRIOR_RUN
              and accepted["source_commit"] == operation["source"]["commit"] == audit["source_commit"] == result["source_commit"]
              and accepted["source_tree"] == operation["source"]["tree"] == audit["source_tree"] == result["source_tree"]
              and accepted["files_sha256"]["operation.json"] == result["packet_sha256"] == audit["packet_sha256"]
              == EXTRA_PINS[f"{PRIOR}/operation.json"] and result["container_id"] == audit["created_container_id"]
              and audit["decision"] == "EXACT_MACHINERY_SUBSET_AND_CLEANUP_VERIFIED"
              and audit["status"] == result["status"] == "PASS_MACHINERY_SUBSET_ONLY"
              and len(audit["cleanup_verified"]) == 8 and all(flag is True for flag in audit["cleanup_verified"].values())
              and result["source_expected_sha256"] == S.EXPECTED
              and result["original_grantor_finalized"] is True
              and result["full8_noop"]["all_eight_columns_unchanged"] is True,
              "PRIOR_INDEPENDENT_TWO_ACCEPTANCE_REQUIRED")
    S.require(review["decision"] == "APPROVE_HELD_SOURCE_PREPARATION" and review["runtime"] == "NOT_RUN"
              and review["operational_authority"] is False and review["assertion_promotions"] == 0
              and review["findings"] == [] and review["reviewer"] != review["source_author"]
              and review["files_sha256"] == {GENERATOR: EXTRA_PINS[GENERATOR], "migration.sql": CANDIDATE_SHA,
                                             "expected-catalog.json": EXTRA_PINS[EXPECTED]}
              and review["reproduced"]["source8_acceptance_sha256"] == EXTRA_PINS[f"{PRIOR}/acceptance.json"]
              and review["reproduced"]["expected_catalog_sha256"] == CATALOG_SHA,
              "INDEPENDENT_HELD_CANDIDATE_REVIEW_REQUIRED")
    return accepted, operation, audit, review


def render_native(blobs, review):
    preparer = S.module(ROOT, S.NATIVE, blobs[S.NATIVE])
    native_pins = S.unique_json(blobs[f"{S.NATIVE_REVIEW}/source-pins.json"])
    original, tools, effective, _, _ = preparer.load_tools(ROOT, native_pins)
    imports = {"catalog_manifest": tools["catalog_manifest"], "runtime_lease_effective_catalog_v1": effective}
    S.require(not any(name in sys.modules for name in imports), "CANDIDATE_COMPILER_IMPORT_COLLISION")
    try:
        sys.modules.update(imports)
        source = S.module(ROOT, GENERATOR, blobs[GENERATOR])
        candidate, expected = source.build(ROOT)
    finally:
        for name in imports:
            del sys.modules[name]
    S.require(candidate == blobs[APPEND] and S.encode(expected) == blobs[EXPECTED]
              and expected["ordered_migration_sha256"] == review["reproduced"]["ordered_migration_sha256"]
              and expected["changed_expected_fields"] == review["reproduced"]["changed_expected_fields"]
              and expected["expected_catalog_sha256"] == CATALOG_SHA, "APPEND_AND_CANDIDATE_CATALOG_READBACK")
    base = S.unique_json(blobs[f"{S.NATIVE_REVIEW}/expected.json"])
    manifest = deepcopy(base)
    manifest["expected"] = expected["expected"]
    manifest["expected_sha256"] = CATALOG_SHA
    manifest["ordered_source"] = {"migration_sha256": expected["ordered_migration_sha256"],
                                  "expected_function_deltas": expected["changed_expected_fields"]}
    manifest["inputs_sha256"] = {**base["inputs_sha256"], APPEND: CANDIDATE_SHA}
    manifest["inputs_aggregate_sha256"] = S.sha("".join(
        f"{name}\t{pin}\n" for name, pin in sorted(manifest["inputs_sha256"].items())).encode())
    # The oracle uses manifest iteration order. Generate from the exact JSON
    # representation that the owning controller will later reopen and validate.
    manifest_raw = S.encode(manifest)
    manifest = S.unique_json(manifest_raw)
    oracle = tools["catalog_expression_oracle"]
    expression = oracle.build_plan(manifest, ROOT)
    previous = S.unique_json(blobs[f"{S.NATIVE_REVIEW}/expression-oracle-plan.json"])
    S.require(expression["expression_count"] == 416 and expression["expected_tables"] == 42
              and expression["expected_columns"] == 600
              and sorted(map(S.encode, expression["expressions"])) == sorted(map(S.encode, previous["expressions"])),
              "CANDIDATE_UNCHANGED_416_ORACLE_EXPRESSIONS")
    public = original.public_registration(manifest, tools["catalog_manifest"])
    S.require(public == S.unique_json(blobs[f"{S.NATIVE_REVIEW}/public-schema-registration.json"]),
              "UNCHANGED_PUBLIC_SCHEMA_REGISTRATION")
    assets = {"native-manifest.json": manifest_raw, "expression-oracle-plan.json": S.encode(expression),
              "expression-oracle.sql": oracle.emit_sql(manifest, expression, database="wa_p0c_rehearsal",
                                                        grantor="postgres").encode(),
              "public-schema-registration.json": S.encode(public)}
    return assets


def render_runtime(parent):
    compiled = parent.render_runtime(ROOT)
    S.require({name.rsplit("/", 1)[1]: S.sha(raw) for name, raw in compiled.items()} == PARENT_LAUNCHER_SHA,
              "EXACT_EXECUTED_TWO_LAUNCHER_REQUIRED")
    config, guard, runner = (compiled[leaf].decode() for leaf in parent.RUNTIME)
    repl = parent.v1.replace
    for old, new in (
        (parent.HISTORY, HISTORY), (parent.HISTORY_MANIFEST, HISTORY_MANIFEST),
        (parent.RUN_SCHEMA, RUN_SCHEMA), (parent.HISTORY_SCHEMA, HISTORY_SCHEMA),
        (parent.ATTESTATION_SCHEMA, ATTESTATION_SCHEMA), (parent.PURPOSE, PURPOSE),
        (parent.LABEL, LABEL), ("wa-p0c-cloud-two-history-", TARGET_PREFIX), (parent.EFFECTIVE, CATALOG_SHA),
        (parent.RUNTIME[0], RUNTIME[0]), (parent.RUNTIME[1], RUNTIME[1]), (parent.RUNTIME[2], RUNTIME[2]),
        ("wa-cloud-runtime-lease-history-v2-attestation.json", "wa-cloud-track-retained-base-v1-attestation.json"),
        ("history.public_source_archive_file_count===8", "history.public_source_archive_file_count===9"),
        ("Both exact applied checksums immutable; no resolve/baseline/direct ledger mutation in this family.", APPLIED_RULE),
        ('"initial_sql_sha256","append_sql_sha256","ordered_history_sha256"',
         '"initial_sql_sha256","append_sql_sha256","track_retained_sql_sha256","ordered_history_sha256"'),
        ("source.append_sql_sha256===APPEND && source.ordered_history_sha256===ORDERED_SHA",
         "source.append_sql_sha256===APPEND && source.track_retained_sql_sha256===TRACK_RETAINED && source.ordered_history_sha256===ORDERED_SHA"),
        *CONVERSION_CODES.items(),
    ):
        guard = repl(guard, old, new)
    guard = repl(guard, "export const ORDERED = [",
                 f'const TRACK_RETAINED = "{CANDIDATE_SHA}";\nexport const ORDERED = [')
    guard = repl(guard, "];\nexport const ORDERED_SHA =",
                 f'  {{id:"{MIGRATION}",path:HISTORY+"/{MIGRATION}/migration.sql",sha256:TRACK_RETAINED}},\n];\nexport const ORDERED_SHA =')
    S.require(runner.count(parent.OP_ARG) == 2, "FIXED_RUNNER_ENTRY_SURFACE")
    runner = runner.replace(parent.OP_ARG, OP_ARG)
    for old, new in ((parent.RESULT_SCHEMA, RESULT_SCHEMA), (parent.REFUSAL_SCHEMA, REFUSAL_SCHEMA)):
        runner = repl(runner, old, new)
    for old, new in CONVERSION_CODES.items():
        expected_count = 3 if old in ("EXACT_TWO_HISTORY_REQUIRED", "EXACT_TWO_SOURCE_PINS") else 1
        S.require(runner.count(old) == expected_count, "EXACT_REFUSAL_CODE_ANCHORS")
        runner = runner.replace(old, new)
    runner = repl(runner, "    summary.ordered_history_sha256 = attestation.planned.source.ordered_history_sha256;",
                  "    summary.track_retained_sql_sha256 = attestation.planned.source.track_retained_sql_sha256;\n"
                  "    summary.ordered_history_sha256 = attestation.planned.source.ordered_history_sha256;")
    return dict(zip(RUNTIME, (config.encode(), guard.encode(), runner.encode()), strict=True))


def history_rows():
    return [{"id": name, "path": f"{HISTORY}/{name}/migration.sql", "sha256": pin} for name, pin in FIXED_HISTORY]


def target_for(parent, run_id):
    S.require(type(run_id) is str and str(uuid.UUID(run_id)) == run_id and uuid.UUID(run_id).version == 4
              and run_id != PRIOR_RUN, "FRESH_DISTINCT_UUID4")
    container = TARGET_PREFIX + run_id
    return {**parent.target_for(run_id), "container_name": container, "volume_name": container + "-data",
            "labels": {"workinants.rehearsal": LABEL, "workinants.rehearsal.run": run_id}}


def compose(tool_archive, run_id):
    parent = reviewed_parent()
    target = target_for(parent, run_id)
    S.require(P.SCRATCH.resolve(strict=True) == P.SCRATCH, "EXACT_TRACK_SCRATCH")
    blobs, reviews = basis.capture()
    for name, pin in EXTRA_PINS.items():
        blobs[name] = S.pinned(ROOT, name, pin)
    for name in OWN_FILES:
        relative = f"{BASE}/{name}"
        blobs[relative] = S.read(ROOT / relative)
    accepted, previous, audit, review = qualification_basis(blobs)
    S.require(all(name in blobs and S.sha(blobs[name]) == pin for name, pin in previous["source_pins"].items()),
              "ACCEPTED_TWO_SOURCE_GRAPH_DRIFT")
    S.require(all(S.git(ROOT, "show", f"{CANDIDATE_COMMIT}:{name}") == blobs[name] for name in EXTRA_PINS
                  if name == GENERATOR or name.startswith(f"{RETAINED}/")), "PUBLISHED_CANDIDATE_COMMIT_BYTES")
    capability, _, _ = basis.capability(blobs)
    S.require(previous["daemon"] == audit["daemon"] == capability["daemon"]
              and previous["image"] == audit["image"] == capability["cached_image"], "CLOUD_ACCEPTED_PROFILE_IDENTITY")
    parser = P.parser_pin()
    S.require(parser["version"] == review["reproduced"]["parser_version"]
              and parser["files_aggregate_sha256"] == review["reproduced"]["parser_files_aggregate_sha256"],
              "EXACT_TRACK_REVIEWED_PARSER")
    assets = render_native(blobs, review)
    tools = parent.inspect_tools(ROOT, tool_archive)
    runtime = render_runtime(parent)
    S.require([(row["id"], row["sha256"]) for row in parent.ORDERED] == list(FIXED_HISTORY[:2]),
              "ACCEPTED_TWO_MIGRATION_IDS")
    order = history_rows()
    hashes = [row["sha256"] for row in order]
    S.require(hashes[:2] == accepted["actual_evidence"]["immutable_source8_history"]
              and hashes == review["reproduced"]["ordered_migration_sha256"], "ACCEPTED_TWO_THEN_TRACK_APPEND")
    files = {**runtime, parent.SCHEMA: blobs[parent.SCHEMA], f"{HISTORY}/migration_lock.toml": b'provider = "postgresql"\n',
             **dict(zip((row["path"] for row in order), (blobs[parent.v1.INITIAL_PATH], blobs[parent.v1.APPEND_PATH], blobs[APPEND]), strict=True))}
    manifest = {"schema": RUN_SCHEMA, "run_id": run_id, "purpose": PURPOSE, "target": target,
                "daemon": parent.exact_daemon(audit["daemon"]), "history": {"path": HISTORY, "ordered": order}, "tools": tools,
                "source": {"initial_sql_sha256": hashes[0], "append_sql_sha256": hashes[1], "track_retained_sql_sha256": hashes[2],
                           "ordered_history_sha256": S.sha(parent.canonical(order)), "effective_expected_sha256": CATALOG_SHA,
                           "foundation_schema_sha256": parent.SCHEMA_SHA,
                           "runtime_files_sha256": {name: S.sha(raw) for name, raw in runtime.items()}}}
    manifest_raw = parent.encoded(manifest)
    files[HISTORY_MANIFEST] = parent.encoded({
        "schema": HISTORY_SCHEMA, "scope": "PROVISIONAL_CLOUD_ONLY_NOT_HOSTED_ADOPTION", "run_id": run_id,
        "run_manifest_sha256": S.sha(manifest_raw), "migrations": HISTORY, "ordered": order,
        "ordered_history_sha256": manifest["source"]["ordered_history_sha256"], "effective_expected_sha256": CATALOG_SHA,
        "foundation_schema": parent.SCHEMA, "files_sha256": {name: S.sha(raw) for name, raw in files.items()},
        "public_source_archive_file_count": 9, "database_contacted": False, "ledger_created_or_modified": False,
        "raw_structure_applied_separately": False, "applied_history_rule": APPLIED_RULE,
    })
    S.require(len(files) == 9 and all(S.sha(files[row["path"]]) == row["sha256"] for row in order),
              "EXACT_NINE_SOURCE_FILES")
    archive = parent.archive_source(files)
    base_dir = P.SCRATCH / f"wa-cloud-f0-track-retained-base-{run_id}"
    files_sha = {name: S.sha(raw) for name, raw in blobs.items()}
    profile = S.unique_json(blobs[f"{basis.PROBE}/profile.json"])
    profile["credential_tmpfs_options"] = target["bootstrap"]["tmpfs_options"]
    packet = {"schema": PACKET_SCHEMA, "status": "HELD_SOURCE_DRAFT_NOT_RUN", "posture": "D", "run_id": run_id,
              "assertion_promotions": 0, "business_tests_executed": False, "runtime_authority": False,
              "independent_source_and_literal_review_required": True, "prior_closed_run": PRIOR_RUN,
              "prior_closed_container_id": audit["created_container_id"], "candidate_commit": CANDIDATE_COMMIT,
              "source_reviews": reviews,
              "source_files_sha256": files_sha, "source_aggregate_sha256": S.aggregate(files_sha),
              "parser": parser, "target": target, "profile": profile, "daemon": audit["daemon"], "image": audit["image"],
              "tools": {"path": str(tool_archive), "sha256": parent.TOOL_TAR_SHA, "bytes": parent.TOOL_TAR_SIZE, "files": 10300},
              "nested_manifest": P.bind(base_dir / "run-manifest.json", manifest_raw),
              "archive": P.bind(base_dir / "source9.tar", archive), "source9_sha256": {path: S.sha(raw) for path, raw in files.items()},
              "native_assets_sha256": {path: S.sha(raw) for path, raw in assets.items()}, "native_expected_sha256": CATALOG_SHA,
              "native_catalog_posture": "ORIGINAL_GRANTOR_FINALIZED_AND_ISOLATED_SCRAM_LOGINS_ACTIVATED",
              "ledger_expected": order, "tooling_claim": "EXACT_ARCHIVED_CLOUD_V2_TOOL_FILES_ONLY",
              "unchanged_original_sql_sha256": {name: files_sha[name] for name in (
                  ORIGINAL_BOOTSTRAP, ORIGINAL_FINALIZER, LEDGER_COLLECTOR, FINGERPRINT_COLLECTOR)}}
    return base_dir, packet, manifest_raw, archive, files, assets


def prepare(tool_archive):
    directory, packet, manifest, archive, files, assets = compose(tool_archive, str(uuid.uuid4()))
    directory.mkdir(mode=0o700)
    for name, raw in {"run-manifest.json": manifest, "source9.tar": archive, "operation.json": S.encode(packet)}.items():
        P.write_new(directory / name, raw)
    P.write_source(directory / "source9", files)
    P.write_source(directory / "native", assets)
    return directory / "operation.json", packet


def read_closed(path):
    S.require(path.parent.parent == P.SCRATCH and path.name == "operation.json", "TRACK_PACKET_SCRATCH_SCOPE")
    P.private_path(path.parent, file=False)
    S.require({entry.name for entry in path.parent.iterdir()} == {"operation.json", "run-manifest.json", "source9.tar",
                                                                 "source9", "native"}, "TRACK_PACKET_EXACT_TREE")
    raw = S.read(P.private_path(path, file=True))
    value = S.unique_json(raw)
    S.require(value["schema"] == PACKET_SCHEMA and value["status"] == "HELD_SOURCE_DRAFT_NOT_RUN", "HELD_TRACK_DRAFT_REQUIRED")
    directory, packet, manifest, archive, source, assets = compose(Path(value["tools"]["path"]), value["run_id"])
    S.require(path == directory / "operation.json" and raw == S.encode(packet), "EXACT_OPERATION_READBACK")
    S.require(S.read(P.private_path(directory / "run-manifest.json", file=True)) == manifest
              and S.read(P.private_path(directory / "source9.tar", file=True)) == archive, "EXACT_ARCHIVE_AND_MANIFEST_READBACK")
    for name, files in (("source9", source), ("native", assets)):
        tree = P.private_path(directory / name, file=False)
        nodes = list(tree.rglob("*"))
        S.require(all(not path.is_symlink() and (path.is_file() or path.is_dir()) for path in nodes), "OWNED_TREE_SHAPE")
        actual = {p.relative_to(tree).as_posix(): S.read(P.private_path(p, file=True)) for p in nodes if p.is_file()}
        directories = {P.private_path(p, file=False).relative_to(tree) for p in nodes if p.is_dir()}
        S.require(actual == files and directories == {part for path in files for part in Path(path).parents if part != Path(".")},
                  "EXACT_OWNED_TREE_READBACK")
    return packet


def main():
    cli = argparse.ArgumentParser(description=__doc__)
    sub = cli.add_subparsers(dest="command", required=True)
    sub.add_parser("prepare").add_argument("--tool-archive", required=True, type=Path)
    sub.add_parser("verify").add_argument("packet", type=Path)
    args = cli.parse_args()
    try:
        path, data = prepare(args.tool_archive) if args.command == "prepare" else (args.packet, read_closed(args.packet))
        print(S.encode({"packet": str(path), "sha256": S.sha(S.encode(data)), "runtime": "NOT_RUN",
                        "source_files": len(data["source_files_sha256"]), "archive_files": len(data["source9_sha256"])}).decode(), end="")
        return 0
    except Exception as error:
        code = str(error)
        if not re.fullmatch(r"[A-Z0-9_]{1,100}", code):
            code = "TRACK_SOURCE_DRAFT_UNCONFIRMED"
        print(S.encode({"status": "HELD", "code": code, "runtime": "NOT_RUN"}).decode(), end="")
        return 1


if __name__ == "__main__":
    sys.exit(main())
