"""Pure CSP1 source preparation; all execution gates remain PENDING."""

import argparse

from copy import deepcopy

import gzip

import hashlib

import io

import json

from pathlib import Path

import re

import stat

import tarfile

import uuid

IMAGE='docker.io/library/postgres:17.11@sha256:996e9dc583ba9f0265a2c75547a9c95fb22c251e394749cab205a0a00e1856a1'

MIGRATION='prisma/foundation/migrations/20261117000100_f0_local_initial/migration.sql'

SQL='review-output/foundation-application.review.sql'

SQL_SHA='5ae39abf991f9c189e367eb6ab6968b0ad50836bf4220ac27ef8c18306ac26ad'

SCHEMA='prisma/review/foundation-candidate.prisma'

LOCK='prisma/foundation/migrations/migration_lock.toml'

RUNTIME=('prisma.local-f0.config.mjs','scripts/sql-review/local-f0-migrate-guard.mjs','scripts/sql-review/local-f0-migrate-runner.mjs')

HISTORY_HELPER='scripts/prepare-local-f0-history.py'

HISTORY_SHA='33fe46e1b50c8d808ffb95b60cc42750e795582e6a1b15fb82f4fe93321281f8'

IMAGE_PROOF_REVIEW=('context/reconciliation/local-f0-operation-sources/owner-read-resource-mount-v2/reviews/image-proof-independent-source.json','b628b6d98ad22ea7def4dd7a51264025c50bde116451ae516f3e52f55ba9542a')

IMAGE_FILES={'scripts/sql-review/local_image_identity.py':'a0742d4f25271cc5c4b8bced19909415181a76fb9856948a3dffed28abb80604','scripts/sql-review/test_local_image_identity.py':'0edae319a544aaaa8ed112e2ec477fe7ac428b58a7970ca8cd0e33ff006abe93','scripts/sql-review/fixtures/postgres-17.11-approved-manifest.json':'996e9dc583ba9f0265a2c75547a9c95fb22c251e394749cab205a0a00e1856a1'}

TOOL_CLOSURE='context/reconciliation/local-f0-tooling/prisma-tools-closure.json'

TOOL_CLOSURE_SHA='610e36e4006e9680d0e6a036486f302a18ecce9593699125b4173f5914acb88b'

TOOL_ARCHIVE_SHA='481b68ef007cf8889045a50ca3545bb8bd2f6d7290dd40ee730adf12bfd198fb'

TASK=Path(__file__).resolve().parent
ROOT=TASK/'workinants-correction-pass'

class Refused(Exception):pass

def need(value,code):
 if not value:raise Refused(code)

def sha(raw):return hashlib.sha256(raw).hexdigest()

def data(value):return (json.dumps(value,indent=2,allow_nan=False)+'\n').encode()

def decoded(raw):
 def pairs(items):
  value={}
  for key,item in items:need(key not in value,'DUPLICATE_JSON_KEY');value[key]=item
  return value
 return json.loads(raw,object_pairs_hook=pairs,parse_constant=lambda _:(_ for _ in ()).throw(Refused('NONFINITE_JSON')))

def relative(name):
 need(type(name) is str and name and not Path(name).is_absolute() and '\\' not in name and ':' not in name and not any(ord(x)<32 for x in name) and all(x not in ('','.','..') for x in name.split('/')),'SAFE_SOURCE_PATH');return name

def mapping(value):
 need(type(value) is dict and bool(value) and all(type(wanted) is str and re.fullmatch('[0-9a-f]{64}',wanted) for wanted in value.values()),'SOURCE_HASH_MAP_REQUIRED')
 for name in value:relative(name)
 return value

def source(relative,wanted=None):
 name=relative;need(type(name) is str and name and not Path(name).is_absolute() and '\\' not in name and ':' not in name and not any(ord(x)<32 for x in name) and all(x not in ('','.','..') for x in name.split('/')),'SAFE_SOURCE_PATH')
 path=ROOT/name;need(not any(p.is_symlink() for p in (path,*path.parents) if p!=ROOT.parent),'SOURCE_SYMLINK_REFUSED');need(stat.S_ISREG(path.lstat().st_mode),'REGULAR_SOURCE_REQUIRED');path=path.resolve();need(path.is_relative_to(ROOT.resolve()),'SOURCE_PATH_ESCAPE');raw=path.read_bytes()
 if wanted is not None:need(sha(raw)==wanted,'SOURCE_FILE_DRIFT')
 return raw

