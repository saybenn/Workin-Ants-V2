"""Environment-free INSTALL derivation, gates and process-boundary checks."""
from contextlib import ExitStack
from copy import deepcopy
import hashlib
import io
import json
from pathlib import Path
import runpy
import socket
import subprocess
import tarfile
import tempfile
from types import SimpleNamespace
import unittest
from unittest.mock import Mock,patch
import uuid

ROOT=Path(__file__).resolve().parents[1];TASK=ROOT.parent
GEN=runpy.run_path(str(ROOT/'scripts/prepare-install-control-rehearsal-v5.py'))
P=runpy.run_path(str(ROOT/'scripts/install_control_protocol_v2.py'))
PHASE=runpy.run_path(str(ROOT/'scripts/install_failed_precleanup_activation_v5.py'))
C=runpy.run_path(str(ROOT/'scripts/sql-review/run-install-control-rehearsal-v5.py'))
TRANSPORT=runpy.run_path(str(ROOT/'scripts/install_independent_review_protocol_source_phase_v5.py'));DISK=runpy.run_path(str(ROOT/'scripts/sql-review/watch-install-independent-review-source-phase-v5.py'))
CANARY='PRIVATE_INSTALL_PASSWORD_HANDLE_AND_ERROR_CANARY'
SOURCE=(ROOT/GEN['APPLICATION']).read_bytes()
sha=lambda raw:hashlib.sha256(raw).hexdigest()

def cli(source=P['CANONICAL'],code=0,status=None,operation='deploy'):
    return {'schema':'workinants.local-f0-migrate-result.v2','operation':operation,'source_sql_sha256':source,'exit_code':code,'status':status or ('CLI_COMPLETED_REQUIRES_INDEPENDENT_LEDGER_CATALOG_CHECKS' if code==0 else 'CLI_FAILED_STOP_AND_INSPECT'),'prisma_codes':[],'sqlstates':[],'no_pending_message_observed':True}

def row(source=P['CANONICAL'],finished=True,rolled=False):
    return {'name_sha256':sha(P['MIGRATION'].encode()),'checksum_sha256':sha(source.encode()),'finished':finished,'rolled_back':rolled,'steps':1 if finished else 0,'logs_state':'NULL','immutable_sha256':'a'*64}

def logs(primary=None,secondary=False):
    registered='WA_F0_DIAG|28P01|wa_worker|wa_p0c_rehearsal|FATAL:  password authentication failed for user "wa_worker"\n'
    if primary:
        state,message=P['PRIMARY'][primary];registered+='WA_F0_DIAG|'+state+'|wa_migrator|wa_p0c_rehearsal|ERROR:  '+message+'\n'
    if secondary:registered+='WA_F0_DIAG|25P02|wa_migrator|wa_p0c_rehearsal|ERROR:  '+P['ABORTED']+'\n'
    return P['summarize_server'](registered,'')

class MemoryEvidence:
    remember_failure=C['Evidence'].remember_failure
    def __init__(self,directory=None):self.value={'targets':{},'current_stage':'ENTRY','first_failure':None,'evidence_complete':True,'persistence_failure':False};self.directory=directory;self.required_cleanup=False;self.safe_codes=PHASE['CODES'];self.safe_stages=frozenset(('ENTRY',))
    def save(self):pass
    def stage(self,value):self.value['current_stage']=value

