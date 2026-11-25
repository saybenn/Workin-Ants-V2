"""Private explicit versioned derivation; no process/network/Git API."""
import ast,hashlib,json,pathlib
A=pathlib.Path(__file__).parent;P=A/'workinants-correction-pass';B=A/'preserved-read13-base';T=A.parent
plan=json.loads((A/'owning-plan.json').read_bytes());FIVE=plan['new_owned_five'];sha=lambda b:hashlib.sha256(b).hexdigest()
def segment(text,name):
    node=next(n for n in ast.parse(text).body if isinstance(n,(ast.FunctionDef,ast.ClassDef))and n.name==name)
    return ast.get_source_segment(text,node)+'\n'
def replace_function(text,name,new):
    old=segment(text,name).rstrip();assert text.count(old)==1;return text.replace(old,new.rstrip())
def family(text):
    return text.replace('remaining_app_read13_owned_v2','customer_stale_predecessor_v1').replace('remaining_app_read13_owned','customer_stale_predecessor').replace('REMAINING_APP_READ13_OWNED_V2','CUSTOMER_STALE_PREDECESSOR_OWNED_V1').replace('remaining-app-read13-owned','customer-stale-predecessor').replace('read13','customer_stale').replace('READ13','CSP1').replace('-customer_stale','-customer-stale')
def put(name,text):
    p=A/name;compile(text,str(p),'exec');raw=text.encode()
    if p.exists()and p.read_bytes()!=raw:
        history=A/'author-history'/('before-'+sha(p.read_bytes())[:12]);history.mkdir(parents=True,exist_ok=True);(history/name).write_bytes(p.read_bytes())
    p.write_bytes(raw)
