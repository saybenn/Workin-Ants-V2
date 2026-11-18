"""Prepare NEW finite lease/revocation source artifacts; never run SQL/processes.

Existing packets remain untouched. Actual selected IDs are TRACK-01 and CTX-02.
Only synthetic SQL transport is prepared; missing owner ports and whole cases
remain NOT_RUN. A separate reviewed root operation is mandatory for execution.
"""
import argparse
import builtins
from copy import deepcopy
import hashlib
import json
from pathlib import Path
from types import ModuleType
import uuid

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'review-output/lease-revoke-control-rehearsal'
SELF='scripts/prepare-lease-revoke-control-rehearsal.py'
CHECK='scripts/check-lease-revoke-control-rehearsal.py'
PROTOCOL='scripts/lease_revoke_control_protocol.py'
DOC='scripts/sql-review/lease-revoke-controls-coordinator.md'
CM='scripts/prepare-customer-control-rehearsal.py'
CS='scripts/contract_schema.py'
WM='scripts/prepare-worker-control-rehearsal.py'
ACL='context/reconciliation/foundation-sql-draft-access.json'
APPLICATION='review-output/foundation-application.review.sql'
PINNED={CM:'6d67c52ab7c3cc95082c5c82cf007910fcb75a7721d832d3236fe213e3bba174',CS:'27b91594ac3dc9e1345b5bde912b4a849f0a324e90819df56150f7e3d326bc8c',WM:'190748986c732b44aa093b00f496cfe318e579bab5f3d4904b7c69fc5400ffd2',APPLICATION:'5ae39abf991f9c189e367eb6ab6968b0ad50836bf4220ac27ef8c18306ac26ad',ACL:'f9d529a7fc481beea3fcb0b2307fce47c44d7168380a7e2dfab6b9be44831eea'}
NS=uuid.UUID('22483d65-0932-45f6-a9ae-e72da3e20d2d')
SCHEMAS=('contracts/shared/SH-004.v1.schema.json','contracts/shared/types.v1.schema.json','contracts/database-review/foundation-payloads.v1.schema.json','contracts/database-review/owner-mutation-evidence.v1.schema.json')
CONTEXTS=('context/reconciliation/database-candidate-tests.json','context/reconciliation/local-f0-assertions.json','context/reconciliation/platform-architecture-rulings.md','context/shared/contracts/SH-051.md','context/shared/contracts/SH-052.md','context/shared/contracts/SH-054.md','context/shared/contracts/SH-114.md','context/clusters/identity, authority, & consent/Track Subscription & Entitlement Module/track-subscription-entitlement-module-architecture.md','context/clusters/identity, authority, & consent/Track Subscription & Entitlement Module/track-subscription-entitlement-implementation-plan.md','context/clusters/identity, authority, & consent/Identity & Access module/identity-access-module-architecture.md','context/clusters/identity, authority, & consent/Identity & Access module/identity-access-module-implementation-plan.md')

def sha(raw):return hashlib.sha256(raw).hexdigest()
def canonical(value):return json.dumps(value,sort_keys=True,separators=(',',':'),ensure_ascii=False,allow_nan=False)
def encoded(value):return (json.dumps(value,indent=2,ensure_ascii=False,allow_nan=False)+'\n').encode()
def uid(name):return str(uuid.uuid5(NS,name))
def quote(value):return "'"+str(value).replace("'","''")+"'"
def need(value,code):
    if not value:raise ValueError(code)

def compile_source(root,path,raw,contract=None):
    module=ModuleType('_lease_revoke_preparation');module.__file__=str(root/path)
    original=builtins.__import__
    def imports(name,*args,**kwargs):
        if name=='contract_schema':need(contract is not None,'CLOSED_CONTRACT_HELPER_REQUIRED');return contract
        return original(name,*args,**kwargs)
    module.__dict__['__builtins__']={**vars(builtins),'__import__':imports}
    exec(compile(raw,module.__file__,'exec'),module.__dict__)
    return module

