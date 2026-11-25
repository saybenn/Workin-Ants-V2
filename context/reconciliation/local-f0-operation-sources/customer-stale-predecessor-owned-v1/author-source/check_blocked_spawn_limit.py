import hashlib,json,pathlib,runpy,subprocess,sys,threading,time
from unittest.mock import patch
sys.dont_write_bytecode=True
A=pathlib.Path(r'C:\Users\elijr\.codex\visualizations\2026\11\09\01a1be05-aeb3-7f42-b0f4-6c5e46dc669f\customer-stale-predecessor-owned-v1-private-20261123')
def audit(event,args):
 if event in('subprocess.Popen','os.system','os.posix_spawn','os.spawn','socket.connect','socket.bind','socket.getaddrinfo'):raise AssertionError('REAL_EXTERNAL_BOUNDARY_FORBIDDEN')
sys.addaudithook(audit)
core=runpy.run_path(str(A/'execute_local_f0_customer_stale_predecessor_v1_20261120.py'));core['initialize'](A/'local-f0-customer-stale-predecessor-v1-plan-73292a8f/operation-manifest.json');checker=runpy.run_path(str(A/'check_local_f0_customer_stale_predecessor_v1_operation.py'));entered=threading.Event();release=threading.Event();finished=threading.Event();original_clock=time.monotonic;offset=[0];outcomes=[];created=[]
def clock():return original_clock()+offset[0]
def popen(args,**kwargs):
 entered.set();release.wait(3);p=checker['ByteProcess'](args,lambda a,b:subprocess.CompletedProcess(a,0,b'',b''));created.append(p);return p
def work():
 try:core['binary_process'](['MOCK_ONLY'],b'x',1);outcomes.append('UNEXPECTED_SUCCESS')
 except core['Stop']as e:outcomes.append(e.code)
 finally:finished.set()
with patch.object(subprocess,'Popen',side_effect=popen),patch.object(time,'monotonic',side_effect=clock):
 worker=threading.Thread(target=work);worker.start();assert entered.wait(1);assert worker.is_alive()and not finished.is_set();offset[0]=2;release.set();worker.join(timeout=3)
assert not worker.is_alive()and outcomes==['PROCESS_DEADLINE_EXCEEDED']and all(p.poll()is not None for p in created)
report={'schema':'workinants.CSP1-blocked-spawn-source-limit-check.v1','status':'PASS_LIMIT_RECORDED','blocked_spawn_requires_return_before_deadline_is_observed':True,'late_return_rejects_success':True,'modeled_process_known_closed_after_release':True,'preemptive_spawn_cancellation_proven':False,'whole_graph_hard_deadline_claimed':False,'new_Core_sha256':hashlib.sha256((A/'execute_local_f0_customer_stale_predecessor_v1_20261120.py').read_bytes()).hexdigest(),'all_external_boundaries':'MOCKED_OR_AUDIT_FORBIDDEN','runtime':'NOT_RUN','Posture':'D'}
out=A/'author-checks/blocked-spawn-limit.json';assert not out.exists();out.write_text(json.dumps(report,indent=2)+'\n',encoding='utf8');print(json.dumps(report))
