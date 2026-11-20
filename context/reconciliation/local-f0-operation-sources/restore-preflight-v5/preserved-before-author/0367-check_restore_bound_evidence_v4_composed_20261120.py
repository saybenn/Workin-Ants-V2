"""Real source/entry/Session/comparator composition; external processes mocked.

The model deliberately stops at the first unexercised physical-backup boundary.
It supplies no installation, native-PASS or production factory replacement.
"""
from pathlib import Path
from contextlib import redirect_stdout
from copy import deepcopy
from types import SimpleNamespace
from unittest.mock import patch
import hashlib,io,json,runpy,shutil,socket,subprocess,tempfile,unittest
T=Path(__file__).resolve().parent;R=T/'workinants-correction-pass'
N=('execute_local_f0_restore_20261119_bound_evidence_v4.py','local_f0_restore_operation_steps_bound_evidence_v4.py','prepare_local_f0_restore_plan_bound_evidence_v4.py','check_local_f0_restore_operation_bound_evidence_v4.py','pin_local_f0_restore_plan_20261119_bound_evidence_v4.py')
V='context/reconciliation/local-f0-restore-bound-evidence-v4-source-validation.json'
A='context/reconciliation/local-f0-operation-sources/restore-bound-evidence-v4'
sha=lambda raw:hashlib.sha256(raw).hexdigest()
APP_CHECKS=T/'check_local_f0_app_write_two_owned_resource_v1_operation.py'
assert sha(APP_CHECKS.read_bytes())=='31fd7030921eb8ea43b59839968a88a0f76282152dacdbaacf73ba9df513c549'
APP=runpy.run_path(str(APP_CHECKS))
FOCUS=runpy.run_path(str(T/'check_restore_bound_evidence_v4_focused_20261120.py'))

class Fixture:
    def __init__(self):
        self.temp=tempfile.TemporaryDirectory(prefix='restore-v4-real-entry-',dir=T);self.base=Path(self.temp.name);self.task=self.base/'mirror';self.root=self.task/'workinants-correction-pass';self.root.mkdir(parents=True)
        baseline=T/'local-f0-catalog-v4-plan-8fa680ed/operation-manifest.json';prep=runpy.run_path(str(T/N[2]));made=prep['prepare'](baseline,sha(baseline.read_bytes()));first=Path(made['operation_manifest']);master=json.loads(first.read_bytes())
        current=dict(master['prepared_source_file_inventory_sha256']);validation=json.loads((R/V).read_bytes());current[V]=sha((R/V).read_bytes());current.update(validation['archive_files_sha256']);current.update(master['catalog']['tool_source_files_sha256'])
        for name,wanted in current.items():
            raw=(R/name).read_bytes();assert sha(raw)==wanted;dest=self.root/name;dest.parent.mkdir(parents=True,exist_ok=True);dest.write_bytes(raw)
        for name in N:(self.task/name).write_bytes((T/name).read_bytes())
        # Sole review boundary: a private synthetic approval, never live gates.
        peer=A+'/reviews/offline-bound-review.json';raw=b'{"decision":"SOURCE_APPROVED","scope":"OFFLINE_MOCK_SOURCE_GATE_ONLY"}\n';(self.root/peer).write_bytes(raw)
        validation['independent_bound_evidence_review']={'decision':'SOURCE_APPROVED','path':peer,'sha256':sha(raw),'exact_five_sha256':validation['all_five_sources_sha256']}
        validation['archive_files_sha256']={p.relative_to(self.root).as_posix():sha(p.read_bytes()) for p in (self.root/A).rglob('*') if p.is_file()};validation['archive_files_aggregate_sha256']=APP['aggregate'](validation['archive_files_sha256']);(self.root/V).write_text(json.dumps(validation,indent=2)+'\n',encoding='utf8',newline='\n')
        base=json.loads(baseline.read_bytes());tool=self.task/'tools.tar.gz';shutil.copyfile(base['tool_archive'],tool);base['tool_archive']=str(tool);private=self.task/'baseline.json';private.write_text(json.dumps(base,indent=2)+'\n',encoding='utf8',newline='\n')
        prep=runpy.run_path(str(self.task/N[2]));self.prep=prep;self.prepared=prep['prepare'](private,sha(private.read_bytes()));self.path=Path(self.prepared['operation_manifest']);pin=runpy.run_path(str(self.task/N[4]))
        with patch.object(subprocess,'run',side_effect=self.git):pin['pin'](self.path)
        value=json.loads(self.path.read_bytes());value['review_status']='APPROVED_LOCAL_F0_RESTORE_ATTEMPT';self.path.write_text(json.dumps(value,indent=2)+'\n',encoding='utf8',newline='\n');self.manifest=value
        # The first pure live preparation remains PENDING; remove only these
        # exact test-created source files via its owned TemporaryDirectory.
        self.live_prepared=first.parent
    def close(self):
        # These ten exact pure-preparation files are test-created. Resolve and
        # check the absolute parent before any removal, and never use rmtree.
        parent=self.live_prepared.resolve();assert parent.parent==T.resolve() and parent.name.startswith('local-f0-restore-plan-')
        for path in sorted(parent.rglob('*'),key=lambda p:len(p.parts),reverse=True):
            assert path.resolve().is_relative_to(parent)
            if path.is_file():path.unlink()
            else:path.rmdir()
        parent.rmdir();assert self.base.resolve().parent==T.resolve();self.temp.cleanup()
    def git(self,args,**options):
        assert args[0]=='git';out=b''
        if args[-1]=='HEAD':out=b'a'*40+b'\n'
        elif args[-1]=='HEAD^{tree}':out=b'b'*40+b'\n'
        elif 'show' in args:out=(self.root/args[-1].split(':',1)[1]).read_bytes()
        else:raise AssertionError('UNMODELED_READONLY_GIT')
        return SimpleNamespace(returncode=0,stdout=out.decode() if options.get('text') else out,stderr='' if options.get('text') else b'')

