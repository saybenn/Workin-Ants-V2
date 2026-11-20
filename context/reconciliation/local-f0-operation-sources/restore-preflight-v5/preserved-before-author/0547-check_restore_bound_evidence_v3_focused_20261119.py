"""Actual new initializer/Steps/WorkerSession, process-boundary-only models."""
from contextlib import ExitStack,redirect_stdout
from pathlib import Path
from types import SimpleNamespace
import ast,copy,hashlib,io,json,queue,re,runpy,socket,subprocess,tempfile,threading,unittest
from unittest.mock import Mock,patch
T=Path(__file__).resolve().parent;R=T/'workinants-correction-pass'
CORE=T/'execute_local_f0_restore_20261119_bound_evidence_v3.py';STEPS=T/'local_f0_restore_operation_steps_bound_evidence_v3.py'
PROPOSAL=json.loads((R/'review-output/restore-control-rehearsal/proposal.json').read_bytes());CANARY='PRIVATE_BOUND_RESPONSE_AND_SECRET_CANARY_NEVER_EXPORT'
def sha(b):return hashlib.sha256(b).hexdigest()
class Pipe:
    def __init__(self):self.q=queue.Queue();self.closed=False
    def feed(self,value):self.q.put(value)
    def readline(self,size=-1):return self.q.get(timeout=10)
    def read(self,size=-1):return self.q.get(timeout=10)
    def end(self):self.q.put('')
class Input:
    def __init__(self,process):self.process=process;self.buffer='';self.closed=False
    def write(self,text):self.buffer+=text
    def flush(self):text=self.buffer;self.buffer='';self.process.flush(text)
    def close(self):self.closed=True
class Process:
    def __init__(self,world,args,kwargs):
        self.world=world;self.args=args;self.role=args[args.index('-U')+1];self.returncode=None;self.stdout=Pipe();self.stderr=Pipe();self.stdin=Input(self);self.number=len(world.processes)+1;world.processes.append(self);world.events.append(('open',self.role))
    def exit(self,code):
        if self.returncode is None:self.returncode=code;self.stdout.end();self.stderr.end()
    def flush(self,text):
        w=self.world
        if text.startswith('BEGIN ISOLATION LEVEL READ COMMITTED;'):
            w.events.append(('capture',self.role))
            if w.capture_failure:raise OSError(CANARY)
            backend={'login':self.role,'current_user':self.role,'database':w.n['DB'],'isolation':'read committed','pid':str(8100+self.number),'xid':str(900000+self.number),'started':'2026-11-18 00:00:00+00'};self.stdout.feed('WA_WORKER_COORDINATOR_TUPLE|'+json.dumps(backend)+'\n');return
        if text.startswith('ROLLBACK;') or text.startswith('\\q'):
            w.events.append(('close',self.role));self.exit(0);return
        token=re.search(r"SELECT '(WA_WORKER_COORDINATOR_ACK\|[0-9a-f]+)';",text)
        if token is None:raise AssertionError('UNMODELED_WORKER_SEND')
        ack=token[1]
        if text.startswith("SELECT jsonb_build_object('clock',clock_timestamp());"):
            rows=[json.dumps({'clock':'2026-11-18T05:00:00+00:00'})]
        elif self.role=='wa_context_issuer':
            w.events.append(('issuer_finish',self.role));rows=[json.dumps({'created_at':'2026-11-18T05:00:00.001+00:00','expires_at':'2026-11-18T05:05:00+00:00'})]
        elif 'SELECT pg_current_xact_id()::text=' in text:
            w.events.append(('same_xid',self.role));rows=['t']
        else:
            negative=text.count('COMMIT;')==0;w.events.append(('negative_bind' if negative else 'bound_finish',self.role))
            if negative or w.error is not None:
                self.stderr.feed(w.binder_error() if negative else w.error);self.exit(3);return
            rows=w.rows
        for row in rows:self.stdout.feed(row+'\n')
        self.stdout.feed(ack+'\n')
    def poll(self):return self.returncode
    def wait(self,timeout=None):
        if self.returncode is None:raise subprocess.TimeoutExpired('PRIVATE_DISCARDED_ARGS',timeout)
        return self.returncode
    def terminate(self):self.world.events.append(('terminate',self.role));self.exit(0)
    def kill(self):self.exit(0)
