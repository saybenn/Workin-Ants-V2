"""Offline accepted SixRead child composition at subprocess boundaries only.

The accepted coordinate/load_inputs/coordinator and frozen CTX Session methods
are never replaced. This is a source-derived transport model, not DB proof.
No historical runtime OUT, credentials or raw output is used as a fixture.
"""
from collections import Counter
from contextlib import ExitStack
from copy import deepcopy
import hashlib
import json
from pathlib import Path
import queue
import re
import runpy
import socket
import subprocess
import sys
import tempfile
import threading
import time
import types
import unittest
from unittest.mock import patch

TASK=Path(__file__).resolve().parent
ROOT=TASK/'workinants-correction-pass'
CHILD='scripts/sql-review/run-scoped-read-companion-rehearsal.py'
CHILD_SHA='4160760bb319e4389182ed5cfcb6c0fae028480bd3d6d418be0130e8156a0f15'
PACKET_PATH='review-output/scoped-read-companion-rehearsal/fixtures.json'
PACKET_SHA='7f5bd6e713a1f0eaf330c2acf0267cd45aa2e8f47467e03d6f4c4c6dc754420c'
ACK='WA_CTX01_ACK|'
TUPLE='WA_CTX01_TUPLE|'
CID='a'*64
CANARY='SIX_READ_PROCESS_PRIVATE_CANARY'
STAMP='2026-11-19 12:00:00+00'
RETURN_STAMP='2026-11-19T12:00:00.001+00:00'
EXPECTED_STAGES={'GLOBAL_BACKEND_CLOSURE':152,'IMMUTABLE_ISSUER_RETENTION':213,
 'EXACT_EIGHT_TRIGGER_RESTORATION':74,'BOUND_OPERATION':71,'SEPARATE_ISSUER_COMMIT':71,
 'PRE_FIXTURE_NATIVE_PARITY':1,'POST_FIXTURE_NATIVE_PARITY':1,
 'FINAL_NATIVE_PARITY':1,'FINALLY_FULL_NATIVE_PARITY':1,
 'SYNTHETIC_EXISTING_ROWS_ONLY':1}

def canonical(value):return json.dumps(value,sort_keys=True,separators=(',',':'),ensure_ascii=False,allow_nan=False)
def sha(raw):return hashlib.sha256(raw).hexdigest()
def digest(value):return sha(canonical(value).encode())
def forbid_actual_runtime():
 def audit(event,args):
  if event in {'subprocess.Popen','os.system','os.posix_spawn','os.spawn','socket.connect','socket.connect_ex','socket.bind','socket.getaddrinfo'}:
   raise AssertionError('ACTUAL_PROCESS_NETWORK_FORBIDDEN')
 sys.addaudithook(audit)
def admitted_child():
 raw=(ROOT/CHILD).read_bytes()
 if sha(raw)!=CHILD_SHA:raise AssertionError('ACCEPTED_CHILD_DRIFT')
 return runpy.run_path(str(ROOT/CHILD))
def fixture_packet():
 raw=(ROOT/PACKET_PATH).read_bytes()
 if sha(raw)!=PACKET_SHA:raise AssertionError('ACCEPTED_PACKET_DRIFT')
 return json.loads(raw)
def literal(value):
 found=re.match(r"'((?:[^']|'')*)'",value)
 if not found:raise AssertionError('EXPECTED_SQL_LITERAL')
 return found[1].replace("''", "'")
def split_sql(value):
 result=[];start=0;depth=0;quoted=False;i=0
 while i<len(value):
  char=value[i]
  if quoted:
   if char=="'":
    if i+1<len(value) and value[i+1]=="'":i+=1
    else:quoted=False
  elif char=="'":quoted=True
  elif char in '([':depth+=1
  elif char in ')]':depth-=1
  elif char==',' and depth==0:result.append(value[start:i].strip());start=i+1
  i+=1
 if quoted or depth:raise AssertionError('UNBALANCED_SQL_TRANSPORT_INPUT')
 result.append(value[start:].strip());return result

