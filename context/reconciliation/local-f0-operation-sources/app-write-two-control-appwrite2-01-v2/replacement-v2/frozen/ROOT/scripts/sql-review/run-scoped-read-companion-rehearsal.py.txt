"""Dormant finite scoped-read-companion coordinator. Import/help execute no process.

Only Root's separately reviewed same-source/run/CID/native packet may execute.
No provisioning, cleanup, repair, migration, owner adapter or worker loop lives here.
"""
import argparse
from copy import deepcopy
import hashlib
import io
import json
import os
from pathlib import Path
import re
import secrets
import subprocess
from contextlib import redirect_stdout,redirect_stderr
import uuid

ROOT=Path(__file__).resolve().parents[2]
TASK=ROOT.parent
PACKET=ROOT/'review-output/scoped-read-companion-rehearsal'
SELF='scripts/sql-review/run-scoped-read-companion-rehearsal.py'
PROTOCOL='scripts/scoped_read_companion_protocol.py'
CONTEXT='scripts/sql-review/run-context-control-rehearsal.py'
COLLECTOR='scripts/sql-review/collect_native_catalog.sql'
HELPERS=(CONTEXT,'scripts/sql-review/run-first-rehearsal.py','scripts/sql-review/run-local-f0-migrate.py','scripts/sql-review/rehearsal-diagnostics.py','scripts/prepare-local-f0-history.py')
EXPECTED_CATALOG='3be81a13d3bb2abb41bf03ef68398da6d92fbdbccffec3d74508e91dd455f433'
APPLICATION='review-output/foundation-application.review.sql'
APPLICATION_SHA='5ae39abf991f9c189e367eb6ab6968b0ad50836bf4220ac27ef8c18306ac26ad'

class HeldFailure(Exception):
 def __init__(self,code):self.code=code;super().__init__(code)

def need(value,code):
 if not value:raise HeldFailure(code)

def sha(raw):return hashlib.sha256(raw).hexdigest()
def canonical(v):return json.dumps(v,sort_keys=True,separators=(',',':'),ensure_ascii=False,allow_nan=False)
def digest(v):return sha(canonical(v).encode())
def quote(v):return "'"+str(v).replace("'","''")+"'"

def unique_json(raw):
 def pairs(items):
  value={}
  for key,item in items:need(key not in value,'DUPLICATE_JSON_FIELD');value[key]=item
  return value
 try:return json.loads(raw,object_pairs_hook=pairs,parse_constant=lambda _:(_ for _ in ()).throw(HeldFailure('NONFINITE_JSON')))
 except HeldFailure:raise
 except BaseException:raise HeldFailure('MALFORMED_JSON') from None

def source_path(relative):
 need(type(relative) is str and '\\' not in relative and ':' not in relative and not relative.startswith('/') and all(p not in ('','.','..') for p in relative.split('/')),'SOURCE_PATH')
 path=(ROOT/relative).resolve();need(path.is_relative_to(ROOT.resolve()),'SOURCE_PATH_ESCAPE');return path

def external(value):
 path=Path(value);need(path.is_absolute(),'EXTERNAL_ABSOLUTE_PATH');path=path.resolve()
 need(path.is_relative_to(TASK.resolve()) and not path.is_relative_to(ROOT.resolve()),'EXTERNAL_TASK_PATH');return path

def checked_source(relative,pins):
 need(relative in pins,'SOURCE_NOT_ADMITTED')
 try:raw=source_path(relative).read_bytes()
 except OSError:raise HeldFailure('SOURCE_FILE_UNAVAILABLE') from None
 need(sha(raw)==pins[relative],'SOURCE_FILE_DRIFT');return raw

def checked_sql(packet,name):
 need(type(name) is str and Path(name).name==name and name in packet['prepared_files_sha256'],'FIXED_SQL_NAME')
 raw=(PACKET/name).read_bytes();need(sha(raw)==packet['prepared_files_sha256'][name],'PREPARED_SQL_DRIFT');return raw.decode('utf8')

def compiled(raw,relative):
 namespace={'__name__':'_owner_read_reviewed','__file__':str(source_path(relative))};output=io.StringIO()
 try:
  with redirect_stdout(output),redirect_stderr(output):exec(compile(raw,str(source_path(relative)),'exec'),namespace)
 except BaseException:raise HeldFailure('VERIFIED_MODULE_LOAD_REFUSED') from None
 need(not output.getvalue(),'VERIFIED_MODULE_OUTPUT_REFUSED');return namespace

