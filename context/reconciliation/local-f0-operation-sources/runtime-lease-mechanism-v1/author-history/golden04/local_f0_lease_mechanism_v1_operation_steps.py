"""New closed four-login profile and binary synthetic protocol.
No canonical coordinator, role globals, default application, or SQL repair.
"""
import hashlib, ipaddress, json, re, secrets
from pathlib import Path
DB='wa_lease_mechanism_v1'
ROLES=('postgres','wa_lease_v1_app','wa_lease_v1_worker','wa_lease_v1_verifier')
LEAVES=ROLES[1:]
PREFIX='review-output/runtime-lease-branch-v1/synthetic/'
FILES=('setup-original.sql','install-nested.sql','restore-old.sql','pending-update.sql','direct-helper.sql','reset-pending-baseline.sql','worker-current.sql','worker-expired.sql','worker-wrong-secret.sql','worker-wrong-fence.sql','observe.sql','observe-preconditions.sql')
ACK='WA_LEASE_MECHANISM_V1_TERMINAL_ACK'
PROFILES={'OLD':'636ea713d4f835fa73c6f7d9006580a1266751cfd142f71c63525f2208d0a86a','NESTED':'94390b19ee1c24a819af8bf49465b63d8d8aa10a56ba109b83a2a2084eff8058'}
CASES=(('old-pending','OLD',LEAVES[0],'pending-update.sql',3,1),('nested-pending','NESTED',LEAVES[0],'pending-update.sql',0,3),('restored-old-pending','OLD',LEAVES[0],'pending-update.sql',3,1),('app-helper-before','OLD',LEAVES[0],'direct-helper.sql',3,1),('app-helper-after','NESTED',LEAVES[0],'direct-helper.sql',3,1),('worker-helper','NESTED',LEAVES[1],'direct-helper.sql',0,2),('verifier-helper','NESTED',LEAVES[2],'direct-helper.sql',0,2),('worker-current','NESTED',LEAVES[1],'worker-current.sql',0,5),('worker-expired','NESTED',LEAVES[1],'worker-expired.sql',3,3),('worker-wrong-secret','NESTED',LEAVES[1],'worker-wrong-secret.sql',3,3),('worker-wrong-fence','NESTED',LEAVES[1],'worker-wrong-fence.sql',3,3))
ROLE_SQL="('wa_lease_v1_app','wa_lease_v1_worker','wa_lease_v1_verifier')"
ALL_SQL="('postgres','wa_lease_v1_app','wa_lease_v1_worker','wa_lease_v1_verifier')"
LOGIN="SELECT jsonb_build_object('login',session_user,'current',current_user,'auth',system_user,'database',current_database(),'client',host(inet_client_addr()),'server',host(inet_server_addr()));"
HBA="SELECT coalesce(jsonb_agg(jsonb_build_object('rule_number',rule_number,'type',type,'database',database,'user_name',user_name,'address',address,'netmask',netmask,'auth_method',auth_method,'error',error) ORDER BY rule_number),'[]'::jsonb) FROM pg_hba_file_rules;"
GLOBAL="SELECT jsonb_build_object('login',session_user,'auth',system_user,'other_clients',(SELECT count(*) FROM pg_stat_activity WHERE backend_type='client backend' AND pid<>pg_backend_pid()));"
ABSENCE="SELECT jsonb_build_object('canonical_namespaces',(SELECT count(*) FROM pg_namespace WHERE nspname IN ('app','platform','platform_private')),'canonical_roles',(SELECT count(*) FROM pg_roles WHERE left(rolname,3)='wa_' AND rolname NOT IN "+ROLE_SQL+"),'migration_ledgers',(SELECT count(*) FROM pg_class WHERE relname='_prisma_migrations'));"
AUTHORITY="""SELECT jsonb_build_object(
'login',session_user,'auth',system_user,
'memberships',(SELECT count(*) FROM pg_auth_members m JOIN pg_roles p ON p.oid=m.member JOIN pg_roles g ON g.oid=m.roleid WHERE p.rolname IN """+ROLE_SQL+""" OR g.rolname IN """+ROLE_SQL+"""),
'owners',(SELECT jsonb_build_object('schema',nspowner='postgres'::regrole,'table',(SELECT relowner='postgres'::regrole FROM pg_class WHERE oid='wa_lease_branch_v1_repro.work'::regclass),'functions',(SELECT count(*)=2 AND bool_and(proowner='postgres'::regrole) FROM pg_proc WHERE pronamespace='wa_lease_branch_v1_repro'::regnamespace)) FROM pg_namespace WHERE nspname='wa_lease_branch_v1_repro'),
'roles',(SELECT jsonb_agg(jsonb_build_object('role',rolname,'login',rolcanlogin,'super',rolsuper,'inherit',rolinherit,'createdb',rolcreatedb,'createrole',rolcreaterole,'replication',rolreplication,'bypass',rolbypassrls,'usage',has_schema_privilege(rolname,'wa_lease_branch_v1_repro','USAGE'),'create',has_schema_privilege(rolname,'wa_lease_branch_v1_repro','CREATE'),'select',has_table_privilege(rolname,'wa_lease_branch_v1_repro.work','SELECT'),'insert',has_table_privilege(rolname,'wa_lease_branch_v1_repro.work','INSERT'),'update',has_table_privilege(rolname,'wa_lease_branch_v1_repro.work','UPDATE'),'delete',has_table_privilege(rolname,'wa_lease_branch_v1_repro.work','DELETE'),'truncate',has_table_privilege(rolname,'wa_lease_branch_v1_repro.work','TRUNCATE'),'helper',has_function_privilege(rolname,'wa_lease_branch_v1_repro.lease_secret_matches(text)','EXECUTE'),'guard',has_function_privilege(rolname,'wa_lease_branch_v1_repro.guard()','EXECUTE'),'columns',(SELECT jsonb_object_agg(attname,has_column_privilege(rolname,'wa_lease_branch_v1_repro.work',attname,'UPDATE')) FROM pg_attribute WHERE attrelid='wa_lease_branch_v1_repro.work'::regclass AND attnum>0 AND NOT attisdropped)) ORDER BY rolname) FROM pg_roles WHERE rolname IN """+ROLE_SQL+"""));"""
STATE="""SELECT jsonb_agg(jsonb_build_object('id',id,
'row_sha256',encode(sha256(convert_to(to_jsonb(w)::text,'UTF8')),'hex'),
'pending_sha256',encode(sha256(convert_to((to_jsonb(w)||jsonb_build_object('state','pending','lease_token_hash',NULL,'lease_expires_at',NULL))::text,'UTF8')),'hex'),
'rescheduled_sha256',encode(sha256(convert_to((to_jsonb(w)||jsonb_build_object('next_attempt_at','2026-01-02T00:00:00+00:00'::timestamptz))::text,'UTF8')),'hex'))
ORDER BY id) FROM wa_lease_branch_v1_repro.work w;"""
SETUP_STATUS="SELECT jsonb_build_object('roles',(SELECT count(*) FROM pg_roles WHERE rolname IN "+ROLE_SQL+"),'schema',(SELECT count(*) FROM pg_namespace WHERE nspname='wa_lease_branch_v1_repro'),'table',(SELECT count(*) FROM pg_class c JOIN pg_namespace n ON n.oid=c.relnamespace WHERE n.nspname='wa_lease_branch_v1_repro' AND c.relname='work'),'functions',(SELECT count(*) FROM pg_proc p JOIN pg_namespace n ON n.oid=p.pronamespace WHERE n.nspname='wa_lease_branch_v1_repro'));"
RECIPES={'LOGIN':LOGIN,'HBA':HBA,'GLOBAL':GLOBAL,'ABSENCE':ABSENCE,'AUTHORITY':AUTHORITY,'STATE':STATE,'SETUP_STATUS':SETUP_STATUS}
COLS=('id','state','fence','attempt_count','lease_token_hash','lease_expires_at','effect_receipt_id','next_attempt_at')

