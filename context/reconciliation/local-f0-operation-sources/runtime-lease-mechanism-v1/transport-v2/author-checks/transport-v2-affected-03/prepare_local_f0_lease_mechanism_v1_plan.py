"""Pure preparation/admission for the held synthetic eleven-case mechanism.

No migration/default application is installed by this family. Git reads are
performed only by the separate pinner, after source and review gates pass.
"""
from pathlib import Path
import argparse
import hashlib
import json
import math
import os
import re
import stat
import uuid

FIVE=('execute_local_f0_lease_mechanism_v1_20261120.py','local_f0_lease_mechanism_v1_operation_steps.py','prepare_local_f0_lease_mechanism_v1_plan.py','check_local_f0_lease_mechanism_v1_operation.py','pin_local_f0_lease_mechanism_v1_plan_20261120.py')
ARCHIVE='context/reconciliation/local-f0-operation-sources/runtime-lease-mechanism-v1'
VALIDATION='context/reconciliation/local-f0-runtime-lease-mechanism-v1-source-validation.json'
SYNTHETIC='review-output/runtime-lease-branch-v1/synthetic/'
PURPOSE='LOCAL_F0_LEASE_MECHANISM_V1_SYNTHETIC_ONLY'
REVIEW_STATUS='APPROVED_LOCAL_F0_LEASE_MECHANISM_V1_ATTEMPT'
IMAGE='docker.io/library/postgres:17.11@sha256:996e9dc583ba9f0265a2c75547a9c95fb22c251e394749cab205a0a00e1856a1'
CONFIG='sha256:eb0fb2377534e65aad04f37838956b3dfb888e1a3dd3c1acf957bc6557eb6c7d'
DATABASE='wa_lease_mechanism_v1'
ROLES=('postgres','wa_lease_v1_app','wa_lease_v1_worker','wa_lease_v1_verifier')
# Filled once by the author freezer from the already reviewed 57 artifacts and
# image proof. These are fixed source identities, never caller supplied pins.
BASE_FILES={'scripts/check-runtime-lease-branch-v1.py': 'c09588aedda35d759d3de4a6b5387a363ffd9e6d8204640d650d2ea325afe634', 'scripts/prepare-runtime-lease-branch-v1.py': '9712fb6dd00cc5c84db693636f63ae513e2b591294c319f89b5e1c6ecce0c570', 'context/reconciliation/local-f0-runtime-lease-branch-v1-source-validation.json': '8d611a80ef2a726f063b3166b35ace8842d0df775ffa9978910496b10986c5d8', 'context/reconciliation/local-f0-operation-sources/runtime-lease-branch-v1/cause-plan.json': '650697274a35632841a9fbfd16e323e401480c232816f892f56c8dc1bef5d568', 'context/reconciliation/local-f0-operation-sources/runtime-lease-branch-v1/check-runtime-lease-branch-v1.py.txt': 'c09588aedda35d759d3de4a6b5387a363ffd9e6d8204640d650d2ea325afe634', 'context/reconciliation/local-f0-operation-sources/runtime-lease-branch-v1/prepare-runtime-lease-branch-v1.py.txt': '9712fb6dd00cc5c84db693636f63ae513e2b591294c319f89b5e1c6ecce0c570', 'context/reconciliation/local-f0-operation-sources/runtime-lease-branch-v1/author-evidence/author-review.json': '7a60b5a3b0dd87a6b95fd233a32df90408da45870ad9a63a6cc4bb2b6a60fe09', 'context/reconciliation/local-f0-operation-sources/runtime-lease-branch-v1/author-evidence/before-preservation.json': '0eefc010ac8628e79f2ae80e2d69dd45deaf5f85ce2d816ceb7ce416e94b76fc', 'context/reconciliation/local-f0-operation-sources/runtime-lease-branch-v1/author-evidence/current-preparation.json': 'c71b3263dee6bcaeb335a5262fc3cdbd03898808919bd89ec80ae5e401a17584', 'context/reconciliation/local-f0-operation-sources/runtime-lease-branch-v1/author-evidence/focused14-initial.json': '92007b3fb253b65547c186d4955ce231c33a240349cea523df66b33163d11786', 'context/reconciliation/local-f0-operation-sources/runtime-lease-branch-v1/author-evidence/focused14-initial.log': 'ce7a9d2dfa7545df875aab6baa0a6126184a416c204bfc5cbd2459e8efc1db24', 'context/reconciliation/local-f0-operation-sources/runtime-lease-branch-v1/author-evidence/implementation-scope.json': '5e2469cbfde9dd2d788278767f60d9ad1b112f08143abf0c44e8b3edce0cdb65', 'context/reconciliation/local-f0-operation-sources/runtime-lease-branch-v1/author-evidence/run_runtime_lease_branch_v1_focused_20261120.py.txt': '4d63f78a7cef0705ca174867da89ce6877c5d3ba06a9270e103ab4e624f4ad53', 'context/reconciliation/local-f0-operation-sources/runtime-lease-branch-v1/author-evidence/static-preparation.json': '23f3b0791a7df24328ef008904dae433c2916cba18fb8670d7fef8128d5ee6b0', 'context/reconciliation/local-f0-operation-sources/runtime-lease-branch-v1/author-history/first-static-preparation/receipt.json': '23f3b0791a7df24328ef008904dae433c2916cba18fb8670d7fef8128d5ee6b0', 'context/reconciliation/local-f0-operation-sources/runtime-lease-branch-v1/author-history/first-static-preparation/static-refinements.json': '6682e1d7478324561087dd3fdad266779338b2152195a47957cc0e02cacaea68', 'context/reconciliation/local-f0-operation-sources/runtime-lease-branch-v1/author-history/static-checker-syntax-before-first-suite/checker.py.txt': '88f730d07db72f028f0c3ca09dcfaade0c0d53e93738bf28f03e8ec9ee349471', 'context/reconciliation/local-f0-operation-sources/runtime-lease-branch-v1/author-history/static-checker-syntax-before-first-suite/outcome.json': '8efb35b66c3aa8f0d22739bd524cc80d4b98288e6587db1301810706692e2d92', 'context/reconciliation/local-f0-operation-sources/runtime-lease-branch-v1/author-history/first-static-preparation/generated/review-output/runtime-lease-branch-v1/effective-runtime-transition.sql': 'e8c54dc020f0469657424876d4b3668f5234ce7c1708fc15c30644744bef9fff', 'context/reconciliation/local-f0-operation-sources/runtime-lease-branch-v1/author-history/first-static-preparation/generated/review-output/runtime-lease-branch-v1/overlay.json': 'e658f7eadb30d95c253b00ae52ef7d506110c6d098aa2dea46df9a2d411950aa', 'context/reconciliation/local-f0-operation-sources/runtime-lease-branch-v1/author-history/first-static-preparation/generated/review-output/runtime-lease-branch-v1/proposal.json': '98b5d2316ba362ea9be3537706f2918c76ffe45076baf6106666700a698ebb92', 'context/reconciliation/local-f0-operation-sources/runtime-lease-branch-v1/author-history/first-static-preparation/generated/review-output/runtime-lease-branch-v1/worker-acl32.json': '6909f3cd9e2a795d1f39379b7f81db4c24f9526e235e802deea5ce1a2da8e5a3', 'context/reconciliation/local-f0-operation-sources/runtime-lease-branch-v1/author-history/first-static-preparation/generated/review-output/runtime-lease-branch-v1/synthetic/direct-helper.sql': '25a7bd120d3918d7c015399146f31b3a8c4f219088f6f18fcd5b2b3ebca8ff15', 'context/reconciliation/local-f0-operation-sources/runtime-lease-branch-v1/author-history/first-static-preparation/generated/review-output/runtime-lease-branch-v1/synthetic/install-nested.sql': 'aa85b8bb7cb0a4c54d36413b1a272b5be59c6536ae5a69f4abe940eb20eb1581', 'context/reconciliation/local-f0-operation-sources/runtime-lease-branch-v1/author-history/first-static-preparation/generated/review-output/runtime-lease-branch-v1/synthetic/observe.sql': '70858d2f7b85921a9af72148e34c0dd844aff58878fda564b7cd25751036e668', 'context/reconciliation/local-f0-operation-sources/runtime-lease-branch-v1/author-history/first-static-preparation/generated/review-output/runtime-lease-branch-v1/synthetic/pending-update.sql': '878fc41806848b068165e029e6cc049928b43303f653d1fe1db6b2630f1bce8b', 'context/reconciliation/local-f0-operation-sources/runtime-lease-branch-v1/author-history/first-static-preparation/generated/review-output/runtime-lease-branch-v1/synthetic/plan.json': '54b1de0cf40155ff1eebdadd41fcc5b682cf58dcb9c47a0d8e10cd04f48cb02c', 'context/reconciliation/local-f0-operation-sources/runtime-lease-branch-v1/author-history/first-static-preparation/generated/review-output/runtime-lease-branch-v1/synthetic/reset-pending-baseline.sql': '662af8936bd9a4e5ed523597494f4360ba695049758d81b578c0cbbbfdb0b122', 'context/reconciliation/local-f0-operation-sources/runtime-lease-branch-v1/author-history/first-static-preparation/generated/review-output/runtime-lease-branch-v1/synthetic/restore-old.sql': 'd4d8159e8eb5d7a7d5e492ff1b3217570979f92b390cfa943694e6a3c079c871', 'context/reconciliation/local-f0-operation-sources/runtime-lease-branch-v1/author-history/first-static-preparation/generated/review-output/runtime-lease-branch-v1/synthetic/setup-original.sql': '01f2905de34317293bbb38920c30367c5b30cb1f95ac75aadf1d979d0a27259b', 'context/reconciliation/local-f0-operation-sources/runtime-lease-branch-v1/author-history/first-static-preparation/generated/review-output/runtime-lease-branch-v1/synthetic/worker-current.sql': '53caac91c0a1de2babd7582fc575a7b883d91fd9dcebb6138f387bda5f31e04d', 'context/reconciliation/local-f0-operation-sources/runtime-lease-branch-v1/author-history/first-static-preparation/generated/review-output/runtime-lease-branch-v1/synthetic/worker-expired.sql': '8f94787197176733cbd8af7b645007915a8d4c518ce4ddecf0228be329062d13', 'context/reconciliation/local-f0-operation-sources/runtime-lease-branch-v1/author-history/first-static-preparation/generated/review-output/runtime-lease-branch-v1/synthetic/worker-wrong-fence.sql': '6b0e66fb4c6e2d19ce93f0a3f75b978cfcf1723fefe3a6976a6c0dc2ed0cc34c', 'context/reconciliation/local-f0-operation-sources/runtime-lease-branch-v1/author-history/first-static-preparation/generated/review-output/runtime-lease-branch-v1/synthetic/worker-wrong-secret.sql': '4245b58cbe1a750167eb6f8d29e364e798d187a800b66ed59a59b16a754a7169', 'context/reconciliation/local-f0-operation-sources/runtime-lease-branch-v1/author-history/first-static-preparation/generated/review-output/runtime-lease-branch-v1/history-source-artifact/migrations/migration_lock.toml': '1db17a8d051aa136110736752c5e1f8b7ed92b6ea8e803112fbbe2497047c210', 'context/reconciliation/local-f0-operation-sources/runtime-lease-branch-v1/author-history/first-static-preparation/generated/review-output/runtime-lease-branch-v1/history-source-artifact/migrations/20261117000100_f0_local_initial/migration.sql': '5ae39abf991f9c189e367eb6ab6968b0ad50836bf4220ac27ef8c18306ac26ad', 'context/reconciliation/local-f0-operation-sources/runtime-lease-branch-v1/author-history/first-static-preparation/generated/review-output/runtime-lease-branch-v1/history-source-artifact/migrations/20261120000100_f0_runtime_lease_branch_v1/migration.sql': '49c3345c281d8ef62355d5392d02085d5fdfa71f7193e7e0bd4264562c33cfb7', 'review-output/runtime-lease-branch-v1/effective-runtime-transition.sql': 'e8c54dc020f0469657424876d4b3668f5234ce7c1708fc15c30644744bef9fff', 'review-output/runtime-lease-branch-v1/overlay.json': 'e658f7eadb30d95c253b00ae52ef7d506110c6d098aa2dea46df9a2d411950aa', 'review-output/runtime-lease-branch-v1/proposal.json': 'afa3e5c1091100ff4f219aef6519162b7d9661c9f9e1296ce9f269b1dc0024df', 'review-output/runtime-lease-branch-v1/worker-acl32.json': '6909f3cd9e2a795d1f39379b7f81db4c24f9526e235e802deea5ce1a2da8e5a3', 'review-output/runtime-lease-branch-v1/synthetic/direct-helper.sql': '25a7bd120d3918d7c015399146f31b3a8c4f219088f6f18fcd5b2b3ebca8ff15', 'review-output/runtime-lease-branch-v1/synthetic/install-nested.sql': 'aa85b8bb7cb0a4c54d36413b1a272b5be59c6536ae5a69f4abe940eb20eb1581', 'review-output/runtime-lease-branch-v1/synthetic/observe-preconditions.sql': '3281842730e91c4dd648590c8005c16ccf4e156b201e9c62cd0b724c5dd60870', 'review-output/runtime-lease-branch-v1/synthetic/observe.sql': '70858d2f7b85921a9af72148e34c0dd844aff58878fda564b7cd25751036e668', 'review-output/runtime-lease-branch-v1/synthetic/pending-update.sql': '878fc41806848b068165e029e6cc049928b43303f653d1fe1db6b2630f1bce8b', 'review-output/runtime-lease-branch-v1/synthetic/plan.json': 'd93b7cbd810251761ff0f0c4e2f28dfa7f10909315e53e16a31dcf667518565f', 'review-output/runtime-lease-branch-v1/synthetic/reset-pending-baseline.sql': '662af8936bd9a4e5ed523597494f4360ba695049758d81b578c0cbbbfdb0b122', 'review-output/runtime-lease-branch-v1/synthetic/restore-old.sql': 'd4d8159e8eb5d7a7d5e492ff1b3217570979f92b390cfa943694e6a3c079c871', 'review-output/runtime-lease-branch-v1/synthetic/setup-original.sql': '01f2905de34317293bbb38920c30367c5b30cb1f95ac75aadf1d979d0a27259b', 'review-output/runtime-lease-branch-v1/synthetic/worker-current.sql': '53caac91c0a1de2babd7582fc575a7b883d91fd9dcebb6138f387bda5f31e04d', 'review-output/runtime-lease-branch-v1/synthetic/worker-expired.sql': '8f94787197176733cbd8af7b645007915a8d4c518ce4ddecf0228be329062d13', 'review-output/runtime-lease-branch-v1/synthetic/worker-wrong-fence.sql': '6b0e66fb4c6e2d19ce93f0a3f75b978cfcf1723fefe3a6976a6c0dc2ed0cc34c', 'review-output/runtime-lease-branch-v1/synthetic/worker-wrong-secret.sql': '4245b58cbe1a750167eb6f8d29e364e798d187a800b66ed59a59b16a754a7169', 'review-output/runtime-lease-branch-v1/history-source-artifact/migrations/migration_lock.toml': '1db17a8d051aa136110736752c5e1f8b7ed92b6ea8e803112fbbe2497047c210', 'review-output/runtime-lease-branch-v1/history-source-artifact/migrations/20261117000100_f0_local_initial/migration.sql': '5ae39abf991f9c189e367eb6ab6968b0ad50836bf4220ac27ef8c18306ac26ad', 'review-output/runtime-lease-branch-v1/history-source-artifact/migrations/20261120000100_f0_runtime_lease_branch_v1/migration.sql': '49c3345c281d8ef62355d5392d02085d5fdfa71f7193e7e0bd4264562c33cfb7', 'scripts/sql-review/local_image_identity.py': 'a0742d4f25271cc5c4b8bced19909415181a76fb9856948a3dffed28abb80604', 'scripts/sql-review/test_local_image_identity.py': '0edae319a544aaaa8ed112e2ec477fe7ac428b58a7970ca8cd0e33ff006abe93', 'scripts/sql-review/fixtures/postgres-17.11-approved-manifest.json': '996e9dc583ba9f0265a2c75547a9c95fb22c251e394749cab205a0a00e1856a1'}

