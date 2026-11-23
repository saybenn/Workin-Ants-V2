"""Authoring only. Writes an exclusive private candidate; never executes evidence code."""
from pathlib import Path
import ast, hashlib, json, shutil

T=Path(__file__).resolve().parent
R=T/'workinants-correction-pass'
D=T/'read1161-evidence-adapter-v1-draft-20261120'
F=D/'future-root'
AR='context/reconciliation/local-f0-operation-sources/read1161-evidence-adapter-v1'
A='context/reconciliation/local-f0-run-assets/0ff2a91-read13-116153b2'
REC='context/reconciliation/local-f0-read13-0ff2a91-116153b2-execution.json'
DER='context/reconciliation/local-f0-read13-0ff2a91-116153b2-qualified-evidence.json'
BASE=AR+'/prior671-ledger.json'
SPEC=AR+'/closed-inputs-and-claims.json'
def raw(p):return p.read_bytes()
def sh(b):return hashlib.sha256(b).hexdigest()
def emit(p,v):
 p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(v,indent=2,ensure_ascii=False,allow_nan=False)+'\n',encoding='utf8',newline='\n')
def cp(src,rel):
 dst=F/rel;dst.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(src,dst);return sh(raw(dst))
def function(path,name):
 text=path.read_text(encoding='utf8');node=next(n for n in ast.parse(text).body if isinstance(n,(ast.FunctionDef,ast.ClassDef)) and n.name==name)
 return '\n'.join(text.splitlines()[node.lineno-1:node.end_lineno])+'\n'