class Held(Exception):
 def __init__(self,code):self.code=code;super().__init__(code)
def require(value,code):
 if not value:raise Held(code)
def sha(raw):return hashlib.sha256(raw).hexdigest()
def decode(raw):
 require(type(raw)is bytes and len(raw)<=65536,'BOUNDED_JSON')
 def pairs(items):
  d={}
  for k,v in items:require(k not in d,'DUPLICATE_JSON');d[k]=v
  return d
 try:return json.loads(raw,object_pairs_hook=pairs,parse_constant=lambda _:(_ for _ in ()).throw(Held('NONFINITE_JSON')))
 except (ValueError,UnicodeError,RecursionError):raise Held('MALFORMED_JSON')from None
def exact_keys(v,keys):return type(v)is dict and set(v)==set(keys)
def records(result):
 require(type(result.returncode)is int and type(result.stdout)is bytes and type(result.stderr)is bytes and len(result.stdout)<=65536 and len(result.stderr)<=65536,'TYPED_BOUNDED_REPLY')
 try:lines=result.stdout.decode('utf8','strict').splitlines()
 except UnicodeError:raise Held('OUTPUT_UTF8')from None
 require(all(line and len(line)<=16384 for line in lines),'OUTPUT_FRAME')
 ack=bool(lines and lines[-1]==ACK)
 require(ACK not in lines[:-1],'DUPLICATE_ACK')
 return lines[:-1]if ack else lines,ack

