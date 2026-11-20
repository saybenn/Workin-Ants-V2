"""Actual owned SixRead CLI + source/native/child/post-proof composition offline.

All process/DB/network boundaries are modeled. Historical sanitized native,
oracle and ledger data are explicitly offline inputs; no runtime qualification.
No coordinator, factory, Session, source verifier or comparator is replaced.
"""
from contextlib import redirect_stdout
from copy import deepcopy
import ast
import hashlib
import io
import json
from pathlib import Path
import runpy
import subprocess
import sys
import tempfile
import time
import types
import unittest
import uuid
from unittest.mock import patch

TASK=Path(__file__).resolve().parent;ROOT=TASK/'workinants-correction-pass'
ADMISSION=runpy.run_path(str(TASK/'check_sixread_owned_resource_v1_preparer_pinner_20261119.py'))
CHILD=runpy.run_path(str(TASK/'check_six_read_owned_resource_v1_child_composed_20261119.py'))
CAPTURE=TASK/'sixread-owned-full-composition-capture2-20261119.json'
CAPTURE_SHA='1af04b3ba5857fba8036d0078517a0eec957e1e101889ac7a7398cd0dba9aa9c'
CORE='execute_local_f0_scoped_reads_owned_resource_v1_20261119.py'
STEPS='local_f0_scoped_reads_owned_resource_v1_operation_steps.py'
OBSERVATIONS=[]

def sha(raw):return hashlib.sha256(raw).hexdigest()
LOADED_HARNESS_SHA=sha(Path(__file__).read_bytes())
def encoded(v):return (json.dumps(v,indent=2,allow_nan=False)+'\n').encode()
def capture_fixture():
 raw=CAPTURE.read_bytes();assert sha(raw)==CAPTURE_SHA;d=json.loads(raw)
 for key in ('TASK','ROOT','baseline'):d[key]=Path(d[key])
 assert d['TASK'].is_relative_to(TASK) and d['TASK']!=TASK
 for name,wanted in d['external'].items():assert sha((d['TASK']/name).read_bytes())==wanted
 d['prepare']=runpy.run_path(str(d['TASK']/ADMISSION['PREP']));d['pin']=runpy.run_path(str(d['TASK']/ADMISSION['PIN']))
 return d

def historical_asset(name):
 record_path=ROOT/'context/reconciliation/local-f0-owner-da5ad66-72934689-execution.json'
 record=json.loads(record_path.read_bytes())
 relative='context/reconciliation/local-f0-run-assets/da5ad66-owner-72934689/evidence/'+name
 wanted=record['assets_sha256'][relative];raw=(ROOT/relative).read_bytes();assert sha(raw)==wanted
 return json.loads(raw)

class FullGitWorld(ADMISSION['GitWorld']):
 def run(self,args,**options):
  if args[:4]==['git','--no-optional-locks','-c','core.longpaths=true']:return super().run(args,**options)
  assert args[:3]==['git','-c','core.longpaths=true'];command=tuple(args[3:]);self.calls.append(command)
  if command==('rev-parse','HEAD'):raw=('b'*40+'\n').encode()
  elif command==('rev-parse','HEAD^{tree}'):raw=('c'*40+'\n').encode()
  elif len(command)==2 and command[0]=='show':
   commit,name=command[1].split(':',1);assert commit=='b'*40;raw=(self.root/name).read_bytes()
  else:raise AssertionError('UNREGISTERED_CORE_READ_ONLY_GIT')
  return types.SimpleNamespace(returncode=0,stdout=raw.decode() if options.get('text') else raw,stderr='' if options.get('text') else b'')

