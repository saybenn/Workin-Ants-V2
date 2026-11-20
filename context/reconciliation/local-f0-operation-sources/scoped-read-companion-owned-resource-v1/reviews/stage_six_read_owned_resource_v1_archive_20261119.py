"""Refresh only the authorized NEW unfrozen archive and PENDING validation."""
from pathlib import Path
import hashlib,json
TASK=Path(__file__).resolve().parent;ROOT=TASK/'workinants-correction-pass'
PLAN=json.loads((TASK/'six-read-owned-resource-v1-source-plan-v2-20261119.json').read_bytes())
ARCHIVE=PLAN['new_outputs_after_ACK']['ROOT_archive'];DEST=ROOT/ARCHIVE
VALIDATION=ROOT/PLAN['new_outputs_after_ACK']['ROOT_validation']
def sha(raw):return hashlib.sha256(raw).hexdigest()
def put(name,raw):
 target=DEST/name;target.parent.mkdir(parents=True,exist_ok=True)
 if target.exists()and target.read_bytes()==raw:return
 target.write_bytes(raw)
def stage():
 for name in PLAN['new_outputs_after_ACK']['TASK_five']:put(name+'.txt',(TASK/name).read_bytes())
 for key,prefix,review in(('accepted_owner_validation','preserved/owner-basis/','accepted-owner-validation.json'),('sixread_source_validation','preserved/sixread-basis/','accepted-sixread-validation.json')):
  info=PLAN['exact_basis'][key];raw=(ROOT/info['path']).read_bytes();assert sha(raw)==info['sha256'];put('reviews/'+review,raw);value=json.loads(raw)
  archive=value['archive_files_sha256'];common='context/reconciliation/local-f0-operation-sources/'+('owner-read-resource-mount-v2/'if key=='accepted_owner_validation'else'scoped-read-companion-source-v1/')
  for relative,wanted in archive.items():
   data=(ROOT/relative).read_bytes();assert sha(data)==wanted;assert relative.startswith(common);put(prefix+relative[len(common):],data)
 raw=(ROOT/'context/reconciliation/local-f0-operation-sources/owner-read-resource-mount-v2/reviews/image-proof-independent-source.json').read_bytes();assert sha(raw)=='b628b6d98ad22ea7def4dd7a51264025c50bde116451ae516f3e52f55ba9542a';put('reviews/image-proof-independent-source.json',raw)
 for name in ('six-read-owned-resource-v1-source-plan-v2-20261119.json','six_read_owned_resource_v1_independent_plan_review_20261119.json','six_read_owned_resource_v1_Root_source_implementation_ACK_20261119.json','six_read_owned_resource_v1_parallel_preservation_20261119.json','check_six_read_owned_resource_v1_child_composed_20261119.py','six_read_owned_resource_v1_child_composed_schema_v1_20261119.json','six_read_owned_resource_v1_child_composed_trace_v1_20261119.json','six_read_owned_resource_v1_child_composed_author_report_20261119.json','build_six_read_owned_resource_v1_20261119.py','apply_six_read_owned_resource_v1_steps_20261119.py','six_read_owned_resource_v1_steps_additions_20261119.py.txt','build_six_read_owned_resource_v1_checks_20261119.py','stage_six_read_owned_resource_v1_archive_20261119.py'):
  put('reviews/'+name,(TASK/name).read_bytes())
 for name in ('check_sixread_owned_resource_v1_preparer_pinner_20261119.py','check_sixread_owned_resource_v1_source_admission_20261119.py','check_six_read_owned_resource_v1_safety_composed_20261119.py','build_six_read_owned_resource_v1_safety_checks_20261119.py','six_read_owned_resource_v1_checks_additions_20261119.py.txt','tighten_six_read_owned_resource_v1_20261119.py','audit_six_read_owned_resource_v1_source_20261119.py','six_read_owned_resource_v1_source_audit_20261119.json'):
  if (TASK/name).exists():put('reviews/'+name,(TASK/name).read_bytes())
 for name in ('check_sixread_owned_resource_v1_full_composed_20261119.py','run_sixread_owned_resource_v1_final_composed_20261119.py','sixread-owned-resource-v1-coauthor-delivery-20261119.json','sixread-owned-full-composed-author-probe-584deb7d-20261119.json','sixread-owned-full-composed-author-probe-35d59d27-20261119.json','six_read_owned_resource_v1_final_composed_author_probe_20261119.json','sixread-owned-full-cli-first-pass-author-record-20261119.json','sixread-owned-full-composition-capture2-20261119.json','sixread-owned-full-composition-tool-data-projection-20261119.json','check_sixread_owned_resource_v1_final_graph_20261119.py'):
  if (TASK/name).exists():put('reviews/'+name,(TASK/name).read_bytes())
 execution='context/reconciliation/local-f0-owner-da5ad66-72934689-execution.json';raw=(ROOT/execution).read_bytes();record=json.loads(raw);put('reviews/mock-fixtures/historical-owner-execution-record.json',raw)
 names=('native-before.json','oracle-preflight.json','oracle-results.json','oracle-closure.json','oracle-evidence.json','ledger-observation.json','ledger-registration.json','ledger-evidence.json','catalog-comparison.json','acl-preflight.json','text-preflight.json')
 fixture_map={}
 for name in names:
  relative='context/reconciliation/local-f0-run-assets/da5ad66-owner-72934689/evidence/'+name;raw=(ROOT/relative).read_bytes();assert sha(raw)==record['assets_sha256'][relative];put('reviews/mock-fixtures/'+name,raw);fixture_map[relative]=sha(raw)
 put('reviews/mock-fixtures/lineage.json',(json.dumps({'scope':'HISTORICAL_OFFLINE_MOCK_FIXTURES_ONLY_NOT_CURRENT_RUNTIME_ATTESTATION','Root_authorization':'Root explicit message permitting already completed Git-preserved sanitized Owner7293 snapshots only; new runtime obtains fresh RAM proofs/CID','original_assets_sha256':fixture_map,'projected_test_identity':'Recorded by owning checker; original copied bytes unchanged'},indent=2)+'\n').encode())
 five={name:sha((TASK/name).read_bytes())for name in PLAN['new_outputs_after_ACK']['TASK_five']}
 archive={p.relative_to(ROOT).as_posix():sha(p.read_bytes())for p in DEST.rglob('*')if p.is_file()}
 value={'schema':'workinants.scoped-read-companion-owned-resource-v1-source-validation.v1','status':'PENDING_INDEPENDENT_SOURCE_REVIEW_NO_RUNTIME_AUTHORITY','source_version':'SCOPED_READ_COMPANION_OWNED_RESOURCE_V1','source_root':ARCHIVE,'operator_sources_sha256':five,'archive_files_sha256':dict(sorted(archive.items())),'independent_owned_resource_review':{'decision':'PENDING'},'independent_safety_sql_review':{'decision':'PENDING'},'accepted_basis_validation_sha256':{PLAN['exact_basis'][k]['path']:PLAN['exact_basis'][k]['sha256']for k in('accepted_owner_validation','sixread_source_validation')},'limits':{'runtime':'NOT_RUN','source_author_review_is_not_independent':True,'SQL_roles_policies_ACL_changed':False,'whole94_451_promoted':False,'Posture':'D'}}
 VALIDATION.write_text(json.dumps(value,indent=2)+'\n',encoding='utf8',newline='\n')
 print(json.dumps({'status':'NEW_ARCHIVE_STAGED_GATE_PENDING','files':len(archive),'validation_sha256':sha(VALIDATION.read_bytes()),'five':five}))
if __name__=='__main__':stage()
