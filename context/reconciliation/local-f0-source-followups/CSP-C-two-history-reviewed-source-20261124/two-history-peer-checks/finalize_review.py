from pathlib import Path
import json,hashlib,datetime,sys
BASE=Path(__file__).resolve().parent
TASK=BASE.parent
F=BASE/'freeze'
AUTHOR=TASK/'runtime-lease-two-history-owned-v1-HOLD-correction-FINAL-frozen-author-20261123'
OLD=TASK/'runtime-lease-two-history-owned-v1-FINAL-frozen-author-20261123'
sha=lambda b:hashlib.sha256(b).hexdigest()
aggregate=lambda m:sha(''.join(n+'\0'+h+'\n' for n,h in sorted(m.items())).encode())
load=lambda p:json.loads(p.read_bytes())
delivery=load(TASK/'runtime_lease_two_history_owned_v1_HOLD_correction_FINAL_author_delivery_20261123.json')
cm=load(F/'candidate-file-map.json');fm=load(F/'FREEZE-MANIFEST.json')
assert sha((OLD/'FREEZE-MANIFEST.json').read_bytes())==load(F/'final-author-report.json')['original834_freeze_manifest_sha256']=='6db06eeb2e618dd9786e0b33a6a86681a1cb98051bae29903b3316b5acf94477'
checks={}
for label,root,mp in [('frozen_author555',AUTHOR,fm['files_sha256']),('exclusive_copy555',F,fm['files_sha256']),('candidate_Root56',F/'future-root',cm['candidate_files_sha256']),('closed_runtime374',F/'future-root',cm['closed_runtime_sources_sha256']),('whole_packet425',F/'future-root',cm['whole_packet_files_sha256']),('original834',OLD,load(OLD/'FREEZE-MANIFEST.json')['files_sha256'])]:
 bad=[n for n,h in mp.items() if not(root/n).is_file() or sha((root/n).read_bytes())!=h]
 checks[label]={'files':len(mp),'aggregate_sha256':aggregate(mp),'bad':bad}
 assert not bad,label
pins={n:sha((F/n).read_bytes()) for n in delivery['external_five_sha256']}
assert pins==delivery['external_five_sha256']
assert sha((AUTHOR/'FREEZE-MANIFEST.json').read_bytes())==delivery['freeze_manifest_sha256']
assert sha((F/'candidate-file-map.json').read_bytes())==delivery['candidate_map_sha256']
required={'light':10,'normal-corrected':1,'node':9,'resource':7,'forced':3,'natural':3}
receipts={}
for name,count in required.items():
 p=BASE/(name+'-checks.json');v=load(p)
 assert v['successful'] is True and len(v['results'])==count and not v['forbidden_edges_attempted'],name
 assert v['operator_sources_sha256']==pins and v['operator_sources_preserved'],name
 receipts[p.name]={'path':str(p),'sha256':sha(p.read_bytes()),'cases':count,'successful':True}
shared=load(BASE/'shared-close-budget-check.json');assert shared['successful'] and shared['tests']==1 and not shared['forbidden_edges_attempted']
assert load(BASE/'static-gates.json')['status']=='PASS_SOURCE_ONLY'
end={'schema':'workinants.independent-two-history-final-preservation.v1','checks':checks,'operator_sources_sha256':pins,'Root_and_frozen_author_program_sources_not_mutated':True,'runtime':'NOT_RUN','Posture':'D'}
ep=BASE/'final-preservation-barriers.json';eraw=(json.dumps(end,sort_keys=True,indent=2)+'\n').encode()
if ep.exists():assert load(ep)==end
else:ep.open('xb').write(eraw)
names=['reviewer-packaging-newline-correction.json','reviewer-packaging-correction.json','finalize_review-v1-preserved.py','offline-environment.json','entry-barriers.json','static-gates.json','static-scope-review.json','shared-close-budget-check.json','normal-checks.json','normal-memory-report.json','reviewer-harness-correction.json','independent_runner-v1-preserved.py','independent_runner.py','finalize_review.py','final-preservation-barriers.json']
for n in names:
 p=BASE/n;receipts[n]={'path':str(p),'sha256':sha(p.read_bytes())}
