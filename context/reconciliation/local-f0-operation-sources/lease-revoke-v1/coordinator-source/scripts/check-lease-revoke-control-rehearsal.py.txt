"""Focused environment-free SQL-model/process mocks. No database qualification.

Every subprocess/Docker/network boundary is forbidden. The finite lease model
interprets emitted UPDATE projections rather than returning outcomes by name.
Source-exact diagnostics, markers, closure, partial evidence and secret exclusion
are checked separately from the previously reviewed pinned CTX transport.
"""
import ast
from contextlib import ExitStack,redirect_stdout,redirect_stderr
from copy import deepcopy
import hashlib
import io
import json
from pathlib import Path
import re
import socket
import subprocess
import tempfile
import unittest
from types import ModuleType,SimpleNamespace
from unittest.mock import patch

ROOT=Path(__file__).resolve().parents[1];TASK=ROOT.parent
GEN=ROOT/'scripts/prepare-lease-revoke-control-rehearsal.py'
PROTO=ROOT/'scripts/lease_revoke_control_protocol.py'
COOR=ROOT/'scripts/sql-review/run-lease-revoke-control-rehearsal.py'
CANARY='postgresql://NEVER_RETAIN_SECRET@private.invalid/RAW_STATEMENT'

def load(path):
    module=ModuleType('_offline_'+path.stem.replace('-','_'));module.__file__=str(path)
    exec(compile(path.read_bytes(),str(path),'exec'),module.__dict__);return module.__dict__

class Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.block=ExitStack()
        for name in ('run','Popen','check_call','check_output','call'):cls.block.enter_context(patch.object(subprocess,name,side_effect=AssertionError('PROCESS_FORBIDDEN')))
        cls.block.enter_context(patch.object(socket,'create_connection',side_effect=AssertionError('NETWORK_FORBIDDEN')))
        cls.gen=load(GEN);cls.proto=load(PROTO);cls.coor=load(COOR);cls.files,cls.packet=cls.gen['build'](ROOT)
        cls.application=(ROOT/'review-output/foundation-application.review.sql').read_text()
        cls.temp=tempfile.TemporaryDirectory(prefix='offline-lease-revoke-',dir=TASK)
    @classmethod
    def tearDownClass(cls):cls.temp.cleanup();cls.block.close()
    def diagnostic(self,name,message=None,state=None,frame_offset=0):
        expected=self.proto['DIAGNOSTICS'][name];state=state or expected[0];message=message or expected[1];function=expected[2]
        body=re.search(r'CREATE FUNCTION platform_private\.'+function+r'\(\).*?AS\s+(\$[a-z_0-9]*\$)(.*?)\1;',self.application,re.S)[2]
        line=next(i for i,row in enumerate(body.split('\n'),1) if 'RAISE EXCEPTION '+self.proto['quote'](expected[1]) in row)
        return 'ERROR:  '+state+': '+message+'\nCONTEXT:  PL/pgSQL function platform_private.'+function+'() line '+str(line+frame_offset)+' at RAISE\n'
    def test_import_and_help_do_not_execute_helpers_or_processes(self):
        output=io.StringIO()
        with redirect_stdout(output),redirect_stderr(output),self.assertRaises(SystemExit) as error:self.coor['main'](['--help'])
        self.assertEqual(error.exception.code,0);self.assertNotIn('API',self.coor.get('GLOBALS',{}))
    def test_pure_artifacts_reproduce_bytes(self):
        actual,packet=self.gen['build'](ROOT);self.assertEqual(actual,self.files);self.assertEqual(packet,self.packet)
        self.assertEqual(packet['status'],'NOT_RUN');self.assertFalse(packet['database_contacted']);self.assertFalse(packet['sql_executed'])
    def test_actual_prepared_bytes_and_coordinator_literal_hashes_match(self):
        directory=ROOT/'review-output/lease-revoke-control-rehearsal';self.assertTrue(directory.is_dir())
        self.assertEqual({path.name for path in directory.iterdir() if path.is_file()},set(self.files))
        for name,raw in self.files.items():self.assertEqual((directory/name).read_bytes(),raw,name)
        self.assertEqual(self.coor['PACKET_SHA'],hashlib.sha256(self.files['fixtures.json']).hexdigest());self.assertEqual(self.coor['CONTENT_SHA'],self.packet['source_only_packet_sha256'])
    def test_actual_register_ids_and_every_assertion_are_preserved(self):
        self.assertEqual(self.packet['selected_control_ids'],['P0C-TRACK-01','P0C-CTX-02'])
        for case in self.packet['source_assertions'].values():self.assertTrue(all(row['status']=='NOT_RUN' for row in case['assertions']))
        self.assertIn('CUSTOMER_UPDATE_RECEIPT',self.packet['coverage_limits']['Customer_update_gate'])
    def test_all_prepared_sql_parses_and_has_no_privileged_expiry_update(self):
        from pglast import parse_sql
        sqls={name:raw.decode() for name,raw in self.files.items() if name.endswith('.sql')}
        for name,text in sqls.items():self.assertTrue(parse_sql(text),name)
        self.assertGreater(len(sqls),25)
        self.assertNotIn('lease_expires_at',sqls['independent-user-fixtures.sql'])
        for name,text in sqls.items():
            if 'lease_expires_at=' in text:self.assertTrue(name in self.packet['prepared_files_sha256'])
            self.assertNotIn('ALTER ROLE',text);self.assertNotIn('GRANT ',text)
    def test_source_module_drift_rejects_before_compilation(self):
        original=Path.read_bytes
        def changed(path):return b"raise RuntimeError('MUST_NOT_EXECUTE')" if path==ROOT/self.gen['CM'] else original(path)
        with patch.object(Path,'read_bytes',changed),self.assertRaisesRegex(ValueError,'REVIEWED_SOURCE_DRIFT'):self.gen['build'](ROOT)
    def test_each_of_32_worker_acl_rows_is_unchanged_and_caps_are_narrow(self):
        acl=json.loads((ROOT/self.gen['ACL']).read_bytes());rows=[r for r in acl if r['role']=='wa_worker'];self.assertEqual(len(rows),32)
        canonical=self.gen['canonical'];self.assertEqual(hashlib.sha256(canonical(rows).encode()).hexdigest(),self.packet['worker_acl_sha256'])
        for name,grant in self.packet['grants'].items():
            self.assertEqual(grant['allowed_fields'],sorted(set(grant['allowed_fields'])))
            self.assertTrue(all('*' not in value for value in grant['allowed_fields']))
            if grant['database_login_role']=='wa_worker':
                self.assertTrue(all(value.startswith('RuntimeWorkItem/'+self.packet['work_ids']['lease']+'/') for value in grant['allowed_fields']))
    def test_new_source_uuid_namespace_is_disjoint_from_existing_packets(self):
        pattern=re.compile(r'\b[0-9a-f]{8}-(?:[0-9a-f]{4}-){3}[0-9a-f]{12}\b');ours=set(pattern.findall(json.dumps({k:self.packet[k] for k in ('sources','work_ids','identity_receipts')})))
        for packet in ('customer','worker','context','unique'):
            previous=(ROOT/('review-output/'+packet+'-control-rehearsal/fixtures.json')).read_text()
            self.assertFalse(ours&set(pattern.findall(previous)),packet)
    def test_customer_positive_has_complete_committed_group_and_no_track_enrollment(self):
        for name,case in self.packet['sources'].items():
            sql=self.files['source-'+name+'.sql'].decode();self.assertIn('COMMIT;',sql);self.assertIn('WA_CUSTOMER_CONTROL_READY_TO_COMMIT',sql)
            self.assertEqual(case['observer_expected'],{'customer':1,'command':1,'history':1,'evidence':1,'outbox':2,'track_enrollments':0,'coherent':True})
            self.assertEqual(self.packet['grants']['source-'+name],case['grant'])
    def test_complete_zero_effect_observer_covers_attempts_and_track_footprint(self):
        sql=self.files['no-effects-observe.sql'].decode()
        for table in ('platform.runtime_attempt','platform.runtime_work_item','app.track_subscriptions','app.track_base_selection','app.track_entitlement_grants','app.track_subscription_events'):self.assertIn(table,sql)
        self.assertIn('effect_receipt_id IS NOT NULL',sql)
    def test_identity_writers_keep_exact_predecessor_link_and_same_transaction(self):
        for step,generation in (('rotate',1),('revoke',2),('recover',3)):
            text=self.files['identity-app-'+step+'.sql'].decode();self.assertIn('previous_receipt_id',text);self.assertIn('previous_generation',text)
            self.assertIn('security_generation='+str(generation),text);self.assertIn('security_generation='+str(generation-1),text)
            self.assertIn('revoked_at=(SELECT revoked_at FROM platform_private.identity_service_receipt',text)
            self.assertEqual(text.count('COMMIT;'),1)
    def test_all_intended_guard_diagnostics_pass_with_exact_source_frames(self):
        for name in self.proto['DIAGNOSTICS']:
            result=self.proto['intended_diagnostic'](self.diagnostic(name),name,self.application);self.assertTrue(result['matched'],name)
    def test_unrelated_P0001_and_42501_never_pass(self):
        for name in self.proto['DIAGNOSTICS']:
            for state in ('P0001','42501'):
                result=self.proto['intended_diagnostic'](self.diagnostic(name,CANARY,state),name,self.application);self.assertFalse(result['matched']);self.assertNotIn(CANARY,json.dumps(result))
    def test_wrong_frame_missing_frame_and_extra_statement_text_reject(self):
        name='shorten-renew-denied';good=self.diagnostic(name)
        for text in (self.diagnostic(name,frame_offset=1),good.split('CONTEXT:')[0],good+'STATEMENT: '+CANARY+'\n',good+good):self.assertFalse(self.proto['intended_diagnostic'](text,name,self.application)['matched'])
    def test_negative_verdict_requires_exact_before_marker_and_no_ack(self):
        name='shorten-renew-denied';rows=self.proto['expected_markers'](name,True);errors=self.diagnostic(name)
        self.assertTrue(self.proto['verdict'](name,3,rows,False,errors,self.application,[])['matched'])
        for changed,ack in (([],False),(rows+[self.proto['marker'](name,'AFTER')],False),(rows,True)):
            self.assertFalse(self.proto['verdict'](name,3,changed,ack,errors,self.application,[])['matched'])
    def test_positive_verdict_requires_markers_around_exact_typed_rows(self):
        name='worker-claim';before,after=self.proto['expected_markers'](name);rows=[before,'{"changed":1}',after]
        self.assertTrue(self.proto['verdict'](name,0,rows,True,'',self.application,[{'changed':1}])['matched'])
        for bad in ([before,after,'{"changed":1}'],[before,'{"changed":true}',after],[before,'{"changed":0}',after],[before,'{"changed":1,"changed":1}',after],[before,'{"changed":NaN}',after]):self.assertFalse(self.proto['verdict'](name,0,bad,True,'',self.application,[{'changed':1}])['matched'])
    def test_finite_driver_stops_first_failure_and_keeps_completed_names(self):
        actions=[]
        class Driver:
            def stage(self,name,count):actions.append(('stage',name,count))
            def case(self,name):
                if name=='live-reclaim-denied':raise ValueError(CANARY)
            def stopped(self,name,count):actions.append(('stopped',name,count))
            def completed(self,name):actions.append(('completed',name))
        with self.assertRaises(ValueError):self.proto['finite_driver'](Driver())
        self.assertEqual(actions[-1],('stopped','live-reclaim-denied',2));self.assertFalse(any('expired-renew-denied' in str(row) for row in actions))
    def test_expiration_query_only_observes_actual_server_clock(self):
        text=self.files['lease-clock.sql'].decode();self.assertIn('lease_expires_at<=clock_timestamp()',text);self.assertNotIn('UPDATE',text);self.assertNotIn('pg_sleep',text)
        self.assertEqual(self.packet['finite_caps']['clock_wait_seconds_max'],45)
    def test_claim_renew_reclaim_projection_contains_real_preimage_and_monotone_changes(self):
        claim=self.files['worker-claim.sql'].decode();renew=self.files['worker-renew.sql'].decode();reclaim=self.files['reclaim.sql'].decode()
        self.assertIn('fence=fence+1,attempt_count=attempt_count+1',claim);self.assertIn("decode(current_setting('wa.lease_secret'),'hex')",claim)
        self.assertNotIn('fence=',renew);self.assertNotIn('attempt_count=',renew);self.assertNotIn('lease_token_hash=',renew)
        self.assertIn("interval '90 seconds'",reclaim);self.assertIn('fence=fence+1',reclaim)
    def test_stale_holder_uses_same_renew_capabilities_and_actual_zero_row_path(self):
        self.assertEqual(self.packet['grants']['old-holder'],self.packet['grants']['renew-1'])
        sql=self.files['stale-holder.sql'].decode();self.assertIn('UPDATE platform.runtime_work_item',sql);self.assertIn('ROLLBACK;',sql)
        self.assertNotIn('worker_lease_valid',sql)
    def test_main_unexpected_failure_preserves_safe_partial_evidence_and_stops(self):
        directory=Path(self.temp.name)/'partial';plan=Path(self.temp.name)/'plan.json';plan.write_text(json.dumps({'run_id':'1','immutable_container_id':'2','source_commit':'3','source_tree':'4','packet_sha256':'5'}))
        packet=self.packet
        class Fails:
            def __init__(self,plan,packet,native,target,evidence):self.evidence=evidence
            def run(self):
                self.evidence.value['results'].append({'name':'worker-claim','status':'PASS_FINITE_SQL_PROTOCOL_ONLY_SELECTED_CASE_NOT_RUN'});self.evidence.stage('BEFORE_UNEXPECTED');raise RuntimeError(CANARY)
        deps={'load_inputs':lambda plan:(packet,{}, {},{},{}),'coordinator':Fails}
        code=self.coor['main'](['--execute-reviewed-lease-revoke-controls','--reviewed-run-plan',str(plan),'--evidence-directory',str(directory)],deps)
        self.assertEqual(code,2);value=json.loads((directory/'lease-revoke-results.json').read_bytes());self.assertEqual(len(value['results']),1);self.assertTrue(value['subsequent_cases_stopped']);self.assertEqual(value['failure']['stage'],'BEFORE_UNEXPECTED');self.assertNotIn(CANARY,json.dumps(value))
    def test_packet_source_and_prepared_fingerprints_close_exactly(self):
        pins=self.packet['source_files_sha256'];prepared=self.packet['prepared_files_sha256']
        self.assertTrue(all(hashlib.sha256((ROOT/path).read_bytes()).hexdigest()==value for path,value in pins.items()))
        self.assertTrue(all(hashlib.sha256(self.files[name]).hexdigest()==value for name,value in prepared.items()))
        self.assertEqual(hashlib.sha256(self.gen['canonical']({'source_files_sha256':pins,'prepared_files_sha256':prepared}).encode()).hexdigest(),self.packet['source_only_packet_sha256'])
    def input_fixture(self):
        directory=Path(tempfile.mkdtemp(prefix='inputs-',dir=self.temp.name));packetdir=directory/'packet';packetdir.mkdir()
        for name,raw in self.files.items():(packetdir/name).write_bytes(raw)
        module=load(COOR);module['PACKET']=packetdir;module['PACKET_SHA']=hashlib.sha256(self.files['fixtures.json']).hexdigest();module['CONTENT_SHA']=self.packet['source_only_packet_sha256']
        base=TASK/'local-f0-native-access-plan-e7a7beff/ok-migration-manifest.json';target=json.loads(base.read_bytes());run=target['run_id'];cid='1'*64
        native={'format':'workinants.native-catalog.v1','server_version_num':170011,'read_only':True,'collected_as':'postgres','collector_is_superuser':True}
        comparison={'format':'workinants.catalog-comparison.v1','status':'PASS','source_expected_sha256':module['EXPECTED'],'native_snapshot_sha256':module['digest'](native),'check_counts':{'PASS':418,'FAIL':0,'INCOMPLETE':0},'findings':[]}
        pins={path:hashlib.sha256((ROOT/path).read_bytes()).hexdigest() for path in module['MODULES']}
        attestation={'schema':'workinants.lease-revoke-native-attestation.v1','run_id':run,'container_id':cid,'source_commit':'a'*40,'source_tree':'b'*40,'packet_sha256':'c'*64,'collector_sha256':pins[module['COLLECTOR']],'source_expected_sha256':module['EXPECTED'],'native_snapshot_sha256':module['digest'](native),'native_comparison_file_sha256':None,'original_grantor_finalized':True,'operation_backends_absent':True,'comparison_status':'PASS'}
        paths={}
        for key,value in (('native_snapshot',native),('native_comparison',comparison)):
            path=directory/(key+'.json');path.write_text(json.dumps(value));paths[key]={'path':str(path),'sha256':hashlib.sha256(path.read_bytes()).hexdigest()}
        attestation['native_comparison_file_sha256']=paths['native_comparison']['sha256'];path=directory/'attestation.json';path.write_text(json.dumps(attestation));paths['native_attestation']={'path':str(path),'sha256':hashlib.sha256(path.read_bytes()).hexdigest()}
        plan={'schema':'workinants.lease-revoke-run.v1','scope':'FINITE_LEASE_AND_APPLICATION_CURRENTNESS_SQL_ONLY','run_id':run,'source_commit':'a'*40,'source_tree':'b'*40,'packet_sha256':'c'*64,'reviewed_packet_sha256':module['PACKET_SHA'],'reviewed_content_sha256':module['CONTENT_SHA'],'source_modules_sha256':pins,'target_manifest':target,'immutable_container_id':cid,**paths,'case_names':list(self.proto['CASE_ORDER'])}
        return module,plan
    def test_source_only_loader_accepts_exact_real_helper_api_and_full_proof_schema(self):
        module,plan=self.input_fixture();packet,native,target,ctx,proto=module['load_inputs'](plan)
        self.assertEqual(packet,self.packet);self.assertTrue(callable(ctx['Session']));self.assertEqual(proto['CASE_ORDER'],self.proto['CASE_ORDER'])
    def test_mismatched_same_run_CID_attestation_rejects_before_helper_compile(self):
        module,plan=self.input_fixture();path=Path(plan['native_attestation']['path']);value=json.loads(path.read_bytes());value['container_id']='2'*64;path.write_text(json.dumps(value));plan['native_attestation']['sha256']=hashlib.sha256(path.read_bytes()).hexdigest()
        module['compiled']=lambda *a:(_ for _ in ()).throw(AssertionError('COMPILE_FORBIDDEN'))
        with self.assertRaisesRegex(module['HeldFailure'],'SAME_RUN_NATIVE_ATTESTATION_REQUIRED'):module['load_inputs'](plan)
    def test_incomplete_or_boolean_native_counts_reject_before_compile(self):
        for counts in ({'PASS':True},{'PASS':418,'INCOMPLETE':1},{'PASS':0}):
            module,plan=self.input_fixture();path=Path(plan['native_comparison']['path']);value=json.loads(path.read_bytes());value['check_counts']=counts;path.write_text(json.dumps(value));plan['native_comparison']['sha256']=hashlib.sha256(path.read_bytes()).hexdigest()
            module['compiled']=lambda *a:(_ for _ in ()).throw(AssertionError('COMPILE_FORBIDDEN'))
            with self.assertRaisesRegex(module['HeldFailure'],'FULL_NATIVE_PASS_REQUIRED'):module['load_inputs'](plan)
    def test_prepared_SQL_drift_rejects_before_helper_compile(self):
        module,plan=self.input_fixture();(module['PACKET']/'worker-claim.sql').write_text('SELECT '+repr(CANARY)+';');module['compiled']=lambda *a:(_ for _ in ()).throw(AssertionError('COMPILE_FORBIDDEN'))
        with self.assertRaisesRegex(module['HeldFailure'],'PREPARED_SQL_DRIFT'):module['load_inputs'](plan)
    def test_omitted_or_reordered_scenario_rejects_before_helper_compile(self):
        module,plan=self.input_fixture();plan['case_names']=plan['case_names'][::-1];module['compiled']=lambda *a:(_ for _ in ()).throw(AssertionError('COMPILE_FORBIDDEN'))
        with self.assertRaisesRegex(module['HeldFailure'],'EXACT_FINITE_CASE_ORDER'):module['load_inputs'](plan)


