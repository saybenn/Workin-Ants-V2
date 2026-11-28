"""Exercise the historical strict observer with SQL-driven snapshot ordering."""

from contextlib import redirect_stdout
from copy import deepcopy
import io
import json
import re
import runpy
import socket
import subprocess
import tempfile
from pathlib import Path
import unittest
from unittest.mock import patch

import prepare


HISTORICAL_PACKET = prepare.ROOT / "review-output/customer-stale-predecessor-v1"
HISTORICAL_ID = json.loads((HISTORICAL_PACKET / "fixtures.json").read_bytes())["fixture_run_id"]
TEST_ID = "d71b17d0-8156-416b-aadb-d2abc2c3ef21"
ORDER = re.compile(
    r"^SELECT jsonb_agg\(jsonb_build_object\('table',table_name,'count',row_count,"
    r"'sha256',row_sha\) ORDER BY table_name(?P<collation> COLLATE \"C\")?\) FROM \("
)
BRANCH = re.compile(
    r"SELECT '(?P<name>[a-z_]+\.[a-z_]+)' AS table_name,.* AS row_sha FROM "
    r"(?P<relation>[a-z_]+\.[a-z_]+) t(?: WHERE id<>ALL\(.*\))?"
)


class SnapshotMock:
    """Model only the finite generated observer, with a different default order."""

    def __init__(self, default_collation_key):
        self.default_collation_key = default_collation_key
        self.rows = None

    def raw(self, role, query):
        order = ORDER.match(query)
        if role != "postgres" or order is None or not query.endswith(") state;\n"):
            raise AssertionError("Unmodeled snapshot observer")
        union = query[order.end():].removesuffix(") state;\n")
        names = []
        for sql in union.split(" UNION ALL "):
            branch = BRANCH.fullmatch(sql)
            if branch is None or branch["name"] != branch["relation"]:
                raise AssertionError("Unmodeled snapshot projection")
            names.append(branch["relation"])
        if len(names) != 42 or len(set(names)) != 42:
            raise AssertionError("Expected 42 distinct SQL projections")
        key = str.encode if order["collation"] else self.default_collation_key
        self.rows = [
            {
                "table": table,
                "count": 0,
                "sha256": prepare.sha(("modeled:" + table).encode("utf-8")),
            }
            for table in sorted(names, key=key)
        ]
        return json.dumps(self.rows)


def punctuation_insensitive(value):
    return (value.replace(".", "").replace("_", ""), value)


