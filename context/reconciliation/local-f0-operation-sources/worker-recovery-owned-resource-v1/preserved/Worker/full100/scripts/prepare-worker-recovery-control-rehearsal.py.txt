"""Prepare NEW exact21 worker recovery source artifacts. No process/DB API."""
import argparse
from copy import deepcopy
import json
from pathlib import Path
import re
import uuid
from worker_recovery_control_protocol import APPLICATION_SHA,PLAN_SHA,CASE_NAMES,READ_MODELS,FIXTURE_TABLES,RESULT_SCHEMA,canonical,digest,sha,quote,operation_sql,marker,need

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'review-output/worker-recovery-control-rehearsal'
GOLD='review-output/worker-control-rehearsal/'
NS=uuid.UUID('e36e6830-5b5a-4da0-b39f-4d4c01c1e230')
SERVICE='worker-recovery-core-fixture.v1'
NEW=('scripts/worker_recovery_control_protocol.py','scripts/prepare-worker-recovery-control-rehearsal.py','scripts/sql-review/run-worker-recovery-control-rehearsal.py','scripts/check-worker-recovery-control-rehearsal.py','scripts/check-worker-recovery-control-coordinator.py')
HELPERS=('scripts/sql-review/run-scoped-read-companion-rehearsal.py','scripts/scoped_read_companion_protocol.py','scripts/sql-review/run-context-control-rehearsal.py','scripts/sql-review/run-first-rehearsal.py','scripts/sql-review/run-local-f0-migrate.py','scripts/sql-review/rehearsal-diagnostics.py','scripts/prepare-local-f0-history.py','scripts/sql-review/collect_native_catalog.sql')
MODEL_KEY={'TrackSubscription':'subscription','TrackEntitlementGrant':'grant','RuntimeCommandReceipt':'command','RuntimeEffectReceipt':'effect','RuntimeAttempt':'attempt','RuntimeInboxReceipt':'inbox','OwnerMutationEvidence':'subscription-evidence','TrackBaseSelection':'selection','TrackEnrollmentReceipt':'enrollment'}
REVISION={'TrackSubscription':0,'TrackEntitlementGrant':0,'RuntimeEffectReceipt':1,'RuntimeAttempt':1,'TrackBaseSelection':0}

def uid(name):return str(uuid.uuid5(NS,name))
def sql_hash(value):return "encode(sha256(convert_to("+quote(json.dumps(value,separators=(',',':'),ensure_ascii=False))+"::jsonb::text,'UTF8')),'hex')"
def insert(table,values):return 'INSERT INTO '+table+' ('+','.join(values)+') VALUES ('+','.join(values.values())+');'

