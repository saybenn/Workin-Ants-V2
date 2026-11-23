"""Pure preparation/admission for the held synthetic eleven-case mechanism.

No migration/default application is installed by this family. Git reads are
performed only by the separate pinner, after source and review gates pass.
"""
from pathlib import Path
import argparse
import hashlib
import json
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
BASE_FILES={}

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
    try:return json.loads(raw,object_pairs_hook=pairs,parse_constant=lambda _:(_ for _ in ()).throw(Held('NONFINITE_JSON')))
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
