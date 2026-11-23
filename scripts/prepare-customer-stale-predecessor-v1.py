"""Prepare source-only three-case Customer rollback packet. No processes."""
import argparse
from copy import deepcopy
import hashlib
import json
from pathlib import Path
import re
import uuid
ROOT=Path(__file__).resolve().parents[1]
OUT='review-output/customer-stale-predecessor-v1'
APPLICATION='review-output/foundation-application.review.sql'
BASE='review-output/customer-control-rehearsal'
BASE_SHA='b59ab33ba26a29d2d82ee4f7f289d26e95300b7afb8ce7eaf7806fd5fb08a9c3'
PROTOCOL='scripts/customer_stale_predecessor_v1_protocol.py'
COORDINATOR='scripts/sql-review/run-customer-stale-predecessor-v1.py'
CHECK='scripts/check-customer-stale-predecessor-v1.py'
SELF='scripts/prepare-customer-stale-predecessor-v1.py'
DOC='scripts/sql-review/CUSTOMER-STALE-PREDECESSOR-V1.md'
SOURCE_INPUTS=(APPLICATION,'context/reconciliation/foundation-sql-draft-access.json','context/reconciliation/database-candidate-tests.json',
 'context/reconciliation/local-f0-assertions.json','context/shared/contracts/SH-004.md','context/shared/contracts/SH-052.md',
 'context/clusters/identity, authority, & consent/Customer Buyer Profile Module/customer-buyer-profile-module-architecture.md',
 BASE+'/fixtures.json',BASE+'/customer-00-valid.sql',BASE+'/customer-00-valid-observe.sql',PROTOCOL,SELF,COORDINATOR,CHECK,DOC,'tests/offline/customer-stale-predecessor-v1/native-before.json','scripts/sql-review/run-context-control-rehearsal.py',
 'scripts/sql-review/run-first-rehearsal.py','scripts/sql-review/run-local-f0-migrate.py','scripts/sql-review/rehearsal-diagnostics.py',
 'scripts/prepare-local-f0-history.py','scripts/sql-review/collect_native_catalog.sql')

def sha(raw):return hashlib.sha256(raw).hexdigest()
def encoded(v):return (json.dumps(v,indent=2)+'\n').encode()
def quote(v):return "'"+str(v).replace("'","''")+"'"
def replace(value,mapping):
    if isinstance(value,dict):return {k:replace(v,mapping)for k,v in value.items()}
    if isinstance(value,list):return [replace(v,mapping)for v in value]
    if type(value)is str:
        for a,b in mapping.items():value=value.replace(a,b)
    return value

