"""Prepare six finite SH003 read criteria and 71 source-only protocols."""
import argparse
from copy import deepcopy
import json
from pathlib import Path
import uuid
from scoped_read_companion_protocol import APPLICATION_SHA,PLAN_SHA,SPECS,REVISION_MODELS,FIXTURE_TABLES,canonical,digest,sha,quote,operation_sql,need

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'review-output/scoped-read-companion-rehearsal'
NS=uuid.UUID('dc9c9db4-8899-4a26-a262-81cd0e3e46ce')
APPLICATION='review-output/foundation-application.review.sql'
HELPERS=('scripts/sql-review/run-context-control-rehearsal.py','scripts/sql-review/run-first-rehearsal.py','scripts/sql-review/run-local-f0-migrate.py','scripts/sql-review/rehearsal-diagnostics.py','scripts/prepare-local-f0-history.py')
INPUTS=('scripts/prepare-scoped-read-companion-rehearsal.py','scripts/scoped_read_companion_protocol.py','scripts/sql-review/run-scoped-read-companion-rehearsal.py','scripts/check-scoped-read-companion-rehearsal.py','scripts/check-scoped-read-companion-coordinator.py',APPLICATION,'review-output/foundation-bootstrap.review.sql','context/reconciliation/local-f0-assertions.json','context/reconciliation/foundation-sql-draft-models.json','context/reconciliation/foundation-sql-draft-access.json','context/reconciliation/foundation-sql-scope-policy.json','context/context-map.md','context/shared/contracts/SH-003.md','contracts/shared/SH-003.v1.schema.json','contracts/shared/types.v1.schema.json','context/clusters/identity, authority, & consent/Identity & Access module/identity-access-module-architecture.md','context/clusters/Moderation holds Audits and Ops/Audit Event Ledger Module/audit-event-ledger-module-architecture.md','scripts/sql-review/collect_native_catalog.sql',*HELPERS)
USERS=('8a9a4b27-ce71-52f9-aa47-c45f09f71952','3950fc46-5cfd-5911-a245-ff5e90e915d3')
SECURITY=('24bb1d93-a33d-5de1-aee2-0a6844186ce0','dbebcfec-f4e8-576a-82f8-122e5bcf3ded')

def uid(key): return str(uuid.uuid5(NS,key))
def insert(table,values): return 'INSERT INTO '+table+' ('+','.join(values)+') VALUES ('+','.join(values.values())+');'
def capabilities(acl,model,keys):
    rows=[r for r in acl if (r['role'],r['model'],r['operation'])==('wa_app_runtime',model,'SELECT')]
    need(len(rows)==1,'EXACT_SELECT_ACL'); fields=rows[0]['fields']
    return sorted([model+'/'+key+'/SELECT/'+field for key in keys for field in fields]+([model+'/'+key+'/revision/0' for key in keys] if model in REVISION_MODELS else []))

