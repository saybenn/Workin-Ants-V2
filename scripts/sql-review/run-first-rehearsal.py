"""Dormant three-case coordinator. Separate Brain execution approval required.

Never creates/starts/pulls resources. Credentials come from private tmpfs; only
allowlisted structured evidence leaves memory. Offline tests mock ALL processes.
"""
import argparse
import hashlib
import ipaddress
import json
import os
from pathlib import Path
import queue
import re
import secrets
import subprocess
import threading

ROOT=Path(__file__).resolve().parents[2]
FIXTURES=ROOT/'review-output/first-rehearsal'
CONTAINER='wa-p0c-first-20261110-ok'
DATABASE='wa_p0c_rehearsal'
ROLES=('wa_migrator','wa_context_issuer','wa_identity_service_authority','wa_app_runtime','wa_worker')
MARKERS=('WA_COMMAND_INSERTED','WA_CUSTOMER_INSERTED','WA_READY_TO_COMMIT')
DIAGNOSTICS={('42501','foreign Customer principal'):'CUSTOMER_PRINCIPAL_GUARD',
             ('P0001','missing durable default-Free intent'):'CUSTOMER_DEFAULT_FREE_GUARD'}
EXPECTED={'positive':(None,'NONE'),'wrong-person':('42501','CUSTOMER_PRINCIPAL_GUARD'),
          'missing-outbox':('P0001','CUSTOMER_DEFAULT_FREE_GUARD')}

class HeldFailure(Exception):
    """Fixed metadata only; never a subprocess exception/string or SQL body."""
    def __init__(self,code):
        self.code=code
        super().__init__(code)

def require(condition,code):
    if not condition:raise HeldFailure(code)

def quote(s):return "'"+str(s).replace("'","''")+"'"

def grant_sql(case,login,pid,xid,token_hash):
    if login!='wa_app_runtime' or not re.fullmatch(r'[0-9]+',str(pid)) or not re.fullmatch(r'[0-9]+',str(xid)) or not re.fullmatch(r'[0-9a-f]{64}',token_hash):raise ValueError('invalid captured runtime tuple/hash')
    fields='ARRAY['+','.join(quote(f) for f in case['allowed_fields'])+']::text[]'
    return "BEGIN; INSERT INTO platform.database_action_grant (id,token_hash,issuer_service,principal_user_id,service_principal,database_login_role,owner_module_id,action,purpose,target_kind,target_id,allowed_fields,policy_version,security_generation,source_generation,backend_pid,transaction_id,expires_at) VALUES ("+','.join([quote(case['grant_id']),quote(token_hash),"'wa_context_issuer'",quote(case['principal_user_id']),'NULL',quote(login),"'customer_buyer_profile'","'SH-004.v1'","'provision'","'CustomerProfile'",quote(case['ids']['CustomerProfile']),fields,"'first-rehearsal.v1'",'0','0',str(pid),quote(xid),"clock_timestamp()+interval '5 minutes'"])+"); COMMIT;\n"

def psql(role,container=CONTAINER,wrong_password=False):
    env=['-e','PGPASSFILE=/dev/null','-e','PGPASSWORD'] if wrong_password else ['-e','PGPASSFILE=/run/wa-secrets/pgpass']
    return ['docker','--context','desktop-linux','exec','-i',*env,container,'psql','-X','-w','-qAt','-v','ON_ERROR_STOP=1','-v','VERBOSITY=verbose','-v','SHOW_CONTEXT=never','-h','127.0.0.1','-p','5432','-U',role,'-d',DATABASE]

def run(role,sql,container=CONTAINER):
    r=subprocess.run(psql(role,container),input=sql,text=True,capture_output=True,timeout=60)
    require(r.returncode==0,'SQL_STEP_FAILED')
    return r.stdout.strip()