def build(root=ROOT):
 root=Path(root);gold_raw=(root/(GOLD+'fixtures.json')).read_bytes();gold=json.loads(gold_raw);original={name:(root/(GOLD+name)).read_bytes() for name in gold['prepared_files_sha256']}
 need(all(sha(raw)==gold['prepared_files_sha256'][name] for name,raw in original.items()),'GOLDEN_SQL_DRIFT')
 inputs=set(NEW+HELPERS)|set(gold['source_files_sha256'])|{GOLD+'fixtures.json',*[GOLD+name for name in original],'context/reconciliation/local-f0-assertions.json','context/reconciliation/foundation-sql-draft-models.json','context/reconciliation/foundation-sql-draft-access.json','context/reconciliation/foundation-sql-scope-policy.json','context/context-map.md'}
 blobs={name:(root/name).read_bytes() for name in sorted(inputs)};pins={name:sha(raw) for name,raw in blobs.items()}
 need(pins['review-output/foundation-application.review.sql']==APPLICATION_SHA,'CANONICAL_SQL_DRIFT')
 for name,wanted in gold['source_files_sha256'].items():need(pins[name]==wanted,'GOLDEN_SOURCE_DRIFT')
 models={r['model']:r for r in json.loads(blobs['context/reconciliation/foundation-sql-draft-models.json'])};acl=json.loads(blobs['context/reconciliation/foundation-sql-draft-access.json']);worker_acl=[r for r in acl if r['role']=='wa_worker'];need(len(worker_acl)==32,'WORKER32_CEILING')
 all_text=gold_raw.decode()+'\n'+'\n'.join(raw.decode() for raw in original.values());uuids=sorted(set(re.findall(r'\b[0-9a-f]{8}(?:-[0-9a-f]{4}){3}-[0-9a-f]{12}\b',all_text)))
 shared={gold['ids'][k] for k in ('plan','definition','benefit','identity-bootstrap','identity-rotate','identity-revoke','identity-recover')}
 maps={label:{old:uid(('shared' if old in shared else label)+'/'+old) for old in uuids} for label in 'ABC'}
 def text(label,value):
  for old,new in maps[label].items():value=value.replace(old,new)
  return value.replace(gold['fixture_values']['service_principal'],SERVICE)
 def value(label,data):return json.loads(text(label,json.dumps(data,ensure_ascii=False)))
 roots={label:{'ids':value(label,gold['ids']),'source':value(label,gold['source_customer'])} for label in 'ABC'}
 files={};grants={}
 for label in 'ABC':
  for name in ('source-customer.sql','source-customer-observe.sql','schedule.sql'):files[label+'-'+name]=text(label,original[name].decode())
  for role in ('source_customer','schedule','claim','process'):
   grant=value(label,gold['grants'][role]);grant['template_id']=label+'-'+role;grant['allowed_fields']=sorted(set(grant['allowed_fields']));grants[label+'-'+role]=grant
 files['identity-bootstrap.sql']=text('A',original['identity-bootstrap.sql'].decode())
 # Only existing reviewed synthetic User/catalog owner_commit bypasses.
 fixture=original['independent-fixtures.sql'].decode().splitlines();seed=[]
 for label in 'ABC':seed += [text(label,line) for line in fixture if line.startswith(('INSERT INTO app.users ','INSERT INTO app.user_security_profiles '))]
 seed += [text('A',line) for line in fixture if line.startswith(('INSERT INTO app.track_plans ','INSERT INTO app.track_entitlement_definitions ','INSERT INTO app.track_plan_entitlements '))]
 restore=['ALTER TABLE '+table+' ENABLE TRIGGER owner_commit;' for table in reversed(FIXTURE_TABLES)]
 files['independent-fixtures.sql']='\n'.join(['BEGIN;']+['ALTER TABLE '+table+' DISABLE TRIGGER owner_commit;' for table in FIXTURE_TABLES]+seed+['SET CONSTRAINTS ALL IMMEDIATE;']+restore+['COMMIT;'])+'\n'
 files['exact-fixture-restore.sql']='\n'.join(['BEGIN;']+restore+['COMMIT;'])+'\n'
 def cap(model,key,verb='SELECT',revision=None):
  row=[r for r in acl if (r['role'],r['model'],r['operation'])==('wa_worker',model,verb)];need(len(row)==1,'CLOSED_WORKER_ROLE_VERB')
  result=[model+'/'+key+'/'+verb+'/'+field for field in row[0]['fields']]
  if revision is not None:result.append(model+'/'+key+'/revision/'+str(revision))
  return result
 def work_caps(label,fence):
  key=roots[label]['ids']['work'];return cap('RuntimeWorkItem',key,revision=fence)+['RuntimeWorkItem/'+key+'/UPDATE/'+f for f in ('@row','state','fence','leaseTokenHash','leaseExpiresAt','attemptCount','effectReceiptId')]
 def object_key(label,model):return roots[label]['source']['ids']['free'] if model=='RuntimeOutboxMessage' else roots[label]['ids'][MODEL_KEY[model]]
 for label in 'ABC':
  proc=grants[label+'-process'];fields=set(proc['allowed_fields']);fields.update(work_caps(label,1));cmd=roots[label]['ids']['command'];fields.update('RuntimeCommandReceipt/'+cmd+'/UPDATE/'+f for f in ('@row','state','resultDigest','resultBody'))
  for foreign in 'AB':
   for model in READ_MODELS:fields.update(cap(model,object_key(foreign,model),revision=REVISION.get(model)))
   fields.update(['RuntimeWorkItem/'+roots[label]['ids']['work']+'/effect/'+roots[foreign]['ids']['effect'],'RuntimeWorkItem/'+roots[label]['ids']['work']+'/command/'+roots[foreign]['ids']['command']])
  proc['allowed_fields']=sorted(fields);proc['source_generation']='1'
  claim=grants[label+'-claim'];claim['allowed_fields']=sorted(set(work_caps(label,0)));claim['source_generation']='0'
  name=label+'-claim';work=roots[label]['ids']['work'];body="WITH changed AS (UPDATE platform.runtime_work_item SET state='leased',fence=fence+1,attempt_count=attempt_count+1,lease_token_hash=encode(sha256(decode(current_setting('wa.lease_secret'),'hex')),'hex'),lease_expires_at=clock_timestamp()+interval '"+('120' if label=='A' else '300')+" seconds' WHERE id="+quote(work)+" AND fence=0 AND state='pending' RETURNING id) SELECT jsonb_build_object('changed',count(*)) FROM changed;"
  files[name+'.sql']=operation_sql(name,body)
 # Preserve the exact registered Track command/result, SQL-storage codec and
 # every deferred business proof. Only final work completion is postponed.
 def golden_group(label,probes):
  ids=roots[label]['ids'];source=roots[label]['source'];body=[];result=value(label,gold['fixture_values']['result']);result_sql=quote(json.dumps(result,separators=(',',':')))+'::jsonb';payload=source['fixture_values']['free_command'];fingerprint=sql_hash(payload)
  command={'id':quote(ids['command']),'owner_module_id':"'track_subscription_entitlement'",'operation':"'assignDefaultFreeTrack.v1'",'subject_scope':quote('CustomerProfile:'+source['ids']['CustomerProfile']),'semantic_key':quote(value(label,gold['semantic_key'])),'fingerprint':fingerprint,'state':"'pending'",'source_revision':'0','result_schema_id':quote(RESULT_SCHEMA),'result_schema_version':"'1'",'result_digest':'NULL','result_body':'NULL'}
  body.append(insert('platform.runtime_command_receipt',command));body.append("UPDATE platform.runtime_command_receipt SET state='committed',result_digest="+sql_hash(result)+',result_body='+result_sql+' WHERE id='+quote(ids['command'])+" AND state='pending';")
  for line in text(label,original['enroll.sql'].decode()).splitlines():
   if line.startswith(('INSERT INTO platform.runtime_command_receipt','SET LOCAL','COMMIT;','UPDATE platform.runtime_work_item SET state=')):continue
   if line.startswith('INSERT INTO platform.runtime_inbox_receipt') and probes:body.append("SELECT jsonb_build_object('missing_exact_inbox_rejects',NOT platform_private.worker_effect_matches("+quote(ids['work'])+','+quote(ids['effect'])+',false));')
   body.append(line)
   if line.startswith('INSERT INTO platform.runtime_inbox_receipt') and probes:body.append("SELECT jsonb_build_object('exact_inbox_matches_before_link',platform_private.worker_effect_matches("+quote(ids['work'])+','+quote(ids['effect'])+',false));')
  body.append("SELECT jsonb_build_object('linked_effect_matches',platform_private.worker_effect_matches("+quote(ids['work'])+','+quote(ids['effect'])+",true),'still_leased',(SELECT state='leased' FROM platform.runtime_work_item WHERE id="+quote(ids['work'])+'));')
  return '\n'.join(body)+'\n'
 files['B-genuine-leased-group.sql']=operation_sql('B-genuine-leased-group',golden_group('B',False))
 cases=[]
 def add(name,grant,body,expected,kind='ordinary',lease='A1',fence=1,root_label='A',delta=None):
  file=name+'.sql';files[file]=operation_sql(name,body);records=[marker(name,'BEFORE'),*expected]+([] if kind=='diagnostic' else [marker(name,'AFTER')]);cases.append({'name':name,'grant':grant,'sql':file,'kind':kind,'expected_records':records,'lease':lease,'fence':fence,'root':root_label,'allowed_changed_tables':delta or [],'status':'NOT_RUN'})
 golden_expected=[{'missing_exact_inbox_rejects':True},{'exact_inbox_matches_before_link':True},'WA_WORKER_EFFECT_LINKED','WA_WORKER_GROUP_STAGED','WA_WORKER_CONSTRAINTS_CHECKED',{'linked_effect_matches':True,'still_leased':True}]
 add(CASE_NAMES[0],'A-process',golden_group('A',True),golden_expected,delta=['platform.runtime_command_receipt','platform.owner_mutation_evidence','platform.runtime_effect_receipt','platform.runtime_inbox_receipt','platform.runtime_attempt','platform.runtime_work_item','app.track_subscriptions','app.track_entitlement_grants','app.track_base_selection','app.track_subscription_events','app.track_enrollment_receipt'])
 for name,model in zip(CASE_NAMES[1:11],READ_MODELS):
  table=models[model]['object'];a,b=[object_key(label,model) for label in 'AB'];body="SELECT jsonb_build_object('target_count',(SELECT count(*) FROM "+table+' WHERE id='+quote(a)+"),'foreign_count',(SELECT count(*) FROM "+table+' WHERE id='+quote(b)+'));';add(name,'A-process',body,[{'target_count':1,'foreign_count':0}])
 workA=roots['A']['ids']['work'];effectA=roots['A']['ids']['effect'];effectB=roots['B']['ids']['effect'];workC=roots['C']['ids']['work']
 def update_count(body):return "WITH changed AS ("+body+" RETURNING id) SELECT jsonb_build_object('changed',count(*)) FROM changed;"
 visible=lambda w:"SELECT jsonb_build_object('lease_valid',platform_private.worker_lease_valid("+quote(w)+',NULL,true));'
 add(CASE_NAMES[11],'A-process',visible(workA)+'\n'+update_count('UPDATE platform.runtime_work_item SET state=state WHERE id='+quote(workA)),[{'lease_valid':False},{'changed':0}],lease='A-stored-hash')
 add(CASE_NAMES[12],'A-process','UPDATE platform.runtime_work_item SET effect_receipt_id='+quote(effectB)+' WHERE id='+quote(workA)+'; ',[],kind='diagnostic')
 add(CASE_NAMES[13],'C-process','UPDATE platform.runtime_work_item SET effect_receipt_id='+quote(effectA)+' WHERE id='+quote(workC)+'; ',[],kind='diagnostic',lease='C1',root_label='C')
 # Reclaim's grant carries ONLY the old row generation token, as required by
 # row_allowed's exact current-xid predecessor convention.
 claim=deepcopy(grants['A-claim']);claim.update(template_id='A-reclaim',source_generation='1',allowed_fields=sorted(set(work_caps('A',1))));grants['A-reclaim']=claim
 reclaim="WITH changed AS (UPDATE platform.runtime_work_item SET state='leased',fence=fence+1,attempt_count=attempt_count+1,lease_token_hash=encode(sha256(decode(current_setting('wa.lease_secret'),'hex')),'hex'),lease_expires_at=clock_timestamp()+interval '300 seconds' WHERE id="+quote(workA)+" AND fence=1 AND state='leased' RETURNING id) SELECT jsonb_build_object('changed',count(*)) FROM changed;"
 add(CASE_NAMES[14],'A-reclaim',reclaim,[{'changed':1}],kind='concurrent',lease='A2',fence=1,delta=['platform.runtime_work_item'])
 files['old-holder-after-reclaim.sql']=operation_sql('old-holder-after-reclaim',visible(workA)+'\n'+update_count('UPDATE platform.runtime_work_item SET state=state WHERE id='+quote(workA)))
 new=deepcopy(grants['A-process']);new['template_id']='A-process2';new['source_generation']='2';new['allowed_fields']=[f.replace('RuntimeWorkItem/'+workA+'/revision/1','RuntimeWorkItem/'+workA+'/revision/2') for f in new['allowed_fields']];attempt2=uid('A/current-attempt2');new['allowed_fields']=sorted(set(new['allowed_fields']+cap('RuntimeAttempt',attempt2,'INSERT')+cap('RuntimeAttempt',attempt2,revision=2)));grants['A-process2']=new
 new_attempt=insert('platform.runtime_attempt',{'id':quote(attempt2),'work_item_id':quote(workA),'attempt_number':'2','fence':'2','worker_id':quote(SERVICE),'result':"'committed'",'reason_code':"'synthetic-retained-effect-recognized'",'started_at':"clock_timestamp()-interval '1 millisecond'",'finished_at':'clock_timestamp()'})
 body="SELECT jsonb_build_object('original_effect_matches',platform_private.worker_effect_matches("+quote(workA)+','+quote(effectA)+",true));\n"+new_attempt
 add(CASE_NAMES[15],'A-process2',body,[{'original_effect_matches':True}],lease='A2',fence=2,delta=['platform.runtime_attempt'])
 duplicate=next(line for line in text('A',original['enroll.sql'].decode()).splitlines() if line.startswith('INSERT INTO app.track_subscriptions ')).replace(quote(roots['A']['ids']['subscription']),quote(uid('A/duplicate-free')))
 duplicate_grant=deepcopy(new);duplicate_grant['template_id']='A-duplicate';duplicate_grant['allowed_fields']=sorted(set(duplicate_grant['allowed_fields']+cap('TrackSubscription',uid('A/duplicate-free'),'INSERT')));grants['A-duplicate']=duplicate_grant
 add(CASE_NAMES[16],'A-duplicate',duplicate,[],kind='diagnostic',lease='A2',fence=2)
 stale_generation=deepcopy(new);stale_generation.update(template_id='A-processing-old-generation',source_generation='1');grants['A-processing-old-generation']=stale_generation
 add(CASE_NAMES[17],'A-processing-old-generation',visible(workA)+'\n'+update_count('UPDATE platform.runtime_work_item SET state=state WHERE id='+quote(workA)),[{'lease_valid':False},{'changed':0}],lease='A2',fence=1)
 add(CASE_NAMES[18],'A-process2',visible(workA)+'\n'+update_count('UPDATE platform.runtime_work_item SET state=state WHERE id='+quote(workA)),[{'lease_valid':False},{'changed':0}],lease='A1',fence=2)
 complete=update_count("UPDATE platform.runtime_work_item SET state='completed' WHERE id="+quote(workA)+" AND state='leased' AND fence=2 AND effect_receipt_id="+quote(effectA))
 add(CASE_NAMES[19],'A-process2',complete+"\nSELECT 'WA_WR_TEMPORARILY_COMPLETED';\nUPDATE platform.runtime_work_item SET attempt_count=attempt_count+1 WHERE id="+quote(workA)+';',[{'changed':1},'WA_WR_TEMPORARILY_COMPLETED'],kind='diagnostic',lease='A2',fence=2)
 add(CASE_NAMES[20],'A-process2',"SELECT jsonb_build_object('original_effect_matches',platform_private.worker_effect_matches("+quote(workA)+','+quote(effectA)+",true));\n"+complete,[{'original_effect_matches':True},{'changed':1}],lease='A2',fence=2,delta=['platform.runtime_work_item'])
 need(tuple(c['name'] for c in cases)==CASE_NAMES,'EXACT21_NAMES')
 tables=sorted({m['object'] for m in models.values()}|{'platform_private.identity_service_authorization','platform_private.identity_service_receipt'});need(len(tables)==42,'FULL42_MODELS')
 fingerprints=[quote(t)+",(SELECT jsonb_build_object('count',count(*),'rows_sha256',encode(sha256(convert_to(COALESCE(jsonb_agg(to_jsonb(x) ORDER BY to_jsonb(x)::text COLLATE \"C\"),'[]'::jsonb)::text,'UTF8')),'hex')) FROM "+t+' x)' for t in tables];files['complete-state-observe.sql']='SELECT jsonb_build_object('+','.join(fingerprints)+');\n'
 files['A-clock.sql']="SELECT jsonb_build_object('near_expiry',lease_expires_at<=clock_timestamp()+interval '5 seconds','expired',lease_expires_at<=clock_timestamp(),'fence1',fence=1,'attempt1',attempt_count=1,'exact_effect',effect_receipt_id="+quote(effectA)+") FROM platform.runtime_work_item WHERE id="+quote(workA)+';\n'
 baseline={t:0 for t in tables};baseline.update({'app.users':3,'app.user_security_profiles':3,'app.track_plans':1,'app.track_entitlement_definitions':1,'app.track_plan_entitlements':1,'app.customer_profiles':3,'app.customer_profile_lifecycle_event':3,'platform.runtime_command_receipt':4,'platform.owner_mutation_evidence':6,'platform.runtime_outbox_message':6,'platform.runtime_work_item':3,'platform.runtime_attempt':1,'platform.runtime_effect_receipt':1,'platform.runtime_inbox_receipt':1,'app.track_subscriptions':1,'app.track_entitlement_grants':1,'app.track_base_selection':1,'app.track_subscription_events':1,'app.track_enrollment_receipt':1,'platform_private.identity_service_authorization':1,'platform_private.identity_service_receipt':1})
 after=deepcopy(baseline)
 for t in cases[0]['allowed_changed_tables']:
  if t!='platform.runtime_work_item':after[t]+=3 if t=='platform.owner_mutation_evidence' else 1
 final=deepcopy(after);final['platform.runtime_attempt']=3
 requested={('P0C-TABLE-'+model+'-ALLOW','positive.wa_worker.select'):'PASS' for model in READ_MODELS};requested.update({('P0C-TABLE-RuntimeCommandReceipt-ALLOW','positive.wa_worker.update'):'PASS',('P0C-TRACK-01','control.concurrent_fence'):'PASS',('P0C-TRACK-01','vector.LEASE-RECOVERY.positive'):'PASS'})
 requested.update({('P0C-TRACK-01',name):'PARTIAL' for name in ('control.lease_transitions','vector.LEASE-ATTACH.adversarial','vector.LEASE-RECOVERY.adversarial','control.preserve_valid_selection')})
 inventory=json.loads(blobs['context/reconciliation/local-f0-assertions.json']);ceilings=[]
 for source_case in inventory['cases']:
  for assertion in source_case['assertions']:
   identity=(source_case['id'],assertion['id'])
   if identity in requested:ceilings.append({'case_id':identity[0],'assertion_id':identity[1],'expected_assertion_sha256':sha(assertion['expected_assertion'].encode()),'complete_source_assertion_sha256':digest(assertion),'maximum_after_actual_evidence_and_review':requested[identity],'status':'NOT_RUN'})
 need(len(ceilings)==17 and sum(r['maximum_after_actual_evidence_and_review']=='PASS' for r in ceilings)==13,'EXACT_ASSERTION_CEILINGS')
 packet={'schema':'workinants.worker-recovery-fixtures.v1','status':'NOT_RUN','database_posture':'D','database_contacted':False,'sql_executed':False,'approved_plan_sha256':PLAN_SHA,'source_files_sha256':pins,'prepared_files_sha256':{},'roots':roots,'service_principal':SERVICE,'attempt2':attempt2,'grants':grants,'cases':cases,'fixture_tables':list(FIXTURE_TABLES),'models':models,'selected_control_ids':sorted({r['case_id'] for r in ceilings}),'assertion_ceilings':ceilings,'setup_expected_counts':baseline,'checkpoint_expected_counts':after,'final_expected_counts':final,'finite_caps':{'case_count':21,'jobs':3,'business_groups':2,'audit_attempts':3,'grant_instances_max':80,'clock_wait_seconds_max':150,'simultaneous_worker_sessions_max':2,'worker_loop':False},'worker_acl_rows':worker_acl,'golden_source_packet_sha256':sha(gold_raw),'scope_limits':['Only exact21 finite core, maximum13 exact PASS+4 compound PARTIAL links after actual evidence and independent review; no status promotion now.','First genuine leased effect/inbox checkpoint must pass before any expiry or recovery. No source/effect success fixtures or disabled business guards.','Only inherited five User/catalog owner_commit synthetic fixture bypasses; all native/physical/FK/RLS/ACL guards and32 worker rows remain exact.','No paid-selection, app reservation, owner result codec, future port, production worker loop, hosted change or full94/451 claim.']}
 packet['prepared_files_sha256']={name:sha(body.encode()) for name,body in files.items()};packet['source_only_packet_sha256']=digest({k:packet[k] for k in ('source_files_sha256','prepared_files_sha256')});files['fixtures.json']=json.dumps(packet,indent=2,ensure_ascii=False)+'\n';return files,packet

def main(argv=None):
 parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--prepare',action='store_true');args=parser.parse_args(argv)
 if not args.prepare:return 1
 files,_=build();OUT.mkdir(exist_ok=False)
 for name,body in files.items():
  with (OUT/name).open('x',encoding='utf8',newline='\n') as f:f.write(body)
 print(json.dumps({'status':'SOURCE_PREPARED_NOT_RUN','files':len(files)}));return 0
if __name__=='__main__':raise SystemExit(main())
