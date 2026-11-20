"""Prepare NEW immutable INSTALL controls. No process, database or Git access.

No Root migration/history is edited. --prepare emits a new source-only packet;
prepare_history returns a fresh seven-file external history for an explicit run.
"""
import argparse
from copy import deepcopy
import hashlib
import json
from pathlib import Path
from types import ModuleType

ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'review-output/install-control-rehearsal-v3'
SELF='scripts/prepare-install-control-rehearsal-v3.py';PROTOCOL='scripts/install_control_protocol_v2.py';CHECK='scripts/check-install-control-rehearsal-v3.py'
APPLICATION='review-output/foundation-application.review.sql';BOOTSTRAP='review-output/foundation-bootstrap.review.sql';FINALIZER='review-output/foundation-bootstrap-finalize.review.sql'
HISTORY='scripts/prepare-local-f0-history.py';SCHEMA='prisma/review/foundation-candidate.prisma';LEDGER='scripts/sql-review/collect_prisma_ledger.sql'
MIGRATION='20261117000100_f0_local_initial'
RUNTIME=('prisma.local-f0.config.mjs','scripts/sql-review/local-f0-migrate-guard.mjs','scripts/sql-review/local-f0-migrate-runner.mjs')
TOOL_CLOSURE='context/reconciliation/local-f0-tooling/prisma-tools-closure.json'
PINNED={TOOL_CLOSURE:'610e36e4006e9680d0e6a036486f302a18ecce9593699125b4173f5914acb88b',APPLICATION:'5ae39abf991f9c189e367eb6ab6968b0ad50836bf4220ac27ef8c18306ac26ad',HISTORY:'33fe46e1b50c8d808ffb95b60cc42750e795582e6a1b15fb82f4fe93321281f8',LEDGER:'6dfa02fa375da4a126b996fc547dfff063c61b41c854db6b07ea62f52d63286b','scripts/sql-review/run-local-f0-migrate.py':'4b929dd8c46fea0fa0e09f92cf54e8bb37db194a9ce5c6fd02c0e91542d7909f',RUNTIME[0]:'ca19d1de07215b7f3304f8693745a446f051b4e46f833db1479d125dbdf46684',RUNTIME[1]:'7c78a4238e0df137f6f97e1b651a856506d86ec27a1e73b9318fcac093de227b',RUNTIME[2]:'7b3c705b2cc29149e9d9e644803d6ea8a968dd9eea8e045caa6c74a3487f52fd'}
COORDINATOR='scripts/sql-review/run-install-control-rehearsal-v3.py'
HELPERS=('scripts/sql-review/run-context-control-rehearsal.py','scripts/sql-review/run-first-rehearsal.py','scripts/sql-review/rehearsal-diagnostics.py','scripts/sql-review/collect_native_catalog.sql')
REVIEW_INPUTS=('scripts/install_independent_review_protocol_v1.py', 'scripts/test_install_independent_review_protocol_v1.py', 'scripts/sql-review/watch-install-independent-review-v2.py', 'scripts/sql-review/test_watch_install_independent_review_v2.py', 'scripts/sql-review/install_ledger_proof_v3.py', 'scripts/sql-review/test_install_ledger_proof_v3.py')
INPUTS=tuple(sorted(set(REVIEW_INPUTS)|set(PINNED)|{SELF,PROTOCOL,CHECK,COORDINATOR,*HELPERS,'scripts/sql-review/install-controls-coordinator-v3.md',BOOTSTRAP,FINALIZER,SCHEMA,'prisma/foundation/history-manifest.json','scripts/sql-review/prisma_ledger_proof.py','context/reconciliation/database-candidate-tests.json','context/reconciliation/local-f0-assertions.json','context/reconciliation/local-f0-tooling/prisma-tools-closure.json'}))
def sha(raw):return hashlib.sha256(raw).hexdigest()
def encoded(value):return (json.dumps(value,indent=2,allow_nan=False)+'\n').encode()
def need(value,code):
    if not value:raise ValueError(code)
