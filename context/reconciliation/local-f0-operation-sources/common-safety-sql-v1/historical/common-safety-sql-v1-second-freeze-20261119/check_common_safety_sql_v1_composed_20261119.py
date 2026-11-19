"""Command-only composed safety SQL tests; no runtime/process/network allowed."""
import ast,copy,hashlib,io,json,runpy,socket,subprocess,tempfile,types,unittest
from pathlib import Path
from contextlib import redirect_stdout
from unittest.mock import patch
TASK=Path(__file__).resolve().parent;ROOT=TASK/'workinants-correction-pass';PRESERVED=TASK/'safety-sql-before-author-20261119';PRES=json.loads((PRESERVED/'preservation-manifest.json').read_bytes());HELPER=TASK/'common_safety_sql_v1_helpers.py.txt';ELIGIBILITY=TASK/'common_safety_sql_v1_install_eligibility.py.txt';CANARY='PRIVATE_SAFETY_IO_SQL_AND_OUTPUT_CANARY_NEVER_EXPORT'
class Raw:
    def __init__(self,value):self.value=value
class World:
    def __init__(self,n):self.n=n;self.trace=[];self.responses={};self.finalizer_code=0;self.fail_selector=None;self.present_c=set(n['created_containers']);self.present_v=set(n['created_volumes']);self.raw_finalizer=(ROOT/'review-output/foundation-bootstrap-finalize.review.sql').read_text();self.labels={'workinants.rehearsal':n['LABEL'],'workinants.rehearsal.run':n['RUN_ID']}
    def result(self,code=0,stdout='',stderr=''):return types.SimpleNamespace(returncode=code,stdout=stdout,stderr=stderr)
    def command(self,args,input=None,timeout=60):
        n=self.n
        if 'psql' in args:
            selector=next(k for k,v in n['_SAFETY_SQL_LABELS'].items() if v==n['report']['stage']) if n['report']['stage'] in n['_SAFETY_SQL_LABELS'].values() else 'NORMAL'
            self.trace.append({'selector':selector,'args':list(args),'sql_sha256':hashlib.sha256(input.encode()).hexdigest(),'timeout':timeout});self.assert_transport(args)
            if self.fail_selector==selector:raise n['Stop']('FIRST_FIXED_COMMAND_STOP')
            if selector=='ORIGINAL_GRANTOR_FINALIZATION':
                assert input==self.raw_finalizer
                return self.result(self.finalizer_code,'',CANARY if self.finalizer_code else '')
            if selector!='NORMAL':assert input==n['_SAFETY_SQL_RECIPES'][selector]
            value=self.responses.get(selector)
            if value is None:
                if selector in ('GLOBAL_BACKENDS','FINALIZATION_BACKENDS','NORMAL'):value={'migrator':0,'other_client_backends':0}
                elif selector=='FINALIZATION_RESULT':value={'grantor':'postgres','auth':'scram-sha-256:postgres','remaining_memberships':0,'leaf_create':dict.fromkeys(n['LEAVES'],False),'active_install_connections':0}
                elif selector=='INSTALL_BOOTSTRAP_ELIGIBILITY':value={'source_roles':4,'login':'postgres','auth':'scram-sha-256:postgres'}
                elif selector=='INSTALL_ORIGINAL_CLEANUP_RESULT':value={'temporary_memberships':0,'leaf_create':False,'auth':'scram-sha-256:postgres','grantor':'postgres'}
                else:raise AssertionError('UNEXPECTED_MOCK_SELECTOR')
            if isinstance(value,BaseException):raise value
            if callable(value):return value()
            return self.result(stdout=value.value if isinstance(value,Raw) else json.dumps(value))
        assert args[:3]==['docker','--context','desktop-linux'];command=args[3:];self.trace.append({'docker':list(command)})
        if command[:3]==['container','ls','-a']:return self.result(stdout='\n'.join(sorted(self.present_c|{'unrelated-container'})))
        if command[:2]==['volume','ls']:return self.result(stdout='\n'.join(sorted(self.present_v|{'unrelated-volume'})))
        if command[:2]==['container','inspect']:
            name=command[-1];return self.result(stdout=json.dumps([{'Name':'/'+name,'Id':n['created_containers'][name],'Config':{'Labels':self.labels}}]))
        if command[:2]==['volume','inspect']:
            name=command[-1];return self.result(stdout=json.dumps([{'Name':name,'Labels':self.labels,'CreatedAt':n['created_volumes'][name]}]))
        if command[:3]==['container','rm','-f']:
            name=next(k for k,v in n['created_containers'].items() if v==command[-1]);self.present_c.remove(name);return self.result()
        if command[:2]==['volume','rm']:self.present_v.remove(command[-1]);return self.result()
        raise AssertionError('UNEXPECTED_PROCESS_BOUNDARY')
    def assert_transport(self,args):
        assert args[args.index('-U')+1]=='postgres' and args[args.index('-h')+1]=='127.0.0.1' and args[args.index('-p')+1]=='5432'
        assert args[args.index('-d')+1]==self.n['DB'] and 'PGPASSFILE=/run/wa-secrets/pgpass' in args
        assert any(cid in args for cid in self.n['created_containers'].values())

