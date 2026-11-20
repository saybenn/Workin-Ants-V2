from contextlib import redirect_stdout
from pathlib import Path
import hashlib,io,json,runpy,sys,time,unittest
T=Path(__file__).resolve().parent;R=T/'workinants-correction-pass';sys.dont_write_bytecode=True
def audit(event,args):
    if event in ('subprocess.Popen','os.system','os.posix_spawn','socket.connect','socket.bind','socket.getaddrinfo'):raise AssertionError('ACTUAL_PROCESS_NETWORK_FORBIDDEN')
sys.addaudithook(audit)
suite=unittest.TestSuite();counts={}
for filename,classname in (('check_restore_bound_evidence_v3_focused_20261119.py','BoundEvidenceTests'),('check_restore_bound_evidence_v3_source_gates_20261119.py','RestoreBoundEvidenceSourceGateTests')):
    n=runpy.run_path(str(T/filename));loaded=unittest.defaultTestLoader.loadTestsFromTestCase(n[classname]);counts[classname]=loaded.countTestCases();suite.addTests(loaded)
log=io.StringIO();stdout=io.StringIO();start=time.perf_counter()
with redirect_stdout(stdout):result=unittest.TextTestRunner(stream=log,verbosity=2).run(suite)
record={'schema':'workinants.restore-bound-evidence-v3-bounded-source-checks.v1','status':'PASS' if result.wasSuccessful() else 'FAIL','tests':result.testsRun,'counts':counts,'seconds':round(time.perf_counter()-start,3),'failures':[{'test':str(t),'detail':s} for t,s in result.errors+result.failures],'log':log.getvalue(),'runtime':'NOT_RUN','actual_process_network':'FORBIDDEN_BY_AUDIT','active_Native_OUT_reads':'NONE','process_API':'Actual WorkerSession methods; mocked Popen pipes and run command boundaries. Actual Core initialize/launch, required closure/finalizer/main/cleanup methods.'}
with (T/'restore_bound_evidence_v3_bounded_checks_second_20261119.json').open('x',encoding='utf8') as f:json.dump(record,f,indent=2);f.write('\n')
print(json.dumps({k:v for k,v in record.items() if k not in ('log','failures')}));print(json.dumps(record['failures'],indent=2));sys.exit(0 if result.wasSuccessful() else 1)
