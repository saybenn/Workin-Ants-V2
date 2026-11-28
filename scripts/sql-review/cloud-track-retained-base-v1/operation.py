"""Own one independently reviewed, disposable Cloud three-migration rehearsal."""

import argparse
import ast
import os
from pathlib import Path
import signal
import sys
from types import ModuleType, SimpleNamespace
import uuid

import candidate_profile as candidate
import three_proof as proof


S, P = candidate.S, candidate.P
ROOT = candidate.ROOT
OWNER_COMMIT = "464caba083c2c53dd158af027df2af933a0bdc18"
OWNER_PINS = {
    "basis.py": "e19319429a5b97fc594f91b882229f767964e4f9dd96891a9b9ebcaa9a4280af",
    "plan.py": "c308295d97ab1d794cf3a7a8b2f241b1c7266b8cb606704ada6f2c3de9c1decb",
    "operation.py": "8680611ab98322a192a70c72f373b1fb4858ddbbd184c1dc4f450bb98823b0c0",
}
OWNER_FILES = ("operation.py", "test_owned_operation.py", "OPERATION.md")
SCHEMA = "workinants.cloud-f0-track-retained-base-owned-operation.v1"
RESULT_SCHEMA = "workinants.cloud-f0-track-retained-base-owned-result.v1"
RESULT_FILE = "track-retained-base-results.json"
PASS = "PASS_TRACK_THREE_MIGRATION_MACHINERY_ONLY"
EXECUTE = "--execute-reviewed-cloud-f0-track-retained-base-owned-v1"
PREFINAL = "GENUINE_THREE_FILE_DEPLOY"
SOURCE_SCOPES = ["accepted_cloud_owner_and_closed_three_history_sources", "candidate_native_and_ledger_authority",
                 "exact_track_leaf_handoff_and_restoration", "bounded_receipts_first_failure_and_cleanup"]
LITERAL_SCOPES = ["actual_cloud_daemon_image_and_fresh_owned_target", "stdin_tmpfs_no_network_and_exact_tool_archive",
                  "three_genuine_migrator_rows_and_original_grantor", "native_oracle_status_and_noop_only",
                  "all_client_closure_and_exact_owned_cleanup"]
BASE_ENTRIES = {"operation.json", "run-manifest.json", "source9.tar", "source9", "native"}


def mechanisms(blobs):
    """Load the exact executed TWO modules in an isolated Python namespace."""
    modules, installed = [], []
    try:
        for leaf, digest in OWNER_PINS.items():
            relative = f"{candidate.TWO}/{leaf}"
            raw = blobs[relative]
            S.require(S.sha(raw) == digest and raw == S.git(ROOT, "show", f"{OWNER_COMMIT}:{relative}"),
                      "EXACT_ACCEPTED_TWO_OWNER_SOURCE")
            name = "_track_inherited_owner" if leaf == "operation.py" else leaf.removesuffix(".py")
            S.require(name not in sys.modules, "TRACK_OWNER_IMPORT_COLLISION")
            module = ModuleType(name)
            module.__file__ = str(ROOT / relative)
            sys.modules[name] = module
            installed.append(name)
            exec(compile(raw, module.__file__, "exec", dont_inherit=True), module.__dict__)
            modules.append(module)
    finally:
        for name in installed:
            del sys.modules[name]
    return modules[-1]


def adapt_inner(parent):
    # The owning transport stays unchanged. Only the finite Track runner
    # namespace, exact ordered files and typed terminal refusal codes differ.
    return SimpleNamespace(
        BASE=candidate.BASE, SCHEMA=parent.SCHEMA, HISTORY=candidate.HISTORY, ORDERED=candidate.history_rows(),
        HISTORY_MANIFEST=candidate.HISTORY_MANIFEST, RUNTIME=candidate.RUNTIME, ENDPOINT=parent.ENDPOINT,
        OP_ARG=candidate.OP_ARG, RESULT_SCHEMA=candidate.RESULT_SCHEMA, REFUSAL_SCHEMA=candidate.REFUSAL_SCHEMA,
        attest=proof.attestation, REFUSAL_CAUSE_CODES=parent.REFUSAL_CAUSE_CODES,
        CLOSED_REFUSAL_PHASE_CODES={phase: tuple(candidate.CONVERSION_CODES.get(code, code) for code in codes)
                                    for phase, codes in parent.CLOSED_REFUSAL_PHASE_CODES.items()},
    )


