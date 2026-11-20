from pathlib import Path
import io,json,runpy,sys,time,unittest
T=Path(__file__).resolve().parent;R=T/'workinants-correction-pass';sys.dont_write_bytecode=True
def audit(event,args):
    if event in ('subprocess.Popen','os.system','os.posix_spawn','socket.connect','socket.bind','socket.getaddrinfo'):raise AssertionError('REAL_PROCESS_NETWORK_FORBIDDEN')
    if event=='open':
        path,mode,flags=args
        if isinstance(path,(str,bytes)) and ((isinstance(mode,str) and any(c in mode for c in 'wax+')) or isinstance(flags,int) and flags&0x3):
            try:inside=Path(path).resolve().is_relative_to(R.resolve())
            except (ValueError,OSError):inside=False
            if inside:raise AssertionError('ACTUAL_ROOT_WRITE_FORBIDDEN_DURING_TESTS')
sys.addaudithook(audit)
paths=(R/'scripts/test_install_independent_review_protocol_v1.py',R/'scripts/sql-review/test_watch_install_independent_review_v2.py',R/'scripts/sql-review/test_install_ledger_proof_v3.py',R/'scripts/check-install-control-rehearsal-v3.py',T/'check_local_f0_install_controls_operation_review_ready_v3.py',T/'check_install_review_ready_v3_source_preservation_20261119.py')
suite=unittest.TestSuite();counts={}
for path in paths:
    n=runpy.run_path(str(path));loaded=unittest.defaultTestLoader.loadTestsFromModule(type('OfflineModule',(),n));counts[path.name]=loaded.countTestCases();suite.addTests(loaded)
n=runpy.run_path(str(T/'check_install_review_ready_v3_safety_composition_20261119.py'));loaded=unittest.defaultTestLoader.loadTestsFromTestCase(n['ActualInstallSafetyTests']);counts['actual_new_Core_Steps_SafetySQL']=loaded.countTestCases();suite.addTests(loaded)
stream=io.StringIO();start=time.perf_counter();result=unittest.TextTestRunner(stream=stream,verbosity=2).run(suite);record={'schema':'workinants.install-v3-final-source-checks.v1','status':'PASS' if result.wasSuccessful() else 'FAIL','tests':result.testsRun,'counts':counts,'seconds':round(time.perf_counter()-start,3),'failures':[{'test':str(t),'detail':s} for t,s in result.failures+result.errors],'log':stream.getvalue(),'runtime':'NOT_RUN','actual_process_network':'FORBIDDEN_BY_AUDIT','actual_Root_writes':'FORBIDDEN_BY_AUDIT'}
with (T/'install_review_ready_v3_final_checks_v2_20261119.json').open('x',encoding='utf8') as f:json.dump(record,f,indent=2);f.write('\n')
print(json.dumps({k:v for k,v in record.items() if k not in ('log','failures')}));print(json.dumps(record['failures'],indent=2));sys.exit(0 if result.wasSuccessful() else 1)