class WholeWorld(CHILD['World']):
 def __init__(self,fixture,manifest):
  self.fixture=fixture;self.master=json.loads(Path(manifest).read_bytes());nested=json.loads(Path(self.master['migration_targets']['ok']['manifest_path']).read_bytes())
  plan={'target_manifest':nested,'immutable_container_id':CHILD['CID'],'run_id':self.master['run_id']}
  super().__init__(plan,historical_asset('native-before.json'),CHILD['fixture_packet']())
  self.git=FullGitWorld(fixture['ROOT']);self.exists_container=False;self.exists_volume=False;self.installed=False;self.bootstrap=False;self.finalizer=False;self.prisma_calls=[];self.native_calls=0;self.oracle_calls=0;self.ledger_calls=0;self.kernel_calls=0;self.copied_tools=False;self.copied_source=False;self.after_child_sql=[]
  self.ledger=historical_asset('ledger-observation.json')
  self.oracle=[historical_asset(name) for name in ('oracle-preflight.json','oracle-results.json','oracle-closure.json')]
  self.acl_preflight=historical_asset('acl-preflight.json');self.text_preflight=historical_asset('text-preflight.json')
  raw=(fixture['ROOT']/'scripts/sql-review/fixtures/postgres-17.11-approved-manifest.json').read_bytes();assert sha(raw)=='996e9dc583ba9f0265a2c75547a9c95fb22c251e394749cab205a0a00e1856a1';self.raw_manifest=raw
  self.image={'Id':'sha256:'+sha(raw),'Os':'linux','Architecture':'amd64','RepoDigests':['postgres@sha256:'+sha(raw)],
   'Descriptor':{'mediaType':'application/vnd.oci.image.manifest.v1+json','digest':'sha256:'+sha(raw),'size':len(raw)},'Config':{'Env':['PG_VERSION=17.11-1.pgdg13+2']}}
  self.container['Image']=self.image['Id'];self.container['HostConfig']['Links']=[];self.container['State']['Running']=False
  self.volume['CreatedAt']='2026-11-19T12:00:00Z'
  source=ast.parse((fixture['TASK']/STEPS).read_bytes());constants={node.targets[0].id:ast.literal_eval(node.value) for node in source.body if isinstance(node,ast.Assign) and len(node.targets)==1 and isinstance(node.targets[0],ast.Name) and node.targets[0].id in ('OWNER_SECRET_TMPFS_SCRIPT','OWNER_SECRET_TMPFS_TOKEN')}
  self.tmpfs_script=constants['OWNER_SECRET_TMPFS_SCRIPT'];self.tmpfs_token=constants['OWNER_SECRET_TMPFS_TOKEN']
  self.fixed_sql={name:(fixture['ROOT']/name).read_text(encoding='utf8') for name in ('review-output/foundation-bootstrap.review.sql','review-output/foundation-bootstrap-finalize.review.sql','scripts/sql-review/catalog-acl-preflight.sql','scripts/sql-review/catalog-text-preflight.sql','scripts/sql-review/collect_prisma_ledger.sql','review-output/native-catalog/expression-oracle.sql')}
 def run(self,args,**options):
  args=list(args)
  if args and args[0]=='git':return self.git.run(args,**options)
  if args and args[0]=='powershell.exe':return self.result('OWNER_ONLY_VERIFIED\n')
  assert args[:3]==['docker','--context','desktop-linux'],'DOCKER_CONTEXT_REQUIRED'
  command=args[3:]
  if 'psql' in command:return self.psql_run(args,options)
  if command[:2]==['context','inspect']:return self.result([self.context])
  if command[:2]==['version','--format']:return self.result({'Os':'linux','Arch':'amd64','Version':'29.6.2'})
  if command[:2]==['container','ls']:return self.result(self.container['Name'][1:]+'\n' if self.exists_container else '')
  if command[:2]==['volume','ls']:return self.result(self.volume['Name']+'\n' if self.exists_volume else '')
  if command[:2]==['image','inspect']:return self.result([self.image])
  if command[:4]==['buildx','imagetools','inspect','--raw']:return self.result(self.raw_manifest.decode())
  if command[:2]==['volume','create']:
   labels=self.plan['target_manifest']['target']['labels'];assert command==['volume','create','--label','workinants.rehearsal='+labels['workinants.rehearsal'],'--label','workinants.rehearsal.run='+labels['workinants.rehearsal.run'],self.volume['Name']] and not self.exists_volume;self.exists_volume=True;return self.result(self.volume['Name']+'\n')
  if command[:2]==['container','create']:
   target=self.plan['target_manifest']['target'];assert command[command.index('--name')+1]==target['container_name'] and not self.exists_container
   assert command[command.index('--network')+1]=='none' and command[command.index('--platform')+1]=='linux/amd64'
   assert not set(command)&{'--privileged','-p','--publish','--publish-all','--device','--cap-add','--pid','--ipc','--link','-v','--volume'}
   labels=[command[i+1] for i,x in enumerate(command) if x=='--label'];assert labels==['workinants.rehearsal=p0c-local-f0','workinants.rehearsal.run='+self.master['run_id']]
   mounts=[command[i+1] for i,x in enumerate(command) if x=='--mount'];assert mounts==['type=volume,src='+target['volume_name']+',dst=/var/lib/postgresql/data','type=bind,src='+target['bootstrap_secret_host_path']+',dst=/run/bootstrap-password,readonly']
   assert command.count('--tmpfs')==1 and command[command.index('--tmpfs')+1]=='/run/wa-secrets:rw,nosuid,noexec,nodev,mode=0700'
   self.exists_container=True;return self.result(self.container['Id']+'\n')
  if command[:2]==['container','start']:
   assert command[2]==self.container['Id'] and self.exists_container;self.container['State']['Running']=True;return self.result(command[2]+'\n')
  if command[:2]==['container','inspect'] or command[0]=='inspect':
   assert command[-1] in (self.container['Name'][1:],self.container['Id']);return self.result([self.container]) if self.exists_container else self.result('',1,'EXACT_MOCK_ABSENT')
  if command[:2]==['volume','inspect']:
   assert command[-1]==self.volume['Name'];return self.result([self.volume]) if self.exists_volume else self.result('',1,'EXACT_MOCK_ABSENT')
  if command[:2]==['container','rm']:
   assert command==['container','rm','-f',self.container['Id']] and self.exists_container;self.exists_container=False;return self.result(command[-1]+'\n')
  if command[:2]==['volume','rm']:
   assert command==['volume','rm',self.volume['Name']] and self.exists_volume;self.exists_volume=False;return self.result(command[-1]+'\n')
  if command[0]=='cp':
   assert command[-1].startswith(self.container['Id']+':/run/wa-f0-')
   if command[-1].endswith('tools.tar.gz'):assert command[1]==self.master['tool_archive'];self.copied_tools=True
   elif command[-1].endswith('source.tar.gz'):assert command[1]==self.master['migration_targets']['ok']['source_archive'];self.copied_source=True
   else:raise AssertionError('UNREGISTERED_COPY')
   return self.result('')
  if command[0]=='exec':return self.exec_run(command,options)
  raise AssertionError('UNREGISTERED_DOCKER_PROCESS_BOUNDARY')
 def exec_run(self,args,options):
  assert self.container['Id'] in args and self.exists_container
  tail=args[args.index(self.container['Id'])+1:]
  if tail==['pg_isready','-h','127.0.0.1','-p','5432','-U','postgres','-d','wa_p0c_rehearsal']:return self.result('ready\n')
  if tail==['sh','-ceu',self.tmpfs_script]:self.kernel_calls+=1;return self.result(self.tmpfs_token+'\n')
  if tail[:2]==['sh','-ceu'] and 'stat -c' in tail[2]:return self.result('600:0:0\n')
  if tail and tail[0] in ('mkdir','tar','rm'):return self.result('')
  if tail[:2]==['/usr/bin/sha256sum','--']:
   assert self.copied_tools and self.copied_source;values=[];nested=self.plan['target_manifest']
   for name in tail[2:]:
    if name.startswith('/run/wa-f0-tools/'):wanted=nested['tools']['files_sha256'][name.removeprefix('/run/wa-f0-tools/')]
    elif name.startswith('/run/wa-f0-source/'):wanted=nested['source']['runtime_files_sha256'][name.removeprefix('/run/wa-f0-source/')]
    else:raise AssertionError('UNREGISTERED_COPIED_SOURCE_HASH')
    values.append(wanted+'  '+name+'\n')
   return self.result(''.join(values))
  if tail==['/run/wa-f0-tools/node/bin/node','--version']:return self.result('v24.22.1\n')
  if tail==['/run/wa-f0-tools/schema-engine','--version']:return self.result('schema-engine d1b3f377ca835d73fd50954a5e22128b9ebdd6b8\n')
  if tail[:2]==['/run/wa-f0-tools/node/bin/node','/run/wa-f0-source/scripts/sql-review/local-f0-migrate-runner.mjs']:
   assert tail[2:]==['--execute-reviewed-local-f0','--operation','deploy'];assert not self.installed and self.bootstrap
   self.prisma_calls.append('deploy');self.installed=True;raw=options['input'];attestation=json.loads(raw);manifest=attestation['planned']
   flags={k:k in ('text_valid','headers_valid') for k in ('text_valid','sgr_stripped','headers_valid','prisma_header_present','prisma_header_unique','database_header_present','database_header_unique')}
   return self.result({'schema':'workinants.local-f0-migrate-result.v2','operation':'deploy','status':'CLI_COMPLETED_REQUIRES_INDEPENDENT_LEDGER_CATALOG_CHECKS','exit_code':0,'prisma_codes':[],'sqlstates':[],'no_pending_message_observed':True,'raw_output_discarded':True,'database_qualification_claimed':False,'run_id':manifest['run_id'],'container_id':self.container['Id'],'source_sql_sha256':manifest['source']['integrated_sql_sha256'],'attestation_sha256':sha(raw.encode()),'diagnostic_format':flags})
  raise AssertionError('UNREGISTERED_EXEC_BOUNDARY')
 def psql_run(self,args,options):
  text=options.get('input','');role=self.role(args)
  if self.child_completed_at_transport():self.after_child_sql.append('GLOBAL_BACKENDS'if"'other_client_backends'"in text else'OTHER_SQL')
  if text==self.fixed_sql['review-output/foundation-bootstrap.review.sql']:self.bootstrap=True;return self.result('')
  if text==self.fixed_sql['review-output/foundation-bootstrap-finalize.review.sql']:assert self.installed;self.finalizer=True;return self.result('')
  if text.startswith('ALTER DATABASE '):assert self.bootstrap;return self.result('')
  if "'diagnostics_safe'" in text and "'superuser'" in text:return self.result({'login':'postgres','auth':'scram-sha-256:postgres','safe':True,'diagnostics_safe':True,'superuser':True})
  if "'application_roles'" in text:
   return self.result({'public_owner':'pg_database_owner','public_acl':[{'role':r,'grantor':'pg_database_owner','privilege':p,'grant_option':False} for r,p in [('pg_database_owner','CREATE'),('pg_database_owner','USAGE'),('PUBLIC','USAGE')]],'application_roles':0,'event_triggers':0})
  if "'application_relations'" in text:return self.result({'public_owner':'pg_database_owner','public_acl':None,'event_triggers':0,'public_relations':0,'application_relations':0})
  if "'other_client_backends'" in text:return self.result({'migrator':0,'other_client_backends':sum(p.poll() is None for p in self.processes)})
  if "'remaining_memberships'" in text:return self.result({'grantor':'postgres','auth':'scram-sha-256:postgres','remaining_memberships':0 if self.finalizer else 3,'leaf_create':{r:not self.finalizer for r in ('wa_private_helper_owner','wa_customer_verifier','wa_track_verifier')},'active_install_connections':0})
  if text==self.fixed_sql['scripts/sql-review/catalog-acl-preflight.sql']:return self.result(self.acl_preflight)
  if text==self.fixed_sql['scripts/sql-review/catalog-text-preflight.sql']:return self.result(self.text_preflight)
  if text==self.fixed_sql['review-output/native-catalog/expression-oracle.sql']:
   assert self.installed and self.finalizer;self.oracle_calls+=1;return self.result('\n'.join(CHILD['canonical'](v) for v in self.oracle)+'\n')
  if text==self.fixed_sql['scripts/sql-review/collect_prisma_ledger.sql']:
   assert self.installed and self.finalizer;self.ledger_calls+=1;return self.result(self.ledger)
  if 'workinants.native-catalog.v1' in text:assert self.installed and self.finalizer;self.native_calls+=1
  return super().run(args,**options)
 def child_completed_at_transport(self):return self.native_calls>=7 and self.read_ordinal==65 and len(self.grants)==71 and all(p.poll() is not None for p in self.processes)
 def retention(self,text):
  value=super().retention(text)
  # Deliberate SQL-response projection: older retained prefix may have expired,
  # while each freshly checked single current grant remains unexpired. This
  # tests the unchanged child distinction, not a clock/DB qualification.
  if value['count']>1:value['unexpired']=False
  return value