class World:
    def __init__(self,n):self.n=n;self.events=[];self.processes=[];self.rows=['WA_CUSTOMER_CONTROL_READY_TO_COMMIT'];self.error=None;self.capture_failure=False;self.constructor_failure=False;self.global_count=0;self.close_count=0;self.present_c=set(n['RESOURCE_CONTAINERS']);self.present_v=set(n['RESOURCE_VOLUMES'])
    def popen(self,args,**kwargs):
        if self.constructor_failure:raise OSError(CANARY)
        return Process(self,list(args),kwargs)
    def binder_error(self):
        raw=(R/'review-output/foundation-application.review.sql').read_text();body=re.search(r'CREATE FUNCTION platform_private\.bind_request_context\(secret text\).*?AS (\$[a-z_0-9]*\$)(.*?)\1;',raw,re.S)[2];line=next(i for i,v in enumerate(body.split('\n'),1) if "RAISE EXCEPTION 'invalid, stale or unsupported context'" in v);return 'ERROR:  42501: invalid, stale or unsupported context\nCONTEXT:  PL/pgSQL function platform_private.bind_request_context(text) line '+str(line)+' at RAISE\n'
    def result(self,stdout='',code=0,stderr=''):return SimpleNamespace(returncode=code,stdout=stdout,stderr=stderr)
    def run(self,args,input=None,**kwargs):
        n=self.n;args=list(args)
        if 'psql' in args:
            if input.startswith('SELECT count(*) FROM pg_stat_activity WHERE pid='):self.events.append(('backend_close',args[args.index('-U')+1]));return self.result(str(0 if "usename='wa_context_issuer'" in input else self.close_count)+'\n')
            if input==n['_SAFETY_SQL_RECIPES']['GLOBAL_BACKENDS']:self.events.append(('global_zero',));return self.result(json.dumps({'migrator':0,'other_client_backends':self.global_count}))
            if input==n['_SAFETY_SQL_RECIPES']['FINALIZATION_BACKENDS']:self.events.append(('finalizer_pre',));return self.result('{"migrator":0,"other_client_backends":0}')
            if input==n['_SAFETY_SQL_RECIPES']['FINALIZATION_RESULT']:self.events.append(('finalizer_post',));return self.result(json.dumps({'grantor':'postgres','auth':'scram-sha-256:postgres','remaining_memberships':0,'leaf_create':dict.fromkeys(n['LEAVES'],False),'active_install_connections':0}))
            if input==(R/'review-output/foundation-bootstrap-finalize.review.sql').read_text():self.events.append(('finalizer',));return self.result()
            if "'exact_fields'" in input:self.events.append(('grant_facts',));return self.result(json.dumps({'count':1,'row_sha256':'e'*64,'issuer_owned':True,'unrevoked':True,'unexpired':True,'exact_fields':True}))
            raise AssertionError('UNMODELED_SQL_BOUNDARY')
        assert args[:3]==['docker','--context','desktop-linux'];part=args[3:]
        if part[:3]==['container','ls','-a']:return self.result('\n'.join(sorted(self.present_c)))
        if part[:2]==['volume','ls']:return self.result('\n'.join(sorted(self.present_v)))
        if part[:2]==['container','inspect']:
            name=part[-1];return self.result(json.dumps([{'Name':'/'+name,'Id':n['created_containers'][name],'Config':{'Labels':{'workinants.rehearsal':n['LABEL'],'workinants.rehearsal.run':n['RUN_ID']}}}]))
        if part[:2]==['volume','inspect']:
            name=part[-1];return self.result(json.dumps([{'Name':name,'Labels':{'workinants.rehearsal':n['LABEL'],'workinants.rehearsal.run':n['RUN_ID']},'CreatedAt':n['created_volumes'][name]}]))
        if part[:3]==['container','rm','-f']:
            name=next(k for k,v in n['created_containers'].items() if v==part[-1]);self.present_c.discard(name);self.events.append(('remove_container',name));return self.result()
        if part[:2]==['volume','rm']:self.present_v.discard(part[-1]);self.events.append(('remove_volume',part[-1]));return self.result()
        raise AssertionError('UNMODELED_PROCESS_BOUNDARY')
