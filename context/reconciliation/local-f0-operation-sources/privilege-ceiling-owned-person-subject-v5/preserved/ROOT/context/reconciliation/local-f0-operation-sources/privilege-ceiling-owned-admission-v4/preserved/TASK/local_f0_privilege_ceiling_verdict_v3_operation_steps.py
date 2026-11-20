import runpy
import tarfile

def validate_archive(path,expected):
    seen=set()
    with tarfile.open(path,'r:gz') as archive:
        for member in archive:
            need(member.isfile() and not member.name.startswith('/') and all(p not in ('','.','..') for p in member.name.split('/')) and member.name not in seen,'UNSAFE_ARCHIVE_MEMBER')
            need(member.name in expected,'UNLISTED_ARCHIVE_MEMBER')
            need(hashlib.sha256(archive.extractfile(member).read()).hexdigest()==expected[member.name],'ARCHIVE_MEMBER_HASH_DRIFT')
            seen.add(member.name)
    need(seen==set(expected),'ARCHIVE_FILE_SET_MISMATCH')

def read_target_manifest(plan):
    raw=Path(plan['manifest_path']).read_bytes()
    need(hashlib.sha256(raw).hexdigest()==plan['manifest_sha256'],'TARGET_PLAN_DRIFT')
    return raw


def verify_common_packet():
    need(MANIFEST['review_status']=='APPROVED_LOCAL_F0_PRIVILEGE_CEILING_ATTEMPT','OPERATION_NOT_REVIEWED')
    validation=unique_json(read_pinned(OWNED_VALIDATION))
    review=validation.get('independent_safety_sql_review')
    need(type(review) is dict and review.get('decision')=='SOURCE_APPROVED','SAFETY_SQL_REVIEW_REQUIRED')
    need(MANIFEST['wrapper_sha256']==hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),'WRAPPER_SOURCE_MISMATCH')
    need(command(['git','-c','core.longpaths=true','rev-parse','HEAD']).stdout.strip()==COMMIT and command(['git','-c','core.longpaths=true','rev-parse','HEAD^{tree}']).stdout.strip()==TREE,'SOURCE_CHECKPOINT_MISMATCH')
    hashes=MANIFEST['packet_files_sha256']
    required={'review-output/foundation-bootstrap.review.sql','review-output/foundation-bootstrap-finalize.review.sql','review-output/foundation-application.review.sql','scripts/sql-review/run-first-rehearsal.py','scripts/sql-review/rehearsal-diagnostics.py','scripts/prepare-local-f0-history.py','scripts/sql-review/run-local-f0-migrate.py','prisma.local-f0.config.mjs','scripts/sql-review/local-f0-migrate-guard.mjs','scripts/sql-review/local-f0-migrate-runner.mjs','scripts/sql-review/migration_server_diagnostics.py'}
    need(required<=set(hashes),'REQUIRED_PACKET_FILES_MISSING')
    for path,expected in hashes.items():
        need(not Path(path).is_absolute() and '..' not in Path(path).parts,'UNSAFE_PACKET_PATH')
        need(hashlib.sha256((ROOT/path).read_bytes()).hexdigest()==expected,'PACKET_FILE_DRIFT',{'path':path})
        blob=subprocess.run(['git','-c','core.longpaths=true','show',COMMIT+':'+path],cwd=ROOT,capture_output=True,timeout=30)
        need(blob.returncode==0 and hashlib.sha256(blob.stdout).hexdigest()==expected,'COMMITTED_PACKET_MISMATCH',{'path':path})
    aggregate=hashlib.sha256(''.join(p+'\0'+hashes[p]+'\n' for p in sorted(hashes)).encode()).hexdigest()
    need(aggregate==PACKET,'PACKET_AGGREGATE_MISMATCH')
    need(MANIFEST['image']==IMAGE and MANIFEST['database']==DB and MANIFEST['run_label']==LABEL,'TARGET_MANIFEST_MISMATCH')
    need(MANIFEST['server_diagnostics']=={'prefix':'WA_F0_DIAG|%e|%u|%d|','verbosity':'terse','lc_messages':'C','log_min_messages':'warning','log_statement':'none','log_min_error_statement':'panic','module_sha256':hashes['scripts/sql-review/migration_server_diagnostics.py'],'raw_log_retention':False},'SERVER_DIAGNOSTIC_PLAN_MISMATCH')
    need(hashlib.sha256(Path(MANIFEST['tool_archive']).read_bytes()).hexdigest()==MANIFEST['tool_archive_sha256'],'TOOL_ARCHIVE_DRIFT')
    verified_tools=None
    for kind,plan in MANIFEST['migration_targets'].items():
        raw=read_target_manifest(plan)
        migration=json.loads(raw);target=next(t for t in TARGETS if t['kind']==kind)
        if verified_tools is None:
            validate_archive(MANIFEST['tool_archive'],migration['tools']['files_sha256']);verified_tools=migration['tools']['files_sha256']
        else:need(verified_tools==migration['tools']['files_sha256'],'TARGET_TOOL_CLOSURES_DIFFER')
        need(migration['run_id']==RUN_ID and migration['target']['container_name']==target['name'] and migration['target']['volume_name']==target['volume'],'TARGET_PLAN_IDENTITY')
        need(migration['target']['bootstrap_secret_host_path']==str(PRIVATE/(kind+'-bootstrap-password')),'SECRET_MOUNT_PLAN_MISMATCH')
        snapshot=Path(plan['source_snapshot'])
        current={p.relative_to(snapshot).as_posix():hashlib.sha256(p.read_bytes()).hexdigest() for p in snapshot.rglob('*') if p.is_file()}
        need(current==plan['source_files_sha256'],'SOURCE_SNAPSHOT_DRIFT')
        need(hashlib.sha256(Path(plan['source_archive']).read_bytes()).hexdigest()==plan['source_archive_sha256'],'SOURCE_ARCHIVE_DRIFT')
        validate_archive(plan['source_archive'],current)
        for path in ('prisma.local-f0.config.mjs','scripts/sql-review/local-f0-migrate-guard.mjs','scripts/sql-review/local-f0-migrate-runner.mjs','prisma/review/foundation-candidate.prisma','prisma/foundation/migrations/migration_lock.toml','prisma/foundation/migrations/20261117000100_f0_local_initial/migration.sql'):
            need(current[path]==hashes[path],'SOURCE_SNAPSHOT_NOT_COMMITTED_PACKET',{'path':path})
    report['source_verification']={'commit':COMMIT,'tree':TREE,'packet_sha256':aggregate,'files_sha256':hashes,'file_count':len(hashes)}
    report['run_manifest']=MANIFEST;report['run_manifest_sha256']=hashlib.sha256(MANIFEST_PATH.read_bytes()).hexdigest()
    event('SOURCE_VERIFICATION','PASS',files=len(hashes),packet_sha256=aggregate)

def bootstrap_all():
    for target in TARGETS:
        name=target['name']
        settings=observe(name,"SELECT jsonb_build_object('login',session_user,'auth',system_user,'safe',current_setting('log_statement')='none' AND current_setting('log_min_error_statement')='panic' AND current_setting('password_encryption')='scram-sha-256' AND current_setting('server_version') LIKE '17.11%','diagnostics_safe',current_setting('log_error_verbosity')='terse' AND current_setting('log_line_prefix')='WA_F0_DIAG|%e|%u|%d|' AND current_setting('lc_messages')='C' AND current_setting('log_min_messages')='warning' AND current_setting('log_destination')='stderr' AND current_setting('logging_collector')='off' AND current_setting('debug_print_parse')='off' AND current_setting('debug_print_rewritten')='off' AND current_setting('debug_print_plan')='off','superuser',(SELECT rolsuper FROM pg_roles WHERE rolname=session_user));",'BOOTSTRAP_SETTINGS')
        need(settings=={'login':'postgres','auth':'scram-sha-256:postgres','safe':True,'diagnostics_safe':True,'superuser':True},'UNSAFE_BOOTSTRAP_SETTINGS')
        report['targets'][name]['server_settings']=settings
        before=observe(name,"SELECT jsonb_build_object('public_owner',(SELECT pg_get_userbyid(nspowner) FROM pg_namespace WHERE nspname='public'),'public_acl',(SELECT jsonb_agg(jsonb_build_object('role',CASE WHEN x.grantee=0 THEN 'PUBLIC' ELSE pg_get_userbyid(x.grantee) END,'privilege',x.privilege_type,'grantor',pg_get_userbyid(x.grantor),'grant_option',x.is_grantable) ORDER BY x.grantee,x.privilege_type) FROM pg_namespace n CROSS JOIN LATERAL aclexplode(coalesce(n.nspacl,acldefault('n',n.nspowner))) x WHERE n.nspname='public'),'application_roles',(SELECT count(*) FROM pg_roles WHERE rolname LIKE 'wa_%'),'event_triggers',(SELECT count(*) FROM pg_event_trigger));",'FRESH_PRE_BOOTSTRAP_PUBLIC_BASELINE')
        expected=[{'role':'pg_database_owner','privilege':p,'grantor':'pg_database_owner','grant_option':False} for p in ('CREATE','USAGE')]+[{'role':'PUBLIC','privilege':'USAGE','grantor':'pg_database_owner','grant_option':False}]
        need(before['public_owner']=='pg_database_owner' and before['application_roles']==before['event_triggers']==0 and sorted(before['public_acl'],key=lambda r:(r['role'],r['privilege']))==sorted(expected,key=lambda r:(r['role'],r['privilege'])),'FRESH_PUBLIC_BASELINE_NOT_EXPECTED')
        report['targets'][name]['pre_bootstrap_public_baseline']=before
        bootstrap_attempted.add(name);report['targets'][name]['bootstrap']='ATTEMPTED';save()
        sql(name,'postgres',read_pinned('review-output/foundation-bootstrap.review.sql').decode('utf8'),'BOOTSTRAP')
        bootstrapped.add(name);report['targets'][name]['bootstrap']='PASS'
        statements=[f'ALTER DATABASE {DB} SET log_statement=none;',f'ALTER DATABASE {DB} SET log_min_error_statement=panic;',f'REVOKE CONNECT,TEMP ON DATABASE {DB} FROM PUBLIC;',f'GRANT CONNECT ON DATABASE {DB} TO '+','.join(ROLES)+';']
        statements+=['ALTER ROLE '+role+" PASSWORD '"+passwords[name][role]+"';" for role in ROLES if role!='postgres']
        sql(name,'postgres','\n'.join(statements),'CREDENTIAL_PROVISION')
        source_authentication_preflight(name)
        baseline=observe(name,"SELECT jsonb_build_object('public_owner',(SELECT pg_get_userbyid(nspowner) FROM pg_namespace WHERE nspname='public'),'public_acl',(SELECT nspacl::text FROM pg_namespace WHERE nspname='public'),'event_triggers',(SELECT count(*) FROM pg_event_trigger),'public_relations',(SELECT count(*) FROM pg_class c JOIN pg_namespace n ON n.oid=c.relnamespace WHERE n.nspname='public'),'application_relations',(SELECT count(*) FROM pg_class c JOIN pg_namespace n ON n.oid=c.relnamespace WHERE n.nspname IN ('app','platform','platform_private')));",'EMPTY_APPLICATION_BASELINE')
        need(baseline['event_triggers']==baseline['public_relations']==baseline['application_relations']==0,'NONEMPTY_MIGRATION_BASELINE')
        report['targets'][name]['baseline']=baseline;event('AUTHENTICATION_PREFLIGHT','PASS',target=name,roles=6)
    report['steps']['CATALOG-AUTH']='PASS';save()

def provision_migration_tools():
    for target in TARGETS:
        name=target['name'];identity=created_containers[name];plan=MANIFEST['migration_targets'][target['kind']]
        expected=json.loads(read_target_manifest(plan))['tools']['files_sha256']
        need(docker(['exec',identity,'mkdir','-p','/run/wa-f0-tools','/run/wa-f0-source']).returncode==0,'TOOL_DIRECTORIES_FAILED')
        need(docker(['cp',MANIFEST['tool_archive'],identity+':/run/wa-f0-tools.tar.gz'],timeout=120).returncode==0,'TOOL_COPY_FAILED')
        need(docker(['exec',identity,'tar','-xzf','/run/wa-f0-tools.tar.gz','-C','/run/wa-f0-tools'],timeout=120).returncode==0,'TOOL_EXTRACT_FAILED')
        need(docker(['exec',identity,'rm','--','/run/wa-f0-tools.tar.gz']).returncode==0,'TOOL_ARCHIVE_REMOVAL_FAILED')
        # This archive is prepared/reviewed from the exact immutable file map.
        need(hashlib.sha256(Path(plan['source_archive']).read_bytes()).hexdigest()==plan['source_archive_sha256'],'SOURCE_ARCHIVE_DRIFT')
        need(docker(['cp',plan['source_archive'],identity+':/run/wa-f0-source.tar.gz'],timeout=120).returncode==0,'SOURCE_COPY_FAILED')
        need(docker(['exec',identity,'tar','-xzf','/run/wa-f0-source.tar.gz','-C','/run/wa-f0-source'],timeout=60).returncode==0,'SOURCE_EXTRACT_FAILED')
        need(docker(['exec',identity,'rm','--','/run/wa-f0-source.tar.gz']).returncode==0,'SOURCE_ARCHIVE_REMOVAL_FAILED')
        migrator_url='postgresql://wa_migrator:'+passwords[name]['wa_migrator']+'@127.0.0.1:5432/'+DB+'?schema=public&sslmode=disable'
        r=docker(['exec','-i',identity,'sh','-ceu','umask 077; cat > /run/wa-secrets/wa-local-f0-migrator-url; chmod 600 /run/wa-secrets/wa-local-f0-migrator-url; stat -c "%a:%u:%g" /run/wa-secrets/wa-local-f0-migrator-url'],input=migrator_url)
        need(r.returncode==0 and r.stdout.strip()=='600:0:0','MIGRATOR_URL_PRIVILEGE_MODE')
        # Trusted image utility verifies copied binaries before first execution.
        names=['node/bin/node','schema-engine','node_modules/prisma/build/index.js','node_modules/prisma/build/cli.js','node_modules/prisma/config.js']
        actual=docker(['exec',identity,'/usr/bin/sha256sum','--',*['/run/wa-f0-tools/'+p for p in names]])
        need(actual.returncode==0,'TOOL_PREEXEC_HASH_FAILED')
        parsed={line.split('  ',1)[1].removeprefix('/run/wa-f0-tools/'):line.split('  ',1)[0] for line in actual.stdout.splitlines()}
        need(parsed=={p:expected[p] for p in names},'TOOL_PREEXEC_HASH_MISMATCH')
        node=docker(['exec',identity,'/run/wa-f0-tools/node/bin/node','--version'])
        engine=docker(['exec',identity,'/run/wa-f0-tools/schema-engine','--version'])
        need(node.returncode==0 and node.stdout.strip()=='v24.22.1' and engine.returncode==0 and re.search(r'\bd1b3f377ca835d73fd50954a5e22128b9ebdd6b8\b',engine.stdout),'LINUX_TOOL_COMPATIBILITY_FAILED')
        report['targets'][name]['linux_tool_compatibility']={'node':'v24.22.1','engine_commit':'d1b3f377ca835d73fd50954a5e22128b9ebdd6b8','preexec_hashes_verified':True};event('LINUX_TOOL_COMPATIBILITY','PASS',target=name)
    report['steps']['CATALOG-TOOLS']='PASS';save()

