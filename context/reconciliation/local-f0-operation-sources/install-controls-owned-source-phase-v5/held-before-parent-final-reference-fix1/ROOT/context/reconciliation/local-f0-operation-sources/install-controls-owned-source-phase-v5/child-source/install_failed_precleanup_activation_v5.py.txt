"""Pure, bounded receipt contracts for one failed-install/precleanup phase.

No process, filesystem, credentials, SQL execution or permission change occurs
here. The original install_control_protocol_v2.ActivationGate stays unchanged.
"""
import json
import re
import uuid

PHASE='POST_FAILED_DEPLOY_PRE_ORIGINAL_GRANTOR_FINALIZATION'
RUNTIME=('wa_context_issuer','wa_identity_service_authority','wa_app_runtime','wa_worker')
VARIANTS={
 'division_failure':('dd088298a5ffc9b42543c249fd433d7de1d22cabcc9ec108f928737c346b8c5c','22012','division_22012','function_42501'),
 'late_function_grant':('bb41107428c6a2868abe402c28d14554cfb073113f5687f806b395366189a61f','42501','function_42501','division_22012'),
}
FIELDS=('run_id','source_commit','source_tree','packet_sha256','variant','container_id','source_sql_sha256')
KINDS=('CLOSED_FAILED_DEPLOY_VERIFIED','GATE_PREREQUISITES','GATE_REFUSED','NULL_VERIFIERS',*('STARTUP_REJECTED_'+r for r in RUNTIME),'TEMPORARY_AUTHORITY','COMPLETE')
CLOSURES=('FAILED_DEPLOY_RETURNED','PRE_DIAGNOSTIC','POST_DIAGNOSTIC','PRE_NULL_VERIFIERS','POST_NULL_VERIFIERS',*(x+'_'+r for r in RUNTIME for x in('PRE_STARTUP','POST_STARTUP')),'PRE_AUTHORITY','POST_AUTHORITY')
CLOSURE_PROOF={'scope':'ALL_DATABASES_ALL_ROLES_ALL_APPLICATION_NAMES','observation_completed':True,'all_other_clients_absent':True}
INACTIVE={'runtime_roles':4,'all_null_verifiers':True,'flags_exact':True}
AUTHORITY={'temporary_memberships':3,'exact_temporary_options':True,'leaf_create':False,'permanent_migrator_edge':True}
FALSE_GATE={'install_closed_success':False,'original_cleanup_verified':False,'activated':False}
CODES=frozenset((
 'INSTALL_PHASE_IDENTITY','INSTALL_PHASE_GENUINE_CLOSED_FAILURE','INSTALL_PHASE_EXACT_PRIMARY_DIAGNOSTIC',
 'INSTALL_PHASE_GATE_STATE','INSTALL_PHASE_EXPECTED_GATE_REFUSAL','INSTALL_PHASE_RUNTIME_NOT_INACTIVE',
 'INSTALL_PHASE_AUTHORITY_NOT_PRESERVED','INSTALL_PHASE_RECEIPT_SHAPE','INSTALL_PHASE_RECEIPT_ORDER',
 'INSTALL_PHASE_CLOSURE_SHAPE','INSTALL_PHASE_CLOSURE_ORDER','INSTALL_PHASE_INCOMPLETE',
 'INSTALL_PHASE_ALREADY_PRESENT','INSTALL_PHASE_OBSERVATION_UNCONFIRMED','INSTALL_PHASE_UNEXPECTED_RESPONSE',
 'INSTALL_PHASE_PROCESS_TIMEOUT','INSTALL_EVIDENCE_WRITE_FAILED','INSTALL_FINALLY_FINALIZATION_OR_CLOSURE_UNCONFIRMED',
 'OTHER_CLIENT_BACKENDS_OR_UNCONFIRMED_OBSERVATION','ACTUAL_REJECTED_STARTUP_REQUIRED',
 'INSTALL_LOG_SCHEMA','INSTALL_LOG_COUNTS','INSTALL_LOG_CHANNEL_UNPROVEN','INSTALL_LOG_LIMIT','INSTALL_LOG_CONTROLS',
))