def load_inputs(plan):
 keys={'schema','scope','run_id','source_commit','source_tree','packet_sha256','packet_files_sha256','reviewed_packet_sha256','reviewed_content_sha256','target_manifest','immutable_container_id','native_snapshot','native_comparison','native_attestation','scenario_names'}
 need(type(plan) is dict and set(plan)==keys,'RUN_PLAN_FIELDS')
 need(plan['schema']=='workinants.scoped-read-companion-run.v1' and plan['scope']=='REVIEWED_SELECTED94_SCOPED_READ_COMPANION_SQL_SUBSET_ONLY','RUN_PLAN_SCOPE')
 need(type(plan['run_id']) is str and str(uuid.UUID(plan['run_id']))==plan['run_id'] and uuid.UUID(plan['run_id']).version==4,'RUN_UUID4')
 for key in ('source_commit','source_tree'):need(type(plan[key]) is str and re.fullmatch('[0-9a-f]{40}',plan[key]),'SOURCE_CHECKPOINT')
 need(type(plan['immutable_container_id']) is str and re.fullmatch('[0-9a-f]{64}',plan['immutable_container_id']),'IMMUTABLE_CREATED_CID')
 pins=plan['packet_files_sha256'];need(type(pins) is dict and pins and all(type(v) is str and re.fullmatch('[0-9a-f]{64}',v) for v in pins.values()),'CLOSED_PACKET_PINS')
 need(sha(''.join(k+'\0'+pins[k]+'\n' for k in sorted(pins)).encode())==plan['packet_sha256'],'CLOSED_PACKET_AGGREGATE')
 blobs={relative:checked_source(relative,pins) for relative in pins}
 raw=(PACKET/'fixtures.json').read_bytes();need(sha(raw)==plan['reviewed_packet_sha256'] and pins.get('review-output/scoped-read-companion-rehearsal/fixtures.json')==sha(raw),'REVIEWED_FIXTURE_FILE')
 packet=unique_json(raw)
 need(packet['schema']=='workinants.scoped-read-companion-fixtures.v1' and packet['status']=='NOT_RUN' and packet['database_posture']=='D' and packet['database_contacted'] is False and packet['sql_executed'] is False,'REVIEWED_FIXTURE_SCOPE')
 need(digest({k:packet[k] for k in ('source_files_sha256','prepared_files_sha256')})==packet['source_only_packet_sha256']==plan['reviewed_content_sha256'],'REVIEWED_CONTENT_AGGREGATE')
 need(packet['source_files_sha256'].get(APPLICATION)==APPLICATION_SHA and pins.get(APPLICATION)==APPLICATION_SHA,'CANONICAL_SQL')
 for relative,value in packet['source_files_sha256'].items():need(pins.get(relative)==value and sha(blobs[relative])==value,'FIXTURE_SOURCE_BINDING')
 for name,value in packet['prepared_files_sha256'].items():
  need(pins.get('review-output/scoped-read-companion-rehearsal/'+name)==value,'FIXTURE_SQL_PACKET_BINDING');checked_sql(packet,name)
 need(plan['scenario_names']==[c['name'] for c in packet['cases']] and len(packet['cases'])==packet['finite_caps']['case_count'] and all(c['status']=='NOT_RUN' for c in packet['cases']),'EXACT_FINITE_CASES')
 need(len(packet['worker_acl_ceiling_rows'])==32,'WORKER_ACL_CEILING')
 documents={}
 for key in ('native_snapshot','native_comparison','native_attestation'):
  entry=plan[key];need(type(entry) is dict and set(entry)=={'path','sha256'},'NATIVE_BINDING_FIELDS');data=external(entry['path']).read_bytes();need(sha(data)==entry['sha256'],'NATIVE_FILE_DRIFT');documents[key]=unique_json(data)
 native,comparison,attestation=(documents[k] for k in ('native_snapshot','native_comparison','native_attestation'))
 need(native.get('format')=='workinants.native-catalog.v1' and type(native.get('server_version_num')) is int and native['server_version_num']==170011 and native.get('read_only') is True and native.get('collected_as')=='postgres' and native.get('collector_is_superuser') is True,'NATIVE_COLLECTOR_IDENTITY')
 need(comparison.get('format')=='workinants.catalog-comparison.v1' and comparison.get('status')=='PASS' and comparison.get('source_expected_sha256')==EXPECTED_CATALOG and comparison.get('native_snapshot_sha256')==digest(native) and comparison.get('findings')==[] and comparison.get('check_counts')=={'PASS':29089},'NATIVE_EXACT_COMPARISON_PASS')
 expected={'schema':'workinants.scoped-read-companion-native-attestation.v1','run_id':plan['run_id'],'container_id':plan['immutable_container_id'],'source_commit':plan['source_commit'],'source_tree':plan['source_tree'],'packet_sha256':plan['packet_sha256'],'collector_sha256':pins[COLLECTOR],'source_expected_sha256':EXPECTED_CATALOG,'native_snapshot_sha256':digest(native),'native_comparison_file_sha256':plan['native_comparison']['sha256'],'original_grantor_finalized':True,'operation_backends_absent':True,'comparison_status':'PASS'}
 need(canonical(attestation)==canonical(expected),'SAME_SOURCE_RUN_CID_NATIVE_ATTESTATION')
 # No helper executes until the complete source closure, packet and evidence bytes were verified.
 need(all(name in blobs for name in (SELF,PROTOCOL,*HELPERS,COLLECTOR)),'HELPER_SOURCE_CLOSURE')
 protocol=compiled(blobs[PROTOCOL],PROTOCOL);context=compiled(blobs[CONTEXT],CONTEXT)
 context['load_helpers'](blobs)
 target=context['HOST']['validate_manifest'](plan['target_manifest'])
 need(target['run_id']==plan['run_id'] and target['source']['integrated_sql_sha256']==APPLICATION_SHA,'TARGET_RUN_SOURCE_BINDING')
 for relative in pins:checked_source(relative,pins)
 return packet,native,target,protocol,context

