"""Environment-free regression for prepared expressions on shared trigger rows.

PostgreSQL resolves every field in one prepared expression. Only a separate
table-name IF can narrow the row shape used by its nested expressions. This
focused analysis covers infrastructure_atomic; it does not qualify all SQL.
"""
import json
from pathlib import Path
import re
import unittest
from pglast import ast, parse_sql, parse_plpgsql
from pglast.stream import RawStream
from pglast.visitors import Visitor

ROOT=Path(__file__).resolve().parents[1]
FUNCTION='platform_private.infrastructure_atomic'
OLD="""IF TG_TABLE_NAME='owner_mutation_evidence' AND (c.owner_module_id<>NEW.owner_module_id OR c.operation<>NEW.action)
   THEN RAISE EXCEPTION 'foreign owner command'; END IF;"""
NEW="""IF TG_TABLE_NAME='owner_mutation_evidence' THEN
   IF c.owner_module_id<>NEW.owner_module_id OR c.operation<>NEW.action
    THEN RAISE EXCEPTION 'foreign owner command'; END IF;
  END IF;"""

def expression(query):return parse_sql('SELECT '+query)[0].stmt.targetList[0].val

class Fields(Visitor):
    def __init__(self):super().__init__();self.fields=set()
    def visit_ColumnRef(self,ancestors,node):
        if len(node.fields)==2 and all(isinstance(v,ast.String) for v in node.fields) and node.fields[0].sval in ('new','old'):
            self.fields.add(node.fields[1].sval)

def narrowing(query):
    """Recognize only a standalone TG_TABLE_NAME equality/IN, never AND/OR."""
    node=expression(query)
    if not isinstance(node,ast.A_Expr) or not isinstance(node.lexpr,ast.ColumnRef):return None
    if len(node.lexpr.fields)!=1 or node.lexpr.fields[0].sval!='tg_table_name':return None
    if len(node.name)!=1 or node.name[0].sval!='=':return None
    values=node.rexpr if type(node.rexpr) is tuple else (node.rexpr,)
    if not all(isinstance(v,ast.A_Const) and isinstance(v.val,ast.String) for v in values):return None
    return {v.val.sval for v in values}

def inspect(sql):
    statements=parse_sql(sql);tables={};attached=set();definition=None
    for raw in statements:
        node=raw.stmt
        if isinstance(node,ast.CreateStmt):
            tables[node.relation.relname]={c.colname for c in node.tableElts or () if isinstance(c,ast.ColumnDef)}
        elif isinstance(node,ast.CreateTrigStmt) and '.'.join(p.sval for p in node.funcname)==FUNCTION:
            attached.add(node.relation.relname)
        elif isinstance(node,ast.CreateFunctionStmt) and '.'.join(p.sval for p in node.funcname)==FUNCTION:
            definition=RawStream()(node)
    assert definition and attached and attached<=set(tables)
    function=parse_plpgsql(definition)[0]['PLpgSQL_function']
    errors=[]
    def check(query,possible,mode):
        tree=expression(query) if mode==2 else parse_sql(query)
        fields=Fields();fields(tree)
        for table in sorted(possible):
            for missing in sorted(fields.fields-tables[table]):
                errors.append({'table':table,'missing_field':missing})
    def walk(stmts,possible):
        for tagged in stmts:
            if 'PLpgSQL_stmt_if' in tagged:
                node=tagged['PLpgSQL_stmt_if'];query=node['cond']['PLpgSQL_expr']['query']
                check(query,possible,2)
                match=narrowing(query)
                walk(node.get('then_body',[]),possible if match is None else possible&match)
                remaining=possible if match is None else possible-match
                for tagged_elsif in node.get('elsif_list',[]):
                    branch=tagged_elsif['PLpgSQL_if_elsif'];query=branch['cond']['PLpgSQL_expr']['query']
                    check(query,remaining,2);match=narrowing(query)
                    walk(branch.get('stmts',[]),remaining if match is None else remaining&match)
                    if match is not None:remaining=remaining-match
                walk(node.get('else_body',[]),remaining)
            else:
                def scan(value):
                    if isinstance(value,dict):
                        if 'PLpgSQL_expr' in value:
                            e=value['PLpgSQL_expr'];check(e['query'],possible,e.get('parseMode',0))
                        else:
                            for item in value.values():scan(item)
                    elif isinstance(value,list):
                        for item in value:scan(item)
                scan(tagged)
    walk(function['action']['PLpgSQL_stmt_block']['body'],attached)
    return errors

class TriggerRowShapeTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):cls.sql=(ROOT/'review-output/foundation-application.review.sql').read_text(encoding='utf8')
    def test_current_shared_trigger_uses_only_fields_on_each_possible_row(self):self.assertEqual(inspect(self.sql),[])
    def test_restored_combined_expression_detects_real_outbox_missing_fields(self):
        self.assertEqual(self.sql.count(NEW),1)
        restored=self.sql.replace(NEW,OLD)
        self.assertEqual(inspect(restored),[{'table':'runtime_outbox_message','missing_field':'action'},{'table':'runtime_outbox_message','missing_field':'owner_module_id'}])
    def test_missing_field_not_protected_by_boolean_false_or_table_term(self):
        mutated=self.sql.replace(NEW,"IF false AND NEW.owner_module_id IS NOT NULL THEN RETURN NULL; END IF;")
        self.assertEqual(inspect(mutated),[{'table':'runtime_outbox_message','missing_field':'owner_module_id'}])
    def test_nested_branch_keeps_both_owner_and_operation_comparisons(self):
        self.assertIn('c.owner_module_id<>NEW.owner_module_id OR c.operation<>NEW.action',self.sql)
        self.assertIn("RAISE EXCEPTION 'foreign owner command'",self.sql)

if __name__=='__main__':unittest.main(verbosity=2)
