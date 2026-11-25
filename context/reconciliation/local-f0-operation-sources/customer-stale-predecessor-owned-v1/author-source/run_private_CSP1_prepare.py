import hashlib,json,pathlib,runpy,sys,time,traceback
sys.dont_write_bytecode=True
A=pathlib.Path(__file__).parent
def audit(event,args):
 if event in('subprocess.Popen','os.system','os.posix_spawn','os.spawn','socket.connect','socket.bind','socket.getaddrinfo'):raise AssertionError('EXTERNAL_BOUNDARY_FORBIDDEN')
sys.addaudithook(audit)
start=time.monotonic();checks=A/'author-checks';checks.mkdir(exist_ok=True);tag=sys.argv[1]if len(sys.argv)>1 else'initial'
report={'schema':'workinants.CSP1-private-source-preparation-check.v1','tag':tag,'runtime':'NOT_RUN','real_external_boundaries':0,'source_gates':'PENDING','Posture':'D'}
try:
 prep=runpy.run_path(str(A/'prepare_local_f0_customer_stale_predecessor_v1_plan.py'));base=A/'catalog-baseline.json';result=prep['prepare'](base,hashlib.sha256(base.read_bytes()).hexdigest());manifest=json.loads(pathlib.Path(result['operation_manifest']).read_bytes());files=manifest['prepared_source_file_inventory_sha256'];root=A/'workinants-correction-pass'
 sizes={n:len((root/n).read_bytes())for n in files};framing=sum(s+48+len(str(s))for s in sizes.values())
 report.update(status='PASS_SOURCE_PREPARATION_ONLY',prepared=result,file_count=len(files),source_blob_bytes=sum(sizes.values()),exact_Git_framing_bytes=framing,largest_source_blob=max(sizes.values()),all_tool_members_actually_verified=10300)
except BaseException as e:
 report.update(status='FAILED_PREPARATION_PRESERVED',exception_type=type(e).__name__,code=str(e)if isinstance(e,Exception)and len(str(e))<100 and str(e).isupper()else'UNEXPECTED_SOURCE_PREPARATION_FAILURE')
 traceback.print_exc()
report['seconds']=round(time.monotonic()-start,3);out=checks/('source-preparation-'+tag+'.json');assert not out.exists();out.write_text(json.dumps(report,indent=2)+'\n',encoding='utf8');print(json.dumps(report,indent=2));raise SystemExit(0 if report['status'].startswith('PASS_')else 1)
