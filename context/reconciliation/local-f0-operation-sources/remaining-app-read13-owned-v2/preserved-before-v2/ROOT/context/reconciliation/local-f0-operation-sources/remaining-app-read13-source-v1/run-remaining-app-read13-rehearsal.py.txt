"""Dormant Read13 SQL SELECT coordinator. Import and --help run no helpers."""
import argparse
import builtins
from contextlib import redirect_stdout,redirect_stderr
from copy import deepcopy
import hashlib
import io
import json
import os
from pathlib import Path
import re
import secrets
import stat
import subprocess
import time
from types import ModuleType
import uuid

ROOT=Path(__file__).resolve().parents[2]
TASK=ROOT.parent
PACKET=ROOT/'review-output/remaining-app-read13-rehearsal'
SELF='scripts/sql-review/run-remaining-app-read13-rehearsal.py'
PROTOCOL='scripts/remaining_app_read13_protocol.py'
GENERATOR='scripts/prepare-remaining-app-read13-rehearsal.py'
CONTEXT='scripts/sql-review/run-context-control-rehearsal.py'
BASE='scripts/sql-review/run-scoped-read-companion-rehearsal.py'
COLLECTOR='scripts/sql-review/collect_native_catalog.sql'
APPLICATION='review-output/foundation-application.review.sql'
VALIDATION='context/reconciliation/local-f0-remaining-app-read13-source-validation.json'
HELPERS=(CONTEXT,BASE,'scripts/scoped_read_companion_protocol.py','scripts/sql-review/run-first-rehearsal.py',
 'scripts/sql-review/run-local-f0-migrate.py','scripts/sql-review/rehearsal-diagnostics.py','scripts/prepare-local-f0-history.py')
APPLICATION_SHA='5ae39abf991f9c189e367eb6ab6968b0ad50836bf4220ac27ef8c18306ac26ad'
EXPECTED_CATALOG='3be81a13d3bb2abb41bf03ef68398da6d92fbdbccffec3d74508e91dd455f433'

class HeldFailure(Exception):
 def __init__(self,code):self.code=code;super().__init__(code)
def need(value,code):
 if not value:raise HeldFailure(code)
def sha(raw):return hashlib.sha256(raw).hexdigest()
def canonical(value):return json.dumps(value,sort_keys=True,separators=(',',':'),ensure_ascii=False,allow_nan=False)
def digest(value):return sha(canonical(value).encode())
def quote(value):return "'"+str(value).replace("'","''")+"'"
def binder_projection(value,application):
 keys={'matched','sqlstate','source_frame_verified','source_body_sha256','source_body_line','classification'}
 need(type(value)is dict and set(value)==keys and sha(application.encode())==APPLICATION_SHA,'CLOSED_BINDER_DIAGNOSTIC_SHAPE')
 body=re.search(r'CREATE FUNCTION platform_private\.bind_request_context\(secret text\).*?AS\s+(\$[a-z_0-9]*\$)(.*?)\1;',application,re.S)
 need(body is not None,'BINDER_SOURCE_BODY');body=body[2];lines=[i for i,line in enumerate(body.split('\n'),1)if "RAISE EXCEPTION 'invalid, stale or unsupported context'"in line]
 need(len(lines)==1,'BINDER_SOURCE_LINE')
 expected={'matched':True,'sqlstate':'42501','source_frame_verified':True,'source_body_sha256':sha(body.encode()),'source_body_line':lines[0],'classification':'EXPECTED_BINDER_SOURCE_GUARD'}
 need(canonical(value)==canonical(expected),'EXACT_BINDER_DIAGNOSTIC_PROJECTION');return expected
def unique_json(raw):
 def pairs(items):
  result={}
  for key,value in items:need(key not in result,'DUPLICATE_JSON_FIELD');result[key]=value
  return result
 try:return json.loads(raw,object_pairs_hook=pairs,parse_constant=lambda _:(_ for _ in ()).throw(HeldFailure('NONFINITE_JSON')))
 except HeldFailure:raise
 except BaseException:raise HeldFailure('MALFORMED_JSON') from None
def source_path(relative):
 need(type(relative) is str and '\\' not in relative and ':' not in relative and not relative.startswith('/') and all(p not in ('','.','..') for p in relative.split('/')),'SOURCE_PATH')
 raw=ROOT/relative
 need(not any(path.is_symlink() for path in (raw,*raw.parents) if path!=ROOT.parent),'SOURCE_SYMLINK_REFUSED')
 try:metadata=raw.lstat()
 except OSError:raise HeldFailure('SOURCE_FILE_UNAVAILABLE') from None
 need(not raw.is_symlink() and stat.S_ISREG(metadata.st_mode),'SOURCE_REGULAR_FILE')
 resolved=raw.resolve();need(resolved.is_relative_to(ROOT.resolve()),'SOURCE_PATH_ESCAPE');return raw
def external(value):
 path=Path(value);need(path.is_absolute(),'EXTERNAL_ABSOLUTE_PATH');path=path.resolve()
 need(path.is_relative_to(TASK.resolve()) and not path.is_relative_to(ROOT.resolve()),'EXTERNAL_TASK_PATH');return path
def checked_source(relative,pins):
 need(relative in pins,'SOURCE_NOT_ADMITTED')
 try:raw=source_path(relative).read_bytes()
 except OSError:raise HeldFailure('SOURCE_FILE_UNAVAILABLE') from None
 need(sha(raw)==pins[relative],'SOURCE_FILE_DRIFT');return raw