def compile_pure(root,path,raw):
    module=ModuleType('_install_source_'+Path(path).stem.replace('-','_'));module.__file__=str(root/path);exec(compile(raw,module.__file__,'exec'),module.__dict__);return module.__dict__
def build(root=ROOT,source_blobs=None):
    root=Path(root)
    if source_blobs is None:blobs={path:(root/path).read_bytes() for path in INPUTS}
    else:
        need(type(source_blobs) is dict and set(source_blobs)==set(INPUTS) and all(type(v) is bytes for v in source_blobs.values()),'CLOSED_CACHED_SOURCE_MAP');blobs=dict(source_blobs)
    pins={path:sha(raw) for path,raw in blobs.items()}
    for path,wanted in PINNED.items():need(pins[path]==wanted,'REVIEWED_SOURCE_DRIFT')
    protocol=compile_pure(root,PROTOCOL,blobs[PROTOCOL]);files={};variants={}
    for variant in protocol['VARIANTS']:
        body=protocol['derive'](blobs[APPLICATION],variant);path=variant+'/'+MIGRATION+'/migration.sql';files[path]=body;variants[variant]={'path':path,'sha256':sha(body),'state':'NOT_RUN','derivation':'UNCHANGED_CANONICAL' if variant=='canonical' else 'ONE_IMMUTABLE_INJECTED_22012_BEFORE_RESET_ROLE' if variant=='division_failure' else 'ONE_EXACT_EXISTING_GRANT_MOVED_AFTER_ITS_OWNER_TRANSFER'}
    files['bootstrap.sql']=blobs[BOOTSTRAP];files['finalize.sql']=blobs[FINALIZER]
    members="'wa_private_helper_owner'::regrole,'wa_customer_verifier'::regrole,'wa_track_verifier'::regrole"
    files['authority-observe.sql']=("SELECT jsonb_build_object('temporary_memberships',(SELECT count(*) FROM pg_auth_members WHERE member='wa_schema_owner'::regrole AND roleid IN ("+members+")),'exact_temporary_options',NOT EXISTS(SELECT 1 FROM pg_auth_members WHERE member='wa_schema_owner'::regrole AND roleid IN ("+members+") AND (grantor<>'postgres'::regrole OR admin_option OR inherit_option OR NOT set_option)),'leaf_create',EXISTS(SELECT 1 FROM (VALUES('wa_private_helper_owner'),('wa_customer_verifier'),('wa_track_verifier')) x(name) WHERE has_schema_privilege(x.name,'platform_private','CREATE')),'permanent_migrator_edge',(SELECT count(*)=1 AND bool_and(roleid='wa_schema_owner'::regrole AND grantor='postgres'::regrole AND NOT admin_option AND NOT inherit_option AND set_option) FROM pg_auth_members WHERE member='wa_migrator'::regrole));\n").encode()
    roles=','.join("'"+role+"'" for role in protocol['RUNTIME_ROLES'])
    files['inactive-observe.sql']=("SELECT jsonb_build_object('runtime_roles',(SELECT count(*) FROM pg_authid WHERE rolname IN ("+roles+")),'all_null_verifiers',(SELECT bool_and(rolpassword IS NULL) FROM pg_authid WHERE rolname IN ("+roles+")),'flags_exact',(SELECT bool_and(rolcanlogin AND NOT rolsuper AND NOT rolbypassrls AND NOT rolinherit AND NOT rolcreaterole AND NOT rolcreatedb AND NOT rolreplication) FROM pg_authid WHERE rolname IN ("+roles+")));\n").encode()
    files['fresh-observe.sql']=b"SELECT jsonb_build_object('no_existing_application_namespaces',NOT EXISTS(SELECT 1 FROM pg_namespace WHERE nspname IN ('app','platform','platform_private')),'no_existing_application_roles',NOT EXISTS(SELECT 1 FROM pg_roles WHERE rolname LIKE 'wa\\_%' ESCAPE '\\'),'ledger_absent',to_regclass('public._prisma_migrations') IS NULL);\n"
    files['inventory.sql']=b"SELECT jsonb_build_object('relations',(SELECT count(*) FROM pg_class c JOIN pg_namespace n ON n.oid=c.relnamespace WHERE n.nspname IN ('app','platform','platform_private')),'functions',(SELECT count(*) FROM pg_proc p JOIN pg_namespace n ON n.oid=p.pronamespace WHERE n.nspname IN ('app','platform','platform_private')),'types',(SELECT count(*) FROM pg_type t JOIN pg_namespace n ON n.oid=t.typnamespace WHERE n.nspname IN ('app','platform','platform_private')),'enums',(SELECT count(*) FROM pg_type t JOIN pg_namespace n ON n.oid=t.typnamespace WHERE n.nspname IN ('app','platform','platform_private') AND t.typtype='e'),'other_clients',(SELECT count(*) FROM pg_stat_activity WHERE backend_type='client backend' AND pid<>pg_backend_pid()));\n"
    # Preserve the reviewed source-safe ordinary-heap/owner/8-builtin-column
    # lock+DO preflight verbatim before the new minimized history projection.
    ledger=blobs[LEDGER].decode();guard=ledger[:ledger.index('WITH ledger AS (')]
    projection="SET LOCAL TimeZone='UTC'; SELECT jsonb_build_object('ids_unique',count(*)=count(DISTINCT id),'rows',COALESCE(jsonb_agg(jsonb_build_object('name_sha256',encode(sha256(convert_to(migration_name,'UTF8')),'hex'),'checksum_sha256',encode(sha256(convert_to(checksum,'UTF8')),'hex'),'finished',finished_at IS NOT NULL,'rolled_back',rolled_back_at IS NOT NULL,'steps',applied_steps_count,'logs_state',CASE WHEN logs IS NULL THEN 'NULL' WHEN logs='' THEN 'EMPTY' ELSE 'NONEMPTY' END,'immutable_sha256',encode(sha256(convert_to(jsonb_build_object('id',id,'name',migration_name,'checksum',checksum,'started',started_at,'logs',logs,'steps',applied_steps_count)::text,'UTF8')),'hex')) ORDER BY started_at,id),'[]'::jsonb)) FROM ONLY public._prisma_migrations; COMMIT;\n"
    files['ledger-observe.sql']=(guard+projection).encode()
    grant=b'GRANT wa_private_helper_owner,wa_customer_verifier,wa_track_verifier TO wa_schema_owner WITH ADMIN FALSE, INHERIT FALSE, SET TRUE;'
    need(blobs[BOOTSTRAP].count(grant)==1,'EXACT_ORIGINAL_TEMPORARY_MEMBERSHIPS');files['rearm.sql']=b'BEGIN;\n'+grant+b'\nCOMMIT;\n'
    files['README.md']=b'''Source-only INSTALL01/02 controls. All assertions remain NOT_RUN. Derived SQL copies never replace Root canonical5ae or its historical provenance. One copy injects SELECT1/0 immediately before RESETROLE/COMMIT; one moves a single existing bind_request_context EXECUTE grant after transfer to the NOINHERIT owner. A warning is unexpected; only exact native42501 function denial qualifies that branch. Genuine Prisma uses unchanged pinned host/Node tools and fresh seven-file run histories. Four runtime roles stay NULL-verifier/inactive until closed successful install and independently verified original-grantor cleanup. Failure cleanup alone never permits activation. Independent actual rollback/ledger review must authorize standard resolve against the faulty history; separately reviewed canonical history then retries without rewriting the retained failed row or any applied checksum. A new22012 proof path never relabels historical42501/196c evidence. Existing masked-ledger adapter is42501-specific, so recovered ledger/source metadata are recorded separately until an applicable full comparison is independently reviewed. No root/admin adversary prevention, provider, owner contract, production readiness or whole94/451 qualification is claimed.\n\nPlain English: Try a safe toy installation and two broken copies. Keep the other keys turned off until the good installation and cleanup are checked. Keep the failure ticket when a reviewer permits a retry. These games have not run.\n'''
    register=json.loads(blobs['context/reconciliation/database-candidate-tests.json']);inventory=json.loads(blobs['context/reconciliation/local-f0-assertions.json']);ids=('P0C-INSTALL-01','P0C-INSTALL-02')
    definitions={name:deepcopy(next(row for row in register['tests'] if row['id']==name)) for name in ids};assertions={name:deepcopy(next(row for row in inventory['cases'] if row['id']==name)) for name in ids}
    prepared={name:sha(raw) for name,raw in files.items()};content={'source_files_sha256':pins,'prepared_files_sha256':prepared}
    packet={'schema':'workinants.install-control-fixtures.v1','status':'NOT_RUN','posture':'D','database_contacted':False,'selected_control_ids':list(ids),'source_definitions':definitions,'source_assertions':assertions,**content,'source_only_packet_sha256':sha(protocol['canonical'](content).encode()),'tool_closure_source':{'path':TOOL_CLOSURE,'sha256':pins[TOOL_CLOSURE],'file_count':10300},'variants':variants,'migration_id':MIGRATION,'runtime_roles':list(protocol['RUNTIME_ROLES']),'source_assessment':{'unchanged_guard_accepts_explicit_SQL_hash':'SOURCE_VERIFIED_OFFLINE_REPRODUCTION_REQUIRED','late_GRANT_requires_zero_effective_privileges':'PG17_PRIMARY_RESTRICT_AND_CHECK_GRANT','current_bootstrap_activates_no_passwords':'FOUR_RUNTIME_ROLES_REMAIN_NULL_UNTIL_NEW_COORDINATOR_ACTIVATION','old_masked_ledger_mode':'42501_SPECIFIC_NOT_REUSED_FOR22012'},'primary_sources':['https://www.postgresql.org/docs/17/sql-grant.html','https://raw.githubusercontent.com/postgres/postgres/REL_17_11/src/backend/catalog/aclchk.c'],'limits':{'all_assertions':'NOT_RUN','posture':'D','whole_94_or_451_promotion':False,'root_canonical_or_history_modified':False,'full_masked_22012_native_ledger_adapter':'NOT_IMPLEMENTED_EXISTING_ADAPTER_UNCHANGED','runtime_requires_independent_source_and_literal_review':True}}
    if source_blobs is None:need(all(sha((root/path).read_bytes())==digest for path,digest in pins.items()),'SOURCE_CHANGED_DURING_PREPARATION')
    files['fixtures.json']=encoded(packet);return files,packet
