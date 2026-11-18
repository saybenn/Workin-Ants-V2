"""Dormant finite owner-read coordinator. Import/help execute no process.

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
PACKET=ROOT/'review-output/owner-read-control-rehearsal'
SELF='scripts/sql-review/run-owner-read-control-rehearsal.py'
PROTOCOL='scripts/owner_read_control_protocol.py'
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
 need(type(relative) is str and '\\' not in relative and not relative.startswith('/') and all(p not in ('','.','..') for p in relative.split('/')),'SOURCE_PATH')
 path=(ROOT/relative).resolve();need(path.is_relative_to(ROOT.resolve()),'SOURCE_PATH_ESCAPE');return path

def external(value):
 path=Path(value);need(path.is_absolute(),'EXTERNAL_ABSOLUTE_PATH');path=path.resolve()
 need(path.is_relative_to(TASK.resolve()) and not path.is_relative_to(ROOT.resolve()),'EXTERNAL_TASK_PATH');return path

def checked_source(relative,pins):
 need(relative in pins,'SOURCE_NOT_ADMITTED');raw=source_path(relative).read_bytes();need(sha(raw)==pins[relative],'SOURCE_FILE_DRIFT');return raw

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
 need(plan['schema']=='workinants.owner-read-run.v1' and plan['scope']=='REVIEWED_SELECTED94_OWNER_READ_SQL_SUBSET_ONLY','RUN_PLAN_SCOPE')
 need(type(plan['run_id']) is str and str(uuid.UUID(plan['run_id']))==plan['run_id'] and uuid.UUID(plan['run_id']).version==4,'RUN_UUID4')
 for key in ('source_commit','source_tree'):need(type(plan[key]) is str and re.fullmatch('[0-9a-f]{40}',plan[key]),'SOURCE_CHECKPOINT')
 need(type(plan['immutable_container_id']) is str and re.fullmatch('[0-9a-f]{64}',plan['immutable_container_id']),'IMMUTABLE_CREATED_CID')
 pins=plan['packet_files_sha256'];need(type(pins) is dict and pins and all(type(v) is str and re.fullmatch('[0-9a-f]{64}',v) for v in pins.values()),'CLOSED_PACKET_PINS')
 need(sha(''.join(k+'\0'+pins[k]+'\n' for k in sorted(pins)).encode())==plan['packet_sha256'],'CLOSED_PACKET_AGGREGATE')
 blobs={relative:checked_source(relative,pins) for relative in pins}
 raw=(PACKET/'fixtures.json').read_bytes();need(sha(raw)==plan['reviewed_packet_sha256'] and pins.get('review-output/owner-read-control-rehearsal/fixtures.json')==sha(raw),'REVIEWED_FIXTURE_FILE')
 packet=unique_json(raw)
 need(packet['schema']=='workinants.owner-read-fixtures.v1' and packet['status']=='NOT_RUN' and packet['database_posture']=='D' and packet['database_contacted'] is False and packet['sql_executed'] is False,'REVIEWED_FIXTURE_SCOPE')
 need(digest({k:packet[k] for k in ('source_files_sha256','prepared_files_sha256')})==packet['source_only_packet_sha256']==plan['reviewed_content_sha256'],'REVIEWED_CONTENT_AGGREGATE')
 need(packet['source_files_sha256'].get(APPLICATION)==APPLICATION_SHA and pins.get(APPLICATION)==APPLICATION_SHA,'CANONICAL_SQL')
 for relative,value in packet['source_files_sha256'].items():need(pins.get(relative)==value and sha(blobs[relative])==value,'FIXTURE_SOURCE_BINDING')
 for name,value in packet['prepared_files_sha256'].items():
  need(pins.get('review-output/owner-read-control-rehearsal/'+name)==value,'FIXTURE_SQL_PACKET_BINDING');checked_sql(packet,name)
 need(plan['scenario_names']==[c['name'] for c in packet['cases']] and len(packet['cases'])==packet['finite_caps']['case_count'] and all(c['status']=='NOT_RUN' for c in packet['cases']),'EXACT_FINITE_CASES')
 need(len(packet['worker_acl_ceiling_rows'])==32,'WORKER_ACL_CEILING')
 documents={}
 for key in ('native_snapshot','native_comparison','native_attestation'):
  entry=plan[key];need(type(entry) is dict and set(entry)=={'path','sha256'},'NATIVE_BINDING_FIELDS');data=external(entry['path']).read_bytes();need(sha(data)==entry['sha256'],'NATIVE_FILE_DRIFT');documents[key]=unique_json(data)
 native,comparison,attestation=(documents[k] for k in ('native_snapshot','native_comparison','native_attestation'))
 need(native.get('format')=='workinants.native-catalog.v1' and type(native.get('server_version_num')) is int and native['server_version_num']==170011 and native.get('read_only') is True and native.get('collected_as')=='postgres' and native.get('collector_is_superuser') is True,'NATIVE_COLLECTOR_IDENTITY')
 need(comparison.get('format')=='workinants.catalog-comparison.v1' and comparison.get('status')=='PASS' and comparison.get('source_expected_sha256')==EXPECTED_CATALOG and comparison.get('native_snapshot_sha256')==digest(native) and comparison.get('findings')==[] and comparison.get('check_counts')=={'PASS':29089},'NATIVE_EXACT_COMPARISON_PASS')
 expected={'schema':'workinants.owner-read-native-attestation.v1','run_id':plan['run_id'],'container_id':plan['immutable_container_id'],'source_commit':plan['source_commit'],'source_tree':plan['source_tree'],'packet_sha256':plan['packet_sha256'],'collector_sha256':pins[COLLECTOR],'source_expected_sha256':EXPECTED_CATALOG,'native_snapshot_sha256':digest(native),'native_comparison_file_sha256':plan['native_comparison']['sha256'],'original_grantor_finalized':True,'operation_backends_absent':True,'comparison_status':'PASS'}
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
  self.directory=external(path);need(not self.directory.exists(),'FRESH_EXTERNAL_EVIDENCE_DIRECTORY');self.directory.mkdir()
  self.path=self.directory/'owner-read-results.json'
  self.value={'schema':'workinants.owner-read-evidence.v1','status':'IN_PROGRESS','current_stage':'ENTRY','current_case':None,'run_id':plan['run_id'],'container_id':plan['immutable_container_id'],'source_commit':plan['source_commit'],'source_tree':plan['source_tree'],'packet_sha256':plan['packet_sha256'],'reviewed_packet_sha256':plan['reviewed_packet_sha256'],'reviewed_content_sha256':plan['reviewed_content_sha256'],'selected_controls':[{'id':x,'status':'NOT_RUN'} for x in packet['selected_control_ids']],'results':[],'operations':[],'authentication':[],'unexpected':[],'subsequent_cases_stopped':False,'cleanup_required':True,'fixture_owner_bypass_restored':False,'database_posture':'D','limits':packet['scope_limits']};self.save()
 def save(self):
  temp=self.path.with_suffix('.json.tmp')
  with temp.open('w',encoding='utf8',newline='\n') as f:f.write(json.dumps(self.value,indent=2,ensure_ascii=False,allow_nan=False)+'\n');f.flush();os.fsync(f.fileno())
  temp.replace(self.path)
 def stage(self,value):self.value['current_stage']=value;self.save()

def coordinator_type(context):
 class Coordinator(context['Coordinator']):
  def __init__(self,plan,packet,native,target,evidence,protocol,session_factory=None):
   super().__init__(plan,packet,native,target,evidence,session_factory or context['Session']);self.protocol=protocol;self.bypass_open=False;self.lease_secret=None
  def text(self,name):return checked_sql(self.packet,name)
  def raw(self,role,text):
   result=subprocess.run(self.psql(role),input=text,text=True,capture_output=True,timeout=90,shell=False)
   need(type(result.returncode) is int and result.returncode==0 and result.stderr=='' and len(result.stdout.encode())<=16*1024*1024,'PRIVILEGED_OR_ISSUER_SQL_UNCONFIRMED');return result.stdout.strip()
  def global_closure(self):
   value=unique_json(self.raw('postgres',"SELECT jsonb_build_object('other_clients',(SELECT count(*) FROM pg_stat_activity WHERE backend_type='client backend' AND pid<>pg_backend_pid()));"))
   need(canonical(value)==canonical({'other_clients':0}),'GLOBAL_BACKEND_CLOSURE_UNCONFIRMED');self.record({'stage':'GLOBAL_BACKEND_CLOSURE','other_clients_zero':True})
  def native_parity(self,label):
   self.global_closure();raw=checked_source(COLLECTOR,self.plan['packet_files_sha256']);actual=unique_json(self.raw('postgres',raw.decode()))
   need(digest(actual)==digest(self.native),'NATIVE_TRIGGER_FUNCTION_ACL_DRIFT');self.record({'stage':label,'native_catalog_match':True,'native_sha256':digest(self.native)})
  def retention(self,instances,unexpired=False):
   need(instances and len(instances)==len(set(instances)) and all(i in self.instances for i in instances),'EXACT_ISSUED_INSTANCE_SET')
   rows=[]
   for key in instances:
    value=self.instances[key]['values'];checks=' AND '.join('g.'+column+' IS NOT DISTINCT FROM ('+value[column]+')' for column in context['GRANT_COLUMNS'])
    rows.append("SELECT ("+checks+") AS exact,g.issuer_service=session_user::text AS issuer_owned,g.revoked_at IS NULL AS unrevoked,g.expires_at>clock_timestamp() AS unexpired FROM platform.database_action_grant g WHERE g.id="+value['id'])
   query="SELECT jsonb_build_object('count',count(*),'exact',coalesce(bool_and(exact),false),'issuer_owned',coalesce(bool_and(issuer_owned),false),'unrevoked',coalesce(bool_and(unrevoked),false),'unexpired',coalesce(bool_and(unexpired),false)) FROM ("+' UNION ALL '.join(rows)+') observed;'
   actual=unique_json(self.raw('wa_context_issuer',query));need(type(actual) is dict and set(actual)=={'count','exact','issuer_owned','unrevoked','unexpired'} and type(actual['count']) is int and actual['count']==len(instances) and all(actual[k] is True for k in ('exact','issuer_owned','unrevoked')) and type(actual['unexpired']) is bool and (not unexpired or actual['unexpired']),'IMMUTABLE_21_FIELD_ISSUER_RETENTION')
   self.record({'stage':'IMMUTABLE_ISSUER_RETENTION','instances':len(instances),'all_21_fields_match':True,'issuer_owned':True,'unrevoked':True,'unexpired_required':unexpired,'current_unexpired_match':actual['unexpired'] if unexpired else None})
  def bound(self,case,custom_lines=None,lease=False):
   self.evidence.value['current_case']=case['name'];self.evidence.stage('BOUND_'+case['name'].upper().replace('-','_'))
   template=self.packet['grants'][case['grant']];session=self.session(template['database_login_role']);record={'stage':'BOUND_OPERATION','case':case['name'],'actual_login':template['database_login_role'],'issuer_committed':False,'same_tuple_verified':False,'operation_closed':False};self.record(record)
   try:
    session.begin('read committed');backend=session.capture();instance=self.issue(template,backend);record['issuer_committed']=True;self.retention([instance],True)
    rows,ack,errors=session.call('SELECT pg_current_xact_id()::text='+quote(backend['xid'])+';');need(rows==['t'] and ack is True and errors=='','SAME_OPERATION_XID');record['same_tuple_verified']=True;self.evidence.save()
    rows,ack,errors=session.call('SELECT platform_private.bind_request_context('+quote(self.instances[instance]['secret'])+');');need(rows==[] and ack is True and errors=='','FRESH_EXACT_BIND_REQUIRED')
    if lease:
     need(self.lease_secret is not None,'ACTUAL_PRIVATE_LEASE_REQUIRED');rows,ack,errors=session.call('SET LOCAL wa.lease_secret='+quote(self.lease_secret)+"; SET LOCAL wa.fence='1';");need(rows==[] and ack is True and errors=='','PRIVATE_LEASE_TRANSPORT_UNCONFIRMED')
    text=self.text(case['sql']);text=context['re'].sub(r'\A(?:(?:\s|--[^\n]*\n)*)BEGIN;','',text,count=1)
    rows,ack,errors=session.call(text)
   finally:
    try:code=session.close()
    finally:record['operation_closed']=session.closed;self.evidence.save()
   self.global_closure();self.retention([instance],True)
   if custom_lines is not None:
    need(type(code) is int and code==0 and ack is True and errors=='' and rows==custom_lines,'EXACT_SOURCE_FIXTURE_COMMIT_MARKERS');result={'status':'PASS_SOURCE_FIXTURE_ONLY','stage_markers_match':True}
   else:result=self.protocol['verdict'](case,code,rows,ack,errors,self.application)
   record.update(terminal_exit=code,result_validated=True);self.evidence.save();return result
  def state(self):
   self.global_closure();actual=unique_json(self.raw('postgres',self.text('complete-state-observe.sql')));expected=self.packet['expected_counts']
   need(type(actual) is dict and set(actual)==set(expected),'COMPLETE_STATE_TABLE_SET')
   for table,count in expected.items():
    value=actual[table];need(type(value) is dict and set(value)=={'count','rows_sha256'} and type(value['count']) is int and value['count']==count and type(value['rows_sha256']) is str and re.fullmatch('[0-9a-f]{64}',value['rows_sha256']),'COMPLETE_STATE_TYPED_COUNTS_HASHES')
   count=self.raw('postgres',self.text('grant-count-observe.sql'));need(count==str(len(self.instances)),'EXACT_ISSUER_ROW_COUNT')
   return actual
  def after(self,case,baseline,result):
   actual=self.state();need(canonical(actual)==canonical(baseline),'COMPLETE_STATE_MUTATION_OR_DRIFT');self.retention(list(self.instances));self.native_trigger_observer()
   self.evidence.value['results'].append({'case':case['name'],'actual_login':case['actual_login'],'status':'PASS_PREPARED_SQL_SUBSET_ONLY','operation_closed_before_observation':True,'complete_state_sha256':digest(actual),'tables_observed':len(actual),'grants_retained':len(self.instances),**result});self.evidence.save()
  def native_trigger_observer(self):
   value=unique_json(self.raw('postgres',self.text('fixture-trigger-restore-observe.sql')));wanted=self.packet['expected_trigger_contract']['observer_expected']
   need(canonical(value)==canonical(wanted),'EXACT_FIXTURE_TRIGGER_RESTORATION')
  def fixture_commit(self,name,label):
   self.global_closure();self.commit('postgres',self.text(name),label);self.global_closure()
  def setup(self):
   self.global_closure();zero=unique_json(self.raw('postgres',self.text('complete-state-observe.sql')))
   need(set(zero)==set(self.packet['expected_counts']) and all(type(v) is dict and type(v.get('count')) is int and v['count']==0 for v in zero.values()) and self.raw('postgres',self.text('grant-count-observe.sql'))=='0','FRESH_EMPTY_FIXTURE_NAMESPACE')
   self.fixture_commit('trusted-identity-fixtures.sql','TRUSTED_IDENTITY_FIXTURE')
   source=self.packet['copy_source_customer'];case={'name':'source-customer','grant':'source_customer','sql':'source-customer.sql'}
   self.bound(case,source['stage_marker_oracle']['expected_completed_markers'])
   self.commit('wa_identity_service_authority',self.text('identity-bootstrap.sql'),'INDEPENDENT_SYNTHETIC_IDENTITY_BOOTSTRAP')
   self.bound({'name':'schedule','grant':'schedule','sql':'schedule.sql'},['WA_CTX01_SCHEDULE_READY'])
   self.fixture_commit('existing-read-fixtures.sql','COHERENT_EXISTING_READ_FIXTURES')
   self.native_parity('PRE_CONSENT_OWNER_BYPASS_BASELINE')
   # A commit may succeed before acknowledgement/closure verification fails.
   # Record the bounded restoration obligation before attempting that commit.
   self.bypass_open=True;self.evidence.value['fixture_owner_bypass_restored']=False;self.evidence.stage('CONSENT_OWNER_BYPASS_OPEN_ATTEMPT')
   self.fixture_commit('consent-owner-fixture-open.sql','CONSENT_FIXTURE_OWNER_PROOF_ONLY_OPEN');self.evidence.stage('RESTRICTED_CONSENT_FIXTURES')
   try:
    for operation in self.packet['fixture_operations']:self.bound(operation)
   finally:
    self.global_closure();self.fixture_commit('consent-owner-fixture-close.sql','CONSENT_FIXTURE_OWNER_PROOF_ONLY_RESTORED');self.bypass_open=False
   self.native_trigger_observer();self.native_parity('POST_FIXTURE_EXACT_NATIVE_PARITY');self.evidence.value['fixture_owner_bypass_restored']=True;self.evidence.save()
   return self.state()
  def claim_for_catalog(self,baseline):
   self.lease_secret=secrets.token_hex(32);case={'name':'worker-read-fixture-claim','kind':'read','model':'RuntimeWorkItem','grant':'worker-read-fixture-claim','sql':'worker-read-fixture-claim.sql','expected':{'claimed':1},'actual_login':'wa_worker'}
   self.bound(case,lease=True)
   self.worker_live('AFTER_ACTUAL_CLAIM')
   after=self.state();need(all(after[k]==v for k,v in baseline.items() if k!='platform.runtime_work_item'),'CATALOG_CLAIM_NONWORK_DRIFT');self.retention(list(self.instances));self.record({'stage':'CATALOG_READ_PREREQUISITE_CLAIM','actual_claim':True,'live_private_preimage_and_fence_match':True,'attempts_effects_enrollments_zero':True,'old_work_sha256':baseline['platform.runtime_work_item']['rows_sha256'],'new_work_sha256':after['platform.runtime_work_item']['rows_sha256']});return after
  def worker_live(self,label):
   self.evidence.stage('WORKER_LIVE_LEASE_'+label.upper().replace('-','_'));need(self.lease_secret is not None,'ACTUAL_PRIVATE_LEASE_REQUIRED');self.global_closure()
   query='BEGIN READ ONLY; SET LOCAL wa.lease_secret='+quote(self.lease_secret)+'; '+self.text('worker-lease-observe.sql')+' COMMIT;'
   value=unique_json(self.raw('postgres',query));need(canonical(value)==canonical({'work_count':1,'exact_live_lease':True,'attempts':0,'effects':0,'enrollments':0}),'EXACT_ACTUAL_LEASE_PREIMAGE_FENCE_CURRENTNESS')
   self.record({'stage':'WORKER_LIVE_LEASE_'+label.upper().replace('-','_'),'live_private_preimage_and_fence_match':True,'attempts_effects_enrollments_zero':True})
  def execute(self):
   # Same immutable object and image are re-inspected immediately before authentication.
   host=context['HOST'];process=subprocess.run
   observed=host['inspect_live'](self.target,host['docker_json'](['context','inspect','desktop-linux'],process),host['docker_json'](['inspect',self.target['target']['container_name']],process),host['docker_json'](['volume','inspect',self.target['target']['volume_name']],process))
   need(observed['container_id']==self.container,'CURRENT_CREATED_CID_REQUIRED');host['verify_image'](self.target,host['docker_json'](['inspect',self.target['target']['container_name']],process),host['docker_json'](['image','inspect',self.target['target']['image']],process))
   context['API']['authentication_preflight'](self.evidence,self.container);self.global_closure()
   need(self.raw('postgres',"SELECT current_setting('server_version_num')='170011' AND current_setting('log_statement')='none' AND current_setting('log_min_error_statement')='panic' AND current_setting('password_encryption')='scram-sha-256';")=='t','SAFE_SERVER_SETTINGS')
   need(self.raw('postgres',"SELECT NOT EXISTS(SELECT 1 FROM pg_auth_members WHERE member='wa_schema_owner'::regrole AND roleid=ANY(ARRAY['wa_private_helper_owner'::regrole,'wa_customer_verifier'::regrole,'wa_track_verifier'::regrole])) AND NOT has_schema_privilege('wa_private_helper_owner','platform_private','CREATE') AND NOT has_schema_privilege('wa_customer_verifier','platform_private','CREATE') AND NOT has_schema_privilege('wa_track_verifier','platform_private','CREATE');")=='t','ORIGINAL_GRANTOR_FINALIZATION_REQUIRED')
   self.native_parity('PRE_FIXTURE_CURRENT_NATIVE_PARITY')
   baseline=self.setup();self.evidence.value['baseline']={'tables':baseline,'sha256':digest(baseline)};self.evidence.save();claimed=False
   for case in self.packet['cases']:
    worker=case['actual_login']=='wa_worker'
    if worker and not claimed:baseline=self.claim_for_catalog(baseline);claimed=True
    self.evidence.value['current_case']=case['name'];self.evidence.save()
    if worker:self.worker_live('BEFORE_'+case['name'])
    result=self.bound(case,lease=worker)
    if worker:self.worker_live('AFTER_'+case['name'])
    self.after(case,baseline,result)
   self.native_parity('FINAL_EXACT_NATIVE_PARITY');self.global_closure()
   need(len(self.instances)<=self.packet['finite_caps']['grant_instances_max'],'FINITE_GRANT_BUDGET')
   self.evidence.value.update(status='PASS_FINITE_OWNER_READ_SQL_SUBSET_ONLY',current_case=None,current_stage='COMPLETE',cleanup_required=True);self.evidence.save()
 return Coordinator

def coordinate(plan,evidence_directory):
 packet,native,target,protocol,context=load_inputs(plan);evidence=Evidence(evidence_directory,plan,packet);coordinator=coordinator_type(context)(plan,packet,native,target,evidence,protocol)
 try:coordinator.execute()
 except BaseException as error:
  safe={'stage':evidence.value['current_stage'],'case':evidence.value['current_case'],'code':error.code if hasattr(error,'code') and type(error.code) is str and re.fullmatch('[A-Z][A-Z0-9_]{0,100}',error.code) else 'TIMEOUT_CLOSURE_UNCONFIRMED' if isinstance(error,subprocess.TimeoutExpired) else 'UNEXPECTED_OPERATION_FAILURE'}
  evidence.value.update(status='STOPPED_PARTIAL_EVIDENCE_PRESERVED',subsequent_cases_stopped=True);evidence.value['unexpected'].append(safe);evidence.save()
 finally:
  try:
   coordinator.global_closure()
   if coordinator.bypass_open:coordinator.fixture_commit('consent-owner-fixture-close.sql','FINALLY_EXACT_CONSENT_OWNER_PROOF_RESTORE');coordinator.bypass_open=False
   coordinator.native_trigger_observer();coordinator.native_parity('FINALLY_EXACT_TRIGGER_FUNCTION_ACL_PARITY');evidence.value['fixture_owner_bypass_restored']=True
  except BaseException:
   evidence.value['unexpected'].append({'stage':'FINALLY','code':'BACKEND_CLOSURE_OR_EXACT_TRIGGER_RESTORATION_UNCONFIRMED'});evidence.value['status']='STOPPED_PARTIAL_EVIDENCE_PRESERVED';evidence.value['subsequent_cases_stopped']=True
  try:
   for relative in plan['packet_files_sha256']:checked_source(relative,plan['packet_files_sha256'])
   evidence.value['source_packet_unchanged_after']=True
  except BaseException:evidence.value['source_packet_unchanged_after']=False;evidence.value['unexpected'].append({'stage':'POSTCHECK','code':'SOURCE_PACKET_DRIFT'});evidence.value['status']='STOPPED_PARTIAL_EVIDENCE_PRESERVED'
  # Only in-memory secrets are scanned; they are never written into this evidence.
  safe=canonical(evidence.value);secrets_to_scan=[v['secret'] for v in coordinator.instances.values()]+([coordinator.lease_secret] if coordinator.lease_secret else [])
  need(all(value not in safe for value in secrets_to_scan),'SECRET_EVIDENCE_EXCLUSION');evidence.value['sanitization']={'context_or_lease_secrets_found':False,'raw_stderr_statement_bodies_or_handles_retained':False};evidence.save()
 return evidence.value

def main(argv=None):
 parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--execute-reviewed-owner-reads',action='store_true');parser.add_argument('--run-plan',type=Path);parser.add_argument('--evidence-directory',type=Path);args=parser.parse_args(argv)
 try:
  need(args.execute_reviewed_owner_reads and args.run_plan is not None and args.evidence_directory is not None,'EXPLICIT_REVIEWED_EXECUTION_REQUIRED')
  value=coordinate(unique_json(external(args.run_plan).read_bytes()),args.evidence_directory);print(json.dumps({'status':value['status'],'completed_cases':len(value['results']),'raw_output_discarded':True}));return 0 if not value['unexpected'] else 1
 except BaseException:print(json.dumps({'status':'HELD_OR_STOPPED','code':'OWNER_READ_COORDINATOR_REFUSED','raw_output_discarded':True}));return 1

if __name__=='__main__':raise SystemExit(main())
