"""Dormant finite CTX01 coordinator. Import/--help execute no helpers or runtime.

An external reviewed plan must pin this module, its whole helper closure, the
unchanged 71f00 source packet and a same-run/current-CID native PASS attestation.
No provisioning, migration, privilege repair, owner adapter or worker loop exists
here. Every selected control remains NOT_RUN; only exact finite scenarios pass.
"""
import argparse
import builtins
from contextlib import redirect_stdout, redirect_stderr
from copy import deepcopy
import datetime
import hashlib
import io
import json
import os
from pathlib import Path
import queue
import re
import secrets
import subprocess
import threading
import time
from types import ModuleType
import uuid

ROOT=Path(__file__).resolve().parents[2]
TASK=ROOT.parent
PACKET=ROOT/'review-output/context-control-rehearsal'
CONTENT_SHA='71f00a7b12cad6bef6f70f232a10b431d3785f03ea36ad9fce803b79ffa537d7'
FIXTURES_SHA='118454c9171267f8c7696ec3df9019a4e8883676157b57c9a2a5154d272edb69'
EXPECTED_CATALOG='3be81a13d3bb2abb41bf03ef68398da6d92fbdbccffec3d74508e91dd455f433'
SELF='scripts/sql-review/run-context-control-rehearsal.py'
API_PATH='scripts/sql-review/run-first-rehearsal.py'
HOST_PATH='scripts/sql-review/run-local-f0-migrate.py'
DIAGNOSTICS='scripts/sql-review/rehearsal-diagnostics.py'
HISTORY='scripts/prepare-local-f0-history.py'
COLLECTOR='scripts/sql-review/collect_native_catalog.sql'
SOURCE_MODULES=(SELF,API_PATH,HOST_PATH,DIAGNOSTICS,HISTORY,COLLECTOR)
DATABASE='wa_p0c_rehearsal'
ROLES={'postgres','wa_context_issuer','wa_identity_service_authority','wa_app_runtime','wa_worker'}
ACK_PREFIX='WA_CTX01_ACK|'
TUPLE='WA_CTX01_TUPLE|'
API={};HOST={}
HEADER=re.compile(r'(?:psql:<stdin>:[0-9]+: )?(?:ERROR|FATAL):\s+([0-9A-Z]{5}):\s+(.*)')
FRAME=re.compile(r'(?:CONTEXT:\s+|\s*)PL/pgSQL function platform_private\.bind_request_context\(text\) line ([1-9][0-9]{0,3}) at RAISE')
GRANT_COLUMNS=('id','token_hash','issuer_service','principal_user_id','service_principal','database_login_role','owner_module_id','action','purpose','target_kind','target_id','allowed_fields','policy_version','security_generation','source_generation','backend_pid','transaction_id','expires_at','revoked_at','created_at','mutation_transaction_id')


class HeldFailure(Exception):
    def __init__(self,code):self.code=code;super().__init__(code)


def require(value,code):
    if not value:raise HeldFailure(code)


def sha(raw):return hashlib.sha256(raw).hexdigest()
def canonical(value):return json.dumps(value,sort_keys=True,separators=(',',':'),ensure_ascii=False,allow_nan=False)
def digest(value):return sha(canonical(value).encode('utf8'))
def quote(value):return "'"+str(value).replace("'","''")+"'"


def exact(value,expected,code):require(canonical(value)==canonical(expected),code)


def bounded_outcomes(value,expected):
    safe={}
    for key,wanted in expected.items():
        actual=value.get(key) if type(value) is dict else None
        valid=type(actual) is bool if type(wanted) is bool else type(actual) is int and 0<=actual<=1000000
        safe[key]=actual if valid else None
    return {'fields_match':type(value) is dict and set(value)==set(expected),'values':safe}


def returned_created_at(rows,issuer_clock):
    """Only grant_guard's generated timestamp may replace its input value.

    The source-pinned INSERT trigger sets created_at=clock_timestamp(). Its
    JSON scalar is validated and stays private; the other 20 expected fields
    remain independently supplied, including the captured issuer transaction ID.
    """
    require(type(rows) is list and len(rows)==1 and type(rows[0]) is str,'ISSUER_CREATED_AT_RETURN_REQUIRED')
    try:value=unique_json(rows[0])
    except BaseException:raise HeldFailure('ISSUER_CREATED_AT_RETURN_REJECTED') from None
    require(type(value) is dict and set(value)=={'created_at'},'ISSUER_CREATED_AT_RETURN_REJECTED')
    stamp=value['created_at']
    require(type(stamp) is str and re.fullmatch(r'[0-9]{4}-[0-9]{2}-[0-9]{2}T[0-9]{2}:[0-9]{2}:[0-9]{2}(?:\.[0-9]{1,6})?(?:Z|[+-][0-9]{2}:[0-9]{2})',stamp),'ISSUER_CREATED_AT_TIMESTAMP_REQUIRED')
    try:
        actual=datetime.datetime.fromisoformat(stamp.replace('Z','+00:00'))
        start=datetime.datetime.fromisoformat(issuer_clock)
        good=actual.utcoffset() is not None and start.utcoffset() is not None and start<=actual<start+datetime.timedelta(seconds=300)
    except BaseException:good=False
    require(good,'ISSUER_CREATED_AT_TIMESTAMP_REQUIRED');return stamp


def unique_json(raw):
    def pairs(items):
        value={}
        for key,item in items:
            require(key not in value,'DUPLICATE_JSON_FIELD');value[key]=item
        return value
    def bad(_):raise HeldFailure('NONFINITE_JSON')
    return json.loads(raw,object_pairs_hook=pairs,parse_constant=bad)


def source_file(relative):
    require(type(relative) is str and '\\' not in relative and not relative.startswith('/') and all(p not in ('','.','..') for p in relative.split('/')),'SOURCE_PATH_INVALID')
    path=(ROOT/relative).resolve();require(path.is_relative_to(ROOT.resolve()),'SOURCE_PATH_ESCAPE');return path


