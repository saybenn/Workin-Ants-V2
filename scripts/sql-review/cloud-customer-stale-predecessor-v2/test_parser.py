"""Check the compiled structure of the changed SQL with the pinned PG17 parser."""

import unittest

import pglast
from pglast import ast, parse_sql

import prepare
from test_prepare import TEST_ID


class ParserChecks(unittest.TestCase):
    def test_outer_aggregate_only_uses_explicit_bytewise_collation(self):
        self.assertEqual(pglast.__version__, "v7.21")
        files, _ = prepare.build(prepare.ROOT, TEST_ID)
        sql = files[prepare.SNAPSHOT].replace("__EXCLUDED_GRANT_IDS__", "ARRAY[]::uuid[]")
        statement, = parse_sql(sql)
        self.assertIsInstance(statement.stmt, ast.SelectStmt)
        result, = statement.stmt.targetList
        self.assertIsInstance(result.val, ast.FuncCall)
        self.assertEqual([part.sval for part in result.val.funcname], ["jsonb_agg"])
        sort, = result.val.agg_order
        self.assertIsInstance(sort.node, ast.CollateClause)
        self.assertEqual([part.sval for part in sort.node.collname], ["C"])
        self.assertIsInstance(sort.node.arg, ast.ColumnRef)
        self.assertEqual([field.sval for field in sort.node.arg.fields], ["table_name"])


if __name__ == "__main__":
    unittest.main()