if __name__=='__main__':
 D.mkdir(exist_ok=False);F.mkdir()
 plan=json.loads(raw(T/'Read1161_bounded_evidence_adapter_admission_plan_20261120.json'))
 inv=json.loads(raw(T/'0ff_Read1161_audited_success_preserved_inventory_20261120.json'))
 proposal=json.loads(raw(T/'Read1161_exact13_assertion_link_proposal_20261120.json'))
 m=json.loads(raw(R/(A+'/manifest/operation-manifest.json')))
 assert plan['source1400_map']==m['packet_files_sha256'] and len(plan['source1400_map'])==1400
 graph=dict(plan['source1400_map']);graph.update(inv['all_files_sha256'])
 # No live ledger/status is an execution-proof dependency. Preserve exact old
 # accepted rows as data, and only merge the proposed 13 additions privately.
 baseline=cp(R/'context/reconciliation/local-f0-assertion-evidence.json',BASE)
 assert baseline=='8b7cd04a5681dc7d2b2996c20b896dc352af67e88f968f1ccc9250f9bdda0d64'
 extras={BASE:baseline}
 for name in ['Read1161_independent_closed_exact13_evidence_audit_20261120.json','Read1161_exact13_assertion_link_proposal_20261120.json','Read1161_bounded_evidence_adapter_admission_plan_20261120.json','0ff_Read1161_audited_success_preserved_inventory_20261120.json']:
  extras[AR+'/'+name]=cp(T/name,AR+'/'+name)
 # Close all real inputs without evaluating or importing any producer.
 for rel,wanted in graph.items():
  assert sh(raw(R/rel))==wanted,rel
  cp(R/rel,rel)
 spec={'schema':'workinants.Read1161-closed-inputs.v1','source_files_sha256':m['packet_files_sha256'],'preserved_assets_sha256':inv['all_files_sha256'],'audit_data_sha256':extras,'claims':proposal['claims'],'source_fixture':'review-output/remaining-app-read13-rehearsal/fixtures.json','operation_manifest':A+'/manifest/operation-manifest.json','archived_prior_ledger':BASE,'limits':['Exactly 13 positive app SQL SELECT assertions only.','Synthetic setup is not owner API, write, worker, SH codec or whole-case qualification.','Attempt1161 aliases only the derived run_id; raw d848 producers and resource identity remain unchanged.','No explanation or qualification of stopped first attempt95321.']}
 assert spec['source_fixture'] in graph
 emit(F/SPEC,spec);extras[SPEC]=sh(raw(F/SPEC));graph.update(extras)
 constants="""\nAR=%r\nASSET=%r\nREC=%r\nDERIVED=%r\nBASELINE=%r\nSPEC=%r\nRUN='116153b2-1af4-4fc9-bde8-f804146b5cea'\nRAW_RUN='d848e852-f857-4c03-8288-4893e2e8aa0c'\nCID='852d3646c9915684d186eb4221c1ab24132ece8f3dac33bcf0a602bbf4cd4356'\nCOMMIT='0ff2a910ce081a0c6e0c6a268d6f876b8e061a45'\nTREE='886f85d4a919a8a04f85c8fe45a01e0a8801ba1c'\nPACKET='7720bb7deb6c5b190d04482be6f263cb45622cba36fe06b548ecddcfc164284f'\nAPP='5ae39abf991f9c189e367eb6ab6968b0ad50836bf4220ac27ef8c18306ac26ad'\nNATIVE='a048478f5e834dc1686b558954ea9bdaeaba4278afcf63976510c114680f1fc6'\nKIND='DERIVED_REVIEWED_REMAINING13_SQL_SELECT_ASSERTIONS_ONLY'\nROLES=('postgres','wa_migrator','wa_context_issuer','wa_identity_service_authority','wa_app_runtime','wa_worker')\n"""%(AR,A,REC,DER,BASE,SPEC)
 reader=R/'scripts/local_f0_worker_recovery_evidence_v2.py'
 common='\n'.join(function(reader,n)for n in ['EvidenceFailure','need','sh','_typed_json','canonical','same','doc','_read'])
 # Canonical producer Read13 JSON deliberately uses Unicode, independently of
 # Worker evidence. The Reader function is byte/AST-identical to reviewed V2.
 common=common.replace("separators=(',',':'),allow_nan=False","separators=(',',':'),ensure_ascii=False,allow_nan=False")
 validator=function(T/'local_f0_remaining_app_read13_owned_v2_operation_steps.py','validate_scoped_component')
 validator=validator.replace('def validate_scoped_component(value,plan,native_sha):','def _validate_child(value,f,application,native_sha):\n    SCOPED_FIXTURES=f;RUN_ID=RAW_RUN;SCOPED_FIXTURES_SHA=PINS[FIXTURE];SCOPED_CONTENT_SHA=f[\'content_sha256\']')
 validator=validator.replace("created_containers[TARGETS[0]['name']]",'CID')
 validator=validator.replace("application=read_pinned('review-output/foundation-application.review.sql').decode();body=",'body=')
 validator=validator.replace("    protocol=load_reviewed_helper(PROTOCOL_FILE)","    protocol={'validate_transaction_observation':validate_transaction_observation,'TRANSACTION_OBSERVATION_FIELDS':TRANSACTION_OBSERVATION_FIELDS}")
 proto=R/'scripts/remaining_app_read13_protocol.py'
 protocol="TRANSACTION_OBSERVATION_STAGES=('NOT_STARTED','SAME_XID','BIND','REVOKED_REBIND','EXPIRED_REBIND','BUSINESS')\nTRANSACTION_OBSERVATION_FIELDS=frozenset(('observation_stage','response_received','response_shape_valid','client_exit_received','client_exit_class','exit_code','acknowledged','stderr_present','stdout_records'))\n"+function(proto,'validate_transaction_observation')
 template=raw(T/'read1161_adapter_module_body_v1.txt').decode()
 head='"""Pure retrospective Read1161 admission. No producer/helper execution or live database work."""\nimport hashlib,json,math,os,re,stat\nfrom collections import Counter\nfrom pathlib import Path\nfrom types import MappingProxyType\n'+constants+common+"\nexact=same\ndef digest(value):return sh(canonical(value).encode())\n"+protocol+'\n'+validator+'\n'+template
 # Derivation data cannot pin its own hash. Its input map omits itself; the
 # module pins it and every closed dependency separately below.
 claims=[]
 for item in proposal['claims']:
  claims.append({k:item[k]for k in ['case_id','assertion_id','status','expected_assertion_sha256','source_whole_assertion_sha256','actual_child_result_pointers','case_names','source_SQL_files_sha256','scope_limit']})
 derived={'schema':'workinants.Read1161-qualified-evidence.v1','derivation':'EXPLICIT_DERIVED_WRAPPER_NOT_RAW_RUNTIME_EVIDENCE','actual_result':'DERIVED_REVIEWED_REMAINING13_SQL_SELECT_ASSERTIONS_ONLY','run_id':'116153b2-1af4-4fc9-bde8-f804146b5cea','raw_run_id':m['run_id'],'source_commit':m['source_commit'],'source_tree':m['source_tree'],'packet_sha256':m['packet_sha256'],'source_record':{'path':REC,'sha256':graph[REC]},'input_files_sha256':graph,'claims':claims,'limits':spec['limits']}
 emit(F/DER,derived);graph[DER]=sh(raw(F/DER))
 pins='\nPINS=MappingProxyType('+repr(dict(sorted(graph.items())))+')\nGRAPH_FILES='+str(len(graph))+'\nMAX_BUNDLE_BYTES='+str(sum(len(raw(F/p))for p in graph))+'\nFIXTURE='+repr(spec['source_fixture'])+'\n'
 module=F/'scripts/local_f0_read1161_evidence.py';module.parent.mkdir(exist_ok=True);module.write_text(head+pins,encoding='utf8',newline='\n')
 # Execute only this NEW authored pure module, not any admitted code artifact.
 ns={'__name__':'read1161_author_delta'};exec(compile(module.read_bytes(),str(module),'exec'),ns)
 ledger=ns['propose_ledger_delta'](json.loads(raw(F/BASE)),derived)
 emit(F/'context/reconciliation/local-f0-assertion-evidence.json',ledger)
 builder=raw(R/'scripts/prepare-local-f0-status.py').decode();original=builder
 builder=builder.replace('ROOT=Path(__file__)',"from local_f0_read1161_evidence import prepare_batch as prepare_read1161_batch, EvidenceFailure as Read1161EvidenceFailure\nROOT=Path(__file__)",1)
 builder=builder.replace('EVIDENCE_RECORDS={','EVIDENCE_RECORDS={\n    '+repr(DER)+':('+repr(graph[DER])+','+repr(derived['actual_result'])+'),',1)
 builder=builder.replace('    worker_recovery_batch=None',"    read1161_batch=None\n    if any(row.get('evidence_path')=="+repr(DER)+" for row in ledger['assertions']):\n        try:read1161_batch=prepare_read1161_batch(ROOT)\n        except Read1161EvidenceFailure as error:raise AssertionError(str(error)) from None\n    worker_recovery_batch=None",1)
 marker="                elif row['evidence_path']=='context/reconciliation/local-f0-worker-5f189aa-b42c35d5-qualified-evidence.json':"
 builder=builder.replace(marker,"                elif row['evidence_path']=="+repr(DER)+":\n                    try:read1161_batch.validate_claim(case['id'],item['id'],row['status'],execution,ROOT,json_pointer=pointer,ledger_row=row)\n                    except Read1161EvidenceFailure as error:raise AssertionError(str(error)) from None\n"+marker,1)
 builder=builder.replace('    return {\'scope\':',"    if read1161_batch is not None:\n        try:read1161_batch.verify_unchanged();read1161_batch.require_finalized()\n        except Read1161EvidenceFailure as error:raise AssertionError(str(error)) from None\n    return {'scope':",1)
 assert builder!=original
 (F/'scripts/prepare-local-f0-status.py').write_text(builder,encoding='utf8',newline='\n')
 cp(R/'scripts/prepare-local-f0-status.py',AR+'/before-builder.py.txt')
 emit(D/'initial-authoring-map.json',{'proposed_module':str(module.relative_to(F)),'closed_input_files':len(graph),'closed_bytes':sum(len(raw(F/p))for p in graph),'preserved_prior_rows':len(ledger['assertions'])-13,'proposed_rows':len(ledger['assertions']),'no_live_Root_write':True,'builder_base_sha256':sh(original.encode()),'runtime_NOT_RUN':True})