def packet_file(name):
    require(type(name) is str and Path(name).name==name and name not in ('','.','..'),'PACKET_FILE_INVALID')
    return PACKET/name


def external_file(value):
    path=Path(value);require(path.is_absolute(),'ABSOLUTE_EXTERNAL_PATH_REQUIRED');path=path.resolve()
    require(path.is_relative_to(TASK.resolve()) and not path.is_relative_to(ROOT.resolve()),'TASK_EXTERNAL_PATH_REQUIRED');return path


def verified_modules(pins):
    require(type(pins) is dict and set(pins)==set(SOURCE_MODULES) and all(type(v) is str and re.fullmatch('[0-9a-f]{64}',v) for v in pins.values()),'CLOSED_MODULE_PINS_REQUIRED')
    blobs={path:source_file(path).read_bytes() for path in SOURCE_MODULES}
    require(all(sha(raw)==pins[path] for path,raw in blobs.items()),'COORDINATOR_SOURCE_DRIFT')
    return blobs


def load_helpers(blobs):
    """Compile only preverified bytes, including both transitive runpy imports."""
    API.clear();HOST.clear();namespaces={};loading=set();ordinary=builtins.__import__
    allowed={API_PATH,HOST_PATH,DIAGNOSTICS,HISTORY}
    def load(path):
        if path in namespaces:return namespaces[path]
        require(path in allowed and path not in loading,'HELPER_IMPORT_CLOSURE')
        loading.add(path);module=ModuleType('_ctx01_reviewed_'+str(len(loading)))
        module.__file__=str(ROOT/path);module.__dict__['__builtins__']={**vars(builtins),'__import__':closed_import}
        stream=io.StringIO()
        try:
            with redirect_stdout(stream),redirect_stderr(stream):exec(compile(blobs[path],str(ROOT/path),'exec'),module.__dict__)
        except BaseException:raise HeldFailure('VERIFIED_HELPER_LOAD_FAILED') from None
        require(not stream.getvalue(),'VERIFIED_HELPER_OUTPUT_REJECTED')
        loading.remove(path);namespaces[path]=module.__dict__;return namespaces[path]
    def run_path(path,init_globals=None,run_name=None):
        require(init_globals is None and run_name is None,'HELPER_RUNPY_ARGUMENTS')
        actual=Path(path).resolve();matches=[p for p in allowed if source_file(p)==actual]
        require(len(matches)==1,'HELPER_RUNPY_PATH');return dict(load(matches[0]))
    shim=ModuleType('runpy');shim.run_path=run_path
    def closed_import(name,globals=None,locals=None,fromlist=(),level=0):
        require(level==0,'HELPER_RELATIVE_IMPORT')
        if name=='runpy':return shim
        require(name.split('.')[0] in {'argparse','hashlib','ipaddress','json','os','pathlib','queue','re','secrets','subprocess','threading'},'HELPER_IMPORT_NOT_REGISTERED')
        return ordinary(name,globals,locals,fromlist,level)
    API.update(load(API_PATH));HOST.update(load(HOST_PATH))
    require(all(callable(API.get(n)) for n in ('psql','authentication_preflight')) and all(callable(HOST.get(n)) for n in ('validate_manifest','docker_json','inspect_live','verify_image')),'HELPER_API_INVALID')


def load_inputs(plan):
    fields={'schema','scope','run_id','source_commit','source_tree','packet_sha256','reviewed_packet_sha256','reviewed_content_sha256','source_modules_sha256','target_manifest','immutable_container_id','native_snapshot','native_comparison','native_attestation','scenario_names'}
    require(type(plan) is dict and set(plan)==fields,'RUN_PLAN_FIELDS')
    require(plan['schema']=='workinants.context-control-run.v1' and plan['scope']=='REVIEWED_LOCAL_CTX01_SQL_SUBSET_ONLY','RUN_PLAN_SCOPE')
    require(plan['reviewed_packet_sha256']==FIXTURES_SHA and plan['reviewed_content_sha256']==CONTENT_SHA,'REVIEWED_PACKET_REQUIRED')
    require(type(plan['immutable_container_id']) is str and re.fullmatch('[0-9a-f]{64}',plan['immutable_container_id']),'CREATED_IMMUTABLE_ID_REQUIRED')
    require(str(uuid.UUID(plan['run_id']))==plan['run_id'] and uuid.UUID(plan['run_id']).version==4,'RUN_ID_REQUIRED')
    for key in ('source_commit','source_tree'):require(type(plan[key]) is str and re.fullmatch('[0-9a-f]{40}',plan[key]),'SOURCE_CHECKPOINT_REQUIRED')
    require(type(plan['packet_sha256']) is str and re.fullmatch('[0-9a-f]{64}',plan['packet_sha256']),'FULL_PACKET_BINDING_REQUIRED')
    blobs=verified_modules(plan['source_modules_sha256'])
    raw=(PACKET/'fixtures.json').read_bytes();require(sha(raw)==FIXTURES_SHA,'CTX01_PACKET_DRIFT');packet=unique_json(raw)
    require(packet['schema']=='workinants.context-control-fixtures.v1' and packet['status']=='NOT_RUN' and packet['database_posture']=='D','CTX01_PACKET_SCOPE')
    require(digest({k:packet[k] for k in ('source_files_sha256','prepared_files_sha256')})==CONTENT_SHA==packet['source_only_packet_sha256'],'CTX01_CONTENT_AGGREGATE')
    for path,value in packet['source_files_sha256'].items():require(sha(source_file(path).read_bytes())==value,'CTX01_SOURCE_INPUT_DRIFT')
    for name,value in packet['prepared_files_sha256'].items():require(sha(packet_file(name).read_bytes())==value,'CTX01_PREPARED_FILE_DRIFT')
    require(plan['scenario_names']==[case['name'] for case in packet['cases']] and len(packet['cases'])==31,'EXACT_31_CASES_REQUIRED')
    docs={}
    for key in ('native_snapshot','native_comparison','native_attestation'):
        entry=plan[key];require(type(entry) is dict and set(entry)=={'path','sha256'},'NATIVE_FILE_BINDING_FIELDS')
        value=external_file(entry['path']).read_bytes();require(sha(value)==entry['sha256'],'NATIVE_FILE_DRIFT');docs[key]=unique_json(value)
    native,comparison,attestation=(docs[k] for k in ('native_snapshot','native_comparison','native_attestation'))
    require(native.get('format')=='workinants.native-catalog.v1' and type(native.get('server_version_num')) is int and native['server_version_num']==170011 and native.get('read_only') is True and native.get('collected_as')=='postgres' and native.get('collector_is_superuser') is True,'REVIEWED_NATIVE_REQUIRED')
    counts=comparison.get('check_counts')
    require(comparison.get('format')=='workinants.catalog-comparison.v1' and comparison.get('status')=='PASS' and comparison.get('native_snapshot_sha256')==digest(native) and comparison.get('source_expected_sha256')==EXPECTED_CATALOG and comparison.get('findings')==[] and type(counts) is dict and set(counts)<={'PASS','FAIL','INCOMPLETE'} and all(type(v) is int and v>=0 for v in counts.values()) and counts.get('PASS',0)>0 and counts.get('FAIL',0)==counts.get('INCOMPLETE',0)==0,'REVIEWED_NATIVE_PASS_REQUIRED')
    # The comparator has no run/CID fields. This separately hashed external
    # attestation is mandatory and must be supplied by the reviewed root runner.
    expected={'schema':'workinants.context-native-attestation.v1','run_id':plan['run_id'],'container_id':plan['immutable_container_id'],'source_commit':plan['source_commit'],'source_tree':plan['source_tree'],'packet_sha256':plan['packet_sha256'],'collector_sha256':plan['source_modules_sha256'][COLLECTOR],'source_expected_sha256':EXPECTED_CATALOG,'native_snapshot_sha256':digest(native),'native_comparison_file_sha256':plan['native_comparison']['sha256'],'original_grantor_finalized':True,'operation_backends_absent':True,'comparison_status':'PASS'}
    exact(attestation,expected,'SAME_RUN_NATIVE_ATTESTATION_REQUIRED')
    load_helpers(blobs)
    target=HOST['validate_manifest'](plan['target_manifest'])
    require(target['run_id']==plan['run_id'] and target['source']['integrated_sql_sha256']==packet['source_files_sha256']['review-output/foundation-application.review.sql'],'TARGET_RUN_SOURCE_MISMATCH')
    verified_modules(plan['source_modules_sha256'])
    return packet,native,target


