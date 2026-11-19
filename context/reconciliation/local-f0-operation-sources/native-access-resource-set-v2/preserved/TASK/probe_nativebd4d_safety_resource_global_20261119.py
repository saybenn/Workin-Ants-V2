"""Actual initialized Native namespace, process-only mocks; never Docker/DB/Git."""
from pathlib import Path
import contextlib,datetime,hashlib,io,json,subprocess,sys
from unittest import mock
TASK=Path(__file__).resolve().parent;ROOT=TASK/'workinants-correction-pass'
core=TASK/'execute_local_f0_native_access_20261119_safety_sql_v1.py'
steps=TASK/'local_f0_native_access_operation_steps_safety_sql_v1.py'
assert hashlib.sha256(core.read_bytes()).hexdigest()=='82ff221e2b740ffeac248474c84bfab80253c34e3234a6a2cf584e6162397574'
assert hashlib.sha256(steps.read_bytes()).hexdigest()=='991210f073adecb1ca0b9dda208f56fba218feb56ab3d6c18db16b437ad8072a'
manifest=TASK/'local-f0-native-access-plan-bd4d6720/operation-manifest.json'
assert hashlib.sha256(manifest.read_bytes()).hexdigest()=='bd1e761a4a669035f91b5a3a0e1b129ab399589c306bad5562df03691c070119'
forbidden=[]
def no_process(*args,**kwargs):forbidden.append(True);raise AssertionError('REAL_PROCESS_FORBIDDEN')
rows=[]
with mock.patch.object(subprocess,'run',side_effect=no_process),mock.patch.object(subprocess,'Popen',side_effect=no_process),mock.patch.object(subprocess,'check_output',side_effect=no_process),mock.patch.object(sys,'argv',[str(core),str(manifest)]):
 def initialized():
  ns={'__name__':'_native_actual_initialization_probe','__file__':str(core)}
  exec(compile(core.read_bytes(),str(core),'exec'),ns)
  assert 'RESOURCE_CONTAINERS'not in ns
  name=ns['TARGETS'][0]['name'];ns['created_containers'][name]='a'*64
  ns['report']['targets'][name]={'finalization':'NOT_RUN'}
  ns['save']=lambda:None
  ns['event']=lambda *a,**k:None
  ns['best_effort_save']=lambda:True
  ns['best_effort_event']=lambda *a,**k:True
  return ns,name
 for action in ('DIRECT_REQUIRED_CLOSURE','ACTUAL_CATALOG_QUERY_COMPOSITION','ACTUAL_FINALIZER'):
  ns,name=initialized();calls=[]
  def command(args,input=None,timeout=None):
   calls.append({'postgres_transport':'-U'in args and args[args.index('-U')+1]=='postgres','input_sha256':hashlib.sha256((input or '').encode()).hexdigest()})
   return subprocess.CompletedProcess(args,0,'','')
  ns['command']=command
  try:
   if action=='DIRECT_REQUIRED_CLOSURE':ns['_required_safety_sql'](name,'GLOBAL_BACKENDS')
   elif action=='ACTUAL_CATALOG_QUERY_COMPOSITION':
    payload=(ROOT/'review-output/native-table-denials-v2/provider-role-simulation-before-migrate.sql').read_text()
    ns['run_catalog_query'](name,payload,'PROVIDER_ROLE_SIMULATION')
   else:ns['finalize'](name)
  except NameError as error:
   assert error.name=='RESOURCE_CONTAINERS'
   rows.append({'action':action,'initialized_namespace_lacks_required_global':True,'exception_class':'NameError','missing_name_exact_allowlisted_RESOURCE_CONTAINERS':True,'mocked_transport_calls':len(calls),'required_safety_query_dispatched':False})
  else:raise AssertionError('OLD_MISSING_GLOBAL_NOT_REPRODUCED')
 ns,name=initialized();ns['RESOURCE_CONTAINERS']=tuple(t['name']for t in ns['TARGETS']);calls=[]
 def fixed_command(args,input=None,timeout=None):
  assert '-U'in args and args[args.index('-U')+1]=='postgres' and 'a'*64 in args
  selectors=[s for s in ('GLOBAL_BACKENDS','FINALIZATION_BACKENDS','ORIGINAL_GRANTOR_FINALIZATION','FINALIZATION_RESULT')if ns['_required_safety_text'](s)==input]
  assert len(selectors)==1
  selector=selectors[0];calls.append(selector)
  if selector in ('GLOBAL_BACKENDS','FINALIZATION_BACKENDS'):value={'migrator':0,'other_client_backends':0}
  elif selector=='FINALIZATION_RESULT':value={'grantor':'postgres','auth':'scram-sha-256:postgres','remaining_memberships':0,'leaf_create':{k:False for k in ns['LEAVES']},'active_install_connections':0}
  else:value=None
  return subprocess.CompletedProcess(args,0,''if value is None else json.dumps(value)+'\n','')
 ns['command']=fixed_command
 assert ns['closed_backends'](name,'OFFLINE_BOUNDARY_PROBE')['all_other_client_backends_absent']is True
 ns['finalize'](name);assert name in ns['finalized']
 assert calls==['GLOBAL_BACKENDS','FINALIZATION_BACKENDS','ORIGINAL_GRANTOR_FINALIZATION','FINALIZATION_RESULT']
 assert not forbidden
record={'schema':'workinants.nativebd4d-source-global-offline-reproduction.v1','recorded_at_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'source_core_sha256':hashlib.sha256(core.read_bytes()).hexdigest(),'source_steps_sha256':hashlib.sha256(steps.read_bytes()).hexdigest(),'actual_initialization':'Entire exact Core with exact Steps via unchanged source loader; __name__ dormant, real process APIs forbidden, only command/persistence boundary mocked afterward','old_source_reproductions':rows,'hypothetical_in_memory_declaration_only_control':{'status':'PASS_MOCKED_FIXED_CLOSURE_AND_FINALIZATION','required_selectors':calls,'files_changed':False,'new_operational_source_authored':False},'actual_historical_exception':'Not retained; proven initialized-source defect is consistent with observed provider closure/finalizer stops, complete historical exception cause remains unobserved','Docker_DB_SQL_Git_network':'NOT_RUN_ALL_BOUNDARIES_MOCKED','forbidden_process_attempts':len(forbidden),'status':'PASS_PROVEN_SOURCE_MISSING_GLOBAL_AND_NARROW_MOCKED_CONTROL'}
raw=(json.dumps(record,indent=2)+'\n').encode();path=TASK/'nativebd4d_safety_resource_global_source_probe_20261119.json'
with path.open('xb')as f:f.write(raw)
print(json.dumps({'path':str(path),'sha256':hashlib.sha256(raw).hexdigest(),'status':record['status']}))