def prepare_and_pin(fixture,run=None):
 run=run or str(uuid.uuid4())
 ADMISSION['approve_clone'](fixture);manifest,out=ADMISSION['prepare_fixture'](fixture,run);git=FullGitWorld(fixture['ROOT'])
 with patch.object(subprocess,'run',side_effect=git.run):pinned=fixture['pin']['pin'](manifest)
 value=json.loads(manifest.read_bytes());value['review_status']='APPROVED_LOCAL_F0_SCOPED_READ_COMPANION_OWNED_RESOURCE_V1_ATTEMPT';manifest.write_bytes(encoded(value))
 return manifest,pinned

def run_full(fixture,manifest,write_fault=None):
 world=WholeWorld(fixture,manifest);core=runpy.run_path(str(fixture['TASK']/CORE));output=io.StringIO();started=time.monotonic()
 outer=Path(json.loads(manifest.read_bytes())['evidence_directory']);original_replace=Path.replace;failures=[];phase_calls=[];namespace=core['launch'].__globals__
 def replace(path,target):
  details=namespace.get('report',{}).get('scoped_read',{});reference=details.get('component_report_reference',{})
  late=details.get('component_closure_confirmed')is True and reference.get('read_status')=='CLOSED_BOUNDED_BYTES'
  if path==outer/'run-evidence.json.tmp'and world.child_completed_at_transport()and(write_fault=='persistent'or write_fault=='transient'and late and not failures):
   failures.append({'phase':'AFTER_CONFIRMED_PARENT_CLOSURE_BEFORE_REFERENCE_PERSIST'if late else'DURING_REQUIRED_PARENT_CLOSURE_RECORD','closed_processes':all(p.poll()is not None for p in world.processes)});raise PermissionError('OFFLINE_TEST_PARENT_WRITER_FAILURE')
  return original_replace(path,target)
 def profile(frame,event,arg):
  if event=='call'and frame.f_code.co_name in ('validate_scoped_component','readonly_post_proof')and Path(frame.f_code.co_filename)==fixture['TASK']/STEPS:phase_calls.append(frame.f_code.co_name)
 old_profile=sys.getprofile();sys.setprofile(profile)
 try:
  with world.boundaries(),redirect_stdout(output),patch.object(Path,'replace',replace):code=core['launch'](['--manifest',str(manifest),'--execute-reviewed-scoped-reads'])
 finally:sys.setprofile(old_profile)
 value=deepcopy(core['launch'].__globals__['report'])
 return {'exit_code':code,'report':value,'world':world,'duration_seconds':time.monotonic()-started,'stdout':output.getvalue(),'writer_failures':failures,'phase_calls':phase_calls,'manifest':manifest,'report_path':outer/'run-evidence.json'}