def binder_diagnostic(stderr,message,application):
    require(message in ('invalid context','invalid, stale or unsupported context'),'UNREGISTERED_BINDER_DIAGNOSTIC')
    found=list(re.finditer(r'CREATE FUNCTION platform_private\.bind_request_context\(secret text\).*?AS\s+(\$[a-z_0-9]*\$)(.*?)\1;',application,re.S))
    require(len(found)==1,'BINDER_SOURCE_BODY_REQUIRED');body=found[0][2]
    lines=[i for i,line in enumerate(body.split('\n'),1) if 'RAISE EXCEPTION '+quote(message) in line]
    require(len(lines)==1,'BINDER_SOURCE_LINE_REQUIRED')
    text=stderr.replace('\r\n','\n');clean=all(c in '\n\t' or c.isprintable() for c in text)
    rows=text.split('\n');headers=[m for line in rows if (m:=HEADER.fullmatch(line))]
    candidates=[line for line in rows if re.search(r'\b(?:ERROR|FATAL|PANIC|WARNING)\b',line)]
    frames=[line for line in rows if 'PL/pgSQL function ' in line];frame=FRAME.fullmatch(frames[0]) if len(frames)==1 else None
    good=clean and len(headers)==len(candidates)==1 and headers[0][1]=='42501' and headers[0][2]==message and frame is not None and int(frame[1])==lines[0]
    return {'matched':bool(good),'sqlstate':'42501' if good else None,'source_frame_verified':bool(good),'source_body_sha256':sha(body.encode()) if good else None,'source_body_line':lines[0] if good else None,'classification':'EXPECTED_BINDER_SOURCE_GUARD' if good else 'UNLISTED_OR_INCOMPLETE_DISCARDED'}


class Evidence:
    def __init__(self,directory,packet):
        directory.mkdir(parents=True,exist_ok=False);self.path=directory/'context-control-results.json'
        self.value={'schema':'workinants.context-control-evidence.v1','status':'IN_PROGRESS','current_stage':'ENTRY','current_case':None,'current':{},'operations':[],'results':[],'authentication':[],'cleanup_required':True,'subsequent_cases_stopped':False,'database_posture':'D','reviewed_content_sha256':CONTENT_SHA,'selected_controls':[{'id':'P0C-CTX-01','status':'NOT_RUN'}],'unprepared_obligations':deepcopy(packet['unprepared_obligations'])};self.save()
    def save(self):
        temporary=self.path.with_suffix('.json.tmp')
        with temporary.open('w',encoding='utf8',newline='\n') as handle:handle.write(json.dumps(self.value,indent=2)+'\n');handle.flush();os.fsync(handle.fileno())
        temporary.replace(self.path)
    def stage(self,name):self.value['current_stage']=name;self.save()


