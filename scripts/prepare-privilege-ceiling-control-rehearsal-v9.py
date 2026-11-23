"""Pure finite source generator. No process, database, Git or network boundary."""
import argparse
from copy import deepcopy
import hashlib
import json
from pathlib import Path
import re
import sys
import uuid

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'scripts'))
import privilege_ceiling_control_protocol_v9 as P

PLAN='context/reconciliation/privilege-ceiling-approved-source-plan.json'
PLAN_SHA='3298704adfe2110a4a333945c37de4432e851e918598dfc966e665473aa7e066'
NATIVE='review-output/native-table-denials-v2/packet.json'
NATIVE_SHA='8044d43f25c4a449f662bbb467183aac86d6a619836aae0988458098d59e0b69'
NATIVE_COORDINATOR='scripts/sql-review/run-native-table-denials-v3.py'
NATIVE_COORDINATOR_SHA='6e74115cc7a77e626c4379c5a5744efdede1257d04b206fc339e62a23fd49cd3'
CTX='scripts/sql-review/run-context-control-rehearsal.py'
CTX_SHA='5ec53d01d7c5b19bea0a584ef9f5b4e6742d9509c21ac7e2250b9bdd62511f33'
APPLICATION='review-output/foundation-application.review.sql'
APPLICATION_SHA='5ae39abf991f9c189e367eb6ab6968b0ad50836bf4220ac27ef8c18306ac26ad'
MODELS='context/reconciliation/foundation-sql-draft-models.json'
EXPECTED='review-output/native-catalog/expected.json'
PROTOCOL='scripts/privilege_ceiling_control_protocol_v9.py'
OUTPUT='review-output/privilege-ceiling-control-rehearsal-v9'
HISTORICAL_PROGRESS='context/reconciliation/local-f0-qualification-status.json'
sha=lambda raw:hashlib.sha256(raw).hexdigest()
encoded=lambda value:(json.dumps(value,indent=2,allow_nan=False)+'\n').encode()


def source(root,name,wanted=None):
    P.require(type(name)is str and not Path(name).is_absolute()and'\\'not in name and':'not in name and all(x not in('','.','..')for x in name.split('/')),'SOURCE_PATH')
    path=(root/name).resolve();P.require(path.is_relative_to(root.resolve()),'SOURCE_PATH_ESCAPE');raw=path.read_bytes()
    if wanted is not None:P.require(sha(raw)==wanted,'PINNED_SOURCE_DRIFT')
    return raw


def body_contract(application,name,message):
    matches=list(re.finditer(r'CREATE FUNCTION platform_private\.'+re.escape(name)+r'\([^;]*?\).*?AS\s+(\$[a-z_0-9]*\$)(.*?)\1;',application,re.S))
    P.require(len(matches)==1,'ONE_SOURCE_FUNCTION_BODY');body=matches[0][2]
    lines=[i for i,line in enumerate(body.split('\n'),1)if'RAISE EXCEPTION '+P.quote(message)in line]
    P.require(len(lines)==1,'ONE_SOURCE_RAISE_LINE')
    return {'body_line':lines[0],'body_sha256':sha(body.encode()),'application_sha256':APPLICATION_SHA}


def contract(table,kind='NATIVE_ACL'):
    schema,relation=table.split('.')
    return {'kind':kind,'schema':schema,'relation':relation}


def provider_statement_lines(text):
    """Exact approved wrapper only; preserves its three statement token bytes."""
    P.require(type(text)is str and text.startswith('BEGIN; SELECT ')and text.endswith('; ROLLBACK;')and text.count(';')==3 and '\n'not in text and '\r'not in text,'EXACT_PROVIDER_TRANSACTION_TEMPLATE')
    return 'BEGIN;\n'+text[len('BEGIN; '):-len(' ROLLBACK;')]+'\nROLLBACK;'


