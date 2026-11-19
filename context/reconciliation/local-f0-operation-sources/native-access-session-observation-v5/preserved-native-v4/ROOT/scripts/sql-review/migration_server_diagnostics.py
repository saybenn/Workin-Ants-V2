"""Bounded, dormant parser for one reviewed owned PostgreSQL error channel.

Never return raw lines, messages, SQL, credentials or connection handles. The
caller must bind this result to its created immutable container, source packet,
verified settings and before/after operation window. Importing runs no process.
"""
import re
import subprocess
import unicodedata
import uuid

PREFIX='WA_F0_DIAG|'
LOG_PREFIX=PREFIX+'%e|%u|%d|'
DATABASE='wa_p0c_rehearsal'
LOGIN='wa_migrator'
SCHEMA='workinants.local-f0-server-error-counts.v1'
FIELDS=('registered_lines','expected_set_role_42501','aborted_transaction_25p02','other_migrator_error','malformed_registered_line','forbidden_diagnostic_body')
SET_ROLE='must be able to SET ROLE "wa_customer_verifier"'
ABORTED='current transaction is aborted, commands ignored until end of transaction block'
MAX_BYTES=2*1024*1024
MAX_LINES=65536
IDENTITY_FIELDS={'run_id','container_id','source_commit','source_tree','packet_sha256','application_sql_sha256','module_sha256','migration_id'}
VERIFIED_FIELDS={'logging_settings_verified','original_grantor_finalized','operation_backends_absent'}
PROOF_FIELDS=IDENTITY_FIELDS|VERIFIED_FIELDS|{'schema','phase','provenance','classification','cli_closed_nonzero','application_object_count','failed_row_logs_state','before','after','delta','cli_status','cli_exit_code'}

class DiagnosticFailure(Exception):
    def __init__(self,code):self.code=code;super().__init__(code)

def need(value,code):
    if not value:raise DiagnosticFailure(code)

def summarize(stdout,stderr):
    need(type(stdout) is str and type(stderr) is str,'SERVER_DIAGNOSTIC_TEXT_REQUIRED')
    need(len(stdout.encode('utf8',errors='replace'))+len(stderr.encode('utf8',errors='replace'))<=MAX_BYTES,'SERVER_DIAGNOSTIC_LIMIT')
    counts=dict.fromkeys(FIELDS,0)
    for stream in (stdout,stderr):
        text=stream.replace('\r\n','\n')
        need(not any(unicodedata.category(c) in ('Cc','Cf','Cs') and c not in '\n\t' or c=='\ufffd' for c in text),'SERVER_DIAGNOSTIC_CONTROL_REJECTED')
        lines=text.split('\n');need(len(lines)<=MAX_LINES,'SERVER_DIAGNOSTIC_LIMIT')
        for line in lines:
            if not line.startswith(PREFIX):continue
            counts['registered_lines']+=1
            parts=line.split('|',4)
            if len(parts)!=5 or not re.fullmatch('[0-9A-Z]{5}',parts[1]):
                counts['malformed_registered_line']+=1;continue
            _,state,login,database,body=parts
            if re.match(r'^(?:DETAIL|HINT|QUERY|CONTEXT|STATEMENT|LOCATION|BACKTRACE):',body):
                counts['forbidden_diagnostic_body']+=1;continue
            if login!=LOGIN or database!=DATABASE or not re.match(r'^(?:ERROR|FATAL|PANIC):',body):continue
            suffix=r'(?: at character [1-9][0-9]{0,7})?'
            if state=='42501' and re.fullmatch(r'ERROR:  '+re.escape(SET_ROLE)+suffix,body):counts['expected_set_role_42501']+=1
            elif state=='25P02' and re.fullmatch(r'ERROR:  '+re.escape(ABORTED)+suffix,body):counts['aborted_transaction_25p02']+=1
            else:counts['other_migrator_error']+=1
    need(all(type(v) is int and 0<=v<=MAX_LINES for v in counts.values()),'SERVER_DIAGNOSTIC_LIMIT')
    return {'schema':SCHEMA,'counts':counts,'raw_output_discarded':True}

