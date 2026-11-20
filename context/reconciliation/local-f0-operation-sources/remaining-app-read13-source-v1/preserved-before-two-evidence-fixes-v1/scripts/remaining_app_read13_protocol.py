"""Pure finite Read13 recipes. This module cannot open a database or a process."""
from copy import deepcopy
import hashlib
import json
import re
import uuid

PLAN_SHA = '90be6c449ca355c4b3b365e289696d93c4831c9270e00f372e15020734d478c0'
ACK_SHA = '465b368e5c7f68e91eaa7686a429464b52f0a4e9dd29006e49f32abacdef0154'
PEER_SHA = 'fe46adf4d272984694d5d5d54a2e224e2d4530841b1cb50401535d8ba4248553'
APPLICATION_SHA = '5ae39abf991f9c189e367eb6ab6968b0ad50836bf4220ac27ef8c18306ac26ad'
SOURCE_ROOT = 'context/reconciliation/local-f0-operation-sources/remaining-app-read13-source-v1'
PLAN_PATH = SOURCE_ROOT + '/read13_concrete_fixture_recipe_source_supplement_v5_20261120.json'
VALIDATION = 'context/reconciliation/local-f0-remaining-app-read13-source-validation.json'
GROUPS = {
 'G1': ('User','Security'),
 'G2': ('Command','Customer','History','Evidence','EventOutbox','CommandOutbox','CommittedEffect'),
 'G3': ('PendingCommand','PendingEffect'), 'G4': ('Work',), 'G5': ('Content',),
 'G6': ('Presentation',), 'G7': ('Disposition',),
 'G8': ('Plan','Definition','PlanEntitlement','Subscription','SubscriptionEvent','Grant'),
 'G9': ('Reservation',), 'G10': ('UsageEvent','Counter')}
APP_GROUPS = {'G2':'SH004-R01', 'G3':'SH004-PENDING','G4':'SCHEDULER',
              'G6':'CONSENT-PRESENTATION','G7':'CONSENT-DISPOSITION'}
FINITE = {'case_count':82,'positive_select_claims':13,'fixture_rows':48,
          'nonnull_fixture_fk_links':78,'setup_bypass_triggers':15,
          'grant_instances_max':79,'setup_grants':10,'read_control_grants':69,
          'user_triggers_restored':100,'simultaneous_app_sessions_max':1,
          'worker_loop':False}

class HeldFailure(Exception):
 def __init__(self,code): self.code=code; super().__init__(code)

def need(condition,code):
 if not condition: raise HeldFailure(code)

def sha(raw): return hashlib.sha256(raw).hexdigest()
def canonical(value): return json.dumps(value,sort_keys=True,separators=(',',':'),ensure_ascii=False,allow_nan=False)
def digest(value): return sha(canonical(value).encode('utf8'))
def exact(value,wanted,code): need(canonical(value)==canonical(wanted),code)
def quote(value): return "'"+str(value).replace("'","''")+"'"

def unique_json(raw):
 def pairs(items):
  result={}
  for key,value in items: need(key not in result,'DUPLICATE_JSON_FIELD'); result[key]=value
  return result
 try: return json.loads(raw,object_pairs_hook=pairs,parse_constant=lambda _:(_ for _ in ()).throw(HeldFailure('NONFINITE_JSON')))
 except HeldFailure: raise
 except BaseException: raise HeldFailure('MALFORMED_JSON') from None

def materialize(plan,run_id):
 """A closed substitution of reviewed preview identifiers, before packet pinning."""
 need(type(run_id) is str and str(uuid.UUID(run_id))==run_id and uuid.UUID(run_id).version==4,'FRESH_UUID4_NAMESPACE')
 preview=plan['fixture_namespace']; need(run_id!=preview['preview'],'PREVIEW_IDS_ARE_NOT_RUNTIME_IDS')
 mapping={old:str(uuid.uuid5(uuid.UUID(run_id),'read13/'+side+'/'+label))
          for side,labels in preview['preview_ids'].items() for label,old in labels.items()}
 need(len(mapping)==48 and len(set(mapping.values()))==48,'EXACT48_UNIQUE_IDS')
 mapping[preview['preview']]=run_id
 pattern=re.compile('|'.join(re.escape(k) for k in sorted(mapping,key=len,reverse=True)))
 def replace(value):
  if type(value) is str:return pattern.sub(lambda m:mapping[m.group()],value)
  if type(value) is list:return [replace(x) for x in value]
  if type(value) is dict:return {key:replace(item) for key,item in value.items()}
  return value
 result=replace(deepcopy(plan));result['fixture_namespace']['actual_run_id']=run_id
 need(len(result['fixture_rows'])==48 and len(result['verified_direct_FK_links'])==78,'FIXTURE_GRAPH_COUNTS')
 need(len(result['selected_reads'])==13 and len(result['scenario_recipes'])==82 and len(result['setup_grant_contexts'])==10,'FINITE_PLAN_COUNTS')
 return result

