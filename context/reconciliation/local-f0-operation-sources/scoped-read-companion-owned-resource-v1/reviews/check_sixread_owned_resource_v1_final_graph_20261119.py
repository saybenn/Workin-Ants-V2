"""Final staged archive/current+committed/full verifier check; no runtime."""
from pathlib import Path
from contextlib import redirect_stdout
import hashlib,io,json,runpy,subprocess,sys,tempfile,time
from unittest.mock import patch
TASK=Path(__file__).resolve().parent;ROOT=TASK/'workinants-correction-pass'
def sha(raw):return hashlib.sha256(raw).hexdigest()
before={p.name:sha(p.read_bytes())for p in TASK.glob('*scoped_reads_owned_resource_v1*.py')}
helper=runpy.run_path(str(TASK/'check_sixread_owned_resource_v1_preparer_pinner_20261119.py'));sys.addaudithook(helper['audit']);started=time.monotonic()
git_helper=runpy.run_path(str(TASK/'check_sixread_owned_resource_v1_source_admission_20261119.py'))['runtime_git']
with tempfile.TemporaryDirectory(prefix='sixread-owned-final-graph-',dir=TASK)as temp:
 fixture=helper['clone_fixture'](Path(temp)/'clone');path,prepared=helper['prepare_fixture'](fixture,'95763468-9cad-4bee-beb4-1733224a51fb');pending=json.loads(path.read_bytes())
 assert pending['review_status']=='PENDING_OPERATIONAL_REVIEW'and pending['source_commit']=='TO_BE_PINNED'and not Path(pending['evidence_directory']).exists()
 with patch.object(subprocess,'run',side_effect=AssertionError('PENDING_MUST_NOT_CONTACT_GIT')):
  try:fixture['pin']['pin'](path)
  except fixture['pin']['Held']as error:assert str(error)=='SAFETY_SQL_REVIEW_REQUIRED'
  else:raise AssertionError('LIVE_PENDING_GATE_NOT_ENFORCED')
 helper['approve_clone'](fixture);path,prepared=helper['prepare_fixture'](fixture,'96763468-9cad-4bee-beb4-1733224a51fb');world=helper['GitWorld'](fixture['ROOT'])
 with patch.object(subprocess,'run',side_effect=world.run):pinned=fixture['pin']['pin'](path)
 value=json.loads(path.read_bytes());value['review_status']='APPROVED_LOCAL_F0_SCOPED_READ_COMPANION_OWNED_RESOURCE_V1_ATTEMPT';path.write_bytes(helper['encoded'](value))
 core=fixture['TASK']/'execute_local_f0_scoped_reads_owned_resource_v1_20261119.py';steps=fixture['TASK']/'local_f0_scoped_reads_owned_resource_v1_operation_steps.py';namespace=runpy.run_path(str(core))['launch'].__globals__;namespace['initialize'](path);exec(compile(steps.read_bytes(),str(steps),'exec'),namespace);namespace['OUT'].mkdir()
 with patch.object(subprocess,'run',side_effect=lambda args,**options:git_helper(fixture['ROOT'],args,**options)),redirect_stdout(io.StringIO()):namespace['verify_scoped_read_packet']()
 assert len(namespace['HELPERS'])==7 and namespace['SCOPED_STATE']['tools_verified_before_compile']is True
 live=json.loads((ROOT/fixture['prepare']['OWNED_VALIDATION']).read_bytes());assert all(live[key]['decision']=='PENDING'for key in('independent_safety_sql_review','independent_owned_resource_review'))
 result={'schema':'workinants.sixread-owned-resource-final-sourcegraph-author-check.v1','status':'PASS_SOURCE_ONLY_NOT_INDEPENDENT_APPROVAL','checks':3,'checks_detail':['Actual preparation with both source gates PENDING and pinner refuses before Git','Clone-only approval projection and actual current+committed full packet pin via read-only Git transport mock','Actual Core.initialize/whole verifier/catalog16/helper7/source7/tool10300 on final staged archive'], 'seconds':time.monotonic()-started,'operator_sources_sha256':fixture['external'],'archive_files':len(live['archive_files_sha256']),'prepared_inventory':len(value['packet_files_sha256']),'pinned_packet_sha256':value['packet_sha256'],'live_validation_sha256':sha((ROOT/fixture['prepare']['OWNED_VALIDATION']).read_bytes()),'source_gates':{key:live[key]['decision']for key in('independent_safety_sql_review','independent_owned_resource_review')},'runtime':'NOT_RUN','actual_Git_Docker_DB_network':False}
after={p.name:sha(p.read_bytes())for p in TASK.glob('*scoped_reads_owned_resource_v1*.py')};assert before==after
target=TASK/'six_read_owned_resource_v1_final_source_graph_author_probe_20261119.json'
with target.open('xb')as handle:handle.write(helper['encoded'](result))
print(json.dumps({'path':str(target),'sha256':sha(target.read_bytes()),'checks':3,'seconds':result['seconds'],'archive':result['archive_files'],'inventory':result['prepared_inventory']}))