class Held(Exception):
    def __init__(self,code):self.code=code;super().__init__(code)

def need(value,code):
    if not value:raise Held(code)

def canonical(value):return json.dumps(value,sort_keys=True,separators=(',',':'),allow_nan=False)
def exact(value,wanted,code):need(canonical(value)==canonical(wanted),code)

def identity(value):
    need(type(value)is dict and set(value)==set(FIELDS),'INSTALL_PHASE_IDENTITY')
    need(all(type(value[k])is str for k in FIELDS),'INSTALL_PHASE_IDENTITY')
    need(value['variant']in VARIANTS and value['source_sql_sha256']==VARIANTS[value['variant']][0],'INSTALL_PHASE_IDENTITY')
    try:run=uuid.UUID(value['run_id'])
    except (ValueError,AttributeError):raise Held('INSTALL_PHASE_IDENTITY')from None
    need(str(run)==value['run_id']and run.version==4,'INSTALL_PHASE_IDENTITY')
    need(all(re.fullmatch('[0-9a-f]{40}',value[k])for k in('source_commit','source_tree'))and all(re.fullmatch('[0-9a-f]{64}',value[k])for k in('packet_sha256','container_id')),'INSTALL_PHASE_IDENTITY')
    return {k:value[k]for k in FIELDS}

def failed_prefix(cli,before,after,expected,protocol):
    """Only source-verified genuine closed failure can enter this phase."""
    expected=identity(expected);variant=expected['variant'];sql,state,field,foreign=VARIANTS[variant]
    need(type(cli)is dict and cli.get('schema')=='workinants.local-f0-migrate-result.v2'and cli.get('operation')=='deploy'and cli.get('status')in('CLI_FAILED_STOP_AND_INSPECT','CLI_OUTPUT_REJECTED_STOP_AND_INSPECT')and type(cli.get('exit_code'))is int and 1<=cli['exit_code']<=255,'INSTALL_PHASE_GENUINE_CLOSED_FAILURE')
    exact({k:cli.get(k)for k in('run_id','container_id','source_sql_sha256')},{k:expected[k]for k in('run_id','container_id','source_sql_sha256')},'INSTALL_PHASE_GENUINE_CLOSED_FAILURE')
    need(type(cli.get('attestation_sha256'))is str and re.fullmatch('[0-9a-f]{64}',cli['attestation_sha256'])and cli.get('raw_output_discarded')is True and cli.get('database_qualification_claimed')is False,'INSTALL_PHASE_GENUINE_CLOSED_FAILURE')
    change=protocol['delta'](before,after)
    need(change[field]==1 and change[foreign]==change['other_migrator_error']==change['malformed']==change['forbidden_body']==0 and change['registered']==1+change['secondary_25p02'],'INSTALL_PHASE_EXACT_PRIMARY_DIAGNOSTIC')
    return {'cli_attestation_sha256':cli['attestation_sha256'],'cli_exit_code':cli['exit_code'],'cli_status':cli['status'],'intended_primary_sqlstate':state,'diagnostic_delta':dict(change),'all_operation_backends_absent':True,'closed_process_result_observed':True}

def gate_state(gate):
    result={k:getattr(gate,k,None)for k in FALSE_GATE}
    exact(result,FALSE_GATE,'INSTALL_PHASE_GATE_STATE');return result

def safe_code(error):
    code=getattr(error,'code',None)
    return code if type(code)is str and code in CODES else 'INSTALL_PHASE_PROCESS_TIMEOUT'if type(error).__name__=='TimeoutExpired'else 'INSTALL_PHASE_UNEXPECTED_RESPONSE'