class Tests(unittest.TestCase):
    def setUp(self):
        self.stack=ExitStack();self.addCleanup(self.stack.close)
        for method in ('run','Popen','check_call','check_output','call'):self.stack.enter_context(patch.object(subprocess,method,side_effect=AssertionError('NO_REAL_PROCESS')))
        self.stack.enter_context(patch.object(socket,'create_connection',side_effect=AssertionError('NO_NETWORK')))
        self.files,self.packet=GEN['build'](ROOT)
    def held(self,call):
        with self.assertRaises((P['Held'],PHASE['Held'],C['HeldFailure'],ValueError)) as error:call()
        self.assertNotIn(CANARY,str(error.exception))
    def coordinator(self,process=None):
        run='12345678-1234-4234-8234-123456789abc';targets={v:{'name':'wa-p0c-'+run[:8]+'-install-'+suffix,'volume':'test-data','container_id':str(i+1)*64} for i,(v,suffix) in enumerate(zip(P['VARIANTS'],('good','division','order')))}
        e=MemoryEvidence();plan={'run_id':run,'source_commit':'a'*40,'source_tree':'b'*40,'packet_sha256':'c'*64,'targets':targets}
        passwords={v:{role:format(n+1,'064x') for n,role in enumerate(P['LOGIN_ROLES'])} for v in P['VARIANTS']}
        co=C['Coordinator'](plan,self.packet,self.files,{},passwords,{'HOST':{},'API':{}},dict(P,_review_transport=TRANSPORT,_review_io=DISK,_failed_precleanup_phase=PHASE),e,process=process or Mock(side_effect=AssertionError('UNMOCKED_PROCESS')))
        return co,e
    def fixture_plan(self,directory):
        run=str(uuid.uuid4());private=directory/'private';private.mkdir();bundle=private/'install-role-passwords.json';passwords={v:{role:format(i*6+n+1,'064x') for n,role in enumerate(P['LOGIN_ROLES'])} for i,v in enumerate(P['VARIANTS'])};bundle.write_text(json.dumps(passwords))
        targets={v:{'name':'wa-p0c-'+run[:8]+'-install-'+suffix,'volume':'wa-p0c-'+run[:8]+'-install-'+suffix+'-data','container_id':str(i+1)*64} for i,(v,suffix) in enumerate(zip(P['VARIANTS'],('good','division','order')))}
        baseline=json.loads((TASK/'local-f0-lease-revoke-plan-eadc8d26/ok-migration-manifest.json').read_bytes());histories={}
        for key in (*P['VARIANTS'],'division_recovery'):
            variant='canonical' if key=='division_recovery' else key;target=targets['division_failure' if key=='division_recovery' else key];m=deepcopy(baseline);m['run_id']=run;m['target'].update(container_name=target['name'],volume_name=target['volume'],labels={'workinants.rehearsal':'p0c-local-f0','workinants.rehearsal.run':run},bootstrap_secret_host_path=str(private/(variant+'-bootstrap-password')));m['source']['integrated_sql_sha256']=self.packet['variants'][variant]['sha256'];raw=(json.dumps(m,indent=2)+'\n').encode();mp=directory/(key+'.json');mp.write_bytes(raw);seven=GEN['prepare_history'](ROOT,raw,variant);ap=directory/(key+'.tar.gz')
            with tarfile.open(ap,'w:gz') as tar:
                for name,body in seven.items():info=tarfile.TarInfo(name);info.size=len(body);tar.addfile(info,io.BytesIO(body))
            histories[key]={'manifest':{'path':str(mp),'sha256':sha(raw)},'source_archive':{'path':str(ap),'sha256':sha(ap.read_bytes())},'source_files_sha256':{p:sha(b) for p,b in seven.items()}}
        return {'schema':'workinants.install-controls-run.v1','scope':'FINITE_INSTALL_HISTORY_AND_AUTHORITY_CONTROLS','run_id':run,'source_commit':'a'*40,'source_tree':'b'*40,'packet_sha256':'c'*64,'reviewed_packet_sha256':sha(self.files['fixtures.json']),'source_modules_sha256':{p:sha((ROOT/p).read_bytes()) for p in C['MODULES']},'targets':targets,'histories':histories,'credential_bundle':str(bundle)}
    def load_plan(self,plan,alter=None):
        original=Path.read_bytes
        def bytes_(path):
            relative=path.relative_to(ROOT).as_posix() if path.is_relative_to(ROOT) else None
            if relative and relative.startswith(C['PACKET']+'/'):raw=self.files[relative[len(C['PACKET'])+1:]]
            else:raw=original(path)
            return alter(path,raw) if alter else raw
        with patch.object(Path,'read_bytes',bytes_):return C['load_inputs'](plan)
    def rehash_tools(self,plan,keys,change):
        # Recreate every dependent manifest/provenance/archive hash using the
        # unchanged real helper. The only adversarial input is the tool map.
        for key in keys:
            item=plan['histories'][key];path=Path(item['manifest']['path']);manifest=json.loads(path.read_bytes());change(manifest['tools']['files_sha256']);raw=(json.dumps(manifest,indent=2)+'\n').encode();path.write_bytes(raw)
            variant='canonical' if key=='division_recovery' else key;seven=GEN['prepare_history'](ROOT,raw,variant);archive=Path(item['source_archive']['path'])
            with tarfile.open(archive,'w:gz') as tar:
                for name,body in seven.items():entry=tarfile.TarInfo(name);entry.size=len(body);tar.addfile(entry,io.BytesIO(body))
            item['manifest']['sha256']=sha(raw);item['source_archive']['sha256']=sha(archive.read_bytes());item['source_files_sha256']={p:sha(b) for p,b in seven.items()}
    def reject_tools_before_compile(self,plan):
        with patch.dict(C['load_inputs'].__globals__,compiled=Mock(side_effect=AssertionError('NO_PROJECT_HELPER_COMPILE'))) as globals_:
            loader=globals_['compiled']
            with self.assertRaises(C['HeldFailure']) as failure:self.load_plan(plan)
            self.assertEqual(failure.exception.code,'HISTORY_TOOL_CLOSURE_NOT_SOURCE_REGISTERED');self.assertNotIn(CANARY,str(failure.exception));loader.assert_not_called()
    def test_rehashed_reduced10299_all_four_histories_reject_before_helper_compile(self):
        with tempfile.TemporaryDirectory(dir=TASK) as directory:
            plan=self.fixture_plan(Path(directory));source=json.loads((ROOT/C['TOOL_CLOSURE']).read_bytes())['tools_files_sha256'];required={'node/bin/node','schema-engine','node_modules/prisma/build/index.js','node_modules/prisma/build/cli.js','node_modules/prisma/config.js','node_modules/prisma/package.json'};removed=next(p for p in sorted(source) if p not in required)
            self.rehash_tools(plan,tuple(plan['histories']),lambda values:values.pop(removed))
            for item in plan['histories'].values():self.assertEqual(len(json.loads(Path(item['manifest']['path']).read_bytes())['tools']['files_sha256']),10299)
            self.reject_tools_before_compile(plan)
    def test_rehashed_samecount_critical_change_all_four_rejects_actual_loader(self):
        with tempfile.TemporaryDirectory(dir=TASK) as directory:
            plan=self.fixture_plan(Path(directory));self.rehash_tools(plan,tuple(plan['histories']),lambda values:values.__setitem__('schema-engine','0'*64))
            for item in plan['histories'].values():self.assertEqual(len(json.loads(Path(item['manifest']['path']).read_bytes())['tools']['files_sha256']),10300)
            self.reject_tools_before_compile(plan)
    def test_each_cross_target_samecount_discrepancy_rejects_before_helper_compile(self):
        for target in (*P['VARIANTS'],'division_recovery'):
            with self.subTest(target=target),tempfile.TemporaryDirectory(dir=TASK) as directory:
                plan=self.fixture_plan(Path(directory));before={key:deepcopy(value) for key,value in plan['histories'].items()};self.rehash_tools(plan,(target,),lambda values:values.__setitem__('schema-engine','0'*64));self.assertTrue(all(before[key]==plan['histories'][key] for key in before if key!=target));self.reject_tools_before_compile(plan)
    def test_rehashed_unknown_tool_path_canary_is_never_executed_or_echoed(self):
        with tempfile.TemporaryDirectory(dir=TASK) as directory:
            plan=self.fixture_plan(Path(directory));source=json.loads((ROOT/C['TOOL_CLOSURE']).read_bytes())['tools_files_sha256'];removed=next(p for p in sorted(source) if p not in {'node/bin/node','schema-engine','node_modules/prisma/build/index.js','node_modules/prisma/build/cli.js','node_modules/prisma/config.js','node_modules/prisma/package.json'})
            def change(values):values.pop(removed);values['node_modules/'+CANARY+'/index.js']='0'*64
            self.rehash_tools(plan,('division_recovery',),change);self.reject_tools_before_compile(plan)
    def test_explicit_source_tool_closure_dependency_cannot_be_missing_or_rebound(self):
        for change in ('missing-binding','missing-source-pin','wrong-binding'):
            with self.subTest(change=change),tempfile.TemporaryDirectory(dir=TASK) as directory:
                plan=self.fixture_plan(Path(directory));packet=deepcopy(self.packet)
                if change=='missing-binding':packet.pop('tool_closure_source')
                elif change=='missing-source-pin':packet['source_files_sha256'].pop(C['TOOL_CLOSURE'])
                else:packet['tool_closure_source']['path']=CANARY
                packet['source_only_packet_sha256']=sha(C['canonical']({k:packet[k] for k in ('source_files_sha256','prepared_files_sha256')}).encode());body=(json.dumps(packet,indent=2)+'\n').encode();plan['reviewed_packet_sha256']=sha(body)
                with patch.dict(self.files,{'fixtures.json':body}),patch.dict(C['load_inputs'].__globals__,compiled=Mock(side_effect=AssertionError('NO_PROJECT_HELPER_COMPILE'))) as globals_:
                    with self.assertRaises(C['HeldFailure']) as failure:self.load_plan(plan)
                    self.assertEqual(failure.exception.code,'PINNED_TOOL_CLOSURE_DEPENDENCY_REQUIRED');self.assertNotIn(CANARY,str(failure.exception));globals_['compiled'].assert_not_called()
    def test_tool_closure_is_explicit_cached_actual_source_dependency_and_sql_unchanged(self):
        self.assertEqual(self.packet['tool_closure_source'],{'path':C['TOOL_CLOSURE'],'sha256':C['TOOL_CLOSURE_SHA'],'file_count':10300});self.assertEqual(self.packet['source_files_sha256'][C['TOOL_CLOSURE']],C['TOOL_CLOSURE_SHA']);self.assertEqual(sha((ROOT/C['TOOL_CLOSURE']).read_bytes()),C['TOOL_CLOSURE_SHA'])
        for name,body in self.files.items():
            if name!='fixtures.json':self.assertEqual(body,(ROOT/'review-output/install-control-rehearsal'/name).read_bytes())
    def test_exact_three_immutable_derivations_preserve_every_other_byte(self):
        self.assertEqual(P['derive'](SOURCE,'canonical'),SOURCE)
        failure=P['derive'](SOURCE,'division_failure');self.assertEqual(failure.replace(b'SELECT 1/0;\n',b'',1),SOURCE);self.assertTrue(failure.endswith(b'SELECT 1/0;\nRESET ROLE;\nCOMMIT;\n'))
        moved=P['derive'](SOURCE,'late_function_grant');self.assertEqual(moved.replace(P['TRANSFER']+P['GRANT'],P['TRANSFER'],1),SOURCE.replace(P['GRANT'],b'',1));self.assertEqual(moved.count(P['GRANT']),1)
        self.held(lambda:P['derive'](SOURCE+b' ', 'canonical'))
    def test_all_three_variants_pass_unchanged_prepare_plan_offline(self):
        with tempfile.TemporaryDirectory(dir=TASK) as d:
            plan=self.fixture_plan(Path(d));self.assertEqual(len(plan['histories']),4)
            for key,item in plan['histories'].items():self.assertEqual(len(item['source_files_sha256']),7)
        self.assertEqual(sha((ROOT/'prisma/foundation/history-manifest.json').read_bytes()),'7b7d385b978f43d06ad519be34c00144ae6b3101f92ce6032dc32202353f971e')
    def test_generated_sql_parses_and_ledger_shape_guard_precedes_history(self):
        from pglast import parse_sql
        total=0
        for name,raw in self.files.items():
            if name.endswith('.sql'):total+=len(parse_sql(raw.decode()))
        self.assertGreater(total,3000);ledger=self.files['ledger-observe.sql'].decode();self.assertLess(ledger.index('LOCK TABLE ONLY'),ledger.index('FROM ONLY public._prisma_migrations'));self.assertIn('exact builtin columns required',ledger)
        self.assertIn("'relations',(SELECT count(*) FROM pg_class",self.files['inventory.sql'].decode())
    def test_source_only_inventory_and_case_strings_are_exact_not_run(self):
        self.assertEqual(self.packet['selected_control_ids'],['P0C-INSTALL-01','P0C-INSTALL-02']);self.assertEqual(self.packet['status'],'NOT_RUN');self.assertFalse(self.packet['database_contacted']);self.assertEqual(self.packet['source_assertions']['P0C-INSTALL-02']['assertions'][0]['status'],'NOT_RUN')
        second,p=GEN['build'](ROOT);self.assertEqual(second,self.files);self.assertEqual(p,self.packet)
    def test_actual_loader_prevalidates_complete_history_and_closed_helper_graph(self):
        with tempfile.TemporaryDirectory(dir=TASK) as d:
            plan=self.fixture_plan(Path(d));packet,sql,histories,passwords,ctx,protocol=self.load_plan(plan);self.assertEqual(packet,self.packet);self.assertEqual(len(histories),4);self.assertTrue(callable(ctx['HOST']['coordinate']));self.assertIn('failure_verdict',protocol)
    def test_verified_helpers_and_generator_use_cached_bytes_without_disk_fallback(self):
        with tempfile.TemporaryDirectory(dir=TASK) as d:
            plan=self.fixture_plan(Path(d));started=[False];original=C['compiled']
            def compiled(path,raw):started[0]=True;return original(path,raw)
            def alter(path,raw):
                if started[0] and path.is_relative_to(ROOT):raise AssertionError('NO_SOURCE_REOPEN_AFTER_HELPER_EXECUTION')
                return raw
            with patch.dict(C['load_inputs'].__globals__,compiled=compiled):self.load_plan(plan,alter)
    def test_drifted_throwing_helper_never_executes(self):
        with tempfile.TemporaryDirectory(dir=TASK) as d:
            plan=self.fixture_plan(Path(d))
            for path in C['MODULES']:
                def alter(p,raw,path=path):return b"raise RuntimeError('"+CANARY.encode()+b"')" if p==ROOT/path else raw
                with self.subTest(path=path):self.held(lambda:self.load_plan(plan,alter))
    def test_current_nested_manifest_hash_and_archive_bytes_cannot_be_swapped(self):
        with tempfile.TemporaryDirectory(dir=TASK) as d:
            plan=self.fixture_plan(Path(d));item=plan['histories']['division_failure'];mp=Path(item['manifest']['path']);mp.write_bytes(mp.read_bytes()+b' ');self.held(lambda:self.load_plan(plan))
    def test_even_rehashed_source_archive_rejects_unsafe_mode_owner_or_pax_metadata(self):
        with tempfile.TemporaryDirectory(dir=TASK) as d:
            plan=self.fixture_plan(Path(d));item=plan['histories']['canonical'];archive=Path(item['source_archive']['path'])
            with tarfile.open(archive) as tar:members=[(entry.name,tar.extractfile(entry).read()) for entry in tar]
            for defect in ('write','owner','pax'):
                with tarfile.open(archive,'w:gz') as tar:
                    for i,(name,body) in enumerate(members):
                        entry=tarfile.TarInfo(name);entry.size=len(body)
                        if i==0:
                            if defect=='write':entry.mode=0o666
                            if defect=='owner':entry.uid=1
                            if defect=='pax':entry.pax_headers={'comment':CANARY}
                        tar.addfile(entry,io.BytesIO(body))
                item['source_archive']['sha256']=sha(archive.read_bytes());self.held(lambda:self.load_plan(plan))
    def test_changed_manifest_is_rejected_again_immediately_before_guarded_cli(self):
        co,e=self.coordinator();co.live=Mock();co.closed=Mock();co.ctx={'HOST':{'coordinate':Mock()}};co.histories={'canonical':{'binding':{'manifest':{'path':'irrelevant','sha256':'0'*64}},'raw':b'{}','members':{}}}
        with patch.dict(C['Coordinator'].migrate.__globals__,read_bound=Mock(return_value=b'changed')):self.held(lambda:co.migrate('canonical','canonical'))
        co.ctx['HOST']['coordinate'].assert_not_called()
    def test_activation_requires_success_closed_install_and_independent_original_cleanup(self):
        gate=P['ActivationGate']();proof={'original_grantor':'postgres','temporary_memberships':0,'leaf_create':False,'other_clients':0}
        self.held(gate.permit);gate.cleaned(proof);self.held(gate.permit);gate.installed(False,True);gate.cleaned(proof);self.held(gate.permit);gate.installed(True,True);self.held(gate.permit);gate.cleaned(proof);self.assertTrue(gate.permit());gate.activated_once();self.held(gate.permit)
        for key,bad in [('temporary_memberships',False),('other_clients',0.0),('leaf_create',0),('original_grantor',CANARY)]:
            changed=dict(proof);changed[key]=bad;self.held(lambda:P['ActivationGate']().cleaned(changed))
    def test_actual_activation_dispatch_never_sends_passwords_until_gate(self):
        co,e=self.coordinator();co.execute=Mock();co.inactive=Mock();co.auth=Mock();self.held(lambda:co.activate('canonical'));co.execute.assert_not_called();co.inactive.assert_not_called()
        gate=co.gates['canonical'];gate.installed(True,True);gate.cleaned({'original_grantor':'postgres','temporary_memberships':0,'leaf_create':False,'other_clients':0});co.activate('canonical');sql=co.execute.call_args.args[2];self.assertEqual(sql.count('ALTER ROLE '),4);self.assertEqual(co.auth.call_count,4);self.assertNotIn(co.passwords['canonical']['wa_worker'],json.dumps(e.value))
    def test_inventory_zero_is_all_relations_functions_types_and_enums(self):
        zero=dict.fromkeys(('relations','functions','types','enums','other_clients'),0);P['validate_inventory'](zero,True)
        for field in zero:
            for value in (1,False,0.0,None):
                bad=dict(zero);bad[field]=value;self.held(lambda:P['validate_inventory'](bad,True))
        P['validate_inventory']({'relations':188,'functions':147,'types':142,'enums':29,'other_clients':0},False)
    def test_intended_22012_is_distinguished_from_permission_or_unrelated_error(self):
        source=self.packet['variants']['division_failure']['sha256'];failed=row(source,False);ledger={'rows':[failed],'ids_unique':True};zero=dict.fromkeys(('relations','functions','types','enums','other_clients'),0)
        value=P['failure_verdict']('division_failure',cli(source,1),zero,ledger,logs(),logs('division_failure',True),source);self.assertFalse(value['P3018_claimed']);self.assertEqual(value['primary_sqlstate'],'22012')
        self.held(lambda:P['failure_verdict']('division_failure',cli(source,1),zero,ledger,logs(),logs('late_function_grant',True),source))
        for status in ('CLI_CLOSURE_UNCONFIRMED_STOP_AND_CLEAN_EXACT_RESOURCE','CLI_COMPLETED_REQUIRES_INDEPENDENT_LEDGER_CATALOG_CHECKS'):
            self.held(lambda:P['failure_verdict']('division_failure',cli(source,1,status),zero,ledger,logs(),logs('division_failure',True),source))
    def test_masked_null_logs_require_actual_secondary_not_historical_inference(self):
        source=self.packet['variants']['division_failure']['sha256'];zero=dict.fromkeys(('relations','functions','types','enums','other_clients'),0);failed=row(source,False);ledger={'rows':[failed],'ids_unique':True}
        self.held(lambda:P['failure_verdict']('division_failure',cli(source,1),zero,ledger,logs(),logs('division_failure'),source))
        ledger['rows'][0]['logs_state']='NONEMPTY';result=P['failure_verdict']('division_failure',cli(source,1),zero,ledger,logs(),logs('division_failure'),source);self.assertEqual(result['classification'],'SERVER_PRIMARY_WITH_NONEMPTY_LOGS')
        self.held(lambda:P['failure_verdict']('division_failure',cli(source,1),zero,ledger,logs(),logs('division_failure',True),source))
    def test_server_parser_drops_unknown_bodies_names_and_handles(self):
        stream='WA_F0_DIAG|42703|wa_migrator|wa_p0c_rehearsal|ERROR:  '+CANARY+'\n';result=P['summarize_server'](stream,'');self.assertEqual(result['counts']['other_migrator_error'],1);self.assertNotIn(CANARY,json.dumps(result))
        for raw in ('\x1b'+CANARY,'\r'+CANARY,'x'*2100000):self.held(lambda:P['summarize_server'](raw,''))
        for body in ('DETAIL:  '+CANARY,'CONTEXT: '+CANARY):self.assertEqual(P['summarize_server']('WA_F0_DIAG|22012|wa_migrator|wa_p0c_rehearsal|'+body,'')['counts']['forbidden_body'],1)
    def test_original_wrong_grantor_diagnostic_is_bound_to_exact_source_raise(self):
        finalizer=self.files['finalize.sql'].decode();body=__import__('re').search(r'DO (\$cleanup\$)(.*?)\1;',finalizer,__import__('re').S)[2];line=next(i for i,s in enumerate(body.split('\n'),1) if "RAISE EXCEPTION 'cleanup requires original bootstrap grantor'" in s);error='psql:<stdin>:2: ERROR:  P0001: cleanup requires original bootstrap grantor\nCONTEXT:  PL/pgSQL function inline_code_block line '+str(line)+' at RAISE\nLOCATION:  exec_stmt_raise, pl_exec.c:3911\n'
        self.assertTrue(P['wrong_finalizer_diagnostic'](error,finalizer)['matched'])
        for bad in (error.replace('P0001','42501'),error.replace('line '+str(line),'line '+str(line+1)),error+'DETAIL: '+CANARY+'\n'):
            result=P['wrong_finalizer_diagnostic'](bad,finalizer);self.assertFalse(result['matched']);self.assertNotIn(CANARY,json.dumps(result))
    def test_success_status_stop_prevents_wrong_grantor_and_runtime_activation(self):
        co,e=self.coordinator();co.bootstrap=Mock();co.stage_history=Mock();co.activation_attempt=Mock();co.finalize=Mock();co.wrong_finalizer=Mock();co.inventory=Mock();co.activate=Mock();co.migrate=Mock(return_value=cli(code=0,status='CLI_OUTPUT_REJECTED_STOP_AND_INSPECT'))
        self.held(co.successful_install);co.finalize.assert_called_once_with('canonical');co.wrong_finalizer.assert_not_called();co.inventory.assert_not_called();co.activate.assert_not_called()
    def test_unknown_failure_keeps_bounded_observations_before_stopping(self):
        # The new precleanup boundary must classify the fresh prefix before
        # finalization; complete real process paths are in the focused checker.
        co,e=self.coordinator();v='division_failure';identity={**{k:co.plan[k]for k in ('run_id','source_commit','source_tree','packet_sha256')},'variant':v,'container_id':co.target(v)['container_id'],'source_sql_sha256':self.packet['variants'][v]['sha256']}
        value=cli(identity['source_sql_sha256'],1);value.update(run_id=identity['run_id'],container_id=identity['container_id'],attestation_sha256='a'*64,raw_output_discarded=True,database_qualification_claimed=False)
        unknown=P['summarize_server']('WA_F0_DIAG|42703|wa_migrator|wa_p0c_rehearsal|ERROR: '+CANARY,'')
        self.held(lambda:PHASE['failed_prefix'](value,logs(),unknown,identity,P));self.assertEqual(unknown['counts']['other_migrator_error'],1);self.assertNotIn(CANARY,json.dumps(unknown))
    def test_genuine_failure_source_state_and_wrong_error_never_issue_recovery(self):
        co,e=self.coordinator();v='division_failure';identity={**{k:co.plan[k]for k in ('run_id','source_commit','source_tree','packet_sha256')},'variant':v,'container_id':co.target(v)['container_id'],'source_sql_sha256':self.packet['variants'][v]['sha256']}
        value=cli(identity['source_sql_sha256'],1);value.update(run_id=identity['run_id'],container_id=identity['container_id'],attestation_sha256='a'*64,raw_output_discarded=True,database_qualification_claimed=False)
        prefix=PHASE['failed_prefix'](value,logs(),logs(v,True),identity,P);self.assertEqual(prefix['intended_primary_sqlstate'],'22012');self.assertEqual(prefix['diagnostic_delta']['registered'],2)
    def test_stage_sends_the_same_verified_archive_bytes_not_a_reread_file_path(self):
        co,e=self.coordinator(process=Mock(return_value=SimpleNamespace(returncode=0,stdout=b'',stderr=b'')));co.live=Mock();co.closed=Mock();co.histories={'canonical':{'archive':b'VALIDATED_ARCHIVE','binding':{'source_archive':{'path':'not-used-by-process','sha256':'0'*64}}}}
        with patch.dict(C['Coordinator'].stage_history.__globals__,read_bound=Mock(return_value=b'VALIDATED_ARCHIVE')):co.stage_history('canonical')
        self.assertEqual(co.process.call_args.kwargs['input'],b'VALIDATED_ARCHIVE');self.assertNotIn('not-used-by-process',co.process.call_args.args[0]);self.assertFalse(co.process.call_args.kwargs.get('text',False));self.assertIn(co.target('canonical')['container_id'],co.process.call_args.args[0])
    def test_recovery_orders_review_resolve_exact_rearm_canonical_retry_cleanup_and_noop(self):
        co,e=self.coordinator();v='division_failure';source=self.packet['variants'][v]['sha256'];failed=row(source,False);co.rows[v]=failed;events=[]
        co.review=lambda variant,verdict:(events.append('independent-review') or {'reviewed':True})
        def migrate(variant,key,operation='deploy',proof=None):events.append((operation,key));return cli(source if key==v else P['CANONICAL'],operation=operation)
        co.migrate=migrate;co.ledger=Mock(side_effect=[{'rows':[dict(failed,rolled_back=True)],'ids_unique':True},{'rows':[dict(failed,rolled_back=True),row()],'ids_unique':True},{'rows':[dict(failed,rolled_back=True),row()],'ids_unique':True}]);co.inventory=Mock();co.execute=lambda *args:events.append('exact-rearm');co.authority=Mock();co.stage_history=lambda key:events.append(('stage',key));co.finalize=lambda variant:events.append('original-finalize');co.activate=lambda variant:events.append('activate');co.good_schema={'sha256':'d'*64};co.schema_fingerprint=Mock(return_value=co.good_schema);co.recovery({})
        self.assertEqual(events,['independent-review',('resolve-rolled-back',v),'exact-rearm',('stage','division_recovery'),('deploy','division_recovery'),'original-finalize','activate',('deploy','division_recovery')])
    def test_review_hold_requires_actual_recorded_inventory_before_publication(self):
        co,e=self.coordinator();co.rows['division_failure']=row(self.packet['variants']['division_failure']['sha256'],False)
        with self.assertRaises(KeyError):co.review('division_failure',{'primary_sqlstate':'22012'})
    def test_standard_resolve_retains_failed_row_and_canonical_retry_does_not_rewrite_it(self):
        failed=row(self.packet['variants']['division_failure']['sha256'],False);resolved={'rows':[dict(failed,rolled_back=True)],'ids_unique':True};P['resolved_ledger'](resolved,failed);recovered={'rows':[dict(failed,rolled_back=True),row()],'ids_unique':True};P['applied_ledger'](recovered,failed)
        for key in failed:
            changed=deepcopy(recovered);changed['rows'][0][key]=False if key in ('finished','rolled_back') else 1 if key=='steps' else '0'*64
            if changed!=recovered:self.held(lambda:P['applied_ledger'](changed,failed))
        self.held(lambda:P['applied_ledger']({'rows':[row()],'ids_unique':True},failed))
    def test_independent_actual_review_binds_proof_run_cid_source_and_reviewer(self):
        identity={'run_id':'test-run','container_id':'1'*64,'source_sql_sha256':'2'*64};proof={'actual_zero_objects':True};approval={'schema':'workinants.install-independent-rollback-review.v1','decision':'APPROVED_STANDARD_RESOLVE_ROLLED_BACK',**identity,'proof_sha256':sha((P['canonical'](proof)+'\n').encode()),'reviewer':'/root/restricted_controls_operator'};self.assertTrue(P['require_recovery_review'](proof,approval,identity))
        for key in approval:
            changed=dict(approval);changed[key]=CANARY;self.held(lambda:P['require_recovery_review'](proof,changed,identity))
    def test_closed_observer_is_global_and_retains_typed_false_proof_on_error(self):
        for result in (SimpleNamespace(returncode=0,stdout='1\n',stderr=''),SimpleNamespace(returncode=False,stdout='0\n',stderr=''),SimpleNamespace(returncode=0,stdout='0\n',stderr=CANARY),RuntimeError(CANARY)):
            co,e=self.coordinator();co.psql=Mock(side_effect=result if isinstance(result,Exception) else None,return_value=result)
            with self.assertRaises(Exception):co.closed('canonical','TEST')
            proof=e.value['targets']['canonical']['closure_TEST'];self.assertFalse(proof['all_other_clients_absent']);self.assertNotIn(CANARY,json.dumps(e.value))
        co,e=self.coordinator();co.psql=Mock(return_value=SimpleNamespace(returncode=0,stdout='0\n',stderr=''));co.closed('canonical','TEST');self.assertNotIn('datname=',co.psql.call_args.args[2]);self.assertNotIn('usename=',co.psql.call_args.args[2])
    def test_return_and_throw_always_attempt_closure_before_sql_verdict(self):
        for fail in (False,True):
            co,e=self.coordinator();calls=[]
            def call(*args):calls.append('psql');raise RuntimeError(CANARY)
            co.psql=call if fail else Mock(return_value=SimpleNamespace(returncode=3,stdout='',stderr=CANARY));co.closed=lambda *args:calls.append('closed')
            with self.assertRaises(Exception):co.execute('canonical','postgres','SELECT 1;','NEGATIVE')
            self.assertEqual(calls[-1],'closed');self.assertNotIn(CANARY,json.dumps(e.value))
    def test_passwords_and_URL_never_appear_in_process_arguments(self):
        co,e=self.coordinator(process=Mock(return_value=SimpleNamespace(returncode=0,stdout='',stderr='')));co.psql('canonical','wa_migrator','SELECT 1;');args=co.process.call_args.args[0];self.assertTrue(any('PGPASSFILE=' in a for a in args));self.assertFalse(any('PGPASSWORD' in a or 'postgresql://' in a for a in args));self.assertIn(co.target('canonical')['container_id'],args)
    def test_pipeline_stops_subsequent_protocols_and_finalizes_all_attempted_targets(self):
        co,e=self.coordinator();calls=[]
        def first():co.bootstrap_attempted.update(('canonical','division_failure'));raise RuntimeError(CANARY)
        co.successful_install=first;co.failure=Mock();co.recovery=Mock();co.finalize=lambda v:calls.append(('finalize',v));co.closed=lambda v,label:calls.append(('closed',v))
        with self.assertRaises(C['HeldFailure']):co.run()
        co.failure.assert_not_called();co.recovery.assert_not_called();self.assertEqual(len(calls),4)
    def test_finalizer_or_closure_failure_cannot_leave_a_pass_status(self):
        co,e=self.coordinator();co.bootstrap_attempted.update(P['VARIANTS']);co.successful_install=Mock();co.failure=Mock(return_value={});co.recovery=Mock();co.finalize=Mock(side_effect=RuntimeError(CANARY));co.closed=Mock(side_effect=RuntimeError(CANARY));self.held(co.run);self.assertEqual(co.finalize.call_count,3);self.assertEqual(co.closed.call_count,3);self.assertNotIn(CANARY,json.dumps(e.value))
    def test_finalization_evidence_io_failure_never_skips_other_target_closure(self):
        co,e=self.coordinator();co.bootstrap_attempted.update(P['VARIANTS']);co.successful_install=Mock();co.failure=Mock(return_value={});co.recovery=Mock();co.finalize=Mock(side_effect=RuntimeError(CANARY));co.record=Mock(side_effect=OSError(CANARY));co.closed=Mock();e.save=Mock(side_effect=OSError(CANARY));self.held(co.run);self.assertEqual(co.finalize.call_count,3);self.assertEqual(co.closed.call_count,3)
    def test_schema_noop_checks_real_dump_bytes_and_discards_raw_bodies(self):
        co,e=self.coordinator();co.closed=Mock();co.docker=Mock(return_value=SimpleNamespace(returncode=0,stderr='',stdout='\\restrict ABC123\nCREATE TABLE '+CANARY+'();\n\\unrestrict ABC123\n'));value=co.schema_fingerprint('canonical');self.assertEqual(value['sha256'],sha(('CREATE TABLE '+CANARY+'();\n').encode()));self.assertNotIn(CANARY,json.dumps(e.value));self.assertTrue(co.closed.called)
    def test_import_help_does_not_execute_helpers_or_processes(self):
        for path in ('scripts/prepare-install-control-rehearsal-v5.py','scripts/install_control_protocol_v2.py',C['SELF']):runpy.run_path(str(ROOT/path))
        with self.assertRaises(SystemExit) as exit_:
            with patch('sys.stdout',io.StringIO()):C['main'](['--help'])
        self.assertEqual(exit_.exception.code,0)

if __name__=='__main__':unittest.main(verbosity=2)