class Model(APP['ProcessModel']):
    def __init__(self,fixture,path):
        self.fixture=fixture;self.path=path;self.manifest=json.loads(path.read_bytes());self.n=None;self.calls=[];self.containers={};self.volumes={};self.running=False;self.finalized=False;self.deploys=0;self.fail_stage=None;self.bad_global=None;self.after_started=False;self.outer_after_component=False;self.mutate_cleanup_reference=False;self.cleanup_reference_mutated=False;self.world=None;self.physical_boundary=False
        self.vm=SimpleNamespace(models=[],coordinator=None,disabled=set())
        # Immutable 980a artifacts are explicit OFFLINE MOCK process responses;
        # actual catalog/expression/ledger comparators produce every verdict.
        assets=fixture.root/A/'reviews/offline-mock-980a'
        inventory=(assets/'preserved-actual-inventory.json').read_bytes();assert sha(inventory)=='7895ae62eded54c08a515f8653d11ac52986ca469251037294a256e298c94b05';retained=json.loads(inventory)['assets_sha256']
        self.catalog={}
        for name in ('native-before','ledger-observation','oracle-preflight','oracle-results','oracle-closure','acl-preflight','text-preflight'):
            path=assets/(name+'.json');relative='context/reconciliation/local-f0-run-assets/c820e39-restore-980a38cb/evidence/'+name+'.json';raw=path.read_bytes();assert sha(raw)==retained[relative];self.catalog[name]=json.loads(raw)
        self.image='docker.io/library/postgres:17.11@sha256:996e9dc583ba9f0265a2c75547a9c95fb22c251e394749cab205a0a00e1856a1';self.md=self.image.split('@')[1];self.cd='sha256:eb0fb2377534e65aad04f37838956b3dfb888e1a3dd3c1acf957bc6557eb6c7d';self.name=self.manifest['targets'][0]['name'];self.volume=self.manifest['targets'][0]['volume'];self.labels={'workinants.rehearsal':'p0c-local-f0','workinants.rehearsal.run':self.manifest['run_id']};self.target=json.loads(Path(self.manifest['migration_targets']['ok']['manifest_path']).read_bytes())
    def popen(self,args,**options):
        if self.world is None:
            self.world=FOCUS['World'](self.n);self.world.present_c=set(self.containers);self.world.present_v=set(self.volumes)
        return self.world.popen(args,**options)
    def recipe(self,name):
        raw=(self.fixture.root/'review-output/restore-control-rehearsal'/name).read_bytes()
        assert sha(raw)==FOCUS['PROPOSAL']['prepared_files_sha256'][name]
        return raw.decode('utf8')
    def _process(self,args,**options):
        text=options.get('input') or ''
        if args[:3]==['docker','--context','desktop-linux'] and 'sh' in args:
            script=args[-1]
            if 'WA_RESTORE_SECRET_TMPFS_V2_OK' in script:return self.response('WA_RESTORE_SECRET_TMPFS_V2_OK\n')
            if script=='id -u postgres; id -g postgres':return self.response('999\n999\n')
        return super()._process(args,**options)
    def sql(self,args,text,options):
        active=sum(p.poll() is None for p in self.world.processes) if self.world else 0
        if "'migrator'" in text and "'other_client_backends'" in text:return self.response({'migrator':0,'other_client_backends':active})
        if text.startswith('SELECT count(*) FROM pg_stat_activity WHERE pid='):
            assert self.world is not None;return self.world.run(args,input=text,**{k:v for k,v in options.items() if k!='input'})
        if text=="SELECT jsonb_build_object('session_user',session_user,'current_user',current_user,'database',current_database(),'system_user',system_user);":
            role=args[args.index('-U')+1];passfile=next(x.split('=',1)[1] for x in args if x.startswith('PGPASSFILE='))
            if passfile.endswith('wrong.pgpass'):
                return self.response('',2,'psql: error: connection to server at "127.0.0.1", port 5432 failed: FATAL:  password authentication failed for user "'+role+'"\npassword retrieved from file "'+passfile+'"\n')
            return self.response({'session_user':role,'current_user':role,'database':'wa_p0c_rehearsal','system_user':'scram-sha-256:'+role})
        if "'exact_fields'" in text:
            assert self.world is not None;return self.world.run(args,input=text,**{k:v for k,v in options.items() if k!='input'})
        if text==self.recipe('all-data-fingerprint.sql'):
            assert self.world is None or not self.world.source_customer_committed
            return self.response({name:{'count':0,'rows_sha256':sha(('OFFLINE_EMPTY_'+name).encode())} for name in FOCUS['PROPOSAL']['tables']})
        if text==self.recipe('fixture-trigger-restore-observe.sql'):return self.response(FOCUS['PROPOSAL']['fixture_trigger_contract']['observer_expected'])
        for entry in FOCUS['PROPOSAL']['mandatory_fixture_observers']:
            if text==self.recipe(entry['file']):
                assert self.world and self.world.source_customer_committed and self.world.source_schedule_committed,'OBSERVER_BEFORE_REAL_RECIPE_COMMITS'
                return self.response(entry['expected'])
        identity=FOCUS['PROPOSAL']['identity_simulation']['observers'][0]
        if text==self.recipe(identity['sql']):return self.response(identity['expected'])
        if text=='SELECT pg_conf_load_time()::text;':
            assert self.world and self.world.source_customer_committed and self.world.source_schedule_committed
            self.physical_boundary=True;raise OSError('OFFLINE_MOCK_INTENTIONAL_UNEXERCISED_PHYSICAL_BOUNDARY')
        return super().sql(args,text,options)

