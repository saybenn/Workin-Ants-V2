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
GUARD_OBSERVATION_PLAN_SHA='971c1394021a1973452353bb4c83eeba815ed1563d4ac6eb1ffad898935fc9e0'
GUARD_OBSERVATION_ACK_SHA='25708eb58b4dba54760d6752dfc9daa4440b2ef467a367bee78d8edebb8ff539'
COMMAND_GUARD_BODY_SHA='01c6a19be31eb4a29e8ca0e676b0b4d5314291a0196e895e7ebee10e36f658c8'
OUTCOME_FIELDS=frozenset(('observed_stage','response_received','response_shape_valid','client_exit_received','client_exit','client_exit_class','acknowledged','record_count','before_marker_matches','after_marker_matches','expected_sequence_matches','diagnostic','operation_closed','global_closure_confirmed'))
OUTCOME_FIELDS=OUTCOME_FIELDS|{'unexpected_diagnostic'}
UNEXPECTED_SQLSTATES=frozenset(('42501','42703','P0001','P0002','23503','23505','23514','22012','25P02','0A000','57014','25P03','57P05'))
UNEXPECTED_CLASSES=frozenset(('UNAVAILABLE','CLOSURE_UNCONFIRMED','EMPTY','OVERSIZED','CONTROL_REDACTED','MALFORMED_HEADER','MULTIPLE_HEADERS','UNLISTED_SQLSTATE','OBSERVED'))
UNEXPECTED_FRAME_STATUS=frozenset(('UNAVAILABLE','NOT_PRESENT','SOURCE_UNAVAILABLE','UNLISTED_FRAME','AMBIGUOUS_FRAME','SOURCE_VERIFIED'))
UNEXPECTED_SOURCE_FRAMES={
 'platform_private.command_state_guard()':('01c6a19be31eb4a29e8ca0e676b0b4d5314291a0196e895e7ebee10e36f658c8',13),
 'platform_private.guard_customerprofile()':('242bc33836b80f24cdcd22495d133678fd8b5d204f145ffa3f689308a91aba95',23),
 'platform_private.guard_runtimeworkitem()':('8fc8e42c9bdd07e4a8eb766b135e668ca8f75afd1ee6249b83e4f3471e2add4f',18),
 'platform_private.runtime_transition()':('10f9fbdd4b20513d2fa74af2136bb2a60e07eaf567b3425c365bc68290e54038',72)}

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
 allow={('P0001','command action/root does not match protected scope','command_state_guard'),('42501','new row violates row-level security policy for table "customer_profiles"',None),('42501','new row violates row-level security policy for table "runtime_command_receipt"',None),('42501','new row violates row-level security policy for table "runtime_effect_receipt"',None),('42501','foreign Customer principal','guard_customerprofile'),('42501','field or CAS scope denied','guard_runtimeworkitem'),('42501','invalid, stale or unsupported context','bind_request_context')}
 need((state,message,function) in allow,'UNLISTED_DIAGNOSTIC_SPEC')
 patterns=[r'(?:psql:(?:<stdin>|-):[0-9]+: )?ERROR:[ \t]+'+state+r':[ \t]+'+re.escape(message)];body_sha=None;body_line=None
 if function:
  signature='secret text' if function=='bind_request_context' else ''
  found=list(re.finditer(r'CREATE FUNCTION platform_private\.'+function+r'\('+signature+r'\).*?AS\s+(\$[a-z_0-9]*\$)(.*?)\1;',application,re.S));need(len(found)==1,'EXACT_DIAGNOSTIC_BODY');body=found[0][2]
  lines=[i for i,line in enumerate(body.split('\n'),1) if 'RAISE EXCEPTION '+quote(message) in line];need(len(lines)==1,'EXACT_DIAGNOSTIC_LINE');body_line=lines[0];body_sha=sha(body.encode())
  if function=='command_state_guard':need(body_sha==COMMAND_GUARD_BODY_SHA and body_line==7,'EXACT_COMMAND_SCOPE_GUARD')
  patterns += [r'CONTEXT:[ \t]+PL/pgSQL function platform_private\.'+function+r'\('+('text' if signature else '')+r'\) line '+str(body_line)+r' at RAISE',r'LOCATION:[ \t]+exec_stmt_raise, pl_exec\.c:[1-9][0-9]{0,5}']
 else:patterns += [r'LOCATION:[ \t]+ExecWithCheckOptions, execMain\.c:[1-9][0-9]{0,5}']
 lines=stderr.replace('\r\n','\n').rstrip('\n').split('\n');matched=len(lines)==len(patterns) and all(re.fullmatch(p,line) is not None for p,line in zip(patterns,lines))
 return {'matched':bool(matched),'sqlstate':state if matched else None,'source_body_sha256':body_sha if matched else None,'source_body_line':body_line if matched else None,'classification':message if matched else 'UNLISTED_DISCARDED'}