class OutputPipe:
 """Bounded line/chunk queues consumed by the actual CTX reader threads."""
 def __init__(self):self.items=queue.Queue();self.closed=False
 def feed(self,text):
  if text:self.items.put(text)
 def finish(self):
  if not self.closed:self.closed=True;self.items.put(None)
 def readline(self,size=-1):
  item=self.items.get(timeout=5)
  if item is None:self.items.put(None);return ''
  return item
 def read(self,size=-1):return self.readline(size)

class InputPipe:
 def __init__(self,process):self.process=process;self.buffer='';self.closed=False
 def write(self,text):
  if self.closed:raise ValueError('CLOSED_STDIN')
  self.buffer+=text;return len(text)
 def flush(self):
  text=self.buffer;self.buffer=''
  if text:self.process.exchange(text)
 def close(self):
  if not self.closed:self.flush();self.closed=True

class Process:
 def __init__(self,world,args,**options):
  if options.get('shell') is not False or not options.get('text'):raise AssertionError('PROCESS_CONTRACT')
  self.world=world;self.args=list(args);self.role=world.role(args)
  self.number=len(world.processes)+1;self.pid=4000+self.number
  self.returncode=None;self.done=threading.Event();self.stdout=OutputPipe();self.stderr=OutputPipe();self.stdin=InputPipe(self)
  self.backend={'login':self.role,'current_user':self.role,'database':'wa_p0c_rehearsal',
   'isolation':'read committed','pid':str(self.pid),'xid':str(10000+self.number),'started':STAMP,'clock':STAMP}
  self.bound=None;self.active=False;self.closed_observed=False;world.processes.append(self)
  world.events.append({'kind':'popen','role':self.role,'ordinal':self.number})
 def poll(self):return self.returncode
 def wait(self,timeout=None):
  if not self.done.wait(min(timeout or 5,5)):raise subprocess.TimeoutExpired('MOCK_PSQL',timeout)
  return self.returncode
 def finish(self,code):
  self.returncode=code;self.stdout.finish();self.stderr.finish();self.done.set()
 def terminate(self):self.finish(143)
 def kill(self):self.finish(137)
 def exchange(self,text):
  self.world.events.append({'kind':'session_input','role':self.role,'ordinal':self.number,'shape':self.world.shape(text)})
  if '\\q' in text:self.active=False;self.finish(0);return
  match=re.search(r"\nSELECT '(WA_CTX01_ACK\|[0-9a-f]{32})';\n\Z",text)
  if not match:raise AssertionError('ACTUAL_SESSION_ACK_CONTRACT')
  body=text[:match.start()];ack=match[1];rows=[]
  if body.startswith('BEGIN ISOLATION LEVEL '):self.active=True
  elif TUPLE in body:rows=[TUPLE+canonical(self.backend)]
  elif body.startswith('INSERT INTO platform.database_action_grant '):
   row=self.world.insert(body,self);rows=[canonical({'created_at':RETURN_STAMP})]
  elif body.startswith('SELECT pg_current_xact_id()::text='):
   rows=['t' if literal(body.split('=',1)[1])==self.backend['xid'] else 'f']
  elif body.startswith("SELECT 'WA_SRC_BIND_"):rows=re.findall(r"SELECT '([^']+)';",body)
  elif body.startswith('SELECT platform_private.bind_request_context('):
   secret=re.fullmatch(r"SELECT platform_private\.bind_request_context\('([0-9a-f]{64})'\);",body)[1]
   token=sha(bytes.fromhex(secret));self.bound=self.world.grants.get(token)
   if self.bound is None:raise AssertionError('BIND_BEFORE_ACTUAL_ISSUER_INSERT')
   value=self.bound['values'];principal=literal(value['principal_user_id'])
   if principal==self.world.packet['ids']['User'][1] and value['security_generation']=='0':
    self.stderr.feed(self.world.binder_diagnostic());self.finish(3);return
  elif body.startswith("SELECT 'WA_SRC_BEFORE_"):
   name=re.search(r"SELECT 'WA_SRC_BEFORE_([^']+)';",body)[1]
   self.world.read_ordinal+=1
   if self.world.fail_read_ordinal==self.world.read_ordinal:
    self.stdout.feed('WA_SRC_BEFORE_'+name+'\n');self.stderr.feed(CANARY);self.finish(3);return
   rows=self.world.project(body,self.bound)
  elif 'DISABLE TRIGGER owner_commit;' in body or 'ENABLE TRIGGER owner_commit;' in body:
   self.world.fixture_transaction(body)
  else:raise AssertionError('UNREGISTERED_SESSION_SQL')
  if body.rstrip().endswith('COMMIT;'):self.active=False
  for row in rows:self.stdout.feed(row+'\n')
  self.stdout.feed(ack+'\n')