class Evidence:
 def __init__(self,path,plan,packet):
  self.directory=external(path);need(not self.directory.exists(),'FRESH_EXTERNAL_EVIDENCE_DIRECTORY');self.directory.mkdir();self.path=self.directory/'scoped-read-companion-results.json';self.finalizing=False;self.failed=False
  self.value={'schema':'workinants.scoped-read-companion-evidence.v1','status':'IN_PROGRESS','current_stage':'ENTRY','current_case':None,'run_id':plan['run_id'],'container_id':plan['immutable_container_id'],'source_commit':plan['source_commit'],'source_tree':plan['source_tree'],'packet_sha256':plan['packet_sha256'],'reviewed_packet_sha256':plan['reviewed_packet_sha256'],'reviewed_content_sha256':plan['reviewed_content_sha256'],'selected_controls':[{'id':x,'status':'NOT_RUN'} for x in packet['selected_control_ids']],'results':[],'operations':[],'authentication':[],'unexpected':[],'subsequent_cases_stopped':False,'cleanup_required':True,'fixture_owner_bypass_restored':False,'evidence_complete':True,'database_posture':'D','limits':packet['scope_limits']};self.save()
 def stop(self,code,stage=None):
  self.value.update(status='STOPPED_PARTIAL_EVIDENCE_PRESERVED',subsequent_cases_stopped=True)
  item={'stage':stage or self.value['current_stage'],'case':self.value['current_case'],'code':code}
  if item not in self.value['unexpected']:self.value['unexpected'].append(item)
 def save(self):
  try:
   temp=self.path.with_suffix('.json.tmp')
   with temp.open('w',encoding='utf8',newline='\n') as f:f.write(json.dumps(self.value,indent=2,ensure_ascii=False,allow_nan=False)+'\n');f.flush();os.fsync(f.fileno())
   temp.replace(self.path);return True
  except BaseException:
   self.failed=True;self.value['evidence_complete']=False;self.stop('SANITIZED_EVIDENCE_WRITE_UNCONFIRMED')
   if not self.finalizing:raise HeldFailure('SANITIZED_EVIDENCE_WRITE_UNCONFIRMED') from None
   return False
 def stage(self,value):self.value['current_stage']=value;self.save()