def migrate(target,operation,label,proof=None):
    name=target['name'];plan=MANIFEST['migration_targets'][target['kind']]
    manifest_raw=read_target_manifest(plan)
    module=load_reviewed_helper('scripts/sql-review/run-local-f0-migrate.py')
    report['stage']=label;save()
    def created_identity_process(arguments,**options):
        result=subprocess.run(arguments,**options)
        if arguments==['docker','--context','desktop-linux','inspect',name] and result.returncode==0:
            objects=json.loads(result.stdout)
            need(len(objects)==1 and objects[0]['Id']==created_containers[name],'CREATED_CONTAINER_IDENTITY_CHANGED')
        return result
    try:value=module['coordinate'](manifest_raw,operation,None if proof is None else proof.read_bytes(),process=created_identity_process)
    except module['HeldFailure'] as error:
        comparison=module['mount_failure_comparison'](error)
        if comparison is not None:report['resource_guard_comparison']=comparison;save()
        raise Stop('MIGRATION_GUARD_REFUSED',{'code':error.code,**({'mount_comparison':comparison} if comparison is not None else {})}) from None
    except subprocess.TimeoutExpired:raise Stop('MIGRATION_PROCESS_TIMEOUT_CLOSURE_UNCONFIRMED') from None
    except Exception:raise Stop('MIGRATION_RESPONSE_OR_PROCESS_UNCONFIRMED') from None
    report.setdefault('migration_operations',[]).append({'target':name,'stage':label,**value});save()
    return value

def migrate_success(target,operation,label,proof=None):
    value=migrate(target,operation,label,proof)
    need(value['status']=='CLI_COMPLETED_REQUIRES_INDEPENDENT_LEDGER_CATALOG_CHECKS' and type(value['exit_code']) is int and value['exit_code']==0,'PRISMA_COMPLETED_STATUS_REQUIRED')
    return value



# New catalog-only pipeline. The common definitions above are preserved; only
# verify_packet was renamed to allow this additional pre-creation verification.
import contextlib
import io
import math
from types import ModuleType

GENERATOR = 'scripts/prepare-native-catalog-review.py'
GENERATOR_SHA = 'cef4f4f191e478593a679e9b86c7eee410531b01501a896c0b6f0e1bc1ac4fa2'
EXPECTED_SHA = '3be81a13d3bb2abb41bf03ef68398da6d92fbdbccffec3d74508e91dd455f433'
MIGRATION = '20261117000100_f0_local_initial'
APPLICATION_SHA = '5ae39abf991f9c189e367eb6ab6968b0ad50836bf4220ac27ef8c18306ac26ad'
CATALOG = {}
ASSET_NAMES = {'source-pins.json','expected.json','expression-oracle-plan.json','expression-oracle.sql','public-schema-registration.json','README.md'}
TOOL_DATA = {'node_modules/@prisma/engines-version/package.json','node_modules/prisma/package.json'}
NATIVE_LISTS = {'schemas','roles','memberships','relations','columns','types','enums','constraints','indexes','functions','triggers','policies','nonowner_acl','owner_acl','generated_type_acl','default_acl','default_acl_outside_registered_schemas','extensions','public_owned_relations','public_schema_acl','public_wa_schema_acl'}
BOOL_KEYS = {'read_only','collector_is_superuser','rolsuper','rolinherit','rolcreaterole','rolcreatedb','rolcanlogin','rolreplication','rolbypassrls','admin','inherit','set','rls','force_rls','nullable','collation_is_type_default','storage_is_type_default','is_local','deferrable','initially_deferred','validated','no_inherit','has_index','unique','primary','valid','ready','live','immediate','clustered','nulls_not_distinct','included','opclass_default','descending','nulls_first','returns_set','security_definer','strict','leakproof','variadic','support_function','internal','constraint','function_release_builtin','has_constraint_relation','has_constraint_index','permissive','grant_option','history_ids_unique','checksum_format_valid','id_is_uuid_v4','started','finished','rolled_back','time_order_valid','no_options','default_tablespace','not_partition','no_inheritance','no_index_acl','no_expressions','no_predicate','no_referenced_relation','no_expression'}
INT_KEYS = {'server_version_num','rolconnlimit','ordinal','typmod','array_dimensions','inherited_count','key_count','total_count','position','default_count','type_bits','argument_count','object_subid','referenced_subid','triggers_count','policies_count','rules_count','steps'}
META_KEYS = NATIVE_LISTS | BOOL_KEYS | INT_KEYS | {'format','collected_as','public_schema_owner','object','owner','name','rolvaliduntil','rolconfig','role','member','grantor','kind','persistence','replica_identity','table_name','type','identity','generated','compression','default_sha256','category','element','relation','labels','columns','references','referenced_columns','match','update_action','delete_action','expression_sha256','definition_sha256','referenced_unique_index','index_name','access_method','keys','predicate_sha256','column','opclass','language','return_type','volatility','parallel','cost','rows','settings','defaults_sha256','body_sha256','parameters','mode','enabled','function','function_identity','arguments_sha256','when_sha256','constraint_name','constraint_table','referenced_table','constraint_index','dependencies','direction','class','dependency_type','command','roles','using_sha256','with_check_sha256','grantee','privilege','creator','schema','entries','database','isolation','session_user','history','logs_state','name_sha256','checksum_sha256'}
SAFE_FILES = {'text-preflight.json','acl-preflight.json','native-before.json','native-after-oracle.json','native-after-ledger.json','oracle-preflight.json','oracle-results.json','oracle-closure.json','oracle-evidence.json','ledger-registration.json','ledger-observation.json','ledger-evidence.json','catalog-comparison.json'}
ACL_FIELDS='grantee grantor privilege grant_option'
NATIVE_ROWS={
 'schemas':'object owner','roles':'name rolsuper rolinherit rolcreaterole rolcreatedb rolcanlogin rolreplication rolbypassrls rolconnlimit rolvaliduntil rolconfig',
 'memberships':'role member grantor admin inherit set','relations':'object kind owner persistence rls force_rls replica_identity',
 'columns':'table_name name ordinal type typmod array_dimensions nullable identity generated collation_is_type_default storage_is_type_default compression is_local inherited_count default_sha256',
 'types':'object owner kind category element relation','enums':'object owner labels',
 'constraints':'table_name name kind deferrable initially_deferred validated no_inherit columns references referenced_columns match update_action delete_action expression_sha256 definition_sha256 has_index referenced_unique_index index_name',
 'indexes':'object table_name owner access_method unique primary valid ready live immediate clustered replica_identity nulls_not_distinct key_count keys predicate_sha256 definition_sha256',
 'functions':'object name owner language return_type returns_set security_definer strict leakproof volatility parallel kind cost rows settings variadic support_function default_count defaults_sha256 body_sha256 parameters',
 'triggers':'table_name name internal type_bits enabled constraint deferrable initially_deferred function function_identity function_release_builtin argument_count arguments_sha256 when_sha256 constraint_name constraint_table has_constraint_relation referenced_table has_constraint_index constraint_index dependencies',
 'policies':'table_name name command permissive roles using_sha256 with_check_sha256',
 'nonowner_acl':'kind object column '+ACL_FIELDS,'owner_acl':'kind object column '+ACL_FIELDS,'generated_type_acl':'object '+ACL_FIELDS,
 'default_acl':'creator schema kind entries','default_acl_outside_registered_schemas':'creator schema kind','extensions':'name version schema owner',
 'public_owned_relations':'object kind owner rls force_rls nonowner_acl','public_schema_acl':ACL_FIELDS,'public_wa_schema_acl':ACL_FIELDS,
}
META_KEYS.add('version')
META_KEYS.update(('table_acl','column_acl'))


def canonical(value):
    return json.dumps(value,sort_keys=True,separators=(',',':'),ensure_ascii=False,allow_nan=False)


def digest(value):
    return hashlib.sha256(canonical(value).encode('utf8')).hexdigest()


def exact(value,expected,code):
    need(canonical(value)==canonical(expected),code)


def unique_json(raw):
    def pairs(items):
        value={}
        for key,item in items:
            need(key not in value,'DUPLICATE_CATALOG_JSON_FIELD');value[key]=item
        return value
    def bad_constant(_):raise Stop('NONFINITE_CATALOG_JSON')
    return json.loads(raw,object_pairs_hook=pairs,parse_constant=bad_constant)


def read_pinned(relative):
    need(type(relative) is str and not relative.startswith('/') and '\\' not in relative and all(x not in ('','.','..') for x in relative.split('/')),'UNSAFE_CATALOG_PACKET_PATH')
    path=(ROOT/relative).resolve();need(path.is_relative_to(ROOT.resolve()),'CATALOG_PACKET_PATH_ESCAPE')
    raw=path.read_bytes()
    need(hashlib.sha256(raw).hexdigest()==MANIFEST['packet_files_sha256'][relative],'CATALOG_PACKET_SOURCE_DRIFT')
    return raw


def verify_tool_data():
    expected=MANIFEST['catalog']['tool_source_files_sha256']
    need(type(expected) is dict and set(expected)==TOOL_DATA,'TOOL_SOURCE_DATA_SET')
    closure=unique_json(read_pinned('context/reconciliation/local-f0-tooling/prisma-tools-closure.json'))
    plan=MANIFEST['migration_targets']['ok']
    raw=read_target_manifest(plan)
    tools=unique_json(raw)['tools']['files_sha256']
    for relative,value in expected.items():
        need(type(value) is str and re.fullmatch('[0-9a-f]{64}',value),'TOOL_SOURCE_DATA_HASH')
        need(value==closure['tools_files_sha256'][relative]==tools[relative],'TOOL_SOURCE_DATA_CLOSURE_MISMATCH')
        need(hashlib.sha256((ROOT/relative).read_bytes()).hexdigest()==value,'TOOL_SOURCE_DATA_DRIFT')


def verify_catalog_packet():
    verify_common_packet()
    need(MANIFEST['packet_files_sha256'].get('scripts/sql-review/catalog-text-preflight.sql')=='f1cab9adf94fe5aa2452f34213eea43cf4ecfe35c9ce5f5289486b7d4f859823','TEXT_PREFLIGHT_SOURCE_REQUIRED')
    need(MANIFEST['packet_files_sha256'].get('scripts/sql-review/catalog-acl-preflight.sql')=='7018c8f415923533dc461b212a0df0f9a0f4144457e410c4505c9322df4647f4','ACL_PREFLIGHT_SOURCE_REQUIRED')
    need(len(TARGETS)==1 and TARGETS[0]['kind']=='ok' and set(MANIFEST['migration_targets'])=={'ok'},'ONE_CATALOG_TARGET_REQUIRED')
    name='wa-p0c-'+RUN_ID[:8]+'-privilege'
    exact(TARGETS,[{'name':name,'volume':name+'-data','kind':'ok'}],'CATALOG_RESOURCE_NAMES')
    cfg=MANIFEST['catalog']
    exact(sorted(cfg),sorted(('generator','artifact_root','assets','source_expected_sha256','public_schema_owner','bootstrap_grantor','tool_source_files_sha256','ledger_expectation')),'CATALOG_CONFIGURATION_FIELDS')
    need(cfg['generator']==GENERATOR and cfg['artifact_root']=='review-output/native-catalog' and cfg['source_expected_sha256']==EXPECTED_SHA and cfg['public_schema_owner']=='pg_database_owner' and cfg['bootstrap_grantor']=='postgres','CATALOG_CONFIGURATION_IDENTITY')
    exact(cfg['ledger_expectation'],[{'path':'prisma/foundation/migrations/'+MIGRATION+'/migration.sql','migration_name':MIGRATION,'sha256':APPLICATION_SHA,'state':'applied','count':1}],'ONE_CANONICAL_APPLIED_HISTORY_REQUIRED')
    verify_tool_data()
    generator=read_pinned(GENERATOR)
    need(hashlib.sha256(generator).hexdigest()==GENERATOR_SHA,'CATALOG_GENERATOR_NOT_REVIEWED')
    namespace=ModuleType('_reviewed_catalog_generator');namespace.__file__=str(ROOT/GENERATOR)
    output=io.StringIO()
    with contextlib.redirect_stdout(output),contextlib.redirect_stderr(output):
        exec(compile(generator,str(ROOT/GENERATOR),'exec'),namespace.__dict__)
    need(not output.getvalue(),'CATALOG_GENERATOR_IMPORT_OUTPUT')
    assets=cfg['assets'];need(type(assets) is dict and set(assets)==ASSET_NAMES,'CATALOG_ASSET_SET')
    actual={}
    for key,value in assets.items():
        exact(value,{'path':cfg['artifact_root']+'/'+key,'sha256':MANIFEST['packet_files_sha256'][cfg['artifact_root']+'/'+key]},'CATALOG_ASSET_BINDING')
        actual[key]=read_pinned(value['path'])
    pins=unique_json(actual['source-pins.json'])
    need(set(pins)==set(namespace.REQUIRED_FILES) and len(pins)==16,'CLOSED_CATALOG_SOURCES_REQUIRED')
    for relative,value in pins.items():need(MANIFEST['packet_files_sha256'][relative]==value,'CATALOG_SOURCE_PIN_NOT_IN_PACKET')
    with contextlib.redirect_stdout(output),contextlib.redirect_stderr(output):
        reproduced,summary=namespace.prepare(ROOT,pins)
        tools=namespace.load_catalog_tools(ROOT,pins)
        runtime_manifest=tools['catalog_manifest'].build_manifest(ROOT,pins)
        runtime_plan=tools['catalog_expression_oracle'].build_plan(runtime_manifest,ROOT)
    need(not output.getvalue(),'CATALOG_PREPARATION_OUTPUT')
    need(reproduced==actual and summary['status']=='NOT_RUN' and summary['source_expected_sha256']==EXPECTED_SHA,'CATALOG_ASSET_REPRODUCTION')
    need(namespace.encoded(runtime_manifest)==actual['expected.json'] and namespace.encoded(runtime_plan)==actual['expression-oracle-plan.json'],'CATALOG_RUNTIME_SOURCE_REPRODUCTION')
    # emit_sql uses source declaration order; sorted JSON is a review artifact,
    # not a replacement for the freshly compiled source object's insertion order.
    CATALOG.update(generator=namespace,tools=tools,pins=pins,expected=runtime_manifest,plan=runtime_plan,oracle_sql=actual['expression-oracle.sql'].decode('utf8'),public=unique_json(actual['public-schema-registration.json']))
    CATALOG['strings'],CATALOG['generated_names']=metadata_allowlist(CATALOG['expected'],tools)
    report['catalog_preparation']={'status':'SOURCE_REPRODUCED_NOT_RUN','assets_sha256':{k:hashlib.sha256(v).hexdigest() for k,v in sorted(actual.items())},'source_expected_sha256':EXPECTED_SHA,'closed_source_files':16}
    save()


