"""Offline receipt, checkpoint, and child-closure tests for the containing owner."""

import hashlib
import json
import os
from pathlib import Path
import re
from tempfile import TemporaryDirectory
from types import SimpleNamespace as NS
import unittest
from unittest.mock import patch

import prior
import proof
import run


class Held(Exception):
    pass


def require(value, code):
    if not value:
        raise Held(code)


S = NS(require=require, Held=Held, HASH=re.compile("[0-9a-f]{64}"), unique_json=json.loads,
       encode=lambda value: json.dumps(value, sort_keys=True).encode(), sha=lambda data: hashlib.sha256(data).hexdigest())


BASE_TABLES = set(proof.CUSTOMER_TABLES) | set(proof.IDENTITY) | {proof.GRANTS, "platform.runtime_work_item",
                "platform.runtime_effect_receipt"}
KEYS = tuple(sorted(BASE_TABLES | {f"registered_{key:02d}" for key in range(42 - len(BASE_TABLES))}))
COUNTERS = {"users": "app.users", "security_profiles": "app.user_security_profiles", "grants": proof.GRANTS,
            "customers": "app.customer_profiles", "receipts": "platform.runtime_command_receipt",
            "history": "app.customer_profile_lifecycle_event", "evidence": "platform.owner_mutation_evidence",
            "outbox": "platform.runtime_outbox_message", "work": "platform.runtime_work_item",
            "effects": "platform.runtime_effect_receipt"}


def response(mode, start=100):
    rows = {}
    for index, (name, (status, steps)) in enumerate(proof.CASE_EXPECTATIONS[mode].items()):
        tuple_ = {"pid": 501 if name == "contender" else 500, "xid": str(start + index),
                  "backend_start_epoch": "1700000000.123456"}
        row = {"status": status, "steps": list(steps), "tuple": None if status == "denied" else tuple_}
        if status in ("created", "replay"):
            row.update(value_sha256="a" * 64, recorded_at="2026-11-28T06:20:30.123Z")
        rows[name] = row
    return {"schema": proof.NODE_SCHEMA, "status": proof.NODE_PASS, "mode": mode, "cases": rows, "pools_ended": True}


def reply(value, code=0, stderr=b""):
    return NS(returncode=code, stdout=S.encode(value), stderr=stderr)


def full42(phase, previous=None):
    if previous is None:
        return {table: {"count": 0, "rows_sha256": S.sha(b"[]")} for table in KEYS}
    delta = proof.DELTAS[phase]
    return {table: {"count": found["count"] + delta[table], "rows_sha256": S.sha((table + phase).encode())}
            if table in delta else found.copy() for table, found in previous.items()}


def observe(rows, nodes):
    present = {"primary": ("create-replay", "created"), "rollback": ("retry", "retried")}
    scopes = {}
    for group, (mode, case) in present.items():
        scopes[group] = proof.EMPTY_GROUP.copy()
        if mode in nodes:
            node = nodes[mode]["cases"][case]
            scopes[group].update(count=6, distinct_xids=1, xid=node["tuple"]["xid"],
                                 coherent=True, rows_sha256=S.sha(group.encode()), result_digest="b" * 64,
                                 recorded_at=node["recorded_at"])
    return {"scope_groups": scopes, "physical_counts": {key: rows[table]["count"] for key, table in COUNTERS.items()},
            "grants_ok": True, "grant_groups": proof.grant_groups(nodes), "restricted_sessions": 0}