def archive_tree(root,pins):
 mapping(pins);need(all(name.startswith(root+'/') for name in pins),'EXACT_ARCHIVE_ROOT')
 actual={p.relative_to(ROOT).as_posix():sha(p.read_bytes()) for p in (ROOT/root).rglob('*') if p.is_file()}
 need(not any(p.is_symlink() for p in (ROOT/root).rglob('*')) and actual==pins,'EXACT_CLOSED_ARCHIVE_TREE')
 for name,wanted in pins.items():source(name,wanted)

def verify_tools(path,wanted,nested_tools):
 closure=decoded(source(TOOL_CLOSURE,TOOL_CLOSURE_SHA));tools=mapping(closure['tools_files_sha256'])
 need(type(closure['file_count']) is int and closure['file_count']==len(tools)==10300 and type(closure['archive_bytes']) is int and closure['archive_bytes']==113900903 and closure['archive_sha256']==wanted==TOOL_ARCHIVE_SHA and nested_tools['files_sha256']==tools,'EXACT_TOOLS10300_CLOSURE')
 need(tuple(nested_tools.get(key) for key in ('node_version','prisma_version','engine_commit'))==tuple(closure[key] for key in ('node_version','prisma_version','engine_commit'))==('v24.22.1','7.10.1','d1b3f377ca835d73fd50954a5e22128b9ebdd6b8'),'EXACT_TOOL_VERSIONS')
 archive=Path(path);need(archive.is_absolute() and archive.resolve().is_relative_to(TASK.resolve()) and not archive.resolve().is_relative_to(ROOT.resolve()) and not archive.is_symlink() and stat.S_ISREG(archive.lstat().st_mode),'EXTERNAL_REGULAR_TOOL_ARCHIVE')
 raw=archive.read_bytes();need(len(raw)==113900903 and sha(raw)==wanted,'EXACT_TOOL_ARCHIVE_BYTES');seen=set()
 with tarfile.open(fileobj=io.BytesIO(raw),mode='r:gz') as tar:
  for member in tar:
   relative(member.name);need(member.isfile() and not member.issym() and not member.islnk() and member.name in tools and member.name not in seen,'SAFE_TOOL_ARCHIVE_MEMBER')
   handle=tar.extractfile(member)
   with handle:content=handle.read()
   need(sha(content)==tools[member.name],'TOOL_MEMBER_CONTENT_DRIFT');seen.add(member.name)
 need(seen==set(tools),'EXACT_TOOL_ARCHIVE_FILE_SET');return closure

FIXTURES='review-output/customer-stale-predecessor-v1/fixtures.json'

FIXTURES_SHA='c2074a45f80147833e958d1f02b5d3840b32eb13a46033ebc7f1e75c322eb10b'

CONTENT_SHA='58f803d0ba96e96b543447a9019c03d668b57885c35c9d6be1bcbc6ea00144c6'

CHILD_VALIDATION='context/reconciliation/customer-stale-predecessor-v1-source-validation.json'

CHILD_VALIDATION_SHA='e143965d80ede2a4730ab1b5632e51d3280cb447c974e61ca2cd18ea59632214'

OWNED_ARCHIVE='context/reconciliation/local-f0-operation-sources/customer-stale-predecessor-owned-v1'

OWNED_VALIDATION='context/reconciliation/local-f0-customer-stale-predecessor-owned-v1-source-validation.json'

EXTERNAL_FILES=('execute_local_f0_customer_stale_predecessor_v1_20261120.py', 'local_f0_customer_stale_predecessor_v1_operation_steps.py', 'prepare_local_f0_customer_stale_predecessor_v1_plan.py', 'check_local_f0_customer_stale_predecessor_v1_operation.py', 'pin_local_f0_customer_stale_predecessor_v1_plan_20261120.py')