def record_outcome(out,kind):
 report=out['report'];world=out['world'];OBSERVATIONS.append({'kind':kind,'source_only_mock':True,'runtime_qualification_claimed':False,'exit_code':out['exit_code'],'status':report['status'],'main_seconds':out['duration_seconds'],'run_id':report['run_id'],'manifest_sha256':sha(Path(out['manifest']).read_bytes()),'safe_disk_report_path':str(out['report_path']),'safe_disk_report_sha256':sha(out['report_path'].read_bytes()),'RAM_report_sha256':sha(encoded(report)),'prisma_calls':world.prisma_calls,'native_process_boundaries':world.native_calls,'oracle_process_boundaries':world.oracle_calls,'ledger_process_boundaries':world.ledger_calls,'grants':len(world.grants),'operation_processes':len(world.processes),'writer_failures':len(out['writer_failures']),'writer_fault_phases':sorted({x['phase']for x in out['writer_failures']}),'actual_verdict_and_post_method_calls':out.get('phase_calls'),'after_child_sql':world.after_child_sql,'component_closure_confirmed':report.get('scoped_read',{}).get('component_closure_confirmed'),'cleanup_actions_confirmed':report.get('cleanup_actions_confirmed'),'evidence_complete':report['evidence_complete'],'source5_sha256':world.fixture['external'],'prefix_aggregate_unexpired_false_projection':True})