def unexpected_business_diagnostic(stderr,application,closure_confirmed=True):
 """Inert closed observations; no message/SQL/argument/parser dict escapes."""
 value={'schema':'workinants.app-unexpected-business-diagnostic.v3','classification':'UNAVAILABLE','sqlstate':None,'header_count':None,'frame_status':'UNAVAILABLE','source_frame':None}
 if closure_confirmed is not True:value['classification']='CLOSURE_UNCONFIRMED';return value
 if type(stderr)is not str:return value
 if len(stderr)>65536:value['classification']='OVERSIZED';return value
 try:
  if len(stderr.encode('utf8'))>65536:value['classification']='OVERSIZED';return value
 except UnicodeError:value['classification']='CONTROL_REDACTED';return value
 text=stderr.replace('\r\n','\n')
 if any(ord(c)>126 or ord(c)<32 and c not in('\n','\t')for c in text):value['classification']='CONTROL_REDACTED';return value
 if text=='':value.update(classification='EMPTY',header_count=0,frame_status='NOT_PRESENT');return value
 candidates=list(re.finditer(r'(?<![A-Za-z0-9_])(?:ERROR|FATAL|PANIC|WARNING)(?=[:\s]|$)',text));value['header_count']=min(len(candidates),2)
 if len(candidates)>1:value['classification']='MULTIPLE_HEADERS';return value
 lines=text.rstrip('\n').split('\n')
 header=re.fullmatch(r'(?:psql:(?:<stdin>|-):[1-9][0-9]{0,8}: )?ERROR:[ \t]+([0-9A-Z]{5}):[ \t]+[^\r\n]+',lines[0])
 if len(candidates)!=1 or header is None or candidates[0].start()not in(0,lines[0].find('ERROR:')):value['classification']='MALFORMED_HEADER';return value
 if header[1]not in UNEXPECTED_SQLSTATES:value['classification']='UNLISTED_SQLSTATE';return value
 value.update(classification='OBSERVED',sqlstate=header[1],frame_status='NOT_PRESENT')
 frames=[line for line in lines[1:]if re.search(r'PL/pgSQL\s+function',line)]
 if not frames:return value
 if len(frames)!=1:value['frame_status']='AMBIGUOUS_FRAME';return value
 frame=re.fullmatch(r'CONTEXT:[ \t]+PL/pgSQL function (platform_private\.[a-z_][a-z_0-9]*)\(\) line ([1-9][0-9]{0,3}) at (RAISE|SQL statement|assignment|IF|RETURN|PERFORM|FOR over SELECT rows|FOR over EXECUTE statement|RETURN NEXT)',frames[0])
 if frame is None or frame[1]+'()'not in UNEXPECTED_SOURCE_FRAMES:value['frame_status']='UNLISTED_FRAME';return value
 try:source_ok=type(application)is str and sha(application.encode())==APPLICATION_SHA
 except UnicodeError:source_ok=False
 if not source_ok:value['frame_status']='SOURCE_UNAVAILABLE';return value
 identity=frame[1]+'()';expected_sha,line_limit=UNEXPECTED_SOURCE_FRAMES[identity];name=frame[1].split('.')[1]
 declarations=list(re.finditer(r'CREATE FUNCTION platform_private\.'+name+r'\(\).*?AS\s+(\$[a-z_0-9]*\$)(.*?)\1;',application,re.S))
 if len(declarations)!=1 or sha(declarations[0][2].encode())!=expected_sha or len(declarations[0][2].split('\n'))!=line_limit:value['frame_status']='SOURCE_UNAVAILABLE';return value
 line=int(frame[2])
 if line>line_limit:value['frame_status']='UNLISTED_FRAME';return value
 value.update(frame_status='SOURCE_VERIFIED',source_frame={'function':identity,'source_body_sha256':expected_sha,'source_body_line':line});return value

