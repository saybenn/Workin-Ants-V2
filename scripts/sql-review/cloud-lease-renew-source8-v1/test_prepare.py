from copy import deepcopy
from pathlib import Path
import unittest
import uuid

import pglast
from pglast import parser

import prepare


FIXTURE = "1913b9fa-998c-40a8-a10d-54981b0a9274"


class LeaseRenewSourceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.packet, cls.assets = prepare.assemble(FIXTURE)
        assert pglast.__version__ == "v7.21"
        assert prepare.sha(Path(pglast.__file__).read_bytes()) == "e085f1a529eedc4e9ddeecbd406255ed8580f4cef00b13a33e7fd056d8374084"
        assert prepare.sha(Path(parser.__file__).read_bytes()) == "c2ab2648a942b314ffcd7ab38f25c052ca08adc323fa556b0ed68b727320e711"

    def test_prior_worker_does_not_supply_renewal_and_held_packet_rebuilds(self):
        self.assertEqual((self.packet, self.assets), prepare.assemble(FIXTURE))
        self.assertEqual(self.packet["prior_worker_transport"]["actual_prior_cases"], 21)
        self.assertIs(self.packet["prior_worker_transport"]["dedicated_renewal_observed"], False)
        self.assertEqual(self.packet["runtime"], "NOT_RUN")
        self.assertEqual(self.packet["assertion_promotions"], 0)
        self.assertNotIn("worker-renew.sql", self.assets)
        self.assertEqual(self.packet["source_pins"][f"{prepare.LEGACY}/worker-renew.sql"], prepare.LEGACY_PINS["worker-renew.sql"])

    def test_four_historical_mutations_preserved_and_denials_only_roll_back(self):
        fixture_id = self.packet["identity"]["work_id"]
        historical_id = "b3c6b69b-8f03-5406-88e6-b2434ee6c797"
        for name in prepare.CASES:
            leaf = name + ".sql"
            historical = (prepare.ROOT / prepare.LEGACY / leaf).read_text()
            expected = historical.replace(historical_id, fixture_id)
            if name in prepare.DENIALS:
                expected = expected.removesuffix("COMMIT;\n") + "ROLLBACK;\n"
            self.assertEqual(self.assets[leaf], expected)
            nodes = [row.stmt for row in pglast.parse_sql(self.assets[leaf])]
            targets = nodes[1].withClause.ctes[0].ctequery.targetList
            self.assertEqual([node.name for node in targets], ["state", "fence", "attempt_count", "lease_token_hash", "lease_expires_at"]
                             if name == "worker-claim" else ["lease_expires_at"])
            self.assertEqual(nodes[-1].kind.name, "TRANS_STMT_ROLLBACK" if name in prepare.DENIALS else "TRANS_STMT_COMMIT")
        self.assertIn("clock_timestamp()+interval '12 seconds'", self.assets["worker-claim.sql"])
        self.assertIn("clock_timestamp()+interval '90 seconds'", self.assets["current-holder-renew.sql"])

    def test_source_setup_and_finite_capabilities(self):
        seed = self.assets["identity-seed.sql"]
        self.assertEqual(seed.count("DISABLE TRIGGER owner_commit"), 2)
        self.assertEqual(seed.count("ENABLE TRIGGER owner_commit"), 2)
        self.assertNotIn("runtime_work_item", seed)
        bootstrap = pglast.parse_sql(self.assets["identity-worker-bootstrap.sql"])
        self.assertEqual([x.stmt.relation.relname for x in bootstrap[1:3]], ["identity_service_receipt", "identity_service_authorization"])
        schedule = pglast.parse_sql(self.assets["schedule-lease.sql"])
        self.assertEqual(schedule[0].stmt.relation.relname, "runtime_work_item")
        self.assertIn(self.packet["identity"]["outbox_id"], self.assets["schedule-lease.sql"])
        source = self.packet["grant_templates"]["source-lease"]
        for grant in self.packet["grant_templates"].values():
            self.assertEqual(grant["allowed_fields"], sorted(set(grant["allowed_fields"])))
        self.assertEqual(len(source["allowed_fields"]), 179)
        renew = self.packet["grant_templates"]["renew-1"]
        self.assertEqual((renew["database_login_role"], renew["action"], str(renew["source_generation"])), ("wa_worker", "runtime.renew_work.v1", "1"))
        self.assertEqual({field.rsplit("/", 1)[1] for field in renew["allowed_fields"] if "/UPDATE/" in field}, {"@row", "leaseExpiresAt"})

    def test_source8_guard_shape_and_exact_terminal_denial_receipt(self):
        errors = (f"psql:<stdin>:2: ERROR:  P0001: {prepare.MESSAGE}\n"
                  f"CONTEXT:  PL/pgSQL function {prepare.GUARD} line 31 at RAISE\n"
                  "LOCATION:  exec_stmt_raise, pl_exec.c:3911\n")
        for name in prepare.DENIALS:
            rows = [prepare.marker(name, "BEFORE")]
            self.assertEqual(prepare.diagnostic_receipt(name, 3, rows, False, errors), {"exact_denial": True, "sqlstate": "P0001",
                                                                                     "body_line": 31, "body_sha256": prepare.GUARD_SHA})
            for result in (prepare.diagnostic_receipt(name, 3, rows, False, errors.replace("line 31", "line 29")),
                           prepare.diagnostic_receipt(name, 3, rows, False, errors + "DETAIL: raw-canary\n"),
                           prepare.diagnostic_receipt(name, 3, rows + [prepare.marker(name, "AFTER")], False, errors),
                           prepare.diagnostic_receipt(name, 0, rows, False, errors)):
                self.assertIs(result["exact_denial"], False)
                self.assertNotIn(b"raw-canary", prepare.canonical(result))

    def test_positive_requires_both_markers_typed_one_row_and_commit(self):
        for name in prepare.CASES[:2]:
            markers = [prepare.marker(name, "BEFORE"), '{"changed" : 1}', prepare.marker(name, "AFTER")]
            self.assertEqual(prepare.commit_receipt(name, 0, markers, True, ""), {"exact_committed_work_change": True, "changed_rows": 1})
            self.assertFalse(prepare.commit_receipt(name, 0, markers, False, "")["exact_committed_work_change"])
            self.assertFalse(prepare.commit_receipt(name, 0, [markers[0], '{"changed": true}', markers[2]], True, "")["exact_committed_work_change"])
            self.assertFalse(prepare.commit_receipt(name, 0, markers[:-1], True, "")["exact_committed_work_change"])

    def test_only_live_deadline_and_guard_xid_may_change_and_denial_retains_row(self):
        before = {"deadline": "2026-11-28T05:12:12.000000Z", "live": True, "mutation_xid": "201",
                  "domain_sha256": "a" * 64, "row_sha256": "b" * 64}
        after = before | {"deadline": "2026-11-28T05:13:37.000000Z", "mutation_xid": "203", "row_sha256": "c" * 64}
        self.assertTrue(prepare.renewal_delta(before, after, "201", "203"))
        self.assertFalse(prepare.renewal_delta(before, after | {"domain_sha256": "d" * 64}, "201", "203"))
        self.assertFalse(prepare.renewal_delta(before | {"live": False}, after, "201", "203"))
        self.assertFalse(prepare.renewal_delta(before, after | {"deadline": before["deadline"]}, "201", "203"))
        self.assertTrue(prepare.exact_negative_state(after, deepcopy(after), "203"))
        self.assertFalse(prepare.exact_negative_state(after, after | {"mutation_xid": "205"}, "203"))

    def test_fixed_state_observers_use_exact_hash_ids_and_c_order(self):
        work = prepare.work_observer_sql(self.assets["work-state-observe.sql"], "a" * 64)
        self.assertEqual(len(pglast.parse_sql(work)), 1)
        with self.assertRaisesRegex(ValueError, "LEASE_RENEW_EXACT_WORK_HASH_BINDING"):
            prepare.work_observer_sql(self.assets["work-state-observe.sql"], "not-a-hash")
        grants = tuple(str(uuid.uuid4()) for _ in range(6))
        full = prepare.full_state_observer_sql(self.assets["full42-state-observe.sql"], grants)
        root = pglast.parse_sql(full)[0].stmt
        collation = root.targetList[0].val.agg_order[0].node
        self.assertEqual([node.sval for node in collation.collname], ["C"])
        self.assertEqual([node.sval for node in collation.arg.fields], ["table_name"])
        self.assertEqual(len(self.packet["full42_table_order"]), 42)
        self.assertTrue(all(full.count(value) == 1 for value in grants))
        with self.assertRaisesRegex(ValueError, "LEASE_RENEW_EXACT_GRANT_EXCLUSIONS"):
            prepare.full_state_observer_sql(self.assets["full42-state-observe.sql"], grants + (str(uuid.uuid4()),))