class Session:
    """One actual login; all context handles and tuple fields remain in memory."""
    def __init__(self,role,coordinator):
        require(role in ROLES,'ACTUAL_LOGIN_REQUIRED');self.role=role;self.coordinator=coordinator;self.backend=None;self.active=False;self.closed=False;self.last_errors='';self.expected_failure=False
        self.lines=queue.Queue(maxsize=256);self.errors=[];self.invalid=threading.Event()
        self.process=subprocess.Popen(coordinator.psql(role),stdin=subprocess.PIPE,stdout=subprocess.PIPE,stderr=subprocess.PIPE,text=True,bufsize=1,shell=False)
        def output():
            try:
                while line:=self.process.stdout.readline(65537):
                    if len(line)>65536:self.invalid.set();continue
                    try:self.lines.put_nowait(line.rstrip('\r\n'))
                    except queue.Full:self.invalid.set()
            except BaseException:self.invalid.set()
        def errors():
            size=0
            try:
                while chunk:=self.process.stderr.read(4096):
                    size+=len(chunk)
                    if size<=65536:self.errors.append(chunk)
                    else:self.invalid.set()
            except BaseException:self.invalid.set()
        self.readers=[threading.Thread(target=output,daemon=True),threading.Thread(target=errors,daemon=True)]
        for reader in self.readers:reader.start()
    def call(self,text):
        require(not self.closed and self.process.poll() is None,'SESSION_ALREADY_ENDED')
        ack=ACK_PREFIX+secrets.token_hex(16);self.process.stdin.write(text+'\nSELECT '+quote(ack)+';\n');self.process.stdin.flush()
        output=[];confirmed=False;deadline=time.monotonic()+15
        while time.monotonic()<deadline:
            try:line=self.lines.get(timeout=.1)
            except queue.Empty:
                if self.process.poll() is not None:break
                continue
            if line==ack:confirmed=True;break
            if line:output.append(line)
        if not confirmed:
            self.process.wait(timeout=10)
            for reader in self.readers:reader.join(timeout=5)
            while not self.lines.empty():
                line=self.lines.get_nowait()
                if line:output.append(line)
        require(not self.invalid.is_set(),'SESSION_OUTPUT_INCOMPLETE')
        if confirmed and re.search(r'\b(?:COMMIT|ROLLBACK);\s*$',text):self.active=False
        self.last_errors=''.join(self.errors)
        return output,confirmed,self.last_errors
    def begin(self,isolation):
        require(not self.active and isolation in ('read committed','repeatable read','serializable'),'SESSION_BEGIN_STATE')
        rows,ack,errors=self.call('BEGIN ISOLATION LEVEL '+isolation.upper()+"; SET LOCAL statement_timeout='5s'; SET LOCAL lock_timeout='1s'; SET LOCAL idle_in_transaction_session_timeout='30s';")
        require(ack and not rows and not errors,'SESSION_BEGIN_UNCONFIRMED');self.active=True;self.isolation=isolation
    def capture(self):
        require(self.active,'CAPTURE_REQUIRES_LIVE_TRANSACTION')
        text="SELECT "+quote(TUPLE)+"||jsonb_build_object('login',session_user,'current_user',current_user,'database',current_database(),'isolation',current_setting('transaction_isolation'),'pid',pg_backend_pid()::text,'xid',pg_current_xact_id()::text,'started',(SELECT backend_start::text FROM pg_stat_activity WHERE pid=pg_backend_pid()),'clock',CURRENT_TIMESTAMP::text)::text;"
        rows,ack,errors=self.call(text);require(ack and not errors and len(rows)==1 and rows[0].startswith(TUPLE),'CAPTURE_OUTPUT_REQUIRED')
        value=unique_json(rows[0][len(TUPLE):]);require(type(value) is dict and set(value)=={'login','current_user','database','isolation','pid','xid','started','clock'},'CAPTURE_FIELDS')
        require(value['login']==value['current_user']==self.role and value['database']==DATABASE and value['isolation']==self.isolation,'CAPTURE_ACTUAL_IDENTITY')
        for key,pattern in [('pid','[1-9][0-9]{0,9}'),('xid','[1-9][0-9]{0,19}'),('started',r'[0-9T:+. \-]{1,64}'),('clock',r'[0-9T:+. \-]{1,64}')]:require(type(value[key]) is str and re.fullmatch(pattern,value[key]),'CAPTURE_TUPLE_FORMAT')
        if self.backend is not None:require((value['pid'],value['started'])==(self.backend['pid'],self.backend['started']),'SESSION_BACKEND_CHANGED')
        self.backend=value;return value
    def close(self):
        if self.closed:return self.process.returncode
        if self.process.poll() is None:
            try:
                self.process.stdin.write(('ROLLBACK;\n' if self.active else '')+'\\q\n');self.process.stdin.close();self.process.wait(timeout=10)
            except (OSError,ValueError,subprocess.TimeoutExpired):
                self.process.terminate()
                try:self.process.wait(timeout=10)
                except subprocess.TimeoutExpired:self.process.kill();self.process.wait(timeout=10)
        for reader in self.readers:reader.join(timeout=5)
        require(self.process.poll() is not None and self.backend is not None and not any(r.is_alive() for r in self.readers),'SESSION_CLOSURE_UNCONFIRMED')
        output_complete=not self.invalid.is_set() and not any(line for line in list(self.lines.queue)) and ''.join(self.errors)==self.last_errors
        require(type(self.process.returncode) is int and 0<=self.process.returncode<=255,'SESSION_TERMINAL_EXIT_UNCONFIRMED')
        b=self.backend;query='SELECT count(*) FROM pg_stat_activity WHERE pid='+b['pid']+' AND backend_start='+quote(b['started'])+'::timestamptz AND usename='+quote(self.role)+' AND datname='+quote(DATABASE)+';'
        require(self.coordinator.raw('postgres',query)=='0','EXACT_BACKEND_STILL_LIVE');self.closed=True
        require(output_complete,'UNOBSERVED_SESSION_OUTPUT');return self.process.returncode


