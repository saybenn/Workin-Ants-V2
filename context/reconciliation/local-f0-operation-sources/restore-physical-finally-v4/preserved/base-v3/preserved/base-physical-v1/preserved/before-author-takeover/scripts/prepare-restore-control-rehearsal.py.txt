"""Prepare a bounded synthetic RESTORE01 proposal; never run SQL or processes.

Physical backup, restore and finite quarantined probes need a separate reviewed
operator and literal resource manifest. The existing compound case stays NOT_RUN.
"""
import argparse
from copy import deepcopy
import hashlib
import json
from pathlib import Path
import re
import uuid

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'review-output/restore-control-rehearsal'
CONTROL = 'P0C-RESTORE-01'
CTX = 'review-output/context-control-rehearsal'
CTX_SHA = '118454c9171267f8c7696ec3df9019a4e8883676157b57c9a2a5154d272edb69'
CTX_CONTENT = '71f00a7b12cad6bef6f70f232a10b431d3785f03ea36ad9fce803b79ffa537d7'
APPLICATION = 'review-output/foundation-application.review.sql'
APPLICATION_SHA = '5ae39abf991f9c189e367eb6ab6968b0ad50836bf4220ac27ef8c18306ac26ad'
IMAGE = 'docker.io/library/postgres:17.11@sha256:996e9dc583ba9f0265a2c75547a9c95fb22c251e394749cab205a0a00e1856a1'
MIGRATION = '20261117000100_f0_local_initial'
ROLES = ('postgres', 'wa_migrator', 'wa_context_issuer', 'wa_identity_service_authority', 'wa_app_runtime', 'wa_worker')
PRIVATE_TABLES = ('platform_private.identity_service_authorization', 'platform_private.identity_service_receipt')
PRIVACY_GATE = 'P0F_PRIVACY_RESTORE_GENERATION_PORT'
OWNER_GATE = 'CUSTOMER_UPDATE_RECEIPT_NO_RESULT_IDENTITY_AND_CODEC_NOT_REGISTERED'
NS = uuid.UUID('8d147ef0-f954-40a8-942e-5146a1e53a5a')
COPIES = ('trusted-identity-fixtures.sql', 'fixture-trigger-restore-observe.sql', 'source-customer.sql',
          'source-customer-observe.sql', 'identity-bootstrap.sql', 'schedule.sql', 'work-observe.sql',
          'app-read.sql', 'worker-read.sql', 'grant-write-acl-observe.sql')
CATALOG_SOURCE_FILES = (
    'scripts/sql-review/catalog_manifest.py', 'scripts/sql-review/pg17_catalog_rules.py',
    'scripts/sql-review/prisma_ledger_proof.py', 'scripts/sql-review/compare_native_catalog.py',
    'scripts/sql-review/catalog_expression_oracle.py', 'scripts/sql-review/migration_server_diagnostics.py',
    'review-output/foundation-bootstrap.review.sql', APPLICATION,
    'review-output/foundation-bootstrap-finalize.review.sql', 'scripts/sql-review/foundation-bootstrap-finalize.sql',
    'prisma/review/foundation-candidate.prisma', 'context/reconciliation/foundation-sql-draft-models.json',
    'context/reconciliation/foundation-sql-draft-access.json', 'context/reconciliation/foundation-sql-verifier-access.json',
    'scripts/sql-review/collect_native_catalog.sql', 'scripts/sql-review/collect_prisma_ledger.sql')
INPUTS = (
    'scripts/prepare-restore-control-rehearsal.py', 'scripts/check-restore-control-rehearsal.py',
    'context/reconciliation/database-candidate-tests.json', 'context/reconciliation/local-f0-assertions.json',
    'context/reconciliation/database-candidate-migration-plan.md',
    'context/reconciliation/database-provenance-requirements.json',
    'context/reconciliation/foundation-sql-draft-models.json',
    'context/reconciliation/foundation-sql-draft-access.json',
    'context/reconciliation/foundation-sql-scope-policy.json',
    'scripts/assemble-foundation-sql-review.py', 'scripts/sql-review/foundation-service-authority.sql',
    'scripts/sql-review/foundation-invariants.sql', 'scripts/sql-review/foundation-verification.sql',
    APPLICATION, 'review-output/foundation-bootstrap.review.sql',
    'review-output/foundation-bootstrap-finalize.review.sql', 'prisma/review/foundation-candidate.prisma',
    'prisma/foundation/migrations/' + MIGRATION + '/migration.sql',
    'scripts/sql-review/collect_native_catalog.sql', 'scripts/sql-review/collect_prisma_ledger.sql',
    'scripts/prepare-native-catalog-review.py', 'review-output/native-catalog/source-pins.json',
    'review-output/native-catalog/public-schema-registration.json',
    'context/clusters/identity, authority, & consent/Identity & Access module/identity-access-module-architecture.md',
    'context/clusters/identity, authority, & consent/Identity & Access module/identity-access-module-implementation-plan.md',
    'context/clusters/Privacy & Location Safety/Privacy Data Erasure Module/privacy-data-erasure-module-architecture.md',
    'context/clusters/Privacy & Location Safety/Privacy Data Erasure Module/privacy-data-erasure-module-implementation-plan.md',
    'context/clusters/Moderation holds Audits and Ops/Observability Ops Module/observability-ops-module-architecture.md',
    'context/clusters/Moderation holds Audits and Ops/Observability Ops Module/observability-ops-module-implementation-plan.md',
    CTX + '/fixtures.json') + tuple(CTX + '/' + name for name in COPIES)
