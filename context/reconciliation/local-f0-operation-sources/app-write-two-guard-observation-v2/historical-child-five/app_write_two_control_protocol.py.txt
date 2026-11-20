"""Pure, finite R01/R02 verdicts. No database or process API is imported."""
from copy import deepcopy
import hashlib
import json
import re

APPLICATION_SHA='5ae39abf991f9c189e367eb6ab6968b0ad50836bf4220ac27ef8c18306ac26ad'
PLAN_SHA='7582a848b2ad46fc15b86e21ce4d083d98ef6e0c72d28daea75076c5bd94ace8'
ACK_SHA='47a5e05e7e7fe60ec464db5f0d1209cd4867661b9110c6279c9633e9102b6c8d'
CORRECTION_PLAN_SHA='fd23aaa9d066e8422b13a2aa1ef5a1d4b3fb0fd6a9d84f66f336d9ea01de02c3'
CORRECTION_ACK_SHA='53f8ea2b4ecbf5abc6a065d16139b41ba98addd19400226f80b1f561a387a0d1'
CORRECTION_PEER_PLAN_SHA='b0023fd2cfbf8d188313850cb45e915b44b31d4f8b1a51e7e7b2b28710a00e80'
CLAIMS=('P0C-TABLE-RuntimeEffectReceipt-ALLOW|positive.wa_app_runtime.insert','P0C-TABLE-RuntimeWorkItem-ALLOW|positive.wa_app_runtime.update')
FIXTURE_TABLES=('app.users','app.user_security_profiles')
CASE_NAMES=('effect-wrong-root','effect-wrong-purpose','effect-missing-result-field','effect-stale-security','effect-wrong-principal','genuine-sh004-effect-insert','customer-existing-complete-revision-read','customer-existing-missing-revision-read','work-wrong-root','work-wrong-purpose','work-missing-update-field','work-missing-revision','work-stale-security','pending-work-next-attempt-update')

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
 need(type(name) is str and re.fullmatch('[a-z][a-z0-9-]{0,100}',name) and stage in ('BEFORE','AFTER','BIND'),'FIXED_PROTOCOL_MARKER')
 return 'WA_AW2_'+stage+'_'+name.upper().replace('-','_')
def operation_sql(name,body):return 'SELECT '+quote(marker(name,'BEFORE'))+';\n'+body.rstrip()+'\nSELECT '+quote(marker(name,'AFTER'))+';\nCOMMIT;\n'

def diagnostic(spec,stderr,application):
 need(type(stderr) is str and sha(application.encode())==APPLICATION_SHA,'EXACT_DIAGNOSTIC_SOURCE_REQUIRED')
 need(type(spec) is dict and set(spec)=={'sqlstate','message','function'},'EXACT_DIAGNOSTIC_FIELDS');state,message,function=(spec[k] for k in ('sqlstate','message','function'))
 allow={('42501','new row violates row-level security policy for table "customer_profiles"',None),('42501','new row violates row-level security policy for table "runtime_command_receipt"',None),('42501','new row violates row-level security policy for table "runtime_effect_receipt"',None),('42501','foreign Customer principal','guard_customerprofile'),('42501','field or CAS scope denied','guard_runtimeworkitem'),('42501','invalid, stale or unsupported context','bind_request_context')}
 need((state,message,function) in allow,'UNLISTED_DIAGNOSTIC_SPEC')
 patterns=[r'(?:psql:(?:<stdin>|-):[0-9]+: )?ERROR:[ \t]+'+state+r':[ \t]+'+re.escape(message)];body_sha=None;body_line=None
 if function:
  signature='secret text' if function=='bind_request_context' else ''
  found=list(re.finditer(r'CREATE FUNCTION platform_private\.'+function+r'\('+signature+r'\).*?AS\s+(\$[a-z_0-9]*\$)(.*?)\1;',application,re.S));need(len(found)==1,'EXACT_DIAGNOSTIC_BODY');body=found[0][2]
  lines=[i for i,line in enumerate(body.split('\n'),1) if 'RAISE EXCEPTION '+quote(message) in line];need(len(lines)==1,'EXACT_DIAGNOSTIC_LINE');body_line=lines[0];body_sha=sha(body.encode())
  patterns += [r'CONTEXT:[ \t]+PL/pgSQL function platform_private\.'+function+r'\('+('text' if signature else '')+r'\) line '+str(body_line)+r' at RAISE',r'LOCATION:[ \t]+exec_stmt_raise, pl_exec\.c:[1-9][0-9]{0,5}']
 else:patterns += [r'LOCATION:[ \t]+ExecWithCheckOptions, execMain\.c:[1-9][0-9]{0,5}']
 lines=stderr.replace('\r\n','\n').rstrip('\n').split('\n');matched=len(lines)==len(patterns) and all(re.fullmatch(p,line) is not None for p,line in zip(patterns,lines))
 return {'matched':bool(matched),'sqlstate':state if matched else None,'source_body_sha256':body_sha if matched else None,'source_body_line':body_line if matched else None,'classification':message if matched else 'UNLISTED_DISCARDED'}

