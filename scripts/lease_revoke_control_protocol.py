"""Pure finite lease/currentness SQL and verdicts. No process or clock access.

Owner policy and canonical SQL remain external source truth. This module emits
only fixed prepared operations; no duration/field/verb is accepted from a client.
"""
import hashlib
import json
import re
import uuid

CASE_ORDER=(
 'worker-claim','worker-renew','live-reclaim-denied','expired-renew-denied',
 'concurrent-reclaim-stale-holder','current-holder-renew','shorten-renew-denied',
 'copied-hash-renew-denied','old-secret-renew-denied','hash-change-denied',
 'attempt-only-denied','app-issuer-revocation','app-bound-before-rotate',
 'app-old-after-rotate','app-fresh-after-rotate','app-bound-before-revoke',
 'app-revoked-generation','app-old-after-recover','app-fresh-after-recover')
DIAGNOSTICS={
 'live-reclaim-denied':('P0001','invalid claim/reclaim','runtime_transition'),
 'expired-renew-denied':('P0001','renewal requires current secret and extends live lease','runtime_transition'),
 'shorten-renew-denied':('P0001','renewal requires current secret and extends live lease','runtime_transition'),
 'copied-hash-renew-denied':('P0001','renewal requires current secret and extends live lease','runtime_transition'),
 'old-secret-renew-denied':('P0001','renewal requires current secret and extends live lease','runtime_transition'),
 'hash-change-denied':('P0001','invalid claim/reclaim','runtime_transition'),
 'attempt-only-denied':('P0001','fence and attempt may change only on claim','runtime_transition'),
 'app-bound-before-rotate':('P0001','job must enter through registered scheduler','runtime_transition'),
 'app-bound-before-revoke':('P0001','job must enter through registered scheduler','runtime_transition')}
APPLICATION_SHA='5ae39abf991f9c189e367eb6ab6968b0ad50836bf4220ac27ef8c18306ac26ad'

class HeldFailure(Exception):
    def __init__(self,code):self.code=code;super().__init__(code)

def need(value,code):
    if not value:raise HeldFailure(code)

def canonical(value):return json.dumps(value,sort_keys=True,separators=(',',':'),ensure_ascii=False,allow_nan=False)
def sha(raw):return hashlib.sha256(raw).hexdigest()
def quote(value):return "'"+str(value).replace("'","''")+"'"
def exact(value,wanted,code):need(canonical(value)==canonical(wanted),code)
def unique_json(raw):
    def pairs(items):
        value={}
        for key,item in items:need(key not in value,'DUPLICATE_RESPONSE_FIELD');value[key]=item
        return value
    return json.loads(raw,object_pairs_hook=pairs,parse_constant=lambda _:(_ for _ in ()).throw(HeldFailure('NONFINITE_RESPONSE')))

def identity(value):
    need(type(value) is str and str(uuid.UUID(value))==value,'FIXED_SOURCE_UUID_REQUIRED')
    return quote(value)+'::uuid'

def marker(name,when):
    need(name in CASE_ORDER and when in ('BEFORE','AFTER'),'REGISTERED_STAGE_MARKER_REQUIRED')
    return 'WA_LR_'+when+'_'+name.upper().replace('-','_')

def mutation(name,work):
    """All timestamp movement uses the actual restricted operation's clock."""
    key=identity(work)
    claim="state='leased',fence=fence+1,attempt_count=attempt_count+1,lease_token_hash=encode(sha256(decode(current_setting('wa.lease_secret'),'hex')),'hex'),lease_expires_at=clock_timestamp()+interval "
    choices={
      'worker-claim':claim+"'12 seconds'",
      'live-reclaim-denied':claim+"'90 seconds'",
      'concurrent-reclaim-stale-holder':claim+"'90 seconds'",
      'worker-renew':"lease_expires_at=clock_timestamp()+interval '40 seconds'",
      'current-holder-renew':"lease_expires_at=clock_timestamp()+interval '90 seconds'",
      'expired-renew-denied':"lease_expires_at=clock_timestamp()+interval '90 seconds'",
      'shorten-renew-denied':"lease_expires_at=lease_expires_at-interval '1 second'",
      'copied-hash-renew-denied':"lease_expires_at=lease_expires_at+interval '10 seconds'",
      'old-secret-renew-denied':"lease_expires_at=lease_expires_at+interval '10 seconds'",
      'hash-change-denied':"lease_token_hash=encode(sha256(decode(current_setting('wa.lease_secret'),'hex')),'hex')",
      'attempt-only-denied':"attempt_count=attempt_count+1"}
    need(name in choices,'REGISTERED_MUTATION_REQUIRED')
    return "WITH changed AS (UPDATE platform.runtime_work_item SET "+choices[name]+" WHERE id="+key+" RETURNING 1) SELECT jsonb_build_object('changed',count(*)) FROM changed;"

def lease_sql(name,work):
    return 'SELECT '+quote(marker(name,'BEFORE'))+';\n'+mutation(name,work)+'\nSELECT '+quote(marker(name,'AFTER'))+';\nCOMMIT;\n'

def schedule_sql(name,work,outbox,semantic):
    need(name in ('app-bound-before-rotate','app-bound-before-revoke','app-fresh-after-recover'),'REGISTERED_SCHEDULER_OPERATION_REQUIRED')
    return ('SELECT '+quote(marker(name,'BEFORE'))+';\nWITH changed AS (INSERT INTO platform.runtime_work_item '
      '(id,outbox_message_id,handler_name,semantic_work_key,state,fence,attempt_count) VALUES ('+identity(work)+','+identity(outbox)+",'assignDefaultFreeTrack.v1',"+quote(semantic)+",'pending',0,0) RETURNING 1) SELECT jsonb_build_object('changed',count(*)) FROM changed;\nSELECT "+quote(marker(name,'AFTER'))+';\nCOMMIT;\n')

