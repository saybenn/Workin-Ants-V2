"""Prepare a NEW finite existing-row read packet. No process or database API."""
import argparse
from copy import deepcopy
import json
from pathlib import Path
import re
import uuid
from owner_read_control_protocol import APPLICATION_SHA,SCOPE_SPECS,REVISION_MODELS,canonical,digest,sha,quote,operation_sql

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'review-output/owner-read-control-rehearsal'
NS=uuid.UUID('8b87c31c-f1ba-413c-a1b4-96a914d24777')
SELF='scripts/prepare-owner-read-control-rehearsal.py'
PROTOCOL='scripts/owner_read_control_protocol.py'
COORDINATOR='scripts/sql-review/run-owner-read-control-rehearsal.py'
APPLICATION='review-output/foundation-application.review.sql'
CTX='review-output/context-control-rehearsal/'
COPY_FILES=('trusted-identity-fixtures.sql','source-customer.sql','source-customer-observe.sql','identity-bootstrap.sql','schedule.sql','work-observe.sql','fixture-trigger-restore-observe.sql','grant-write-acl-observe.sql')
SOURCE_CONTEXTS=('context/context-map.md','context/shared/contracts/SH-049.md',
 'context/clusters/professional supply & readiness/professional-supply-readiness-architecture.md',
 'context/clusters/professional supply & readiness/Professional Eligibility Module/professional-eligbility-module-architecture.md',
 'context/clusters/professional supply & readiness/Professional Eligibility Module/professional-eligbility-module-implementation-plan.md',
 'context/clusters/Organization Hiring & Candidate Pipeline/organization-hiring-candidate-piepline-architecture.md',
 'context/clusters/Organization Hiring & Candidate Pipeline/Candidate Application & Resume Privacy Module/candidate-application-resume-privacy-module-architecture.md',
 'context/clusters/Organization Hiring & Candidate Pipeline/Candidate Application & Resume Privacy Module/candidate-application-resume-privacy-module-implementation-plan.md',
 'context/clusters/identity, authority, & consent/Identity & Access module/identity-access-module-architecture.md',
 'context/clusters/identity, authority, & consent/Consent & Disclosure Module/consent-disclosure-module-architecture.md',
 'context/clusters/identity, authority, & consent/Consent & Disclosure Module/consent-disclosure-implementation-plan.md',
 'context/clusters/identity, authority, & consent/Track Subscription & Entitlement Module/track-subscription-entitlement-module-architecture.md',
 'context/clusters/Privacy & Location Safety/Privacy Data Erasure Module/privacy-data-erasure-module-architecture.md')
INPUTS=(SELF,PROTOCOL,COORDINATOR,'scripts/check-owner-read-control-rehearsal.py','scripts/check-owner-read-control-coordinator.py',APPLICATION,
 'context/reconciliation/foundation-sql-draft-models.json','context/reconciliation/foundation-sql-draft-access.json','context/reconciliation/foundation-sql-scope-policy.json',
 'context/reconciliation/local-f0-assertions.json','context/reconciliation/database-candidate-tests.json',CTX+'fixtures.json',*[CTX+name for name in COPY_FILES],
 'scripts/sql-review/run-context-control-rehearsal.py','scripts/sql-review/run-worker-control-rehearsal.py','scripts/sql-review/run-first-rehearsal.py','scripts/sql-review/run-local-f0-migrate.py','scripts/sql-review/rehearsal-diagnostics.py','scripts/prepare-local-f0-history.py','scripts/sql-review/collect_native_catalog.sql',*SOURCE_CONTEXTS,
 *['context/shared/contracts/SH-'+n+'.md' for n in ('001','003','005','007','008','009','010','015','016','031','094','115','125')],
 *['contracts/shared/SH-'+n+'.v1.schema.json' for n in ('001','003','005','007','008','009','010','015','016','031','049','094','115','125')])

