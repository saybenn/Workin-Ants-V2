"""Environment-free subprocess mocks. NEVER invokes Docker or a database."""
import contextlib
import io
import ipaddress
import json
from pathlib import Path
import queue
import re
import runpy
import subprocess
import tempfile
import unittest
from unittest.mock import patch

ROOT=Path(__file__).resolve().parents[1]
runner=runpy.run_path(str(ROOT/'scripts/sql-review/run-first-rehearsal.py'))
CASES=json.loads((ROOT/'review-output/first-rehearsal/fixtures.json').read_text(encoding='utf8'))['scenarios']
SECRET='a'*64
CANARY='DO_NOT_RETAIN_PASSWORD_HANDLE_STATEMENT'

def projected_address(sql,label,addresses):
    """Model the selected SQL expression, including inet::text's host mask.

    Deliberately limited to the two projections under review. An unknown
    expression is an unmocked boundary, never a fabricated successful result.
    """
    expression=re.search("'"+label+r"'\s*,\s*(host\s*\(\s*inet_(?:client|server)_addr\s*\(\s*\)\s*\)|inet_(?:client|server)_addr\s*\(\s*\)\s*::\s*text)",sql,re.I)
    assert expression is not None,'Unmodeled address projection'
    expression=expression[1].lower()
    address=addresses['client' if 'inet_client_addr' in expression else 'server']
    if address is None:return None
    value=ipaddress.ip_interface(address)
    return str(value.ip) if expression.startswith('host') else str(value)

class Output:
    def __init__(self):self.lines=queue.Queue()
    def __iter__(self):return self
    def __next__(self):
        line=self.lines.get(timeout=5)
        if line is None:raise StopIteration
        return line

class Input:
    def __init__(self,process):self.process=process;self.closed=False
    def write(self,text):
        assert not self.closed
        p=self.process
        if 'WA_TUPLE|' in text:
            p.stdout.lines.put('WA_TUPLE|'+json.dumps({'login':'wa_app_runtime','pid':'12345','xid':'98765','started':'2026-11-11 00:00:00+00'})+'\n')
        elif 'bind_request_context' in text:
            assert SECRET in text
            markers=list(runner['MARKERS'][:1]) if p.case['name']=='wrong-person' else list(runner['MARKERS'])
            if p.world.mode=='missing-marker' and p.case['name']=='wrong-person':markers=[]
            for marker in markers:p.stdout.lines.put(marker+'\n')
            p.behavior=True
        elif 'ROLLBACK' in text:p.finish(3)
        else:raise AssertionError('Unexpected mocked operation input')
    def flush(self):pass
    def close(self):
        self.closed=True
        if self.process.behavior and self.process.world.mode!='timeout':self.process.finish(0 if self.process.case['expected_commit'] else 3)

class Process:
    def __init__(self,world,case):
        self.world=world;self.case=case;self.code=None;self.behavior=False
        self.stdout=Output();self.stdin=Input(self)
        state=case['expected_sqlstate'];message='foreign Customer principal' if state=='42501' else 'missing durable default-Free intent'
        if world.mode=='unrelated-'+str(state):message='unrelated failure '+CANARY+' '+SECRET
        self.stderr=io.StringIO('' if not state else 'psql:<stdin>:7: ERROR:  '+state+': '+message+'\nDETAIL: '+CANARY+'\nSTATEMENT: '+SECRET+'\n')
    def finish(self,code):
        if self.code is None:self.code=code;self.stdout.lines.put(None)
    def poll(self):return self.code
    def wait(self,timeout):
        if self.world.mode=='timeout' and self.case['name']=='wrong-person' and timeout==45:
            raise subprocess.TimeoutExpired(CANARY,timeout,output=SECRET,stderr=CANARY)
        if self.code is None:self.finish(0 if self.case['expected_commit'] else 3)
        return self.code
    def terminate(self):self.finish(-15)
    def kill(self):self.finish(-9)