def coordinator_type(context):
 class Coordinator(context['Coordinator']):
  def __init__(self,plan,packet,native,target,evidence,protocol,session_factory=None):
   super().__init__(plan,packet,native,target,evidence,session_factory or context['Session']);self.protocol=protocol;self.bypass_open=False;self.sessions=[]
  def text(self,name):return checked_sql(self.packet,name)
  def session(self,role):
   value=self.session_factory(role,self);self.sessions.append(value);return value
  def raw(self,role,text):
   result=subprocess.run(self.psql(role),input=text,text=True,capture_output=True,timeout=90,shell=False)
   need(type(result.returncode) is int and result.returncode==0 and result.stderr=='' and len(result.stdout.encode())<=16*1024*1024,'PRIVILEGED_OR_ISSUER_SQL_UNCONFIRMED');return result.stdout.strip()
  def global_closure(self):
   actual=unique_json(self.raw('postgres',"SELECT jsonb_build_object('other_clients',(SELECT count(*) FROM pg_stat_activity WHERE backend_type='client backend' AND pid<>pg_backend_pid()));"))
   need(canonical(actual)==canonical({'other_clients':0}),'GLOBAL_BACKEND_CLOSURE_UNCONFIRMED');self.record({'stage':'GLOBAL_BACKEND_CLOSURE','other_clients_zero':True})
  def native_parity(self,label):
   self.global_closure();raw=checked_source(COLLECTOR,self.plan['packet_files_sha256']);actual=unique_json(self.raw('postgres',raw.decode()))
   need(digest(actual)==digest(self.native),'NATIVE_TRIGGER_FUNCTION_ACL_DRIFT');self.record({'stage':label,'native_catalog_match':True,'native_sha256':digest(self.native)})
  def restoration_identity(self):
   self.global_closure();raw=checked_source(COLLECTOR,self.plan['packet_files_sha256']);actual=unique_json(self.raw('postgres',raw.decode()))
   try:proof=self.protocol['restoration_identity'](self.native,actual)
   except BaseException as error:
    allowed={'RESTORATION_NATIVE_SHAPE','RESTORATION_TRIGGER_SHAPE','RESTORATION_EXACT_EIGHT_IDENTITIES','RESTORATION_ORIGINAL_OWNER_CONTRACT','RESTORATION_ONLY_OWNER_O_OR_D','RESTORATION_FULL_NATIVE_IDENTITY_DRIFT'}
    code=getattr(error,'code',None);self.record({'stage':'PRE_RESTORATION_EXACT_NATIVE_IDENTITY','comparison_passed':False,'failed_check':code if type(code) is str and code in allowed else 'RESTORATION_IDENTITY_UNCONFIRMED'})
    raise HeldFailure('PRE_RESTORATION_IDENTITY_UNCONFIRMED') from None
   self.record({'stage':'PRE_RESTORATION_EXACT_NATIVE_IDENTITY','comparison_passed':True,'observed_native_sha256':digest(actual),**proof})
  def retention(self,instances,unexpired=False):
   need(instances and len(instances)==len(set(instances)) and all(i in self.instances for i in instances),'EXACT_ISSUED_INSTANCE_SET');rows=[]
   for key in instances:
    value=self.instances[key]['values'];checks=' AND '.join('g.'+column+' IS NOT DISTINCT FROM ('+value[column]+')' for column in context['GRANT_COLUMNS'])
    rows.append('SELECT ('+checks+') AS exact,g.issuer_service=session_user::text AS issuer_owned,g.revoked_at IS NULL AS unrevoked,g.expires_at>clock_timestamp() AS unexpired FROM platform.database_action_grant g WHERE g.id='+value['id'])
   query="SELECT jsonb_build_object('count',count(*),'exact',coalesce(bool_and(exact),false),'issuer_owned',coalesce(bool_and(issuer_owned),false),'unrevoked',coalesce(bool_and(unrevoked),false),'unexpired',coalesce(bool_and(unexpired),false)) FROM ("+' UNION ALL '.join(rows)+') observed;'
   actual=unique_json(self.raw('wa_context_issuer',query));need(type(actual) is dict and set(actual)=={'count','exact','issuer_owned','unrevoked','unexpired'} and type(actual['count']) is int and actual['count']==len(instances) and all(actual[k] is True for k in ('exact','issuer_owned','unrevoked')) and type(actual['unexpired']) is bool and (not unexpired or actual['unexpired']),'IMMUTABLE_21_FIELD_ISSUER_RETENTION')
   self.record({'stage':'IMMUTABLE_ISSUER_RETENTION','instances':len(instances),'all_21_fields_match':True,'issuer_owned':True,'unrevoked':True,'unexpired_required':unexpired,'current_unexpired_match':actual['unexpired'] if unexpired else None})
  def fixture_commit(self,name,label):
   self.global_closure()
   try:self.commit('postgres',self.text(name),label)
   finally:self.global_closure()
  def trigger_observer(self):
   actual=unique_json(self.raw('postgres',self.text('exact-trigger-observe.sql')));need(canonical(actual)==canonical({'owner_count':8,'physical_count':8,'all_enabled':True}),'EXACT_EIGHT_TRIGGER_RESTORATION')
   self.record({'stage':'EXACT_EIGHT_TRIGGER_RESTORATION','owner_and_physical_enabled':True})
  def state(self,empty=False):
   self.global_closure();actual=unique_json(self.raw('postgres',self.text('complete-state-observe.sql')));expected=self.packet['expected_counts']
   need(type(actual) is dict and set(actual)==set(expected) and len(actual)==42,'COMPLETE42_TABLE_SET')
   for table,count in expected.items():
    value=actual[table];wanted=0 if empty else len(self.instances) if table=='platform.database_action_grant' else count
    need(type(value) is dict and set(value)=={'count','rows_sha256'} and type(value['count']) is int and value['count']==wanted and type(value['rows_sha256']) is str and re.fullmatch('[0-9a-f]{64}',value['rows_sha256']),'COMPLETE42_TYPED_COUNTS_HASHES')
   if not empty:
    coherence=unique_json(self.raw('postgres',self.text('fixture-coherence-observe.sql')));need(canonical(coherence)==canonical({'users':2,'coherent':True}),'EXACT_CURRENT_PRINCIPAL_FIXTURES')
   return actual
  def setup(self):
   self.native_parity('PRE_FIXTURE_NATIVE_PARITY');self.state(empty=True);self.trigger_observer()
   # A commit may succeed before acknowledgement/closure verification fails.
   self.bypass_open=True;self.evidence.stage('EXACT_EIGHT_FIXTURE_TRANSACTION_ATTEMPT')
   self.fixture_commit('existing-scoped-read-fixtures.sql','SYNTHETIC_EXISTING_ROWS_ONLY');self.trigger_observer();self.native_parity('POST_FIXTURE_NATIVE_PARITY')
   self.bypass_open=False;self.evidence.value['fixture_owner_bypass_restored']=True;self.evidence.save();return self.state()
  def bound(self,case):
   self.evidence.value['current_case']=case['name'];self.evidence.stage('BOUND_READ');template=self.packet['grants'][case['grant']]
   session=self.session('wa_app_runtime');record={'stage':'BOUND_OPERATION','case':case['name'],'actual_login':'wa_app_runtime','issuer_committed':False,'same_tuple_verified':False,'bind_stage_marker':False,'query_stage_reached':False,'operation_closed':False};self.record(record);instance=None
   try:
    session.begin('read committed');backend=session.capture();instance=self.issue(template,backend);record['issuer_committed']=True;self.retention([instance],True)
    rows,ack,errors=session.call('SELECT pg_current_xact_id()::text='+quote(backend['xid'])+';');need(rows==['t'] and ack is True and errors=='','SAME_OPERATION_XID');record['same_tuple_verified']=True
    bind_marker=self.protocol['marker'](case['name'],'BIND');rows,ack,errors=session.call('SELECT '+quote(bind_marker)+';');need(rows==[bind_marker] and ack is True and errors=='','EXACT_BIND_STAGE_MARKER');record['bind_stage_marker']=True;self.evidence.save()
    rows,ack,errors=session.call('SELECT platform_private.bind_request_context('+quote(self.instances[instance]['secret'])+');')
    if case['kind']=='read':
     need(rows==[] and ack is True and errors=='','FRESH_EXACT_BIND_REQUIRED');record['query_stage_reached']=True;self.evidence.save();rows,ack,errors=session.call(self.text(case['sql']))
   finally:
    try:
     try:code=session.close()
     finally:record['operation_closed']=session.closed;self.evidence.save()
    finally:self.global_closure()
   need(record['operation_closed'] is True,'EXACT_OPERATION_CLOSURE_REQUIRED');self.retention([instance],True)
   result=self.protocol['verdict'](case,code,rows,ack,errors,self.application);record.update(terminal_exit=code,result_validated=True);self.evidence.save();return result
  def execute(self):
   self.evidence.stage('CURRENT_RESOURCE_AUTHENTICATION_AND_FINALIZATION');host=context['HOST'];process=subprocess.run
   observed=host['inspect_live'](self.target,host['docker_json'](['context','inspect','desktop-linux'],process),host['docker_json'](['inspect',self.target['target']['container_name']],process),host['docker_json'](['volume','inspect',self.target['target']['volume_name']],process))
   need(observed['container_id']==self.container,'CURRENT_CREATED_CID_REQUIRED');host['verify_image'](self.target,host['docker_json'](['inspect',self.target['target']['container_name']],process),host['docker_json'](['image','inspect',self.target['target']['image']],process))
   context['API']['authentication_preflight'](self.evidence,self.container);self.global_closure()
   need(self.raw('postgres',"SELECT current_setting('server_version_num')='170011' AND current_setting('log_statement')='none' AND current_setting('log_min_error_statement')='panic' AND current_setting('password_encryption')='scram-sha-256';")=='t','SAFE_SERVER_SETTINGS')
   need(self.raw('postgres',"SELECT NOT EXISTS(SELECT 1 FROM pg_auth_members WHERE member='wa_schema_owner'::regrole AND roleid=ANY(ARRAY['wa_private_helper_owner'::regrole,'wa_customer_verifier'::regrole,'wa_track_verifier'::regrole])) AND NOT has_schema_privilege('wa_private_helper_owner','platform_private','CREATE') AND NOT has_schema_privilege('wa_customer_verifier','platform_private','CREATE') AND NOT has_schema_privilege('wa_track_verifier','platform_private','CREATE');")=='t','ORIGINAL_GRANTOR_FINALIZATION_REQUIRED')
   baseline=self.setup();self.evidence.value['baseline']={'tables':baseline,'sha256':digest(baseline)};self.evidence.save()
   for case in self.packet['cases']:
    result=self.bound(case);actual=self.state();need(all(canonical(actual[t])==canonical(baseline[t]) for t in actual if t!='platform.database_action_grant'),'COMPLETE42_UNEXPECTED_DATA_EFFECT')
    self.retention(list(self.instances));self.trigger_observer()
    self.evidence.value['results'].append({'case':case['name'],'case_id':case['case_id'],'assertion_id':case['assertion_id'],'actual_login':'wa_app_runtime','operation_closed_before_observers':True,'tables_observed':42,'complete_state_sha256':digest(actual),'issued_grants':len(self.instances),**result});self.evidence.save()
   self.native_parity('FINAL_NATIVE_PARITY');self.evidence.value.update(status='PASS_FINITE_SCOPED_READ_COMPANION_SQL_SUBSET_ONLY',current_case=None,current_stage='COMPLETE');self.evidence.save()
 return Coordinator