class Held(Exception):
    def __init__(self,code):self.code=code;super().__init__(code)

def need(value,code):
    if not value:raise Held(code)

def sha(value):return hashlib.sha256(value).hexdigest()
def encoded(value):return (json.dumps(value,indent=2,allow_nan=False)+'\n').encode('utf8')
def aggregate(files):return sha(''.join(name+'\0'+files[name]+'\n' for name in sorted(files)).encode())

def decoded(raw):
    need(type(raw)is bytes and len(raw)<=8*1024*1024,'BOUNDED_JSON_BYTES')
    def pairs(items):
        value={}
        for key,item in items:need(key not in value,'DUPLICATE_JSON_KEY');value[key]=item
        return value
    def finite(text):
        value=float(text);need(math.isfinite(value),'NONFINITE_JSON');return value
    try:return json.loads(raw,object_pairs_hook=pairs,parse_float=finite,parse_constant=lambda _:(_ for _ in ()).throw(Held('NONFINITE_JSON')))
    except (ValueError,RecursionError,UnicodeError):raise Held('MALFORMED_JSON') from None

def relative(name):
    need(type(name)is str and name and '\\'not in name and ':'not in name and not any(ord(c)<32 for c in name) and all(p not in ('','.','..')for p in name.split('/')),'SAFE_RELATIVE_PATH')
    need(not Path(name).is_absolute(),'SAFE_RELATIVE_PATH');return name

