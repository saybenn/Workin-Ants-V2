"""Pure source-bound INSTALL ledger comparison; no filesystem/process/network.

The owned outer operator admits immutable source bytes before constructing this
adapter. Schema/ACL rules are byte-derived from the reviewed1cb source function;
no native observation is ever an expected schema. The old42501 module is intact.
"""
import ast
from collections import Counter
import hashlib
import json
import re
from types import ModuleType
import uuid

SELF='scripts/sql-review/install_ledger_proof_v3.py'
OLD='scripts/sql-review/prisma_ledger_proof.py'
COLLECTOR='scripts/sql-review/collect_prisma_ledger.sql'
PROTOCOL='scripts/install_control_protocol_v2.py'
CLOSURE='context/reconciliation/local-f0-tooling/prisma-tools-closure.json'
CANONICAL='prisma/foundation/migrations/20261117000100_f0_local_initial/migration.sql'
FAULT='review-output/install-control-rehearsal-v3/division_failure/20261117000100_f0_local_initial/migration.sql'
ENGINE_PACKAGE='node_modules/@prisma/engines-version/package.json'
PRISMA_PACKAGE='node_modules/prisma/package.json'
FIXED={OLD:'1cb05b1d82b67580671cccf5f9289fbc481fef2d77532b049658912428604b21',COLLECTOR:'6dfa02fa375da4a126b996fc547dfff063c61b41c854db6b07ea62f52d63286b',PROTOCOL:'6c1474dc12a603b07346fff014c8ab8bd15dec5be0b972ec1d504342115ba48f',CLOSURE:'610e36e4006e9680d0e6a036486f302a18ecce9593699125b4173f5914acb88b',CANONICAL:'5ae39abf991f9c189e367eb6ab6968b0ad50836bf4220ac27ef8c18306ac26ad',FAULT:'dd088298a5ffc9b42543c249fd433d7de1d22cabcc9ec108f928737c346b8c5c'}
INPUTS=(*FIXED,SELF,ENGINE_PACKAGE,PRISMA_PACKAGE)
ENGINE='d1b3f377ca835d73fd50954a5e22128b9ebdd6b8';EXPECTED='3be81a13d3bb2abb41bf03ef68398da6d92fbdbccffec3d74508e91dd455f433'
MIGRATION='20261117000100_f0_local_initial';OWNER='wa_migrator';LEDGER='public._prisma_migrations'
PRIVILEGES=('SELECT','INSERT','UPDATE','DELETE','TRUNCATE','REFERENCES','TRIGGER','MAINTAIN')
REG_FORMAT='workinants.prisma-ledger-registration.v1';EVIDENCE_FORMAT='workinants.prisma-ledger-evidence.v1';NATIVE_FORMAT='workinants.prisma-ledger-native.v1'

class LedgerProofError(ValueError):pass
def need(value,code):
    if not value:raise LedgerProofError(code)
def canonical(value):return json.dumps(value,sort_keys=True,separators=(',',':'),ensure_ascii=False,allow_nan=False)
def sha(raw):return hashlib.sha256(raw).hexdigest()
def digest(value):return sha(canonical(value).encode())
def text_hash(value):return sha(value.encode())
def exact(actual,wanted,code):need(canonical(actual)==canonical(wanted),code)
def hash_(value):need(type(value) is str and re.fullmatch('[0-9a-f]{64}',value),'HASH_REQUIRED');return value
def public_relation():return {'object':LEDGER,'kind':'r','owner':OWNER,'rls':False,'force_rls':False,'nonowner_acl':[]}

