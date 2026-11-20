"""Environment-free real-evidence admission and bounded status integration tests.

All mutations affect independent temporary copies. Process, socket, and dynamic
code boundaries are forbidden while the new qualifier runs. Legacy validators
are exact-row boundaries only in the aggregation test; they have their own suites.
"""
import ast
from contextlib import ExitStack, contextmanager
from copy import deepcopy
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import runpy
import shutil
import socket
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

HERE = Path(__file__).resolve().parent
DRAFT_ROOT = HERE.parent
EXISTING_ROOT = Path(os.environ.get('OWNER_LEASE_EXISTING_ROOT', str(DRAFT_ROOT)))
sys.path.insert(0, str(HERE))
sys.path.append(str(EXISTING_ROOT / 'scripts'))
import local_f0_owner_lease_evidence as adapter


@contextmanager
def no_external_boundaries():
    with ExitStack() as stack:
        for module, name in ((subprocess, 'Popen'), (subprocess, 'run'), (subprocess, 'call'),
             (subprocess, 'check_call'), (subprocess, 'check_output'), (os, 'system'),
             (os, 'popen'), (socket, 'socket'), (socket, 'create_connection')):
            stack.enter_context(patch.object(module, name, side_effect=AssertionError('FORBIDDEN_EXTERNAL_BOUNDARY')))
        stack.enter_context(patch('builtins.exec', side_effect=AssertionError('FORBIDDEN_DYNAMIC_SOURCE')))
        stack.enter_context(patch('builtins.eval', side_effect=AssertionError('FORBIDDEN_DYNAMIC_SOURCE')))
        yield


class OwnerLeaseEvidenceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.temporary = tempfile.TemporaryDirectory(prefix='owner-lease-adapter-test-')
        cls.root = Path(cls.temporary.name).resolve()
        cls.records = {}
        cls.raws = {}
        cls.components = {}
        cls.wrappers = {}
        cls.copy_pins = {}

        def copy(relative, wanted=None):
            source = DRAFT_ROOT / relative
            if not source.is_file():
                source = EXISTING_ROOT / relative
            data = source.read_bytes()
            if wanted is not None:
                assert hashlib.sha256(data).hexdigest() == wanted
            target = cls.root / relative
            target.parent.mkdir(parents=True, exist_ok=True)
            if not target.exists():
                target.write_bytes(data)
            else:
                assert target.read_bytes() == data
            cls.copy_pins[relative] = hashlib.sha256(data).hexdigest()
            return json.loads(data) if relative.endswith('.json') else data

        for relative, wanted in adapter.AUDIT_PINS.items():
            copy(relative, wanted)
        for family, cfg in adapter.FAMILIES.items():
            cls.records[family] = copy(cfg['derived_record'], cfg['derived_sha256'])
            raw = cls.raws[family] = copy(cfg['raw_record'], cfg['raw_record_sha256'])
            for relative, wanted in raw['assets_sha256'].items():
                copy(relative, wanted)
            manifest = json.loads((cls.root / cfg['asset_base'] / 'manifest/operation-manifest.json').read_bytes())
            for relative, wanted in manifest['packet_files_sha256'].items():
                copy(relative, wanted)
            cls.components[family] = json.loads((cls.root / cfg['asset_base'] / 'evidence' / cfg['component_relative']).read_bytes())
            cls.wrappers[family] = json.loads((cls.root / cfg['asset_base'] / 'evidence/run-evidence.json').read_bytes())
        cls.inventory = copy(adapter.INVENTORY, adapter.INVENTORY_SHA)
        for relative, wanted in cls.inventory['source_provenance']['files_sha256'].items():
            copy(relative, wanted)
        copy(adapter.SQL_PATH, adapter.SQL_SHA)
        copy('prisma/foundation/migrations/20261117000100_f0_local_initial/migration.sql', adapter.SQL_SHA)
        copy(adapter.ACCESS_PATH, adapter.ACCESS_SHA)
        cls.fixture = copy('review-output/owner-read-control-rehearsal/fixtures.json')
        cls.ledger = copy('context/reconciliation/local-f0-assertion-evidence.json')
        # Retain only the five old immutable execution records for the bounded
        # legacy dispatch contract. Their operational source is not executed.
        cls.before = json.loads((cls.root / adapter.ARCHIVE / 'preserved/assertion-evidence.before.json').read_bytes())
        for row in cls.before['assertions']:
            copy(row['evidence_path'], row['evidence_sha256'])
        cls.mapping = {family: json.loads((cls.root / cfg['mapping']).read_bytes()) for family, cfg in adapter.FAMILIES.items()}

    @classmethod
    def tearDownClass(cls):
        cls.temporary.cleanup()

    def selected(self, family='owner', status=None):
        return next((key, value) for key, value in adapter.CLOSED_CLAIMS.items()
                    if value[0] == family and (status is None or value[2] == status))

    def validate(self, key=None, value=None, execution=None, pointer=None):
        if key is None:
            key, value = self.selected()
        family, index, status = value
        with no_external_boundaries():
            return adapter.validate_claim(*key, status, self.records[family] if execution is None else execution,
                 self.root, json_pointer='/claims/' + str(index) if pointer is None else pointer)

    @contextmanager
    def changed_file(self, relative, raw):
        path = self.root / relative
        original = path.read_bytes()
        try:
            path.write_bytes(raw)
            yield
        finally:
            path.write_bytes(original)

    def test_all_exact28_claims_pass_with_all_external_boundaries_forbidden(self):
        self.assertEqual(len(adapter.CLOSED_CLAIMS), 28)
        for key, value in adapter.CLOSED_CLAIMS.items():
            with self.subTest(key=key):
                self.assertIs(self.validate(key, value), True)

    def test_eight_partial_caps_cannot_be_promoted(self):
        partial = [(key, value) for key, value in adapter.CLOSED_CLAIMS.items() if value[2] == 'PARTIAL']
        self.assertEqual(len(partial), 8)
        for key, (family, index, _) in partial:
            with self.subTest(key=key), self.assertRaisesRegex(adapter.EvidenceFailure, '^OWNER_LEASE_STATUS_CAP$'):
                self.validate(key, (family, index, 'PASS'))

    def test_unknown_claims_and_wrong_statuses_reject(self):
        key, value = self.selected()
        for unknown in [('P0C-UNKNOWN', key[1]), (key[0], 'control.invented'), ('P0C-TRACK-01', 'control.attach_recovery')]:
            with self.subTest(unknown=unknown), self.assertRaises(adapter.EvidenceFailure):
                self.validate(unknown, value)
        for status in ['FAILED', 'NOT_RUN', 'PASS_WITH_LIMITS', None, True, 1]:
            with self.subTest(status=status), self.assertRaises(adapter.EvidenceFailure):
                self.validate(key, (value[0], value[1], status))

    def test_claim_pointer_aliases_and_other_claims_reject(self):
        for pointer in ['/claims/00', '/claims/-1', '/claims/999', '/claims', '/claims/1/status', '/', 'claims/0', '/source_record']:
            with self.subTest(pointer=pointer), self.assertRaises(adapter.EvidenceFailure):
                self.validate(pointer=pointer)

    def test_derived_identity_and_claim_mutations_reject(self):
        key, value = self.selected()
        for field, replacement in [('run_id', 'wrong-run'), ('source_commit', '0'*40), ('source_tree', '0'*40),
             ('packet_sha256', '0'*64), ('actual_result', 'PASS'), ('raw_record_fields_invented', True)]:
            changed = deepcopy(self.records[value[0]])
            changed[field] = replacement
            with self.subTest(field=field), self.assertRaises(adapter.EvidenceFailure):
                self.validate(key, value, changed)
        changed = deepcopy(self.records[value[0]])
        changed['claims'][value[1]]['whole_case_promoted'] = True
        with self.assertRaises(adapter.EvidenceFailure):
            self.validate(key, value, changed)

    def test_source_record_asset_audit_requirement_sql_acl_and_packet_tamper_reject(self):
        cfg = adapter.FAMILIES['owner']
        manifest = json.loads((self.root / cfg['asset_base'] / 'manifest/operation-manifest.json').read_bytes())
        paths = [cfg['raw_record'], cfg['derived_record'], cfg['mapping'], adapter.ARCHIVE+'/owner-review.json',
                 cfg['asset_base']+'/evidence/'+cfg['component_relative'],
                 cfg['asset_base']+'/manifest/operation-manifest.json', adapter.INVENTORY, adapter.SQL_PATH, adapter.ACCESS_PATH,
                 next(path for path in manifest['packet_files_sha256'] if path.endswith('.py'))]
        for relative in paths:
            with self.subTest(relative=relative), self.changed_file(relative, (self.root/relative).read_bytes()+b'\nTAMPER'), self.assertRaises(adapter.EvidenceFailure):
                self.validate()

    def test_raw_reports_stay_original_without_builder_aliases(self):
        for family, raw in self.raws.items():
            self.assertNotIn('actual_result', raw)
            self.assertNotIn('packet_sha256', raw)
            self.assertEqual(self.records[family]['source_record']['sha256'], adapter.FAMILIES[family]['raw_record_sha256'])
            self.assertEqual(self.records[family]['packet_sha256'], raw['operation_packet_sha256'])

    def test_safe_path_and_strict_json_primitives(self):
        for relative in ['/absolute', '../escape', 'C:/outside', 'x\\outside', 'x//y', './x', 'x/../y']:
            with self.subTest(relative=relative), self.assertRaises(adapter.EvidenceFailure):
                adapter.read(self.root, relative, '0'*64)
        for raw in [b'{"a":1,"a":2}', b'{"a":NaN}', b'{"a":Infinity}']:
            with self.subTest(raw=raw), self.assertRaises(adapter.EvidenceFailure):
                adapter.document(raw)

    def test_safe_failures_do_not_include_canary_or_input_metadata(self):
        canary='PRIVATE_PASSWORD_HANDLE_STATEMENT_CANARY_9f2'
        with patch.object(Path, 'read_bytes', side_effect=OSError(canary)), self.assertRaises(adapter.EvidenceFailure) as result:
            self.validate()
        self.assertEqual(str(result.exception), 'OWNER_LEASE_EVIDENCE_REJECTED')
        self.assertNotIn(canary, str(result.exception))
        with self.assertRaises(adapter.EvidenceFailure) as result:
            self.validate((canary, canary), ('owner', 0, 'PASS'))
        self.assertEqual(str(result.exception), 'OWNER_LEASE_UNSUPPORTED_CLAIM')

    def test_module_has_pure_stdlib_import_and_no_dynamic_or_process_calls(self):
        tree = ast.parse((HERE/'local_f0_owner_lease_evidence.py').read_text(encoding='utf8'))
        imports = [node for node in ast.walk(tree) if isinstance(node, (ast.Import, ast.ImportFrom))]
        names = {alias.name for node in imports if isinstance(node, ast.Import) for alias in node.names}
        names |= {node.module for node in imports if isinstance(node, ast.ImportFrom)}
        self.assertEqual(names, {'hashlib', 'json', 'pathlib', 're', 'collections'})
        forbidden = {'exec', 'eval', 'compile', '__import__', 'system', 'Popen', 'run', 'connect', 'socket', 'write_bytes', 'write_text'}
        for node in ast.walk(tree):
            if isinstance(node, ast.Call):
                name = node.func.id if isinstance(node.func, ast.Name) else node.func.attr if isinstance(node.func, ast.Attribute) else ''
                self.assertNotIn(name, forbidden)

    def test_common_actual_run_source_cid_native_finalizer_and_cleanup_mutants_reject(self):
        for family, cfg in adapter.FAMILIES.items():
            def check(raw, wrapper, component):
                adapter._common(raw, wrapper, component, cfg)
            check(self.raws[family], self.wrappers[family], self.components[family])
            mutations = [lambda r,w,c: r.update(run_id='wrong'), lambda r,w,c: r.update(source_commit='0'*40),
                lambda r,w,c: c.update(container_id='0'*64), lambda r,w,c: c.update(packet_sha256='0'*64),
                lambda r,w,c: w['catalog_comparison']['check_counts'].update(PASS=29089.0),
                lambda r,w,c: next(iter(w['targets'].values()))['finalization_observation'].update(grantor='wa_migrator'),
                lambda r,w,c: w['backend_closures'][0].update(other_clients_zero=False),
                lambda r,w,c: w['cleanup_summary'].update(private_directory_absent=False),
                lambda r,w,c: c['authentication'][0].update(wrong_password_exit_code=True),
                lambda r,w,c: c['authentication_comparison'].update(client_loopback=False)]
            for index, mutate in enumerate(mutations):
                raw, wrapper, component = deepcopy((self.raws[family], self.wrappers[family], self.components[family]))
                mutate(raw, wrapper, component)
                with self.subTest(family=family, mutation=index), self.assertRaises(adapter.EvidenceFailure):
                    check(raw, wrapper, component)

    def test_owner_role_tuple_issuer_currentness_and_complete_state_mutants_reject(self):
        mutations = [lambda c:c['results'][0].update(actual_login='postgres'),
            lambda c:c['results'][0].update(operation_closed_before_observation=False),
            lambda c:c['results'][0].update(tables_observed=42),
            lambda c:c['results'][0]['counts'].update(foreign=1),
            lambda c:c['results'][-1].update(complete_state_sha256=c['baseline']['sha256']),
            lambda c:next(o for o in c['operations']if o['stage']=='BOUND_OPERATION').update(same_tuple_verified=False),
            lambda c:next(o for o in c['operations']if o['stage']=='SEPARATE_ISSUER_COMMIT').update(issuer_committed=False),
            lambda c:next(o for o in c['operations']if o['stage']=='IMMUTABLE_ISSUER_RETENTION').update(current_unexpired_match=False),
            lambda c:c.update(fixture_owner_bypass_restored=False)]
        for index, mutate in enumerate(mutations):
            component = deepcopy(self.components['owner']); mutate(component)
            with self.subTest(mutation=index), self.assertRaises(adapter.EvidenceFailure):
                adapter._owner(component, self.fixture)

    def test_owner_exact_diagnostics_and_before_after_markers_reject_mutations(self):
        for field, replacement in [('sqlstate','P0001'), ('source_frame_verified', False), ('body_line', 27),
             ('body_sha256', '0'*64), ('classification', 'unrelated-guard')]:
            component = deepcopy(self.components['owner'])
            result = next(row for row in component['results']if row['case']=='privacy-completion-gate')
            result['expected_guard'][field] = replacement
            with self.subTest(field=field), self.assertRaises(adapter.EvidenceFailure):
                adapter._owner(component, self.fixture)
        component = deepcopy(self.components['owner']);component['results'][0]['stage_markers']['after']=False
        with self.assertRaises(adapter.EvidenceFailure):adapter._owner(component, self.fixture)

    def test_lease_actual_role_closure_diagnostic_marker_and_restoration_mutants_reject(self):
        mutations = [lambda c:next(o for o in c['operations']if o['stage']=='ACTUAL_OPERATION').update(actual_login='postgres'),
            lambda c:next(o for o in c['operations']if o['stage']=='ACTUAL_OPERATION').update(operation_closed=False),
            lambda c:next(o for o in c['operations']if o['stage']=='ACTUAL_OPERATION')['outcome'].update(stage_markers=[]),
            lambda c:next(o for o in c['operations']if o['stage']=='ACTUAL_OPERATION'and o['outcome']['exit_code']==3)['outcome']['diagnostic'].update(source_body_line=999),
            lambda c:next(o for o in c['operations']if o['stage']=='SEPARATE_ISSUER_COMMIT').update(created_at_return_verified=False),
            lambda c:next(o for o in c['operations']if o['stage']=='TRIGGER_RESTORATION')['observation']['values'].update(no_project_user_trigger_disabled=False),
            lambda c:next(o for o in c['operations']if o['stage']=='APP_ISSUER_REVOCATION').update(protected_rows_disclosed=1),
            lambda c:next(o for o in c['operations']if o['stage']=='GLOBAL_CLIENT_CLOSURE').update(all_other_client_backends_absent=False)]
        adapter._lease(self.components['lease'])
        for index, mutate in enumerate(mutations):
            component = deepcopy(self.components['lease']);mutate(component)
            with self.subTest(mutation=index), self.assertRaises(adapter.EvidenceFailure):adapter._lease(component)

    def test_mapping_hashes_requirement_complete_snapshot_pointers_and_partial_caps_reject(self):
        for family, cfg in adapter.FAMILIES.items():
            baseline = self.records[family]
            for field, replacement in [('expected_assertion_sha256', '0'*64), ('complete_source_assertion_sha256', '0'*64),
                 ('source_case_results', [{'source_case_name':'wrong','json_pointer':'/results/0'}]),
                 ('source_operation_pointers', ['/operations/99999']), ('remaining_limits', [])]:
                changed = deepcopy(baseline);changed['claims'][0][field]=replacement
                with self.subTest(family=family,field=field), self.assertRaises(adapter.EvidenceFailure):
                    adapter._validate_claims(changed,self.mapping[family],family,cfg,self.inventory,self.components[family])
            changed=deepcopy(baseline);next(row for row in changed['claims']if row['status']=='PARTIAL')['status']='PASS'
            with self.assertRaises(adapter.EvidenceFailure):
                adapter._validate_claims(changed,self.mapping[family],family,cfg,self.inventory,self.components[family])

    def test_ledger_only21_additions_seven_corroborations_and_frozen_baseline(self):
        old=self.before['assertions'];new=self.ledger['assertions']
        self.assertEqual(len(new)-len(old),21)
        self.assertEqual(new[:len(old)],old)
        self.assertEqual(sum(row['status']=='PASS'for row in new[len(old):]),16)
        self.assertEqual(sum(row['status']=='PARTIAL'for row in new[len(old):]),5)
        keys={(row['case_id'],row['assertion_id'])for row in old}
        self.assertEqual(len(keys&set(adapter.CLOSED_CLAIMS)),7)
        self.assertEqual(len({(row['case_id'],row['assertion_id'])for row in new}),len(new))

    def test_real_builder_dispatch_and_mandatory_aggregation(self):
        namespace=runpy.run_path(str(HERE/'prepare-local-f0-status.py'));build=namespace['build'];g=build.__globals__
        old={(row['case_id'],row['assertion_id']):row for row in self.before['assertions']}
        old_calls=[];new_calls=[]
        def legacy(case,assertion,status,execution,root,json_pointer=None):
            row=old[(case,assertion)]
            self.assertEqual(status,row['status'])
            self.assertEqual(execution['run_id'],row['run_id'])
            self.assertEqual(execution['source_commit'],row['source_commit'])
            self.assertEqual(execution['source_tree'],row['source_tree'])
            self.assertEqual(execution['packet_sha256'],row['packet_sha256'])
            if json_pointer is not None:self.assertEqual(json_pointer,row['json_pointer'])
            old_calls.append((case,assertion));return True
        def current(*args,**kwargs):
            new_calls.append((args[0],args[1],args[2]));return adapter.validate_claim(*args,**kwargs)
        with patch.dict(g, ROOT=self.root, REC=self.root/'context/reconciliation', validate_claim=legacy,
             validate_catalog_claim=legacy,validate_restricted_claim=legacy,validate_native_prefix_claim=legacy,
             validate_owner_lease_claim=current), no_external_boundaries():
            result=build()
        self.assertEqual(len(new_calls),21)
        self.assertEqual(len(old_calls),len(old)-len(g['SMALL_PASSES']))
        self.assertEqual(result['assertion_status_counts'],dict(PASS=227,PARTIAL=32,FAILED=0,DEPENDENCY_BLOCKED=32,NOT_RUN=736,UNRESOLVED_SOURCE=7))
        self.assertEqual({case['id']for case in result['cases']if case['status']=='PASS'},
             {'P0C-UNIQUE-01','P0C-TABLE-DatabaseActionGrant-ALLOW',
              'P0C-TABLE-ProfessionalProfile-ALLOW','P0C-TABLE-CandidateProfile-ALLOW'})
        # Each newly complete READ-only case has exactly one mandatory frozen
        # SELECT assertion. These results follow the existing aggregation rule.
        for case_id in ('P0C-TABLE-ProfessionalProfile-ALLOW','P0C-TABLE-CandidateProfile-ALLOW'):
            source=next(case for case in self.inventory['cases']if case['id']==case_id)
            mandatory=[item for item in source['assertions']if item['mandatory_for_case']]
            self.assertEqual(len(mandatory),1)
            self.assertEqual(mandatory[0]['id'],'positive.wa_app_runtime.select')
        self.assertEqual(result['database_posture'],'D');self.assertEqual(result['Brain_acceptance'],'PENDING')
        self.assertEqual(result['selected_cases'],94)
        self.assertEqual(sum(result['assertion_status_counts'].values()),1034)
        self.assertFalse(any(case['status']=='PASS'and any(word in case['id']for word in ('TRACK','CTX','CONSENT','Privacy'))for case in result['cases']))
        self.__class__.aggregation_result={key:result[key]for key in ('assertion_status_counts','case_status_counts','database_posture','Brain_acceptance','selected_cases')}


if __name__=='__main__':
    unittest.main(verbosity=2)
