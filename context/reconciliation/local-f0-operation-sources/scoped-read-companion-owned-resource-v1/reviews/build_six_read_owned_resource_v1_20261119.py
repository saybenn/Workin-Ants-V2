"""Authorized source-only derivation from accepted Owner MountV2, never old prototype."""
from pathlib import Path
import ast, hashlib, json

TASK=Path(__file__).resolve().parent
ROOT=TASK/'workinants-correction-pass'
PLAN=json.loads((TASK/'six-read-owned-resource-v1-source-plan-v2-20261119.json').read_bytes())
OLD=list(PLAN['exact_basis']['accepted_owner_validation']['operator_sources_sha256'])
NEW=PLAN['new_outputs_after_ACK']['TASK_five']
ARCHIVE=PLAN['new_outputs_after_ACK']['ROOT_archive']
VALIDATION=PLAN['new_outputs_after_ACK']['ROOT_validation']
def sha(raw):return hashlib.sha256(raw).hexdigest()
def replace_function(text,name,replacement):
 tree=ast.parse(text);node=next(x for x in tree.body if isinstance(x,(ast.FunctionDef,ast.AsyncFunctionDef)) and x.name==name)
 lines=text.splitlines(keepends=True);return ''.join(lines[:node.lineno-1])+replacement.rstrip()+'\n'+''.join(lines[node.end_lineno:])
def transformed(text):
 for old,new in zip(OLD,NEW):text=text.replace(old,new)
 replacements={
 'context/reconciliation/local-f0-operation-sources/owner-read-controls-v1/reviews/independent-final.json':'context/reconciliation/local-f0-operation-sources/scoped-read-companion-source-v1/independent-root-source-review.json',
 'f6931e2a7c56a09ddd30e26171b54468368a2c4e6f660c160222b013c706fe31':'ae37a4f11b55971de2835205019a0fe60492c2dac7f45e9abfcae50f7fdd1249',
 'review-output/owner-read-control-rehearsal':'review-output/scoped-read-companion-rehearsal',
 'scripts/sql-review/run-owner-read-control-rehearsal.py':'scripts/sql-review/run-scoped-read-companion-rehearsal.py',
 'scripts/owner_read_control_protocol.py':'scripts/scoped_read_companion_protocol.py',
 '7f8d292ddc8ca11e12ae91e94ac62cca6cdd09d0c1f8a427ac5eefa414e66aca':'7f5bd6e713a1f0eaf330c2acf0267cd45aa2e8f47467e03d6f4c4c6dc754420c',
 'fd722b13789f1afcf244bafd4484acf4d331e1ba97387be88317718c6e42605c':'99085dd68fb5ce8558460821f694bc4a8e11c2003cb4847c6be62b8850f16a16',
 '8b55f608573459531d15dd732da5947f0cfda0aeb2b2632ca6ec9223e8dae6a5':'4160760bb319e4389182ed5cfcb6c0fae028480bd3d6d418be0130e8156a0f15',
 'context/reconciliation/local-f0-owner-read-resource-mount-v2-source-validation.json':VALIDATION,
 'context/reconciliation/local-f0-operation-sources/owner-read-resource-mount-v2':ARCHIVE,
 'LOCAL_F0_OWNER_READ_REHEARSAL':'LOCAL_F0_SCOPED_READ_COMPANION_OWNED_RESOURCE_V1_REHEARSAL',
 'APPROVED_LOCAL_F0_OWNER_READ_ATTEMPT':'APPROVED_LOCAL_F0_SCOPED_READ_COMPANION_OWNED_RESOURCE_V1_ATTEMPT',
 'workinants.owner-read-owned-operator-source-validation.v1':'workinants.scoped-read-companion-owned-resource-v1-source-validation.v1',
 }
 for old,new in replacements.items():text=text.replace(old,new)
 text=text.replace('OWNER_READ','SCOPED_READ').replace('owner_read','scoped_read').replace('OWNER-READ','SCOPED-READ').replace('owner-read','scoped-read').replace('ownerreads','scopedreads')
 # The source packet, evidence schema and staging namespace are exact separate domains.
 text=text.replace('workinants.scoped-read-fixtures.v1','workinants.scoped-read-companion-fixtures.v1')
 text=text.replace("'local-f0-scoped-read-plan-'","'local-f0-scoped-reads-resource-v1-plan-'").replace("'local-f0-scoped-read-'","'local-f0-scoped-reads-resource-v1-'")
 # Image proof remains the exact accepted historical provenance, with no fallback.
 text=text.replace(ARCHIVE+'/reviews/image-proof-independent-source.json','context/reconciliation/local-f0-operation-sources/owner-read-resource-mount-v2/reviews/image-proof-independent-source.json')
 return text

def main():
 preservation=json.loads((TASK/'six-read-owned-resource-v1-plan-preservation-20261119/preservation.json').read_bytes())
 parallel=json.loads((TASK/'app-write-two-APPWRITE2-01-source-correction-plan-20261119.json').read_bytes())
 allowed=set(parallel['bounded_source_changes_after_ACK']['paths'])
 for name,wanted in preservation['files_sha256'].items():assert sha((TASK/'six-read-owned-resource-v1-plan-preservation-20261119'/name).read_bytes())==wanted,name
 exceptions={}
 for name,wanted in preservation['current_ROOT_files_sha256'].items():
  if name in allowed or name.startswith('review-output/app-write-two-control-rehearsal/'):
   exceptions[name]={'historical_sha256':wanted,'current_version':'AUTHORIZED_PARALLEL_APPWRITE_CORRECTION_NOT_READ_OR_ADMITTED'};continue
  assert sha((ROOT/name).read_bytes())==wanted,name
 for name,wanted in preservation['current_TASK_files_sha256'].items():assert sha((TASK/name).read_bytes())==wanted,name
 for old,new in zip(OLD,NEW):
  raw=(TASK/old).read_bytes();assert sha(raw)==PLAN['exact_basis']['accepted_owner_validation']['operator_sources_sha256'][old]
  path=TASK/new;assert not path.exists(),new
  text=transformed(raw.decode('utf8')).replace('121','71')
  if new==NEW[0]:
   text=text.replace("'prepared_protocols':71","'prepared_protocols':71")
  if new==NEW[1]:
   text=text.replace('OWNER_PACKET','SCOPED_PACKET').replace('OWNER_FIXTURES','SCOPED_FIXTURES').replace('OWNER_CONTENT','SCOPED_CONTENT').replace('OWNER_COORDINATOR','SCOPED_COORDINATOR').replace('OWNER_PEER','SCOPED_PEER')
  path.write_text(text,encoding='utf8',newline='\n')
 (TASK/'six_read_owned_resource_v1_parallel_preservation_20261119.json').write_text(json.dumps({'historical250_snapshots_unchanged':True,'all_non_AppWrite_current_bindings_unchanged':True,'Root_explicit_parallel_exception':'Root message confirming ACK53f8/exact planfd23 paths and generated AppWrite namespace only; no AppWrite current bytes read or admitted','exceptions':exceptions},indent=2)+'\n')
 print(json.dumps({'status':'NEW_SOURCE_SKELETON_ONLY_UNREVIEWED','new_five':NEW,'historical250_snapshots_unchanged':True,'authorized_parallel_exceptions':len(exceptions)}))
if __name__=='__main__':main()
