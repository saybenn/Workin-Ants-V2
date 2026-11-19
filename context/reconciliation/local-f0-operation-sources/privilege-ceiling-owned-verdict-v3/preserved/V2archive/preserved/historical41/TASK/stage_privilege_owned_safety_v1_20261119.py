"""Refresh only NEW unfrozen privilege source/archive metadata; no processes."""
from pathlib import Path
import hashlib,json,shutil
TASK=Path(__file__).resolve().parent;ROOT=TASK/'workinants-correction-pass'
PREFIX='context/reconciliation/local-f0-operation-sources/privilege-ceiling-owned-safety-sql-v1'
VALIDATION='context/reconciliation/local-f0-privilege-ceiling-owned-safety-sql-v1-source-validation.json'
FILES=('execute_local_f0_privilege_ceiling_safety_sql_v1_20261119.py','local_f0_privilege_ceiling_safety_sql_v1_operation_steps.py','prepare_local_f0_privilege_ceiling_safety_sql_v1_plan.py','check_local_f0_privilege_ceiling_safety_sql_v1_operation.py','pin_local_f0_privilege_ceiling_safety_sql_v1_plan_20261119.py')
sha=lambda data:hashlib.sha256(data).hexdigest()
def stage():
    directory=ROOT/PREFIX;directory.mkdir(exist_ok=True)
    for name in FILES:(directory/(name+'.txt')).write_bytes((TASK/name).read_bytes())
    reviews=directory/'reviews';reviews.mkdir(exist_ok=True)
    source=ROOT/'context/reconciliation/local-f0-operation-sources/owner-read-safety-sql-v1/reviews/image-proof-independent-source.json'
    (reviews/'image-proof-independent-source.json').write_bytes(source.read_bytes())
    for name in('owner_safety_sql_v1_independent_source_review_20261119.json','owner_safety_sql_v1_root_source_review_20261119.json','privilege_ceiling_owned_safety_source_plan_20261119.json','privilege_ceiling_independent_root_source_review_20261119.json'):(reviews/name).write_bytes((TASK/name).read_bytes())
    base='context/reconciliation/local-f0-owner-read-safety-sql-v1-source-validation.json';raw=(ROOT/base).read_bytes();assert sha(raw)=='57c8e8dbb6624c71fc5146c200e82c23056f5b1874f8c46cd82424677d2b877e';record=json.loads(raw)
    (directory/'accepted-owner-validation.json').write_bytes(raw)
    for name,wanted in record['archive_files_sha256'].items():
        data=(ROOT/name).read_bytes();assert sha(data)==wanted
        destination=directory/'accepted-owner-archive'/name.split('owner-read-safety-sql-v1/',1)[1];destination.parent.mkdir(parents=True,exist_ok=True);destination.write_bytes(data)
    for name in('build_privilege_owned_safety_v1_20261119.py','privilege_owned_component_adapter_v1.py.txt'):(reviews/(name if name.endswith('.txt')else name+'.txt')).write_bytes((TASK/name).read_bytes())
    snapshots={p.relative_to(ROOT).as_posix():sha(p.read_bytes())for p in directory.rglob('*')if p.is_file()}
    metadata={'schema':'workinants.privilege-ceiling-owned-operator-source-validation.v1','status':'DRAFT_SOURCE_PREPARED_INDEPENDENT_REVIEW_REQUIRED','source_version':'privilege-ceiling-owned-safety-sql-v1','operator_sources_sha256':{name:sha((TASK/name).read_bytes())for name in FILES},'archive_files_sha256':snapshots,'independent_safety_sql_review':{'decision':'PENDING_ROOT_AND_INDEPENDENT_REVIEW','scope':'NEW_PRIVILEGE_FAMILY_NOT_APPROVED'},'base_source_validation':{'path':base,'sha256':sha(raw),'status':'SOURCE_APPROVED_EXACT_OWNER5'},'limits':{'runtime':'NOT_RUN','posture':'D','no_source_SQL_or_permission_change':True,'no_Git_Docker_network_or_database':True,'all_old_and_frozen_sources_preserved':True}}
    (ROOT/VALIDATION).write_text(json.dumps(metadata,indent=2)+'\n',encoding='utf8')
    print(json.dumps({'archive_files':len(snapshots),'validation_sha256':sha((ROOT/VALIDATION).read_bytes())}))
if __name__=='__main__':stage()