def compose(tool_archive, run_id, *, draft=False):
    _, held, nested, archive, files, native = candidate.compose(tool_archive, run_id)
    blobs = {name: S.pinned(ROOT, name, digest) for name, digest in held["source_files_sha256"].items()}
    blobs.update({f"{candidate.BASE}/{name}": S.read(candidate.HERE / name) for name in OWNER_FILES})
    previous = S.unique_json(blobs[f"{candidate.PRIOR}/operation.json"])
    directory = P.SCRATCH / f"wa-cloud-f0-track-retained-base-owned-{run_id}"
    hashes = {name: S.sha(raw) for name, raw in blobs.items()}
    operation = {
        "schema": SCHEMA, "status": "SOURCE_DRAFT_NOT_RUN" if draft else "HELD_PENDING_EXACT_TRACK_REVIEW",
        "run_id": run_id, "source": None if draft else S.verify_committed(ROOT, blobs), "source_pins": hashes,
        "source_aggregate_sha256": S.aggregate(hashes), "posture": "D", "assertion_promotions": 0,
        "candidate_adoption": False, "business_tests_executed": False,
        "prior_two_acceptance_sha256": candidate.EXTRA_PINS[f"{candidate.PRIOR}/acceptance.json"],
        "held_profile_sha256": S.sha(S.encode(held)), "prior_closed_container_id": held["prior_closed_container_id"],
        "candidate_commit": held["candidate_commit"], "candidate_review_sha256": candidate.EXTRA_PINS[candidate.REVIEW],
        "profile": held["profile"], "target": held["target"], "daemon": held["daemon"], "image": held["image"],
        "parser": held["parser"], "tools": held["tools"], "database": proof.DATABASE,
        "nested_manifest": P.bind(directory / "run-manifest.json", nested), "archive": P.bind(directory / "source9.tar", archive),
        "source9": held["source9_sha256"], "ledger_expected": held["ledger_expected"],
        "native_files_sha256": previous["native_files_sha256"],  # Exact inherited startup/source preflight assets.
        "track_native_files_sha256": held["native_assets_sha256"], "native_expected_sha256": candidate.CATALOG_SHA,
        "expected_expression_count": 416, "historical_reviews_supply_execution_authority": False,
        "runtime_cases": dict.fromkeys(("same_live_daemon_and_owned_startup", "pre_finalization_track_authority",
                                        "genuine_three_migrations_and_ledger", "original_grantor_restoration",
                                        "native_catalog_oracle_and_noop", "exact_owned_cleanup"), "NOT_RUN"),
    }
    two = mechanisms(blobs)
    steps = track_steps(blobs[S.STEPS])
    inner = adapt_inner(candidate.reviewed_parent())
    prepared = (directory, operation, blobs, inner, S.unique_json(nested), nested, files, archive)
    return prepared, two, steps, native


def prepare(tool_archive, *, draft=False):
    (directory, operation, _, _, _, nested, files, archive), _, _, native = compose(tool_archive, str(uuid.uuid4()), draft=draft)
    directory.mkdir(mode=0o700)
    for leaf, raw in {"run-manifest.json": nested, "source9.tar": archive, "operation.json": S.encode(operation)}.items():
        P.write_new(directory / leaf, raw)
    P.write_source(directory / "source9", files)
    P.write_source(directory / "native", native)
    return directory / "operation.json", operation


def exact_tree(root, files):
    P.private_path(root, file=False)
    inventory = tuple(root.rglob("*"))
    S.require(all(not path.is_symlink() and (path.is_file() or path.is_dir()) for path in inventory), "TRACK_OWNED_TREE_SHAPE")
    observed = {path.relative_to(root).as_posix(): S.read(P.private_path(path, file=True)) for path in inventory if path.is_file()}
    directories = {P.private_path(path, file=False).relative_to(root) for path in inventory if path.is_dir()}
    S.require(observed == files and directories == {part for name in files for part in Path(name).parents if part != Path(".")},
              "TRACK_OWNED_TREE_READBACK")


def compare_source9(directory, nested, files, archive):
    S.require(S.read(P.private_path(directory / "run-manifest.json", file=True)) == nested
              and S.read(P.private_path(directory / "source9.tar", file=True)) == archive, "TRACK_SOURCE9_ARCHIVE_READBACK")
    exact_tree(directory / "source9", files)