def global_zero(o,safety=False):
 r=o.call(o.psql_args('postgres')+['-f','-','-c','\\echo '+ACK],GLOBAL.encode()+b'\n')
 rows,ack=records(r);v=decode(rows[0].encode())if len(rows)==1 else None
 passed=r.returncode==0 and r.stderr==b''and ack and exact_keys(v,('login','auth','other_clients'))and v['login']=='postgres'and v['auth']=='scram-sha-256:postgres'and type(v['other_clients'])is int and v['other_clients']==0
 o.report['closures'].append({'original_grantor':True,'integer_zero':passed,'confirmed':passed});o.persist();require(passed,'GLOBAL_BACKENDS_UNCONFIRMED')
 if not safety:require(o.report['evidence_complete']is True,'EVIDENCE_WRITE_UNCONFIRMED')
 return True

def raw(o,role,payload=None,file=None,wrong=False,closure=True,safety=False,profile=None):
 """Exactly one binary client; save safe primary before any later observation."""
 require(role in ROLES and ((type(payload)is bytes)^(file is not None)),'BINARY_SESSION_PROFILE')
 if file is not None:
  require(file in FILES and file in o.staged,'UNREGISTERED_SYNTHETIC_FILE')
  path='/run/wa-secrets/sql/'+file
  actual=o.ok(['exec',o.cid,'sh','-ceu','sha256sum '+path+'; wc -c < '+path+'; stat -c "%a:%u:%g" '+path])
  require(actual==(o.staged[file]['sha256']+'  '+path+'\n'+str(o.staged[file]['length'])+'\n400:0:0\n').encode(),'PRE_EXECUTION_FILE_BYTES')
 args=o.psql_args(role,wrong)+['-f',('/run/wa-secrets/sql/'+file)if file is not None else'-','-c','\\echo '+ACK]
 result=None;first=None
 try:
  result=o.call(args,payload)
  if file is not None:
   # Fixed safe projection occurs before closure observers/retention/verdicts.
   # Unexpected strings and dictionaries never become evidence.
   safe={'file':file,'role':role,'reply_received':True,'exit_known':type(result.returncode)is int,'ack':False,'record_count':None,'diagnostic':None}
   o.report['received_operation']=safe
   rows,ack=records(result);safe['ack']=ack;safe['record_count']=len(rows)
   if profile in PROFILES and result.returncode==3:
    kind='WORKER_GUARD'if file.startswith('worker-')else'PRIVATE_HELPER'
    safe['diagnostic']=diagnostic(result.stderr,file,kind,profile)
   o.persist()
 except BaseException as e:
  first=e;o.fail(e.code if hasattr(e,'code')else'BINARY_SESSION_UNEXPECTED');o.persist()
 finally:
  if closure:
   try:global_zero(o,safety=True)
   except BaseException as e:
    if first is None:first=e;o.fail(e.code if hasattr(e,'code')else'CLOSURE_UNEXPECTED');o.persist()
 if first is not None:raise first
 if not safety:require(o.report['evidence_complete']is True,'EVIDENCE_WRITE_UNCONFIRMED')
 return result

