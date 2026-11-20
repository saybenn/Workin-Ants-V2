"""Actual frozen Worker/CTX Session integration; only process/clock boundaries are modeled."""
from pathlib import Path
from copy import deepcopy
import inspect,io,json,queue,re,runpy,subprocess,threading,time,types,unittest
from unittest.mock import patch
T=Path(__file__).resolve().parent;R=T/'workinants-correction-pass'
B=runpy.run_path(str(T/'check_local_f0_worker_recovery_owned_v1_operation.py'))
W=runpy.run_path(str(R/'scripts/check-worker-recovery-control-coordinator.py'))
P=W['P'];CID=B['CID']
class Pipe:
 def __init__(self):self.q=queue.Queue();self.saved=''
 def emit(self,value):self.q.put(value)
 def readline(self,n=-1):return self.q.get()
 def read(self,n=-1):return self.q.get()
 def end(self):self.q.put('')
class Input:
 def __init__(self,process):self.p=process;self.text=''
 def write(self,text):self.text+=text
 def flush(self):
  text=self.text;self.text='';self.p.execute(text)
 def close(self):self.flush()
class Process:
 def __init__(self,vm,role,c):
  self.vm=vm;self.model=vm.session(role,c);self.returncode=None;self.stdout=Pipe();self.stderr=Pipe();self.stdin=Input(self);self.ended=False
 def poll(self):return self.returncode
 def wait(self,timeout=None):
  if self.returncode is None:raise subprocess.TimeoutExpired('MOCK_UNENDED',timeout)
  return self.returncode
 def finish(self,code):
  if not self.ended:self.ended=True;self.returncode=code;self.model.closed=True;self.stdout.end();self.stderr.end()
 def terminate(self):self.finish(0)
 def kill(self):self.finish(0)
 def execute(self,text):
  if '\\q' in text:self.model.close();self.finish(self.model.process.returncode);return
  found=re.search(r"\nSELECT '(WA_CTX01_ACK\|[0-9a-f]+)';\n$",text)
  if not found:raise AssertionError('ACTUAL_SESSION_ACK_SQL_SHAPE')
  sql=text[:found.start()];rows=[];ack=True;error=''
  if sql.startswith('BEGIN ISOLATION LEVEL '):self.model.begin(re.search(r'BEGIN ISOLATION LEVEL ([A-Z ]+);',sql)[1].lower())
  elif "'login',session_user" in sql and 'pg_backend_pid()::text' in sql:
   tuple_=self.model.capture();rows=['WA_CTX01_TUPLE|'+json.dumps(tuple_)]
  else:rows,ack,error=self.model.call(sql)
  for row in rows:self.stdout.emit(row+'\n')
  if error:self.stderr.emit(error)
  if ack:self.stdout.emit(found[1]+'\n')
  else:self.finish(self.model.process.returncode)
class Proxy:
 def __init__(self,c):self.c=c
 def __getattr__(self,key):return W['M']['compiled']((R/'scripts/sql-review/run-context-control-rehearsal.py').read_bytes(),'scripts/sql-review/run-context-control-rehearsal.py')['GRANT_COLUMNS']if key=='context_columns'else getattr(self.c,key)