def read_closed(path, *, draft=False):
    S.require(path.parent.parent == P.SCRATCH and path.name == "operation.json", "TRACK_OWNED_PACKET_SCOPE")
    P.private_path(path.parent, file=False)
    raw = S.read(P.private_path(path, file=True))
    value = S.unique_json(raw)
    S.require(value["schema"] == SCHEMA and value["status"] == (
        "SOURCE_DRAFT_NOT_RUN" if draft else "HELD_PENDING_EXACT_TRACK_REVIEW"), "TRACK_COMMITTED_OWNED_PACKET_REQUIRED")
    prepared, two, steps, native = compose(Path(value["tools"]["path"]), value["run_id"], draft=draft)
    directory, expected, _, _, _, nested, files, archive = prepared
    S.require(path == directory / "operation.json" and raw == S.encode(expected), "TRACK_OWNED_PACKET_DRIFT")
    compare_source9(directory, nested, files, archive)
    exact_tree(directory / "native", native)
    return prepared, two, steps, native, raw


def review_bindings(plan, raw):
    return {
        "packet_sha256": S.sha(raw), "source_commit": plan["source"]["commit"], "source_tree": plan["source"]["tree"],
        "operation_run_id": plan["run_id"], "all_sources_sha256": plan["source_aggregate_sha256"],
        "nested_plan_sha256": plan["nested_manifest"]["sha256"], "source_archive_sha256": plan["archive"]["sha256"],
        "tool_archive_sha256": plan["tools"]["sha256"], "prior_two_acceptance_sha256": plan["prior_two_acceptance_sha256"],
        "candidate_review_sha256": plan["candidate_review_sha256"], "candidate_native_sha256": plan["native_expected_sha256"],
    }


def exact_reviews(directory, plan, raw):
    bindings = review_bindings(plan, raw)
    source, source_hash = P.read_review(directory / "source-review.json",
        schema="workinants.cloud-f0-track-retained-base-source-review.v1", bindings=bindings, scopes=SOURCE_SCOPES)
    literal, literal_hash = P.read_review(directory / "literal-review.json",
        schema="workinants.cloud-f0-track-retained-base-literal-review.v1",
        bindings={**bindings, "source_review_sha256": source_hash}, scopes=LITERAL_SCOPES)
    S.require(source["source_author"] == literal["source_author"], "TRACK_REVIEWED_AUTHOR_IDENTITY")
    return {"source": source_hash, "literal": literal_hash,
            "source_reviewer": source["reviewer"], "literal_reviewer": literal["reviewer"]}


def attempt_receipt(plan, raw, reviews):
    return S.encode({"run_id": plan["run_id"], "packet_sha256": S.sha(raw), "reviews": reviews})