class ProjectionModelTests(unittest.TestCase):
    """Parse actual emitted UPDATE expressions to model source guard branches."""
    setUpClass=classmethod(Tests.setUpClass.__func__)
    tearDownClass=classmethod(Tests.tearDownClass.__func__)
    def simulate(self,sql,*,fence=1,attempt=1,expiry=100,now=10,secret='a'*64,stored=None,action='runtime.renew_work.v1',grant_fence=1):
        stored=stored or hashlib.sha256(bytes.fromhex(secret)).hexdigest();changed=re.search(r'UPDATE platform.runtime_work_item SET (.*?) WHERE id=',sql,re.S)[1]
        if grant_fence!=fence:return {'changed':0,'fence':fence,'attempt':attempt,'hash':stored,'expiry':expiry}
        hash_new=hashlib.sha256(bytes.fromhex(secret)).hexdigest() if 'lease_token_hash=' in changed else stored
        fence_new=fence+1 if 'fence=fence+1' in changed else fence;attempt_new=attempt+1 if 'attempt_count=attempt_count+1' in changed else attempt
        amount=re.search(r"clock_timestamp\(\)\+interval '([0-9]+) seconds'",changed)
        expiry_new=now+int(amount[1]) if amount else expiry-1 if "lease_expires_at-interval '1 second'" in changed else expiry+10 if "lease_expires_at+interval '10 seconds'" in changed else expiry
        if hash_new!=stored or (fence==0 and "state='leased'" in changed):
            if action!='runtime.claim_work.v1' or fence_new!=fence+1 or attempt_new!=attempt+1 or expiry_new<=now or (fence>0 and expiry>now):return {'error':'invalid claim/reclaim'}
        elif fence_new!=fence or attempt_new!=attempt:return {'error':'fence and attempt may change only on claim'}
        if hash_new==stored and expiry_new!=expiry:
            if action!='runtime.renew_work.v1' or expiry<=now or hashlib.sha256(bytes.fromhex(secret)).hexdigest()!=stored or expiry_new<=expiry:return {'error':'renewal requires current secret and extends live lease'}
        return {'changed':1,'fence':fence_new,'attempt':attempt_new,'hash':hash_new,'expiry':expiry_new}
    def test_model_claim_renew_expiry_reclaim_and_old_fence(self):
        work=self.packet['work_ids']['lease'];p=self.proto
        claim=self.simulate(p['mutation']('worker-claim',work),fence=0,attempt=0,expiry=0,action='runtime.claim_work.v1',grant_fence=0,stored='0'*64)
        self.assertEqual((claim['changed'],claim['fence'],claim['attempt'],claim['expiry']),(1,1,1,22))
        renew=self.simulate(p['mutation']('worker-renew',work),expiry=22);self.assertEqual((renew['fence'],renew['attempt'],renew['expiry']),(1,1,50))
        self.assertEqual(self.simulate(p['mutation']('live-reclaim-denied',work),secret='b'*64,stored=claim['hash'],action='runtime.claim_work.v1')['error'],'invalid claim/reclaim')
        reclaimed=self.simulate(p['mutation']('concurrent-reclaim-stale-holder',work),now=60,expiry=50,secret='b'*64,stored=claim['hash'],action='runtime.claim_work.v1')
        self.assertEqual((reclaimed['changed'],reclaimed['fence'],reclaimed['attempt']),(1,2,2))
        stale=self.simulate(p['mutation']('current-holder-renew',work),fence=2,attempt=2,expiry=130,now=50,grant_fence=1);self.assertEqual(stale['changed'],0)
    def test_model_rejects_projected_shorten_attempt_hash_copy_and_expiry(self):
        p=self.proto;work=self.packet['work_ids']['lease'];stored=hashlib.sha256(bytes.fromhex('a'*64)).hexdigest()
        self.assertEqual(self.simulate(p['mutation']('shorten-renew-denied',work))['error'],'renewal requires current secret and extends live lease')
        self.assertEqual(self.simulate(p['mutation']('attempt-only-denied',work),action='runtime.claim_work.v1')['error'],'fence and attempt may change only on claim')
        self.assertEqual(self.simulate(p['mutation']('hash-change-denied',work),secret='b'*64,stored=stored,action='runtime.claim_work.v1')['error'],'invalid claim/reclaim')
        self.assertEqual(self.simulate(p['mutation']('copied-hash-renew-denied',work),secret=stored,stored=stored)['error'],'renewal requires current secret and extends live lease')
        self.assertEqual(self.simulate(p['mutation']('expired-renew-denied',work),expiry=5)['error'],'renewal requires current secret and extends live lease')