def stale_holder_sql(work):
    key=identity(work);name='concurrent-reclaim-stale-holder'
    return ('SELECT '+quote(marker(name,'BEFORE'))+";\nSELECT jsonb_build_object('visible_exact_work',(SELECT count(*) FROM platform.runtime_work_item WHERE id="+key+"));\nWITH changed AS (UPDATE platform.runtime_work_item SET lease_expires_at=clock_timestamp()+interval '90 seconds' WHERE id="+key+" RETURNING 1) SELECT jsonb_build_object('changed',count(*)) FROM changed;\nSELECT "+quote(marker(name,'AFTER'))+';\nROLLBACK;\n')

def expected_markers(name,negative=False):return [marker(name,'BEFORE')] if negative else [marker(name,'BEFORE'),marker(name,'AFTER')]

def intended_diagnostic(stderr,name,application):
    """State alone never proves a guard; require exact source message/frame."""
    need(name in DIAGNOSTICS,'REGISTERED_DIAGNOSTIC_REQUIRED')
    state,message,function=DIAGNOSTICS[name]
    need(sha(application.encode())==APPLICATION_SHA,'CANONICAL_DIAGNOSTIC_SOURCE_REQUIRED')
    found=list(re.finditer(r'CREATE FUNCTION platform_private\.'+re.escape(function)+r'\(\).*?AS\s+(\$[a-z_0-9]*\$)(.*?)\1;',application,re.S))
    need(len(found)==1,'SOURCE_GUARD_FUNCTION_REQUIRED');body=found[0][2]
    lines=[i for i,line in enumerate(body.split('\n'),1) if 'RAISE EXCEPTION '+quote(message) in line]
    need(len(lines)==1,'EXACT_SOURCE_RAISE_REQUIRED')
    clean=type(stderr) is str and len(stderr)<=65536 and all(c in '\n\r\t' or c.isprintable() for c in stderr)
    rows=stderr.replace('\r\n','\n').splitlines() if clean else []
    header=re.compile(r'(?:psql:<stdin>:[0-9]+: )?(?:ERROR|FATAL):\s+([0-9A-Z]{5}):\s+(.*)')
    heads=[m for row in rows if (m:=header.fullmatch(row))]
    frame=re.compile(r'(?:CONTEXT:\s+|\s*)PL/pgSQL function platform_private\.'+function+r'\(\) line ([1-9][0-9]{0,3}) at RAISE')
    frames=[m for row in rows if (m:=frame.fullmatch(row))]
    permitted=lambda row:not row or header.fullmatch(row) or frame.fullmatch(row) or re.fullmatch(r'LOCATION:\s+exec_stmt_raise, pl_exec\.c:[1-9][0-9]{0,5}',row)
    good=bool(clean and len(heads)==len(frames)==1 and heads[0][1]==state and heads[0][2]==message and int(frames[0][1])==lines[0] and all(permitted(row) for row in rows))
    return {'matched':good,'sqlstate':state if good else None,'source_guard':function if good else None,'source_body_sha256':sha(body.encode()) if good else None,'source_body_line':lines[0] if good else None,'classification':'SOURCE_EXACT_GUARD' if good else 'UNLISTED_RESPONSE_DISCARDED'}

def safe_comparison(actual,expected):
    """Retain fixed Boolean outcomes, never arbitrary result dictionaries."""
    return {'row_count_matches':type(actual) is list and len(actual)==len(expected),'shape_and_values_match':canonical(actual)==canonical(expected)}

def verdict(name,code,rows,ack,errors,application,expected):
    need(name in CASE_ORDER,'REGISTERED_CASE_REQUIRED')
    negative=name in DIAGNOSTICS
    allowed=set(expected_markers(name,negative));markers=[row for row in rows if type(row) is str and row.startswith('WA_')]
    outcomes={'exit_code':code if type(code) is int and 0<=code<=255 else None,'acknowledged':ack is True,'stage_markers':[m for m in markers if m in allowed]}
    if negative:
        outcomes['diagnostic']=intended_diagnostic(errors,name,application)
        good=type(code) is int and code==3 and ack is False and rows==expected_markers(name,True) and outcomes['diagnostic']['matched']
    else:
        values=[];parsed=True
        for row in rows:
            if row in allowed:continue
            try:values.append(unique_json(row))
            except (TypeError,ValueError,HeldFailure):parsed=False
        outcomes['comparisons']=safe_comparison(values,expected)
        good=type(code) is int and code==0 and ack is True and not errors and parsed and markers==expected_markers(name) and rows[:1]==[marker(name,'BEFORE')] and rows[-1:]==[marker(name,'AFTER')] and len(rows)==len(expected)+2 and canonical(values)==canonical(expected)
    outcomes['matched']=bool(good)
    return outcomes

def finite_driver(driver):
    """Finite declared order; callback implementation owns all real boundaries."""
    completed=[]
    for name in CASE_ORDER:
        driver.stage(name,len(completed))
        try:driver.case(name)
        except BaseException:
            driver.stopped(name,len(completed));raise
        completed.append(name);driver.completed(name)
    return completed