def metadata_allowlist(manifest,tools):
    allowed={'',' ','postgres','pg_database_owner','PUBLIC','public','pg_catalog','plpgsql','sql','internal','btree','1.0','repeatable read','NULL','EMPTY','NONEMPTY','O','r','p','v','m','S','f','b','c','e','u','x','t','d','n','a','s','i','w','C','A','E','U','*','TABLE','SEQUENCE','FUNCTION','TYPE','SCHEMA','SELECT','INSERT','UPDATE','DELETE','TRUNCATE','REFERENCES','TRIGGER','MAINTAIN','EXECUTE','USAGE','CREATE','trigger_to','to_trigger','function','relation','constraint','unsupported','workinants.native-catalog.v1','workinants.prisma-ledger-native.v1',DB}
    def add(value):
        if type(value) is str:
            if len(value)<=1024 and not any(ord(x)<32 for x in value):allowed.add(value)
        elif type(value) is dict:
            for key,item in value.items():add(key);add(item)
        elif type(value) is list:
            for item in value:add(item)
    expected=manifest['expected']
    for key in ('roles','schemas','tables','enums','functions','explicit_indexes','policies','triggers','memberships','nonowner_acl','default_acl'):add(expected[key])
    add(tools['pg17_catalog_rules'].generated_types(expected))
    add(tools['prisma_ledger_proof'].schema_expectation())
    add(tools['pg17_catalog_rules'].PINNED_TRIGGER_FUNCTIONS)
    for name in tools['pg17_catalog_rules'].PINNED_TRIGGER_FUNCTIONS:add(name.removesuffix('()'))
    for typ in ('uuid','text','timestamptz','timestamp','int2','int4','int8','bool','numeric','float4','float8','jsonb','array','enum','bpchar','varchar'):
        allowed.add('pg_catalog.'+typ+'_ops')
    generated=[]
    for table,info in expected['tables'].items():
        ns,base=table.split('.')
        for con in info['constraints']:
            if con['name']:
                add(con['name']);add(ns+'.'+con['name']);add(table+'/'+con['name'])
            elif con['kind'] in ('PRIMARY','UNIQUE','FOREIGN','CHECK'):
                label={'PRIMARY':'pkey','UNIQUE':'key','FOREIGN':'fkey','CHECK':'check'}[con['kind']]
                columns=con['columns']
                names=[None] if label=='pkey' else ['_'.join(columns)] if columns else [None]
                if label=='check':
                    names=[None]+sorted(tools['compare_native_catalog']._column_refs(con['expression']['ast'])) if con['expression'] else [None]
                generated.extend((ns,base,column,label,table) for column in names)
        for column in info['columns'].values():
            value=column['type'];add(value['name']+'[]'*value['array_dimensions'])
    for identity,fn in expected['functions'].items():
        add(identity);add(fn['name']);add(fn['return_type']['name']+'[]'*fn['return_type']['array_dimensions'])
        for setting in fn['settings_ast']:
            add(setting['name']+'='+', '.join(str(tools['catalog_manifest'].literal(v)) for v in setting.get('args',[])))
    return allowed,generated


def generated_identifier(value):
    if re.fullmatch(r'(?:RI_ConstraintTrigger_[ac]_|Unique_ConstraintTrigger_)[0-9]{1,12}',value):return True
    if '/' in value:
        table,value=value.split('/',1);namespace=table.split('.')[0]
    else:
        table=None
        if '.' in value:namespace,value=value.split('.',1)
        else:namespace=None
    match=re.search(r'_(pkey|key|check|fkey)([0-9]{0,3})$',value)
    if not match or len(value)>63:return False
    for ns,base,column,label,relation in CATALOG['generated_names']:
        if label!=match[1] or namespace not in (None,ns) or table not in (None,relation):continue
        suffix=label+match[2];one,two=len(base),len(column) if column else 0
        available=63-len(suffix)-(2 if column else 1)
        while one+two>available:
            if one>two:one-=1
            else:two-=1
        candidate=base[:one]+('_'+column[:two] if column else '')+'_'+suffix
        if value==candidate:return True
    return False


def filter_metadata(value,key=None,depth=0):
    need(depth<=20,'CATALOG_METADATA_DEPTH')
    if key in BOOL_KEYS:need(type(value) is bool,'CATALOG_METADATA_BOOLEAN');return
    if key in INT_KEYS:need(type(value) is int and -1<=value<=2147483647,'CATALOG_METADATA_INTEGER');return
    if value is None:return
    if key and key.endswith('_sha256'):
        need(type(value) is str and re.fullmatch('[0-9a-f]{64}',value),'CATALOG_METADATA_HASH');return
    if type(value) is dict:
        need(set(value)<=META_KEYS,'CATALOG_METADATA_FIELD')
        for name,item in value.items():filter_metadata(item,name,depth+1)
    elif type(value) is list:
        need(len(value)<=20000,'CATALOG_METADATA_LIMIT')
        for item in value:filter_metadata(item,None,depth+1)
    elif type(value) is str:
        if key in ('owner','role','member','grantor','grantee','creator','collected_as','session_user','public_schema_owner'):
            need(value in set(CATALOG['expected']['expected']['roles'])|{'postgres','PUBLIC','pg_database_owner'},'CATALOG_METADATA_ROLE')
        if key in ('table_name','references','constraint_table','referenced_table','relation'):
            need(value in CATALOG['expected']['expected']['tables'],'CATALOG_METADATA_RELATION')
        need(value in CATALOG['strings'] or generated_identifier(value),'CATALOG_METADATA_STRING')
    elif type(value) is bool:pass
    elif type(value) in (int,float):
        need(key in ('cost','rows') and math.isfinite(value) and 0<=value<=1000000,'CATALOG_METADATA_NUMBER')
    else:raise Stop('CATALOG_METADATA_TYPE')


# Diagnostics describe rejected strings only by fixed paths and hashes. They do
# not expand metadata_allowlist/filter_metadata or authorize a native snapshot.
METADATA_DIAGNOSTIC_ENTRY_LIMIT=256
METADATA_DIAGNOSTIC_NODE_LIMIT=262144

def metadata_vocabulary_diagnostics(value):
    import unicodedata
    hints=[];stats={'visited_nodes':0,'unknown_strings_seen':0,'unregistered_fields_omitted':0,'traversal_complete':True}
    def length_class(size):
        if size==0:return 'EMPTY'
        if size==1:return 'ONE'
        if size<=63:return 'TWO_TO_63'
        if size<=255:return '64_TO_255'
        if size<=1024:return '256_TO_1024'
        return 'OVER_1024'
    def walk(item,path,key=None,depth=0):
        if stats['visited_nodes']>=METADATA_DIAGNOSTIC_NODE_LIMIT or depth>20:
            stats['traversal_complete']=False;return
        stats['visited_nodes']+=1
        if type(item) is dict:
            # Never place an unregistered dictionary key or its subtree in a path.
            registered=sorted(name for name in item if type(name) is str and name in META_KEYS)
            omitted=len(item)-len(registered)
            stats['unregistered_fields_omitted']+=omitted
            if omitted:stats['traversal_complete']=False
            for name in registered:walk(item[name],path+[name],name,depth+1)
        elif type(item) is list:
            if len(item)>20000:stats['traversal_complete']=False
            for index,child in enumerate(item[:20000]):
                if stats['visited_nodes']>=METADATA_DIAGNOSTIC_NODE_LIMIT:
                    stats['traversal_complete']=False;break
                walk(child,path+[index],None,depth+1)
        elif type(item) is str:
            if key and key.endswith('_sha256') and re.fullmatch('[0-9a-f]{64}',item):return
            if item in CATALOG['strings'] or generated_identifier(item):return
            stats['unknown_strings_seen']+=1
            if len(hints)<METADATA_DIAGNOSTIC_ENTRY_LIMIT:
                hints.append({'path':path,'value_sha256':hashlib.sha256(item.encode('utf8')).hexdigest(),
                              'length_class':length_class(len(item)),
                              'has_control_characters':any(unicodedata.category(char) in ('Cc','Cf','Cs') for char in item)})
        elif item is not None and type(item) not in (bool,int,float):stats['traversal_complete']=False
    walk(value,[])
    return {'format':'workinants.catalog-metadata-refusal-diagnostics.v1','qualification':'NOT_QUALIFIED',
            **stats,'entry_limit':METADATA_DIAGNOSTIC_ENTRY_LIMIT,'node_limit':METADATA_DIAGNOSTIC_NODE_LIMIT,
            'entries_truncated':stats['unknown_strings_seen']>len(hints),'unknown_strings':hints}


def row_shapes(value,spec):
    for category,fields in spec.items():
        rows=value[category];need(type(rows) is list,'CATALOG_COMPONENT_ARRAY')
        for row in rows:
            need(type(row) is dict and set(row)==set(fields.split()),'CATALOG_COMPONENT_FIELDS')
    nested=[(row['keys'],'position column included expression_sha256 opclass opclass_default collation_is_type_default descending nulls_first') for row in value.get('indexes',[]) if 'table_name' in row]
    nested += [(row['keys'],'position column included opclass opclass_default collation_is_type_default descending nulls_first') for row in value.get('indexes',[]) if 'table_name' not in row]
    nested += [(row['parameters'],'name mode type') for row in value.get('functions',[])]
    nested += [(row['dependencies'],'direction class object dependency_type object_subid referenced_subid') for row in value.get('triggers',[])]
    nested += [(row['entries'],ACL_FIELDS) for row in value.get('default_acl',[])]
    nested += [(row['nonowner_acl'],ACL_FIELDS) for row in value.get('public_owned_relations',[])]
    for rows,fields in nested:
        need(type(rows) is list and all(type(row) is dict and set(row)==set(fields.split()) for row in rows),'CATALOG_NESTED_FIELDS')


def write_safe(name,value):
    need(name in SAFE_FILES,'UNREGISTERED_SAFE_ARTIFACT')
    raw=(json.dumps(value,indent=2,ensure_ascii=False,allow_nan=False)+'\n').encode('utf8')
    path=OUT/name
    with path.open('xb') as handle:handle.write(raw)
    return {'artifact':name,'artifact_sha256':hashlib.sha256(raw).hexdigest()}


def safe_rejection(stage,value,raw_sha,vocabulary_review=None):
    info={'stage':stage,'status':'REJECTED_NOT_QUALIFIED','raw_sha256':raw_sha}
    if type(value) is dict:
        if value.get('format') in ('workinants.native-catalog.v1','workinants.prisma-ledger-native.v1'):info['format']=value['format']
        info['known_component_counts']={key:len(value[key]) for key in sorted(NATIVE_LISTS|{'history'}) if type(value.get(key)) is list}
        if type(value.get('server_version_num')) is int:info['server_version_num']=value['server_version_num']
        for key in ('read_only','collector_is_superuser'):
            if type(value.get(key)) is bool:info[key]=value[key]
        if value.get('collected_as') in {'postgres'}:info['collected_as']='postgres'
    if vocabulary_review is not None and (vocabulary_review['unknown_strings_seen'] or not vocabulary_review['traversal_complete']):info['metadata_vocabulary_review']=vocabulary_review
    report.setdefault('rejected_observations',[]).append(info);save()






def run_catalog_query(name, text, stage):
    report['stage'] = stage
    save()
    source_sha = hashlib.sha256(text.encode('utf8')).hexdigest()
    with _RequiredSafetyBoundary('CLOSE', name, stage):
        try:
            result = command(psql_args(name, 'postgres'), text, timeout=180)
        except subprocess.TimeoutExpired:
            raise Stop('CATALOG_QUERY_TIMEOUT_CLOSURE_UNCONFIRMED') from None
        except BaseException:
            raise Stop('CATALOG_QUERY_PROCESS_UNCONFIRMED') from None
        need(type(result.returncode) is int and 0 <= result.returncode <= 255, 'CATALOG_QUERY_EXIT_UNCONFIRMED')
        states = sorted(set(re.findall('(?:ERROR|FATAL):\\s+([0-9A-Z]{5}):', result.stderr)))[:8]
        report.setdefault('catalog_operations', []).append({'stage': stage, 'input_sha256': source_sha, 'exit_code': result.returncode, 'client_exited': True, 'sqlstates': states, 'unexpected_stderr': bool(result.stderr.strip()), 'raw_output_discarded': True})
        save()
    report['stage'] = stage
    save()
    return result