class CoordinatorTransportTests(unittest.TestCase):
    setUpClass=classmethod(Tests.setUpClass.__func__)
    tearDownClass=classmethod(Tests.tearDownClass.__func__)
    def setUp(self):
        self.directory=Path(tempfile.mkdtemp(prefix='coordinator-',dir=self.temp.name))
        self.ctx=load(ROOT/'scripts/sql-review/run-context-control-rehearsal.py')
        self.klass=self.coor['coordinator_class'](self.ctx,self.proto)
        self.plan={'immutable_container_id':'1'*64,'run_id':'719dffcb-a5f9-4a93-bffe-7faf83f7a914','source_modules_sha256':{self.coor['COLLECTOR']:hashlib.sha256((ROOT/self.coor['COLLECTOR']).read_bytes()).hexdigest()}}
        self.evidence=self.coor['Evidence'](self.directory/'evidence',self.packet)
        self.actions=[];self.sequence=0
        outer=self
        class Session:
            def __init__(self,role,coordinator):
                outer.sequence+=1;self.role=role;self.coordinator=coordinator;self.closed=False;self.active=False;self.expected_failure=False;self.code=0;self.backend=None;self.secret=None;self.instance=None
                self.pid=str(100+outer.sequence);self.xid=str(1000+outer.sequence)
            def begin(self,isolation):outer.actions.append(('begin',self.role));self.active=True
            def capture(self):
                self.backend={'login':self.role,'current_user':self.role,'database':'wa_p0c_rehearsal','isolation':'read committed','pid':self.pid,'xid':self.xid,'started':'2026-11-18 00:00:00+00','clock':'2026-11-18 00:00:01+00'};return self.backend
            def call(self,text):
                outer.actions.append(('sql',self.role,text))
                if text.startswith('INSERT INTO platform.database_action_grant'):
                    # Parse the emitted source projection: the returned field
                    # must be created_at, and actual bound PID/xid are in VALUES.
                    outer.assertIn("RETURNING pg_catalog.jsonb_build_object('created_at',created_at); COMMIT;",text)
                    outer.assertIn('backend_pid,transaction_id',text)
                    return [json.dumps({'created_at':self.backend['clock'].replace(' ','T')+':00'})],True,''
                if text.startswith('SELECT platform_private.bind_request_context('):
                    token=re.search(r"\('([0-9a-f]{64})'\)",text)[1]
                    found=[item for item in self.coordinator.instances.values() if item['secret']==token]
                    outer.assertEqual(len(found),1);self.instance=found[0]
                    outer.assertEqual(self.instance['backend']['pid'],self.pid);outer.assertEqual(self.instance['backend']['xid'],self.xid)
                    return [],True,''
                if text.startswith('SET LOCAL wa.lease_secret='):
                    self.secret=re.search(r"wa\.lease_secret='([0-9a-f]{64})'",text)[1];return [],True,''
                return outer.operation_response(self,text)
            def close(self):self.closed=True;self.active=False;outer.actions.append(('closed',self.role));return self.code
        self.Session=Session
        self.operation_response=lambda session,text:([],True,'')
        self.instance=self.klass(self.plan,self.packet,{}, {},self.evidence,session_factory=Session)
        self.instance.text=lambda name:self.files[name].decode()
        self.instance.clock_query=lambda sql,timeout:self.instance.raw('postgres',sql)
    def tearDown(self):pass
    def model_response(self,session,text,model):
        action=session.instance['values']['action'].strip("'");grant_fence=int(session.instance['values']['source_generation'])
        result=ProjectionModelTests.simulate(None,text,**{k:model[k] for k in ('fence','attempt','expiry','now')},secret=session.secret,stored=model['stored'],action=action,grant_fence=grant_fence)
        markers=re.findall(r"SELECT '(WA_LR_[A-Z0-9_]+)';",text)
        if 'error' in result:
            name=next(key for key,value in self.proto['DIAGNOSTICS'].items() if value[1]==result['error']);session.code=3
            errors=Tests.diagnostic(self,name);return markers[:1],False,errors
        model.update(fence=result['fence'],attempt=result['attempt'],expiry=result['expiry'],stored=result['hash']);session.code=0
        return [markers[0],json.dumps({'changed':result['changed']}),markers[-1]],True,''
    def test_actual_pinned_issuer_commits_before_same_connection_bind_and_lease_sql(self):
        model={'fence':0,'attempt':0,'expiry':0,'now':10,'stored':'0'*64}
        self.operation_response=lambda session,text:self.model_response(session,text,model)
        self.instance.operation('worker-claim','claim-0','worker-claim.sql',self.instance.lease_a,0)
        issuer=next(i for i,row in enumerate(self.actions) if row[:2]==('sql','wa_context_issuer'))
        issuer_closed=next(i for i,row in enumerate(self.actions) if row==('closed','wa_context_issuer'))
        bind=next(i for i,row in enumerate(self.actions) if row[:2]==('sql','wa_worker') and row[2].startswith('SELECT platform_private.bind_request_context'))
        mutation=next(i for i,row in enumerate(self.actions) if row[:2]==('sql','wa_worker') and 'UPDATE platform.runtime_work_item' in row[2])
        self.assertLess(issuer,issuer_closed);self.assertLess(issuer_closed,bind);self.assertLess(bind,mutation)
        self.assertEqual((model['fence'],model['attempt']),(1,1));self.assertTrue(all(s.closed for s in self.instance.live))
        evidence=json.dumps(self.evidence.value)
        for secret in (self.instance.lease_a,self.instance.lease_b,self.instance.lease_c):self.assertNotIn(secret,evidence)
        self.assertNotIn('backend_pid',evidence);self.assertNotIn('transaction_id',evidence)
    def test_modelled_actual_negative_closes_before_retaining_guard_verdict(self):
        model={'fence':1,'attempt':1,'expiry':100,'now':10,'stored':hashlib.sha256(bytes.fromhex(self.instance.lease_a)).hexdigest()}
        self.operation_response=lambda session,text:self.model_response(session,text,model)
        self.instance.operation('shorten-renew-denied','renew-1','shorten-renew-denied.sql',self.instance.lease_a,1)
        current=self.evidence.value['operations'][-1];self.assertTrue(current['operation_closed']);self.assertTrue(current['outcome']['diagnostic']['matched'])
        self.assertEqual(model['expiry'],100);self.assertEqual(self.actions[-1],('closed','wa_worker'))
    def test_unrelated_guard_error_stops_after_close_without_raw_output(self):
        def response(session,text):session.code=3;return [self.proto['marker']('shorten-renew-denied','BEFORE')],False,'ERROR: P0001: '+CANARY+'\n'
        self.operation_response=response
        with self.assertRaisesRegex(self.coor['HeldFailure'],'SOURCE_OPERATION_VERDICT_NOT_PROVEN'):self.instance.operation('shorten-renew-denied','renew-1','shorten-renew-denied.sql',self.instance.lease_a,1)
        self.assertTrue(all(s.closed for s in self.instance.live));self.assertNotIn(CANARY,json.dumps(self.evidence.value))
    def test_unexpected_process_failure_keeps_partial_and_closes_all(self):
        self.operation_response=lambda *args:(_ for _ in ()).throw(RuntimeError(CANARY))
        with self.assertRaises(RuntimeError):self.instance.operation('worker-claim','claim-0','worker-claim.sql',self.instance.lease_a,0)
        self.instance.all_closed();self.assertTrue(all(s.closed for s in self.instance.live));self.assertNotIn(CANARY,json.dumps(self.evidence.value))
    def test_closure_failure_blocks_all_rollback_and_metadata_observations(self):
        self.instance.live=[SimpleNamespace(closed=False,close=lambda:(_ for _ in ()).throw(RuntimeError(CANARY)))]
        with self.assertRaisesRegex(self.coor['HeldFailure'],'OPERATION_CLOSURE_UNCONFIRMED'):self.instance.all_closed()
        self.assertFalse(self.evidence.value['operations'][-1]['all_original_sessions_closed']);self.assertNotIn(CANARY,json.dumps(self.evidence.value))
    def test_clock_poll_rejects_wrong_types_without_leaking_probe_values(self):
        self.instance.raw=lambda *args:json.dumps({'expired':CANARY,'same_fence':True,'same_attempt':True,'effect_absent':True})
        with self.assertRaisesRegex(self.coor['HeldFailure'],'BOUNDED_CLOCK_OBSERVATION_REQUIRED'):self.instance.wait_expired()
        self.assertNotIn(CANARY,json.dumps(self.evidence.value))
    def test_clock_wait_is_bounded_and_never_mutates_expiry(self):
        clocks=iter([0,0,0,46]);calls=[];self.instance.clock=lambda:next(clocks);self.instance.sleep=lambda seconds:calls.append(('sleep',seconds))
        self.instance.raw=lambda role,text:(calls.append(('sql',text)) or json.dumps({'expired':False,'same_fence':True,'same_attempt':True,'effect_absent':True}))
        with self.assertRaisesRegex(self.coor['HeldFailure'],'ACTUAL_LEASE_EXPIRY_NOT_OBSERVED'):self.instance.wait_expired()
        self.assertTrue(all('UPDATE' not in row[1] for row in calls if row[0]=='sql'));self.assertEqual([r for r in calls if r[0]=='sleep'],[('sleep',.1)])
    def test_slow_expired_response_after_deadline_cannot_qualify_expiry(self):
        clocks=iter([0,0,0,1,46]);responses=iter([False,True]);timeouts=[];self.instance.clock=lambda:next(clocks);self.instance.sleep=lambda seconds:None
        def clock_query(sql,timeout):timeouts.append(timeout);return json.dumps({'expired':next(responses),'same_fence':True,'same_attempt':True,'effect_absent':True})
        self.instance.clock_query=clock_query
        with self.assertRaisesRegex(self.coor['HeldFailure'],'ACTUAL_LEASE_EXPIRY_NOT_OBSERVED'):self.instance.wait_expired()
        self.assertEqual(timeouts,[5,5]);self.assertTrue(self.evidence.value['current']['clock_budget_exhausted']);self.assertFalse(self.evidence.value['current']['actual_clock_expiry_qualified'])
        self.assertNotIn('actual_clock_expired',self.evidence.value['current'])
    def test_clock_process_timeout_is_remaining_budget_bound_and_safe(self):
        self.instance.psql=lambda role:['MOCK_DOCKER_DATABASE',role];calls=[]
        def process(args,**options):calls.append(options['timeout']);return SimpleNamespace(returncode=0,stdout='{}',stderr='')
        with patch.object(self.ctx['subprocess'],'run',side_effect=process):self.assertEqual(self.instance.clock_observation('SOURCE_CLOCK_SQL',.125),'{}')
        self.assertEqual(calls,[.125])
        with patch.object(self.ctx['subprocess'],'run',side_effect=subprocess.TimeoutExpired('MOCK',.125,output=CANARY,stderr=CANARY)),self.assertRaisesRegex(self.coor['HeldFailure'],'LEASE_CLOCK_QUERY_TIMEOUT_CLOSURE_UNCONFIRMED'):self.instance.clock_observation('SOURCE_CLOCK_SQL',.125)
        self.assertNotIn(CANARY,json.dumps(self.evidence.value))
    def test_old_holder_live_then_actual_expiry_are_both_observed(self):
        values=iter([False,True]);self.instance.clock=lambda:0;self.instance.sleep=lambda seconds:None
        self.instance.raw=lambda *a:json.dumps({'expired':next(values),'same_fence':True,'same_attempt':True,'effect_absent':True})
        self.instance.wait_expired();self.assertTrue(self.evidence.value['current']['actual_clock_expired']);self.assertTrue(self.evidence.value['current']['live_lease_observed_after_old_holder_bind'])
    def test_already_expired_old_holder_precondition_is_unexpected(self):
        self.instance.raw=lambda *a:json.dumps({'expired':True,'same_fence':True,'same_attempt':True,'effect_absent':True})
        with self.assertRaisesRegex(self.coor['HeldFailure'],'OLD_HOLDER_MUST_BIND_DURING_LIVE_LEASE'):self.instance.wait_expired()
    def test_three_lease_preimages_must_be_independent(self):
        with patch.object(self.coor['secrets'],'token_hex',return_value='a'*64),self.assertRaisesRegex(self.coor['HeldFailure'],'THREE_INDEPENDENT_LEASE_PREIMAGES_REQUIRED'):
            self.klass(self.plan,self.packet,{}, {},self.evidence,session_factory=self.Session)
    def test_global_closure_rejects_other_database_or_tag_and_retains_fixed_result(self):
        queries=[];self.instance.raw=lambda role,sql:(queries.append(sql) or '1')
        with self.assertRaisesRegex(self.coor['HeldFailure'],'GLOBAL_CLIENT_CLOSURE_REQUIRED'):self.instance.global_closed()
        self.assertNotIn('datname',queries[0]);self.assertNotIn('application_name',queries[0]);self.assertNotIn('usename',queries[0])
        self.assertFalse(self.evidence.value['operations'][-1]['all_other_client_backends_absent'])
        self.instance.raw=lambda *a:(_ for _ in ()).throw(RuntimeError(CANARY))
        with self.assertRaisesRegex(self.coor['HeldFailure'],'GLOBAL_CLIENT_CLOSURE_REQUIRED'):self.instance.global_closed()
        self.assertFalse(self.evidence.value['operations'][-1]['observation_completed']);self.assertNotIn(CANARY,json.dumps(self.evidence.value))
    def test_rollback_witness_keeps_prior_captured_transaction_not_a_new_baseline(self):
        self.instance.state=1;queries=[];self.instance.observe=lambda stage,sql,expected:queries.append(sql)
        self.instance.work_observe('lease',{'xid':'1500'});self.instance.work_observe('lease')
        self.assertTrue(all("mutation_transaction_id='1500'" in sql for sql in queries))
    def test_complete_state_refuses_an_original_open_session_before_any_observer(self):
        self.instance.live=[SimpleNamespace(closed=False)];calls=[];self.instance.raw=lambda *a:calls.append(a)
        with self.assertRaisesRegex(self.coor['HeldFailure'],'ALL_ORIGINAL_SESSIONS_MUST_CLOSE_BEFORE_STATE_OBSERVERS'):self.instance.complete()
        self.assertEqual(calls,[])
    def test_recovery_commits_before_old_generation_probe_and_not_twice(self):
        calls=[];self.instance.identity=lambda step:calls.append(('Identity',step));self.instance.opened=lambda template,**kw:(calls.append(('bind',template['security_generation'],kw)) or (None,None));self.instance.complete=lambda:calls.append(('complete',))
        self.instance.case('app-old-after-recover');self.assertEqual(calls[0],('Identity','recover'));self.assertEqual(calls[1][0:2],('bind','1'))
    def test_issuer_revocation_retains_exact_new_mutation_xid_and_old_consumer_tuple(self):
        committed=[]
        def response(session,text):
            if session.role=='wa_context_issuer':
                self.assertIn('UPDATE platform.database_action_grant SET revoked_at=clock_timestamp()',text);committed.append(session.backend['xid']);return ['{"changed":1}'],True,''
            self.assertEqual(session.role,'wa_app_runtime');self.assertTrue(committed);self.assertIn('count(*)',text);return ['{"visible_exact_work":0}'],True,''
        self.operation_response=response;self.instance.complete=lambda:None
        self.instance.case('app-issuer-revocation');key=next(iter(self.instance.revoked));value=self.instance.instances[key]
        self.assertEqual(value['values']['mutation_transaction_id'],"'"+committed[0]+"'")
        self.assertNotEqual(value['values']['transaction_id'],value['values']['mutation_transaction_id'])
        self.assertEqual(value['values']['transaction_id'],"'"+value['backend']['xid']+"'")
        self.assertTrue(all(session.closed for session in self.instance.live))
    def test_actual_context_capture_rejects_wrong_login_projection(self):
        fake=SimpleNamespace(active=True,isolation='read committed',role='wa_worker',backend=None)
        response={'login':'wa_app_runtime','current_user':'wa_app_runtime','database':'wa_p0c_rehearsal','isolation':'read committed','pid':'101','xid':'1001','started':'2026-11-18 00:00:00+00','clock':'2026-11-18 00:00:01+00'}
        def call(sql):self.assertIn('pg_backend_pid()',sql);self.assertIn('pg_current_xact_id()',sql);return [self.ctx['TUPLE']+json.dumps(response)],True,''
        fake.call=call
        with self.assertRaisesRegex(self.ctx['HeldFailure'],'CAPTURE_ACTUAL_IDENTITY'):self.ctx['Session'].capture(fake)
    def old_context_fixture(self):
        old,key=self.instance.opened(self.packet['grants']['old-holder'],self.instance.lease_a,1);self.instance.old_key=key;self.instance.renew_positive_proven=True
        values=dict.fromkeys(('exact_original_tuple_and_immutable_grant','unrevoked','context_grant_unexpired','renew_route_exact','independent_service_epoch_current','higher_fence_lease_still_live','original_backend_live'),True)
        return old,key,values
    def test_old_fence_witness_distinguishes_context_TTL_live_lease_and_exact_renew_route(self):
        from pglast import parse_sql
        old,key,values=self.old_context_fixture();queries=[]
        self.instance.raw=lambda role,sql:(queries.append(sql) or json.dumps(values));self.instance.old_context_current('BEFORE_STALE_ACTION',True)
        self.assertTrue(parse_sql(queries[0]));self.assertIn('g.expires_at>clock_timestamp()',queries[0]);self.assertIn('lease_expires_at>clock_timestamp()',queries[0]);self.assertIn("g.action='runtime.renew_work.v1'",queries[0]);self.assertIn('g.revoked_at IS NULL',queries[0]);self.assertIn('a.security_generation=g.security_generation',queries[0])
        old.close();values['original_backend_live']=False;self.instance.old_context_current('AFTER_STALE_ACTION',False)
        self.assertTrue(parse_sql(queries[-1]));evidence=json.dumps(self.evidence.value)
        for value in self.instance.instances[key].values():
            if type(value) is str and len(value)>=32:self.assertNotIn(value,evidence)
        self.assertNotIn('"pid":',evidence);self.assertNotIn('"xid":',evidence)
    def test_expired_revoked_wrong_route_or_service_epoch_never_qualifies_old_fence(self):
        old,key,values=self.old_context_fixture()
        for field in ('unrevoked','context_grant_unexpired','renew_route_exact','independent_service_epoch_current','higher_fence_lease_still_live'):
            bad={**values,field:False};self.instance.raw=lambda *args,bad=bad:json.dumps(bad)
            with self.assertRaisesRegex(self.ctx['HeldFailure'],'COMPLETE_STATE_OBSERVER_MISMATCH'):self.instance.old_context_current('BEFORE_STALE_ACTION',True)
        old.close()
    def test_old_fence_witness_requires_preceding_real_renew_positive(self):
        calls=[];self.instance.raw=lambda *a:calls.append(a)
        with self.assertRaisesRegex(self.coor['HeldFailure'],'PRIOR_VALID_RENEW_AND_FIXED_PHASE_REQUIRED'):self.instance.old_context_current('BEFORE_STALE_ACTION',True)
        self.assertEqual(calls,[])

if __name__=='__main__':unittest.main(verbosity=2)