def compiled(raw,relative,imports=None):
 imports=imports or {};ordinary=builtins.__import__;namespace={'__name__':'_read13_reviewed','__file__':str(source_path(relative))}
 def closed_import(name,globals=None,locals=None,fromlist=(),level=0):
  need(level==0,'RELATIVE_HELPER_IMPORT_REFUSED')
  if name in imports:
   module=ModuleType(name);module.__dict__.update(imports[name]);return module
  need(name.split('.')[0] in {'argparse','builtins','contextlib','copy','datetime','hashlib','io','json','os','pathlib','queue','re','secrets','stat','subprocess','threading','time','types','uuid'},'HELPER_IMPORT_CLOSURE')
  return ordinary(name,globals,locals,fromlist,level)
 namespace['__builtins__']={**vars(builtins),'__import__':closed_import};output=io.StringIO()
 try:
  with redirect_stdout(output),redirect_stderr(output):exec(compile(raw,str(source_path(relative)),'exec'),namespace)
 except BaseException:raise HeldFailure('VERIFIED_MODULE_LOAD_REFUSED') from None
 need(not output.getvalue(),'VERIFIED_MODULE_OUTPUT_REFUSED');return namespace

def load_inputs(plan):
 keys={'schema','scope','run_id','source_commit','source_tree','packet_sha256','packet_files_sha256','reviewed_packet_sha256','reviewed_content_sha256','target_manifest','immutable_container_id','native_snapshot','native_comparison','native_attestation','scenario_names'}
 need(type(plan) is dict and set(plan)==keys,'RUN_PLAN_FIELDS')
 need(plan['schema']=='workinants.remaining-app-read13-run.v1' and plan['scope']=='REVIEWED_REMAINING13_APP_SELECT_ONLY','RUN_PLAN_SCOPE')
 need(type(plan['run_id']) is str and str(uuid.UUID(plan['run_id']))==plan['run_id'] and uuid.UUID(plan['run_id']).version==4,'RUN_UUID4')
 for key in ('source_commit','source_tree'):need(type(plan[key]) is str and re.fullmatch('[0-9a-f]{40}',plan[key]),'SOURCE_CHECKPOINT')
 need(type(plan['immutable_container_id']) is str and re.fullmatch('[0-9a-f]{64}',plan['immutable_container_id']),'IMMUTABLE_CREATED_CID')
 pins=plan['packet_files_sha256'];need(type(pins) is dict and pins and all(type(v) is str and re.fullmatch('[0-9a-f]{64}',v) for v in pins.values()),'CLOSED_PACKET_PINS')
 need(sha(''.join(k+'\0'+pins[k]+'\n' for k in sorted(pins)).encode())==plan['packet_sha256'],'CLOSED_PACKET_AGGREGATE')
 blobs={name:checked_source(name,pins) for name in pins}
 need(all(name in blobs for name in (SELF,PROTOCOL,GENERATOR,VALIDATION,APPLICATION,COLLECTOR,*HELPERS)),'COMPLETE_TRANSITIVE_SOURCE_CLOSURE')
 validation=unique_json(blobs[VALIDATION]);review=validation.get('independent_source_review',{});need(review.get('decision')=='SOURCE_APPROVED','INDEPENDENT_READ13_SOURCE_REVIEW_REQUIRED')
 need(validation.get('fixture_sha256')==plan['reviewed_packet_sha256'] and validation.get('content_sha256')==plan['reviewed_content_sha256'],'SOURCE_REVIEW_FIXTURE_BINDING')
 for mapping in(validation.get('source_files_sha256'),validation.get('archive_files_sha256')):
  need(type(mapping)is dict and mapping and all(pins.get(path)==wanted and path in blobs for path,wanted in mapping.items()),'SOURCE_REVIEW_FULL_GRAPH_BINDING')
 need(type(review.get('path'))is str and review['path'].startswith('context/reconciliation/local-f0-operation-sources/remaining-app-read13-source-v1/')and pins.get(review['path'])==review.get('sha256')and review['path']in blobs,'SOURCE_REVIEW_RECORD_ADMISSION')
 path='review-output/remaining-app-read13-rehearsal/fixtures.json';need(path in blobs and sha(blobs[path])==plan['reviewed_packet_sha256'],'REVIEWED_FIXTURE_FILE')
 packet=unique_json(blobs[path]);need(packet['schema']=='workinants.remaining-app-read13-fixtures.v1' and packet['status']=='NOT_RUN' and packet['database_posture']=='D' and packet['database_contacted'] is False and packet['sql_executed'] is False,'SOURCE_PACKET_SCOPE')
 need(packet['fixture_run_id']==plan['run_id'],'FROZEN_FRESH_FIXTURE_UUID')
 need(digest({k:packet[k] for k in ('source_files_sha256','prepared_files_sha256')})==packet['source_only_packet_sha256']==plan['reviewed_content_sha256'],'REVIEWED_CONTENT_AGGREGATE')
 for path,h in packet['source_files_sha256'].items():need(pins.get(path)==h and sha(blobs[path])==h,'PACKET_SOURCE_BINDING')
 need(pins[APPLICATION]==APPLICATION_SHA,'CANONICAL_APPLICATION_SOURCE')
 for name,h in packet['prepared_files_sha256'].items():need(Path(name).name==name and pins.get('review-output/remaining-app-read13-rehearsal/'+name)==h and sha(blobs['review-output/remaining-app-read13-rehearsal/'+name])==h,'PREPARED_ARTIFACT_BINDING')
 need(plan['scenario_names']==[c['name'] for c in packet['cases']] and len(packet['cases'])==82 and all(c['status']=='NOT_RUN' for c in packet['cases']),'EXACT82_FINITE_CASES')
 documents={}
 for key in ('native_snapshot','native_comparison','native_attestation'):
  entry=plan[key];need(type(entry) is dict and set(entry)=={'path','sha256'},'NATIVE_FILE_BINDING_FIELDS')
  raw=external(entry['path']).read_bytes();need(sha(raw)==entry['sha256'],'NATIVE_FILE_DRIFT');documents[key]=unique_json(raw)
 native,comparison,attestation=(documents[k] for k in ('native_snapshot','native_comparison','native_attestation'))
 need(native.get('format')=='workinants.native-catalog.v1' and type(native.get('server_version_num')) is int and native['server_version_num']==170011 and native.get('read_only') is True and native.get('collected_as')=='postgres' and native.get('collector_is_superuser') is True,'NATIVE_COLLECTOR_IDENTITY')
 need(type(comparison.get('check_counts')) is dict and set(comparison['check_counts'])=={'PASS'} and type(comparison['check_counts']['PASS']) is int and comparison['check_counts']['PASS']==29089,'FULL_NATIVE_TYPED_29089')
 need(comparison.get('format')=='workinants.catalog-comparison.v1' and comparison.get('status')=='PASS' and comparison.get('source_expected_sha256')==EXPECTED_CATALOG and comparison.get('native_snapshot_sha256')==digest(native) and comparison.get('findings')==[],'FULL_NATIVE_COMPARISON_PASS')
 expected={'schema':'workinants.remaining-app-read13-native-attestation.v1','run_id':plan['run_id'],'container_id':plan['immutable_container_id'],'source_commit':plan['source_commit'],'source_tree':plan['source_tree'],'packet_sha256':plan['packet_sha256'],'collector_sha256':pins[COLLECTOR],'source_expected_sha256':EXPECTED_CATALOG,'native_snapshot_sha256':digest(native),'native_comparison_file_sha256':plan['native_comparison']['sha256'],'original_grantor_finalized':True,'operation_backends_absent':True,'comparison_status':'PASS'}
 need(canonical(attestation)==canonical(expected),'SAME_SOURCE_RUN_CID_NATIVE_ATTESTATION')
 # All data and transitive executable bytes are admitted before the first compile.
 protocol=compiled(blobs[PROTOCOL],PROTOCOL);need(canonical(packet['finite_caps'])==canonical(protocol['FINITE']),'EXACT_TYPED_FINITE_CAPS')
 generator=compiled(blobs[GENERATOR],GENERATOR,{'remaining_app_read13_protocol':protocol})
 reproduced,reproduced_packet=generator['build'](ROOT,plan['run_id'])
 for name,text in reproduced.items():need(blobs.get('review-output/remaining-app-read13-rehearsal/'+name)==text.encode(),'PURE_SOURCE_PACKET_REPRODUCTION')
 need(canonical(reproduced_packet)==canonical(packet),'PURE_FIXTURE_REPRODUCTION')
 context=compiled(blobs[CONTEXT],CONTEXT);context['load_helpers'](blobs)
 target=context['HOST']['validate_manifest'](plan['target_manifest']);need(target['run_id']==plan['run_id'] and target['source']['integrated_sql_sha256']==APPLICATION_SHA,'TARGET_RUN_SOURCE_BINDING')
 base=compiled(blobs[BASE],BASE)
 for name in pins:checked_source(name,pins)
 sql={name:blobs['review-output/remaining-app-read13-rehearsal/'+name].decode('utf8') for name in packet['prepared_files_sha256'] if name.endswith('.sql')}
 return packet,native,target,protocol,context,base,sql