class World:
    def __init__(self,mode='normal'):
        self.mode=mode;self.processes=[];self.events=[];self.evidence=None;self.incremental_seen=False
        self.auth_queries=[];self.wrong_password_roles=[];self.comparison_saved_before_wrong_control=True
        self.comparison_saved_before_assertion=False
    def check_output(self,args,**kwargs):
        assert args[:3]==['docker','--context','desktop-linux']
        if self.mode=='resource-error':raise subprocess.CalledProcessError(1,CANARY,output=SECRET,stderr=CANARY)
        if args[3:]==['context','inspect','desktop-linux']:
            return json.dumps([{'Endpoints':{'docker':{'Host':'npipe:////./pipe/dockerDesktopLinuxEngine'}}}])
        assert args[3]=='inspect' and args[4] in (runner['CONTAINER'],'wa-p0c-first-20261110-fail')
        image=json.loads((ROOT/'context/reconciliation/database-candidate-tests.json').read_text(encoding='utf8'))['first_rehearsal']['image']['reference']
        return json.dumps([{'Config':{'Image':image,'Labels':{'workinants.rehearsal':'p0c-first-20261110'}},'HostConfig':{'NetworkMode':'none','PortBindings':{}}}])
    def popen(self,args,**kwargs):
        assert args==runner['psql']('wa_app_runtime')
        p=Process(self,CASES[len(self.processes)]);self.processes.append(p);self.events.append('open:'+p.case['name']);return p
    def run(self,args,*,input,**kwargs):
        assert args[:5]==['docker','--context','desktop-linux','exec','-i']
        role=args[args.index('-U')+1];sql=input;output='';code=0;stderr=''
        assert args[args.index('-h')+1]=='127.0.0.1' and '-w' in args
        if 'PGPASSWORD' in args:
            self.wrong_password_roles.append(role)
            saved=json.loads(self.evidence.read_text())
            self.comparison_saved_before_wrong_control &= all(saved['authentication_comparison'].values())
            assert kwargs['env']['PGPASSWORD']==SECRET and SECRET not in ' '.join(args)
            code=0 if self.mode=='wrong-accepted' else 2
            stderr='psql: error: connection to server at "127.0.0.1", port 5432 failed: FATAL:  password authentication failed for user "'+role+'"\n'
            if self.mode=='wrong-unrelated':stderr='FATAL: unrelated '+CANARY+' '+SECRET
        elif 'pg_hba_file_rules' in sql:
            rows=[]
            for n,address,mask in [(1,'127.0.0.1','255.255.255.255'),(2,'::1','ffff:ffff:ffff:ffff:ffff:ffff:ffff:ffff')]:
                rows.append({'rule_number':n,'type':'host','database':['all'],'user_name':['all'],'address':address,'netmask':mask,'auth_method':'trust' if self.mode=='hba-trust' else 'scram-sha-256','error':None})
            output=json.dumps(rows)
        elif 'pg_authid' in sql:output=json.dumps(dict.fromkeys(('postgres',*runner['ROLES']),True))
        elif 'system_user' in sql:
            # These modes replay restored SQL casts at the process boundary;
            # normal mode always evaluates the coordinator's actual query.
            for label in ('client','server'):
                if self.mode in ('legacy-both-casts','legacy-'+label+'-cast'):
                    sql=sql.replace('host(inet_'+label+'_addr())','inet_'+label+'_addr()::text')
            self.auth_queries.append(sql)
            addresses={'client':'127.0.0.1','server':'127.0.0.1'}
            for label in addresses:
                if self.mode=='null-'+label:addresses[label]=None
                if self.mode=='nonloopback-'+label:addresses[label]='192.0.2.7'
            probe={'login':role,'auth':None if self.mode=='loaded-trust' else 'scram-sha-256:'+role,'database':runner['DATABASE'],**{label:projected_address(sql,label,addresses) for label in addresses}}
            if self.mode=='wrong-login':probe['login']=CANARY+SECRET
            if self.mode=='wrong-auth-identity':probe['auth']='scram-sha-256:unintended_role'
            if self.mode=='wrong-method':probe['auth']='md5:'+role
            if self.mode=='wrong-database':probe['database']=CANARY+SECRET
            if self.mode=='missing-field':del probe['client']
            if self.mode=='extra-field':probe[CANARY]=SECRET
            if self.mode=='wrong-type':probe['client']={CANARY:SECRET}
            output=json.dumps(probe)
            if self.mode=='malformed-json':output=CANARY+SECRET
            if self.mode=='array-response':output=json.dumps([probe])
            if self.mode=='string-response':output=json.dumps(CANARY+SECRET)
            if self.mode=='null-response':output='null'
            if self.mode=='duplicate-field':output=output[:-1]+',"login":'+json.dumps(role)+'}'
        elif 'current_setting' in sql:output='t'
        elif 'pg_auth_members' in sql:output='0'
        elif 'has_schema_privilege' in sql:output='f'
        elif 'DISABLE TRIGGER USER' in sql:self.events.append('seed')
        elif 'INSERT INTO platform.database_action_grant' in sql:
            if len(self.processes)==2 and self.mode=='issuer-error':
                saved=json.loads(self.evidence.read_text());self.incremental_seen=len(saved['results'])==1 and saved['current_stage']=='ISSUE_GRANT'
                raise subprocess.CalledProcessError(3,CANARY,output=SECRET,stderr=CANARY)
        elif 'pg_stat_activity WHERE pid=' in sql:
            assert self.processes[-1].poll() is not None
            self.events.append('closed:'+self.processes[-1].case['name'])
            output='1' if self.mode=='backend-live' else '0'
        elif "jsonb_build_object('command'" in sql:
            case=self.processes[-1].case;assert self.events[-1]=='closed:'+case['name']
            self.events.append('observe:'+case['name'])
            if self.mode=='observer-error' and len(self.processes)==2:raise OSError(CANARY+SECRET)
            counts=case['expected_counts'].copy()
            if self.mode=='partial-state' and len(self.processes)==2:counts['outbox']=1
            output=json.dumps(counts)
        else:raise AssertionError('Unmocked database boundary')
        return subprocess.CompletedProcess(args,code,stdout=output,stderr=stderr)

