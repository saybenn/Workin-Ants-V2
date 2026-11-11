"""Prepare exact synthetic SQL/capabilities only. No DB, Docker or network calls."""
from pathlib import Path
import hashlib
import json
from contract_schema import Registry

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'review-output/first-rehearsal'
OWNER='customer_buyer_profile'
def quote(value):return "'"+str(value).replace("'","''")+"'"
def json_sql(value):return quote(json.dumps(value,separators=(',',':')))+'::jsonb'
def digest(value):return "encode(sha256(convert_to("+json_sql(value)+"::text,'UTF8')),'hex')"
def uid(prefix,number):return f'{prefix}0000000-0000-4000-8000-{number:012d}'
def insert(table,values):return 'INSERT INTO '+table+' ('+','.join('"'+k+'"' for k in values)+') VALUES ('+','.join(values.values())+');'

def prepare():
    OUT.mkdir(parents=True,exist_ok=True)
    acl=json.loads((ROOT/'context/reconciliation/foundation-sql-draft-access.json').read_text())
    registry=Registry(ROOT)
    types=registry.documents['urn:workin-ants:types:v1']
    free_schema=json.loads((ROOT/'contracts/database-review/foundation-payloads.v1.schema.json').read_text())
    registry.documents[free_schema['$id']]=free_schema
    scenarios=[]
    for number,name,user,principal,omit in [(1,'positive',1,1,False),(2,'wrong-person',1,2,False),(3,'missing-outbox',2,2,True)]:
        ids={model:uid(prefix,number) for model,prefix in [('CustomerProfile','2'),('RuntimeCommandReceipt','3'),('CustomerProfileLifecycleEvent','4'),('OwnerMutationEvidence','5'),('event','6'),('command','7')]}
        c,q,h,e,o0,o1=[ids[k] for k in ['CustomerProfile','RuntimeCommandReceipt','CustomerProfileLifecycleEvent','OwnerMutationEvidence','event','command']]
        u=uid('1',user);semantic='first-customer-'+name
        fingerprint=hashlib.sha256(('synthetic-intent:'+semantic).encode()).hexdigest()
        event={'eventName':'customer.lifecycle_changed.v1','customerProfileId':c,'userId':u,'lifecycleRevision':'0','safeState':'active'}
        free={'sourceOwner':OWNER,'userId':u,'track':'customer','customerProfileId':c,'sourceCreationRevision':'0','sourceCreationReceipt':q,'semanticKey':OWNER+'/'+c+'/default-free-enrollment/v1'}
        evidence={'schema':'database-owner-evidence.v1','owner':OWNER,'model':'CustomerProfile','primaryKey':{'id':c},'prior':None,'committed':{'id':c,'userId':u,'status':'active','revision':'0','privacyGeneration':'0'},'decisionRef':'first-customer-v1'}
        response={'contract':'SH-004.v1','requestId':'first-'+name,'status':'ok','value':{'customerProfileId':c,'userId':u,'lifecycle':'active','sourceToken':'0','receipt':{'owner':OWNER,'id':q,'semanticKey':semantic,'fingerprint':fingerprint,'sourceToken':'0','recordedAt':'2026-11-10T00:00:00Z'}}}
        errors=registry.check('SH-004','response',response)+registry.errors(event,types['$defs']['EventPayload_customer_lifecycle_changed_v1'],types)+registry.errors(free,free_schema['$defs']['assignDefaultFreeTrackCustomerCommand'],free_schema)
        if errors:raise ValueError(name+': invalid exact fixture JSON '+str(errors))
        statements=[insert('platform.runtime_command_receipt',{'id':quote(q),'owner_module_id':quote(OWNER),'operation':quote('SH-004.v1'),'subject_scope':quote('CustomerProfile:'+c),'semantic_key':quote(semantic),'fingerprint':quote(fingerprint),'state':quote('committed'),'source_revision':'0','result_schema_id':quote('SH-004.v1#/$defs/response'),'result_schema_version':quote('1'),'result_digest':digest(response),'result_body':json_sql(response)}),
            insert('app.customer_profiles',{'id':quote(c),'user_id':quote(u),'status':quote('active'),'revision':'0','privacy_generation':'0'}),
            insert('app.customer_profile_lifecycle_event',{'id':quote(h),'customer_profile_id':quote(c),'command_receipt_id':quote(q),'source_revision':'0','from_status':'NULL','to_status':quote('active'),'name':quote('customer.lifecycle_changed.v1'),'actor_user_id':quote(u)}),
            insert('platform.owner_mutation_evidence',{'id':quote(e),'command_receipt_id':quote(q),'owner_module_id':quote(OWNER),'aggregate_kind':quote('CustomerProfile'),'aggregate_id':quote(c),'previous_revision':'NULL','committed_revision':'0','action':quote('SH-004.v1'),'decision_ref':quote('first-customer-v1'),'evidence_schema_id':quote('urn:workinants:database-review:owner-evidence:v1#/$defs/CustomerProfile'),'evidence_schema_version':quote('1'),'evidence_digest':digest(evidence),'evidence_body':json_sql(evidence)})]
        for ordinal,body,kind,message,schema,oid in [(0,event,'event','customer.lifecycle_changed.v1','urn:workin-ants:types:v1#/$defs/EventPayload_customer_lifecycle_changed_v1',o0),(1,free,'command','assignDefaultFreeTrack.v1','urn:workinants:database-review:foundation-payloads:v1#/$defs/assignDefaultFreeTrackCustomerCommand',o1)]:
            if omit and ordinal==1:continue
            statements.append(insert('platform.runtime_outbox_message',{'id':quote(oid),'command_receipt_id':quote(q),'kind':quote(kind),'producer_owner':quote(OWNER),'aggregate_kind':quote('CustomerProfile'),'aggregate_id':quote(c),'source_revision':'0','source_generation':'0','ordinal':str(ordinal),'name':quote(message),'schema_version':quote('1'),'payload_schema_id':quote(schema),'payload_hash':digest(body),'payload':json_sql(body),'correlation_id':quote('first-'+name),'causation_id':quote(q),'occurred_at':'clock_timestamp()','effective_at':'clock_timestamp()'}))
        staged=[]
        for index,statement in enumerate(statements):
            staged.append(statement)
            if index==0:staged.append("SELECT 'WA_COMMAND_INSERTED';")
            if index==1:staged.append("SELECT 'WA_CUSTOMER_INSERTED';")
        staged.append("SELECT 'WA_READY_TO_COMMIT';")
        file=name+'.sql';(OUT/file).write_text('-- PROPOSED ONLY. Send inside the same already-bound runtime transaction.\n'+'\n'.join(staged)+'\nCOMMIT;\n',encoding='utf8',newline='\n')
        fields=[]
        for model,source_ids in {**{m:[ids[m]] for m in ['CustomerProfile','RuntimeCommandReceipt','CustomerProfileLifecycleEvent','OwnerMutationEvidence']},'RuntimeOutboxMessage':[o0,o1]}.items():
            for row in acl:
                if row['model']==model and row['role']=='wa_app_runtime' and row['operation'] in ['SELECT','INSERT']:
                    for source_id in source_ids:fields.extend(model+'/'+source_id+'/'+row['operation']+'/'+f for f in row['fields'])
        fields.append('CustomerProfile/'+c+'/revision/0')
        observe="SELECT jsonb_build_object('command',(SELECT count(*) FROM platform.runtime_command_receipt WHERE id="+quote(q)+"),'customer',(SELECT count(*) FROM app.customer_profiles WHERE id="+quote(c)+"),'history',(SELECT count(*) FROM app.customer_profile_lifecycle_event WHERE id="+quote(h)+"),'evidence',(SELECT count(*) FROM platform.owner_mutation_evidence WHERE id="+quote(e)+"),'outbox',(SELECT count(*) FROM platform.runtime_outbox_message WHERE command_receipt_id="+quote(q)+"));\n"
        coherent=f'''EXISTS(SELECT 1 FROM platform.runtime_command_receipt q
 JOIN app.customer_profiles c ON c.id={quote(c)} AND c.user_id={quote(u)} AND c.status='active' AND c.revision=0 AND c.privacy_generation=0
 JOIN app.customer_profile_lifecycle_event h ON h.id={quote(h)} AND h.customer_profile_id=c.id AND h.command_receipt_id=q.id AND h.source_revision=0 AND h.actor_user_id=c.user_id AND h.from_status IS NULL AND h.to_status='active'
 JOIN platform.owner_mutation_evidence e ON e.id={quote(e)} AND e.command_receipt_id=q.id AND e.aggregate_kind='CustomerProfile' AND e.aggregate_id=c.id::text AND e.committed_revision=0 AND e.previous_revision IS NULL AND e.owner_module_id=q.owner_module_id
 WHERE q.id={quote(q)} AND q.owner_module_id='customer_buyer_profile' AND q.operation='SH-004.v1' AND q.subject_scope='CustomerProfile:'||c.id::text AND q.state='committed' AND q.source_revision=0
 AND q.result_digest=encode(sha256(convert_to(q.result_body::text,'UTF8')),'hex') AND e.evidence_digest=encode(sha256(convert_to(e.evidence_body::text,'UTF8')),'hex')
 AND q.mutation_transaction_id=c.mutation_transaction_id AND h.mutation_transaction_id=c.mutation_transaction_id AND e.mutation_transaction_id=c.mutation_transaction_id
 AND (SELECT count(*) FROM platform.runtime_outbox_message o WHERE o.command_receipt_id=q.id AND o.aggregate_kind='CustomerProfile' AND o.aggregate_id=c.id::text AND o.source_revision=0 AND o.source_generation=0
  AND o.mutation_transaction_id=c.mutation_transaction_id AND o.payload->>'userId'=c.user_id::text AND o.payload_hash=encode(sha256(convert_to(o.payload::text,'UTF8')),'hex')
  AND ((o.ordinal=0 AND o.kind='event' AND o.name='customer.lifecycle_changed.v1') OR (o.ordinal=1 AND o.kind='command' AND o.name='assignDefaultFreeTrack.v1')))=2)'''
        observe=observe.removesuffix(');\n')+",'coherent',"+coherent+",'track_enrollments',(SELECT count(*) FROM app.track_enrollment_receipt WHERE profile_id="+quote(c)+"));\n"
        (OUT/(name+'-observe.sql')).write_text(observe,encoding='utf8',newline='\n')
        counts={'command':1,'customer':1,'history':1,'evidence':1,'outbox':2} if name=='positive' else dict.fromkeys(['command','customer','history','evidence','outbox'],0)
        counts.update(coherent=name=='positive',track_enrollments=0)
        scenarios.append({'name':name,'principal_user_id':uid('1',principal),'source_user_id':u,'ids':ids,'grant_id':uid('8',number),'allowed_fields':sorted(set(fields)),'transaction_sql':file,'observer_sql':name+'-observe.sql','fixture_values':{'response':response,'event':event,'free_command':free,'evidence':evidence},'expected_commit':name=='positive','expected_sqlstate':None if name=='positive' else '42501' if name=='wrong-person' else 'P0001','expected_diagnostic':'NONE' if name=='positive' else 'CUSTOMER_PRINCIPAL_GUARD' if name=='wrong-person' else 'CUSTOMER_DEFAULT_FREE_GUARD','expected_counts':counts,'status':'NOT_RUN'})
    seed=['-- Privileged synthetic fixture preparation only; never owner-runtime proof.','BEGIN;','ALTER TABLE app.users DISABLE TRIGGER USER;','ALTER TABLE app.user_security_profiles DISABLE TRIGGER USER;']
    for n in [1,2]:
        seed.append(insert('app.users',{'id':quote(uid('1',n)),'is_public':'false','revision':'0','privacy_generation':'0','created_at':'clock_timestamp()','updated_at':'clock_timestamp()','mutation_transaction_id':'pg_current_xact_id()::text'}))
        seed.append(insert('app.user_security_profiles',{'id':quote(uid('9',n)),'user_id':quote(uid('1',n)),'revision':'0','security_generation':'0','created_at':'clock_timestamp()','updated_at':'clock_timestamp()','mutation_transaction_id':'pg_current_xact_id()::text'}))
    seed+=['ALTER TABLE app.user_security_profiles ENABLE TRIGGER USER;','ALTER TABLE app.users ENABLE TRIGGER USER;','COMMIT;']
    (OUT/'fixtures.sql').write_text('\n'.join(seed)+'\n',encoding='utf8',newline='\n')
    result={'scope':'DORMANT_SYNTHETIC_SQL_AND_EXACT_CAPABILITIES_ONLY','runtime_status':'NOT_RUN','fingerprint_codec':'SHA256 UTF8 synthetic-intent:<scenario semantic key>; fixture only, not an auth/request adapter proof','scenarios':scenarios}
    (OUT/'fixtures.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf8',newline='\n')
    print(json.dumps({'prepared_scenarios':len(scenarios),'runtime_executed':False}))

if __name__=='__main__':prepare()
