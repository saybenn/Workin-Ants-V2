"""Pure INSTALL test derivation, bounded diagnostics and activation/review gates.

No filesystem, process, clock or database operation occurs here. Existing
canonical migration and historical 42501 diagnostics retain their exact meaning.
"""
import hashlib
import json
import re
import unicodedata

CANONICAL='5ae39abf991f9c189e367eb6ab6968b0ad50836bf4220ac27ef8c18306ac26ad'
VARIANTS=('canonical','division_failure','late_function_grant')
LOGIN_ROLES=('postgres','wa_migrator','wa_context_issuer','wa_identity_service_authority','wa_app_runtime','wa_worker')
RUNTIME_ROLES=LOGIN_ROLES[2:]
MEMBERS=('wa_private_helper_owner','wa_customer_verifier','wa_track_verifier')
MIGRATION='20261117000100_f0_local_initial'
GRANT=b'GRANT EXECUTE ON FUNCTION platform_private.bind_request_context(text) TO wa_app_runtime,wa_worker;\n\n'
TRANSFER=b'ALTER FUNCTION platform_private.bind_request_context(text) OWNER TO wa_private_helper_owner;\n\n'
PRIMARY={'division_failure':('22012','division by zero'),'late_function_grant':('42501','permission denied for function bind_request_context')}
ABORTED='current transaction is aborted, commands ignored until end of transaction block'
COUNT_FIELDS=('registered','division_22012','function_42501','secondary_25p02','other_migrator_error','malformed','forbidden_body')
class Held(Exception):
    def __init__(self,code):self.code=code;super().__init__(code)
def need(value,code):
    if not value:raise Held(code)
def sha(raw):return hashlib.sha256(raw).hexdigest()
def canonical(value):return json.dumps(value,sort_keys=True,separators=(',',':'),allow_nan=False)
def exact(actual,wanted,code):need(canonical(actual)==canonical(wanted),code)
def derive(source,variant):
    need(type(source) is bytes and sha(source)==CANONICAL and variant in VARIANTS,'CANONICAL_VARIANT_SOURCE_REQUIRED')
    need(source.endswith(b'RESET ROLE;\nCOMMIT;\n') and source.count(GRANT)==source.count(TRANSFER)==1,'EXACT_AUTHORITY_LAYOUT_REQUIRED')
    if variant=='canonical':return source
    if variant=='division_failure':return source[:-len(b'RESET ROLE;\nCOMMIT;\n')]+b'SELECT 1/0;\nRESET ROLE;\nCOMMIT;\n'
    # Remove one exact existing grant and move the same bytes after ownership
    # transfer. No other SQL byte, role, policy or permission is added/changed.
    return source.replace(GRANT,b'',1).replace(TRANSFER,TRANSFER+GRANT,1)
def summarize_server(stdout,stderr):
    need(type(stdout) is str and type(stderr) is str and len(stdout.encode('utf8',errors='replace'))+len(stderr.encode('utf8',errors='replace'))<=2*1024*1024,'INSTALL_LOG_LIMIT')
    counts=dict.fromkeys(COUNT_FIELDS,0)
    for stream in (stdout,stderr):
        stream=stream.replace('\r\n','\n');need(not any(unicodedata.category(c) in ('Cc','Cf','Cs') and c not in '\n\t' or c=='\ufffd' for c in stream),'INSTALL_LOG_CONTROLS')
        lines=stream.split('\n');need(len(lines)<=65536,'INSTALL_LOG_LIMIT')
        for line in lines:
            if not line.startswith('WA_F0_DIAG|'):continue
            counts['registered']+=1;parts=line.split('|',4)
            if len(parts)!=5 or not re.fullmatch('[0-9A-Z]{5}',parts[1]):counts['malformed']+=1;continue
            _,state,role,database,body=parts
            if re.match(r'^(?:DETAIL|HINT|QUERY|CONTEXT|STATEMENT|LOCATION|BACKTRACE):',body):counts['forbidden_body']+=1;continue
            if role!='wa_migrator' or database!='wa_p0c_rehearsal' or not re.match(r'^(?:ERROR|FATAL|PANIC):',body):continue
            suffix=r'(?: at character [1-9][0-9]{0,7})?'
            if state=='22012' and re.fullmatch('ERROR:  division by zero'+suffix,body):counts['division_22012']+=1
            elif state=='42501' and re.fullmatch('ERROR:  permission denied for function bind_request_context'+suffix,body):counts['function_42501']+=1
            elif state=='25P02' and re.fullmatch('ERROR:  '+re.escape(ABORTED)+suffix,body):counts['secondary_25p02']+=1
            else:counts['other_migrator_error']+=1
    return {'schema':'workinants.install-server-counts.v1','counts':counts,'raw_output_discarded':True}