class FullCompositionTests(unittest.TestCase):
 def test_00_independent_owned_review_pending_rejects_before_git(self):
  fixture=capture_fixture();path=fixture['ROOT']/fixture['prepare']['OWNED_VALIDATION'];original=path.read_bytes();record=json.loads(original)
  record['independent_safety_sql_review']['decision']='SOURCE_APPROVED';record['independent_owned_resource_review']['decision']='PENDING';path.write_bytes(encoded(record))
  try:
   manifest,out=ADMISSION['prepare_fixture'](fixture,str(uuid.uuid4()))
   with patch.object(subprocess,'run')as git,self.assertRaises(fixture['pin']['Held'])as failure:fixture['pin']['pin'](manifest)
   self.assertEqual(str(failure.exception),'OWNED_RESOURCE_REVIEW_REQUIRED');git.assert_not_called()
  finally:path.write_bytes(original)
 def test_actual_owned_CLI_source_install_native_child_post_and_cleanup(self):
  fixture=capture_fixture();manifest,pinned=prepare_and_pin(fixture);out=run_full(fixture,manifest);report=out['report'];world=out['world']
  self.assertEqual(out['exit_code'],0,report.get('primary_failure'));self.assertEqual(report['status'],'PASS_LOCAL_SCOPED_READ_SQL_SUBSET_ONLY')
  self.assertEqual(world.prisma_calls,['deploy']);self.assertEqual(world.oracle_calls,2);self.assertEqual(world.ledger_calls,2)
  self.assertEqual(len(world.grants),71);world.assert_closed();self.assertFalse(world.exists_container);self.assertFalse(world.exists_volume)
  self.assertTrue(report['cleanup_actions_confirmed']);self.assertTrue(report['evidence_complete']);self.assertEqual(report['unexpected'],[])
  self.assertEqual(report['catalog_comparison']['check_counts'],{'PASS':29089});self.assertEqual(len(report['ledger_comparison']['checks']),22)
  post=report['scoped_read']['post_proof'];self.assertEqual(post['status'],'PASS_READ_ONLY_SOURCE_BOUND_SUBSET');self.assertFalse(post['second_deploy']);self.assertEqual(post['before_state_sha256'],post['after_state_sha256']);self.assertEqual(post['before_state_sha256'],post['child_final_state_sha256'])
  for flag in ('packet_unchanged_after_run','tool_source_data_unchanged_after_run','external_sources_unchanged_after_run','external_inputs_unchanged_after_run'):self.assertTrue(report[flag])
  record_outcome(out,'LATEST_WHOLE_CLI_HAPPY_PREFIX_EXPIRY_ALLOWED')
 def test_parent_writer_persistent_failure_after_real_child_still_closes_and_cleans(self):self.writer_fault('persistent')
 def test_parent_writer_transient_failure_after_real_child_is_sticky_and_cleans(self):self.writer_fault('transient')
 def writer_fault(self,kind):
  fixture=capture_fixture();manifest,pinned=prepare_and_pin(fixture);out=run_full(fixture,manifest,kind);report=out['report'];world=out['world']
  self.assertEqual(out['exit_code'],1);self.assertEqual(report['status'],'STOPPED_ATTEMPT_PRESERVED');self.assertFalse(report['evidence_complete']);self.assertTrue(report['persistence_failure'])
  self.assertGreater(len(out['writer_failures']),0);self.assertTrue(all(x['closed_processes']for x in out['writer_failures']))
  self.assertEqual(world.prisma_calls,['deploy']);self.assertEqual(world.oracle_calls,1);self.assertEqual(world.ledger_calls,1);self.assertEqual(world.native_calls,7)
  self.assertEqual(len(world.grants),71);world.assert_closed();self.assertTrue(world.after_child_sql);self.assertTrue(all(x=='GLOBAL_BACKENDS'for x in world.after_child_sql))
  self.assertNotIn('post_proof',report['scoped_read']);self.assertFalse((Path(json.loads(manifest.read_bytes())['evidence_directory'])/'scoped-read-component-result.json').exists())
  self.assertTrue(report['scoped_read']['component_closure_attempted']);self.assertIs(report['scoped_read']['component_closure_confirmed'],kind=='transient')
  closure=[row for row in report['backend_closures']if row['stage']=='SCOPED_READ_COMPONENT_FINALLY_GLOBAL_CLOSURE'];self.assertEqual(len(closure),1);self.assertTrue(closure[0]['all_other_client_backends_absent']);self.assertTrue(closure[0]['counts_valid'])
  self.assertEqual(out['phase_calls'],[])
  self.assertTrue(report['cleanup_actions_confirmed']);self.assertFalse(world.exists_container);self.assertFalse(world.exists_volume);self.assertTrue(report['host_secret_cleanup']['private_directory_absent'])
  record_outcome(out,'LATEST_WHOLE_CLI_AFTER_CHILD_'+kind.upper()+'_PARENT_SAVE_FAILURE')
 def test_single_current_expired_grant_stops_real_child_before_query(self):
  class Expired(CHILD['World']):
   def retention(self,text):value=super().retention(text);value['unexpired']=False;return value
  with tempfile.TemporaryDirectory(prefix='sixread-owned-expiry-child-',dir=TASK)as temp:
   plan,native,packet=CHILD['standalone_plan'](temp);world=Expired(plan,native,packet);result=world.run_child(Path(temp)/'component')
   self.assertEqual(result['status'],'STOPPED_PARTIAL_EVIDENCE_PRESERVED');self.assertEqual(result['results'],[]);self.assertEqual(len(world.grants),1);self.assertEqual(world.read_ordinal,0);world.assert_closed()