def mapping(value):
    need(type(value)is dict and value and all(type(v)is str and re.fullmatch('[0-9a-f]{64}',v)for v in value.values()),'EXACT_SOURCE_MAP')
    for n in value:relative(n)
    return value

def closed(path,cap=8*1024*1024):
    """Two independently closed byte reads with handle/path identity barriers.

    This detects changes during the bounded read; it promises no perpetual
    atomicity after return. On Windows ctime may differ by representation, so
    each representation is compared with itself, rather than cross-compared.
    """
    path=Path(path)
    need(not any(p.is_symlink()for p in (path,*path.parents)),'SYMLINK_REFUSED')
    def ident(s):return (s.st_dev,s.st_ino,s.st_mode,s.st_nlink,s.st_size,s.st_mtime_ns,s.st_ctime_ns)
    def once():
        a=path.lstat();need(stat.S_ISREG(a.st_mode)and a.st_nlink==1 and 0<=a.st_size<=cap,'REGULAR_BOUNDED_SINGLE_LINK')
        with path.open('rb')as f:
            h=os.fstat(f.fileno());need(stat.S_ISREG(h.st_mode)and h.st_nlink==1 and (h.st_dev,h.st_ino,h.st_size)==(a.st_dev,a.st_ino,a.st_size),'OPEN_IDENTITY')
            raw=f.read(cap+1);z=os.fstat(f.fileno());need(ident(h)==ident(z),'HANDLE_CHANGED_DURING_READ')
        b=path.lstat();need(ident(a)==ident(b)and len(raw)==a.st_size,'PATH_CHANGED_DURING_READ')
        return raw,ident(b)
    first,a=once();second,b=once();need(a==b and first==second,'CLOSED_READ_BYTES_CHANGED');return first