class VM(W['Transport']):
 def session(self,role,c):
  self.actual=c;value=super().session(role,Proxy(c));self.coordinator=Proxy(c);return value
 def popen(self,args,**kwargs):
  frame=inspect.currentframe().f_back
  while frame and not(type(frame.f_locals.get('self')).__name__=='Session'and hasattr(frame.f_locals['self'],'coordinator')):frame=frame.f_back
  if frame is None:raise AssertionError('ACTUAL_CTX_SESSION_CONSTRUCTOR_REQUIRED')
  c=frame.f_locals['self'].coordinator;role=args[args.index('-U')+1];self.process_calls.append((role,tuple(args)));return Process(self,role,c)
 def raw(self,args,**options):
  frame=inspect.currentframe().f_back
  while frame:
   candidate=frame.f_locals.get('self')
   if candidate is not None and type(candidate).__name__=='Coordinator'and hasattr(candidate,'instances'):self.coordinator=Proxy(candidate);break
   frame=frame.f_back
  text=options.get('input','');role=args[args.index('-U')+1]if '-U'in args else None
  if role:
   if 'PGPASSWORD'in args:return types.SimpleNamespace(returncode=2,stdout='',stderr='FATAL:  password authentication failed for user "'+role+'"\n')
   if 'pg_hba_file_rules'in text:return types.SimpleNamespace(returncode=0,stdout=json.dumps([{'rule_number':i+1,'type':'host','database':['all'],'user_name':['all'],'address':a,'netmask':m,'auth_method':'scram-sha-256','error':None}for i,(a,m)in enumerate([('127.0.0.1','255.255.255.255'),('::1','ffff:ffff:ffff:ffff:ffff:ffff:ffff:ffff')])]),stderr='')
   if 'FROM pg_authid'in text:return types.SimpleNamespace(returncode=0,stdout=json.dumps(dict.fromkeys(('postgres','wa_migrator','wa_app_runtime','wa_worker','wa_context_issuer','wa_identity_service_authority'),True)),stderr='')
   if "'auth',system_user"in text:return types.SimpleNamespace(returncode=0,stdout=json.dumps({'login':role,'auth':'scram-sha-256:'+role,'database':'wa_p0c_rehearsal','client':'127.0.0.1','server':'127.0.0.1'}),stderr='')
   if text.startswith('SELECT count(*) FROM pg_stat_activity WHERE pid='):
    pid=re.search(r'WHERE pid=([0-9]+)',text)[1];return types.SimpleNamespace(returncode=0,stdout=str(sum(not s.closed and getattr(s,'backend',{}).get('pid')==pid for s in self.sessions)),stderr='')
   return super().raw(args,**options)
  target=self.target['target'];image=target['image'];digest=image.split('@')[1]
  if args[3:5]==['context','inspect']:value={'Name':'desktop-linux','Endpoints':{'docker':{'Host':'npipe:////./pipe/dockerDesktopLinuxEngine'}}}
  elif args[3:5]==['volume','inspect']:value={'Name':target['volume_name'],'Driver':'local','Options':{},'Scope':'local','Labels':target['labels']}
  elif args[3:5]==['image','inspect']:value={'Id':digest,'Os':'linux','Architecture':'amd64','RepoDigests':[image]}
  elif args[3]=='inspect':value={'Id':CID,'Name':'/'+target['container_name'],'Config':{'Image':image,'Labels':target['labels']},'Image':digest,'Platform':'linux','State':{'Running':True},'HostConfig':{'NetworkMode':'none','PortBindings':{},'Privileged':False,'PidMode':'','IpcMode':'private','Devices':[],'CapAdd':[],'Tmpfs':{'/run/wa-secrets':'rw,nosuid,noexec,nodev,mode=0700'}},'NetworkSettings':{'Ports':{'5432/tcp':None}},'Mounts':[{'Type':'volume','Name':target['volume_name'],'Destination':'/var/lib/postgresql/data','RW':True},{'Type':'bind','Source':target['bootstrap_secret_host_path'],'Destination':'/run/bootstrap-password','RW':False}]}
  else:raise AssertionError('UNKNOWN_PROCESS_BOUNDARY')
  return types.SimpleNamespace(returncode=0,stdout=json.dumps([value]),stderr='')