def query(o,kind,roles=None,safety=False):
 require(kind in RECIPES or kind=='VERIFIERS','UNREGISTERED_QUERY')
 if kind=='VERIFIERS':
  require(roles in (('postgres',),ROLES),'VERIFIER_ROLE_SET');sql="SELECT jsonb_object_agg(rolname,rolcanlogin AND rolpassword LIKE 'SCRAM-SHA-256$%') FROM pg_authid WHERE rolname IN ("+','.join("'"+r+"'"for r in roles)+");"
 else:sql=RECIPES[kind]
 r=raw(o,'postgres',sql.encode()+b'\n',closure=kind!='GLOBAL',safety=safety);rows,ack=records(r);require(r.returncode==0 and r.stderr==b''and ack and len(rows)==1,'QUERY_TERMINAL')
 return decode(rows[0].encode())

def login_comparison(v,role):
 expected={'login':role,'current':role,'auth':'scram-sha-256:'+role,'database':DB,'client':'127.0.0.1','server':'127.0.0.1'}
 return {'fields':exact_keys(v,expected),'types':type(v)is dict and all(type(v.get(k))is str for k in expected),**{k:type(v)is dict and type(v.get(k))is str and v[k]==wanted for k,wanted in expected.items()}}

def hba_selections(rows,roles):
 require(type(rows)is list and 0<len(rows)<=128,'HBA_ROWS')
 seen=set()
 for r in rows:
  require(exact_keys(r,('rule_number','type','database','user_name','address','netmask','auth_method','error'))and type(r['rule_number'])is int and 0<r['rule_number']<=10000 and r['rule_number']not in seen and r['error']is None,'HBA_ROW');seen.add(r['rule_number'])
  require(r['type']in('local','host')and type(r['database'])is list and r['database']and type(r['user_name'])is list and r['user_name']and all(type(x)is str and x in('all','replication',DB)for x in r['database'])and all(type(x)is str and x in('all',*ROLES)for x in r['user_name']),'HBA_UNSUPPORTED')
 selected=[]
 for address in ('127.0.0.1','::1'):
  for role in roles:
   match=None
   for r in sorted(rows,key=lambda x:x['rule_number']):
    if r['type']=='local':continue
    if 'all'not in r['database']and DB not in r['database']:continue
    if 'all'not in r['user_name']and role not in r['user_name']:continue
    try:
     bits=bin(int(ipaddress.ip_address(r['netmask'])))[2:].zfill(ipaddress.ip_address(r['netmask']).max_prefixlen);require('01'not in bits,'HBA_MASK')
     net=ipaddress.ip_network(r['address']+'/'+str(bits.count('1')),strict=False)
    except (ValueError,TypeError):raise Held('HBA_ADDRESS')from None
    if ipaddress.ip_address(address)in net:match=r;break
   require(match is not None and match['auth_method']=='scram-sha-256','HBA_FIRST_SCRAM')
   selected.append({'role':role,'address':address,'rule_number':match['rule_number'],'method':'scram-sha-256'})
 return selected

def auth_one(o,role):
 r=raw(o,role,LOGIN.encode()+b'\n');rows,ack=records(r);v=decode(rows[0].encode())if len(rows)==1 else None;checks=login_comparison(v,role)
 item={'role':role,'correct_reply_received':True,'correct_exit_zero':r.returncode==0,'ack':ack,'stderr_empty':r.stderr==b'','comparisons':checks,'wrong_rejected':False}
 o.report['authentication'].append(item);o.persist();require(item['correct_exit_zero']and ack and item['stderr_empty']and all(checks.values()),'AUTH_SCRAM_IDENTITY')
 wrong=secrets.token_hex(32);o.secrets.append(wrong);payload=('127.0.0.1:5432:'+DB+':'+role+':'+wrong+'\n').encode()
 try:
  out=o.ok(['exec','-i',o.cid,'sh','-ceu','umask 077; cat > /run/wa-secrets/wrong-pgpass; chmod 600 /run/wa-secrets/wrong-pgpass; stat -c "%a:%u:%g" /run/wa-secrets/wrong-pgpass'],payload)
  require(out==b'600:0:0\n','WRONG_PGPASS_OWNER')
  r=raw(o,role,LOGIN.encode()+b'\n',wrong=True)
  try:text=r.stderr.decode('utf8','strict')
  except UnicodeError:raise Held('WRONG_AUTH_UTF8')from None
  pattern=r'psql: error: connection to server at "127\.0\.0\.1", port 5432 failed: FATAL:  password authentication failed for user "'+role+r'"\n'
  item['wrong_rejected']=type(r.returncode)is int and r.returncode==2 and r.stdout==b''and re.fullmatch(pattern,text)is not None;o.persist();require(item['wrong_rejected'],'WRONG_PASSWORD_REQUIRED')
 finally:o.ok(['exec',o.cid,'rm','--','/run/wa-secrets/wrong-pgpass'])

