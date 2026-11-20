"""Disk-only immutable INSTALL handoff reader; default never approves.

Poll only the fixed ready name. No mutable outer/child result is opened.
Explicit approval publication requires the independently reviewed protocol6c
decision, a fresh handoff reload, an unexpired reviewer deadline and no handles.
"""
import argparse,hashlib,json,os,stat,time
from pathlib import Path
from types import ModuleType
ROOT=Path(__file__).resolve().parents[2]
HELPER='scripts/install_independent_review_protocol_source_phase_v5.py'
AUTHORITY='scripts/install_control_protocol_v2.py'
AUTHORITY_SHA='6c1474dc12a603b07346fff014c8ab8bd15dec5be0b972ec1d504342115ba48f'
SELF='scripts/sql-review/watch-install-independent-review-source-phase-v5.py'
PHASE_SOURCE='scripts/install_failed_precleanup_activation_v5.py'
V2_FILE='independent-review-child-v2-evidence.json'
OPEN_HANDLES=0
class Held(ValueError):pass
def need(ok,code):
    if not ok:raise Held(code)
def sha(raw):return hashlib.sha256(raw).hexdigest()
def regular(path,cap):
    st=path.lstat();need(stat.S_ISREG(st.st_mode) and not stat.S_ISLNK(st.st_mode) and st.st_nlink==1 and st.st_size<=cap,'FRESH_SINGLE_LINK_REGULAR_REQUIRED');return st
def read_regular(path,cap):
    global OPEN_HANDLES
    before=regular(path,cap);handle=path.open('rb');OPEN_HANDLES+=1
    try:
        opened=os.fstat(handle.fileno());need((before.st_dev,before.st_ino)==(opened.st_dev,opened.st_ino) and opened.st_nlink==1,'IMMUTABLE_FILE_REPLACED');raw=handle.read(cap+1);after=os.fstat(handle.fileno());need((before.st_dev,before.st_ino,before.st_size,before.st_mtime_ns)==(after.st_dev,after.st_ino,after.st_size,after.st_mtime_ns) and len(raw)<=cap,'IMMUTABLE_FILE_CHANGED')
    finally:
        try:handle.close()
        finally:OPEN_HANDLES-=1
    end=regular(path,cap);need((before.st_dev,before.st_ino,before.st_size,before.st_mtime_ns)==(end.st_dev,end.st_ino,end.st_size,end.st_mtime_ns),'IMMUTABLE_PATH_CHANGED');return raw
def publish_immutable(path,raw,cap,before_publish=None):
    # Windows rename atomically refuses an existing destination. POSIX rename
    # can overwrite; fail closed there. No hardlink or replace is used.
    need(os.name=='nt' and type(raw) is bytes and len(raw)<=cap and OPEN_HANDLES==0,'WINDOWS_CLOSED_BOUNDED_PUBLICATION_REQUIRED')
    try:path.lstat()
    except FileNotFoundError:pass
    else:raise Held('IMMUTABLE_DESTINATION_EXISTS')
    temp=path.with_name(path.name+'.publishing')
    with temp.open('xb') as handle:handle.write(raw);handle.flush();os.fsync(handle.fileno())
    regular(temp,cap)
    if before_publish is not None:before_publish()
    temp.rename(path);regular(path,cap)
def compile_source(path,raw):
    module=ModuleType('_install_review_'+path.stem.replace('-','_'));module.__file__=str(path);exec(compile(raw,str(path),'exec'),module.__dict__);return module.__dict__
def load_sources(pins):
    need(type(pins) is dict and set(pins)=={HELPER,AUTHORITY,SELF,PHASE_SOURCE},'CLOSED_WATCH_SOURCE_MAP');raws={p:read_regular(ROOT/p,1024*1024) for p in pins};need(all(type(pins[p]) is str and sha(raw)==pins[p] for p,raw in raws.items()) and pins[AUTHORITY]==AUTHORITY_SHA,'WATCH_SOURCE_DRIFT');p=compile_source(ROOT/HELPER,raws[HELPER]);p['_phase']=compile_source(ROOT/PHASE_SOURCE,raws[PHASE_SOURCE]);return p,compile_source(ROOT/AUTHORITY,raws[AUTHORITY])
def handoff_paths(out,p):return {p['READY']:out/'install-controls'/p['READY'],p['PROOF']:out/'install-controls'/p['PROOF'],p['SNAPSHOT']:out/'install-controls'/p['SNAPSHOT'],p['IDENTITY']:out/p['IDENTITY'],p['PLAN']:out/p['PLAN']}
def read_handoff(out,p,expected):
    paths=handoff_paths(out,p);raws={name:read_regular(path,p['CAPS'][name]) for name,path in paths.items()};need(OPEN_HANDLES==0,'READER_HANDLES_OPEN');value=p['bindings'](raws,expected);validate_v2_handoff(out,p,value);return value,raws