class SafetySQLTests(unittest.TestCase):
    def setUp(self):
        for key in ('run','Popen','call','check_call','check_output'):
            guard=patch.object(subprocess,key,side_effect=AssertionError('UNMOCKED_PROCESS'));guard.start();self.addCleanup(guard.stop)
        guard=patch.object(socket,'create_connection',side_effect=AssertionError('NETWORK_FORBIDDEN'));guard.start();self.addCleanup(guard.stop)
    def fixture(self,family='install',out_exists=True):
        names=PRES['families_sha256'][family];core=next(name for name in names if name.startswith('execute_'));steps=next(name for name in names if name.startswith('local_f0_'))
        if family=='native':
            # The frozen native script has literal argv initialization at top
            # level. Load its exact real function/class/import nodes instead;
            # mock no safety, SQL, observer, finalizer or cleanup function.
            tree=ast.parse((PRESERVED/core).read_bytes());nodes=[x for x in tree.body if isinstance(x,(ast.Import,ast.ImportFrom,ast.FunctionDef,ast.ClassDef))];n={'__file__':str(PRESERVED/core),'__name__':'_offline_native_safety'};exec(compile(ast.Module(body=nodes,type_ignores=[]),str(PRESERVED/core),'exec'),n)
        else:n=runpy.run_path(str(PRESERVED/core))['launch'].__globals__
        exec(compile((PRESERVED/steps).read_bytes(),str(PRESERVED/steps),'exec'),n);normal={key:ast.dump(next(x for x in ast.parse((PRESERVED/core).read_bytes()).body if isinstance(x,ast.FunctionDef) and x.name==key),include_attributes=False) for key in ('sql','observe')};original_finalize=n['finalize'];original_closed=n['closed_backends']
        temporary=tempfile.TemporaryDirectory(prefix='offline-safety-composed-',dir=TASK);self.addCleanup(temporary.cleanup);base=Path(temporary.name);root=base/'source';path=root/'review-output/foundation-bootstrap-finalize.review.sql';path.parent.mkdir(parents=True);path.write_bytes((ROOT/'review-output/foundation-bootstrap-finalize.review.sql').read_bytes());out=base/'evidence'
        if out_exists:out.mkdir()
        targets=('first','second','third');volumes=tuple(name+'-data' for name in targets);n.update(ROOT=root,TASK=TASK,OUT=out,PRIVATE=out/'private',RUN_ID='550e8400-e29b-41d4-a716-446655440000',LABEL='p0c-local-f0',CONNECTION_TAG='wa-safety-offline',DB='wa_p0c_rehearsal',ROLES=('postgres','wa_migrator','wa_context_issuer','wa_identity_service_authority','wa_app_runtime','wa_worker'),LEAVES=('wa_private_helper_owner','wa_customer_verifier','wa_track_verifier'),RESOURCE_CONTAINERS=targets,RESOURCE_VOLUMES=volumes,TARGETS=[{'name':name,'volume':name+'-data','kind':'ok'} for name in targets],created_containers={name:format(i+1,'064x') for i,name in enumerate(targets)},created_volumes={name:'FIXED_CREATED_AT' for name in volumes},attempted_containers=set(targets),attempted_volumes=set(volumes),bootstrap_attempted=set(targets),finalization_attempted=set(),finalized=set(),all_secrets=[],secret_paths=[],EVIDENCE_FAILED=False,INSTALL={})
        n['report']={'stage':'ENTRY','status':'IN_PROGRESS','evidence_complete':True,'persistence_failure':False,'targets':{name:{'finalization':'NOT_RUN'} for name in targets},'events':[],'unexpected':[],'steps':{},'cleanup':{},'restore':{},'install':{},'source_verification':{'files_sha256':{'review-output/foundation-bootstrap-finalize.review.sql':hashlib.sha256(path.read_bytes()).hexdigest()}}}
        approval={'lease':'APPROVED_LOCAL_F0_LEASE_REVOKE_ATTEMPT','restore':'APPROVED_LOCAL_F0_RESTORE_ATTEMPT','native':'APPROVED_LOCAL_F0_NATIVE_ACCESS_ATTEMPT','owner':'APPROVED_LOCAL_F0_OWNER_READ_ATTEMPT','install':'APPROVED_LOCAL_F0_INSTALL_OWNED_ATTEMPT'}[family]
        n['MANIFEST']={'review_status':approval,'packet_files_sha256':{'review-output/foundation-bootstrap-finalize.review.sql':hashlib.sha256(path.read_bytes()).hexdigest()},'operator_sources_sha256':{core:hashlib.sha256((PRESERVED/core).read_bytes()).hexdigest()},'restore':{'external_files_sha256':{core:hashlib.sha256((PRESERVED/core).read_bytes()).hexdigest()}}}
        n['OPERATOR_FILES']=(core,);helper=HELPER.read_text().replace("_SAFETY_SQL_PROFILE='STANDARD'","_SAFETY_SQL_PROFILE="+repr('INSTALL' if family=='install' else 'STANDARD')).replace("_SAFETY_IO_PROFILE='COMMON'","_SAFETY_IO_PROFILE="+repr('OWNER' if family=='owner' else 'COMMON'));exec(compile(helper,str(HELPER),'exec'),n)
        if family=='install':exec(compile(ELIGIBILITY.read_bytes(),str(ELIGIBILITY),'exec'),n)
        world=World(n);n['command']=world.command
        return n,world,path,normal,original_finalize,original_closed
    def writes_fail(self,n,world,mode='all'):
        original=Path.open
        def open_(path,*args,**kwargs):
            kind=args[0] if args else kwargs.get('mode','r')
            if path.is_relative_to(n['OUT']) and any(flag in kind for flag in 'wax') and (mode=='all' or mode=='pre' and not world.trace or mode=='post' and bool(world.trace)):raise OSError(CANARY)
            return original(path,*args,**kwargs)
        guard=patch.object(Path,'open',open_);guard.start();self.addCleanup(guard.stop)
    def selectors(self,world):return [x['selector'] for x in world.trace if 'selector' in x]
    def safe(self,n):self.assertNotIn(CANARY,json.dumps(n['report']));self.assertTrue(all(x.get('exit_code') is None or type(x['exit_code']) is int for x in n['report']['events'] if 'exit_code' in x))
    def test_real_finalizers_all_five_profiles_execute_pre_revoke_post_under_persistent_io(self):
        for family in ('lease','restore','native','owner','install'):
            n,w,p,*_=self.fixture(family);self.writes_fail(n,w)
            with redirect_stdout(io.StringIO()):
                for name in n['RESOURCE_CONTAINERS']:
                    with self.assertRaises(n['Stop']) as stopped:n['finalize'](name)
                    self.assertEqual(stopped.exception.code,'REQUIRED_SAFETY_EVIDENCE_UNCONFIRMED')
            self.assertEqual(self.selectors(w),['FINALIZATION_BACKENDS','ORIGINAL_GRANTOR_FINALIZATION','FINALIZATION_RESULT']*3);self.assertEqual(n['finalized'],set(n['RESOURCE_CONTAINERS']));self.assertFalse(n['_required_safety_evidence_complete']());self.assertTrue(all(x['finalization']=='OBSERVED_CLEANUP_EVIDENCE_INCOMPLETE' for x in n['report']['targets'].values()));self.safe(n)
    def test_pre_post_write_and_event_failure_each_preserve_actual_safety_order(self):
        for mode in ('pre','post','event'):
            n,w,p,*_=self.fixture('lease')
            if mode=='event':
                guard=patch('builtins.print',side_effect=BrokenPipeError(CANARY));guard.start();self.addCleanup(guard.stop)
            else:self.writes_fail(n,w,mode)
            with self.assertRaises(n['Stop']),redirect_stdout(io.StringIO()):n['finalize']('first')
            self.assertEqual(self.selectors(w),['FINALIZATION_BACKENDS','ORIGINAL_GRANTOR_FINALIZATION','FINALIZATION_RESULT']);self.assertFalse(n['_required_safety_evidence_complete']());self.safe(n)
    def test_global_closure_real_sql_still_runs_then_public_barrier_blocks_normal_continuation(self):
        n,w,p,*_=self.fixture();self.writes_fail(n,w)
        with self.assertRaises(n['Stop']),redirect_stdout(io.StringIO()):
            n['closed_backends']('first','AFTER_OPERATION');n['observe']('first','SELECT 1;','LATER_NORMAL')
        self.assertEqual(self.selectors(w),['GLOBAL_BACKENDS']);self.assertTrue(n['report']['backend_closures'][-1]['all_other_client_backends_absent']);self.assertFalse(n['_required_safety_evidence_complete']());self.safe(n)
    def test_normal_sql_and_observe_are_unchanged_and_still_stop_before_command(self):
        n,w,p,*_=self.fixture();self.writes_fail(n,w)
        with self.assertRaises(OSError):n['observe']('first',n['_SAFETY_SQL_RECIPES']['GLOBAL_BACKENDS'],'NORMAL_QUERY')
        self.assertEqual(w.trace,[]);self.assertFalse(n['_required_safety_evidence_complete']());self.safe(n)
    def test_invalid_or_active_precondition_never_dispatches_original_finalizer(self):
        values=[{'migrator':1,'other_client_backends':0},{'migrator':0,'other_client_backends':1},{'migrator':False,'other_client_backends':0},{'migrator':0.0,'other_client_backends':0},{'migrator':None,'other_client_backends':0},{'migrator':0},{'migrator':0,'other_client_backends':0,'extra':CANARY},[],None,Raw(CANARY),Raw('{"migrator":0,"migrator":0,"other_client_backends":0}'),Raw('{"migrator":NaN,"other_client_backends":0}')]
        for value in values:
            n,w,p,*_=self.fixture();w.responses['FINALIZATION_BACKENDS']=Raw('null') if value is None else value
            with self.assertRaises(n['Stop']),redirect_stdout(io.StringIO()):n['finalize']('first')
            self.assertEqual(self.selectors(w),['FINALIZATION_BACKENDS']);self.assertNotIn('first',n['finalized']);self.safe(n)
    def test_nonzero_unknown_or_malformed_command_response_blocks_revoke(self):
        for result in ((2,'{}',CANARY),(False,'{}',''),(0.0,'{}',''),(None,'{}',''),(0,None,''),(0,{},''),(0,'{}',None),(0,'{}',CANARY)):
            n,w,p,*_=self.fixture();w.responses['FINALIZATION_BACKENDS']=lambda result=result:w.result(*result)
            with self.assertRaises(n['Stop']),redirect_stdout(io.StringIO()):n['finalize']('first')
            self.assertEqual(self.selectors(w),['FINALIZATION_BACKENDS']);self.safe(n)
    def test_missing_drifted_unadmitted_or_symlink_source_blocks_finalizer_and_still_observes_post(self):
        for kind in ('missing','drift','unadmitted','symlink'):
            n,w,p,*_=self.fixture()
            if kind=='missing':p.unlink()
            elif kind=='drift':p.write_text(CANARY)
            elif kind=='unadmitted':n['MANIFEST']['packet_files_sha256']={}
            original=Path.is_symlink
            def symlink(path):return True if kind=='symlink' and path==p else original(path)
            with patch.object(Path,'is_symlink',symlink),self.assertRaises(n['Stop']) as error,redirect_stdout(io.StringIO()):n['finalize']('first')
            self.assertEqual(error.exception.code,'REQUIRED_FINALIZER_SOURCE_UNCONFIRMED');self.assertEqual(self.selectors(w),['FINALIZATION_BACKENDS','FINALIZATION_RESULT']);self.assertNotIn('first',n['finalized']);self.safe(n)
    def test_source_recipe_preservation_and_foreign_profile_target_selector_are_closed(self):
        n,w,p,*_=self.fixture('lease');origins=json.loads((TASK/'common_safety_sql_v1_recipe_origins_20261119.json').read_bytes())
        for selector,value in n['_SAFETY_SQL_RECIPES'].items():self.assertEqual(hashlib.sha256(value.encode()).hexdigest(),origins['selector_sql_sha256'][selector])
        for selector,target in [('INSTALL_BOOTSTRAP_ELIGIBILITY','first'),('UNKNOWN_SQL','first'),('FINALIZATION_BACKENDS','foreign')]:
            with self.assertRaises(n['Stop']):n['_required_safety_sql'](target,selector)
        self.assertEqual(w.trace,[])
    def test_real_install_eligibility_all_three_targets_can_finalize_despite_io(self):
        n,w,p,*_=self.fixture();self.writes_fail(n,w)
        with redirect_stdout(io.StringIO()):
            for name in n['RESOURCE_CONTAINERS']:
                with self.assertRaises(n['Stop']):n['ensure_original_cleanup'](name)
        self.assertEqual(self.selectors(w),['INSTALL_BOOTSTRAP_ELIGIBILITY','GLOBAL_BACKENDS','FINALIZATION_BACKENDS','ORIGINAL_GRANTOR_FINALIZATION','FINALIZATION_RESULT']*3);self.assertEqual(n['finalized'],set(n['RESOURCE_CONTAINERS']));self.safe(n)
    def test_absent_mixed_foreign_role_eligibility_never_revokes(self):
        for value in ({'source_roles':0,'login':'postgres','auth':'scram-sha-256:postgres'},{'source_roles':2,'login':'postgres','auth':'scram-sha-256:postgres'},{'source_roles':False,'login':'postgres','auth':'scram-sha-256:postgres'},{'source_roles':4,'login':CANARY,'auth':'scram-sha-256:postgres'}):
            n,w,p,*_=self.fixture();self.writes_fail(n,w);w.responses['INSTALL_BOOTSTRAP_ELIGIBILITY']=value
            with self.assertRaises(n['Stop']),redirect_stdout(io.StringIO()):n['ensure_original_cleanup']('first')
            self.assertEqual(self.selectors(w),['INSTALL_BOOTSTRAP_ELIGIBILITY']);self.assertNotIn('first',n['finalized']);self.safe(n)
    def test_independent_child_cleanup_observation_uses_no_duplicate_revoke_under_io(self):
        n,w,p,*_=self.fixture();self.writes_fail(n,w);n['INSTALL']['qualified_result']={}
        with self.assertRaises(n['Stop']),redirect_stdout(io.StringIO()):n['ensure_original_cleanup']('first')
        self.assertEqual(self.selectors(w),['INSTALL_BOOTSTRAP_ELIGIBILITY','GLOBAL_BACKENDS','INSTALL_ORIGINAL_CLEANUP_RESULT']);self.assertIn('first',n['finalized']);self.safe(n)
    def test_first_command_stop_survives_post_observer_stop(self):
        n,w,p,*_=self.fixture();w.fail_selector='ORIGINAL_GRANTOR_FINALIZATION';w.responses['FINALIZATION_RESULT']=Raw(CANARY)
        with self.assertRaises(n['Stop']) as error,redirect_stdout(io.StringIO()):n['finalize']('first')
        self.assertEqual(error.exception.code,'FIRST_FIXED_COMMAND_STOP');self.assertEqual(self.selectors(w),['FINALIZATION_BACKENDS','ORIGINAL_GRANTOR_FINALIZATION','FINALIZATION_RESULT']);self.assertNotIn('first',n['finalized']);self.safe(n)
    def test_original_operation_stop_survives_nested_closure_persistence_error(self):
        n,w,p,*_=self.fixture();self.writes_fail(n,w)
        with self.assertRaises(n['Stop']) as error,redirect_stdout(io.StringIO()):
            with n['_RequiredSafetyBoundary']('CLOSE','first','OPERATION_FINALLY'):
                n['report']['stage']='ORIGINAL_OPERATION';raise n['Stop']('ORIGINAL_OPERATION_STOP')
            n['observe']('first','SELECT 1;','LATER_NORMAL')
        self.assertEqual(error.exception.code,'ORIGINAL_OPERATION_STOP');self.assertEqual(error.exception.stage,'ORIGINAL_OPERATION');self.assertEqual(self.selectors(w),['GLOBAL_BACKENDS']);n['record_failure'](error.exception.stage,error.exception.code,primary=True);self.assertEqual(n['report']['primary_failure'],{'stage':'ORIGINAL_OPERATION','code':'ORIGINAL_OPERATION_STOP'});self.safe(n)
    def test_actual_owning_mains_only_command_mock_still_finalize_and_remove_all_owned_resources(self):
        for family in ('lease','restore','native','owner','install'):
            n,w,p,*_=self.fixture(family,out_exists=False);self.writes_fail(n,w)
            with redirect_stdout(io.StringIO()):result=n['main']()
            self.assertEqual(result,1);self.assertFalse(n['_required_safety_evidence_complete']());self.assertFalse(w.present_c);self.assertFalse(w.present_v);self.assertEqual(self.selectors(w).count('ORIGINAL_GRANTOR_FINALIZATION'),3);self.assertFalse(any(n['report']['cleanup_summary']['resource_presence_after'].values()));self.assertEqual(n['report']['primary_failure']['code'],'EVIDENCE_WRITE_UNCONFIRMED');self.safe(n)
    def test_old_real_composition_is_detected_without_stubbing_sql_observe_or_finalizer(self):
        n,w,p,normal,old_finalizer,old_closure=self.fixture();self.writes_fail(n,w)
        with self.assertRaises(OSError):old_finalizer('first')
        self.assertEqual(w.trace,[])
        n['finalization_attempted'].clear()
        with self.assertRaises(n['Stop']):old_closure('first','OLD_CLOSURE')
        self.assertEqual(w.trace,[])
    def test_clean_success_all_profiles_and_no_io_error_permits_normal_continuation(self):
        for family in ('lease','restore','native','owner','install'):
            n,w,p,*_=self.fixture(family)
            with redirect_stdout(io.StringIO()):n['finalize']('first');n['closed_backends']('first','AFTER_SAFETY');n['observe']('first',n['_SAFETY_SQL_RECIPES']['GLOBAL_BACKENDS'],'NORMAL_QUERY')
            self.assertEqual(self.selectors(w),['FINALIZATION_BACKENDS','ORIGINAL_GRANTOR_FINALIZATION','FINALIZATION_RESULT','GLOBAL_BACKENDS','NORMAL']);self.assertTrue(n['_required_safety_evidence_complete']());self.assertEqual(n['report']['targets']['first']['finalization'],'PASS');self.safe(n)
    def test_timeout_and_command_stop_preserve_first_failure_and_never_qualify_cleanup(self):
        for selector in ('FINALIZATION_BACKENDS','ORIGINAL_GRANTOR_FINALIZATION'):
            n,w,p,*_=self.fixture()
            if selector=='ORIGINAL_GRANTOR_FINALIZATION':
                original=w.command
                def command(args,input=None,timeout=60):
                    if input==w.raw_finalizer:
                        w.trace.append({'selector':selector});raise subprocess.TimeoutExpired(CANARY,timeout,output=CANARY,stderr=CANARY)
                    return original(args,input,timeout)
                n['command']=command
            else:w.responses[selector]=subprocess.TimeoutExpired(CANARY,120,output=CANARY,stderr=CANARY)
            with self.assertRaises(subprocess.TimeoutExpired),redirect_stdout(io.StringIO()):n['finalize']('first')
            self.assertNotIn('first',n['finalized']);self.safe(n)
    def test_post_observer_strict_identity_shape_and_authority_never_get_promoted(self):
        changes=[{'grantor':CANARY},{'auth':CANARY},{'remaining_memberships':False},{'active_install_connections':0.0},{'leaf_create':{'wa_private_helper_owner':False}},{'remaining_memberships':1}]
        for change in changes:
            n,w,p,*_=self.fixture();value={'grantor':'postgres','auth':'scram-sha-256:postgres','remaining_memberships':0,'leaf_create':dict.fromkeys(n['LEAVES'],False),'active_install_connections':0};value.update(change);w.responses['FINALIZATION_RESULT']=value
            with self.assertRaises(n['Stop']),redirect_stdout(io.StringIO()):n['finalize']('first')
            self.assertEqual(self.selectors(w),['FINALIZATION_BACKENDS','ORIGINAL_GRANTOR_FINALIZATION','FINALIZATION_RESULT']);self.assertNotIn('first',n['finalized']);self.safe(n)
    def test_owner_original_stop_is_preserved_before_its_distinct_failure_bookkeeping(self):
        n,w,p,*_=self.fixture('owner');self.writes_fail(n,w)
        with self.assertRaises(n['Stop']) as stopped,redirect_stdout(io.StringIO()):
            with n['_RequiredSafetyBoundary']('FINALIZE','first'):
                n['report']['stage']='FIRST_OPERATION';raise n['Stop']('FIRST_OPERATION_STOP')
        self.assertEqual(stopped.exception.code,'FIRST_OPERATION_STOP');self.assertEqual(n['report']['primary_failure'],{'stage':'FIRST_OPERATION','code':'FIRST_OPERATION_STOP'});self.assertEqual(self.selectors(w),['FINALIZATION_BACKENDS','ORIGINAL_GRANTOR_FINALIZATION','FINALIZATION_RESULT']);self.safe(n)
    def test_existing_original_primary_survives_later_finalizer_and_post_failures_all_profiles(self):
        for family in ('lease','restore','native','owner','install'):
            for post in ('clean','malformed'):
                n,w,p,*_=self.fixture(family);n['_required_safety_failure']('ORIGINAL_OPERATION','ORIGINAL_OPERATION_STOP',primary=True);first=copy.deepcopy(n['report']['primary_failure']);w.fail_selector='ORIGINAL_GRANTOR_FINALIZATION'
                if post=='malformed':w.responses['FINALIZATION_RESULT']=Raw(CANARY)
                with self.assertRaises(n['Stop']) as error,redirect_stdout(io.StringIO()):n['finalize']('first')
                self.assertEqual(error.exception.code,'FIRST_FIXED_COMMAND_STOP');self.assertEqual(n['report']['primary_failure'],first);self.assertTrue(any(x.get('code')=='FIRST_FIXED_COMMAND_STOP' for x in n['report']['unexpected']));self.assertEqual(self.selectors(w),['FINALIZATION_BACKENDS','ORIGINAL_GRANTOR_FINALIZATION','FINALIZATION_RESULT']);self.assertNotIn('first',n['finalized']);self.safe(n)
    def test_ordinary_finalizer_exit3_retains_clean_or_dirty_safe_poststate_as_unqualified_all_profiles(self):
        for family in ('lease','restore','native','owner','install'):
            for dirty in (False,True):
                n,w,p,*_=self.fixture(family);n['_required_safety_failure']('ORIGINAL_OPERATION','ORIGINAL_OPERATION_STOP',primary=True);first=copy.deepcopy(n['report']['primary_failure']);w.finalizer_code=3;state={'grantor':'postgres','auth':'scram-sha-256:postgres','remaining_memberships':3 if dirty else 0,'leaf_create':dict.fromkeys(n['LEAVES'],dirty),'active_install_connections':0};w.responses['FINALIZATION_RESULT']=state
                with self.assertRaises(n['Stop']) as error,redirect_stdout(io.StringIO()):n['finalize']('first')
                self.assertEqual(error.exception.code,'REQUIRED_SAFETY_COMMAND_UNCONFIRMED');self.assertEqual(n['report']['primary_failure'],first);self.assertEqual(n['report']['targets']['first']['finalization_observation'],state);self.assertEqual(n['report']['targets']['first']['finalization_observation_status'],'OBSERVED_NOT_QUALIFIED');self.assertEqual(n['report']['targets']['first']['finalization'],'UNCONFIRMED');self.assertNotIn('first',n['finalized']);self.safe(n)
    def test_source_failure_retains_only_validated_post_and_preserves_recorded_primary_all_profiles(self):
        for family in ('lease','restore','native','owner','install'):
            for malformed in (False,True):
                n,w,p,*_=self.fixture(family);n['_required_safety_failure']('ORIGINAL_OPERATION','ORIGINAL_OPERATION_STOP',primary=True);first=copy.deepcopy(n['report']['primary_failure']);p.unlink()
                if malformed:w.responses['FINALIZATION_RESULT']={'grantor':CANARY}
                with self.assertRaises(n['Stop']) as error,redirect_stdout(io.StringIO()):n['finalize']('first')
                self.assertEqual(error.exception.code,'REQUIRED_FINALIZER_SOURCE_UNCONFIRMED');self.assertEqual(n['report']['primary_failure'],first);row=n['report']['targets']['first']
                if malformed:self.assertNotIn('finalization_observation',row)
                else:self.assertEqual(row['finalization_observation_status'],'OBSERVED_NOT_QUALIFIED')
                self.assertEqual(row['finalization'],'UNCONFIRMED');self.assertNotIn('first',n['finalized']);self.safe(n)
    def test_existing_primary_survives_nested_closure_failure_all_profiles(self):
        for family in ('lease','restore','native','owner','install'):
            n,w,p,*_=self.fixture(family);n['_required_safety_failure']('ORIGINAL_OPERATION','ORIGINAL_OPERATION_STOP',primary=True);first=copy.deepcopy(n['report']['primary_failure']);w.responses['GLOBAL_BACKENDS']=Raw(CANARY)
            with self.assertRaises(n['Stop']) as error,redirect_stdout(io.StringIO()):
                with n['_RequiredSafetyBoundary']('CLOSE','first','NESTED_CLOSURE'):raise n['Stop']('LATER_FIXED_OPERATION_STOP')
            self.assertEqual(error.exception.code,'LATER_FIXED_OPERATION_STOP');self.assertEqual(n['report']['primary_failure'],first);self.assertEqual(self.selectors(w),['GLOBAL_BACKENDS']);self.safe(n)
    def test_all_frozen30_and_install_extra2_stay_exact(self):
        for names in PRES['families_sha256'].values():
            for name,digest in names.items():self.assertEqual(hashlib.sha256((TASK/name).read_bytes()).hexdigest(),digest)
        for name in ('workinants-correction-pass/scripts/sql-review/install_ledger_proof_v2.py','workinants-correction-pass/scripts/sql-review/test_install_ledger_proof_v2.py'):self.assertEqual(hashlib.sha256((TASK/name).read_bytes()).hexdigest(),PRES['files_sha256'][name])
if __name__=='__main__':unittest.main(verbosity=2)
