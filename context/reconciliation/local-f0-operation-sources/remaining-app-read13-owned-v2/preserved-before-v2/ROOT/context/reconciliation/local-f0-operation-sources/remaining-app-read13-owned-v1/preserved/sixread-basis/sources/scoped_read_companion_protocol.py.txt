"""Pure verdicts for six registered SH003 read criteria; runtime remains NOT_RUN."""
import hashlib
from copy import deepcopy
import json
import re

APPLICATION_SHA = '5ae39abf991f9c189e367eb6ab6968b0ad50836bf4220ac27ef8c18306ac26ad'
PLAN_SHA = 'e47149f77d615d5af15f8436a3a1640645962f4cb1bbec3c901da1ad1e8137ed'
SPECS = (('AgeGateAttempt',36),('AgeGateBlock',56),('AccessAuditLog',75),('UserRole',108),('AuditEvent',167),('AuthProviderAccount',200))
REVISION_MODELS = {'UserRole','AuthProviderAccount','User','UserSecurityProfile'}
FIXTURE_TABLES = ('app.users','app.user_security_profiles','app.age_gate_attempts','app.age_gate_blocks','app.access_audit_logs','app.user_roles','app.audit_events','app.auth_provider_accounts')

class HeldFailure(Exception):
    def __init__(self,code): self.code=code; super().__init__(code)

def need(value,code):
    if not value: raise HeldFailure(code)
def canonical(value): return json.dumps(value,sort_keys=True,separators=(',',':'),ensure_ascii=False,allow_nan=False)
def sha(value): return hashlib.sha256(value).hexdigest()
def digest(value): return sha(canonical(value).encode())
def quote(value): return "'"+str(value).replace("'","''")+"'"
def exact(actual,expected,code): need(canonical(actual)==canonical(expected),code)
def unique_json(raw):
    def pairs(items):
        value={}
        for key,item in items: need(key not in value,'DUPLICATE_RESPONSE_FIELD'); value[key]=item
        return value
    try: return json.loads(raw,object_pairs_hook=pairs,parse_constant=lambda _: (_ for _ in ()).throw(HeldFailure('NONFINITE_RESPONSE')))
    except HeldFailure: raise
    except BaseException: raise HeldFailure('MALFORMED_RESPONSE') from None

def marker(name,position):
    need(type(name) is str and re.fullmatch('[a-z][A-Za-z0-9-]{0,100}',name) and position in ('BEFORE','AFTER','BIND'),'FIXED_CASE_MARKER')
    return 'WA_SRC_'+position+'_'+name.upper().replace('-','_')

def operation_sql(name,body):
    return 'SELECT '+quote(marker(name,'BEFORE'))+';\n'+body.rstrip()+'\nSELECT '+quote(marker(name,'AFTER'))+';\nCOMMIT;\n'

def restoration_identity(baseline,actual):
    """Permit only the eight original owner_commit O/D flags to differ."""
    need(type(baseline) is dict and type(actual) is dict,'RESTORATION_NATIVE_SHAPE')
    wanted={(table,'owner_commit') for table in FIXTURE_TABLES}
    def selected(document):
        rows=document.get('triggers');need(type(rows) is list and all(type(row) is dict for row in rows),'RESTORATION_TRIGGER_SHAPE')
        found=[row for row in rows if (row.get('table_name'),row.get('name')) in wanted]
        need(len(found)==8 and {(row.get('table_name'),row.get('name')) for row in found}==wanted,'RESTORATION_EXACT_EIGHT_IDENTITIES')
        return found
    original=selected(baseline);need(all(row.get('enabled')=='O' and row.get('internal') is False for row in original),'RESTORATION_ORIGINAL_OWNER_CONTRACT')
    normalized=deepcopy(actual);observed=selected(normalized)
    need(all(row.get('enabled') in ('O','D') and row.get('internal') is False for row in observed),'RESTORATION_ONLY_OWNER_O_OR_D')
    disabled=sum(row['enabled']=='D' for row in observed)
    for row in observed:row['enabled']='O'
    exact(normalized,baseline,'RESTORATION_FULL_NATIVE_IDENTITY_DRIFT')
    return {'full_native_identity_match_except_declared_enable_flags':True,'declared_owner_triggers':8,'disabled_owner_triggers':disabled}

def binder_diagnostic(stderr,application):
    need(type(stderr) is str and sha(application.encode())==APPLICATION_SHA,'DIAGNOSTIC_SOURCE_REQUIRED')
    bodies=list(re.finditer(r'CREATE FUNCTION platform_private\.bind_request_context\(secret text\).*?AS\s+(\$[a-z_0-9]*\$)(.*?)\1;',application,re.S))
    need(len(bodies)==1,'BINDER_SOURCE_BODY_REQUIRED'); body=bodies[0][2]
    message='invalid, stale or unsupported context'
    lines=[i for i,line in enumerate(body.split('\n'),1) if 'RAISE EXCEPTION '+quote(message) in line]
    need(len(lines)==1,'BINDER_SOURCE_LINE_REQUIRED')
    text=stderr.replace('\r\n','\n').rstrip('\n').split('\n')
    patterns=[r'(?:psql:(?:<stdin>|-):[0-9]+: )?ERROR:[ \t]+42501:[ \t]+'+re.escape(message),r'CONTEXT:[ \t]+PL/pgSQL function platform_private\.bind_request_context\(text\) line '+str(lines[0])+r' at RAISE',r'LOCATION:[ \t]+exec_stmt_raise, pl_exec\.c:[1-9][0-9]{0,5}']
    good=len(text)==3 and all(re.fullmatch(pattern,line) is not None for pattern,line in zip(patterns,text))
    return {'matched':bool(good),'sqlstate':'42501' if good else None,'classification':'EXACT_PRINCIPAL_CURRENTNESS_BINDER_GUARD' if good else 'UNLISTED_DISCARDED','source_body_sha256':sha(body.encode()) if good else None,'source_body_line':lines[0] if good else None,'native_location':'exec_stmt_raise@pl_exec.c' if good else None}

def verdict(case,code,rows,ack,stderr,application):
    need(type(code) is int and type(rows) is list and all(type(x) is str for x in rows) and type(ack) is bool and type(stderr) is str,'TYPED_OPERATION_RESULT')
    if case['kind']=='binder-denial':
        proof=binder_diagnostic(stderr,application)
        need(code==3 and rows==[] and ack is False and proof['matched'],'INTENDED_BINDER_GUARD_REQUIRED')
        return {'status':'PASS_FINITE_SCOPED_READ_ONLY','diagnostic':proof,'query_stage_reached':False,'counts':None}
    need(code==0 and ack is True and stderr=='' and len(rows)==3 and rows[0]==marker(case['name'],'BEFORE') and rows[2]==marker(case['name'],'AFTER'),'READ_TERMINAL_MARKERS')
    actual=unique_json(rows[1]); need(type(actual) is dict and all(type(x) is int and x>=0 for x in actual.values()),'TYPED_NONNEGATIVE_COUNTS')
    exact(actual,case['expected'],'EXACT_READ_COUNTS_REQUIRED')
    return {'status':'PASS_FINITE_SCOPED_READ_ONLY','diagnostic':None,'query_stage_reached':True,'counts':actual,'stage_markers':{'before':True,'after':True}}
