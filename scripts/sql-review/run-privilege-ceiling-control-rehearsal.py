"""Dormant finite privilege coordinator. Never provisions resources/credentials.

Import/help uses stdlib only. Execution requires a reviewed external same-run
Native/oracle/ledger PASS attestation, exact full source pins and an owned CID.
"""
import argparse
import builtins
import contextlib
from copy import deepcopy
import datetime
import hashlib
import io
import ipaddress
import json
import os
from pathlib import Path
import queue
import re
import runpy
import secrets
import subprocess
import sys
import threading
import time
import types
import uuid

ROOT=Path(__file__).resolve().parents[2];TASK=ROOT.parent
SELF='scripts/sql-review/run-privilege-ceiling-control-rehearsal.py'
PROTOCOL='scripts/privilege_ceiling_control_protocol.py'
GENERATOR='scripts/prepare-privilege-ceiling-control-rehearsal.py'
PACKET='review-output/privilege-ceiling-control-rehearsal'
NATIVE='scripts/sql-review/run-native-table-denials-v3.py'
NATIVE_SHA='6e74115cc7a77e626c4379c5a5744efdede1257d04b206fc339e62a23fd49cd3'
CTX='scripts/sql-review/run-context-control-rehearsal.py'
CTX_SHA='5ec53d01d7c5b19bea0a584ef9f5b4e6742d9509c21ac7e2250b9bdd62511f33'
NATIVE_PACKET_SHA='8044d43f25c4a449f662bbb467183aac86d6a619836aae0988458098d59e0b69'
APPLICATION_SHA='5ae39abf991f9c189e367eb6ab6968b0ad50836bf4220ac27ef8c18306ac26ad'
EXPECTED_NATIVE='3be81a13d3bb2abb41bf03ef68398da6d92fbdbccffec3d74508e91dd455f433'
DATABASE='wa_p0c_rehearsal'


class Held(Exception):
    def __init__(self,code):self.code=code;super().__init__(code)


def need(value,code):
    if not value:raise Held(code)


def sha(raw):return hashlib.sha256(raw).hexdigest()
def canonical(value):return json.dumps(value,sort_keys=True,separators=(',',':'),allow_nan=False)
def digest(value):return sha(canonical(value).encode())
def quote(value):return "'"+str(value).replace("'","''")+"'"
def unique_json(raw):
    def pairs(items):
        result={}
        for key,value in items:need(key not in result,'DUPLICATE_JSON_KEY');result[key]=value
        return result
    return json.loads(raw,object_pairs_hook=pairs,parse_constant=lambda _:(_ for _ in()).throw(Held('NONFINITE_JSON')))


def person_binding_comparison(rows,ack,errors):
    """Return only fixed Boolean checks; raw scalar rows never enter evidence."""
    checks={'acknowledged':ack is True,'stderr_empty':type(errors)is str and errors=='','rows_list':type(rows)is list,'one_row':False,'row_text_bounded':False,'json_parsed':False,'object':False,'exact_fields':False,'boolean_fields':False,'allowed':False,'owner_subject':False,'same_tuple':False}
    if type(rows)is not list:return checks
    checks['one_row']=len(rows)==1
    if not checks['one_row']or type(rows[0])is not str:return checks
    try:checks['row_text_bounded']=len(rows[0].encode('utf8'))<=4096
    except UnicodeError:return checks
    if not checks['row_text_bounded']:return checks
    try:value=unique_json(rows[0])
    except Exception:return checks
    checks['json_parsed']=True;checks['object']=type(value)is dict
    if not checks['object']:return checks
    checks['exact_fields']=set(value)=={'allowed','subject','same_tuple'}
    checks['boolean_fields']=checks['exact_fields']and all(type(value[k])is bool for k in('allowed','subject','same_tuple'))
    checks['allowed']=value.get('allowed')is True;checks['owner_subject']=value.get('subject')is True;checks['same_tuple']=value.get('same_tuple')is True
    return checks


def source_path(name):
    need(type(name)is str and not Path(name).is_absolute()and'\\'not in name and':'not in name and all(part not in('','.','..')for part in name.split('/')),'SOURCE_PATH')
    path=(ROOT/name).resolve();need(path.is_relative_to(ROOT.resolve()),'SOURCE_PATH_ESCAPE');return path


def external_path(value):
    path=Path(value);need(path.is_absolute(),'EXTERNAL_ABSOLUTE_PATH');path=path.resolve()
    need(path.is_relative_to(TASK.resolve())and not path.is_relative_to(ROOT.resolve())and path!=TASK.resolve(),'EXTERNAL_TASK_PATH');return path


def read_asset(item):
    need(type(item)is dict and set(item)=={'path','sha256'}and type(item['sha256'])is str and re.fullmatch('[0-9a-f]{64}',item['sha256']),'ASSET_REFERENCE_FIELDS')
    raw=external_path(item['path']).read_bytes();need(sha(raw)==item['sha256'],'EXTERNAL_ASSET_DRIFT');return raw


def compile_closed(blobs,path,cache):
    """Only same prehashed bytes; no project module may fall through to disk."""
    need(path in blobs,'MODULE_NOT_ADMITTED')
    if path in cache:return cache[path]
    allowed_stdlib={name:sys.modules[name]for name in('argparse','builtins','contextlib','copy','datetime','hashlib','io','ipaddress','json','os','pathlib','queue','re','runpy','secrets','subprocess','sys','threading','time','types','uuid')}
    def imported(name,globals=None,locals=None,fromlist=(),level=0):
        if name=='privilege_ceiling_control_protocol'and level==0:
            values=compile_closed(blobs,PROTOCOL,cache);module=types.ModuleType(name);module.__dict__.update(values);return module
        need(level==0 and name in allowed_stdlib,'UNAPPROVED_SOURCE_IMPORT')
        if name=='sys'and path==GENERATOR:return types.SimpleNamespace(path=list(sys.path),argv=list(sys.argv))
        return allowed_stdlib[name]
    value={'__name__':'_verified_privilege_source','__file__':str(ROOT/path),'__builtins__':{**vars(builtins),'__import__':imported}}
    output=io.StringIO()
    from contextlib import redirect_stdout,redirect_stderr
    with redirect_stdout(output),redirect_stderr(output):exec(compile(blobs[path],str(ROOT/path),'exec'),value)
    need(not output.getvalue(),'SOURCE_MODULE_OUTPUT_REFUSED');cache[path]=value;return value