class Evidence:
    def __init__(self,directory,mode,container):
        directory.mkdir(parents=True,exist_ok=True)
        self.path=directory/('authentication-results-'+('ok' if container==CONTAINER else 'fail')+'.json' if mode else 'first-customer-results.json')
        self.value={'scope':'AUTH_PREFLIGHT_ONLY' if mode else 'THREE_SQL_FIXTURES_ONLY_NOT_94_OR_451_QUALIFICATION',
                    'status':'IN_PROGRESS','current_stage':'ENTRY','current_case':None,
                    'authentication':[],'results':[],'current':{},'failure':None,
                    'cleanup_required':True,'subsequent_cases_stopped':False}
        # Preserve prior evidence, including interrupted/incomplete runs.
        with self.path.open('x',encoding='utf8',newline='\n') as f:f.write(json.dumps(self.value,indent=2)+'\n')
    def save(self):
        temporary=self.path.with_suffix('.json.tmp')
        with temporary.open('w',encoding='utf8',newline='\n') as f:
            f.write(json.dumps(self.value,indent=2)+'\n');f.flush();os.fsync(f.fileno())
        temporary.replace(self.path)
    def stage(self,name):
        self.value['current_stage']=name;self.save()

def diagnostic(stderr):
    """Parse only PostgreSQL verbose ERROR headers; discard every other byte."""
    headers=[]
    for line in stderr.splitlines():
        m=re.fullmatch(r'(?:psql:<stdin>:[0-9]+: )?(?:ERROR|FATAL):\s+([0-9A-Z]{5}):\s+(.*)',line)
        if m:headers.append((m[1],m[2]))
    if len(headers)!=1:return {'sqlstate':None,'diagnostic':'NONE' if not headers else 'MULTIPLE_ERRORS'}
    state,message=headers[0]
    return {'sqlstate':state,'diagnostic':DIAGNOSTICS.get((state,message),'UNLISTED')}

def hba_matches(rows):
    """Inspect first applicable rules in the proposed fresh-initdb configuration.

    pg_hba_file_rules reports disk content, not loaded rules. system_user and the
    wrong-password controls below additionally prove actual authentication.
    """
    require(bool(rows) and all(r['error'] is None for r in rows),'HBA_PARSE_ERROR')
    selected=[]
    for address in ('127.0.0.1','::1'):
        for role in ('postgres',*ROLES):
            match=None
            for r in sorted(rows,key=lambda x:x['rule_number']):
                if r['type']=='local':continue
                require(r['type']=='host','HBA_UNSUPPORTED_RULE')
                databases=r['database'];users=r['user_name']
                require(all(x in ('all','replication',DATABASE) for x in databases),'HBA_AMBIGUOUS_DATABASE')
                require(all(x in ('all','postgres',*ROLES) for x in users),'HBA_AMBIGUOUS_USER')
                if 'all' not in databases and DATABASE not in databases:continue
                if 'all' not in users and role not in users:continue
                try:
                    mask=ipaddress.ip_address(r['netmask'])
                    bits=bin(int(mask))[2:].zfill(mask.max_prefixlen)
                    require('01' not in bits,'HBA_NONCONTIGUOUS_MASK')
                    net=ipaddress.ip_network(r['address']+'/'+str(bits.count('1')),strict=False)
                except ValueError:raise HeldFailure('HBA_UNSUPPORTED_ADDRESS') from None
                if ipaddress.ip_address(address) in net:match=r;break
            require(match is not None and match['auth_method']=='scram-sha-256','HBA_SCRAM_REQUIRED')
            selected.append({'role':role,'address':address,'rule_number':match['rule_number'],'method':'scram-sha-256'})
    return selected