def root_read(root,name,wanted=None):
    relative(name);root=Path(root).resolve();path=root/name
    need(path.resolve().is_relative_to(root),'ROOT_ESCAPE');raw=closed(path)
    if wanted is not None:need(sha(raw)==wanted,'CURRENT_SOURCE_DRIFT')
    return raw

def five_map(external):return {name:sha(closed(Path(external)/name))for name in FIVE}

def admit(root,external,require_reviews=True):
    root=Path(root).resolve();external=Path(external).resolve();five=five_map(external)
    value=decoded(root_read(root,VALIDATION));need(value.get('schema')=='workinants.lease-mechanism-v1-source-validation.v1','OWNED_SOURCE_SCHEMA')
    need(value.get('source_files_sha256')==BASE_FILES and value.get('operator_sources_sha256')==five,'EXACT_SOURCE_AND_FIVE')
    archive=mapping(value.get('archive_files_sha256'));need(all(n.startswith(ARCHIVE+'/')for n in archive),'EXACT_ARCHIVE_PREFIX')
    actual={p.relative_to(root).as_posix():sha(closed(p))for p in (root/ARCHIVE).rglob('*')if p.is_file()}
    need(actual==archive and not any(p.is_symlink()for p in (root/ARCHIVE).rglob('*')),'EXACT_CLOSED_ARCHIVE')
    for name,wanted in five.items():need(archive.get(ARCHIVE+'/'+name+'.txt')==wanted,'ARCHIVED_FIVE_IDENTITY')
    files={**BASE_FILES,**archive,VALIDATION:sha(root_read(root,VALIDATION))}
    blobs={n:root_read(root,n,w)for n,w in files.items()}
    need(len(BASE_FILES)==60,'EXACT_REVIEWED_ARTIFACT57_IMAGE3')
    if require_reviews:
        for gate in ('independent_source_review','independent_binary_safety_review'):
            review=value.get(gate);need(type(review)is dict and review.get('decision')=='SOURCE_APPROVED'and review.get('operator_sources_sha256')==five,'PENDING_SOURCE_REVIEW')
            need(review.get('path')in archive and archive[review['path']]==review.get('sha256'),'PINNED_INDEPENDENT_REVIEW')
            receipt=decoded(blobs[review['path']]);need(receipt.get('decision')=='SOURCE_APPROVED'and receipt.get('operator_sources_sha256')==five,'INDEPENDENT_REVIEW_BINDING')
    return files,blobs,five

