"""Private static assembly only; no subprocess or database operations."""
from pathlib import Path
import ast, hashlib, json, re
OUT=Path(__file__).resolve().parent
TASK=OUT.parent
ROOT=OUT/'future-root'
PRESERVED=TASK/'runtime-lease-two-history-owned-v1-FINAL-frozen-author-20261123/preserved-before-implementation'
FIVE=('execute_local_f0_runtime_lease_two_history_owned_v1_20261123.py','local_f0_runtime_lease_two_history_owned_v1_operation_steps.py','prepare_local_f0_runtime_lease_two_history_owned_v1_plan.py','check_local_f0_runtime_lease_two_history_owned_v1_operation.py','pin_local_f0_runtime_lease_two_history_owned_v1_plan_20261123.py')
def sha(b):return hashlib.sha256(b).hexdigest()
def write(name,text):
 p=OUT/name
 if p.exists():
  held=OUT/'author-history'/('before-'+str(len(list((OUT/'author-history').glob('*'))))+'.txt');held.parent.mkdir(exist_ok=True);held.open('xb').write(p.read_bytes())
 p.write_bytes(text.encode('utf8'))
def old(name):return(PRESERVED/'TASK'/name).read_text(encoding='utf8')
core=old('execute_local_f0_install_controls_20261120_source_phase_v5.py')
core=core[:core.index('def launch(')]
core=core.replace('def initialize(manifest_path):','def initialize(manifest_path,io=None):\n    global TRANSPORT,PROCESS_ADMITTED,MANIFEST_ORIGIN,FIRST_OPERATION_FAILURE\n    FIRST_OPERATION_FAILURE=None\n    PROCESS_ADMITTED=False')
core=core.replace("ROOT=TASK/'workinants-correction-pass'","ROOT=Path(MANIFEST['source_root']).resolve()")
# MANIFEST must be read before resolving its explicit, confined source root.
core=core.replace("    ROOT=Path(MANIFEST['source_root']).resolve()\n",'')
core=core.replace("    MANIFEST_PATH=Path(manifest_path).resolve()","    raw_manifest_path=Path(manifest_path)\n    hold(not any(p.is_symlink()for p in(raw_manifest_path,*raw_manifest_path.parents)),'MANIFEST_PATH_LINK')\n    MANIFEST_PATH=raw_manifest_path.resolve()")
core=core.replace("    MANIFEST=json.loads(MANIFEST_PATH.read_text(encoding='utf8'))","    manifest_raw,MANIFEST_ORIGIN=closed_bytes(MANIFEST_PATH)\n    MANIFEST=strict_json(manifest_raw)\n    ROOT=Path(MANIFEST['source_root']).resolve()\n    hold(ROOT.parent==TASK and ROOT.name in('future-root','workinants-correction-pass'),'SOURCE_ROOT_CONFINEMENT')\n    TRANSPORT=Transport(ROOT,io)")
core=core.replace("assert MANIFEST['purpose']=='LOCAL_F0_INSTALL_CONTROLS_REHEARSAL'","hold(MANIFEST['schema']=='workinants.local-f0-runtime-lease-two-history-owned-operation.v1'and MANIFEST['purpose']=='LOCAL_F0_TWO_HISTORY_OWNED','OWNED_OPERATION_SCHEMA')")
core=core.replace("    if name in finalization_attempted:return\n", "    need(not TRANSPORT.unknown,'FINALIZATION_UNKNOWN_TRANSPORT')\n    if name in finalization_attempted:return\n")
core=core.replace("        need(docker(['container','start',created_containers[name]]).returncode==0,'CONTAINER_START_FAILED')", "        report['stage']='RESOURCE_PRESTART';save();inspect_owned(running=False)\n        need(docker(['container','start',created_containers[name]]).returncode==0,'CONTAINER_START_FAILED')")
core=core.replace("        need(ready,'DATABASE_READINESS_TIMEOUT')", "        need(ready,'DATABASE_READINESS_TIMEOUT')\n        report['stage']='RESOURCE_RUNNING';save();inspect_owned(running=True)")
core=core.replace("report['steps']['CATALOG-CLEANUP']='PASS'","report['steps']['TWO-HISTORY-CLEANUP']='PASS'")
core=core.replace("path.name in ('canonical-bootstrap-password','division_failure-bootstrap-password','late_function_grant-bootstrap-password','install-role-passwords.json')","path.name == 'ok-bootstrap-password'")
core=core.replace("report['stage']=stage;report['events'].append({'stage':stage,'status':status,**safe});save()","report['stage']=stage;report['events'].append({'stage':stage,'status':status,**safe});\n        mapped={'LOCAL_PREFLIGHT':'LOCAL','RESOURCE_READY':'RESOURCES','CONTROLLED_CLEANUP':'CLEANUP'}.get(stage,stage)\n        if mapped in report.get('steps',{}):report['steps'][mapped]=status\n        save()")
transport=(OUT/'core_transport.py.txt').read_text(encoding='utf8').replace('else30','else 30').replace('import math, threading','import math, threading, stat')
# Earlier definitions are preserved static provenance; the new facade/entry and
# cached image implementation are explicit same-file definitions, not patches
# to any old imported module. Remove superseded old definitions entirely.
tree=ast.parse(core)
remove={'command','json_ok','ensure_image','record_failure','_required_safety_first_exception','_RequiredSafetyBoundary'}
lines=core.splitlines(keepends=True)
for node in sorted((n for n in tree.body if isinstance(n,(ast.FunctionDef,ast.ClassDef))and n.name in remove),key=lambda n:n.lineno,reverse=True):
 del lines[node.lineno-1:node.end_lineno]