def track_steps(raw):
    """Change only the versioned proof and evidence seams in the accepted main."""
    S.require(S.sha(raw) == S.HISTORICAL_PINS[S.STEPS], "TRACK_EXACT_INHERITED_STEPS")
    selected = {node.name: node for node in ast.parse(raw).body if isinstance(node, ast.FunctionDef)
                and node.name in ("main", "activate_runtime")}
    S.require(set(selected) == {"main", "activate_runtime"}, "TRACK_EXACT_STAGE_FUNCTIONS")
    main = selected["main"]

    def literal(function, old, new, count=1):
        values = [node for node in ast.walk(function) if isinstance(node, ast.Constant) and node.value == old]
        S.require(len(values) == count, "TRACK_EXACT_STAGE_LITERALS")
        for node in values:
            node.value = new

    literal(selected["activate_runtime"], "two_applied_verified", "three_applied_verified")
    for old, new, count in (
        ("two_applied_verified", "three_applied_verified", 1), ("initial_two_rows", "initial_three_rows", 1),
        ("GENUINE_TWO_FILE_DEPLOY", PREFINAL, 1), ("PASS_TWO_APPLIED_ROWS", "PASS_THREE_APPLIED_ROWS", 1),
        ("PASS_TWO_GENUINE_APPLIED_ROWS", "PASS_THREE_GENUINE_APPLIED_ROWS", 1),
        ("PASS_BASELINE_TWO_FULL_ROWS", "PASS_BASELINE_THREE_FULL_ROWS", 1),
        ("two-history-results.json", RESULT_FILE, 1), ("workinants.runtime-lease-two-history-owned-results.v1", RESULT_SCHEMA, 1),
        ("PASS_MACHINERY_SUBSET_ONLY", PASS, 3),
    ):
        literal(main, old, new, count)

    def call(node, name):
        return (isinstance(node, ast.Expr) and isinstance(node.value, ast.Call)
                and isinstance(node.value.func, ast.Name) and node.value.func.id == name)

    outer, = (item for item in main.body if isinstance(item, ast.Try) and item.finalbody)
    first, = (item for item in outer.body if isinstance(item, ast.Try) and len(item.finalbody) == 1
              and call(item.finalbody[0], "ensure_cleanup"))
    S.require(not first.handlers and len(first.body) == 3 and isinstance(first.body[0], ast.Assign)
              and isinstance(first.body[0].targets[0], ast.Name) and first.body[0].targets[0].id == "installed"
              and sum(call(item, "bootstrap") for item in outer.body[:outer.body.index(first)]) == 1,
              "TRACK_PRE_FINALIZATION_INSERTION")
    index = outer.body.index(first)
    outer.body[index:index + 1] = [ast.parse("track_pre_deploy()").body[0], first, ast.parse("track_post_finalization()").body[0]]
    first.body.insert(1, ast.parse("track_pre_finalization(installed)").body[0])
    first.handlers = ast.parse("""try:
    pass
except BaseException as error:
    if FIRST_OPERATION_FAILURE is None:
        _required_safety_first_exception(error, report.get('stage','ENTRY'))
    raise
""").body[0].handlers
    terminal, = (item for item in outer.body if call(item, "event") and item.value.args[0].value == "NOOP")
    outer.body.insert(outer.body.index(terminal), ast.parse("track_proof = track_terminal(installed, before, after)").body[0])
    summary, = (node for node in ast.walk(main) if isinstance(node, ast.Dict) and
                any(isinstance(key, ast.Constant) and key.value == "full8_noop" for key in node.keys))
    summary.keys.append(ast.Constant(value="track"))
    summary.values.append(ast.Name(id="track_proof", ctx=ast.Load()))
    S.require(sum(call(node, "cleanup") for part in outer.finalbody for node in ast.walk(part)) == 1,
              "TRACK_EXACT_OWNED_CLEANUP_SEAM")
    return compile(ast.fix_missing_locations(ast.Module(body=list(selected.values()), type_ignores=[])), S.STEPS, "exec")


def track_result(original):
    def validate(result, validator, manifest, observed, operation, raw, authorization, inner):
        S.require(type(result.returncode) is int and result.returncode in (0, 1) and result.stderr == b""
                  and type(result.stdout) is bytes and 0 < len(result.stdout) <= 65536, "CLOUD_RUNNER_RESPONSE")
        value = S.unique_json(result.stdout)
        S.require(type(value) is dict, "CLOUD_RUNNER_RESPONSE")
        if value.get("schema") == inner.REFUSAL_SCHEMA:
            return original(result, validator, manifest, observed, operation, raw, authorization, inner)
        S.require(value.get("track_retained_sql_sha256") == manifest["source"]["track_retained_sql_sha256"]
                  == candidate.CANDIDATE_SHA, "TRACK_MIGRATION_RESULT_BINDING")
        projected = type(result)(result.returncode, S.encode({key: val for key, val in value.items()
                                                             if key != "track_retained_sql_sha256"}), result.stderr)
        original(projected, validator, manifest, observed, operation, raw, authorization, inner)
        return value
    return validate