def build(root=ROOT):
    root=Path(root); blobs={p:(root/p).read_bytes() for p in INPUTS}; source={p:sha(raw) for p,raw in blobs.items()}
    need(source[APPLICATION]==APPLICATION_SHA,'CANONICAL_SQL_DRIFT')
    models={m['model']:m for m in json.loads(blobs['context/reconciliation/foundation-sql-draft-models.json'])}
    acl=json.loads(blobs['context/reconciliation/foundation-sql-draft-access.json']); scopes=json.loads(blobs['context/reconciliation/foundation-sql-scope-policy.json'])['domain_scopes']
    inventory=json.loads(blobs['context/reconciliation/local-f0-assertions.json'])['cases']
    need(len([x for x in acl if x['role']=='wa_worker'])==32,'WORKER_ACL_CEILING')
    ids={model:[uid(model+'/'+str(i)) for i in range(2)] for model,_ in SPECS}; ids.update(User=list(USERS),UserSecurityProfile=list(SECURITY));ids['UserRole']=[u+':user' for u in USERS]
    files={}; grants={}; cases=[]; selected=[]
    def predicate(model,key):
        return "user_id::text||':'||role::text="+quote(key) if model=='UserRole' else 'id='+quote(key)
    def query(model,cross):
        parts=[]
        for m,prefix in [(model,'')]+([('User','User_'),('UserSecurityProfile','UserSecurityProfile_')] if cross else []):
            for i,label in enumerate(('root','foreign')): parts.append(quote(prefix+label)+',(SELECT count(*) FROM '+models[m]['object']+' WHERE '+predicate(m,ids[m][i])+')')
        return 'SELECT jsonb_build_object('+','.join(parts)+');'
    for model,index in SPECS:
        registration={'owner':models[model]['owner'],'action':'SH-003.v1','purpose':'owner:queryOwnerFacts','root_kind':model,'verbs':['SELECT']}
        need(all(scopes[index].get(k)==v for k,v in registration.items()),'EXACT_REGISTERED_SCOPE_INDEX')
        case_id='P0C-TABLE-'+model+'-ALLOW'; matched=[a for c in inventory if c['id']==case_id for a in c['assertions'] if a['id']=='positive.wa_app_runtime.select'];need(len(matched)==1,'EXACT_SELECTED_READ_ASSERTION');selected.append({'case_id':case_id,'assertion_id':matched[0]['id'],'expected_assertion_sha256':sha(matched[0]['expected_assertion'].encode()),'complete_assertion_sha256':digest(matched[0]),'status':'NOT_RUN'})
        fields=capabilities(acl,model,ids[model]); variants=['positive-root','wrong-purpose','wrong-action','wrong-owner','other-existing-root','missing-primary-field','missing-createdAt','missing-mutationTransactionId','cross-model-complete-caps','principal-generation-mismatch','principalB-current-control']
        if model in ('UserRole','AuthProviderAccount'): variants+=['missing-revision-capability','wrong-source-generation']
        if model=='UserRole': variants+=['wrong-composite-target']
        for variant in variants:
            name=model.lower()+'-'+variant; grant={'template_id':name,'database_login_role':'wa_app_runtime','issuer_service':'wa_context_issuer','owner_module_id':registration['owner'],'action':'SH-003.v1','purpose':'owner:queryOwnerFacts','target_kind':model,'target_id':ids[model][0],'principal_user_id':USERS[0],'service_principal':None,'source_generation':'0','security_generation':'0','allowed_fields':deepcopy(fields),'policy_version':'scoped-read-companion.v1','status':'NOT_RUN'}
            expected={'root':1,'foreign':0}; kind='read'
            if variant=='wrong-purpose': grant['purpose']='owner:unregisteredReadPurpose'; expected={'root':0,'foreign':0}
            if variant=='wrong-action': grant['action']='unregisteredScopedRead.v1'; expected={'root':0,'foreign':0}
            if variant=='wrong-owner': grant['owner_module_id']='audit_event_ledger' if registration['owner']=='identity_access' else 'identity_access';expected={'root':0,'foreign':0}
            if variant=='other-existing-root': grant['target_id']=ids[model][1];expected={'root':0,'foreign':1}
            if variant.startswith('missing-'):
                field={'missing-primary-field':'userId' if model=='UserRole' else 'id','missing-createdAt':'createdAt','missing-mutationTransactionId':'mutationTransactionId'}.get(variant)
                drop=model+'/'+ids[model][0]+('/revision/0' if variant=='missing-revision-capability' else '/SELECT/'+field)
                need(drop in grant['allowed_fields'],'EXACT_DROPPED_CAPABILITY');grant['allowed_fields'].remove(drop);expected={'root':0,'foreign':0}
            if variant=='wrong-source-generation':grant['source_generation']='1';expected={'root':0,'foreign':0}
            if variant=='wrong-composite-target':grant['target_id']=USERS[0];expected={'root':0,'foreign':0}
            cross=variant=='cross-model-complete-caps'
            if cross:
                grant['allowed_fields']=sorted(fields+capabilities(acl,'User',USERS)+capabilities(acl,'UserSecurityProfile',SECURITY));expected.update(User_root=0,User_foreign=0,UserSecurityProfile_root=0,UserSecurityProfile_foreign=0)
            if variant.startswith('principal'):
                grant['principal_user_id']=USERS[1]
                if variant=='principalB-current-control':grant['security_generation']='1'
                else:kind='binder-denial';expected=None
            grants[name]=grant;file=name+'.sql';files[file]=operation_sql(name,query(model,cross))
            cases.append({'name':name,'model':model,'variant':variant,'kind':kind,'case_id':case_id,'assertion_id':'positive.wa_app_runtime.select','actual_login':'wa_app_runtime','grant':name,'sql':file,'expected':expected,'status':'NOT_RUN'})
    seeds=[]
    for i,user in enumerate(USERS): seeds.append(insert('app.users',{'id':quote(user),'updated_at':'clock_timestamp()','revision':'0','privacy_generation':'0'}))
    for i,user in enumerate(USERS): seeds.append(insert('app.user_security_profiles',{'id':quote(SECURITY[i]),'user_id':quote(user),'updated_at':'clock_timestamp()','revision':'0','security_generation':str(i)}))
    for i,user in enumerate(USERS):
        seeds += [insert('app.age_gate_attempts',{'id':quote(ids['AgeGateAttempt'][i]),'user_id':quote(user),'result':"'allowed'"}),insert('app.age_gate_blocks',{'id':quote(ids['AgeGateBlock'][i]),'reason':"'synthetic-owner-read'",'blocked_until':"clock_timestamp()+interval '1 day'"}),insert('app.access_audit_logs',{'id':quote(ids['AccessAuditLog'][i]),'actor_user_id':quote(user),'target_type':"'synthetic-owner-read'",'target_id':quote(uid('audit-target/'+str(i))),'action':"'file_read'",'sensitivity':"'normal'",'access_decision':"'allowed'"}),insert('app.user_roles',{'user_id':quote(user),'role':"'user'",'revision':'0'}),insert('app.audit_events',{'id':quote(ids['AuditEvent'][i]),'actor_user_id':quote(user),'entity_type':"'synthetic-owner-read'",'entity_id':quote(uid('audit-entity/'+str(i))),'action':"'synthetic_read'",'metadata':'NULL'}),insert('app.auth_provider_accounts',{'id':quote(ids['AuthProviderAccount'][i]),'user_id':quote(user),'security_profile_id':quote(SECURITY[i]),'provider_type':"'other'",'status':"'active'",'updated_at':'clock_timestamp()','revision':'0'})]
    restore=['ALTER TABLE '+t+' ENABLE TRIGGER owner_commit;' for t in reversed(FIXTURE_TABLES)]
    files['existing-scoped-read-fixtures.sql']='\n'.join(['BEGIN;']+['ALTER TABLE '+t+' DISABLE TRIGGER owner_commit;' for t in FIXTURE_TABLES]+seeds+['SET CONSTRAINTS ALL IMMEDIATE;']+restore+['COMMIT;'])+'\n'
    files['exact-owner-trigger-restore.sql']='\n'.join(['BEGIN;']+restore+['COMMIT;'])+'\n'
    table_array='ARRAY['+','.join(quote(t) for t in FIXTURE_TABLES)+']::text[]'
    files['exact-trigger-observe.sql']="SELECT jsonb_build_object('owner_count',count(*) FILTER (WHERE t.tgname='owner_commit'),'physical_count',count(*) FILTER (WHERE t.tgname='physical_guard'),'all_enabled',coalesce(bool_and(t.tgenabled='O'),false)) FROM pg_trigger t JOIN pg_class c ON c.oid=t.tgrelid JOIN pg_namespace n ON n.oid=c.relnamespace WHERE n.nspname::text||'.'||c.relname::text=ANY("+table_array+") AND t.tgname IN ('owner_commit','physical_guard') AND NOT t.tgisinternal;\n"
    tables=sorted({m['object'] for m in models.values()}|{'platform_private.identity_service_authorization','platform_private.identity_service_receipt'})
    need(len(tables)==42,'FULL42_SOURCE_TABLES')
    observations=[quote(t)+",(SELECT jsonb_build_object('count',count(*),'rows_sha256',encode(sha256(convert_to(COALESCE(jsonb_agg(to_jsonb(x) ORDER BY to_jsonb(x)::text COLLATE \"C\"),'[]'::jsonb)::text,'UTF8')),'hex')) FROM "+t+' x)' for t in tables]
    files['complete-state-observe.sql']='SELECT jsonb_build_object('+','.join(observations)+');\n'
    files['fixture-coherence-observe.sql']="SELECT jsonb_build_object('users',count(*),'coherent',coalesce(bool_and(u.revision=0 AND u.privacy_generation=0 AND s.revision=0 AND s.security_generation=CASE WHEN u.id="+quote(USERS[0])+" THEN 0 ELSE 1 END AND s.user_id=u.id AND u.mutation_transaction_id<>'' AND s.mutation_transaction_id<>''),false)) FROM app.users u JOIN app.user_security_profiles s ON s.user_id=u.id WHERE u.id=ANY(ARRAY["+','.join(quote(u) for u in USERS)+']::uuid[]);\n'
    expected_counts={t:2 if t in FIXTURE_TABLES else 0 for t in tables}
    limits=['Six exact local SQL SELECT criteria only; all runtime NOT_RUN until actual evidence and independent mapping.','Two rows per fixture table are privileged synthetic facts, never owner creation/API/upstream Identity authentication evidence.','Scope and principal generation are distinct: principalB current generation may legitimately read rootA; no row ownership or invented child-edge denial.','Only exact eight owner_commit bypass; physical/native/FK/RLS/ACL guards and 32 worker ACL rows unchanged.','No worker behavior, Track enrollment, command receipts, outbox, effects, service epoch, hosted changes or full-case promotion.']
    packet={'schema':'workinants.scoped-read-companion-fixtures.v1','plan_sha256':PLAN_SHA,'status':'NOT_RUN','database_posture':'D','database_contacted':False,'sql_executed':False,'selected_control_ids':[r['case_id'] for r in selected],'selected_assertions':selected,'source_files_sha256':source,'prepared_files_sha256':{},'ids':ids,'models':{m:models[m] for m in ids},'grants':grants,'cases':cases,'finite_caps':{'case_count':71,'grant_instances_max':71},'expected_counts':expected_counts,'worker_acl_ceiling_rows':[r for r in acl if r['role']=='wa_worker'],'fixture_tables':list(FIXTURE_TABLES),'scope_limits':limits,'packet_digest_recipe':'SHA256 UTF8 canonical JSON of source_files_sha256 and prepared_files_sha256; fixtures.json excluded.'}
    need(len(cases)==71 and len(grants)==71 and len(seeds)==16,'CLOSED_FINITE_SCOPE')
    packet['prepared_files_sha256']={name:sha(text.encode()) for name,text in files.items()};packet['source_only_packet_sha256']=digest({k:packet[k] for k in ('source_files_sha256','prepared_files_sha256')})
    files['fixtures.json']=json.dumps(packet,indent=2,ensure_ascii=False)+'\n';return files,packet

def main(argv=None):
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--prepare',action='store_true');args=parser.parse_args(argv)
    if not args.prepare:return 1
    files,_=build();OUT.mkdir(exist_ok=False)
    for name,text in files.items():
        with (OUT/name).open('x',encoding='utf8',newline='\n') as f:f.write(text)
    print(json.dumps({'status':'SOURCE_PREPARED_NOT_RUN','files':len(files)}));return 0
if __name__=='__main__':raise SystemExit(main())
