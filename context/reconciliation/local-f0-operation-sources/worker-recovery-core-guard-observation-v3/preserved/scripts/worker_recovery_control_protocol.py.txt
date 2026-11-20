"""Pure verdicts for the exact21 retained-effect worker source protocols."""
from copy import deepcopy
import hashlib
import json
import re

APPLICATION_SHA='5ae39abf991f9c189e367eb6ab6968b0ad50836bf4220ac27ef8c18306ac26ad'
PLAN_SHA='1a6b3bfe380aba7250fd8dfbf900ab260fab5668c0e4352c0624b850a6bd612b'
READ_MODELS=('TrackSubscription','TrackEntitlementGrant','RuntimeCommandReceipt','RuntimeOutboxMessage','RuntimeEffectReceipt','RuntimeAttempt','RuntimeInboxReceipt','OwnerMutationEvidence','TrackBaseSelection','TrackEnrollmentReceipt')
CASE_NAMES=('genuine-effect-committed-work-still-leased',)+tuple('current-worker-read-'+model for model in READ_MODELS)+('copied-readable-hash-is-not-preimage','nonnull-effect-relink-denied','null-pointer-foreign-same-fence-effect-denied','real-higher-fence-reclaim-with-retained-effect','fresh-holder-recognizes-original-lower-fence-effect','valid-current-Free-selection-survives-duplicate-attempt','fresh-processing-old-fence-denied','fresh-processing-old-preimage-denied','terminal-work-trigger-denial-rolls-back-completion','original-effect-completes-once-without-reenrollment')
FIXTURE_TABLES=('app.users','app.user_security_profiles','app.track_plans','app.track_entitlement_definitions','app.track_plan_entitlements')
RESULT_SCHEMA='urn:workinants:database-review:foundation-payloads:v1#/$defs/assignDefaultFreeTrackCustomerResult'
DIAGNOSTICS={
 'nonnull-effect-relink-denied':('P0001','effect link must be one exact protected attachment','runtime_transition'),
 'null-pointer-foreign-same-fence-effect-denied':('P0001','effect link must be one exact protected attachment','runtime_transition'),
 'valid-current-Free-selection-survives-duplicate-attempt':('42501','new row violates row-level security policy for table "track_subscriptions"',None),
 'terminal-work-trigger-denial-rolls-back-completion':('P0001','terminal work/regressive attempt','runtime_transition')}

class HeldFailure(Exception):
 def __init__(self,code):self.code=code;super().__init__(code)
def need(value,code):
 if not value:raise HeldFailure(code)
def canonical(value):return json.dumps(value,sort_keys=True,separators=(',',':'),ensure_ascii=False,allow_nan=False)
def sha(raw):return hashlib.sha256(raw).hexdigest()
def digest(value):return sha(canonical(value).encode())
def quote(value):return "'"+str(value).replace("'","''")+"'"
def exact(actual,expected,code):need(canonical(actual)==canonical(expected),code)
def unique_json(raw):
 def pairs(items):
  value={}
  for key,item in items:need(key not in value,'DUPLICATE_RESPONSE_FIELD');value[key]=item
  return value
 try:return json.loads(raw,object_pairs_hook=pairs,parse_constant=lambda _:(_ for _ in ()).throw(HeldFailure('NONFINITE_RESPONSE')))
 except HeldFailure:raise
 except BaseException:raise HeldFailure('MALFORMED_RESPONSE') from None
def marker(name,stage):
 need(type(name) is str and re.fullmatch('[A-Za-z][A-Za-z0-9-]{0,110}',name) and stage in ('BEFORE','AFTER'),'FIXED_PROTOCOL_MARKER')
 return 'WA_WR_'+stage+'_'+name.upper().replace('-','_')
def operation_sql(name,body):return 'SELECT '+quote(marker(name,'BEFORE'))+';\n'+body.rstrip()+'\nSELECT '+quote(marker(name,'AFTER'))+';\nCOMMIT;\n'