generated={}
for p in (F/'unit-correction-reports').glob('independent-peer-*.json'):generated[p.relative_to(BASE).as_posix()]=sha(p.read_bytes())
assert len(generated)==22
normal=load(BASE/'normal-corrected-checks.json')['results'][0]
out={'schema':'workinants.runtime-lease-two-history-owned-v1-successor-independent-code-security-resource-SafetySQL-transport-review.v1','decision':'SOURCE_APPROVED','reviewer':'/root/two_history_successor_code_peer','independent_of_source_author':True,'routing_refinement_sha256':'eb989b411d1ddc6c3db5902993abfd88ab39f2ed6b173a59757cbacd2fede756','recorded_at_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'author_delivery_sha256':sha((TASK/'runtime_lease_two_history_owned_v1_HOLD_correction_FINAL_author_delivery_20261123.json').read_bytes()),'author_report_sha256':delivery['author_report_sha256'],'findings':[],'operator_sources_sha256':pins,
'frozen_author':{'path':str(AUTHOR),'files':555,'manifest_sha256':delivery['freeze_manifest_sha256'],'aggregate_sha256':delivery['freeze_aggregate_sha256']},
'candidate_Root':{'files':56,'candidate_file_map_path':delivery['candidate_map_path'],'candidate_file_map_sha256':delivery['candidate_map_sha256'],'aggregate_sha256':cm['candidate_aggregate_sha256'],'files_sha256':cm['candidate_files_sha256']},
'current_closure_maps':{'closed_runtime_source_count':374,'closed_runtime_sources_sha256':cm['closed_runtime_sources_sha256'],'whole_packet_file_count':425,'whole_packet_aggregate_sha256':cm['whole_packet_aggregate_sha256'],'whole_packet_files_sha256':cm['whole_packet_files_sha256']},
'decisions':{'independent_source_review':'SOURCE_APPROVED','resource_review':'SOURCE_APPROVED','SafetySQL_review':'SOURCE_APPROVED','binary_transport_review':'SOURCE_APPROVED','source_gate_and_pinner_review':'SOURCE_APPROVED','Root_source_admission':'NOT_PERFORMED_ROOT_ONLY','runtime_authorization':False},
'original_HOLD_closures':{'TWOH-INNER-CLOSURE-01':'CLOSED: validated status/null and no fully validated result after exact Node dispatch sticky-latch unknown before persistence/observers; SQL finalizer veto survives later globalzero/good calls; validated integer failure remains eligible.','TWOH-FIRST-ORIGIN-02':'CLOSED: finite memory-first earliest originating phase/code survives immutable HeldFailure, secondary observer/IO/finalizer/cleanup; arbitrary strings/SQLSTATE/nonstring codes rejected.','TWOH-RESOURCE-ORDER-03':'CLOSED: honest actualFalse pure prestart with immutable mount comparison before start, actual immutable running+kernel before candidate pgpass/URL/wrong files; bad source/mode/extra mounts/kernel vectors dispatch no candidate credential write.'},
'aligned_remote_exec_rule':'CLOSED: authorized abnormal exec byte API marks remote unknown before persistence/translation while preserving physically observed process/pipes/threads true; natural raw byte result followed by UTF8/semantic/integer failure is known-closed eligible contrast; Node inner receipt remains separate.',
'bounded_independent_verification':{'unit_tests_PASS':11,'actual_entry_normal_pipeline_PASS':1,'Node_inner_receipt_first_origin_PASS':9,'resource_order_PASS':7,'forced_remote_exec_PASS':3,'natural_binary_result_contrast_PASS':3,'actual_nested_Git_Docker_Node_psql_database_socket_calls':0,'all_inner_boundaries':'MODELED_OR_AUDIT_FORBIDDEN','normal_pipeline':normal,'receipts':receipts,'independent_probe_memory_reports_sha256':generated},
'static_code_chain':load(BASE/'static-scope-review.json'),
'source_preservation':{'source13_validation_sha256':'9b85cf469d15d3feda0cff8d46ee5c8b36800dd06cf53d62c8450085e4abe65a','source36_code13_initial5ae_append49c_source8_cfb_dee63_unchanged':True,'all32_worker_ACL_and_owner_defaultACL_RLS_grantor_NOLOGIN_leaf_sources_preserved':True,'original834_and_final555_all_bytes_unchanged':True,'original834_manifest_sha256':'6db06eeb2e618dd9786e0b33a6a86681a1cb98051bae29903b3316b5acf94477','after_all_checks':checks},
'Root_admission_contract':'This immutable nonauthor source review binds exact candidate56/runtime374/whole425 and external five. Root alone may admit bounded new owning metadata and refresh maps/source8/archives/pin/literal/current+committed checks. All new owning source gates remain PENDING here; no runtime was authorized or run.',
'limits':['Pure offline process/filesystem/thread/clock/SQL-response boundary models do not establish Docker/PostgreSQL/Prisma runtime or remote-exit semantics.','Source13 default Windows text CLI remains NOT_RUNTIME_APPROVED; review covers NEW owning supported binary callback only.','The normal pinner model has427 files: exact candidate packet425 plus two isolated UNIT-only review records. Commit/tree and all Git responses are boundary models, never actual Root admission or committed-source observations.','No broad unchanged 1301-second mutation suite, no App/Worker business assertions/owner writes/worker loops or runtime/provider/production/hosted/migration-adoption qualification.','Prior failed normal-reviewer postcondition and source/parser-count harness mistake are preserved as reviewer harness corrections; production sources were unchanged. The successful corrected normal path was independently rerun.','Author historical hardlink support denial remains NOT_RUN_SUPPORT_ENVIRONMENT; author21340-second elapsed gap remains observed without inventing CPU/source cause.'],
'new_business_assertions_qualified':0,'source_gates':'PENDING_UNTIL_ROOT_ADMISSION','runtime':'NOT_RUN','Posture':'D','plain_English':'The code checks the secret drawer before filling it, remembers the first error, and keeps the stop sign up whenever an inside tool may still be running. The pretend tests passed. Root still controls review admission and any real run.'}
out['static_code_chain']['status']='SOURCE_APPROVED_AFTER_BOUNDED_MODELS'
p=BASE/'SOURCE-APPROVED-independent-review.json';raw=(json.dumps(out,sort_keys=True,indent=2)+'\n').encode();p.open('xb').write(raw)
print(json.dumps({'decision':out['decision'],'findings':[],'path':str(p),'sha256':sha(raw),'checks':sum(required.values())+1,'runtime':'NOT_RUN','Posture':'D'}))