AUTHORITIES = {
    'basebackup': 'https://raw.githubusercontent.com/postgres/postgres/REL_17_11/doc/src/sgml/ref/pg_basebackup.sgml',
    'verifybackup': 'https://raw.githubusercontent.com/postgres/postgres/REL_17_11/doc/src/sgml/ref/pg_verifybackup.sgml',
    'password_file': 'https://www.postgresql.org/docs/17/libpq-pgpass.html',
    'hba_first_match_and_replication': 'https://www.postgresql.org/docs/17/auth-pg-hba-conf.html',
    'physical_whole_cluster': 'https://www.postgresql.org/docs/17/backup-file.html',
    'wal_and_recovery_limits': 'https://www.postgresql.org/docs/17/continuous-archiving.html',
    'logical_dump_limits': 'https://www.postgresql.org/docs/17/backup-dump.html',
    'logical_globals_separate': 'https://www.postgresql.org/docs/17/app-pg-dumpall.html'}


def sha(value): return hashlib.sha256(value).hexdigest()
def uid(name): return str(uuid.uuid5(NS, name))
def quote(value): return "'" + str(value).replace("'", "''") + "'"
def canonical(value): return json.dumps(value, sort_keys=True, separators=(',', ':'), allow_nan=False)
def sql(*lines): return '\n'.join(lines) + '\n'
def stable_read_settings():
    return ["SET LOCAL TimeZone='UTC';", "SET LOCAL DateStyle='ISO, YMD';", "SET LOCAL extra_float_digits=3;", "SET LOCAL bytea_output='hex';"]


def fingerprint_sql(tables):
    # Aggregate digest only. No row bodies, grant hashes, receipt handles or raw
    # history timestamps escape. Ordering and UTF8 encoding are explicit.
    pairs = []
    for table in tables:
        if not re.fullmatch(r'(?:app|platform|platform_private)\.[a-z_]+', table):
            raise ValueError('unsafe source table')
        pairs += [quote(table), "(SELECT jsonb_build_object('count',count(*),'rows_sha256',encode(sha256(convert_to(COALESCE(jsonb_agg(to_jsonb(x) ORDER BY to_jsonb(x)::text COLLATE \"C\"),'[]'::jsonb)::text,'UTF8')),'hex')) FROM " + table + ' x)']
    return sql('BEGIN ISOLATION LEVEL REPEATABLE READ READ ONLY;', 'SET LOCAL search_path=pg_catalog;',
               *stable_read_settings(), "SET LOCAL statement_timeout='5s';", 'SELECT jsonb_build_object(' + ',\n'.join(pairs) + ');', 'COMMIT;')


def identity_transition(service, previous_id, receipt_id, generation, transition):
    # Revocation timestamp is assigned by the real source trigger. The authority
    # update fetches that exact stored value within the SAME actual transaction.
    return sql('-- Synthetic upstream authorization only; actual separate Identity SQL login.', 'BEGIN;',
        'INSERT INTO platform_private.identity_service_receipt (id,service_principal,previous_generation,previous_receipt_id,security_generation,transition,identity_authorization_ref) VALUES (' +
        ','.join([quote(receipt_id), quote(service), str(generation - 1), quote(previous_id), str(generation), quote(transition), quote('restore01-synthetic-' + transition + '.v1')]) + ');',
        'UPDATE platform_private.identity_service_authorization a SET security_generation=r.security_generation,identity_receipt_id=r.id,revoked_at=r.revoked_at FROM platform_private.identity_service_receipt r WHERE a.service_principal=' + quote(service) + ' AND r.id=' + quote(receipt_id) + ';',
        "SELECT 'WA_RESTORE01_IDENTITY_READY';", 'COMMIT;')


def authority_observer(service, receipt_id, previous_id, generation, transition):
    revoked = 'IS NOT NULL' if transition == 'revoke' else 'IS NULL'
    prior = 'r.previous_receipt_id IS NULL' if previous_id is None else 'r.previous_receipt_id=' + quote(previous_id)
    return sql('SELECT jsonb_build_object(', "'authorization_count',(SELECT count(*) FROM platform_private.identity_service_authorization),",
        "'receipt_count',(SELECT count(*) FROM platform_private.identity_service_receipt),",
        "'exact_current_link',EXISTS(SELECT 1 FROM platform_private.identity_service_authorization a JOIN platform_private.identity_service_receipt r ON r.id=a.identity_receipt_id WHERE a.service_principal=" + quote(service) + ' AND a.security_generation=' + str(generation) + ' AND r.id=' + quote(receipt_id) + ' AND r.security_generation=a.security_generation AND r.service_principal=a.service_principal AND r.transition=' + quote(transition) + ' AND ' + prior + ' AND a.revoked_at ' + revoked + ' AND r.revoked_at IS NOT DISTINCT FROM a.revoked_at AND r.mutation_transaction_id=a.mutation_transaction_id));')


def hba(roles, physical_backup=False):
    # OS postgres must read PGDATA/pg_hba.conf. Client pgpass stays root0600 in
    # root0700 tmpfs. Do not put the server HBA inside that root-only directory.
    return sql('# Fixed synthetic quarantine; first-match order is normative.', 'local all all reject',
        *['host all ' + role + ' 127.0.0.1/32 scram-sha-256' for role in roles],
        *(['host replication postgres 127.0.0.1/32 scram-sha-256'] if physical_backup else []),
        'host replication all 127.0.0.1/32 reject', 'host all all 127.0.0.1/32 reject',
        'host replication all ::1/128 reject', 'host all all ::1/128 reject',
        'host replication all 0.0.0.0/0 reject', 'host all all 0.0.0.0/0 reject',
        'host replication all ::/0 reject', 'host all all ::/0 reject')


