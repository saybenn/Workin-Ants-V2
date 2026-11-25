"""Focused CSP1 source/transport/whole-lifecycle mocks. No real external boundary."""
import ast,hashlib,io,json,os,queue,re,runpy,shutil,socket,subprocess,tempfile,threading,time,types,unittest
from pathlib import Path
from contextlib import ExitStack,redirect_stdout,redirect_stderr
from copy import deepcopy
from unittest.mock import patch,Mock
from pglast import ast as pgast,parse_sql,parser
TASK=Path(__file__).resolve().parent;ROOT=TASK/'workinants-correction-pass'
FIVE=('execute_local_f0_customer_stale_predecessor_v1_20261120.py','local_f0_customer_stale_predecessor_v1_operation_steps.py','prepare_local_f0_customer_stale_predecessor_v1_plan.py','check_local_f0_customer_stale_predecessor_v1_operation.py','pin_local_f0_customer_stale_predecessor_v1_plan_20261120.py')
ARCHIVE='context/reconciliation/local-f0-operation-sources/customer-stale-predecessor-owned-v1';VALIDATION='context/reconciliation/local-f0-customer-stale-predecessor-owned-v1-source-validation.json'
GATES=('independent_source_review','independent_owned_resource_review','independent_safety_sql_review','independent_binary_transport_review','Root_source_review')
FLAG='APPROVED_LOCAL_F0_CUSTOMER_STALE_PREDECESSOR_OWNED_V1_ATTEMPT';CID='a'*64;CANARY='CSP1_PRIVATE_PASSWORD_OPAQUE_HANDLE_STDERR_CANARY'
IMAGE='docker.io/library/postgres:17.11@sha256:996e9dc583ba9f0265a2c75547a9c95fb22c251e394749cab205a0a00e1856a1';CONFIG='sha256:eb0fb2377534e65aad04f37838956b3dfb888e1a3dd3c1acf957bc6557eb6c7d'
sha=lambda b:hashlib.sha256(b).hexdigest()
encoded=lambda v:(json.dumps(v,indent=2,allow_nan=False)+'\n').encode()
ctx_protocol=runpy.run_path(str(ROOT/'scripts/sql-review/run-context-control-rehearsal.py'))
child_tests=runpy.run_path(str(ROOT/'scripts/check-customer-stale-predecessor-v1.py'))
ChildProcess=child_tests['Process'];ChildWorld=child_tests['World'];child_constant=child_tests['constant']
MODEL_CATALOG_PINS={'native-before': '24cf2f60e9c6a396d53b8f897b0aa6feea6b8498a1f231eb0241fc6e157d0eb0', 'ledger-observation': '5a3d33491366fb9587bcc4a167efa4e38bda170b7b3291c022f28676dbdd94b3', 'oracle-preflight': 'e64b96e2f73e7a6d369d61c09301dc7c986c08bcd1cf95af06c6ab9756bcbe66', 'oracle-results': 'd7f91fb358b73d3f36acde73ec730c41259009c1e0f06931ded2a7d44510f995', 'oracle-closure': '89067a06862e197fd49f3aed1e3f18bfc93d6a6c2035f9cdfc85a57036257ab9', 'acl-preflight': 'b1dffe67c99d83c46073c8db1f5e14bbda1b5dc0ed053be56d56a67a6018f3c8', 'text-preflight': '176676da1274c55ec6f8800089b61d1c5249c44ed52b3ecfbcf2c8edf6a3cda1'}
class PrimitiveCommandModel:
 def response(self, value='', code=0, stderr='', binary=False):
     out = value if isinstance(value, str) else json.dumps(value)
     return types.SimpleNamespace(returncode=code, stdout=out.encode() if binary else out, stderr=stderr.encode() if binary else stderr)
 def image_value(self):
     return {'Id': self.md, 'Os': 'linux', 'Architecture': 'amd64', 'RepoDigests': ['postgres@' + self.md], 'Descriptor': {'digest': self.md, 'mediaType': 'application/vnd.oci.image.manifest.v1+json', 'size': 3628}, 'Config': {'Env': ['PG_VERSION=17.11-1.pgdg13+1']}}
 def container(self):
     return {'Id': CID, 'Name': '/' + self.name, 'Config': {'Image': self.image, 'Labels': self.labels}, 'Image': self.md, 'Platform': 'linux', 'State': {'Running': self.running}, 'HostConfig': {'NetworkMode': 'none', 'PortBindings': {}, 'Privileged': False, 'PidMode': '', 'IpcMode': 'private', 'Devices': [], 'CapAdd': [], 'Links': None, 'Tmpfs': {'/run/wa-secrets': 'rw,nosuid,noexec,nodev,mode=0700'}}, 'NetworkSettings': {'Ports': {'5432/tcp': None}}, 'Mounts': [{'Type': 'volume', 'Name': self.volume, 'Destination': '/var/lib/postgresql/data', 'RW': True}, {'Type': 'bind', 'Source': self.target['target']['bootstrap_secret_host_path'], 'Destination': '/run/bootstrap-password', 'RW': False}]}
 def process(self, args, **options):
     try:
         return self._process(args, **options)
     except BaseException as error:
         text = error.args[0] if type(error) is AssertionError and error.args else None
         self.last_mock_fault = {'class': type(error).__name__, 'fixed_code': text if type(text) is str and re.fullmatch('[A-Z0-9_]{1,100}', text) else 'UNCLASSIFIED_MODEL_BOUNDARY'}
         raise
 def _process(self, args, **options):
     self.calls.append((list(args), self.n['report']['stage'] if self.n else 'ENTRY'))
     text = options.get('input') or ''
     if args[0] == 'git':
         return self.fixture.git(args, **options)
     if args[0] == 'powershell.exe':
         return self.response('OWNER_ONLY_VERIFIED\n')
     assert args[:3] == ['docker', '--context', 'desktop-linux'], 'UNREGISTERED_PROCESS'
     d = args[3:]
     if d[:2] == ['context', 'inspect']:
         return self.response([{'Name': 'desktop-linux', 'Endpoints': {'docker': {'Host': 'npipe:////./pipe/dockerDesktopLinuxEngine'}}}])
     if d[0] == 'version':
         return self.response({'Version': '29.6.2', 'Os': 'linux', 'Arch': 'amd64'})
     if d[:2] == ['container', 'ls']:
         return self.response('\n'.join(self.containers))
     if d[:2] == ['volume', 'ls']:
         if self.mutate_cleanup_reference and self.deploys == 1 and (not self.containers) and (not self.volumes) and (not self.cleanup_reference_mutated):
             path = Path(self.manifest['evidence_directory']) / 'app-write-two-component/app-write-two-results.json'
             raw = path.read_bytes()
             changed = raw.replace(b'"status": "PASS_FINITE_TWO_APP_WRITE_CRITERIA_ONLY"', b'"status": "FAIL_FINITE_TWO_APP_WRITE_CRITERIA_ONLY"')
             assert raw != changed and len(raw) == len(changed), 'ACTUAL_REFERENCE_MUTANT_SHAPE'
             path.write_bytes(changed)
             self.cleanup_reference_mutated = True
         return self.response('\n'.join(self.volumes))
     if d[:2] == ['image', 'inspect']:
         return self.response([self.image_value()])
     if d[:3] == ['buildx', 'imagetools', 'inspect']:
         return self.response((self.fixture.root / 'scripts/sql-review/fixtures/postgres-17.11-approved-manifest.json').read_text())
     if d[:2] == ['volume', 'create']:
         self.volumes[self.volume] = {'Name': self.volume, 'CreatedAt': 'MOCK_CREATED', 'Labels': self.labels, 'Driver': 'local', 'Options': {}, 'Scope': 'local'}
         return self.response(self.volume)
     if d[:2] == ['volume', 'inspect']:
         return self.response([self.volumes[self.volume]]) if self.volume in self.volumes else self.response('', 1)
     if d[:2] == ['container', 'create']:
         self.containers[self.name] = CID
         return self.response(CID)
     if d[:2] == ['container', 'inspect'] or d[0] == 'inspect':
         return self.response([self.container()]) if self.name in self.containers else self.response('', 1)
     if d[:2] == ['container', 'start']:
         assert d[2] == CID
         self.running = True
         return self.response(CID)
     if d[:2] == ['container', 'rm']:
         assert d == ['container', 'rm', '-f', CID]
         self.containers.clear()
         self.running = False
         return self.response(CID)
     if d[:2] == ['volume', 'rm']:
         assert d == ['volume', 'rm', self.volume]
         self.volumes.clear()
         return self.response(self.volume)
     if d[0] == 'cp':
         assert d[-1].startswith(CID + ':/run/wa-f0-')
         return self.response()
     assert d[0] == 'exec', 'UNREGISTERED_DOCKER'
     stage = self.n['report']['stage'] if self.n else ''
     if self.fail_stage and stage == self.fail_stage:
         raise OSError(CANARY)
     if 'pg_isready' in d:
         return self.response()
     if 'psql' in d:
         return self.sql(args, text, options)
     if 'sh' in d:
         script = d[-1]
         if 'WA_OWNER_SECRET_TMPFS_V2_OK' in script:
             return self.response('WA_OWNER_SECRET_TMPFS_V2_OK\n')
         if 'stat -c' in script:
             return self.response('600:0:0\n')
         raise AssertionError('UNREGISTERED_SHELL')
     if '/usr/bin/sha256sum' in d:
         paths = d[d.index('--') + 1:]
         values = {**{'/run/wa-f0-tools/' + k: v for k, v in self.target['tools']['files_sha256'].items()}, **{'/run/wa-f0-source/' + k: v for k, v in self.target['source']['runtime_files_sha256'].items()}}
         return self.response(''.join((values[p] + '  ' + p + '\n' for p in paths)))
     if d[-1] == '--version':
         return self.response('v24.22.1\n' if 'node/bin/node' in d[-2] else 'schema-engine d1b3f377ca835d73fd50954a5e22128b9ebdd6b8\n')
     if 'mkdir' in d or 'tar' in d or 'rm' in d:
         return self.response()
     if '/run/wa-f0-source/scripts/sql-review/local-f0-migrate-runner.mjs' in d:
         public = json.loads(text)
         assert d[-1] == 'deploy' and public['observed']['container_id'] == CID
         self.deploys += 1
         assert self.deploys == 1, 'SECOND_DEPLOY_FORBIDDEN'
         return self.response({'schema': 'workinants.local-f0-migrate-result.v2', 'operation': 'deploy', 'status': 'CLI_COMPLETED_REQUIRES_INDEPENDENT_LEDGER_CATALOG_CHECKS', 'exit_code': 0, 'prisma_codes': [], 'sqlstates': [], 'no_pending_message_observed': False, 'raw_output_discarded': True, 'database_qualification_claimed': False, 'run_id': self.manifest['run_id'], 'container_id': CID, 'source_sql_sha256': self.target['source']['integrated_sql_sha256'], 'attestation_sha256': sha(text.encode()), 'diagnostic_format': {'text_valid': True, 'sgr_stripped': False, 'headers_valid': True, 'prisma_header_present': False, 'prisma_header_unique': False, 'database_header_present': False, 'database_header_unique': False}})
     raise AssertionError('UNREGISTERED_EXEC')


