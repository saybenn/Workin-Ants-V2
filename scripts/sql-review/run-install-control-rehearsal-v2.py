"""Dormant finite INSTALL controls on Root-created disposable local targets.

No container/volume creation/removal, image pull, direct ledger writes, reset,
db push, schema repair or owner API occurs here. Import/help load no project
helper. The external operator owns protected credentials, tools and cleanup.
Full native ACL/schema comparison remains an explicit downstream requirement.
"""
import argparse
from contextlib import redirect_stdout,redirect_stderr
import hashlib
import io
import json
from pathlib import Path
import re
import subprocess
import tarfile
import time
from types import ModuleType
import uuid

ROOT=Path(__file__).resolve().parents[2];TASK=ROOT.parent
PACKET='review-output/install-control-rehearsal-v2'
SELF='scripts/sql-review/run-install-control-rehearsal-v2.py'
PROTOCOL='scripts/install_control_protocol_v2.py';GEN='scripts/prepare-install-control-rehearsal-v2.py'
CTX='scripts/sql-review/run-context-control-rehearsal.py'
API='scripts/sql-review/run-first-rehearsal.py';HOST='scripts/sql-review/run-local-f0-migrate.py'
DIAG='scripts/sql-review/rehearsal-diagnostics.py';HISTORY='scripts/prepare-local-f0-history.py'
COLLECTOR='scripts/sql-review/collect_native_catalog.sql'
MODULES=(SELF,PROTOCOL,GEN,CTX,API,HOST,DIAG,HISTORY,COLLECTOR)
TOOL_CLOSURE='context/reconciliation/local-f0-tooling/prisma-tools-closure.json'
TOOL_CLOSURE_SHA='610e36e4006e9680d0e6a036486f302a18ecce9593699125b4173f5914acb88b'
CTX_SHA='5ec53d01d7c5b19bea0a584ef9f5b4e6742d9509c21ac7e2250b9bdd62511f33'
HISTORY_SHA='33fe46e1b50c8d808ffb95b60cc42750e795582e6a1b15fb82f4fe93321281f8'
HOST_SHA='4b929dd8c46fea0fa0e09f92cf54e8bb37db194a9ce5c6fd02c0e91542d7909f'
ROLES=('postgres','wa_migrator','wa_context_issuer','wa_identity_service_authority','wa_app_runtime','wa_worker')
VARIANTS=('canonical','division_failure','late_function_grant')
MIGRATION='20261117000100_f0_local_initial';DB='wa_p0c_rehearsal'
RUNTIME=('prisma.local-f0.config.mjs','scripts/sql-review/local-f0-migrate-guard.mjs','scripts/sql-review/local-f0-migrate-runner.mjs')
SOURCE_SQL='prisma/foundation/migrations/'+MIGRATION+'/migration.sql'
SOURCE_SEVEN={SOURCE_SQL,'prisma/foundation/migrations/migration_lock.toml','prisma/review/foundation-candidate.prisma',*RUNTIME,'prisma/foundation/history-manifest.json'}

class HeldFailure(Exception):
    def __init__(self,code):self.code=code;super().__init__(code)

def need(ok,code):
    if not ok:raise HeldFailure(code)

def sha(raw):return hashlib.sha256(raw).hexdigest()
def canonical(value):return json.dumps(value,sort_keys=True,separators=(',',':'),ensure_ascii=False,allow_nan=False)
def quote(value):return "'"+value.replace("'","''")+"'"
def exact(value,wanted,code):need(canonical(value)==canonical(wanted),code)

def unique_json(raw):
    def pairs(items):
        value={}
        for key,item in items:need(key not in value,'DUPLICATE_JSON_FIELD');value[key]=item
        return value
    return json.loads(raw,object_pairs_hook=pairs,parse_constant=lambda _:(_ for _ in ()).throw(HeldFailure('NONFINITE_JSON')))

def source(relative):
    need(type(relative) is str and relative and ':' not in relative and '\\' not in relative and not relative.startswith('/') and all(p not in ('','.','..') for p in relative.split('/')),'SOURCE_PATH')
    path=(ROOT/relative).resolve();need(path.is_relative_to(ROOT.resolve()),'SOURCE_PATH');return path

def external(value):
    path=Path(value).resolve();need(path.is_relative_to(TASK.resolve()) and path!=TASK.resolve() and not path.is_relative_to(ROOT.resolve()),'TASK_EXTERNAL_PATH');return path

def read_bound(binding,limit=16*1024*1024):
    need(type(binding) is dict and set(binding)=={'path','sha256'} and type(binding['sha256']) is str and re.fullmatch('[0-9a-f]{64}',binding['sha256']),'FILE_BINDING')
    path=external(binding['path']);need(not path.is_symlink() and path.is_file() and path.stat().st_size<=limit,'BOUNDED_REGULAR_FILE_REQUIRED')
    with path.open('rb') as f:raw=f.read(limit+1)
    need(len(raw)<=limit and sha(raw)==binding['sha256'],'FILE_HASH_DRIFT');return raw