def schema_expectation():
    columns = []
    for ordinal, (name, typ, typmod, nullable, default) in enumerate((
        ('id', 'varchar', 40, False, None), ('checksum', 'varchar', 68, False, None),
        ('finished_at', 'timestamptz', -1, True, None), ('migration_name', 'varchar', 259, False, None),
        ('logs', 'text', -1, True, None), ('rolled_back_at', 'timestamptz', -1, True, None),
        ('started_at', 'timestamptz', -1, False, 'now()'), ('applied_steps_count', 'int4', -1, False, '0')), 1):
        columns.append({'name': name, 'ordinal': ordinal, 'type': 'pg_catalog.' + typ, 'typmod': typmod,
            'nullable': nullable, 'array_dimensions': 0, 'identity': '', 'generated': '',
            'collation_is_type_default': True, 'storage_is_type_default': True,
            'compression': '', 'is_local': True, 'inherited_count': 0,
            'default_sha256': text_hash(default) if default is not None else None})
    index = {'object': 'public._prisma_migrations_pkey', 'owner': OWNER, 'access_method': 'btree', 'persistence': 'p',
        'no_index_acl': True, 'no_options': True, 'default_tablespace': True,
        'unique': True, 'primary': True, 'valid': True, 'ready': True, 'live': True, 'immediate': True,
        'clustered': False, 'replica_identity': False, 'nulls_not_distinct': False,
        'key_count': 1, 'total_count': 1, 'no_expressions': True, 'no_predicate': True,
        'keys': [{'position': 1, 'column': 'id', 'included': False, 'opclass': 'pg_catalog.text_ops',
                  'opclass_default': True, 'collation_is_type_default': True, 'descending': False, 'nulls_first': False}]}
    return {'relations': [{'object': LEDGER, 'kind': 'r', 'owner': OWNER, 'persistence': 'p', 'access_method': 'heap',
            'rls': False, 'force_rls': False, 'replica_identity': 'd', 'no_options': True,
            'default_tablespace': True, 'not_partition': True, 'no_inheritance': True}],
        'columns': columns,
        'constraints': [{'name': '_prisma_migrations_pkey', 'kind': 'p', 'deferrable': False,
            'initially_deferred': False, 'validated': True, 'no_inherit': True, 'columns': ['id'],
            'index_name': 'public._prisma_migrations_pkey', 'no_referenced_relation': True, 'no_expression': True}],
        'indexes': [index], 'table_acl': sorted([{'grantee': OWNER, 'grantor': OWNER, 'privilege': privilege, 'grant_option': False}
            for privilege in PRIVILEGES], key=lambda item: (item['grantee'], item['grantor'], item['privilege'], item['grant_option'])),
        'column_acl': [], 'triggers_count': 0, 'policies_count': 0, 'rules_count': 0}