def load_inputs(plan):
    fields={'schema','scope','run_id','source_commit','source_tree','packet_sha256','packet_files_sha256','fixtures_sha256','content_sha256','native_plan','prerequisite_attestation'}
    need(type(plan)is dict and set(plan)==fields and plan['schema']=='workinants.privilege-ceiling-run.v1'and plan['scope']=='FINITE_EXISTING_PRIVILEGE_CEILINGS_ONLY','PLAN_SCOPE')
    need(type(plan['run_id'])is str and str(uuid.UUID(plan['run_id']))==plan['run_id']and uuid.UUID(plan['run_id']).version==4 and all(type(plan[key])is str and re.fullmatch('[0-9a-f]{40}',plan[key])for key in('source_commit','source_tree')),'SOURCE_RUN_IDENTITY')
    pins=plan['packet_files_sha256'];need(type(pins)is dict and bool(pins)and all(type(wanted)is str and re.fullmatch('[0-9a-f]{64}',wanted)for wanted in pins.values()),'FULL_SOURCE_HASH_MAP')
    need(sha(''.join(name+'\0'+pins[name]+'\n'for name in sorted(pins)).encode())==plan['packet_sha256'],'FULL_SOURCE_AGGREGATE')
    required={SELF,PROTOCOL,GENERATOR,NATIVE,CTX,PACKET+'/fixtures.json'}
    need(required<=set(pins),'REQUIRED_SOURCE_CLOSURE_MISSING')
    blobs={name:source_path(name).read_bytes()for name in pins}
    need(all(sha(raw)==pins[name]for name,raw in blobs.items()),'FULL_SOURCE_DRIFT')
    need(sha(blobs[NATIVE])==NATIVE_SHA and sha(blobs[CTX])==CTX_SHA,'EXACT_REVIEWED_TRANSPORTS')
    raw=blobs[PACKET+'/fixtures.json'];need(sha(raw)==plan['fixtures_sha256'],'FIXTURE_SOURCE_IDENTITY');packet=unique_json(raw)
    need(packet['schema']=='workinants.privilege-ceiling-fixtures.v1'and packet['status']=='NOT_RUN'and packet['database_posture']=='D'and len(packet['cases'])==200 and len(packet['source_definers'])==16,'FINITE_PRIVILEGE_SCOPE')
    need(packet['source_only_packet_sha256']==plan['content_sha256']==digest({key:packet[key]for key in('source_files_sha256','prepared_files_sha256')}),'FINITE_CONTENT_AGGREGATE')
    for name,wanted in packet['source_files_sha256'].items():need(name in blobs and pins[name]==wanted,'PACKET_SOURCE_NOT_ADMITTED')
    for name,wanted in packet['prepared_files_sha256'].items():
        need(Path(name).name==name and name.endswith('.sql'),'FINITE_SQL_NAME');relative=PACKET+'/'+name
        need(relative in blobs and pins[relative]==wanted,'PACKET_SQL_NOT_ADMITTED')
    need(pins.get('review-output/foundation-application.review.sql')==APPLICATION_SHA and pins.get('review-output/native-table-denials-v2/packet.json')==NATIVE_PACKET_SHA,'CANONICAL_UNCHANGED_INPUTS')
    # All source/SQL inputs are admitted before the first helper compile. The
    # source factory reproduces byte-for-byte and cannot select a prior packet.
    cache={};protocol=compile_closed(blobs,PROTOCOL,cache);generator=compile_closed(blobs,GENERATOR,cache)
    files,reproduced=generator['generate'](ROOT)
    need(reproduced==packet and all(PACKET+'/'+name in blobs and blobs[PACKET+'/'+name]==value for name,value in files.items()),'EXACT_SOURCE_PACKET_REPRODUCTION')
    native=compile_closed(blobs,NATIVE,cache);ctx=compile_closed(blobs,CTX,cache)
    native_plan=plan['native_plan']
    need(type(native_plan)is dict and native_plan.get('run_id')==plan['run_id']and native_plan.get('source_commit')==plan['source_commit']and native_plan.get('source_tree')==plan['source_tree']and native_plan.get('packet_sha256')==NATIVE_PACKET_SHA,'SAME_RUN_NATIVE_PLAN')
    need(set(native_plan.get('source_modules_sha256',{}))==set(native['MODULES'])and all(name in blobs and pins[name]==wanted for name,wanted in native_plan['source_modules_sha256'].items()),'NATIVE_HELPER_FULL_PACKET_BINDING')
    native_packet,native_blobs,snapshot,api,host=native['load_inputs'](native_plan)
    proof=unique_json(read_asset(plan['prerequisite_attestation']))
    wanted={'schema':'workinants.privilege-ceiling-native-attestation.v1','run_id':plan['run_id'],'container_id':native_plan['immutable_container_id'],'source_commit':plan['source_commit'],'source_tree':plan['source_tree'],'operation_packet_sha256':plan['packet_sha256'],'native_sql_packet_sha256':NATIVE_PACKET_SHA,'application_sql_sha256':APPLICATION_SHA,'source_expected_sha256':EXPECTED_NATIVE,'native_snapshot_sha256':digest(snapshot),'native_comparison_file_sha256':native_plan['native_comparison']['sha256'],'genuine_prisma_one_applied_migration':True,'original_grantor_finalized':True,'native_expression_oracle_and_private_ledger_pass':True,'all_other_client_backends_absent':True,'provider_preinstall_source_proven':True,'posture':'D','whole_case_promotion':False}
    need(canonical(proof)==canonical(wanted),'FULL_NATIVE_ORACLE_LEDGER_PREREQUISITE')
    return packet,blobs,protocol,native,ctx,native_packet,native_blobs,snapshot,api,host


class Evidence:
    def __init__(self,directory,packet):
        directory.mkdir(parents=True,exist_ok=False);self.path=directory/'privilege-ceiling-results.json';self.failed=False
        self.value={'schema':'workinants.privilege-ceiling-evidence.v1','status':'IN_PROGRESS','database_posture':'D','current_stage':'ENTRY','current_case':None,'current':{},'operations':[],'results':[],'authentication':[],'native_controls':[],'facets':[],'selected_cases':[],'selected_controls':deepcopy(packet['control_links']),'source_assertion_links':'NOT_PROMOTED','cleanup_required':True,'subsequent_cases_stopped':False,'evidence_complete':True,'limits':{'whole94_451':False,'hosted_parity':False,'NOLOGIN_startup_guard':False,'function_body_confidentiality':False,'shadow_object_resistance':False,'owner_API_positive':False,'worker_loop':False}}
        self.save()
    def save(self):
        try:
            temporary=self.path.with_suffix('.tmp')
            with temporary.open('w',encoding='utf8',newline='\n')as stream:stream.write(json.dumps(self.value,indent=2,allow_nan=False)+'\n');stream.flush();os.fsync(stream.fileno())
            temporary.replace(self.path)
        except BaseException:self.failed=True;self.value['evidence_complete']=False;raise
    def stage(self,value):self.value['current_stage']=value;self.save()