class SourcePreservation(unittest.TestCase):
 def test_exact_original_115_and_guard_source(self):
  before=json.loads((ROOT/ARCHIVE/'author-source/before-author-preservation.json').read_bytes())
  for n,h in before['child_current_files_sha256'].items():self.assertEqual(sha((ROOT/n).read_bytes()),h)
  packet=json.loads((ROOT/'review-output/customer-stale-predecessor-v1/fixtures.json').read_bytes());self.assertEqual({r['table']for r in packet['fixture_bypasses']},{'app.users','app.user_security_profiles'})
  self.assertEqual(sha((ROOT/'review-output/foundation-application.review.sql').read_bytes()),'5ae39abf991f9c189e367eb6ab6968b0ad50836bf4220ac27ef8c18306ac26ad');self.assertEqual(sha((ROOT/'context/reconciliation/foundation-sql-draft-access.json').read_bytes()),'f9d529a7fc481beea3fcb0b2307fce47c44d7168380a7e2dfab6b9be44831eea')
class ByteStream:
 def __init__(self,process,index):self.process=process;self.index=index;self.offset=0;self.closed=False
 def read(self,count):
  self.process.done.wait(5);assert self.process.done.is_set(),'MODEL_RESULT_NOT_RECEIVED'
  value=(self.process.stdout_value,self.process.stderr_value)[self.index];chunk=value[self.offset:self.offset+count];self.offset+=len(chunk);return chunk
 def close(self):self.closed=True