def safe_code(error):
 code=getattr(error,'code',None)
 allowed={'SANITIZED_EVIDENCE_WRITE_UNCONFIRMED','GLOBAL_BACKEND_CLOSURE_UNCONFIRMED','NATIVE_TRIGGER_FUNCTION_ACL_DRIFT','IMMUTABLE_21_FIELD_ISSUER_RETENTION','EXACT_EIGHT_TRIGGER_RESTORATION','COMPLETE42_TABLE_SET','COMPLETE42_TYPED_COUNTS_HASHES','EXACT_CURRENT_PRINCIPAL_FIXTURES','SAME_OPERATION_XID','EXACT_BIND_STAGE_MARKER','FRESH_EXACT_BIND_REQUIRED','EXACT_OPERATION_CLOSURE_REQUIRED','CURRENT_CREATED_CID_REQUIRED','SAFE_SERVER_SETTINGS','ORIGINAL_GRANTOR_FINALIZATION_REQUIRED','COMPLETE42_UNEXPECTED_DATA_EFFECT','TYPED_OPERATION_RESULT','INTENDED_BINDER_GUARD_REQUIRED','READ_TERMINAL_MARKERS','TYPED_NONNEGATIVE_COUNTS','EXACT_READ_COUNTS_REQUIRED','DUPLICATE_RESPONSE_FIELD','NONFINITE_RESPONSE','MALFORMED_RESPONSE','SOURCE_FILE_DRIFT','SOURCE_FILE_UNAVAILABLE','PREPARED_SQL_DRIFT','ISSUER_OR_PRIVILEGED_COMMIT_UNCONFIRMED','SEPARATE_ISSUER_COMMIT_UNCONFIRMED','ISSUER_TERMINAL_EXIT_UNEXPECTED','SESSION_CLOSURE_UNCONFIRMED','UNOBSERVED_SESSION_OUTPUT','EXACT_BACKEND_STILL_LIVE'}
 return code if type(code) is str and code in allowed else 'TIMEOUT_CLOSURE_UNCONFIRMED' if isinstance(error,subprocess.TimeoutExpired) else 'UNEXPECTED_OPERATION_FAILURE'

