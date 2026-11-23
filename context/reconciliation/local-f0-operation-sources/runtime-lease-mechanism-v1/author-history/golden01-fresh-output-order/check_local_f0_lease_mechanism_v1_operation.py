"""Environment-free actual pipeline and boundary regressions.
All subprocess/Docker/database/network edges are modeled. Models derive SQL,
roles, file bytes and predicate outcomes from the actual admitted source.
Synthetic mocks provide no PostgreSQL execution evidence or source approval.
"""
from pathlib import Path
import ast, copy, hashlib, io, json, os, re, shutil, socket, tempfile, threading, types, unittest, uuid
from unittest import mock

HERE=Path(__file__).resolve().parent
FUTURE=HERE/'future-root'
FIVE=('execute_local_f0_lease_mechanism_v1_20261120.py','local_f0_lease_mechanism_v1_operation_steps.py','prepare_local_f0_lease_mechanism_v1_plan.py','check_local_f0_lease_mechanism_v1_operation.py','pin_local_f0_lease_mechanism_v1_plan_20261120.py')
ARCHIVE='context/reconciliation/local-f0-operation-sources/runtime-lease-mechanism-v1'
VALIDATION='context/reconciliation/local-f0-runtime-lease-mechanism-v1-source-validation.json'
def load(name):
 p=HERE/name;m=types.ModuleType('_test_'+name.replace('.','_'));m.__file__=str(p);exec(compile(p.read_bytes(),str(p),'exec'),m.__dict__);return m
def sha(raw):return hashlib.sha256(raw).hexdigest()
def rawjson(v):return json.dumps(v,sort_keys=True).encode()
CORE=load(FIVE[0]);STEPS=load(FIVE[1]);PREP=load(FIVE[2])

class Pipe:
 def __init__(self,p,index):self.p=p;self.index=index;self.closed=False;self.used=False
 def read(self,n):
  self.p.done.wait(10)
  if not self.p.done.is_set():raise AssertionError('mock process not dispatched')
  if self.used:return b''
  self.used=True;return self.p.reply[self.index][:]
 def close(self):self.closed=True
class Input:
 def __init__(self,p):self.p=p;self.closed=False;self.buf=bytearray()
 def write(self,b):
  assert type(b)is bytes;self.buf.extend(b);return len(b)
 def close(self):
  if not self.closed:self.closed=True;self.p.dispatch()
class Child:
 def __init__(self,model,args,**kw):
  assert set(kw)=={'stdin','stdout','stderr'} and all(kw[x]==-1 for x in kw);self.model=model;self.args=args;self.done=threading.Event();self.reply=(b'',b'');self.returncode=None;self.stdin=Input(self);self.stdout=Pipe(self,0);self.stderr=Pipe(self,1);model.children.append(self)
 def dispatch(self):
  try:self.returncode,out,err=self.model.dispatch(self.args,bytes(self.stdin.buf));self.reply=(out,err)
  except BaseException as e:self.model.boundary_errors.append(type(e).__name__);self.returncode=99;self.reply=(b'',b'')
  self.done.set()
 def wait(self,timeout=None):
  if not self.done.is_set():self.dispatch()
  return self.returncode
 def poll(self):return self.returncode
 def terminate(self):self.returncode=-15;self.done.set()
 def kill(self):self.returncode=-9;self.done.set()