def owner_type(two, steps, native):
    two.compare_source8 = compare_source9  # Override only this isolated module's host source lookup.
    two.validate_result = track_result(two.validate_result)

    class Owner(two.Owner):
        def configure_program(self):
            super().configure_program()
            p = self.program
            self.report["schema"] = "workinants.cloud-f0-track-retained-base-owned-run-evidence.v1"
            self.report["track_authority"] = {}
            self.report["limits"].update(candidate_history_only=True, track_business_cases="NOT_RUN")
            p.EXPECTED_SHA = candidate.CATALOG_SHA
            p.MANIFEST["migration_target"]["source_snapshot"] = str(self.directory / "source9")
            p.__dict__.update(track_pre_deploy=lambda: self.track_authority("PRE_DEPLOY"),
                              track_pre_finalization=self.track_pre_finalization,
                              track_post_finalization=lambda: self.track_authority("POST_FINALIZATION"),
                              track_terminal=self.track_terminal, compare_ledger=self.compare_ledger)
            exec(steps, p.__dict__)
            p.SAFE_FAILURE_STAGES |= {
                PREFINAL, "TRACK_SOURCE", "TRACK_PRE_DEPLOY", "TRACK_PRE_FINALIZATION", "TRACK_POST_FINALIZATION",
                "TRACK_POST_NOOP", "TRACK_TERMINAL", "NATIVE_TRACK_PRE_FINALIZATION_BEFORE",
                "NATIVE_TRACK_PRE_FINALIZATION_AFTER", "LEDGER_TRACK_PRE_FINALIZATION", "LEDGER_FINGERPRINT_track-before-finalization",
            }
            p.SAFE_FAILURE_CODES |= {
                "TRACK_LIVE_TARGET_ALREADY_CLOSED", "TRACK_NATIVE_ASSETS_DRIFT", "TRACK_PRE_FINALIZATION_LEDGER_DRIFT",
                "TRACK_AUTHORITY_PHASE", "TRACK_LEAF_MEMBERSHIP_OR_RESTORATION_DRIFT", "STABLE_CANDIDATE_FUNCTION_OWNERS",
                "TRACK_NATIVE_THREE_ROW_LEDGER_REFUSED", "EXACT_THREE_MIGRATION_REGISTRATION", "EXACT_THREE_APPLIED_ROWS",
                "EXACT_PREVIOUSLY_REVIEWED_LEDGER_TOOL_METADATA", "TRACK_MIGRATION_RESULT_BINDING", "TRACK_ATTESTATION_SIZE",
                "EXACT_TRACK_LIVE_OBSERVATION", "EXACT_TRACK_LIVE_AUTHORIZATION", "TRACK_SOURCE9_ARCHIVE_READBACK",
                "TRACK_OWNED_TREE_SHAPE", "TRACK_OWNED_TREE_READBACK", "TRACK_FINGERPRINT_MIGRATION_ORDER",
                "TRACK_FINGERPRINT_FIELDS", "TRACK_FINGERPRINT_CONTEXT", "EXACT_THREE_FULL_ROW_FINGERPRINTS",
                "TRACK_FINGERPRINT_EXACT_HISTORY", "NOOP_CHANGED_A_FULL_TRACK_LEDGER_ROW", "TRACK_THREE_NATIVE_ORACLE_PROOF",
                "TRACK_GENUINE_MIGRATION_SEQUENCE", "TRACK_AUTHORITY_OBSERVATION_CONTEXT", "TRACK_REQUIRED_AUTHORITY_PROOF",
            }

        def verify_packet(self):
            super().verify_packet()
            p = self.program
            self.report["stage"] = "TRACK_SOURCE"
            exact_tree(self.directory / "native", native)
            expected = S.unique_json(native["native-manifest.json"])
            order = self.operation["ledger_expected"]
            S.require(expected["expected_sha256"] == candidate.CATALOG_SHA and order == candidate.history_rows()
                      and {name: S.sha(raw) for name, raw in native.items()} == self.operation["track_native_files_sha256"],
                      "TRACK_NATIVE_ASSETS_DRIFT")

            def registration(ledger, *, root, run_id, target_attestation_sha256, source_expected_sha256):
                S.require(source_expected_sha256 == candidate.CATALOG_SHA, "TRACK_NATIVE_ASSETS_DRIFT")
                return proof.registration(ledger, order, source_root=root, run_id=run_id, attestation_sha256=target_attestation_sha256)

            def compare_noop(before, after):
                return {**proof.unchanged_noop(before, after, order), "status": "PASS_EXACT_THREE_ROW_HASH_PRESERVATION_ONLY",
                        "history_count": 3, "database_qualification_claimed": False}

            p.CATALOG.update(expected=expected, plan=S.unique_json(native["expression-oracle-plan.json"]),
                             public=S.unique_json(native["public-schema-registration.json"]),
                             oracle_sql=native["expression-oracle.sql"].decode("utf-8"),
                             two=SimpleNamespace(registration=registration, fingerprint_shape=lambda observation: proof.fingerprints(observation, order),
                                                 compare_noop=compare_noop))
            p.CATALOG["strings"], p.CATALOG["generated_names"] = p.metadata_allowlist(expected, p.CATALOG["tools"])
            self.report["source_verification"].update(native_sha256=candidate.CATALOG_SHA, original_two_source_preflight=True,
                                                       exact_three_migration_source_readback=True)
            p.event("TRACK_SOURCE", "PASS_EXACT_THREE_HISTORY_SOURCE")

        def provision(self):
            super().provision()
            S.require(self.resources.cid != self.operation["prior_closed_container_id"], "TRACK_LIVE_TARGET_ALREADY_CLOSED")

        def observed_target(self):
            actual = super().observed_target()
            S.require(actual["container_id"] != self.operation["prior_closed_container_id"], "TRACK_LIVE_TARGET_ALREADY_CLOSED")
            return actual

        def track_authority(self, timing):
            p = self.program
            stage = f"TRACK_{timing}"
            self.report["stage"] = stage
            S.require(not self.transport.unknown and self.resources.cid is not None
                      and (timing not in ("POST_FINALIZATION", "POST_NOOP") or p.STATE.get("finalization_verified") is True),
                      "TRACK_AUTHORITY_OBSERVATION_CONTEXT")
            result = p.run_catalog_query(self.name, proof.AUTHORITY_SQL, stage)
            p.successful_query(result)
            rows = p.records(result.stdout)
            S.require(len(rows) == 1 and timing not in self.report["track_authority"], "TRACK_AUTHORITY_OBSERVATION_CONTEXT")
            closure = proof.authority(rows[0], p.CATALOG["expected"], timing=timing)
            self.report["track_authority"][timing] = closure
            p.write_safe(timing.lower().replace("_", "-") + "-track-authority.json", rows[0])
            p.event(stage, "PASS_EXACT_TRACK_INSTALLATION_AUTHORITY")
            return closure

        def compare_ledger(self, registered, observation, snapshot):
            p = self.program
            evidence, result = proof.verify_ledger(p.CATALOG["tools"]["prisma_ledger_proof"], registered, observation,
                                                   snapshot, snapshot, self.directory / "source9")
            return result, evidence

        def track_pre_finalization(self, installed):
            p = self.program
            self.track_authority("PRE_FINALIZATION")
            before = p.collect_native(self.name, "NATIVE_TRACK_PRE_FINALIZATION_BEFORE", "track-prefinal-native-before.json")
            reg, ledger = p.ledger_observation(installed, "TRACK_PRE_FINALIZATION")
            after = p.collect_native(self.name, "NATIVE_TRACK_PRE_FINALIZATION_AFTER", "track-prefinal-native-after.json")
            S.require(before == after, "TRACK_PRE_FINALIZATION_LEDGER_DRIFT")
            checked, evidence = self.compare_ledger(reg, ledger, after)
            p.write_safe("track-prefinal-ledger-registration.json", reg)
            p.write_safe("track-prefinal-ledger-evidence.json", evidence)
            p.write_safe("track-prefinal-ledger-comparison.json", checked)
            p.STATE["track_prefinal_fingerprints"] = p.fingerprints("track-before-finalization")
            self.report["track_pre_finalization"] = {"same_read_only_native_snapshot": True, "native_sha256": p.digest(before),
                "ledger_checks": len(checked["checks"]), "applied_rows": len(reg["history_expected"])}
            p.event("TRACK_PRE_FINALIZATION", "PASS_THREE_ROWS_AND_EXACT_TRACK_VERIFIER")

        def track_terminal(self, installed, before, after):
            p = self.program
            self.report["stage"] = "TRACK_TERMINAL"
            records = self.report.get("migration_results", [])
            S.require(not self.transport.unknown and records and records[0] == installed
                      and [rec["operation"] for rec in records] == ["deploy", "status", "deploy"]
                      and all(rec["status"] == proof.RESULT_COMPLETE and rec["exit_code"] == 0
                              and rec["container_id"] == self.resources.cid and rec["run_id"] == self.operation["run_id"]
                              and rec["packet_sha256"] == S.sha(self.raw) for rec in records)
                      and records[-1]["no_pending_message_observed"] is True, "TRACK_GENUINE_MIGRATION_SEQUENCE")
            receipts = self.report["native_results"]
            expected_counts = ({"PASS": 29089}, 3, 22, 416)
            S.require(set(receipts) == {"initial", "noop"}
                      and receipts["initial"]["native_sha256"] == receipts["noop"]["native_sha256"]
                      and all(S.encode(tuple(rec[key] for key in ("catalog_check_counts", "applied_rows", "ledger_checks", "oracle_expressions")))
                              == S.encode(expected_counts) for rec in receipts.values()), "TRACK_THREE_NATIVE_ORACLE_PROOF")
            proof.unchanged_noop(p.STATE["track_prefinal_fingerprints"], before, self.operation["ledger_expected"])
            proof.unchanged_noop(before, after, self.operation["ledger_expected"])
            self.track_authority("POST_NOOP")
            S.require(p.STATE.get("three_applied_verified") is True and p.STATE.get("activated") is True
                      and self.report["targets"][self.name]["finalization"] == "PASS"
                      and set(self.report["track_authority"]) == {"PRE_DEPLOY", "PRE_FINALIZATION", "POST_FINALIZATION", "POST_NOOP"},
                      "TRACK_REQUIRED_AUTHORITY_PROOF")
            return {"three_applied_historical_order": self.operation["ledger_expected"],
                    "authority": self.report["track_authority"], "pre_finalization": self.report["track_pre_finalization"],
                    "finalization_and_noop_preserved_all_eight_ledger_columns": True,
                    "cleanup_acceptance_requires_final_evidence": True, "business_cases": "NOT_RUN"}

        def cleanup(self):
            super().cleanup()
            self.report["steps"]["TRACK-HISTORY-CLEANUP"] = self.report["steps"].pop("TWO-HISTORY-CLEANUP")

        def postchecks(self):
            prepared, _, _, _, raw = read_closed(self.directory / "operation.json")
            S.require(raw == self.raw and prepared[1] == self.operation
                      and exact_reviews(self.directory, self.operation, self.raw) == self.reviews
                      and S.read(P.private_path(self.directory / "attempt.json", file=True))
                          == attempt_receipt(self.operation, self.raw, self.reviews),
                      "CLOUD_OWNING_SOURCE_REVIEW_DRIFT")
            self.report["immutable_source_postcheck"] = "PASS"
            if self.transport.unknown:
                self.report["postcheck_remote_uncertainty_retained"] = True
                if self.report["status"] == PASS:
                    self.program.record_failure("POSTCHECKS", "CLOUD_STICKY_TRANSPORT_UNCERTAINTY")

    return Owner


