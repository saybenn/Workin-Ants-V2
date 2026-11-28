"""Offline checks for the closed files, native ledger receipts and lifecycle model."""

from copy import deepcopy
import io
from pathlib import Path
import subprocess
import tarfile
from tempfile import TemporaryDirectory
from types import SimpleNamespace
import unittest

from pglast import parse_sql

import candidate_profile as C
import three_proof as P


S = C.S
RUNTIME_ARCHIVE = Path("/workspace/scratch/workin-ants-cloud-f0-tools-v2-verified.EdsdbM/pinned-prisma-tools-cloud-v2.tar.gz")
RUN_ID = "77777777-7777-4777-8777-777777777777"
PIN = "a" * 64
LEDGER = "scripts/sql-review/prisma_ledger_proof.py"


def value(item):
    return lambda: deepcopy(item)


def stopped(code):
    def fail():
        raise S.Held(code)
    return fail


class ThreeHistoryTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        _, cls.packet, raw, cls.archive, cls.files, cls.assets = C.compose(RUNTIME_ARCHIVE, RUN_ID)
        cls.manifest = S.unique_json(raw)
        cls.native = S.unique_json(cls.assets["native-manifest.json"])
        cls.scope = {key: deepcopy(cls.manifest["target"][key]) for key in
                     ("container_name", "volume_name", "image", "network", "labels", "bootstrap")}
        cls.scope.update(endpoint="unix:///var/run/docker.sock", daemon=cls.manifest["daemon"],
                         container_id="b" * 64, volume_created_at="2000-01-01T00:00:00.000000000Z",
                         image_id=cls.packet["image"]["image_id"], published_ports=False, bootstrap_removed=True,
                         mount_destinations=["/run/wa-secrets", "/var/lib/postgresql/data"])

    def authority(self, temporary, installed=True):
        rows = self.native["expected"]["functions"]
        return {
            "database": "wa_p0c_rehearsal", "login": "postgres", "effective_login": "postgres",
            "authentication": "scram-sha-256:postgres", "server_version_num": 170011, "read_only": True,
            "other_client_backends": 0, "temporary_memberships": [
                {"role": role, "grantor": "postgres", "admin": False, "inherit": False, "set": True}
                for role in ("wa_customer_verifier", "wa_private_helper_owner", "wa_track_verifier")
            ] if temporary else [],
            "permanent_migrator_owner": [{"grantor": "postgres", "admin": False, "inherit": False, "set": True}],
            "temporary_leaf_schema_create": {"wa_customer_verifier": False, "wa_private_helper_owner": False,
                                             "wa_track_verifier": False},
            "migrator_can_set_owner": True, "migrator_can_set_track_verifier": temporary,
            "functions": {name: {f: rows[name][f] for f in ("owner", "body_sha256", "security_definer")}
                          for name in P.FUNCTIONS} if installed else {},
        }

    def full_rows(self):
        rows = sorted((S.sha(row["id"].encode()), S.sha(row["sha256"].encode())) for row in self.packet["ledger_expected"])
        return {"schema": "workinants.runtime-lease-history-fingerprints.v1", "server_version_num": 170011,
                "database": "wa_p0c_rehearsal", "collected_as": "postgres", "collector_is_superuser": True,
                "read_only": True, "history_count": 3,
                "rows": [{"name_sha256": name, "checksum_sha256": checksum, "row_sha256": S.sha(checksum.encode())}
                         for name, checksum in rows]}

    def model(self):
        migration = {"closed": True, "operation": "deploy", "status": P.RESULT_COMPLETE, "exit_code": 0,
                     "no_pending_message_observed": False}
        finalization = {"grantor": "postgres", "temporary_leaves_absent": True, "leaf_create_absent": True, "closed": True}
        native = {"expected_sha256": C.CATALOG_SHA, "snapshot_sha256": "b" * 64, "catalog_checks": 29089,
                  "oracle_expressions": 416, "ledger_checks": 22, "applied_rows": 3}
        responses = {
            "FRESH_OWNED_RESOURCE": {"owned": True, "isolated": True, "no_host_bind": True},
            "OWNED_BOOTSTRAP": {"owned_bootstrap": True, "business_roles_inactive": True, "closed": True},
            "AUTHENTICATION_BEFORE_DEPLOY": {"authenticated_roles": list(P.SCRAM_ROLES[:2]),
                                             "inactive_roles_rejected": list(P.SCRAM_ROLES[2:]),
                                             "all_clients_closed": True, "loopback_only": True},
            "PRE_DEPLOY": self.authority(True, installed=False), "PRE_FINALIZATION": self.authority(True),
            "POST_FINALIZATION": self.authority(False), "POST_NOOP": self.authority(False),
            "DEPLOY_THREE": migration, "STATUS": {**migration, "operation": "status"},
            "REDEPLOY": {**migration, "no_pending_message_observed": True},
            "ORIGINAL_GRANTOR_FINALIZATION": finalization, "FAILURE_PATH_ORIGINAL_GRANTOR_FINALIZATION": finalization,
            "THREE_ROW_LEDGER_BEFORE_FINALIZATION": {"applied_rows": 3, "ledger_checks": 22, "native_unchanged": True},
            "THREE_ROW_LEDGER_BEFORE_ACTIVATION": {"applied_rows": 3, "ledger_checks": 22, "native_unchanged": True},
            "ACTIVATE_ISOLATED_LOGINS_AND_VERIFY_SCRAM": {"roles": list(P.SCRAM_ROLES), "loopback_only": True,
                                                         "all_clients_closed": True, "wrong_passwords_rejected": True,
                                                         "business_cases": "NOT_RUN"},
            "INITIAL_NATIVE_ORACLE_AND_THREE_ROW_LEDGER": native, "COMPLETE_NATIVE_AND_LEDGER_PARITY": native,
            "EXACT_OWNED_CLEANUP": {"full_container_id_absent": True, "container_name_absent": True,
                                    "volume_absent": True, "private_runtime_path_absent": True},
        }
        for name in ("DEPLOY_THREE", "STATUS", "REDEPLOY", "FAILURE_PATH"):
            responses[name + "_ALL_CLIENTS_ABSENT"] = {"all_other_clients_absent": True}
        for name in ("PRE_FINALIZATION_THREE_APPLIED_ROW_FINGERPRINTS", "BEFORE_NOOP_FULL_ROWS", "AFTER_NOOP_FULL_ROWS"):
            responses[name] = self.full_rows()
        return SimpleNamespace(offline_model=True, responses={name: value(item) for name, item in responses.items()})

    def test_exact_tars_and_reviewed_source(self):
        self.assertIs(self.packet["runtime_authority"], False)
        self.assertIs(self.packet["business_tests_executed"], False)
        self.assertEqual(self.packet["candidate_commit"], C.CANDIDATE_COMMIT)
        self.assertEqual(self.native["expected_sha256"], C.CATALOG_SHA)
        self.assertEqual(self.packet["ledger_expected"], C.history_rows())
        self.assertEqual(S.unique_json(self.assets["expression-oracle-plan.json"])["expression_count"], 416)
        self.assertEqual(len(parse_sql(P.AUTHORITY_SQL)), 4)
        self.assertEqual(len(self.files), 9)
        self.assertEqual(len(self.manifest["tools"]["files_sha256"]), 10300)
        with tarfile.open(fileobj=io.BytesIO(self.archive)) as archive:
            self.assertEqual(archive.getnames(), sorted(self.files))
            for member in archive:
                self.assertTrue(member.isreg())
                self.assertEqual((member.mode, member.uid, member.gid, member.mtime), (0o444, 0, 0, 0))
                self.assertEqual(archive.extractfile(member).read(), self.files[member.name])

    def test_node_verifies_only_exact_three_migrations_and_copy(self):
        runner = r'''
import assert from "node:assert/strict";
import fs from "node:fs";
import { pathToFileURL } from "node:url";
const [guardPath, source, leaf] = process.argv.slice(1);
const g = await import(pathToFileURL(guardPath));
const launcher = await import(new URL("./runner.mjs", pathToFileURL(guardPath)));
const raw = fs.readFileSync(0);
const a = g.strictJson(raw);
const read = file => file.startsWith(g.SOURCE_ROOT + "/") ?
  fs.readFileSync(source + file.slice(g.SOURCE_ROOT.length)) :
  Buffer.from(file.endsWith("effect/package.json") ? '{"version":"3.22.1"}' : '{"version":"7.10.1"}');
const dir = g.SOURCE_ROOT+"/"+g.HISTORY;
const sourceFiles = [...Object.keys(JSON.parse(read(g.SOURCE_ROOT+"/"+g.HISTORY_MANIFEST)).files_sha256), g.HISTORY_MANIFEST];
const io = {
  loopbackOnly: () => true,
  mountInfo: () => '11 10 0:5 / /run/wa-secrets rw,nodev,nosuid,noexec - tmpfs tmpfs rw,size=8192k,mode=700\n'
     + '12 10 0:6 /example /var/lib/postgresql/data rw,relatime - ext4 /dev/loop1 rw\n',
  bootstrapAbsent: () => {},
  listFiles: path => path===g.SOURCE_ROOT ? [...sourceFiles] : path===dir ?
    ["migration_lock.toml", ...g.ORDERED.map(row => row.id+"/migration.sql")] : Object.keys(a.planned.tools.files_sha256),
  read, readPrivate(file) {
    assert.equal(file, g.URL_FILE);
    return Buffer.from("postgresql://wa_migrator:MODEL@127.0.0.1:5432/wa_p0c_rehearsal?schema=public&sslmode=disable");
  },
  toolHash(file, relative, size) {
    assert.equal(size, a.planned.tools.file_sizes[relative]);
    return a.planned.tools.files_sha256[relative];
  }
};
const id = { platform:"linux", arch:"x64", node:"v24.22.1", hostname:"b".repeat(12), uid:0 };
const local = g.verifyInputs(a, io, id);
assert.equal(local.orderedHistory.length, 3);
const missing = structuredClone(a);
missing.planned.history.ordered.pop();
assert.throws(() => g.validateAttestation(missing), /EXACT_THREE_HISTORY_REQUIRED/);
assert.throws(() => g.verifyInputs(a, {...io, read: file => file.endsWith(leaf) ? Buffer.from("drift") : read(file)}, id),
  /SOURCE_FILE_DRIFT/);
const flag = "--execute-reviewed-cloud-f0-track-retained-base-v1";
for (const operation of ["deploy", "status"]) {
  const input = Buffer.from(JSON.stringify({...a, operation}));
  let receipt, dispatched = 0;
  const code = launcher.main([flag, "--operation", operation], {
    readStdin: () => input, store() {}, load: () => local,
    spawn(binary, args, options) {
      dispatched++;
      assert.equal(binary, g.TOOLS_ROOT+"/node/bin/node");
      assert.deepEqual(args, [local.cli, "migrate", operation, "--config", local.config]);
      assert.equal(options.shell, false);
      assert.equal(options.env.DATABASE_URL, undefined);
      return {status:0, stdout:operation === "deploy" ? "No pending migrations to apply.\n" : "", stderr:""};
    },
    emit(value) { receipt = value; }
  });
  assert.equal(code, 0);
  assert.equal(dispatched, 1);
  assert.equal(receipt.track_retained_sql_sha256, g.ORDERED[2].sha256);
  assert.equal(receipt.attestation_sha256, g.sha256(input));
  assert.equal(receipt.database_qualification_claimed, false);
}
let refused;
assert.equal(launcher.main([flag, "--operation", "deploy"], {
  readStdin: () => raw, store() {}, load: () => { throw new g.HeldFailure("EXACT_ORDERED_THREE_HISTORY"); },
  spawn() { assert.fail("refused preflight dispatched a child"); }, emit(value) { refused = value; }
}), 1);
assert.equal(refused.code, "EXACT_ORDERED_THREE_HISTORY");
assert.equal(refused.child_dispatch, "NOT_ATTEMPTED");
assert.equal(refused.packet_sha256, a.authorization.packet_sha256);
'''
        with TemporaryDirectory(prefix="wa-track-node-model-") as folder:
            root = Path(folder) / "source9"
            C.P.write_source(root, self.files)
            for path in C.RUNTIME:
                subprocess.run(["node", "--check", str(root / path)], check=True, capture_output=True, timeout=10)
            raw = P.attestation(self.manifest, self.scope, "deploy", packet_sha256=PIN, literal_review_sha256=PIN)
            self.assertLess(len(raw), 2 * 1024 * 1024)
            subprocess.run(["node", "--input-type=module", "-e", runner, str(root / C.RUNTIME[1]), str(root),
                            self.packet["ledger_expected"][2]["path"]], input=raw, check=True, capture_output=True, timeout=10)

    def test_wrong_live_identity_rejected_before_attestation(self):
        for changes in ({"image_id": "bad"}, {"bootstrap_removed": False}, {"mount_destinations": ["/wrong"]},
                        {"volume_name": "other"}):
            with self.subTest(changes=changes), self.assertRaisesRegex(S.Held, "EXACT_TRACK_LIVE_OBSERVATION"):
                P.attestation(self.manifest, {**self.scope, **changes}, "deploy", packet_sha256=PIN, literal_review_sha256=PIN)

    def test_restricted_result_projection(self):
        blobs, _ = C.basis.capture()
        validator = C.basis.B.result_validator(C.ROOT, blobs)
        reading = P.attestation(self.manifest, self.scope, "deploy", packet_sha256=PIN, literal_review_sha256=PIN)
        result = {"schema": C.RESULT_SCHEMA, "operation": "deploy", "status": P.RESULT_COMPLETE, "exit_code": 0,
                  "prisma_codes": [], "sqlstates": [], "no_pending_message_observed": True, "raw_output_discarded": True,
                  "database_qualification_claimed": False, "run_id": self.manifest["run_id"],
                  "container_id": self.scope["container_id"], "daemon_id": self.scope["daemon"]["daemon_id"],
                  "packet_sha256": PIN, "literal_review_sha256": PIN, "attestation_sha256": S.sha(reading),
                  "diagnostic_format": {name: name in ("text_valid", "headers_valid") for name in validator.DIAGNOSTIC_FLAGS},
                  **{key: self.manifest["source"][key] for key in ("initial_sql_sha256", "append_sql_sha256",
                     "track_retained_sql_sha256", "ordered_history_sha256", "effective_expected_sha256")}}

        def parse(receipt, status=0):
            return P.qualified_migration_result(S.encode(receipt), status, b"", self.manifest, self.scope, "deploy", reading,
                                                packet_sha256=PIN, literal_review_sha256=PIN, historical_validator=validator)

        self.assertEqual(parse(result), result)
        for edited in ({**result, "literal_review_sha256": "c" * 64}, {**result, "track_retained_sql_sha256": PIN},
                       {**result, "schema": C.REFUSAL_SCHEMA}, {**result, "unexpected": True}):
            with self.assertRaises((S.Held, ValueError)):
                parse(edited)
        with self.assertRaisesRegex(S.Held, "TRACK_WRAPPER_RESULT_EXIT"):
            parse(result, 1)
        ambiguous = {**result, "status": "CLI_CLOSURE_UNCONFIRMED_STOP_AND_CLEAN_EXACT_RESOURCE", "exit_code": None,
                     "no_pending_message_observed": False}
        with self.assertRaisesRegex(P.RemoteUnconfirmed, "TRACK_REPORTED_CHILD_CLOSURE_UNCONFIRMED"):
            parse(ambiguous, 1)

    def test_exact_track_authority_restored(self):
        self.assertTrue(P.authority(self.authority(True), self.native, timing="PRE_FINALIZATION")["leaf_create_absent"])
        self.assertTrue(P.authority(self.authority(False), self.native, timing="POST_FINALIZATION")["leaf_create_absent"])
        leaf = self.authority(True)
        leaf["temporary_leaf_schema_create"]["wa_track_verifier"] = True
        wrong_body = self.authority(True)
        wrong_body["functions"][P.FUNCTIONS[0]]["body_sha256"] = PIN
        wrong_grantor = self.authority(True)
        wrong_grantor["temporary_memberships"][2]["grantor"] = "wa_migrator"
        for phase, observation in (("PRE_FINALIZATION", leaf), ("PRE_FINALIZATION", wrong_body),
                                   ("PRE_FINALIZATION", wrong_grantor), ("POST_FINALIZATION", self.authority(True))):
            with self.assertRaisesRegex(S.Held, "TRACK_LEAF_MEMBERSHIP_OR_RESTORATION_DRIFT"):
                P.authority(observation, self.native, timing=phase)

    def test_ledger_uses_generic_22_check_native_registration(self):
        proof = S.module(C.ROOT, LEDGER, S.read(C.ROOT / LEDGER))
        with TemporaryDirectory(prefix="wa-track-ledger-model-") as folder:
            root = Path(folder) / "source9"
            C.P.write_source(root, self.files)
            ordered = self.packet["ledger_expected"]
            registered = P.registration(proof, ordered, source_root=root, run_id=RUN_ID, attestation_sha256=PIN)
            observation = {**proof.schema_expectation(), "format": proof.NATIVE_FORMAT, "server_version_num": 170011,
                           "database": "wa_p0c_rehearsal", "read_only": True, "isolation": "repeatable read",
                           "collected_as": "postgres", "session_user": "postgres", "collector_is_superuser": True,
                           "history_ids_unique": True, "history": deepcopy(registered["history_expected"])}
            snapshot = {"model_catalog": "no native database snapshot collected"}
            _, result = P.verify_ledger(proof, registered, observation, snapshot, snapshot, root)
            self.assertEqual(len(result["checks"]), 22)
            for edited in (ordered[:2], ordered[::-1], [{**ordered[0], "sha256": PIN}, *ordered[1:]]):
                with self.assertRaisesRegex(S.Held, "EXACT_THREE_MIGRATION_REGISTRATION"):
                    P.registration(proof, edited, source_root=root, run_id=RUN_ID, attestation_sha256=PIN)
            observation["history"][2] = deepcopy(observation["history"][0])
            with self.assertRaisesRegex(S.Held, "TRACK_NATIVE_THREE_ROW_LEDGER_REFUSED"):
                P.verify_ledger(proof, registered, observation, snapshot, snapshot, root)

    def test_full_noop_changes_are_rejected(self):
        rows = self.full_rows()
        self.assertEqual(P.unchanged_noop(rows, deepcopy(rows), C.history_rows())["rows"], 3)
        updated = deepcopy(rows)
        updated["rows"][0]["row_sha256"] = PIN
        with self.assertRaisesRegex(S.Held, "NOOP_CHANGED_A_FULL_TRACK_LEDGER_ROW"):
            P.unchanged_noop(rows, updated, C.history_rows())

    def test_modeled_order_starts_pre_finalization_after_client_closure(self):
        report = P.model_owned_sequence(self.model(), self.packet, self.native)
        self.assertEqual(report["status"], "MODEL_COMPLETE")
        self.assertEqual(report["stages"], [
            "FRESH_OWNED_RESOURCE", "OWNED_BOOTSTRAP", "AUTHENTICATION_BEFORE_DEPLOY", "PRE_DEPLOY", "DEPLOY_THREE",
            "DEPLOY_THREE_ALL_CLIENTS_ABSENT",
            "PRE_FINALIZATION", "THREE_ROW_LEDGER_BEFORE_FINALIZATION", "PRE_FINALIZATION_THREE_APPLIED_ROW_FINGERPRINTS",
            "ORIGINAL_GRANTOR_FINALIZATION",
            "POST_FINALIZATION", "THREE_ROW_LEDGER_BEFORE_ACTIVATION", "ACTIVATE_ISOLATED_LOGINS_AND_VERIFY_SCRAM",
            "INITIAL_NATIVE_ORACLE_AND_THREE_ROW_LEDGER", "BEFORE_NOOP_FULL_ROWS", "STATUS",
            "STATUS_ALL_CLIENTS_ABSENT", "REDEPLOY", "REDEPLOY_ALL_CLIENTS_ABSENT", "AFTER_NOOP_FULL_ROWS",
            "COMPLETE_NATIVE_AND_LEDGER_PARITY", "POST_NOOP", "EXACT_OWNED_CLEANUP",
        ])
        self.assertEqual((report["runtime"], report["assertion_promotions"]), ("NOT_RUN", 0))

    def test_unknown_descendant_skips_finalizer_and_keeps_first_failure(self):
        model = self.model()
        model.responses["DEPLOY_THREE_ALL_CLIENTS_ABSENT"] = value({"all_other_clients_absent": False})
        model.responses["EXACT_OWNED_CLEANUP"] = stopped("SECONDARY_CLEANUP_STOP")
        report = P.model_owned_sequence(model, self.packet, self.native)
        self.assertEqual(report["first_failure"], {"stage": "DEPLOY_THREE_ALL_CLIENTS_ABSENT",
                                                 "code": "TRACK_ALL_CLIENT_BACKENDS_NOT_CLOSED"})
        self.assertTrue(report["sticky_remote_uncertainty"])
        self.assertFalse(report["cleanup_complete"])
        self.assertEqual(report["stages"][-2:], ["DEPLOY_THREE_ALL_CLIENTS_ABSENT", "EXACT_OWNED_CLEANUP"])

    def test_known_migration_failure_finalizes_once_only_after_client_closure(self):
        model = self.model()
        model.responses["DEPLOY_THREE"] = value({"operation": "deploy", "closed": True, "exit_code": 1,
                                                "status": "CLI_FAILED_STOP_AND_INSPECT", "no_pending_message_observed": False})
        report = P.model_owned_sequence(model, self.packet, self.native)
        self.assertEqual(report["first_failure"]["code"], "TRACK_PRISMA_OPERATION_STOPPED")
        self.assertFalse(report["sticky_remote_uncertainty"])
        self.assertTrue(report["cleanup_complete"])
        self.assertEqual(report["stages"][-4:], ["DEPLOY_THREE_ALL_CLIENTS_ABSENT", "FAILURE_PATH_ALL_CLIENTS_ABSENT",
                                                "FAILURE_PATH_ORIGINAL_GRANTOR_FINALIZATION", "EXACT_OWNED_CLEANUP"])

    def test_unknown_bootstrap_skips_all_further_database_stages(self):
        model = self.model()
        model.responses["OWNED_BOOTSTRAP"] = stopped("BOOTSTRAP_EXEC_INTERRUPTED")
        report = P.model_owned_sequence(model, self.packet, self.native)
        self.assertEqual(report["stages"], ["FRESH_OWNED_RESOURCE", "OWNED_BOOTSTRAP", "EXACT_OWNED_CLEANUP"])
        self.assertTrue(report["sticky_remote_uncertainty"])

    def test_failed_pre_activation_ledger_leaves_logins_inactive(self):
        model = self.model()
        model.responses["THREE_ROW_LEDGER_BEFORE_ACTIVATION"] = stopped("EXACT_THREE_ROWS_REFUSED")
        report = P.model_owned_sequence(model, self.packet, self.native)
        self.assertEqual(report["first_failure"]["code"], "EXACT_THREE_ROWS_REFUSED")
        self.assertEqual(report["stages"][-2:], ["THREE_ROW_LEDGER_BEFORE_ACTIVATION", "EXACT_OWNED_CLEANUP"])

    def test_integer_lookalikes_do_not_pass_modeled_native_shape(self):
        phase = "INITIAL_NATIVE_ORACLE_AND_THREE_ROW_LEDGER"
        for field in ("applied_rows", "ledger_checks", "oracle_expressions"):
            model = self.model()
            native = model.responses[phase]()
            native[field] = float(native[field])
            model.responses[phase] = value(native)
            report = P.model_owned_sequence(model, self.packet, self.native)
            self.assertEqual(report["first_failure"], {"stage": phase, "code": "TRACK_NATIVE_LEDGER_ORACLE_UNCONFIRMED"})
            self.assertEqual(report["stages"][-2:], [phase, "EXACT_OWNED_CLEANUP"])

    def test_cleanup_remote_uncertainty_is_latched(self):
        model = self.model()

        def fail_cleanup():
            raise P.RemoteUnconfirmed("EXACT_TRACK_CLEANUP_UNCONFIRMED")

        model.responses["EXACT_OWNED_CLEANUP"] = fail_cleanup
        report = P.model_owned_sequence(model, self.packet, self.native)
        self.assertEqual(report["status"], "MODEL_STOPPED")
        self.assertFalse(report["cleanup_complete"])
        self.assertTrue(report["sticky_remote_uncertainty"])


if __name__ == "__main__":
    unittest.main()
