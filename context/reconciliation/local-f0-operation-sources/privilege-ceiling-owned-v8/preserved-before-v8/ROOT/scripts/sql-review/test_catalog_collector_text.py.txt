"""Source and retained-hash regressions for full ACL function identities.

No database boundary exists here. The separately reviewed native control proves
PostgreSQL's type resolution; these checks reject restoring the faulty first arm.
"""
from collections import Counter
import hashlib,json
from pathlib import Path
import unittest
from pglast.parser import parse_sql_json

ROOT=Path(__file__).resolve().parents[2]
SOURCE=ROOT/'scripts/sql-review/collect_native_catalog.sql'
PROBE=ROOT/'scripts/sql-review/catalog-text-preflight.sql'
EVIDENCE=ROOT/'context/reconciliation/local-f0-catalog-eb2aae6-2e4f5d40-execution.json'
sha=lambda b:hashlib.sha256(b).hexdigest()

def walk(value):
    if isinstance(value,dict):
        yield value
        for item in value.values():yield from walk(item)
    elif isinstance(value,list):
        for item in value:yield from walk(item)

def first_acl_object(sql):
    tree=json.loads(parse_sql_json(sql))
    cte=next(n['CommonTableExpr'] for n in walk(tree) if n.get('CommonTableExpr',{}).get('ctename')=='acl_objects')
    select=cte['ctequery']['SelectStmt']
    while select.get('op')=='SETOP_UNION':select=select['larg'].get('SelectStmt',select['larg'])
    return next(n['ResTarget']['val'] for n in select['targetList'] if n['ResTarget'].get('name')=='object')

def require_text_projection(sql):
    value=first_acl_object(sql)
    assert set(value)=={'TypeCast'}
    cast=value['TypeCast'];typ=cast['typeName']
    assert [n['String']['sval'] for n in typ['names']]==['text']
    assert not typ.get('arrayBounds') and not typ.get('typmods')
    assert [n['String']['sval'] for n in cast['arg']['ColumnRef']['fields']]==['n','nspname']

class CollectorTextTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        expected=(ROOT/'review-output/native-catalog/expected.json').read_bytes()
        assert sha(expected)=='9ad2129c9b7b7b5fd99f2088ae94215326f6ccbf40550945694c44538d8d0976'
        cls.expected=json.loads(expected)['expected']
        raw=EVIDENCE.read_bytes();assert sha(raw)=='76923eea9f3a68cb6157a0ed23432662492d79c068a7b58be507309edbe3e452'
        cls.evidence=json.loads(raw)
        cls.diag=cls.evidence['sanitized_report']['rejected_observations'][0]['metadata_vocabulary_review']

    def test_first_union_object_is_explicit_unbounded_text(self):
        require_text_projection(SOURCE.read_text())

    def test_restoring_name_or_another_first_type_is_detected(self):
        text=SOURCE.read_text()
        for replacement in ('n.nspname AS object','n.nspname::name AS object','n.nspname::varchar AS object','n.nspname::text[] AS object'):
            changed=text.replace('n.nspname::text AS object',replacement)
            self.assertNotEqual(changed,text)
            with self.assertRaises(AssertionError):require_text_projection(changed)

    def test_all_actual_unknown_hashes_match_exactly_the_source_long_signatures(self):
        expected={sha(name.encode()[:63]):name for name in self.expected['functions'] if len(name.encode())>63}
        self.assertEqual(len(expected),45)
        self.assertTrue(all(name.isascii() for name in expected.values()))
        self.assertEqual({r['value_sha256'] for r in self.diag['unknown_strings']},set(expected))
        self.assertEqual(self.diag['unknown_strings_seen'],125)
        self.assertTrue(self.diag['traversal_complete']);self.assertFalse(self.diag['entries_truncated'])
        self.assertEqual(self.diag['unregistered_fields_omitted'],0)
        self.assertTrue(all(row['path'][0] in ('nonowner_acl','owner_acl') and row['path'][-1]=='object' and not row['has_control_characters'] for row in self.diag['unknown_strings']))

    def test_actual_acl_multiplicities_equal_source_grants_and_owner_rows(self):
        long={name for name in self.expected['functions'] if len(name.encode())>63}
        wanted=Counter(sha(row['object'].encode()[:63]) for row in self.expected['nonowner_acl'] if row['kind']=='FUNCTION' and row['object'] in long)
        got=Counter(row['value_sha256'] for row in self.diag['unknown_strings'] if row['path'][0]=='nonowner_acl')
        self.assertEqual(got,wanted);self.assertEqual(sum(got.values()),80)
        owners=Counter(row['value_sha256'] for row in self.diag['unknown_strings'] if row['path'][0]=='owner_acl')
        self.assertEqual(owners,Counter({sha(name.encode()[:63]):1 for name in long}))

    def test_native_probe_is_read_only_and_uses_a_real_source_signature(self):
        text=PROBE.read_text();tree=json.loads(parse_sql_json(text))
        self.assertEqual([next(iter(row['stmt'])) for row in tree['stmts']],['TransactionStmt','VariableSetStmt','SelectStmt','TransactionStmt'])
        self.assertIn('BEGIN READ ONLY;',text);self.assertIn('ROLLBACK;',text)
        signature='platform_private.track_atomic_valid(pg_catalog.text,pg_catalog.jsonb,pg_catalog.jsonb)'
        self.assertIn(signature,self.expected['functions']);self.assertGreater(len(signature.encode()),63)
        self.assertIn(signature,text)
        self.assertNotIn('FROM app.',text);self.assertNotIn('FROM platform.',text)

if __name__=='__main__':unittest.main(verbosity=2)