class Evidence:
 def __init__(self,path,plan,packet):
  self.directory=external(path);need(not self.directory.exists(),'FRESH_EXTERNAL_EVIDENCE_DIRECTORY');self.directory.mkdir();self.path=self.directory/'remaining-app-read13-results.json';self.finalizing=False;self.failed=False
  self.value={'schema':'workinants.remaining-app-read13-evidence.v1','status':'IN_PROGRESS','current_stage':'ENTRY','current_case':None,'run_id':plan['run_id'],'container_id':plan['immutable_container_id'],'source_commit':plan['source_commit'],'source_tree':plan['source_tree'],'packet_sha256':plan['packet_sha256'],'reviewed_packet_sha256':plan['reviewed_packet_sha256'],'reviewed_content_sha256':plan['reviewed_content_sha256'],'selected_controls':[{'id':x,'status':'NOT_RUN'} for x in packet['selected_control_ids']],'results':[],'operations':[],'authentication':[],'unexpected':[],'subsequent_cases_stopped':False,'cleanup_required':True,'fixture_owner_bypass_restored':False,'evidence_complete':True,'database_posture':'D','limits':packet['scope_limits']};self.save()
 def stop(self,code,stage=None):
  self.value.update(status='STOPPED_PARTIAL_EVIDENCE_PRESERVED',subsequent_cases_stopped=True)
  item={'stage':stage or self.value['current_stage'],'case':self.value['current_case'],'code':code}
  if item not in self.value['unexpected']:self.value['unexpected'].append(item)
 def save(self):
  try:
   temporary=self.path.with_suffix('.json.tmp')
   with temporary.open('w',encoding='utf8',newline='\n') as stream:stream.write(json.dumps(self.value,indent=2,ensure_ascii=False,allow_nan=False)+'\n');stream.flush();os.fsync(stream.fileno())
   temporary.replace(self.path);return True
  except BaseException:
   self.failed=True;self.value['evidence_complete']=False;self.stop('SANITIZED_EVIDENCE_WRITE_UNCONFIRMED')
   if not self.finalizing:raise HeldFailure('SANITIZED_EVIDENCE_WRITE_UNCONFIRMED') from None
   return False
 def stage(self,value):self.value['current_stage']=value;self.save()