def authentication_preflight(evidence,container):
    evidence.stage('AUTH_HBA')
    rows=json.loads(run('postgres',"SELECT coalesce(jsonb_agg(jsonb_build_object('rule_number',rule_number,'type',type,'database',database,'user_name',user_name,'address',address,'netmask',netmask,'auth_method',auth_method,'error',error) ORDER BY rule_number),'[]'::jsonb) FROM pg_hba_file_rules;",container))
    evidence.value['effective_hba_selections']=hba_matches(rows);evidence.save()
    verifiers=json.loads(run('postgres',"SELECT jsonb_object_agg(rolname,rolcanlogin AND rolpassword LIKE 'SCRAM-SHA-256$%') FROM pg_authid WHERE rolname IN ("+','.join(quote(r) for r in ('postgres',*ROLES))+");",container))
    require(verifiers==dict.fromkeys(('postgres',*ROLES),True),'SCRAM_VERIFIERS_REQUIRED')
    for role in ('postgres',*ROLES):
        evidence.value['current_auth_role']=role
        evidence.stage('AUTH_CORRECT_PASSWORD')
        probe=json.loads(run(role,"SELECT jsonb_build_object('login',session_user,'auth',system_user,'database',current_database(),'client',inet_client_addr()::text,'server',inet_server_addr()::text);",container))
        require(probe=={'login':role,'auth':'scram-sha-256:'+role,'database':DATABASE,'client':'127.0.0.1','server':'127.0.0.1'},'AUTHENTICATED_SCRAM_LOGIN_REQUIRED')
        evidence.stage('AUTH_WRONG_PASSWORD')
        # The value is ephemeral environment transport, never argv or evidence.
        env=os.environ.copy();env['PGPASSWORD']=secrets.token_hex(32)
        wrong=subprocess.run(psql(role,container,True),input='SELECT 1;\n',text=True,capture_output=True,timeout=30,env=env)
        message='FATAL:  password authentication failed for user "'+role+'"'
        require(wrong.returncode==2 and wrong.stdout.strip()=='' and sum(line.strip().endswith(message) for line in wrong.stderr.splitlines())==1,'WRONG_PASSWORD_CONTROL_FAILED')
        evidence.value['authentication'].append({'role':role,'transport':'TCP_127.0.0.1_5432','correct_password':'PASS_SCRAM','wrong_password':'PASS_REJECTED','wrong_password_exit_code':2})
        evidence.save()

def close_operation(app,backend,container):
    """Exit/abort client, then independently confirm exact backend absence.

    Killing a Docker CLI alone is insufficient. Unconfirmed closure prevents
    rollback observations and leaves evidence for exact-resource cleanup.
    """
    if app.poll() is None:
        try:
            if not app.stdin.closed:app.stdin.write('ROLLBACK;\n\\q\n');app.stdin.close()
            app.wait(timeout=10)
        except (OSError,ValueError,subprocess.TimeoutExpired):
            app.terminate()
            try:app.wait(timeout=10)
            except subprocess.TimeoutExpired:app.kill();app.wait(timeout=10)
    require(app.poll() is not None,'OPERATION_CLIENT_STILL_LIVE')
    require(backend is not None,'OPERATION_BACKEND_UNCONFIRMED')
    check="SELECT count(*) FROM pg_stat_activity WHERE pid="+backend['pid']+" AND backend_start="+quote(backend['started'])+"::timestamptz AND usename='wa_app_runtime' AND datname="+quote(DATABASE)+";"
    require(run('postgres',check,container)=='0','OPERATION_BACKEND_STILL_LIVE')