def generate(root):
    root=root.resolve();plan=json.loads(source(root,PLAN,PLAN_SHA));native=json.loads(source(root,NATIVE,NATIVE_SHA))
    source(root,NATIVE_COORDINATOR,NATIVE_COORDINATOR_SHA);source(root,CTX,CTX_SHA)
    application=source(root,APPLICATION,APPLICATION_SHA).decode();models=json.loads(source(root,MODELS));expected=json.loads(source(root,EXPECTED))['expected']
    # The approved plan preserves its then-current progress hash. Later Root
    # evidence updates are not executable policy or a privilege verdict input.
    # The exact assertion inventory/register and every SQL/code input still pin.
    for name,wanted in plan['source_files_sha256'].items():
        if name!=HISTORICAL_PROGRESS:source(root,name,wanted)
    by_model={case['model']:case for case in native['cases']};model_rows={row['model']:row for row in models}
    artifacts={};cases=[]
    def add(row,text):
        P.require(row['name']not in{case['name']for case in cases},'UNIQUE_FINITE_CASE')
        P.require(text.lstrip().startswith(('--','BEGIN;'))and text.rstrip().endswith('ROLLBACK;'),'ROLLBACK_ONLY_NEGATIVE')
        name=f'{len(cases)+1:03d}-'+row['name']+'.sql';raw=text.encode();artifacts[name]=raw
        cases.append({**row,'status':'NOT_RUN','file':name,'sql_sha256':sha(raw),'whole_case_promoted':False})
    for link in plan['exact40_issuer_umbrella_map']:
        for item in link['contrasts']:
            P.require(item['actual_login']=='wa_context_issuer'and item['verb']in('INSERT','UPDATE','DELETE')and item['preparation_blocker']is None,'EXACT_117_ISSUER_SOURCE_CONTRASTS')
            case=by_model[link['model']];probe=next(p for p in case['probes']if p['role']=='wa_context_issuer'and p['verb']==item['verb'])
            P.require(sha(item['source_sql'].encode())==item['sql_sha256']==probe['sql_sha256'],'NATIVE_ISSUER_SOURCE_IDENTITY')
            fields=model_rows[link['model']]['fields']
            referenced=sorted(fields.values())if item['verb']=='INSERT'else[fields[field]for field in model_rows[link['model']]['pk']]
            add({'name':item['id'],'family':'ISSUER_BUSINESS_DML','role':'wa_context_issuer','verb':item['verb'],'table':link['table'],'model':link['model'],'source_case_id':link['case_id'],'assertion_id':link['assertion_id'],'diagnostic':contract(link['table']),'native_validity_file':case['native_controls'],'native_existing_file':case['existing_row_observer'],'referenced_columns':referenced,'native_probe':deepcopy(probe)},item['source_sql'])
    P.require(len(cases)==117,'EXACT_117_NON_GRANT_CASES')
    grant=by_model['DatabaseActionGrant']
    for row in plan['runtime_core_contrasts']:
        name=row['id'];role=row['actual_login'];base={'name':name,'family':'RUNTIME_ESCALATION','role':role,'source_case_id':'P0C-PRIV-01','assertion_id':'control.runtime_escalation'}
        if name.startswith('ROLE-'):
            target=name.removeprefix('ROLE-'+role+'-');add({**base,'operation':'SET_ROLE','diagnostic':{'kind':'SET_ROLE','target_role':target}},row['sql'])
        elif name.startswith('CREATE-'):
            schema=name.removeprefix('CREATE-'+role+'-');add({**base,'operation':'CREATE','schema':schema,'diagnostic':{'kind':'SCHEMA_CREATE','schema':schema}},row['sql'].replace('<run8>','__WA_RUN8__'))
        elif name.startswith('TRUNCATE-'):
            table=name.removeprefix('TRUNCATE-'+role+'-');add({**base,'operation':'TRUNCATE','table':table,'verb':'TRUNCATE','diagnostic':contract(table)},row['sql'])
        else:
            verb=name.rsplit('-',1)[1];probe=next(p for p in grant['probes']if p['role']==role and p['verb']==verb)
            text=probe['sql_text']
            if verb=='INSERT':
                # The runtime renderer replaces all 21 values with the actual
                # probe's live tuple; inert Native pid0/expired values never run.
                text='BEGIN;\nSET LOCAL search_path=pg_catalog;\nINSERT INTO platform.database_action_grant('+','.join(P.GRANT_COLUMNS)+') VALUES ('+','.join("'__WA_"+column.upper()+"__'::"+expected['tables']['platform.database_action_grant']['columns'][column]['type']['name']+('[]'if expected['tables']['platform.database_action_grant']['columns'][column]['type']['array_dimensions']else'')for column in P.GRANT_COLUMNS)+');\nROLLBACK;\n'
            add({**base,'operation':'GRANT_'+verb,'table':'platform.database_action_grant','verb':verb,'diagnostic':contract('platform.database_action_grant'),'native_probe':deepcopy(probe),'actual_tuple_required':verb=='INSERT','native_existing_file':grant['existing_row_observer'],'native_validity_file':grant['native_controls'],'referenced_columns':list(P.GRANT_COLUMNS)if verb=='INSERT'else['id']},text)
    P.require(len(cases)==151,'EXACT_34_RUNTIME_CASES')
    for row in plan['provider_contrasts']:
        schema=next(schema for schema in ('platform_private','platform','app')if schema+'.'in row['sql'])
        add({'name':row['id'],'family':'PROVIDER_REACHABILITY','role':row['actual_login'],'operation':'SCHEMA_REACHABILITY','diagnostic':{'kind':'NATIVE_ACL','schema':schema,'relation':'database_action_grant'if schema=='platform'else'identity_service_authorization'if schema=='platform_private'else'users'},'source_case_id':'P0C-PRIV-01','assertion_id':'control.browser_simulation','maximum':row['maximum']},provider_statement_lines(row['sql']))
    P.require(len(cases)==169,'EXACT_18_PROVIDER_CASES')
    baseline=native['synthetic_facts']['baseline']
    for table in ('platform_private.identity_service_authorization','platform_private.identity_service_receipt'):
        columns=expected['tables'][table]['columns'];facts=baseline[table];pk='service_principal'if table.endswith('authorization')else'id';predicate=P.ident(pk)+'='+P.typed(facts[pk],columns[pk]['type'])
        ordered=sorted(columns,key=lambda c:columns[c]['ordinal'])
        for verb in ('INSERT','UPDATE'):
            candidate=dict(facts)
            candidate[pk]='privilege-ceiling-source-native-candidate.v1'if pk=='service_principal'else str(uuid.uuid5(uuid.NAMESPACE_URL,'workinants-privilege-private-native-candidate'))
            if verb=='INSERT':text='INSERT INTO '+P.table(table)+'('+','.join(P.ident(c)for c in ordered)+') VALUES ('+','.join(P.typed(candidate[c],columns[c]['type'])for c in ordered)+');'
            else:text='UPDATE '+P.table(table)+' SET '+P.ident('security_generation')+'='+P.typed(facts['security_generation'],columns['security_generation']['type'])+' WHERE '+predicate+' RETURNING 1;'
            add({'name':'ISSUER-PRIVATE-'+table.rsplit('.',1)[1]+'-'+verb,'family':'ISSUER_IDENTITY_SOURCE_CEILING','role':'wa_context_issuer','verb':verb,'table':table,'operation':'PRIVATE_'+verb,'diagnostic':contract(table),'source_case_id':'P0C-PRIV-01','assertion_id':'control.issuer_ceiling','referenced_columns':ordered if verb=='INSERT'else['security_generation',pk],'existing_predicate':predicate,'validity_limit':'Known existing source table/target and exact column types. Only the independently proven earlier native permission gate may qualify; deeper private INSERT guard/FK/unique validity is not claimed.'},'BEGIN;\nSET LOCAL search_path=pg_catalog;\n'+text+'\nROLLBACK;\n')
    for column in P.GRANT_COLUMNS:
        if column=='revoked_at':continue
        add({'name':'ISSUER-IMMUTABLE-'+column,'family':'ISSUER_COLUMN_CEILING','role':'wa_context_issuer','operation':'GRANT_FIELD_UPDATE','field':column,'table':'platform.database_action_grant','verb':'UPDATE','diagnostic':contract('platform.database_action_grant'),'source_case_id':'P0C-PRIV-01','assertion_id':'control.issuer_ceiling','referenced_columns':[column,'id'],'actual_own_grant_required':True},'BEGIN;\nSET LOCAL search_path=pg_catalog;\nUPDATE platform.database_action_grant SET '+P.ident(column)+"='__WA_CHANGED_VALUE__'::"+expected['tables']['platform.database_action_grant']['columns'][column]['type']['name']+('[]'if expected['tables']['platform.database_action_grant']['columns'][column]['type']['array_dimensions']else'')+" WHERE id='__WA_OWN_GRANT_ID__'::uuid RETURNING 1;\nROLLBACK;\n")
    for item in plan['helper_and_definer_contract']['actual_deny_calls']:
        for role in item['roles']:
            function=re.search(r'SELECT platform_private\.([a-z_]+)\(',item['sql'])[1]
            text=item['sql'].replace('<existing-source-id>',baseline['app.customer_profiles']['id'])
            add({'name':'HELPER-'+role+'-'+function,'family':'HELPER_RESULT_CEILING','role':role,'operation':'FUNCTION','diagnostic':{'kind':'FUNCTION','schema':'platform_private','function':function},'source_case_id':'P0C-PRIV-01','assertion_id':'control.helper_ceiling'},'BEGIN;\n'+text+'\nROLLBACK;\n')
    # Three separately named grant-guard cases have exact source RAISE frames.
    immutable={'kind':'IMMUTABLE_GRANT',**body_contract(application,'grant_guard','immutable grant')}
    add({'name':'ISSUER-UNREVOKED-NULL-REVOKE','family':'ISSUER_UNREVOKED_GUARD','role':'wa_context_issuer','operation':'UNREVOKED_GRANT_UPDATE','table':'platform.database_action_grant','verb':'UPDATE','diagnostic':immutable,'source_case_id':'P0C-PRIV-01','assertion_id':'control.issuer_ceiling','actual_unrevoked_own_grant_required':True},"BEGIN;\nUPDATE platform.database_action_grant SET revoked_at=NULL::timestamptz WHERE id='__WA_OWN_GRANT_ID__'::uuid RETURNING 1;\nROLLBACK;\n")
    for action in ('repeat-revoke','unrevoke'):
        value='clock_timestamp()'if action=='repeat-revoke'else'NULL::timestamptz'
        add({'name':'ISSUER-'+action.upper(),'family':'ISSUER_GRANT_GUARD','role':'wa_context_issuer','operation':'REVOKED_GRANT_UPDATE','table':'platform.database_action_grant','verb':'UPDATE','diagnostic':immutable,'source_case_id':'P0C-PRIV-01','assertion_id':'control.issuer_ceiling','actual_revoked_own_grant_required':True},'BEGIN;\nUPDATE platform.database_action_grant SET revoked_at='+value+" WHERE id='__WA_OWN_GRANT_ID__'::uuid RETURNING 1;\nROLLBACK;\n")
    bind={'kind':'BIND_CURRENTNESS',**body_contract(application,'bind_request_context','invalid, stale or unsupported context')}
    source_inputs=(set(plan['source_files_sha256'])-{HISTORICAL_PROGRESS})|set(native['source_inputs_sha256'])|{PLAN,NATIVE,NATIVE_COORDINATOR,CTX,PROTOCOL,'scripts/prepare-privilege-ceiling-control-rehearsal-v9.py','scripts/sql-review/collect_native_catalog.sql','scripts/sql-review/run-first-rehearsal.py','scripts/sql-review/run-local-f0-migrate.py','scripts/sql-review/rehearsal-diagnostics.py','scripts/prepare-local-f0-history.py','review-output/first-rehearsal/diagnostic-identifiers.json'}|{'review-output/native-table-denials-v2/'+name for name in native['files_sha256']}
    source_map={name:sha(source(root,name))for name in sorted(source_inputs)}
    definitions=[{'case_id':row['case_id'],'assertion_id':row['assertion_id'],'expected_assertion':row['expected_assertion'],'expected_assertion_sha256':row['expected_assertion_sha256'],'status':'NOT_RUN','maximum':row['planned_maximum']}for row in plan['exact5_control_claims']]
    fixtures={'schema':P.SCHEMA,'status':'NOT_RUN','database_posture':'D','database_contacted':False,'sql_executed':False,'approved_plan_sha256':PLAN_SHA,'source_files_sha256':source_map,'native_source_packet_sha256':NATIVE_SHA,'native_83_unchanged':True,'source_definers':plan['helper_and_definer_contract']['source_metadata'],'control_links':definitions,'issuer_umbrella_links':[{k:row[k]for k in('case_id','assertion_id','model','planned_maximum')}for row in plan['exact40_issuer_umbrella_map']],'finite_counts':{'issuer_business':117,'runtime_escalation':34,'provider_reachability':18,'source_definers':16,'private_Identity_native_ceilings':4,'immutable_column_ceilings':20,'helper_calls':4,'immutable_guard_cases':2,'prepared_negative_cases':len(cases)},'cases':cases,'positive_protocol':['SOURCE_NATIVE_205_SETUP_AND_40_ROLLBACK_VALIDITY_CONTROLS_ONLY_NO_NATIVE960_REPLAY','ACTUAL_ISSUER_INSERT_OWN_SELECT_SEPARATE_COMMIT','SAME_APP_PID_XID_BIND_AND_SCALAR_RESULT_TWO_CALLER_PATHS','CLOSE_APP_BEFORE_REVOKE_EXCLUSIVE_LOCK','20_FORBIDDEN_COLUMN_UPDATES_OF_EXISTING_OWN_GRANT','ACTUAL_ONE_WAY_REVOKE_AND_COMPLETE_STATE','REPEAT_AND_UNREVOKE_SOURCE_GUARD','ACTUAL_WORKER_SERVICE_GRANT_WITH_KNOWN_REVOKED_IDENTITY_CANNOT_SELF_ATTEST'],'person_grant':{'principal_user_id':baseline['app.user_security_profiles']['user_id'],'security_generation':baseline['app.user_security_profiles']['security_generation'],'database_login_role':'wa_app_runtime','owner_module_id':'customer_buyer_profile','action':'SH-004.v1','purpose':'resolve','target_kind':'CustomerProfile','target_id':baseline['app.customer_profiles']['id'],'source_generation':baseline['app.customer_profiles']['revision'],'policy_version':'privilege-ceiling-fixture.v1','allowed_fields':['CustomerProfile/'+baseline['app.customer_profiles']['id']+'/SELECT/id']},'revoked_service_fixture':baseline['platform_private.identity_service_authorization'],'bind_currentness_diagnostic':bind,'grant_columns':list(P.GRANT_COLUMNS),'grant_column_types':{name:expected['tables']['platform.database_action_grant']['columns'][name]['type']for name in P.GRANT_COLUMNS},'native_guard_restoration':'Exact100 trigger/function/state/body set; source205 full fingerprint excluding only enumerated new grant UUIDs; independent full native/oracle/ledger PASS prerequisite','maximum_claims':'All source results remain prepared subsets. Grant business-write umbrella unresolved; helper NOLOGIN startup/body confidentiality/shadow-object isolation/hosted parity/whole94/451 not claimed.','prepared_files_sha256':{name:sha(raw)for name,raw in sorted(artifacts.items())},'packet_digest_recipe':'SHA256(canonical JSON of source_files_sha256 and prepared_files_sha256; sorted keys, compact separators)'}
    fixtures['finite_counts']['immutable_guard_cases']=3
    fixtures['source_only_packet_sha256']=P.digest({key:fixtures[key]for key in('source_files_sha256','prepared_files_sha256')})
    fixtures['historical_progress_context']={'path':HISTORICAL_PROGRESS,'approved_plan_historical_sha256':plan['source_files_sha256'][HISTORICAL_PROGRESS],'runtime_input':False,'status_or_permission_authority':False}
    fixtures['fixed_execution_phases']=['FRESH_NATIVE_AND_ORACLE_LEDGER_ATTESTATION','EXACT_NATIVE205_SETUP_AND40_ROLLBACK_VALIDITY_CONTROLS','FRESH_PERSON_ISSUER_OWN_READ_COMMIT_AND_SAME_APP_BIND','ISSUER_COLUMN_CEILING','ISSUER_UNREVOKED_GUARD','ACTUAL_FIRST_REVOKE','ISSUER_GRANT_GUARD','RUNTIME_ESCALATION','HELPER_RESULT_CEILING','ISSUER_IDENTITY_SOURCE_CEILING','LEGITIMATE_WORKER_SERVICE_GRANT_REVOKED_CURRENTNESS_DENIAL','ISSUER_BUSINESS_DML','PROVIDER_REACHABILITY','FINAL_FULL_NATIVE_AND_COMPLETE_SOURCE_STATE']
    fixtures['finite_lifetimes']={'grant_seconds_max':300,'held_application_sessions_max':1,'declared_new_grants_max':2,'issuer_COMMIT_before_actual_restricted_bind':True,'no_unbounded_polling_or_worker_loop':True,'no_raw_grant_values_or_handles_exported':True}
    artifacts['fixtures.json']=encoded(fixtures)
    artifacts['README.md']=('Prepared finite privilege SQL only; every runtime outcome remains NOT_RUN.\n117 issuer +34 runtime +18 provider +4 private object gates +20 forbidden grant columns +4 helper calls +3 source immutable guards.\nAll100 guards and Native205 facts must be independently observed before/after; no Native960 replay, permission repair or case promotion.\nPrivate INSERT cases establish only their earlier native permission gate, never deeper business/constraint validity.\n').encode()
    return artifacts,fixtures


def main(argv=None):
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--write-source-only-packet',action='store_true');parser.add_argument('--check-reproduction',action='store_true');args=parser.parse_args(argv)
    P.require(args.write_source_only_packet!=args.check_reproduction,'EXACT_SOURCE_ACTION_REQUIRED');files,packet=generate(ROOT);directory=ROOT/OUTPUT
    if args.write_source_only_packet:
        directory.mkdir(exist_ok=False)
        for name,raw in files.items():
            with(directory/name).open('xb')as stream:stream.write(raw)
    else:P.require(directory.is_dir()and{p.name:p.read_bytes()for p in directory.iterdir()if p.is_file()}==files,'BYTE_REPRODUCTION_REQUIRED')
    print(json.dumps({'status':'SOURCE_PREPARED_NOT_RUN','files':len(files),'cases':len(packet['cases']),'packet_sha256':packet['source_only_packet_sha256'],'sql_files':sum(name.endswith('.sql')for name in files)}))


if __name__=='__main__':main()