def build(root,run_id):
    root=Path(root);run=uuid.UUID(run_id)
    if str(run)!=run_id or run.version!=4:raise ValueError('FRESH_UUID4_FIXTURE_RUN')
    application=(root/APPLICATION).read_bytes()
    if sha(application)!='5ae39abf991f9c189e367eb6ab6968b0ad50836bf4220ac27ef8c18306ac26ad':raise ValueError('CANONICAL_SOURCE_DRIFT')
    oldraw=(root/BASE/'fixtures.json').read_bytes()
    if sha(oldraw)!=BASE_SHA:raise ValueError('REVIEWED_CUSTOMER_BASELINE_REQUIRED')
    base=json.loads(oldraw);old=base['cases'][0]
    if old['name']!='customer-00-valid'or old['expected_commit']is not True:raise ValueError('EXACT_GENUINE_CREATE_BASELINE')
    uid=lambda name:str(uuid.uuid5(run,name));mapping={v:uid(k)for k,v in old['ids'].items()};name='csp1-'+run_id[:8]+'-baseline';mapping[old['name']]=name
    mapping[old['fixture_values']['response']['value']['receipt']['fingerprint']]=sha(('synthetic-intent:'+old['semantic_key'].replace(old['name'],name)).encode())
    baseline=replace(deepcopy(old),mapping);baseline['name']=name
    files={}
    for key,dest in(('transaction_sql','baseline-create.sql'),('observer_sql','baseline-observe.sql')):
        src=old[key];raw=(root/BASE/src).read_bytes()
        if sha(raw)!=base['files_sha256'][src]:raise ValueError('REVIEWED_BASELINE_LEAF_DRIFT')
        files[dest]=replace(raw.decode('utf8'),mapping);baseline[key]=dest
    c,u=baseline['ids']['CustomerProfile'],baseline['ids']['user'];security=uid('security-profile')
    seed=["-- Trusted Identity seed only. All Customer physical/deferred guards stay enabled.","BEGIN;","ALTER TABLE app.users DISABLE TRIGGER owner_commit;","ALTER TABLE app.user_security_profiles DISABLE TRIGGER owner_commit;",
     f"INSERT INTO app.users(id,is_public,revision,privacy_generation,created_at,updated_at,mutation_transaction_id) VALUES({quote(u)},false,0,0,clock_timestamp(),clock_timestamp(),pg_current_xact_id()::text);",
     f"INSERT INTO app.user_security_profiles(id,user_id,revision,security_generation,created_at,updated_at,mutation_transaction_id) VALUES({quote(security)},{quote(u)},0,0,clock_timestamp(),clock_timestamp(),pg_current_xact_id()::text);",
     'SET CONSTRAINTS ALL IMMEDIATE;','ALTER TABLE app.user_security_profiles ENABLE TRIGGER owner_commit;','ALTER TABLE app.users ENABLE TRIGGER owner_commit;','SET CONSTRAINTS ALL DEFERRED;','COMMIT;']
    files['trusted-identity-setup.sql']='\n'.join(seed)+'\n'
    acl=json.loads((root/'context/reconciliation/foundation-sql-draft-access.json').read_bytes());select=[r for r in acl if r['model']=='CustomerProfile'and r['role']=='wa_app_runtime'and r['operation']=='SELECT'];assert len(select)==1 and len(select[0]['fields'])==14
    caps=sorted({f'CustomerProfile/{c}/SELECT/'+x for x in select[0]['fields']}|{f'CustomerProfile/{c}/UPDATE/'+x for x in('@row','displayName','revision','updatedAt')}|{f'CustomerProfile/{c}/revision/0'})
    grant={'database_login_role':'wa_app_runtime','principal_user_id':u,'owner_module_id':'customer_buyer_profile','action':'updateCustomerProfileIdentity.v1','purpose':'profile_update','target_kind':'CustomerProfile','target_id':c,'source_generation':'0','security_generation':'0','allowed_fields':caps,'policy_version':'customer-stale-predecessor.v1'}
    files['visible-revision0.sql']=f"SELECT jsonb_build_object('rows',count(*),'exact_target',coalesce(bool_and(id={quote(c)}::uuid AND user_id={quote(u)}::uuid),false),'revision_zero',coalesce(bool_and(revision=0 AND privacy_generation=0),false),'original_fields',coalesce(bool_and(status='active' AND display_name IS NULL AND avatar_media_id IS NULL AND city IS NULL AND state IS NULL AND country IS NULL AND archived_at IS NULL),false)) FROM app.customer_profiles WHERE id={quote(c)}::uuid;\n"
    update=lambda delta,pre:f"UPDATE app.customer_profiles SET display_name='csp1-synthetic-prefix',revision=revision+{delta} WHERE id={quote(c)}::uuid AND revision={pre} RETURNING id,revision"
    files['first-update-prefix.sql']="WITH changed AS ("+update(1,0)+f") SELECT jsonb_build_object('rows',count(*),'target',coalesce(bool_and(id={quote(c)}::uuid),false),'revision_one',coalesce(bool_and(revision=1),false)) FROM changed;\n"
    files['wrong-predecessor.sql']="SELECT 'WA_CSP1_BEFORE';\nWITH changed AS ("+update(1,1)+") SELECT jsonb_build_object('rows',count(*)) FROM changed;\nSELECT 'WA_CSP1_AFTER';\nROLLBACK;\nSELECT 'WA_CSP1_ROLLBACK';\n"
    def negative(statement):return "SELECT 'WA_CSP1_BEFORE';\n\\set ON_ERROR_STOP off\n"+statement+";\n\\if :ERROR\n\\echo WA_CSP1_FAILED_STATEMENT\n\\echo WA_CSP1_SQLSTATE :SQLSTATE\n\\else\n\\echo WA_CSP1_UNEXPECTED_SUCCESS\n\\endif\n\\set ON_ERROR_STOP on\nROLLBACK;\nSELECT 'WA_CSP1_ROLLBACK';\n"
    files['skipped-revision.sql']=negative(update(2,0));files['same-grant-second-source-update.sql']=negative(update(1,1))
    sql=application.decode('utf8');tables=sorted(x.replace('"','')for x in re.findall(r'CREATE TABLE ("?[a-z_][a-z_0-9]*"?\."?[a-z_][a-z_0-9]*"?)\s*\(',sql));assert len(tables)==42 and len(set(tables))==42
    selects=[]
    for table in tables:
        where=' WHERE id<>ALL(__EXCLUDED_GRANT_IDS__)'if table=='platform.database_action_grant'else''
        selects.append("SELECT "+quote(table)+" AS table_name,count(*) AS row_count,encode(sha256(convert_to(coalesce(jsonb_agg(to_jsonb(t) ORDER BY to_jsonb(t)::text),'[]'::jsonb)::text,'UTF8')),'hex') AS row_sha FROM "+table+" t"+where)
    files['full42-state-observe.sql']="SELECT jsonb_agg(jsonb_build_object('table',table_name,'count',row_count,'sha256',row_sha) ORDER BY table_name) FROM ("+' UNION ALL '.join(selects)+") state;\n"
    tr=[]
    for m in re.finditer(r'CREATE\s+(?:CONSTRAINT\s+)?TRIGGER\s+"?([a-z_][a-z_0-9]*)"?\s+([^;]*);',sql,re.S):
        table=re.search(r'\bON\s+("?[a-z_][a-z_0-9]*"?\."?[a-z_][a-z_0-9]*"?)',m[2]);fn=re.search(r'EXECUTE FUNCTION ([a-z_][a-z_0-9]*\.[a-z_][a-z_0-9]*)\(\)',m[2])
        if table and fn:tr.append((table[1].replace('"',''),m[1],fn[1]))
    assert len(tr)==100
    vals=','.join('('+','.join(quote(x)for x in row)+')'for row in sorted(tr))
    files['all100-trigger-observe.sql']="WITH expected(table_name,name,function_name)AS(VALUES "+vals+"),actual AS(SELECT n.nspname||'.'||c.relname,t.tgname::text,fn.nspname||'.'||p.proname FROM pg_trigger t JOIN pg_class c ON c.oid=t.tgrelid JOIN pg_namespace n ON n.oid=c.relnamespace JOIN pg_proc p ON p.oid=t.tgfoid JOIN pg_namespace fn ON fn.oid=p.pronamespace WHERE n.nspname IN('app','platform','platform_private') AND NOT t.tgisinternal) SELECT jsonb_build_object('expected',100,'actual',(SELECT count(*)FROM actual),'exact',NOT EXISTS((SELECT * FROM expected EXCEPT SELECT * FROM actual)UNION ALL(SELECT * FROM actual EXCEPT SELECT * FROM expected)),'enabled',NOT EXISTS(SELECT 1 FROM pg_trigger t JOIN pg_class c ON c.oid=t.tgrelid JOIN pg_namespace n ON n.oid=c.relnamespace WHERE n.nspname IN('app','platform','platform_private')AND NOT t.tgisinternal AND t.tgenabled<>'O'));\n"
    tables_by_id={'CustomerProfile':'app.customer_profiles','RuntimeCommandReceipt':'platform.runtime_command_receipt','duplicate':'platform.runtime_command_receipt','CustomerProfileLifecycleEvent':'app.customer_profile_lifecycle_event','OwnerMutationEvidence':'platform.owner_mutation_evidence','event':'platform.runtime_outbox_message','free':'platform.runtime_outbox_message','extra':'platform.runtime_outbox_message','user':'app.users','grant':'platform.database_action_grant'}
    fresh=['NOT EXISTS(SELECT 1 FROM '+tables_by_id[k]+' WHERE id='+quote(v)+'::uuid)'for k,v in baseline['ids'].items()]
    fresh += [f"NOT EXISTS(SELECT 1 FROM app.user_security_profiles WHERE id={quote(security)}::uuid OR user_id={quote(u)}::uuid)",f"NOT EXISTS(SELECT 1 FROM platform.database_action_grant WHERE principal_user_id={quote(u)}::uuid)"]
    files['fresh-namespace.sql']='SELECT '+' AND '.join(fresh)+';\n'
    bypasses=[]
    for table in('app.users','app.user_security_profiles'):
        trigger=next(row for row in tr if row[0]==table and row[1]=='owner_commit');function=trigger[2]
        body=re.search(r'CREATE FUNCTION '+re.escape(function)+r'\(\).*?AS \$wa\$(.*?)\$wa\$;',sql,re.S)
        assert body is not None
        bypasses.append({'table':table,'trigger':'owner_commit','function':function,'body_sha256':sha(body[1].encode()),'expected_enabled':'O','setup_only':True})
    pins={p:sha((root/p).read_bytes())for p in SOURCE_INPUTS}
    cases=[{'name':name,'sql':name+'.sql','status':'NOT_RUN','explicit_rollback_required':True,'first_update_prefix':name=='same-grant-second-source-update','intended':None if name=='wrong-predecessor'else {'state':'P0001'if name=='skipped-revision'else'42501','message':'CAS revision must increment once'if name=='skipped-revision'else'field or CAS scope denied','function':'platform_private.guard_customerprofile','body_sha256':'242bc33836b80f24cdcd22495d133678fd8b5d204f145ffa3f689308a91aba95','line':9 if name=='skipped-revision'else 13}}for name in('wrong-predecessor','skipped-revision','same-grant-second-source-update')]
    packet={'schema':'workinants.customer-stale-predecessor-fixtures.v1','status':'NOT_RUN','database_posture':'D','database_contacted':False,'sql_executed':False,'fixture_run_id':run_id,'case_id':'P0C-CAS-01','assertion_id':'control.stale_predecessor','assertion_expected_sha256':'72f2d75ee3f9af764982f379f5dc82805531d09dc85f0925f8d7c6ab69795d3e','case_order':[x['name']for x in cases],'cases':cases,'baseline':baseline,'baseline_creation_group':{'customer':1,'command':1,'history':1,'evidence':1,'outbox':2,'track_enrollments':0,'coherent':True},'identity_security_profile_id':security,'update_grant':grant,'source_files_sha256':pins,'prepared_files_sha256':{p:sha(s.encode())for p,s in sorted(files.items())},'full42_tables':tables,'fixture_bypasses':bypasses,'full_native_prerequisite':{'source_expected_sha256':'3be81a13d3bb2abb41bf03ef68398da6d92fbdbccffec3d74508e91dd455f433','native_PASS':29089,'expression_oracle_PASS':416,'private_ledger_PASS':22},'worker_ACL_rows':32,'execution':'OWNED_WRAPPER_NOT_IMPLEMENTED_SOURCE_ONLY','limits':['No COMMIT of Customer UPDATE, update result or no-result codec.','No concurrent winner, full P0C-CAS-01 or OWNER-REVISIONS claim.','Only one retained creation history/evidence group; failed source prefixes add none.','Fixture exceptions apply only to trusted Identity seed, never Customer guards.']}
    packet['content_sha256']=sha(json.dumps({k:packet[k]for k in('source_files_sha256','prepared_files_sha256')},sort_keys=True,separators=(',',':')).encode())
    files['fixtures.json']=encoded(packet).decode();return files,packet

def main(argv=None):
    ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--fixture-run-id',required=True);args=ap.parse_args(argv)
    files,packet=build(ROOT,args.fixture_run_id);out=ROOT/OUT
    if out.exists():raise ValueError('EXCLUSIVE_NEW_PACKET_DIRECTORY_REQUIRED')
    out.mkdir(parents=True)
    for p,s in files.items():(out/p).write_text(s,encoding='utf8',newline='\n')
    print(json.dumps({'status':'SOURCE_PREPARED_NOT_EXECUTED','files':len(files),'fixtures_sha256':sha((out/'fixtures.json').read_bytes()),'content_sha256':packet['content_sha256']}))
if __name__=='__main__':main()