def verdict(case,code,rows,ack,stderr,application):
 need(type(code) is int and type(rows) is list and all(type(x) is str for x in rows) and type(ack) is bool and type(stderr) is str,'TYPED_OPERATION_RESULT')
 expected=case['expected_records'];need(type(expected) is list and len(rows)==len(expected),'EXACT_RECORD_COUNT');parsed=[unique_json(raw) if type(want) is dict else raw for raw,want in zip(rows,expected)]
 exact(parsed,expected,'EXACT_STAGE_AND_RECORD_SEQUENCE')
 if case['diagnostic'] is not None:
  proof=diagnostic(case['diagnostic'],stderr,application);need(code==3 and ack is False and proof['matched'],'INTENDED_SOURCE_GUARD_REQUIRED')
 else:need(code==0 and ack is True and stderr=='','ACKNOWLEDGED_SOURCE_COMMIT_REQUIRED');proof=None
 result={'status':'PASS_FINITE_APP_WRITE_PROTOCOL_ONLY','source_guard':proof,'complete_record_sequence_match':True,'claim':case['claim']}
 if case['kind']=='read-support':
  need(case['claim'] is None and type(parsed[1]) is dict and set(parsed[1])=={'existing_customer'} and type(parsed[1]['existing_customer']) is int and parsed[1]['existing_customer'] in (0,1),'EXACT_EXISTING_CUSTOMER_READ_COUNT')
  result.update(read_counts=deepcopy(parsed[1]),read_stage_markers={'before':True,'after':True})
 return result

def restoration_identity(baseline,actual):
 wanted={(table,'owner_commit') for table in FIXTURE_TABLES};need(type(baseline) is dict and type(actual) is dict,'RESTORE_NATIVE_SHAPE');normalized=deepcopy(actual)
 def rows(document):
  value=document.get('triggers');need(type(value) is list and all(type(r) is dict for r in value),'RESTORE_TRIGGER_SHAPE');selected=[r for r in value if (r.get('table_name'),r.get('name')) in wanted];need(len(selected)==2 and {(r.get('table_name'),r.get('name')) for r in selected}==wanted,'RESTORE_EXACT_TWO_IDENTITIES');return selected
 need(all(r.get('enabled')=='O' and r.get('internal') is False for r in rows(baseline)),'RESTORE_ORIGINAL_OWNER_CONTRACT');selected=rows(normalized);need(all(r.get('enabled') in ('O','D') and r.get('internal') is False for r in selected),'RESTORE_ONLY_OWNER_O_D');disabled=sum(r['enabled']=='D' for r in selected)
 for row in selected:row['enabled']='O'
 exact(normalized,baseline,'RESTORE_FULL_NATIVE_IDENTITY_DRIFT');return {'full_native_identity_match':True,'declared_owner_triggers':2,'disabled_owner_triggers':disabled}