def compiled(path,raw):
    module=ModuleType('_install_'+Path(path).stem.replace('-','_'));module.__file__=str(source(path));stream=io.StringIO()
    try:
        with redirect_stdout(stream),redirect_stderr(stream):exec(compile(raw,module.__file__,'exec'),module.__dict__)
    except BaseException:raise HeldFailure('PINNED_HELPER_LOAD_FAILED') from None
    need(not stream.getvalue(),'PINNED_HELPER_OUTPUT');return module.__dict__

def load_inputs(plan):
    fields={'schema','scope','run_id','source_commit','source_tree','packet_sha256','reviewed_packet_sha256','source_modules_sha256','targets','histories','credential_bundle'}
    need(type(plan) is dict and set(plan)==fields and plan['schema']=='workinants.install-controls-run.v1' and plan['scope']=='FINITE_INSTALL_HISTORY_AND_AUTHORITY_CONTROLS','RUN_PLAN_SCOPE')
    need(type(plan['run_id']) is str and str(uuid.UUID(plan['run_id']))==plan['run_id'] and uuid.UUID(plan['run_id']).version==4,'RUN_UUID')
    for key in ('source_commit','source_tree'):need(type(plan[key]) is str and re.fullmatch('[0-9a-f]{40}',plan[key]),'SOURCE_CHECKPOINT')
    for key in ('packet_sha256','reviewed_packet_sha256'):need(type(plan[key]) is str and re.fullmatch('[0-9a-f]{64}',plan[key]),'SOURCE_PACKET_HASH')
    pins=plan['source_modules_sha256'];need(type(pins) is dict and set(pins)==set(MODULES),'CLOSED_MODULE_MAP')
    modules={path:source(path).read_bytes() for path in MODULES}
    need(all(type(pins[p]) is str and sha(raw)==pins[p] for p,raw in modules.items()) and pins[CTX]==CTX_SHA and pins[HISTORY]==HISTORY_SHA and pins[HOST]==HOST_SHA,'SOURCE_MODULE_DRIFT')
    packet_raw=source(PACKET+'/fixtures.json').read_bytes();need(sha(packet_raw)==plan['reviewed_packet_sha256'],'REVIEWED_FIXTURE_HASH');packet=unique_json(packet_raw)
    need(packet['schema']=='workinants.install-control-fixtures.v1' and packet['status']=='NOT_RUN' and packet['posture']=='D' and packet['database_contacted'] is False,'SOURCE_ONLY_PACKET')
    exact(packet['selected_control_ids'],['P0C-INSTALL-01','P0C-INSTALL-02'],'SOURCE_CASE_IDS')
    content={k:packet[k] for k in ('source_files_sha256','prepared_files_sha256')};need(sha(canonical(content).encode())==packet['source_only_packet_sha256'],'PACKET_CONTENT_HASH')
    # Source-pinned data dependency, not a caller-selected tool whitelist.
    exact(packet.get('tool_closure_source'),{'path':TOOL_CLOSURE,'sha256':TOOL_CLOSURE_SHA,'file_count':10300},'PINNED_TOOL_CLOSURE_DEPENDENCY_REQUIRED')
    need(packet['source_files_sha256'].get(TOOL_CLOSURE)==TOOL_CLOSURE_SHA,'PINNED_TOOL_CLOSURE_DEPENDENCY_REQUIRED')
    inputs={path:source(path).read_bytes() for path in packet['source_files_sha256']}
    need(all(sha(inputs[p])==digest for p,digest in packet['source_files_sha256'].items()) and all(inputs[p]==raw for p,raw in modules.items()),'SOURCE_INPUT_DRIFT')
    closure=unique_json(inputs[TOOL_CLOSURE])
    need(type(closure) is dict and type(closure.get('tools_files_sha256')) is dict and type(closure.get('file_count')) is int and closure['file_count']==len(closure['tools_files_sha256'])==10300,'PINNED_TOOL_CLOSURE_SHAPE')
    tool_files=closure['tools_files_sha256']
    sql={}
    for name,digest in packet['prepared_files_sha256'].items():
        need(type(name) is str and ':' not in name and '\\' not in name and all(p not in ('','.','..') for p in name.split('/')),'PREPARED_PATH')
        raw=source(PACKET+'/'+name).read_bytes();need(sha(raw)==digest,'PREPARED_SQL_DRIFT');sql[name]=raw
    targets=plan['targets'];need(type(targets) is dict and set(targets)==set(VARIANTS),'EXACT_THREE_TARGETS')
    suffix={'canonical':'good','division_failure':'division','late_function_grant':'order'};ids=set()
    for variant,target in targets.items():
        name='wa-p0c-'+plan['run_id'][:8]+'-install-'+suffix[variant]
        need(type(target) is dict and set(target)=={'name','volume','container_id'} and target['name']==name and target['volume']==name+'-data' and type(target['container_id']) is str and re.fullmatch('[0-9a-f]{64}',target['container_id']),'EXACT_OWNED_TARGET');ids.add(target['container_id'])
    need(len(ids)==3,'DISTINCT_TARGET_IDENTITIES')
    histories=plan['histories'];need(type(histories) is dict and set(histories)=={'canonical','division_failure','late_function_grant','division_recovery'},'EXACT_FOUR_IMMUTABLE_HISTORIES')
    admitted={}
    # No project helper executes before every source and every immutable history
    # has been hashed. Helper validation follows against the same cached bytes.
    for key,item in histories.items():
        need(type(item) is dict and set(item)=={'manifest','source_archive','source_files_sha256'},'HISTORY_BINDING')
        raw=read_bound(item['manifest']);archive=read_bound(item['source_archive'],64*1024*1024);manifest=unique_json(raw);wanted=item['source_files_sha256']
        need(type(manifest.get('tools')) is dict and type(manifest['tools'].get('files_sha256')) is dict,'HISTORY_TOOL_CLOSURE_SHAPE')
        exact(manifest['tools']['files_sha256'],tool_files,'HISTORY_TOOL_CLOSURE_NOT_SOURCE_REGISTERED')
        need(type(wanted) is dict and set(wanted)==SOURCE_SEVEN,'EXACT_SEVEN_SOURCE_FILES')
        members={}
        with tarfile.open(fileobj=io.BytesIO(archive),mode='r:gz') as tar:
            for entry in tar:
                need(entry.isfile() and entry.name in wanted and entry.name not in members and entry.size<=8*1024*1024 and entry.uid==entry.gid==0 and entry.mode in (0o600,0o644) and not entry.pax_headers and not entry.sparse,'SOURCE_ARCHIVE_MEMBER')
                body=tar.extractfile(entry).read();need(sha(body)==wanted[entry.name],'SOURCE_ARCHIVE_DRIFT');members[entry.name]=body
        need(set(members)==SOURCE_SEVEN,'SOURCE_ARCHIVE_CLOSURE')
        variant='canonical' if key=='division_recovery' else key;sql_sha=packet['variants'][variant]['sha256']
        need(sha(members[SOURCE_SQL])==sql_sha and members[SOURCE_SQL]==sql[packet['variants'][variant]['path']],'SOURCE_VARIANT_HASH')
        target=targets['division_failure' if key=='division_recovery' else key]
        need(manifest['run_id']==plan['run_id'] and manifest['target']['container_name']==target['name'] and manifest['target']['volume_name']==target['volume'] and manifest['source']['integrated_sql_sha256']==sql_sha,'HISTORY_RUN_IDENTITY')
        history=unique_json(members['prisma/foundation/history-manifest.json'])
        need(history['schema']=='workinants.local-f0-history.v1' and history['run_id']==plan['run_id'] and history['run_manifest_sha256']==sha(raw) and history['source_sql_sha256']==sql_sha and history['files_sha256']=={p:wanted[p] for p in SOURCE_SEVEN if p!='prisma/foundation/history-manifest.json'} and history['database_contacted'] is False and history['ledger_created_or_modified'] is False,'FRESH_HISTORY_PROVENANCE')
        for path in RUNTIME:need(sha(modules[HISTORY])==HISTORY_SHA and sha(source(path).read_bytes())==wanted[path]==manifest['source']['runtime_files_sha256'][path],'UNCHANGED_RUNTIME_BOUNDARY')
        admitted[key]={'manifest':manifest,'raw':raw,'archive':archive,'members':members,'binding':item,'target':target}
    bundle=external(plan['credential_bundle']);need(bundle.name=='install-role-passwords.json' and bundle.parent.name=='private' and not bundle.is_symlink() and bundle.is_file() and bundle.stat().st_size<=16384,'PRIVATE_CREDENTIAL_BUNDLE')
    passwords=unique_json(bundle.read_bytes());need(type(passwords) is dict and set(passwords)==set(VARIANTS),'PRIVATE_CREDENTIAL_TARGETS')
    for values in passwords.values():need(type(values) is dict and set(values)==set(ROLES) and all(type(v) is str and re.fullmatch('[0-9a-f]{64}',v) for v in values.values()) and len(set(values.values()))==6,'INDEPENDENT_PRIVATE_PASSWORDS')
    need(len({v for values in passwords.values() for v in values.values()})==18,'INDEPENDENT_TARGET_PASSWORDS')
    ctx=compiled(CTX,modules[CTX]);ctx['load_helpers']({p:modules[p] for p in ctx['SOURCE_MODULES']});protocol=compiled(PROTOCOL,modules[PROTOCOL])
    generator=compiled(GEN,modules[GEN]);reproduced,prepared=generator['build'](ROOT,inputs)
    exact(prepared,packet,'PACKET_REPRODUCTION');need(all(reproduced[name]==raw for name,raw in sql.items()),'PREPARED_BYTES_REPRODUCTION')
    for key,item in admitted.items():
        ctx['HOST']['validate_manifest'](item['manifest'])
        need(Path(item['manifest']['target']['bootstrap_secret_host_path']).resolve().parent==bundle.parent,'SAME_RUN_PRIVATE_DIRECTORY')
        expected=generator['prepare_history'](ROOT,item['raw'],'canonical' if key=='division_recovery' else key,inputs)
        exact({p:sha(b) for p,b in expected.items()},{p:sha(b) for p,b in item['members'].items()},'IMMUTABLE_SEVEN_REPRODUCTION')
    return packet,sql,admitted,passwords,ctx,protocol

