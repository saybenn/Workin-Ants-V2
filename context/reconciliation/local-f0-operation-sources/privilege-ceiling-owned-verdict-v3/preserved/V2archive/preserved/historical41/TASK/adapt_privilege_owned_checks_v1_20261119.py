"""Adapt NEW draft tests only; no runtime/source permission changes."""
from pathlib import Path
import ast
TASK=Path(__file__).resolve().parent
path=TASK/'check_local_f0_privilege_ceiling_safety_sql_v1_operation.py'
text=path.read_text().replace("len(n['HELPERS']),7","len(n['HELPERS']),8").replace("len(n['PRIVILEGE_FIXTURES']['cases']),121","len(n['PRIVILEGE_FIXTURES']['cases']),200")
text=text.replace('scripts/sql-review/run-worker-control-rehearsal.py','scripts/sql-review/run-native-table-denials-v3.py')
text=text.replace("['coordinate']","['main']").replace("{'coordinate':","{'main':")
def replace_method(name,body):
    global text
    tree=ast.parse(text);node=next(n for n in ast.walk(tree)if isinstance(n,ast.FunctionDef)and n.name==name)
    lines=text.splitlines(keepends=True);text=''.join(lines[:node.lineno-1])+body.rstrip()+'\n'+''.join(lines[node.end_lineno:])