class Tests(unittest.TestCase):
    def exercise(self,mode='normal',auth_only=False):
        world=World(mode)
        with tempfile.TemporaryDirectory(prefix='wa-offline-mock-') as temp:
            directory=Path(temp);world.evidence=directory/('authentication-results-ok.json' if auth_only else 'first-customer-results.json')
            original_require=runner['main'].__globals__['require']
            def observe_assertion(ok,code):
                if code=='AUTHENTICATED_SCRAM_LOGIN_REQUIRED' and not ok:
                    saved=json.loads(world.evidence.read_text())
                    world.comparison_saved_before_assertion='authentication_comparison' in saved and not all(saved['authentication_comparison'].values())
                return original_require(ok,code)
            # Patching every process API used by the coordinator is mandatory.
            with patch.object(subprocess,'run',side_effect=world.run),patch.object(subprocess,'check_output',side_effect=world.check_output),patch.object(subprocess,'Popen',side_effect=world.popen),patch.object(runner['secrets'],'token_hex',return_value=SECRET),patch.dict(runner['main'].__globals__,require=observe_assertion):
                args=['--execute-approved-rehearsal','--evidence-directory',temp]
                if auth_only:args.append('--authentication-preflight-only')
                code=runner['main'](args)
            content=world.evidence.read_text();data=json.loads(content)
            for prohibited in (SECRET,CANARY,'STATEMENT:','INSERT INTO','PGPASSWORD','raw_handle','backend_start'):self.assertNotIn(prohibited,content)
            if 'authentication_comparison' in data:
                checks=data['authentication_comparison']
                self.assertEqual(set(checks),{'json_parsed','object','fields','string_fields','login','scram_identity','database','client_loopback','server_loopback'})
                self.assertTrue(all(type(value) is bool for value in checks.values()))
            self.assertTrue(data['cleanup_required'])
            return code,data,world
    def test_intended_diagnostics_and_closed_before_observation(self):
        code,data,w=self.exercise();self.assertEqual(code,0);self.assertEqual(len(data['results']),3)
        self.assertEqual([r['diagnostic'] for r in data['results']],['NONE','CUSTOMER_PRINCIPAL_GUARD','CUSTOMER_DEFAULT_FREE_GUARD'])
        self.assertEqual(len(data['authentication']),6)
        self.assertEqual(len(w.wrong_password_roles),6);self.assertTrue(w.comparison_saved_before_wrong_control)
        for case in CASES:self.assertLess(w.events.index('closed:'+case['name']),w.events.index('observe:'+case['name']))
    def test_unrelated_42501_rejects(self):self.assert_stopped('unrelated-42501',1,2,'INTENDED_GUARD_NOT_PROVEN')
    def test_unrelated_p0001_rejects(self):self.assert_stopped('unrelated-P0001',2,3,'INTENDED_GUARD_NOT_PROVEN')
    def assert_stopped(self,mode,completed,opened,failure):
        code,data,w=self.exercise(mode);self.assertEqual(code,1);self.assertEqual(len(data['results']),completed)
        self.assertEqual(len(w.processes),opened);self.assertTrue(data['subsequent_cases_stopped']);self.assertEqual(data['failure']['code'],failure)
        if failure=='AUTHENTICATED_SCRAM_LOGIN_REQUIRED':self.assertTrue(w.comparison_saved_before_assertion)
        return data,w
    def test_unexpected_issuer_failure_retains_partial_incremental_evidence(self):
        data,w=self.assert_stopped('issuer-error',1,2,'SUBPROCESS');self.assertTrue(w.incremental_seen)
        self.assertEqual(data['failure']['stage'],'ISSUE_GRANT');self.assertTrue(data['current']['operation_closed'])
    def test_unexpected_timeout_retains_markers_and_stops(self):
        data,w=self.assert_stopped('timeout',1,2,'TIMEOUT');self.assertEqual(data['failure']['stage'],'BEHAVIOR')
        self.assertEqual(data['current']['stage_markers'],['WA_COMMAND_INSERTED']);self.assertTrue(data['current']['operation_closed'])
    def test_unexpected_observer_failure_stops(self):self.assert_stopped('observer-error',1,2,'SUBPROCESS')
    def test_live_backend_prevents_observation(self):
        data,w=self.assert_stopped('backend-live',0,1,'OPERATION_CLOSURE_UNCONFIRMED');self.assertFalse(any(e.startswith('observe:') for e in w.events))
    def test_complete_state_checks_remain(self):self.assert_stopped('partial-state',1,2,'COMPLETE_STATE_MISMATCH')
    def test_stage_checks_remain(self):self.assert_stopped('missing-marker',1,2,'INTENDED_STAGE_NOT_REACHED')
    def test_auth_only_has_no_behavior_or_fixture_seed(self):
        code,data,w=self.exercise(auth_only=True);self.assertEqual(code,0);self.assertEqual(w.events,[]);self.assertEqual(data['status'],'PASS_PREFLIGHT_ONLY')
    def test_hba_trust_stops_before_behavior(self):self.assert_stopped('hba-trust',0,0,'HBA_SCRAM_REQUIRED')
    def test_loaded_trust_stops_before_behavior(self):self.assert_stopped('loaded-trust',0,0,'AUTHENTICATED_SCRAM_LOGIN_REQUIRED')
    def test_wrong_password_acceptance_stops_before_behavior(self):self.assert_stopped('wrong-accepted',0,0,'WRONG_PASSWORD_CONTROL_FAILED')
    def test_wrong_password_unrelated_failure_rejects(self):self.assert_stopped('wrong-unrelated',0,0,'WRONG_PASSWORD_CONTROL_FAILED')
    def test_address_results_depend_on_sql_projection(self):
        addresses={'client':'127.0.0.1','server':'127.0.0.1'}
        for label in addresses:
            host="SELECT jsonb_build_object('"+label+"',host(inet_"+label+"_addr()));"
            cast="SELECT jsonb_build_object('"+label+"',inet_"+label+"_addr()::text);"
            self.assertEqual(projected_address(host,label,addresses),'127.0.0.1')
            self.assertEqual(projected_address(cast,label,addresses),'127.0.0.1/32')
    def test_corrected_projection_and_comparisons_succeed(self):
        code,data,w=self.exercise(auth_only=True);self.assertEqual(code,0)
        self.assertTrue(all(data['authentication_comparison'].values()))
        self.assertTrue(w.comparison_saved_before_wrong_control);self.assertEqual(w.wrong_password_roles,['postgres',*runner['ROLES']])
        for sql in w.auth_queries:
            self.assertIn('host(inet_client_addr())',sql);self.assertIn('host(inet_server_addr())',sql)
    def test_restoring_either_or_both_casts_reproduces_mask_mismatch(self):
        for mode,failed in [('legacy-client-cast',{'client_loopback'}),('legacy-server-cast',{'server_loopback'}),('legacy-both-casts',{'client_loopback','server_loopback'})]:
            with self.subTest(mode=mode):
                data,w=self.assert_stopped(mode,0,0,'AUTHENTICATED_SCRAM_LOGIN_REQUIRED')
                self.assertEqual({k for k,v in data['authentication_comparison'].items() if not v},failed)
                self.assertEqual(data['failure']['stage'],'AUTH_CORRECT_PASSWORD');self.assertEqual(w.wrong_password_roles,[])
                self.assertTrue(any('::text' in sql for sql in w.auth_queries))
    def test_null_and_nonloopback_addresses_reject_with_named_checks(self):
        for label in ('client','server'):
            for kind in ('null','nonloopback'):
                with self.subTest(label=label,kind=kind):
                    data,w=self.assert_stopped(kind+'-'+label,0,0,'AUTHENTICATED_SCRAM_LOGIN_REQUIRED')
                    checks=data['authentication_comparison'];self.assertFalse(checks[label+'_loopback'])
                    self.assertTrue(checks['server_loopback' if label=='client' else 'client_loopback'])
                    self.assertEqual(checks['string_fields'],kind!='null');self.assertEqual(w.wrong_password_roles,[])
    def test_wrong_identities_methods_and_database_reject_without_values(self):
        for mode,failed in [('wrong-login','login'),('wrong-auth-identity','scram_identity'),('wrong-method','scram_identity'),('wrong-database','database')]:
            with self.subTest(mode=mode):
                data,w=self.assert_stopped(mode,0,0,'AUTHENTICATED_SCRAM_LOGIN_REQUIRED')
                self.assertEqual({k for k,v in data['authentication_comparison'].items() if not v},{failed})
                self.assertEqual(w.wrong_password_roles,[])
    def test_malformed_or_unexpected_responses_stop_without_probe_values(self):
        for mode,failed in [('malformed-json','json_parsed'),('duplicate-field','json_parsed'),('array-response','object'),('string-response','object'),('null-response','object'),('missing-field','fields'),('extra-field','fields'),('wrong-type','string_fields')]:
            with self.subTest(mode=mode):
                data,w=self.assert_stopped(mode,0,0,'AUTHENTICATED_SCRAM_LOGIN_REQUIRED')
                self.assertFalse(data['authentication_comparison'][failed]);self.assertEqual(w.wrong_password_roles,[])
    def test_resource_failure_retains_safe_entry_evidence(self):
        data,w=self.assert_stopped('resource-error',0,0,'SUBPROCESS');self.assertEqual(data['failure']['stage'],'RESOURCE_PREFLIGHT')
    def test_generator_and_register_authentication_boundary(self):
        plan=json.loads((ROOT/'context/reconciliation/database-candidate-tests.json').read_text(encoding='utf8'))['first_rehearsal']
        generated=runpy.run_path(str(ROOT/'scripts/database-candidate-correction-rules.py'))['FIRST_REHEARSAL']
        self.assertEqual(plan,generated)
        template=plan['resource_commands_after_separate_approval']['container_template']
        for fragment in ('POSTGRES_INITDB_ARGS=--auth-host=scram-sha-256','POSTGRES_HOST_AUTH_METHOD=scram-sha-256','password_encryption=scram-sha-256','--network none'):self.assertIn(fragment,template)
        self.assertEqual(plan['authentication_preflight']['status'],'NOT_RUN')
        self.assertTrue(all(s['status']=='NOT_RUN' for s in plan['steps']))
        for case in CASES:self.assertEqual((case['expected_sqlstate'],case['expected_diagnostic']),runner['EXPECTED'][case['name']])
    def test_prior_evidence_is_never_overwritten(self):
        with tempfile.TemporaryDirectory(prefix='wa-offline-mock-') as temp:
            evidence=runner['Evidence'](Path(temp),False,runner['CONTAINER']);before=evidence.path.read_bytes()
            with self.assertRaises(FileExistsError):runner['Evidence'](Path(temp),False,runner['CONTAINER'])
            self.assertEqual(evidence.path.read_bytes(),before)
    def test_execution_guard_precedes_all_boundaries(self):
        with patch.object(subprocess,'run',side_effect=AssertionError),patch.object(subprocess,'check_output',side_effect=AssertionError),patch.object(subprocess,'Popen',side_effect=AssertionError),contextlib.redirect_stderr(io.StringIO()):
            with self.assertRaises(SystemExit):runner['main']([])
    def test_diagnostic_requires_one_exact_pair(self):
        parse=runner['diagnostic']
        for text in ('ERROR:  P0001: unrelated','ERROR:  42501: unrelated','ERROR:  P0001: foreign Customer principal','ERROR:  42501: foreign Customer principal\nERROR:  P0001: missing durable default-Free intent'):
            self.assertNotIn(parse(text)['diagnostic'],('CUSTOMER_PRINCIPAL_GUARD','CUSTOMER_DEFAULT_FREE_GUARD'))

if __name__=='__main__':unittest.main(verbosity=2)