core=''.join(lines)+'\n'+(OUT/'correction_core.py.txt').read_text(encoding='utf8')
start=core.index('"""');end=core.index('"""',start+3)
core='"""Dormant one-target two-history machinery operator; Root alone executes.\nNo business cases, permission repair or recovery.\n"""'+core[end+3:]
core=core.replace('STANDING_LOCAL_F0_INSTALL_CONTROLS_REHEARSAL','STANDING_LOCAL_F0_TWO_HISTORY_MACHINERY_ONLY')
core=core.replace("    passwords={};secret_paths=[];", "    report['schema']='workinants.two-history-owned-run-evidence.v1'\n    passwords={};secret_paths=[];")
# Finite versioned code/stage vocabularies. No arbitrary exception strings or
# caller-created stage labels are admitted to retained first-origin metadata.
all_text=core+'\n'+transport+'\n'+(OUT/'steps.py.txt').read_text(encoding='utf8')
vocabulary={n.value for n in ast.walk(ast.parse(re.sub(r'\belse(?=[0-9])','else ',all_text)))if isinstance(n,ast.Constant)and type(n.value)is str and re.fullmatch('[A-Za-z][A-Za-z0-9_-]{0,95}',n.value)}
def error_codes(tree):
 result=set()
 second={'need','hold','require','record_failure','_required_safety_failure','_latch_first_failure'}
 first={'Stop','TransportStop','HeldFailure','ValueError','remember','mark_evidence_incomplete'}
 for node in ast.walk(tree):
  if not isinstance(node,ast.Call)or not isinstance(node.func,ast.Name):continue
  at=1 if node.func.id in second else 0 if node.func.id in first else None
  if at is not None and len(node.args)>at and isinstance(node.args[at],ast.Constant)and type(node.args[at].value)is str and re.fullmatch('[A-Z0-9_]{1,96}',node.args[at].value):result.add(node.args[at].value)
 return result
failure_codes=error_codes(ast.parse(re.sub(r'\belse(?=[0-9])','else ',all_text)))|{'UNEXPECTED_OWNED_FAILURE','EVIDENCE_WRITE_UNCONFIRMED'}
for n in('scripts/sql-review/run-local-f0-runtime-lease-history-v1.py','scripts/sql-review/runtime_lease_two_row_ledger_v1.py','scripts/sql-review/runtime_lease_effective_catalog_v1.py'):
 tree=ast.parse((ROOT/n).read_bytes());failure_codes.update(error_codes(tree))