def coordinator_type(context,base):
 class Coordinator(base['coordinator_type'](context)):
  def __init__(self,plan,packet,native,target,evidence,protocol,sql,session_factory=None):
   super().__init__(plan,packet,native,target,evidence,protocol,session_factory);self.sql=dict(sql);self.counts=dict.fromkeys(packet['setup_expected_counts'],0);self.setup_xids=set();self.revoked=set();self.collector=checked_source(COLLECTOR,plan['packet_files_sha256']).decode()
  def text(self,name):need(name in self.sql,'CACHED_FIXED_SQL_NAME');return self.sql[name]
  def barrier(self):need(not self.evidence.failed and not self.evidence.value['unexpected'],'EVIDENCE_BARRIER_STOP')
  def quiet_save(self):
   prior=self.evidence.finalizing;self.evidence.finalizing=True
   try:return self.evidence.save()
   except BaseException:
    self.evidence.failed=True;self.evidence.value['evidence_complete']=False;self.evidence.stop('SANITIZED_EVIDENCE_WRITE_UNCONFIRMED');return False
   finally:self.evidence.finalizing=prior
  def global_closure(self):
   observation={'scope':'ALL_DATABASES_ALL_CLIENT_ROLES_EXCEPT_THIS_OBSERVER','observation_completed':False,'all_other_clients_absent':False};failure=None
   try:
    actual=unique_json(self.raw('postgres',"SELECT jsonb_build_object('other_clients',(SELECT count(*) FROM pg_stat_activity WHERE backend_type='client backend' AND pid<>pg_backend_pid()));"))
    need(type(actual) is dict and set(actual)=={'other_clients'} and type(actual['other_clients']) is int and actual['other_clients']>=0,'GLOBAL_BACKEND_CLOSURE_SHAPE');observation['observation_completed']=True;observation['all_other_clients_absent']=actual['other_clients']==0
    need(observation['all_other_clients_absent'],'GLOBAL_BACKEND_CLOSURE_UNCONFIRMED')
   except BaseException as error:failure=error;self.evidence.stop(safe_code(error))
   finally:self.evidence.value['operations'].append({'stage':'GLOBAL_BACKEND_CLOSURE',**observation});self.quiet_save()
   if failure is not None:raise failure
   return True
  def native_parity(self,label):
   self.global_closure();actual=unique_json(self.raw('postgres',self.collector));need(digest(actual)==digest(self.native),'FULL_NATIVE_IDENTITY_DRIFT');self.record({'stage':label,'full_native_identity_match':True,'native_sha256':digest(actual)})
  def restoration_identity(self):
   self.global_closure();actual=unique_json(self.raw('postgres',self.collector));proof=self.protocol['restoration_identity'](self.native,actual,self.packet['fixture_plan']['trigger_setup_allowlist'],True);self.evidence.value['operations'].append({'stage':'EXACT15_RESTORE_ELIGIBILITY',**proof});self.quiet_save()
  def trigger_observer(self):
   self.global_closure();actual=unique_json(self.raw('postgres',self.collector));proof=self.protocol['restoration_identity'](self.native,actual,self.packet['fixture_plan']['trigger_setup_allowlist'],False);self.record({'stage':'ALL100_GUARDS_RESTORED',**proof})
  def state(self):
   self.global_closure();actual=unique_json(self.raw('postgres',self.text('complete-state-observe.sql')));need(type(actual) is dict and set(actual)==set(self.counts) and len(actual)==42,'COMPLETE42_TABLE_SET')
   for table,count in self.counts.items():
    row=actual[table];wanted=len(self.instances) if table=='platform.database_action_grant' else count
    need(type(row) is dict and set(row)=={'count','rows_sha256'} and type(row['count']) is int and row['count']==wanted and type(row['rows_sha256']) is str and re.fullmatch('[0-9a-f]{64}',row['rows_sha256']),'COMPLETE42_TYPED_COUNTS_HASHES')
   return actual
  def issue(self,template,backend,short=False):
   self.barrier();self.sequence+=1;need(self.sequence<=79,'EXACT79_ISSUED_GRANT_LIMIT')
   identity=str(uuid.uuid4());secret=secrets.token_hex(32);token_hash=sha(bytes.fromhex(secret));issuer=None;primary=None;code=None;instance=None
   record={'stage':'SEPARATE_ISSUER_COMMIT','issuer_committed':False,'created_at_return_verified':False,'operation_closed':False}
   self.evidence.value['operations'].append(record)
   try:
    issuer=self.session('wa_context_issuer');issuer.begin('read committed');captured=issuer.capture();values=self.grant_values(template,backend,captured,identity,token_hash)
    if short:values['expires_at']=quote(captured['clock'])+"::timestamptz+interval '10 seconds'"
    rows,ack,errors=issuer.call('INSERT INTO platform.database_action_grant ('+','.join(context['GRANT_COLUMNS'])+') VALUES ('+','.join(values[k] for k in context['GRANT_COLUMNS'])+") RETURNING jsonb_build_object('created_at',created_at); COMMIT;")
    need(ack is True and errors=='','SEPARATE_ISSUER_COMMIT_UNCONFIRMED');created=context['returned_created_at'](rows,captured['clock']);values['created_at']=quote(created)+'::timestamptz';record.update(issuer_committed=True,created_at_return_verified=True)
    instance={'id':identity,'secret':secret,'token_hash':token_hash,'values':values,'backend':deepcopy(backend),'login':'wa_app_runtime'}
   except BaseException as error:primary=error;self.evidence.stop(safe_code(error))
   finally:
    if issuer is not None:
     try:code=issuer.close()
     except BaseException as error:
      if primary is None:primary=error;self.evidence.stop(safe_code(error))
     record['operation_closed']=issuer.closed
    self.quiet_save()
   if primary is not None:raise primary
   need(record['operation_closed'] is True and type(code) is int and code==0,'SEPARATE_ISSUER_CLOSURE_REQUIRED');self.barrier();self.instances[self.sequence]=instance;return self.sequence
  def retention(self,keys,unexpired=False):
   need(keys and len(keys)==len(set(keys)) and all(k in self.instances for k in keys),'EXACT_ISSUED_INSTANCE_SET');parts=[]
   for key in keys:
    value=self.instances[key]['values'];checks=' AND '.join('g.'+column+' IS NOT DISTINCT FROM ('+value[column]+')' for column in context['GRANT_COLUMNS'])
    parts.append('SELECT ('+checks+') AS exact,g.issuer_service=session_user::text AS issuer_owned,g.expires_at>clock_timestamp() AS unexpired FROM platform.database_action_grant g WHERE g.id='+value['id'])
   query="SELECT jsonb_build_object('count',count(*),'exact',coalesce(bool_and(exact),false),'issuer_owned',coalesce(bool_and(issuer_owned),false),'unexpired',coalesce(bool_and(unexpired),false)) FROM ("+' UNION ALL '.join(parts)+') observed;'
   actual=unique_json(self.raw('wa_context_issuer',query));need(type(actual) is dict and set(actual)=={'count','exact','issuer_owned','unexpired'} and type(actual['count']) is int and actual['count']==len(keys) and actual['exact'] is True and actual['issuer_owned'] is True and type(actual['unexpired']) is bool and (not unexpired or actual['unexpired'] is True),'EXACT21_GRANT_RETENTION')
   self.record({'stage':'EXACT21_GRANT_RETENTION','instances':len(keys),'all21_expected_fields_match':True,'issuer_owned':True,'unexpired_required':unexpired})
  def transaction(self,name,login,sql,grant=None,short=False,control=None):
   self.barrier();session=None;primary=None;code=None;backend=None;instance=None;exit_received=False;phase='NOT_STARTED'
   slots={key:{'received':False,'response':None}for key in self.protocol['TRANSACTION_OBSERVATION_STAGES']}
   record={'stage':'ACTUAL_TRANSACTION','case':name,'actual_login':login,'same_tuple_verified':False,'issuer_committed':False,'operation_closed':False,'global_closure_confirmed':False,'read_stage_reached':False,'commit_acknowledged':False}
   record.update(self.protocol['transaction_observation'](phase,False,None,False,None))
   self.evidence.value['operations'].append(record)
   def call(next_phase,text):
    nonlocal phase
    phase=next_phase;slot=slots[phase];slot.update(received=False,response=None)
    response=session.call(text);slot.update(received=True,response=response)
    observation=self.protocol['transaction_observation'](phase,True,response,False,None)
    need(observation['response_shape_valid'],'TYPED_TRANSACTION_RESPONSE')
    return response
   try:
    session=self.session(login);session.begin('read committed');backend=session.capture();need(backend['xid'] not in self.setup_xids,'FRESH_READ_TRANSACTION_REQUIRED')
    if grant is not None:
     instance=self.issue(grant,backend,short);record['issuer_committed']=True;self.retention([instance],True)
    rows,ack,errors=call('SAME_XID','SELECT pg_current_xact_id()::text='+quote(backend['xid'])+';');need(rows==['t'] and ack is True and errors=='','SAME_ACTUAL_TRANSACTION_XID');record['same_tuple_verified']=True
    if grant is not None:
     secret=self.instances[instance]['secret'];bind='SELECT platform_private.bind_request_context('+quote(secret)+');'
     if control=='identity_generation_mismatch':rows,ack,errors=call('BIND',bind)
     else:
      rows,ack,errors=call('BIND',bind);need(rows==[] and ack is True and errors=='','FRESH_CONTEXT_BIND_REQUIRED')
      if control=='revoked_before_action':self.revoke(instance);rows,ack,errors=call('REVOKED_REBIND',bind)
      elif control=='server_expired':self.wait_expired(instance);rows,ack,errors=call('EXPIRED_REBIND',bind)
    if control is None:
     self.barrier();record['read_stage_reached']=any(c['name']==name and c['kind']=='read' for c in self.packet['cases']);rows,ack,errors=call('BUSINESS',sql);record['commit_acknowledged']=sql.rstrip().endswith('COMMIT;') and ack is True and errors==''
   except BaseException as error:primary=error;self.evidence.stop(safe_code(error))
   finally:
    if session is not None:
     try:code=session.close();exit_received=True
     except BaseException as error:
      if primary is None:primary=error;self.evidence.stop(safe_code(error))
     record['operation_closed']=session.closed
    try:self.global_closure();record['global_closure_confirmed']=True
    except BaseException as error:
     if primary is None:primary=error;self.evidence.stop(safe_code(error))
    slot=slots[phase]
    try:
     observation=self.protocol['transaction_observation'](phase,slot['received'],slot['response'],exit_received,code)
     self.protocol['validate_transaction_observation'](observation);record.update(observation)
    except BaseException as error:
     self.evidence.failed=True;self.evidence.value['evidence_complete']=False
     record.update(self.protocol['transaction_observation'](phase,slot['received'],None,exit_received,code))
     if primary is None:primary=error;self.evidence.stop(safe_code(error))
    if not self.quiet_save() and primary is None:primary=HeldFailure('SANITIZED_EVIDENCE_WRITE_UNCONFIRMED')
   if primary is not None:raise primary
   self.barrier();need(record['operation_closed'] is True and record['global_closure_confirmed'] is True,'CLOSED_BEFORE_OBSERVER_AND_VERDICT')
   rows,ack,errors=slots[phase]['response']
   return {'code':code,'rows':rows,'ack':ack,'errors':errors,'backend':backend,'instance':instance,'record':record}
  def revoke(self,key):
   value=self.instances[key]['values'];issuer=None;primary=None;code=None
   try:
    issuer=self.session('wa_context_issuer');issuer.begin('read committed');captured=issuer.capture();rows,ack,errors=issuer.call('UPDATE platform.database_action_grant SET revoked_at=clock_timestamp() WHERE id='+value['id']+" RETURNING jsonb_build_object('revoked_at',revoked_at); COMMIT;")
    need(ack is True and errors=='' and len(rows)==1,'SEPARATE_REVOKE_COMMIT_REQUIRED');actual=unique_json(rows[0]);need(type(actual) is dict and set(actual)=={'revoked_at'} and type(actual['revoked_at']) is str and re.fullmatch(r'[0-9T:+. \-]{1,64}',actual['revoked_at']),'PRIVATE_REVOKED_AT_SHAPE')
    value['revoked_at']=quote(actual['revoked_at'])+'::timestamptz';value['mutation_transaction_id']=quote(captured['xid'])
   except BaseException as error:primary=error;self.evidence.stop(safe_code(error))
   finally:
    if issuer is not None:
     try:code=issuer.close()
     except BaseException as error:
      if primary is None:primary=error;self.evidence.stop(safe_code(error))
    self.quiet_save()
   if primary is not None:raise primary
   need(issuer is not None and issuer.closed and type(code) is int and code==0,'REVOKE_ISSUER_CLOSURE_REQUIRED');self.revoked.add(key);self.retention([key]);self.record({'stage':'SEPARATE_REVOKE_COMMIT_BEFORE_ACTION','issuer_closed':True,'same_app_transaction_remains_bound':True})
  def wait_expired(self,key):
   deadline=time.monotonic()+45;value=self.instances[key]['values'];observed=False
   while True:
    remaining=deadline-time.monotonic();need(remaining>0,'SERVER_EXPIRY_BUDGET_EXHAUSTED')
    process=subprocess.run(self.psql('wa_context_issuer'),input='SELECT clock_timestamp()>expires_at FROM platform.database_action_grant WHERE id='+value['id']+';',text=True,capture_output=True,timeout=min(5,remaining),shell=False)
    need(time.monotonic()<deadline,'SERVER_EXPIRY_BUDGET_EXHAUSTED');need(type(process.returncode) is int and process.returncode==0 and process.stderr=='' and process.stdout.strip() in ('t','f'),'BOUNDED_SERVER_CLOCK_OBSERVATION')
    if process.stdout.strip()=='t':observed=True;break
    time.sleep(min(.1,max(0,deadline-time.monotonic())))
   need(observed and time.monotonic()<deadline,'SERVER_EXPIRY_BUDGET_EXHAUSTED');self.record({'stage':'ACTUAL_SERVER_EXPIRY','clock_observed_expired':True,'monotonic_budget_seconds':45,'late_response_accepted':False})
  def setup(self):
   host=context['HOST'];process=subprocess.run;observed=host['inspect_live'](self.target,host['docker_json'](['context','inspect','desktop-linux'],process),host['docker_json'](['inspect',self.target['target']['container_name']],process),host['docker_json'](['volume','inspect',self.target['target']['volume_name']],process))
   need(observed['container_id']==self.container,'CURRENT_CREATED_CID_REQUIRED');host['verify_image'](self.target,host['docker_json'](['inspect',self.target['target']['container_name']],process),host['docker_json'](['image','inspect',self.target['target']['image']],process));context['API']['authentication_preflight'](self.evidence,self.container);self.global_closure()
   need(self.raw('postgres',"SELECT current_setting('server_version_num')='170011' AND current_setting('log_statement')='none' AND current_setting('log_min_error_statement')='panic' AND current_setting('password_encryption')='scram-sha-256';")=='t','SAFE_SERVER_SETTINGS')
   need(self.raw('postgres',"SELECT NOT EXISTS(SELECT 1 FROM pg_auth_members WHERE member='wa_schema_owner'::regrole AND roleid=ANY(ARRAY['wa_private_helper_owner'::regrole,'wa_customer_verifier'::regrole,'wa_track_verifier'::regrole])) AND NOT has_schema_privilege('wa_private_helper_owner','platform_private','CREATE') AND NOT has_schema_privilege('wa_customer_verifier','platform_private','CREATE') AND NOT has_schema_privilege('wa_track_verifier','platform_private','CREATE');")=='t','ORIGINAL_GRANTOR_FINALIZATION_REQUIRED')
   self.native_parity('PRE_SETUP_NATIVE');self.state();self.trigger_observer();self.bypass_open=True;self.evidence.stage('EXACT15_RESTORATION_OBLIGATION_RECORDED')
   result=self.transaction('DISABLE_EXACT15','postgres',self.text('fixture-disable-exact15.sql').removeprefix('BEGIN;\n'));need(type(result['code']) is int and result['code']==0 and result['ack'] is True and result['rows']==[] and result['errors']=='','EXACT15_DISABLE_COMMIT')
   for group in self.packet['setup_groups']:
    self.evidence.value['current_case']=group['name'];self.evidence.stage('SOURCE_REVIEWED_FIXTURE_GROUP');before=self.state();grant=self.packet['grants'][group['grant_id']] if group['grant_id'] else None
    result=self.transaction(group['name'],group['login'],self.text(group['sql']),grant);self.protocol['ordinary_verdict']({'expected_records':[self.protocol['marker'](group['name'],'BEFORE'),self.protocol['marker'](group['name'],'AFTER')],'claim':None},result['code'],result['rows'],result['ack'],result['errors']);need(result['record']['commit_acknowledged'] is True,'FIXTURE_COMMIT_REQUIRED')
    self.setup_xids.add(result['backend']['xid'])
    for table,increment in group['table_increments'].items():self.counts[table]+=increment
    after=self.state();allowed=set(group['table_increments'])|{'platform.database_action_grant'};need(all(canonical(before[t])==canonical(after[t]) for t in before if t not in allowed),'UNDECLARED_FIXTURE_DATA_CHANGE')
    checks=' UNION ALL '.join('SELECT mutation_transaction_id FROM '+r['table']+' WHERE id='+quote(r['values']['id']) for r in self.packet['fixture_plan']['fixture_rows'] if r['values']['id'] in group['row_ids'])
    actual=unique_json(self.raw('postgres',"SELECT jsonb_build_object('count',count(*),'same_actual_group_xid',coalesce(bool_and(mutation_transaction_id="+quote(result['backend']['xid'])+'),false)) FROM ('+checks+') facts;'))
    need(canonical(actual)==canonical({'count':len(group['row_ids']),'same_actual_group_xid':True}),'ACTUAL_SETUP_GROUP_XID_REQUIRED');self.record({'stage':'FIXTURE_GROUP_COMMITTED','name':group['name'],'rows':len(group['row_ids']),'same_actual_group_xid':True,'application_write_claim':False})
   self.restore();self.coherence();need(canonical(self.counts)==canonical(self.packet['setup_expected_counts']),'EXACT48_SETUP_COUNTS');self.native_parity('BEFORE_FIRST_SELECTED_READ');return self.state()
  def restore(self):
   self.restoration_identity();result=self.transaction('RESTORE_EXACT15','postgres',self.text('fixture-restore-exact15.sql').removeprefix('BEGIN;\n'));need(type(result['code']) is int and result['code']==0 and result['ack'] is True and result['rows']==[] and result['errors']=='','EXACT15_RESTORE_COMMIT');self.bypass_open=False;self.trigger_observer();self.native_parity('RESTORED_FULL_NATIVE');self.evidence.value['fixture_owner_bypass_restored']=True;self.evidence.save()
  def coherence(self):
   actual=unique_json(self.raw('postgres',self.text('fixture-coherence-observe.sql')));need(canonical(actual)==canonical({'rows':48,'all_source_values_match':True,'usage_source_window_sum_limit_match':True}),'EXACT48_PRIVATE_SOURCE_COHERENCE');self.record({'stage':'EXACT48_SOURCE_COHERENCE','all_static_values_and78_fk_links_match':True,'actual_pg_storage_digests_match':True,'synthetic_usage_source_window_sum_limit_match':True,'adapter_or_write_qualification':False})
  def execute(self):
   baseline=self.setup();self.evidence.value['baseline']={'tables':baseline,'sha256':digest(baseline)};self.evidence.save()
   for case in self.packet['cases']:
    self.evidence.value['current_case']=case['name'];self.evidence.stage('FINITE_READ13_PROTOCOL');self.trigger_observer();before=self.state();grant=self.packet['grants'][case['grant']] if case['grant'] else None
    result=self.transaction(case['name'],'wa_app_runtime',self.text(case['sql']),grant,case['control']=='server_expired',case['control'] if case['kind']=='binder-denial' else None)
    if case['kind']=='binder-denial':
     diagnostic=binder_projection(context['binder_diagnostic'](result['errors'],'invalid, stale or unsupported context',self.application),self.application)
     need(type(result['code']) is int and result['code']==3 and result['rows']==[] and result['ack'] is False and diagnostic['matched'] is True and diagnostic['source_frame_verified'] is True,'EXACT_BINDER_CURRENTNESS_SOURCE_GUARD')
     verdict={'status':'PASS','intended_stage':'BIND_CURRENTNESS_RECHECK','selected_reads_executed':False,'guard_diagnostic':diagnostic,'claim':None}
    else:
     if result['instance'] is not None:self.retention([result['instance']],True)
     verdict=self.protocol['ordinary_verdict'](case,result['code'],result['rows'],result['ack'],result['errors'])
    if self.instances:self.retention(list(self.instances))
    after=self.state();need(all(canonical(before[t])==canonical(after[t]) for t in before if t!='platform.database_action_grant'),'COMPLETE42_UNEXPECTED_READ_DATA_EFFECT');self.coherence();self.trigger_observer();self.barrier()
    self.evidence.value['results'].append({'case':case['name'],'claim':case['claim'],'actual_login':'wa_app_runtime','operation_closed_before_observers':True,'global_closure_confirmed':True,'all100_guards_restored':True,'tables_observed':42,'before_tables':before,'after_tables':after,'before_complete_state_sha256':digest(before),'complete_state_sha256':digest(after),'all_business_tables_unchanged':True,**verdict});self.evidence.save()
   need(len(self.evidence.value['results'])==82 and len(self.instances)==79,'EXACT82_PROTOCOLS79_GRANTS');self.native_parity('FINAL_FULL_NATIVE_PARITY');self.evidence.value.update(status='PASS_FINITE_REMAINING13_APP_SELECT_SQL_SUBSET_ONLY',current_stage='COMPLETE',current_case=None);self.evidence.save()
 return Coordinator

