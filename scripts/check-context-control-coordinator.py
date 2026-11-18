"""Offline CTX01 transport/FSM mocks. No Docker, database, SQL or network runs.

The 31 protocols are unchanged source proposals. Fake sessions model tuple and
savepoint lifetime only; these tests do not qualify database behavior or CTX01.
"""
import builtins
from contextlib import ExitStack, redirect_stdout, redirect_stderr
from copy import deepcopy
import hashlib
import io
import json
from pathlib import Path
import re
import runpy
import socket
import subprocess
import tempfile
import queue
import threading
from types import SimpleNamespace
import unittest
from unittest.mock import patch

ROOT=Path(__file__).resolve().parents[1]
PATH=ROOT/'scripts/sql-review/run-context-control-rehearsal.py'
M=runpy.run_path(str(PATH))
CANARY='postgresql://RAW_SECRET_PASSWORD@unlisted.invalid/statement'
RUN='719dffcb-a5f9-4a93-bffe-7faf83f7a914'
CID='c'*64


class MemoryEvidence:
    def __init__(self,packet):self.value={'current':{},'current_stage':'ENTRY','operations':[],'results':[],'authentication':[],'selected_controls':[{'id':'P0C-CTX-01','status':'NOT_RUN'}]};self.saves=[]
    def save(self):self.saves.append(json.dumps(self.value))
    def stage(self,name):self.value['current_stage']=name;self.save()


class FakeSession:
    next_pid=1000;next_xid=5000
    def __init__(self,role,coordinator):
        self.role=role;self.coordinator=coordinator;self.closed=False;self.active=False;self.binding=None;self.saved_binding=None;self.backend=None;self.expected_failure=False
        FakeSession.next_pid+=1;self.pid=str(FakeSession.next_pid);self.process=SimpleNamespace(returncode=None,poll=lambda:self.process.returncode)
        coordinator.test_sessions.append(self)
    def begin(self,isolation):
        M['require'](not self.active,'SESSION_BEGIN_STATE');self.active=True;self.isolation=isolation;self.binding=None;FakeSession.next_xid+=1;self.xid=str(FakeSession.next_xid)
    def capture(self):
        M['require'](self.active,'CAPTURE_REQUIRES_LIVE_TRANSACTION')
        self.backend={'login':self.role,'current_user':self.role,'database':M['DATABASE'],'isolation':self.isolation,'pid':self.pid,'xid':self.xid,'started':'2026-11-18 05:00:00+00','clock':'2026-11-18 05:00:01+00'}
        return deepcopy(self.backend)
    def diagnostic(self,message):
        pattern=r'CREATE FUNCTION platform_private\.bind_request_context\(secret text\).*?AS\s+(\$[a-z_0-9]*\$)(.*?)\1;'
        body=re.search(pattern,self.coordinator.application,re.S)[2]
        line=next(i for i,s in enumerate(body.split('\n'),1) if 'RAISE EXCEPTION '+M['quote'](message) in s)
        return 'ERROR:  42501: '+message+'\nCONTEXT:  PL/pgSQL function platform_private.bind_request_context(text) line '+str(line)+' at RAISE\n'
    def call(self,text):
        M['require'](not self.closed and self.process.returncode is None,'SESSION_ALREADY_ENDED')
        rows=[]
        match=re.search(r"bind_request_context\('([^']*)'\)",text)
        if 'INSERT INTO platform.database_action_grant (' in text:
            # Model the actual source trigger, which overwrites issuer input
            # created_at with its later clock_timestamp(), not CURRENT_TIMESTAMP.
            identity=re.search(r"VALUES \('([0-9a-f-]{36})'::uuid",text)[1]
            created='2026-11-18T05:00:02.123456+00:00'
            self.coordinator.test_created_at[identity]=created
            if "RETURNING pg_catalog.jsonb_build_object('created_at',created_at)" in text:
                rows=deepcopy(getattr(self.coordinator,'test_return_override',[json.dumps({'created_at':created})]))
        elif match:
            secret=match[1];instance=next((v for v in self.coordinator.instances.values() if v['secret']==secret),None)
            valid=instance and instance['login']==self.role and instance['backend']['pid']==self.pid and instance['backend']['xid']==self.xid and self.isolation=='read committed'
            if not valid:
                self.process.returncode=3;message='invalid context' if not re.fullmatch('[0-9a-f]{64}',secret) else 'invalid, stale or unsupported context'
                return [],False,self.diagnostic(message)
            self.binding=instance
        elif text.strip()=='SAVEPOINT ctx01_before_bind;':self.saved_binding=self.binding
        elif text.strip()=='ROLLBACK TO SAVEPOINT ctx01_before_bind;':self.binding=self.saved_binding
        elif 'SET LOCAL wa.context_hash=' in text:self.binding=None
        elif 'AS visible_exact_root' in text or "'visible_exact_root'" in text:
            visible=False
            if self.binding:
                v=self.binding['values'];packet=self.coordinator.packet
                if self.role=='wa_app_runtime':
                    visible=all(v[k]==M['quote'](expected) for k,expected in {'owner_module_id':'customer_buyer_profile','action':'SH-004.v1','purpose':'resolve','target_kind':'CustomerProfile','target_id':packet['namespace_policy']['ids']['CustomerProfile']}.items())
                else:visible=v['purpose']==M['quote']('work.claim')
            rows=[json.dumps({'visible_exact_root':int(bool(visible))})]
        elif "'modified'" in text:rows=[json.dumps({'modified':0})]
        elif 'WA_CUSTOMER_CONTROL_READY_TO_COMMIT' in text:rows=['WA_CUSTOMER_CONTROL_READY_TO_COMMIT']
        elif 'WA_CTX01_SCHEDULE_READY' in text:rows=['WA_CTX01_SCHEDULE_READY']
        if re.search(r'\b(?:COMMIT|ROLLBACK);\s*$',text):self.active=False;self.binding=None
        return rows,True,''
    def close(self):self.closed=True;self.active=False;self.process.returncode=3 if self.expected_failure else self.process.returncode or 0;return self.process.returncode


class ContextCoordinatorTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.packet=json.loads((M['PACKET']/'fixtures.json').read_text());cls.native={'format':'workinants.native-catalog.v1','server_version_num':170011,'read_only':True,'collected_as':'postgres','collector_is_superuser':True}
        cls.target=json.loads((ROOT.parent/'local-f0-catalog-plan-719dffcb/ok-migration-manifest.json').read_text())
    def setUp(self):
        self.stack=ExitStack();self.addCleanup(self.stack.close)
        for name in ('run','Popen','check_output','check_call'):self.stack.enter_context(patch.object(subprocess,name,side_effect=AssertionError('PROCESS_FORBIDDEN')))
        self.stack.enter_context(patch.object(socket,'create_connection',side_effect=AssertionError('NETWORK_FORBIDDEN')))
        self.evidence=MemoryEvidence(self.packet)
        self.plan={'run_id':RUN,'immutable_container_id':CID,'source_modules_sha256':{p:M['sha'](M['source_file'](p).read_bytes()) for p in M['SOURCE_MODULES']}}
        self.coordinator=M['Coordinator'](self.plan,self.packet,self.native,self.target,self.evidence,session_factory=FakeSession);self.coordinator.test_sessions=[];self.coordinator.test_created_at={};self.queries=[]
        self.coordinator.raw=self.raw
        self.stack.enter_context(patch.dict(M['API'],{'psql':lambda role,cid:['docker','--context','desktop-linux','exec','-i',cid,'psql','-U',role]}))
    def raw(self,role,text):
        self.queries.append((role,text))
        if 'all_immutable_fields_equal' in text:
            count=text.count('SELECT g.id,')
            identities=re.findall(r"WHERE g.id='([0-9a-f-]{36})'::uuid",text)
            stamps=all('g.created_at IS NOT DISTINCT FROM ('+M['quote'](self.coordinator.test_created_at[key])+'::timestamptz)' in text for key in identities)
            return json.dumps({'exact_count':count,'all_immutable_fields_equal':stamps,'issuer_owned':True,'revoked_false':True,'unexpired':True})
        for row in self.packet['mandatory_after_case_observers']:
            if text==self.coordinator.text(row['file']):return json.dumps(row['expected'])
        if text==self.coordinator.text('source-customer-observe.sql'):return json.dumps(self.packet['mandatory_after_case_observers'][0]['expected'])
        if 'workinants.native-catalog.v1' in text:return json.dumps(self.native)
        if 'SELECT NOT EXISTS' in text or text.startswith('SELECT NOT EXISTS') or "current_setting('server_version_num')" in text:return 't'
        if 'pg_stat_activity' in text:return '0'
        raise AssertionError('unregistered mock query')
    def refuse(self,code,callback):
        with self.assertRaises(M['HeldFailure']) as error:callback()
        self.assertEqual(error.exception.code,code)
        self.assertNotIn(CANARY,str(error.exception)+json.dumps(self.evidence.value))
    def case(self,name):return next(c for c in self.packet['cases'] if c['name']==name)
    def protocol(self,name):
        case=self.case(name);self.coordinator.run_protocol(name,case['actual_login'],case['steps'])
    def issued(self):
        session=FakeSession('wa_app_runtime',self.coordinator);session.begin('read committed');backend=session.capture()
        key=self.coordinator.issue(self.packet['grants']['app'],backend)
        return session,key

    def test_import_help_and_no_flag_are_helper_free(self):
        ordinary=builtins.__import__
        def guard(name,*args,**kwargs):
            if name=='runpy':raise AssertionError('NO_HELPER_IMPORT')
            return ordinary(name,*args,**kwargs)
        namespace={'__file__':str(PATH),'__name__':'ctx_import'}
        with patch.object(builtins,'__import__',side_effect=guard):exec(compile(PATH.read_bytes(),str(PATH),'exec'),namespace)
        with redirect_stdout(io.StringIO()),redirect_stderr(io.StringIO()):
            with self.assertRaises(SystemExit) as result:namespace['main'](['--help'])
            self.assertEqual(result.exception.code,0);self.assertEqual(namespace['main']([]),1)

    def test_all_sources_and_transitive_helpers_prehashed_before_compile(self):
        pins={p:M['sha'](M['source_file'](p).read_bytes()) for p in M['SOURCE_MODULES']}
        for relative in M['SOURCE_MODULES']:
            original=Path.read_bytes
            def bad(path):return ('print('+repr(CANARY)+');raise SystemExit('+repr(CANARY)+')').encode() if path==M['source_file'](relative) else original(path)
            with patch.object(Path,'read_bytes',bad):self.refuse('COORDINATOR_SOURCE_DRIFT',lambda:M['verified_modules'](pins))
        blobs=M['verified_modules'](pins);M['load_helpers'](blobs)
        self.assertTrue(callable(M['API']['authentication_preflight']));self.assertTrue(callable(M['HOST']['inspect_live']))

    def test_same_live_xid_rebind_and_savepoint_rollback_are_legitimate(self):
        for name in ('app-same-live-xid-rebind','app-savepoint-bind-rollback-rebind','worker-same-live-xid-rebind','worker-savepoint-bind-rollback-rebind'):
            self.protocol(name)
        self.assertEqual(len(self.coordinator.retired),4)
        self.assertTrue(all(s.closed for s in self.coordinator.test_sessions))

    def test_all_31_case_protocols_retire_every_instance_on_new_actual_tuple(self):
        for case in self.packet['cases']:self.coordinator.run_protocol(case['name'],case['actual_login'],case['steps'])
        self.assertEqual(len(self.coordinator.instances),27);self.assertEqual(self.coordinator.retired,set(self.coordinator.instances))
        self.assertTrue(all(s.closed for s in self.coordinator.test_sessions))
        self.assertEqual(self.evidence.value['selected_controls'],[{'id':'P0C-CTX-01','status':'NOT_RUN'}])

    def test_source_same_backend_rollback_retry_commit_and_old_secret(self):
        self.coordinator.run_protocol('source-creation-lifetime','wa_app_runtime',self.packet['source_creation_lifetime_protocol']['steps'])
        self.assertEqual(len(self.coordinator.instances),2);self.assertEqual(len(self.coordinator.retired),2)
        original=self.coordinator.test_sessions[0]
        self.assertTrue(original.closed)
        self.assertNotIn(original.pid,json.dumps(self.evidence.value))

    def test_different_backend_and_wrong_isolation_fail_at_binder_only(self):
        for name in ('app-different-backend','worker-different-backend','app-wrong-isolation-repeatable-read','worker-wrong-isolation-serializable','app-grant-does-not-bind-worker-login'):
            self.protocol(name)
        failures=[r for r in self.evidence.value['operations'] if r['stage']=='EXPECTED_BINDER_FAILURE']
        self.assertTrue(failures and all(r['exit_code']==3 and not r['acknowledged'] and r['diagnostic']['matched'] for r in failures))

    def test_issuer_commits_and_closes_before_consumer_bind(self):
        session,key=self.issued();issuer=self.coordinator.test_sessions[-1]
        self.assertTrue(issuer.closed);self.assertEqual(issuer.role,'wa_context_issuer')
        instance=self.coordinator.instances[key]
        self.assertNotEqual(instance['id'],self.packet['namespace_policy']['ids']['grant'])
        self.assertRegex(instance['secret'],'^[0-9a-f]{64}$');self.assertEqual(instance['token_hash'],M['sha'](bytes.fromhex(instance['secret'])))
        value=json.dumps(self.evidence.value)
        for private in (instance['secret'],instance['token_hash'],instance['id'],session.backend['xid'],session.backend['started']):self.assertNotIn(private,value)

    def test_trigger_overwrites_clock_and_only_returned_created_at_changes_expectation(self):
        session,key=self.issued();issuer=self.coordinator.test_sessions[-1];instance=self.coordinator.instances[key]
        original=self.coordinator.grant_values(self.packet['grants']['app'],session.backend,issuer.backend,instance['id'],instance['token_hash'])
        self.assertNotEqual(instance['values']['created_at'],original['created_at'])
        self.assertEqual({k:v for k,v in instance['values'].items() if k!='created_at'},{k:v for k,v in original.items() if k!='created_at'})
        session.close();self.coordinator.retention([key])
        # Restoring the old CURRENT_TIMESTAMP expectation must fail against the
        # modeled source trigger; a hardcoded immutable=True oracle would miss it.
        instance['values']['created_at']=original['created_at']
        self.refuse('ISSUER_ROW_RETENTION_NOT_PROVEN',lambda:self.coordinator.retention([key]))

    def test_invalid_issuer_returning_stops_before_instance_or_secret_retention(self):
        good='2026-11-18T05:00:02.123456+00:00'
        bad=[[],['not json '+CANARY],[json.dumps({'created_at':CANARY})],[json.dumps({'created_at':good,'token_hash':CANARY})],['{"created_at":"'+good+'","created_at":"'+good+'"}'],[json.dumps({'created_at':'2026-13-18T05:00:02+00:00'})],[json.dumps({'created_at':'2026-11-18T05:00:02'})],[json.dumps({'created_at':'2026-11-18T05:10:02+00:00'})]]
        for rows in bad:
            with self.subTest(rows=len(rows)):
                self.coordinator.test_return_override=rows
                session=FakeSession('wa_app_runtime',self.coordinator);session.begin('read committed');backend=session.capture()
                with self.assertRaises(M['HeldFailure']):self.coordinator.issue(self.packet['grants']['app'],backend)
                session.close();self.assertEqual(self.coordinator.instances,{})
                self.assertTrue(self.coordinator.test_sessions[-1].closed)
                self.assertNotIn(CANARY,json.dumps(self.evidence.value))
        del self.coordinator.test_return_override

    def test_returned_timestamp_does_not_replace_required_commit_acknowledgement(self):
        original=FakeSession.call
        def missing_ack(session,text):
            rows,ack,errors=original(session,text)
            return (rows,False,errors) if 'INSERT INTO platform.database_action_grant (' in text else (rows,ack,errors)
        session=FakeSession('wa_app_runtime',self.coordinator);session.begin('read committed');backend=session.capture()
        with patch.object(FakeSession,'call',missing_ack):self.refuse('SEPARATE_ISSUER_COMMIT_UNCONFIRMED',lambda:self.coordinator.issue(self.packet['grants']['app'],backend))
        session.close();self.assertEqual(self.coordinator.instances,{})

    def test_retention_query_checks_every_immutable_column_without_exporting_rows(self):
        session,key=self.issued();session.close();self.coordinator.retention([key]);role,query=self.queries[-1]
        self.assertEqual(role,'wa_context_issuer')
        for column in M['GRANT_COLUMNS']:self.assertIn('g.'+column+' IS NOT DISTINCT FROM',query)
        self.assertNotIn('UPDATE ',query);self.assertNotIn('DELETE ',query)
        self.assertIn("'unexpired'",query);self.assertIn('clock_timestamp()',query)
        self.assertNotIn(self.coordinator.instances[key]['id'],json.dumps(self.evidence.value))

    def test_grant_builder_rechecks_captured_numeric_tuple_and_issuer_clock(self):
        session,key=self.issued();issuer=next(s for s in self.coordinator.test_sessions if s.role=='wa_context_issuer');backend=deepcopy(session.backend)
        backend['pid']=CANARY
        self.refuse('CAPTURED_GRANT_TUPLE_FORMAT',lambda:self.coordinator.grant_values(self.packet['grants']['app'],backend,issuer.backend,str(__import__('uuid').uuid4()),'0'*64))

    def test_unknown_observer_data_retains_only_bounded_known_fields(self):
        self.coordinator.raw=lambda *a:json.dumps({'count':2,'coherent':CANARY,'extra':CANARY})
        self.refuse('COMPLETE_STATE_OBSERVER_MISMATCH',lambda:self.coordinator.observe('TEST','STATIC_SQL',{'count':1,'coherent':True}))
        observed=self.evidence.value['operations'][-1]['observation']
        self.assertEqual(observed,{'fields_match':False,'values':{'count':2,'coherent':None}})

    def test_retention_expiry_revocation_and_typed_count_cannot_substitute_for_tuple(self):
        session,key=self.issued();session.close()
        for field,value in [('unexpired',False),('revoked_false',False),('exact_count',True),('all_immutable_fields_equal',False)]:
            good={'exact_count':1,'all_immutable_fields_equal':True,'issuer_owned':True,'revoked_false':True,'unexpired':True};good[field]=value
            original=self.coordinator.raw;self.coordinator.raw=lambda *a,g=good:json.dumps(g)
            try:self.refuse('ISSUER_ROW_RETENTION_NOT_PROVEN',lambda:self.coordinator.retention([key]))
            finally:self.coordinator.raw=original

    def test_fresh_instance_cap_and_no_duplicate_retirement(self):
        session,key=self.issued();session.close();self.coordinator.retire([key])
        self.refuse('INSTANCE_RETIREMENT_REUSED',lambda:self.coordinator.retire([key]))
        self.coordinator.sequence=30
        self.refuse('FINITE_GRANT_INSTANCE_LIMIT',lambda:self.coordinator.issue(self.packet['grants']['app'],session.backend))

    def test_generic_permission_error_or_malformed_frame_never_proves_expected_denial(self):
        session,key=self.issued();instance=self.coordinator.instances[key]
        correct=session.diagnostic('invalid, stale or unsupported context')
        for text in ('ERROR:  42501: permission denied\n',correct+correct,correct.replace('at RAISE','at assignment'),correct+'\x1b[31m'+CANARY):
            value=M['binder_diagnostic'](text,'invalid, stale or unsupported context',self.coordinator.application)
            self.assertFalse(value['matched']);self.assertNotIn(CANARY,json.dumps(value))

    def test_failed_bind_forbids_later_behavior_and_still_closes_every_session(self):
        case=deepcopy(self.case('app-well-formed-unissued-secret'))
        original=self.coordinator.stale
        def bad(*args):raise M['HeldFailure']('EXPECTED_SOURCE_BINDER_FAILURE_NOT_PROVEN')
        self.coordinator.stale=bad
        self.refuse('EXPECTED_SOURCE_BINDER_FAILURE_NOT_PROVEN',lambda:self.coordinator.run_protocol(case['name'],case['actual_login'],case['steps']))
        self.assertTrue(all(s.closed for s in self.coordinator.test_sessions))
        self.assertTrue(any(r.get('stage')=='TRIGGER_RESTORATION_AFTER_FAILURE' for r in self.evidence.value['operations']))
        self.coordinator.stale=original

    def test_complete_state_uses_all_four_fixed_observers_then_native(self):
        self.coordinator.complete_state()
        self.assertEqual(len(self.queries),5)
        for index,row in enumerate(self.packet['mandatory_after_case_observers']):self.assertEqual(self.queries[index],('postgres',self.coordinator.text(row['file'])))

    def test_constructor_rejects_changed_canonical_diagnostic_source_before_session(self):
        original=Path.read_bytes;path=M['source_file']('review-output/foundation-application.review.sql')
        def changed(actual):return ('SELECT '+repr(CANARY)+';').encode() if actual==path else original(actual)
        factory=lambda *_:self.fail('session boundary reached with drifted application source')
        with patch.object(Path,'read_bytes',changed):
            self.refuse('CANONICAL_APPLICATION_SOURCE_DRIFT',lambda:M['Coordinator'](self.plan,self.packet,self.native,self.target,self.evidence,session_factory=factory))
        self.assertEqual(self.queries,[])

    def test_constructor_uses_the_same_verified_canonical_read(self):
        original=Path.read_bytes;path=M['source_file']('review-output/foundation-application.review.sql');reads=[]
        def changed(actual):
            if actual==path:
                reads.append(actual)
                if len(reads)>1:return ('SELECT '+repr(CANARY)+';').encode()
            return original(actual)
        with patch.object(Path,'read_bytes',changed):coordinator=M['Coordinator'](self.plan,self.packet,self.native,self.target,self.evidence,session_factory=FakeSession)
        self.assertEqual(len(reads),1)
        self.assertEqual(M['sha'](coordinator.application.encode()),self.packet['source_files_sha256']['review-output/foundation-application.review.sql'])

    def test_changed_collector_bytes_are_rejected_before_postgres_boundary(self):
        original=Path.read_bytes;path=M['source_file'](M['COLLECTOR'])
        def changed(actual):return ('SELECT '+repr(CANARY)+';').encode() if actual==path else original(actual)
        with patch.object(Path,'read_bytes',changed):self.refuse('NATIVE_COLLECTOR_SOURCE_DRIFT',self.coordinator.native_unchanged)
        self.assertEqual(self.queries,[])

    def test_collector_executes_the_same_verified_read_without_reopening(self):
        original=Path.read_bytes;path=M['source_file'](M['COLLECTOR']);reads=[]
        def changed(actual):
            if actual==path:
                reads.append(actual)
                if len(reads)>1:return ('SELECT '+repr(CANARY)+';').encode()
            return original(actual)
        with patch.object(Path,'read_bytes',changed):self.coordinator.native_unchanged()
        self.assertEqual(len(reads),1);self.assertEqual(len(self.queries),1)
        self.assertEqual(M['sha'](self.queries[0][1].encode()),self.plan['source_modules_sha256'][M['COLLECTOR']])

    def test_wrong_same_backend_or_xid_or_count_stops_later_steps(self):
        case=deepcopy(self.case('app-rollback-same-pool-fresh-then-old'))
        capture=next(s for s in case['steps'] if s.get('tuple_label')=='T2');capture['require_distinct_xid_from']='T2_missing'
        with self.assertRaises(KeyError):self.coordinator.run_protocol(case['name'],case['actual_login'],case['steps'])
        self.assertTrue(all(s.closed for s in self.coordinator.test_sessions))
        self.assertFalse(any(r.get('stage')=='PROTOCOL_COMPLETE' for r in self.evidence.value['operations']))

    def test_actual_psql_argv_uses_created_CID_actual_role_and_private_pgpass_helper(self):
        args=self.coordinator.psql('wa_worker');self.assertIn(CID,args);self.assertIn('PGAPPNAME=wa-ctx01-'+RUN,args);self.assertEqual(args[-1],'wa_worker')
        self.refuse('ACTUAL_LOGIN_REQUIRED',lambda:self.coordinator.psql('invented_role'))

    def test_evidence_file_contains_only_scoped_not_run_controls(self):
        with tempfile.TemporaryDirectory(prefix='ctx-evidence-',dir=ROOT.parent) as folder:
            evidence=M['Evidence'](Path(folder)/'new',self.packet)
            saved=json.loads(evidence.path.read_text());self.assertEqual(saved['selected_controls'],[{'id':'P0C-CTX-01','status':'NOT_RUN'}]);self.assertEqual(saved['database_posture'],'D')

    def native_plan(self,directory):
        snapshot=deepcopy(self.native)
        comparison={'format':'workinants.catalog-comparison.v1','status':'PASS','native_snapshot_sha256':M['digest'](snapshot),'source_expected_sha256':M['EXPECTED_CATALOG'],'findings':[],'check_counts':{'PASS':1}}
        pins={p:M['sha'](M['source_file'](p).read_bytes()) for p in M['SOURCE_MODULES']}
        plan={'schema':'workinants.context-control-run.v1','scope':'REVIEWED_LOCAL_CTX01_SQL_SUBSET_ONLY','run_id':RUN,'source_commit':'a'*40,'source_tree':'b'*40,'packet_sha256':'d'*64,'reviewed_packet_sha256':M['FIXTURES_SHA'],'reviewed_content_sha256':M['CONTENT_SHA'],'source_modules_sha256':pins,'target_manifest':self.target,'immutable_container_id':CID,'scenario_names':[c['name'] for c in self.packet['cases']]}
        for key,value in [('native_snapshot',snapshot),('native_comparison',comparison)]:
            path=directory/(key+'.json');path.write_text(json.dumps(value),encoding='utf8');plan[key]={'path':str(path),'sha256':M['sha'](path.read_bytes())}
        attestation={'schema':'workinants.context-native-attestation.v1','run_id':RUN,'container_id':CID,'source_commit':plan['source_commit'],'source_tree':plan['source_tree'],'packet_sha256':plan['packet_sha256'],'collector_sha256':pins[M['COLLECTOR']],'source_expected_sha256':M['EXPECTED_CATALOG'],'native_snapshot_sha256':M['digest'](snapshot),'native_comparison_file_sha256':plan['native_comparison']['sha256'],'original_grantor_finalized':True,'operation_backends_absent':True,'comparison_status':'PASS'}
        path=directory/'native_attestation.json';path.write_text(json.dumps(attestation),encoding='utf8');plan['native_attestation']={'path':str(path),'sha256':M['sha'](path.read_bytes())}
        return plan,attestation

    def test_native_pass_sparse_counts_and_exact_same_run_attestation_load_before_helpers(self):
        with tempfile.TemporaryDirectory(prefix='ctx-native-plan-',dir=ROOT.parent) as folder:
            plan,attestation=self.native_plan(Path(folder))
            packet,native,target=M['load_inputs'](plan)
            self.assertEqual(packet['source_only_packet_sha256'],M['CONTENT_SHA']);self.assertEqual(target['run_id'],RUN)
            for field in ('run_id','container_id','source_commit','source_tree','packet_sha256','collector_sha256','native_snapshot_sha256','native_comparison_file_sha256','original_grantor_finalized','operation_backends_absent'):
                changed=deepcopy(attestation);changed[field]=False if type(changed[field]) is bool else '0'*len(changed[field])
                path=Path(plan['native_attestation']['path']);path.write_text(json.dumps(changed),encoding='utf8');plan['native_attestation']['sha256']=M['sha'](path.read_bytes())
                with patch.dict(M,load_helpers=lambda *_:self.fail('helper executed before native proof validation')):
                    self.refuse('SAME_RUN_NATIVE_ATTESTATION_REQUIRED',lambda:M['load_inputs'](plan))

    def test_native_claim_cannot_borrow_another_control_or_boolean_pass_count(self):
        with tempfile.TemporaryDirectory(prefix='ctx-native-count-',dir=ROOT.parent) as folder:
            plan,unused=self.native_plan(Path(folder));path=Path(plan['native_comparison']['path'])
            comparison=json.loads(path.read_text());comparison['check_counts']={'PASS':True};path.write_text(json.dumps(comparison),encoding='utf8');plan['native_comparison']['sha256']=M['sha'](path.read_bytes())
            with patch.dict(M,load_helpers=lambda *_:self.fail('invalid proof ran helper')):self.refuse('REVIEWED_NATIVE_PASS_REQUIRED',lambda:M['load_inputs'](plan))

    def test_popen_transport_uses_real_login_no_shell_and_created_cid(self):
        process=SimpleNamespace(stdin=io.StringIO(),stdout=io.StringIO(),stderr=io.StringIO(),returncode=0,poll=lambda:0)
        with patch.object(subprocess,'Popen',return_value=process) as start:
            session=M['Session']('wa_worker',self.coordinator)
            for reader in session.readers:reader.join(timeout=1)
        args,options=start.call_args
        self.assertIn(CID,args[0]);self.assertEqual(args[0][-1],'wa_worker');self.assertIs(options['shell'],False)
        self.assertNotIn('SET ROLE',' '.join(args[0]))

    def test_transport_capture_rejects_wrong_actual_login_and_untyped_xid(self):
        session=M['Session'].__new__(M['Session']);session.active=True;session.role='wa_app_runtime';session.isolation='read committed';session.backend=None
        value={'login':'wa_worker','current_user':'wa_worker','database':M['DATABASE'],'isolation':'read committed','pid':'1','xid':'2','started':'2026-11-18 05:00:00+00','clock':'2026-11-18 05:00:01+00'}
        session.call=lambda *_:([M['TUPLE']+json.dumps(value)],True,'')
        self.refuse('CAPTURE_ACTUAL_IDENTITY',session.capture)
        value.update(login='wa_app_runtime',current_user='wa_app_runtime',xid=2)
        self.refuse('CAPTURE_TUPLE_FORMAT',session.capture)

    def test_exact_backend_absence_precedes_late_output_refusal(self):
        session=M['Session'].__new__(M['Session']);session.closed=False;session.role='wa_app_runtime';session.backend={'pid':'123','started':'2026-11-18 05:00:00+00'}
        session.process=SimpleNamespace(returncode=0,poll=lambda:0);session.readers=[];session.invalid=threading.Event();session.lines=queue.Queue();session.errors=[CANARY];session.last_errors=''
        observed=[];session.coordinator=SimpleNamespace(raw=lambda role,text:observed.append((role,text)) or '0')
        self.refuse('UNOBSERVED_SESSION_OUTPUT',session.close)
        self.assertTrue(session.closed);self.assertEqual(len(observed),1);self.assertIn('backend_start=',observed[0][1])

    def test_full_prepared_workflow_is_31_cases_30_grants_no_whole_control_pass(self):
        self.coordinator.preflight=lambda:None
        self.coordinator.run()
        self.assertEqual(len(self.coordinator.retired),30);self.assertEqual(len(self.evidence.value['results']),31)
        self.assertEqual(self.evidence.value['selected_controls'],[{'id':'P0C-CTX-01','status':'NOT_RUN'}])
        self.assertEqual(self.evidence.value['status'],'PASS_CTX01_PREPARED_SQL_PROTOCOLS_ONLY_CONTROLS_NOT_RUN')

    def test_unconfirmed_setup_backend_never_runs_restore_observer(self):
        self.coordinator.preflight=lambda:None
        def bad(*args):self.coordinator.last_transaction={'operation_closed':False};raise RuntimeError(CANARY)
        self.coordinator.commit=bad
        self.refuse('SETUP_CLOSURE_UNCONFIRMED',self.coordinator.run)
        self.assertEqual(self.queries,[])


if __name__=='__main__':unittest.main(verbosity=2)
