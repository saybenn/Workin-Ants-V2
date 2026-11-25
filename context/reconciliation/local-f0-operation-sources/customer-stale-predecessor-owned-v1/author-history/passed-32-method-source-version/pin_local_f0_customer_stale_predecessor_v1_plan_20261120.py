"""Closed current+committed CSP1 source pinning; no runtime/resource API."""
import argparse,hashlib,io,json,os,re,stat,types
from pathlib import Path
TASK=Path(__file__).resolve().parent;ROOT=TASK/'workinants-correction-pass'
ARCHIVE='context/reconciliation/local-f0-operation-sources/customer-stale-predecessor-owned-v1'
VALIDATION='context/reconciliation/local-f0-customer-stale-predecessor-owned-v1-source-validation.json'
FIVE=('execute_local_f0_customer_stale_predecessor_v1_20261120.py','local_f0_customer_stale_predecessor_v1_operation_steps.py','prepare_local_f0_customer_stale_predecessor_v1_plan.py','check_local_f0_customer_stale_predecessor_v1_operation.py','pin_local_f0_customer_stale_predecessor_v1_plan_20261120.py')
GATES=('independent_source_review','independent_owned_resource_review','independent_safety_sql_review','independent_binary_transport_review','Root_source_review')
class Held(Exception):
 def __init__(self,code):self.code=code;super().__init__(code)
def need(value,code):
 if not value:raise Held(code)
def sha(raw):return hashlib.sha256(raw).hexdigest()
def encoded(v):return (json.dumps(v,indent=2,allow_nan=False)+'\n').encode()
def unique(raw):
 def pairs(items):
  d={}
  for k,v in items:need(k not in d,'DUPLICATE_JSON');d[k]=v
  return d
 return json.loads(raw,object_pairs_hook=pairs,parse_constant=lambda _:(_ for _ in()).throw(Held('NONFINITE_JSON')))
def closed(path,limit=16*1024*1024):
 path=Path(path);before=path.lstat();need(not path.is_symlink() and stat.S_ISREG(before.st_mode) and before.st_nlink==1 and before.st_size<=limit,'SOURCE_REGULAR_LIMIT')
 keys=('st_mode','st_dev','st_ino','st_nlink','st_size','st_mtime_ns');identity=lambda s:tuple(getattr(s,k)for k in keys)
 with path.open('rb')as stream:
  opened=os.fstat(stream.fileno());need(identity(opened)==identity(before),'SOURCE_OPEN_IDENTITY');raw=stream.read(limit+1);after=os.fstat(stream.fileno());need(identity(after)==identity(opened) and after.st_ctime_ns==opened.st_ctime_ns,'SOURCE_READ_IDENTITY')
 final=path.lstat();need(identity(final)==identity(before) and final.st_ctime_ns==before.st_ctime_ns and len(raw)==before.st_size and len(raw)<=limit,'SOURCE_CLOSED_IDENTITY');return raw
def metadata_before_compile(value):
 five={n:sha(closed(TASK/n))for n in FIVE};need(value['customer_stale']['external_files_sha256']==five,'EXACT_PHYSICAL_FIVE')
 val=unique(closed(ROOT/VALIDATION));need(val['operator_sources_sha256']==five,'SOURCE_FIVE_VALIDATION')
 for n,h in five.items():need(closed(ROOT/ARCHIVE/(n+'.txt'))==closed(TASK/n),'SOURCE_FIVE_ARCHIVE')
 for key in GATES:
  review=val.get(key);need(type(review)is dict and review.get('decision')=='SOURCE_APPROVED' and review.get('operator_sources_sha256')==five and type(review.get('path'))is str and review['path'].startswith(ARCHIVE+'/reviews/'),'PENDING_SOURCE_REVIEW')
  path=review['path'];need(path in val['archive_files_sha256'] and val['archive_files_sha256'][path]==review['sha256'],'REVIEW_CLOSED_ARCHIVE')
  raw=closed(ROOT/path);need(sha(raw)==review['sha256'],'REVIEW_RECEIPT_HASH');actual=unique(raw);need(actual.get('decision')=='SOURCE_APPROVED' and actual.get('operator_sources_sha256')==five,'REVIEW_RECEIPT_BINDING')
 return five
def compiler(name,five):
 raw=closed(TASK/name);need(sha(raw)==five[name],'CLOSED_CODE_DRIFT');module=types.ModuleType('_CSP1_closed_'+name.replace('.','_'));module.__file__=str(TASK/name);exec(compile(raw,module.__file__,'exec'),module.__dict__);return module
def verified_view(path,*,pinned):
 path=Path(path).resolve();need(path.name=='operation-manifest.json' and path.is_relative_to(TASK) and not path.is_relative_to(ROOT),'EXTERNAL_MANIFEST_PATH')
 raw=closed(path);value=unique(raw);five=metadata_before_compile(value)
 prep=compiler(FIVE[2],five);files=prep.validate_plan(value,pinned=pinned,require_reviews=True)
 need(closed(path)==raw and all(sha(closed(TASK/n))==h for n,h in five.items()),'SOURCE_OR_MANIFEST_DRIFT')
 return path,raw,value,five,files