FIXED_CATALOG_MAP_SHA='23513b3f52f7ae960b25b0b0864c4ddfff69373fe1865b2b0776a21bb816fedf'

FIXED_CHILD_MAP_SHA='30e893686b10be86d0f43b3692879881d070905524475f9b4355f7dcd243afb0'

OPERATION_RUN='73292a8f-838e-4d92-be2e-42170dd5ec6a'
FIXTURE_RUN='36e9cae1-53fc-44a7-b90f-b91fb6e8d2b5'
SOURCE_GATES=('independent_source_review','independent_owned_resource_review','independent_safety_sql_review','independent_binary_transport_review','Root_source_review')

def source_inventory(current,packet,external,require_reviews=False):
 need(type(require_reviews)is bool,'REVIEW_MODE_TYPE')
 fixed=decoded(source(OWNED_ARCHIVE+'/fixed-catalog-source-map.json',FIXED_CATALOG_MAP_SHA))
 need(current==fixed,'EXACT_CATALOG_BASIS_MAP')
 child_fixed=decoded(source(OWNED_ARCHIVE+'/fixed-child-current-map.json',FIXED_CHILD_MAP_SHA))
 need(len(child_fixed)==115,'EXACT_CURRENT_CHILD115')
 child_raw=source(CHILD_VALIDATION,CHILD_VALIDATION_SHA);child=decoded(child_raw);owned_raw=source(OWNED_VALIDATION);owned=decoded(owned_raw)
 need(child['review_gate']=='SOURCE_APPROVED' and child['source_files_sha256']==packet['source_files_sha256'] and owned['schema']=='workinants.customer-stale-predecessor-owned-v1-source-validation.v1' and owned['operator_sources_sha256']==external,'CSP1_SOURCE_METADATA_BINDING')
 expected=dict(current)
 def add(name,wanted):
  relative(name);need(name not in expected or expected[name]==wanted,'SOURCE_BINDING_CONFLICT');source(name,wanted);expected[name]=wanted
 for mapping_ in(child_fixed,child['source_files_sha256'],child['packet_files_sha256'],child['archive_files_sha256'],owned['archive_files_sha256'],IMAGE_FILES):
  for name,wanted in mapping(mapping_).items():add(name,wanted)
 for n,h in((CHILD_VALIDATION,CHILD_VALIDATION_SHA),(OWNED_VALIDATION,sha(owned_raw)),(FIXTURES,FIXTURES_SHA),(TOOL_CLOSURE,TOOL_CLOSURE_SHA),IMAGE_PROOF_REVIEW):add(n,h)
 archive_tree(OWNED_ARCHIVE,owned['archive_files_sha256'])
 for n,h in external.items():need(expected.get(OWNED_ARCHIVE+'/'+n+'.txt')==h and sha((TASK/n).read_bytes())==h and not(TASK/n).is_symlink(),'EXACT_PHYSICAL_FIVE')
 for key in SOURCE_GATES:
  review=owned.get(key);need(type(review)is dict and review.get('decision')in('PENDING','SOURCE_APPROVED'),'NEW_PENDING_SOURCE_GATE_REQUIRED')
  if require_reviews:
   need(review.get('decision')=='SOURCE_APPROVED' and review.get('operator_sources_sha256')==external and type(review.get('path'))is str and review['path'].startswith(OWNED_ARCHIVE+'/reviews/') and expected.get(review['path'])==review.get('sha256'),'CSP1_REVIEW_REQUIRED')
   actual=decoded(source(review['path'],review['sha256']));need(actual.get('decision')=='SOURCE_APPROVED' and actual.get('operator_sources_sha256')==external,'CSP1_REVIEW_RECEIPT_BINDING')
 for key in('independent_source_review','Root_source_review'):
  review=child[key];need(review['decision']=='SOURCE_APPROVED' and expected.get(review['path'])==review['sha256'],'ACCEPTED_CHILD_REVIEW_BYTES')
 for n,h in packet['source_files_sha256'].items():need(expected.get(n)==h,'CHILD_SOURCE_NOT_ADMITTED')
 for n,h in packet['prepared_files_sha256'].items():need(expected.get('review-output/customer-stale-predecessor-v1/'+n)==h,'CHILD_ARTIFACT_NOT_ADMITTED')
 catalog=decoded(source('review-output/native-catalog/source-pins.json'));need(len(mapping(catalog))==16 and all(expected.get(n)==h for n,h in catalog.items()),'CLOSED_CATALOG16')
 return dict(sorted(expected.items()))