if __name__=='__main__':
 sys.addaudithook(ADMISSION['audit']);started=time.monotonic();suite=unittest.main(exit=False)
 record={'schema':'workinants.sixread-owned-full-composed-author-checks.v2','source_only_mock':True,'runtime_qualification_claimed':False,'actual_test_methods':suite.result.testsRun,'failures':len(suite.result.failures),'errors':len(suite.result.errors),'duration_seconds':time.monotonic()-started,'capture_sha256':CAPTURE_SHA,'harness_sha256':LOADED_HARNESS_SHA,'harness_unchanged_during_run':sha(Path(__file__).read_bytes())==LOADED_HARNESS_SHA,'observations':OBSERVATIONS,'limits':['All actual Docker/database/network/process execution forbidden; only stdlib process/file boundary transports modeled','Historical sanitized Owner7293 native/oracle/ledger rows are offline fixtures only, every asset hash verified before JSON','Clone-only source approval/literal projection never changes live PENDING gates','Prefix expiry is a deliberate aggregate SQL-response projection; single current expiry is independently rejected','Coauthor tests are not independent source approval']}
 path=TASK/('sixread-owned-full-composed-author-probe-'+uuid.uuid4().hex[:8]+'-20261119.json')
 with path.open('xb')as handle:handle.write(encoded(record))
 print(json.dumps({'author_probe':str(path),'sha256':sha(path.read_bytes()),'test_methods':suite.result.testsRun,'success':suite.result.wasSuccessful()}))
 raise SystemExit(0 if suite.result.wasSuccessful()else 1)