def validate_receipts(rows,expected,complete=False):
    expected=identity(expected)
    need(type(rows)is list and len(rows)<=len(KINDS),'INSTALL_PHASE_RECEIPT_SHAPE')
    for index,row in enumerate(rows):
        need(type(row)is dict and set(row)=={'phase','sequence','identity','kind','facts'}and row['phase']==PHASE and type(row['sequence'])is int and row['sequence']==index,'INSTALL_PHASE_RECEIPT_SHAPE')
        exact(row['identity'],expected,'INSTALL_PHASE_IDENTITY');need(row['kind']==KINDS[index],'INSTALL_PHASE_RECEIPT_ORDER');facts=row['facts']
        if index==0:
            need(type(facts)is dict and set(facts)=={'cli_attestation_sha256','cli_exit_code','cli_status','intended_primary_sqlstate','diagnostic_delta','all_operation_backends_absent','closed_process_result_observed'}and type(facts['cli_attestation_sha256'])is str and re.fullmatch('[0-9a-f]{64}',facts['cli_attestation_sha256'])and type(facts['cli_exit_code'])is int and 1<=facts['cli_exit_code']<=255 and facts['cli_status']in('CLI_FAILED_STOP_AND_INSPECT','CLI_OUTPUT_REJECTED_STOP_AND_INSPECT')and facts['intended_primary_sqlstate']==VARIANTS[expected['variant']][1]and facts['all_operation_backends_absent']is True and facts['closed_process_result_observed']is True,'INSTALL_PHASE_GENUINE_CLOSED_FAILURE')
            change=facts['diagnostic_delta'];fields={'registered','division_22012','function_42501','secondary_25p02','other_migrator_error','malformed','forbidden_body'}
            need(type(change)is dict and set(change)==fields and all(type(v)is int and 0<=v<=65536 for v in change.values()),'INSTALL_PHASE_EXACT_PRIMARY_DIAGNOSTIC')
            _,_,field,foreign=VARIANTS[expected['variant']]
            need(change[field]==1 and change[foreign]==change['other_migrator_error']==change['malformed']==change['forbidden_body']==0 and change['registered']==1+change['secondary_25p02'],'INSTALL_PHASE_EXACT_PRIMARY_DIAGNOSTIC')
        elif index==1:exact(facts,FALSE_GATE,'INSTALL_PHASE_GATE_STATE')
        elif index==2:exact(facts,{'outcome':'REFUSED','refusal_code':'INSTALL_RUNTIME_ACTIVATION_HELD','database_password_sql_executed':False},'INSTALL_PHASE_EXPECTED_GATE_REFUSAL')
        elif index==3:exact(facts,INACTIVE,'INSTALL_PHASE_RUNTIME_NOT_INACTIVE')
        elif 4<=index<=7:exact(facts,{'role':RUNTIME[index-4],'candidate_startup':'PASS_REJECTED_INACTIVE','exit_code':2,'operation_connection_closed':True},'INSTALL_PHASE_RUNTIME_NOT_INACTIVE')
        elif index==8:exact(facts,AUTHORITY,'INSTALL_PHASE_AUTHORITY_NOT_PRESERVED')
        else:exact(facts,{'observations_complete':True,'original_finalization_not_yet_run':True,'database_password_sql_executed':False,'gate_state':FALSE_GATE},'INSTALL_PHASE_INCOMPLETE')
    if complete:need(len(rows)==len(KINDS),'INSTALL_PHASE_INCOMPLETE')
    return True

def validate_closures(rows,complete=False):
    need(type(rows)is list and len(rows)<=len(CLOSURES),'INSTALL_PHASE_CLOSURE_SHAPE')
    for index,row in enumerate(rows):
        need(type(row)is dict and set(row)=={'phase','sequence','stage','proof'}and row['phase']==PHASE and type(row['sequence'])is int and row['sequence']==index,'INSTALL_PHASE_CLOSURE_SHAPE')
        need(row['stage']==CLOSURES[index],'INSTALL_PHASE_CLOSURE_ORDER');exact(row['proof'],CLOSURE_PROOF,'INSTALL_PHASE_CLOSURE_SHAPE')
    if complete:need(len(rows)==len(CLOSURES),'INSTALL_PHASE_INCOMPLETE')
    return True