core=family((B/'execute_local_f0_remaining_app_read13_owned_v2_20261120.py').read_text())
core=core.replace('import uuid','import uuid\nimport threading\nimport types\nimport stat')
core=core.replace("self.stage=report.get('stage','ENTRY')","self.stage=globals().get('report',{}).get('stage','ENTRY')")
core=core.replace("'prepared_protocols':82","'prepared_protocols':3")
core=core.replace("    passwords={};", "    report['transport_closure']={'transport_closure_unconfirmed':False,'first_unconfirmed_closure':None}\n    passwords={};")
core=core.replace("    first=None;observation=None\n    try:_required_safety_sql(name,'ORIGINAL_GRANTOR_FINALIZATION')", "    need(report['transport_closure']['transport_closure_unconfirmed']is False,'FINALIZATION_BLOCKED_UNKNOWN_CLIENT_TRANSPORT')\n    first=None;observation=None\n    try:_required_safety_sql(name,'ORIGINAL_GRANTOR_FINALIZATION')")
lease=(T/'execute_local_f0_lease_mechanism_v1_20261120.py').read_bytes();assert sha(lease)=='8e2c2529727fd8270f709737c3129c1ad650e09c6f70914dedd0ea46354250e9'
process=segment(lease.decode(),'process').replace('def process(args,payload=None,timeout=30):','def binary_process(args,payload=None,timeout=60,*,cwd=None,env=None,output_limit=16*1024*1024,closed_git_files=None,git_commit=None):')
process=process.replace("0<timeout<=120,'PROCESS_PROFILE')","0<timeout<=180 and type(output_limit)is int and 0<output_limit<=16*1024*1024 and (env is None or type(env)is dict and all(type(k)is str and type(v)is str for k,v in env.items())),'PROCESS_PROFILE')")
process=process.replace(' deadline=time.monotonic()+timeout',' bounds=closed_git_budget(args,payload,cwd,closed_git_files,git_commit)if closed_git_files is not None else(output_limit,output_limit)\n deadline=time.monotonic()+timeout')
process=process.replace('len(buffers[index])+len(chunk)>65536','len(buffers[index])+len(chunk)>bounds[index]')
process=process.replace('stderr=subprocess.PIPE)','stderr=subprocess.PIPE,cwd=ROOT if cwd is None else cwd,env=env)')
process=process.replace('  if failure is not None:\n', '  csp_record_transport_closure(p,(*threads,*cleanup_threads)if p is not None else threads)\n  if failure is not None:\n')
facade='''def csp_record_transport_closure(process,threads):
    """Latch only fixed process/pipe/thread closure outcomes; retain no identity."""
    value=globals().get('report')
    if type(value)is not dict:return
    outcomes={'process_exited':False,'pipes_closed':False,'threads_closed':False}
    if process is not None:
        try:outcomes['process_exited']=type(process.poll())is int
        except BaseException:pass
        try:outcomes['pipes_closed']=all(stream.closed is True for stream in(process.stdin,process.stdout,process.stderr))
        except BaseException:pass
    try:outcomes['threads_closed']=not any(thread.is_alive()for thread in threads)
    except BaseException:pass
    state=value['transport_closure']
    if not all(outcomes.values()):
        state['transport_closure_unconfirmed']=True
        if state['first_unconfirmed_closure']is None:state['first_unconfirmed_closure']=outcomes

def closed_git_budget(args,payload,cwd,files,commit):
    need(args==['git','--no-optional-locks','-c','core.longpaths=true','cat-file','--batch'] and type(files)is dict and bool(files) and type(commit)is str and re.fullmatch('[0-9a-f]{40}',commit) and cwd is not None,'CLOSED_GIT_PROFILE_REQUIRED')
    root=Path(cwd).resolve();need(payload==''.join(commit+':'+name+'\\n'for name in sorted(files)).encode(),'CLOSED_GIT_REQUEST_REQUIRED')
    total=0
    for name,wanted in sorted(files.items()):
        need(type(name)is str and name and ':'not in name and '\\\\'not in name and not Path(name).is_absolute() and all(p not in('','.','..')for p in name.split('/')) and type(wanted)is str and re.fullmatch('[0-9a-f]{64}',wanted),'CLOSED_GIT_SOURCE_MAP')
        path=root/name;need(not any(p.is_symlink()for p in(path,*path.parents)if p.is_relative_to(root)) and path.resolve().is_relative_to(root),'CLOSED_GIT_SOURCE_PATH')
        before=path.lstat();need(stat.S_ISREG(before.st_mode) and before.st_nlink==1 and before.st_size<=16*1024*1024,'CLOSED_GIT_SOURCE_FILE_BOUND')
        with path.open('rb')as stream:
            opened=os.fstat(stream.fileno());raw=stream.read(16*1024*1024+1);after=os.fstat(stream.fileno())
        final=path.lstat();keys=('st_mode','st_dev','st_ino','st_nlink','st_size','st_mtime_ns');version=lambda s:tuple(getattr(s,k)for k in keys)
        need(version(before)==version(opened)==version(after)==version(final) and before.st_ctime_ns==final.st_ctime_ns and opened.st_ctime_ns==after.st_ctime_ns and len(raw)==before.st_size and hashlib.sha256(raw).hexdigest()==wanted,'CLOSED_GIT_CURRENT_SOURCE_DRIFT')
        total+=len(raw)+48+len(str(len(raw)))
    return total,65536

def strict_process_text(raw):
    need(type(raw)is bytes,'PROCESS_TEXT_BYTES_REQUIRED')
    try:return raw.decode('utf8','strict').replace('\\r\\n','\\n').replace('\\r','\\n')
    except UnicodeError:raise Stop('PROCESS_UTF8_REJECTED')from None

def command(args,input=None,timeout=60):
    need(input is None or type(input)is str,'PROCESS_TEXT_INPUT_REQUIRED')
    result=binary_process(args,None if input is None else input.encode('utf8','strict'),timeout)
    return subprocess.CompletedProcess(args,result.returncode,strict_process_text(result.stdout),strict_process_text(result.stderr))

def migration_process(args,**options):
    need(set(options)<={'input','text','capture_output','timeout','shell','encoding','errors','cwd','env'} and options.get('text')is True and options.get('capture_output')is True and options.get('shell',False)is False and options.get('encoding','utf8')in('utf8','utf-8') and options.get('errors','strict')=='strict','MIGRATION_PROCESS_PROFILE')
    payload=options.get('input');need(payload is None or type(payload)is str,'MIGRATION_TEXT_INPUT')
    result=binary_process(args,None if payload is None else payload.encode('utf8'),options.get('timeout',60),cwd=options.get('cwd'),env=options.get('env'))
    return subprocess.CompletedProcess(args,result.returncode,strict_process_text(result.stdout),strict_process_text(result.stderr))
'''
core=replace_function(core,'command',segment(lease.decode(),'Result')+'\n'+process+'\n'+facade)
core=core.replace("MANIFEST=json.loads(MANIFEST_PATH.read_text(encoding='utf8'))","MANIFEST=source_unique_json(MANIFEST_PATH.read_bytes())")
gate='''
OWNED_VALIDATION='context/reconciliation/local-f0-customer-stale-predecessor-owned-v1-source-validation.json'
OWNED_ARCHIVE='context/reconciliation/local-f0-operation-sources/customer-stale-predecessor-owned-v1'
SOURCE_GATE_KEYS=('independent_source_review','independent_owned_resource_review','independent_safety_sql_review','independent_binary_transport_review','Root_source_review')

def source_unique_json(raw):
    def pairs(items):
        d={}
        for k,v in items:need(k not in d,'DUPLICATE_SOURCE_JSON');d[k]=v
        return d
    return json.loads(raw,object_pairs_hook=pairs,parse_constant=lambda _:(_ for _ in()).throw(Stop('NONFINITE_SOURCE_JSON')))

def csp_source_gate_before_steps():
    pins=MANIFEST.get('packet_files_sha256');need(type(pins)is dict and OWNED_VALIDATION in pins,'CSP1_FULL_SOURCE_MAP_REQUIRED')
    cfg=MANIFEST.get('customer_stale');need(type(cfg)is dict and type(cfg.get('external_files_sha256'))is dict,'CSP1_SOURCE_CONFIGURATION_REQUIRED');five=cfg['external_files_sha256']
    need(len(five)==5 and all(type(h)is str and re.fullmatch('[0-9a-f]{64}',h)for h in five.values()),'CSP1_EXACT_FIVE_REQUIRED')
    def read(name):
        need(type(name)is str and name and ':'not in name and '\\\\'not in name and not Path(name).is_absolute() and all(p not in('','.','..')for p in name.split('/')),'CSP1_SOURCE_PATH')
        p=ROOT/name;need(not p.is_symlink() and p.resolve().is_relative_to(ROOT.resolve()),'CSP1_SOURCE_PATH_ESCAPE');raw=p.read_bytes();need(hashlib.sha256(raw).hexdigest()==pins.get(name),'CSP1_SOURCE_DRIFT');return raw
    value=source_unique_json(read(OWNED_VALIDATION));need(value.get('operator_sources_sha256')==five,'CSP1_GATE_FIVE_BINDING')
    for key in SOURCE_GATE_KEYS:
        review=value.get(key);need(type(review)is dict and review.get('decision')=='SOURCE_APPROVED' and review.get('operator_sources_sha256')==five,'CSP1_PENDING_SOURCE_REVIEW')
        need(type(review.get('path'))is str and review['path'].startswith(OWNED_ARCHIVE+'/reviews/'),'CSP1_REVIEW_NAMESPACE')
        raw=read(review['path']);need(hashlib.sha256(raw).hexdigest()==review.get('sha256'),'CSP1_REVIEW_BYTES');actual=source_unique_json(raw)
        need(actual.get('decision')=='SOURCE_APPROVED' and actual.get('operator_sources_sha256')==five,'CSP1_REVIEW_BINDING')
    for name,wanted in five.items():
        need(type(name)is str and '/'not in name and '\\\\'not in name and ':'not in name,'CSP1_EXTERNAL_NAME')
        p=TASK/name;need(not p.is_symlink() and hashlib.sha256(p.read_bytes()).hexdigest()==wanted and read(OWNED_ARCHIVE+'/'+name+'.txt')==p.read_bytes(),'CSP1_PHYSICAL_FIVE')
    need(MANIFEST.get('review_status')=='APPROVED_LOCAL_F0_CUSTOMER_STALE_PREDECESSOR_OWNED_V1_ATTEMPT','CSP1_PENDING_OPERATIONAL_LITERAL')
    pin_name='pin_local_f0_customer_stale_predecessor_v1_plan_20261120.py';raw=(TASK/pin_name).read_bytes()
    need(hashlib.sha256(raw).hexdigest()==five.get(pin_name),'CSP1_REVIEWED_PINNER_SOURCE')
    pin=types.ModuleType('_CSP1_closed_source_pinner');pin.__file__=str(TASK/pin_name);exec(compile(raw,str(TASK/pin_name),'exec'),pin.__dict__)
    pin.verify_pinned(MANIFEST_PATH)

'''
core=core.replace('def launch(argv=None):',gate+'def launch(argv=None):')
core=core.replace("initialize(args.manifest)\n        need(","initialize(args.manifest)\n        csp_source_gate_before_steps()\n        need(")
put(FIVE[0],core)
old=(B/'local_f0_remaining_app_read13_owned_v2_operation_steps.py').read_text()
prefix=old[:old.index('# Restore-specific operations follow;')]
prefix=prefix.replace("result=subprocess.run(arguments,**options)","result=migration_process(arguments,**options)")
prefix=prefix.replace("    except subprocess.TimeoutExpired:raise Stop('MIGRATION_PROCESS_TIMEOUT_CLOSURE_UNCONFIRMED') from None", "    except Stop:raise\n    except subprocess.TimeoutExpired:raise Stop('MIGRATION_PROCESS_TIMEOUT_CLOSURE_UNCONFIRMED') from None")
prefix=prefix.replace("blob=subprocess.run(['git','-c','core.longpaths=true','show',COMMIT+':'+path],cwd=ROOT,capture_output=True,timeout=30)","blob=binary_process(['git','-c','core.longpaths=true','show',COMMIT+':'+path],timeout=30)")
prefix=prefix.replace('SCOPED_STATE','CSP_STATE')
shared='\nimport builtins\nimport types\nfrom pathlib import PureWindowsPath\nimport stat\n'
shared+=old[old.index("OWNER_SECRET_TMPFS_TOKEN="):old.index('def admit_read13_sources():')]
shared=shared.replace("HELPER_FILES",'CSP_HELPER_FILES').replace('HELPERS','CSP_HELPERS')
shared+=segment(old,'verify_external_input_preservation')+segment(old,'validate_owned_source_snapshot')+segment(old,'validate_owned_tool_archive')+segment(old,'qualify_native_counts')+segment(old,'bounded_component_reference')+segment(old,'component_reference_integrity')
shared=shared.replace('SCOPED_STATE','CSP_STATE')
post=segment(old,'readonly_post_proof')
post=post.replace("first=SCOPED_STATE['first_install']","first=CSP_STATE['first_install']").replace("baseline=child['baseline']['tables'];final_sha=child['results'][-1]['complete_state_sha256']","baseline=CSP_STATE['baseline_state'];final_sha=digest(baseline)")
post=post.replace("report['read13']","report['customer_stale']")
steps=family(prefix+shared+post+'\n'+(A/'CSP1_steps_extension.py.txt').read_text())
put(FIVE[1],steps)
archive=P/plan['new_archive'];archive.mkdir(parents=True,exist_ok=True)
pres=json.loads((A/'before-author-preservation.json').read_bytes());baseline=json.loads((A/'catalog-baseline.json').read_bytes())
fixed={'fixed-catalog-source-map.json':baseline['packet_files_sha256'],'fixed-child-current-map.json':pres['child_current_files_sha256']}
for n,v in fixed.items():(archive/n).write_text(json.dumps(v,indent=2)+'\n',encoding='utf8')
prep_old=(B/'prepare_local_f0_remaining_app_read13_owned_v2_plan.py').read_text();tree=ast.parse(prep_old)
constants={'IMAGE','MIGRATION','SQL','SQL_SHA','SCHEMA','LOCK','RUNTIME','HISTORY_HELPER','HISTORY_SHA','IMAGE_PROOF_REVIEW','IMAGE_FILES','TOOL_CLOSURE','TOOL_CLOSURE_SHA','TOOL_ARCHIVE_SHA'}
parts=['"""Pure CSP1 source preparation; all execution gates remain PENDING."""\n']
for n in tree.body:
    if isinstance(n,(ast.Import,ast.ImportFrom))or isinstance(n,ast.Assign)and any(isinstance(t,ast.Name)and t.id in constants for t in n.targets):parts.append(ast.get_source_segment(prep_old,n)+'\n')