replace_method('component', ''' def component(self,status='PASS_PREPARED_PRIVILEGE_CEILINGS_ONLY_CASES_NOT_RUN',wrong_cid=False,extra=False):
  n=self.n;n['OUT'].mkdir();native={'format':'workinants.native-catalog.v1'};(n['OUT']/'native-before.json').write_text(json.dumps(native));(n['OUT']/'catalog-comparison.json').write_text(json.dumps({'status':'PASS'}));fixture=json.loads((ROOT/'review-output/privilege-ceiling-control-rehearsal/fixtures.json').read_bytes());np=json.loads((ROOT/'review-output/native-table-denials-v2/packet.json').read_bytes());module=runpy.run_path(str(ROOT/'scripts/sql-review/run-native-table-denials-v3.py'))
  n.update(COMMIT='b'*40,TREE='c'*40,PACKET='d'*64,PRIVILEGE_FIXTURES=fixture,finalized={NAME},inspect_owner=lambda *a,**k:None,closed_backends=lambda *a,**k:None,collect_native=lambda *a,**k:native,read_target_manifest=lambda p:b'{}')
  n['PRIVILEGE_NATIVE'].update(module=module,packet=np,preinstall_observed=True,postinstall_observed=True)
  n['report'].update(catalog_comparison={'status':'PASS','check_counts':{'PASS':29089}},ledger_comparison={'status':'PASS','checks':[{'status':'PASS'}for _ in range(22)]},qualified_native_snapshot_sha256=n['digest'](native));n['report']['steps']['CATALOG-ORACLE']='PASS_ROLLBACK_OBSERVED_NOT_WHOLE_CASE'
  n['MANIFEST']={'packet_files_sha256':{p:hashlib.sha256((ROOT/p).read_bytes()).hexdigest()for p in module['MODULES']},'migration_targets':{'ok':{}},'privilege_ceiling':{}}
  n['SAFE_FILES'].update({'provider-preinstall-proof.json','privilege-ceiling-native-attestation.json','privilege-ceiling-run-plan.json','privilege-ceiling-component-result.json','privilege-ceiling-native-final.json'})
  plans=[]
  def main(argv):
   plan_path=Path(argv[argv.index('--run-plan')+1]);raw=plan_path.read_bytes();plan=json.loads(raw);evidence=Path(argv[argv.index('--evidence-directory')+1]);plans.append(plan)
   results=[]
   for c in fixture['cases']:
    kind=c['diagnostic']['kind'];d={'matched':True,'sqlstate':'P0001'if kind=='IMMUTABLE_GRANT'else'42501','kind':kind,'gate':None,'object':None,'source_position_verified':False,'source_frame_verified':kind=='IMMUTABLE_GRANT','selected_column_or_verb_isolation_claimed':False}
    results.append({'name':c['name'],'source_case_id':c['source_case_id'],'assertion_id':c['assertion_id'],'status':'PASS_FINITE_PRIVILEGE_CONTRAST_ONLY','closed_before_observers':True,'complete_state_unchanged':True,'diagnostic':d,'whole_case_promoted':False})
   if status!='PASS_PREPARED_PRIVILEGE_CEILINGS_ONLY_CASES_NOT_RUN':results=results[:2]
   value={'schema':'workinants.privilege-ceiling-evidence.v1','status':status,'run_id':RUN,'source_commit':n['COMMIT'],'source_tree':n['TREE'],'operation_packet_sha256':n['PACKET'],'reviewed_privilege_content_sha256':n['PRIVILEGE_CONTENT_SHA'],'run_plan_sha256':'0'*64 if wrong_cid else hashlib.sha256(raw).hexdigest(),'database_posture':'D','evidence_complete':True,'source_packet_unchanged_after':True,'subsequent_cases_stopped':False,'facets':[],'results':results,'selected_controls':fixture['control_links'],'authentication':[{}for _ in range(9)],'definer_metadata':[{'function':r['identity'],'owner_body_definer_path_match':True}for r in fixture['source_definers']],'native_controls':[{'case_id':r['id'],'status':'NATIVE_FIXTURE_VALIDITY_ONLY_NO_OWNER_OR_CASE_QUALIFICATION','rolled_back':True,'all100_guards_restored':True,'native205_unchanged':True}for r in np['cases']],'issuer_protocols':[{'name':name,'status':'PASS_FINITE_ISSUER_PROTOCOL_ONLY','same_run_and_actual_logins':True,'all_operation_backends_closed_before_observation':True,'complete_state_verified':True,'whole_case_promoted':False}for name in('ISSUER-LEGITIMATE-PERSON-ISSUE-OWN-READ-BOUND-SCALARS','ISSUER-LEGITIMATE-FIRST-ONE-WAY-REVOKE','ISSUER-STORED-SERVICE-GRANT-CANNOT-SELF-ATTEST-REVOKED-IDENTITY')],'operations':[{'closed_before_observers':True}for _ in range(244)],'global_client_boundaries':[{'stage':'MOCK_BOUNDARY','attempted':True,'confirmed':True}]}
   if extra:value['untrusted_extra']=CANARY
   evidence.mkdir();(evidence/'privilege-ceiling-results.json').write_text(json.dumps(value));return 0 if status=='PASS_PREPARED_PRIVILEGE_CEILINGS_ONLY_CASES_NOT_RUN'else 2
  n['load_reviewed_helper']=lambda p:{'main':main};return plans
''')
replace_method('test_component_plan_binds_same_source_run_CID_and_exact121_names', ''' def test_component_plan_binds_same_source_run_CID_and_exact200_native_digest(self):
  plans=self.component();self.n['privilege_ceiling_experiment']();self.assertEqual(len(plans),1);plan=plans[0];self.assertEqual((plan['run_id'],plan['native_plan']['immutable_container_id']),(RUN,CID));self.assertEqual(plan['packet_sha256'],self.n['PACKET']);self.assertEqual(plan['native_plan']['packet_sha256'],'8044d43f25c4a449f662bbb467183aac86d6a619836aae0988458098d59e0b69');self.assertEqual(self.n['report']['steps']['PRIVILEGE-CEILING-COMPONENT'],'PASS_FINITE_PREPARED_SQL_ONLY')
  value=json.loads((self.n['OUT']/'privilege-ceiling-component-result.json').read_bytes());self.assertEqual((value['completed_negative_contrasts'],value['definer_metadata'],value['native_validity_controls'],value['issuer_protocols']),(200,16,40,3));self.assertNotIn(CANARY,json.dumps(value))
''')
replace_method('test_partial_component_keeps_safe_summary_and_stops_without_native_final', ''' def test_partial_component_keeps_safe_reference_and_stops_without_native_final(self):
  self.component(status='STOPPED_PARTIAL_EVIDENCE_PRESERVED');native=Mock(side_effect=AssertionError('NO_LATER_NATIVE_CASE'));self.n['collect_native']=native
  with self.assertRaises(self.n['Stop']):self.n['privilege_ceiling_experiment']()
  self.assertEqual(self.n['report']['privilege_ceiling']['component_report_reference']['read_status'],'RETAINED');self.assertEqual(self.n['report']['primary_failure']['code'],'PRIVILEGE_CEILING_COMPONENT_NOT_QUALIFIED');native.assert_not_called()
''')
text=text.replace("'PASS_FINITE_PRIVILEGE_CEILING_SQL_SUBSET_ONLY'","'PASS_PREPARED_PRIVILEGE_CEILINGS_ONLY_CASES_NOT_RUN'")
text=text.replace("'PASS_FINITE_OWNER_READ_SQL_SUBSET_ONLY'","'PASS_PREPARED_PRIVILEGE_CEILINGS_ONLY_CASES_NOT_RUN'")
compile(text,str(path),'exec');path.write_text(text,encoding='utf8',newline='\n')