def successful_query(result):
    need(result.returncode==0,'CATALOG_SQL_FAILED')
    need(not result.stderr.strip(),'CATALOG_UNEXPECTED_STDERR')


def records(stdout):
    need(type(stdout) is str and len(stdout.encode('utf8'))<=16*1024*1024,'CATALOG_OUTPUT_LIMIT')
    try:return [unique_json(line) for line in stdout.splitlines() if line.strip()]
    except Stop:raise
    except BaseException:raise Stop('CATALOG_JSON_OUTPUT_REJECTED') from None


def collect_native(name,stage,filename):
    text=read_pinned('scripts/sql-review/collect_native_catalog.sql').decode('utf8')
    result=run_catalog_query(name,text,stage)
    value=None;vocabulary_review=None;raw_sha=hashlib.sha256(result.stdout.encode('utf8')).hexdigest()
    try:
        parsed=records(result.stdout);need(len(parsed)==1,'ONE_NATIVE_RECORD_REQUIRED');value=parsed[0]
        need(type(value) is dict and set(value)==NATIVE_LISTS|{'format','server_version_num','read_only','collected_as','collector_is_superuser','public_schema_owner'},'NATIVE_TOP_LEVEL_FIELDS')
        vocabulary_review=metadata_vocabulary_diagnostics(value)
        row_shapes(value,NATIVE_ROWS)
        filter_metadata(value)
        exact({k:value[k] for k in ('format','server_version_num','read_only','collected_as','collector_is_superuser')},{'format':'workinants.native-catalog.v1','server_version_num':170011,'read_only':True,'collected_as':'postgres','collector_is_superuser':True},'NATIVE_COLLECTOR_IDENTITY')
    except BaseException:
        safe_rejection(stage,value,raw_sha,vocabulary_review);raise
    reference=write_safe(filename,value)
    report.setdefault('native_snapshots',[]).append({'stage':stage,'status':'OBSERVED_NOT_QUALIFIED','native_sha256':digest(value),**reference});save()
    successful_query(result)
    return value


def observe_public_baseline(name):
    before=report['targets'][name]['pre_bootstrap_public_baseline'];recipe=CATALOG['public']
    need(type(before) is dict and set(before)=={'public_owner','public_acl','application_roles','event_triggers'},'PUBLIC_PREBOOTSTRAP_FIELDS')
    exact({k:before[k] for k in ('public_owner','application_roles','event_triggers')},{'public_owner':recipe['owner'],'application_roles':0,'event_triggers':0},'PUBLIC_PREBOOTSTRAP_IDENTITY')
    converted=[]
    for row in before['public_acl']:
        need(type(row) is dict and set(row)=={'role','grantor','privilege','grant_option'},'PUBLIC_PREBOOTSTRAP_ACL_FIELDS')
        converted.append({'grantee':row['role'],'grantor':row['grantor'],'privilege':row['privilege'],'grant_option':row['grant_option']})
    exact(sorted(converted,key=canonical),sorted(recipe['baseline_acl'],key=canonical),'PUBLIC_PREBOOTSTRAP_ACL_NOT_PREDECLARED')
    report['public_baseline_verification']={'predeclared_owner_and_three_acl_rows_match':True,'learned_post_install_baseline':False};save()


def oracle_records(stdout):
    need(type(stdout) is str and len(stdout.encode('utf8'))<=16*1024*1024,'CATALOG_OUTPUT_LIMIT')
    safe=[]
    formats=('workinants.expression-oracle-preflight.v1','workinants.expression-oracle-results.v1','workinants.expression-oracle-closure.v1')
    plan=CATALOG['plan'];expected=CATALOG['expected'];oracle=CATALOG['tools']['catalog_expression_oracle']
    # Retain a valid preflight even when a later output line is malformed.
    for index,line in enumerate(line for line in stdout.splitlines() if line.strip()):
        need(index<3,'ORACLE_RECORD_COUNT')
        try:value=unique_json(line)
        except Stop:raise
        except BaseException:raise Stop('CATALOG_JSON_OUTPUT_REJECTED') from None
        need(type(value) is dict and value.get('format')==formats[index],'ORACLE_RECORD_ORDER')
        if index==0:
            need(set(value)=={'format','plan_sha256','outcomes'},'ORACLE_PREFLIGHT_FIELDS')
            exact(value['plan_sha256'],plan['plan_sha256'],'ORACLE_PLAN_BINDING')
            required=set(oracle._prerequisites(expected,DB,'postgres'))
            need(type(value['outcomes']) is dict and set(value['outcomes'])==required and all(type(x) is bool for x in value['outcomes'].values()),'ORACLE_PREFLIGHT_OUTCOMES')
        elif index==1:
            need(set(value)=={'format','source_expected_sha256','source_inputs_aggregate_sha256','plan_sha256','server_version_num','expression_count','expressions'},'ORACLE_RESULT_FIELDS')
            exact({k:value[k] for k in ('source_expected_sha256','source_inputs_aggregate_sha256','plan_sha256','server_version_num','expression_count')},{'source_expected_sha256':EXPECTED_SHA,'source_inputs_aggregate_sha256':expected['inputs_aggregate_sha256'],'plan_sha256':plan['plan_sha256'],'server_version_num':170011,'expression_count':416},'ORACLE_RESULT_BINDING')
            wanted={(r['category'],r['subject'],r['field'],r['source_expression_sha256']) for r in plan['expressions']};seen=set()
            need(type(value['expressions']) is list and len(value['expressions'])==416,'ORACLE_EXPRESSION_COUNT')
            for row in value['expressions']:
                need(type(row) is dict and set(row)=={'category','subject','field','source_expression_sha256','value_sha256'},'ORACLE_EXPRESSION_FIELDS')
                identity=tuple(row[k] for k in ('category','subject','field','source_expression_sha256'))
                need(identity in wanted and identity not in seen and type(row['value_sha256']) is str and re.fullmatch('[0-9a-f]{64}',row['value_sha256']),'ORACLE_EXPRESSION_IDENTITY')
                seen.add(identity)
            need(seen==wanted,'ORACLE_EXPRESSION_COVERAGE')
        else:
            need(set(value)=={'format','plan_sha256','all_oracle_tables_absent','all_oracle_functions_absent'},'ORACLE_CLOSURE_FIELDS')
            exact(value,{'format':formats[index],'plan_sha256':plan['plan_sha256'],'all_oracle_tables_absent':True,'all_oracle_functions_absent':True},'ORACLE_TEMP_ABSENCE')
        write_safe(('oracle-preflight.json','oracle-results.json','oracle-closure.json')[index],value)
        report.setdefault('oracle_records',[]).append({'index':index,'status':'OBSERVED_NOT_QUALIFIED','sha256':digest(value)});save()
        safe.append(value)
    return safe


def acl_compatibility_preflight(name):
    text=read_pinned('scripts/sql-review/catalog-acl-preflight.sql').decode('utf8')
    result=run_catalog_query(name,text,'CATALOG_ACL_COMPATIBILITY')
    successful_query(result)
    parsed=records(result.stdout)
    expected={'format':'workinants.catalog-acl-preflight.v1','server_version_num':170011,'read_only':True,'collected_as':'postgres','collector_is_superuser':True,'old_zero_dimensional_acl_rejected_exactly':True,'null_acl_has_zero_rows':True,'empty_acl_guard_has_zero_rows':True,'sequence_default_has_exact_owner_privileges':True}
    need(len(parsed)==1 and type(parsed[0]) is dict and set(parsed[0])==set(expected),'ACL_PREFLIGHT_FIELDS')
    for key,value in expected.items():need(type(parsed[0][key]) is type(value) and parsed[0][key]==value,'ACL_PREFLIGHT_COMPARISON')
    write_safe('acl-preflight.json',parsed[0])
    report['acl_compatibility_preflight']=parsed[0]
    report['steps']['CATALOG-ACL-COMPAT']='PASS_NEW_SOURCE_COMPATIBILITY_CONTROL';save()


def text_compatibility_preflight(name):
    text=read_pinned('scripts/sql-review/catalog-text-preflight.sql').decode('utf8')
    result=run_catalog_query(name,text,'CATALOG_TEXT_COMPATIBILITY')
    successful_query(result)
    parsed=records(result.stdout)
    expected={'format':'workinants.catalog-text-preflight.v1','server_version_num':170011,'read_only':True,'collected_as':'postgres','collector_is_superuser':True,'identifier_limit_is_63':True,'old_projection_type_is_name':True,'old_projection_truncates_long_value':True,'corrected_projection_type_is_text':True,'corrected_projection_preserves_long_value':True}
    need(len(parsed)==1 and type(parsed[0]) is dict and set(parsed[0])==set(expected),'TEXT_PREFLIGHT_FIELDS')
    for key,value in expected.items():need(type(parsed[0][key]) is type(value) and parsed[0][key]==value,'TEXT_PREFLIGHT_COMPARISON')
    write_safe('text-preflight.json',parsed[0])
    report['text_compatibility_preflight']=parsed[0]
    report['steps']['CATALOG-TEXT-COMPAT']='PASS_NEW_SOURCE_COMPATIBILITY_CONTROL';save()


def catalog_experiment():
    target = TARGETS[0]
    name = target['name']
    tools = CATALOG['tools']
    manifest = CATALOG['expected']
    recipe = CATALOG['public']
    observe_public_baseline(name)
    with _RequiredSafetyBoundary('FINALIZE', name):
        installed = migrate_success(target, 'deploy', 'CATALOG_GENUINE_INITIAL_DEPLOY')
    exact({k: installed[k] for k in ('schema', 'operation', 'run_id', 'container_id', 'source_sql_sha256')}, {'schema': 'workinants.local-f0-migrate-result.v2', 'operation': 'deploy', 'run_id': RUN_ID, 'container_id': created_containers[name], 'source_sql_sha256': APPLICATION_SHA}, 'CATALOG_GENUINE_INSTALL_BINDING')
    need(type(installed['attestation_sha256']) is str and re.fullmatch('[0-9a-f]{64}', installed['attestation_sha256']), 'CATALOG_TARGET_ATTESTATION')
    provider_postinstall(name,installed)
    report['steps']['CATALOG-INSTALL'] = 'PASS'
    save()
    verify_tool_data()
    registration = tools['prisma_ledger_proof'].build_registration(MANIFEST['catalog']['ledger_expectation'], run_id=RUN_ID, target_attestation_sha256=installed['attestation_sha256'], source_expected_sha256=EXPECTED_SHA, root=ROOT, database=DB)
    write_safe('ledger-registration.json', registration)
    report['ledger_registration_sha256'] = digest(registration)
    save()
    acl_compatibility_preflight(name)
    text_compatibility_preflight(name)
    native = collect_native(name, 'NATIVE_BEFORE_ORACLE', 'native-before.json')
    report['steps']['CATALOG-NATIVE'] = 'PASS_OBSERVED_NOT_QUALIFIED'
    save()
    result = run_catalog_query(name, CATALOG['oracle_sql'], 'EXPRESSION_ORACLE')
    parts = oracle_records(result.stdout)
    successful_query(result)
    need(len(parts) == 3 and all((x is True for x in parts[0]['outcomes'].values())), 'ORACLE_ALL_THREE_RECORDS_REQUIRED')
    second = collect_native(name, 'NATIVE_AFTER_ORACLE', 'native-after-oracle.json')
    exact(digest(second), digest(native), 'ORACLE_CHANGED_NATIVE_CATALOG')
    oracle_evidence = {'format': 'workinants.reviewed-expression-oracle-evidence.v1', 'database': DB, 'oracle_sql_sha256': hashlib.sha256(CATALOG['oracle_sql'].encode()).hexdigest(), 'preflight': parts[0], 'results': parts[1], 'closure': parts[2], 'connection_closed_before_observation': True, 'pre_oracle_catalog_sha256': digest(native), 'post_rollback_catalog_sha256': digest(second)}
    tools['catalog_expression_oracle'].validate_evidence(manifest, native, oracle_evidence, database=DB, grantor='postgres', root=ROOT)
    write_safe('oracle-evidence.json', oracle_evidence)
    report['steps']['CATALOG-ORACLE'] = 'PASS_ROLLBACK_OBSERVED_NOT_WHOLE_CASE'
    save()
    result = run_catalog_query(name, read_pinned('scripts/sql-review/collect_prisma_ledger.sql').decode(), 'PRISMA_LEDGER_NATIVE')
    parsed = records(result.stdout)
    value = parsed[0] if len(parsed) == 1 else None
    try:
        need(type(value) is dict, 'ONE_LEDGER_RECORD_REQUIRED')
        need(set(value) == set(tools['prisma_ledger_proof'].schema_expectation()) | {'format', 'server_version_num', 'database', 'read_only', 'isolation', 'collected_as', 'session_user', 'collector_is_superuser', 'history', 'history_ids_unique'}, 'LEDGER_TOP_LEVEL_FIELDS')
        spec = tools['prisma_ledger_proof'].schema_expectation()
        shapes = {key: ' '.join(rows[0]) for key, rows in spec.items() if type(rows) is list and rows}
        shapes.update({'column_acl': 'column ' + ACL_FIELDS, 'history': 'name_sha256 checksum_sha256 checksum_format_valid id_is_uuid_v4 started finished rolled_back time_order_valid steps logs_state'})
        row_shapes(value, shapes)
        filter_metadata(value)
    except BaseException:
        safe_rejection('PRISMA_LEDGER_NATIVE', value, hashlib.sha256(result.stdout.encode()).hexdigest())
        raise
    write_safe('ledger-observation.json', value)
    report['ledger_observation_sha256'] = digest(value)
    save()
    successful_query(result)
    third = collect_native(name, 'NATIVE_AFTER_LEDGER', 'native-after-ledger.json')
    exact(digest(third), digest(native), 'LEDGER_COLLECTION_CHANGED_NATIVE_CATALOG')
    ledger_evidence = {'format': 'workinants.prisma-ledger-evidence.v1', 'registration_sha256': digest(registration), 'collector_sql_sha256': MANIFEST['packet_files_sha256']['scripts/sql-review/collect_prisma_ledger.sql'], 'run_id': RUN_ID, 'target_attestation_sha256': installed['attestation_sha256'], 'native_catalog_before_sha256': digest(second), 'native_catalog_after_sha256': digest(third), 'observation': value}
    write_safe('ledger-evidence.json', ledger_evidence)
    ledger_result = tools['prisma_ledger_proof'].compare_proof(registration, ledger_evidence, native, bootstrap_grantor='postgres', source_expected_sha256=EXPECTED_SHA, root=ROOT)
    report['ledger_comparison'] = ledger_result
    save()
    need(ledger_result['status'] == 'PASS', 'NATIVE_LEDGER_COMPARISON_NOT_PASS')
    report['steps']['CATALOG-LEDGER'] = 'PASS_SOURCE_BOUND_NATIVE_SUBSET'
    save()
    comparison = tools['compare_native_catalog'].compare_manifest(manifest, native, bootstrap_grantor='postgres', bootstrap_superuser=True, public_schema_owner='pg_database_owner', public_acl_registration=recipe['full_acl'], ledger_registration=registration, ledger_evidence=ledger_evidence, expression_oracle_evidence=oracle_evidence, oracle_database=DB, root=ROOT)
    write_safe('catalog-comparison.json', comparison)
    report['catalog_comparison'] = comparison
    save()
    need(comparison['status'] == 'PASS', 'NATIVE_CATALOG_COMPARISON_NOT_PASS')
    report['qualified_native_snapshot_sha256'] = digest(native)
    report['steps']['CATALOG-COMPARE'] = 'PASS_SOURCE_BOUND_NATIVE_CATALOG_ONLY'
    event('NATIVE_CATALOG_REHEARSAL', 'PASS_SUBSET_ONLY')