def counts(value):
    need(type(value) is dict and set(value)=={'schema','counts','raw_output_discarded'} and value['schema']=='workinants.install-server-counts.v1' and value['raw_output_discarded'] is True,'INSTALL_LOG_SCHEMA')
    row=value['counts'];need(type(row) is dict and set(row)==set(COUNT_FIELDS) and all(type(v) is int and 0<=v<=65536 for v in row.values()) and sum(v for k,v in row.items() if k!='registered')<=row['registered'],'INSTALL_LOG_COUNTS');return row
def delta(before,after):
    old,new=counts(before),counts(after);need(old['registered']>0 and all(new[k]>=old[k] for k in COUNT_FIELDS) and old['malformed']==old['forbidden_body']==new['malformed']==new['forbidden_body']==0,'INSTALL_LOG_CHANNEL_UNPROVEN')
    return {k:new[k]-old[k] for k in COUNT_FIELDS}
def inventory_shape(value):
    need(type(value) is dict and set(value)=={'relations','functions','types','enums','other_clients'} and all(type(v) is int and v>=0 for v in value.values()),'INSTALL_INVENTORY_SHAPE')
    return value

def validate_inventory(value,empty):
    inventory_shape(value)
    if empty:exact(value,dict.fromkeys(value,0),'INSTALL_TRANSACTION_NOT_ROLLED_BACK')
    # Includes all pg_class objects: 42 tables plus 146 indexes. A rollback
    # must leave zero relations of every kind, rather than checking tables only.
    else:exact(value,{'relations':188,'functions':147,'types':142,'enums':29,'other_clients':0},'INSTALL_CANONICAL_OBJECT_COUNTS')
def failure_verdict(variant,cli,inventory,ledger,before,after,source_sha):
    need(variant in PRIMARY and type(cli) is dict and cli.get('schema')=='workinants.local-f0-migrate-result.v2' and cli.get('operation')=='deploy' and cli.get('status') in ('CLI_FAILED_STOP_AND_INSPECT','CLI_OUTPUT_REJECTED_STOP_AND_INSPECT') and type(cli.get('exit_code')) is int and 1<=cli['exit_code']<=255 and cli.get('source_sql_sha256')==source_sha,'INSTALL_GENUINE_CLOSED_FAILURE_REQUIRED')
    validate_inventory(inventory,True);change=delta(before,after);field='division_22012' if variant=='division_failure' else 'function_42501';foreign='function_42501' if variant=='division_failure' else 'division_22012'
    need(change[field]==1 and change[foreign]==change['other_migrator_error']==change['malformed']==change['forbidden_body']==0,'INSTALL_EXACT_SERVER_FAILURE_REQUIRED')
    need(type(ledger) is dict and set(ledger)=={'rows','ids_unique'} and ledger['ids_unique'] is True and type(ledger['rows']) is list and len(ledger['rows'])==1,'INSTALL_FAILED_LEDGER_SHAPE')
    row=ledger['rows'][0];need(type(row) is dict and set(row)=={'name_sha256','checksum_sha256','finished','rolled_back','steps','logs_state','immutable_sha256'} and row['name_sha256']==sha(MIGRATION.encode()) and row['checksum_sha256']==sha(source_sha.encode()) and row['finished'] is False and row['rolled_back'] is False and type(row['steps']) is int and row['steps']==0 and row['logs_state'] in ('NULL','EMPTY','NONEMPTY') and type(row['immutable_sha256']) is str and re.fullmatch('[0-9a-f]{64}',row['immutable_sha256']),'INSTALL_FAILED_LEDGER_IDENTITY')
    if change['secondary_25p02']:
        need(row['logs_state']=='NULL','INSTALL_MASKED_LOG_STATE_UNPROVEN');classification='SERVER_PRIMARY_WITH_SECONDARY_25P02_NULL_LOGS'
    else:
        need(row['logs_state']=='NONEMPTY','INSTALL_FAILURE_RETENTION_UNPROVEN');classification='SERVER_PRIMARY_WITH_NONEMPTY_LOGS'
    return {'variant':variant,'primary_sqlstate':PRIMARY[variant][0],'classification':classification,'delta':change,'failed_row_immutable_sha256':row['immutable_sha256'],'P3018_claimed':cli.get('prisma_codes')==['P3018'],'actual_database_failure_observed':True,'rollback_observed':True,'recovery_approved':False}

def ledger_rows(value):
    need(type(value) is dict and set(value)=={'rows','ids_unique'} and value['ids_unique'] is True and type(value['rows']) is list and len(value['rows'])<=2,'INSTALL_LEDGER_SHAPE')
    fields={'name_sha256','checksum_sha256','finished','rolled_back','steps','logs_state','immutable_sha256'}
    for row in value['rows']:
        need(type(row) is dict and set(row)==fields and all(type(row[k]) is str and re.fullmatch('[0-9a-f]{64}',row[k]) for k in ('name_sha256','checksum_sha256','immutable_sha256')) and type(row['finished']) is bool and type(row['rolled_back']) is bool and type(row['steps']) is int and 0<=row['steps']<=1 and row['logs_state'] in ('NULL','EMPTY','NONEMPTY'),'INSTALL_LEDGER_ROW')
        need(row['name_sha256']==sha(MIGRATION.encode()),'INSTALL_LEDGER_NAME')
    return value['rows']

