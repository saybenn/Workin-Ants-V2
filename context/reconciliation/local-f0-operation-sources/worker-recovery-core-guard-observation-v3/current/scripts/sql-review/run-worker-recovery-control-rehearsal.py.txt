"""Dormant finite worker-recovery coordinator. Import/help execute no process.

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
import time

ROOT=Path(__file__).resolve().parents[2]
TASK=ROOT.parent
PACKET=ROOT/'review-output/worker-recovery-control-rehearsal'
SELF='scripts/sql-review/run-worker-recovery-control-rehearsal.py'
PROTOCOL='scripts/worker_recovery_control_protocol.py'
BASE='scripts/sql-review/run-scoped-read-companion-rehearsal.py'
CONTEXT='scripts/sql-review/run-context-control-rehearsal.py'
COLLECTOR='scripts/sql-review/collect_native_catalog.sql'
HELPERS=(BASE,CONTEXT,'scripts/sql-review/run-first-rehearsal.py','scripts/sql-review/run-local-f0-migrate.py','scripts/sql-review/rehearsal-diagnostics.py','scripts/prepare-local-f0-history.py')
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
 need(plan['schema']=='workinants.worker-recovery-run.v1' and plan['scope']=='REVIEWED_SELECTED94_WORKER_RECOVERY_SQL_SUBSET_ONLY','RUN_PLAN_SCOPE')
 need(type(plan['run_id']) is str and str(uuid.UUID(plan['run_id']))==plan['run_id'] and uuid.UUID(plan['run_id']).version==4,'RUN_UUID4')
 for key in ('source_commit','source_tree'):need(type(plan[key]) is str and re.fullmatch('[0-9a-f]{40}',plan[key]),'SOURCE_CHECKPOINT')
 need(type(plan['immutable_container_id']) is str and re.fullmatch('[0-9a-f]{64}',plan['immutable_container_id']),'IMMUTABLE_CREATED_CID')
 pins=plan['packet_files_sha256'];need(type(pins) is dict and pins and all(type(v) is str and re.fullmatch('[0-9a-f]{64}',v) for v in pins.values()),'CLOSED_PACKET_PINS')
 need(sha(''.join(k+'\0'+pins[k]+'\n' for k in sorted(pins)).encode())==plan['packet_sha256'],'CLOSED_PACKET_AGGREGATE')
 blobs={relative:checked_source(relative,pins) for relative in pins}
 raw=(PACKET/'fixtures.json').read_bytes();need(sha(raw)==plan['reviewed_packet_sha256'] and pins.get('review-output/worker-recovery-control-rehearsal/fixtures.json')==sha(raw),'REVIEWED_FIXTURE_FILE')
 packet=unique_json(raw)
 need(packet['schema']=='workinants.worker-recovery-fixtures.v1' and packet['status']=='NOT_RUN' and packet['database_posture']=='D' and packet['database_contacted'] is False and packet['sql_executed'] is False,'REVIEWED_FIXTURE_SCOPE')
 need(digest({k:packet[k] for k in ('source_files_sha256','prepared_files_sha256')})==packet['source_only_packet_sha256']==plan['reviewed_content_sha256'],'REVIEWED_CONTENT_AGGREGATE')
 need(packet['source_files_sha256'].get(APPLICATION)==APPLICATION_SHA and pins.get(APPLICATION)==APPLICATION_SHA,'CANONICAL_SQL')
 for relative,value in packet['source_files_sha256'].items():need(pins.get(relative)==value and sha(blobs[relative])==value,'FIXTURE_SOURCE_BINDING')
 for name,value in packet['prepared_files_sha256'].items():
  need(pins.get('review-output/worker-recovery-control-rehearsal/'+name)==value,'FIXTURE_SQL_PACKET_BINDING');checked_sql(packet,name)
 finite={'case_count':21,'jobs':3,'business_groups':2,'audit_attempts':3,'grant_instances_max':80,'clock_wait_seconds_max':150,'simultaneous_worker_sessions_max':2,'worker_loop':False};caps=packet['finite_caps']
 need(type(caps) is dict and set(caps)==set(finite) and all(type(caps[k]) is type(wanted) and caps[k]==wanted for k,wanted in finite.items()),'EXACT_TYPED_FINITE_CAPS')
 need(type(packet['cases']) is list and plan['scenario_names']==[c['name'] for c in packet['cases']] and len(packet['cases'])==caps['case_count'] and all(c['status']=='NOT_RUN' for c in packet['cases']),'EXACT_FINITE_CASES')
 tables={model['object'] for model in packet['models'].values()}|{'platform_private.identity_service_authorization','platform_private.identity_service_receipt'}
 need(len(tables)==42 and all(type(packet[k]) is dict and set(packet[k])==tables and all(type(v) is int and v>=0 for v in packet[k].values()) for k in ('setup_expected_counts','checkpoint_expected_counts','final_expected_counts')),'EXACT_TYPED_COMPLETE42_COUNTS')
 need(type(packet['worker_acl_rows']) is list and len(packet['worker_acl_rows'])==32,'WORKER_ACL_CEILING')
 documents={}
 for key in ('native_snapshot','native_comparison','native_attestation'):
  entry=plan[key];need(type(entry) is dict and set(entry)=={'path','sha256'},'NATIVE_BINDING_FIELDS');data=external(entry['path']).read_bytes();need(sha(data)==entry['sha256'],'NATIVE_FILE_DRIFT');documents[key]=unique_json(data)
 native,comparison,attestation=(documents[k] for k in ('native_snapshot','native_comparison','native_attestation'))
 need(native.get('format')=='workinants.native-catalog.v1' and type(native.get('server_version_num')) is int and native['server_version_num']==170011 and native.get('read_only') is True and native.get('collected_as')=='postgres' and native.get('collector_is_superuser') is True,'NATIVE_COLLECTOR_IDENTITY')
 counts=comparison.get('check_counts');need(type(counts) is dict and set(counts)=={'PASS'} and type(counts['PASS']) is int and counts['PASS']==29089,'NATIVE_EXACT_INTEGER_COMPARISON_COUNT')
 need(comparison.get('format')=='workinants.catalog-comparison.v1' and comparison.get('status')=='PASS' and comparison.get('source_expected_sha256')==EXPECTED_CATALOG and comparison.get('native_snapshot_sha256')==digest(native) and comparison.get('findings')==[],'NATIVE_EXACT_COMPARISON_PASS')
 expected={'schema':'workinants.worker-recovery-native-attestation.v1','run_id':plan['run_id'],'container_id':plan['immutable_container_id'],'source_commit':plan['source_commit'],'source_tree':plan['source_tree'],'packet_sha256':plan['packet_sha256'],'collector_sha256':pins[COLLECTOR],'source_expected_sha256':EXPECTED_CATALOG,'native_snapshot_sha256':digest(native),'native_comparison_file_sha256':plan['native_comparison']['sha256'],'original_grantor_finalized':True,'operation_backends_absent':True,'comparison_status':'PASS'}
 need(canonical(attestation)==canonical(expected),'SAME_SOURCE_RUN_CID_NATIVE_ATTESTATION')
 # No helper executes until the complete source closure, packet and evidence bytes were verified.
 need(all(name in blobs for name in (SELF,PROTOCOL,*HELPERS,COLLECTOR)),'HELPER_SOURCE_CLOSURE')
 protocol=compiled(blobs[PROTOCOL],PROTOCOL);context=compiled(blobs[CONTEXT],CONTEXT)
 context['load_helpers'](blobs)
 target=context['HOST']['validate_manifest'](plan['target_manifest'])
 need(target['run_id']==plan['run_id'] and target['source']['integrated_sql_sha256']==APPLICATION_SHA,'TARGET_RUN_SOURCE_BINDING')
 for relative in pins:checked_source(relative,pins)
 base=compiled(blobs[BASE],BASE)
 return packet,native,target,protocol,context,base

class Evidence:
 def __init__(self,path,plan,packet):
  self.directory=external(path);need(not self.directory.exists(),'FRESH_EXTERNAL_EVIDENCE_DIRECTORY');self.directory.mkdir();self.path=self.directory/'worker-recovery-results.json';self.finalizing=False;self.failed=False
  self.value={'schema':'workinants.worker-recovery-evidence.v1','status':'IN_PROGRESS','current_stage':'ENTRY','current_case':None,'run_id':plan['run_id'],'container_id':plan['immutable_container_id'],'source_commit':plan['source_commit'],'source_tree':plan['source_tree'],'packet_sha256':plan['packet_sha256'],'reviewed_packet_sha256':plan['reviewed_packet_sha256'],'reviewed_content_sha256':plan['reviewed_content_sha256'],'selected_controls':[{'id':x,'status':'NOT_RUN'} for x in packet['selected_control_ids']],'results':[],'operations':[],'authentication':[],'unexpected':[],'subsequent_cases_stopped':False,'cleanup_required':True,'fixture_owner_bypass_restored':False,'evidence_complete':True,'database_posture':'D','limits':packet['scope_limits']};self.save()
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

def coordinator_type(context,base):
 class Coordinator(base['coordinator_type'](context)):
  def __init__(self,plan,packet,native,target,evidence,protocol,session_factory=None,clock=time.monotonic,sleep=time.sleep):
   super().__init__(plan,packet,native,target,evidence,protocol,session_factory);self.checkpoint_committed=False;self.clock=clock;self.sleep=sleep
   self.leases={key:secrets.token_hex(32) for key in ('A1','A2','B1','C1')};need(len(set(self.leases.values()))==4,'FOUR_PRIVATE_PREIMAGES_REQUIRED')
   self.current_lease={label:label+'1' for label in 'ABC'};self.fences=dict.fromkeys('ABC',0);self.linked=dict.fromkeys('ABC',False);self.completed_a=False;self.audit2=False;self.work_xids={};self.counts={table:0 for table in packet['setup_expected_counts']};self.concurrent_old=None
  def text(self,name):return checked_sql(self.packet,name)
  def session(self,role):
   value=super().session(role);need(len([s for s in self.sessions if not s.closed and s.role=='wa_worker'])<=2 and len([s for s in self.sessions if not s.closed])<=3,'FINITE_LIVE_CLIENT_BOUND');return value
  def reclaim_clients(self,new):
   old=self.concurrent_old;need(old is not None and not old.closed and old.role==new.role=='wa_worker','EXACT_RECLAIM_PARTICIPANTS_REQUIRED');parts=[]
   for session in (old,new):
    b=session.backend;parts.append('(pid='+b['pid']+' AND backend_start='+quote(b['started'])+"::timestamptz AND usename='wa_worker' AND datname='wa_p0c_rehearsal')")
   query="SELECT jsonb_build_object('clients',count(*),'only_exact_participants',coalesce(bool_and("+' OR '.join(parts)+"),false)) FROM pg_stat_activity WHERE backend_type='client backend' AND pid<>pg_backend_pid();"
   observed=unique_json(self.raw('postgres',query));need(canonical(observed)==canonical({'clients':2,'only_exact_participants':True}),'UNDECLARED_CLIENT_DURING_RECLAIM');self.record({'stage':'EXACT_TWO_RECLAIM_CLIENTS','two_captured_workers_only':True,'all_other_database_role_tag_clients_absent':True})
  def trigger_observer(self):
   self.native_parity('FULL_NATIVE_FIXTURE_GUARD_PARITY')
  def transaction(self,name,grant_name,filename,expected_records,lease=None,fence=None,global_after=True):
   template=self.packet['grants'][grant_name];record={'stage':'RESTRICTED_TRANSACTION','name':name,'login':template['database_login_role'],'issuer_committed':False,'same_tuple_verified':False,'operation_closed':False};self.record(record)
   session=None;instance=None;primary=None;rows=None;ack=None;errors=None;code=None;backend=None;result_received=False;client_exit_received=False
   try:
    session=self.session(template['database_login_role']);session.begin('read committed');backend=session.capture();instance=self.issue(template,backend);record['issuer_committed']=True;self.retention([instance],True)
    rows,ack,errors=session.call('SELECT pg_current_xact_id()::text='+quote(backend['xid'])+';');need(rows==['t'] and ack is True and errors=='','SAME_RESTRICTED_XID');record['same_tuple_verified']=True;self.evidence.save()
    rows,ack,errors=session.call('SELECT platform_private.bind_request_context('+quote(self.instances[instance]['secret'])+');');need(rows==[] and ack is True and errors=='','FRESH_TUPLE_CONTEXT_REQUIRED')
    if lease is not None:
     secret=self.leases[lease] if lease in self.leases else lease
     rows,ack,errors=session.call('SET LOCAL wa.lease_secret='+quote(secret)+'; SET LOCAL wa.fence='+quote(str(fence))+';');need(rows==[] and ack is True and errors=='','PRIVATE_LEASE_BINDING_REQUIRED')
    if not global_after:
     need(name==self.protocol['CASE_NAMES'][14],'ONLY_DECLARED_RECLAIM_HAS_OVERLAP');self.reclaim_clients(session)
    body=context['re'].sub(r'\A(?:(?:\s|--[^\n]*\n)*)BEGIN;','',self.text(filename),count=1);rows=None;ack=None;errors=None
    response=session.call(body);result_received=True
    need(type(response) in (tuple,list) and len(response)==3,'TYPED_OPERATION_RESULT');rows,ack,errors=response
   except BaseException as error:primary=error
   finally:
    if session is not None:
     try:code=session.close();client_exit_received=True
     except BaseException as error:
      if primary is None:primary=error
     record['operation_closed']=session.closed is True
    prior=self.evidence.finalizing;self.evidence.finalizing=True
    try:
     if primary is not None:self.evidence.stop(safe_code(primary))
     try:record['operation_observation']=self.protocol['operation_observation']({'name':name,'expected_records':expected_records},code,rows,ack,errors,self.application,result_received=result_received,client_exit_received=client_exit_received)
     except BaseException as error:
      if primary is None:primary=error
      self.evidence.stop(safe_code(error))
     try:
      if self.evidence.save() is not True and primary is None:primary=HeldFailure('SANITIZED_EVIDENCE_WRITE_UNCONFIRMED')
     except BaseException as error:
      if primary is None:primary=error
      self.evidence.stop(safe_code(error))
     try:
      if global_after:self.global_closure()
     except BaseException as error:
      if primary is None:primary=error
      self.evidence.stop(safe_code(error))
     try:
      if self.evidence.save() is not True and primary is None:primary=HeldFailure('SANITIZED_EVIDENCE_WRITE_UNCONFIRMED')
     except BaseException as error:
      if primary is None:primary=error
      self.evidence.stop(safe_code(error))
    finally:self.evidence.finalizing=prior
   if primary is not None:raise primary
   need(record['operation_closed'] is True,'RESTRICTED_CONNECTION_CLOSURE_REQUIRED');self.retention([instance],True)
   result=self.protocol['verdict']({'name':name,'expected_records':expected_records},code,rows,ack,errors,self.application);record.update(exit_code=code,verdict=result);self.evidence.save();return backend,result
  def operation(self,case,global_after=True):
   lease=case['lease']
   if lease=='A-stored-hash':lease=self.stored_hash()
   return self.transaction(case['name'],case['grant'],case['sql'],case['expected_records'],lease,case['fence'],global_after)
  def live(self,label):
   work=self.packet['roots'][label]['ids']['work'];fence=self.fences[label];secret=self.leases[self.current_lease[label]];hash_=sha(bytes.fromhex(secret));state='completed' if label=='A' and self.completed_a else 'leased'
   query="SELECT jsonb_build_object('work',count(*),'live_exact_holder',coalesce(bool_and(state="+quote(state)+' AND fence='+str(fence)+' AND attempt_count='+str(fence)+' AND lease_token_hash='+quote(hash_)+" AND lease_expires_at>clock_timestamp()),false),'service_epoch_current',EXISTS(SELECT 1 FROM platform_private.identity_service_authorization a JOIN platform_private.identity_service_receipt r ON r.id=a.identity_receipt_id AND r.service_principal=a.service_principal AND r.security_generation=a.security_generation AND r.mutation_transaction_id=a.mutation_transaction_id WHERE a.service_principal="+quote(self.packet['service_principal'])+' AND a.security_generation=0 AND a.revoked_at IS NULL AND r.revoked_at IS NULL)) FROM platform.runtime_work_item WHERE id='+quote(work)+';'
   actual=unique_json(self.raw('postgres',query));need(canonical(actual)==canonical({'work':1,'live_exact_holder':True,'service_epoch_current':True}),'LIVE_LEASE_AND_INDEPENDENT_IDENTITY_REQUIRED');self.record({'stage':'LIVE_HOLDER_CONTROL','root':label,'exact_live_holder':True,'independent_epoch_current':True})
  def work_observer(self):
   for label in 'ABC':
    ids=self.packet['roots'][label]['ids'];fence=self.fences[label];state='pending' if not fence else 'completed' if label=='A' and self.completed_a else 'leased';checks=['state='+quote(state),'fence='+str(fence),'attempt_count='+str(fence),'effect_receipt_id IS '+('NOT DISTINCT FROM '+quote(ids['effect'])+'::uuid' if self.linked[label] else 'NULL')]
    if fence:checks+=['lease_token_hash='+quote(sha(bytes.fromhex(self.leases[self.current_lease[label]]))),'lease_expires_at IS NOT NULL']
    else:checks+=['lease_token_hash IS NULL','lease_expires_at IS NULL']
    if label in self.work_xids:checks+=['mutation_transaction_id='+quote(self.work_xids[label])]
    value=unique_json(self.raw('postgres',"SELECT jsonb_build_object('count',count(*),'coherent',coalesce(bool_and("+' AND '.join(checks)+'),false)) FROM platform.runtime_work_item WHERE id='+quote(ids['work'])+';'));need(canonical(value)==canonical({'count':1,'coherent':True}),'EXACT_WORK_POINTER_FENCE_AND_TRANSACTION')
   if self.audit2:
    a=self.packet['roots']['A']['ids']['work'];value=self.raw('postgres','SELECT EXISTS(SELECT 1 FROM platform.runtime_attempt WHERE id='+quote(self.packet['attempt2'])+' AND work_item_id='+quote(a)+" AND attempt_number=2 AND fence=2 AND worker_id="+quote(self.packet['service_principal'])+" AND result='committed');");need(value=='t','EXACT_CURRENT_AUDIT_ATTEMPT_REQUIRED')
  def state(self):
   self.global_closure();value=unique_json(self.raw('postgres',self.text('complete-state-observe.sql')));need(type(value) is dict and set(value)==set(self.counts) and len(value)==42,'FULL42_TABLE_SET')
   for table,count in self.counts.items():
    actual=value[table];wanted=len(self.instances) if table=='platform.database_action_grant' else count
    need(type(actual) is dict and set(actual)=={'count','rows_sha256'} and type(actual['count']) is int and actual['count']==wanted and type(actual['rows_sha256']) is str and re.fullmatch('[0-9a-f]{64}',actual['rows_sha256']),'FULL42_TYPED_COUNTS_HASHES')
   return value
  def restore_fixture_identity(self):
   self.global_closure();actual=unique_json(self.raw('postgres',checked_source(COLLECTOR,self.plan['packet_files_sha256']).decode()));proof=self.protocol['restoration_identity'](self.native,actual);self.record({'stage':'PRE_RESTORATION_EXACT_FIVE_IDENTITY',**proof})
  def setup(self):
   self.resource();context['API']['authentication_preflight'](self.evidence,self.container);self.global_closure()
   need(self.raw('postgres',"SELECT current_setting('server_version_num')='170011' AND current_setting('log_statement')='none' AND current_setting('log_min_error_statement')='panic' AND current_setting('password_encryption')='scram-sha-256';")=='t','SAFE_SERVER_SETTINGS')
   need(self.raw('postgres',"SELECT NOT EXISTS(SELECT 1 FROM pg_auth_members WHERE member='wa_schema_owner'::regrole AND roleid=ANY(ARRAY['wa_private_helper_owner'::regrole,'wa_customer_verifier'::regrole,'wa_track_verifier'::regrole])) AND NOT has_schema_privilege('wa_private_helper_owner','platform_private','CREATE') AND NOT has_schema_privilege('wa_customer_verifier','platform_private','CREATE') AND NOT has_schema_privilege('wa_track_verifier','platform_private','CREATE');")=='t','ORIGINAL_GRANTOR_FINALIZATION_REQUIRED')
   self.native_parity('PRE_FIXTURE_FULL_NATIVE');self.state();self.bypass_open=True;self.evidence.stage('EXACT_USER_CATALOG_FIXTURE_ATTEMPT');self.fixture_commit('independent-fixtures.sql','SYNTHETIC_USER_CATALOG_ONLY');self.native_parity('POST_FIXTURE_FULL_NATIVE');self.bypass_open=False;self.evidence.value['fixture_owner_bypass_restored']=True
   for label in 'ABC':
    source=self.packet['roots'][label]['source'];self.transaction('source-'+label,label+'-source_customer',label+'-source-customer.sql',['WA_CUSTOMER_CONTROL_READY_TO_COMMIT'])
    actual=unique_json(self.raw('postgres',self.text(label+'-source-customer-observe.sql')));need(canonical(actual)==canonical(source['observer_expected']),'GENUINE_COMPLETE_CUSTOMER_SOURCE_REQUIRED')
   self.commit('wa_identity_service_authority',self.text('identity-bootstrap.sql'),'INDEPENDENT_SYNTHETIC_SERVICE_BOOTSTRAP');self.global_closure()
   for label in 'ABC':
    backend,_=self.transaction('schedule-'+label,label+'-schedule',label+'-schedule.sql',['WA_WORKER_SCHEDULE_READY']);self.work_xids[label]=backend['xid']
   for label in 'BC':self.claim(label)
   expected=[self.protocol['marker']('B-genuine-leased-group','BEFORE'),'WA_WORKER_EFFECT_LINKED','WA_WORKER_GROUP_STAGED','WA_WORKER_CONSTRAINTS_CHECKED',{'linked_effect_matches':True,'still_leased':True},self.protocol['marker']('B-genuine-leased-group','AFTER')]
   backend,_=self.transaction('B-genuine-leased-group','B-process','B-genuine-leased-group.sql',expected,'B1',1);self.linked['B']=True;self.work_xids['B']=backend['xid'];self.claim('A')
   self.counts=deepcopy(self.packet['setup_expected_counts']);baseline=self.state();self.work_observer();self.native_parity('PRE_CHECKPOINT_FULL_NATIVE');self.evidence.value['setup_complete_state']=baseline;self.evidence.save()
  def claim(self,label):
   name=label+'-claim';expected=[self.protocol['marker'](name,'BEFORE'),{'changed':1},self.protocol['marker'](name,'AFTER')];backend,_=self.transaction(name,label+'-claim',name+'.sql',expected,label+'1',0);self.fences[label]=1;self.work_xids[label]=backend['xid']
  def stored_hash(self):
   # The actually readable column is consumed only in memory. It is never
   # substituted for a credential without the deliberate negative protocol.
   template=self.packet['grants']['A-process'];session=self.session('wa_worker');instance=None;failure=None
   try:
    session.begin('read committed');backend=session.capture();instance=self.issue(template,backend);self.retention([instance],True)
    rows,ack,errors=session.call('SELECT platform_private.bind_request_context('+quote(self.instances[instance]['secret'])+'); SET LOCAL wa.lease_secret='+quote(self.leases['A1'])+"; SET LOCAL wa.fence='1';");need(rows==[] and ack is True and errors=='','CURRENT_HASH_READ_BIND')
    rows,ack,errors=session.call('SELECT lease_token_hash FROM platform.runtime_work_item WHERE id='+quote(self.packet['roots']['A']['ids']['work'])+'; COMMIT;');need(ack is True and errors=='' and rows==[sha(bytes.fromhex(self.leases['A1']))],'ACTUAL_READABLE_HASH_REQUIRED');result=rows[0]
   except BaseException as error:failure=error
   finally:
    try:code=session.close()
    except BaseException as error:
     if failure is None:failure=error
    prior=self.evidence.finalizing;self.evidence.finalizing=True
    try:self.global_closure()
    except BaseException as error:
     if failure is None:failure=error
    finally:self.evidence.finalizing=prior
   if failure is not None:raise failure
   need(code==0 and session.closed,'HASH_READ_CLOSURE');self.retention([instance],True);self.record({'stage':'ACTUAL_HASH_READ','current_preimage_hash_matches_readable_column':True,'raw_value_retained':False});return result
  def clock_value(self,deadline,code):
   remaining=deadline-self.clock();need(remaining>0,code)
   try:result=subprocess.run(self.psql('postgres'),input=self.text('A-clock.sql'),text=True,capture_output=True,timeout=min(5.,remaining),shell=False)
   except subprocess.TimeoutExpired:raise HeldFailure('ACTUAL_CLOCK_OBSERVER_TIMEOUT') from None
   need(self.clock()<deadline,code)
   need(type(result.returncode) is int and result.returncode==0 and result.stderr=='' and len(result.stdout.encode())<=16*1024*1024,'BOUNDED_ACTUAL_CLOCK_OBSERVER_UNCONFIRMED')
   value=unique_json(result.stdout.strip());need(type(value) is dict and set(value)=={'near_expiry','expired','fence1','attempt1','exact_effect'} and all(type(v) is bool for v in value.values()) and all(value[k] is True for k in ('fence1','attempt1','exact_effect')),'BOUNDED_ACTUAL_CLOCK_SHAPE');return value
  def concurrent_reclaim(self,case):
   need(self.checkpoint_committed is True,'GENUINE_CHECKPOINT_BEFORE_ANY_CLOCK');deadline=self.clock()+150;polls=0
   while True:
    need(self.clock()<deadline,'ACTUAL_EXPIRY_BUDGET_EXHAUSTED');value=self.clock_value(deadline,'ACTUAL_EXPIRY_BUDGET_EXHAUSTED');polls+=1;need(value['expired'] is False,'OLD_HOLDER_MUST_BIND_WHILE_LIVE')
    if value['near_expiry']:break
    remaining=deadline-self.clock();need(remaining>0,'ACTUAL_EXPIRY_BUDGET_EXHAUSTED');self.sleep(min(.1,remaining))
   # Establish each deadline once. Slow responses and holder setup consume the
   # existing window; observing a late true value never starts a new window.
   near_deadline=min(deadline,self.clock()+15);old=None;failure=None;old_key=None
   try:
    need(self.clock()<near_deadline,'ACTUAL_EXPIRY_NOT_OBSERVED');self.live('A');need(self.clock()<near_deadline,'ACTUAL_EXPIRY_NOT_OBSERVED')
    old=self.session('wa_worker');self.concurrent_old=old;old.begin('read committed');backend=old.capture();old_key=self.issue(self.packet['grants']['A-process'],backend);need(self.clock()<near_deadline,'ACTUAL_EXPIRY_NOT_OBSERVED');self.retention([old_key],True);need(self.clock()<near_deadline,'ACTUAL_EXPIRY_NOT_OBSERVED')
    rows,ack,errors=old.call('SELECT platform_private.bind_request_context('+quote(self.instances[old_key]['secret'])+'); SET LOCAL wa.lease_secret='+quote(self.leases['A1'])+"; SET LOCAL wa.fence='1';");need(rows==[] and ack is True and errors=='','ORIGINAL_PROCESSING_HOLDER_BOUND')
    value=self.clock_value(near_deadline,'ACTUAL_EXPIRY_NOT_OBSERVED');need(value['expired'] is False,'LIVE_LEASE_AFTER_OLD_BIND_REQUIRED')
    while not value['expired']:
     remaining=near_deadline-self.clock();need(remaining>0,'ACTUAL_EXPIRY_NOT_OBSERVED');self.sleep(min(.1,remaining));value=self.clock_value(near_deadline,'ACTUAL_EXPIRY_NOT_OBSERVED')
    need(self.clock()<near_deadline,'ACTUAL_EXPIRY_NOT_OBSERVED');reclaim_backend,result=self.operation(case,global_after=False);need(self.clock()<near_deadline,'ACTUAL_EXPIRY_NOT_OBSERVED');need(reclaim_backend['pid']!=backend['pid'] and reclaim_backend['xid']!=backend['xid'],'TWO_ACTUAL_DISTINCT_WORKER_TUPLES')
    self.fences['A']=2;self.current_lease['A']='A2';self.work_xids['A']=reclaim_backend['xid'];self.retention([old_key],True);need(self.clock()<near_deadline,'ACTUAL_EXPIRY_NOT_OBSERVED');self.live('A');need(self.clock()<near_deadline,'ACTUAL_EXPIRY_NOT_OBSERVED')
    original=deepcopy(backend);again=old.capture();need(self.clock()<near_deadline,'ACTUAL_EXPIRY_NOT_OBSERVED');need(all(again[k]==original[k] for k in ('pid','started','xid','login','current_user','database','isolation')),'ORIGINAL_HOLDER_TUPLE_RETAINED')
    rows,ack,errors=old.call(self.text('old-holder-after-reclaim.sql'));code=old.close();need(old.closed,'OLD_PROCESSING_BACKEND_CLOSURE')
    expected=[self.protocol['marker']('old-holder-after-reclaim','BEFORE'),{'lease_valid':False},{'changed':0},self.protocol['marker']('old-holder-after-reclaim','AFTER')];self.protocol['verdict']({'name':'old-holder-after-reclaim','expected_records':expected},code,rows,ack,errors,self.application);self.retention([old_key],True)
    need(self.clock()<near_deadline,'ACTUAL_EXPIRY_NOT_OBSERVED');self.live('A');need(self.clock()<near_deadline,'ACTUAL_EXPIRY_NOT_OBSERVED');self.record({'stage':'ACTUAL_RECLAIM_ORDERING','distinct_overlapping_original_sessions':True,'original_tuple_retained':True,'new_reclaim_commit_before_old_action':True,'old_current_unrevoked_unexpired_grant':True,'old_protected_change_count':0,'effect_link_retained':True,'actual_clock_expiry':True,'clock_polls':polls})
   except BaseException as error:failure=error
   finally:
    if old is not None and not old.closed:
     try:old.close()
     except BaseException as error:
      if failure is None:failure=error
    self.concurrent_old=None;prior=self.evidence.finalizing;self.evidence.finalizing=True
    try:self.global_closure()
    except BaseException as error:
     if failure is None:failure=error
    finally:self.evidence.finalizing=prior
   if failure is not None:raise failure
   return result
  def run_case(self,case):
   self.evidence.value['current_case']=case['name'];self.evidence.stage('FINITE_WORKER_PROTOCOL');before=self.state()
   if case['kind']=='concurrent':result=self.concurrent_reclaim(case)
   else:
    self.live(case['root']);backend,result=self.operation(case)
    if case['name']==self.packet['cases'][0]['name']:self.linked['A']=True;self.work_xids['A']=backend['xid'];self.counts=deepcopy(self.packet['checkpoint_expected_counts'])
    if case['name']==self.packet['cases'][15]['name']:self.audit2=True;self.counts['platform.runtime_attempt']=3
    if case['name']==self.packet['cases'][20]['name']:self.completed_a=True;self.work_xids['A']=backend['xid']
    self.live(case['root'])
   after=self.state();self.work_observer();self.retention(list(self.instances));allowed=set(case['allowed_changed_tables'])|{'platform.database_action_grant'}
   need(all(canonical(before[t])==canonical(after[t]) for t in before if t not in allowed),'UNDECLARED_COMPLETE42_DATA_CHANGE')
   if case['name']==self.packet['cases'][0]['name']:
    self.native_parity('GENUINE_LEASED_CHECKPOINT_NATIVE');self.checkpoint_committed=True;self.record({'stage':'GENUINE_LEASED_CHECKPOINT','actual_worker_commit':True,'all_deferred_guards_preserved':True,'work_still_leased_with_exact_committed_effect_inbox':True})
   self.evidence.value['results'].append({'case':case['name'],'status':'PASS_FINITE_WORKER_PROTOCOL_ONLY','connections_closed_before_terminal_observers':True,'tables_observed':42,'complete_state_sha256':digest(after),'grants_retained':len(self.instances),**result});self.evidence.save()
  def execute(self):
   self.setup();self.protocol['finite_driver'](self);need(self.checkpoint_committed and self.audit2 and self.completed_a,'EXACT21_COMPLETION_REQUIRED');self.native_parity('FINAL_FULL_NATIVE_PARITY');self.evidence.value.update(status='PASS_FINITE_WORKER_RECOVERY_CORE_ONLY',current_case=None,current_stage='COMPLETE');self.evidence.save()
 return Coordinator

def safe_code(error):
 allowed={'GENUINE_LEASED_CHECKPOINT_REQUIRED_BEFORE_RECOVERY','GENUINE_CHECKPOINT_BEFORE_ANY_CLOCK','ACKNOWLEDGED_SOURCE_COMMIT_REQUIRED','INTENDED_SOURCE_GUARD_REQUIRED','EXACT_STAGE_AND_RECORD_SEQUENCE','EXACT_RECORD_COUNT','FULL42_TABLE_SET','FULL42_TYPED_COUNTS_HASHES','UNDECLARED_COMPLETE42_DATA_CHANGE','LIVE_LEASE_AND_INDEPENDENT_IDENTITY_REQUIRED','IMMUTABLE_21_FIELD_ISSUER_RETENTION','EXACT_WORK_POINTER_FENCE_AND_TRANSACTION','EXACT_CURRENT_AUDIT_ATTEMPT_REQUIRED','ACTUAL_EXPIRY_BUDGET_EXHAUSTED','OLD_HOLDER_MUST_BIND_WHILE_LIVE','ACTUAL_EXPIRY_NOT_OBSERVED','ORIGINAL_HOLDER_TUPLE_RETAINED','TWO_ACTUAL_DISTINCT_WORKER_TUPLES','SANITIZED_EVIDENCE_WRITE_UNCONFIRMED','GLOBAL_BACKEND_CLOSURE_UNCONFIRMED','NATIVE_TRIGGER_FUNCTION_ACL_DRIFT','RESTRICTED_CONNECTION_CLOSURE_REQUIRED','SOURCE_FILE_DRIFT','SOURCE_FILE_UNAVAILABLE','PREPARED_SQL_DRIFT'}
 allowed|={'ACTUAL_CLOCK_OBSERVER_TIMEOUT','BOUNDED_ACTUAL_CLOCK_OBSERVER_UNCONFIRMED','TYPED_OPERATION_RESULT','BOUNDED_OPERATION_DIAGNOSTIC'}
 code=getattr(error,'code',None);return code if type(code) is str and code in allowed else 'UNEXPECTED_WORKER_PROTOCOL_FAILURE'

def coordinate(plan,evidence_directory):
 packet,native,target,protocol,context,base=load_inputs(plan);evidence=Evidence(evidence_directory,plan,packet);coordinator=coordinator_type(context,base)(plan,packet,native,target,evidence,protocol)
 try:coordinator.execute()
 except BaseException as error:evidence.stop(safe_code(error));evidence.finalizing=True;evidence.save()
 finally:
  evidence.finalizing=True
  for session in coordinator.sessions:
   if not session.closed:
    try:session.close()
    except BaseException:evidence.stop('ORIGINAL_CONNECTION_CLOSURE_UNCONFIRMED','FINALLY')
  absent=False
  try:coordinator.global_closure();absent=True
  except BaseException:evidence.stop('GLOBAL_BACKEND_CLOSURE_UNCONFIRMED','FINALLY')
  if absent:
   restored=True
   if coordinator.bypass_open:
    try:coordinator.restore_fixture_identity();coordinator.fixture_commit('exact-fixture-restore.sql','FINALLY_EXACT_FIVE_FIXTURE_RESTORE');coordinator.bypass_open=False
    except BaseException:restored=False;evidence.stop('EXACT_FIXTURE_RESTORATION_UNCONFIRMED','FINALLY')
   try:coordinator.native_parity('FINALLY_FULL_NATIVE_PARITY')
   except BaseException:restored=False;evidence.stop('FINAL_NATIVE_PARITY_UNCONFIRMED','FINALLY')
   evidence.value['fixture_owner_bypass_restored']=restored
  try:
   for relative in plan['packet_files_sha256']:checked_source(relative,plan['packet_files_sha256'])
   evidence.value['source_packet_unchanged_after']=True
  except BaseException:evidence.value['source_packet_unchanged_after']=False;evidence.stop('SOURCE_PACKET_DRIFT','POSTCHECK')
  secrets_to_scan=list(coordinator.leases.values())+[v[k] for v in coordinator.instances.values() for k in ('secret','token_hash')]
  if any(secret in canonical(evidence.value) for secret in secrets_to_scan):
   evidence.value={k:evidence.value[k] for k in ('schema','run_id','database_posture')};evidence.value.update(status='STOPPED_PARTIAL_EVIDENCE_PRESERVED',current_stage='SANITIZATION',current_case=None,results=[],operations=[],unexpected=[],subsequent_cases_stopped=True,evidence_complete=False);evidence.stop('SECRET_EVIDENCE_EXCLUSION','SANITIZATION')
  else:evidence.value['sanitization']={'context_and_lease_secrets_or_hashes_found':False,'raw_errors_handles_statement_bodies_or_row_values_retained':False}
  evidence.save()
 return evidence.value

def main(argv=None):
 parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--execute-reviewed-worker-recovery',action='store_true');parser.add_argument('--run-plan',type=Path);parser.add_argument('--evidence-directory',type=Path);args=parser.parse_args(argv)
 try:
  need(args.execute_reviewed_worker_recovery and args.run_plan is not None and args.evidence_directory is not None,'EXPLICIT_REVIEWED_EXECUTION_REQUIRED');value=coordinate(unique_json(external(args.run_plan).read_bytes()),args.evidence_directory);print(json.dumps({'status':value['status'],'completed_protocols':len(value['results']),'raw_output_discarded':True}));return 0 if not value['unexpected'] and value['evidence_complete'] is True else 1
 except BaseException:print(json.dumps({'status':'HELD_OR_STOPPED','code':'WORKER_RECOVERY_COORDINATOR_REFUSED','raw_output_discarded':True}));return 1
if __name__=='__main__':raise SystemExit(main())