class ByteInput:
 def __init__(self,process):self.process=process;self.payload=bytearray();self.closed=False
 def write(self,data):
  assert type(data)is bytes;self.payload.extend(data);return len(data)
 def close(self):
  if self.closed:return
  self.closed=True
  try:
   result=self.process.dispatch(self.process.args,bytes(self.payload))
   self.process.returncode=result.returncode;self.process.stdout_value=result.stdout if type(result.stdout)is bytes else result.stdout.encode('utf8');self.process.stderr_value=result.stderr if type(result.stderr)is bytes else result.stderr.encode('utf8')
  except BaseException as error:self.process.error=error;self.process.returncode=1
  finally:self.process.done.set()
class ByteProcess:
 def __init__(self,args,dispatch):
  self.args=args;self.dispatch=dispatch;self.done=threading.Event();self.returncode=None;self.stdout_value=b'';self.stderr_value=b'';self.error=None;self.stdin=ByteInput(self);self.stdout=ByteStream(self,0);self.stderr=ByteStream(self,1)
 def poll(self):return self.returncode
 def wait(self,timeout=None):
  if not self.done.wait(timeout):raise subprocess.TimeoutExpired(self.args,timeout)
  return self.returncode
 def terminate(self):self.returncode=-15;self.done.set()
 def kill(self):self.returncode=-9;self.done.set()