def authenticate(o,roles):
 require(roles in (('postgres',),ROLES),'CLOSED_AUTH_PROFILE');o.stage('AUTHENTICATION')
 selections=hba_selections(query(o,'HBA'),roles);verifiers=query(o,'VERIFIERS',roles);require(exact_keys(verifiers,roles)and all(v is True for v in verifiers.values()),'SCRAM_VERIFIERS')
 o.record('AUTH_PROFILE',{'roles':list(roles),'hba_selections':selections,'verifiers_all_scram':True})
 for role in roles:auth_one(o,role)

def provision(o):
 sql=''.join("ALTER ROLE "+role+" PASSWORD '"+o.passwords[role]+"';\n"for role in LEAVES)
 # Dynamic secret SQL exists only in this fixed three-role administrative
 # transport. It is never hashed, echoed, placed in argv/env or persisted.
 r=raw(o,'postgres',sql.encode());rows,ack=records(r);require(r.returncode==0 and r.stderr==b''and ack and not rows,'ROLE_CREDENTIAL_PROVISION')
 o.record('CREDENTIAL_PROVISION',{'independent_three_logins':True,'secret_sql_retained':False})

def stage_files(o):
 require(o.kernel is True,'STAGING_KERNEL_FIRST')
 for name in FILES:
  rawbytes=o.source_blobs[PREFIX+name];wanted=o.m['packet_files_sha256'][PREFIX+name];require(sha(rawbytes)==wanted,'HOST_FILE_HASH')
  path='/run/wa-secrets/sql/'+name
  script='umask 077; mkdir -p /run/wa-secrets/sql; cat > '+path+'; chmod 400 '+path+'; sha256sum '+path+'; wc -c < '+path+'; stat -c "%a:%u:%g" '+path
  out=o.ok(['exec','-i',o.cid,'sh','-ceu',script],rawbytes)
  expected=(wanted+'  '+path+'\n'+str(len(rawbytes))+'\n400:0:0\n').encode();require(out==expected,'BINARY_LINUX_FILE_BYTES')
  o.staged[name]={'sha256':wanted,'length':len(rawbytes)}
 o.record('BINARY_STAGING',{'files':len(FILES),'host_linux_hash_length_equal':True,'root0400':True})

def authority(v):
 require(exact_keys(v,('login','auth','memberships','owners','roles'))and v['login']=='postgres'and v['auth']=='scram-sha-256:postgres'and type(v['memberships'])is int and v['memberships']==0,'FIXTURE_GRANTOR_MEMBERSHIPS')
 require(exact_keys(v['owners'],('schema','table','functions'))and all(x is True for x in v['owners'].values()),'FIXTURE_ORIGINAL_OWNERS')
 require(type(v['roles'])is list and len(v['roles'])==3 and [r.get('role')for r in v['roles']]==sorted(LEAVES),'FIXTURE_ROLE_SET')
 for row in v['roles']:
  require(exact_keys(row,('role','login','super','inherit','createdb','createrole','replication','bypass','usage','create','select','insert','update','delete','truncate','helper','guard','columns')),'FIXTURE_ROLE_FIELDS')
  expected={'login':True,'super':False,'inherit':False,'createdb':False,'createrole':False,'replication':False,'bypass':False,'usage':True,'create':False,'select':True,'insert':False,'update':False,'delete':False,'truncate':False,'helper':row['role']in LEAVES[1:],'guard':False}
  require(all(type(row[k])is bool and row[k]is value for k,value in expected.items()),'FIXTURE_ROLE_PRIVILEGE')
  allowed={'next_attempt_at'}if row['role']==LEAVES[0]else({'state','lease_token_hash','lease_expires_at'}if row['role']==LEAVES[1]else set())
  require(exact_keys(row['columns'],COLS)and all(type(v)is bool and v is(k in allowed)for k,v in row['columns'].items()),'FIXTURE_COLUMN_PRIVILEGE')
 return True