class ProofTests(unittest.TestCase):
    def test_pinned_smoke_source_can_be_read_with_an_old_access_time(self):
        raw = b"verified = True\n"
        with TemporaryDirectory() as directory:
            source = Path(directory) / run.SMOKE
            source.parent.mkdir(parents=True)
            source.write_bytes(raw)
            os.utime(source, ns=(0, source.stat().st_mtime_ns))
            with patch.object(run, "SMOKE_SHA", S.sha(raw)):
                self.assertTrue(run.load_smoke(Path(directory)).verified)
                source.write_bytes(b"verified = False\n")
                with self.assertRaisesRegex(ValueError, run.INPUT):
                    run.load_smoke(Path(directory))

    def test_exact_all_modes(self):
        for index, mode in enumerate(proof.MODES):
            value = response(mode, 100 + index * 10)
            self.assertEqual(proof.node_receipt(reply(value), mode, S, ()), value)

    def test_replay_projection_change_and_wrong_mode_reject(self):
        value = response("create-replay")
        value["cases"]["metadata_replay"]["value_sha256"] = "c" * 64
        with self.assertRaisesRegex(Held, proof.RESPONSE):
            proof.node_receipt(reply(value), "create-replay", S, ())
        with self.assertRaisesRegex(Held, proof.RESPONSE):
            proof.node_receipt(reply(response("retry")), "rollback", S, ())

    def test_known_stop_shape_and_no_stderr(self):
        stopped = {"schema": proof.NODE_SCHEMA, "status": "STOPPED", "stage": "FINAL_FREE_INTENT_RLS_ROLLBACK"}
        self.assertEqual(proof.node_receipt(reply(stopped, 1), "rollback", S, ()), stopped)
        for payload in (reply(stopped, 1, b"stderr"), reply({**stopped, "mode": "rollback"}, 1)):
            with self.assertRaisesRegex(Held, proof.RESPONSE):
                proof.node_receipt(payload, "rollback", S, ())
        with self.assertRaisesRegex(Held, proof.RESPONSE):
            proof.node_receipt(reply(stopped, 1), "retry", S, ())

    def test_diagnostic_requires_finite_codes_and_an_exact_first_failure(self):
        origin = {"side": "primary", "step": "APP_SQL_RECEIPT", "sqlstate": "42804"}
        primary = {"phase": "COMPETING_KNOWN_CREATE", "last": "APP_ROLLBACK_BUILD", "failure": origin,
                   "owner_failure": "rolled_back", "outcome": None, "completed_steps": ["READ_EMPTY", "CLOCK_DATE"],
                   "terminal_builds": ["rollback"]}
        stopped = {"schema": proof.STOP_SCHEMA, "status": "STOPPED", "stage": primary["phase"],
                   "first_failure": origin, "attempts": {"primary": primary, "peer": None}, "pools": "END_RESOLVED"}
        self.assertEqual(proof.node_receipt(reply(stopped, 1), "create-replay", S, ()), stopped)
        for bad in ({**origin, "sqlstate": "00000"}, {**origin, "step": "APP_SQL_BIND"},
                    {**origin, "side": "peer"}, {**origin, "message": "unexpected field"}):
            with self.assertRaisesRegex(Held, proof.RESPONSE):
                proof.node_receipt(reply({**stopped, "first_failure": bad}, 1), "create-replay", S, ())

    def test_full_sequence_observe(self):
        nodes, previous, previous_obs = {}, None, None
        for index, phase in enumerate(proof.PHASES):
            if phase in proof.MODES:
                nodes[phase] = response(phase, 100 + index * 10)
            rows = full42(phase, previous)
            proof.validate_full42(rows, KEYS, phase, previous, S)
            new_obs = observe(rows, nodes)
            proof.validate_observation(new_obs, rows, nodes, previous_obs, S)
            previous, previous_obs = rows, new_obs

    def test_no_residue_and_group_xid_checks(self):
        seeded = full42("seeded", full42("unborn"))
        before = full42("create-replay", seeded)
        after = full42("rollback", before)
        after["app.customer_profiles"]["rows_sha256"] = "7" * 64
        with self.assertRaisesRegex(Held, proof.FULL42):
            proof.validate_full42(after, KEYS, "rollback", before, S)
        nodes = {"create-replay":response("create-replay")}
        obs = observe(before, nodes)
        obs["scope_groups"]["primary"]["xid"] = nodes["create-replay"]["cases"]["contender"]["tuple"]["xid"]
        with self.assertRaisesRegex(Held, proof.OBSERVATION):
            proof.validate_observation(obs, before, nodes, None, S)

    def test_prior_read_requires_fixed_accepted_path_digest_and_success(self):
        lookups = []
        supplied = {"decision": prior.DECISION, "schema": prior.SCHEMA,
                    "posture": "D", "integrated_runtime_qualified": False, "operator_exit_code": 1}

        def pinned(_root, path, digest):
            lookups.append((path, digest))
            return S.encode(supplied)

        source = NS(**vars(S), pinned=pinned)
        accepted_path = prior.BASE + "/owner-123456ab/acceptance.json"
        digest = "b" * 64
        cases = (("/tmp/acceptance.json", digest), (accepted_path, "bad-digest"), (accepted_path, digest))
        for path, pin in cases:
            with self.assertRaisesRegex(Held, prior.CODE):
                prior.verify(Path("/reviewed"), path, pin, {}, {}, None, None, source)
        self.assertEqual(lookups, [(accepted_path, digest)])

    def test_prior_audit_requires_exact_approval_and_environment(self):
        bound = {"run_id": "test-only", "daemon": {"id": "exact-daemon"}, "image": {"id": "exact-image"}}
        audit = {**bound, "schema": prior.AUDIT_SCHEMA, "decision": prior.AUDIT_DECISION, "cleanup_verified": True,
                 "operator_exit_code": 0, "outer_status": prior.OUTER_PASS}
        prior.verify_independent(audit, bound, S)
        for change in ({"decision": "REJECTED"}, {"schema": "wrong-scope"}, {"daemon": {"id": "different"}},
                       {"operator_exit_code": False}):
            with self.assertRaisesRegex(Held, prior.CODE):
                prior.verify_independent({**audit, **change}, bound, S)


class FakeOwner:
    def configure_program(self):
        pass