def mock_git(root,args,payload=None,*,text=False):
 assert args[0]=='git';tail=args[args.index('core.longpaths=true')+1:]if'core.longpaths=true'in args else args[1:]
 if tail==['rev-parse','HEAD']:body=b'a'*40+b'\n'
 elif tail==['rev-parse','HEAD^{tree}']:body=b'b'*40+b'\n'
 elif tail==['cat-file','--batch']:
  pieces=[]
  for request in payload.decode('utf8').splitlines():
   commit,name=request.split(':',1);assert commit=='a'*40;raw=(root/name).read_bytes();oid=hashlib.sha1(b'blob '+str(len(raw)).encode()+b'\0'+raw).hexdigest().encode();pieces.extend((oid+b' blob '+str(len(raw)).encode()+b'\n',raw,b'\n'))
  body=b''.join(pieces)
 elif len(tail)==2 and tail[0]=='show':commit,name=tail[1].split(':',1);assert commit=='a'*40;body=(root/name).read_bytes()
 else:raise AssertionError('UNMODELED_READ_ONLY_GIT')
 return subprocess.CompletedProcess(args,0,body.decode('utf8')if text else body,''if text else b'')

class Fixture:
 def __init__(self):
  self.temporary=tempfile.TemporaryDirectory(prefix='CSP1-owned-offline-',dir=TASK);self.task=Path(self.temporary.name);self.root=self.task/'workinants-correction-pass';self.root.mkdir()
  prep=runpy.run_path(str(TASK/FIVE[2]));baseline=json.loads((TASK/'catalog-baseline.json').read_bytes());packet=json.loads((ROOT/'review-output/customer-stale-predecessor-v1/fixtures.json').read_bytes());five={n:sha((TASK/n).read_bytes())for n in FIVE}
  names=prep['source_inventory'](baseline['packet_files_sha256'],packet,five,False)
  for n,h in names.items():target=self.root/n;target.parent.mkdir(parents=True,exist_ok=True);raw=(ROOT/n).read_bytes();assert sha(raw)==h;target.write_bytes(raw)
  for n,h in baseline['catalog']['tool_source_files_sha256'].items():target=self.root/n;target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes((ROOT/n).read_bytes());assert sha(target.read_bytes())==h
  for n in FIVE:(self.task/n).write_bytes((TASK/n).read_bytes())
  self.pending_owned=(self.root/VALIDATION).read_bytes();owned=json.loads(self.pending_owned)
  receipt={'schema':'workinants.CSP1.OFFLINE-only-future-review-fixture.v1','decision':'SOURCE_APPROVED','operator_sources_sha256':five,'actual_runtime_authority':False}
  rp=ARCHIVE+'/reviews/OFFLINE-only-future-peer-Root-fixture.json';target=self.root/rp;target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(encoded(receipt))
  for key in GATES:owned[key]={'decision':'SOURCE_APPROVED','path':rp,'sha256':sha(target.read_bytes()),'operator_sources_sha256':five}
  owned['archive_files_sha256']={p.relative_to(self.root).as_posix():sha(p.read_bytes())for p in(self.root/ARCHIVE).rglob('*')if p.is_file()};(self.root/VALIDATION).write_bytes(encoded(owned))
  archive=self.task/'pinned-prisma-tools.tar.gz';shutil.copyfile(baseline['tool_archive'],archive);baseline['tool_archive']=str(archive)
  old=baseline['migration_targets']['ok'];nested=self.task/'OFFLINE-baseline-nested.json';nested.write_bytes(Path(old['manifest_path']).read_bytes());old['manifest_path']=str(nested)
  self.baseline=self.task/'OFFLINE-baseline.json';self.baseline.write_bytes(encoded(baseline));self.prep=runpy.run_path(str(self.task/FIVE[2]))
  result=self.prep['prepare'](self.baseline,sha(self.baseline.read_bytes()));self.path=Path(result['operation_manifest']);self.unpinned=self.path.read_bytes()
  self.byte_processes=[];self.pin=runpy.run_path(str(self.task/FIVE[4]));self.pin_bytes=[]
  def popen(args,**kwargs):
   p=ByteProcess(args,lambda a,b:mock_git(self.root,a,b or None));self.byte_processes.append(p);return p
  with patch.object(subprocess,'Popen',side_effect=popen):self.pin_result=self.pin['pin'](self.path)
  self.pending=self.path.read_bytes();m=json.loads(self.pending);assert m['review_status']=='PENDING_OPERATIONAL_REVIEW';m['review_status']=FLAG;self.path.write_bytes(encoded(m));self.approved=self.path.read_bytes();self.manifest=m
  self.last_out=None;self.history=self.task/'closed-mock-history';self.history.mkdir()
 def preserve_out(self,tag):
  out=Path(self.manifest['evidence_directory'])
  if out.exists():
   target=self.history/tag;assert out.resolve().parent==self.task.resolve()and target.resolve().is_relative_to(self.task.resolve())and not out.resolve().is_relative_to(self.root.resolve())and not target.exists();out.rename(target)
  self.path.write_bytes(self.approved)
 def close(self):self.temporary.cleanup()