def absence(o,safety=False):
 v=query(o,'ABSENCE',safety=safety);require(exact_keys(v,('canonical_namespaces','canonical_roles','migration_ledgers'))and all(type(x)is int and x==0 for x in v.values()),'CANONICAL_OBJECTS_MUST_BE_ABSENT')
 o.record('CANONICAL_ABSENCE',{'all_absent':True},safety)

def finalize(o):
 """Read-only authority and zero-client proof, never canonical TEMP3 cleanup."""
 o.report['stage']='SYNTHETIC_GRANTOR_FINALIZATION'
 global_zero(o,safety=True)
 if o.setup_attempted:
  status=query(o,'SETUP_STATUS',safety=True)
  require(exact_keys(status,('roles','schema','table','functions'))and all(type(x)is int for x in status.values()),'SETUP_STATUS_TYPES')
  require(status in ({'roles':0,'schema':0,'table':0,'functions':0},{'roles':3,'schema':1,'table':1,'functions':2}),'SETUP_TRANSACTION_ATOMICITY')
 else:status={'roles':0}
 if status['roles']==3:
  authority(query(o,'AUTHORITY',safety=True));absence(o,safety=True)
  o.record('FIXTURE_GRANTOR_FINALIZATION',{'actual_original_grantor':'postgres','read_only_authority_verified':True,'synthetic_memberships_zero':True,'leaf_create_false':True,'canonical_temp_memberships':'NOT_CREATED_NOT_APPLICABLE'},safety=True)
 global_zero(o,safety=True)

def admin_file(o,name):
 require(name in ('setup-original.sql','install-nested.sql','restore-old.sql'),'CLOSED_ADMIN_FILE')
 if name=='setup-original.sql':o.setup_attempted=True
 r=raw(o,'postgres',file=name);rows,ack=records(r);require(r.returncode==0 and ack and not rows and r.stderr==b'','ADMIN_FILE_TERMINAL')
 if name=='setup-original.sql':o.setup_done=True
 o.record('SOURCE_VARIANT_INSTALL',{'file':name,'exact_bytes':True,'closed':True,'ack':True})

def observer(o,name):
 require(name in ('observe.sql','observe-preconditions.sql'),'CLOSED_OBSERVER');r=raw(o,'postgres',file=name);rows,ack=records(r);require(r.returncode==0 and ack and r.stderr==b''and len(rows)==1,'OBSERVER_TERMINAL');return decode(rows[0].encode())