class RealEntryCompositionTests(unittest.TestCase):
    def setUp(self):
        for name in ('run','Popen','call','check_call','check_output'):
            guard=patch.object(subprocess,name,side_effect=AssertionError('UNMODELED_PROCESS_FORBIDDEN'));guard.start();self.addCleanup(guard.stop)
        for object,name in ((socket,'create_connection'),(socket.socket,'connect')):
            guard=patch.object(object,name,side_effect=AssertionError('NETWORK_FORBIDDEN'));guard.start();self.addCleanup(guard.stop)
    def test_actual_prepare_pin_launch_native_comparators_Sessions_and_cleanup(self):
        fixture=Fixture();self.addCleanup(fixture.close);module=runpy.run_path(str(fixture.task/N[0]));model=Model(fixture,fixture.path);model.n=module['launch'].__globals__
        with patch.object(subprocess,'run',side_effect=model.process),patch.object(subprocess,'Popen',side_effect=model.popen),redirect_stdout(io.StringIO()) as output:
            code=module['launch'](['--execute-reviewed-restore','--manifest',str(fixture.path)])
        n=model.n;self.assertEqual(code,1);self.assertTrue(model.physical_boundary);self.assertEqual(model.deploys,1);self.assertEqual(n['report']['steps']['RESTORE-SOURCE'],'PASS_SYNTHETIC_SQL_SUBSET_ONLY');self.assertEqual(len(n['report']['restore']['bound_operations']),4)
        for proof in n['report']['restore']['bound_operations']:self.assertTrue(proof['matched']);self.assertTrue(proof['operation_closed']);self.assertTrue(proof['outcome']['stderr_empty']);self.assertEqual(proof['transaction_envelope']['emitted_commit_count'],1)
        comparison=json.loads((n['OUT']/'catalog-comparison.json').read_bytes());self.assertEqual(comparison['status'],'PASS');self.assertEqual(sum(comparison['check_counts'].values()),29089);self.assertEqual(comparison['findings'],[])
        self.assertEqual(n['report']['ledger_comparison']['status'],'PASS');self.assertEqual(len(n['report']['ledger_comparison']['checks']),22)
        self.assertEqual(len(json.loads((n['OUT']/'oracle-evidence.json').read_bytes())['results']['expressions']),416)
        self.assertFalse(model.containers);self.assertFalse(model.volumes);self.assertFalse(n['PRIVATE'].exists());self.assertTrue(n['report']['all_source_and_external_inputs_preserved_after_run']);self.assertNotEqual(n['report']['status'],'PASS_LOCAL_PHYSICAL_RESTORE_SUBSET_ONLY_FULL_CASE_NOT_RUN')
        safe=json.dumps(n['report']);self.assertNotIn(FOCUS['CANARY'],safe)
        for secret in n['all_secrets']:self.assertNotIn(secret,safe)
        self.assertTrue(all(p.poll() is not None for p in model.world.processes));self.assertFalse(any(x[0]=='extra_commit_warning' for x in model.world.events));self.assertNotIn('OFFLINE_MOCK_INTENTIONAL',safe)

if __name__=='__main__':unittest.main(verbosity=2)