def make_adapter(blobs,source_hashes,protocol,target_identity):
    """Return the old comparator API over a closed admitted source-byte graph."""
    need(type(blobs) is dict and set(blobs)==set(INPUTS) and type(source_hashes) is dict and set(source_hashes)==set(INPUTS),'EXACT_LEDGER_SOURCE_GRAPH')
    need(all(type(body) is bytes and sha(body)==source_hashes[path] for path,body in blobs.items()),'LEDGER_SOURCE_HASH_MISMATCH')
    need(all(source_hashes[path]==digest_ for path,digest_ in FIXED.items()),'FIXED_LEDGER_SOURCE_CHANGED')
    source_hashes=dict(source_hashes)
    closure=json.loads(blobs[CLOSURE]);need(type(closure['file_count']) is int and closure['file_count']==len(closure['tools_files_sha256'])==10300,'FIXED_TOOL_CLOSURE_REQUIRED')
    for path in (ENGINE_PACKAGE,PRISMA_PACKAGE):need(source_hashes[path]==closure['tools_files_sha256'][path],'TOOL_PACKAGE_SOURCE_MISMATCH')
    need(json.loads(blobs[ENGINE_PACKAGE])['prisma']['enginesVersion']==ENGINE and json.loads(blobs[PRISMA_PACKAGE])['version']=='7.10.1','PINNED_ENGINE_SOURCE_REQUIRED')
    def schema_ast(raw):
        tree=ast.parse(raw);node=next(n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name=='schema_expectation');return ast.dump(node,include_attributes=False)
    need(schema_ast(blobs[SELF])==schema_ast(blobs[OLD]),'ORIGINAL_LEDGER_SCHEMA_RULES_CHANGED')
    need(type(protocol) is dict and all(callable(protocol.get(key)) for key in ('failure_verdict','require_recovery_review','ledger_rows','applied_ledger','completed')),'PINNED_INSTALL_PROTOCOL_API')
    need(type(target_identity) is dict and set(target_identity)=={'run_id','container_id','source_commit','source_tree','packet_sha256','target_attestation_sha256'},'ACTUAL_OUTER_TARGET_BINDING')
    target_identity=json.loads(canonical(target_identity))
    need(type(target_identity['run_id']) is str and str(uuid.UUID(target_identity['run_id']))==target_identity['run_id'] and uuid.UUID(target_identity['run_id']).version==4,'OUTER_RUN_ID')
    for key in ('container_id','packet_sha256','target_attestation_sha256'):hash_(target_identity[key])
    for key in ('source_commit','source_tree'):need(type(target_identity[key]) is str and re.fullmatch('[0-9a-f]{40}',target_identity[key]),'OUTER_SOURCE_CHECKPOINT')
    def failure_proof(value,identity):
        fields={'format','identity','rollback','approval','failed_cli','server_before','server_after','settings','retained_ledger','recovered_cli'}
        need(type(value) is dict and set(value)==fields and value['format']=='workinants.install-ledger-failure-proof.v1','INSTALL_FAILURE_PROOF_FIELDS');exact(value['identity'],identity,'INSTALL_FAILURE_PROOF_IDENTITY')
        need(set(identity)=={'run_id','container_id','source_commit','source_tree','packet_sha256','source_sql_sha256'} and identity['source_sql_sha256']==FIXED[FAULT],'INSTALL_FAILURE_SOURCE_IDENTITY')
        need(type(identity['run_id']) is str and str(uuid.UUID(identity['run_id']))==identity['run_id'] and uuid.UUID(identity['run_id']).version==4,'INSTALL_FAILURE_RUN')
        for key in ('container_id','packet_sha256','source_sql_sha256'):hash_(identity[key])
        for key in ('source_commit','source_tree'):need(type(identity[key]) is str and re.fullmatch('[0-9a-f]{40}',identity[key]),'INSTALL_FAILURE_SOURCE_CHECKPOINT')
        rollback=value['rollback'];need(type(rollback) is dict and set(rollback)=={'schema','run_id','source_commit','source_tree','packet_sha256','container_id','source_sql_sha256','failure','failed_ledger','application_inventory','original_grantor_finalized','disposition'},'INSTALL_ROLLBACK_FIELDS')
        need(rollback['schema']=='workinants.install-rollback-observation.v1' and rollback['disposition']=='PENDING_INDEPENDENT_REVIEW' and rollback['original_grantor_finalized'] is True,'OBSERVED_INSTALL_ROLLBACK_REQUIRED')
        exact({k:rollback[k] for k in identity},identity,'INSTALL_ROLLBACK_IDENTITY')
        exact(value['settings'],dict.fromkeys(('prefix','terse','no_statements','no_error_statements','locale','passwords','version'),True),'INSTALL_SAFE_SERVER_SETTINGS')
        exact({k:value['failed_cli'].get(k) for k in ('run_id','container_id','source_sql_sha256')},{'run_id':target_identity['run_id'],'container_id':target_identity['container_id'],'source_sql_sha256':FIXED[FAULT]},'GENUINE_FAILED_CLI_TARGET_BINDING_REQUIRED')
        rebuilt=protocol['failure_verdict']('division_failure',value['failed_cli'],rollback['application_inventory'],{'rows':[rollback['failed_ledger']],'ids_unique':True},value['server_before'],value['server_after'],FIXED[FAULT])
        exact(rebuilt,rollback['failure'],'ACTUAL_INSTALL_FAILURE_CHAIN_REQUIRED')
        protocol['require_recovery_review'](rollback,value['approval'],{key:identity[key] for key in ('run_id','container_id','source_sql_sha256')})
        protocol['applied_ledger'](value['retained_ledger'],rollback['failed_ledger'])
        recovered=value['recovered_cli'];protocol['completed'](recovered)
        exact({k:recovered.get(k) for k in ('run_id','container_id','source_sql_sha256','attestation_sha256')},{'run_id':target_identity['run_id'],'container_id':target_identity['container_id'],'source_sql_sha256':FIXED[CANONICAL],'attestation_sha256':target_identity['target_attestation_sha256']},'GENUINE_RECOVERED_CLI_BINDING_REQUIRED')
        return rollback['failed_ledger']['logs_state']
    def build_registration(migrations,*,run_id,target_attestation_sha256,source_expected_sha256,root=None,database='wa_p0c_rehearsal',install_failure_proof=None):
        need(run_id==target_identity['run_id'] and database=='wa_p0c_rehearsal' and target_attestation_sha256==target_identity['target_attestation_sha256'],'INSTALL_LEDGER_TARGET');hash_(target_attestation_sha256);need(source_expected_sha256==EXPECTED,'SOURCE_EXPECTED_CATALOG_REQUIRED')
        wanted=[{'path':CANONICAL,'migration_name':MIGRATION,'sha256':FIXED[CANONICAL],'state':'applied','count':1}]
        history=[{'name_sha256':text_hash(MIGRATION),'checksum_sha256':text_hash(FIXED[CANONICAL]),'checksum_format_valid':True,'id_is_uuid_v4':True,'started':True,'finished':True,'rolled_back':False,'time_order_valid':True,'steps':1,'logs_state':'NULL'}]
        if install_failure_proof is not None:
            identity={k:v for k,v in target_identity.items() if k!='target_attestation_sha256'};identity['source_sql_sha256']=FIXED[FAULT];logs=failure_proof(install_failure_proof,identity)
            wanted.append({'path':FAULT,'migration_name':MIGRATION,'sha256':FIXED[FAULT],'state':'rolled_back','count':1})
            history.append({'name_sha256':text_hash(MIGRATION),'checksum_sha256':text_hash(FIXED[FAULT]),'checksum_format_valid':True,'id_is_uuid_v4':True,'started':True,'finished':False,'rolled_back':True,'time_order_valid':True,'steps':0,'logs_state':logs})
        exact(migrations,wanted,'PREDECLARED_INSTALL_HISTORY_REQUIRED')
        registration={'format':REG_FORMAT,'profile':'SOURCE_BOUND_INSTALL_V2_LEDGER','engine_commit':ENGINE,'prisma_version':'7.10.1','run_id':run_id,'database':database,'target_attestation_sha256':target_attestation_sha256,'target_identity':target_identity,'source_expected_sha256':EXPECTED,'migrations':migrations,'history_expected':sorted(history,key=canonical),'schema_spec_sha256':digest(schema_expectation()),'tool_source_files_sha256':dict(source_hashes),'scope':'ACTUAL_INSTALL_LEDGER_SCHEMA_ACL_AND_COMPLETE_RETAINED_HISTORY_ONLY'}
        if install_failure_proof is not None:registration['install_failure_proof']=install_failure_proof
        return registration
    def compare_proof(registration,evidence,native,*,bootstrap_grantor,source_expected_sha256,root=None):
        findings=[]
        def check(field,wanted,actual):findings.append({'field':field,'status':'PASS' if canonical(wanted)==canonical(actual) else 'FAIL','expected_sha256':digest(wanted),'actual_sha256':digest(actual)})
        try:
            rebuilt=build_registration(registration['migrations'],run_id=registration['run_id'],target_attestation_sha256=registration['target_attestation_sha256'],source_expected_sha256=source_expected_sha256,database=registration['database'],install_failure_proof=registration.get('install_failure_proof'))
            check('source-bound-install-registration',rebuilt,registration)
            if canonical(rebuilt)!=canonical(registration):return {'status':'FAIL','checks':findings}
            if 'install_failure_proof' in registration:check('source-bound-install-failure-and-independent-review',True,True)
            need(type(evidence) is dict and set(evidence)=={'format','registration_sha256','collector_sql_sha256','run_id','target_attestation_sha256','native_catalog_before_sha256','native_catalog_after_sha256','observation'},'INSTALL_LEDGER_ENVELOPE')
            wanted={'format':EVIDENCE_FORMAT,'registration_sha256':digest(registration),'collector_sql_sha256':FIXED[COLLECTOR],'run_id':registration['run_id'],'target_attestation_sha256':registration['target_attestation_sha256'],'native_catalog_before_sha256':digest(native),'native_catalog_after_sha256':digest(native)}
            check('same-run-collector-and-native-binding',wanted,{k:v for k,v in evidence.items() if k!='observation'})
            got=evidence['observation'];need(type(got) is dict,'INSTALL_LEDGER_OBSERVATION');spec=schema_expectation();keys=set(spec)|{'format','server_version_num','database','read_only','isolation','collected_as','session_user','collector_is_superuser','history','history_ids_unique'};check('complete-observation-fields',sorted(keys),sorted(got))
            for key,value in {'format':NATIVE_FORMAT,'server_version_num':170011,'database':'wa_p0c_rehearsal','read_only':True,'isolation':'repeatable read','collected_as':bootstrap_grantor,'session_user':bootstrap_grantor,'collector_is_superuser':True,'history_ids_unique':True}.items():check(key,value,got.get(key))
            need(bootstrap_grantor=='postgres','ORIGINAL_GRANTOR_COLLECTION_REQUIRED')
            for key,value in spec.items():check('exact-'+key,value,got.get(key))
            need(type(got.get('history')) is list,'COMPLETE_LEDGER_HISTORY_REQUIRED');check('complete-retained-source-history',sorted(registration['history_expected'],key=canonical),sorted(got['history'],key=canonical))
        except Exception:check('complete-source-bound-install-ledger-proof',True,False)
        return {'status':'FAIL' if any(x['status']=='FAIL' for x in findings) else 'PASS','checks':findings}
    module=ModuleType('reviewed_install_ledger_proof_v3');module.build_registration=build_registration;module.compare_proof=compare_proof;module.schema_expectation=schema_expectation;module.public_relation=public_relation;module.validate_failure_proof=failure_proof;return module