class CSPProcess(ChildProcess):
 def execute(self,text):
  w=self.world
  if text.startswith('-- Trusted Identity'):
   stop=text.index('COMMIT;')+len('COMMIT;');chunk=text[:stop];statements=parse_sql(chunk)
   assert self.role=='postgres' and self.active and not w.seeded
   toggles=[];inserted=[];flushed=False
   for raw in statements:
    stmt=raw.stmt
    if isinstance(stmt,pgast.AlterTableStmt):
     table=stmt.relation.schemaname+'.'+stmt.relation.relname;cmd=stmt.cmds[0];assert table in('app.users','app.user_security_profiles')and cmd.name=='owner_commit'
     toggle=cmd.subtype.name;toggles.append((table,toggle))
     if toggle=='AT_DisableTrig':w.disabled.add(table)
     else:assert toggle=='AT_EnableTrig'and flushed;w.disabled.remove(table)
    elif isinstance(stmt,pgast.InsertStmt):
     table=stmt.relation.schemaname+'.'+stmt.relation.relname;assert table in w.disabled;inserted.append(table)
    elif isinstance(stmt,pgast.ConstraintsSetStmt):
     if not stmt.deferred:flushed=True
    elif isinstance(stmt,pgast.TransactionStmt):assert stmt.kind.name=='TRANS_STMT_COMMIT'
    else:raise AssertionError('UNMODELED_IDENTITY_SETUP_AST')
   assert inserted==['app.users','app.user_security_profiles']and len(toggles)==4 and not w.disabled
   w.seeded=True;self.active=False;return super().execute(text[stop:])
  if text.startswith('INSERT INTO platform.runtime_command_receipt '):
   stop=text.index('COMMIT;')+len('COMMIT;');chunk=text[:stop];nodes=parse_sql(chunk);assert self.role=='wa_app_runtime' and w.seeded and not w.created and hasattr(self,'bound')
   assert self.bound['allowed_fields']==w.packet['baseline']['grant']['allowed_fields']and len(w.grants)==1 and not w.disabled
   tables=[n.stmt.relation.schemaname+'.'+n.stmt.relation.relname for n in nodes if isinstance(n.stmt,pgast.InsertStmt)]
   assert tables==['platform.runtime_command_receipt','app.customer_profiles','app.customer_profile_lifecycle_event','platform.owner_mutation_evidence','platform.runtime_outbox_message','platform.runtime_outbox_message']
   assert any(isinstance(n.stmt,pgast.TransactionStmt)and n.stmt.kind.name=='TRANS_STMT_COMMIT'for n in nodes)
   w.creation_ast=[json.loads(parser.parse_sql_json(chunk))];w.created=True;self.active=False;self.output('WA_CUSTOMER_CONTROL_READY_TO_COMMIT');return super().execute(text[stop:])
  if text.startswith('INSERT INTO platform.database_action_grant '):
   line=text.splitlines()[0];parsed=parse_sql(line);stmt=parsed[0].stmt;columns=[x.name for x in stmt.cols];assert columns==list(w.columns)and len(parsed)==2 and parsed[1].stmt.kind.name=='TRANS_STMT_COMMIT'
   values={k:child_constant(v)for k,v in zip(columns,stmt.selectStmt.valuesLists[0])if k!='expires_at'}
   template=w.packet['update_grant']if w.created else w.packet['baseline']['grant'];assert self.role=='wa_context_issuer'and values['issuer_service']==self.role and values['mutation_transaction_id']==self.xid and values['allowed_fields']==template['allowed_fields']
   for key in('database_login_role','owner_module_id','action','purpose','target_kind','target_id','principal_user_id'):assert values[key]==template[key]
   apps=[p for p in w.processes if p.role=='wa_app_runtime'and p.poll()is None];assert len(apps)==1 and str(values['backend_pid'])==apps[0].pid and values['transaction_id']==apps[0].xid
   w.grants.append(values);self.output(json.dumps({'created_at':'2026-11-20T12:00:00+00:00'}));self.active=False;return super().execute('\n'.join(text.splitlines()[1:]))
  return super().execute(text)