def safe_code(error):
 code=getattr(error,'code',None)
 allowed={'SANITIZED_EVIDENCE_WRITE_UNCONFIRMED','GLOBAL_BACKEND_CLOSURE_SHAPE','GLOBAL_BACKEND_CLOSURE_UNCONFIRMED','EXACT21_GRANT_RETENTION','EXACT_BINDER_CURRENTNESS_SOURCE_GUARD','EXACT_READ_ROWSETS_REQUIRED','CLEAN_READ_TERMINAL_REQUIRED','SERVER_EXPIRY_BUDGET_EXHAUSTED','BOUNDED_SERVER_CLOCK_OBSERVATION','SOURCE_FILE_DRIFT','SOURCE_FILE_UNAVAILABLE','FULL_NATIVE_IDENTITY_DRIFT','FULL_NATIVE_RESTORATION_IDENTITY','COMPLETE42_TABLE_SET','COMPLETE42_TYPED_COUNTS_HASHES','COMPLETE42_UNEXPECTED_READ_DATA_EFFECT','CLOSED_BEFORE_OBSERVER_AND_VERDICT','EXACT48_PRIVATE_SOURCE_COHERENCE','ACTUAL_SETUP_GROUP_XID_REQUIRED','EVIDENCE_BARRIER_STOP','SEPARATE_ISSUER_COMMIT_UNCONFIRMED','SEPARATE_ISSUER_CLOSURE_REQUIRED','SESSION_CLOSURE_UNCONFIRMED','EXACT_BACKEND_STILL_LIVE','UNOBSERVED_SESSION_OUTPUT'}
 allowed|={'TYPED_TRANSACTION_RESPONSE','FIXED_TRANSACTION_OBSERVATION_STAGE','TYPED_TRANSACTION_OBSERVATION_FLAGS','EXACT_TRANSACTION_OBSERVATION_FIELDS','TYPED_TRANSACTION_EXIT_CLASS','OBSERVED_TRANSACTION_EXIT','TYPED_TRANSACTION_EXIT','OBSERVED_TRANSACTION_RESPONSE','UNAVAILABLE_TRANSACTION_RESPONSE'}
 return code if type(code) is str and code in allowed else 'READ13_UNEXPECTED_OPERATION_FAILURE'

