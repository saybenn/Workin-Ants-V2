"""Pure held three-target INSTALL preparation; never execute subprocesses or SQL."""
import argparse,ast,copy,gzip,hashlib,io,json,tarfile,uuid
from pathlib import Path
from types import ModuleType
from contextlib import redirect_stdout,redirect_stderr
TASK=Path(__file__).resolve().parent;ROOT=TASK/'workinants-correction-pass'
FILES=('execute_local_f0_install_controls_20261120_source_phase_v5.py','local_f0_install_controls_operation_steps_source_phase_v5.py','prepare_local_f0_install_controls_plan_source_phase_v5.py','check_local_f0_install_controls_operation_source_phase_v5.py','pin_local_f0_install_controls_plan_20261120_source_phase_v5.py')
GEN='scripts/prepare-install-control-rehearsal-v5.py';FIXTURES='review-output/install-control-rehearsal-v5/fixtures.json';FIXTURES_SHA='3992a73c920a510f18ee903e15d74f98c42720266eb4ff26abd61478e6c398e5';CONTENT='2240b048ed002e304829b5985e7402219647df7e0c7aedf4235aa5087ef44542'
LEDGER='scripts/sql-review/install_ledger_proof_v3.py';LEDGER_TEST='scripts/sql-review/test_install_ledger_proof_v3.py'
CLOSURE='context/reconciliation/local-f0-tooling/prisma-tools-closure.json';CLOSURE_SHA='610e36e4006e9680d0e6a036486f302a18ecce9593699125b4173f5914acb88b'
MODULES={'scripts/sql-review/run-install-control-rehearsal-v5.py': '2216187773803e940961b745585e553ee85d4b2a3bc874baa36367b78524c90c', 'scripts/install_control_protocol_v2.py': '6c1474dc12a603b07346fff014c8ab8bd15dec5be0b972ec1d504342115ba48f', 'scripts/prepare-install-control-rehearsal-v5.py': '99fc6b2b779f1f747362964a507875e864ad9372cda12de72453da44f6eeb1d7', 'scripts/sql-review/run-context-control-rehearsal.py': '5ec53d01d7c5b19bea0a584ef9f5b4e6742d9509c21ac7e2250b9bdd62511f33', 'scripts/sql-review/run-first-rehearsal.py': '279b8384c7847ec5e2411013dc5def4b0cdd155de4bff75586a29a156f87bf6e', 'scripts/sql-review/run-local-f0-migrate.py': '4b929dd8c46fea0fa0e09f92cf54e8bb37db194a9ce5c6fd02c0e91542d7909f', 'scripts/sql-review/rehearsal-diagnostics.py': 'c595883eb8013defc967feb0fc94db1366227ce89b843eeea2235b5a3adbeb7e', 'scripts/prepare-local-f0-history.py': '33fe46e1b50c8d808ffb95b60cc42750e795582e6a1b15fb82f4fe93321281f8', 'scripts/sql-review/collect_native_catalog.sql': '9313c892ae3e5ade97167aa1818ed4b371d04b835ac736be7c13c3206bc85b3f', 'scripts/install_independent_review_protocol_source_phase_v5.py': '973ebe07aa52152fee99cded1b0add6d93c753f2818078592f890aeff305ff38', 'scripts/sql-review/watch-install-independent-review-source-phase-v5.py': '5fb09251e7bf7d70b8935f5bfb93dc7413bdb98c5cc864bce976bb57fa62db3a', 'scripts/install_failed_precleanup_activation_v5.py': '4d3235b174fb184509e993ed2548f89ba62805f01947ade613f884df31451018'}
EXTRA=('review-output/install-control-rehearsal-v3/division_failure/20261117000100_f0_local_initial/migration.sql','scripts/sql-review/test_run_install_control_rehearsal_v5.py','scripts/sql-review/prisma_ledger_proof.py','scripts/sql-review/collect_prisma_ledger.sql',LEDGER,LEDGER_TEST,'scripts/sql-review/local_image_identity.py','scripts/sql-review/test_local_image_identity.py','scripts/sql-review/fixtures/postgres-17.11-approved-manifest.json','scripts/check-install-control-rehearsal-v5.py','scripts/sql-review/install-controls-coordinator-v5.md','scripts/install_independent_review_protocol_source_phase_v5.py','scripts/test_install_independent_review_protocol_source_phase_v5.py','scripts/sql-review/watch-install-independent-review-source-phase-v5.py','scripts/sql-review/test_watch_install_independent_review_source_phase_v5.py')
SQL='prisma/foundation/migrations/20261117000100_f0_local_initial/migration.sql';RUNTIME=('prisma.local-f0.config.mjs','scripts/sql-review/local-f0-migrate-guard.mjs','scripts/sql-review/local-f0-migrate-runner.mjs')
TOOL_DATA=('node_modules/@prisma/engines-version/package.json','node_modules/prisma/package.json')
class Held(ValueError):pass
def need(ok,code):
    if not ok:raise Held(code)