class OwnerTests(unittest.TestCase):
    def instance(self, result, *, close_ok=True, write_ok=True):
        two = NS(Owner=FakeOwner)
        smoke = NS(owner_type=lambda renewal, modules: FakeOwner, CODES=set(), NODE="/approved/node",
                   DRIVER="/approved/driver")
        owner = run.owner_type(Path("/reviewed"), smoke, NS(SEAM=("NOOP", "PASS")), (NS(S=S), None, two))()
        owner.transport, owner.docker = NS(unknown=False), NS(remote_unknown=False)
        owner.operation = {"known_customer":{"prior_smoke":{"sha256":"a" * 64}}}
        owner.report, owner.name, owner.resources = {}, "owned", NS(cid="test-cid")
        owner.observed_target = lambda: {"container_id":"test-cid", "network":"none", "published_ports":False}
        owner.check_runtime_sources = lambda: {"node":"PASS"}
        sent, first, attempted = [], [], []

        def write_safe(name, _value):
            attempted.append(name)
            if not write_ok:
                raise Held("WRITE_UNCONFIRMED")
            return {"path": name}

        def terminate(_action, _target, stage):
            class Boundary:
                def __enter__(self):
                    return self

                def __exit__(self, _kind, error, _trace):
                    if error is not None and not first:
                        first.append(str(error))
                    success = close_ok and not owner.transport.unknown
                    owner.report.setdefault("backend_closures", []).append({
                        "stage": stage, "scope": "ALL_DATABASES_ALL_ROLES_ALL_TAGS", "observation_completed": success,
                        "counts_valid": success, "migrator_zero": success, "other_clients_zero": success,
                        "all_other_client_backends_absent": success,
                    })
                    return False
            return Boundary()

        def send(*args, **kw):
            sent.append((args, kw))
            return result

        owner.exact_container_exec = send
        owner.program = NS(SAFE_FAILURE_CODES=set(), SAFE_FAILURE_STAGES=set(), event=lambda *_args, **_kwargs:None,
                           save=lambda:None, _RequiredSafetyBoundary=terminate, write_safe=write_safe,
                           _required_safety_first_exception=lambda error, _stage: first.append(str(error)) if not first else None,
                           passwords={"owned":{"wa_app_runtime":"e" * 64, "wa_context_issuer":"f" * 64}},
                           all_secrets=("e" * 64, "f" * 64))
        owner.configure_program()
        return owner, sent, first, attempted

    def test_valid_child_uses_private_fixed_argv_and_closed_proof(self):
        owner, sent, first, _ = self.instance(reply(response("retry")))
        self.assertEqual(owner.invoke("retry")["status"], proof.NODE_PASS)
        args, kw = sent[0]
        self.assertEqual(args, ("-i", "--user", "65534:65534", "test-cid", "/usr/bin/env", "-i", "/approved/node",
                                f"{run.REMOTE}/{run.NODE_MAIN}", "retry", "/approved/driver"))
        self.assertEqual(json.loads(kw["input"]), {"app":"e" * 64, "issuer":"f" * 64})
        self.assertEqual(first, [])
        self.assertIs(owner.report["known_customer"]["closure_probes"]["P0D_CUSTOMER_RETRY_NODE"], True)

    def test_known_stop_retains_first_when_evidence_write_fails(self):
        stopped = {"schema":proof.NODE_SCHEMA, "status":"STOPPED", "stage":"ORIGINAL_KEY_RETRY"}
        owner, _, first, attempted = self.instance(reply(stopped, 1), write_ok=False)
        with self.assertRaisesRegex(Held, "WRITE_UNCONFIRMED"):
            owner.invoke("retry")
        self.assertEqual(first, [run.STOP])
        self.assertEqual(attempted, ["customer-retry-node.json"])
        self.assertIs(owner.transport.unknown, False)

    def test_unconfirmed_driver_end_retains_stop_and_marks_transport_uncertain(self):
        stopped = {"schema": proof.STOP_SCHEMA, "status": "STOPPED", "stage": "POOL_CLOSE", "pools": "END_UNCONFIRMED",
                   "first_failure": {"side": "harness", "step": "POOL_CLOSE", "sqlstate": None},
                   "attempts": {"primary": None, "peer": None}}
        owner, _, first, retained = self.instance(reply(stopped, 1))
        with self.assertRaisesRegex(Held, run.STOP):
            owner.invoke("retry")
        self.assertEqual(first, [run.STOP])
        self.assertEqual(retained, ["customer-retry-node.json"])
        self.assertTrue(owner.transport.unknown and owner.docker.remote_unknown)
        self.assertIs(owner.report["known_customer"]["closure_probes"]["P0D_CUSTOMER_RETRY_NODE"], False)

    def test_invalid_or_unclosed_response_is_sticky(self):
        for value, closed in ((reply(response("rollback")), True), (reply(response("retry")), False)):
            owner, _, _, _ = self.instance(value, close_ok=closed)
            with self.assertRaises(Held):
                owner.invoke("retry")
            self.assertTrue(owner.transport.unknown and owner.docker.remote_unknown)


if __name__ == "__main__":
    unittest.main()