def json_sql(value):
 """Source JSON uses PostgreSQL values; clock markers never become JSON objects."""
 if type(value) is dict:
  if set(value)=={'from_actual_server_clock'}:
   return "to_char(transaction_timestamp() AT TIME ZONE 'UTC','YYYY-MM-DD\"T\"HH24:MI:SS.US\"Z\"')"
  need(not any(key in value for key in ('server_value','server_expression','source_default_or_guard','PG_jsonb_text_UTF8_SHA256')),'JSON_PLACEHOLDER_SCOPE')
  return 'jsonb_build_object('+','.join(quote(k)+','+json_sql(v) for k,v in value.items())+')'
 if type(value) is list:return 'jsonb_build_array('+','.join(json_sql(x) for x in value)+')'
 if value is None:return 'NULL'
 if type(value) is bool:return 'true' if value else 'false'
 if type(value) is int:return str(value)
 need(type(value) is str,'SOURCE_JSON_SCALAR_TYPE');return quote(value)+'::text'

def value_sql(value):
 if type(value) is dict:
  if set(value)=={'source_default_or_guard'}:need(value['source_default_or_guard'] is True,'SOURCE_DEFAULT_MARKER');return 'DEFAULT'
  if set(value)=={'server_value'}:
   need(value['server_value'] in ('T_SETUP UTC; observe actual guard timestamps/XID privately','T_USAGE'),'CLOSED_SERVER_CLOCK_MARKER')
   return 'clock_timestamp()' if value['server_value'].startswith('T_SETUP') else 'transaction_timestamp()'
  if set(value)=={'server_expression'}:
   expressions={'T_SETUP minus 1 day':"transaction_timestamp()-interval '1 day'",
    'date_trunc(month,T_USAGE AT TIME ZONE UTC) AT TIME ZONE UTC':"date_trunc('month',transaction_timestamp() AT TIME ZONE 'UTC') AT TIME ZONE 'UTC'",
    'same period_start plus interval 1 month':"(date_trunc('month',transaction_timestamp() AT TIME ZONE 'UTC')+interval '1 month') AT TIME ZONE 'UTC'"}
   need(value['server_expression'] in expressions,'CLOSED_SERVER_EXPRESSION');return expressions[value['server_expression']]
  if set(value)=={'PG_jsonb_text_UTF8_SHA256','host_JSON_digest_forbidden'}:
   need(value['host_JSON_digest_forbidden'] is True,'POSTGRES_STORAGE_DIGEST_REQUIRED')
   return "encode(sha256(convert_to(("+json_sql(value['PG_jsonb_text_UTF8_SHA256'])+")::text,'UTF8')),'hex')"
  return json_sql(value)
 if value is None:return 'NULL'
 if type(value) is bool:return 'true' if value else 'false'
 if type(value) is int:return str(value)
 need(type(value) is str,'SOURCE_ROW_SCALAR_TYPE');return quote(value)

def insert_sql(row):
 need(re.fullmatch(r'(app|platform)\.[a-z_]+',row['table']),'SOURCE_TABLE_IDENTITY')
 # Do not name server-owned/default columns in a restricted INSERT. Even a
 # literal DEFAULT in the column list would require that column's privilege.
 values={key:value for key,value in row['values'].items() if not(type(value) is dict and set(value)=={'source_default_or_guard'} and value['source_default_or_guard'] is True)}
 need(all(re.fullmatch('[a-z_]+',k) for k in values),'SOURCE_COLUMN_IDENTITY')
 return 'INSERT INTO '+row['table']+' ('+','.join(values)+') VALUES ('+','.join(value_sql(v) for v in values.values())+');'

def marker(name,position):return {'read13_marker':name,'position':position}
def marker_sql(name,position):return 'SELECT '+json_sql(marker(name,position))+';'
def operation_sql(name,body,commit=False):
 return '\n'.join([marker_sql(name,'BEFORE'),body,'SET CONSTRAINTS ALL IMMEDIATE;',marker_sql(name,'AFTER')]+(['COMMIT;'] if commit else []))+'\n'

