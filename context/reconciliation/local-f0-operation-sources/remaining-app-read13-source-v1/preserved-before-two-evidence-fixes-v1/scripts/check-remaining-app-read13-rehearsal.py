"""Environment-free source, policy projection and recipe regressions for Read13."""
from copy import deepcopy
import importlib.util
import json
from pathlib import Path
import re
import sys
import unittest
import uuid
from pglast import ast,parse_sql
from pglast.stream import RawStream
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'scripts'))
import remaining_app_read13_protocol as P
spec=importlib.util.spec_from_file_location('read13_source_generator',ROOT/'scripts/prepare-remaining-app-read13-rehearsal.py');G=importlib.util.module_from_spec(spec);spec.loader.exec_module(G)

def scalar(node):
 if isinstance(node,ast.TypeCast):return scalar(node.arg)
 if isinstance(node,ast.A_Const):return None if node.isnull else node.val.sval if isinstance(node.val,ast.String) else node.val.ival
 if isinstance(node,ast.A_ArrayExpr):return [scalar(x) for x in node.elements]
 raise AssertionError('UNREGISTERED_POLICY_CONSTANT')

class SourceTests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.files,cls.packet=G.build();cls.plan=cls.packet['fixture_plan'];cls.application=(ROOT/'review-output/foundation-application.review.sql').read_bytes();cls.policies={};cls.triggers={};cls.foreign={}
  for raw in parse_sql(cls.application.decode()):
   node=raw.stmt
   if isinstance(node,ast.CreatePolicyStmt) and node.cmd_name=='select' and any(r.rolename=='wa_app_runtime' for r in node.roles):cls.policies[node.table.schemaname+'.'+node.table.relname]=node
   if isinstance(node,ast.CreateTrigStmt):cls.triggers[node.relation.schemaname+'.'+node.relation.relname+'/'+node.trigname]=node
   constraints=[]
   if isinstance(node,ast.CreateStmt):constraints=[x for x in(node.tableElts or())if isinstance(x,ast.Constraint)]
   elif isinstance(node,ast.AlterTableStmt):constraints=[x.def_ for x in node.cmds if isinstance(x.def_,ast.Constraint)]
   for constraint in constraints:
    if constraint.contype.name=='CONSTR_FOREIGN':cls.foreign[node.relation.schemaname+'.'+node.relation.relname,constraint.conname]=constraint
 def test_all_generated_sql_parses(self):
  statements=0
  for name,text in self.files.items():
   if name.endswith('.sql'):statements+=len(parse_sql(text))
  self.assertGreater(statements,400)
 def test_byte_reproduction(self):self.assertEqual(self.files,G.build()[0])
 def test_exact_limits_claims_and_79_issued_grants(self):
  P.exact(self.packet['finite_caps'],P.FINITE,'LIMITS');self.assertEqual(len(self.packet['cases']),82);self.assertEqual(sum(c['grant'] is not None for c in self.packet['cases'])+len(self.plan['setup_grant_contexts']),79)
  self.assertEqual(len(self.packet['claim_ceilings']),13);self.assertEqual(sum(c['claim'] is not None for c in self.packet['cases']),26)
  self.assertEqual(len({c['claim'] for c in self.packet['cases'] if c['claim']}),13)
 def test_before_pin_uuid_mapping_every_reference(self):
  original=P.unique_json((ROOT/P.PLAN_PATH).read_bytes());run=str(uuid.uuid4());actual=P.materialize(original,run);text=P.canonical(actual)
  for side,labels in original['fixture_namespace']['preview_ids'].items():
   for label,old in labels.items():self.assertNotIn(old,text);self.assertIn(str(uuid.uuid5(uuid.UUID(run),'read13/'+side+'/'+label)),text)
  self.assertNotIn(original['fixture_namespace']['preview'],text)
  with self.assertRaises(P.HeldFailure):P.materialize(original,original['fixture_namespace']['preview'])
 def test_all_13_actual_policy_projections(self):
  for read in self.plan['selected_reads']:
   policy=self.policies[read['table']];call=policy.qual;self.assertIsInstance(call,ast.FuncCall);self.assertEqual(call.funcname[-1].sval,'row_allowed');self.assertEqual(len(call.args),7)
   self.assertEqual(scalar(call.args[1]),read['model']);self.assertEqual(scalar(call.args[3]),'SELECT');self.assertEqual(scalar(call.args[4]),read['fields'])
   revision=call.args[5].arg if isinstance(call.args[5],ast.TypeCast) else call.args[5]
   if read['revision_column'] is None:self.assertIsNone(scalar(revision))
   else:self.assertIsInstance(revision,ast.ColumnRef);self.assertEqual(revision.fields[-1].sval,read['revision_column'])
 def test_complete_role_visible_columns_not_select_id_only(self):
  for read in self.plan['selected_reads']:
   text=self.files[next(c['sql'] for c in self.packet['cases'] if c['name']==read['model']+'/positive/A')]
   statement=next(r.stmt for r in parse_sql(text) if isinstance(r.stmt,ast.SelectStmt) and r.stmt.fromClause and isinstance(r.stmt.fromClause[0],ast.RangeSubselect) and r.stmt.fromClause[0].subquery.fromClause[0].schemaname+'.'+r.stmt.fromClause[0].subquery.fromClause[0].relname==read['table'])
   selected=statement.fromClause[0].subquery
   self.assertEqual([x.val.fields[-1].sval for x in selected.targetList],read['columns'])
 def test_exact15_real_trigger_names_and_deferral(self):
  identities=[]
  for t in self.plan['trigger_setup_allowlist']:
   identity=t['identity'];identities.append(identity);actual=self.triggers[identity];self.assertEqual(actual.trigname,t['definition']['name']);self.assertEqual(bool(actual.deferrable),t['definition']['deferrable']);self.assertEqual(bool(actual.initdeferred),t['definition']['initially_deferred']);self.assertEqual('.'.join(x.sval for x in actual.funcname),t['definition']['function'])
  self.assertEqual(len(identities),15);self.assertIn('app.track_subscription_events/enrollment_commit',identities);self.assertNotIn('app.track_subscription_events/owner_commit',identities)
  disabled=[r.stmt for r in parse_sql(self.files['fixture-disable-exact15.sql']) if isinstance(r.stmt,ast.AlterTableStmt)]
  self.assertEqual(len(disabled),15)
  self.assertNotRegex(self.files['fixture-disable-exact15.sql'],r'(?i)\bALL\b|session_replication_role')
 def test_deferred_flush_precedes_each_setup_commit(self):
  for group in self.packet['setup_groups']:
   statements=parse_sql(self.files[group['sql']]);flush=[i for i,r in enumerate(statements) if isinstance(r.stmt,ast.ConstraintsSetStmt)];commits=[i for i,r in enumerate(statements) if isinstance(r.stmt,ast.TransactionStmt)]
   self.assertEqual(len(flush),1);self.assertEqual(len(commits),1);self.assertLess(flush[0],commits[0])
 def test_restricted_setup_never_names_server_owned_default_columns(self):
  access=json.loads((ROOT/'context/reconciliation/foundation-sql-draft-access.json').read_bytes())
  models={row['object']:row for row in self.packet['models'].values()}
  for group in self.packet['setup_groups']:
   if group['login']!='wa_app_runtime':continue
   for raw in parse_sql(self.files[group['sql']]):
    node=raw.stmt
    if not isinstance(node,ast.InsertStmt):continue
    table=node.relation.schemaname+'.'+node.relation.relname;columns={column.name for column in node.cols}
    self.assertNotIn('created_at',columns);self.assertNotIn('mutation_transaction_id',columns)
    allowed=next(row for row in access if row['role']=='wa_app_runtime' and row['model']==models[table]['model'] and row['operation']=='INSERT')
    self.assertTrue(columns<=set(allowed['columns']),table)
 def test_48_rows_and_78_fk_source_links(self):
  values={(r['table'],r['values']['id']):r['values'] for r in self.plan['fixture_rows']};self.assertEqual(len(values),48)
  self.assertEqual(len(self.plan['verified_direct_FK_links']),78)
  self.assertEqual(sum(sum(g['table_increments'].values()) for g in self.packet['setup_groups']),48)
 def test_all78_links_survive_the_actual_emitted_INSERT_projection(self):
  rows={r['side']+'/'+r['label']:r for r in self.plan['fixture_rows']};inserted={}
  for group in self.packet['setup_groups']:
   for raw in parse_sql(self.files[group['sql']]):
    node=raw.stmt
    if not isinstance(node,ast.InsertStmt):continue
    table=node.relation.schemaname+'.'+node.relation.relname;values={col.name:val for col,val in zip(node.cols,node.selectStmt.valuesLists[0])};inserted[table,scalar(values['id'])]=values
  for link in self.plan['verified_direct_FK_links']:
   child,parent=rows[link['child']],rows[link['parent']];foreign=self.foreign[child['table'],link['constraint']];self.assertEqual(foreign.pktable.schemaname+'.'+foreign.pktable.relname,parent['table']);values=inserted[child['table'],child['values']['id']]
   referenced=[x.sval for x in foreign.pk_attrs]if foreign.pk_attrs else['id']
   for column,pk in zip(foreign.fk_attrs,referenced):self.assertEqual(scalar(values[column.sval]),parent['values'][pk],link['constraint'])
 def test_key_grammars_and_distinct_slash_enrollment_key(self):
  for side in ('A','B'):
   rows={r['label']:r['values'] for r in self.plan['fixture_rows'] if r['side']==side};q=rows['Command'];key=q['semantic_key'];self.assertRegex(key,r'^[A-Za-z0-9][A-Za-z0-9._:-]*$')
   self.assertEqual(q['result_body']['value']['receipt']['semanticKey'],key)
   for label,column in [('CommittedEffect','semantic_effect_key'),('Reservation','semantic_key'),('UsageEvent','semantic_effect_key')]:self.assertEqual(rows[label][column],key)
   enrollment='customer_buyer_profile/'+rows['Customer']['id']+'/default-free-enrollment/v1';self.assertEqual(rows['CommandOutbox']['payload']['semanticKey'],enrollment);self.assertEqual(rows['Work']['semantic_work_key'],enrollment)
 def test_clock_markers_never_json_strings_and_digest_postgres_only(self):
  sql=self.files['G2-A.sql'];self.assertNotIn('from_actual_server_clock',sql);self.assertNotIn('host_JSON_digest_forbidden',sql);self.assertIn('transaction_timestamp()',sql);self.assertIn("encode(sha256(convert_to(",sql)
  with self.assertRaises(P.HeldFailure):P.json_sql({'server_value':'CANARY'})
  with self.assertRaises(P.HeldFailure):P.value_sql({'server_expression':'pg_sleep(9)'})
 def test_only_selected_target_generation_equality_model(self):
  read=next(r for r in self.plan['selected_reads'] if r['model']=='RuntimeEffectReceipt');ctx=deepcopy(read['contexts']['A']);ctx['security_generation']=19;ctx['source_generation']=7
  effect=ctx['expected_ids'][0];self.assertIn('RuntimeEffectReceipt/'+effect+'/revision/0',ctx['allowed_fields']);self.assertNotEqual(ctx['target_kind'],'RuntimeEffectReceipt')
  # Actual row_allowed applies root equality only in this source condition;
  # Effect's independent row_revision/fence token is still mandatory.
  text=self.application.decode();self.assertIn('IF row_revision IS NOT NULL AND g.target_kind=model_name AND g.target_id=row_key',text)
 def test_read_rowset_verdict_strict_types_and_canaries(self):
  case=self.packet['cases'][0];rows=[json.dumps(x) for x in case['expected_records']];self.assertEqual(P.ordinary_verdict(case,0,rows,True,'')['status'],'PASS')
  for code,ack,stderr in [(False,True,''),(0,1,''),(0,True,'CANARY'),(3,False,'ERROR: 42501')]:
   with self.assertRaises(P.HeldFailure):P.ordinary_verdict(case,code,rows,ack,stderr)
  with self.assertRaises(P.HeldFailure):P.ordinary_verdict(case,0,rows+[json.dumps({'CANARY':True})],True,'')
 def test_wrong_parent_prerequisite_not_invented(self):
  reservation=next(c for c in self.plan['scenario_recipes'] if c['id']=='RuntimeReservation/root');self.assertEqual(reservation['expected_ids'],[]);self.assertTrue(all(x['expected_ids'] for x in reservation['expected_prerequisite_rowsets']))
 def test_no_read_only_factory_or_typed_owner_contract_claim(self):
  self.assertTrue(all(c['claim'] is None for c in self.packet['cases'] if c['kind']=='binder-denial'));self.assertEqual(len(self.packet['worker_acl_ceiling_rows']),32)
  self.assertTrue(all(g['login']!='wa_worker' for g in self.packet['setup_groups']))

if __name__=='__main__':unittest.main()