def git_bytes(args,five,payload=None,files=None,commit=None):
 need(args in (['rev-parse','HEAD'],['rev-parse','HEAD^{tree}'],['cat-file','--batch']),'READONLY_GIT_ALLOWLIST')
 core=compiler(FIVE[0],five)
 options={'closed_git_files':files,'git_commit':commit}if args==['cat-file','--batch']else{}
 need(args!=['cat-file','--batch']or files is not None,'CLOSED_FULL_GIT_PROFILE_REQUIRED')
 result=core.binary_process(['git','--no-optional-locks','-c','core.longpaths=true',*args],payload,120,cwd=ROOT,**options)
 need(type(result.returncode)is int and result.returncode==0 and result.stderr==b'','READONLY_GIT_FAILED');return result.stdout
def committed_barrier(value,five,files):
 need(git_bytes(['rev-parse','HEAD'],five).decode('ascii').strip()==value['source_commit'] and git_bytes(['rev-parse','HEAD^{tree}'],five).decode('ascii').strip()==value['source_tree'],'CURRENT_PUBLISHED_CHECKPOINT')
 request=''.join(value['source_commit']+':'+n+'\n'for n in sorted(files)).encode();data=io.BytesIO(git_bytes(['cat-file','--batch'],five,request,files,value['source_commit']))
 for n,h in sorted(files.items()):
  head=data.readline().split();need(len(head)==3 and re.fullmatch(b'[0-9a-f]{40}',head[0]) and head[1]==b'blob' and head[2].isdigit(),'COMMITTED_BLOB_HEADER');length=int(head[2]);body=data.read(length)
  need(len(body)==length and sha(body)==h and hashlib.sha1(b'blob '+str(length).encode()+b'\0'+body).hexdigest().encode()==head[0] and data.read(1)==b'\n','COMMITTED_SOURCE_DRIFT')
 need(data.read()==b'' and git_bytes(['rev-parse','HEAD'],five).decode('ascii').strip()==value['source_commit'],'COMMITTED_STREAM_OR_HEAD_DRIFT')
 for n,h in files.items():need(sha(closed(ROOT/n))==h,'FINAL_CURRENT_SOURCE_DRIFT')
 for n,h in five.items():need(sha(closed(TASK/n))==h,'FINAL_PHYSICAL_FIVE_DRIFT')
def verify_pinned(path):
 path,raw,value,five,files=verified_view(path,pinned=True);committed_barrier(value,five,files);need(closed(path)==raw,'FINAL_MANIFEST_REFERENCE_DRIFT')
 return {'status':'SOURCE_CURRENT_AND_COMMITTED_ONLY','files':len(files),'packet_sha256':value['packet_sha256'],'manifest_unchanged':True,'runtime':'NOT_RUN'}
def pin(path):
 path,raw,value,five,files=verified_view(path,pinned=False);need(value['review_status']=='PENDING_OPERATIONAL_REVIEW','PIN_LEAVES_PENDING_LITERAL')
 commit=git_bytes(['rev-parse','HEAD'],five).decode('ascii').strip();tree=git_bytes(['rev-parse','HEAD^{tree}'],five).decode('ascii').strip();need(re.fullmatch('[0-9a-f]{40}',commit) and re.fullmatch('[0-9a-f]{40}',tree),'COMMIT_TREE_FORMAT')
 pinned={**value,'source_commit':commit,'source_tree':tree,'packet_files_sha256':files,'packet_sha256':sha(''.join(n+'\0'+files[n]+'\n'for n in sorted(files)).encode()),'pin_helper_sha256':five[FIVE[4]]}
 committed_barrier(pinned,five,files);_,again,_,_,again_files=verified_view(path,pinned=False);need(again==raw and again_files==files,'PIN_INPUT_DRIFT')
 before=path.with_name('operation-manifest-before-source-pin.json');temp=path.with_name('operation-manifest-source-pin.tmp');need(not before.exists() and not temp.exists(),'FRESH_PIN_OUTPUTS')
 with before.open('xb')as f:f.write(raw)
 with temp.open('xb')as f:f.write(encoded(pinned))
 temp.replace(path)
 return {'status':'SOURCE_PINNED_PENDING_OPERATIONAL_REVIEW','source_commit':commit,'source_tree':tree,'packet_sha256':pinned['packet_sha256'],'packet_files':len(files),'manifest_sha256':sha(closed(path)),'runtime':'NOT_RUN','Git_mutated':False}
def main(argv=None):
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('manifest',type=Path);p.add_argument('--verify-pinned-only',action='store_true');a=p.parse_args(argv)
 try:print(json.dumps(verify_pinned(a.manifest)if a.verify_pinned_only else pin(a.manifest)));return 0
 except BaseException as e:print(json.dumps({'status':'HELD','code':e.code if isinstance(e,Held)else'CSP1_SOURCE_PIN_REFUSED','raw_error_discarded':True,'runtime':'NOT_RUN'}));return 1
if __name__=='__main__':raise SystemExit(main())