def validate_unexpected_diagnostic(value):
 fields={'schema','classification','sqlstate','header_count','frame_status','source_frame'}
 need(type(value)is dict and set(value)==fields and value['schema']=='workinants.app-unexpected-business-diagnostic.v3','TYPED_UNEXPECTED_DIAGNOSTIC_FIELDS')
 need(type(value['classification'])is str and value['classification']in UNEXPECTED_CLASSES and type(value['frame_status'])is str and value['frame_status']in UNEXPECTED_FRAME_STATUS,'TYPED_UNEXPECTED_DIAGNOSTIC_ENUMS')
 need(value['header_count']is None or type(value['header_count'])is int and value['header_count']in(0,1,2),'TYPED_UNEXPECTED_HEADER_COUNT')
 if value['classification']=='OBSERVED':need(type(value['sqlstate'])is str and value['sqlstate']in UNEXPECTED_SQLSTATES and value['header_count']==1,'TYPED_UNEXPECTED_SQLSTATE')
 else:need(value['sqlstate']is None and value['source_frame']is None,'REDACTED_UNEXPECTED_DIAGNOSTIC')
 if value['classification']=='EMPTY':need(value['header_count']==0 and value['frame_status']=='NOT_PRESENT','EMPTY_UNEXPECTED_DIAGNOSTIC')
 if value['classification']=='MULTIPLE_HEADERS':need(value['header_count']==2,'MULTIPLE_UNEXPECTED_HEADERS')
 if value['classification']in('UNAVAILABLE','CLOSURE_UNCONFIRMED','OVERSIZED','CONTROL_REDACTED'):need(value['header_count']is None and value['frame_status']=='UNAVAILABLE','UNAVAILABLE_UNEXPECTED_DIAGNOSTIC')
 if value['classification']=='MALFORMED_HEADER':need(value['header_count']in(0,1)and value['frame_status']=='UNAVAILABLE','MALFORMED_UNEXPECTED_HEADER')
 if value['classification']=='UNLISTED_SQLSTATE':need(value['header_count']==1 and value['frame_status']=='UNAVAILABLE','UNLISTED_UNEXPECTED_SQLSTATE')
 if value['classification']=='MULTIPLE_HEADERS':need(value['frame_status']=='UNAVAILABLE','MULTIPLE_UNEXPECTED_HEADER_FRAME')
 if value['classification']=='OBSERVED':need(value['frame_status']!='UNAVAILABLE','OBSERVED_UNEXPECTED_FRAME_STATUS')
 frame=value['source_frame']
 if value['frame_status']=='SOURCE_VERIFIED':
  need(value['classification']=='OBSERVED' and type(frame)is dict and set(frame)=={'function','source_body_sha256','source_body_line'} and type(frame['function'])is str and frame['function']in UNEXPECTED_SOURCE_FRAMES,'TYPED_UNEXPECTED_SOURCE_FRAME')
  expected,limit=UNEXPECTED_SOURCE_FRAMES[frame['function']];need(type(frame['source_body_sha256'])is str and frame['source_body_sha256']==expected and type(frame['source_body_line'])is int and 0<frame['source_body_line']<=limit,'BOUND_UNEXPECTED_SOURCE_FRAME')
 else:need(frame is None,'REDACTED_UNEXPECTED_SOURCE_FRAME')
 return value

def operation_outcome(case,stage,received,response,exit_received,code,closed,global_closed,application):
 """Bounded observations only; never a verdict or a raw response projection."""
 need(stage in ('NOT_STARTED','SAME_XID','BIND_MARKER','BIND','BUSINESS'),'FIXED_OBSERVATION_STAGE')
 valid=received is True and type(response) is tuple and len(response)==3 and type(response[0]) is list and len(response[0])<=16 and all(type(x) is str and len(x)<=65536 for x in response[0]) and type(response[1]) is bool and type(response[2]) is str and len(response[2])<=65536
 rows,ack,stderr=response if valid else (None,None,None)
 before=after=sequence=None;proof=None
 if valid:
  if stage in ('BIND','BUSINESS'):
   expected=case['expected_records'] if stage=='BUSINESS' or case['kind']=='binder-denial' else []
  else:expected=['t'] if stage=='SAME_XID' else [marker(case['name'],'BIND')] if stage=='BIND_MARKER' else []
  try:sequence=canonical([unique_json(raw) if type(want) is dict else raw for raw,want in zip(rows,expected)])==canonical(expected) and len(rows)==len(expected)
  except BaseException:sequence=False
  if stage=='BUSINESS':before=bool(rows and rows[0]==marker(case['name'],'BEFORE'));after=bool(rows and rows[-1]==marker(case['name'],'AFTER'))
  if case['diagnostic'] is not None and stage==('BIND' if case['kind']=='binder-denial' else 'BUSINESS'):
   proof=diagnostic(case['diagnostic'],stderr,application)
 known=exit_received is True and type(code) is int and code in (0,1,2,3)
 unexpected=unexpected_business_diagnostic(stderr,application,closed is True and global_closed is True)if stage=='BUSINESS'else None
 return {'observed_stage':stage,'response_received':received is True,'response_shape_valid':bool(valid),'client_exit_received':exit_received is True,'client_exit':code if known else None,'client_exit_class':'KNOWN' if known else 'OTHER' if exit_received is True else 'UNAVAILABLE','acknowledged':ack,'record_count':len(rows) if valid else None,'before_marker_matches':before,'after_marker_matches':after,'expected_sequence_matches':sequence,'diagnostic':proof,'unexpected_diagnostic':unexpected,'operation_closed':closed is True,'global_closure_confirmed':global_closed is True}