class World:
 """Models SQL result transport from source facts and actual received SQL.

 No coordinator object, factory, private instances, expected case counts or
 expected verdicts is read by this model. The case packet only supplies source
 declarations (model maps, fixture IDs and prepared SQL bindings).
 """
 def __init__(self,plan,native,packet=None):
  self.plan=deepcopy(plan);self.native=deepcopy(native);self.packet=deepcopy(packet or fixture_packet())
  self.processes=[];self.events=[];self.grants={};self.seeded=False;self.disabled=False;self.read_ordinal=0;self.fail_read_ordinal=None
  self.acl=json.loads((ROOT/'context/reconciliation/foundation-sql-draft-access.json').read_bytes())
  self.application=(ROOT/'review-output/foundation-application.review.sql').read_text(encoding='utf8')
  self.sql={name:(ROOT/'review-output/scoped-read-companion-rehearsal'/name).read_text(encoding='utf8') for name in self.packet['prepared_files_sha256']}
  self.protocol=runpy.run_path(str(ROOT/'scripts/scoped_read_companion_protocol.py'))
  self.container,self.volume,self.context,self.image=self.inspect_facts()
 def shape(self,text):
  if 'INSERT INTO platform.database_action_grant ' in text:return 'ISSUER_INSERT21'
  if 'bind_request_context(' in text:return 'BINDER'
  if 'WA_SRC_BEFORE_' in text:return 'READ_PROJECTION'
  if 'DISABLE TRIGGER owner_commit;' in text:return 'FIXTURE'
  if 'ENABLE TRIGGER owner_commit;' in text:return 'RESTORE'
  if TUPLE in text:return 'CAPTURE'
  if '\\q' in text:return 'CLOSE'
  if text.startswith('BEGIN ISOLATION'):return 'BEGIN'
  if 'WA_SRC_BIND_' in text:return 'BIND_MARKER'
  if 'pg_current_xact_id()' in text:return 'SAME_XID'
  return 'FIXED_RAW'
 def role(self,args):
  if 'psql' not in args or '-U' not in args:raise AssertionError('PSQL_ONLY_PROCESS')
  if self.plan['immutable_container_id'] not in args:raise AssertionError('IMMUTABLE_CID_REQUIRED')
  return args[args.index('-U')+1]
 def inspect_facts(self):
  target=self.plan['target_manifest']['target'];image_id='sha256:'+'f'*64
  container={'Id':self.plan['immutable_container_id'],'Name':'/'+target['container_name'],'Image':image_id,
   'Config':{'Image':target['image'],'Labels':target['labels']},'Platform':'linux','State':{'Running':True},
   'HostConfig':{'NetworkMode':'none','PortBindings':{},'Privileged':False,'PidMode':'','IpcMode':'private','Devices':[],'CapAdd':[],
    'Tmpfs':{'/run/wa-secrets':'rw,noexec,nosuid,nodev,mode=0700'}},'NetworkSettings':{'Ports':{}},
   'Mounts':[{'Type':'volume','Name':target['volume_name'],'Destination':'/var/lib/postgresql/data','RW':True},
    {'Type':'bind','Source':target['bootstrap_secret_host_path'],'Destination':'/run/bootstrap-password','RW':False}]}
  volume={'Name':target['volume_name'],'Driver':'local','Options':{},'Scope':'local','Labels':target['labels']}
  context={'Name':'desktop-linux','Endpoints':{'docker':{'Host':'npipe:////./pipe/dockerDesktopLinuxEngine'}}}
  image={'Id':image_id,'Os':'linux','Architecture':'amd64','RepoDigests':[target['image']]}
  return container,volume,context,image
 def popen(self,args,**options):return Process(self,args,**options)
 def result(self,value,code=0,stderr=''):
  return types.SimpleNamespace(returncode=code,stdout=value if isinstance(value,str) else canonical(value),stderr=stderr)
 def run(self,args,**options):
  if options.get('shell',False) is not False:raise AssertionError('NO_SHELL_BOUNDARY')
  args=list(args)
  if 'psql' not in args:
   if args[:5]==['docker','--context','desktop-linux','context','inspect']:value=self.context
   elif args[3]=='inspect' or 'container' in args and 'inspect' in args:value=self.container
   elif 'volume' in args and 'inspect' in args:value=self.volume
   elif 'image' in args and 'inspect' in args:value=self.image
   else:raise AssertionError('UNREGISTERED_DOCKER_READ_BOUNDARY')
   self.events.append({'kind':'inspect','object':args[3]});return self.result([value])
  role=self.role(args);text=options.get('input','');self.events.append({'kind':'raw','role':role,'shape':self.shape(text)})
  if 'PGPASSWORD' in args:return self.result('',2,'psql: error: connection to server at "127.0.0.1", port 5432 failed: FATAL:  password authentication failed for user "'+role+'"\n')
  if 'pg_hba_file_rules' in text:
   return self.result([{'rule_number':n,'type':'host','database':['all'],'user_name':['all'],'address':ip,'netmask':mask,'auth_method':'scram-sha-256','error':None}
    for n,ip,mask in [(1,'127.0.0.1','255.255.255.255'),(2,'::1','ffff:ffff:ffff:ffff:ffff:ffff:ffff:ffff')]])
  if 'pg_authid' in text:return self.result({r:True for r in ('postgres','wa_migrator','wa_context_issuer','wa_identity_service_authority','wa_app_runtime','wa_worker')})
  if "'auth',system_user" in text:return self.result({'login':role,'auth':'scram-sha-256:'+role,'database':'wa_p0c_rehearsal','client':'127.0.0.1','server':'127.0.0.1'})
  if "'other_clients'" in text:return self.result({'other_clients':sum(p.poll() is None for p in self.processes)})
  if text.startswith('SELECT count(*) FROM pg_stat_activity WHERE pid='):
   pid=int(re.search(r'WHERE pid=([0-9]+)',text)[1]);found=next((p for p in self.processes if p.pid==pid),None)
   if found is None:raise AssertionError('UNKNOWN_EXACT_BACKEND')
   found.closed_observed=found.poll() is not None;return self.result('0' if found.closed_observed else '1')
  if "'issuer_owned'" in text:return self.result(self.retention(text))
  if text==self.sql['complete-state-observe.sql']:return self.result(self.state())
  if text==self.sql['fixture-coherence-observe.sql']:return self.result({'users':2 if self.seeded else 0,'coherent':self.seeded})
  if text==self.sql['exact-trigger-observe.sql']:return self.result({'owner_count':8,'physical_count':8,'all_enabled':not self.disabled})
  if 'workinants.native-catalog.v1' in text:
   value=deepcopy(self.native)
   if self.disabled:
    for row in value.get('triggers',[]):
     if row.get('table_name') in self.protocol['FIXTURE_TABLES'] and row.get('name')=='owner_commit':row['enabled']='D'
   return self.result(value)
  if text.startswith('SELECT current_setting(') or text.startswith('SELECT NOT EXISTS('):return self.result('t')
  raise AssertionError('UNREGISTERED_RAW_SQL')
 def insert(self,text,process):
  match=re.fullmatch(r'INSERT INTO platform\.database_action_grant \(([^)]+)\) VALUES \((.*)\) RETURNING pg_catalog\.jsonb_build_object\(\x27created_at\x27,created_at\); COMMIT;',text,re.S)
  if not match:raise AssertionError('ISSUER_INSERT_SQL_SHAPE')
  columns=[x.strip() for x in match[1].split(',')];values=split_sql(match[2])
  if len(columns)!=21 or len(values)!=21 or len(set(columns))!=21:raise AssertionError('ISSUER_COLUMN21_CLOSURE')
  row=dict(zip(columns,values));token=literal(row['token_hash'])
  if token in self.grants or literal(row['issuer_service'])!=process.role:raise AssertionError('ISSUER_INSERT_IDENTITY')
  # This is the source-pinned grant_guard's returned clock_timestamp projection.
  row['created_at']="'"+RETURN_STAMP+"'::timestamptz"
  self.grants[token]={'values':row,'issuer':process.role,'issuer_process':process,'committed':True}
  return row
 def retention(self,text):
  parts=text.split(' FROM (',1)[1].rsplit(') observed;',1)[0].split(' UNION ALL ')
  count=0;exact=True;issuer=True;unrevoked=True
  for part in parts:
   identity=re.search(r'WHERE g.id=(.+)\Z',part)[1]
   found=[g for g in self.grants.values() if g['values']['id']==identity]
   if len(found)!=1:exact=False;continue
   grant=found[0];value=grant['values'];count+=1
   comparisons=re.findall(r'g\.([a-z_]+) IS NOT DISTINCT FROM \((.*?)\)(?= AND g\.|\) AS exact)',part,re.S)
   exact=exact and len(comparisons)==21 and len({k for k,v in comparisons})==21 and all(value.get(k)==v for k,v in comparisons)
   issuer=issuer and grant['issuer']=='wa_context_issuer' and grant['committed'] and grant['issuer_process'].poll()==0
   unrevoked=unrevoked and value['revoked_at']=='NULL::timestamptz'
  return {'count':count,'exact':bool(exact),'issuer_owned':bool(issuer),'unrevoked':bool(unrevoked),'unexpired':True}
 def fixture_transaction(self,text):
  if 'DISABLE TRIGGER owner_commit;' in text:
   if text.count('DISABLE TRIGGER owner_commit;')!=8 or text.count('ENABLE TRIGGER owner_commit;')!=8:raise AssertionError('FIXTURE_EXACT_EIGHT')
   self.disabled=True;self.seeded=True
  if text.count('ENABLE TRIGGER owner_commit;')==8:self.disabled=False
  if not text.rstrip().endswith('COMMIT;'):raise AssertionError('FIXTURE_COMMIT_REQUIRED')
 def state(self):
  return {table:{'count':len(self.grants) if table=='platform.database_action_grant' else wanted if self.seeded else 0,
   'rows_sha256':digest(sorted(g['values']['id'] for g in self.grants.values())) if table=='platform.database_action_grant' else
    digest({'table':table,'fixture_sql_sha256':self.packet['prepared_files_sha256']['existing-scoped-read-fixtures.sql'],'seeded':self.seeded,'count':wanted if self.seeded else 0})}
   for table,wanted in self.packet['expected_counts'].items()}
 def binder_diagnostic(self):
  body=re.search(r'CREATE FUNCTION platform_private\.bind_request_context\(secret text\).*?AS\s+(\$[a-z_0-9]*\$)(.*?)\1;',self.application,re.S)[2]
  line=next(i for i,x in enumerate(body.split('\n'),1) if "RAISE EXCEPTION 'invalid, stale or unsupported context'" in x)
  return 'ERROR:  42501: invalid, stale or unsupported context\nCONTEXT:  PL/pgSQL function platform_private.bind_request_context(text) line '+str(line)+' at RAISE\nLOCATION:  exec_stmt_raise, pl_exec.c:3911\n'
 def project(self,text,bound):
  if bound is None or not bound['committed'] or bound['issuer_process'].poll()!=0:raise AssertionError('READ_BEFORE_CLOSED_ISSUER')
  projections=re.findall(r"'([^']+)',\(SELECT count\(\*\) FROM ([a-z_]+\.[a-z_]+) WHERE (?:id=|user_id::text\|\|':'\|\|role::text=)'([0-9a-z:-]+)'\)",text)
  if not projections:raise AssertionError('ACTUAL_SQL_PROJECTION_REQUIRED')
  value=bound['values'];caps=re.findall(r"'((?:[^']|'')*)'",value['allowed_fields']);root=literal(value['target_kind']);root_id=literal(value['target_id'])
  registered=root in dict(self.protocol['SPECS']) and literal(value['owner_module_id'])==self.packet['models'][root]['owner'] and literal(value['action'])=='SH-003.v1' and literal(value['purpose'])=='owner:queryOwnerFacts'
  result={}
  for label,table,key in projections:
   model=next(m for m,meta in self.packet['models'].items() if meta['object']==table)
   fields=next(row['fields'] for row in self.acl if (row['role'],row['model'],row['operation'])==('wa_app_runtime',model,'SELECT'))
   visible=self.seeded and registered and model==root and key==root_id and all(model+'/'+key+'/SELECT/'+field in caps for field in fields)
   if model in self.protocol['REVISION_MODELS']:visible=visible and model+'/'+key+'/revision/0' in caps and value['source_generation']=='0'
   result[label]=int(bool(visible))
  markers=re.findall(r"SELECT '(WA_SRC_(?:BEFORE|AFTER)_[^']+)';",text)
  if len(markers)!=2:raise AssertionError('ACTUAL_READ_MARKERS_REQUIRED')
  return [markers[0],canonical(result),markers[1]]
 def boundaries(self):
  stack=ExitStack();stack.enter_context(patch.object(subprocess,'run',side_effect=self.run));stack.enter_context(patch.object(subprocess,'Popen',side_effect=self.popen))
  for name in ('call','check_call','check_output'):stack.enter_context(patch.object(subprocess,name,side_effect=AssertionError('FORBIDDEN_UNMODELED_PROCESS')))
  stack.enter_context(patch.object(socket,'create_connection',side_effect=AssertionError('FORBIDDEN_NETWORK')));return stack
 def run_child(self,freshdir):
  module=admitted_child()
  with self.boundaries():return module['coordinate'](deepcopy(self.plan),Path(freshdir))
 def assert_closed(self):
  if not all(p.poll() in (0,3) and p.closed_observed and p.stdout.closed and p.stderr.closed for p in self.processes):raise AssertionError('PROCESS_BACKEND_CLOSURE_REQUIRED')