def validate_plan(value,*,pinned=False,require_reviews=True):
 need(type(value)is dict and value.get('purpose')=='LOCAL_F0_CUSTOMER_STALE_PREDECESSOR_OWNED_V1_REHEARSAL' and value.get('status')=='SOURCE_PREPARED_NOT_EXECUTED' and value.get('review_status')in('PENDING_OPERATIONAL_REVIEW','APPROVED_LOCAL_F0_CUSTOMER_STALE_PREDECESSOR_OWNED_V1_ATTEMPT'),'EXACT_CSP1_SOURCE_PLAN')
 fields={'purpose','authority','run_id','source_commit','source_tree','packet_files_sha256','packet_sha256','evidence_directory','targets','migration_targets','image','database','run_label','tool_archive','tool_archive_sha256','wrapper_sha256','review_status','storage','cleanup','source_history_rule','status','server_diagnostics','catalog','allowed_catalog_operations','steps_sha256','customer_stale','prepared_source_file_inventory_sha256','guarded_history_helper_sha256','execution_hold'}
 need(set(value)==fields|({'pin_helper_sha256'}if pinned else set()),'CSP1_MANIFEST_FIELD_ALLOWLIST')
 run=value['run_id'];need(run==OPERATION_RUN and str(uuid.UUID(run))==run and uuid.UUID(run).version==4 and run!=FIXTURE_RUN,'DISTINCT_FROZEN_UUIDS')
 name='wa-p0c-'+run[:8]+'-customer-stale';out=TASK/('local-f0-customer-stale-predecessor-v1-'+run[:8]);directory=TASK/('local-f0-customer-stale-predecessor-v1-plan-'+run[:8])
 need(value['targets']==[{'name':name,'volume':name+'-data','kind':'ok'}] and value['evidence_directory']==str(out) and not out.exists() and value['image']==IMAGE and value['database']=='wa_p0c_rehearsal' and value['run_label']=='p0c-local-f0','CSP1_TARGET_PROFILE')
 need(value['storage']=={'container':name,'volume':name+'-data','network':'none','ports':[],'mounts':'exactPGDATAvolume+readonlybootstrapbind+root0700secret-tmpfs','extra_mounts':False,'host_namespaces':False,'privileged':False} and value['guarded_history_helper_sha256']==HISTORY_SHA,'CSP1_STORAGE_AND_HISTORY_PROFILE')
 cfg=value['customer_stale'];need(set(cfg)=={'fixtures_sha256','content_sha256','coordinator_sha256','external_files_sha256','fixture_run_id'} and cfg['fixtures_sha256']==FIXTURES_SHA and cfg['content_sha256']==CONTENT_SHA and cfg['fixture_run_id']==FIXTURE_RUN and cfg['coordinator_sha256']=='2a3cd4730408d294b767448b2d9f563d4f14937ca95edd1be232383c30591b3e','EXACT_CHILD_PACKET')
 external=mapping(cfg['external_files_sha256']);need(set(external)==set(EXTERNAL_FILES),'EXACT_FIVE_SET')
 packet=decoded(source(FIXTURES,FIXTURES_SHA));fixed=decoded(source(OWNED_ARCHIVE+'/fixed-catalog-source-map.json',FIXED_CATALOG_MAP_SHA));files=source_inventory(fixed,packet,external,require_reviews)
 need(value['prepared_source_file_inventory_sha256']==files and value['wrapper_sha256']==external[EXTERNAL_FILES[0]] and value['steps_sha256']==external[EXTERNAL_FILES[1]],'EXACT_PREPARED_SOURCE_AND_WRAPPER')
 if pinned:need(value['packet_files_sha256']==files and value['packet_sha256']==sha(''.join(n+'\0'+files[n]+'\n'for n in sorted(files)).encode()) and all(type(value[k])is str and re.fullmatch('[0-9a-f]{40}',value[k])for k in('source_commit','source_tree')) and value['pin_helper_sha256']==external[EXTERNAL_FILES[4]],'EXACT_PINNED_VIEW')
 else:need(value['packet_files_sha256']=={} and value['source_commit']==value['source_tree']==value['packet_sha256']=='TO_BE_PINNED','EXACT_UNPINNED_VIEW')
 need(set(value['migration_targets'])=={'ok'},'SINGLE_CANONICAL_SOURCE_TARGET');plan=value['migration_targets']['ok']
 need(plan['manifest_path']==str(directory/'ok-migration-manifest.json') and plan['source_snapshot']==str(directory/'source-ok') and plan['source_archive']==str(directory/'source-ok.tar.gz'),'FRESH_SOURCE_INPUT_PATHS')
 raw=Path(plan['manifest_path']).read_bytes();need(sha(raw)==plan['manifest_sha256'],'NESTED_MANIFEST_HASH');nested=decoded(raw)
 need(nested['run_id']==run and nested['target']=={'container_name':name,'volume_name':name+'-data','database':'wa_p0c_rehearsal','image':IMAGE,'network':'none','labels':{'workinants.rehearsal':'p0c-local-f0','workinants.rehearsal.run':run},'bootstrap_secret_host_path':str(out/'private/ok-bootstrap-password')},'NESTED_EXACT_TARGET')
 snapshot=Path(plan['source_snapshot']);need(not any(p.is_symlink()for p in snapshot.rglob('*')),'NO_SOURCE_LINKS')
 expected={MIGRATION,LOCK,SCHEMA,*RUNTIME,'prisma/foundation/history-manifest.json'};members={p.relative_to(snapshot).as_posix():p.read_bytes()for p in snapshot.rglob('*')if p.is_file()}
 need(set(members)==expected and {n:sha(b)for n,b in members.items()}==plan['source_files_sha256'],'EXACT_SOURCE_SEVEN')
 for n in expected-{'prisma/foundation/history-manifest.json'}:need(sha(members[n])==files[n],'SOURCE_SNAPSHOT_CURRENT_BINDING')
 history=decoded(members['prisma/foundation/history-manifest.json']);need(history['run_id']==run and history['run_manifest_sha256']==sha(raw) and history['source_sql_sha256']==SQL_SHA and history['database_contacted']is False and history['ledger_created_or_modified']is False,'FRESH_HISTORY_BINDING')
 archive=Path(plan['source_archive']).read_bytes();need(sha(archive)==plan['source_archive_sha256'],'SOURCE_ARCHIVE_SHA');seen=set()
 with tarfile.open(fileobj=io.BytesIO(archive),mode='r:gz')as tar:
  for m in tar:
   need(m.isfile() and m.name in expected and m.name not in seen and tar.extractfile(m).read()==members[m.name],'EXACT_SOURCE_ARCHIVE_MEMBER');seen.add(m.name)
 need(seen==expected,'EXACT_SOURCE_ARCHIVE_SEVEN');verify_tools(value['tool_archive'],value['tool_archive_sha256'],nested['tools'])
 return files