def validate_operation_outcome(value):
 need(type(value) is dict and set(value)==OUTCOME_FIELDS,'EXACT_OPERATION_OUTCOME_FIELDS')
 need(type(value['observed_stage']) is str and value['observed_stage'] in ('NOT_STARTED','SAME_XID','BIND_MARKER','BIND','BUSINESS'),'TYPED_OPERATION_OUTCOME_STAGE')
 need(all(type(value[k]) is bool for k in ('response_received','response_shape_valid','client_exit_received','operation_closed','global_closure_confirmed')),'TYPED_OPERATION_OUTCOME_FLAGS')
 need(value['client_exit_class'] in ('KNOWN','OTHER','UNAVAILABLE') and type(value['client_exit_class']) is str,'TYPED_OPERATION_EXIT_CLASS')
 need((value['client_exit'] is None or type(value['client_exit']) is int and value['client_exit'] in (0,1,2,3)) and (value['client_exit_class']=='KNOWN')==(value['client_exit'] is not None),'TYPED_OPERATION_EXIT')
 need((value['client_exit_class']=='UNAVAILABLE')==(value['client_exit_received'] is False),'OBSERVED_OPERATION_EXIT')
 for k in ('acknowledged','before_marker_matches','after_marker_matches','expected_sequence_matches'):need(value[k] is None or type(value[k]) is bool,'TYPED_OPERATION_COMPARISON')
 need(value['record_count'] is None or type(value['record_count']) is int and 0<=value['record_count']<=16,'TYPED_OPERATION_RECORD_COUNT')
 if not value['response_shape_valid']:need(value['acknowledged'] is None and value['record_count'] is None and all(value[k] is None for k in ('before_marker_matches','after_marker_matches','expected_sequence_matches','diagnostic')),'UNAVAILABLE_OPERATION_RESPONSE')
 else:need(value['response_received'] and type(value['acknowledged']) is bool and type(value['record_count']) is int and type(value['expected_sequence_matches']) is bool,'OBSERVED_OPERATION_RESPONSE')
 proof=value['diagnostic']
 if value['observed_stage']=='BUSINESS':
  validate_unexpected_diagnostic(value['unexpected_diagnostic'])
  if not value['operation_closed']or not value['global_closure_confirmed']:need(value['unexpected_diagnostic']['classification']=='CLOSURE_UNCONFIRMED','UNCONFIRMED_UNEXPECTED_DIAGNOSTIC_CLOSURE')
  elif not value['response_shape_valid']:need(value['unexpected_diagnostic']['classification']=='UNAVAILABLE','UNAVAILABLE_UNEXPECTED_DIAGNOSTIC_RESPONSE')
 else:need(value['unexpected_diagnostic']is None,'NO_UNEXPECTED_DIAGNOSTIC_BEFORE_BUSINESS')
 if proof is not None:
  need(type(proof) is dict and set(proof)=={'matched','sqlstate','source_body_sha256','source_body_line','classification'} and type(proof['matched']) is bool,'TYPED_OPERATION_DIAGNOSTIC')
  if not proof['matched']:exact(proof,{'matched':False,'sqlstate':None,'source_body_sha256':None,'source_body_line':None,'classification':'UNLISTED_DISCARDED'},'DISCARDED_OPERATION_DIAGNOSTIC')
  else:
   allow={('P0001','command action/root does not match protected scope',COMMAND_GUARD_BODY_SHA,7)}
   # Other accepted bodies are checked against the source by the producer and
   # the parent's per-case expected guard; this pure validator only admits the
   # finite classifications and typed source fingerprint shape.
   need(type(proof['sqlstate']) is str and proof['sqlstate'] in ('42501','P0001') and type(proof['classification']) is str and proof['classification'] in ('command action/root does not match protected scope','new row violates row-level security policy for table "customer_profiles"','new row violates row-level security policy for table "runtime_command_receipt"','new row violates row-level security policy for table "runtime_effect_receipt"','foreign Customer principal','field or CAS scope denied','invalid, stale or unsupported context'),'ALLOWLISTED_OPERATION_DIAGNOSTIC')
   need((proof['source_body_sha256'] is None and proof['source_body_line'] is None) or type(proof['source_body_sha256']) is str and re.fullmatch('[0-9a-f]{64}',proof['source_body_sha256']) and type(proof['source_body_line']) is int and 0<proof['source_body_line']<=10000,'TYPED_OPERATION_SOURCE_FRAME')
   if proof['sqlstate']=='P0001':need((proof['sqlstate'],proof['classification'],proof['source_body_sha256'],proof['source_body_line']) in allow,'EXACT_COMMAND_OPERATION_DIAGNOSTIC')
 return value

def verdict(case,code,rows,ack,stderr,application):
 if case['diagnostic'] is not None and case['diagnostic'].get('function')=='command_state_guard':need(case['name']=='effect-wrong-root','EXACT_COMMAND_GUARD_CASE')
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
