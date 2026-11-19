"""Exclusive SOURCE derivation only; never invokes Git/process/network/database."""
from pathlib import Path
import ast,hashlib,json,shutil
TASK=Path(__file__).resolve().parent;ROOT=TASK/'workinants-correction-pass'
sha=lambda value:hashlib.sha256(value).hexdigest()
OLD=('execute_local_f0_owner_read_20261119_safety_sql_v1.py','local_f0_owner_read_operation_steps_safety_sql_v1.py','prepare_local_f0_owner_read_plan_safety_sql_v1.py','check_local_f0_owner_read_operation_safety_sql_v1.py','pin_local_f0_owner_read_plan_20261119_safety_sql_v1.py')
NEW=('execute_local_f0_privilege_ceiling_safety_sql_v1_20261119.py','local_f0_privilege_ceiling_safety_sql_v1_operation_steps.py','prepare_local_f0_privilege_ceiling_safety_sql_v1_plan.py','check_local_f0_privilege_ceiling_safety_sql_v1_operation.py','pin_local_f0_privilege_ceiling_safety_sql_v1_plan_20261119.py')
BASE_VALIDATION='context/reconciliation/local-f0-owner-read-safety-sql-v1-source-validation.json'
ARCHIVE='context/reconciliation/local-f0-operation-sources/privilege-ceiling-owned-safety-sql-v1'
VALIDATION='context/reconciliation/local-f0-privilege-ceiling-owned-safety-sql-v1-source-validation.json'
PEER='context/reconciliation/local-f0-operation-sources/privilege-ceiling-source-v1/reviews/privilege_ceiling_independent_root_source_review_20261119.json'
PEER_SHA='41f6ad5a4abf7b6e7cc085d6ff545192fb4587272f7baa87dc7e18dd823e2f4a'
COORD='scripts/sql-review/run-privilege-ceiling-control-rehearsal.py'
COORD_SHA='80ca5e62a6a89891e73ecb7afc0e134c3c5b75ed81d0f3adc01ba7c718d03d3f'
FIXTURE_SHA='4ebe8b6cd7b85ff5ad8dbb79d431bb7001cf16dea72e3920138be4b5f2855e68'
CONTENT_SHA='643232e4d068892b49e49122b7ce3b909bd86caa9e770aa923d7df00def1ec32'

def replaced_function(text,name,new):
    tree=ast.parse(text);node=next(node for node in tree.body if isinstance(node,(ast.FunctionDef,ast.ClassDef))and node.name==name)
    lines=text.splitlines(keepends=True);return ''.join(lines[:node.lineno-1])+new.rstrip()+'\n'+''.join(lines[node.end_lineno:])

def renamed(text):
    for old,new in zip(OLD,NEW):text=text.replace(old,new)
    return(text.replace('owner-read-safety-sql-v1','privilege-ceiling-owned-safety-sql-v1')
        .replace('local-f0-owner-read-safety-sql-v1-source-validation.json','local-f0-privilege-ceiling-owned-safety-sql-v1-source-validation.json')
        .replace('owner-read-owned-operator-source-validation.v1','privilege-ceiling-owned-operator-source-validation.v1')
        .replace('owner-read-control-rehearsal','privilege-ceiling-control-rehearsal')
        .replace('owner-read-fixtures.v1','privilege-ceiling-fixtures.v1')
        .replace('7f8d292ddc8ca11e12ae91e94ac62cca6cdd09d0c1f8a427ac5eefa414e66aca',FIXTURE_SHA)
        .replace('fd722b13789f1afcf244bafd4484acf4d331e1ba97387be88317718c6e42605c',CONTENT_SHA)
        .replace('scripts/sql-review/run-owner-read-control-rehearsal.py',COORD)
        .replace('8b55f608573459531d15dd732da5947f0cfda0aeb2b2632ca6ec9223e8dae6a5',COORD_SHA)
        .replace('context/reconciliation/local-f0-operation-sources/owner-read-controls-v1/reviews/independent-final.json',PEER)
        .replace('f6931e2a7c56a09ddd30e26171b54468368a2c4e6f660c160222b013c706fe31',PEER_SHA)
        .replace('scripts/owner_read_control_protocol.py','scripts/privilege_ceiling_control_protocol.py')
        .replace('LOCAL_F0_OWNER_READ','LOCAL_F0_PRIVILEGE_CEILING')
        .replace('STANDING_LOCAL_F0_OWNER_READ','STANDING_LOCAL_F0_PRIVILEGE_CEILING')
        .replace('owner_read','privilege_ceiling').replace('OWNER_READ','PRIVILEGE_CEILING')
        .replace('OWNER-READ','PRIVILEGE-CEILING').replace('owner-read','privilege-ceiling')
        .replace('OWNER_','PRIVILEGE_').replace('OwnerOperationTests','PrivilegeOperationTests')
        .replace('-ownerreads','-privilege').replace('owner-read','privilege-ceiling'))