parts.append("TASK=Path(__file__).resolve().parent\nROOT=TASK/'workinants-correction-pass'\n")
for n in ('Refused','need','sha','data','decoded','relative','mapping','source','archive_tree','verify_tools'):parts.append(segment(prep_old,n))
packet=json.loads((P/'review-output/customer-stale-predecessor-v1/fixtures.json').read_bytes())
newconst={'FIXTURES':'review-output/customer-stale-predecessor-v1/fixtures.json','FIXTURES_SHA':'c2074a45f80147833e958d1f02b5d3840b32eb13a46033ebc7f1e75c322eb10b','CONTENT_SHA':packet['content_sha256'],'CHILD_VALIDATION':'context/reconciliation/customer-stale-predecessor-v1-source-validation.json','CHILD_VALIDATION_SHA':'e143965d80ede2a4730ab1b5632e51d3280cb447c974e61ca2cd18ea59632214','OWNED_ARCHIVE':plan['new_archive'],'OWNED_VALIDATION':plan['new_validation'],'EXTERNAL_FILES':tuple(FIVE),'FIXED_CATALOG_MAP_SHA':sha((archive/'fixed-catalog-source-map.json').read_bytes()),'FIXED_CHILD_MAP_SHA':sha((archive/'fixed-child-current-map.json').read_bytes())}
parts.extend(n+'='+repr(v)+'\n'for n,v in newconst.items())
prep='\n'.join(parts)+'\n'+(A/'CSP1_prepare_extension.py.txt').read_text()+'\n'+segment(prep_old,'main')+"\nif __name__=='__main__':raise SystemExit(main())\n"
put(FIVE[2],prep)
print(json.dumps({'Core_sha256':sha((A/FIVE[0]).read_bytes()),'Steps_sha256':sha((A/FIVE[1]).read_bytes()),'private_only':True}))
