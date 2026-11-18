"""Evaluate the collector's actual ACL projection AST without a database.

The separate reviewed runtime probe establishes PostgreSQL's zero-dimensional
array behavior; these tests detect restoring the erroneous source projections.
"""
import json
from pathlib import Path
import unittest
from pglast.parser import parse_sql_json

SOURCE=Path(__file__).with_name('collect_native_catalog.sql')

def walk(value):
    if isinstance(value,dict):
        yield value
        for item in value.values():yield from walk(item)
    elif isinstance(value,list):
        for item in value:yield from walk(item)

def names(items):return '.'.join(v['String']['sval'] for v in items)

def evaluate(node,values):
    if 'TypeCast' in node:return evaluate(node['TypeCast']['arg'],values)
    if 'A_Const' in node:
        value=node['A_Const']
        return None if value.get('isnull') else value['sval']['sval'] if 'sval' in value else value['ival'].get('ival',0)
    if 'ColumnRef' in node:return values[names(node['ColumnRef']['fields'])]
    if 'CaseExpr' in node:
        expression=node['CaseExpr']
        for clause in expression['args']:
            part=clause['CaseWhen']
            if evaluate(part['expr'],values) is True:return evaluate(part['result'],values)
        return evaluate(expression['defresult'],values)
    if 'CoalesceExpr' in node:
        for arg in node['CoalesceExpr']['args']:
            value=evaluate(arg,values)
            if value is not None:return value
        return None
    if 'A_Expr' in node:
        expression=node['A_Expr'];left=evaluate(expression['lexpr'],values);right=evaluate(expression['rexpr'],values)
        if left is None or right is None:return None
        operator=names(expression['name'])
        if operator=='=':return left==right
        if operator=='>':return left>right
    if 'FuncCall' in node:
        function=node['FuncCall'];name=names(function['funcname']);args=[evaluate(arg,values) for arg in function['args']]
        if name=='acldefault':return ('DEFAULT_ACL',args[0],args[1])
        if name=='cardinality':return None if args[0] is None else len(args[0])
    raise AssertionError('Unrecognized projection AST')

def projections(sql):
    tree=json.loads(parse_sql_json(sql));nodes=list(walk(tree))
    slot=next(n['CommonTableExpr']['ctequery'] for n in nodes if n.get('CommonTableExpr',{}).get('ctename')=='default_slots')
    acl=next(n['ResTarget']['val'] for n in walk(slot) if n.get('ResTarget',{}).get('name')=='acl')
    rows=next(n['CommonTableExpr']['ctequery'] for n in nodes if n.get('CommonTableExpr',{}).get('ctename')=='default_rows')
    explode=next(n['FuncCall']['args'][0] for n in walk(rows) if names(n.get('FuncCall',{}).get('funcname',[]))=='aclexplode')
    direct=next(n['FuncCall']['args'][0] for n in nodes if names(n.get('FuncCall',{}).get('funcname',[]))=='acldefault' and 'CaseExpr' in n['FuncCall']['args'][0] and any(names(x['ColumnRef']['fields'])=='r.relkind' for x in walk(n['FuncCall']['args'][0]) if 'ColumnRef' in x))
    return tree,acl,explode,direct

def contract(sql):
    tree,acl,explode,direct=projections(sql)
    assert evaluate(acl,{'s.schema':'app','d.defaclacl':None,'k.code':'S','r.oid':1}) is None
    assert evaluate(explode,{'d.acl':[]}) is None
    assert evaluate(acl,{'s.schema':'*','d.defaclacl':None,'k.code':'S','r.oid':1})==('DEFAULT_ACL','s',1)
    assert evaluate(direct,{'r.relkind':'S'})=='s'
    slots=next(n['CommonTableExpr']['ctequery'] for n in walk(tree) if n.get('CommonTableExpr',{}).get('ctename')=='default_slots')
    assert any([evaluate(x,{}) for x in row['List']['items']]==['SEQUENCE','S'] for n in walk(slots) if 'SelectStmt' in n for row in n['SelectStmt'].get('valuesLists',[]))

class CollectorAclTests(unittest.TestCase):
    def test_missing_schema_acl_remains_null_and_existing_acl_is_preserved(self):
        _,acl,_,_=projections(SOURCE.read_text());values={'s.schema':'app','d.defaclacl':None,'k.code':'S','r.oid':1}
        self.assertIsNone(evaluate(acl,values))
        for value in ([],['existing grant']):
            self.assertEqual(evaluate(acl,{**values,'d.defaclacl':value}),value)

    def test_empty_acl_skips_strict_expansion_and_nonempty_is_preserved(self):
        _,_,explode,_=projections(SOURCE.read_text())
        for value in (None,[]):self.assertIsNone(evaluate(explode,{'d.acl':value}))
        self.assertEqual(evaluate(explode,{'d.acl':['existing grant']}),['existing grant'])

    def test_sequence_function_code_and_catalog_code_remain_distinct(self):
        contract(SOURCE.read_text());_,acl,_,direct=projections(SOURCE.read_text())
        self.assertEqual(evaluate(direct,{'r.relkind':'r'}),'r')
        for code in ('r','f','T','n'):
            self.assertEqual(evaluate(acl,{'s.schema':'*','d.defaclacl':None,'k.code':code,'r.oid':1}),('DEFAULT_ACL',code,1))

    def test_restoring_each_original_projection_or_wrong_catalog_code_is_detected(self):
        sql=SOURCE.read_text()
        mutations=[sql.replace('ELSE d.defaclacl END AS acl',"ELSE COALESCE(d.defaclacl,'{}'::aclitem[]) END AS acl"),sql.replace('aclexplode(CASE WHEN cardinality(d.acl)>0 THEN d.acl ELSE NULL::aclitem[] END)','aclexplode(d.acl)'),sql.replace("r.relkind='S' THEN 's'", "r.relkind='S' THEN 'S'"),sql.replace("acldefault(CASE WHEN k.code='S' THEN 's'::\"char\" ELSE k.code END,r.oid)",'acldefault(k.code,r.oid)'),sql.replace("('SEQUENCE','S'::\"char\")","('SEQUENCE','s'::\"char\")")]
        for mutated in mutations:
            self.assertNotEqual(mutated,sql)
            with self.assertRaises(AssertionError):contract(mutated)

    def test_read_only_statement_boundary_is_preserved(self):
        tree,_,_,_=projections(SOURCE.read_text())
        self.assertEqual(len(tree['stmts']),4)
        self.assertEqual([next(iter(row['stmt'])) for row in tree['stmts']],['TransactionStmt','VariableSetStmt','SelectStmt','TransactionStmt'])
        self.assertIn('BEGIN READ ONLY;',SOURCE.read_text())

if __name__=='__main__':unittest.main(verbosity=2)