def build(root=ROOT, expected_sha256=None):
    root = Path(root)
    pins = {name: sha((root / name).read_bytes()) for name in INPUTS}
    if pins[APPLICATION] != APPLICATION_SHA or pins['prisma/foundation/migrations/' + MIGRATION + '/migration.sql'] != APPLICATION_SHA:
        raise ValueError('canonical source changed')
    if pins[CTX + '/fixtures.json'] != CTX_SHA: raise ValueError('unreviewed context fixture source')
    ctx = json.loads((root / CTX / 'fixtures.json').read_bytes())
    if ctx['source_only_packet_sha256'] != CTX_CONTENT: raise ValueError('context packet binding')
    ctx_digest = sha(canonical({key: ctx[key] for key in ('source_files_sha256', 'prepared_files_sha256')}).encode())
    if ctx_digest != CTX_CONTENT: raise ValueError('context digest')
    for name, digest in ctx['source_files_sha256'].items():
        if sha((root / name).read_bytes()) != digest: raise ValueError('context source drift')
        pins.setdefault(name, digest)
    for name, digest in ctx['prepared_files_sha256'].items():
        if sha((root / CTX / name).read_bytes()) != digest: raise ValueError('context artifact drift')
        pins.setdefault(CTX + '/' + name, digest)
    catalog_pins = json.loads((root / 'review-output/native-catalog/source-pins.json').read_bytes())
    if set(catalog_pins) != set(CATALOG_SOURCE_FILES): raise ValueError('closed native catalog source set changed')
    for name, digest in catalog_pins.items():
        if sha((root / name).read_bytes()) != digest: raise ValueError('native catalog assets await source refresh')
        pins.setdefault(name, digest)
    if expected_sha256 is not None and expected_sha256 != pins:
        raise ValueError('approved source pins differ')
    register = json.loads((root / 'context/reconciliation/database-candidate-tests.json').read_bytes())
    control = next(row for row in register['tests'] if row['id'] == CONTROL)
    assertions = next(row for row in json.loads((root / 'context/reconciliation/local-f0-assertions.json').read_bytes())['cases'] if row['id'] == CONTROL)
    if control['status'] != 'NOT_RUN' or len(assertions['assertions']) != 6 or any(row['status'] != 'NOT_RUN' for row in assertions['assertions']):
        raise ValueError('registered restore obligations changed')
    models = json.loads((root / 'context/reconciliation/foundation-sql-draft-models.json').read_bytes())
    tables = sorted(row['object'] for row in models) + list(PRIVATE_TABLES)
    if len(models) != 40 or len(set(tables)) != 42: raise ValueError('closed table graph changed')
    files = {name: (root / CTX / name).read_text(encoding='utf8') for name in COPIES}
    files['all-data-fingerprint.sql'] = fingerprint_sql(tables)
    business = [name for name in tables if name not in PRIVATE_TABLES and name != 'platform.database_action_grant']
    files['business-data-fingerprint.sql'] = fingerprint_sql(business)
    files['ledger-fingerprint.sql'] = sql('-- Run ONLY after guarded source collector confirms native ledger type/columns/ACL.',
        'BEGIN ISOLATION LEVEL REPEATABLE READ READ ONLY;', 'SET LOCAL search_path=pg_catalog;',
        *stable_read_settings(),
        'SELECT jsonb_build_object(\'count\',count(*),\'rows_sha256\',encode(sha256(convert_to(COALESCE(jsonb_agg(to_jsonb(x) ORDER BY to_jsonb(x)::text COLLATE "C"),\'[]\'::jsonb)::text,\'UTF8\')),\'hex\'),',
        "'exact_applied',count(*)=1 AND COALESCE(bool_and(migration_name=" + quote(MIGRATION) + ' AND checksum=' + quote(APPLICATION_SHA) + " AND finished_at IS NOT NULL AND rolled_back_at IS NULL AND logs IS NULL AND applied_steps_count=1),false)) FROM public._prisma_migrations x;", 'COMMIT;')
    files['authority-fingerprint.sql'] = sql('BEGIN ISOLATION LEVEL REPEATABLE READ READ ONLY;', 'SET LOCAL search_path=pg_catalog;',
        *stable_read_settings(),
        "WITH role_rows AS (SELECT rolname,rolsuper,rolinherit,rolcreaterole,rolcreatedb,rolcanlogin,rolreplication,rolbypassrls,rolconnlimit,rolvaliduntil,rolconfig FROM pg_roles WHERE rolname !~ '^pg_'),",
        'members AS (SELECT member::regrole::text AS member,roleid::regrole::text AS role,grantor::regrole::text AS grantor,admin_option,inherit_option,set_option FROM pg_auth_members),',
        'db AS (SELECT datname,datdba::regrole::text AS owner,datacl FROM pg_database WHERE datname=current_database())',
        "SELECT jsonb_build_object('role_attributes_sha256',(SELECT encode(sha256(convert_to(COALESCE(jsonb_agg(to_jsonb(x) ORDER BY rolname),'[]'::jsonb)::text,'UTF8')),'hex') FROM role_rows x),",
        "'memberships_sha256',(SELECT encode(sha256(convert_to(COALESCE(jsonb_agg(to_jsonb(x) ORDER BY to_jsonb(x)::text COLLATE \"C\"),'[]'::jsonb)::text,'UTF8')),'hex') FROM members x),",
        "'database_authority_sha256',(SELECT encode(sha256(convert_to(to_jsonb(db)::text,'UTF8')),'hex') FROM db),",
        "'all_six_have_scram',(SELECT count(*)=6 AND bool_and(rolpassword LIKE 'SCRAM-SHA-256$%') FROM pg_authid WHERE rolname=ANY(ARRAY[" + ','.join(quote(role) for role in ROLES) + '])),',
        "'temporary_memberships',(SELECT count(*) FROM pg_auth_members WHERE member='wa_schema_owner'::regrole AND roleid IN ('wa_private_helper_owner'::regrole,'wa_customer_verifier'::regrole,'wa_track_verifier'::regrole)),",
        "'permanent_migrator_edge',(SELECT count(*)=1 AND bool_and(roleid='wa_schema_owner'::regrole AND grantor='postgres'::regrole AND NOT admin_option AND NOT inherit_option AND set_option) FROM pg_auth_members WHERE member='wa_migrator'::regrole),",
        "'leaf_create_false',NOT EXISTS(SELECT 1 FROM (VALUES('wa_private_helper_owner'),('wa_customer_verifier'),('wa_track_verifier')) l(role) CROSS JOIN (VALUES('app'),('platform'),('platform_private')) s(name) WHERE has_schema_privilege(l.role,s.name,'CREATE')));", 'COMMIT;')
    files['backup-preflight.sql'] = sql('BEGIN READ ONLY;', 'SET LOCAL search_path=pg_catalog;',
        "SELECT jsonb_build_object('version_170011',current_setting('server_version_num')='170011','direct_postgres',session_user='postgres' AND current_user='postgres',",
        "'primary',NOT pg_is_in_recovery(),'wal_level_replica',current_setting('wal_level')='replica','two_wal_senders',current_setting('max_wal_senders')::int>=2,",
        "'temporary_slot_available',current_setting('max_replication_slots')::int>=1 AND NOT EXISTS(SELECT 1 FROM pg_replication_slots),'full_page_writes',current_setting('full_page_writes')='on',",
        "'no_senders',NOT EXISTS(SELECT 1 FROM pg_stat_replication),'no_other_clients',NOT EXISTS(SELECT 1 FROM pg_stat_activity WHERE backend_type='client backend' AND pid<>pg_backend_pid()),",
        "'no_external_tablespaces',NOT EXISTS(SELECT 1 FROM pg_tablespace WHERE spcname NOT IN ('pg_default','pg_global')),'only_expected_databases',NOT EXISTS(SELECT 1 FROM pg_database WHERE datname NOT IN ('template0','template1','postgres','wa_p0c_rehearsal')),",
        "'no_recovery_or_archive_transport',current_setting('primary_conninfo')='' AND current_setting('primary_slot_name')='' AND current_setting('restore_command')='' AND current_setting('archive_mode')='off' AND current_setting('archive_command')='' AND current_setting('archive_library')='' AND current_setting('synchronous_standby_names')='',",
        "'no_preload',current_setting('shared_preload_libraries')='' AND current_setting('session_preload_libraries')='' AND current_setting('local_preload_libraries')='','no_subscriptions',NOT EXISTS(SELECT 1 FROM pg_subscription),'no_foreign_servers',NOT EXISTS(SELECT 1 FROM pg_foreign_server),",
        "'safe_logging',current_setting('log_statement')='none' AND current_setting('log_min_error_statement')='panic' AND current_setting('log_error_verbosity')='terse' AND current_setting('lc_messages')='C',",
        "'system_identifier_sha256',(SELECT encode(sha256(convert_to(system_identifier::text,'UTF8')),'hex') FROM pg_control_system()));", 'COMMIT;')
    service = ctx['grants']['worker']['service_principal']
    bootstrap = str(uuid.UUID('9f6b0fa9-7a6f-52a6-8297-6ea55cbf6c0f'))
    if quote(bootstrap) not in files['identity-bootstrap.sql']: raise ValueError('bootstrap identity changed')
    revoke, recover = uid('identity-revoke'), uid('identity-recover')
    files['identity-revoke.sql'] = identity_transition(service, bootstrap, revoke, 1, 'revoke')
    files['identity-recover.sql'] = identity_transition(service, revoke, recover, 2, 'recover')
    for generation, name, receipt, previous in [(0, 'bootstrap', bootstrap, None), (1, 'revoke', revoke, bootstrap), (2, 'recover', recover, revoke)]:
        files['identity-' + name + '-observe.sql'] = authority_observer(service, receipt, previous, generation, name)
    files['quarantine-admin.pg_hba.conf'] = hba(('postgres',))
    files['quarantine-identity.pg_hba.conf'] = hba(('postgres', 'wa_identity_service_authority'))
    files['quarantine-diagnostic.pg_hba.conf'] = hba(ROLES)
    files['source-backup.pg_hba.conf'] = hba(('postgres',), physical_backup=True)
    source = deepcopy(ctx['source_customer']); source['control_ids'] = [CONTROL]
    grants = {}
    for name in ('source_customer', 'schedule', 'app', 'worker'):
        grant = deepcopy(ctx['grants'][name]); grant.pop('id', None)
        grant.update(template_id='restore01-' + name, status='NOT_RUN', policy_version='restore01-synthetic-fixture.v1')
        grants[name] = grant
    source['grant'] = deepcopy(grants['source_customer'])
    grants['target-app'] = {**deepcopy(grants['app']), 'template_id': 'target-app'}
    grants['target-worker-old-epoch'] = {**deepcopy(grants['worker']), 'template_id': 'target-worker-old-epoch'}
    grants['target-worker-current'] = {**deepcopy(grants['worker']), 'template_id': 'target-worker-current', 'security_generation': '2'}
    grants['target-worker-wrong-source-generation'] = {**deepcopy(grants['target-worker-current']), 'template_id': 'target-worker-wrong-source-generation', 'source_generation': '1'}
    expected_counts = {table: 0 for table in tables}
    expected_counts.update({'app.users': 1, 'app.user_security_profiles': 1, 'app.customer_profiles': 1,
        'app.customer_profile_lifecycle_event': 1, 'platform.runtime_command_receipt': 1,
        'platform.owner_mutation_evidence': 1, 'platform.runtime_outbox_message': 2,
        'platform.runtime_work_item': 1, 'platform.database_action_grant': 4,
        PRIVATE_TABLES[0]: 1, PRIVATE_TABLES[1]: 1})
    # Metadata are a source-only proposal. A future coordinator must derive grant
    # retention queries from its actual issued UUIDs, never from pretend handles.
    binding = {'actual_login': True, 'isolation': 'read committed', 'capture_before_protected_read': True,
        'capture_fields': ['backend_pid', 'backend_start', 'full_transaction_id', 'session_user', 'database'],
        'secret': 'Fresh 32 random bytes, hex; hash with SHA256(decoded bytes); private memory only.',
        'grant_id': 'Fresh UUIDv4 per issuance; no static grant UUID or fake session tuple.',
        'issuer': 'Actual separate wa_context_issuer commits and closes before same-app/worker-PID/xid bind.',
        'ttl_seconds_max': 300, 'close_before_observe': 'Client exit plus independent exact backend absence before all observers.',
        'retention': 'Each actual issued row exists, unchanged, issuer-owned and unrevoked. The source app old-tuple test additionally requires still-unexpired source grant and unchanged user security_generation0; expiry or unknown tuple makes the subprobe unqualified.',
        'diagnostic': {'sqlstate': '42501', 'exact_message': 'invalid, stale or unsupported context', 'psql_exit': 3,
            'function': 'platform_private.bind_request_context(text)', 'source_body_and_raise_line_required': True,
            'acknowledgement': False, 'no_later_statement_after_error': True}}
    probes = [
        ('target-app-current', 'target-app', 'app-read.sql', {'visible_exact_root': 1}, 'Fresh target tuple; unchanged user generation0, finite SH004 resolve only.'),
        ('source-app-old-tuple', None, None, binding['diagnostic'], 'Reuse actual source app secret on target new tuple; prove source grant unexpired/unrevoked and user gen0 unchanged so expiry/currentness cannot explain denial.'),
        ('target-worker-old-epoch', 'target-worker-old-epoch', None, binding['diagnostic'], 'Fresh target tuple with restored service epoch0; current independently recovered epoch2 denies binding.'),
        ('target-worker-current', 'target-worker-current', 'worker-read.sql', {'visible_exact_root': 1}, 'Existing SELECT-only pending-work scope at epoch2; no claim, lease or work effect.'),
        ('target-worker-wrong-source-generation', 'target-worker-wrong-source-generation', 'worker-read.sql', {'visible_exact_root': 0}, 'Bind succeeds at epoch2; finite revision0 caps and source_generation1 deny actual fence0 row through row_allowed. Transport-generation simulation only.')]
    stages = [
        ('00-review', 'Pin full source/packet/operator/literal run manifest; prove source, target and staging names, volumes, evidence and private archive absent; inspect existing pinned image only.'),
        ('01-source-install', 'Create ONE fresh run-owned source PGDATA volume/container, exact image/network-none/no ports and existing reviewed mounts only. Genuine guarded Prisma deploy once; original-grantor finalize; zero temporary memberships/leaf CREATEfalse; exact source native catalog+ledger proof and six actual SCRAM controls.'),
        ('02-source-fixtures', 'Privileged synthetic Identity seed bypasses only the exact two owner_commit triggers. Independently prove exact four restored USER trigger identities/states and no disabled project trigger. Actual app commits source Customer group and schedules pending work; actual Identity login bootstraps single synthetic principal. Source app and worker SELECT positives each issue fresh grants; observe exact source counts4grants and complete group; no business worker loop.'),
        ('03-quiesce', 'Install exact source-backup.pg_hba.conf into owned source PGDATA as observed OS postgres0600 and reload as direct postgres; independently verify pg_hba_file_rules contents/order/errorabsence and actualSCRAM. Close every restricted/issuer/Identity client. Run backup-preflight, all42 data/authority/ledger fingerprints and native-source proof; only backup admin allowed. Record no external tablespaces/slots and exact physical-replication SCRAM rule for postgres127.0.0.1 before its reject-all-replication row. This is a declared source HBA config delta, no role/grant change.'),
        ('04-backup', 'Inside exact source container root0700 private writable-layer directory OUTSIDE PGDATA, protected replication pgpass0600. Run pinned17.11 pg_basebackup over127.0.0.1/physical replication as existing postgres, WALstream two connections/temp slot; no new role/grants/ports/mounts. Run pg_verifybackup, then protect regular-file-only full tar0600; include backup_manifest, all required WAL and authid verifiers.'),
        ('05-artifact', 'Copy exact createdCID archive to exclusive owner-DACL host private path OUTSIDE Git. Retain archiveSHA256/manifestSHA256/regular file count/bytes/versions only. All-data/native/ledger/authority/source pre-post backup parity and no remaining slots/senders/restricted clients required. Stop source before restore; preserve source password in protected memory/file only.'),
        ('06-empty-target-copy', 'Create fresh target PGDATA volume and separate same-image network-none/no-port staging container. Exact hostarchiveRO+new target volumeRW mounts only. Verify host/archive hash and regular-file/directory safe names (no symlink/hardlink/devices/FIFO/dotdot/absolute), empty target, extract there, rerun pinned pg_verifybackup BEFORE config edits. No initdb/bootstrap/applicationSQL/Prisma/ledger writes on target. Verify PG_VERSION17/globalpg_control and no recovery.signal/standby.signal; chown only exact volume to image-observed postgres UID/GID, never assume999. Remove staging container.'),
        ('07-quarantine-start', 'Install fixed admin-only target PGDATA/pg_hba.conf owned by OS postgres0600 after backup verification; record permitted HBA delta. Server cannot read a root0700 client-secret tmpfs file. Start target exact image/volume/network-none/no ports/private tmpfs, same safe logging; existing PG_VERSION must skip initdb. Authenticate only postgres using protected ephemeral source credential; no service/app/worker/issuer connection.'),
        ('08-restore-parity', 'Before any role rotation/Identity transition: exact all42 row counts+digests, immutable ledger one applied row/full digest, role attributes/memberships/DBauthority/full native source catalog equal source; full physical system identifier parity. Independently observe every source fixture and trigger restoration. No postinstall baseline adoption.'),
        ('09-credential-rotation', 'As restored direct postgres with safe logging, rotate all SIX target credentials independently using fresh per-role/target256bit secrets through private stdin SQL/pgpass root0600, never argv/env/logs. No role-attribute/ACL change. Prove original postgres credential rejects after rotation and all6 new verifier presences are SCRAM; target never contacts source.'),
        ('10-identity-recovery-simulation', 'Reload exact management HBA (postgres and actual Identity login only); check parsed file/first-match order. Actual separate wa_identity_service_authority commits revoke0→1 then recovery1→2 with immutable linked receipts; same actual xid and trigger-assigned timestamp copied from receipt. Independent observers after each closed backend require exact1authorization/2then3receipts/current link. This is synthetic SQL owner-currentness, not real upstream authorization/Privacy recovery.'),
        ('11-finite-quarantined-diagnostics', 'Only now load exact diagnostic HBA/networknone/noserving. Six correct + six random-wrong + six source-old password controls, each closed, actualSCRAM errors only; plus five finite data probes. Independent restricted login and issuer commit/closure; retain original source app secret only in private memory, source grant still unexpired. After EACH closed probe verify group/work/trigger/ACL, all39 business+ledger/native+authority parity and exact allowed grant/Identity deltas; stop on any unknown. No live app server, worker loop, owner adapter or serving.'),
        ('12-requarantine', 'Close every diagnostic/issuer/Identity backend; restore admin-only HBA and reload/verify; actual five non-postgres roles must be HBA-denied. All39business/ledger/native/roleattribute parity, expected8grantrows/3Identityreceipts/1authorization, independent finalized leaf states. Keep service_activation=false.'),
        ('13-evidence-cleanup', 'Persist only source-bound hashes/counts/typed booleans/fixed stages. On any failure STOP later probes; close actualclients before observers. Remove ONLY exact createdCID/name/labels and named source+target volumes/CreatedAt plus staging. Delete exact owned secret/archive files/private dirs; all PGDATA/authid/verifier backups gone. Independently confirm all owned resources and private files absent; retain prior reports, cached image, source/tool snapshots.')]
    proposal = {'schema': 'workinants.restore-control-proposal.v1', 'status': 'NOT_RUN', 'database_posture': 'D',
        'database_contacted': False, 'sql_executed': False, 'selected_control_ids': [CONTROL],
        'source_control_definition': deepcopy(control), 'source_assertion_definition': deepcopy(assertions),
        'source_files_sha256': pins, 'authorities': AUTHORITIES, 'image': IMAGE, 'postgres_version_num': 170011,
        'method': 'PHYSICAL_WHOLE_CLUSTER_PLAIN_WAL_STREAM', 'source_customer': source,
        'required_literal_resource_manifest': {'run_id': 'Fresh UUIDv4 before any creation; separately reviewed full manifest SHA.',
            'container_names': ['wa-p0c-<run8>-restore-source', 'wa-p0c-<run8>-restore-staging', 'wa-p0c-<run8>-restore-target'],
            'volume_names': ['wa-p0c-<run8>-restore-source-data', 'wa-p0c-<run8>-restore-target-data'],
            'labels': {'workinants.rehearsal': 'p0c-local-f0', 'workinants.rehearsal.run': '<exact run UUID>'},
            'source_mounts': 'Only reviewed source PGDATA volume, exact bootstrap-password RO bind and root0700 secret tmpfs; backup in writable layer, never an extra migrate-guard mount.',
            'staging_mounts': 'Exactly protected manifested host archive RO and exact newly created target PGDATA volume RW; no source PGDATA mount.',
            'target_mounts': 'Exactly restored target PGDATA volume and root0700 client-secret tmpfs; no bootstrap bind, source volume or host archive.',
            'inspect_required': 'Immutable created CIDs, exact names/labels/image/volume CreatedAt/mount Source+Destination+RW, stopped source, absent staging before target startup; reject extras/symlinks/host PID/IPC/network namespaces, privileged/devices/Docker socket/ports/links.',
            'ipc_allowlist': ['', 'private'], 'network': 'none', 'ports': [],
            'host_archive': 'Exact exclusive owner-DACL TASK/run-evidence/private/restore01-base.tar outside Git; validated absolute Windows task-owned path plus exact Docker Desktop bind Source mapping, never credentials in manifest.',
            'server_settings': 'Exact reviewed image command-line logging prefix/terse/C/none/panic/disabled statement sampling and no external recovery/archive/preload; bootstrap verifies before provisioning any password.'},
        'source_fixture_reuse': {'context_manifest_sha256': CTX_SHA, 'context_content_sha256': CTX_CONTENT,
            'sql_bytes_copied_unchanged': list(COPIES), 'only_fresh_separate_source': True,
            'source_creation_retry_not_claimed': True, 'not_CTX01_execution': True},
        'fixture_trigger_contract': deepcopy(ctx['fixture_trigger_contract']),
        'mandatory_fixture_observers': deepcopy(ctx['mandatory_after_case_observers']),
        'tables': tables, 'business_tables': business, 'source_and_initial_restore_counts': expected_counts,
        'after_recovery_allowed_data_changes': {'platform.database_action_grant': {'before': 4, 'after': 8, 'existing_rows_immutable': True},
            PRIVATE_TABLES[0]: {'count': 1, 'generation': 2, 'revoked': False},
            PRIVATE_TABLES[1]: {'before': 1, 'after': 3, 'prior_rows_immutable': True},
            'role_passwords': 'Only independently rotated six credential verifiers; never export verifier bytes or hashes.'},
        'grants': grants, 'runtime_binding_contract': binding,
            'quarantined_simulation_probes': [{'name': name, 'status': 'NOT_RUN', 'grant_template': grant, 'sql': file,
            'expected': expected, 'scope_limit': limit, 'requires_exact_closed_backend_before_observers': True}
            for name, grant, file, expected, limit in probes],
        'identity_simulation': {'service_principal': service, 'restored_generation': 0,
            'bootstrap_receipt': bootstrap, 'revoke_receipt': revoke, 'recovery_receipt': recover,
            'order': ['rotate all6target credentials', 'revoke0to1', 'recover1to2', 'quarantined diagnostic role connections'],
            'authorization_count': 1, 'receipt_counts': [1, 2, 3], 'upstream_owner_adapter': 'SYNTHETIC_UNQUALIFIED'},
        'backup_client': {'argv': ['pg_basebackup', '--host=127.0.0.1', '--port=5432', '--username=postgres', '--no-password',
            '--pgdata=/run/wa-restore-backup/base', '--format=plain', '--wal-method=stream', '--checkpoint=fast',
            '--manifest-checksums=SHA256', '--label=wa-p0c-restore01'],
            'environment': {'PGPASSFILE': '/run/wa-secrets/replication.pgpass'},
            'password_file_fields_without_value': ['127.0.0.1', '5432', 'replication', 'postgres'],
            'password_file_mode': 'root0600', 'no_new_replication_role_or_privilege': True,
            'required_physical_replication_hba': 'host replication postgres 127.0.0.1/32 scram-sha-256',
            'source_hba_file': 'source-backup.pg_hba.conf',
            'source_mounts_unchanged': True, 'directory': 'root0700 source writable layer OUTSIDE PGDATA'},
        'backup_verify': {'argv': ['pg_verifybackup', '--exit-on-error', '--quiet', '/run/wa-restore-backup/base'],
            'version': '17.11', 'twice': ['source backup', 'staged empty target BEFORE config edits'],
            'must_parse_wal_and_verify_manifest_checksums': True,
            'independent_closure': 'Full protected archive digest plus independent PG_VERSION, pg_control, required WAL, no recovery/standby signals and exact auto.conf/HBA review. pg_verifybackup ignores some configuration/signal/WAL-directory changes; its success alone is insufficient.'},
        'quarantine': {'service_activation': False, 'serving_process': False, 'worker_loop': False,
            'network': 'none', 'host_ports': [], 'hba_files': ['quarantine-admin.pg_hba.conf', 'quarantine-identity.pg_hba.conf', 'quarantine-diagnostic.pg_hba.conf'],
            'server_hba_location': 'Target PGDATA/pg_hba.conf, observed OS postgres UID/GID0600',
            'client_secret_location': 'root0700 noexec,nosuid,nodev tmpfs; root0600 pgpass, never env password',
            'diagnostic_role_connections': 'Explicit synthetic simulations only, after Identity epoch2. Full SERVICE-RESTORE remains NOT_RUN.'},
        'stages': [{'id': name, 'status': 'NOT_RUN', 'required': text} for name, text in stages],
        'qualification': {'whole_case_status': 'NOT_RUN', 'production_restore_ready': False,
            'assertion_claim_limit': {'control.real_backup': 'Candidate real physical artifact only, pending reviewed operator + actual evidence.',
                'control.restored_parity': 'Candidate exact physical schema/data/ledger/authority parity only, pending actual evidence.',
                'control.restored_authority': 'PARTIAL only: synthetic credential/currentness/tuple simulations; real service activation stays held.'},
            'mandatory_blocked': [deepcopy(row) for row in assertions['assertions'] if row['availability'] == 'DEPENDENCY_BLOCKED'],
            'other_gates': [OWNER_GATE, 'USER_SECURITY_OWNER_RESULT_PORT_NOT_QUALIFIED', 'REVIEWED_LITERAL_RESTORE_OPERATOR_AND_RUN_MANIFEST'],
            'no_vacuous_privacy_pass': 'No Privacy rows/restore markers are synthesized. Empty fixture inventory or quarantined reads cannot prove Privacy replay before serving; missing ' + PRIVACY_GATE + ' keeps all three obligations and full case NOT_RUN.'},
        'retention': {'outside_git_protected': ['full source PGDATA', 'full target PGDATA', 'backup_manifest', 'archive with pg_authid verifiers', 'source/target credentials and raw client output'],
            'export_only': ['source/packet/run/image/tool hashes', 'protected archive/manifest aggregate SHA256', 'byte/file/row counts', 'native/data/ledger/authority aggregate hashes', 'typed booleans', 'source-allowlisted diagnostics/stages'],
            'raw_backup_or_log_export': False, 'cleanup_exact_owned_only': True},
        'limits': ['Same pinned version and quiesced synthetic whole-cluster backup only; actual test restore still mandatory after pg_verifybackup.',
            'No PITR/continuous archive/incremental/cross-version/provider backup/retention/RPO/RTO/production-readiness claim.',
            'Logical pg_dump omits cluster roles/globals; a logical variant would require separately reviewed pg_dumpall globals/ownership/ACL restoration, not silently substitute for this physical proposal.',
            'Privacy U-08-08/U-08-09 and legal backup-expiry/final-shell requirements remain external; Ops backup receipt never becomes Privacy authorization.',
            'No app/worker permission, source contract, historical migration or client ledger modification; no target bootstrap or duplicate migration application.']}
    for probe, grant_count in zip(proposal['quarantined_simulation_probes'], [5, 5, 6, 7, 8]):
        probe['mandatory_after_closed_case'] = {'fixture_observers': 'All four exact mandatory_fixture_observers',
            'native_catalog_sha256': 'Equals source qualified native snapshot',
            'business_39_tables': 'Exact unchanged counts and per-table aggregate digests',
            'ledger': 'Exact source one-applied row and full aggregate digest',
            'authority': 'Exact unchanged role-attribute/membership/database-ACL hashes; zero temporary memberships/leaf CREATEfalse',
            'database_action_grant_count': grant_count, 'identity_authorization_count': 1,
            'identity_receipt_count': 3, 'identity_generation': 2, 'identity_revoked': False,
            'grant_retention': binding['retention']}
    proposal['identity_simulation']['observers'] = [
        {'sql': 'identity-' + phase + '-observe.sql', 'expected': {'authorization_count': 1, 'receipt_count': number, 'exact_current_link': True}}
        for phase, number in [('bootstrap', 1), ('revoke', 2), ('recover', 3)]]
    files['README.md'] = '''# RESTORE01 proposed physical synthetic rehearsal

Source-only NOT_RUN proposal; no executable coordinator is included. A separately
reviewed root operator/literal source, staging, target and private-artifact manifest
is mandatory before any creation. Existing P0C-RESTORE-01 remains NOT_RUN.

Create a real whole-cluster pg_basebackup with streamed WAL and SHA256 manifest;
verify it using the same pinned 17.11 tools. A protected archive contains role
password verifiers: keep it outside Git under owner-only protection, export only
aggregate hashes/counts, and destroy every exact owned copy/PGDATA volume at end.
Restore into an empty owned volume, verify again, then start under an admin-only
HBA. Never run initdb, bootstrap, application SQL or a migration on restored data.
Compare all42 table rows, catalog, ledger and role authority before any transition.

Rotate all six target credentials independently before restricted diagnostics.
Actual Identity SQL performs a clearly synthetic revoke/recover simulation before
any other restored service login. Five finite diagnostic probes use the existing
Customer SELECT and pending-work SELECT scopes only; no worker claim or serving.
Old-source tuple denial requires its exact still-unexpired grant and unchanged user
generation. An expired grant cannot be relabeled as proof of tuple invalidation.

The whole SERVICE-RESTORE vector and real Privacy generation/marker replay remain
blocked by P0F_PRIVACY_RESTORE_GENERATION_PORT. This proposal never fabricates a
Privacy marker or treats an empty Privacy inventory as proof. Every case, assertion
and proposed subprobe stays NOT_RUN; synthetic SQL does not qualify owner adapters.

The proposal JSON specifies exact stages, copies, expected state and controlled
deltas, HBA order, tools, protections, STOP rules and owned cleanup. Physical backup
is selected because it preserves cluster roles/globals; a logical variant needs a
separate globals/ownership design. No production restore or RPO/RTO is claimed.

Plain English: Make a real locked copy of the toy database. Put the copy in a new
locked box. Check that every piece came back. Change all keys before testing a few
doors. Keep the box closed because the real privacy repair work is still missing.
'''
    proposal['prepared_files_sha256'] = {name: sha(text.encode()) for name, text in files.items()}
    proposal['packet_digest_recipe'] = 'SHA256(UTF8 canonical JSON of source_files_sha256 and prepared_files_sha256); proposal.json excluded.'
    proposal['source_only_packet_sha256'] = sha(canonical({key: proposal[key] for key in ('source_files_sha256', 'prepared_files_sha256')}).encode())
    files['proposal.json'] = json.dumps(proposal, indent=2, allow_nan=False) + '\n'
    return files, proposal


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--prepare', action='store_true')
    args = parser.parse_args()
    files, proposal = build()
    if args.prepare:
        OUT.mkdir(parents=True, exist_ok=False)
        for name, value in files.items():
            with (OUT / name).open('x', encoding='utf8', newline='\n') as handle: handle.write(value)
    print(json.dumps({'status': 'PREPARED_NOT_RUN' if args.prepare else 'PLAN_ONLY_NOT_RUN', 'files': len(files),
        'case_id': CONTROL, 'packet_sha256': proposal['source_only_packet_sha256'], 'database_contacted': False}))


if __name__ == '__main__': main()