class CSPWorld(ChildWorld):
 def __init__(self,packet):super().__init__(packet);self.seeded=False;self.created=False;self.disabled=set();self.creation_ast=[]
 def popen(self,args,**kwargs):return CSPProcess(self,args,**kwargs)
 def state(self):
  counts={'app.users':int(self.seeded),'app.user_security_profiles':int(self.seeded),'app.customer_profiles':int(self.created),'platform.runtime_command_receipt':int(self.created),'app.customer_profile_lifecycle_event':int(self.created),'platform.owner_mutation_evidence':int(self.created),'platform.runtime_outbox_message':2*int(self.created)}
  return [{'table':t,'count':counts.get(t,0),'sha256':sha((t+':'+str(counts.get(t,0))+':'+json.dumps(self.creation_ast,sort_keys=True)).encode())}for t in self.packet['full42_tables']]
 def run(self,args,**kwargs):
  query=kwargs.get('input','')
  if query==self.sql['fresh-namespace.sql']:assert not self.seeded and not self.created;return subprocess.CompletedProcess(args,0,'t','')
  if query==self.sql['baseline-observe.sql']:
   assert self.created and len(self.creation_ast)==1 and self.revision==0;counts={r['table']:r['count']for r in self.state()};return subprocess.CompletedProcess(args,0,json.dumps({'customer':counts['app.customer_profiles'],'command':counts['platform.runtime_command_receipt'],'history':counts['app.customer_profile_lifecycle_event'],'evidence':counts['platform.owner_mutation_evidence'],'outbox':counts['platform.runtime_outbox_message'],'track_enrollments':counts.get('platform.track_enrollment',0),'coherent':True}),'')
  if 'FROM platform.database_action_grant g WHERE id='in query:
   assert args[args.index('-U')+1]=='wa_context_issuer' and len(self.grants)>0 and all(g['id']in query and g['token_hash']in query for g in self.grants)
  return super().run(args,**kwargs)