def validate_counts(value):
    need(type(value) is dict and set(value)=={'schema','counts','raw_output_discarded'} and value['schema']==SCHEMA and value['raw_output_discarded'] is True,'SERVER_DIAGNOSTIC_SCHEMA')
    counts=value['counts']
    need(type(counts) is dict and set(counts)==set(FIELDS) and all(type(v) is int and 0<=v<=MAX_LINES for v in counts.values()),'SERVER_DIAGNOSTIC_COUNTS')
    need(sum(v for k,v in counts.items() if k!='registered_lines')<=counts['registered_lines'],'SERVER_DIAGNOSTIC_COUNTS_INCONSISTENT')
    return counts

def difference(before,after):
    old=validate_counts(before);new=validate_counts(after)
    need(all(new[k]>=old[k] for k in FIELDS),'SERVER_DIAGNOSTIC_NONMONOTONIC')
    need(old['registered_lines']>0 and old['malformed_registered_line']==old['forbidden_diagnostic_body']==new['malformed_registered_line']==new['forbidden_diagnostic_body']==0,'SERVER_DIAGNOSTIC_CHANNEL_UNPROVEN')
    delta={key:new[key]-old[key] for key in FIELDS}
    validate_counts({'schema':SCHEMA,'counts':delta,'raw_output_discarded':True})
    return delta

def read_owned(container_id,process=subprocess.run):
    need(type(container_id) is str and re.fullmatch('[0-9a-f]{64}',container_id),'SERVER_DIAGNOSTIC_IMMUTABLE_ID_REQUIRED')
    try:
        result=process(['docker','--context','desktop-linux','logs',container_id],text=True,encoding='utf8',errors='strict',capture_output=True,timeout=30,shell=False)
    except Exception:raise DiagnosticFailure('SERVER_DIAGNOSTIC_READ_UNCONFIRMED') from None
    need(result.returncode==0,'SERVER_DIAGNOSTIC_READ_UNCONFIRMED')
    return summarize(result.stdout,result.stderr)

def classify_failure(cli,ledger,delta):
    validate_counts({'schema':SCHEMA,'counts':delta,'raw_output_discarded':True})
    need(cli['status'] in ('CLI_FAILED_STOP_AND_INSPECT','CLI_OUTPUT_REJECTED_STOP_AND_INSPECT') and type(cli['exit_code']) is int and 1<=cli['exit_code']<=255,'EXPECTED_CLOSED_CLI_FAILURE_NOT_PROVEN')
    need(delta['expected_set_role_42501']==1 and delta['other_migrator_error']==delta['malformed_registered_line']==delta['forbidden_diagnostic_body']==0,'SOURCE_GUARD_SERVER_DIAGNOSTIC_NOT_PROVEN')
    rows=ledger['rows']
    fields=('application_relations','application_functions','application_types','application_enums','active_migrators')
    need(len(rows)==1 and rows[0]['finished'] is False and rows[0]['rolled_back'] is False and type(rows[0]['steps']) is int and rows[0]['steps']==0 and all(type(ledger[k]) is int and ledger[k]==0 for k in fields),'FAILED_TRANSACTION_ROLLBACK_NOT_PROVEN')
    if delta['aborted_transaction_25p02']==0:
        need(cli['status']=='CLI_FAILED_STOP_AND_INSPECT' and cli['prisma_codes']==['P3018'] and cli['sqlstates']==['42501'] and rows[0]['logs_state']=='NONEMPTY' and rows[0]['expected_error_code'] is True and rows[0]['expected_set_role_error'] is True,'NORMAL_FAILURE_RETENTION_NOT_PROVEN')
        return 'NORMAL_P3018_PERSISTENCE'
    need(rows[0]['logs_state']=='NULL','MASKED_FAILURE_LOG_STATE_NOT_PROVEN')
    return 'SERVER_42501_WITH_SECONDARY_25P02_UNWRITTEN_FAILURE_LOGS'