class Coordinator:
    def __init__(self,plan,packet,native,target,evidence,session_factory=Session):
        self.plan,self.packet,self.native,self.target,self.evidence=plan,packet,native,target,evidence
        self.container=plan['immutable_container_id'];self.session_factory=session_factory;self.instances={};self.retired=set();self.sequence=0
        path='review-output/foundation-application.review.sql';raw=source_file(path).read_bytes()
        require(sha(raw)==packet['source_files_sha256'][path],'CANONICAL_APPLICATION_SOURCE_DRIFT');self.application=raw.decode('utf8')
    def psql(self,role):
        require(role in ROLES,'ACTUAL_LOGIN_REQUIRED');args=API['psql'](role,self.container)
        pos=args.index(self.container);return args[:pos]+['-e','PGAPPNAME=wa-ctx01-'+self.plan['run_id']]+args[pos:]
    def raw(self,role,text):
        result=subprocess.run(self.psql(role),input=text,text=True,capture_output=True,timeout=60,shell=False)
        require(type(result.returncode) is int and result.returncode==0 and not result.stderr.strip(),'INDEPENDENT_SQL_UNCONFIRMED')
        require(len(result.stdout.encode('utf8'))<=16*1024*1024,'INDEPENDENT_OUTPUT_LIMIT');return result.stdout.strip()
    def text(self,name):
        raw=packet_file(name).read_bytes();require(sha(raw)==self.packet['prepared_files_sha256'][name],'CTX01_SQL_CHANGED');return raw.decode('utf8')
    def record(self,value):self.evidence.value['operations'].append(value);self.evidence.save()
    def observe(self,name,text,expected):
        self.evidence.stage(name);value=unique_json(self.raw('postgres',text))
        # Only expected typed values may enter evidence; arbitrary rows never do.
        good=canonical(value)==canonical(expected)
        self.record({'stage':name,'shape_and_values_match':good,'observation':bounded_outcomes(value,expected)});require(good,'COMPLETE_STATE_OBSERVER_MISMATCH');return value
    def session(self,role):return self.session_factory(role,self)
    def commit(self,role,text,label):
        session=self.session(role);record={'stage':label,'actual_login':role,'commit_acknowledged':False,'operation_closed':False}
        self.last_transaction=record
        self.record(record)
        try:
            session.begin('read committed');session.capture()
            match=re.match(r'\A(?:(?:\s|--[^\n]*\n)*)BEGIN;',text)
            require(match is not None and text.rstrip().endswith('COMMIT;'),'PRIVILEGED_TRANSACTION_SHAPE')
            rows,ack,errors=session.call(text[match.end():]);record['commit_acknowledged']=ack and not rows and not errors
            require(record['commit_acknowledged'],'ISSUER_OR_PRIVILEGED_COMMIT_UNCONFIRMED')
        finally:
            try:code=session.close()
            finally:record['operation_closed']=session.closed;self.evidence.save()
            require(type(code) is int and code==0,'PRIVILEGED_TERMINAL_EXIT_UNEXPECTED')
    def grant_values(self,template,backend,issuer,identity,token_hash):
        require(template['database_login_role'] in ('wa_app_runtime','wa_worker') and backend['login'] in ('wa_app_runtime','wa_worker'),'DECLARED_GRANT_LOGIN')
        require(backend['current_user']==backend['login'] and issuer['login']=='wa_context_issuer','EXACT_ISSUER_TUPLE')
        for value in (backend,issuer):
            require(type(value.get('pid')) is str and re.fullmatch('[1-9][0-9]{0,9}',value['pid']) and type(value.get('xid')) is str and re.fullmatch('[1-9][0-9]{0,19}',value['xid']),'CAPTURED_GRANT_TUPLE_FORMAT')
        require(type(issuer.get('clock')) is str and re.fullmatch(r'[0-9T:+. \-]{1,64}',issuer['clock']),'CAPTURED_ISSUER_CLOCK_FORMAT')
        require(type(token_hash) is str and re.fullmatch('[0-9a-f]{64}',token_hash) and str(uuid.UUID(identity))==identity and uuid.UUID(identity).version==4,'FRESH_GRANT_ID_AND_HASH_REQUIRED')
        fields=template['allowed_fields'];require(fields==sorted(set(fields)) and fields and len(fields)<=1024 and all(type(f) is str and '*' not in f for f in fields),'FINITE_CAPABILITIES_REQUIRED')
        principal,service=template.get('principal_user_id'),template.get('service_principal')
        require((principal is None)!=(service is None),'ONE_GRANT_PRINCIPAL_REQUIRED')
        values={'id':quote(identity)+'::uuid','token_hash':quote(token_hash),'issuer_service':quote('wa_context_issuer'),'principal_user_id':'NULL::uuid' if principal is None else quote(principal)+'::uuid','service_principal':'NULL::text' if service is None else quote(service),'database_login_role':quote(template['database_login_role']),'owner_module_id':quote(template['owner_module_id']),'action':quote(template['action']),'purpose':quote(template['purpose']),'target_kind':quote(template['target_kind']),'target_id':quote(template['target_id']),'allowed_fields':'ARRAY['+','.join(quote(f) for f in fields)+']::text[]','policy_version':quote(template.get('policy_version','ctx01-source-fixture.v1')),'security_generation':str(int(template['security_generation'])),'source_generation':str(int(template['source_generation'])),'backend_pid':backend['pid'],'transaction_id':quote(backend['xid']),'expires_at':quote(issuer['clock'])+"::timestamptz+interval '300 seconds'",'revoked_at':'NULL::timestamptz','created_at':quote(issuer['clock'])+'::timestamptz','mutation_transaction_id':quote(issuer['xid'])}
        require(set(values)==set(GRANT_COLUMNS),'GRANT_COLUMN_CLOSURE');return values
    def issue(self,template,backend):
        self.sequence+=1;require(self.sequence<=self.packet['finite_caps']['grant_instances_max'],'FINITE_GRANT_INSTANCE_LIMIT')
        identity=str(uuid.uuid4());secret=secrets.token_hex(32);token_hash=sha(bytes.fromhex(secret));issuer=self.session('wa_context_issuer')
        record={'stage':'SEPARATE_ISSUER_COMMIT','issuer_committed':False,'commit_acknowledged':False,'created_at_return_verified':False,'operation_closed':False};self.record(record)
        try:
            issuer.begin('read committed');captured=issuer.capture();values=self.grant_values(template,backend,captured,identity,token_hash)
            rows,ack,errors=issuer.call('INSERT INTO platform.database_action_grant ('+','.join(GRANT_COLUMNS)+') VALUES ('+','.join(values[k] for k in GRANT_COLUMNS)+") RETURNING pg_catalog.jsonb_build_object('created_at',created_at); COMMIT;")
            record['commit_acknowledged']=ack is True;self.evidence.save()
            require(ack is True and not errors,'SEPARATE_ISSUER_COMMIT_UNCONFIRMED')
            actual_created_at=returned_created_at(rows,captured['clock'])
            values['created_at']=quote(actual_created_at)+'::timestamptz'
            record['created_at_return_verified']=True;record['issuer_committed']=True;self.evidence.save()
        finally:
            try:code=issuer.close()
            finally:record['operation_closed']=issuer.closed;self.evidence.save()
            require(type(code) is int and code==0,'ISSUER_TERMINAL_EXIT_UNEXPECTED')
        instance={'id':identity,'secret':secret,'token_hash':token_hash,'values':values,'backend':deepcopy(backend),'login':template['database_login_role']}
        self.instances[self.sequence]=instance;return self.sequence
    def retention(self,instances):
        if not instances:return
        require(len(instances)==len(set(instances)) and all(i in self.instances for i in instances),'ISSUED_INSTANCE_SET_REQUIRED')
        rows=[]
        for key in instances:
            value=self.instances[key]['values'];comparison=' AND '.join('g.'+k+' IS NOT DISTINCT FROM ('+value[k]+')' for k in GRANT_COLUMNS)
            rows.append('SELECT g.id,('+comparison+') AS exact, g.issuer_service=session_user::text AS issuer_owned, g.revoked_at IS NULL AS revoked_false, g.expires_at>clock_timestamp() AS unexpired FROM platform.database_action_grant g WHERE g.id='+value['id'])
        query="SELECT jsonb_build_object('exact_count',count(*),'all_immutable_fields_equal',coalesce(bool_and(exact),false),'issuer_owned',coalesce(bool_and(issuer_owned),false),'revoked_false',coalesce(bool_and(revoked_false),false),'unexpired',coalesce(bool_and(unexpired),false)) FROM ("+' UNION ALL '.join(rows)+') observed;'
        result=unique_json(self.raw('wa_context_issuer',query));expected={'exact_count':len(instances),'all_immutable_fields_equal':True,'issuer_owned':True,'revoked_false':True,'unexpired':True}
        good=canonical(result)==canonical(expected);self.record({'stage':'ISSUER_ROW_RETENTION','instances':len(instances),'immutable_issuer_rows_match':good,'observation':bounded_outcomes(result,expected)});require(good,'ISSUER_ROW_RETENTION_NOT_PROVEN')
    def stale(self,session,secret,message):
        rows,ack,errors=session.call('SELECT platform_private.bind_request_context('+quote(secret)+');')
        code=session.process.poll();diagnostic=binder_diagnostic(errors,message,self.application)
        self.record({'stage':'EXPECTED_BINDER_FAILURE','exit_code':code if type(code) is int else None,'acknowledged':bool(ack),'unexpected_stdout':bool(rows),'diagnostic':diagnostic})
        require(type(code) is int and code==3 and not rows and not ack and diagnostic['matched'],'EXPECTED_SOURCE_BINDER_FAILURE_NOT_PROVEN')
        session.expected_failure=True
    def retire(self,instances):
        self.retention(instances)
        for key in instances:
            require(key not in self.retired,'INSTANCE_RETIREMENT_REUSED');instance=self.instances[key];session=self.session(instance['login'])
            try:
                session.begin('read committed');backend=session.capture();require(backend['xid']!=instance['backend']['xid'],'RETIREMENT_REQUIRES_NEW_XID')
                self.stale(session,instance['secret'],'invalid, stale or unsupported context')
            finally:session.close()
            self.retired.add(key);self.record({'stage':'OLD_INSTANCE_RETIREMENT','stale_source_guard':True,'operation_closed':True})
        self.retention(instances)
    def run_protocol(self,name,role,steps):
        self.evidence.value.update(current_case=name,current={'completed_steps':0,'all_original_sessions_closed':False});self.evidence.stage('FINITE_CONTEXT_PROTOCOL')
        sessions={};labels={};instances={};issued=[];failure=None
        try:
            for index,step in enumerate(steps):
                op=step['op'];sid=step.get('session')
                self.evidence.value['current'].update(step_index=index,operation=op);self.evidence.stage('CTX01_'+op.upper())
                if sid is not None and sid not in sessions:require(sid in ('A','B') and len(sessions)<2,'FINITE_SESSION_LIMIT');sessions[sid]=self.session(role)
                session=sessions.get(sid)
                if op=='begin':session.begin(step['isolation'])
                elif op=='capture':
                    if not session.active:session.begin('read committed')
                    backend=session.capture()
                    other=step.get('require_same_backend_as')
                    if other:require((backend['pid'],backend['started'])==(labels[other]['pid'],labels[other]['started']),'SAME_POOL_BACKEND_NOT_PROVEN')
                    other=step.get('require_distinct_backend_from')
                    if other:require(backend['pid']!=labels[other]['pid'],'DIFFERENT_BACKEND_NOT_PROVEN')
                    prior=step.get('require_distinct_xid_from',[]);prior=[prior] if type(prior) is str else prior
                    require(all(backend['xid']!=labels[p]['xid'] for p in prior),'NEW_POOL_XID_NOT_PROVEN')
                    if 'tuple_label' in step:require(step['tuple_label'] not in labels,'DUPLICATE_TUPLE_LABEL');labels[step['tuple_label']]=deepcopy(backend)
                elif op=='issue':
                    require(step['instance'] not in instances and session.backend is not None,'INSTANCE_ISSUANCE_STATE')
                    key=self.issue(self.packet['grants'][step['template']],session.backend);instances[step['instance']]=key;issued.append(key)
                elif op=='bind':
                    secret=self.instances[instances[step['instance']]]['secret'];rows,ack,errors=session.call('SELECT platform_private.bind_request_context('+quote(secret)+');');require(ack and not rows and not errors,'LEGITIMATE_CONTEXT_BIND_FAILED')
                elif op=='expect_bind_error':
                    if step['instance']=='UNISSUED_FRESH_SECRET':
                        secret=secrets.token_hex(32);query='SELECT NOT EXISTS(SELECT 1 FROM platform.database_action_grant WHERE token_hash='+quote(sha(bytes.fromhex(secret)))+');';require(self.raw('postgres',query)=='t','UNISSUED_TOKEN_ROW_EXISTS')
                    elif step['instance']=='MALFORMED_RUNTIME_SECRET':secret='ctx01-malformed'
                    else:secret=self.instances[instances[step['instance']]]['secret']
                    self.stale(session,secret,step['diagnostic']['exact_message'])
                elif op=='sql':
                    rows,ack,errors=session.call(self.text(step['file']));require(ack and not errors,'CONTEXT_SQL_ACK_NOT_PROVEN')
                    expected=step['expected']
                    if type(expected) is dict and 'marker' in expected:exact(rows,[expected['marker']],'SOURCE_TRANSACTION_MARKER_REQUIRED')
                    elif expected is None:exact(rows,[],'UNEXPECTED_CONTEXT_SQL_OUTPUT')
                    else:require(len(rows)==1,'CONTEXT_SQL_ONE_RECORD_REQUIRED');exact(unique_json(rows[0]),expected,'CONTEXT_SQL_OBSERVATION_MISMATCH')
                elif op=='close':
                    code=session.close();require(type(code) is int and code==(3 if session.expected_failure else 0),'PROTOCOL_TERMINAL_EXIT_UNEXPECTED')
                elif op=='observer':
                    require(all(s.closed for s in sessions.values()),'OBSERVER_BEFORE_ALL_ORIGINAL_CLOSURES')
                    if step['file']=='grant-retention':self.retention([instances[k] for k in step['instances']])
                    else:self.observe('SOURCE_COMPLETE_STATE',self.text(step['file']),step['expected'])
                else:raise HeldFailure('UNKNOWN_PACKET_PROTOCOL_OPERATION')
                self.evidence.value['current']['completed_steps']=index+1;self.evidence.save()
        except BaseException as error:failure=error
        finally:
            closed=True
            for session in sessions.values():
                try:session.close()
                except BaseException:closed=False
            self.evidence.value['current']['all_original_sessions_closed']=closed;self.evidence.save()
            if not closed:raise HeldFailure('PROTOCOL_CLOSURE_UNCONFIRMED') from None
        if failure is not None:
            self.observe('TRIGGER_RESTORATION_AFTER_FAILURE',self.text('fixture-trigger-restore-observe.sql'),self.packet['fixture_trigger_contract']['observer_expected'])
            self.native_unchanged()
            raise failure
        self.retire(issued)
        self.record({'stage':'PROTOCOL_COMPLETE','scenario':name,'issued_instances':len(issued),'all_retirement_probes_closed':True})
    def complete_state(self):
        for row in self.packet['mandatory_after_case_observers']:self.observe('COMPLETE_'+Path(row['file']).stem.upper().replace('-','_'),self.text(row['file']),row['expected'])
        self.native_unchanged()
    def native_unchanged(self):
        self.evidence.stage('VERIFY_NATIVE_COLLECTOR_SOURCE')
        raw=source_file(COLLECTOR).read_bytes()
        require(sha(raw)==self.plan['source_modules_sha256'][COLLECTOR],'NATIVE_COLLECTOR_SOURCE_DRIFT')
        self.evidence.stage('OBSERVE_NATIVE_CATALOG')
        actual=unique_json(self.raw('postgres',raw.decode('utf8')));good=digest(actual)==digest(self.native)
        self.record({'stage':'NATIVE_CATALOG_PRESERVATION','unchanged':good});require(good,'NATIVE_CATALOG_DRIFT')
    def resource(self):
        context=HOST['docker_json'](['context','inspect','desktop-linux'],subprocess.run)
        container=HOST['docker_json'](['inspect',self.container],subprocess.run)
        volume=HOST['docker_json'](['volume','inspect',self.target['target']['volume_name']],subprocess.run)
        observed=HOST['inspect_live'](self.target,context,container,volume);require(observed['container_id']==self.container,'CURRENT_CREATED_CID_MISMATCH')
        image=HOST['docker_json'](['image','inspect',self.target['target']['image']],subprocess.run);HOST['verify_image'](self.target,container,image)
        self.record({'stage':'RESOURCE_PREFLIGHT','immutable_created_CID_verified':True})
    def preflight(self):
        self.resource();self.native_unchanged();API['authentication_preflight'](self.evidence,self.container)
        require(self.raw('postgres',"SELECT current_setting('server_version_num')='170011' AND current_setting('log_statement')='none' AND current_setting('log_min_error_statement')='panic' AND current_setting('password_encryption')='scram-sha-256';")=='t','SAFE_SERVER_SETTINGS_REQUIRED')
        require(self.raw('postgres',"SELECT NOT EXISTS(SELECT 1 FROM pg_auth_members WHERE member='wa_schema_owner'::regrole AND roleid=ANY(ARRAY['wa_private_helper_owner'::regrole,'wa_customer_verifier'::regrole,'wa_track_verifier'::regrole])) AND NOT has_schema_privilege('wa_private_helper_owner','platform_private','CREATE') AND NOT has_schema_privilege('wa_customer_verifier','platform_private','CREATE') AND NOT has_schema_privilege('wa_track_verifier','platform_private','CREATE');")=='t','ORIGINAL_GRANTOR_FINALIZATION_REQUIRED')
        self.observe('TRIGGER_RESTORATION',self.text('fixture-trigger-restore-observe.sql'),self.packet['fixture_trigger_contract']['observer_expected'])
        ids=self.packet['namespace_policy']['ids'];tables={'CustomerProfile':'app.customer_profiles','RuntimeCommandReceipt':'platform.runtime_command_receipt','CustomerProfileLifecycleEvent':'app.customer_profile_lifecycle_event','OwnerMutationEvidence':'platform.owner_mutation_evidence','event':'platform.runtime_outbox_message','free':'platform.runtime_outbox_message','extra':'platform.runtime_outbox_message','duplicate':'platform.runtime_command_receipt','user':'app.users','grant':'platform.database_action_grant','work':'platform.runtime_work_item','identity_bootstrap':'platform_private.identity_service_receipt','user_security':'app.user_security_profiles'}
        checks=['NOT EXISTS(SELECT 1 FROM '+tables[k]+' WHERE id='+quote(v)+'::uuid)' for k,v in ids.items()]
        service=quote(self.packet['namespace_policy']['service_principal']);checks+=['NOT EXISTS(SELECT 1 FROM platform_private.identity_service_authorization WHERE service_principal='+service+')','NOT EXISTS(SELECT 1 FROM platform_private.identity_service_receipt WHERE service_principal='+service+')','NOT EXISTS(SELECT 1 FROM platform.database_action_grant WHERE service_principal='+service+' OR principal_user_id='+quote(ids['user'])+'::uuid)',"NOT EXISTS(SELECT 1 FROM platform.database_action_grant WHERE token_hash='"+'0'*64+"')"]
        require(self.raw('postgres','SELECT '+' AND '.join(checks)+';')=='t','FRESH_CTX01_NAMESPACE_REQUIRED')
    def run(self):
        self.preflight()
        try:self.commit('postgres',self.text('trusted-identity-fixtures.sql'),'TRUSTED_IDENTITY_FIXTURES')
        finally:
            require(getattr(self,'last_transaction',{}).get('operation_closed') is True,'SETUP_CLOSURE_UNCONFIRMED')
            self.observe('TRIGGER_RESTORATION_AFTER_SETUP',self.text('fixture-trigger-restore-observe.sql'),self.packet['fixture_trigger_contract']['observer_expected'])
        self.run_protocol('source-creation-lifetime','wa_app_runtime',self.packet['source_creation_lifetime_protocol']['steps'])
        self.commit('wa_identity_service_authority',self.text('identity-bootstrap.sql'),'INDEPENDENT_IDENTITY_BOOTSTRAP')
        setup=[{'op':'capture','session':'A'},{'op':'issue','session':'A','instance':'SCHEDULE','template':'schedule'},{'op':'bind','session':'A','instance':'SCHEDULE'},{'op':'sql','session':'A','file':'schedule.sql','expected':{'marker':'WA_CTX01_SCHEDULE_READY','transaction_end':'COMMIT_ACK'}},{'op':'close','session':'A'}]
        self.run_protocol('one-pending-work-schedule','wa_app_runtime',setup);self.complete_state()
        for case in self.packet['cases']:
            self.run_protocol(case['name'],case['actual_login'],case['steps']);self.complete_state()
            self.evidence.value['results'].append({'name':case['name'],'status':'PASS_FINITE_SCENARIO_ONLY_NOT_SELECTED_CONTROL'});self.evidence.save()
        require(self.retired==set(self.instances) and len(self.retired)==30,'ALL_30_INSTANCES_MUST_BE_RETIRED')
        verified_modules(self.plan['source_modules_sha256'])
        require(sha((PACKET/'fixtures.json').read_bytes())==FIXTURES_SHA and all(sha(source_file(p).read_bytes())==h for p,h in self.packet['source_files_sha256'].items()) and all(sha(packet_file(p).read_bytes())==h for p,h in self.packet['prepared_files_sha256'].items()),'POST_RUN_SOURCE_PACKET_DRIFT')
        self.evidence.value['source_packet_unchanged_after_run']=True
        self.evidence.value.update(status='PASS_CTX01_PREPARED_SQL_PROTOCOLS_ONLY_CONTROLS_NOT_RUN',current_stage='COMPLETE');self.evidence.save()