class Evidence:
    def __init__(self,directory):
        self.directory=directory;directory.mkdir(exist_ok=False);self.value={'schema':'workinants.install-controls-results.v1','status':'RUNNING','current_stage':'ENTRY','targets':{},'subsequent_cases_stopped':False,'limits':{'posture':'D','whole_cases':'NOT_PROMOTED','full_native_acl_and_ledger_comparison':'PENDING_OUTER_OPERATOR','451_register':'NOT_PROMOTED','raw_output_retained':False}};self.save()
    def save(self):
        path=self.directory/'install-controls-results.json';tmp=path.with_suffix('.tmp');tmp.write_text(json.dumps(self.value,indent=2,allow_nan=False)+'\n',encoding='utf8');tmp.replace(path)
    def stage(self,name):self.value['current_stage']=name;self.save()

class Coordinator:
    def __init__(self,plan,packet,sql,histories,passwords,ctx,protocol,evidence,process=subprocess.run,monotonic=time.monotonic,sleep=time.sleep):
        self.plan=plan;self.packet=packet;self.sql=sql;self.histories=histories;self.passwords=passwords;self.ctx=ctx;self.p=protocol;self.e=evidence;self.process=process;self.monotonic=monotonic;self.sleep=sleep;self.bootstrap_attempted=set();self.bootstrapped=set();self.finalized=set();self.gates={v:protocol['ActivationGate']() for v in VARIANTS};self.rows={}
    def record(self,variant,key,value):self.e.value['targets'].setdefault(variant,{})[key]=value;self.e.save()
    def target(self,variant):return self.plan['targets'][variant]
    def text(self,name):
        raw=self.sql[name];need(sha(raw)==self.packet['prepared_files_sha256'][name],'CACHED_SQL_DRIFT');return raw.decode('utf8')
    def docker(self,args,input=None,timeout=30):return self.process(['docker','--context','desktop-linux',*args],input=input,text=True,capture_output=True,timeout=timeout,shell=False)
    def live(self,variant,history=None):
        item=self.histories[history or variant];host=self.ctx['HOST'];m=item['manifest'];context=host['docker_json'](['context','inspect','desktop-linux'],self.process);c=host['docker_json'](['inspect',m['target']['container_name']],self.process);v=host['docker_json'](['volume','inspect',m['target']['volume_name']],self.process);o=host['inspect_live'](m,context,c,v);host['verify_image'](m,c,host['docker_json'](['image','inspect',m['target']['image']],self.process));need(o['container_id']==self.target(variant)['container_id'],'IMMUTABLE_CID_CHANGED');return o
    def psql(self,variant,role,text,wrong=False):
        need(role in ROLES,'LOGIN_ROLE');cid=self.target(variant)['container_id'];path='/run/wa-secrets/wrong-'+role+'.pgpass' if wrong else '/run/wa-secrets/pgpass'
        return self.docker(['exec','-i','-e','PGPASSFILE='+path,'-e','PGAPPNAME=wa-install-'+self.plan['run_id'],cid,'psql','-X','-w','-qAt','-v','ON_ERROR_STOP=1','-v','VERBOSITY=verbose','-v','SHOW_CONTEXT=errors','-h','127.0.0.1','-p','5432','-U',role,'-d',DB,'-f','-'],text,30)
    def closed(self,variant,label):
        proof={'scope':'ALL_DATABASES_ALL_ROLES_ALL_APPLICATION_NAMES','observation_completed':False,'all_other_clients_absent':False}
        try:
            r=self.psql(variant,'postgres',"SELECT count(*) FROM pg_stat_activity WHERE backend_type='client backend' AND pid<>pg_backend_pid();\n")
            need(type(r.returncode) is int and r.returncode==0 and r.stdout.strip()=='0' and r.stderr=='','OTHER_CLIENT_BACKENDS_OR_UNCONFIRMED_OBSERVATION');proof.update(observation_completed=True,all_other_clients_absent=True)
        finally:self.record(variant,'closure_'+label,proof)
    def execute(self,variant,role,text,label):
        self.e.stage(label)
        try:r=self.psql(variant,role,text)
        finally:self.closed(variant,label)
        need(type(r.returncode) is int and r.returncode==0 and r.stderr=='' and r.stdout.strip()=='','INSTALL_SQL_COMPLETION_REQUIRED');return r
    def observe(self,variant,name,label):
        self.e.stage(label)
        try:r=self.psql(variant,'postgres',self.text(name))
        finally:self.closed(variant,label)
        need(type(r.returncode) is int and r.returncode==0 and r.stderr=='' and len(r.stdout)<=1024*1024,'INSTALL_OBSERVATION_UNCONFIRMED');return unique_json(r.stdout)
    def auth(self,variant,role,accepted):
        query="SELECT jsonb_build_object('login',session_user,'auth',system_user,'database',current_database(),'client',host(inet_client_addr()),'server',host(inet_server_addr()));\n"
        self.e.stage('AUTH_'+role.upper())
        try:r=self.psql(variant,role,query)
        finally:self.closed(variant,'AUTH_'+role)
        if accepted:
            need(type(r.returncode) is int and r.returncode==0 and r.stderr=='' and len(r.stdout)<=4096,'ACTUAL_SCRAM_LOGIN_REQUIRED')
            checks=self.ctx['API']['authentication_comparison'](r.stdout,role);need(all(type(v) is bool and v for v in checks.values()),'ACTUAL_SCRAM_IDENTITY')
            try:wrong=self.psql(variant,role,'SELECT 1;\n',True)
            finally:self.closed(variant,'WRONG_AUTH_'+role)
            self.rejected_auth(wrong,role)
        else:self.rejected_auth(r,role)
        self.record(variant,'auth_'+role,{'role':role,'correct_password':'PASS_SCRAM' if accepted else 'PASS_REJECTED_INACTIVE','wrong_password':'PASS_REJECTED' if accepted else 'NOT_RUN','actual_connection_closed':True})
    def rejected_auth(self,r,role):
        message='FATAL:  password authentication failed for user "'+role+'"'
        need(type(r.returncode) is int and r.returncode==2 and r.stdout=='' and len(r.stderr)<=8192 and sum(line.strip().endswith(message) for line in r.stderr.splitlines())==1,'ACTUAL_REJECTED_STARTUP_REQUIRED')
    def settings(self,variant):
        text="SELECT jsonb_build_object('prefix',current_setting('log_line_prefix')='WA_F0_DIAG|%e|%u|%d|','terse',current_setting('log_error_verbosity')='terse','no_statements',current_setting('log_statement')='none','no_error_statements',current_setting('log_min_error_statement')='panic','locale',current_setting('lc_messages')='C','passwords',current_setting('password_encryption')='scram-sha-256','version',current_setting('server_version_num')='170011');\n"
        try:r=self.psql(variant,'postgres',text)
        finally:self.closed(variant,'SETTINGS')
        need(type(r.returncode) is int and r.returncode==0 and r.stderr=='' and len(r.stdout)<=4096,'SAFE_SETTINGS_OBSERVATION');value=unique_json(r.stdout);exact(value,dict.fromkeys(('prefix','terse','no_statements','no_error_statements','locale','passwords','version'),True),'SAFE_SERVER_LOGGING_REQUIRED');self.record(variant,'settings',value)
    def inactive(self,variant,label):
        value=self.observe(variant,'inactive-observe.sql',label);exact(value,{'runtime_roles':4,'all_null_verifiers':True,'flags_exact':True},'RUNTIME_CREDENTIALS_ALREADY_ACTIVE');self.record(variant,label,value)
        for role in ROLES[2:]:self.auth(variant,role,False)
    def authority(self,variant,temporary):
        value=self.observe(variant,'authority-observe.sql','AUTHORITY_OBSERVE');exact(value,{'temporary_memberships':temporary,'exact_temporary_options':True,'leaf_create':False,'permanent_migrator_edge':True},'INSTALL_AUTHORITY_NOT_EXACT');self.record(variant,'authority',value);return value
    def bootstrap(self,variant):
        self.live(variant);self.settings(variant);fresh=self.observe(variant,'fresh-observe.sql','EMPTY_TARGET_PRE_BOOTSTRAP');exact(fresh,dict.fromkeys(('no_existing_application_namespaces','no_existing_application_roles','ledger_absent'),True),'FRESH_DISPOSABLE_DATABASE_REQUIRED')
        self.bootstrap_attempted.add(variant);self.execute(variant,'postgres',self.text('bootstrap.sql'),'SEPARATE_ORIGINAL_BOOTSTRAP');self.bootstrapped.add(variant)
        sql='ALTER ROLE wa_migrator PASSWORD '+quote(self.passwords[variant]['wa_migrator'])+';\n'
        self.execute(variant,'postgres',sql,'ACTIVATE_ONLY_MIGRATOR');self.auth(variant,'postgres',True);self.auth(variant,'wa_migrator',True);self.authority(variant,3);self.inactive(variant,'BEFORE_INSTALL_RUNTIME_INACTIVE')
    def finalize(self,variant):
        self.closed(variant,'PRE_FINALIZATION');self.execute(variant,'postgres',self.text('finalize.sql'),'ORIGINAL_GRANTOR_FINALIZATION');self.authority(variant,0);self.finalized.add(variant)
        proof={'original_grantor':'postgres','temporary_memberships':0,'leaf_create':False,'other_clients':0};self.gates[variant].cleaned(proof);self.record(variant,'original_cleanup',proof)
    def activation_attempt(self,variant,expected):
        allowed=False
        try:allowed=self.gates[variant].permit()
        except self.p['Held'] as error:need(error.code=='INSTALL_RUNTIME_ACTIVATION_HELD','ACTIVATION_UNEXPECTED_REFUSAL')
        need(allowed is expected,'RUNTIME_ACTIVATION_GATE_MISMATCH');self.record(variant,'activation_gate_'+('allowed' if expected else 'held'),{'permit':allowed,'database_password_sql_executed':False})
    def activate(self,variant):
        self.activation_attempt(variant,True);self.inactive(variant,'AFTER_VERIFIED_CLEANUP_STILL_INACTIVE')
        sql='BEGIN;\n'+''.join('ALTER ROLE '+role+' PASSWORD '+quote(self.passwords[variant][role])+';\n' for role in ROLES[2:])+'COMMIT;\n'
        self.execute(variant,'postgres',sql,'ACTIVATE_FOUR_AFTER_VERIFIED_SUCCESS_CLEANUP');self.gates[variant].activated_once()
        for role in ROLES[2:]:self.auth(variant,role,True)
    def stage_history(self,key):
        item=self.histories[key];variant='division_failure' if key=='division_recovery' else key;self.live(variant,key)
        # Re-read/hash the exact immutable archive consumed by Docker; Root
        # preserves every previous archive and history, including failed bytes.
        raw=read_bound(item['binding']['source_archive'],64*1024*1024);need(raw==item['archive'],'STAGED_SOURCE_ARCHIVE_CHANGED')
        command='mkdir -p /run/wa-f0-source && tar -xzf - -C /run/wa-f0-source'
        result=self.process(['docker','--context','desktop-linux','exec','-i',self.target(variant)['container_id'],'sh','-ceu',command],input=raw,capture_output=True,timeout=30,shell=False)
        need(type(result.returncode) is int and result.returncode==0 and result.stdout==b'' and result.stderr==b'','SOURCE_ARCHIVE_STAGE_FAILED');self.closed(variant,'STAGE_'+key)
    def migrate(self,variant,key,operation='deploy',proof=None):
        item=self.histories[key];self.live(variant,key);self.e.stage('GENUINE_'+operation.upper())
        need(read_bound(item['binding']['manifest'])==item['raw'],'CURRENT_NESTED_MANIFEST_DRIFT')
        try:value=self.ctx['HOST']['coordinate'](item['raw'],operation,proof_bytes=proof,process=self.process,runtime_sources={p:item['members'][p] for p in RUNTIME})
        finally:self.closed(variant,'CLI_'+operation)
        self.record(variant,'cli_'+key+'_'+operation,value);return value
    def inventory(self,variant,empty):
        value=self.observe(variant,'inventory.sql','COMPLETE_APPLICATION_INVENTORY');self.p['inventory_shape'](value);self.record(variant,'inventory',value);self.p['validate_inventory'](value,empty);return value
    def ledger(self,variant):
        value=self.observe(variant,'ledger-observe.sql','GUARDED_PRIVATE_LEDGER');self.p['ledger_rows'](value);self.record(variant,'ledger',value);return value
    def server(self,variant):
        r=self.docker(['logs',self.target(variant)['container_id']],timeout=30);need(type(r.returncode) is int and r.returncode==0,'OWNED_SERVER_LOG_READ_FAILED');value=self.p['summarize_server'](r.stdout,r.stderr);self.p['counts'](value);return value
    def wrong_finalizer(self,variant):
        before=self.authority(variant,3)
        try:r=self.psql(variant,'wa_migrator',self.text('finalize.sql'))
        finally:self.closed(variant,'WRONG_FINALIZER')
        diagnostic=self.p['wrong_finalizer_diagnostic'](r.stderr,self.text('finalize.sql'))
        need(type(r.returncode) is int and r.returncode==3 and r.stdout=='' and diagnostic['matched'] is True,'EXACT_WRONG_GRANTOR_REFUSAL_REQUIRED');after=self.authority(variant,3);exact(before,after,'WRONG_GRANTOR_CHANGED_AUTHORITY');self.record(variant,'wrong_grantor',diagnostic)
    def schema_fingerprint(self,variant):
        args=['exec','-e','PGPASSFILE=/run/wa-secrets/pgpass','-e','PGAPPNAME=wa-install-'+self.plan['run_id'],self.target(variant)['container_id'],'pg_dump','--schema-only','--schema=app','--schema=platform','--schema=platform_private','--schema=public','-h','127.0.0.1','-U','postgres','-d',DB]
        try:r=self.docker(args,timeout=90)
        finally:self.closed(variant,'SCHEMA_FINGERPRINT')
        need(type(r.returncode) is int and r.returncode==0 and r.stderr=='' and len(r.stdout)<=64*1024*1024,'SCHEMA_FINGERPRINT_UNCONFIRMED')
        lines=r.stdout.splitlines();meta=[line for line in lines if line.startswith(('\\restrict','\\unrestrict'))]
        need(len(meta) in (0,2) and all(re.fullmatch(r'\\(?:un)?restrict [A-Za-z0-9]{1,128}',line) for line in meta) and (not meta or meta[0][len('\\restrict '):]==meta[1][len('\\unrestrict '):]),'SCHEMA_FINGERPRINT_META_FORMAT')
        result={'sha256':sha(('\n'.join(line for line in lines if line not in meta)+'\n').encode()),'random_meta_lines_removed':len(meta),'raw_dump_retained':False};self.record(variant,'schema_fingerprint',result);return result
    def successful_install(self):
        variant='canonical';self.bootstrap(variant);self.activation_attempt(variant,False);self.stage_history(variant)
        try:value=self.migrate(variant,variant);self.p['completed'](value);self.gates[variant].installed(True,True);self.activation_attempt(variant,False);self.wrong_finalizer(variant)
        finally:self.finalize(variant)
        self.inventory(variant,False);first=self.ledger(variant);self.p['applied_ledger'](first);self.activate(variant);self.good_schema=self.schema_fingerprint(variant)
        again=self.migrate(variant,variant);self.p['completed'](again);need(again['no_pending_message_observed'] is True,'GENUINE_NOOP_MESSAGE_REQUIRED');exact(self.ledger(variant),first,'NOOP_LEDGER_CHANGED');self.inventory(variant,False);exact(self.schema_fingerprint(variant),self.good_schema,'NOOP_APPLICATION_DDL_CHANGED')
        self.record(variant,'finite_result',{'success_cleanup_and_runtime_activation':'PASS_FINITE_PROTOCOL','genuine_second_deploy':'PASS_UNCHANGED_PRIVATE_LEDGER','full_schema_and_acl_parity':'PENDING_OUTER_OPERATOR_FULL_NATIVE_COMPARISON'})
    def failure(self,variant):
        self.bootstrap(variant);self.activation_attempt(variant,False);self.stage_history(variant);before=self.server(variant);self.record(variant,'server_before',before)
        try:value=self.migrate(variant,variant);self.gates[variant].installed(False,True)
        finally:self.finalize(variant)
        inventory=self.inventory(variant,True);ledger=self.ledger(variant);after=self.server(variant);self.record(variant,'server_after',after)
        verdict=self.p['failure_verdict'](variant,value,inventory,ledger,before,after,self.packet['variants'][variant]['sha256']);self.record(variant,'failure_verdict',verdict);self.inactive(variant,'FAILED_INSTALL_REMAINS_INACTIVE');self.activation_attempt(variant,False);self.rows[variant]=ledger['rows'][0];return verdict
    def review(self,variant,verdict):
        proof={'schema':'workinants.install-rollback-observation.v1','run_id':self.plan['run_id'],'source_commit':self.plan['source_commit'],'source_tree':self.plan['source_tree'],'packet_sha256':self.plan['packet_sha256'],'container_id':self.target(variant)['container_id'],'source_sql_sha256':self.packet['variants'][variant]['sha256'],'failure':verdict,'failed_ledger':self.rows[variant],'application_inventory':dict.fromkeys(('relations','functions','types','enums','other_clients'),0),'original_grantor_finalized':variant in self.finalized,'disposition':'PENDING_INDEPENDENT_REVIEW'}
        path=self.e.directory/'rollback-proof-for-review.json';approval=self.e.directory/'independent-recovery-approval.json';need(not path.exists() and not approval.exists(),'FRESH_INDEPENDENT_REVIEW_FILES')
        path.write_bytes((self.p['canonical'](proof)+'\n').encode());self.record(variant,'review_hold',{'proof_sha256':sha(path.read_bytes()),'decision':'PENDING_INDEPENDENT_REVIEW','timeout_seconds':240});self.e.stage('INDEPENDENT_ROLLBACK_REVIEW_REQUIRED');deadline=self.monotonic()+240
        while not approval.exists() and self.monotonic()<deadline:self.sleep(1)
        need(approval.exists() and self.monotonic()<deadline and not approval.is_symlink() and approval.is_file() and approval.stat().st_size<=8192,'RECOVERY_REVIEW_PENDING_OR_TIMEOUT')
        with approval.open('rb') as file:raw=file.read(8193)
        need(len(raw)<=8192,'BOUNDED_REVIEW_DECISION');decision=unique_json(raw);identity={k:proof[k] for k in ('run_id','container_id','source_sql_sha256')};self.p['require_recovery_review'](proof,decision,identity);self.record(variant,'independent_recovery_review',decision)
        # Existing immutable guard requires its original closed proof schema.
        # The new independent observation is the authority; this exact adapter
        # supplies only its already-proven zero-object/checksum facts.
        return {'schema':'workinants.local-f0-reviewed-rollback.v1','run_id':proof['run_id'],'container_id':proof['container_id'],'migration_id':MIGRATION,'source_sql_sha256':proof['source_sql_sha256'],'disposition':'REVIEWED_FOR_STANDARD_RESOLVE_ROLLED_BACK','backend_closed':True,'application_transaction_rolled_back':True,'application_object_count':0,'failed_migration_rows':1,'finished_migration_rows':0,'rolled_back_migration_rows':0,'failed_row_checksum':proof['source_sql_sha256'],'catalog_evidence_sha256':sha(canonical(proof['application_inventory']).encode()),'ledger_evidence_sha256':sha(canonical(self.rows[variant]).encode())}
    def recovery(self,verdict):
        v='division_failure';proof=self.review(v,verdict);value=self.migrate(v,v,'resolve-rolled-back',(canonical(proof)+'\n').encode());self.p['completed'](value,'resolve-rolled-back');self.p['resolved_ledger'](self.ledger(v),self.rows[v]);self.inventory(v,True)
        self.finalized.discard(v);self.execute(v,'postgres',self.text('rearm.sql'),'ORIGINAL_GRANTOR_THREE_EXACT_MEMBERSHIPS');self.authority(v,3);self.stage_history('division_recovery')
        try:value=self.migrate(v,'division_recovery');self.p['completed'](value);self.gates[v].installed(True,True)
        finally:self.finalize(v)
        self.inventory(v,False);first=self.ledger(v);self.p['applied_ledger'](first,self.rows[v]);self.activate(v);schema=self.schema_fingerprint(v);exact(schema,self.good_schema,'RECOVERED_CANONICAL_SCHEMA_DIFFERS');value=self.migrate(v,'division_recovery');self.p['completed'](value);need(value['no_pending_message_observed'] is True,'RECOVERED_GENUINE_NOOP_REQUIRED');exact(self.ledger(v),first,'RECOVERED_NOOP_LEDGER_CHANGED');self.inventory(v,False);exact(self.schema_fingerprint(v),schema,'RECOVERED_NOOP_DDL_CHANGED')
        self.record(v,'recovery_result',{'standard_resolve':'PASS_AFTER_INDEPENDENT_REVIEW','failed_row_retained_unchanged':True,'canonical_retry_and_noop':'PASS_FINITE_PROTOCOL','full_schema_and_acl_parity':'PENDING_OUTER_OPERATOR_FULL_NATIVE_COMPARISON'})
    def run(self):
        try:self.successful_install();verdict=self.failure('division_failure');self.recovery(verdict);self.failure('late_function_grant');self.e.value['status']='PASS_FINITE_INSTALL_PROTOCOLS_PENDING_FULL_NATIVE_COMPARISON'
        finally:
            failures=[]
            for variant in sorted(self.bootstrap_attempted-self.finalized):
                try:self.finalize(variant)
                except BaseException:
                    failures.append('ORIGINAL_FINALIZATION_UNCONFIRMED')
                    try:self.record(variant,'finally_cleanup',{'confirmed':False,'code':'ORIGINAL_FINALIZATION_UNCONFIRMED'})
                    except BaseException:failures.append('FINALIZATION_EVIDENCE_WRITE_UNCONFIRMED')
            for variant in sorted(self.bootstrap_attempted):
                try:self.closed(variant,'FINAL_GLOBAL')
                except BaseException:failures.append('FINAL_GLOBAL_CLOSURE_UNCONFIRMED')
            try:self.e.save()
            except BaseException:failures.append('FINAL_EVIDENCE_WRITE_UNCONFIRMED')
            need(not failures,'INSTALL_FINALLY_FINALIZATION_OR_CLOSURE_UNCONFIRMED')