def build():
    assert sha((TASK/'privilege_ceiling_owned_safety_source_plan_20261119.json').read_bytes())=='44865cee7954c7204d77df58ea06f5d7e7cd0df089644ebb7eec908b6000a224'
    raw=(ROOT/BASE_VALIDATION).read_bytes();assert sha(raw)=='57c8e8dbb6624c71fc5146c200e82c23056f5b1874f8c46cd82424677d2b877e';base=json.loads(raw)
    assert base['independent_safety_sql_review']['decision']=='SOURCE_APPROVED'
    for name,wanted in base['operator_sources_sha256'].items():assert sha((TASK/name).read_bytes())==wanted
    for name,wanted in base['archive_files_sha256'].items():assert sha((ROOT/name).read_bytes())==wanted
    freeze=json.loads((TASK/'privilege_ceiling_frozen_source_plan_20261119.json').read_bytes())
    for name,wanted in {**freeze['source_files_sha256'],**freeze['artifacts_sha256']}.items():assert sha((ROOT/name).read_bytes())==wanted
    preservation=TASK/'privilege-owned-before-derivation-20261119';preservation.mkdir(exist_ok=False)
    for name in OLD:(preservation/(name+'.txt')).write_bytes((TASK/name).read_bytes())
    (preservation/'owner-approved-validation.json').write_bytes(raw)
    for name in ('owner_safety_sql_v1_independent_source_review_20261119.json','owner_safety_sql_v1_root_source_review_20261119.json','privilege_ceiling_owned_safety_source_plan_20261119.json'):(preservation/name).write_bytes((TASK/name).read_bytes())
    pmap={p.relative_to(preservation).as_posix():sha(p.read_bytes())for p in preservation.rglob('*')if p.is_file()};(preservation/'manifest.json').write_text(json.dumps(pmap,indent=2)+'\n')
    texts={new:renamed((TASK/old).read_text())for old,new in zip(OLD,NEW)}
    # Concrete binding changes are source-only. Required safety functions,
    # transport, creation, finalization, cleanup and IO machinery remain exact.
    core=texts[NEW[0]].replace("'prepared_protocols':121","'prepared_protocols':200")
    core=core.replace('Held finite owner-read operator','Held finite privilege-ceiling operator').replace('exact reviewed read/gate packet','exact reviewed privilege packet')
    texts[NEW[0]]=core
    steps=texts[NEW[1]]
    helpers="(PRIVILEGE_COORDINATOR,'scripts/sql-review/run-native-table-denials-v3.py','scripts/privilege_ceiling_control_protocol.py','scripts/sql-review/run-context-control-rehearsal.py','scripts/sql-review/run-first-rehearsal.py','scripts/sql-review/rehearsal-diagnostics.py','scripts/sql-review/run-local-f0-migrate.py','scripts/prepare-local-f0-history.py')"
    lines=steps.splitlines();lines=[('HELPER_FILES='+helpers)if line.startswith('HELPER_FILES=')else line for line in lines];steps='\n'.join(lines)+'\n'
    steps=steps.replace("len(fixtures['cases'])==121","len(fixtures['cases'])==200")
    packet=json.loads((ROOT/'review-output/privilege-ceiling-control-rehearsal/fixtures.json').read_bytes())
    steps=steps.replace("len(fixtures['source_files_sha256'])==67 and len(fixtures['prepared_files_sha256'])==140",f"len(fixtures['source_files_sha256'])=={len(packet['source_files_sha256'])} and len(fixtures['prepared_files_sha256'])==200")
    steps=steps.replace("SAFE_FILES.update({'privilege-ceiling-native-attestation.json'","SAFE_FILES.update({'provider-preinstall-proof.json','privilege-ceiling-native-attestation.json'")
    steps=steps.replace("provision_migration_tools();catalog_experiment();privilege_ceiling_experiment()","provision_migration_tools();provider_preinstall();catalog_experiment();privilege_ceiling_experiment()")
    # Original provider SQL and authentication boundaries are copied by exact
    # function source from reviewed NativeV5, never its unsafe old main.
    native_raw=(TASK/'local_f0_native_access_v5_operation_steps.py').read_bytes();assert sha(native_raw)=='d815cf21217be9792c8e77962d11d16448f6dc52c6fe74604d52bb1ba6943a09'
    native=native_raw.decode();tree=ast.parse(native);nodes={node.name:node for node in tree.body if isinstance(node,ast.FunctionDef)}
    provider='\nPROVIDER_ROLES=(\'anon\',\'authenticated\',\'service_role\')\nPRIVILEGE_NATIVE={}\n'
    for name in('provider_observation','provider_authentication','provider_preinstall','provider_postinstall'):
        function=ast.get_source_segment(native,nodes[name]).replace('NATIVE_ACCESS','PRIVILEGE_NATIVE')
        if name in('provider_authentication','provider_preinstall','provider_postinstall'):
            lines=function.splitlines();body=lines[1:]
            if name=='provider_authentication':body=[line for line in body if line.strip()!="closed_backends(name,'PROVIDER_AUTHENTICATION')"]
            if name=='provider_preinstall':
                lines=[lines[0],"    name=TARGETS[0]['name']"]
            else:lines=lines[:1]
            lines.append("    with _RequiredSafetyBoundary('CLOSE',name,'"+name.upper()+"'):")
            function='\n'.join(lines+['    '+line for line in body])
        provider+=function+'\n\n'
    provider=provider.replace("PROVIDER_ROLES=(","PROVIDER_ROLES=(",1)
    steps=steps.replace('def privilege_ceiling_experiment():',provider+'\ndef privilege_ceiling_experiment():')
    steps=steps.replace("report['steps']['CATALOG-INSTALL'] = 'PASS'","provider_postinstall(name,installed)\n    report['steps']['CATALOG-INSTALL'] = 'PASS'",1)
    # New packet adapter, finite verdict and attestation are reviewed separately.
    adapter=(TASK/'privilege_owned_component_adapter_v1.py.txt').read_text()
    for name in('admit_privilege_ceiling_sources','verify_privilege_ceiling_packet','privilege_ceiling_experiment'):
        tree=ast.parse(adapter);node=next(node for node in tree.body if isinstance(node,ast.FunctionDef)and node.name==name)
        steps=replaced_function(steps,name,ast.get_source_segment(adapter,node))
    steps+= '\n'+ast.get_source_segment(adapter,next(node for node in ast.parse(adapter).body if isinstance(node,ast.FunctionDef)and node.name=='verify_privilege_result'))+'\n'
    texts[NEW[1]]=steps
    for new in(NEW[2],NEW[4]):
        text=texts[new].replace("len(packet['cases'])==121","len(packet['cases'])==200")
        text=text.replace("packet['source_files_sha256']['"+COORD+"']","'"+COORD_SHA+"'")
        text=text.replace("HELPERS={", "HELPERS={")
        if new==NEW[4]:
            start=text.index('HELPERS=');end=text.index('\nclass Held',start);text=text[:start]+'HELPERS=set('+helpers+')\n'+text[end:]
            text=text.replace('PRIVILEGE_COORDINATOR',repr(COORD))
        else:
            text=text.replace("validation='context/reconciliation/local-f0-privilege-ceiling-operation-source-validation.json'","validation='context/reconciliation/privilege-ceiling-control-source-validation.json'")
            text=text.replace("set(packet['source_files_sha256'])|", "set(packet['source_files_sha256'])|{'"+COORD+"','scripts/sql-review/run-native-table-denials-v3.py'}|")
        texts[new]=text
    for name,text in texts.items():
        compile(text,str(TASK/name),'exec')
        with(TASK/name).open('x',encoding='utf8',newline='\n')as stream:stream.write(text)
    return {name:sha((TASK/name).read_bytes())for name in NEW}

if __name__=='__main__':print(json.dumps(build(),indent=2))