class Checks(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.core = runpy.run_path(str(prepare.ROOT / "scripts/sql-review/run-customer-stale-predecessor-v1.py"))
        cls.protocol = runpy.run_path(str(prepare.ROOT / prepare.PROTOCOL))
        cls.application = (prepare.ROOT / "review-output/foundation-application.review.sql").read_bytes()
        cls.native = json.loads(
            (prepare.ROOT / "tests/offline/customer-stale-predecessor-v1/native-before.json").read_bytes()
        )

    def setUp(self):
        for owner, name in ((subprocess, "Popen"), (subprocess, "run"), (socket.socket, "connect")):
            guard = patch.object(owner, name, side_effect=AssertionError("Actual execution is forbidden"))
            guard.start()
            self.addCleanup(guard.stop)
        self.original, self.old = prepare.load_parent(prepare.ROOT).build(prepare.ROOT, HISTORICAL_ID)
        self.corrected, self.new = prepare.build(prepare.ROOT, HISTORICAL_ID)
        self.world = SnapshotMock(punctuation_insensitive)

    def coordinator(self, files, packet):
        evidence = self.core["Evidence"](lambda report: None)
        core = self.core["coordinator_class"]({}, self.protocol)
        coordinator = core(
            packet,
            files,
            {"review-output/foundation-application.review.sql": self.application},
            "a" * 64,
            self.native,
            evidence,
        )
        coordinator.raw = self.world.raw
        return coordinator

    def test_exact_leaf_and_source_binding_delta(self):
        observed = {p.name: p.read_bytes() for p in HISTORICAL_PACKET.iterdir() if p.is_file()}
        self.assertEqual({name: text.encode("utf-8") for name, text in self.original.items()}, observed)
        self.assertEqual(set(self.original), set(self.corrected))
        changed = [name for name in self.original if self.original[name] != self.corrected[name]]
        self.assertEqual(set(changed), {prepare.SNAPSHOT, "fixtures.json"})
        observer = self.corrected[prepare.SNAPSHOT]
        self.assertEqual(observer.count('COLLATE "C"'), 1)
        self.assertEqual(observer.replace(' COLLATE "C"', "", 1), self.original[prepare.SNAPSHOT])

        expected = deepcopy(self.old)
        expected["source_files_sha256"][prepare.SELF] = prepare.sha((prepare.ROOT / prepare.SELF).read_bytes())
        expected["prepared_files_sha256"][prepare.SNAPSHOT] = prepare.sha(observer.encode("utf-8"))
        content = {key: expected[key] for key in ("source_files_sha256", "prepared_files_sha256")}
        expected["content_sha256"] = prepare.sha(
            json.dumps(content, sort_keys=True, separators=(",", ":")).encode("utf-8")
        )
        self.assertEqual(json.loads(self.corrected["fixtures.json"]), expected)

    def test_default_order_stops_at_strict_shape_check(self):
        coordinator = self.coordinator(self.original, self.old)
        with self.assertRaises(self.core["HeldFailure"]) as refusal:
            coordinator.snapshot()
        self.assertEqual(refusal.exception.code, "COMPLETE42_STATE_SHAPE")
        self.assertEqual(coordinator.evidence.value["operations"][-1]["shape_valid"], False)
        self.assertEqual(
            set(row["table"] for row in self.world.rows), set(self.old["full42_tables"])
        )
        self.assertNotEqual(
            [row["table"] for row in self.world.rows], self.old["full42_tables"]
        )

    def test_explicit_order_passes_same_strict_shape_check(self):
        coordinator = self.coordinator(self.corrected, self.new)
        rows = coordinator.snapshot()
        self.assertEqual([row["table"] for row in rows], self.new["full42_tables"])
        self.assertEqual(
            coordinator.evidence.value["operations"][-1],
            {"stage": "FULL42_STATE", "shape_valid": True, "table_count": 42},
        )
        for wrong in (rows[:-1], list(reversed(rows)), [dict(rows[0], count=True), *rows[1:]]):
            self.assertFalse(self.protocol["state_shape"](wrong, self.new["full42_tables"]))

    def test_mock_refuses_unmodeled_collation(self):
        wrong = self.corrected[prepare.SNAPSHOT].replace('COLLATE "C"', 'COLLATE "default"')
        with self.assertRaisesRegex(AssertionError, "Unmodeled snapshot observer"):
            self.world.raw("postgres", wrong)

    def test_fresh_fixture_output_is_exact_and_exclusive(self):
        with tempfile.TemporaryDirectory() as temp:
            output = Path(temp) / "source-only"
            args = ["--fixture-run-id", TEST_ID, "--output", str(output)]
            with redirect_stdout(io.StringIO()) as result:
                self.assertEqual(prepare.main(args), 0)
            emitted = json.loads(result.getvalue())
            files, packet = prepare.build(prepare.ROOT, TEST_ID)
            self.assertNotEqual(packet["baseline"]["ids"], self.old["baseline"]["ids"])
            self.assertEqual(packet["status"], "NOT_RUN")
            self.assertIs(packet["database_contacted"], False)
            self.assertIs(packet["sql_executed"], False)
            self.assertEqual(emitted["fixtures_sha256"], prepare.sha(files["fixtures.json"].encode("utf-8")))
            with self.assertRaises(FileExistsError):
                prepare.main(args)
            self.assertEqual(
                {p.name: p.read_bytes() for p in output.iterdir()},
                {name: text.encode("utf-8") for name, text in files.items()},
            )


if __name__ == "__main__":
    unittest.main()