class CSPModel(PrimitiveCommandModel):
 def __init__(self,fixture,path,mode='normal'):
  self.fixture=fixture;self.path=path;self.manifest=json.loads(path.read_bytes());self.n=None;self.calls=[];self.containers={};self.volumes={};self.running=False;self.finalized=False;self.deploys=0;self.fail_stage=None;self.bad_global=None;self.after_started=False;self.outer_after_component=False;self.mutate_cleanup_reference=False;self.cleanup_reference_mutated=False;self.mode=mode;self.byte_processes=[]
  packet=json.loads((fixture.root/'review-output/customer-stale-predecessor-v1/fixtures.json').read_bytes());self.vm=CSPWorld(packet);self.vm.sql={n:(fixture.root/'review-output/customer-stale-predecessor-v1'/n).read_text()for n in packet['prepared_files_sha256']};self.vm.columns=tuple(ctx_protocol['GRANT_COLUMNS']);self.vm.collector=(fixture.root/'scripts/sql-review/collect_native_catalog.sql').read_text()
  self.catalog={n:json.loads((fixture.root/ARCHIVE/'OFFLINE-model-inputs'/(n+'.json')).read_bytes())for n in MODEL_CATALOG_PINS};self.vm.native=self.catalog['native-before']
  self.image=IMAGE;self.md=IMAGE.split('@')[1];self.cd=CONFIG;self.name=self.manifest['targets'][0]['name'];self.volume=self.manifest['targets'][0]['volume'];self.labels={'workinants.rehearsal':'p0c-local-f0','workinants.rehearsal.run':self.manifest['run_id']};self.target=json.loads(Path(self.manifest['migration_targets']['ok']['manifest_path']).read_bytes())
  if mode=='wrong-message':self.vm.error_override='ERROR:  P0001: '+CANARY+'\nCONTEXT:  PL/pgSQL function platform_private.guard_customerprofile() line 9 at RAISE\nLOCATION:  exec_stmt_raise, pl_exec.c:3911\n'
 def native(self):
  value=deepcopy(self.catalog['native-before'])
  for row in value['triggers']:
   if row['table_name']in self.vm.disabled and row['name']=='owner_commit':row['enabled']='D'
  return value
 def popen(self,args,**kwargs):
  if kwargs.get('text')is True:return self.vm.popen(args,**kwargs)
  def dispatch(a,b):
   if a[0]=='git':return mock_git(self.fixture.root,a,b or None,text=False)
   return self.process(a,input=b.decode('utf8')if b else None,text=True)
  p=ByteProcess(args,dispatch);self.byte_processes.append(p);return p
 def sql(self,args,text,options):
  stage=self.n['report']['stage'];active=sum(p.poll()is None for p in self.vm.processes)
  if "'migrator'"in text and "'other_client_backends'"in text:return self.response({'migrator':0,'other_client_backends':active if self.bad_global is None else self.bad_global})
  if text==self.n['_required_safety_text']('ORIGINAL_GRANTOR_FINALIZATION'):self.finalized=True;return self.response()
  if "'remaining_memberships'"in text:return self.response({'grantor':'postgres','auth':'scram-sha-256:postgres','remaining_memberships':0 if self.finalized else 3,'leaf_create':dict.fromkeys(self.n['LEAVES'],not self.finalized),'active_install_connections':active})
  if stage=='BOOTSTRAP_SETTINGS':return self.response({'login':'postgres','auth':'scram-sha-256:postgres','safe':True,'diagnostics_safe':True,'superuser':True})
  if stage=='FRESH_PRE_BOOTSTRAP_PUBLIC_BASELINE':return self.response({'public_owner':'pg_database_owner','public_acl':[{'role':'pg_database_owner','privilege':p,'grantor':'pg_database_owner','grant_option':False}for p in('CREATE','USAGE')]+[{'role':'PUBLIC','privilege':'USAGE','grantor':'pg_database_owner','grant_option':False}],'application_roles':0,'event_triggers':0})
  if stage in('BOOTSTRAP','CREDENTIAL_PROVISION'):return self.response()
  if stage=='EMPTY_APPLICATION_BASELINE':return self.response({'public_owner':'pg_database_owner','public_acl':None,'event_triggers':0,'public_relations':0,'application_relations':0})
  if 'pg_hba_file_rules'in text:return self.response([{'rule_number':i+1,'type':'host','database':['all'],'user_name':['all'],'address':a,'netmask':mask,'auth_method':'scram-sha-256','error':None}for i,(a,mask)in enumerate([('127.0.0.1','255.255.255.255'),('::1','ffff:ffff:ffff:ffff:ffff:ffff:ffff:ffff')])])
  if 'FROM pg_authid'in text:return self.response(dict.fromkeys(('postgres','wa_migrator','wa_context_issuer','wa_identity_service_authority','wa_app_runtime','wa_worker'),True))
  role=args[args.index('-U')+1]
  if 'PGPASSWORD'in args:return self.response('',2,'FATAL:  password authentication failed for user "'+role+'"\n')
  if "'auth',system_user"in text:return self.response({'login':role,'auth':'scram-sha-256:'+role,'database':'wa_p0c_rehearsal','client':'127.0.0.1','server':'127.0.0.1'})
  if 'workinants.native-catalog.v1'in text:assert self.deploys==1 and self.finalized;return self.response(self.native())
  if 'workinants.expression-oracle-preflight.v1'in text:self.after_started=self.after_started or stage.startswith('SCOPED_POST_');return self.response('\n'.join(json.dumps(self.catalog[k])for k in('oracle-preflight','oracle-results','oracle-closure')))
  if 'workinants.prisma-ledger-native.v1'in text:return self.response(self.catalog['ledger-observation'])
  if 'workinants.catalog-acl-preflight.v1'in text:return self.response(self.catalog['acl-preflight'])
  if 'workinants.catalog-text-preflight.v1'in text:return self.response(self.catalog['text-preflight'])
  return self.vm.run(args,input=text)
 def process(self,args,**options):
  if args[0]=='git':
   reply=mock_git(self.fixture.root,args,options.get('input').encode()if type(options.get('input'))is str else options.get('input'),text=bool(options.get('text')))
   return reply
  if self.mode=='late-reference'and list(args)[3:5]==['volume','ls']and self.deploys==1 and not self.containers and not self.volumes and not self.cleanup_reference_mutated:
   path=Path(self.manifest['evidence_directory'])/'customer-stale-component/customer-stale-predecessor-results.json'
   if path.exists():raw=path.read_bytes();changed=raw.replace(b'PASS_THREE_STALE_PREDECESSOR_ROLLBACK_CONTROLS_ONLY',b'FAIL_THREE_STALE_PREDECESSOR_ROLLBACK_CONTROLS_ONLY');assert raw!=changed;path.write_bytes(changed);self.cleanup_reference_mutated=True
  return super().process(args,**options)

