"""Actual entry with internally consistent current source pins and PENDING gates."""
import hashlib,io,json,pathlib,runpy,subprocess,sys,tempfile
from contextlib import redirect_stdout
from unittest.mock import patch
sys.dont_write_bytecode=True
A=pathlib.Path(__file__).resolve().parent;P=A/'workinants-correction-pass';sha=lambda b:hashlib.sha256(b).hexdigest()
def audit(event,args):
 if event in('subprocess.Popen','os.system','os.posix_spawn','os.spawn','socket.connect','socket.bind','socket.getaddrinfo'):raise AssertionError('REAL_EXTERNAL_BOUNDARY_FORBIDDEN')
sys.addaudithook(audit)
plan=json.loads((A/'owning-plan.json').read_bytes());five={n:sha((A/n).read_bytes())for n in plan['new_owned_five']};prep=runpy.run_path(str(A/plan['new_owned_five'][2]));baseline=json.loads((A/'catalog-baseline.json').read_bytes());packet=json.loads((P/'review-output/customer-stale-predecessor-v1/fixtures.json').read_bytes());files=prep['source_inventory'](baseline['packet_files_sha256'],packet,five,False)
value=json.loads((A/'local-f0-customer-stale-predecessor-v1-plan-73292a8f/operation-manifest.json').read_bytes());value.update(source_commit='a'*40,source_tree='b'*40,packet_files_sha256=files,packet_sha256=sha(''.join(n+'\0'+files[n]+'\n'for n in sorted(files)).encode()),prepared_source_file_inventory_sha256=files,wrapper_sha256=five[plan['new_owned_five'][0]],steps_sha256=five[plan['new_owned_five'][1]],pin_helper_sha256=five[plan['new_owned_five'][4]]);value['customer_stale']['external_files_sha256']=five
val_path=P/plan['new_validation'];val_before=val_path.read_bytes();owned=json.loads(val_before);assert owned['operator_sources_sha256']==five and files[plan['new_validation']]==sha(val_before)
root_out=pathlib.Path(value['evidence_directory']);assert not root_out.exists();directory=tempfile.TemporaryDirectory(prefix='CSP1-PENDING-gate-',dir=A);temp=pathlib.Path(directory.name);assert temp.resolve().parent==A.resolve();path=temp/'operation-manifest.json';path.write_text(json.dumps(value),encoding='utf8');core=runpy.run_path(str(A/plan['new_owned_five'][0]));core['initialize'](path);compiled=[];actual_compile=compile

def compile_(raw,name,*args,**kwargs):
 if str(name).endswith(tuple(plan['new_owned_five'][1:])):compiled.append(pathlib.Path(name).name)
 return actual_compile(raw,name,*args,**kwargs)
try:
 with patch.object(subprocess,'Popen',side_effect=AssertionError('PENDING_PROCESS_FORBIDDEN')),patch.object(subprocess,'run',side_effect=AssertionError('PENDING_PROCESS_FORBIDDEN')),patch('builtins.compile',compile_):
  try:core['csp_source_gate_before_steps']();raise AssertionError('PENDING_MUST_REJECT')
  except core['Stop']as e:assert e.code=='CSP1_PENDING_SOURCE_REVIEW'
  with redirect_stdout(io.StringIO()):assert core['launch'](['--execute-reviewed-customer-stale-predecessor','--manifest',str(path)])==1
 assert not compiled and not root_out.exists()and val_path.read_bytes()==val_before
finally:
 assert temp.resolve().parent==A.resolve()and temp.name.startswith('CSP1-PENDING-gate-');directory.cleanup()
report={'schema':'workinants.CSP1-consistent-PENDING-source-gate-check.v1','status':'PASS','current_source_pins_consistent':True,'all_real_new_gates_pending':True,'specific_actual_refusal':'CSP1_PENDING_SOURCE_REVIEW','whole_entry_refused':True,'project_helper_or_Steps_compiles':0,'process_calls':0,'resources_or_evidence_directory_created':False,'actual_approval_values_changed':False,'operator_sources_sha256':five,'runtime':'NOT_RUN','Posture':'D'}
out=A/('author-checks/consistent-PENDING-source-gate'+('-'+sys.argv[1]if len(sys.argv)>1 else'')+'.json');assert not out.exists();out.write_text(json.dumps(report,indent=2)+'\n',encoding='utf8');print(json.dumps(report))