def prepare_history(root,manifest_bytes,variant,source_blobs=None):
    root=Path(root);files,packet=build(root,source_blobs);manifest=json.loads(manifest_bytes);need(variant in packet['variants'],'REGISTERED_VARIANT');v=packet['variants'][variant];source=files[v['path']]
    need(manifest['source']['integrated_sql_sha256']==v['sha256'],'EXPLICIT_VARIANT_MANIFEST_PIN')
    raw=(root/HISTORY).read_bytes() if source_blobs is None else source_blobs[HISTORY];need(sha(raw)==PINNED[HISTORY],'HISTORY_HELPER_DRIFT');helper=compile_pure(root,HISTORY,raw)
    runtime={name:(root/name).read_bytes() if source_blobs is None else source_blobs[name] for name in RUNTIME};schema=(root/SCHEMA).read_bytes() if source_blobs is None else source_blobs[SCHEMA];generated,history=helper['prepare_plan'](manifest,manifest_bytes,source,schema,runtime,v['sha256'])
    return {**generated,SCHEMA:schema,**runtime,'prisma/foundation/history-manifest.json':encoded(history)}
def main(argv=None):
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--prepare',action='store_true');args=parser.parse_args(argv)
    if not args.prepare:parser.error('explicit source preparation required; no runtime')
    files,packet=build();OUT.mkdir(exist_ok=False)
    for name,raw in files.items():
        path=OUT/name;path.parent.mkdir(parents=True,exist_ok=True)
        with path.open('xb') as handle:handle.write(raw)
    print(json.dumps({'status':'SOURCE_PREPARED_NOT_RUN','files':len(files),'content_sha256':packet['source_only_packet_sha256'],'database_contacted':False}));return 0
if __name__=='__main__':raise SystemExit(main())