def build(root=ROOT):
    root=Path(root)
    paths=sorted(set((SELF,CHECK,PROTOCOL,DOC,CM,CS,WM,ACL,APPLICATION)+SCHEMAS+CONTEXTS))
    blobs={path:(root/path).read_bytes() for path in paths};pins={path:sha(raw) for path,raw in blobs.items()}
    for path,wanted in PINNED.items():need(pins[path]==wanted,'REVIEWED_SOURCE_DRIFT')
    contract=compile_source(root,CS,blobs[CS]);cm=compile_source(root,CM,blobs[CM],contract);wm=compile_source(root,WM,blobs[WM]);protocol=compile_source(root,PROTOCOL,blobs[PROTOCOL])
    # Only the four used closed schema documents enter this evaluator. Missing
    # refs fail; no filesystem/network fallback or semantic-schema substitute.
    registry=cm.FixtureRegistry.__new__(cm.FixtureRegistry);registry.root=root
    registry.documents={json.loads(blobs[path])['$id']:json.loads(blobs[path]) for path in SCHEMAS}
    for path in SCHEMAS[:2]:doc=json.loads(blobs[path]);registry.preflight(doc,doc)
    cm.NAMESPACE=NS
    acl=json.loads(blobs[ACL]);worker_acl=[row for row in acl if row['role']=='wa_worker'];need(len(worker_acl)==32,'EXACT_32_WORKER_ACL_ROWS_REQUIRED')
    register=json.loads(blobs[CONTEXTS[0]]);assertions=json.loads(blobs[CONTEXTS[1]])
    selected=('P0C-TRACK-01','P0C-CTX-02');definitions={name:deepcopy(next(row for row in register['tests'] if row['id']==name)) for name in selected}
    exact_assertions={name:deepcopy(next(row for row in assertions['cases'] if row['id']==name)) for name in selected}
    need(all(row['status']=='NOT_RUN' for row in definitions.values()) and all(row['status']=='NOT_RUN' for case in exact_assertions.values() for row in case['assertions']),'REGISTER_MUST_REMAIN_NOT_RUN')
    files={};sources={}
    for name in ('lease','app-positive','app-recovery'):
        case,body,observer=cm.create_case('lease-revoke-'+name,'valid',acl,registry)
        sources[name]=case;files['source-'+name+'.sql']=body;files['source-'+name+'-observe.sql']=observer
    fixtures=['BEGIN;','ALTER TABLE app.users DISABLE TRIGGER owner_commit;','ALTER TABLE app.user_security_profiles DISABLE TRIGGER owner_commit;']
    for name,case in sources.items():
        user=case['ids']['user']
        fixtures += ["INSERT INTO app.users(id,is_public,revision,privacy_generation,created_at,updated_at) VALUES ("+quote(user)+",false,0,0,clock_timestamp(),clock_timestamp());","INSERT INTO app.user_security_profiles(id,user_id,revision,security_generation,created_at,updated_at) VALUES ("+quote(uid(name+'/security'))+','+quote(user)+',0,0,clock_timestamp(),clock_timestamp());']
    fixtures+=['ALTER TABLE app.user_security_profiles ENABLE TRIGGER owner_commit;','ALTER TABLE app.users ENABLE TRIGGER owner_commit;','COMMIT;'];files['independent-user-fixtures.sql']='\n'.join(fixtures)+'\n'
    triggers,trigger_sql=cm.fixture_trigger_restoration(blobs[APPLICATION].decode());files['fixture-trigger-restore-observe.sql']=trigger_sql
    work={name:uid(name+'/work') for name in sources};services={'worker':'lease-revoke-worker.v1','app':'lease-revoke-app.v1'}
    def caps(role,key,update=(),insert=False,revision=0):
        ops={'SELECT':[]}
        if update:ops['UPDATE']=list(update)
        if insert:ops['INSERT']=[]
        return wm.capabilities(acl,role,{'RuntimeWorkItem':[work[key]]},{'RuntimeWorkItem':ops},{'RuntimeWorkItem':[(work[key],revision)]})
    def grant(role,key,action,purpose,fields,revision=0,generation=0,principal=None,service=None):
        return {'database_login_role':role,'owner_module_id':'platform_integration_owner','action':action,'purpose':purpose,'target_kind':'RuntimeWorkItem','target_id':work[key],'principal_user_id':principal,'service_principal':service,'source_generation':str(revision),'security_generation':str(generation),'allowed_fields':fields,'policy_version':'lease-revoke-synthetic-transport.v1'}
    grants={'source-'+name:deepcopy(case['grant']) for name,case in sources.items()}
    grants['schedule-lease']=grant('wa_app_runtime','lease','runtime.schedule_work.v1','work.schedule',caps('wa_app_runtime','lease',insert=True),principal=sources['lease']['ids']['user'])
    for fence in (0,1,2):
        grants['claim-'+str(fence)]=grant('wa_worker','lease','runtime.claim_work.v1','work.claim',caps('wa_worker','lease',('state','fence','leaseTokenHash','leaseExpiresAt','attemptCount'),revision=fence),fence,service=services['worker'])
    for fence in (1,2):
        grants['renew-'+str(fence)]=grant('wa_worker','lease','runtime.renew_work.v1','work.renew',caps('wa_worker','lease',('leaseExpiresAt',),revision=fence),fence,service=services['worker'])
    grants['old-holder']=deepcopy(grants['renew-1'])
    for generation in (0,1,2,3):
        grants['app-read-'+str(generation)]=grant('wa_app_runtime','app-positive','runtime.schedule_work.v1','work.schedule',caps('wa_app_runtime','app-positive'),generation=generation,service=services['app'])
        grants['app-write-'+str(generation)]=grant('wa_app_runtime','app-recovery','runtime.schedule_work.v1','work.schedule',caps('wa_app_runtime','app-recovery',insert=True),generation=generation,service=services['app'])
    grants['app-positive']=grant('wa_app_runtime','app-positive','runtime.schedule_work.v1','work.schedule',caps('wa_app_runtime','app-positive',insert=True),service=services['app'])
    for name,case in sources.items():
        scheduler="INSERT INTO platform.runtime_work_item(id,outbox_message_id,handler_name,semantic_work_key,state,fence,attempt_count) VALUES ("+quote(work[name])+','+quote(case['ids']['free'])+",'assignDefaultFreeTrack.v1',"+quote(case['fixture_values']['free_command']['semanticKey'])+",'pending',0,0);\nSELECT 'WA_LR_SCHEDULE_READY';\nCOMMIT;\n"
        files['schedule-'+name+'.sql']=scheduler
    for name in protocol.CASE_ORDER:
        if name in ('app-bound-before-rotate','app-bound-before-revoke','app-fresh-after-recover'):
            source=sources['app-recovery'];files[name+'.sql']=protocol.schedule_sql(name,work['app-recovery'],source['ids']['free'],source['fixture_values']['free_command']['semanticKey'])
        elif name in protocol.DIAGNOSTICS or name in ('worker-claim','worker-renew','current-holder-renew'):
            files[name+'.sql']=protocol.lease_sql(name,work['lease'])
    files['reclaim.sql']=protocol.lease_sql('concurrent-reclaim-stale-holder',work['lease'])
    files['stale-holder.sql']=protocol.stale_holder_sql(work['lease'])
    files['app-read.sql']="SELECT jsonb_build_object('visible_exact_work',count(*)) FROM platform.runtime_work_item WHERE id="+quote(work['app-positive'])+';\nROLLBACK;\n'
    files['lease-clock.sql']="SELECT jsonb_build_object('expired',lease_expires_at<=clock_timestamp(),'same_fence',fence=1,'same_attempt',attempt_count=1,'effect_absent',effect_receipt_id IS NULL) FROM platform.runtime_work_item WHERE id="+quote(work['lease'])+';\n'
    users=','.join(quote(case['ids']['user']) for case in sources.values());work_ids=','.join(quote(value) for value in work.values())
    files['no-effects-observe.sql']="SELECT jsonb_build_object('attempt_rows',(SELECT count(*) FROM platform.runtime_attempt WHERE work_item_id="+quote(work['lease'])+"),'effect_links',(SELECT count(*) FROM platform.runtime_work_item WHERE id IN ("+work_ids+") AND effect_receipt_id IS NOT NULL),'track_subscriptions',(SELECT count(*) FROM app.track_subscriptions WHERE user_id IN ("+users+")),'track_selections',(SELECT count(*) FROM app.track_base_selection WHERE user_id IN ("+users+")),'track_grants',(SELECT count(*) FROM app.track_entitlement_grants WHERE user_id IN ("+users+")),'track_history',(SELECT count(*) FROM app.track_subscription_events WHERE user_id IN ("+users+")));\n"
    identities={}
    for kind,service in services.items():
        receipts={step:uid(kind+'/identity/'+step) for step in ('bootstrap','rotate','revoke','recover')};identities[kind]=receipts
        for generation,step in enumerate(('bootstrap','rotate','revoke','recover')):
            if kind=='worker' and step!='bootstrap':continue
            values={'id':quote(receipts[step]),'service_principal':quote(service),'security_generation':str(generation),'transition':quote(step),'identity_authorization_ref':quote('synthetic-lease-revoke-'+kind+'-'+step+'.v1')}
            if generation:values.update(previous_generation=str(generation-1),previous_receipt_id=quote(receipts[('bootstrap','rotate','revoke','recover')[generation-1]]))
            if step!='revoke':values['revoked_at']='NULL'
            statements=['BEGIN;',wm.insert('platform_private.identity_service_receipt',values)]
            if not generation:statements.append(wm.insert('platform_private.identity_service_authorization',{'service_principal':quote(service),'security_generation':'0','identity_receipt_id':quote(receipts[step])}))
            else:statements.append('UPDATE platform_private.identity_service_authorization SET security_generation='+str(generation)+',identity_receipt_id='+quote(receipts[step])+',revoked_at=(SELECT revoked_at FROM platform_private.identity_service_receipt WHERE id='+quote(receipts[step])+') WHERE service_principal='+quote(service)+' AND security_generation='+str(generation-1)+' AND identity_receipt_id='+quote(receipts[('bootstrap','rotate','revoke','recover')[generation-1]])+';')
            files['identity-'+kind+'-'+step+'.sql']='\n'.join(statements+['COMMIT;'])+'\n'
    files['README.md']='''Source-only finite lease and application-context currentness packet. All selected controls remain NOT_RUN. No provisioning, migrations, permission repair, privileged expiry edits, worker loop, production Identity adapter or Customer UPDATE codec is provided. Restricted native scheduler/claim/renew plus independent synthetic Identity transitions require a separately reviewed Root operation, exact same-run/CID/full native PASS attestation, safe logging and owner-only credentials. Expiration uses actual clock_timestamp(), bounded waiting and no timestamp edits. Partial source exact guards and closed-backend observations never promote the compound Track/CTX cases. Missing owner security/source-generation ports and lease attach/recovery stay explicit outside this packet.\n\nPlain English: timed work tickets change hands only through their real locks; canceled permissions must stop working. These games have not run.\n'''
    need(all(sha((root/path).read_bytes())==value for path,value in pins.items()),'SOURCE_CHANGED_DURING_PREPARATION')
    prepared={name:sha(text.encode()) for name,text in files.items()}
    packet={'schema':'workinants.lease-revoke-fixtures.v1','status':'NOT_RUN','database_posture':'D','database_contacted':False,'sql_executed':False,'selected_control_ids':list(selected),'source_definitions':definitions,'source_assertions':exact_assertions,'source_files_sha256':pins,'prepared_files_sha256':prepared,'worker_acl_rows':32,'worker_acl_sha256':sha(canonical(worker_acl).encode()),'sources':sources,'work_ids':work,'services':services,'identity_receipts':identities,'grants':grants,'case_order':list(protocol.CASE_ORDER),'finite_caps':{'grant_instances_max':48,'sessions_simultaneous_max':3,'clock_wait_seconds_max':45,'clock_poll_seconds':0.1,'old_holder_idle_seconds_max':60,'no_enrollment_loop':True},'fixture_trigger_contract':{'expected':triggers,'observer_expected':{'expected_user_trigger_count':len(triggers),'actual_user_trigger_count':len(triggers),'exact_user_trigger_set_and_states':True,'no_project_user_trigger_disabled':True}},'coverage_limits':{'selected_cases':'NOT_RUN','whole_94':'NOT_PROMOTED','whole_451':'NOT_PROMOTED','Identity_adapter':'SYNTHETIC_NOT_QUALIFIED','lease_attach_and_recovery':'NOT_PREPARED_HERE','owner_generations':'NOT_PREPARED_MISSING_OWNER_PORTS','Customer_update_gate':cm.GATE},'source_only_packet_sha256':sha(canonical({'source_files_sha256':pins,'prepared_files_sha256':prepared}).encode())}
    files['fixtures.json']=encoded(packet)
    return {name:text.encode() if type(text) is str else text for name,text in files.items()},packet

def main(argv=None):
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--prepare',action='store_true');args=parser.parse_args(argv)
    if not args.prepare:parser.error('explicit source preparation only; no runtime')
    files,packet=build();OUT.mkdir(exist_ok=False)
    for name,raw in files.items():
        with (OUT/name).open('xb') as handle:handle.write(raw)
    print(json.dumps({'status':'SOURCE_PREPARED_NOT_RUN','files':len(files),'content_sha256':packet['source_only_packet_sha256'],'selected_controls':'NOT_RUN','database_contacted':False}));return 0
if __name__=='__main__':raise SystemExit(main())