def render(plan):
 rows={(r['side'],r['label']):r for r in plan['fixture_rows']};need(len(rows)==48,'EXACT48_ROWS')
 files={};groups=[]
 for group,labels in GROUPS.items():
  sides=('A','B') if group in APP_GROUPS else ('AB',)
  for side in sides:
   name=group+'-'+side;selected=[rows[s,label] for s in (('A','B') if side=='AB' else (side,)) for label in labels]
   body='\n'.join(insert_sql(row) for row in selected);files[name+'.sql']=operation_sql(name,body,commit=True)
   groups.append({'name':name,'group':group,'side':side,'sql':name+'.sql','login':'wa_app_runtime' if group in APP_GROUPS else 'postgres',
     'grant_id':APP_GROUPS[group]+'/'+side if group in APP_GROUPS else None,'row_ids':[r['values']['id'] for r in selected],
     'table_increments':{table:sum(r['table']==table for r in selected) for table in sorted({r['table'] for r in selected})}})
 allow=plan['trigger_setup_allowlist'];need(len(allow)==15 and len({x['identity'] for x in allow})==15,'EXACT15_BYPASSES')
 def ddl(enabled):return '\n'.join('ALTER TABLE '+x['definition']['table']+' '+('ENABLE' if enabled else 'DISABLE')+' TRIGGER '+x['definition']['name']+';' for x in (reversed(allow) if enabled else allow))
 files['fixture-disable-exact15.sql']='BEGIN;\n'+ddl(False)+'\nCOMMIT;\n'
 files['fixture-restore-exact15.sql']='BEGIN;\n'+ddl(True)+'\nCOMMIT;\n'
 reads={r['model']:r for r in plan['selected_reads']};grants={x['id']:normalize_grant(x) for x in plan['setup_grant_contexts']};cases=[]
 for index,recipe in enumerate(plan['scenario_recipes']):
  name=recipe['id'];shared=name.startswith('shared/');model='TrackSubscription' if shared else recipe['model'];read=reads[model]
  side='A' if shared else recipe['context'];grant=normalize_grant(read['contexts'][side]);kind=name.split('/')[1];grant['template_id']=name
  if kind=='field':grant['allowed_fields'].remove(model+'/'+read['contexts'][side]['expected_ids'][0]+'/SELECT/id')
  elif kind=='purpose':grant['purpose']='read13.unregistered-purpose'
  elif kind=='revision':
   token=model+'/'+read['contexts'][side]['expected_ids'][0]+'/revision/0';need(token in grant['allowed_fields'],'ACTUAL_OWN_REVISION_TOKEN');grant['allowed_fields'].remove(token);grant['allowed_fields'].append(token[:-1]+'1');grant['allowed_fields'].sort()
  elif kind=='root':grant['target_id']=read['contexts']['B']['target_id']
  elif kind=='identity_generation_mismatch':grant['security_generation']=1
  grants[name]=grant
  body=[];expected=[marker(name,'BEFORE')]
  if not shared:
   for prerequisite in recipe['expected_prerequisite_rowsets']:
    other=reads.get(prerequisite['model']);columns=other['columns'] if other else prerequisite_columns(plan,prerequisite['model'])
    table=other['table'] if other else prerequisite_table(prerequisite['model'])
    body.append(rowset_sql(prerequisite['model'],table,columns,[prerequisite['id']]))
    expected.append({'model':prerequisite['model'],'ids':sorted(prerequisite['expected_ids'])})
   body.append(rowset_sql(model,read['table'],read['columns'],read['contexts'][side]['query_ids']));expected.append({'model':model,'ids':sorted(recipe['expected_ids'])});expected.append(marker(name,'AFTER'))
  filename='read-'+str(index+1).zfill(2)+'.sql';files[filename]=operation_sql(name,'\n'.join(body))
  cases.append({'name':name,'status':'NOT_RUN','model':model,'kind':'binder-denial' if shared else 'read','control':kind,'grant':None if kind=='unbound' else name,'sql':filename,'expected_records':expected if not shared else [],'claim':read['case_id']+'|'+read['assertion_id'] if kind=='positive' else None,'allowed_changed_tables':[]})
 need(sum(c['grant'] is not None for c in cases)==69 and len(grants)==92,'EXACT79_ISSUED_NOT_TEMPLATE_COUNT')
 return files,groups,grants,cases