def uid(key):return str(uuid.uuid5(NS,key))
def sql(*lines):return '\n'.join(lines)+'\n'
def insert(table,values):return 'INSERT INTO '+table+' ('+','.join(values)+') VALUES ('+','.join(values.values())+');'
def text_hash(value):return "encode(sha256(convert_to("+quote(value)+",'UTF8')),'hex')"
def capabilities(acl,role,model,ids,verb='SELECT'):
 rows=[r for r in acl if (r['role'],r['model'],r['operation'])==(role,model,verb)]
 if len(rows)!=1:raise ValueError('exact ACL row missing')
 fields=rows[0]['fields'];tokens=[model+'/'+key+'/'+verb+'/'+f for key in ids for f in fields]
 if model in REVISION_MODELS:tokens += [model+'/'+key+'/revision/0' for key in ids]
 if verb=='UPDATE':tokens += [model+'/'+key+'/UPDATE/@row' for key in ids]
 return sorted(set(tokens))

def build(root=ROOT):
 root=Path(root);read=lambda p:(root/p).read_bytes();source={name:sha(read(name)) for name in INPUTS}
 if source[APPLICATION]!=APPLICATION_SHA:raise ValueError('canonical SQL changed')
 acl=json.loads(read('context/reconciliation/foundation-sql-draft-access.json'));models={m['model']:m for m in json.loads(read('context/reconciliation/foundation-sql-draft-models.json'))}
 scopes=json.loads(read('context/reconciliation/foundation-sql-scope-policy.json'));ctx=json.loads(read(CTX+'fixtures.json'));assertions=json.loads(read('context/reconciliation/local-f0-assertions.json'))['cases']
 if len([x for x in acl if x['role']=='wa_worker'])!=32:raise ValueError('worker ACL ceiling changed')
 for name,model,action,purpose in SCOPE_SPECS:
  expected={'owner':models[model]['owner'],'action':action,'purpose':purpose,'root_kind':model,'verbs':['SELECT']}
  if not any(all(row.get(k)==v for k,v in expected.items()) for row in scopes['domain_scopes']):raise ValueError('unregistered read scope')
 ids={model:[uid(model+'/0'),uid(model+'/1')] for model in dict.fromkeys(x[1] for x in SCOPE_SPECS)}
 user=ctx['source_customer']['ids']['user'];ids['User'][0]=user
 ids['UserSecurityProfile'][0]=str(uuid.uuid5(uuid.UUID('5f48469a-ec0d-4582-83c4-9794e5a620e4'),'user-security'))
 files={name:read(CTX+name).decode('utf8') for name in COPY_FILES};grants=deepcopy(ctx['grants']);cases=[]
 def template(key,model,action,purpose,fields,role='wa_app_runtime'):
  worker=role=='wa_worker';base=ctx['grants']['worker'] if worker else ctx['grants']['app']
  value={**deepcopy(base),'template_id':key,'owner_module_id':models[model]['owner'],'action':action,'purpose':purpose,'target_kind':model,'target_id':ids[model][0],'allowed_fields':sorted(set(fields)),'policy_version':'owner-read-fixture.v1'}
  if worker:value.update(owner_module_id='track_subscription_entitlement',action='assignDefaultFreeTrack.v1',purpose='default_free_enrollment',target_kind='RuntimeWorkItem',target_id=ctx['grants']['worker']['target_id'])
  grants[key]=value;return value
 def query(model):
  table=models[model]['object'];a,b=ids[model]
  parts=[quote('root')+',(SELECT count(*) FROM '+table+' WHERE id='+quote(a)+')',quote('foreign')+',(SELECT count(*) FROM '+table+' WHERE id='+quote(b)+')']
  if model in ('ConsentLog','ConsentPresentation'):
   children=['ConsentContentRevision']+(['ConsentPresentation'] if model=='ConsentLog' else [])
   for child in children:
    for i,label in [(0,'related'),(1,'foreign_related')]:parts.append(quote(child+'_'+label)+',(SELECT count(*) FROM '+models[child]['object']+' WHERE id='+quote(ids[child][i])+')')
  return 'SELECT jsonb_build_object('+','.join(parts)+');'
 def counts(model,root_count=1,foreign=0,children=1):
  value={'root':root_count,'foreign':foreign}
  if model in ('ConsentLog','ConsentPresentation'):
   for child in ['ConsentContentRevision']+(['ConsentPresentation'] if model=='ConsentLog' else []):value.update({child+'_related':children,child+'_foreign_related':0})
  return value
 def add(name,key,model,expected,body=None,kind='read'):
  file=name+'.sql';files[file]=operation_sql(name,query(model) if body is None else body)
  cases.append({'name':name,'kind':kind,'model':model,'grant':key,'sql':file,'expected':expected,'status':'NOT_RUN','actual_login':grants[key]['database_login_role']})
 for name,model,action,purpose in SCOPE_SPECS:
  fields=capabilities(acl,'wa_app_runtime',model,ids[model]);relations=[]
  if model in ('ConsentLog','ConsentPresentation'):
   for child,relation in [('ConsentContentRevision','contentRevision')]+([('ConsentPresentation','presentation')] if model=='ConsentLog' else []):
    fields+=capabilities(acl,'wa_app_runtime',child,ids[child]);relations.append(model+'/'+ids[model][0]+'/'+relation+'/'+ids[child][0])
   fields+=relations
  base=template(name,model,action,purpose,fields);add(name,name,model,counts(model))
  for variant,changes in [('wrong-purpose',{'purpose':'owner:unregisteredReadPurpose'}),('wrong-action',{'action':'unregisteredOwnerRead.v1'}),('wrong-root',{'target_id':ids[model][1]})]:
   key=name+'-'+variant;grants[key]={**deepcopy(base),**changes,'template_id':key};add(key,key,model,counts(model,0,1 if variant=='wrong-root' else 0,0))
  key=name+'-missing-field';drop=model+'/'+ids[model][0]+'/SELECT/'+next(x['fields'][0] for x in acl if x['model']==model and x['role']=='wa_app_runtime' and x['operation']=='SELECT')
  grants[key]={**deepcopy(base),'template_id':key,'allowed_fields':[f for f in base['allowed_fields'] if f!=drop]};add(key,key,model,counts(model,0,0,1 if relations else 0))
  if model in REVISION_MODELS:
   key=name+'-stale-revision';grants[key]={**deepcopy(base),'template_id':key,'source_generation':'1'};add(key,key,model,counts(model,0,0,0))
  if relations:
   for variant in ('missing-relation','wrong-root-relation'):
    key=name+'-'+variant;tokens=[f for f in base['allowed_fields'] if f not in relations]
    if variant=='wrong-root-relation':tokens += [f.replace('/'+ids[model][0]+'/', '/'+ids[model][1]+'/',1) for f in relations]
    grants[key]={**deepcopy(base),'template_id':key,'allowed_fields':sorted(tokens)};add(key,key,model,counts(model,1,0,0))
 for model,stem in [('TrackPlan','plan'),('TrackEntitlementDefinition','definition'),('TrackPlanEntitlement','benefit')]:
  name=stem+'-worker';fields=capabilities(acl,'wa_worker',model,[ids[model][0]])+['CustomerProfile/'+ctx['source_customer']['ids']['CustomerProfile']+'/revision/0','TrackPlan/'+ids['TrackPlan'][0]+'/revision/0','TrackPlan/'+ids['TrackPlan'][0]+'/version/owner-read.v1','TrackPlan/'+ids['TrackPlan'][0]+'/contentHash/'+sha(b'synthetic read plan0')]
  base=template(name,model,'','',fields,'wa_worker');base['source_generation']='1';add(name,name,model,counts(model))
  for variant in ('wrong-purpose','missing-field','missing-revision'):
   key=name+'-'+variant;value={**deepcopy(base),'template_id':key}
   if variant=='wrong-purpose':value['purpose']='owner:resolveEntitlement'
   else:
    suffix='/revision/0' if variant=='missing-revision' else '/SELECT/id';value['allowed_fields']=[x for x in value['allowed_fields'] if not x.endswith(suffix)]
   grants[key]=value;add(key,key,model,counts(model,0,0,0))
 # Otherwise matching native UPDATE ACL and exact fields cannot turn read scopes into writes.
 for stem,model,column,value in [('user-actor','User','display_name',quote('forbidden read-purpose update')),('security-actor','UserSecurityProfile','lock_reason',quote('forbidden read-purpose update')),('plan-app','TrackPlan','name',quote('forbidden read-purpose update'))]:
  name=stem+'-write-denied';base=grants[stem];grants[name]={**deepcopy(base),'template_id':name,'allowed_fields':sorted(set(base['allowed_fields']+capabilities(acl,'wa_app_runtime',model,[ids[model][0]],'UPDATE')))}
  body='WITH changed AS (UPDATE '+models[model]['object']+' SET '+column+'='+value+',revision=revision+1 WHERE id='+quote(ids[model][0])+' RETURNING id) SELECT jsonb_build_object(\'modified\',count(*)) FROM changed;';add(name,name,model,{'modified':0},body)
 # New fixture rows are current, coherent and intentionally not owner-operation evidence.
 seed_tables=['app.users','app.user_security_profiles']+[models[m]['object'] for m in ('TrackPlan','TrackEntitlementDefinition','TrackPlanEntitlement','PrivacyRequest','ConsentContentRevision')]
 seed=['BEGIN;']+['ALTER TABLE '+t+' DISABLE TRIGGER owner_commit;' for t in seed_tables]
 seed+=[insert('app.users',{'id':quote(ids['User'][1]),'updated_at':'clock_timestamp()'}),insert('app.user_security_profiles',{'id':quote(ids['UserSecurityProfile'][1]),'user_id':quote(ids['User'][1]),'updated_at':'clock_timestamp()'})]
 content_text='Synthetic owner-read consent text; no legal or publisher qualification.';rendered='Synthetic exact owner-read rendering; no actual UI rendered.'
 for i in range(2):
  seed += [insert(models['ProfessionalProfile']['object'],{'id':quote(ids['ProfessionalProfile'][i]),'user_id':quote(ids['User'][i]),'slug':quote('owner-read-'+str(i)),'updated_at':'clock_timestamp()'}),insert(models['CandidateProfile']['object'],{'id':quote(ids['CandidateProfile'][i]),'user_id':quote(ids['User'][i]),'updated_at':'clock_timestamp()'}),
   insert(models['TrackPlan']['object'],{'id':quote(ids['TrackPlan'][i]),'track':"'customer'",'key':quote('owner-read-'+str(i)),'name':quote('Synthetic read plan'),'status':"'active'",'billing_model':"'free'",'version':quote('owner-read.v1'),'content_hash':quote(sha(('synthetic read plan'+str(i)).encode())),'updated_at':'clock_timestamp()'}),
   insert(models['TrackEntitlementDefinition']['object'],{'id':quote(ids['TrackEntitlementDefinition'][i]),'key':quote('owner-read-'+str(i)),'label':quote('Synthetic read definition'),'value_type':"'boolean'",'track':"'customer'",'updated_at':'clock_timestamp()'}),
   insert(models['TrackPlanEntitlement']['object'],{'id':quote(ids['TrackPlanEntitlement'][i]),'plan_id':quote(ids['TrackPlan'][i]),'entitlement_id':quote(ids['TrackEntitlementDefinition'][i]),'value_type':"'boolean'",'boolean_value':'true','updated_at':'clock_timestamp()'}),
   insert(models['PrivacyRequest']['object'],{'id':quote(ids['PrivacyRequest'][i]),'user_id':quote(user),'type':"'access'",'status':"'submitted'",'updated_at':'clock_timestamp()'}),
   insert(models['ConsentContentRevision']['object'],{'id':quote(ids['ConsentContentRevision'][i]),'type':"'terms'",'version':quote('owner-read-'+str(i)),'locale':"'en'",'jurisdiction_scope':"'synthetic'",'content_text':quote(content_text),'content_hash':text_hash(content_text),'review_state':"'test_only'",'effective_from':"clock_timestamp()-interval '1 day'"})]
 seed += ['ALTER TABLE '+t+' ENABLE TRIGGER owner_commit;' for t in reversed(seed_tables)]+['COMMIT;'];files['existing-read-fixtures.sql']=sql(*seed)
 # These two source fixtures preserve physical/subject/proof guards and use actual app contexts.
 consent_tables=['app.consent_presentation','app.consent_logs'];files['consent-owner-fixture-open.sql']=sql('BEGIN;',*['ALTER TABLE '+t+' DISABLE TRIGGER owner_commit;' for t in consent_tables],'COMMIT;');files['consent-owner-fixture-close.sql']=sql('BEGIN;',*['ALTER TABLE '+t+' ENABLE TRIGGER owner_commit;' for t in reversed(consent_tables)],'COMMIT;')
 fixture_operations=[]
 for i in range(2):
  presentation={'id':quote(ids['ConsentPresentation'][i]),'content_revision_id':quote(ids['ConsentContentRevision'][i]),'user_id':quote(user),'action_owner':"'consent_disclosure'",'action':"'SH-007.v1'",'render_version':"'owner-read.v1'",'rendered_text':quote(rendered),'rendered_hash':text_hash(rendered),'context_owner':"'consent_disclosure'",'context_kind':"'ConsentLog'",'context_id':quote(ids['ConsentLog'][i])}
  proof={'id':quote(ids['ConsentLog'][i]),'user_id':quote(user),'type':"'terms'",'version':quote('owner-read-'+str(i)),'accepted_at':"clock_timestamp()+interval '1 second'",'acceptance_key':quote('owner-read-'+str(i)),'fingerprint':quote(sha(('owner-read-proof'+str(i)).encode())),'action_owner':"'consent_disclosure'",'action':"'SH-007.v1'",'context_owner':"'consent_disclosure'",'context_kind':"'ConsentLog'",'context_id':quote(ids['ConsentLog'][i]),'presentation_hash':text_hash(rendered),'content_revision_id':quote(ids['ConsentContentRevision'][i]),'presentation_id':quote(ids['ConsentPresentation'][i])}
  for model,action,purpose,values in [('ConsentPresentation','recordConsentPresentation.v1','consent.record_presentation',presentation),('ConsentLog','SH-007.v1','owner:recordConsentProof',proof)]:
   name='fixture-'+model.lower()+'-'+str(i);fields=capabilities(acl,'wa_app_runtime',model,[ids[model][i]],'INSERT')+capabilities(acl,'wa_app_runtime',model,[ids[model][i]])
   children=[('ConsentContentRevision','contentRevision')]+([('ConsentPresentation','presentation')] if model=='ConsentLog' else [])
   for child,relationship in children:fields += capabilities(acl,'wa_app_runtime',child,[ids[child][i]])+[model+'/'+ids[model][i]+'/'+relationship+'/'+ids[child][i]]
   base=template(name,model,action,purpose,fields);base['target_id']=ids[model][i]
   files[name+'.sql']=operation_sql(name,insert(models[model]['object'],values)+'\nSELECT jsonb_build_object(\'inserted_fixture\',1);');fixture_operations.append({'name':name,'kind':'read','model':model,'grant':name,'sql':name+'.sql','expected':{'inserted_fixture':1},'status':'NOT_RUN','actual_login':'wa_app_runtime'})
   if i==0:
    query_name='presentation-query-insert' if model=='ConsentPresentation' else None
    if query_name:
     values={**values,'id':quote(uid('denied-presentation'))};fields=capabilities(acl,'wa_app_runtime',model,[uid('denied-presentation')],'INSERT')+capabilities(acl,'wa_app_runtime','ConsentContentRevision',[ids['ConsentContentRevision'][0]])+[model+'/'+uid('denied-presentation')+'/contentRevision/'+ids['ConsentContentRevision'][0]]
     g=template(query_name,model,'SH-010.v1','owner:presentStandaloneConsent',fields);g['target_id']=uid('denied-presentation');add(query_name,query_name,model,None,insert(models[model]['object'],values),'diagnostic')
 # Query-only content root with coherent INSERT data still fails the exact RLS gate.
 name='content-query-insert';g=template(name,'ConsentContentRevision','SH-009.v1','owner:resolveActiveConsentVersion',capabilities(acl,'wa_app_runtime','ConsentContentRevision',[uid('denied-content')],'INSERT'));g['target_id']=uid('denied-content')
 body=insert(models['ConsentContentRevision']['object'],{'id':quote(uid('denied-content')),'type':"'terms'",'version':"'owner-read-denied'",'locale':"'en'",'jurisdiction_scope':"'synthetic'",'content_text':quote(content_text),'content_hash':text_hash(content_text),'review_state':"'test_only'",'effective_from':"clock_timestamp()-interval '1 day'"});add(name,name,'ConsentContentRevision',None,body,'diagnostic')
 name='privacy-completion-gate';g=template(name,'PrivacyRequest','SH-049.v1','owner:orchestrateWorkflowSteps',capabilities(acl,'wa_app_runtime','PrivacyRequest',[ids['PrivacyRequest'][0]])+capabilities(acl,'wa_app_runtime','PrivacyRequest',[ids['PrivacyRequest'][0]],'UPDATE'))
 body='UPDATE app.privacy_requests SET status=\'completed\',completed_at=clock_timestamp(),revision=revision+1 WHERE id='+quote(ids['PrivacyRequest'][0])+';';add(name,name,'PrivacyRequest',None,body,'diagnostic')
 work=ctx['grants']['worker']['target_id'];claim=deepcopy(ctx['grants']['worker']);claim['template_id']='worker-read-fixture-claim';claim['allowed_fields']=sorted(set(claim['allowed_fields']+['RuntimeWorkItem/'+work+'/UPDATE/'+field for field in ('@row','state','fence','attemptCount','leaseTokenHash','leaseExpiresAt')]))
 grants['worker-read-fixture-claim']=claim
 files['worker-read-fixture-claim.sql']=operation_sql('worker-read-fixture-claim',"WITH changed AS (UPDATE platform.runtime_work_item SET state='leased',fence=fence+1,attempt_count=attempt_count+1,lease_token_hash=encode(sha256(decode(current_setting('wa.lease_secret'),'hex')),'hex'),lease_expires_at=clock_timestamp()+interval '300 seconds' WHERE id="+quote(work)+") SELECT jsonb_build_object('claimed',count(*)) FROM changed;")
 # RETURNING is required for a data-modifying CTE to be read.
 files['worker-read-fixture-claim.sql']=files['worker-read-fixture-claim.sql'].replace(') SELECT jsonb_build_object(\'claimed\'', ' RETURNING id) SELECT jsonb_build_object(\'claimed\'')
 files['worker-lease-observe.sql']=sql("SELECT jsonb_build_object('work_count',count(*),'exact_live_lease',coalesce(bool_and(state='leased' AND fence=1 AND attempt_count=1 AND lease_expires_at>clock_timestamp() AND effect_receipt_id IS NULL AND lease_token_hash=encode(sha256(decode(current_setting('wa.lease_secret'),'hex')),'hex')),false),'attempts',(SELECT count(*) FROM platform.runtime_attempt),'effects',(SELECT count(*) FROM platform.runtime_effect_receipt),'enrollments',(SELECT count(*) FROM app.track_enrollment_receipt)) FROM platform.runtime_work_item WHERE id="+quote(work)+';')
 cases=[case for case in cases if case['actual_login']!='wa_worker']+[case for case in cases if case['actual_login']=='wa_worker']
 # Every application relation, including private Identity, is observed; grant row changes are independently checked.
 tables=sorted({m['object'] for m in models.values()}|{'platform_private.identity_service_authorization','platform_private.identity_service_receipt'})
 state_tables=[t for t in tables if t!='platform.database_action_grant']
 fingerprints=[quote(t)+",(SELECT jsonb_build_object('count',count(*),'rows_sha256',encode(sha256(convert_to(COALESCE(jsonb_agg(to_jsonb(x) ORDER BY to_jsonb(x)::text COLLATE \"C\"),'[]'::jsonb)::text,'UTF8')),'hex')) FROM "+t+' x)' for t in state_tables]
 files['complete-state-observe.sql']=sql('SELECT jsonb_build_object('+','.join(fingerprints)+');')
 files['grant-count-observe.sql']="SELECT count(*) FROM platform.database_action_grant;\n"
 expected_counts={t:0 for t in state_tables};expected_counts.update({'app.users':2,'app.user_security_profiles':2,'app.customer_profiles':1,'app.customer_profile_lifecycle_event':1,'platform.runtime_command_receipt':1,'platform.owner_mutation_evidence':1,'platform.runtime_outbox_message':2,'platform.runtime_work_item':1,'platform_private.identity_service_authorization':1,'platform_private.identity_service_receipt':1})
 expected_counts.update({models[m]['object']:2 for m in ids if m not in ('User','UserSecurityProfile')})
 selected=sorted({'P0C-TABLE-'+m+'-ALLOW' for m in ids}|{'P0C-CTX-01'})
 packet={'schema':'workinants.owner-read-fixtures.v1','status':'NOT_RUN','database_posture':'D','database_contacted':False,'sql_executed':False,'selected_control_ids':selected,'source_files_sha256':source,'prepared_files_sha256':{},'ids':ids,'models':{m:models[m] for m in ids},'grants':grants,'cases':cases,'fixture_operations':fixture_operations,'finite_caps':{'case_count':len(cases),'grant_instances_max':len(cases)+7},'expected_counts':expected_counts,'worker_acl_ceiling_rows':[x for x in acl if x['role']=='wa_worker'],'copy_source_customer':ctx['source_customer'],'expected_trigger_contract':ctx['fixture_trigger_contract'],'setup_observers':ctx['mandatory_after_case_observers'],'source_customer_grant':ctx['grants']['source_customer'],'schedule_grant':ctx['grants']['schedule'],'assertion_source':{row['id']:row for row in assertions if row['id'] in selected},'fixture_bypasses':{'existing_read_owner_commit_only':seed_tables,'restricted_consent_owner_commit_only':consent_tables,'physical_subject_consent_guards_retained':True,'no_function_replacement':True},'scope_limits':['Read fixtures establish existing rows, not owner creation/publisher/legal policy or application API readiness.','Only exact finite registered nonmutating purposes; no general SH003 or invented no-result codec.','Worker catalog rights are issuer-authorized finite fields under registered default-Free work scope, not evidence of a lease/enrollment loop or hidden work-to-catalog FK check.','Consent related reads require exact capability edges; no claim that SELECT itself validates physical FK relationships when an issuer explicitly authorizes a foreign edge.','Consent positive proof/publisher/rendering vectors and all unavailable write/owner paths remain NOT_RUN.','Privacy completion denial qualifies only the named0A000 gate; blocked positive and full Privacy/restore paths remain NOT_RUN.','All selected cases/assertions remain NOT_RUN until independent actual evidence mapping.'],'packet_digest_recipe':'SHA256 UTF8 canonical JSON of source_files_sha256 and prepared_files_sha256; fixtures.json excluded.'}
 packet['prepared_files_sha256']={name:sha(value.encode()) for name,value in files.items()};packet['source_only_packet_sha256']=digest({k:packet[k] for k in ('source_files_sha256','prepared_files_sha256')})
 files['fixtures.json']=json.dumps(packet,indent=2,ensure_ascii=False)+'\n';return files,packet

def main(argv=None):
 parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--prepare',action='store_true');args=parser.parse_args(argv)
 if not args.prepare:return 1
 files,_=build();OUT.mkdir(exist_ok=False)
 for name,text in files.items():(OUT/name).write_text(text,encoding='utf8',newline='\n')
 print(json.dumps({'status':'SOURCE_PREPARED_NOT_RUN','files':len(files)}));return 0

if __name__=='__main__':raise SystemExit(main())