# Restore-specific operations follow; no old operator is changed.

import builtins
import types
from pathlib import PureWindowsPath

PRIVILEGE_PACKET='review-output/privilege-ceiling-control-rehearsal'
PRIVILEGE_FIXTURES_SHA='4ebe8b6cd7b85ff5ad8dbb79d431bb7001cf16dea72e3920138be4b5f2855e68'
PRIVILEGE_CONTENT_SHA='643232e4d068892b49e49122b7ce3b909bd86caa9e770aa923d7df00def1ec32'
PRIVILEGE_COORDINATOR='scripts/sql-review/run-privilege-ceiling-control-rehearsal.py'
PRIVILEGE_COORDINATOR_SHA='80ca5e62a6a89891e73ecb7afc0e134c3c5b75ed81d0f3adc01ba7c718d03d3f'
PRIVILEGE_PEER='context/reconciliation/local-f0-operation-sources/privilege-ceiling-source-v1/reviews/privilege_ceiling_independent_root_source_review_20261119.json'
PRIVILEGE_PEER_SHA='41f6ad5a4abf7b6e7cc085d6ff545192fb4587272f7baa87dc7e18dd823e2f4a'
IMAGE_FILES={'scripts/sql-review/local_image_identity.py':'a0742d4f25271cc5c4b8bced19909415181a76fb9856948a3dffed28abb80604','scripts/sql-review/test_local_image_identity.py':'0edae319a544aaaa8ed112e2ec477fe7ac428b58a7970ca8cd0e33ff006abe93','scripts/sql-review/fixtures/postgres-17.11-approved-manifest.json':'996e9dc583ba9f0265a2c75547a9c95fb22c251e394749cab205a0a00e1856a1'}
IMAGE_PEER='context/reconciliation/local-f0-operation-sources/privilege-ceiling-owned-verdict-v3/reviews/image-proof-independent-source.json'
IMAGE_PEER_SHA='b628b6d98ad22ea7def4dd7a51264025c50bde116451ae516f3e52f55ba9542a'
OWNED_ARCHIVE='context/reconciliation/local-f0-operation-sources/privilege-ceiling-owned-verdict-v3'
OWNED_VALIDATION='context/reconciliation/local-f0-privilege-ceiling-owned-verdict-v3-source-validation.json'
EXTERNAL_FILES=('execute_local_f0_privilege_ceiling_verdict_v3_20261119.py','local_f0_privilege_ceiling_verdict_v3_operation_steps.py','prepare_local_f0_privilege_ceiling_verdict_v3_plan.py','check_local_f0_privilege_ceiling_verdict_v3_operation.py','pin_local_f0_privilege_ceiling_verdict_v3_plan_20261119.py')
HELPER_FILES=(PRIVILEGE_COORDINATOR,'scripts/sql-review/run-native-table-denials-v3.py','scripts/privilege_ceiling_control_protocol.py','scripts/sql-review/run-context-control-rehearsal.py','scripts/sql-review/run-first-rehearsal.py','scripts/sql-review/rehearsal-diagnostics.py','scripts/sql-review/run-local-f0-migrate.py','scripts/prepare-local-f0-history.py')
HELPERS={}

def inspect_owner(name,running=True):
    report['stage']='PRIVILEGE_CEILING_RESOURCE_RUNNING_INSPECTION'if running else'PRIVILEGE_CEILING_RESOURCE_PRESTART_INSPECTION'
    record={'phase':'RUNNING'if running else'PRESTART','comparisons':{},'mount_counts':{'data':0,'bootstrap':0,'tmpfs_api':0},'kernel_required':running is True,'confirmed':False}
    report.setdefault('resource_inspection_checks',[]).append(record);save()
    def check(key,condition,code):
        record['comparisons'][key]=condition is True;save();need(record['comparisons'][key],code)
    check('single_resource',name==TARGETS[0]['name']and type(running)is bool,'PRIVILEGE_CEILING_SINGLE_RESOURCE')
    value=inspect_container(name)
    check('container_shape',type(value)is dict and type(value.get('Config'))is dict and type(value.get('HostConfig'))is dict and type(value.get('State'))is dict and type(value.get('NetworkSettings'))is dict and type(value.get('Mounts'))is list,'PRIVILEGE_CEILING_CONTAINER_SHAPE')
    check('created_identity',value.get('Id')==created_containers[name]and value.get('Name')=='/'+name and owned(value['Config'].get('Labels')or{}),'PRIVILEGE_CEILING_CREATED_CONTAINER_IDENTITY')
    host=value['HostConfig'];required={'NetworkMode','PortBindings','Privileged','PidMode','IpcMode','Devices','CapAdd','Tmpfs','Links'}
    check('isolation',required<=set(host)and value['Config'].get('Image')==IMAGE and value.get('Image')==report['image']['image_id']and value.get('Platform')=='linux'and value['State'].get('Running')is running and host['NetworkMode']=='none'and host['PortBindings']in(None,{})and host['Privileged']is False and host['PidMode']==''and host['IpcMode']in('','private')and not host['Devices']and not host['CapAdd']and not host['Links'],'PRIVILEGE_CEILING_CONTAINER_ISOLATION')
    ports=value['NetworkSettings'].get('Ports')
    check('no_published_ports',ports is None or type(ports)is dict and all(item is None for item in ports.values()),'PRIVILEGE_CEILING_NO_PUBLISHED_PORTS')
    volume=TARGETS[0]['volume'];expected=str(PRIVATE/'ok-bootstrap-password');windows=PureWindowsPath(expected);desktop='/run/desktop/mnt/host/'+windows.drive[0].lower()+'/'+'/'.join(windows.parts[1:])
    mounts=value['Mounts'];check('bounded_mount_list',2<=len(mounts)<=3,'PRIVILEGE_CEILING_EXACT_MOUNT_SET')
    for mount in mounts:
        check('mount_row_shape',type(mount)is dict and {'Type','Destination','RW'}<=set(mount),'PRIVILEGE_CEILING_MOUNT_ROW_SHAPE')
        if mount['Type']=='volume':
            check('data_mount',mount.get('Name')==volume and mount['Destination']=='/var/lib/postgresql/data'and mount['RW']is True,'PRIVILEGE_CEILING_EXACT_DATA_MOUNT');record['mount_counts']['data']+=1
        elif mount['Type']=='bind':
            check('bootstrap_mount',mount.get('Source')in(expected,desktop)and mount['Destination']=='/run/bootstrap-password'and mount['RW']is False,'PRIVILEGE_CEILING_EXACT_BOOTSTRAP_BIND');record['mount_counts']['bootstrap']+=1
        elif mount['Type']=='tmpfs':
            check('optional_tmpfs_api_mount',mount['Destination']=='/run/wa-secrets'and mount['RW']is True,'PRIVILEGE_CEILING_EXACT_SECRET_TMPFS');record['mount_counts']['tmpfs_api']+=1
        else:check('known_mount_type',False,'PRIVILEGE_CEILING_EXTRA_MOUNT')
        save()
    counts=record['mount_counts'];check('logical_mount_set',counts['data']==1 and counts['bootstrap']==1 and counts['tmpfs_api']in(0,1),'PRIVILEGE_CEILING_EXACT_MOUNT_SET')
    check('host_tmpfs_key',type(host['Tmpfs'])is dict and set(host['Tmpfs'])=={'/run/wa-secrets'},'PRIVILEGE_CEILING_EXACT_TMPFS_CONFIGURATION')
    options=host['Tmpfs']['/run/wa-secrets'];tokens=options.split(',')if type(options)is str else[]
    check('exact_tmpfs_options',len(tokens)==5 and len(set(tokens))==5 and set(tokens)in({'rw','nosuid','noexec','nodev','mode=0700'},{'rw','nosuid','noexec','nodev','mode=700'}),'PRIVILEGE_CEILING_PRIVATE_TMPFS_OPTIONS')
    disk=inspect_volume(volume)
    check('volume_identity',type(disk)is dict and disk.get('Name')==volume and disk.get('CreatedAt')==created_volumes[volume]and owned(disk.get('Labels')or{})and disk.get('Driver')=='local'and not disk.get('Options')and disk.get('Scope')=='local','PRIVILEGE_CEILING_EXACT_VOLUME_IDENTITY')
    if running:verify_running_secret_tmpfs(name,value['Id'])
    record['confirmed']=True;save()
    event('PRIVILEGE_CEILING_RESOURCE_IDENTITY','PASS',target=name,actual_image_id=report['image']['image_id'],exact_mounts_and_private_namespaces=True)
    return value

def load_reviewed_helper(relative):
    need(relative in HELPER_FILES,'UNREGISTERED_PRIVILEGE_CEILING_HELPER')
    if relative in HELPERS:
        need(HELPERS[relative] is not None,'CYCLIC_PRIVILEGE_CEILING_HELPER');return HELPERS[relative]
    blobs={name:read_pinned(name) for name in HELPER_FILES}
    HELPERS[relative]=None
    ordinary=builtins.__import__
    def run_path(path,**options):
        need(not options,'PRIVILEGE_CEILING_HELPER_RUNPY_OPTIONS')
        actual=Path(path).resolve();need(actual.is_relative_to(ROOT),'PRIVILEGE_CEILING_HELPER_PATH')
        return load_reviewed_helper(actual.relative_to(ROOT).as_posix())
    def imported(name,globals=None,locals=None,fromlist=(),level=0):
        if name=='runpy' and level==0:return types.SimpleNamespace(run_path=run_path)
        return ordinary(name,globals,locals,fromlist,level)
    namespace={'__name__':'_verified_privilege_ceiling_helper','__file__':str(ROOT/relative),'__builtins__':{**vars(builtins),'__import__':imported}}
    output=io.StringIO()
    try:
        with contextlib.redirect_stdout(output),contextlib.redirect_stderr(output):exec(compile(blobs[relative],str(ROOT/relative),'exec'),namespace)
    except BaseException:raise Stop('PRIVILEGE_CEILING_HELPER_LOAD_REFUSED') from None
    need(not output.getvalue(),'PRIVILEGE_CEILING_HELPER_OUTPUT_REFUSED');HELPERS[relative]=namespace;return namespace

def source_authentication_preflight(name):
    with _RequiredSafetyBoundary('CLOSE', name, 'PRIVILEGE_CEILING_AUTHENTICATION_PREFLIGHT'):

        class AuthEvidence:
            value = report

            def stage(self, value):
                report['stage'] = value
                save()

            def save(self):
                save()
        report.setdefault('authentication', [])
        load_reviewed_helper('scripts/sql-review/run-first-rehearsal.py')['authentication_preflight'](AuthEvidence(), created_containers[name])