def normalize_grant(value):
 keys=('principal_user_id','service_principal','owner_module_id','action','purpose','target_kind','target_id','security_generation','source_generation','allowed_fields')
 g={k:deepcopy(value[k]) for k in keys};g.update(database_login_role='wa_app_runtime',policy_version='read13-source-fixture.v1')
 need(all(type(g[k]) is int and g[k]>=0 for k in ('security_generation','source_generation')),'TYPED_CONTEXT_GENERATIONS')
 g['allowed_fields']=sorted(g['allowed_fields']);need(len(g['allowed_fields'])==len(set(g['allowed_fields'])) and len(g['allowed_fields'])<=1024,'FINITE_DISTINCT_FIELD_CAPS')
 return g

def prerequisite_table(model):
 tables={'CustomerProfile':'app.customer_profiles','ConsentPresentation':'app.consent_presentation','RuntimeCommandReceipt':'platform.runtime_command_receipt','RuntimeEffectReceipt':'platform.runtime_effect_receipt'}
 need(model in tables,'CLOSED_PREREQUISITE_MODEL');return tables[model]

def prerequisite_columns(plan,model):
 # Columns must come from the actual policy projection captured by the plan.
 for read in plan['selected_reads']:
  if read['model']==model:return read['columns']
 if model=='CustomerProfile':return ['id','user_id','status','revision','privacy_generation','display_name','avatar_media_id','city','country','created_at','updated_at','archived_at','state','mutation_transaction_id']
 if model=='ConsentPresentation':return ['id','user_id','content_revision_id','rendered_text','rendered_hash','render_version','context_owner','context_kind','context_id','action_owner','action','created_at','mutation_transaction_id']
 raise HeldFailure('PREREQUISITE_POLICY_COLUMNS_REQUIRED')

def rowset_sql(model,table,columns,identities):
 need(re.fullmatch(r'(app|platform)\.[a-z_]+',table) and all(re.fullmatch('[a-z_]+',c) for c in columns),'SOURCE_READ_IDENTIFIERS')
 return 'SELECT jsonb_build_object(\'model\','+quote(model)+",'ids',coalesce(jsonb_agg(observed.id::text ORDER BY observed.id::text COLLATE \"C\"),'[]'::jsonb)) FROM (SELECT "+','.join(columns)+' FROM '+table+' WHERE id IN ('+','.join(quote(x)+'::uuid' for x in identities)+')) observed;'

def ordinary_verdict(case,code,rows,ack,stderr):
 need(type(code) is int and code==0 and ack is True and type(rows) is list and all(type(x) is str for x in rows) and type(stderr) is str and stderr=='','CLEAN_READ_TERMINAL_REQUIRED')
 actual=[unique_json(row) for row in rows];exact(actual,case['expected_records'],'EXACT_READ_ROWSETS_REQUIRED')
 return {'status':'PASS','intended_stage':'SELECT','exact_rowsets':True,'observed_records':actual,'guard_diagnostic':None,'claim':case['claim']}

def restoration_identity(baseline,actual,allowlist,allow_disabled=False):
 """Only exact reviewed user-trigger enabled flags may differ during setup."""
 expected=deepcopy(baseline);observed=deepcopy(actual);allowed={(x['definition']['table'],x['definition']['name']) for x in allowlist}
 need(len(allowed)==15,'EXACT15_RESTORATION_ALLOWLIST')
 def triggers(document):
  collection=document['triggers'];need(type(collection) is list and len(collection)==412,'EXACT412_TRIGGER_ROWS')
  user=[t for t in collection if t['internal'] is False];need(len(user)==100,'EXACT100_USER_TRIGGERS')
  result={(t['table_name'],t['name']):t for t in user};need(len(result)==100,'UNIQUE100_TRIGGER_IDENTITIES');return result
 before,after=triggers(expected),triggers(observed);need(set(before)==set(after),'USER_TRIGGER_IDENTITY_SET')
 for identity in allowed:
  need(identity in before and before[identity]['enabled']=='O','SOURCE_TRIGGER_ORIGIN_ENABLED')
  need(after[identity]['enabled'] in (('O','D') if allow_disabled else ('O',)),'EXACT_ALLOWED_TRIGGER_FLAGS')
  after[identity]['enabled']='O'
 exact(observed,expected,'FULL_NATIVE_RESTORATION_IDENTITY')
 return {'all100_user_trigger_identities_match':True,'internal312_identities_unchanged':True,'exact15_only_flags_eligible':True,'source_function_owner_acl_dependencies_unchanged':True}