class Model:
 def __init__(self,root,external,manifest):
  self.root=root;self.external=external;self.m=manifest;self.children=[];self.boundary_errors=[];self.commands=[];self.cid='c'*64;self.created=False;self.volume=False;self.running=False;self.created_at='2026-11-20T00:00:00Z';self.files={};self.rows={};self.guard=None;self.setup=False;self.passwords={};self.fail_file=None;self.bad_diag=False;self.bad_auth=None;self.bad_hba=False;self.bad_body=False;self.bad_global=False;self.writer_hook=None;self.after_case=None;self.behaviors=[];self.closed_count=0;self.setup_sql=None
 def run_git(self,args,**kw):
  assert args[:3]==['git','-C',str(self.root)] and kw=={'capture_output':True,'timeout':30};rest=args[3:]
  if rest==['rev-parse',self.m['source_commit']+'^{commit}']:out=(self.m['source_commit']+'\n').encode()
  elif rest==['rev-parse',self.m['source_commit']+'^{tree}']:out=(self.m['source_tree']+'\n').encode()
  else:
   assert rest[:2]==['cat-file','blob'];commit,n=rest[2].split(':',1);assert commit==self.m['source_commit']and n in self.m['packet_files_sha256'];out=(self.root/n).read_bytes()
  return types.SimpleNamespace(returncode=0,stdout=out,stderr=b'')
 def body(self,name):
  b=self.files[name];matches=re.findall(rb'AS \$wa\$(.*?)\$wa\$',b,re.S);return matches[-1].decode()
 def row(self,i):
  return {'id':i,'state':'pending'if i==1 else'leased','fence':0 if i==1 else 7,'attempt_count':0 if i==1 else 1,'lease_token_hash':None if i==1 else sha(bytes.fromhex('a'*64)),'lease_expires_at':None if i==1 else('past'if i==3 else'future'),'effect_receipt_id':None,'next_attempt_at':'2026-01-01T00:00:00+00:00'}
 def safe_row(self,r):
  return {k:r[k]for k in('id','state','fence','attempt_count')}|{'lease_fields_null':r['lease_token_hash']is None and r['lease_expires_at']is None,'effect_absent':r['effect_receipt_id']is None,'next_attempt_at':r['next_attempt_at']}
 def fingerprint(self,r):return sha(rawjson(r))
 def authority(self):
  source=self.setup_sql.decode();role_rows=[]
  for role in sorted(STEPS.LEAVES):
   statement=re.search(r'CREATE ROLE '+role+r' ([^;]+);',source)[1]
   fields={'role':role,'login':'LOGIN'in statement,'super':'NOSUPERUSER'not in statement,'inherit':'NOINHERIT'not in statement,'createdb':'NOCREATEDB'not in statement,'createrole':'NOCREATEROLE'not in statement,'replication':'NOREPLICATION'not in statement,'bypass':'NOBYPASSRLS'not in statement,'usage':re.search(r'GRANT USAGE ON SCHEMA .* TO ([^;]+);',source)[1].find(role)>=0,'create':False,'select':re.search(r'GRANT SELECT ON .* TO ([^;]+);',source)[1].find(role)>=0,'insert':False,'update':False,'delete':False,'truncate':False,'helper':re.search(r'GRANT EXECUTE ON FUNCTION .* TO ([^;]+);',source)[1].find(role)>=0,'guard':False,'columns':dict.fromkeys(STEPS.COLS,False)}
   grant=re.search(r'GRANT UPDATE\(([^)]+)\) ON [^;]+ TO '+role+r';',source)
   if grant:
    for col in grant[1].split(','):fields['columns'][col]=True
   role_rows.append(fields)
  return {'login':'postgres','auth':'scram-sha-256:postgres','memberships':0,'owners':dict.fromkeys(('schema','table','functions'),True),'roles':role_rows}
 def native_error(self,name,worker=False):
  state='P0001'if worker else'42501';text='expired or foreign worker'if worker else'permission denied for function lease_secret_matches'
  if self.bad_diag:text='unrelated sentinel'
  context='CONTEXT:  PL/pgSQL function wa_lease_branch_v1_repro.guard() line '+('7 at RAISE'if worker else'3 at IF')+'\n'if name!='direct-helper.sql'else''
  location='exec_stmt_raise, pl_exec.c:3912'if worker else'aclcheck_error, aclchk.c:2812'
  return ('psql:/run/wa-secrets/sql/'+name+':4: ERROR:  '+state+': '+text+'\n'+context+'LOCATION:  '+location+'\n').encode()
 def file_sql(self,name,role):
  assert name in STEPS.FILES and self.files[name]==(self.root/(STEPS.PREFIX+name)).read_bytes()
  sql=self.files[name].decode();out=[];err=b'';code=0
  if name=='setup-original.sql':
   assert role=='postgres'and not self.setup;self.setup_sql=self.files[name];self.guard=self.body(name);self.rows={i:self.row(i)for i in range(1,6)};self.setup=True
  elif name in('install-nested.sql','restore-old.sql'):
   assert role=='postgres'and self.setup;self.guard=self.body(name)
  elif name=='observe.sql':
   assert role=='postgres';a=self.authority();grants={r['role']:r['helper']for r in a['roles']};out=[json.dumps({'rows':[self.safe_row(r)for r in self.rows.values()],'app_helper_execute':grants[STEPS.LEAVES[0]],'worker_helper_execute':grants[STEPS.LEAVES[1]],'verifier_helper_execute':grants[STEPS.LEAVES[2]],'trigger_enabled':'CREATE TRIGGER exact_guard BEFORE UPDATE'in self.setup_sql.decode()})]
  elif name=='observe-preconditions.sql':
   assert role=='postgres';profile={'body_sha256':sha(self.guard.encode()),**dict.fromkeys(('original_grantor_owner','invoker','volatile','unsafe','not_strict','cost100','search_path_exact'),True)}
   if self.bad_body:profile['body_sha256']='e'*64
   out=[json.dumps({'guard_source':profile,'lease_fixture':[{'id':i,'lease_hash_matches_public_dummy':None if r['lease_token_hash']is None else r['lease_token_hash']==sha(bytes.fromhex('a'*64)),'expired':None if r['lease_expires_at']is None else r['lease_expires_at']=='past'}for i,r in self.rows.items()]})]
  elif name=='direct-helper.sql':
   out=['t'];allowed=next(r['helper']for r in self.authority()['roles']if r['role']==role)
   if allowed:out+=['t']
   else:code=3;err=self.native_error(name)
  elif name=='reset-pending-baseline.sql':
   assert role==STEPS.LEAVES[0]and 'IF OLD.state=\'leased\' AND NEW.state<>\'leased\' THEN'in self.guard
   self.rows[1]['next_attempt_at']='2026-01-01T00:00:00+00:00';out=['1|2026-01-01 00:00:00+00']
  elif name=='pending-update.sql':
   assert role==STEPS.LEAVES[0];self.behaviors.append(name);out=['LEASE_V1_BEFORE']
   # Source-sensitive expression initialization: old compound outer condition
   # initializes private helper before pending-row Boolean evaluation; nested
   # branch does not initialize it when the outer leased test is false.
   nested="IF OLD.state='leased' AND NEW.state<>'leased' THEN"in self.guard
   if nested:
    self.rows[1]['next_attempt_at']='2026-01-02T00:00:00+00:00';out+=[json.dumps(self.safe_row(self.rows[1])),'LEASE_V1_AFTER']
   else:code=3;err=self.native_error(name)
  elif name.startswith('worker-'):
   assert role==STEPS.LEAVES[1];self.behaviors.append(name);target=int(re.search(r'WHERE id=([2-5])',sql)[1]);r=self.rows[target];out=['t','t','LEASE_V1_BEFORE'];secret=re.search(r"repeat\('([ab])',64\)",sql)[1]*64;fence=re.search(r"set_config\('wa.fence','([78])'",sql)[1]
   denied=r['lease_expires_at']=='past'or sha(bytes.fromhex(secret))!=r['lease_token_hash']or fence!=str(r['fence'])
   if denied:code=3;err=self.native_error(name,True)
   else:r.update(state='pending',lease_token_hash=None,lease_expires_at=None);out+=['2|pending|7|1','LEASE_V1_AFTER']
  else:raise AssertionError('unknown SQL')
  if self.fail_file==name:code=3;err=self.native_error(name);out=[]
  if self.after_case and name not in('observe.sql','observe-preconditions.sql'):self.after_case(name)
  return code,out,err
 def sql(self,args,payload):
  assert args[0:5]==['docker','--context','desktop-linux','exec','-i']and self.cid in args and 'psql'in args and args[args.index('-d')+1]==CORE.DATABASE and args[args.index('-h')+1]=='127.0.0.1'
  role=args[args.index('-U')+1];assert role in CORE.ROLES and args[-2:]==['-c','\\echo '+CORE.ACK]
  assert 'PGPASSWORD'not in ' '.join(args)and not any(p in ' '.join(args)for p in self.passwords.values())
  if 'PGPASSFILE=/run/wa-secrets/wrong-pgpass'in args:
   assert self.files['wrong-pgpass'].split(b':')[3].decode()==role
   return 2,b'',('psql: error: connection to server at "127.0.0.1", port 5432 failed: FATAL:  password authentication failed for user "'+role+'"\n').encode()
  file=args[args.index('-f')+1]
  if file!='-':
   assert payload==b''and file.startswith('/run/wa-secrets/sql/');name=file.rsplit('/',1)[1];code,out,err=self.file_sql(name,role)
  else:
   sql=payload.decode();assert role=='postgres'or sql.strip()==STEPS.LOGIN
   code=0;err=b''
   if sql.strip()==STEPS.LOGIN:
    v={'login':role,'current':role,'auth':'scram-sha-256:'+role,'database':CORE.DATABASE,'client':'127.0.0.1','server':'127.0.0.1'}
    if self.bad_auth:v[self.bad_auth[0]]=self.bad_auth[1]
    out=[json.dumps(v)]
   elif sql.strip()==STEPS.GLOBAL:
    out=[json.dumps({'login':'postgres','auth':'scram-sha-256:postgres','other_clients':1 if self.bad_global else 0})]
   elif sql.strip()==STEPS.HBA:
    out=[json.dumps([{'rule_number':i+1,'type':'host','database':['all'],'user_name':['all'],'address':address,'netmask':mask,'auth_method':'trust'if self.bad_hba else'scram-sha-256','error':None}for i,(address,mask)in enumerate((('127.0.0.1','255.255.255.255'),('::1','ffff:ffff:ffff:ffff:ffff:ffff:ffff:ffff')))])]
   elif 'FROM pg_authid WHERE rolname IN'in sql:
    names=re.findall(r"'([^']+)'",sql.split('rolname IN ')[1]);assert set(names)<=set(CORE.ROLES);out=[json.dumps(dict.fromkeys(names,True))]
   elif sql.strip()==STEPS.ABSENCE:out=[json.dumps({'canonical_namespaces':0,'canonical_roles':0,'migration_ledgers':0})]
   elif sql.strip()==STEPS.SETUP_STATUS:out=[json.dumps({'roles':3 if self.setup else 0,'schema':int(self.setup),'table':int(self.setup),'functions':2 if self.setup else 0})]
   elif sql.strip()==STEPS.AUTHORITY:out=[json.dumps(self.authority())]
   elif sql.strip()==STEPS.STATE:
    out=[json.dumps([{'id':i,'row_sha256':self.fingerprint(r),'pending_sha256':self.fingerprint(r|{'state':'pending','lease_token_hash':None,'lease_expires_at':None}),'rescheduled_sha256':self.fingerprint(r|{'next_attempt_at':'2026-01-02T00:00:00+00:00'})}for i,r in self.rows.items()])]
   elif sql.startswith('ALTER ROLE '):
    assert self.setup
    matches=re.findall(r"ALTER ROLE (wa_lease_v1_\w+) PASSWORD '([0-9a-f]{64})';\n",sql);assert len(matches)==3 and ''.join("ALTER ROLE "+r+" PASSWORD '"+p+"';\n"for r,p in matches)==sql;self.passwords.update(matches);out=[]
   else:raise AssertionError('unregistered administrative SQL')
  if code==0:out.append(CORE.ACK)
  return code,('\n'.join(out)+'\n').encode()if out else b'',err
 def dispatch(self,args,payload):
  self.commands.append((args,payload))
  if args[0]=='powershell.exe':assert args[1:4]==['-NoProfile','-NonInteractive','-File'];return 0,b'OWNER_ONLY_VERIFIED\n',b''
  assert args[:3]==['docker','--context','desktop-linux'];a=args[3:];out=b''
  if a==['context','inspect','desktop-linux']:out=rawjson([{'Endpoints':{'docker':{'Host':'npipe:////./pipe/dockerDesktopLinuxEngine'}}}])
  elif a==['version','--format','{{json .Server}}']:out=rawjson({'Os':'linux','Arch':'amd64'})
  elif a==['container','ls','-a','--format','{{.Names}}']:out=(self.m['target']['name']+'\n').encode()if self.created else b''
  elif a==['volume','ls','--format','{{.Name}}']:out=(self.m['target']['volume']+'\n').encode()if self.volume else b''
  elif a==['image','inspect',CORE.IMAGE]:
   # Real validator consumes official pinned raw manifest and this store form.
   out=rawjson([{'Id':CORE.CONFIG,'Os':'linux','Architecture':'amd64','RepoDigests':['postgres@'+CORE.IMAGE.split('@')[1]]}])
  elif a[:2]==['volume','create']:
   assert a[-1]==self.m['target']['volume']and a[2:-1]==[x for k,v in self.m['target']['labels'].items()for x in('--label',k+'='+v)];self.volume=True;out=(a[-1]+'\n').encode()
  elif a[:2]==['volume','inspect']:
   assert self.volume and a[2]==self.m['target']['volume'];out=rawjson([{'Name':a[2],'Labels':self.m['target']['labels'],'CreatedAt':self.created_at,'Driver':'local','Options':None,'Scope':'local'}])
  elif a[:2]==['container','create']:
   assert not self.created and a[a.index('--network')+1]=='none'and a[a.index('--platform')+1]=='linux/amd64'and CORE.IMAGE in a and 'POSTGRES_HOST_AUTH_METHOD=scram-sha-256'in a and 'POSTGRES_INITDB_ARGS=--auth-host=scram-sha-256'in a and '--publish'not in a;self.created=True;out=(self.cid+'\n').encode()
  elif a[:2]==['container','inspect']:
   assert self.created;out=rawjson([{'Id':self.cid,'Name':'/'+self.m['target']['name'],'Config':{'Image':CORE.IMAGE,'Labels':self.m['target']['labels']},'Image':CORE.CONFIG,'Platform':'linux','State':{'Running':self.running},'HostConfig':{'NetworkMode':'none','PortBindings':{},'Privileged':False,'PidMode':'','IpcMode':'private','Devices':[],'CapAdd':[],'Links':None,'Tmpfs':{'/run/wa-secrets':'rw,nosuid,noexec,nodev,mode=0700'}},'NetworkSettings':{'Ports':{'5432/tcp':None}},'Mounts':[{'Type':'volume','Name':self.m['target']['volume'],'Destination':'/var/lib/postgresql/data','RW':True},{'Type':'bind','Source':str(Path(self.m['evidence_directory'])/'private/ok-bootstrap-password'),'Destination':'/run/bootstrap-password','RW':False}]}])
  elif a[:2]==['container','start']:assert a[2]==self.cid;self.running=True;out=(self.cid+'\n').encode()
  elif a[:2]==['container','rm']:assert a==['container','rm','-f',self.cid];self.created=False
  elif a[:2]==['volume','rm']:assert not self.created and a[2]==self.m['target']['volume'];self.volume=False
  elif 'psql'in a:return self.sql(args,payload)
  elif a[:3]==['exec',self.cid,'pg_isready']:assert self.running
  elif a[:4]==['exec','-i',self.cid,'sh']or a[:3]==['exec',self.cid,'sh']:
   script=a[-1];assert self.running
   if script==CORE.KERNEL_SCRIPT:out=b'WA_LEASE_MECHANISM_TMPFS_PGDATA_OK\n'
   elif script.startswith('umask 077; cat > /run/wa-secrets/'):
    name='wrong-pgpass'if 'wrong-pgpass'in script else'pgpass';self.files[name]=payload;out=b'600:0:0\n'
   elif 'sha256sum /run/wa-secrets/sql/'in script:
    name=re.search(r'sha256sum /run/wa-secrets/sql/([\w-]+\.sql)',script)[1]
    assert name in STEPS.FILES
    if script.startswith('umask 077; mkdir -p '):self.files[name]=payload
    b=self.files[name];out=(sha(b)+'  /run/wa-secrets/sql/'+name+'\n'+str(len(b))+'\n400:0:0\n').encode()
   else:raise AssertionError('unlisted shell recipe')
  elif a==['exec',self.cid,'rm','--','/run/wa-secrets/wrong-pgpass']:self.files.pop('wrong-pgpass',None)
  else:raise AssertionError('unlisted process boundary')
  return 0,out,b''