def interactive_type(native):
    class Interactive(native['Session']):
        """Exact reviewed Native constructor/capture/reap/close; finite CTX call."""
        def call(self,text):
            need(self.process.poll()is None,'INTERACTIVE_SESSION_ENDED')
            token='WA_PRIV_ACK|'+secrets.token_hex(16);self.send(text+'\nSELECT '+quote(token)+';\n')
            rows=[];ack=False;deadline=time.monotonic()+15
            while time.monotonic()<deadline:
                try:line=self.queue.get(timeout=.1)
                except queue.Empty:
                    if self.process.poll()is not None:break
                    continue
                if line==token:ack=True;break
                if line:rows.append(line)
            if not ack:
                self.process.wait(timeout=10)
                for reader in self.readers:reader.join(timeout=5)
                while not self.queue.empty():
                    line=self.queue.get_nowait()
                    if line:rows.append(line)
            need(not self.invalid.is_set(),'INTERACTIVE_OUTPUT_INCOMPLETE')
            return rows,ack,''.join(self.errors)
    return Interactive


def runner_type(native,ctx,protocol):
    P=types.SimpleNamespace(**protocol)
    Interactive=interactive_type(native)
    class Runner(native['Coordinator']):
        def __init__(self,plan,packet,blobs,native_packet,native_blobs,snapshot,api,host,evidence):
            self.review_plan=plan;self.privileges_packet=packet;self.source_blobs=blobs
            self.grants={};self.failed=False;self._fingerprinting=False
            super().__init__(plan['native_plan'],native_packet,native_blobs,snapshot,api,host,evidence)
            self.columns={}
            for row in snapshot['columns']:self.columns.setdefault(row['table_name'],[]).append(row['name'])
            self.person=None;self.context_instances=0

        def persist(self):
            try:
                self.evidence.save()
                if self.evidence.value.get('evidence_complete')is not True:self.failed=True
                return not self.failed
            except BaseException:self.failed=True;self.evidence.value['evidence_complete']=False;return False

        def raw(self,role,text):
            if self._fingerprinting and self.grants:
                need(role=='postgres'and len(self.grants)<=2,'EXACT_DECLARED_GRANT_EXCLUSION')
                needle='FROM "platform"."database_action_grant" t'
                need(text.count(needle)==1,'SOURCE_FINGERPRINT_QUERY_IDENTITY')
                identities=','.join(quote(identity)+'::uuid'for identity in self.grants)
                text=text.replace(needle,'FROM (SELECT * FROM "platform"."database_action_grant" WHERE id NOT IN ('+identities+')) t')
            return super().raw(role,text)

        def fingerprint(self):
            self._fingerprinting=True
            try:return super().fingerprint()
            finally:self._fingerprinting=False

        def global_closed(self,label):
            record={'stage':label,'attempted':True,'confirmed':False}
            self.evidence.value.setdefault('global_client_boundaries',[]).append(record)
            self.persist()
            try:
                value=self.json("SELECT jsonb_build_object('other_clients',(SELECT count(*) FROM pg_stat_activity WHERE backend_type='client backend' AND pid<>pg_backend_pid()));")
                record['confirmed']=type(value)is dict and set(value)=={'other_clients'}and type(value['other_clients'])is int and value['other_clients']==0
            finally:self.persist()
            need(record['confirmed'],'GLOBAL_CLIENT_CLOSURE_UNCONFIRMED')
            need(not self.failed and self.evidence.value['evidence_complete']is True,'EVIDENCE_INCOMPLETE')

        def failure_metadata(self,error,phase):
            value=native['session_failure_metadata'](error,phase)
            fixed={'GLOBAL_CLIENT_CLOSURE_UNCONFIRMED','EVIDENCE_INCOMPLETE','INTENDED_PRIVILEGE_GUARD_NOT_PROVEN','PRIVATE_GRANT_STATE_MISMATCH','ISSUER_COMMIT_UNCONFIRMED','PRIVATE_CREATED_AT_REJECTED','INTERACTIVE_OUTPUT_UNCONFIRMED','SAME_APP_TUPLE_REQUIRED','OPERATION_BACKEND_CLOSURE_UNCONFIRMED','CURRENT_OWN_GRANT_REQUIRED','ISSUER_OWN_READ_REQUIRED','EXPECTED_FIRST_REVOKE_REQUIRED','GRANT_NOT_SOURCE_CURRENT','SOURCE_NATIVE_METADATA_REQUIRED','UNRESOLVED_SQL_TEMPLATE','INTERACTIVE_OUTPUT_INCOMPLETE','INTERACTIVE_SESSION_ENDED'}
            if isinstance(error,Held)and type(error.code)is str and error.code in fixed:value={'phase':phase,'classification':'SOURCE_HELD_FAILURE','code':error.code}
            return value

        def actor(self,role,record,interactive=False):
            def observed(point,partial,error):
                key='constructor_before_reap'if point=='BEFORE_REAP'else'constructor_after_reap'
                record[key]=native['session_observation'](partial)
                if error is not None:record.setdefault('original_operation_failure',self.failure_metadata(error,'CONSTRUCT'))
                self.persist()
            return (Interactive if interactive else native['Session'])(role,self.cid,self.api,self.raw,observed)

        def close_actor(self,session,record):
            record['session_before_close']=native['session_observation'](session);self.persist()
            try:session.close();record['closed_before_observers']=True
            except BaseException as error:
                record['close_failure']=self.failure_metadata(error,'CLOSE');record['closed_before_observers']=False
            finally:record['session_after_close']=native['session_observation'](session);self.persist()
            return record['closed_before_observers']

        def grants_unchanged(self,require_current=False):
            # Complete values are compared by the server and stay in RAM/SQL.
            # No returned grant, timestamp, token, backend tuple or ID is saved.
            for instance in self.grants.values():
                expected='jsonb_build_object('+','.join(quote(column)+','+instance['values'][column]for column in P.GRANT_COLUMNS)+')'
                query="SELECT jsonb_build_object('count',count(*),'complete_row_matches',coalesce(bool_and(to_jsonb(g)="+expected+"),false),'unexpired',coalesce(bool_and(expires_at>clock_timestamp()),false)) FROM platform.database_action_grant g WHERE id="+quote(instance['id'])+'::uuid;'
                value=self.json(query);good=type(value)is dict and set(value)=={'count','complete_row_matches','unexpired'}and type(value['count'])is int and value['count']==1 and value['complete_row_matches']is True and type(value['unexpired'])is bool
                if require_current:good=good and value['unexpired']is True
                observed=value.get('count')if type(value)is dict else None
                self.evidence.value['current'].setdefault('private_grant_checks',[]).append({'expected_count':1,'observed_count':observed if type(observed)is int and 0<=observed<=1000000000 else None,'complete_known_row_matches':bool(good),'unexpired_required':require_current,'unexpired':value.get('unexpired')is True if type(value)is dict else False})
                need(self.persist(),'EVIDENCE_INCOMPLETE');need(good,'PRIVATE_GRANT_STATE_MISMATCH')
            total=self.json("SELECT jsonb_build_object('count',count(*)) FROM platform.database_action_grant;")
            expected_total=self.setup_counts['platform.database_action_grant']+len(self.grants);good=type(total)is dict and set(total)=={'count'}and type(total['count'])is int and total['count']==expected_total
            observed=total.get('count')if type(total)is dict else None
            self.evidence.value['current']['grant_total_check']={'expected_count':expected_total,'observed_count':observed if type(observed)is int and 0<=observed<=1000000000 else None,'matches':bool(good)}
            need(self.persist(),'EVIDENCE_INCOMPLETE');need(good,'PRIVATE_GRANT_STATE_MISMATCH')

        def after_case(self,label,require_current=False):
            self.global_closed(label);self.guards();self.fingerprint();self.grants_unchanged(require_current);self.catalog()

        def metadata(self,case):
            role=case['role'];kind=case['diagnostic']['kind'];schema=case['diagnostic'].get('schema')
            if kind in('IMMUTABLE_GRANT','BIND_CURRENTNESS'):return {}
            if kind=='SET_ROLE':
                target=case['diagnostic']['target_role'];query="SELECT jsonb_build_object('role_assumption_allowed',pg_has_role("+quote(role)+','+quote(target)+",'SET'));";expected={'role_assumption_allowed':False}
            elif kind=='SCHEMA_CREATE':
                query="SELECT jsonb_build_object('schema_usage',has_schema_privilege("+quote(role)+','+quote(schema)+",'USAGE'),'schema_create',has_schema_privilege("+quote(role)+','+quote(schema)+",'CREATE'));"
                expected={'schema_usage':P.expected_acl(self.native,role,'SCHEMA',schema,'USAGE'),'schema_create':P.expected_acl(self.native,role,'SCHEMA',schema,'CREATE')}
                need(expected['schema_create']is False,'SOURCE_NATIVE_METADATA_REQUIRED')
            elif kind=='FUNCTION':
                name=case['diagnostic']['function'];matches=[row for row in self.native['functions']if row['name']==schema+'.'+name]
                need(len(matches)==1,'SOURCE_NATIVE_METADATA_REQUIRED');identity=matches[0]['object']
                query="SELECT jsonb_build_object('schema_usage',has_schema_privilege("+quote(role)+','+quote(schema)+",'USAGE'),'function_execute',has_function_privilege("+quote(role)+','+quote(identity)+",'EXECUTE'));"
                expected={'schema_usage':P.expected_acl(self.native,role,'SCHEMA',schema,'USAGE'),'function_execute':P.expected_acl(self.native,role,'FUNCTION',identity,'EXECUTE')}
                need(expected['function_execute']is False,'SOURCE_NATIVE_METADATA_REQUIRED')
            else:
                name=case.get('table',schema+'.'+case['diagnostic']['relation']);verb=case.get('verb','SELECT');columns=case.get('referenced_columns',[])
                if case.get('native_probe',{}).get('native_forbidden_column')not in(None,*columns):columns=columns+[case['native_probe']['native_forbidden_column']]
                expected={'schema_usage':P.expected_acl(self.native,role,'SCHEMA',schema,'USAGE'),'table_privilege':P.expected_acl(self.native,role,'TABLE',name,verb),'columns':{column:P.expected_acl(self.native,role,'TABLE',name,verb,column)for column in columns}}
                column_sql='jsonb_build_object('+','.join(quote(column)+',has_column_privilege('+quote(role)+','+quote(name)+','+quote(column)+','+quote(verb)+')'for column in columns)+')'if columns else"'{}'::jsonb"
                query="SELECT jsonb_build_object('schema_usage',has_schema_privilege("+quote(role)+','+quote(schema)+",'USAGE'),'table_privilege',has_table_privilege("+quote(role)+','+quote(name)+','+quote(verb)+"),'columns',"+column_sql+');'
            actual=self.json(query);need(canonical(actual)==canonical(expected),'SOURCE_NATIVE_METADATA_REQUIRED')
            result=deepcopy(expected)
            if 'table_privilege'in result:
                result['missing_referenced_columns']=[column for column,allowed in result['columns'].items()if allowed is False]
                result['required_permission_missing']=result['table_privilege']is False and(not result['columns']or bool(result['missing_referenced_columns']))
                result.pop('columns');result['column_privilege_projection_matches_source']=True
            self.evidence.value['current']['source_native_privilege_projection']=deepcopy(result);need(self.persist(),'EVIDENCE_INCOMPLETE');return result

        def template(self,case):return self.source_blobs[PACKET+'/'+case['file']].decode()

        def unexpected_metadata(self,errors,record):
            metadata=None
            if type(errors)is str and len(errors)<=16384 and native['clean_text'](errors)is not None:
                try:metadata=self.api['source_metadata'](errors)
                except BaseException:pass
            record['unexpected_operation_diagnostic']=native['unexpected_operation_metadata'](errors,self.native,APPLICATION_SHA,metadata,unique_json(self.blobs['__diagnostic_identifiers']))
            self.persist()

        def changed_grant_expression(self,column):
            need(self.person is not None,'CURRENT_OWN_GRANT_REQUIRED')
            original=self.person['values'];source=self.privileges_packet['person_grant']
            old_pid=int(self.person['backend']['pid']);new_pid=1 if old_pid==2147483647 else old_pid+1
            values={'id':str(uuid.uuid4()),'token_hash':sha(secrets.token_bytes(32)),'issuer_service':'wa_app_runtime','principal_user_id':self.packet['synthetic_facts']['delete-leaf/User']['app.users']['id'],'service_principal':self.privileges_packet['revoked_service_fixture']['service_principal'],'database_login_role':'wa_worker','owner_module_id':'platform_integration_owner','action':'runtime.claim_work.v1','purpose':'work.claim','target_kind':'User','target_id':source['principal_user_id'],'allowed_fields':['CustomerProfile/'+source['target_id']+'/SELECT/userId'],'policy_version':'privilege-ceiling.other.v1','security_generation':source['security_generation']+1,'source_generation':source['source_generation']+1,'backend_pid':new_pid,'transaction_id':str(int(self.person['backend']['xid'])+1),'mutation_transaction_id':str(int(self.person['issuer_xid'])+1)}
            if column in('expires_at','created_at'):return '('+original[column]+")+interval '1 second'"
            need(column in values,'UNRESOLVED_SQL_TEMPLATE')
            return P.typed(values[column],self.privileges_packet['grant_column_types'][column])

        def render(self,case,backend):
            text=P.reviewed_text(self.template(case),self.review_plan['run_id'])
            operation=case.get('operation')
            if operation=='GRANT_INSERT':
                source=self.privileges_packet['person_grant'];role=case['role']
                need(backend['login']==backend['current_user']==role and role in P.APP_ROLES,'SAME_APP_TUPLE_REQUIRED')
                values={'id':str(uuid.uuid4()),'token_hash':sha(secrets.token_bytes(32)),'issuer_service':role,'principal_user_id':source['principal_user_id'],'service_principal':None,'database_login_role':role,'owner_module_id':source['owner_module_id'],'action':source['action'],'purpose':source['purpose'],'target_kind':source['target_kind'],'target_id':source['target_id'],'allowed_fields':source['allowed_fields'],'policy_version':source['policy_version'],'security_generation':source['security_generation'],'source_generation':source['source_generation'],'backend_pid':int(backend['pid']),'transaction_id':backend['xid'],'expires_at':None,'revoked_at':None,'created_at':None,'mutation_transaction_id':backend['xid']}
                for column in P.GRANT_COLUMNS:
                    spec=self.privileges_packet['grant_column_types'][column];kind=spec['name']+('[]'if spec['array_dimensions']else'')
                    needle="'__WA_"+column.upper()+"__'::"+kind;need(text.count(needle)==1,'UNRESOLVED_SQL_TEMPLATE')
                    expression="clock_timestamp()+interval '300 seconds'"if column=='expires_at'else'clock_timestamp()'if column=='created_at'else P.typed(values[column],spec)
                    text=text.replace(needle,expression)
            elif operation=='GRANT_FIELD_UPDATE':
                need(self.person is not None and self.person['revoked']is False,'CURRENT_OWN_GRANT_REQUIRED');column=case['field'];spec=self.privileges_packet['grant_column_types'][column]
                needle="'__WA_CHANGED_VALUE__'::"+spec['name']+('[]'if spec['array_dimensions']else'');need(text.count(needle)==1,'UNRESOLVED_SQL_TEMPLATE')
                text=text.replace(needle,self.changed_grant_expression(column))
            if '__WA_OWN_GRANT_ID__'in text:
                need(self.person is not None,'CURRENT_OWN_GRANT_REQUIRED')
                if case.get('actual_revoked_own_grant_required'):need(self.person['revoked']is True,'CURRENT_OWN_GRANT_REQUIRED')
                if case.get('actual_unrevoked_own_grant_required'):need(self.person['revoked']is False,'CURRENT_OWN_GRANT_REQUIRED')
                text=text.replace('__WA_OWN_GRANT_ID__',self.person['id'])
            need('__WA_'not in text,'UNRESOLVED_SQL_TEMPLATE');return text

        def negative(self,case):
            record={'name':case['name'],'role':case['role'],'source_template_sha256':case['sql_sha256'],'closed_before_observers':False}
            self.evidence.value['current']=record;self.evidence.value['current_case']=case['name'];self.evidence.value['current_stage']='PRIVILEGE_METADATA'
            need(self.persist(),'EVIDENCE_INCOMPLETE');self.global_closed('BEFORE_'+case['name']);metadata=self.metadata(case)
            actor=None;failure=None;phase='CONSTRUCT';matched=False
            try:
                actor=self.actor(case['role'],record);phase='CAPTURE';actor.capture();record['actual_login_context_absent']=True
                text=self.render(case,actor.backend);need('__WA_'not in text,'UNRESOLVED_SQL_TEMPLATE');record['executed_sql_sha256']=sha(text.encode());phase='FINISH'
                need(self.persist(),'EVIDENCE_INCOMPLETE');code,rows,ack,errors=actor.finish(native['captured_tail'](text))
                record.update(exit_code=code if type(code)is int and -255<=code<=255 else None,acknowledgement=ack is True,exact_empty_output=type(rows)is list and rows==[])
                verdict=P.diagnostic(errors,case['diagnostic'],metadata,text,P.source_position_matches);record['diagnostic']=verdict
                if verdict['matched']is not True:self.unexpected_metadata(errors,record)
                phase='VERDICT';need(self.persist(),'EVIDENCE_INCOMPLETE');matched=type(code)is int and code==3 and ack is False and rows==[]and verdict['matched']is True
                need(matched,'INTENDED_PRIVILEGE_GUARD_NOT_PROVEN')
            except BaseException as error:
                failure=error;record.setdefault('original_operation_failure',self.failure_metadata(error,phase));self.persist()
            finally:
                self.evidence.value['current_stage']='CLOSE_'+case['name'];self.persist()
                if actor is not None:self.close_actor(actor,record)
                self.evidence.value['operations'].append(record);self.persist()
                record['global_client_closure_confirmed']=False
                try:self.global_closed('AFTER_OPERATION_'+case['name']);record['global_client_closure_confirmed']=True
                except BaseException as error:
                    record.setdefault('global_closure_failure',self.failure_metadata(error,'CLOSE'));self.persist()
                    if failure is None:failure=error
            if not record['closed_before_observers']:raise Held('OPERATION_BACKEND_CLOSURE_UNCONFIRMED')from None
            if not record['global_client_closure_confirmed']:raise Held('GLOBAL_CLIENT_CLOSURE_UNCONFIRMED')from None
            if not self.failed:
                try:self.after_case('AFTER_'+case['name'],case['family']in('ISSUER_COLUMN_CEILING','ISSUER_UNREVOKED_GUARD'))
                except BaseException as error:
                    record['post_case_state_verified']=False;record.setdefault('observation_failure',self.failure_metadata(error,'VERDICT'));self.persist()
                    if failure is None:failure=error
                else:record['post_case_state_verified']=True
            if self.failed:raise Held('EVIDENCE_INCOMPLETE')from None
            if failure is not None:raise Held('INTENDED_PRIVILEGE_GUARD_NOT_PROVEN')from None
            self.evidence.value['results'].append({'name':case['name'],'source_case_id':case['source_case_id'],'assertion_id':case['assertion_id'],'status':'PASS_FINITE_PRIVILEGE_CONTRAST_ONLY','closed_before_observers':True,'complete_state_unchanged':True,'diagnostic':record['diagnostic'],'whole_case_promoted':False});need(self.persist(),'EVIDENCE_INCOMPLETE')

        def clock(self,session):
            rows,ack,errors=session.call("SELECT jsonb_build_object('clock',CURRENT_TIMESTAMP::text);")
            checks={'acknowledged':ack is True,'stderr_empty':errors=='','one_row':type(rows)is list and len(rows)==1,'exact_fields':False,'clock_format_and_timezone':False}
            value=None
            if checks['one_row']:
                try:value=unique_json(rows[0])
                except BaseException:pass
            checks['exact_fields']=type(value)is dict and set(value)=={'clock'}
            if checks['exact_fields']and type(value['clock'])is str and re.fullmatch(r'[0-9T:+. \-]{1,64}',value['clock']):
                try:checks['clock_format_and_timezone']=datetime.datetime.fromisoformat(value['clock']).utcoffset()is not None
                except BaseException:pass
            record=self.evidence.value['current'];record['clock_comparison']=checks
            if errors:self.unexpected_metadata(errors,record)
            need(self.persist(),'EVIDENCE_INCOMPLETE');need(all(checks.values()),'INTERACTIVE_OUTPUT_UNCONFIRMED')
            return value['clock']

        def issue(self,template,backend,actors,record):
            need(len(self.grants)<2,'CURRENT_OWN_GRANT_REQUIRED')
            actor_record={'role':'wa_context_issuer','closed_before_observers':False};record['actors'].append(actor_record)
            issuer=self.actor('wa_context_issuer',actor_record,True);actors.append((issuer,actor_record));issuer.capture();actor_record['actual_login_context_absent']=True;clock=self.clock(issuer)
            identity=str(uuid.uuid4());secret=secrets.token_hex(32);token_hash=sha(bytes.fromhex(secret))
            values=ctx['Coordinator'].grant_values(None,template,backend,{**issuer.backend,'clock':clock},identity,token_hash)
            foreign=self.packet['synthetic_facts']['foreign-issuer-negative-only']['platform.database_action_grant']['id']
            insert='INSERT INTO platform.database_action_grant('+','.join(P.GRANT_COLUMNS)+') VALUES ('+','.join(values[column]for column in P.GRANT_COLUMNS)+") RETURNING jsonb_build_object('created_at',created_at);"
            own="SELECT jsonb_build_object('own',(SELECT count(*) FROM platform.database_action_grant WHERE id="+quote(identity)+"::uuid),'foreign',(SELECT count(*) FROM platform.database_action_grant WHERE id="+quote(foreign)+'::uuid)); COMMIT;'
            record['issuer_statement_sha256']=sha((insert+own).encode());need(self.persist(),'EVIDENCE_INCOMPLETE')
            rows,ack,errors=issuer.call(insert+'\n'+own)
            if errors:self.unexpected_metadata(errors,record)
            record.update(issuer_COMMIT_acknowledged=ack is True and errors=='',created_at_source_return_verified=False,issuer_return_count=len(rows)if type(rows)is list and len(rows)<=256 else None)
            need(self.persist(),'EVIDENCE_INCOMPLETE')
            need(ack is True and errors==''and len(rows)==2,'ISSUER_COMMIT_UNCONFIRMED')
            actual=ctx['returned_created_at'](rows[:1],clock);need(canonical(unique_json(rows[1]))==canonical({'own':1,'foreign':0}),'ISSUER_OWN_READ_REQUIRED')
            values['created_at']=quote(actual)+'::timestamptz'
            instance={'id':identity,'secret':secret,'token_hash':token_hash,'values':values,'backend':deepcopy(backend),'issuer_xid':issuer.backend['xid'],'revoked':False,'login':template['database_login_role']}
            self.grants[identity]=instance
            record.update(issuer_COMMIT_acknowledged=True,created_at_source_return_verified=True,own_grant_visible=True,foreign_grant_hidden=True)
            need(self.persist(),'EVIDENCE_INCOMPLETE')
            need(self.close_actor(issuer,actor_record),'OPERATION_BACKEND_CLOSURE_UNCONFIRMED')
            return instance

        def interactive_case(self,label,role,behavior):
            record={'name':label,'role':role,'source_case_id':'P0C-PRIV-01','assertion_id':'control.issuer_ceiling','actors':[],'closed_before_observers':False}
            self.evidence.value['current']=record;self.evidence.value['current_case']=label;self.evidence.value['current_stage']=label
            need(self.persist(),'EVIDENCE_INCOMPLETE');self.global_closed('BEFORE_'+label)
            actors=[];failure=None;result=None;phase='CONSTRUCT'
            try:
                actor_record={'role':role,'closed_before_observers':False};record['actors'].append(actor_record)
                actor=self.actor(role,actor_record,True);actors.append((actor,actor_record));phase='CAPTURE';actor.capture();actor_record['actual_login_context_absent']=True
                phase='FINISH';result=behavior(actor,actors,record)
            except BaseException as error:
                failure=error;record.setdefault('original_operation_failure',self.failure_metadata(error,phase));self.persist()
            finally:
                self.evidence.value['current_stage']='CLOSE_'+label;self.persist()
                for actor,actor_record in reversed(actors):
                    if actor_record['closed_before_observers']is not True:self.close_actor(actor,actor_record)
                record['closed_before_observers']=bool(record['actors'])and all(item['closed_before_observers']is True for item in record['actors'])
                self.evidence.value['operations'].append(record);self.persist()
                record['global_client_closure_confirmed']=False
                try:self.global_closed('AFTER_OPERATION_'+label);record['global_client_closure_confirmed']=True
                except BaseException as error:
                    record.setdefault('global_closure_failure',self.failure_metadata(error,'CLOSE'));self.persist()
                    if failure is None:failure=error
            if not record['closed_before_observers']:raise Held('OPERATION_BACKEND_CLOSURE_UNCONFIRMED')from None
            if not record['global_client_closure_confirmed']:raise Held('GLOBAL_CLIENT_CLOSURE_UNCONFIRMED')from None
            if not self.failed:
                try:self.after_case('AFTER_'+label)
                except BaseException as error:
                    record['post_case_state_verified']=False;record.setdefault('observation_failure',self.failure_metadata(error,'VERDICT'));self.persist()
                    if failure is None:failure=error
                else:record['post_case_state_verified']=True
            if self.failed:raise Held('EVIDENCE_INCOMPLETE')from None
            if failure is not None:raise Held('INTERACTIVE_OUTPUT_UNCONFIRMED')from None
            self.evidence.value.setdefault('issuer_protocols',[]).append({'name':label,'status':'PASS_FINITE_ISSUER_PROTOCOL_ONLY','same_run_and_actual_logins':True,'all_operation_backends_closed_before_observation':True,'complete_state_verified':True,'whole_case_promoted':False});need(self.persist(),'EVIDENCE_INCOMPLETE')
            return result

        def person_binding(self):
            template=self.privileges_packet['person_grant']
            def behavior(app,actors,record):
                instance=self.issue(template,app.backend,actors,record);self.person=instance
                bind='SELECT platform_private.bind_request_context('+quote(instance['secret'])+');'
                expression="SELECT jsonb_build_object('allowed',platform_private.context_allows("+','.join(quote(template[key])for key in('owner_module_id','action','target_kind','target_id','purpose'))+"),'subject',platform_private.context_subject_owner("+quote(template['principal_user_id'])+"::uuid,"+quote(template['owner_module_id'])+"),'same_tuple',pg_backend_pid()="+app.backend['pid']+' AND pg_current_xact_id()::text='+quote(app.backend['xid'])+');'
                outcomes=[]
                for path in ('pg_catalog','public,app,platform,platform_private,pg_catalog'):
                    rows,ack,errors=app.call('SET LOCAL search_path='+path+';\n'+bind+'\n'+bind+'\n'+expression)
                    checks=person_binding_comparison(rows,ack,errors);good=all(value is True for value in checks.values())
                    outcomes.append(good);record['caller_path_comparisons']=list(outcomes);record.setdefault('caller_path_comparison_outcomes',[]).append(checks)
                    need(self.persist(),'EVIDENCE_INCOMPLETE')
                    if type(errors)is str and errors:self.unexpected_metadata(errors,record)
                    need(good,'SAME_APP_TUPLE_REQUIRED')
                rows,ack,errors=app.call('ROLLBACK;');need(ack is True and rows==[]and errors=='','INTERACTIVE_OUTPUT_UNCONFIRMED')
                record['same_app_tuple_and_separate_issuer_COMMIT']=True
            self.interactive_case('ISSUER-LEGITIMATE-PERSON-ISSUE-OWN-READ-BOUND-SCALARS','wa_app_runtime',behavior)

        def revoke_person(self):
            need(self.person is not None and self.person['revoked']is False,'CURRENT_OWN_GRANT_REQUIRED')
            def behavior(issuer,actors,record):
                clock=self.clock(issuer);text='UPDATE platform.database_action_grant SET revoked_at=clock_timestamp() WHERE id='+quote(self.person['id'])+"::uuid RETURNING jsonb_build_object('created_at',revoked_at); COMMIT;"
                record['issuer_statement_sha256']=sha(text.encode());need(self.persist(),'EVIDENCE_INCOMPLETE');rows,ack,errors=issuer.call(text)
                if errors:self.unexpected_metadata(errors,record)
                record.update(first_revoke_COMMIT_acknowledged=ack is True and errors=='',source_mutated_timestamp_verified=False);need(self.persist(),'EVIDENCE_INCOMPLETE')
                need(ack is True and errors==''and len(rows)==1,'EXPECTED_FIRST_REVOKE_REQUIRED');actual=ctx['returned_created_at'](rows,clock)
                self.person['values']['revoked_at']=quote(actual)+'::timestamptz';self.person['values']['mutation_transaction_id']=quote(issuer.backend['xid']);self.person['revoked']=True
                record.update(first_revoke_COMMIT_acknowledged=True,source_mutated_timestamp_verified=True)
            self.interactive_case('ISSUER-LEGITIMATE-FIRST-ONE-WAY-REVOKE','wa_context_issuer',behavior)

        def service_binding_denied(self):
            fixture=self.privileges_packet['revoked_service_fixture'];work=self.packet['synthetic_facts']['baseline']['platform.runtime_work_item']
            def behavior(worker,actors,record):
                # A real stored, committed tuple targets this exact live worker.
                # The known Identity authority row remains independently revoked.
                template={'database_login_role':'wa_worker','principal_user_id':None,'service_principal':fixture['service_principal'],'owner_module_id':'platform_integration_owner','action':'runtime.claim_work.v1','purpose':'work.claim','target_kind':'RuntimeWorkItem','target_id':work['id'],'policy_version':'privilege-ceiling-fixture.v1','security_generation':fixture['security_generation'],'source_generation':0,'allowed_fields':['RuntimeWorkItem/'+work['id']+'/SELECT/id']}
                instance=self.issue(template,worker.backend,actors,record)
                value=self.json("SELECT jsonb_build_object('count',count(*),'revoked',coalesce(bool_and(revoked_at IS NOT NULL),false),'generation_matches',coalesce(bool_and(security_generation="+str(fixture['security_generation'])+"),false)) FROM platform_private.identity_service_authorization WHERE service_principal="+quote(fixture['service_principal'])+';')
                good=canonical(value)==canonical({'count':1,'revoked':True,'generation_matches':True});record['known_revoked_identity_source_witness']=good;need(self.persist(),'EVIDENCE_INCOMPLETE');need(good,'GRANT_NOT_SOURCE_CURRENT')
                text='SELECT platform_private.bind_request_context('+quote(instance['secret'])+');\nROLLBACK;';record['restricted_statement_sha256']=sha(text.encode())
                code,rows,ack,errors=worker.finish(text)
                verdict=P.diagnostic(errors,self.privileges_packet['bind_currentness_diagnostic'],{},text,P.source_position_matches);record['diagnostic']=verdict
                if verdict['matched']is not True:self.unexpected_metadata(errors,record)
                need(type(code)is int and code==3 and ack is False and rows==[]and verdict['matched']is True,'INTENDED_PRIVILEGE_GUARD_NOT_PROVEN')
                record['issuer_did_not_manufacture_service_currentness']=True
            self.interactive_case('ISSUER-STORED-SERVICE-GRANT-CANNOT-SELF-ATTEST-REVOKED-IDENTITY','wa_worker',behavior)

        def metadata_preflight(self):
            self.global_closed('PRIVILEGE_METADATA_PREFLIGHT');self.catalog()
            outcomes=P.source_metadata_contract(self.native,self.privileges_packet['source_definers'])
            self.evidence.value['definer_metadata']=outcomes;need(self.persist(),'EVIDENCE_INCOMPLETE')
            need(len(outcomes)==16 and all(row['owner_body_definer_path_match']is True for row in outcomes),'SOURCE_NATIVE_METADATA_REQUIRED')
            roles={row['name']:row for row in self.native['roles']}
            leaves=('wa_private_helper_owner','wa_customer_verifier','wa_track_verifier');owners=('wa_schema_owner',*leaves)
            fields=('rolcanlogin','rolinherit','rolsuper','rolcreaterole','rolcreatedb','rolreplication','rolbypassrls')
            flags={name:type(roles.get(name))is dict and all(roles[name].get(key)is False for key in fields)for name in owners}
            expected=[{'role':'wa_schema_owner','member':'wa_migrator','grantor':'postgres','admin':False,'inherit':False,'set':True}]
            memberships=canonical(self.native['memberships'])==canonical(expected)
            query='SELECT jsonb_build_object('+','.join(quote(name)+',has_schema_privilege('+quote(name)+",'platform_private','CREATE')"for name in leaves)+');'
            actual=self.json(query);create=canonical(actual)==canonical(dict.fromkeys(leaves,False))
            self.evidence.value['role_metadata']={'four_owner_roles_NOLOGIN_NOINHERIT_nonprivileged':flags,'exact_permanent_migrator_edge_and_zero_temporary_edges':memberships,'all_three_leaf_CREATE_false':create,'direct_NOLOGIN_startup_guard_exercised':False,'function_body_catalog_confidentiality_claimed':False}
            need(self.persist(),'EVIDENCE_INCOMPLETE');need(all(flags.values())and memberships and create,'SOURCE_NATIVE_METADATA_REQUIRED')

        def setup_facts(self):
            self.preflight();self.global_closed('BEFORE_EXACT_NATIVE_FACT_SETUP')
            self.operation('native-fact-setup','postgres',self.text('native-fact-setup.sql'),expected=[{'control':'all-native-fact-setup-triggers-restored','all_declared_user_triggers_restored':True}])
            self.seeded=True;self.guards();self.baseline=self.fingerprint();self.catalog()
            for case in self.packet['cases']:
                self.evidence.value['current_case']=case['id'];text=self.text(case['native_controls'])
                need('\nCOMMIT;'not in text and text.count('\nROLLBACK;')==1 and all(row['table']==case['table']for row in case['control_bypassed_user_triggers']),'EXACT_NATIVE_ROLLBACK_VALIDITY_REQUIRED')
                expected=['t']*(2+len(case['native_update_control_columns']))+[{'control':'native-control-'+case['model'],'all_declared_user_triggers_restored':True}]
                self.operation('native-control-'+case['model'],'postgres',text,expected=expected);self.after_case('AFTER_NATIVE_VALIDITY_'+case['model'])
                self.evidence.value['native_controls'].append({'case_id':case['id'],'status':'NATIVE_FIXTURE_VALIDITY_ONLY_NO_OWNER_OR_CASE_QUALIFICATION','rolled_back':True,'all100_guards_restored':True,'native205_unchanged':True});need(self.persist(),'EVIDENCE_INCOMPLETE')

        def run(self):
            self.setup_facts();self.metadata_preflight();self.person_binding()
            cases=self.privileges_packet['cases'];executed=[]
            def group(family):
                for case in cases:
                    if case['family']==family:self.negative(case);executed.append(case['name'])
            group('ISSUER_COLUMN_CEILING');group('ISSUER_UNREVOKED_GUARD');self.revoke_person();group('ISSUER_GRANT_GUARD')
            group('RUNTIME_ESCALATION');group('HELPER_RESULT_CEILING');group('ISSUER_IDENTITY_SOURCE_CEILING');self.service_binding_denied()
            group('ISSUER_BUSINESS_DML');group('PROVIDER_REACHABILITY')
            need(len(executed)==200 and set(executed)=={case['name']for case in cases}and len(self.evidence.value['results'])==200,'EXACT_FINITE_CASE_SET_REQUIRED')
            self.after_case('FINAL_PRIVILEGE_SOURCE_STATE')
            for name,wanted in self.review_plan['packet_files_sha256'].items():need(sha(source_path(name).read_bytes())==wanted,'POST_RUN_SOURCE_DRIFT')
            self.evidence.value.update(status='PASS_PREPARED_PRIVILEGE_CEILINGS_ONLY_CASES_NOT_RUN',source_packet_unchanged_after=True,subsequent_cases_stopped=False)
            self.evidence.stage('FINISHED')
    return Runner