def execute(path, *, explicitly_reviewed):
    S.require(explicitly_reviewed is True, "EXPLICIT_TRACK_OWNED_EXECUTION_REQUIRED")
    prepared, two, steps, native, raw = read_closed(path)
    directory, operation, *_ = prepared
    reviews = exact_reviews(directory, operation, raw)
    S.require({entry.name for entry in directory.iterdir()} == BASE_ENTRIES | {"source-review.json", "literal-review.json"},
              "FRESH_TRACK_EXECUTION_DIRECTORY_REQUIRED")
    os.umask(0o077)
    P.write_new(directory / "attempt.json", attempt_receipt(operation, raw, reviews))
    signal.signal(signal.SIGTERM, two.interrupt)
    signal.signal(signal.SIGHUP, two.interrupt)
    return owner_type(two, steps, native)(prepared, raw, reviews).run()


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    actions = parser.add_subparsers(dest="action", required=True)
    make = actions.add_parser("prepare")
    make.add_argument("--draft", action="store_true")
    make.add_argument("--tool-archive", type=Path, required=True)
    verify = actions.add_parser("verify")
    verify.add_argument("--draft", action="store_true")
    verify.add_argument("--packet", type=Path, required=True)
    operate = actions.add_parser("execute")
    operate.add_argument(EXECUTE, action="store_true", dest="approved")
    operate.add_argument("--packet", type=Path, required=True)
    args = parser.parse_args(argv)
    try:
        if args.action == "execute":
            return execute(args.packet, explicitly_reviewed=args.approved)
        packet, value = prepare(args.tool_archive, draft=args.draft) if args.action == "prepare" else (args.packet, read_closed(args.packet, draft=args.draft)[0][1])
        print(S.encode({"packet": str(packet), "state": value["status"], "sha256": S.sha(S.encode(value)),
                        "runtime": "NOT_RUN", "source_files": len(value["source_pins"]), "source_archive_files": len(value["source9"])}).decode(), end="")
        return 0
    except BaseException as error:
        print(S.encode({"status": "HELD_OR_STOPPED", "code": candidate.basis.safe_code(error),
                        "runtime_pass_claimed": False}).decode(), end="")
        return 1


if __name__ == "__main__":
    sys.exit(main())
