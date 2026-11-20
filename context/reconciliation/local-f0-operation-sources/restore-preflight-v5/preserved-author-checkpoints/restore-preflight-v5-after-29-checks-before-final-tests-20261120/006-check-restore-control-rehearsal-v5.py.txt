"""Offline source checks only; no Docker/database/SQL execution."""
from contextlib import redirect_stdout
from copy import deepcopy
import hashlib
import io
import json
from pathlib import Path
import runpy
import sys
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
M = runpy.run_path(str(ROOT / 'scripts/prepare-restore-control-rehearsal-v5.py'))


def archive_transport_projection(text, settings, rows):
    """Interpret the actual emitted SELECT expression, never execute SQL."""
    from pglast import ast, parse_sql
    statement=next(raw.stmt for raw in parse_sql(text) if isinstance(raw.stmt,ast.SelectStmt))
    args=statement.targetList[0].val.args
    expression=next(args[i+1] for i in range(0,len(args),2) if args[i].val.sval=='no_recovery_or_archive_transport')
    def evaluate(node,row=None):
        if isinstance(node,ast.A_Const):
            if node.isnull:return None
            return node.val.sval if isinstance(node.val,ast.String) else node.val.boolval if isinstance(node.val,ast.Boolean) else node.val.ival
        if isinstance(node,ast.TypeCast):return evaluate(node.arg,row)
        if isinstance(node,ast.ColumnRef):return row[node.fields[0].sval]
        if isinstance(node,ast.BoolExpr):
            values=[evaluate(arg,row) for arg in node.args]
            return all(value is True for value in values) if node.boolop.name=='AND_EXPR' else any(value is True for value in values) if node.boolop.name=='OR_EXPR' else not values[0]
        if isinstance(node,ast.A_Expr):
            assert node.name[0].sval=='='
            left,right=evaluate(node.lexpr,row),evaluate(node.rexpr,row)
            return None if left is None or right is None else left==right
        if isinstance(node,ast.NullTest):return (evaluate(node.arg,row) is not None) if node.nulltesttype.name=='IS_NOT_NULL' else evaluate(node.arg,row) is None
        if isinstance(node,ast.BooleanTest):
            assert node.booltesttype.name=='IS_FALSE'
            return evaluate(node.arg,row) is False
        if isinstance(node,ast.SubLink):
            query=node.subselect
            assert len(query.fromClause)==1 and query.fromClause[0].relname=='pg_settings'
            selected=[entry for entry in rows if evaluate(query.whereClause,entry) is True]
            return evaluate(query.targetList[0].val,selected)
        if isinstance(node,ast.CoalesceExpr):
            return next((value for arg in node.args if (value:=evaluate(arg,row)) is not None),None)
        if isinstance(node,ast.FuncCall):
            name=node.funcname[-1].sval
            if name=='current_setting':return settings[evaluate(node.args[0],row)]
            if name=='count':return len(row)
            if name=='bool_and':
                values=[evaluate(node.args[0],entry) for entry in row]
                return None if not values else all(value is True for value in values)
        raise AssertionError('UNMODELED_ARCHIVE_PROJECTION_AST')
    return evaluate(expression)


class RestoreProposalTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls): cls.files, cls.proposal = M['build']()

    def test_exact_existing_case_and_all_six_assertions_retained_not_run(self):
        actual = next(row for row in json.loads((ROOT / 'context/reconciliation/database-candidate-tests.json').read_bytes())['tests'] if row['id'] == 'P0C-RESTORE-01')
        self.assertEqual(self.proposal['source_control_definition'], actual)
        self.assertEqual(self.proposal['selected_control_ids'], ['P0C-RESTORE-01'])
        self.assertEqual(len(self.proposal['source_assertion_definition']['assertions']), 6)
        self.assertTrue(all(row['status'] == 'NOT_RUN' for row in self.proposal['source_assertion_definition']['assertions']))
        self.assertEqual(self.proposal['status'], 'NOT_RUN')

    def test_privacy_and_full_service_restore_remain_blocked(self):
        q = self.proposal['qualification']
        self.assertEqual(q['whole_case_status'], 'NOT_RUN')
        blocked = q['mandatory_blocked']
        self.assertEqual({row['id'] for row in blocked}, {'control.privacy_reapplication', 'vector.SERVICE-RESTORE.positive', 'vector.SERVICE-RESTORE.adversarial'})
        self.assertTrue(all(row['status'] == 'NOT_RUN' and row['dependency_ids'] == ['P0F_PRIVACY_RESTORE_GENERATION_PORT'] for row in blocked))
        self.assertFalse(self.proposal['quarantine']['service_activation'])
        self.assertFalse(q['production_restore_ready'])
        self.assertIn('PARTIAL', q['assertion_claim_limit']['control.restored_authority'])
        for value in self.files.values(): self.assertNotIn('INSERT INTO app.privacy_', value)

    def test_actual_physical_backup_and_two_verifications_preserve_wal_checks(self):
        b = self.proposal['backup_client']
        self.assertEqual(b['argv'][0], 'pg_basebackup')
        for value in ('--wal-method=stream', '--manifest-checksums=SHA256', '--format=plain', '--no-password', '--username=postgres', '--host=127.0.0.1'):
            self.assertIn(value, b['argv'])
        self.assertEqual(b['environment'], {'PGPASSFILE': '/run/wa-secrets/replication.pgpass'})
        self.assertEqual(b['password_file_fields_without_value'], ['127.0.0.1', '5432', 'replication', 'postgres'])
        self.assertTrue(b['no_new_replication_role_or_privilege'])
        self.assertEqual(self.proposal['backup_verify']['argv'], ['pg_verifybackup', '--exit-on-error', '--quiet', '/run/wa-restore-backup/base'])
        self.assertEqual(len(self.proposal['backup_verify']['twice']), 2)
        source_hba = self.files['source-backup.pg_hba.conf'].splitlines()
        self.assertIn('host replication postgres 127.0.0.1/32 scram-sha-256', source_hba)
        self.assertLess(source_hba.index('host replication postgres 127.0.0.1/32 scram-sha-256'), source_hba.index('host replication all 127.0.0.1/32 reject'))
        self.assertEqual([line for line in source_hba if line.endswith('scram-sha-256')],
            ['host all postgres 127.0.0.1/32 scram-sha-256', 'host replication postgres 127.0.0.1/32 scram-sha-256'])
        for role in M['ROLES'][1:]: self.assertNotIn(role, self.files['source-backup.pg_hba.conf'])
        for forbidden in ('--no-sync', '--no-manifest', '--no-verify-checksums', '--no-parse-wal', '--skip-checksums', '--ignore', '-R', '--write-recovery-conf'):
            self.assertNotIn(forbidden, b['argv'] + self.proposal['backup_verify']['argv'])

    def test_exact_hba_order_quarantines_before_and_after_diagnostics(self):
        for file, roles in [('quarantine-admin.pg_hba.conf', ['postgres']), ('quarantine-identity.pg_hba.conf', ['postgres', 'wa_identity_service_authority']), ('quarantine-diagnostic.pg_hba.conf', list(M['ROLES']))]:
            lines = self.files[file].splitlines()
            self.assertEqual(lines[1], 'local all all reject')
            self.assertEqual([line.split()[2] for line in lines if line.endswith('scram-sha-256')], roles)
            self.assertTrue(all(line.endswith(('reject', 'scram-sha-256')) for line in lines[1:]))
            self.assertIn('host replication all 127.0.0.1/32 reject', lines)
            self.assertNotIn(' trust', self.files[file]); self.assertNotIn(' md5', self.files[file])
        q = self.proposal['quarantine']
        self.assertEqual(q['network'], 'none'); self.assertEqual(q['host_ports'], [])
        self.assertIn('PGDATA/pg_hba.conf', q['server_hba_location'])
        self.assertIn('root0700', q['client_secret_location'])

    def test_exact_42_table_initial_counts_and_39_table_parity_scope(self):
        p = self.proposal
        self.assertEqual(len(p['tables']), 42); self.assertEqual(len(set(p['tables'])), 42)
        self.assertEqual(len(p['business_tables']), 39)
        self.assertEqual(set(p['tables']) - set(p['business_tables']), {'platform.database_action_grant', *M['PRIVATE_TABLES']})
        counts = p['source_and_initial_restore_counts']
        self.assertEqual(set(counts), set(p['tables']))
        self.assertEqual(counts['platform.database_action_grant'], 4)
        self.assertEqual(counts['platform.runtime_outbox_message'], 2)
        self.assertEqual(sum(counts.values()), 15)
        self.assertEqual(counts['app.privacy_restore_marker'], 0)
        self.assertEqual(counts['app.track_enrollment_receipt'], 0)

    def test_fingerprints_only_export_aggregate_hashes_counts_and_typed_booleans(self):
        for name in ('all-data-fingerprint.sql', 'business-data-fingerprint.sql', 'ledger-fingerprint.sql'):
            value = self.files[name]
            self.assertIn('READ ONLY', value); self.assertIn('sha256(convert_to(', value)
            self.assertIn('ORDER BY to_jsonb(x)::text COLLATE "C"', value)
            self.assertIn('rows_sha256', value)
        self.assertIn('Run ONLY after guarded source collector', self.files['ledger-fingerprint.sql'])
        a = self.files['authority-fingerprint.sql']
        self.assertEqual(a.count('rolpassword'), 1)
        self.assertIn("bool_and(rolpassword LIKE 'SCRAM-SHA-256$%')", a)
        self.assertNotIn('sha256(rolpassword', a)
        self.assertIn('temporary_memberships', a); self.assertIn('leaf_create_false', a)

    def test_actual_bootstrap_and_finalizer_keep_permanent_edge_out_of_temporary_count(self):
        from pglast import ast, parse_sql
        rows = []
        for raw in parse_sql((ROOT / 'review-output/foundation-bootstrap.review.sql').read_text()):
            stmt = raw.stmt
            if not isinstance(stmt, ast.GrantRoleStmt): continue
            options = {option.defname + '_option': option.arg.boolval for option in stmt.opt}
            for role in stmt.granted_roles:
                for member in stmt.grantee_roles:
                    rows.append({'member': member.rolename, 'roleid': role.priv_name, 'grantor': 'postgres', **options})
        self.assertEqual(len(rows), 4)
        for raw in parse_sql((ROOT / 'review-output/foundation-bootstrap-finalize.review.sql').read_text()):
            stmt = raw.stmt
            if isinstance(stmt, ast.GrantRoleStmt) and stmt.is_grant is False:
                revoked = {(member.rolename, role.priv_name) for member in stmt.grantee_roles for role in stmt.granted_roles}
                rows = [row for row in rows if (row['member'], row['roleid']) not in revoked]
        self.assertEqual(len(rows), 1)
        def evaluate(node, row):
            if isinstance(node, ast.TypeCast): return evaluate(node.arg, row)
            if isinstance(node, ast.A_Const):
                if isinstance(node.val, ast.String): return node.val.sval
                if isinstance(node.val, ast.Boolean): return node.val.boolval
            if isinstance(node, ast.ColumnRef): return row[node.fields[0].sval]
            if isinstance(node, ast.BoolExpr):
                values = [evaluate(arg, row) for arg in node.args]
                if node.boolop.name == 'AND_EXPR': return all(values)
                if node.boolop.name == 'OR_EXPR': return any(values)
                if node.boolop.name == 'NOT_EXPR': return not values[0]
            if isinstance(node, ast.A_Expr):
                if node.kind.name == 'AEXPR_IN': return evaluate(node.lexpr, row) in [evaluate(arg, row) for arg in node.rexpr]
                if node.name[0].sval == '=': return evaluate(node.lexpr, row) == evaluate(node.rexpr, row)
            raise AssertionError('Unrecognized membership projection AST')
        def member_queries(text):
            statement = next(raw.stmt for raw in parse_sql(text) if isinstance(raw.stmt, ast.SelectStmt))
            args = statement.targetList[0].val.args
            return {args[index].val.sval: args[index + 1].subselect for index in range(0, len(args), 2)
                    if isinstance(args[index + 1], ast.SubLink)}
        text = self.files['authority-fingerprint.sql']; queries = member_queries(text)
        count = sum(evaluate(queries['temporary_memberships'].whereClause, row) for row in rows)
        self.assertEqual(count, 0)
        permanent = [row for row in rows if evaluate(queries['permanent_migrator_edge'].whereClause, row)]
        self.assertEqual(len(permanent), 1)
        # Actual emitted bool_and projection must enforce every permanent option.
        conjunction = queries['permanent_migrator_edge'].targetList[0].val
        check = next(arg for arg in conjunction.args if isinstance(arg, ast.FuncCall) and arg.funcname[0].sval == 'bool_and').args[0]
        self.assertTrue(evaluate(check, permanent[0]))
        for field, value in [('admin_option', True), ('inherit_option', True), ('set_option', False), ('grantor', 'wa_context_issuer'), ('roleid', 'wa_customer_verifier')]:
            self.assertFalse(evaluate(check, {**permanent[0], field: value}))
        mutant = text.replace("member='wa_schema_owner'::regrole AND roleid IN", "member='wa_migrator'::regrole OR roleid IN")
        self.assertNotEqual(mutant, text)
        self.assertEqual(sum(evaluate(member_queries(mutant)['temporary_memberships'].whereClause, row) for row in rows), 1)

    def test_identity_recovery_uses_actual_receipt_timestamp_and_same_xid_source_contract(self):
        p = self.proposal['identity_simulation']
        self.assertEqual(p['receipt_counts'], [1, 2, 3])
        for action in ('revoke', 'recover'):
            value = self.files['identity-' + action + '.sql']
            self.assertIn('BEGIN;', value); self.assertTrue(value.rstrip().endswith('COMMIT;'))
            self.assertIn('revoked_at=r.revoked_at', value)
            self.assertNotIn('SET revoked_at=clock_timestamp()', value)
            self.assertNotIn('SET ROLE', value)
            observe = self.files['identity-' + action + '-observe.sql']
            self.assertIn('r.mutation_transaction_id=a.mutation_transaction_id', observe)
        self.assertIn(p['bootstrap_receipt'], self.files['identity-revoke.sql'])
        self.assertIn(p['revoke_receipt'], self.files['identity-recover.sql'])
        self.assertIn('SYNTHETIC', p['upstream_owner_adapter'])

    def test_all_grants_are_fresh_finite_and_keep_native_role_scope_boundaries(self):
        for grant in self.proposal['grants'].values():
            self.assertNotIn('id', grant)
            self.assertEqual(grant['status'], 'NOT_RUN')
            self.assertTrue(grant['allowed_fields']); self.assertTrue(all('*' not in field for field in grant['allowed_fields']))
            self.assertIn(grant['database_login_role'], ['wa_app_runtime', 'wa_worker'])
        worker = self.proposal['grants']['target-worker-current']
        self.assertEqual((worker['owner_module_id'], worker['action'], worker['purpose']), ('platform_integration_owner', 'runtime.claim_work.v1', 'work.claim'))
        self.assertEqual(worker['security_generation'], '2')
        self.assertTrue(all('/SELECT/' in field or '/revision/0' in field for field in worker['allowed_fields']))
        wrong = deepcopy(worker); wrong.update(template_id='target-worker-wrong-source-generation', source_generation='1')
        self.assertEqual(wrong, self.proposal['grants']['target-worker-wrong-source-generation'])

    def test_tuple_and_epoch_denials_are_not_expiry_or_fake_authority_passes(self):
        cases = self.proposal['quarantined_simulation_probes']
        self.assertEqual(len(cases), 5); self.assertTrue(all(row['status'] == 'NOT_RUN' for row in cases))
        old = next(row for row in cases if row['name'] == 'source-app-old-tuple')
        self.assertIsNone(old['grant_template']); self.assertIsNone(old['sql'])
        self.assertIn('unexpired', old['scope_limit']); self.assertIn('user gen0 unchanged', old['scope_limit'])
        self.assertEqual(old['expected']['psql_exit'], 3); self.assertFalse(old['expected']['acknowledgement'])
        self.assertTrue(old['expected']['source_body_and_raise_line_required'])
        self.assertEqual(next(row for row in cases if row['name'] == 'target-worker-current')['expected'], {'visible_exact_root': 1})
        self.assertEqual(cases[-1]['expected'], {'visible_exact_root': 0})
        self.assertIn('Transport-generation simulation', cases[-1]['scope_limit'])
        self.assertEqual([row['mandatory_after_closed_case']['database_action_grant_count'] for row in cases], [5, 5, 6, 7, 8])
        for case in cases:
            state = case['mandatory_after_closed_case']
            self.assertEqual((state['identity_authorization_count'], state['identity_receipt_count'], state['identity_generation']), (1, 3, 2))
            self.assertFalse(state['identity_revoked']); self.assertIn('All four', state['fixture_observers'])

    def test_source_seed_only_two_owner_commit_bypasses_and_exact_restoration(self):
        contract = self.proposal['fixture_trigger_contract']
        self.assertEqual(len(contract['bypassed']), 2); self.assertEqual(len(contract['expected_user_triggers']), 4)
        value = self.files['trusted-identity-fixtures.sql']
        self.assertEqual(value.count('DISABLE TRIGGER owner_commit'), 2)
        self.assertEqual(value.count('ENABLE TRIGGER owner_commit'), 2)
        self.assertNotIn('DISABLE TRIGGER ALL', value)
        self.assertTrue(contract['physical_guards_retained'])
        observers = self.proposal['mandatory_fixture_observers']
        self.assertEqual({row['file'] for row in observers}, {'source-customer-observe.sql', 'work-observe.sql', 'fixture-trigger-restore-observe.sql', 'grant-write-acl-observe.sql'})

    def test_stages_require_protected_artifact_empty_target_no_duplicate_install_and_owned_cleanup(self):
        stages = self.proposal['stages']
        self.assertTrue(all(row['status'] == 'NOT_RUN' for row in stages))
        byid = {row['id']: row['required'] for row in stages}
        self.assertIn('OUTSIDE Git', byid['05-artifact'])
        self.assertIn('empty target', byid['06-empty-target-copy'])
        self.assertIn('No initdb/bootstrap/applicationSQL/Prisma/ledger writes', byid['06-empty-target-copy'])
        self.assertIn('before any role rotation', byid['08-restore-parity'].lower())
        self.assertIn('rotate all SIX', byid['09-credential-rotation'])
        self.assertIn('source-old password', byid['11-finite-quarantined-diagnostics'])
        self.assertIn('service_activation=false', byid['12-requarantine'])
        self.assertIn('CreatedAt', byid['13-evidence-cleanup']); self.assertIn('absent', byid['13-evidence-cleanup'])
        self.assertFalse(self.proposal['retention']['raw_backup_or_log_export'])

    def test_all_sql_parses_without_any_execution(self):
        from pglast import parse_sql
        count = 0
        for name, value in self.files.items():
            if not name.endswith('.sql'): continue
            self.assertTrue(parse_sql(value), name); count += 1
        self.assertEqual(count, 20)

    def test_new_sql_mutations_are_limited_to_two_identity_transition_tables(self):
        from pglast import parse_sql
        for name, value in self.files.items():
            if not name.endswith('.sql') or name in M['COPIES']: continue
            statements = [item.stmt for item in parse_sql(value)]
            allowed = {'TransactionStmt', 'VariableSetStmt', 'SelectStmt'}
            if name in ('identity-revoke.sql', 'identity-recover.sql'):
                allowed |= {'InsertStmt', 'UpdateStmt'}
                mutations = [stmt for stmt in statements if type(stmt).__name__ in ('InsertStmt', 'UpdateStmt')]
                self.assertEqual([(stmt.relation.schemaname, stmt.relation.relname) for stmt in mutations],
                    [('platform_private', 'identity_service_receipt'), ('platform_private', 'identity_service_authorization')])
            self.assertTrue(all(type(stmt).__name__ in allowed for stmt in statements), name)

    def test_resource_contract_binds_only_owned_three_containers_two_volumes(self):
        resources = self.proposal['required_literal_resource_manifest']
        self.assertEqual(len(resources['container_names']), 3); self.assertEqual(len(resources['volume_names']), 2)
        self.assertEqual(resources['ipc_allowlist'], ['', 'private'])
        self.assertEqual(resources['network'], 'none'); self.assertEqual(resources['ports'], [])
        self.assertIn('CreatedAt', resources['inspect_required'])
        self.assertIn('no bootstrap bind', resources['target_mounts'])
        self.assertIn('archive RO', resources['staging_mounts'])
        self.assertIn('outside Git', resources['host_archive'])

    def test_preflight_refuses_unreviewed_external_recovery_and_preload_channels(self):
        value = self.files['backup-preflight.sql']
        for name in ('primary_conninfo', 'primary_slot_name', 'restore_command', 'archive_mode', 'archive_command', 'archive_library', 'synchronous_standby_names', 'shared_preload_libraries', 'session_preload_libraries', 'local_preload_libraries', 'pg_subscription', 'pg_foreign_server'):
            self.assertIn(name, value)
        self.assertIn("current_setting('archive_mode')='off'", value)
        self.assertIn('no_other_clients', value)

    def test_pg17_show_hook_and_raw_reset_model_depends_on_actual_projection(self):
        value=self.files['backup-preflight.sql']
        settings={key:'' for key in ('primary_conninfo','primary_slot_name','restore_command','archive_library','synchronous_standby_names')}
        settings.update(archive_mode='off',archive_command='(disabled)')
        row={'name':'archive_command','reset_val':'','vartype':'string','context':'sighup','pending_restart':False}
        self.assertIs(archive_transport_projection(value,settings,[row]),True)
        for field,bad in [('reset_val','PRIVATE_COMMAND_CANARY'),('reset_val',None),('vartype','integer'),('context','user'),('pending_restart',True),('pending_restart',None)]:
            self.assertIsNot(archive_transport_projection(value,settings,[{**row,field:bad}]),True)
        for rows in ([],[row,row],[{**row,'name':'other'}]):self.assertIsNot(archive_transport_projection(value,settings,rows),True)
        for key,bad in [('archive_mode','on'),('archive_mode','always'),('archive_command',''),('archive_command','PRIVATE_UNKNOWN_DISPLAY')]:
            self.assertIsNot(archive_transport_projection(value,{**settings,key:bad},[row]),True)
        # The old predicate rejects the source-correct off/empty-reset model.
        old=(ROOT/'review-output/restore-control-rehearsal/backup-preflight.sql').read_text()
        self.assertIs(archive_transport_projection(old,settings,[row]),False)
        self.assertNotIn('boot_val',value);self.assertNotIn('SELECT setting',value)

    def test_only_archive_predicate_changes_other_fifteen_and_twenty_four_leaves_exact(self):
        from pglast import ast,parse_sql
        def fields(text):
            statement=next(raw.stmt for raw in parse_sql(text) if isinstance(raw.stmt,ast.SelectStmt))
            args=statement.targetList[0].val.args
            return {args[i].val.sval:args[i+1] for i in range(0,len(args),2)}
        old=ROOT/'review-output/restore-control-rehearsal'
        before,after=fields((old/'backup-preflight.sql').read_text()),fields(self.files['backup-preflight.sql'])
        self.assertEqual(set(before),set(after));self.assertEqual(len(after),17)
        for name in before:
            if name!='no_recovery_or_archive_transport':self.assertEqual(before[name],after[name])
        for name in self.proposal['prepared_files_sha256']:
            if name!='backup-preflight.sql':self.assertEqual((old/name).read_bytes(),self.files[name].encode())

    def test_unchanged_context_source_sql_and_byte_reproduction(self):
        for name in M['COPIES']: self.assertEqual(self.files[name].encode(), (ROOT / M['CTX'] / name).read_bytes())
        files, proposal = M['build'](expected_sha256=self.proposal['source_files_sha256'])
        self.assertEqual(files, self.files); self.assertEqual(proposal, self.proposal)
        for name, digest in proposal['prepared_files_sha256'].items(): self.assertEqual(hashlib.sha256(files[name].encode()).hexdigest(), digest)
        if M['OUT'].exists():
            self.assertEqual({path.name for path in M['OUT'].iterdir()}, set(files))
            for name, value in files.items(): self.assertEqual((M['OUT'] / name).read_bytes(), value.encode())

    def test_bad_or_missing_approved_source_pin_is_rejected(self):
        for alter in ('missing', 'drift'):
            pins = deepcopy(self.proposal['source_files_sha256'])
            if alter == 'missing': pins.pop(M['APPLICATION'])
            else: pins[M['APPLICATION']] = '0' * 64
            with self.assertRaisesRegex(ValueError, 'approved source pins differ'): M['build'](expected_sha256=pins)

    def test_import_and_help_are_stdlib_only_and_never_run_build(self):
        path = ROOT / 'scripts/prepare-restore-control-rehearsal-v5.py'
        namespace = {'__file__': str(path), '__name__': 'restore_source_import_only'}
        exec(compile(path.read_bytes(), str(path), 'exec'), namespace)
        with patch.dict(namespace, build=lambda: (_ for _ in ()).throw(AssertionError('UNEXPECTED_BUILD'))):
            with patch.object(sys, 'argv', [str(path), '--help']), redirect_stdout(io.StringIO()), self.assertRaises(SystemExit) as found:
                namespace['main']()
            self.assertEqual(found.exception.code, 0)
        source = path.read_text(encoding='utf8')
        for forbidden in ('import subprocess', 'import runpy', 'import psycopg', 'import socket', 'exec(', 'eval('): self.assertNotIn(forbidden, source)


if __name__ == '__main__': unittest.main(verbosity=2)