def admit_privilege_ceiling_sources():
    """The complete actual source inventory is read before first compile."""
    global PRIVILEGE_FIXTURES
    cfg=MANIFEST.get('privilege_ceiling')
    need(type(cfg)is dict and set(cfg)=={'fixtures_sha256','content_sha256','coordinator_sha256','external_files_sha256'},'PRIVILEGE_CEILING_CONFIGURATION_FIELDS')
    need(cfg['fixtures_sha256']==PRIVILEGE_FIXTURES_SHA and cfg['content_sha256']==PRIVILEGE_CONTENT_SHA and cfg['coordinator_sha256']==PRIVILEGE_COORDINATOR_SHA,'EXACT_PRIVILEGE_CEILING_PACKET')
    pins=MANIFEST.get('packet_files_sha256');need(type(pins)is dict and bool(pins)and all(type(v)is str and re.fullmatch('[0-9a-f]{64}',v)for v in pins.values()),'PRIVILEGE_CEILING_FULL_SOURCE_MAP_REQUIRED')
    external=cfg['external_files_sha256'];need(type(external)is dict and set(external)==set(EXTERNAL_FILES)and all(type(v)is str and re.fullmatch('[0-9a-f]{64}',v)for v in external.values()),'PRIVILEGE_CEILING_EXTERNAL_SOURCE_SET')
    fixed=set(HELPER_FILES)|set(IMAGE_FILES)|{PRIVILEGE_PEER,IMAGE_PEER,OWNED_VALIDATION,PRIVILEGE_PACKET+'/fixtures.json',GENERATOR,'review-output/native-catalog/source-pins.json','review-output/native-table-denials-v2/packet.json'}|{OWNED_ARCHIVE+'/'+n+'.txt'for n in EXTERNAL_FILES}
    need(fixed<=set(pins),'PRIVILEGE_CEILING_REQUIRED_SOURCE_MISSING')
    admitted={name:read_pinned(name)for name in pins}
    for name,wanted in IMAGE_FILES.items():need(hashlib.sha256(admitted[name]).hexdigest()==wanted,'IMAGE_PROOF_SOURCE_PACKET_REQUIRED')
    need(hashlib.sha256(admitted[IMAGE_PEER]).hexdigest()==IMAGE_PEER_SHA,'IMAGE_PROOF_INDEPENDENT_REVIEW_REQUIRED')
    for name,wanted in external.items():
        raw=(TASK/name).read_bytes();need(hashlib.sha256(raw).hexdigest()==wanted and raw==admitted[OWNED_ARCHIVE+'/'+name+'.txt'],'PRIVILEGE_CEILING_COMMITTED_EXTERNAL_SNAPSHOT_REQUIRED')
    owned=unique_json(admitted[OWNED_VALIDATION]);need(owned['schema']=='workinants.privilege-ceiling-owned-operator-source-validation.v1'and owned['operator_sources_sha256']==external,'PRIVILEGE_CEILING_OWNED_VALIDATION_BINDING')
    archive=owned['archive_files_sha256'];need(type(archive)is dict and all(n.startswith(OWNED_ARCHIVE+'/')and pins.get(n)==v for n,v in archive.items()),'PRIVILEGE_CEILING_OWNED_ARCHIVE_ADMISSION')
    actual={p.relative_to(ROOT).as_posix():hashlib.sha256(p.read_bytes()).hexdigest()for p in(ROOT/OWNED_ARCHIVE).rglob('*')if p.is_file()};need(actual==archive,'PRIVILEGE_CEILING_OWNED_ARCHIVE_TREE')
    raw=admitted[PRIVILEGE_PACKET+'/fixtures.json'];need(hashlib.sha256(raw).hexdigest()==PRIVILEGE_FIXTURES_SHA,'PRIVILEGE_CEILING_FIXTURE_DRIFT');fixtures=unique_json(raw)
    need(fixtures['schema']=='workinants.privilege-ceiling-fixtures.v1'and fixtures['status']=='NOT_RUN'and fixtures['database_posture']=='D'and len(fixtures['cases'])==200 and len(fixtures['source_definers'])==16 and len(fixtures['control_links'])==5 and len(fixtures['issuer_umbrella_links'])==40,'PRIVILEGE_CEILING_FINITE_SOURCE_SCOPE')
    need(digest({k:fixtures[k]for k in('source_files_sha256','prepared_files_sha256')})==PRIVILEGE_CONTENT_SHA and len(fixtures['prepared_files_sha256'])==200,'PRIVILEGE_CEILING_CONTENT_AGGREGATE')
    for n,v in fixtures['source_files_sha256'].items():need(pins.get(n)==v and n in admitted,'PRIVILEGE_CEILING_SOURCE_NOT_IN_PACKET')
    for n,v in fixtures['prepared_files_sha256'].items():need(pins.get(PRIVILEGE_PACKET+'/'+n)==v and PRIVILEGE_PACKET+'/'+n in admitted,'PRIVILEGE_CEILING_SQL_NOT_IN_PACKET')
    native_raw=admitted['review-output/native-table-denials-v2/packet.json'];need(hashlib.sha256(native_raw).hexdigest()=='8044d43f25c4a449f662bbb467183aac86d6a619836aae0988458098d59e0b69','PRIVILEGE_NATIVE_PACKET_BINDING')
    native=unique_json(native_raw);need(len(native['cases'])==40 and len(native['files_sha256'])==83,'PRIVILEGE_NATIVE_FINITE_SOURCE')
    for n,v in native['source_inputs_sha256'].items():need(pins.get(n)==v and n in admitted,'PRIVILEGE_NATIVE_INPUT_MISSING')
    native_blobs={}
    for n,v in native['files_sha256'].items():
        path='review-output/native-table-denials-v2/'+n;need(pins.get(path)==v and path in admitted,'PRIVILEGE_NATIVE_SQL_MISSING');native_blobs[n]=admitted[path]
    catalog=unique_json(admitted['review-output/native-catalog/source-pins.json']);need(type(catalog)is dict and len(catalog)==16 and all(pins.get(n)==v and n in admitted for n,v in catalog.items()),'PRIVILEGE_CEILING_CLOSED_CATALOG_IMPORTS_REQUIRED')
    need(hashlib.sha256(admitted[PRIVILEGE_COORDINATOR]).hexdigest()==PRIVILEGE_COORDINATOR_SHA and hashlib.sha256(admitted[PRIVILEGE_PEER]).hexdigest()==PRIVILEGE_PEER_SHA,'PRIVILEGE_CEILING_INDEPENDENT_SOURCE_REVIEW_REQUIRED')
    PRIVILEGE_FIXTURES=fixtures;PRIVILEGE_NATIVE.update(packet=native,blobs=native_blobs,preinstall_observed=False,postinstall_observed=False)
    return admitted

def verify_privilege_ceiling_packet():
    need(re.fullmatch('[0-9a-f]{40}',COMMIT)and re.fullmatch('[0-9a-f]{40}',TREE)and re.fullmatch('[0-9a-f]{64}',PACKET),'PRIVILEGE_CEILING_SOURCE_NOT_PINNED');need(uuid.UUID(RUN_ID).version==4,'PRIVILEGE_CEILING_FRESH_UUID4')
    admit_privilege_ceiling_sources();verify_catalog_packet()
    for name in HELPER_FILES:load_reviewed_helper(name)
    native=load_reviewed_helper('scripts/sql-review/run-native-table-denials-v3.py')
    need(hashlib.sha256(read_pinned('scripts/sql-review/run-native-table-denials-v3.py')).hexdigest()=='6e74115cc7a77e626c4379c5a5744efdede1257d04b206fc339e62a23fd49cd3'and all(n in MANIFEST['packet_files_sha256']for n in native['MODULES']),'PRIVILEGE_NATIVE_MODULE_GRAPH')
    PRIVILEGE_NATIVE['module']=native
    SAFE_FILES.update({'provider-preinstall-proof.json','privilege-ceiling-native-attestation.json','privilege-ceiling-run-plan.json','privilege-ceiling-component-result.json','privilege-ceiling-native-final.json'})
    report['steps']['PRIVILEGE-CEILING-REVIEW']='PASS_SOURCE_ADMISSION_ONLY';report['privilege_ceiling']={'selected_assertions':'NOT_RUN','whole_selected94_or451':'NOT_PROMOTED','owner_api_policy_qualified':False};save()


PROVIDER_ROLES=('anon','authenticated','service_role')
PRIVILEGE_NATIVE={}
def provider_observation(name,stage):
    roles="'anon','authenticated','service_role'"
    query="SELECT jsonb_build_object('roles',(SELECT jsonb_agg(jsonb_build_object('name',rolname,'login',rolcanlogin,'inherit',rolinherit,'superuser',rolsuper,'createdb',rolcreatedb,'createrole',rolcreaterole,'replication',rolreplication,'bypassrls',rolbypassrls,'memberships',(SELECT count(*) FROM pg_auth_members m WHERE m.member=r.oid OR m.roleid=r.oid),'connect',has_database_privilege(rolname,current_database(),'CONNECT'),'create',has_database_privilege(rolname,current_database(),'CREATE'),'temp',has_database_privilege(rolname,current_database(),'TEMP')) ORDER BY rolname) FROM pg_roles r WHERE rolname IN ("+roles+")),'explicit_usage',(SELECT count(*) FROM pg_namespace n CROSS JOIN LATERAL aclexplode(n.nspacl) a WHERE n.nspname IN ('app','platform','platform_private') AND a.grantee IN (SELECT oid FROM pg_roles WHERE rolname IN ("+roles+")) AND a.privilege_type='USAGE'),'effective_usage',(SELECT count(*) FROM (VALUES('anon'),('authenticated'),('service_role')) r(role) CROSS JOIN (VALUES('app'),('platform'),('platform_private')) n(schema) WHERE has_schema_privilege(r.role,n.schema,'USAGE')));"
    result=run_catalog_query(name,query,stage);successful_query(result);rows=records(result.stdout)
    need(len(rows)==1 and type(rows[0]) is dict and set(rows[0])=={'roles','explicit_usage','effective_usage'},'PROVIDER_OBSERVATION_FIELDS')
    value=rows[0];flags=sorted(PRIVILEGE_NATIVE['module']['provider_flags'](),key=lambda row:row['name'])
    exact(value['roles'],flags,'PROVIDER_FLAGS_DIFFERENT')
    for key in ('explicit_usage','effective_usage'):need(type(value[key]) is int and 0<=value[key]<=9,'PROVIDER_USAGE_COUNT')
    safe={'stage':stage,'roles':flags,'explicit_usage':value['explicit_usage'],'effective_usage':value['effective_usage']}
    report.setdefault('provider_observations',[]).append(safe);save();return value

def provider_authentication(name):
    with _RequiredSafetyBoundary('CLOSE',name,'PROVIDER_AUTHENTICATION'):
        for role in PROVIDER_ROLES:
            result=command(psql_args(name,role),"SELECT jsonb_build_object('login',session_user,'auth',system_user,'database',current_database(),'client',host(inet_client_addr()),'server',host(inet_server_addr()));")
            need(type(result.returncode) is int and result.returncode==0 and not result.stderr.strip(),'PROVIDER_CORRECT_PASSWORD_REQUIRED')
            rows=records(result.stdout)
            expected={'login':role,'auth':'scram-sha-256:'+role,'database':DB,'client':'127.0.0.1','server':'127.0.0.1'}
            need(len(rows)==1 and canonical(rows[0])==canonical(expected),'PROVIDER_AUTH_IDENTITY')
            # This random wrong-password control is not an actual credential.
            environment=os.environ.copy();environment['PGPASSWORD']=secrets.token_hex(32)
            args=psql_args(name,role);slot=args.index('PGPASSFILE=/run/wa-secrets/pgpass');args[slot]='PGPASSFILE=/dev/null';args[slot+1:slot+1]=['-e','PGPASSWORD']
            wrong=subprocess.run(args,input='SELECT 1;\n',capture_output=True,text=True,encoding='utf8',errors='strict',env=environment,timeout=30,cwd=ROOT)
            text=wrong.stderr.replace('\r\n','\n')
            pattern=r'(?:psql: error: connection to server at "127\.0\.0\.1", port 5432 failed: )?FATAL:\s+password authentication failed for user "'+role+r'"\n?'
            good=type(wrong.returncode) is int and wrong.returncode==2 and wrong.stdout=='' and re.fullmatch(pattern,text) is not None
            report.setdefault('provider_authentication',[]).append({'role':role,'correct_password':'PASS_SCRAM','wrong_password_rejected':good,'wrong_password_exit_code':wrong.returncode});save()
            need(good,'PROVIDER_WRONG_PASSWORD_CONTROL_REQUIRED')

def provider_preinstall():
    name=TARGETS[0]['name']
    with _RequiredSafetyBoundary('CLOSE',name,'PROVIDER_PREINSTALL'):
        name=TARGETS[0]['name'];report['stage']='NATIVE_PROVIDER_PREINSTALL';save()
        roles="'anon','authenticated','service_role'"
        absent=observe(name,'SELECT jsonb_build_object(\'roles\',(SELECT count(*) FROM pg_roles WHERE rolname IN ('+roles+')));','PROVIDER_ROLE_ABSENCE')
        exact(absent,{'roles':0},'FRESH_PROVIDER_ROLES_REQUIRED')
        text=PRIVILEGE_NATIVE['blobs']['provider-role-simulation-before-migrate.sql'].decode('utf8')
        result=run_catalog_query(name,text,'PROVIDER_ROLE_SIMULATION');successful_query(result);need(not result.stdout.strip(),'PROVIDER_SETUP_UNEXPECTED_OUTPUT')
        for role in PROVIDER_ROLES:
            password=secrets.token_hex(32);passwords[name][role]=password;all_secrets.append(password)
        statement='REVOKE CONNECT,CREATE,TEMP ON DATABASE '+DB+' FROM '+','.join(PROVIDER_ROLES)+';\nGRANT CONNECT ON DATABASE '+DB+' TO '+','.join(PROVIDER_ROLES)+';\n'
        statement+='\n'.join('ALTER ROLE '+role+" PASSWORD '"+passwords[name][role]+"';" for role in PROVIDER_ROLES)
        result=run_catalog_query(name,statement,'PROVIDER_PRIVATE_SCRAM_PROVISION');successful_query(result);need(not result.stdout.strip(),'PROVIDER_CREDENTIAL_OUTPUT')
        need(len(set(passwords[name].values()))==9,'NINE_INDEPENDENT_CREDENTIALS_REQUIRED')
        pgpass=''.join('127.0.0.1:5432:'+DB+':'+role+':'+passwords[name][role]+'\n' for role in (*ROLES,*PROVIDER_ROLES))
        result=docker(['exec','-i',created_containers[name],'sh','-ceu','umask 077; cat > /run/wa-secrets/pgpass; chmod 600 /run/wa-secrets/pgpass; stat -c "%a:%u:%g" /run/wa-secrets/pgpass'],input=pgpass)
        need(result.returncode==0 and result.stdout.strip()=='600:0:0','PROVIDER_PGPASS_OWNER_MODE')
        value=provider_observation(name,'PROVIDER_BEFORE_CANONICAL_INSTALL');exact({k:value[k] for k in ('explicit_usage','effective_usage')},{'explicit_usage':9,'effective_usage':9},'ALL_NINE_PREINSTALL_SENTINELS_REQUIRED')
        provider_authentication(name);PRIVILEGE_NATIVE['preinstall_observed']=True
        report['steps']['NATIVE-PROVIDER-PREINSTALL']='PASS_LOCAL_SIMULATION_ONLY';save()