def child_only_native():
 """Minimal declared native transport fixture; NOT a 29089-check proof.

 Parent owning harness must provide its independently source-derived full native
 catalog. The accepted child binds the supplied comparator/attestation; this
 small fixture only makes the child transport standalone and explicit.
 """
 protocol=runpy.run_path(str(ROOT/'scripts/scoped_read_companion_protocol.py'))
 return {'format':'workinants.native-catalog.v1','server_version_num':170011,'read_only':True,
  'collected_as':'postgres','collector_is_superuser':True,
  'triggers':[{'table_name':table,'name':name,'enabled':'O','internal':False,'function_identity':'source-only.'+name+'()'}
   for table in protocol['FIXTURE_TABLES'] for name in ('owner_commit','physical_guard')]}

def historical_owner_native():
 """Explicitly authorized, immutable historical offline mock data only.

 No current run proof is inferred. Both the execution record's asset binding
 and retained native bytes must match before JSON decoding.
 """
 relative='context/reconciliation/local-f0-run-assets/da5ad66-owner-72934689/evidence/native-before.json'
 expected='e2bc04014b3f3d57ac6669d3364cc15162d923f1fd29ccb782bdc809f7a861f8'
 record=json.loads((ROOT/'context/reconciliation/local-f0-owner-da5ad66-72934689-execution.json').read_bytes())
 if record['assets_sha256'].get(relative)!=expected:raise AssertionError('HISTORICAL_NATIVE_RECORD_BINDING')
 raw=(ROOT/relative).read_bytes()
 if sha(raw)!=expected:raise AssertionError('HISTORICAL_NATIVE_FIXTURE_DRIFT')
 return json.loads(raw)