def sha(raw):return hashlib.sha256(raw).hexdigest()
def encoded(v):return (json.dumps(v,sort_keys=True,indent=2,ensure_ascii=False,allow_nan=False)+'\n').encode()
def aggregate(files):return sha(''.join(p+'\0'+h+'\n' for p,h in sorted(files.items())).encode())
def cached(root,name,pin):
    raw=(root/name).read_bytes();need(sha(raw)==pin,'SOURCE_INPUT_CHANGED');return raw

def tar_bytes(files):
    stream=io.BytesIO()
    with gzip.GzipFile(fileobj=stream,mode='wb',mtime=0) as zipped:
        with tarfile.open(fileobj=zipped,mode='w') as archive:
            for name,raw in sorted(files.items()):
                entry=tarfile.TarInfo(name);entry.size=len(raw);entry.mode=0o644;entry.uid=entry.gid=0;entry.mtime=0;archive.addfile(entry,io.BytesIO(raw))
    return stream.getvalue()

def prepare(root,task,baseline,run_id=None):
    root=Path(root).resolve();task=Path(task).resolve();run_id=run_id or str(uuid.uuid4());need(str(uuid.UUID(run_id))==run_id and uuid.UUID(run_id).version==4,'RUN_UUID')
    directory=task/('local-f0-install-controls-plan-'+run_id[:8]);out=task/('local-f0-install-controls-20261119-'+run_id[:8]);need(not directory.exists() and not out.exists(),'FRESH_PREPARATION_DIRECTORIES')
    raw=cached(root,FIXTURES,FIXTURES_SHA);packet=json.loads(raw);need(packet['source_only_packet_sha256']==CONTENT and packet['status']=='NOT_RUN','REVIEWED_SOURCE_ONLY_PACKET')
    blobs={name:cached(root,name,pin) for name,pin in packet['source_files_sha256'].items()}
    for name,pin in MODULES.items():need(name in blobs and sha(blobs[name])==pin,'PINNED_CLOSED_RUNTIME_MODULES')
    need(CLOSURE in blobs and sha(blobs[CLOSURE])==CLOSURE_SHA,'PINNED_TOOL_CLOSURE');closure=json.loads(blobs[CLOSURE]);need(type(closure['file_count']) is int and closure['file_count']==len(closure['tools_files_sha256'])==10300,'PINNED_TOOL_COUNT')
    old=baseline['migration_targets']['ok'];nested_raw=Path(old['manifest_path']).read_bytes();need(sha(nested_raw)==old['manifest_sha256'],'BASELINE_NESTED_MANIFEST_CHANGED');base=json.loads(nested_raw)
    need(base['tools']['files_sha256']==closure['tools_files_sha256'],'EXACT10300_TOOLS_BEFORE_HELPER_COMPILE')
    tools_raw={name:(root/name).read_bytes() for name in TOOL_DATA};need(all(sha(body)==closure['tools_files_sha256'][name] for name,body in tools_raw.items()),'PINNED_TOOL_DATA')
    # Every source input and every four-history tooling basis is cached before
    # the first project helper can execute. The same source bytes feed build.
    for name in EXTRA:
        if name not in blobs:blobs[name]=(root/name).read_bytes()
    prepared={name:cached(root,'review-output/install-control-rehearsal-v5/'+name,pin) for name,pin in packet['prepared_files_sha256'].items()}
    generator=ModuleType('_reviewed_install_generator');generator.__file__=str(root/GEN);output=io.StringIO()
    with redirect_stdout(output),redirect_stderr(output):exec(compile(blobs[GEN],generator.__file__,'exec'),generator.__dict__);reproduced,repacket=generator.build(root,{name:blobs[name] for name in packet['source_files_sha256']})
    need(not output.getvalue() and repacket==packet and all(reproduced[n]==b for n,b in prepared.items()),'INSTALL_SOURCE_REPRODUCTION')
    master=copy.deepcopy(baseline);master.update(purpose='LOCAL_F0_INSTALL_CONTROLS_REHEARSAL',authority='STANDING_LOCAL_F0_INSTALL_SOURCE_ONLY',run_id=run_id,source_commit='TO_BE_PINNED',source_tree='TO_BE_PINNED',packet_sha256='TO_BE_PINNED',evidence_directory=str(out),review_status='PENDING_OPERATIONAL_REVIEW',status='SOURCE_PREPARED_NOT_RUN')
    suffix={'canonical':'good','division_failure':'division','late_function_grant':'order'};targets=[{'name':'wa-p0c-'+run_id[:8]+'-install-'+suffix[k],'volume':'wa-p0c-'+run_id[:8]+'-install-'+suffix[k]+'-data','kind':k} for k in suffix];master['targets']=targets;by={t['kind']:t for t in targets};files={};histories={};initial={}
    for key in ('canonical','division_failure','late_function_grant','division_recovery'):
        variant='canonical' if key=='division_recovery' else key;kind='division_failure' if key=='division_recovery' else key;target=by[kind];nested=copy.deepcopy(base);nested['run_id']=run_id;nested['target'].update(container_name=target['name'],volume_name=target['volume'],labels={'workinants.rehearsal':master['run_label'],'workinants.rehearsal.run':run_id},bootstrap_secret_host_path=str(out/'private'/(kind+'-bootstrap-password')));nested['source']['integrated_sql_sha256']=packet['variants'][variant]['sha256'];nested['source']['runtime_files_sha256']={name:sha(blobs[name]) for name in RUNTIME};manifest=encoded(nested)
        with redirect_stdout(output),redirect_stderr(output):snapshot=generator.prepare_history(root,manifest,variant,{name:blobs[name] for name in packet['source_files_sha256']})
        need(not output.getvalue() and len(snapshot)==7,'EXACT_FRESH_SEVEN_SOURCE_FILES');smap={p:sha(b) for p,b in snapshot.items()};archive=tar_bytes(snapshot);name=key+'-migration-manifest.json';tarname='source-'+key+'.tar.gz';snapname='source-'+key
        files[name]=manifest;files[tarname]=archive
        for p,b in snapshot.items():files[snapname+'/'+p]=b
        histories[key]={'manifest':{'path':str(directory/name),'sha256':sha(manifest)},'source_archive':{'path':str(directory/tarname),'sha256':sha(archive)},'source_files_sha256':smap}
        if key!='division_recovery':initial[key]={'manifest_path':str(directory/name),'manifest_sha256':sha(manifest),'source_snapshot':str(directory/snapname),'source_archive':str(directory/tarname),'source_archive_sha256':sha(archive),'source_files_sha256':smap}
    master['migration_targets']=initial;master['install']={'fixtures':FIXTURES,'fixtures_sha256':FIXTURES_SHA,'content_sha256':CONTENT,'histories':histories,'history_snapshots':{key:str(directory/('source-'+key)) for key in histories},'credential_bundle':str(out/'private/install-role-passwords.json'),'ledger_adapter':LEDGER,'scope':'FINITE_THREE_TARGET_INSTALL_ONLY','recovered_history_expectation':[{'path':'prisma/foundation/migrations/20261117000100_f0_local_initial/migration.sql','migration_name':'20261117000100_f0_local_initial','sha256':packet['variants']['canonical']['sha256'],'state':'applied','count':1},{'path':'review-output/install-control-rehearsal-v3/'+packet['variants']['division_failure']['path'],'migration_name':'20261117000100_f0_local_initial','sha256':packet['variants']['division_failure']['sha256'],'state':'rolled_back','count':1}]}
    master['install']['independent_review_transport']={'schema':'workinants.install-independent-review-ready.v1','ready':'independent-review-ready.json','proof':'rollback-proof-for-review.json','snapshot':'independent-review-child-snapshot.json','identity':'independent-review-outer-identity.json','plan':'install-coordinator-run-plan.json','approval':'independent-recovery-approval.json','timeout_seconds':240,'source_modules_sha256':{n:sha(blobs[n]) for n in ('scripts/install_independent_review_protocol_source_phase_v5.py','scripts/sql-review/watch-install-independent-review-source-phase-v5.py','scripts/install_control_protocol_v2.py','scripts/install_failed_precleanup_activation_v5.py')}}
    inventory=set(baseline['packet_files_sha256'])|set(blobs)|{FIXTURES}|{'review-output/install-control-rehearsal-v5/'+name for name in prepared}
    master['packet_files_sha256']={name:sha((root/name).read_bytes()) for name in sorted(inventory)};master['prepared_source_files_aggregate_sha256']=aggregate(master['packet_files_sha256']);master['prepared_source_file_inventory_sha256']=master['packet_files_sha256'].copy();master['catalog']['tool_source_files_sha256']={p:sha(b) for p,b in tools_raw.items()}
    master['operator_sources_sha256']={name:sha((task/name).read_bytes()) for name in FILES};master['wrapper_sha256']=master['operator_sources_sha256'][FILES[0]];master['steps_sha256']=master['operator_sources_sha256'][FILES[1]]
    master['cleanup']={'containers':[t['name'] for t in targets],'volumes':[t['volume'] for t in targets],'exact_owned_id_labels_createdat_only':True,'image_removed':False,'private_files':'four_exact_owner_only_host_files_and_owned_container_tmpfs'};master['source_history_rule']='Four immutable fresh seven-file histories: canonical5ae, deliberate division22012, late existing functionGRANT42501, and canonical5ae recovery on the same division target. Root old migration/history remain unchanged.';master['allowed_catalog_operations']=['Fixed reviewed INSTALL V5 coordinator with exact failed/precleanup activation phase on3 Root-owned targets; all runtime credentials inactive until closed verified install+original-grantor cleanup.','One independent actual240s rollback proof review before standard resolve and same-target canonical retry/noop.','Full source-derived native,416expression oracle and complete private-ledger schema/ACL/history checks on canonical and recovered division; retained failed row is mandatory.','Exact owned finalization, global backend closure, source preservation and cleanup; no permission repair or automatic retry.'];master['execution_hold']='Source commit/tree/full packet/external snapshots and independent source+literal review required. No permission repair or automatic recovery approval.'
    need(all(sha((root/p).read_bytes())==sha(b) for p,b in blobs.items()),'SOURCE_CHANGED_DURING_PREPARATION')
    return directory,master,files

def main(argv=None):
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--prepare',action='store_true');parser.add_argument('--baseline-manifest',type=Path);parser.add_argument('--baseline-sha256');args=parser.parse_args(argv)
    if not args.prepare or not args.baseline_manifest or not args.baseline_sha256:return 1
    raw=args.baseline_manifest.read_bytes();need(sha(raw)==args.baseline_sha256,'EXACT_BASELINE_BYTES');directory,master,files=prepare(ROOT,TASK,json.loads(raw));directory.mkdir(exist_ok=False)
    for name,body in files.items():p=directory/name;p.parent.mkdir(parents=True,exist_ok=True);p.open('xb').write(body)
    path=directory/'operation-manifest.json';path.open('xb').write(encoded(master));print(json.dumps({'status':'HELD_SOURCE_ONLY_NOT_RUN','manifest':str(path),'sha256':sha(path.read_bytes())}));return 0
if __name__=='__main__':raise SystemExit(main())