def applied_ledger(value,fault=None):
    rows=ledger_rows(value);good=[r for r in rows if r['checksum_sha256']==sha(CANONICAL.encode()) and r['finished'] is True and r['rolled_back'] is False and r['steps']==1 and r['logs_state']=='NULL']
    need(len(good)==1 and len(rows)==(2 if fault else 1),'INSTALL_APPLIED_LEDGER_REQUIRED')
    if fault:
        need(type(fault) is dict,'INSTALL_RETAINED_FAULT_REQUIRED');wanted=dict(fault,rolled_back=True)
        need(sum(canonical(r)==canonical(wanted) for r in rows)==1,'INSTALL_FAILED_HISTORY_CHANGED')
    return True

def resolved_ledger(value,fault):
    rows=ledger_rows(value);exact(rows,[dict(fault,rolled_back=True)],'INSTALL_STANDARD_RESOLVE_TRANSITION');return True

def completed(value,operation='deploy'):
    need(type(value) is dict and value.get('schema')=='workinants.local-f0-migrate-result.v2' and value.get('operation')==operation and value.get('status')=='CLI_COMPLETED_REQUIRES_INDEPENDENT_LEDGER_CATALOG_CHECKS' and type(value.get('exit_code')) is int and value['exit_code']==0,'INSTALL_CLI_COMPLETED_REQUIRED');return True
def wrong_finalizer_diagnostic(stderr,finalizer):
    need(type(stderr) is str and len(stderr)<=65536,'INSTALL_FINALIZER_DIAGNOSTIC_LIMIT')
    body=re.search(r'DO (\$cleanup\$)(.*?)\1;',finalizer,re.S);need(body is not None,'INSTALL_FINALIZER_SOURCE_BODY')
    locations=[i for i,line in enumerate(body[2].split('\n'),1) if "RAISE EXCEPTION 'cleanup requires original bootstrap grantor'" in line];need(len(locations)==1,'INSTALL_FINALIZER_SOURCE_RAISE')
    lines=stderr.replace('\r\n','\n').splitlines();header=re.compile(r'(?:psql:(?:<stdin>|-):[0-9]+: )?ERROR:\s+P0001:\s+cleanup requires original bootstrap grantor');frame=re.compile(r'(?:CONTEXT:\s+|\s*)PL/pgSQL function inline_code_block line '+str(locations[0])+r' at RAISE')
    good=sum(bool(header.fullmatch(line)) for line in lines)==sum(bool(frame.fullmatch(line)) for line in lines)==1 and all(not line or header.fullmatch(line) or frame.fullmatch(line) or re.fullmatch(r'LOCATION:\s+exec_stmt_raise, pl_exec\.c:[1-9][0-9]{0,5}',line) for line in lines)
    return {'matched':bool(good),'sqlstate':'P0001' if good else None,'source_body_sha256':sha(body[2].encode()) if good else None,'source_line':locations[0] if good else None,'raw_output_discarded':True}
class ActivationGate:
    def __init__(self):self.install_closed_success=False;self.original_cleanup_verified=False;self.activated=False
    def installed(self,success,closed):need(type(success) is bool and closed is True,'INSTALL_CLOSURE_REQUIRED');self.install_closed_success=success;self.original_cleanup_verified=False
    def cleaned(self,proof):
        exact(proof,{'original_grantor':'postgres','temporary_memberships':0,'leaf_create':False,'other_clients':0},'INSTALL_ORIGINAL_CLEANUP_REQUIRED');self.original_cleanup_verified=True
    def permit(self):need(self.install_closed_success and self.original_cleanup_verified and not self.activated,'INSTALL_RUNTIME_ACTIVATION_HELD');return True
    def activated_once(self):self.permit();self.activated=True
def require_recovery_review(proof,approval,identity):
    need(type(proof) is dict and type(approval) is dict and type(identity) is dict,'INSTALL_REVIEW_SHAPE')
    fields={'schema','decision','run_id','container_id','source_sql_sha256','proof_sha256','reviewer'};need(set(approval)==fields,'INSTALL_REVIEW_FIELDS')
    exact({k:approval[k] for k in ('schema','decision','run_id','container_id','source_sql_sha256')},{'schema':'workinants.install-independent-rollback-review.v1','decision':'APPROVED_STANDARD_RESOLVE_ROLLED_BACK','run_id':identity['run_id'],'container_id':identity['container_id'],'source_sql_sha256':identity['source_sql_sha256']},'INSTALL_REVIEW_IDENTITY')
    need(approval['proof_sha256']==sha((canonical(proof)+'\n').encode()) and type(approval['reviewer']) is str and approval['reviewer'] in ('/root/review_track_ports','/root/restricted_controls_operator','/root/catalog_v4_review'),'INSTALL_INDEPENDENT_PROOF_REVIEW_REQUIRED')
    return True