def observations(o,profile,expected,baseline=None):
 global_zero(o);authority(query(o,'AUTHORITY'));absence(o)
 p=observer(o,'observe-preconditions.sql')
 require(exact_keys(p,('guard_source','lease_fixture'))and exact_keys(p['guard_source'],('body_sha256','original_grantor_owner','invoker','volatile','unsafe','not_strict','cost100','search_path_exact')),'SOURCE_PROFILE_FIELDS')
 require(p['guard_source']['body_sha256']==PROFILES[profile]and all(p['guard_source'][k]is True for k in p['guard_source']if k!='body_sha256'),'NATIVE_GUARD_BODY_PROFILE')
 require(type(p['lease_fixture'])is list and len(p['lease_fixture'])==5,'LEASE_FIXTURE_SET')
 for i,v in enumerate(p['lease_fixture'],1):
  require(exact_keys(v,('id','lease_hash_matches_public_dummy','expired'))and type(v['id'])is int and v['id']==i,'LEASE_FIXTURE_ID')
  null=i==1 or(i==2 and expected['worker_done'])
  require(v['lease_hash_matches_public_dummy']is(None if null else True)and v['expired']is(None if null else i==3),'LEASE_FIXTURE_CURRENTNESS')
 v=observer(o,'observe.sql');require(exact_keys(v,('rows','app_helper_execute','worker_helper_execute','verifier_helper_execute','trigger_enabled'))and v['app_helper_execute']is False and v['worker_helper_execute']is True and v['verifier_helper_execute']is True and v['trigger_enabled']is True,'HELPER_ACL_AND_ENABLED_TRIGGER')
 require(type(v['rows'])is list and len(v['rows'])==5,'FIVE_COMPLETE_ROWS')
 for i,row in enumerate(v['rows'],1):
  null=i==1 or(i==2 and expected['worker_done']);pending=null
  ts='2026-01-02T00:00:00+00:00'if i==1 and expected['rescheduled']else'2026-01-01T00:00:00+00:00'
  wanted={'id':i,'state':'pending'if pending else'leased','fence':0 if i==1 else 7,'attempt_count':0 if i==1 else 1,'lease_fields_null':null,'effect_absent':True,'next_attempt_at':ts}
  require(exact_keys(row,wanted)and all(type(row[k])is type(w)and row[k]==w for k,w in wanted.items()),'FIVE_ROW_COHERENCE')
 fingerprints=query(o,'STATE');require(type(fingerprints)is list and len(fingerprints)==5,'FIVE_FULL_FINGERPRINTS')
 for i,row in enumerate(fingerprints,1):
  require(exact_keys(row,('id','row_sha256','pending_sha256','rescheduled_sha256'))and type(row['id'])is int and row['id']==i and all(type(row[k])is str and re.fullmatch('[0-9a-f]{64}',row[k])for k in row if k!='id'),'FINGERPRINT_TYPES')
  if baseline is not None:
   key='rescheduled_sha256'if i==1 and expected['rescheduled']else'pending_sha256'if i==2 and expected['worker_done']else'row_sha256'
   require(row['row_sha256']==baseline[i-1][key],'COMPLETE_STATE_CHANGE_BOUNDARY')
 o.record('COMPLETE_STATE',{'profile':profile,'guard_body_sha256':PROFILES[profile],'row_count':5,'complete_state_coherent':True,'trigger_enabled':True,'all_other_rows_exact':True,'row_sha256':[r['row_sha256']for r in fingerprints]})
 return fingerprints

def diagnostic(stderr,file,kind,profile):
 safe={'sqlstate':None,'diagnostic':'UNCONFIRMED','single_header':False,'source_frame':False,'native_location':False,'body_sha256':PROFILES[profile],'line':None}
 if type(stderr)is not bytes or len(stderr)>16384:return safe
 try:text=stderr.decode('utf8','strict')
 except UnicodeError:return safe
 # Count malformed and multiple severity occurrences, not merely valid headers.
 if len(re.findall(r'\b(?:ERROR|FATAL|PANIC|WARNING)\b',text))!=1:return safe
 lines=text.splitlines()
 header=re.fullmatch(r'psql:/run/wa-secrets/sql/'+re.escape(file)+r':([1-9][0-9]{0,4}): ERROR:  (42501|P0001): (.+)',lines[0])if lines else None
 if header is None:return safe
 safe['single_header']=True;state,message=header[2],header[3]
 location=re.fullmatch(r'LOCATION:  (aclcheck_error, aclchk\.c|exec_stmt_raise, pl_exec\.c):([1-9][0-9]{0,5})',lines[-1])if len(lines)>1 else None
 if location is None:return safe
 if kind=='PRIVATE_HELPER':
  expected=['CONTEXT:  PL/pgSQL function wa_lease_branch_v1_repro.guard() line 3 at IF']if file=='pending-update.sql'else[]
  good=state=='42501'and message=='permission denied for function lease_secret_matches'and location[1]=='aclcheck_error, aclchk.c'and lines[1:-1]==expected
  frame=bool(expected);line=3 if frame else None
 elif kind=='WORKER_GUARD':
  good=state=='P0001'and message=='expired or foreign worker'and location[1]=='exec_stmt_raise, pl_exec.c'and lines[1:-1]==['CONTEXT:  PL/pgSQL function wa_lease_branch_v1_repro.guard() line 7 at RAISE']and profile=='NESTED'
  frame=True;line=7
 else:return safe
 if good:safe.update(sqlstate=state,diagnostic=kind,source_frame=frame,native_location=True,line=line)
 return safe

