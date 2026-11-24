from pathlib import Path
from types import MappingProxyType
import ast,hashlib,importlib.util,json,sys
P=Path(__file__).resolve().parent;sys.dont_write_bytecode=True
E=[]
def guard(event,args):
 if event.startswith(('subprocess.','socket.')) or event in ('os.system','os.posix_spawn','os.spawn','os.exec'):E.append(event);raise AssertionError('FORBIDDEN_BOUNDARY')
sys.addaudithook(guard)
loader=importlib.util.spec_from_file_location('new_reader_spec_only',P/'scripts/local_f0_privilege485517b0_evidence.py');M=importlib.util.module_from_spec(loader);loader.loader.exec_module(M)
read=lambda rel:json.loads((P/rel).read_bytes())
plan=read('governance/bounded-source-plan.FROZEN.json');F=plan['preservation_and_frozen_graph'];parent=read(M.ASSET+'/evidence/run-evidence.json');child=read(M.ASSET+'/evidence/privilege-ceiling-component/privilege-ceiling-results.json');prior=read(M.ARCHIVE+'/prior687-assertion-evidence.json')
history=('prior687-assertion-evidence.json','prior687-qualification-status.json','prior-issuer-partial-record.json','validating-full687-build.json','prior-builder7a2.py.txt','prior-restricted-validator.py.txt')
# Parse only the static assignment; no archived helper is loaded or executed.
source_ast=ast.parse((P/'scripts/sql-review/run-privilege-ceiling-control-rehearsal-v9.py').read_bytes())
assignments=[n.value for n in source_ast.body if isinstance(n,ast.Assign) and any(isinstance(t,ast.Name) and t.id=='METADATA_DESCRIPTORS' for t in n.targets)];assert len(assignments)==1
descriptors=ast.literal_eval(assignments[0])
def frame(v):
 if type(v) is dict:return {'object':{k:frame(x) for k,x in sorted(v.items())}}
 if type(v) is list:return {'array':[json.loads(x) for x in sorted({M.canonical(frame(x)) for x in v})],'length':len(v)}
 return type(v).__name__
paths=[p for p in F['preserved_actual56_sha256'] if p.endswith('.json') and '/audit-history/' not in p]
assert 'exact44' in plan['claim_maxima_and_no_links']
rebuilt={'schema':'workinants.privilege485517b0-closed-inputs-and-claims.v1','source455_sha256':F['executed_source455_sha256'],'preserved56_sha256':F['preserved_actual56_sha256'],'closed_existing511_sha256':F['closed_existing_union511_sha256'],'six_history_sha256':{M.ARCHIVE+'/'+n:hashlib.sha256((P/M.ARCHIVE/n).read_bytes()).hexdigest() for n in history},'source_metadata_descriptors':descriptors,'source_ledger_schema':M._ledger_schema(),'source_parent_closure_stages':[r['stage'] for r in parent['backend_closures']],'sanitized_json_frames':{p:frame(read(p)) for p in paths},'claim_maxima':plan['claim_maxima_and_no_links']['exact44'],'prior_issuer_row70':prior['assertions'][70],'validating_build_contract':read(M.ARCHIVE+'/validating-full687-build.json'),'prior_status_semantic_sha256':M.digest(read(M.ARCHIVE+'/prior687-qualification-status.json')),'observed':{'native_catalog_sha256':M.digest(read(M.ASSET+'/evidence/native-before.json')),'filtered42_baseline':child['operations'][0]['data_projection'],'rendered_statement_sha256':{o['name']:o['executed_sql_sha256'] for o in child['operations'] if 'executed_sql_sha256' in o},'grant_check_profiles':{o['name']:{'count':len(o['private_grant_checks']),'unexpired_required':[r['unexpired_required'] for r in o['private_grant_checks']]} for o in child['operations'] if 'private_grant_checks' in o},'protocol_statement_sha256':{o['name']:o['issuer_statement_sha256'] for o in child['operations'] if 'issuer_statement_sha256' in o},'restricted_service_statement_sha256':next(o['restricted_statement_sha256'] for o in child['operations'] if 'restricted_statement_sha256' in o)},'limits':{'Posture':'D','exact44_only':True,'new_assertions':43,'issuer_history_preserving_PARTIAL_replacement':1,'helper_and_browser':'PARTIAL','DAG_umbrella':'NO_LINK','whole_cases':'NOT_PROMOTED','selected94':'NOT_PROMOTED','451_register':'NOT_PROMOTED','native960_replayed':False,'owner_API_positive':False,'worker_loop':False,'hosted_parity':False,'function_body_confidentiality':False,'NOLOGIN_startup_guard':False,'post_behavior_oracle_or_ledger_rerun':False,'runtime':'NOT_RUN_RETROSPECTIVE_SOURCE_ONLY'},'prior_Restore3_rows':[r for r in prior['assertions'] if r['case_id']=='P0C-RESTORE-01']}
assert M.encoded(rebuilt)==(P/M.SPEC).read_bytes()
assert not E
report={'schema':'workinants.independent-spec-byte-reproduction.v1','status':'PASS','actual_encoded_bytes_equal_frozen_spec':True,'spec_sha256':hashlib.sha256(M.encoded(rebuilt)).hexdigest(),'reconstructed_with':'independently authored recipe; source descriptors literal AST; frozen preservation plan; observed fields explicitly separate','archived_helpers_executed':False,'runtime':'NOT_RUN_SOURCE_ONLY','boundary_events':E}
(P/'independent-spec-reproduction.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf8')
print(json.dumps(report))