def finish_component(coordinator,evidence,plan):
 evidence.finalizing=True;absent=False
 for session in coordinator.sessions:
  if not session.closed:
   try:session.close()
   except BaseException:evidence.stop('OPERATION_CLOSURE_UNCONFIRMED','FINALLY')
 try:coordinator.global_closure();absent=True
 except BaseException:evidence.stop('GLOBAL_BACKEND_CLOSURE_UNCONFIRMED','FINALLY')
 if absent:
  if coordinator.bypass_open:
   # Required restoration is allowed despite a failed evidence barrier, only
   # after exact source identity and complete all-client absence were proved.
   prior_failed=evidence.failed;restored=False
   try:
    coordinator.restoration_identity();session=None;primary=None
    try:
     session=coordinator.session('postgres');session.begin('read committed');session.capture();rows,ack,errors=session.call(coordinator.text('fixture-restore-exact15.sql').removeprefix('BEGIN;\n'));need(rows==[] and ack is True and errors=='','EXACT15_RESTORE_COMMIT')
    except BaseException as error:primary=error
    finally:
     if session is not None:
      try:code=session.close();need(type(code) is int and code==0,'RESTORE_SESSION_CLOSURE')
      except BaseException as error:
       if primary is None:primary=error
     try:coordinator.global_closure()
     except BaseException as error:
      if primary is None:primary=error
    if primary is not None:raise primary
    coordinator.bypass_open=False;restored=True
   except BaseException:evidence.stop('EXACT15_RESTORATION_UNCONFIRMED','FINALLY')
   evidence.failed=evidence.failed or prior_failed
  try:coordinator.trigger_observer();coordinator.native_parity('FINALLY_FULL_NATIVE_IDENTITY');evidence.value['fixture_owner_bypass_restored']=not coordinator.bypass_open
  except BaseException:evidence.stop('ALL100_NATIVE_RESTORATION_UNCONFIRMED','FINALLY')
 try:
  for relative in plan['packet_files_sha256']:checked_source(relative,plan['packet_files_sha256'])
  evidence.value['source_packet_unchanged_after']=True
 except BaseException:evidence.value['source_packet_unchanged_after']=False;evidence.stop('SOURCE_PACKET_DRIFT','POSTCHECK')
 try:
  serialized=canonical(evidence.value)
  def strings(value):
   if type(value) is str:yield value
   elif type(value) is list:
    for item in value:yield from strings(item)
   elif type(value) is dict:
    need(not ({'pid','xid','backend_pid','transaction_id','token_hash','secret'} & set(value)),'SECRET_OR_HANDLE_FIELD')
    for item in value.values():yield from strings(item)
  retained=set(strings(evidence.value));need(all(x['secret'] not in serialized and x['token_hash'] not in serialized and x['backend']['pid'] not in retained and x['backend']['xid'] not in retained for x in coordinator.instances.values()),'SECRET_OR_HANDLE_EVIDENCE_EXCLUSION')
  evidence.value['sanitization']={'context_secrets_hashes_or_backend_handles_retained':False,'raw_stderr_statement_bodies_retained':False}
 except BaseException:
  evidence.value={k:evidence.value[k] for k in ('schema','run_id','database_posture')};evidence.value.update(status='STOPPED_PARTIAL_EVIDENCE_PRESERVED',current_stage='SANITIZATION',current_case=None,results=[],operations=[],authentication=[],unexpected=[],evidence_complete=False,subsequent_cases_stopped=True);evidence.failed=True;evidence.stop('SECRET_OR_HANDLE_EVIDENCE_EXCLUSION','SANITIZATION')
 evidence.save()