def shape(manifest,root,external,require_reviews=True,require_literal=True):
    required={'schema','purpose','run_id','evidence_directory','source_commit','source_tree','packet_sha256','packet_files_sha256','external_files_sha256','image','config_digest','database','target','review_status'}
    need(type(manifest)is dict and set(manifest)==required,'MANIFEST_EXACT_FIELDS')
    need(manifest['schema']=='workinants.lease-mechanism-v1-operation-manifest.v1'and manifest['purpose']==PURPOSE,'MANIFEST_PURPOSE')
    run=manifest['run_id'];need(type(run)is str and str(uuid.UUID(run))==run,'RUN_UUID')
    target={'name':'wa-p0c-'+run[:8]+'-leasemech','volume':'wa-p0c-'+run[:8]+'-leasemech-data','labels':{'workinants.rehearsal':'p0c-local-f0','workinants.rehearsal.run':run}}
    need(manifest['target']==target and manifest['image']==IMAGE and manifest['config_digest']==CONFIG and manifest['database']==DATABASE,'EXACT_RESOURCE_PROFILE')
    need(type(manifest['evidence_directory'])is str,'EVIDENCE_PATH_TYPE');out=Path(manifest['evidence_directory']);base=Path(external).resolve()
    need(out.is_absolute()and out.resolve().parent==base and out.name=='local-f0-lease-mechanism-v1-'+run[:8]and not out.exists(),'FRESH_EXTERNAL_EVIDENCE')
    files,blobs,five=admit(root,external,require_reviews)
    need(manifest['packet_files_sha256']==files and manifest['external_files_sha256']==five and manifest['packet_sha256']==aggregate(files),'EXACT_FULL_PACKET')
    need(all(type(manifest[k])is str and re.fullmatch('[0-9a-f]{40}',manifest[k])for k in ('source_commit','source_tree')),'PINNED_COMMIT_TREE')
    if require_literal:need(manifest['review_status']==REVIEW_STATUS,'PENDING_OPERATIONAL_LITERAL')
    return files,blobs,five

def prepare(root,external,run_id):
    run_id=str(uuid.UUID(run_id));files,_,five=admit(root,external,False)
    return {'schema':'workinants.lease-mechanism-v1-operation-manifest.v1','purpose':PURPOSE,'run_id':run_id,'evidence_directory':str(Path(external).resolve()/('local-f0-lease-mechanism-v1-'+run_id[:8])),'source_commit':'UNPINNED','source_tree':'UNPINNED','packet_sha256':aggregate(files),'packet_files_sha256':files,'external_files_sha256':five,'image':IMAGE,'config_digest':CONFIG,'database':DATABASE,'target':{'name':'wa-p0c-'+run_id[:8]+'-leasemech','volume':'wa-p0c-'+run_id[:8]+'-leasemech-data','labels':{'workinants.rehearsal':'p0c-local-f0','workinants.rehearsal.run':run_id}},'review_status':'PENDING'}

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--root',required=True);p.add_argument('--run-id',required=True);p.add_argument('--output',required=True);a=p.parse_args()
    value=prepare(a.root,Path(__file__).resolve().parent,a.run_id)
    with Path(a.output).open('xb')as f:f.write(encoded(value))