def validate_v2_handoff(out,p,value):
    # Read exactly one fixed additional immutable file, never a caller path.
    snapshot=value['snapshot'];target=snapshot['targets']['division_failure'];binding=target.get('completed_v2_evidence')
    need(type(binding)is dict and set(binding)=={'file','sha256'}and binding['file']==V2_FILE,'V2_EVIDENCE_BINDING');p['hash_'](binding['sha256'])
    raw=read_regular(out/'install-controls'/V2_FILE,p['CAPS'][p['SNAPSHOT']]);need(sha(raw)==binding['sha256']and OPEN_HANDLES==0,'V2_EVIDENCE_BYTES_OR_HANDLES')
    full=p['decode'](raw);need(type(full)is dict and set(full)==p['SNAPSHOT_FIELDS']|{'evidence_complete','persistence_failure','first_failure'} and full.get('schema')=='workinants.install-controls-results.v2'and full.get('evidence_complete')is True and full.get('persistence_failure')is False and full.get('first_failure')is None,'CLEAN_COMPLETED_REVIEW_SNAPSHOT_REQUIRED')
    projection={k:full[k]for k in p['SNAPSHOT_FIELDS']};projection['schema']='workinants.install-controls-results.v1'
    phase=full['targets']['division_failure'];h=p['_phase'];expected={**{k:value['ready'][k]for k in ('run_id','source_commit','source_tree','packet_sha256','container_id','source_sql_sha256')},'variant':'division_failure'}
    h['validate_receipts'](phase.get('failed_precleanup_activation'),expected,True);h['validate_closures'](phase.get('failed_precleanup_closures'),True)
    need('completed_v2_evidence'not in phase,'V2_EVIDENCE_RECURSION');phase['completed_v2_evidence']=binding;need(p['exact'](projection,snapshot),'V2_EVIDENCE_EXACT_PROJECTION')
    return True

def wait_ready(out,p,expected,monotonic=time.monotonic,sleep=time.sleep,watch_seconds=1800):
    need(type(watch_seconds) is int and 1<=watch_seconds<=1800,'BOUNDED_WATCH');paths=handoff_paths(out,p);approval=out/'install-controls'/p['APPROVAL']
    last_absent=None
    for path in (*paths.values(),approval):
        checked_at=monotonic()
        try:path.lstat()
        except FileNotFoundError:
            if path==paths[p['READY']]:last_absent=checked_at
            continue
        raise Held('FRESH_PRELAUNCH_HANDOFF_REQUIRED')
    end=monotonic()+watch_seconds
    while monotonic()<end:
        checked_at=monotonic()
        try:paths[p['READY']].lstat()
        except FileNotFoundError:last_absent=checked_at;sleep(1);continue
        deadline=last_absent+220;need(monotonic()<deadline,'REVIEW_DEADLINE_EXPIRED');value,raws=read_handoff(out,p,expected);need(monotonic()<deadline and OPEN_HANDLES==0,'REVIEW_DEADLINE_OR_HANDLES');return value,raws,deadline
    raise Held('WATCH_EXPIRED_WITHOUT_READY')
def publish_explicit_approval(out,p,authority,expected,decision,deadline,monotonic=time.monotonic):
    # A caller supplies a distinct reviewer's already-decided seven fields.
    # No code constructs an APPROVED decision from transport observations.
    need(monotonic()<deadline and OPEN_HANDLES==0,'REVIEW_DEADLINE_OR_HANDLES');value,raws=read_handoff(out,p,expected);proof=value['proof'];identity={k:proof[k] for k in ('run_id','container_id','source_sql_sha256')};authority['require_recovery_review'](proof,decision,identity);raw=p['canonical'](decision)
    def deadline_before_rename():need(monotonic()<deadline and OPEN_HANDLES==0,'REVIEW_DEADLINE_OR_HANDLES')
    deadline_before_rename();publish_immutable(out/'install-controls'/p['APPROVAL'],raw,p['CAPS'][p['APPROVAL']],before_publish=deadline_before_rename);return sha(raw)
def main(argv=None):
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--arming',required=True,type=Path);args=parser.parse_args(argv)
    raw=read_regular(args.arming,65536)
    def unique(items):
        value={}
        for k,v in items:need(k not in value,'DUPLICATE_ARMING_FIELD');value[k]=v
        return value
    a=json.loads(raw.decode('utf8'),object_pairs_hook=unique,parse_constant=lambda _:(_ for _ in ()).throw(Held('NONFINITE_ARMING')));need(type(a) is dict and set(a)=={'schema','evidence_directory','expected','source_modules_sha256','watch_seconds'} and a['schema']=='workinants.install-independent-review-watch.v2','WATCH_ARMING_SCHEMA');p,authority=load_sources(a['source_modules_sha256']);out=Path(a['evidence_directory']);need(out.is_absolute() and out==out.resolve() and not out.is_symlink() and out.is_relative_to(ROOT.parent) and not out.is_relative_to(ROOT),'TASK_EXTERNAL_WATCH');need(type(a['expected']) is dict and set(a['expected'])=={'run_id','source_commit','source_tree','packet_sha256'},'CLOSED_EXPECTED_IDENTITY');value,raws,deadline=wait_ready(out,p,a['expected'],watch_seconds=a['watch_seconds']);print(json.dumps({'status':'IMMUTABLE_HANDOFF_READY_REQUIRES_EXPLICIT_INDEPENDENT_REVIEW','run_id':value['ready']['run_id'],'ready_sha256':sha(raws[p['READY']]),'arming_sha256':sha(raw),'watcher_source_sha256':a['source_modules_sha256'][SELF],'local_review_budget_seconds':220,'review_deadline_monotonic':deadline,'approval_issued':False,'all_read_handles_closed':OPEN_HANDLES==0},allow_nan=False),flush=True);return 0
if __name__=='__main__':raise SystemExit(main())
