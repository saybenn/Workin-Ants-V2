"""Held vanilla-PG synthetic mechanism operator; Root alone executes.
No canonical application, Prisma, migration, worker loop or qualification.
Binary IO only; reviewed twelve synthetic files plus closed admin recipes.
"""
from pathlib import Path, PureWindowsPath
import argparse, hashlib, json, os, re, secrets, stat, subprocess, threading, time, types

FIVE=('execute_local_f0_lease_mechanism_v1_20261120.py','local_f0_lease_mechanism_v1_operation_steps.py','prepare_local_f0_lease_mechanism_v1_plan.py','check_local_f0_lease_mechanism_v1_operation.py','pin_local_f0_lease_mechanism_v1_plan_20261120.py')
DATABASE='wa_lease_mechanism_v1'
ROLES=('postgres','wa_lease_v1_app','wa_lease_v1_worker','wa_lease_v1_verifier')
IMAGE='docker.io/library/postgres:17.11@sha256:996e9dc583ba9f0265a2c75547a9c95fb22c251e394749cab205a0a00e1856a1'
CONFIG='sha256:eb0fb2377534e65aad04f37838956b3dfb888e1a3dd3c1acf957bc6557eb6c7d'
ACK='WA_LEASE_MECHANISM_V1_TERMINAL_ACK'

class Stop(Exception):
 def __init__(self,code):self.code=code;super().__init__(code)
def need(value,code):
 if not value:raise Stop(code)
def sha(raw):return hashlib.sha256(raw).hexdigest()
def data(value):return (json.dumps(value,indent=2,allow_nan=False)+'\n').encode()
def unique(raw):
 need(type(raw)is bytes and len(raw)<=1024*1024,'JSON_BOUNDED_BYTES')
 def pairs(items):
  value={}
  for k,v in items:need(k not in value,'JSON_DUPLICATE_KEY');value[k]=v
  return value
 try:return json.loads(raw,object_pairs_hook=pairs,parse_constant=lambda _:(_ for _ in ()).throw(Stop('JSON_NONFINITE')))
 except (ValueError,UnicodeError,RecursionError):raise Stop('JSON_MALFORMED')from None

def closed(path,cap=8*1024*1024):
 """Two closed byte reads; same-representation metadata and fstat barriers.
 Bounded in-flight integrity, not perpetual atomicity after return.
 """
 path=Path(path);need(not any(p.is_symlink()for p in(path,*path.parents)),'SOURCE_SYMLINK')
 def key(s):return(s.st_dev,s.st_ino,s.st_nlink,s.st_mode,s.st_size,s.st_mtime_ns,s.st_ctime_ns)
 def once():
  a=path.lstat();need(stat.S_ISREG(a.st_mode)and a.st_nlink==1 and 0<=a.st_size<=cap,'SOURCE_REGULAR_BOUNDED')
  with path.open('rb')as f:
   h=os.fstat(f.fileno());need((h.st_dev,h.st_ino,h.st_size)==(a.st_dev,a.st_ino,a.st_size)and stat.S_ISREG(h.st_mode)and h.st_nlink==1,'SOURCE_HANDLE_IDENTITY')
   raw=f.read(cap+1);need(key(h)==key(os.fstat(f.fileno())),'SOURCE_HANDLE_DRIFT')
  b=path.lstat();need(key(a)==key(b)and len(raw)==a.st_size,'SOURCE_PATH_DRIFT');return raw,key(b)
 x,a=once();y,b=once();need(x==y and a==b,'SOURCE_CLOSED_BYTE_DRIFT');return x

class Result:
 def __init__(self,code,out,err):self.returncode=code;self.stdout=out;self.stderr=err