class BoundEvidenceTests(unittest.TestCase):
    def setUp(self):
        self.stack=ExitStack();self.addCleanup(self.stack.close);tmp=tempfile.TemporaryDirectory(prefix='restore-bound-evidence-',dir=T);self.addCleanup(tmp.cleanup);self.base=Path(tmp.name);out=self.base/'evidence';run='550e8400-e29b-41d4-a716-446655440000';source='wa-p0c-'+run[:8]+'-restore-source';master={'purpose':'LOCAL_F0_RESTORE_REHEARSAL','evidence_directory':str(out),'source_commit':'a'*40,'source_tree':'b'*40,'packet_sha256':'c'*64,'run_id':run,'targets':[{'name':source,'volume':source+'-data','kind':'ok'}]};mp=self.base/'manifest.json';mp.write_text(json.dumps(master));n=runpy.run_path(str(CORE))['launch'].__globals__;n['initialize'](mp);exec(compile(STEPS.read_bytes(),str(STEPS),'exec'),n);out.mkdir();n['PRIVATE'].mkdir();n['PROPOSAL']=copy.deepcopy(PROPOSAL);n['report']['restore']={};n['SOURCE']=source;n['RESTORED']='wa-p0c-'+run[:8]+'-restore-target';n['STAGING']='wa-p0c-'+run[:8]+'-restore-staging';n['ARCHIVE']=n['PRIVATE']/'restore01-base.tar';n['HELPERS'].clear();n['GRANTS'].clear();n['created_containers']={name:format(i+1,'064x') for i,name in enumerate(n['RESOURCE_CONTAINERS'])};n['created_volumes']={name:'FIXED_CREATED_AT' for name in n['RESOURCE_VOLUMES']};n['attempted_containers']=set(n['RESOURCE_CONTAINERS']);n['attempted_volumes']=set(n['RESOURCE_VOLUMES']);n['report']['targets']={name:{'finalization':'NOT_RUN'} for name in n['RESOURCE_CONTAINERS']}
        pins=dict(PROPOSAL['source_files_sha256']);pins.update({'review-output/restore-control-rehearsal/'+name:h for name,h in PROPOSAL['prepared_files_sha256'].items()});pins.update({name:sha((R/name).read_bytes()) for name in (*n['HELPER_FILES'],n['RESTORE_BOUND_DECLARATION'],n['RESTORE_BOUND_SOURCE'],'review-output/foundation-bootstrap-finalize.review.sql')});n['MANIFEST']['packet_files_sha256']=pins;n['report']['source_verification']={'files_sha256':pins};self.n=n;self.world=World(n)
        self.stack.enter_context(patch.object(subprocess,'Popen',side_effect=self.world.popen));self.stack.enter_context(patch.object(subprocess,'run',side_effect=self.world.run))
        for name in ('call','check_call','check_output'):self.stack.enter_context(patch.object(subprocess,name,side_effect=AssertionError('UNMOCKED_PROCESS_FORBIDDEN')))
        self.stack.enter_context(patch.object(socket,'create_connection',side_effect=AssertionError('NETWORK_FORBIDDEN')));n['WORKER']=n['load_reviewed_helper']('scripts/sql-review/run-worker-control-rehearsal.py')
    def invoke(self,grant='source_customer',negative=False,old=None):
        n=self.n;return n['bound_operation'](n['SOURCE'],grant,n['source_text']('source-customer.sql') if grant=='source_customer' else '',expected_lines=PROPOSAL['source_customer']['stage_marker_oracle']['expected_completed_markers'],old=old,negative=negative)
    def proof(self):return self.n['report']['restore']['bound_operations'][-1]
    def safe(self):
        exported=json.dumps(self.n['report']);self.assertNotIn(CANARY,exported)
        for value in self.n['all_secrets']:self.assertNotIn(value,exported)
        for process in self.world.processes:self.assertNotIn('"'+str(900000+process.number)+'"',exported)
    def test_actual_initializer_worker_session_positive_issuer_commit_and_global_closure(self):
        record=self.invoke();proof=self.proof();self.assertTrue(proof['matched']);self.assertTrue(proof['operation_closed']);self.assertEqual(proof['outcome']['exit_code'],0);self.assertEqual(proof['outcome']['marker_presence'],[True]);self.assertEqual(self.world.events[-1],('global_zero',));self.assertLess(self.world.events.index(('issuer_finish','wa_context_issuer')),self.world.events.index(('same_xid','wa_app_runtime')));self.assertNotIn(record['id'],json.dumps(self.n['report']));self.safe()
    def test_unexpected_positive_error_has_partial_exit_ack_diagnostic_before_stop(self):
        self.world.error='ERROR:  42703: '+CANARY+'\nCONTEXT:  '+CANARY+'\n'
        with self.assertRaises(self.n['Stop']) as error:self.invoke()
        self.assertEqual(error.exception.code,'RESTORE_BOUND_OPERATION_NOT_COMMITTED');proof=self.proof();self.assertEqual(proof['outcome']['exit_code'],3);self.assertFalse(proof['outcome']['acknowledgement']);self.assertEqual(proof['outcome']['diagnostic']['sqlstate'],'42703');self.assertTrue(proof['operation_closed']);self.assertFalse(proof['matched']);self.assertEqual(self.world.events[-1],('global_zero',));self.safe()
    def test_exact_negative_binder_predicate_stays_required(self):
        old={'id':'NOT_EXPORTED','secret':'1'*64,'backend':{'pid':'1','xid':'1'},'grant':PROPOSAL['grants']['app']};self.invoke('app',negative=True,old=old);self.assertTrue(self.proof()['matched']);self.assertTrue(self.proof()['operation_closed']);self.assertEqual(self.proof()['outcome']['exit_code'],3);self.assertNotIn(('bound_finish','wa_app_runtime'),self.world.events);self.safe()
    def test_constructor_and_capture_failures_always_attempt_global_zero(self):
        self.world.constructor_failure=True
        with self.assertRaises(self.n['Stop']):self.invoke()
        self.assertFalse(self.proof()['operation_closed']);self.assertTrue(self.proof()['global_zero_confirmed']);self.assertEqual(self.world.events[-1],('global_zero',))
        self.world.constructor_failure=False;self.world.capture_failure=True
        with self.assertRaises(self.n['Stop']):self.invoke()
        self.assertFalse(self.proof()['session_close_confirmed']);self.assertTrue(self.proof()['global_zero_confirmed']);self.assertEqual(self.world.events[-1],('global_zero',));self.safe()
    def test_failed_session_close_preserves_original_error_then_observes_global(self):
        self.world.error='ERROR:  22012: '+CANARY+'\n';self.world.close_count=1
        with self.assertRaises(self.n['Stop']) as error:self.invoke()
        self.assertEqual(error.exception.code,'RESTORE_BOUND_OPERATION_NOT_COMMITTED');self.assertFalse(self.proof()['operation_closed']);self.assertTrue(self.proof()['global_zero_confirmed']);self.assertEqual(self.n['report']['primary_failure']['code'],'RESTORE_BOUND_OPERATION_NOT_COMMITTED');self.safe()
    def test_active_global_clients_cannot_qualify_or_run_later_observer(self):
        self.world.global_count=1;later=Mock()
        with self.assertRaises(self.n['Stop']):self.invoke();later()
        later.assert_not_called();self.assertFalse(self.proof()['operation_closed']);self.assertFalse(self.proof()['matched']);self.safe()
    def test_persistent_evidence_io_still_attempts_global_and_never_passes(self):
        original=Path.open
        def fail(path,*args,**kwargs):
            mode=args[0] if args else kwargs.get('mode','r')
            if path.is_relative_to(self.n['OUT']) and any(c in mode for c in 'wax'):raise OSError(CANARY)
            return original(path,*args,**kwargs)
        with patch.object(Path,'open',fail),self.assertRaises(self.n['Stop']):self.invoke()
        self.assertEqual(self.world.events,[('global_zero',)]);self.assertFalse(self.proof()['operation_closed']);self.assertFalse(self.n['evidence_is_complete']());self.safe()
    def test_closed_metadata_column_and_no_argument_frame_are_source_bound(self):
        errors='ERROR:  42703: record "new" has no field "accepted_at"\nCONTEXT:  PL/pgSQL function platform_private.block_usage_mutation() line 1 at RAISE\n';value=self.n['bound_diagnostic'](errors);self.assertTrue(value['source_binding_confirmed']);meta=value['source_metadata'];self.assertEqual(meta['column'],'accepted_at');self.assertEqual(meta['frame']['body_line'],1);self.assertEqual(meta['source_sha256'],self.n['RESTORE_BOUND_SOURCE_SHA']);self.safe()
    def test_fixed13_only_single_exact_headers_never_export_unknown_or_multiple(self):
        self.assertEqual(len(self.n['RESTORE_BOUND_STATES']),13)
        for state in self.n['RESTORE_BOUND_STATES']:
            value=self.n['bound_diagnostic']('ERROR:  '+state+': '+CANARY+'\n');self.assertEqual(value['sqlstate'],state);self.assertNotIn(CANARY,json.dumps(value))
        for errors in ('ERROR:  XXXXX: '+CANARY,'ERROR: malformed\nERROR:  42501: '+CANARY,'ERROR:  42501: one\nFATAL:  42501: two',CANARY,None,CANARY*7000,'ERROR:  42501: '+CANARY+'\x00'):
            value=self.n['bound_diagnostic'](errors);self.assertIsNone(value['sqlstate']);self.assertFalse(value['source_binding_confirmed']);self.assertNotIn(CANARY,json.dumps(value))
    def test_inline_and_malformed_severity_candidates_are_not_one_attributable_header(self):
        vectors=('ERROR:  42501: fixed ERROR:  22012: second\n','ERROR:  42501: fixed\nERROR malformed\n','ERROR:  42501: '+CANARY+'FATAL:  22012: second\n','ERROR:  42501: fixed\nFATAL malformed\n')
        for errors in vectors:
            value=self.n['bound_diagnostic'](errors);self.assertIsNone(value['sqlstate']);self.assertFalse(value['single_header']);self.assertFalse(value['source_binding_confirmed']);self.assertIsNone(value['source_metadata']);self.assertEqual(value['redaction'],'NO_SINGLE_EXACT_HEADER');self.assertNotIn(CANARY,json.dumps(value))
        for errors in vectors[:2]:
            self.world.error=errors
            with self.assertRaises(self.n['Stop']) as error:self.invoke()
            self.assertEqual(error.exception.code,'RESTORE_BOUND_OPERATION_NOT_COMMITTED');self.assertIsNone(self.proof()['outcome']['diagnostic']['sqlstate']);self.assertTrue(self.proof()['operation_closed']);self.assertFalse(self.proof()['matched']);self.safe()
    def test_bad_types_controls_and_multiple_headers_keep_state_and_single_header_unconfirmed(self):
        for errors in (None,0,[],{'stderr':CANARY},'ERROR:  42501: '+CANARY+'\x00','ERROR:  42501: '+CANARY+'\x1f','ERROR:  42501: one\nFATAL:  22012: two\n','ERROR malformed','prefixERROR:  42501: hidden'):
            value=self.n['bound_diagnostic'](errors);self.assertIsNone(value['sqlstate']);self.assertFalse(value['single_header']);self.assertFalse(value['source_binding_confirmed']);self.assertNotIn(CANARY,json.dumps(value))
    def test_single_exact_header_with_legitimate_multiline_pg_context_stays_source_bound(self):
        errors='psql:<stdin>:19: ERROR:  42703: record "new" has no field "accepted_at"\r\nDETAIL:  '+CANARY+'\r\nCONTEXT:  SQL statement "SELECT 1"\r\nPL/pgSQL function platform_private.block_usage_mutation() line 1 at RAISE\r\n'
        value=self.n['bound_diagnostic'](errors);self.assertEqual(value['sqlstate'],'42703');self.assertTrue(value['single_header']);self.assertTrue(value['source_binding_confirmed']);self.assertEqual(value['source_metadata']['column'],'accepted_at');self.assertEqual(value['source_metadata']['frame']['body_line'],1);self.assertNotIn(CANARY,json.dumps(value))
    def test_restoring_only_original_header_classifier_fails_both_required_null_expectations(self):
        path=T/'restore-bound-evidence-v3-author-freeze-20261119/files/TASK/local_f0_restore_operation_steps_bound_evidence_v3.py';raw=path.read_bytes();self.assertEqual(sha(raw),'cbc5485b76bc8d1d84b9fb1bb0cbbd8a490c7d4ae4f3e08d2ed1c11920223944');node=next(n for n in ast.parse(raw).body if isinstance(n,ast.FunctionDef) and n.name=='bound_diagnostic');scope=dict(self.n);exec(compile(ast.Module(body=[node],type_ignores=[]),str(path),'exec'),scope)
        for errors in ('ERROR:  42501: fixed ERROR:  22012: second\n','ERROR:  42501: fixed\nERROR malformed\n'):
            value=scope['bound_diagnostic'](errors);self.assertEqual(value['sqlstate'],'42501');self.assertTrue(value['single_header'])
            with self.assertRaises(AssertionError):self.assertIsNone(value['sqlstate'])
    def test_helper_metadata_arbitrary_keys_or_unbound_frames_are_discarded(self):
        helper=self.n['load_reviewed_helper']('scripts/sql-review/run-first-rehearsal.py');original=helper['source_metadata'];decl=json.loads((R/self.n['RESTORE_BOUND_DECLARATION']).read_bytes());function=decl['no_argument_plpgsql_functions']['platform_private.block_usage_mutation'];valid={'classification':'UNRECOGNIZED','frame_classification':'SOURCE_BOUND_FRAME','frame':{'schema':'platform_private','function':'block_usage_mutation','body_line':1,'body_sha256':function['body_sha256'],'source_sha256':self.n['RESTORE_BOUND_SOURCE_SHA']}}
        mutations=[dict(valid,unknown=CANARY)]
        for key,value in (('body_line',True),('body_line',3),('body_sha256','0'*64),('source_sha256','0'*64),('function',CANARY)):
            changed=copy.deepcopy(valid);changed['frame'][key]=value;mutations.append(changed)
        for value in mutations:
            helper['source_metadata']=lambda errors,value=value:value
            result=self.n['bound_diagnostic']('ERROR:  42501: '+CANARY+'\n');self.assertFalse(result['source_binding_confirmed']);self.assertIsNone(result['source_metadata']);self.assertNotIn(CANARY,json.dumps(result))
        helper['source_metadata']=original
    def test_metadata_enum_and_alias_require_exact_builtin_strings(self):
        helper=self.n['load_reviewed_helper']('scripts/sql-review/run-first-rehearsal.py')
        class Disguised(str):
            def __eq__(self,other):return True
            def __hash__(self):return hash('UNRECOGNIZED')
        values=[{'classification':Disguised(CANARY),'frame_classification':'NOT_RETAINED'},{'classification':'RECORD_FIELD_MISSING','frame_classification':'NOT_RETAINED','record_alias':Disguised(CANARY),'column':'accepted_at','source_sha256':self.n['RESTORE_BOUND_SOURCE_SHA']}]
        for value in values:
            helper['source_metadata']=lambda errors,value=value:value;result=self.n['bound_diagnostic']('ERROR:  42703: '+CANARY+'\n');self.assertFalse(result['source_binding_confirmed']);self.assertIsNone(result['source_metadata']);self.assertNotIn(CANARY,json.dumps(result))
    def test_declaration_or_source_drift_before_after_helper_is_not_accepted(self):
        helper=self.n['load_reviewed_helper']('scripts/sql-review/run-first-rehearsal.py');original_helper=helper['source_metadata'];original_read=self.n['read_pinned']
        for name in (self.n['RESTORE_BOUND_DECLARATION'],self.n['RESTORE_BOUND_SOURCE']):
            calls=[0]
            def read(path):
                raw=original_read(path)
                if path==name:
                    calls[0]+=1
                    if calls[0]>1:return raw+b' '
                return raw
            with patch.dict(self.n,read_pinned=read):value=self.n['bound_diagnostic']('ERROR:  42501: '+CANARY+'\n')
            self.assertFalse(value['source_binding_confirmed']);self.assertIsNone(value['source_metadata']);self.assertNotIn(CANARY,json.dumps(value))
    def test_malformed_outcomes_are_only_fixed_counts_and_booleans(self):
        for code,lines,ack,errors in ((True,[],True,''),(0,[CANARY],1,''),(0,{},True,''),(0,[CANARY*7000],True,''),(0,[CANARY],True,None)):
            value=self.n['bound_outcome'](code,lines,ack,errors,expected_json={'visible_exact_root':1});self.assertFalse(value['fields_typed']);self.assertNotIn(CANARY,json.dumps(value))
    def test_restoring_old_bound_operation_loses_required_partial_evidence(self):
        raw=(T/'local_f0_restore_operation_steps_resource_mount_v2.py').read_bytes();node=next(x for x in ast.parse(raw).body if isinstance(x,ast.FunctionDef) and x.name=='bound_operation');exec(compile(ast.Module(body=[node],type_ignores=[]),'RESTORED_OLD_BOUND_OPERATION','exec'),self.n);self.world.error='ERROR:  42703: '+CANARY+'\n'
        with self.assertRaises(self.n['Stop']):self.invoke()
        with self.assertRaises((AssertionError,KeyError)):self.assertTrue(self.n['report']['restore']['bound_operations'][-1]['outcome']['exit_code']==3)
        self.assertNotIn(('global_zero',),self.world.events);self.safe()
    def test_actual_json_success_and_canary_row_failure_keep_only_comparisons(self):
        self.world.rows=['{"visible_exact_root":1}'];self.n['bound_operation'](self.n['SOURCE'],'app','SELECT 1;',expected_json={'visible_exact_root':1});self.assertTrue(self.proof()['outcome']['json_shape_matches']);self.assertTrue(self.proof()['outcome']['json_matches']);self.assertTrue(self.proof()['matched'])
        self.world.rows=[json.dumps({'visible_exact_root':CANARY})]
        with self.assertRaises(self.n['Stop']) as error:self.n['bound_operation'](self.n['SOURCE'],'app','SELECT 1;',expected_json={'visible_exact_root':1})
        self.assertEqual(error.exception.code,'RESTORE_READ_RESULT');self.assertFalse(self.proof()['outcome']['json_matches']);self.assertFalse(self.proof()['matched']);self.assertTrue(self.proof()['operation_closed']);self.safe()
    def test_incomplete_source_markers_and_extra_output_preserve_count_before_stop(self):
        for rows in ([],['NOT_A_SOURCE_MARKER'],['WA_CUSTOMER_CONTROL_READY_TO_COMMIT',CANARY]):
            self.world.rows=rows
            with self.assertRaises(self.n['Stop']) as error:self.invoke()
            self.assertEqual(error.exception.code,'RESTORE_SOURCE_MARKERS');self.assertEqual(self.proof()['outcome']['line_count'],len(rows));self.assertFalse(self.proof()['outcome']['marker_order_matches']);self.assertFalse(self.proof()['matched']);self.safe()
    def test_negative_guard_cannot_pass_if_source_metadata_is_unconfirmed(self):
        helper=self.n['load_reviewed_helper']('scripts/sql-review/run-first-rehearsal.py');helper['source_metadata']=lambda errors:{'classification':CANARY};old={'id':'NOT_EXPORTED','secret':'1'*64,'backend':{'pid':'1','xid':'1'},'grant':PROPOSAL['grants']['app']}
        with self.assertRaises(self.n['Stop']) as error:self.invoke('app',negative=True,old=old)
        self.assertEqual(error.exception.code,'RESTORE_BOUND_DIAGNOSTIC_UNCONFIRMED');self.assertFalse(self.proof()['matched']);self.assertTrue(self.proof()['operation_closed']);self.safe()
    def test_mid_finish_save_failure_preserves_partial_outcome_and_closes_actual_session(self):
        original=Path.open
        def fail(path,*args,**kwargs):
            mode=args[0] if args else kwargs.get('mode','r')
            if ('bound_finish','wa_app_runtime') in self.world.events and path.is_relative_to(self.n['OUT']) and any(c in mode for c in 'wax'):raise OSError(CANARY)
            return original(path,*args,**kwargs)
        with patch.object(Path,'open',fail),self.assertRaises(self.n['Stop']):self.invoke()
        self.assertEqual(self.proof()['outcome']['exit_code'],0);self.assertTrue(self.proof()['outcome']['acknowledgement']);self.assertTrue(self.proof()['operation_closed']);self.assertFalse(self.proof()['matched']);self.assertFalse(self.n['evidence_is_complete']());self.assertEqual(self.world.events[-1],('global_zero',));self.safe()
    def test_event_output_failure_does_not_skip_actual_global_selector_or_allow_pass(self):
        with patch('builtins.print',side_effect=BrokenPipeError(CANARY)),self.assertRaises(self.n['Stop']):self.invoke()
        self.assertEqual(self.world.events[-1],('global_zero',));self.assertTrue(self.proof()['operation_closed']);self.assertFalse(self.proof()['matched']);self.assertFalse(self.n['evidence_is_complete']());self.safe()
    def test_first_operation_stop_survives_secondary_global_failure(self):
        self.world.error='ERROR:  22012: '+CANARY+'\n';self.world.global_count=1
        with self.assertRaises(self.n['Stop']) as error:self.invoke()
        self.assertEqual(error.exception.code,'RESTORE_BOUND_OPERATION_NOT_COMMITTED');self.assertEqual(self.n['report']['primary_failure']['code'],'RESTORE_BOUND_OPERATION_NOT_COMMITTED');self.assertFalse(self.proof()['operation_closed']);self.assertFalse(self.proof()['matched']);self.safe()
    def test_actual_main_failure_persistent_io_runs_finalizer_exact3c2v_private_cleanup(self):
        n=self.n;n['OUT']=self.base/'main-evidence';n['PRIVATE']=n['OUT']/'private';n['ARCHIVE']=n['PRIVATE']/'restore01-base.tar';n['MANIFEST']['review_status']='APPROVED_LOCAL_F0_RESTORE_ATTEMPT';n['MANIFEST']['restore']={'external_files_sha256':{name:sha((T/name).read_bytes()) for name in n['EXTERNAL_FILES']}};later=Mock()
        for name in ('verify_restore_packet','preflight','ensure_image','bootstrap_all','provision_migration_tools','catalog_experiment'):n[name]=lambda:None
        def create():
            n['PRIVATE'].mkdir();n['secret_paths']=[n['PRIVATE']/'ok-bootstrap-password',n['ARCHIVE']]
            for path in n['secret_paths']:path.write_text(CANARY)
            n['bootstrap_attempted'].add(n['SOURCE'])
        n['create_resources']=create
        def experiment():self.invoke();later()
        n['restore_experiment']=experiment;self.world.error='ERROR:  42703: '+CANARY+'\n';original=Path.open
        def fail(path,*args,**kwargs):
            mode=args[0] if args else kwargs.get('mode','r')
            if ('bound_finish','wa_app_runtime') in self.world.events and path.is_relative_to(n['OUT']) and any(c in mode for c in 'wax'):raise OSError(CANARY)
            return original(path,*args,**kwargs)
        with patch.object(Path,'open',fail),redirect_stdout(io.StringIO()) as output:code=n['main']()
        self.assertEqual(code,1);later.assert_not_called();self.assertNotIn(CANARY,output.getvalue());self.assertIn(('finalizer',),self.world.events);self.assertFalse(self.world.present_c);self.assertFalse(self.world.present_v);self.assertFalse(n['PRIVATE'].exists());self.assertTrue(n['report']['cleanup_summary']['resource_absence_observation_completed']);self.assertFalse(n['evidence_is_complete']());self.assertNotEqual(n['report']['status'],'PASS_LOCAL_PHYSICAL_RESTORE_SUBSET_ONLY_FULL_CASE_NOT_RUN');self.safe()
if __name__=='__main__':unittest.main(verbosity=2)