def coordinate(plan,evidence_directory):
 packet,native,target,protocol,context=load_inputs(plan);evidence=Evidence(evidence_directory,plan,packet);coordinator=coordinator_type(context)(plan,packet,native,target,evidence,protocol)
 try:coordinator.execute()
 except BaseException as error:evidence.stop(safe_code(error));evidence.finalizing=True;evidence.save()
 finally:
  evidence.finalizing=True;global_absent=False
  # Every closure and restoration step progresses despite evidence I/O failure.
  for session in coordinator.sessions:
   if not session.closed:
    try:session.close()
    except BaseException:evidence.stop('OPERATION_CLOSURE_UNCONFIRMED','FINALLY')
  try:coordinator.global_closure();global_absent=True
  except BaseException:evidence.stop('GLOBAL_BACKEND_CLOSURE_UNCONFIRMED','FINALLY')
  # Global absence permits controlled restoration; it never qualifies the
  # failed operation whose own closure/output was unconfirmed.
  if global_absent:
   restored=True
   if coordinator.bypass_open:
    try:coordinator.restoration_identity();coordinator.fixture_commit('exact-owner-trigger-restore.sql','FINALLY_EXACT_EIGHT_RESTORE');coordinator.bypass_open=False
    except BaseException:restored=False;evidence.stop('EXACT_EIGHT_RESTORE_UNCONFIRMED','FINALLY')
   try:coordinator.trigger_observer()
   except BaseException:restored=False;evidence.stop('EXACT_EIGHT_TRIGGER_VERIFICATION_UNCONFIRMED','FINALLY')
   try:coordinator.native_parity('FINALLY_FULL_NATIVE_PARITY')
   except BaseException:restored=False;evidence.stop('FULL_NATIVE_PARITY_UNCONFIRMED','FINALLY')
   evidence.value['fixture_owner_bypass_restored']=restored
  try:
   for relative in plan['packet_files_sha256']:checked_source(relative,plan['packet_files_sha256'])
   evidence.value['source_packet_unchanged_after']=True
  except BaseException:evidence.value['source_packet_unchanged_after']=False;evidence.stop('SOURCE_PACKET_DRIFT','POSTCHECK')
  try:
   safe=canonical(evidence.value);need(all(v['secret'] not in safe and v['token_hash'] not in safe for v in coordinator.instances.values()),'SECRET_EVIDENCE_EXCLUSION')
   evidence.value['sanitization']={'context_secrets_or_hashes_found':False,'raw_stderr_statement_bodies_or_handles_retained':False}
  except BaseException:
   # A contaminated dictionary is never serialized on a stopped path.
   evidence.value={k:evidence.value[k] for k in ('schema','run_id','database_posture')};evidence.value.update(status='STOPPED_PARTIAL_EVIDENCE_PRESERVED',current_stage='SANITIZATION',current_case=None,results=[],operations=[],unexpected=[],evidence_complete=False,subsequent_cases_stopped=True);evidence.stop('SECRET_EVIDENCE_EXCLUSION','SANITIZATION');evidence.failed=True
  evidence.save()
 return evidence.value

def main(argv=None):
 parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--execute-reviewed-scoped-reads',action='store_true');parser.add_argument('--run-plan',type=Path);parser.add_argument('--evidence-directory',type=Path);args=parser.parse_args(argv)
 try:
  need(args.execute_reviewed_scoped_reads and args.run_plan is not None and args.evidence_directory is not None,'EXPLICIT_REVIEWED_EXECUTION_REQUIRED');value=coordinate(unique_json(external(args.run_plan).read_bytes()),args.evidence_directory)
  print(json.dumps({'status':value['status'],'completed_protocols':len(value['results']),'raw_output_discarded':True}));return 0 if not value['unexpected'] and value['evidence_complete'] is True else 1
 except BaseException:print(json.dumps({'status':'HELD_OR_STOPPED','code':'SCOPED_READ_COORDINATOR_REFUSED','raw_output_discarded':True}));return 1
if __name__=='__main__':raise SystemExit(main())

