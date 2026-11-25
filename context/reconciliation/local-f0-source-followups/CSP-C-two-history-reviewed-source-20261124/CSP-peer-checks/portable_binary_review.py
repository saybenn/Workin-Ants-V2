from pathlib import Path
import sys,runpy,json,hashlib,unittest,time,traceback,subprocess
from contextlib import ExitStack
from unittest.mock import patch
sys.dont_write_bytecode=True
R=Path(__file__).resolve().parent;Q=R/'exclusive';edges=[]
def audit(e,a):
 if e.startswith(('subprocess.','socket.'))or e in('os.system','os.posix_spawn','os.spawn'):edges.append(e);raise AssertionError('UNMOCKED_BOUNDARY_FORBIDDEN')
sys.addaudithook(audit)
M=runpy.run_path(str(Q/'check_local_f0_customer_stale_predecessor_v1_operation.py'));guard=ExitStack()
for n in('run','Popen','call','check_call','check_output'):guard.enter_context(patch.object(subprocess,n,side_effect=AssertionError('REAL_PROCESS_FORBIDDEN')))
start=time.monotonic();fixture=M['Fixture']()
def real_initialized_core(self):
 core=runpy.run_path(str(fixture.task/M['FIVE'][0]));core['initialize'](fixture.path);return core
M['BinaryTransport'].core=real_initialized_core
class Result(unittest.TestResult):
 def __init__(self):super().__init__();self.rows=[]
 def addSuccess(self,t):super().addSuccess(t);self.rows.append({'method':t.id(),'status':'PASS'});print(json.dumps(self.rows[-1]),flush=True)
 def err(self,t,e,s):self.rows.append({'method':t.id(),'status':s,'exception_type':e[0].__name__,'frames':[{'file':Path(f.filename).name,'line':f.lineno,'function':f.name}for f in traceback.extract_tb(e[2])]});print(json.dumps(self.rows[-1]),flush=True)
 def addError(self,t,e):super().addError(t,e);self.err(t,e,'ERROR')
 def addFailure(self,t,e):super().addFailure(t,e);self.err(t,e,'FAIL')
 def addSubTest(self,t,st,e):
  super().addSubTest(t,st,e)
  if e:self.err(t,e,'SUBTEST_FAIL')
r=Result()
try:unittest.TestSuite(M['BinaryTransport'](n)for n in sorted(M['BinaryTransport'].__dict__)if n.startswith('test_')).run(r)
finally:fixture.close();guard.close()
report={'schema':'workinants.CSP1-C-independent-portable-binary-checks.v1','reviewer':'/root/lease_v2_code_review','status':'PASS'if r.wasSuccessful()else'CHECK_FAILURES_PRESERVED','methods':r.testsRun,'results':r.rows,'seconds':round(time.monotonic()-start,3),'support_adaptation':'Only checker BinaryTransport.core fixture helper now loads exact source bytes copied by the actual Fixture constructor and calls actual initialize on its freshly prepared/pinned UNIT-only manifest. No production function/global/proof API changed. Original frozen preprepared manifest remains byte-exact.','supersedes_support_execution_only':'light-checks eight initialize-confinement refusals; those original results remain preserved.','operator_sources_sha256':{n:hashlib.sha256((Q/n).read_bytes()).hexdigest()for n in M['FIVE']},'forbidden_edges_attempted':edges,'runtime':'NOT_RUN','Posture':'D'}
raw=(json.dumps(report,indent=2)+'\n').encode();p=R/'portable-binary-checks.json';p.open('xb').write(raw);print(json.dumps({'status':report['status'],'receipt':str(p),'sha256':hashlib.sha256(raw).hexdigest(),'methods':r.testsRun}),flush=True);raise SystemExit(0 if r.wasSuccessful()else 1)