def process(args,payload=None,timeout=30):
 """Binary bounded readers; client/pipe closure in finally, no backend claim."""
 need(type(args)is list and all(type(a)is str for a in args)and(payload is None or type(payload)is bytes)and type(timeout)is int and 0<timeout<=120,'PROCESS_PROFILE')
 p=None;threads=[];buffers=[bytearray(),bytearray()];bad=threading.Event();failure=None;code=None
 try:
  p=subprocess.Popen(args,stdin=subprocess.PIPE,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
  def reader(stream,index):
   try:
    while True:
     chunk=stream.read(4096)
     if not chunk:break
     if type(chunk)is not bytes or len(buffers[index])+len(chunk)>65536:bad.set();break
     buffers[index].extend(chunk)
   except BaseException:bad.set()
  for i,s in enumerate((p.stdout,p.stderr)):
   th=threading.Thread(target=reader,args=(s,i),daemon=True);threads.append(th);th.start()
  if payload:p.stdin.write(payload)
  p.stdin.close();code=p.wait(timeout=timeout)
  for th in threads:th.join(timeout=2)
  need(not bad.is_set()and all(not th.is_alive()for th in threads),'PROCESS_BOUNDED_COMPLETE_OUTPUT');need(type(code)is int,'PROCESS_EXIT_TYPE')
 except BaseException as error:failure=error
 finally:
  if p is not None:
   try:
    if p.poll()is None:
     p.terminate()
     try:p.wait(timeout=5)
     except subprocess.TimeoutExpired:p.kill();p.wait(timeout=5)
    need(type(p.poll())is int,'PROCESS_EXIT_UNCONFIRMED')
   except BaseException:
    if failure is None:failure=Stop('PROCESS_CLOSE_UNCONFIRMED')
   for stream in (p.stdin,p.stdout,p.stderr):
    try:stream.close()
    except BaseException:
     if failure is None:failure=Stop('PROCESS_PIPE_CLOSE_UNCONFIRMED')
   for th in threads:th.join(timeout=2)
  if failure is not None:
   if isinstance(failure,Stop):raise failure
   raise Stop('PROCESS_BOUNDARY_UNEXPECTED')from None
 return Result(code,bytes(buffers[0]),bytes(buffers[1]))

ACL_SCRIPT=r"""$ErrorActionPreference='Stop'
$privateTarget=[System.IO.Path]::GetFullPath($args[0])
$sid=[System.Security.Principal.WindowsIdentity]::GetCurrent().User
$acl=[System.Security.AccessControl.DirectorySecurity]::new()
$acl.SetOwner($sid)
$acl.SetAccessRuleProtection($true,$false)
$rule=[System.Security.AccessControl.FileSystemAccessRule]::new($sid,'FullControl','ContainerInherit,ObjectInherit','None','Allow')
$acl.AddAccessRule($rule)
[System.IO.Directory]::SetAccessControl($privateTarget,$acl)
$actual=[System.IO.Directory]::GetAccessControl($privateTarget)
$rules=$actual.GetAccessRules($true,$true,[System.Security.Principal.SecurityIdentifier])
if ($rules.Count -ne 1 -or $rules[0].IdentityReference.Value -ne $sid.Value -or -not $actual.AreAccessRulesProtected -or $actual.GetOwner([System.Security.Principal.SecurityIdentifier]).Value -ne $sid.Value) { throw 'Owner-only ACL verification failed' }
Write-Output 'OWNER_ONLY_VERIFIED'
"""
KERNEL_SCRIPT=r"""set -f
export LC_ALL=C
count=0
while IFS=' ' read -r source target filesystem options dump pass extra; do
 [ "$target" = /run/wa-secrets ] || continue
 count=$((count+1))
 [ -n "$source" ] && [ "$filesystem" = tmpfs ] && [ -z "$extra" ] || exit 21
 case "$options" in ''|,*|*,|*,,*) exit 22;; esac
 seen_rw=0; seen_noexec=0; seen_nosuid=0; seen_nodev=0
 saved_ifs=$IFS; IFS=,; set -- $options; IFS=$saved_ifs
 for option do
  case "$option" in rw) seen_rw=$((seen_rw+1));; noexec) seen_noexec=$((seen_noexec+1));; nosuid) seen_nosuid=$((seen_nosuid+1));; nodev) seen_nodev=$((seen_nodev+1));; ro|exec|suid|dev) exit 23;; esac
 done
 [ "$seen_rw" -eq 1 ] && [ "$seen_noexec" -eq 1 ] && [ "$seen_nosuid" -eq 1 ] && [ "$seen_nodev" -eq 1 ] || exit 24
done < /proc/mounts
[ "$count" -eq 1 ] || exit 25
[ "$(stat -c '%F:%a:%u:%g' -- /run/wa-secrets)" = 'directory:700:0:0' ] || exit 26
[ "$(stat -c '%u:%g' -- /var/lib/postgresql/data)" = "$(id -u postgres):$(id -g postgres)" ] || exit 27
printf '%s\n' 'WA_LEASE_MECHANISM_TMPFS_PGDATA_OK'
"""

class Operator:
 def __init__(self,manifest_path,root,external):
  self.root=Path(root).resolve();self.external=Path(external).resolve();self.manifest_path=Path(manifest_path).resolve();self.manifest_bytes=closed(self.manifest_path)
  self.m=unique(self.manifest_bytes);self.out=Path(self.m['evidence_directory']);self.private=self.out/'private';self.run_id=self.m['run_id'];self.target=self.m['target'];self.cid=None;self.volume_created=None;self.container_attempted=False;self.volume_attempted=False;self.setup_attempted=False;self.setup_done=False;self.kernel=False;self.ready=False;self.passwords={};self.secrets=[];self.staged={};self.source_blobs={}
  self.report={'schema':'workinants.lease-mechanism-v1-run-evidence.v1','run_id':self.run_id,'source_commit':self.m['source_commit'],'source_tree':self.m['source_tree'],'packet_sha256':self.m['packet_sha256'],'status':'IN_PROGRESS','stage':'ENTRY','evidence_complete':True,'persistence_failure':False,'output_complete':True,'events':[],'authentication':[],'cases':[],'closures':[],'unexpected':[],'cleanup':{},'limits':{'Posture':'D','synthetic_mechanism_only':True,'canonical_application':'NOT_RUN','Prisma':'NOT_RUN','native29089':'NOT_RUN','oracle416':'NOT_RUN','ledger22':'NOT_RUN','migration_adoption':False,'worker_loop':False,'assertion_promotion':False}}
 def fail(self,code):
  need(type(code)is str and re.fullmatch('[A-Z0-9_]{1,96}',code),'FAILURE_CODE_ENUM')
  item={'stage':self.report['stage'],'code':code};self.report.setdefault('primary_failure',item)
  if item not in self.report['unexpected']:self.report['unexpected'].append(item)
  self.report['status']='STOPPED_ATTEMPT_PRESERVED'
 def save(self):
  raw=data(self.report);need(not any(s.encode()in raw for s in self.secrets),'SECRET_IN_EVIDENCE');tmp=self.out/'run-evidence.json.tmp'
  with tmp.open('wb')as f:f.write(raw);f.flush();os.fsync(f.fileno())
  tmp.replace(self.out/'run-evidence.json')
 def persist(self):
  try:self.save();return True
  except BaseException:
   self.report['evidence_complete']=False;self.report['persistence_failure']=True;self.fail('EVIDENCE_WRITE_UNCONFIRMED');return False
 def stage(self,name):self.report['stage']=name;need(self.persist(),'EVIDENCE_WRITE_UNCONFIRMED')
 def record(self,kind,value,safety=False):
  self.report['events'].append({'kind':kind,**value});ok=self.persist()
  if not safety:need(ok,'EVIDENCE_WRITE_UNCONFIRMED')
  return ok
 def docker(self,args,payload=None,timeout=30):return process(['docker','--context','desktop-linux',*args],payload,timeout)
 def call(self,args,payload=None,timeout=15):return process(args,payload,timeout)
 def ok(self,args,payload=None,timeout=30):
  r=self.docker(args,payload,timeout);need(type(r.returncode)is int and r.returncode==0 and r.stderr==b'','DOCKER_OPERATION_FAILED');return r.stdout
 def inventory(self):
  c=self.ok(['container','ls','-a','--format','{{.Names}}']);v=self.ok(['volume','ls','--format','{{.Name}}']);return set(c.decode('utf8').splitlines()),set(v.decode('utf8').splitlines())
 def inspect(self,kind):
  need(kind in ('container','volume'),'RESOURCE_KIND');name=self.target['name'if kind=='container'else'volume'];values=unique(self.ok([kind,'inspect',name]));need(type(values)is list and len(values)==1 and type(values[0])is dict,'EXACT_RESOURCE_INSPECTION');return values[0]
 def source_gate(self):
  path=self.root/'context/reconciliation/local-f0-runtime-lease-mechanism-v1-source-validation.json';v=unique(closed(path));five={n:sha(closed(self.external/n))for n in FIVE}
  need(v.get('operator_sources_sha256')==five==self.m.get('external_files_sha256'),'EXACT_EXTERNAL_FIVE')
  for key in ('independent_source_review','independent_binary_safety_review'):
   g=v.get(key);need(type(g)is dict and g.get('decision')=='SOURCE_APPROVED'and g.get('operator_sources_sha256')==five,'PENDING_SOURCE_REVIEW')
  need(self.m.get('review_status')=='APPROVED_LOCAL_F0_LEASE_MECHANISM_V1_ATTEMPT','PENDING_OPERATIONAL_LITERAL')
  p=self.external/FIVE[4];raw=closed(p);need(sha(raw)==five[FIVE[4]],'PINNER_SOURCE_DRIFT')
  pin=types.ModuleType('_lease_mechanism_pin');pin.__file__=str(p);exec(compile(raw,str(p),'exec'),pin.__dict__);proof=pin.validate(self.m,self.root,self.external)
  self.source_blobs={n:closed(self.root/n)for n in self.m['packet_files_sha256']};self.report['events'].append({'kind':'SOURCE_VERIFICATION',**proof})
  p=self.external/FIVE[1];raw=closed(p);need(sha(raw)==five[FIVE[1]],'STEPS_SOURCE_DRIFT');steps=types.ModuleType('_lease_mechanism_steps');steps.__file__=str(p);exec(compile(raw,str(p),'exec'),steps.__dict__);return steps
 def preflight(self):
  context=unique(self.ok(['context','inspect','desktop-linux']));need(type(context)is list and len(context)==1 and context[0].get('Endpoints',{}).get('docker',{}).get('Host')=='npipe:////./pipe/dockerDesktopLinuxEngine','LOCAL_ENDPOINT_REQUIRED')
  server=unique(self.ok(['version','--format','{{json .Server}}']));need(server.get('Os')=='linux'and server.get('Arch')=='amd64','LINUX_AMD64_REQUIRED')
  c,v=self.inventory();need(self.target['name']not in c and self.target['volume']not in v,'RESOURCE_NAME_CONFLICT');self.record('LOCAL_PREFLIGHT',{'local_endpoint':True,'linux_amd64':True,'exact_names_absent':True})
 def ensure_image(self):
  r=self.docker(['image','inspect',IMAGE])
  if r.returncode!=0:self.ok(['pull',IMAGE],timeout=120);r=self.docker(['image','inspect',IMAGE])
  need(r.returncode==0 and r.stderr==b'','PINNED_IMAGE_REQUIRED');raw=self.source_blobs['scripts/sql-review/fixtures/postgres-17.11-approved-manifest.json'];path='scripts/sql-review/local_image_identity.py';mod=types.ModuleType('_lease_image_identity');exec(compile(self.source_blobs[path],path,'exec'),mod.__dict__)
  try:proof=mod.validate_cached_image(unique(r.stdout),raw)
  except mod.ImageIdentityError as e:raise Stop(e.code)from None
  self.report['image']=proof;self.persist();return proof
 def create(self):
  self.private.mkdir();helper=self.out/'set-private-acl.ps1';helper.write_bytes(ACL_SCRIPT.encode());r=process(['powershell.exe','-NoProfile','-NonInteractive','-File',str(helper),str(self.private)])
  need(r.returncode==0 and r.stdout.strip()==b'OWNER_ONLY_VERIFIED'and r.stderr==b'','HOST_OWNER_ONLY_ACL')
  self.passwords={role:secrets.token_hex(32)for role in ROLES};self.secrets.extend(self.passwords.values());secret=self.private/'ok-bootstrap-password'
  with secret.open('xb')as f:f.write((self.passwords['postgres']+'\n').encode())
  c,v=self.inventory();need(self.target['name']not in c and self.target['volume']not in v,'LATE_RESOURCE_CONFLICT');labels=[item for k,v in self.target['labels'].items()for item in ('--label',k+'='+v)]
  self.volume_attempted=True;self.ok(['volume','create',*labels,self.target['volume']]);disk=self.inspect('volume');need(disk.get('Name')==self.target['volume']and disk.get('Labels')==self.target['labels']and type(disk.get('CreatedAt'))is str,'CREATED_VOLUME_IDENTITY');self.volume_created=disk['CreatedAt']
  args=['container','create','--name',self.target['name'],*labels,'--network','none','--platform','linux/amd64','--mount','type=volume,src='+self.target['volume']+',dst=/var/lib/postgresql/data','--mount','type=bind,src='+str(secret)+',dst=/run/bootstrap-password,readonly','--tmpfs','/run/wa-secrets:rw,nosuid,noexec,nodev,mode=0700','-e','POSTGRES_DB='+DATABASE,'-e','POSTGRES_PASSWORD_FILE=/run/bootstrap-password','-e','POSTGRES_HOST_AUTH_METHOD=scram-sha-256','-e','POSTGRES_INITDB_ARGS=--auth-host=scram-sha-256',IMAGE,'postgres']
  for option in ('password_encryption=scram-sha-256','log_statement=none','log_min_error_statement=panic','log_error_verbosity=terse','log_line_prefix=WA_F0_DIAG|%e|%u|%d|','lc_messages=C','log_min_messages=warning'):args+=['-c',option]
  self.container_attempted=True;returned=self.ok(args).strip().decode('ascii');need(re.fullmatch('[0-9a-f]{64}',returned)is not None,'CREATED_CID');self.cid=returned
  self.inspect_owner(False);self.ok(['container','start',self.cid]);self.inspect_owner(True)
  for _ in range(60):
   r=self.docker(['exec',self.cid,'pg_isready','-h','127.0.0.1','-p','5432','-U','postgres','-d',DATABASE])
   if r.returncode==0:self.ready=True;break
   time.sleep(1)
  need(self.ready,'DATABASE_READINESS_TIMEOUT')
  pgpass=''.join('127.0.0.1:5432:'+DATABASE+':'+role+':'+self.passwords[role]+'\n'for role in ROLES).encode();out=self.ok(['exec','-i',self.cid,'sh','-ceu','umask 077; cat > /run/wa-secrets/pgpass; chmod 600 /run/wa-secrets/pgpass; stat -c "%a:%u:%g" /run/wa-secrets/pgpass'],pgpass)
  need(out==b'600:0:0\n','PGPASS_OWNER_MODE');self.record('RESOURCE_READY',{'container_id':self.cid,'volume_created_at':self.volume_created,'kernel_tmpfs':True,'owner_only_credentials':True})
 def inspect_owner(self,running):
  c=self.inspect('container');d=self.inspect('volume');h=c.get('HostConfig',{});cfg=c.get('Config',{});mounts=c.get('Mounts');ports=c.get('NetworkSettings',{}).get('Ports')
  need(c.get('Id')==self.cid and c.get('Name')=='/'+self.target['name']and cfg.get('Labels')==self.target['labels']and cfg.get('Image')==IMAGE and c.get('Image')==self.report['image']['image_id']and c.get('Platform')=='linux'and c.get('State',{}).get('Running')is running,'EXACT_CONTAINER_IDENTITY')
  need(h.get('NetworkMode')=='none'and h.get('PortBindings')in(None,{})and h.get('Privileged')is False and h.get('PidMode')==''and h.get('IpcMode')in('','private')and h.get('Devices')in(None,[])and h.get('CapAdd')in(None,[])and h.get('Links')in(None,[])and(ports is None or type(ports)is dict and all(v is None for v in ports.values())),'EXACT_CONTAINER_ISOLATION')
  need(type(mounts)is list and 2<=len(mounts)<=3,'EXACT_MOUNT_SET');counts={'volume':0,'bind':0,'tmpfs':0};secret=str(self.private/'ok-bootstrap-password');w=PureWindowsPath(secret);aliases={secret}
  if w.drive:aliases.add('/run/desktop/mnt/host/'+w.drive[0].lower()+'/'+'/'.join(w.parts[1:]))
  for m in mounts:
   kind=m.get('Type');need(kind in counts,'EXTRA_MOUNT');counts[kind]+=1
   if kind=='volume':need(m.get('Name')==self.target['volume']and m.get('Destination')=='/var/lib/postgresql/data'and m.get('RW')is True,'DATA_MOUNT')
   if kind=='bind':need(m.get('Source')in aliases and m.get('Destination')=='/run/bootstrap-password'and m.get('RW')is False,'BOOTSTRAP_MOUNT')
   if kind=='tmpfs':need(m.get('Destination')=='/run/wa-secrets'and m.get('RW')is True,'TMPFS_API_MOUNT')
  need(counts['volume']==counts['bind']==1 and counts['tmpfs']in(0,1),'EXACT_LOGICAL_MOUNTS');tmp=h.get('Tmpfs');need(type(tmp)is dict and set(tmp)=={'/run/wa-secrets'},'EXACT_TMPFS_KEY');tokens=tmp['/run/wa-secrets'].split(',');need(len(tokens)==5 and len(set(tokens))==5 and set(tokens)in({'rw','nosuid','noexec','nodev','mode=0700'},{'rw','nosuid','noexec','nodev','mode=700'}),'EXACT_TMPFS_OPTIONS')
  need(d.get('Name')==self.target['volume']and d.get('CreatedAt')==self.volume_created and d.get('Labels')==self.target['labels']and d.get('Driver')=='local'and d.get('Scope')=='local'and not d.get('Options'),'EXACT_VOLUME_IDENTITY')
  if running:need(self.ok(['exec','-i',self.cid,'sh','-ceu',KERNEL_SCRIPT])==b'WA_LEASE_MECHANISM_TMPFS_PGDATA_OK\n','RUNNING_KERNEL_PROOF');self.kernel=True
  self.record('RESOURCE_IDENTITY',{'running':running,'exact_identity':True,'kernel_proved':running})
 def psql_args(self,role,wrong=False):
  need(role in ROLES and self.kernel and re.fullmatch('[0-9a-f]{64}',self.cid or'')is not None,'PSQL_OWNED_ROLE_CID')
  return ['docker','--context','desktop-linux','exec','-i','-e','PGPASSFILE=/run/wa-secrets/'+('wrong-pgpass'if wrong else'pgpass'),'-e','PGSSLMODE=disable','-e','PGGSSENCMODE=disable','-e','PGAPPNAME=wa-lease-'+self.run_id,'-e','PGOPTIONS=-c statement_timeout=5000 -c lock_timeout=1000 -c idle_in_transaction_session_timeout=30000',self.cid,'psql','-X','-w','-qAt','-v','ON_ERROR_STOP=1','-v','VERBOSITY=verbose','-v','SHOW_CONTEXT=errors','-h','127.0.0.1','-p','5432','-U',role,'-d',DATABASE]
 def cleanup(self):
  self.report['stage']='CONTROLLED_CLEANUP';proof={'container_removed':False,'volume_removed':False,'private_removed':False,'physical_absence':False,'image_retained':False}
  if not self.container_attempted and not self.volume_attempted and not self.private.exists():
   self.report['cleanup']={'resources_created':False,'resource_operations':'NOT_RUN','private_removed':True};self.persist();return
  try:
   c,v=self.inventory()
   if self.target['name']in c:
    x=self.inspect('container');need(self.container_attempted and self.cid is not None and x.get('Id')==self.cid and x.get('Name')=='/'+self.target['name']and x.get('Config',{}).get('Labels')==self.target['labels'],'CLEANUP_CONTAINER_IDENTITY');self.ok(['container','rm','-f',self.cid]);proof['container_removed']=True
   if self.target['volume']in v:
    x=self.inspect('volume');need(self.volume_attempted and self.volume_created is not None and x.get('CreatedAt')==self.volume_created and x.get('Labels')==self.target['labels']and x.get('Name')==self.target['volume'],'CLEANUP_VOLUME_IDENTITY');self.ok(['volume','rm',self.target['volume']]);proof['volume_removed']=True
   if self.private.exists():
    children=list(self.private.iterdir());need(all(p.name=='ok-bootstrap-password'and p.is_file()and not p.is_symlink()for p in children),'CLEANUP_PRIVATE_EXACT_SET')
    for p in children:p.unlink()
    self.private.rmdir()
   proof['private_removed']=not self.private.exists();c,v=self.inventory();proof['physical_absence']=self.target['name']not in c and self.target['volume']not in v and proof['private_removed'];r=self.docker(['image','inspect',IMAGE]);proof['image_retained']=r.returncode==0 and r.stderr==b'';need(proof['physical_absence']and proof['image_retained'],'CLEANUP_ABSENCE_UNCONFIRMED')
  except BaseException as e:self.fail(e.code if isinstance(e,Stop)else'CLEANUP_UNEXPECTED')
  self.report['cleanup']=proof;self.persist()
 def source_barrier(self):
  need(closed(self.manifest_path)==self.manifest_bytes,'MANIFEST_REFERENCE_DRIFT')
  for n,w in self.m['packet_files_sha256'].items():need(sha(closed(self.root/n))==w,'FINAL_SOURCE_DRIFT')
  for n,w in self.m['external_files_sha256'].items():need(sha(closed(self.external/n))==w,'FINAL_EXTERNAL_DRIFT')
 def run(self):
  need(not self.out.exists()and self.out.parent==self.external,'FRESH_OUTPUT_DIRECTORY');steps=None
  try:
   self.report['stage']='SOURCE_VERIFICATION';steps=self.source_gate();self.out.mkdir();self.stage('LOCAL_PREFLIGHT');self.preflight();self.ensure_image();self.create();steps.execute(self)
  except BaseException as e:
   if not self.out.exists():self.out.mkdir()
   self.fail(e.code if hasattr(e,'code')and type(e.code)is str else'UNEXPECTED_WRAPPER_FAILURE');self.persist()
  finally:
   if steps is not None and self.ready:
    try:steps.finalize(self)
    except BaseException as e:self.fail(e.code if hasattr(e,'code')and type(e.code)is str else'FINALIZATION_UNEXPECTED');self.persist()
   self.cleanup()
   try:self.source_barrier()
   except BaseException as e:self.fail(e.code if isinstance(e,Stop)else'FINAL_SOURCE_UNEXPECTED')
   if not self.report['unexpected']and self.report['evidence_complete']and self.report['cleanup'].get('physical_absence')and len(self.report['cases'])==11:self.report['status']='PASS_SYNTHETIC_PG_EXPRESSION_ACL_MECHANISM_ONLY'
   self.report['stage']='COMPLETE';self.persist()
   try:
    saved=closed(self.out/'run-evidence.json');expected=sha(saved);length=len(saved);self.source_barrier();need(closed(self.out/'run-evidence.json')==saved and len(saved)==length and sha(saved)==expected,'FINAL_SAVED_REFERENCE_DRIFT')
   except BaseException as e:self.fail(e.code if isinstance(e,Stop)else'FINAL_REFERENCE_UNEXPECTED');self.persist()
  return 0 if self.report['status']=='PASS_SYNTHETIC_PG_EXPRESSION_ACL_MECHANISM_ONLY'else 1

def main(argv=None):
 p=argparse.ArgumentParser();p.add_argument('--manifest',required=True);p.add_argument('--root',required=True);a=p.parse_args(argv);return Operator(a.manifest,a.root,Path(__file__).resolve().parent).run()
if __name__=='__main__':raise SystemExit(main())