def scenario(case,evidence,container):
    evidence.value['current_case']=case['name'];evidence.value['current']={'operation_closed':False,'stage_markers':[]}
    evidence.stage('OPEN_OPERATION')
    require((case['expected_sqlstate'],case['expected_diagnostic'])==EXPECTED[case['name']],'FIXTURE_VERDICT_CHANGED')
    app=None;backend=None;failure=None;failed_stage=None;reader=None;error_reader=None;errors=[];lines=queue.Queue();stream_failed=threading.Event();code=None;verdict=None
    try:
        app=subprocess.Popen(psql('wa_app_runtime',container),stdin=subprocess.PIPE,stdout=subprocess.PIPE,stderr=subprocess.PIPE,text=True,bufsize=1)
        def read_output():
            try:
                for line in app.stdout:lines.put(line.rstrip())
            except Exception:stream_failed.set()
        reader=threading.Thread(target=read_output,daemon=True);reader.start()
        # Drain both pipes while the process runs; unrestricted bytes stay in
        # memory only and never enter an exception message or evidence record.
        def read_errors():
            try:errors.append(app.stderr.read())
            except Exception:stream_failed.set()
        error_reader=threading.Thread(target=read_errors,daemon=True);error_reader.start()
        evidence.stage('CAPTURE_TUPLE')
        app.stdin.write("BEGIN ISOLATION LEVEL READ COMMITTED; SELECT 'WA_TUPLE|'||jsonb_build_object('login',session_user,'pid',pg_backend_pid()::text,'xid',pg_current_xact_id()::text,'started',(SELECT backend_start::text FROM pg_stat_activity WHERE pid=pg_backend_pid()))::text;\n");app.stdin.flush()
        tuple_line=lines.get(timeout=30)
        require(tuple_line.startswith('WA_TUPLE|'),'RUNTIME_TUPLE_INVALID')
        captured=json.loads(tuple_line.removeprefix('WA_TUPLE|'))
        require(captured['login']=='wa_app_runtime' and re.fullmatch('[0-9]+',captured['pid']) and re.fullmatch('[0-9]+',captured['xid']) and re.fullmatch(r'[0-9T:+. \-]+',captured['started']),'RUNTIME_TUPLE_INVALID')
        backend=captured
        evidence.value['current']['authenticated_login']='wa_app_runtime'
        evidence.stage('ISSUE_GRANT')
        secret=secrets.token_hex(32)
        run('wa_context_issuer',grant_sql(case,backend['login'],backend['pid'],backend['xid'],hashlib.sha256(bytes.fromhex(secret)).hexdigest()),container)
        evidence.stage('BEHAVIOR')
        app.stdin.write('SELECT platform_private.bind_request_context('+quote(secret)+');\n'+(FIXTURES/case['transaction_sql']).read_text(encoding='utf8')+'\n\\q\n');app.stdin.close()
        code=app.wait(timeout=45);reader.join(timeout=5);error_reader.join(timeout=5)
        require(not reader.is_alive() and not error_reader.is_alive() and not stream_failed.is_set(),'OPERATION_OUTPUT_INCOMPLETE')
        verdict=diagnostic(errors[0])
        evidence.value['current'].update(exit_code=code,**verdict);evidence.save()
    except (Exception,KeyboardInterrupt) as exc:
        failure=exc;failed_stage=evidence.value['current_stage']
    finally:
        evidence.stage('CLOSE_OPERATION')
        if app is not None:
            try:
                close_operation(app,backend,container)
                evidence.value['current']['operation_closed']=True;evidence.save()
            except Exception:
                evidence.value['current']['closure_failure']='UNCONFIRMED';evidence.save()
                if failure is None:failure=HeldFailure('OPERATION_CLOSURE_UNCONFIRMED');failed_stage='CLOSE_OPERATION'
        if reader is not None:reader.join(timeout=5)
        if error_reader is not None:error_reader.join(timeout=5)
        while not lines.empty():
            line=lines.get_nowait()
            if line in MARKERS:evidence.value['current']['stage_markers'].append(line)
        evidence.save()
    if failure is not None:
        evidence.stage(failed_stage);raise failure
    # Operation closure is confirmed BEFORE any rollback/state observation.
    evidence.stage('OBSERVE_COMPLETE_STATE')
    counts=json.loads(run('postgres',(FIXTURES/case['observer_sql']).read_text(encoding='utf8'),container))
    require(set(counts)==set(case['expected_counts']) and all(type(v) is type(case['expected_counts'][k]) for k,v in counts.items()),'OBSERVER_SHAPE_INVALID')
    evidence.value['current']['counts']=counts;evidence.save()
    evidence.stage('CHECK_VERDICT')
    require((code==0)==case['expected_commit'],'UNEXPECTED_SCENARIO_EXIT')
    expected_state,expected_diagnostic=EXPECTED[case['name']]
    require(verdict=={'sqlstate':expected_state,'diagnostic':expected_diagnostic},'INTENDED_GUARD_NOT_PROVEN')
    expected_markers=list(MARKERS[:1]) if case['name']=='wrong-person' else list(MARKERS)
    require(evidence.value['current']['stage_markers']==expected_markers,'INTENDED_STAGE_NOT_REACHED')
    require(counts==case['expected_counts'],'COMPLETE_STATE_MISMATCH')
    evidence.value['results'].append({'case':case['name'],**evidence.value['current'],'status':'PASS_REHEARSAL_ONLY'})
    evidence.stage('SCENARIO_COMPLETE')