def validate_identity(identity):
    need(type(identity) is dict and set(identity)==IDENTITY_FIELDS,'SERVER_PROOF_IDENTITY_FIELDS')
    for key in ('container_id','packet_sha256','application_sql_sha256','module_sha256'):
        need(type(identity[key]) is str and re.fullmatch('[0-9a-f]{64}',identity[key]),'SERVER_PROOF_IDENTITY_VALUE')
    for key in ('source_commit','source_tree'):
        need(type(identity[key]) is str and re.fullmatch('[0-9a-f]{40}',identity[key]),'SERVER_PROOF_IDENTITY_VALUE')
    try:run=uuid.UUID(identity['run_id'])
    except Exception:raise DiagnosticFailure('SERVER_PROOF_IDENTITY_VALUE') from None
    need(str(run)==identity['run_id'] and run.version==4 and identity['migration_id']=='20261117000100_f0_local_initial','SERVER_PROOF_IDENTITY_VALUE')
    return identity

def validate_proof(value,expected_identity=None):
    """Validate protocol/binding only; independent review proves observations."""
    need(type(value) is dict and set(value)==PROOF_FIELDS,'SERVER_PROOF_FIELDS')
    identity=validate_identity({key:value[key] for key in IDENTITY_FIELDS})
    if expected_identity is not None:
        validate_identity(expected_identity);need(identity==expected_identity,'SERVER_PROOF_IDENTITY_MISMATCH')
    need(value['schema']=='workinants.local-f0-server-error-proof.v1' and value['phase']=='EXPECTED_FAILED_PRISMA_DEPLOY' and value['provenance']=='OWNED_POSTGRES_TERSE_ERROR_LOG_DELTA','SERVER_PROOF_SOURCE')
    need(all(value[key] is True for key in VERIFIED_FIELDS|{'cli_closed_nonzero'}) and type(value['application_object_count']) is int and value['application_object_count']==0,'SERVER_PROOF_VERIFICATION')
    need(type(value['cli_exit_code']) is int and 1<=value['cli_exit_code']<=255 and value['cli_status'] in ('CLI_FAILED_STOP_AND_INSPECT','CLI_OUTPUT_REJECTED_STOP_AND_INSPECT'),'SERVER_PROOF_CLI_CLOSURE')
    delta=difference(value['before'],value['after']);validate_counts({'schema':SCHEMA,'counts':value['delta'],'raw_output_discarded':True})
    need(value['delta']==delta and delta['expected_set_role_42501']==1 and delta['other_migrator_error']==delta['malformed_registered_line']==delta['forbidden_diagnostic_body']==0,'SERVER_PROOF_GUARD')
    if value['classification']=='NORMAL_P3018_PERSISTENCE':
        need(delta['aborted_transaction_25p02']==0 and value['failed_row_logs_state']=='NONEMPTY' and value['cli_status']=='CLI_FAILED_STOP_AND_INSPECT','SERVER_PROOF_NORMAL_CLASSIFICATION')
    else:
        need(value['classification']=='SERVER_42501_WITH_SECONDARY_25P02_UNWRITTEN_FAILURE_LOGS' and delta['aborted_transaction_25p02']>=1 and value['failed_row_logs_state']=='NULL','SERVER_PROOF_MASK_CLASSIFICATION')
    return value

def build_proof(identity,cli,ledger,before,after,verified):
    validate_identity(identity)
    need(cli.get('schema')=='workinants.local-f0-migrate-result.v2' and cli.get('operation')=='deploy' and cli.get('run_id')==identity['run_id'] and cli.get('container_id')==identity['container_id'] and cli.get('source_sql_sha256')==identity['application_sql_sha256'],'SERVER_PROOF_CLI_IDENTITY')
    need(type(verified) is dict and set(verified)==VERIFIED_FIELDS and all(v is True for v in verified.values()),'SERVER_PROOF_VERIFICATION')
    rows=ledger['rows']
    need(len(rows)==1 and rows[0]['name']==identity['migration_id'] and rows[0]['checksum']==identity['application_sql_sha256'],'SERVER_PROOF_LEDGER_IDENTITY')
    delta=difference(before,after);classification=classify_failure(cli,ledger,delta)
    proof={**identity,**verified,'schema':'workinants.local-f0-server-error-proof.v1','phase':'EXPECTED_FAILED_PRISMA_DEPLOY','provenance':'OWNED_POSTGRES_TERSE_ERROR_LOG_DELTA','classification':classification,'cli_closed_nonzero':True,'application_object_count':0,'failed_row_logs_state':rows[0]['logs_state'],'before':before,'after':after,'delta':delta,'cli_status':cli['status'],'cli_exit_code':cli['exit_code']}
    return validate_proof(proof,identity)