class Case(unittest.TestCase):
 def setUp(self):
  self.tmp=tempfile.TemporaryDirectory(prefix='wa-lease-mech-');self.base=Path(self.tmp.name);self.ext=self.base/'external';self.ext.mkdir();self.root=self.base/'future-root';shutil.copytree(FUTURE,self.root)
  for n in FIVE:shutil.copyfile(HERE/n,self.ext/n)
  # Test-only source-review stand-ins enable the real entrypoint with the
  # process graph mocked. They are never published or actual review evidence.
  self.seal();self.m=PREP.prepare(self.root,self.ext,str(uuid.uuid4()));self.m.update(source_commit='a'*40,source_tree='b'*40,review_status=PREP.REVIEW_STATUS);self.mp=self.ext/'operation-manifest.json';self.mp.write_bytes(PREP.encoded(self.m));self.model=Model(self.root,self.ext,self.m)
 def tearDown(self):
  for p in self.model.children:
   self.assertTrue(p.done.is_set());self.assertTrue(p.stdin.closed and p.stdout.closed and p.stderr.closed)
  self.tmp.cleanup()
 def seal(self):
  v=json.loads((self.root/VALIDATION).read_bytes());five={n:sha((self.ext/n).read_bytes())for n in FIVE}
  for n,w in five.items():(self.root/ARCHIVE/(n+'.txt')).write_bytes((self.ext/n).read_bytes())
  receipt={'decision':'SOURCE_APPROVED','operator_sources_sha256':five,'test_only':True};r=self.root/ARCHIVE/'TEST_ONLY_REVIEW.json';r.write_bytes(rawjson(receipt));pins={p.relative_to(self.root).as_posix():sha(p.read_bytes())for p in(self.root/ARCHIVE).rglob('*')if p.is_file()}
  v['operator_sources_sha256']=five;v['archive_files_sha256']=pins
  for k in('independent_source_review','independent_binary_safety_review'):v[k]={'decision':'SOURCE_APPROVED','operator_sources_sha256':five,'path':r.relative_to(self.root).as_posix(),'sha256':sha(r.read_bytes())}
  (self.root/VALIDATION).write_bytes(PREP.encoded(v))
 def operator(self):return CORE.Operator(self.mp,self.root,self.ext)
 def run_operator(self,op=None):
  op=op or self.operator()
  with mock.patch.object(CORE.subprocess,'Popen',side_effect=lambda *a,**k:Child(self.model,*a,**k)),mock.patch.object(CORE.subprocess,'run',side_effect=self.model.run_git),mock.patch.object(socket.socket,'connect',side_effect=AssertionError('NETWORK_FORBIDDEN')):
   code=op.run()
  self.assertEqual(self.model.boundary_errors,[]);return code,op
 def test_01_actual_pipeline_eleven_and_exact_cleanup(self):
  code,o=self.run_operator();self.assertEqual(code,0,o.report.get('primary_failure'));self.assertEqual([r['case']for r in o.report['cases']],[c[0]for c in STEPS.CASES]);self.assertTrue(o.report['cleanup']['physical_absence']);self.assertFalse(self.model.created or self.model.volume);self.assertNotIn(b'ALTER ROLE',CORE.data(o.report));self.assertTrue(all(c['operation_closed']for c in o.report['cases']))
 def test_02_pending_gate_precedes_steps_and_any_process(self):
  v=json.loads((self.root/VALIDATION).read_bytes());v['independent_source_review']['decision']='PENDING';(self.root/VALIDATION).write_bytes(PREP.encoded(v));code,o=self.run_operator();self.assertEqual(code,1);self.assertEqual(self.model.commands,[]);self.assertEqual(o.report['primary_failure']['code'],'PENDING_SOURCE_REVIEW')
 def test_03_native_source_profile_wrong_stops_before_cases(self):
  self.model.bad_body=True;code,o=self.run_operator();self.assertEqual(code,1);self.assertEqual(o.report['cases'],[]);self.assertTrue(o.report['cleanup']['physical_absence'])
 def test_04_unrelated_native_diagnostic_stops_later_cases(self):
  self.model.bad_diag=True;code,o=self.run_operator();self.assertEqual(code,1);self.assertEqual(o.report['cases'],[]);self.assertEqual(o.report['current']['diagnostic']['diagnostic'],'UNCONFIRMED');self.assertEqual(self.model.behaviors,['pending-update.sql'])
 def test_05_login_null_loopback_wrong_identity_method_database(self):
  for key,value in(('client',None),('server','::1'),('client','192.0.2.1'),('login','postgres'),('current','postgres'),('auth','trust:wa_lease_v1_app'),('database','other')):
   with self.subTest(key=key,value=value):
    p={'login':STEPS.LEAVES[0],'current':STEPS.LEAVES[0],'auth':'scram-sha-256:'+STEPS.LEAVES[0],'database':CORE.DATABASE,'client':'127.0.0.1','server':'127.0.0.1'};p[key]=value;self.assertFalse(all(STEPS.login_comparison(p,STEPS.LEAVES[0]).values()))
 def test_06_hba_first_trust_and_malformed_masks_reject(self):
  rows=[{'rule_number':1,'type':'host','database':['all'],'user_name':['all'],'address':'127.0.0.1','netmask':'255.255.255.255','auth_method':'trust','error':None}]
  with self.assertRaises(STEPS.Held):STEPS.hba_selections(rows,('postgres',))
  rows[0]['auth_method']='scram-sha-256';rows[0]['netmask']='255.0.255.0'
  with self.assertRaises(STEPS.Held):STEPS.hba_selections(rows,('postgres',))
 def test_07_diagnostic_header_frame_location_types(self):
  good=self.model.native_error('pending-update.sql');v=STEPS.diagnostic(good,'pending-update.sql','PRIVATE_HELPER','OLD');self.assertEqual(v['diagnostic'],'PRIVATE_HELPER')
  bad=[good+good,good+b'FATAL malformed\n',good.replace(b'42501',b'P0001'),good.replace(b'line 3',b'line 4'),good.replace(b'permission denied for function lease_secret_matches',b'permission denied for table work'),good.replace(b'aclchk.c',b'foreign.c'),good.replace(b'ERROR:',b'WARNING:'),good+b'SECRET_CANARY\n']
  for b in bad:self.assertIsNone(STEPS.diagnostic(b,'pending-update.sql','PRIVATE_HELPER','OLD')['sqlstate'])
  d=self.model.native_error('worker-expired.sql',True);self.assertEqual(STEPS.diagnostic(d,'worker-expired.sql','WORKER_GUARD','NESTED')['sqlstate'],'P0001');self.assertIsNone(STEPS.diagnostic(d,'worker-expired.sql','WORKER_GUARD','OLD')['sqlstate'])
 def test_08_binary_transport_and_old_text_conversion_tripwire(self):
  raw=(self.root/(STEPS.PREFIX+'setup-original.sql')).read_bytes();self.assertNotIn(b'\r',raw);old=raw.replace(b'\n',b'\r\n');self.assertNotEqual(sha(raw),sha(old))
  code,o=self.run_operator();self.assertEqual(code,0);self.assertEqual(self.model.files['setup-original.sql'],raw)
  self.assertNotIn('text=',ast.unparse(ast.parse((HERE/FIVE[0]).read_bytes())))
 def test_09_old_expression_restoration_is_source_sensitive(self):
  old=self.model # standalone actual source-driven model, not outcome factory
  old.files={n:(self.root/(STEPS.PREFIX+n)).read_bytes()for n in STEPS.FILES};old.file_sql('setup-original.sql','postgres')
  self.assertEqual(old.file_sql('pending-update.sql',STEPS.LEAVES[0])[0],3);old.file_sql('install-nested.sql','postgres');self.assertEqual(old.file_sql('pending-update.sql',STEPS.LEAVES[0])[0],0);old.file_sql('restore-old.sql','postgres');self.assertEqual(old.file_sql('pending-update.sql',STEPS.LEAVES[0])[0],3)
  # Restoring only the faulty outer expression causes the required nested
  # positive to fail, with no altered grants/predicate/model expectation.
  old.guard=old.body('restore-old.sql');self.assertNotEqual(old.file_sql('pending-update.sql',STEPS.LEAVES[0])[0],0)
 def test_10_persistent_writer_failure_still_cleanup_and_first_origin(self):
  o=self.operator();original=o.save
  def save():
   if o.report['stage'].startswith('CASE_'):raise OSError('SECRET_CANARY_RAW_EXCEPTION')
   return original()
  o.save=save;code,o=self.run_operator(o);self.assertEqual(code,1);self.assertTrue(o.report['persistence_failure']);self.assertTrue(o.report['cleanup']['physical_absence']);self.assertEqual(o.report['cases'],[]);self.assertNotIn('SECRET_CANARY',str(o.report))
 def test_11_closure_failure_prevents_observers_and_retains_reply(self):
  def after(name):
   if name=='pending-update.sql':self.model.bad_global=True
  self.model.after_case=after;code,o=self.run_operator();self.assertEqual(code,1);self.assertEqual(o.report['received_operation']['file'],'pending-update.sql');self.assertTrue(o.report['received_operation']['reply_received']);self.assertEqual(o.report['received_operation']['diagnostic']['sqlstate'],'42501');self.assertEqual(o.report['cases'],[]);self.assertTrue(o.report['cleanup']['physical_absence'])
 def test_12_source_drift_and_committed_mismatch_before_resources(self):
  n=next(iter(self.m['packet_files_sha256']));p=self.root/n;p.write_bytes(p.read_bytes()+b'\n');code,o=self.run_operator();self.assertEqual(code,1);self.assertEqual(self.model.commands,[])
 def test_13_secret_safe_sanitized_partial(self):
  self.model.bad_diag=True;code,o=self.run_operator();self.assertEqual(code,1);text=CORE.data(o.report);self.assertFalse(any(s.encode()in text for s in o.secrets));self.assertNotIn(b'unrelated sentinel',text);self.assertNotIn(b'permission denied',text);self.assertNotIn(b'repeat(',text)
 def test_14_source_transaction_ownership_and_column_grammar(self):
  text=(HERE/FIVE[1]).read_text();self.assertNotRegex(text,r"has_column_privilege\([^;\n]*(?:DELETE|TRUNCATE)")
  for name in STEPS.FILES:
   source=(self.root/(STEPS.PREFIX+name)).read_bytes();self.assertTrue(source.startswith(b'BEGIN'));self.assertEqual(len(re.findall(rb'^(?:COMMIT|ROLLBACK);$',source,re.M)),1)
  tree=ast.parse((HERE/FIVE[1]).read_bytes());self.assertNotIn('Session.begin',ast.unparse(tree));self.assertNotIn('SET ROLE',text)
 def test_15_constructor_and_output_failure_safe_cleanup(self):
  model=self.model;original=model.dispatch
  def dispatch(args,payload):
   if 'psql'in args and args[args.index('-f')+1].endswith('pending-update.sql'):return 0,b'\xff',b'SECRET_CANARY\n'
   return original(args,payload)
  model.dispatch=dispatch;code,o=self.run_operator();self.assertEqual(code,1);self.assertEqual(o.report['cases'],[]);self.assertTrue(o.report['cleanup']['physical_absence']);self.assertNotIn('SECRET_CANARY',str(o.report))
 def test_16_closed_reader_same_size_race_and_all_handles_closed(self):
  p=self.base/'closed.bin';p.write_bytes(b'PASS');original=Path.open;reads=[0]
  class Reader:
   def __init__(self,f):self.f=f
   def __enter__(self):self.f.__enter__();return self
   def __exit__(self,*a):return self.f.__exit__(*a)
   def fileno(self):return self.f.fileno()
   def read(self,*a):
    b=self.f.read(*a);reads[0]+=1
    if reads[0]==1:
     s=p.stat()
     with original(p,'r+b')as w:w.write(b'FAIL')
     os.utime(p,ns=(s.st_atime_ns,s.st_mtime_ns))
    return b
  def opened(path,*a,**k):
   f=original(path,*a,**k);return Reader(f)if path==p and a and a[0]=='rb'else f
  with mock.patch.object(Path,'open',opened),self.assertRaises(CORE.Stop):CORE.closed(p)
  self.assertEqual(p.read_bytes(),b'FAIL')

if __name__=='__main__':unittest.main(verbosity=2)