def diagnostic(name,stderr,application):
 need(name in DIAGNOSTICS and sha(application.encode())==APPLICATION_SHA,'EXACT_DIAGNOSTIC_SOURCE_REQUIRED')
 state,message,function=DIAGNOSTICS[name];text=stderr.replace('\r\n','\n').rstrip('\n').split('\n');body_sha=None;body_line=None
 header=r'(?:psql:(?:<stdin>|-):[0-9]+: )?ERROR:[ \t]+'+state+r':[ \t]+'+re.escape(message)
 patterns=[header]
 if function:
  found=list(re.finditer(r'CREATE FUNCTION platform_private\.'+function+r'\(\).*?AS\s+(\$[a-z_0-9]*\$)(.*?)\1;',application,re.S));need(len(found)==1,'EXACT_DIAGNOSTIC_BODY');body=found[0][2]
  lines=[i for i,line in enumerate(body.split('\n'),1) if 'RAISE EXCEPTION '+quote(message) in line];need(len(lines)==1,'EXACT_DIAGNOSTIC_LINE');body_line=lines[0];body_sha=sha(body.encode())
  patterns += [r'CONTEXT:[ \t]+PL/pgSQL function platform_private\.'+function+r'\(\) line '+str(body_line)+r' at RAISE',r'LOCATION:[ \t]+exec_stmt_raise, pl_exec\.c:[1-9][0-9]{0,5}']
 else:patterns += [r'LOCATION:[ \t]+ExecWithCheckOptions, execMain\.c:[1-9][0-9]{0,5}']
 matched=len(text)==len(patterns) and all(re.fullmatch(p,line) is not None for p,line in zip(patterns,text))
 return {'matched':bool(matched),'sqlstate':state if matched else None,'classification':name if matched else 'UNLISTED_DISCARDED','source_body_sha256':body_sha if matched else None,'source_body_line':body_line if matched else None,'native_location':('exec_stmt_raise@pl_exec.c' if function else 'ExecWithCheckOptions@execMain.c') if matched else None}

def verdict(case,code,rows,ack,stderr,application):
 need(type(code) is int and type(rows) is list and all(type(x) is str for x in rows) and type(ack) is bool and type(stderr) is str,'TYPED_OPERATION_RESULT')
 expected=case['expected_records'];need(type(expected) is list,'FIXED_RECORD_SEQUENCE')
 parsed=[]
 for raw,wanted in zip(rows,expected):parsed.append(unique_json(raw) if type(wanted) is dict else raw)
 exact(parsed,expected,'EXACT_STAGE_AND_RECORD_SEQUENCE');need(len(rows)==len(expected),'EXACT_RECORD_COUNT')
 if case['name'] in DIAGNOSTICS:
  proof=diagnostic(case['name'],stderr,application);need(code==3 and ack is False and proof['matched'],'INTENDED_SOURCE_GUARD_REQUIRED')
 else:need(code==0 and ack is True and stderr=='','ACKNOWLEDGED_SOURCE_COMMIT_REQUIRED');proof=None
 return {'status':'PASS_FINITE_WORKER_PROTOCOL_ONLY','source_guard':proof,'complete_record_sequence_match':True}

def restoration_identity(baseline,actual):
 wanted={(table,'owner_commit') for table in FIXTURE_TABLES};need(type(baseline) is dict and type(actual) is dict,'RESTORE_NATIVE_SHAPE');normalized=deepcopy(actual)
 def rows(document):
  value=document.get('triggers');need(type(value) is list and all(type(r) is dict for r in value),'RESTORE_TRIGGER_SHAPE');selected=[r for r in value if (r.get('table_name'),r.get('name')) in wanted];need(len(selected)==5 and {(r.get('table_name'),r.get('name')) for r in selected}==wanted,'RESTORE_EXACT_FIVE_IDENTITIES');return selected
 need(all(r.get('enabled')=='O' and r.get('internal') is False for r in rows(baseline)),'RESTORE_ORIGINAL_OWNER_CONTRACT');selected=rows(normalized);need(all(r.get('enabled') in ('O','D') and r.get('internal') is False for r in selected),'RESTORE_ONLY_OWNER_O_D');disabled=sum(r['enabled']=='D' for r in selected)
 for row in selected:row['enabled']='O'
 exact(normalized,baseline,'RESTORE_FULL_NATIVE_IDENTITY_DRIFT');return {'full_native_identity_match':True,'declared_owner_triggers':5,'disabled_owner_triggers':disabled}

def finite_driver(coordinator):
 need(tuple(c['name'] for c in coordinator.packet['cases'])==CASE_NAMES,'EXACT21_SOURCE_CASES')
 for index,case in enumerate(coordinator.packet['cases']):
  if index:need(coordinator.checkpoint_committed is True,'GENUINE_LEASED_CHECKPOINT_REQUIRED_BEFORE_RECOVERY')
  coordinator.run_case(case)