def provider_postinstall(name,installed):
    with _RequiredSafetyBoundary('CLOSE',name,'PROVIDER_POSTINSTALL'):
        need(PRIVILEGE_NATIVE.get('preinstall_observed') is True,'PROVIDER_PREINSTALL_NOT_OBSERVED')
        need(name in finalized and report['targets'][name].get('finalization')=='PASS','PROVIDER_ORIGINAL_GRANTOR_NOT_FINALIZED')
        value=provider_observation(name,'PROVIDER_AFTER_CANONICAL_INSTALL');exact({k:value[k] for k in ('explicit_usage','effective_usage')},{'explicit_usage':0,'effective_usage':0},'CANONICAL_PROVIDER_REVOKES_REQUIRED')
        need(installed['status']=='CLI_COMPLETED_REQUIRES_INDEPENDENT_LEDGER_CATALOG_CHECKS' and type(installed['exit_code']) is int and installed['exit_code']==0,'PROVIDER_GENUINE_INSTALL_REQUIRED')
        PRIVILEGE_NATIVE['postinstall_observed']=True
        report['steps']['NATIVE-PROVIDER-POSTINSTALL']='PASS_NINE_SOURCE_REVOKES_OBSERVED';save()


def privilege_ceiling_experiment():
    name=TARGETS[0]['name'];inspect_owner(name);need(name in finalized,'PRIVILEGE_CEILING_ORIGINAL_GRANTOR_FINALIZATION_REQUIRED');closed_backends(name,'PRIVILEGE_CEILING_PRE_COMPONENT')
    counts=report['catalog_comparison']['check_counts']
    need(report['catalog_comparison']['status']=='PASS'and type(counts)is dict and set(counts)=={'PASS'}and type(counts['PASS'])is int and counts['PASS']==29089 and report['ledger_comparison']['status']=='PASS'and len(report['ledger_comparison']['checks'])==22 and all(r['status']=='PASS'for r in report['ledger_comparison']['checks'])and report['steps']['CATALOG-ORACLE']=='PASS_ROLLBACK_OBSERVED_NOT_WHOLE_CASE','PRIVILEGE_CEILING_FULL_NATIVE_ORACLE_LEDGER_PASS_REQUIRED')
    need(PRIVILEGE_NATIVE.get('preinstall_observed')is True and PRIVILEGE_NATIVE.get('postinstall_observed')is True,'PRIVILEGE_CEILING_PROVIDER_SEQUENCE_PROOF_REQUIRED')
    native=PRIVILEGE_NATIVE['module'];native_packet_sha='8044d43f25c4a449f662bbb467183aac86d6a619836aae0988458098d59e0b69'
    provider={'schema':'workinants.native-deny-provider-preinstall.v1','run_id':RUN_ID,'container_id':created_containers[name],'source_commit':COMMIT,'source_tree':TREE,'packet_sha256':native_packet_sha,'application_sql_sha256':APPLICATION_SHA,'roles':native['provider_flags'](),'all_nine_schema_usage_sentinels_before_install':True,'canonical_install_removed_all_nine':True,'genuine_prisma_one_applied_migration':True,'original_grantor_finalized':True,'local_simulation_only':True,'hosted_parity_claimed':False};proof_ref=write_safe('provider-preinstall-proof.json',provider)
    nested={'schema':'workinants.native-deny-run.v1','scope':'FINITE_NATIVE_DENIAL_FACETS_ONLY','run_id':RUN_ID,'source_commit':COMMIT,'source_tree':TREE,'packet_sha256':native_packet_sha,'source_modules_sha256':{p:MANIFEST['packet_files_sha256'][p]for p in native['MODULES']},'target_manifest':unique_json(read_target_manifest(MANIFEST['migration_targets']['ok'])),'immutable_container_id':created_containers[name],'native_snapshot':{'path':str(OUT/'native-before.json'),'sha256':hashlib.sha256((OUT/'native-before.json').read_bytes()).hexdigest()},'native_comparison':{'path':str(OUT/'catalog-comparison.json'),'sha256':hashlib.sha256((OUT/'catalog-comparison.json').read_bytes()).hexdigest()},'provider_preinstall_proof':{'path':str(OUT/'provider-preinstall-proof.json'),'sha256':proof_ref['artifact_sha256']},'selected_case_ids':PRIVILEGE_NATIVE['packet']['selected_case_ids']}
    attestation={'schema':'workinants.privilege-ceiling-native-attestation.v1','run_id':RUN_ID,'container_id':created_containers[name],'source_commit':COMMIT,'source_tree':TREE,'operation_packet_sha256':PACKET,'native_sql_packet_sha256':native_packet_sha,'application_sql_sha256':APPLICATION_SHA,'source_expected_sha256':EXPECTED_SHA,'native_snapshot_sha256':report['qualified_native_snapshot_sha256'],'native_comparison_file_sha256':nested['native_comparison']['sha256'],'genuine_prisma_one_applied_migration':True,'original_grantor_finalized':True,'native_expression_oracle_and_private_ledger_pass':True,'all_other_client_backends_absent':True,'provider_preinstall_source_proven':True,'posture':'D','whole_case_promotion':False};attestation_ref=write_safe('privilege-ceiling-native-attestation.json',attestation)
    plan={'schema':'workinants.privilege-ceiling-run.v1','scope':'FINITE_EXISTING_PRIVILEGE_CEILINGS_ONLY','run_id':RUN_ID,'source_commit':COMMIT,'source_tree':TREE,'packet_sha256':PACKET,'packet_files_sha256':MANIFEST['packet_files_sha256'],'fixtures_sha256':PRIVILEGE_FIXTURES_SHA,'content_sha256':PRIVILEGE_CONTENT_SHA,'native_plan':nested,'prerequisite_attestation':{'path':str(OUT/'privilege-ceiling-native-attestation.json'),'sha256':attestation_ref['artifact_sha256']}}
    write_safe('privilege-ceiling-run-plan.json',plan);plan_raw=(OUT/'privilege-ceiling-run-plan.json').read_bytes();module=load_reviewed_helper(PRIVILEGE_COORDINATOR);failure=None;raw=None;exit_code=None
    report['privilege_ceiling'].update(component_closure_attempted=False,component_closure_confirmed=False)
    try:
        try:
            exit_code=module['main'](['--execute-reviewed-privilege-ceilings','--run-plan',str(OUT/'privilege-ceiling-run-plan.json'),'--evidence-directory',str(OUT/'privilege-ceiling-component')])
            report['privilege_ceiling']['component_exit_code']=exit_code if type(exit_code)is int and 0<=exit_code<=255 else None
            if type(exit_code)is not int or exit_code!=0:
                failure=Stop('PRIVILEGE_CEILING_COMPONENT_NOT_QUALIFIED');remember_failure('PRIVILEGE_CEILING_COMPONENT',failure.code)
        except BaseException:
            failure=Stop('PRIVILEGE_CEILING_COMPONENT_UNEXPECTED_STOP_EVIDENCE_RETAINED');remember_failure('PRIVILEGE_CEILING_COMPONENT',failure.code)
        finally:
            fixed=OUT/'privilege-ceiling-component/privilege-ceiling-results.json';reference={'artifact':'privilege-ceiling-component/privilege-ceiling-results.json','present':None,'read_status':'UNAVAILABLE'};report['privilege_ceiling']['component_report_reference']=reference
            try:
                import stat
                try:metadata=fixed.lstat()
                except FileNotFoundError:reference.update(present=False,read_status='ABSENT');raise Stop('PRIVILEGE_CEILING_COMPONENT_REFERENCE_ABSENT')from None
                reference['present']=True;size=metadata.st_size;limit=16*1024*1024
                need(type(metadata.st_mode)is int and stat.S_ISREG(metadata.st_mode)and type(size)is int and size>=0,'PRIVILEGE_CEILING_COMPONENT_REFERENCE_SHAPE')
                if size>limit:reference['read_status']='OVERSIZED';raise Stop('PRIVILEGE_CEILING_COMPONENT_REFERENCE_LIMIT')
                with fixed.open('rb')as stream:raw=stream.read(limit+1)
                need(type(raw)is bytes,'PRIVILEGE_CEILING_COMPONENT_REFERENCE_SHAPE')
                if len(raw)>limit:reference['read_status']='OVERSIZED';raise Stop('PRIVILEGE_CEILING_COMPONENT_REFERENCE_LIMIT')
                reference.update(read_status='RETAINED',artifact_sha256=hashlib.sha256(raw).hexdigest(),bytes=len(raw))
            except BaseException:
                remember_failure('PRIVILEGE_CEILING_COMPONENT_REFERENCE','PRIVILEGE_CEILING_COMPONENT_REFERENCE_UNCONFIRMED')
                if failure is None:failure=Stop('PRIVILEGE_CEILING_COMPONENT_REFERENCE_UNCONFIRMED')
    finally:
        report['privilege_ceiling']['component_closure_attempted']=True
        try:closed_backends(name,'PRIVILEGE_CEILING_POST_COMPONENT');report['privilege_ceiling']['component_closure_confirmed']=True
        except BaseException:
            remember_failure('PRIVILEGE_CEILING_COMPONENT_CLOSURE','PRIVILEGE_CEILING_COMPONENT_GLOBAL_CLOSURE_UNCONFIRMED')
            if failure is None:failure=Stop('PRIVILEGE_CEILING_COMPONENT_GLOBAL_CLOSURE_UNCONFIRMED')
        finally:
            if not persist_best_effort('PRIVILEGE_CEILING_COMPONENT_FINALLY')and failure is None:failure=Stop('PRIVILEGE_CEILING_COMPONENT_EVIDENCE_UNCONFIRMED')
    if failure is not None:raise failure
    need(type(exit_code)is int and exit_code==0,'PRIVILEGE_CEILING_COMPONENT_NOT_QUALIFIED');value=unique_json(raw);summary=verify_privilege_result(value,plan,plan_raw)
    write_safe('privilege-ceiling-component-result.json',summary);report['privilege_ceiling']['component_report_sha256']=summary['component_report_sha256'];save()
    after=collect_native(name,'PRIVILEGE_CEILING_FINAL_NATIVE','privilege-ceiling-native-final.json');need(digest(after)==report['qualified_native_snapshot_sha256'],'PRIVILEGE_CEILING_NATIVE_CHANGED')
    report['steps']['PRIVILEGE-CEILING-COMPONENT']='PASS_FINITE_PREPARED_SQL_ONLY';report['privilege_ceiling'].update(completed_negative_contrasts=200,definer_metadata=16,native_validity_controls=40,issuer_protocols=3,selected_assertions='NOT_PROMOTED_PENDING_EVIDENCE_REVIEW');save()

def verify_external_input_preservation():
    complete=True
    try:need(hashlib.sha256(Path(MANIFEST['tool_archive']).read_bytes()).hexdigest()==MANIFEST['tool_archive_sha256'],'PRIVILEGE_CEILING_TOOL_ARCHIVE_POSTRUN_DRIFT')
    except BaseException:complete=False
    for plan in MANIFEST['migration_targets'].values():
        try:read_target_manifest(plan)
        except BaseException:complete=False
        try:need(hashlib.sha256(Path(plan['source_archive']).read_bytes()).hexdigest()==plan['source_archive_sha256'],'PRIVILEGE_CEILING_SOURCE_ARCHIVE_POSTRUN_DRIFT')
        except BaseException:complete=False
        try:
            source=Path(plan['source_snapshot']);current={path.relative_to(source).as_posix():hashlib.sha256(path.read_bytes()).hexdigest() for path in source.rglob('*') if path.is_file()};need(current==plan['source_files_sha256'],'PRIVILEGE_CEILING_SOURCE_SNAPSHOT_POSTRUN_DRIFT')
        except BaseException:complete=False
    need(complete,'PRIVILEGE_CEILING_EXTERNAL_INPUT_PRESERVATION_UNCONFIRMED')

def main():
    need(MANIFEST['review_status']=='APPROVED_LOCAL_F0_PRIVILEGE_CEILING_ATTEMPT','PRIVILEGE_CEILING_EXACT_OPERATION_NOT_REVIEWED');need(not OUT.exists(),'PRIVILEGE_CEILING_FRESH_EVIDENCE_DIRECTORY');OUT.mkdir(exist_ok=False)
    report.setdefault('evidence_complete',True);report.setdefault('persistence_failure',False);report.setdefault('output_complete',True)
    try:
        need(persist_best_effort('INITIAL_EVIDENCE'),'INITIAL_EVIDENCE_UNAVAILABLE')
        verify_privilege_ceiling_packet();preflight();ensure_image();create_resources();bootstrap_all();provision_migration_tools();provider_preinstall();catalog_experiment();privilege_ceiling_experiment();report['status']='PASS_LOCAL_PRIVILEGE_CEILING_SQL_SUBSET_ONLY'
    except BaseException as error:
        stage=error.stage if isinstance(error,Stop) else report['stage']
        code=error.code if isinstance(error,Stop) else 'TIMEOUT_CLOSURE_UNCONFIRMED' if isinstance(error,subprocess.TimeoutExpired) else 'INTERRUPTED' if isinstance(error,KeyboardInterrupt) else 'UNEXPECTED_PRIVILEGE_CEILING_WRAPPER_FAILURE'
        remember_failure(stage,code)
        event_best_effort('STOP','NO_LATER_STEPS',failure={'stage':stage,'code':code})
    finally:
        for name in sorted(bootstrap_attempted-finalization_attempted):
            try:finalize(name)
            except BaseException:
                remember_failure('FINALLY_FINALIZATION','FINALIZATION_UNCONFIRMED');persist_best_effort('FINALIZATION_FAILURE_RECORD')
        try:secret_scan()
        except BaseException:
            remember_failure('SANITIZATION','SECRET_SCAN_UNCONFIRMED');persist_best_effort('SANITIZATION_FAILURE_RECORD')
        try:
            cleanup();need(report.get('cleanup_actions_confirmed') is True,'CLEANUP_ACTIONS_UNCONFIRMED')
        except BaseException:
            remember_failure('CLEANUP','CLEANUP_UNCONFIRMED');persist_best_effort('CLEANUP_FAILURE_RECORD')
        # Every preservation family is independently attempted even after an
        # earlier read, archive check, finalizer or evidence writer failed.
        checks=(
          ('packet_unchanged_after_run',lambda:bool(report.get('source_verification',{}).get('files_sha256')) and all(hashlib.sha256((ROOT/path).read_bytes()).hexdigest()==wanted for path,wanted in report['source_verification']['files_sha256'].items())),
          ('tool_source_data_unchanged_after_run',lambda:(verify_tool_data(),True)[1]),
          ('external_sources_unchanged_after_run',lambda:all(hashlib.sha256((TASK/path).read_bytes()).hexdigest()==wanted for path,wanted in MANIFEST['privilege_ceiling']['external_files_sha256'].items())),
          ('external_inputs_unchanged_after_run',lambda:(verify_external_input_preservation(),True)[1]))
        for flag,check in checks:
            try:report[flag]=check() is True
            except BaseException:report[flag]=False
            if report[flag] is not True:remember_failure('SOURCE_PRESERVATION','SOURCE_OR_ARCHIVE_DRIFT_OR_UNVERIFIED')
            persist_best_effort('SOURCE_PRESERVATION_RECORD')
        if report['unexpected'] or report['evidence_complete'] is not True or report['output_complete'] is not True:
            report['status']='STOPPED_ATTEMPT_PRESERVED';report.pop('qualified_native_snapshot_sha256',None)
        report['finished_at']=datetime.datetime.now(datetime.timezone.utc).isoformat()
        persist_best_effort('FINAL_EVIDENCE')
        emit_best_effort({'status':report['status'],'evidence_complete':report['evidence_complete'],'cleanup_actions_confirmed':report.get('cleanup_actions_confirmed') is True,'unexpected_count':len(report['unexpected'])})
    return 0 if report['status']=='PASS_LOCAL_PRIVILEGE_CEILING_SQL_SUBSET_ONLY' and not report['unexpected'] and report['evidence_complete'] is True and report['output_complete'] is True else 1