SAFE_FAILURES=frozenset({'PLAN_SCOPE','SOURCE_RUN_IDENTITY','FULL_SOURCE_HASH_MAP','FULL_SOURCE_AGGREGATE','REQUIRED_SOURCE_CLOSURE_MISSING','FULL_SOURCE_DRIFT','EXACT_REVIEWED_TRANSPORTS','FIXTURE_SOURCE_IDENTITY','FINITE_PRIVILEGE_SCOPE','FINITE_CONTENT_AGGREGATE','PACKET_SOURCE_NOT_ADMITTED','FINITE_SQL_NAME','PACKET_SQL_NOT_ADMITTED','CANONICAL_UNCHANGED_INPUTS','SOURCE_MODULE_OUTPUT_REFUSED','MODULE_NOT_ADMITTED','EXACT_SOURCE_PACKET_REPRODUCTION','SAME_RUN_NATIVE_PLAN','NATIVE_HELPER_FULL_PACKET_BINDING','FULL_NATIVE_ORACLE_LEDGER_PREREQUISITE','GLOBAL_CLIENT_CLOSURE_UNCONFIRMED','EVIDENCE_INCOMPLETE','OPERATION_BACKEND_CLOSURE_UNCONFIRMED','INTENDED_PRIVILEGE_GUARD_NOT_PROVEN','INTERACTIVE_OUTPUT_UNCONFIRMED','PRIVATE_GRANT_STATE_MISMATCH','SOURCE_NATIVE_METADATA_REQUIRED','EXACT_FINITE_CASE_SET_REQUIRED','POST_RUN_SOURCE_DRIFT','EXACT_NATIVE_ROLLBACK_VALIDITY_REQUIRED','SOURCE_PATH','SOURCE_PATH_ESCAPE','ASSET_REFERENCE_FIELDS','EXTERNAL_ASSET_DRIFT','DUPLICATE_JSON_KEY','NONFINITE_JSON','EXTERNAL_ABSOLUTE_PATH','EXTERNAL_TASK_PATH'})