def coordinate(plan,evidence_directory):
 packet,native,target,protocol,context,base,sql=load_inputs(plan);evidence=Evidence(evidence_directory,plan,packet);coordinator=coordinator_type(context,base)(plan,packet,native,target,evidence,protocol,sql)
 try:coordinator.execute()
 except BaseException as error:evidence.stop(safe_code(error));evidence.finalizing=True;evidence.save()
 finally:
  finish_component(coordinator,evidence,plan)
 return evidence.value

def main(argv=None):
 parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--execute-reviewed-remaining-app-read13',action='store_true');parser.add_argument('--run-plan',type=Path);parser.add_argument('--evidence-directory',type=Path);args=parser.parse_args(argv)
 try:
  need(args.execute_reviewed_remaining_app_read13 and args.run_plan is not None and args.evidence_directory is not None,'EXPLICIT_REVIEWED_EXECUTION_REQUIRED');value=coordinate(unique_json(external(args.run_plan).read_bytes()),args.evidence_directory)
  print(json.dumps({'status':value['status'],'completed_protocols':len(value['results']),'raw_output_discarded':True}));return 0 if not value['unexpected'] and value['evidence_complete'] is True else 1
 except BaseException:print(json.dumps({'status':'HELD_OR_STOPPED','code':'READ13_COORDINATOR_REFUSED','raw_output_discarded':True}));return 1
if __name__=='__main__':raise SystemExit(main())
