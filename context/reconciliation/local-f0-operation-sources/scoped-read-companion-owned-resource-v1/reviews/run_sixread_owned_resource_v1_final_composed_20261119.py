"""Exact loaded-harness final happy/gate/clock checks; all transports mocked."""
from pathlib import Path
import hashlib,json,runpy,sys,time,unittest
TASK=Path(__file__).resolve().parent
HARNESS=TASK/'check_sixread_owned_resource_v1_full_composed_20261119.py'
def sha(raw):return hashlib.sha256(raw).hexdigest()
before=sha(HARNESS.read_bytes());n=runpy.run_path(str(HARNESS));assert n['LOADED_HARNESS_SHA']==before
sys.addaudithook(n['ADMISSION']['audit'])
names=('test_00_independent_owned_review_pending_rejects_before_git','test_actual_owned_CLI_source_install_native_child_post_and_cleanup','test_single_current_expired_grant_stops_real_child_before_query')
started=time.monotonic();result=unittest.TextTestRunner(verbosity=2).run(unittest.TestSuite(n['FullCompositionTests'](name)for name in names));after=sha(HARNESS.read_bytes());assert before==after
value={'schema':'workinants.sixread-owned-resource-final-composed-author-check.v1','source_only_mock':True,'independent_source_approval':False,'runtime_qualification_claimed':False,'loaded_harness_sha256':before,'end_harness_sha256':after,'harness_unchanged_during_run':True,'actual_methods':list(names),'methods_run':result.testsRun,'failures':len(result.failures),'errors':len(result.errors),'duration_seconds':time.monotonic()-started,'capture_sha256':n['CAPTURE_SHA'],'observations':n['OBSERVATIONS'],'limits':['Only process transports simulated; real CLI/main/helpers/comparators/child/Session unchanged','Historical sanitized Owner native/oracle/ledger rows are mock data only; original byte hashes checked','Clone-only source/literal approval projection; live source gates remain PENDING','Tests do not qualify any actual database assertion']}
path=TASK/'six_read_owned_resource_v1_final_composed_author_probe_20261119.json'
with path.open('xb')as handle:handle.write((json.dumps(value,indent=2,allow_nan=False)+'\n').encode())
print(json.dumps({'path':str(path),'sha256':sha(path.read_bytes()),'success':result.wasSuccessful(),'methods':result.testsRun,'seconds':value['duration_seconds']}))
raise SystemExit(0 if result.wasSuccessful()else 1)