def case(o,entry):
 cid,profile,role,file,exitcode,count=entry;o.stage('CASE_'+cid.replace('-','_').upper());auth_one(o,role)
 safe={'case':cid,'role':role,'profile':profile,'file_sha256':o.staged[file]['sha256'],'reply_received':False,'exit_known':False,'exit_matches':False,'ack':False,'record_count':None,'markers_match':False,'operation_closed':False,'diagnostic':None}
 o.report['current']=safe;o.persist();r=None;first=None
 try:
  r=raw(o,role,file=file,profile=profile);safe['operation_closed']=True;safe['reply_received']=True;safe['exit_known']=type(r.returncode)is int;safe['exit_matches']=safe['exit_known']and r.returncode==exitcode
  rows,ack=records(r);safe.update(ack=ack,record_count=len(rows))
  if exitcode:
   kind='WORKER_GUARD'if cid.startswith('worker-')else'PRIVATE_HELPER';safe['diagnostic']=diagnostic(r.stderr,file,kind,profile)
  else:safe['diagnostic']={'sqlstate':None,'diagnostic':'NONE','stderr_empty':r.stderr==b''}
  if file=='pending-update.sql':safe['markers_match']=bool(rows and rows[0]=='LEASE_V1_BEFORE'and(rows[-1]=='LEASE_V1_AFTER'if not exitcode else'LEASE_V1_AFTER'not in rows))
  elif file.startswith('worker-'):safe['markers_match']=rows[:3]==['t','t','LEASE_V1_BEFORE']and(rows[-1]=='LEASE_V1_AFTER'if not exitcode else'LEASE_V1_AFTER'not in rows)
  else:safe['markers_match']=rows==(['t']if exitcode else['t','t'])
  o.persist();require(safe['exit_matches']and ack is(exitcode==0)and len(rows)==count and safe['markers_match'],'CASE_TERMINAL_MARKERS')
  if exitcode:require(safe['diagnostic']['diagnostic']==kind and safe['diagnostic']['sqlstate']==('P0001'if kind=='WORKER_GUARD'else'42501'),'CASE_INTENDED_DIAGNOSTIC')
  else:
   require(r.stderr==b'','SUCCESS_STDERR')
   if file=='pending-update.sql':
    got=decode(rows[1].encode());wanted={'id':1,'state':'pending','fence':0,'attempt_count':0,'lease_fields_null':True,'effect_absent':True,'next_attempt_at':'2026-01-02T00:00:00+00:00'}
    require(exact_keys(got,wanted)and all(type(got[k])is type(w)and got[k]==w for k,w in wanted.items()),'PENDING_RETURN_EXACT')
   if file=='worker-current.sql':require(rows[3]=='2|pending|7|1','WORKER_RETURN_EXACT')
 except BaseException as e:
  first=e;o.fail(e.code if hasattr(e,'code')else'CASE_UNEXPECTED');o.persist()
 if first is not None:raise first
 safe['status']='PASS_SYNTHETIC_ONLY';o.report['cases'].append(dict(safe));o.persist()

def execute(o):
 o.stage('BOOTSTRAP_AUTH');authenticate(o,('postgres',));absence(o);stage_files(o);admin_file(o,'setup-original.sql');provision(o);authenticate(o,ROLES);finalize(o)
 expected={'rescheduled':False,'worker_done':False};baseline=observations(o,'OLD',expected)
 for entry in CASES:
  cid=entry[0]
  if cid in ('nested-pending','app-helper-after'):admin_file(o,'install-nested.sql')
  if cid=='restored-old-pending':
   r=raw(o,LEAVES[0],file='reset-pending-baseline.sql');rows,ack=records(r);require(r.returncode==0 and r.stderr==b''and ack and rows==['1|2026-01-01 00:00:00+00'],'PLANNED_RESET_TERMINAL')
   expected['rescheduled']=False;observations(o,'NESTED',expected,baseline);admin_file(o,'restore-old.sql')
  observations(o,entry[1],expected,baseline);case(o,entry)
  if cid=='nested-pending':expected['rescheduled']=True
  if cid=='worker-current':expected['worker_done']=True
  observations(o,entry[1],expected,baseline)
 require(len(o.report['cases'])==11,'ELEVEN_CASES_REQUIRED')
 o.record('MECHANISM_COMPLETE',{'cases':11,'old_nested_restored':True,'app_helper_acl_unchanged':True,'worker_contrasts':4,'canonical_qualification':False})