def verify_privilege_result(value,plan,raw):
    allowed={'schema','status','database_posture','current_stage','current_case','current','operations','results','authentication','native_controls','facets','selected_cases','selected_controls','source_assertion_links','cleanup_required','subsequent_cases_stopped','evidence_complete','limits','run_id','source_commit','source_tree','operation_packet_sha256','reviewed_privilege_content_sha256','run_plan_sha256','source_packet_unchanged_after','definer_metadata','role_metadata','issuer_protocols','global_client_boundaries','provider_roles','effective_hba_selections','current_auth_role','authentication_comparison','fingerprint_order_control','fingerprint_order_comparisons','resource','authentication_comparisons','failure'}
    need(type(value)is dict and set(value)<=allowed,'PRIVILEGE_CEILING_COMPONENT_RESULT_FIELDS')
    expected={'schema':'workinants.privilege-ceiling-evidence.v1','run_id':RUN_ID,'source_commit':COMMIT,'source_tree':TREE,'operation_packet_sha256':PACKET,'reviewed_privilege_content_sha256':PRIVILEGE_CONTENT_SHA,'run_plan_sha256':hashlib.sha256(raw).hexdigest(),'database_posture':'D'}
    exact({k:value.get(k)for k in expected},expected,'PRIVILEGE_CEILING_COMPONENT_EXACT_SOURCE_RUN_CID_PLAN')
    need(value.get('status')=='PASS_PREPARED_PRIVILEGE_CEILINGS_ONLY_CASES_NOT_RUN'and value.get('evidence_complete')is True and value.get('source_packet_unchanged_after')is True and value.get('subsequent_cases_stopped')is False and value.get('facets')==[],'PRIVILEGE_CEILING_COMPONENT_NOT_QUALIFIED')
    cases={row['name']:row for row in PRIVILEGE_FIXTURES['cases']};results=value.get('results');need(type(results)is list and len(results)==200 and len({r.get('name')for r in results if type(r)is dict})==200,'PRIVILEGE_CEILING_EXACT200_RESULT_SET')
    for row in results:
        need(type(row)is dict and set(row)=={'name','source_case_id','assertion_id','status','closed_before_observers','complete_state_unchanged','diagnostic','whole_case_promoted'}and row['name']in cases,'PRIVILEGE_CEILING_FINITE_RESULT_FIELDS');case=cases[row['name']]
        exact({k:row[k]for k in('source_case_id','assertion_id')},{k:case[k]for k in('source_case_id','assertion_id')},'PRIVILEGE_CEILING_ASSERTION_LINK')
        need(privilege_diagnostic_allowed(row['diagnostic'],case['diagnostic']),'PRIVILEGE_CEILING_EXACT_DIAGNOSTIC_REQUIRED')
        need(row['status']=='PASS_FINITE_PRIVILEGE_CONTRAST_ONLY'and row['closed_before_observers']is True and row['complete_state_unchanged']is True and row['whole_case_promoted']is False,'PRIVILEGE_CEILING_FINITE_RESULT_CONTRACT')
    definitions=value.get('definer_metadata');need(type(definitions)is list and len(definitions)==16 and {r.get('function')for r in definitions if type(r)is dict}=={r['identity']for r in PRIVILEGE_FIXTURES['source_definers']}and all(type(r)is dict and set(r)=={'function','owner_body_definer_path_match'}and r['owner_body_definer_path_match']is True for r in definitions),'PRIVILEGE_CEILING_EXACT16_DEFINERS')
    controls=value.get('native_controls');need(type(controls)is list and len(controls)==40 and {r.get('case_id')for r in controls if type(r)is dict}=={r['id']for r in PRIVILEGE_NATIVE['packet']['cases']}and all(type(r)is dict and set(r)=={'case_id','status','rolled_back','all100_guards_restored','native205_unchanged'}and r['status']=='NATIVE_FIXTURE_VALIDITY_ONLY_NO_OWNER_OR_CASE_QUALIFICATION'and all(r[k]is True for k in('rolled_back','all100_guards_restored','native205_unchanged'))for r in controls),'PRIVILEGE_CEILING_EXACT40_VALIDITY')
    protocols=value.get('issuer_protocols');wanted=['ISSUER-LEGITIMATE-PERSON-ISSUE-OWN-READ-BOUND-SCALARS','ISSUER-LEGITIMATE-FIRST-ONE-WAY-REVOKE','ISSUER-STORED-SERVICE-GRANT-CANNOT-SELF-ATTEST-REVOKED-IDENTITY']
    need(type(protocols)is list and len(protocols)==3 and [r.get('name')for r in protocols if type(r)is dict]==wanted and all(type(r)is dict and set(r)=={'name','status','same_run_and_actual_logins','all_operation_backends_closed_before_observation','complete_state_verified','whole_case_promoted'}and r['status']=='PASS_FINITE_ISSUER_PROTOCOL_ONLY'and all(r[k]is True for k in('same_run_and_actual_logins','all_operation_backends_closed_before_observation','complete_state_verified'))and r['whole_case_promoted']is False for r in protocols),'PRIVILEGE_CEILING_EXACT3_ISSUER_PROTOCOLS')
    operations=value.get('operations');operation_names=set(cases)|{'native-fact-setup'}|{'native-control-'+r['model']for r in PRIVILEGE_NATIVE['packet']['cases']}|set(wanted)
    need(type(operations)is list and len(operations)==244 and len(operation_names)==244 and {r.get('name')for r in operations if type(r)is dict}==operation_names and all(type(r)is dict and r.get('closed_before_observers')is True for r in operations),'PRIVILEGE_CEILING_COMPLETE_OPERATION_CLOSURE')
    boundaries=value.get('global_client_boundaries');need(type(boundaries)is list and boundaries and all(type(r)is dict and set(r)=={'stage','attempted','confirmed'}and type(r['stage'])is str and r['attempted']is True and r['confirmed']is True for r in boundaries),'PRIVILEGE_CEILING_GLOBAL_CLIENT_BOUNDARIES')
    auth=value.get('authentication');roles=set(PRIVILEGE_NATIVE['module']['AUTH_ROLES'])
    need(type(auth)is list and len(auth)==9 and {r.get('role')for r in auth if type(r)is dict}==roles and all(type(r)is dict and set(r)=={'role','correct_password','wrong_password_rejected','wrong_password_exit_code'}and r['correct_password']=='PASS_SCRAM'and r['wrong_password_rejected']is True and type(r['wrong_password_exit_code'])is int and r['wrong_password_exit_code']==2 for r in auth),'PRIVILEGE_CEILING_NINE_AUTH_CONTROLS')
    exact(value.get('selected_controls'),PRIVILEGE_FIXTURES['control_links'],'PRIVILEGE_CEILING_SOURCE_CONTROLS_NOT_PROMOTED')
    exact(value.get('selected_cases'),[{'id':r['id'],'status':'NOT_RUN','source_vectors_status':'NOT_RUN','allow_case_status':'NOT_RUN'}for r in PRIVILEGE_NATIVE['packet']['cases']],'PRIVILEGE_CEILING_NATIVE_CASE_PROMOTION_FORBIDDEN')
    return {'schema':'workinants.privilege-ceiling-component-summary.v1','status':value['status'],'completed_negative_contrasts':200,'definer_metadata':16,'native_validity_controls':40,'issuer_protocols':3,'component_report_sha256':digest(value),'selected_assertions':'NOT_PROMOTED_PENDING_EVIDENCE_REVIEW'}


PRIVILEGE_SECRET_TMPFS_TOKEN='WA_PRIVILEGE_SECRET_TMPFS_V2_OK'

PRIVILEGE_SECRET_TMPFS_SCRIPT=r'''set -f
export LC_ALL=C
count=0
while IFS=' ' read -r source target filesystem options dump pass extra; do
  [ "$target" = /run/wa-secrets ] || continue
  count=$((count+1))
  [ -n "$source" ] && [ "$filesystem" = tmpfs ] && [ -z "$extra" ] || exit 21
  case "$options" in ''|,*|*,|*,,*) exit 22;; esac
  seen_rw=0; seen_noexec=0; seen_nosuid=0; seen_nodev=0
  saved_ifs=$IFS; IFS=,; set -- $options; IFS=$saved_ifs
  for option do
    case "$option" in
      rw) seen_rw=$((seen_rw+1));;
      noexec) seen_noexec=$((seen_noexec+1));;
      nosuid) seen_nosuid=$((seen_nosuid+1));;
      nodev) seen_nodev=$((seen_nodev+1));;
      ro|exec|suid|dev) exit 23;;
    esac
  done
  [ "$seen_rw" -eq 1 ] && [ "$seen_noexec" -eq 1 ] && [ "$seen_nosuid" -eq 1 ] && [ "$seen_nodev" -eq 1 ] || exit 24
done < /proc/mounts
[ "$count" -eq 1 ] || exit 25
[ "$(stat -c '%F:%a:%u:%g' -- /run/wa-secrets)" = 'directory:700:0:0' ] || exit 26
printf '%s\n' 'WA_PRIVILEGE_SECRET_TMPFS_V2_OK'
'''

def verify_running_secret_tmpfs(name,identity):
    report['stage']='PRIVILEGE_CEILING_RUNNING_SECRET_TMPFS'
    record={'phase':'RUNNING_KERNEL_TMPFS','owned_identity':False,'attempted':False,'command_returned':False,'integer_exit_zero':False,'fixed_token':False,'stderr_empty':False,'confirmed':False}
    report.setdefault('resource_kernel_checks',[]).append(record);save()
    record['owned_identity']=name in RESOURCE_CONTAINERS and name in created_containers and created_containers[name]==identity and type(identity)is str and re.fullmatch('[0-9a-f]{64}',identity)is not None
    save();need(record['owned_identity'],'PRIVILEGE_CEILING_TMPFS_OWNED_CID_REQUIRED')
    record['attempted']=True;save()
    try:
        result=docker(['exec','-i',identity,'sh','-ceu',PRIVILEGE_SECRET_TMPFS_SCRIPT],timeout=30)
        code=getattr(result,'returncode',None);stdout=getattr(result,'stdout',None);stderr=getattr(result,'stderr',None)
        record.update(command_returned=True,integer_exit_zero=type(code)is int and code==0,fixed_token=type(stdout)is str and stdout==PRIVILEGE_SECRET_TMPFS_TOKEN+'\n',stderr_empty=type(stderr)is str and stderr=='')
        record['confirmed']=all(record[key]is True for key in('owned_identity','attempted','command_returned','integer_exit_zero','fixed_token','stderr_empty'))
    except BaseException:
        record['confirmed']=False
    finally:save()
    need(record['confirmed'],'PRIVILEGE_CEILING_SECRET_TMPFS_KERNEL_UNCONFIRMED')

def privilege_diagnostic_allowed(value,contract):
    """Admit only the frozen case's bounded diagnostic projection."""
    fields={'matched','sqlstate','kind','gate','object','source_position_verified','source_frame_verified','selected_column_or_verb_isolation_claimed'}
    shapes={'IMMUTABLE_GRANT':{'kind','application_sha256','body_line','body_sha256'},'SET_ROLE':{'kind','target_role'},'SCHEMA_CREATE':{'kind','schema'},'FUNCTION':{'kind','schema','function'},'NATIVE_ACL':{'kind','schema','relation'}}
    if type(value)is not dict or set(value)!=fields or type(contract)is not dict:return False
    kind=contract.get('kind')
    if type(kind)is not str or kind not in shapes or set(contract)!=shapes[kind]:return False
    if value['matched']is not True or value['kind']!=kind or value['selected_column_or_verb_isolation_claimed']is not False:return False
    if type(value['source_position_verified'])is not bool or type(value['source_frame_verified'])is not bool:return False
    if type(value['object'])is not str or not(value['gate']is None or type(value['gate'])is str):return False
    if kind=='IMMUTABLE_GRANT':
        return value['sqlstate']=='P0001'and value['gate']is None and value['object']=='platform_private.grant_guard'and value['source_frame_verified']is True and value['source_position_verified']is False
    if value['sqlstate']!='42501'or value['source_frame_verified']is not False:return False
    if any(type(contract[k])is not str for k in shapes[kind]-{'kind'}):return False
    if kind=='SET_ROLE':allowed={('ROLE',contract['target_role'])}
    elif kind=='SCHEMA_CREATE':allowed={('SCHEMA_CREATE',contract['schema'])}
    elif kind=='FUNCTION':allowed={('SCHEMA',contract['schema']),('FUNCTION',contract['schema']+'.'+contract['function'])}
    else:allowed={('SCHEMA',contract['schema']),('TABLE',contract['schema']+'.'+contract['relation']),('COLUMN',contract['schema']+'.'+contract['relation'])}
    return (value['gate'],value['object'])in allowed