def failure_code(error):
    if isinstance(error,HeldFailure):return error.code
    if isinstance(error,KeyboardInterrupt):return 'INTERRUPTED'
    if isinstance(error,(subprocess.TimeoutExpired,queue.Empty)):return 'TIMEOUT_CLOSURE_UNCONFIRMED'
    return 'INVALID_RESPONSE_OR_INTERNAL'


def main(argv=None,dependencies=None):
    dependencies=dependencies or {};parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--execute-reviewed-context-controls',action='store_true');parser.add_argument('--reviewed-run-plan',type=Path);parser.add_argument('--evidence-directory',type=Path)
    args=parser.parse_args(argv);evidence=None
    try:
        require(args.execute_reviewed_context_controls and args.reviewed_run_plan and args.evidence_directory,'EXPLICIT_REVIEWED_EXECUTION_REQUIRED')
        raw=external_file(str(args.reviewed_run_plan)).read_bytes();plan=unique_json(raw)
        packet,native,target=(dependencies.get('load_inputs') or load_inputs)(plan)
        directory=external_file(str(args.evidence_directory));require(not directory.exists(),'FRESH_EVIDENCE_DIRECTORY_REQUIRED')
        evidence=(dependencies.get('evidence') or Evidence)(directory,packet)
        evidence.value.update(reviewed_run_plan_sha256=sha(raw),run_id=plan['run_id'],container_id=plan['immutable_container_id'],source_commit=plan['source_commit'],source_tree=plan['source_tree'],packet_sha256=plan['packet_sha256']);evidence.save()
        coordinator=(dependencies.get('coordinator') or Coordinator)(plan,packet,native,target,evidence);coordinator.run();return 0
    except BaseException as error:
        code=failure_code(error)
        if evidence is not None:evidence.value.update(status='STOPPED_RETAINED_FOR_CONTROLLED_CLEANUP',subsequent_cases_stopped=True,failure={'code':code,'stage':evidence.value['current_stage']});evidence.save()
        print(json.dumps({'schema':'workinants.context-control-summary.v1','status':'REFUSED_OR_STOPPED','code':code,'raw_output_discarded':True}));return 1


if __name__=='__main__':raise SystemExit(main())