def main(argv=None):
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--execute-approved-rehearsal',action='store_true')
    p.add_argument('--authentication-preflight-only',action='store_true')
    p.add_argument('--container',choices=(CONTAINER,'wa-p0c-first-20261110-fail'),default=CONTAINER)
    p.add_argument('--evidence-directory',type=Path)
    a=p.parse_args(argv)
    if not a.execute_approved_rehearsal:p.error('EXECUTION HELD: separate Brain approval required; no Docker/DB call performed')
    if a.evidence_directory is None:p.error('an external test-owned evidence directory is required')
    evidence_dir=a.evidence_directory.resolve()
    if evidence_dir==ROOT or ROOT in evidence_dir.parents:p.error('runtime evidence must remain outside source checkout')
    if not a.authentication_preflight_only and a.container!=CONTAINER:p.error('behavior is success-target only')
    evidence=Evidence(evidence_dir,a.authentication_preflight_only,a.container)
    try:
        evidence.stage('RESOURCE_PREFLIGHT')
        endpoint=json.loads(subprocess.check_output(['docker','--context','desktop-linux','context','inspect','desktop-linux'],text=True,timeout=30))[0]['Endpoints']['docker']['Host']
        require(endpoint=='npipe:////./pipe/dockerDesktopLinuxEngine','UNEXPECTED_DOCKER_ENDPOINT')
        resource=json.loads(subprocess.check_output(['docker','--context','desktop-linux','inspect',a.container],text=True,timeout=30))[0]
        plan=json.loads((ROOT/'context/reconciliation/database-candidate-tests.json').read_text(encoding='utf8'))['first_rehearsal']
        require(resource['Config']['Image']==plan['image']['reference'],'UNEXPECTED_IMAGE')
        require(resource['Config']['Labels'].get('workinants.rehearsal')=='p0c-first-20261110' and resource['HostConfig']['NetworkMode']=='none' and not resource['HostConfig'].get('PortBindings'),'UNEXPECTED_RESOURCE_NETWORK')
        evidence.stage('SERVER_PREFLIGHT')
        require(run('postgres',"SELECT current_setting('server_version') LIKE '17.11%';",a.container)=='t','WRONG_SERVER_VERSION')
        require(run('postgres',"SELECT current_setting('log_statement')='none' AND current_setting('log_min_error_statement')='panic' AND current_setting('password_encryption')='scram-sha-256';",a.container)=='t','UNSAFE_SERVER_SETTINGS')
        authentication_preflight(evidence,a.container)
        if not a.authentication_preflight_only:
            evidence.stage('FINALIZATION_PREFLIGHT')
            require(run('postgres',"SELECT count(*) FROM pg_auth_members m WHERE m.roleid IN ('wa_private_helper_owner'::regrole,'wa_customer_verifier'::regrole,'wa_track_verifier'::regrole) AND m.member='wa_schema_owner'::regrole;",a.container)=='0','TEMPORARY_AUTHORITY_REMAINS')
            require(run('postgres',"SELECT has_schema_privilege('wa_private_helper_owner','platform_private','CREATE') OR has_schema_privilege('wa_customer_verifier','platform_private','CREATE') OR has_schema_privilege('wa_track_verifier','platform_private','CREATE');",a.container)=='f','TEMPORARY_CREATE_REMAINS')
            evidence.stage('FIXTURE_SETUP')
            run('postgres',(FIXTURES/'fixtures.sql').read_text(encoding='utf8'),a.container)
            for case in json.loads((FIXTURES/'fixtures.json').read_text(encoding='utf8'))['scenarios']:scenario(case,evidence,a.container)
        evidence.value.update(status='PASS_PREFLIGHT_ONLY' if a.authentication_preflight_only else 'PASS_REHEARSAL_ONLY',current_stage='COMPLETE')
        evidence.save();return 0
    except (Exception,KeyboardInterrupt) as exc:
        # Never retain str/repr(exc), stdout, stderr, commands, SQL or env.
        category='INTERRUPTED' if isinstance(exc,KeyboardInterrupt) else 'TIMEOUT' if isinstance(exc,(subprocess.TimeoutExpired,queue.Empty)) else 'SUBPROCESS' if isinstance(exc,(OSError,subprocess.SubprocessError)) else 'INVALID_RESPONSE_OR_INTERNAL'
        evidence.value.update(status='STOPPED_RETAINED_FOR_CONTROLLED_CLEANUP',subsequent_cases_stopped=True,
                              failure={'code':exc.code if isinstance(exc,HeldFailure) else category,'stage':evidence.value['current_stage']})
        evidence.save();return 1

if __name__=='__main__':raise SystemExit(main())