def main(argv=None):
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--execute-reviewed-privilege-ceilings',action='store_true',required=True)
    parser.add_argument('--run-plan',type=Path,required=True);parser.add_argument('--evidence-directory',type=Path,required=True)
    args=parser.parse_args(argv);evidence=None
    try:
        directory=external_path(args.evidence_directory);need(not directory.exists(),'FRESH_EVIDENCE_DIRECTORY')
        evidence=Evidence(directory,{'control_links':[]});evidence.stage('VERIFY_REVIEWED_INPUTS')
        raw=external_path(args.run_plan).read_bytes();plan=unique_json(raw)
        packet,blobs,protocol,native,ctx,native_packet,native_blobs,snapshot,api,host=load_inputs(plan)
        evidence.value.update(run_id=plan['run_id'],source_commit=plan['source_commit'],source_tree=plan['source_tree'],operation_packet_sha256=plan['packet_sha256'],reviewed_privilege_content_sha256=packet['source_only_packet_sha256'],run_plan_sha256=sha(raw),selected_controls=deepcopy(packet['control_links']))
        evidence.save();Runner=runner_type(native,ctx,protocol)
        Runner(plan,packet,blobs,native_packet,native_blobs,snapshot,api,host,evidence).run();return 0
    except BaseException as error:
        if evidence is not None:
            try:code=error.code if isinstance(error,Held)and type(error.code)is str and error.code in SAFE_FAILURES else'UNEXPECTED_PRIVILEGE_CONTROL_FAILURE'
            except BaseException:code='UNEXPECTED_PRIVILEGE_CONTROL_FAILURE'
            evidence.value.update(status='STOPPED_PARTIAL_EVIDENCE_PRESERVED',subsequent_cases_stopped=True,failure={'stage':evidence.value['current_stage'],'code':code})
            try:evidence.save()
            except BaseException:evidence.value['evidence_complete']=False
        return 2


if __name__=='__main__':raise SystemExit(main())