class ActualTransportTests(unittest.TestCase):
 setUp=B['WorkerOperationTests'].setUp;prepared=B['WorkerOperationTests'].prepared
 def fixture(self):
  _,manifest=self.prepared();core=runpy.run_path(str(T/'execute_local_f0_worker_recovery_owned_v1_20261119.py'));path=self.directory/'actual.json';path.write_text(json.dumps(manifest));core['initialize'](path);n=core['initialize'].__globals__;exec(compile((T/'local_f0_worker_recovery_owned_v1_operation_steps.py').read_bytes(),'steps','exec'),n);n['OUT'].mkdir();n['MANIFEST']['packet_files_sha256']=manifest['prepared_source_file_inventory_sha256'];n['COMMIT']='b'*40;n['TREE']='c'*40;n['PACKET']=P.sha(''.join(k+'\0'+v+'\n'for k,v in sorted(n['MANIFEST']['packet_files_sha256'].items())).encode());n['MANIFEST']['packet_sha256']=n['PACKET'];n['verify_common_packet']=lambda:None;n['verify_worker_recovery_packet']()
  native=json.loads((R/'context/reconciliation/local-f0-run-assets/b9703d7-native-catalog-23bd8979/native-before.json').read_bytes());native.update(server_version_num=170011)
  comparison={'format':'workinants.catalog-comparison.v1','status':'PASS','source_expected_sha256':n['EXPECTED_SHA'],'native_snapshot_sha256':P.digest(native),'findings':[],'check_counts':{'PASS':29089}}
  (n['OUT']/'native-before.json').write_text(json.dumps(native));(n['OUT']/'catalog-comparison.json').write_text(json.dumps(comparison));n['report'].update(catalog_comparison=comparison,ledger_comparison={'status':'PASS','checks':[{'status':'PASS'}]*22},qualified_native_snapshot_sha256=P.digest(native));n['report']['steps']['CATALOG-ORACLE']='PASS_ROLLBACK_OBSERVED_NOT_WHOLE_CASE';n['report']['targets'][n['TARGETS'][0]['name']]={'finalization':'PASS'};n['finalized'].add(n['TARGETS'][0]['name']);n['created_containers'][n['TARGETS'][0]['name']]=CID;n['WORKER_INSTALL'].update(attestation_sha256='a'*64,registration={'synthetic':'FIRST_INSTALL_PROOF'});n['inspect_owner']=lambda*a,**k:None;n['closed_backends']=lambda*a,**k:None;n['worker_after_proofs']=lambda*a,**k:None
  self.n=n;vm=VM(n['WORKER_FIXTURES']);vm.process_calls=[];vm.target=json.loads(n['read_target_manifest'](manifest['migration_targets']['ok']));self.vm=vm;return n,vm
 def test_real_outer_component_actual_loader_coordinator_CTX_session_processes(self):
  n,vm=self.fixture()
  try:
   with patch.object(subprocess,'run',side_effect=vm.raw),patch.object(subprocess,'Popen',side_effect=vm.popen),patch.object(time,'monotonic',side_effect=vm.clock),patch.object(time,'sleep',side_effect=vm.sleep):n['worker_recovery_experiment']()
  except BaseException:
   value=json.loads((n['OUT']/'worker-recovery-component/worker-recovery-results.json').read_bytes());print('SAFE_MOCK_FAILURE',value['current_stage'],value['unexpected'],len(value['results']),len(vm.process_calls));raise
  value=json.loads((n['OUT']/'worker-recovery-component/worker-recovery-results.json').read_bytes());self.assertEqual(len(value['results']),21);self.assertTrue(value['fixture_owner_bypass_restored']);self.assertTrue(all(s.closed for s in vm.sessions));self.assertGreater(len(vm.process_calls),50);self.assertEqual(n['report']['steps']['WORKER-RECOVERY-COMPONENT'],'PASS_FINITE_PREPARED_SQL_ONLY');self.assertNotIn(W['CANARY'],json.dumps(value));self.assertEqual(len(value['operations']),295)
  (T/'worker_owned_v1_MOCK_ONLY_component_result_20261119.json').write_text(json.dumps(value,indent=2)+'\n')
  (self.directory/'modeled-success.json').write_text(json.dumps(value));self.value=value
if __name__=='__main__':unittest.main(verbosity=2)
