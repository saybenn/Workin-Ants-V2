"""Build NEW source-only wrapper from the exact independently reviewed V4 base."""
from pathlib import Path
import hashlib
TASK=Path(__file__).resolve().parent
def read(name,expected):
    raw=(TASK/name).read_bytes();assert hashlib.sha256(raw).hexdigest()==expected;return raw.decode()
def create(name,text):
    path=TASK/name
    if path.exists():
        assert path.read_bytes()==text.encode(),'EXISTING_SOURCE_BYTES_DIFFER'
    else:
        with path.open('x',encoding='utf8',newline='\n') as handle:handle.write(text)
    print(name,hashlib.sha256((TASK/name).read_bytes()).hexdigest())
core=read('execute_local_f0_catalog_v4_20261118.py','c8cc84c8b35811609200487a90aeb49ef1370232368e14b3fe66184aec96cad2')
core=core.replace("MANIFEST['purpose']=='LOCAL_F0_NATIVE_CATALOG_REHEARSAL'","MANIFEST['purpose']=='LOCAL_F0_RESTRICTED_CONTROLS_REHEARSAL'")
core=core.replace('STANDING_LOCAL_F0_NATIVE_CATALOG_REHEARSAL','STANDING_LOCAL_F0_RESTRICTED_CONTROLS_REHEARSAL')
core=core.replace("'CATALOG-SANITIZED_EXPORT','CATALOG-CLEANUP'","'CONTROL-CUSTOMER','CONTROL-WORKER','CONTROL-CONTEXT','CONTROL-UNIQUE','CATALOG-SANITIZED_EXPORT','CATALOG-CLEANUP'")
core=core.replace("TASK/'local_f0_catalog_v4_operation_steps.py'","TASK/'restricted_controls_operation_steps.py'")
core=core.replace('Only one reviewed initial migration and source-bound catalog/temp-oracle observations are prepared.','One reviewed initial migration, full native proof and explicitly selected finite restricted packets are prepared; no owner adapter or worker loop is qualified.')
core=core.replace("need(hashlib.sha256(STEPS.read_bytes()).hexdigest()==MANIFEST['steps_sha256'],'OPERATION_STEPS_SOURCE_MISMATCH')\nexec(compile(STEPS.read_text(encoding='utf8'),str(STEPS),'exec'),globals())","steps_raw=STEPS.read_bytes()\nneed(hashlib.sha256(steps_raw).hexdigest()==MANIFEST['steps_sha256'],'OPERATION_STEPS_SOURCE_MISMATCH')\nexec(compile(steps_raw,str(STEPS),'exec'),globals())")
create('restricted_controls_operator_20261118.py',core)
steps=read('local_f0_catalog_v4_operation_steps.py','ddc9e55d0a5e1c696cdc6dbd146b923f92257a57c57a0c2aadb718b5ed20c777')
steps=steps.replace("APPROVED_LOCAL_F0_NATIVE_CATALOG_ATTEMPT","APPROVED_LOCAL_F0_RESTRICTED_CONTROLS_ATTEMPT")
steps=steps.replace('def verify_packet():','def verify_catalog_packet():',1)
steps=steps.replace("name='wa-p0c-'+RUN_ID[:8]+'-catalog'","name='wa-p0c-'+RUN_ID[:8]+'-controls'",1)
steps=steps.replace('provision_migration_tools();catalog_experiment()','provision_migration_tools();catalog_experiment();restricted_experiments()',1)
steps=steps.replace("report['status']='PASS_LOCAL_NATIVE_CATALOG_SUBSET_ONLY'","report['status']='PASS_LOCAL_RESTRICTED_CONTROL_PACKETS_ONLY'",1)
steps=steps.replace('UNEXPECTED_CATALOG_WRAPPER_FAILURE','UNEXPECTED_RESTRICTED_WRAPPER_FAILURE')
steps=steps.replace("runpy.run_path(str(ROOT/'scripts/sql-review/run-first-rehearsal.py'))","closed_module('scripts/sql-review/run-first-rehearsal.py')")
steps=steps.replace("runpy.run_path(str(ROOT/'scripts/sql-review/run-local-f0-migrate.py'))","closed_module('scripts/sql-review/run-local-f0-migrate.py')")
steps+='\n\n'+(TASK/'restricted_controls_additions.py.txt').read_text()
create('restricted_controls_operation_steps.py',steps)
