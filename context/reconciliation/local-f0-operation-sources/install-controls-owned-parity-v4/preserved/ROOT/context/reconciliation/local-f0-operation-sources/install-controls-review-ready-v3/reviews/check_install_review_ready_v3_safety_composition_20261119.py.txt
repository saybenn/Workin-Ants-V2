"""Actual new INSTALL Core+Steps command-only composition; no helper injection."""
from pathlib import Path
import ast,hashlib,inspect,io,json,runpy,sys,textwrap,time,unittest
T=Path(__file__).resolve().parent
def audit(event,args):
    if event in ('subprocess.Popen','os.system','os.posix_spawn','socket.connect','socket.bind','socket.getaddrinfo'):raise AssertionError('REAL_PROCESS_NETWORK_FORBIDDEN')
sys.addaudithook(audit)
B=runpy.run_path(str(T/'check_derived_safety_sql_v1_composed_20261119.py'));Old=B['DerivedSafetySQLCompositionTests'];scope=Old.fixture.__globals__;scope['PRES']={'families_sha256':{'install':{'execute_local_f0_install_controls_20261119_review_ready_v3.py':'','local_f0_install_controls_operation_steps_review_ready_v3.py':''}}}
class ActualInstallSafetyTests(unittest.TestCase):
    setUp=Old.setUp;fixture=Old.fixture;writes_fail=Old.writes_fail;selectors=Old.selectors;safe=Old.safe
skip={'test_all_actual_runtime_gates_reject_pending_new_family_review_before_command','test_source_recipe_preservation_and_foreign_profile_target_selector_are_closed','test_owner_original_stop_is_preserved_before_its_distinct_failure_bookkeeping'}
for name,method in Old.__dict__.items():
    if name.startswith('test_') and name not in skip:
        original=B['BASE']['SafetySQLTests'].__dict__.get(name,method)
        src=textwrap.dedent(inspect.getsource(original)).replace("('lease','restore','native','owner','install')","('install',)").replace("self.fixture('lease')","self.fixture('install')").replace("n['record_failure'](error.exception.stage,error.exception.code,primary=True)","n['_required_safety_first_exception'](error.exception)")
        n={};exec(compile(src,str(Path(__file__)),'exec'),scope,n);setattr(ActualInstallSafetyTests,name,n[name])
if __name__=='__main__':
    stream=io.StringIO();start=time.perf_counter();result=unittest.TextTestRunner(stream=stream,verbosity=2).run(unittest.defaultTestLoader.loadTestsFromTestCase(ActualInstallSafetyTests));record={'schema':'workinants.install-v3-actual-safety-composition.v1','status':'PASS' if result.wasSuccessful() else 'FAIL','tests':result.testsRun,'seconds':round(time.perf_counter()-start,3),'log':stream.getvalue(),'failures':[{'test':str(t),'detail':s} for t,s in result.failures+result.errors],'runtime':'NOT_RUN','boundary':'ACTUAL_NEW_CORE_STEPS_ONLY_COMMAND_MOCK_NO_FINALIZER_SQL_OBSERVE_SHADOW_OR_TEMPLATE_INJECTION'}
    with (T/'install_review_ready_v3_actual_safety_composition_first_20261119.json').open('x',encoding='utf8') as f:json.dump(record,f,indent=2);f.write('\n')
    print(json.dumps({k:v for k,v in record.items() if k not in ('log','failures')}));print(stream.getvalue()[-7500:]);sys.exit(0 if result.wasSuccessful() else 1)