def prepare(baseline_path,baseline_sha,run_id=None):
 path=Path(baseline_path).resolve();need(path.is_relative_to(TASK) and not path.is_relative_to(ROOT) and sha(path.read_bytes())==baseline_sha,'REVIEWED_EXTERNAL_BASELINE')
 baseline=decoded(path.read_bytes());need(baseline['purpose']=='LOCAL_F0_NATIVE_CATALOG_REHEARSAL' and baseline['review_status']=='APPROVED_LOCAL_F0_NATIVE_CATALOG_ATTEMPT','CATALOG_BASELINE_ONLY')
 packet=decoded(source(FIXTURES,FIXTURES_SHA));need(packet['fixture_run_id']==FIXTURE_RUN and packet['content_sha256']==CONTENT_SHA and packet['status']=='NOT_RUN' and packet['worker_ACL_rows']==32,'FROZEN_CHILD_FIXTURE')
 external={n:sha((TASK/n).read_bytes())for n in EXTERNAL_FILES};inventory=source_inventory(baseline['packet_files_sha256'],packet,external,False)
 need(sha(source(MIGRATION))==sha(source(SQL))==SQL_SHA,'UNCHANGED_CANONICAL_INITIAL')
 run=OPERATION_RUN if run_id is None else run_id;need(run==OPERATION_RUN and run!=FIXTURE_RUN,'FIXED_DISTINCT_OPERATION_RUN')
 name='wa-p0c-'+run[:8]+'-customer-stale';directory=TASK/('local-f0-customer-stale-predecessor-v1-plan-'+run[:8]);out=TASK/('local-f0-customer-stale-predecessor-v1-'+run[:8]);need(not directory.exists() and not out.exists(),'EXCLUSIVE_FRESH_PLAN')
 old=baseline['migration_targets']['ok'];raw=Path(old['manifest_path']).read_bytes();need(sha(raw)==old['manifest_sha256'],'BASELINE_NESTED_HASH');nested=decoded(raw)
 nested['run_id']=run;nested['target'].update(container_name=name,volume_name=name+'-data',bootstrap_secret_host_path=str(out/'private/ok-bootstrap-password'));nested['target']['labels']={'workinants.rehearsal':'p0c-local-f0','workinants.rehearsal.run':run};nested['source']['runtime_files_sha256']={n:sha(source(n))for n in RUNTIME}
 verify_tools(baseline['tool_archive'],baseline['tool_archive_sha256'],nested['tools'])
 blobs={n:source(n,h)for n,h in inventory.items()};need(all(sha((TASK/n).read_bytes())==h and blobs[OWNED_ARCHIVE+'/'+n+'.txt']==(TASK/n).read_bytes()for n,h in external.items()),'EXACT_FIVE_BEFORE_COMPILE')
 generator={'__file__':str(ROOT/'scripts/prepare-customer-stale-predecessor-v1.py'),'__name__':'_pure_CSP1_reproduction'};exec(compile(blobs['scripts/prepare-customer-stale-predecessor-v1.py'],generator['__file__'],'exec'),generator)
 generated,again=generator['build'](ROOT,FIXTURE_RUN);need(again==packet and len(generated)==12 and all(blobs['review-output/customer-stale-predecessor-v1/'+n]==text.encode()for n,text in generated.items()),'EXACT_TWELVE_REPRODUCTION')
 snapshot={n:blobs[n]for n in(MIGRATION,LOCK,SCHEMA,*RUNTIME)};nested_raw=data(nested);helper={'__file__':str(ROOT/HISTORY_HELPER),'__name__':'_CSP1_source7_history'};exec(compile(blobs[HISTORY_HELPER],helper['__file__'],'exec'),helper)
 generated,history=helper['prepare_plan'](nested,nested_raw,snapshot[MIGRATION],snapshot[SCHEMA],{n:snapshot[n]for n in RUNTIME},SQL_SHA);need(set(generated)=={MIGRATION,LOCK} and all(generated[n]==snapshot[n]for n in generated),'EXACT_INITIAL_HISTORY');snapshot['prisma/foundation/history-manifest.json']=data(history)
 buffer=io.BytesIO()
 with gzip.GzipFile(fileobj=buffer,mode='wb',mtime=0)as zipped:
  with tarfile.open(fileobj=zipped,mode='w',format=tarfile.PAX_FORMAT)as tar:
   for n,content in sorted(snapshot.items()):m=tarfile.TarInfo(n);m.size=len(content);m.mode=0o600;m.mtime=0;tar.addfile(m,io.BytesIO(content))
 master=deepcopy(baseline);master.update(purpose='LOCAL_F0_CUSTOMER_STALE_PREDECESSOR_OWNED_V1_REHEARSAL',run_id=run,source_commit='TO_BE_PINNED',source_tree='TO_BE_PINNED',packet_sha256='TO_BE_PINNED',packet_files_sha256={},evidence_directory=str(out),targets=[{'name':name,'volume':name+'-data','kind':'ok'}],review_status='PENDING_OPERATIONAL_REVIEW',status='SOURCE_PREPARED_NOT_EXECUTED',wrapper_sha256=external[EXTERNAL_FILES[0]],steps_sha256=external[EXTERNAL_FILES[1]])
 archive=buffer.getvalue();master['migration_targets']={'ok':{'manifest_path':str(directory/'ok-migration-manifest.json'),'manifest_sha256':sha(nested_raw),'source_snapshot':str(directory/'source-ok'),'source_files_sha256':{n:sha(b)for n,b in snapshot.items()},'source_archive':str(directory/'source-ok.tar.gz'),'source_archive_sha256':sha(archive)}}
 master['customer_stale']={'fixtures_sha256':FIXTURES_SHA,'content_sha256':CONTENT_SHA,'coordinator_sha256':packet['source_files_sha256']['scripts/sql-review/run-customer-stale-predecessor-v1.py'],'external_files_sha256':external,'fixture_run_id':FIXTURE_RUN}
 master['prepared_source_file_inventory_sha256']=inventory;master['guarded_history_helper_sha256']=HISTORY_SHA
 master['storage']={'container':name,'volume':name+'-data','network':'none','ports':[],'mounts':'exactPGDATAvolume+readonlybootstrapbind+root0700secret-tmpfs','extra_mounts':False,'host_namespaces':False,'privileged':False}
 master['cleanup']='Only exact attempted CID/name/both labels and volume/name/CreatedAt. Delete only test-owned private/ok-bootstrap-password and empty private directory. Verify exact C1V/private absence; retain image and unrelated work.'
 master['allowed_catalog_operations']=['One genuine canonical initial5ae deploy and original-grantor finalization; native29089/oracle416/ledger22 before grants.','Actual SH004 Customer creation, only two Identity fixture toggles and exactly three explicit rollback predecessor controls; no Customer bypass, UPDATE COMMIT, winner/codec/Track/worker loop.','Read-only post native/oracle/ledger and complete42 excluding only exact four genuine issuer grants; maximum prospective stale_predecessor assertion, no automatic promotion.']
 master['execution_hold']='PENDING new source/resource/SafetySQL/binary reviews, Root admission/publication/current+committed pin and distinct literal/fresh live preflight. This source preparation cannot execute.'
 directory.mkdir();(directory/'ok-migration-manifest.json').write_bytes(nested_raw)
 for n,b in snapshot.items():p=directory/'source-ok'/n;p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(b)
 (directory/'source-ok.tar.gz').write_bytes(archive);(directory/'operation-manifest.json').write_bytes(data(master))
 return {'status':'SOURCE_PREPARED_NOT_EXECUTED','run_id':run,'fixture_run_id':FIXTURE_RUN,'operation_manifest':str(directory/'operation-manifest.json'),'manifest_sha256':sha(data(master)),'source_archive_sha256':sha(archive),'source_files':7,'database_contacted':False,'resources_created':False}

def main(argv=None):
 parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--prepare-plan',action='store_true');parser.add_argument('--baseline-manifest',type=Path);parser.add_argument('--baseline-sha256');parser.add_argument('--run-id');args=parser.parse_args(argv)
 try:
  need(args.prepare_plan and args.baseline_manifest and args.baseline_sha256,'EXPLICIT_REVIEWED_PREPARATION_REQUIRED');print(json.dumps(prepare(args.baseline_manifest,args.baseline_sha256,args.run_id)));return 0
 except BaseException as error:print(json.dumps({'status':'HELD','code':str(error) if isinstance(error,Refused) else 'SOURCE_PREPARATION_REFUSED','raw_output_discarded':True}));return 1

if __name__=='__main__':raise SystemExit(main())