def main(argv=None,dependencies=None):
    dependencies=dependencies or {};parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--execute-reviewed-install-controls',action='store_true');parser.add_argument('--reviewed-run-plan',type=Path);parser.add_argument('--evidence-directory',type=Path);args=parser.parse_args(argv);evidence=None
    try:
        need(args.execute_reviewed_install_controls and args.reviewed_run_plan and args.evidence_directory,'EXPLICIT_REVIEWED_EXECUTION_REQUIRED');raw=external(args.reviewed_run_plan).read_bytes();need(len(raw)<=1024*1024,'BOUNDED_RUN_PLAN');plan=unique_json(raw);loaded=(dependencies.get('load_inputs') or load_inputs)(plan);directory=external(args.evidence_directory);need(not directory.exists(),'FRESH_EXTERNAL_EVIDENCE')
        evidence=(dependencies.get('evidence') or Evidence)(directory);evidence.value.update(run_id=plan['run_id'],source_commit=plan['source_commit'],source_tree=plan['source_tree'],packet_sha256=plan['packet_sha256'],reviewed_plan_sha256=sha(raw));evidence.save();factory=dependencies.get('coordinator') or Coordinator;factory(plan,*loaded[:4],loaded[4],loaded[5],evidence).run();return 0
    except BaseException as error:
        if evidence is not None:
            code=getattr(error,'code','UNEXPECTED_RESPONSE_OR_INTERNAL');code=code if type(code) is str and re.fullmatch('[A-Z0-9_]{1,96}',code) else 'UNEXPECTED_RESPONSE_OR_INTERNAL';evidence.value.update(status='STOPPED_UNEXPECTED_RESULT',subsequent_cases_stopped=True,failure={'stage':evidence.value['current_stage'],'code':code,'raw_exception_discarded':True});evidence.save()
        else:print(json.dumps({'status':'HELD_BEFORE_RUNTIME','code':'SOURCE_PLAN_OR_PRIVATE_INPUT_REQUIRED'}))
        return 2
if __name__=='__main__':raise SystemExit(main())