stages=set(vocabulary)|{'UNEXPECTED_STAGE'}|{'AUTH_'+r for r in('postgres','wa_migrator','wa_context_issuer','wa_identity_service_authority','wa_app_runtime','wa_worker')}
stages.update(('NATIVE_INITIAL_LEDGER_BEFORE','NATIVE_INITIAL_LEDGER_AFTER','LEDGER_INITIAL','NATIVE_initial','NATIVE_AFTER_ORACLE_initial','NATIVE_AFTER_LEDGER_initial','ORACLE_initial','LEDGER_initial','NATIVE_NOOP','LEDGER_NOOP','NATIVE_AFTER_NOOP_LEDGER','LEDGER_FINGERPRINT_before-noop','LEDGER_FINGERPRINT_after-noop'))
safe='\nSAFE_FAILURE_CODES=frozenset('+repr(sorted(failure_codes))+')\nSAFE_FAILURE_STAGES=frozenset('+repr(sorted(stages))+')\n'
write(FIVE[0],core+safe+'\n'+transport)
for i,part in ((1,'steps.py.txt'),(2,'prepare.py.txt'),(3,'checks.py.txt'),(4,'pin.py.txt')):
 if(OUT/part).exists():
  text=re.sub(r'\belse(?=[0-9])','else ',(OUT/part).read_text(encoding='utf8'))
  if i==1:
   source=old('local_f0_owner_read_operation_steps_resource_mount_v2.py');tree=ast.parse(source)
   names={'NATIVE_LISTS','BOOL_KEYS','INT_KEYS','META_KEYS','ACL_FIELDS','NATIVE_ROWS','METADATA_DIAGNOSTIC_ENTRY_LIMIT','METADATA_DIAGNOSTIC_NODE_LIMIT','OWNER_SECRET_TMPFS_TOKEN','OWNER_SECRET_TMPFS_SCRIPT'}
   functions={'canonical','digest','exact','unique_json','metadata_allowlist','generated_identifier','filter_metadata','metadata_vocabulary_diagnostics','row_shapes','safe_rejection','successful_query','records','collect_native','observe_public_baseline','oracle_records','acl_compatibility_preflight','text_compatibility_preflight'}
   pieces=[]
   for node in tree.body:
    target={n.id for n in node.targets if isinstance(n,ast.Name)}if isinstance(node,ast.Assign)else set()
    if target&names or isinstance(node,ast.FunctionDef)and node.name in functions or isinstance(node,ast.Expr)and ast.get_source_segment(source,node).startswith('META_KEYS.'):
     pieces.append(ast.get_source_segment(source,node))
   codes=set()
   for n in('scripts/sql-review/run-local-f0-runtime-lease-history-v1.py','scripts/sql-review/runtime_lease_two_row_ledger_v1.py','scripts/sql-review/runtime_lease_effective_catalog_v1.py'):
    for node in ast.walk(ast.parse((ROOT/n).read_bytes())):
     if isinstance(node,ast.Call)and isinstance(node.func,ast.Name)and node.func.id in('need','require')and node.args and isinstance(node.args[-1],ast.Constant)and type(node.args[-1].value)is str and re.fullmatch('[A-Z0-9_]{1,96}',node.args[-1].value):codes.add(node.args[-1].value)
   text=text.replace('# INSERT_STATIC_REVIEWED_METADATA_HELPERS','SAFE_HELPER_CODES='+repr(sorted(codes))+'\n\n'+'\n\n'.join(pieces))
  write(FIVE[i],text)
for name in FIVE:
 if(OUT/name).exists():compile((OUT/name).read_bytes(),str(OUT/name),'exec')
print(json.dumps({'static_files_written':sum((OUT/n).exists()for n in FIVE),'runtime':'NOT_RUN','Root_changed':False}))