def standalone_plan(directory,native=None):
 directory=Path(directory);packet=fixture_packet();module=admitted_child();native=deepcopy(native or child_only_native())
 pins=dict(packet['source_files_sha256']);pins[PACKET_PATH]=PACKET_SHA
 for name,value in packet['prepared_files_sha256'].items():pins['review-output/scoped-read-companion-rehearsal/'+name]=value
 for path,value in pins.items():
  if sha((ROOT/path).read_bytes())!=value:raise AssertionError('SOURCE_CLOSURE_DRIFT')
 history=runpy.run_path(str(ROOT/'scripts/prepare-local-f0-history.py'))
 run='550e8400-e29b-41d4-a716-446655440000'
 target={'schema':'workinants.local-f0-run.v1','run_id':run,'purpose':'LOCAL_F0_MIGRATION_REHEARSAL',
  'target':{'container_name':'wa-p0c-source-only-sixread','volume_name':'wa-p0c-source-only-sixread-data','database':'wa_p0c_rehearsal','image':history['IMAGE'],'network':'none',
   'labels':{'workinants.rehearsal':'p0c-local-f0','workinants.rehearsal.run':run},'bootstrap_secret_host_path':str(directory/'bootstrap-password')},
  'source':{'integrated_sql_sha256':module['APPLICATION_SHA'],'foundation_schema_sha256':'f'*64,'runtime_files_sha256':{p:'a'*64 for p in history['RUNTIME_FILES']}},
  'migration':{'id':'20261117000100_f0_local_initial','history':history['HISTORY']},
  'tools':{'node_version':'v24.22.1','prisma_version':'7.10.1','engine_commit':'d1b3f377ca835d73fd50954a5e22128b9ebdd6b8',
   'files_sha256':{p:'a'*64 for p in ('node/bin/node','schema-engine','node_modules/prisma/build/index.js','node_modules/prisma/build/cli.js','node_modules/prisma/config.js','node_modules/prisma/package.json')}}}
 plan={'schema':'workinants.scoped-read-companion-run.v1','scope':'REVIEWED_SELECTED94_SCOPED_READ_COMPANION_SQL_SUBSET_ONLY',
  'run_id':run,'source_commit':'b'*40,'source_tree':'c'*40,'packet_sha256':sha(''.join(p+'\0'+pins[p]+'\n' for p in sorted(pins)).encode()),'packet_files_sha256':pins,
  'reviewed_packet_sha256':PACKET_SHA,'reviewed_content_sha256':packet['source_only_packet_sha256'],'target_manifest':target,'immutable_container_id':CID,
  'scenario_names':[c['name'] for c in packet['cases']]}
 comparison={'format':'workinants.catalog-comparison.v1','status':'PASS','source_expected_sha256':module['EXPECTED_CATALOG'],'native_snapshot_sha256':digest(native),'findings':[],'check_counts':{'PASS':29089}}
 def bind(key,value):
  path=directory/(key+'.json');path.write_text(canonical(value),encoding='utf8');plan[key]={'path':str(path),'sha256':sha(path.read_bytes())}
 bind('native_snapshot',native);bind('native_comparison',comparison)
 attestation={'schema':'workinants.scoped-read-companion-native-attestation.v1','run_id':run,'container_id':CID,
  'source_commit':plan['source_commit'],'source_tree':plan['source_tree'],'packet_sha256':plan['packet_sha256'],
  'collector_sha256':pins[module['COLLECTOR']],'source_expected_sha256':module['EXPECTED_CATALOG'],'native_snapshot_sha256':digest(native),
  'native_comparison_file_sha256':plan['native_comparison']['sha256'],'original_grantor_finalized':True,'operation_backends_absent':True,'comparison_status':'PASS'}
 bind('native_attestation',attestation);return plan,native,packet