class WholeLifecycle(unittest.TestCase):
 @classmethod
 def setUpClass(cls):cls.guard=ExitStack();[cls.guard.enter_context(patch.object(subprocess,n,side_effect=AssertionError('REAL_PROCESS_FORBIDDEN')))for n in('run','Popen','call','check_call','check_output')];cls.fixture=Fixture()
 @classmethod
 def tearDownClass(cls):cls.fixture.close();cls.guard.close()
 def run_case(self,mode='normal',io_fault=False):
  self.fixture.preserve_out(mode+('-IO'if io_fault else''));module=runpy.run_path(str(self.fixture.task/FIVE[0]));g=module['launch'].__globals__;model=CSPModel(self.fixture,self.fixture.path,mode);model.n=g;original=Path.open;faults=[]
  def opened(path,*args,**kwargs):
   if io_fault and model.vm.update_calls>0 and path==Path(model.manifest['evidence_directory'])/'run-evidence.json.tmp':faults.append(True);raise OSError(CANARY)
   return original(path,*args,**kwargs)
  output=io.StringIO();events=[]
  def traced(frame,event,arg):
   if event=='exception'and Path(frame.f_code.co_filename).name in FIVE:events.append((Path(frame.f_code.co_filename).name,frame.f_lineno,arg[0].__name__))
   return traced
  with patch.object(subprocess,'Popen',side_effect=model.popen),patch.object(subprocess,'run',side_effect=model.process),patch.object(Path,'open',opened),redirect_stdout(output):
   previous=sys.gettrace();sys.settrace(traced)
   try:code=module['launch'](['--execute-reviewed-customer-stale-predecessor','--manifest',str(self.fixture.path)])
   finally:sys.settrace(previous)
  model.safe_exception_frames=events[-12:]
  self.assertTrue(all(p.poll()is not None for p in model.vm.processes));self.assertTrue(all(p.poll()is not None for p in model.byte_processes));self.assertNotIn(CANARY,output.getvalue());self.assertNotIn(CANARY,json.dumps(g['report']));return code,g,model,faults
 def test_actual_full_constructor_install_native_child_three_and_cleanup(self):
  code,g,m,_=self.run_case();self.assertEqual(code,0,(g['report'].get('primary_failure'),getattr(m,'last_mock_fault',None),m.safe_exception_frames,[(type(p.error).__name__,str(p.error))for p in m.byte_processes if p.error]));self.assertEqual(m.deploys,1);self.assertEqual(g['report']['catalog_comparison']['check_counts'],{'PASS':29089});self.assertEqual(len(g['report']['ledger_comparison']['checks']),22)
  raw=json.loads((g['OUT']/g['COMPONENT_ARTIFACT']).read_bytes());self.assertEqual(len(raw['results']),3);self.assertEqual(len(m.vm.grants),4);self.assertTrue(m.vm.seeded and m.vm.created);self.assertEqual(len(m.vm.creation_ast),1);self.assertFalse(m.vm.disabled);self.assertFalse(m.containers or m.volumes);self.assertTrue(g['report']['cleanup_actions_confirmed']);self.assertEqual(g['report']['customer_stale']['post_proof']['native_checks'],29089)
 def test_wrong_guard_partial_prefix_stops_later_cases(self):
  code,g,m,_=self.run_case('wrong-message');self.assertEqual(code,1);self.assertEqual(m.vm.update_calls,2);raw=json.loads((g['OUT']/g['COMPONENT_ARTIFACT']).read_bytes());self.assertEqual([r['name']for r in raw['results']],['wrong-predecessor']);self.assertEqual(raw['status'],'STOPPED');self.assertFalse(m.containers or m.volumes);self.assertTrue(g['report']['cleanup_actions_confirmed']);self.assertNotIn('post_proof',g['report']['customer_stale'])
 def test_persistent_parent_writer_failure_still_closes_and_cleans(self):
  code,g,m,faults=self.run_case('normal',True);self.assertEqual(code,1);self.assertTrue(faults);self.assertFalse(g['report']['evidence_complete']);self.assertTrue(g['report']['cleanup_actions_confirmed']);self.assertFalse(m.containers or m.volumes)
 def test_late_closed_reference_drift_rejects_after_cleanup(self):
  code,g,m,_=self.run_case('late-reference');self.assertEqual(code,1);self.assertTrue(m.cleanup_reference_mutated);self.assertTrue(g['report']['cleanup_actions_confirmed']);self.assertFalse(m.containers or m.volumes)

class PendingAndProjection(unittest.TestCase):
 def test_actual_pending_entry_before_steps_or_processes(self):
  manifest=TASK/'local-f0-customer-stale-predecessor-v1-plan-73292a8f/operation-manifest.json';self.assertTrue(manifest.exists());core=runpy.run_path(str(TASK/FIVE[0]));calls=[];actual=compile
  def compile_(source,filename,*a,**kw):
   if str(filename).endswith(FIVE[1]):calls.append(True)
   return actual(source,filename,*a,**kw)
  with patch.object(subprocess,'Popen',side_effect=AssertionError('PENDING_PROCESS_FORBIDDEN')),patch.object(subprocess,'run',side_effect=AssertionError('PENDING_PROCESS_FORBIDDEN')),patch('builtins.compile',compile_),redirect_stdout(io.StringIO()):self.assertEqual(core['launch'](['--execute-reviewed-customer-stale-predecessor','--manifest',str(manifest)]),1)
  self.assertEqual(calls,[]);self.assertFalse(Path(json.loads(manifest.read_bytes())['evidence_directory']).exists())

if __name__=='__main__':unittest.main()