def assert_complete(result,world):
 assert result['status']=='PASS_FINITE_SCOPED_READ_COMPANION_SQL_SUBSET_ONLY',result.get('unexpected')
 assert result['evidence_complete'] is True and result['source_packet_unchanged_after'] is True
 assert len(result['results'])==71 and len(result['operations'])==586
 assert Counter(x['stage'] for x in result['operations'])==Counter(EXPECTED_STAGES),dict(Counter(x['stage'] for x in result['operations']))
 prefix=['GLOBAL_BACKEND_CLOSURE','GLOBAL_BACKEND_CLOSURE','PRE_FIXTURE_NATIVE_PARITY','GLOBAL_BACKEND_CLOSURE',
  'EXACT_EIGHT_TRIGGER_RESTORATION','GLOBAL_BACKEND_CLOSURE','SYNTHETIC_EXISTING_ROWS_ONLY','GLOBAL_BACKEND_CLOSURE',
  'EXACT_EIGHT_TRIGGER_RESTORATION','GLOBAL_BACKEND_CLOSURE','POST_FIXTURE_NATIVE_PARITY','GLOBAL_BACKEND_CLOSURE']
 group=['BOUND_OPERATION','SEPARATE_ISSUER_COMMIT','IMMUTABLE_ISSUER_RETENTION','GLOBAL_BACKEND_CLOSURE',
  'IMMUTABLE_ISSUER_RETENTION','GLOBAL_BACKEND_CLOSURE','IMMUTABLE_ISSUER_RETENTION','EXACT_EIGHT_TRIGGER_RESTORATION']
 suffix=['GLOBAL_BACKEND_CLOSURE','FINAL_NATIVE_PARITY','GLOBAL_BACKEND_CLOSURE','EXACT_EIGHT_TRIGGER_RESTORATION','GLOBAL_BACKEND_CLOSURE','FINALLY_FULL_NATIVE_PARITY']
 assert [x['stage'] for x in result['operations']]==prefix+group*71+suffix
 for index,case in enumerate(world.packet['cases']):
  observed=result['operations'][12+8*index:20+8*index]
  assert observed[0]['case']==case['name'] and observed[0]['operation_closed'] is True
  assert observed[0]['terminal_exit']==(3 if case['kind']=='binder-denial' else 0)
  assert observed[1]['operation_closed'] is True and observed[1]['created_at_return_verified'] is True
  assert observed[2]['instances']==observed[4]['instances']==1 and observed[6]['instances']==index+1
  assert observed[2]['unexpired_required'] is observed[4]['unexpired_required'] is True
  assert observed[6]['unexpired_required'] is False and observed[6]['current_unexpired_match'] is None
 assert sum(x['query_stage_reached'] for x in result['results'])==65
 assert sum(x['diagnostic'] is not None for x in result['results'])==6
 assert len(result['authentication'])==6 and all(x['correct_password']=='PASS_SCRAM' and x['wrong_password']=='PASS_REJECTED' for x in result['authentication'])
 assert len(world.grants)==71 and all(len(x['values'])==21 for x in world.grants.values())
 assert all(r['issued_grants']==i for i,r in enumerate(result['results'],1))
 world.assert_closed()
 retained=canonical(result)
 assert CANARY not in retained
 for token,grant in world.grants.items():assert token not in retained and literal(grant['values']['id']) not in retained

class ChildCompositionTests(unittest.TestCase):
 def test_real_whole_child_586_stages_no_factories_or_session_substitution(self):
  with tempfile.TemporaryDirectory(prefix='sixread-owned-child-',dir=TASK) as temp:
   plan,native,packet=standalone_plan(temp);world=World(plan,native,packet)
   result=world.run_child(Path(temp)/'component');assert_complete(result,world)
 def test_real_session_unexpected_read_exit_stops_later_cases_and_closes(self):
  with tempfile.TemporaryDirectory(prefix='sixread-owned-child-stop-',dir=TASK) as temp:
   plan,native,packet=standalone_plan(temp);world=World(plan,native,packet);world.fail_read_ordinal=2
   result=world.run_child(Path(temp)/'component')
   self.assertEqual(result['status'],'STOPPED_PARTIAL_EVIDENCE_PRESERVED');self.assertEqual(len(result['results']),1)
   self.assertEqual(world.read_ordinal,2);self.assertEqual(len(world.grants),2);self.assertTrue(result['subsequent_cases_stopped'])
   self.assertTrue(result['source_packet_unchanged_after']);world.assert_closed();self.assertNotIn(CANARY,canonical(result))
 def test_actual_load_inputs_rejects_forged_native_binding_before_any_process(self):
  with tempfile.TemporaryDirectory(prefix='sixread-owned-child-admission-',dir=TASK) as temp:
   plan,native,packet=standalone_plan(temp);plan['native_snapshot']['sha256']='0'*64;world=World(plan,native,packet)
   with world.boundaries(),self.assertRaises(Exception):admitted_child()['load_inputs'](plan)
   self.assertEqual(world.events,[])

if __name__=='__main__':
 forbid_actual_runtime()
 unittest.main()
