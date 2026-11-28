"""Offline integration of the draft packet, acceptance gate and evidence barrier."""

from copy import deepcopy
import os
from pathlib import Path
from tempfile import TemporaryDirectory
from types import SimpleNamespace
import unittest
from unittest import mock

import business_owner as business
import business_proof as proof
import owned_operation as owned
import prior_machinery as prior
import reviewed_fragments as fragments


ARCHIVE = Path(os.environ.get('WORKINANTS_CLOUD_PRISMA_TOOLS_ARCHIVE', ''))
RUN_ID = '90000000-0000-4000-8000-000000000001'


def modeled_machinery():
    """In-memory shape test. Does not create an admission file or operate a target."""
    cid = 'a' * 64
    birth = '2026-11-28T00:01:02Z'
    labels = {'workinants.rehearsal.run': RUN_ID, 'workinants.rehearsal': 'p0c-cloud-f0-track-retained-base-v1'}
    source = {'commit': 'b' * 40, 'tree': 'c' * 40}
    target = {'container_name': 'modeled-track', 'volume_name': 'modeled-track-data', 'network': 'none', 'labels': labels}
    order = [{'sha256': digest} for digest in proof.MIGRATION_SHA]
    daemon, image = {'model_daemon': True}, {'model_image': True}
    plan = {'schema': prior.PLAN_SCHEMA, 'source': source, 'target': target, 'run_id': RUN_ID, 'posture': 'D',
            'native_expected_sha256': proof.CATALOG_SHA, 'candidate_adoption': False, 'business_tests_executed': False,
            'candidate_commit': prior.CANDIDATE_COMMIT, 'ledger_expected': order, 'source_pins': owned.ACCEPTANCE_PINS,
            'daemon': daemon, 'image': image}
    packet = proof.sha(proof.canonical(plan))
    container = {'run_id': RUN_ID, 'name': target['container_name'], 'id': cid, 'labels': labels}
    volume = {'run_id': RUN_ID, 'name': target['volume_name'], 'created_at': birth, 'labels': labels}
    native = {phase: {'native_sha256': 'd' * 64, 'applied_rows': 3, 'oracle_expressions': 416, 'ledger_checks': 22,
                      'catalog_check_counts': {'PASS': 29089}} for phase in ('initial', 'noop')}
    authority = {phase: {'phase': phase, 'exact_role_options': True, 'leaf_create_absent': True,
                         'candidate_function_bodies_verified': phase != 'PRE_DEPLOY'}
                 for phase in ('PRE_DEPLOY', 'PRE_FINALIZATION', 'POST_FINALIZATION', 'POST_NOOP')}
    result = {'schema': prior.RESULT_SCHEMA, 'run_id': RUN_ID, 'status': prior.PASS, 'container_id': cid,
              'source_commit': source['commit'], 'source_tree': source['tree'], 'packet_sha256': packet,
              'Posture': 'D', 'source_expected_sha256': proof.CATALOG_SHA, 'native': native, 'business_assertions_qualified': 0,
              'original_grantor_finalized': True, 'full8_noop': {'all_eight_columns_compared': True, 'history_count': 3,
                  'status': 'PASS_EXACT_THREE_ROW_HASH_PRESERVATION_ONLY'}, 'track': {'authority': authority,
                  'pre_finalization': {'applied_rows': 3, 'ledger_checks': 22}, 'business_cases': 'NOT_RUN',
                  'finalization_and_noop_preserved_all_eight_ledger_columns': True, 'three_applied_historical_order': order}}
    report = {'schema': prior.RUN_SCHEMA, 'run_id': RUN_ID, 'status': prior.PASS, 'approved_packet_sha256': packet,
              'approved_commit': source['commit'], 'approved_tree': source['tree'], 'actual_daemon': daemon, 'image': image,
              'unexpected': [], 'native_results': native, 'track_authority': authority, 'transport': {'unknown_closure': False},
              'targets': {container['name']: {'container_id': cid, 'volume_created_at': birth, 'labels': labels, 'finalization': 'PASS'}},
              'cleanup': 'EXACT_CONTAINER_VOLUME_AND_PRIVATE_SECRET_ABSENT', 'cleanup_full_container_identity_absent': True,
              'cleanup_steps': dict.fromkeys(('docker_resources', 'local_client', 'private_files'), 'CONFIRMED'),
              'immutable_source_postcheck': 'PASS', 'final_original_references_verified': True,
              'migration_results': [{'run_id': RUN_ID, 'container_id': cid, 'packet_sha256': packet, 'exit_code': 0,
                  'status': 'CLI_COMPLETED_REQUIRES_INDEPENDENT_LEDGER_CATALOG_CHECKS', 'track_retained_sql_sha256': proof.MIGRATION_SHA[-1],
                  'operation': operation, 'no_pending_message_observed': index == 2}
                 for index, operation in enumerate(('deploy', 'status', 'deploy'))]}
    exit_row = {'run_id': RUN_ID, 'method': 'ACTUAL_OPERATING_PROCESS_EXIT', 'exit_code': 0, 'stdout_status': prior.PASS,
                'evidence_complete': True, 'source_commit': source['commit'], 'outer_evidence_sha256': proof.sha(proof.canonical(report)),
                'first_reported_failure': None, 'packet_sha256': packet}
    values = dict(zip(prior.REQUIRED_FILES, (plan, exit_row, container, volume, report, result), strict=False))
    return values


def model_acceptance(values):
    recorded = deepcopy(values)
    file_hashes = {name: proof.sha(proof.canonical(value)) for name, value in values.items()}
    recorded['independent-closure.json'] = {'schema': 'MODELED_ONLY', 'run_id': RUN_ID, 'reviewer': 'reviewer-model',
        'decision': prior.CLOSURE_DECISION, 'daemon': values['operation.json']['daemon'], 'image': values['operation.json']['image'],
        'created_container': values['created-container.json'], 'created_volume': values['created-volume.json'],
        'cleanup_verified': dict.fromkeys(prior.CLEANUP, True), 'file_sha256': file_hashes}
    files = {name: proof.canonical(value) for name, value in recorded.items()}
    source = values['operation.json']['source']
    accept = {'schema': prior.SCHEMA, 'decision': prior.DECISION, 'posture': 'D', 'assertion_promotions': 0,
              'business_cases': 'NOT_RUN', 'run_id': RUN_ID, 'container_id': values['created-container.json']['id'],
              'volume_created_at': values['created-volume.json']['created_at'], 'source_commit': source['commit'],
              'source_tree': source['tree'], 'candidate_commit': prior.CANDIDATE_COMMIT, 'candidate_catalog_sha256': proof.CATALOG_SHA,
              'ordered_migration_sha256': list(proof.MIGRATION_SHA), 'operator_exit_code': 0, 'reviewer': 'reviewer-model',
              'source_author': 'source-author-model', 'files_sha256': {name: proof.sha(raw) for name, raw in files.items()}}
    return accept, files


class Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.material = proof.load()

    def test_prior_actual_shape_correlates_and_refuses_stop_or_older_source(self):
        files = modeled_machinery()
        accepted, raw = model_acceptance(files)
        self.assertEqual(prior.validate(accepted, raw, corrected_source_pins=owned.ACCEPTANCE_PINS)['run_id'], RUN_ID)
        failed = deepcopy(files)
        failed['operation-exit.json']['exit_code'] = 1
        with self.assertRaisesRegex(proof.Held, 'TRACK_PRIOR_ACTUAL_EXIT_AND_RESULT'):
            prior.validate(*model_acceptance(failed), corrected_source_pins=owned.ACCEPTANCE_PINS)
        older = deepcopy(files)
        older['operation.json']['source_pins'][f'{owned.TRACK}/operation.py'] = '0' * 64
        with self.assertRaisesRegex(proof.Held, 'TRACK_PRIOR_CORRECTED_RUN_SOURCE_AND_POSTURE'):
            prior.validate(*model_acceptance(older), corrected_source_pins=owned.ACCEPTANCE_PINS)
        bad_identity = {**accepted, 'reviewer': accepted['source_author']}
        with self.assertRaisesRegex(proof.Held, 'TRACK_INDEPENDENT_ACTUAL_ACCEPTANCE_SHAPE'):
            prior.validate(bad_identity, raw, corrected_source_pins=owned.ACCEPTANCE_PINS)

    def test_committed_preparation_requires_prior_before_any_compilation(self):
        with mock.patch.object(owned, 'mechanism', side_effect=AssertionError('admission progressed')):
            with self.assertRaisesRegex(proof.Held, 'TRACK_PRIOR_INDEPENDENT_MACHINERY_ACCEPTANCE_REQUIRED'):
                owned.compose(ARCHIVE, RUN_ID)
            with self.assertRaisesRegex(proof.Held, 'TRACK_PRIOR_PATH_AND_SHA_REQUIRED_TOGETHER'):
                owned.compose(ARCHIVE, RUN_ID, draft=True, prior_sha='a' * 64)
            with self.assertRaisesRegex(proof.Held, 'EXPLICIT_TRACK_BUSINESS_OPERATION_REQUIRED'):
                owned.execute(Path('/somewhere'), explicitly_reviewed=False)

    def test_actual_draft_roundtrip_with_closed_recipe_tree_and_no_execution(self):
        canonical_track = owned.mechanism()
        with TemporaryDirectory() as scratch, mock.patch.object(canonical_track.P, 'SCRATCH', Path(scratch)), \
             mock.patch.object(owned, 'mechanism', return_value=canonical_track), mock.patch.object(owned, 'owning_class') as construct:
            path, plan = owned.prepare(ARCHIVE, draft=True)
            composition, raw = owned.read_closed(path, draft=True)
            self.assertEqual(composition[0][1], plan)
            self.assertEqual((plan['status'], plan['source'], len(composition[-1]), len(composition[0][6])), (owned.DRAFT, None, 27, 9))
            self.assertIsNone(plan['track_business']['prior_closed_track_run'])
            self.assertEqual(raw, canonical_track.S.encode(plan))
            with self.assertRaisesRegex(proof.Held, 'TRACK_BUSINESS_COMMITTED_PACKET_REQUIRED'):
                owned.execute(path, explicitly_reviewed=True)
            construct.assert_not_called()
            codes = owned.scoped_codes(composition[0][2])
            self.assertIn('TRACK_UNDECLARED_WORK_FIELD_OR_ROW_DRIFT', codes)
            self.assertIn('TRACK_CHILD_EVIDENCE_WRITE_UNCONFIRMED', codes)
            self.assertNotIn('MODELED_PRIMARY', codes)
            modeled = {**plan, 'source': {'commit': 'b' * 40, 'tree': 'c' * 40}}
            modeled_raw = canonical_track.S.encode(modeled)
            bind = owned.bindings(canonical_track, modeled, modeled_raw)
            source = {'schema': owned.SOURCE_REVIEW, 'decision': 'APPROVE', 'reviewer': 'modeled-peer',
                      'source_author': 'modeled-author', 'bindings': bind, 'scopes': owned.SOURCE_SCOPES}
            source_raw = canonical_track.S.encode(source)
            literal = {**source, 'schema': owned.LITERAL_REVIEW, 'scopes': owned.LITERAL_SCOPES,
                       'bindings': {**bind, 'source_review_sha256': proof.sha(source_raw)}}
            for leaf, value in (('source-review.json', source_raw), ('literal-review.json', canonical_track.S.encode(literal))):
                canonical_track.P.write_new(path.parent / leaf, value)
            verified = owned.exact_reviews(canonical_track, path.parent, modeled, modeled_raw)
            self.assertEqual(verified['source'], proof.sha(source_raw))
            with self.assertRaisesRegex(canonical_track.S.Held, 'FRESH_TYPED_REVIEW_REQUIRED'):
                owned.exact_reviews(canonical_track, path.parent, modeled, modeled_raw + b'\n')
            canonical_track.P.write_new(path.parent / 'attempt.json', b'modeled prior receipt\n')
            with mock.patch.object(owned, 'read_closed', return_value=(composition, raw)), \
                 mock.patch.object(owned, 'exact_reviews', return_value=verified):
                with self.assertRaisesRegex(proof.Held, 'TRACK_FRESH_BUSINESS_ATTEMPT_DIRECTORY_REQUIRED'):
                    owned.execute(path, explicitly_reviewed=True)
            construct.assert_not_called()
            canonical_track.P.write_new(path.parent / 'business-recipes' / 'extra', b'modeled drift')
            with self.assertRaisesRegex(canonical_track.S.Held, 'TRACK_OWNED_TREE_READBACK'):
                owned.read_closed(path, draft=True)

    def test_both_mutating_context_methods_stop_before_session_when_evidence_fails(self):
        core, _, _ = fragments.load(self.material, lambda *_: None)
        for selector in ('commit', 'issue'):
            program = SimpleNamespace(best_effort_save=mock.Mock(return_value=False))
            owner = SimpleNamespace(program=program, report={})
            state = business.Evidence(owner, {'modeled': True})
            model = core.__new__(core)
            model.evidence = state
            model.session = mock.Mock(side_effect=AssertionError('opened before persistence'))
            model.sequence = 0
            model.packet = {'finite_caps': {'grant_instances_max': 8}}
            args = ('postgres', 'BEGIN; COMMIT;', 'modeled-fixture') if selector == 'commit' else ({}, {})
            with self.assertRaisesRegex(proof.Held, 'TRACK_CHILD_EVIDENCE_WRITE_UNCONFIRMED'):
                getattr(model, selector)(*args)
            model.session.assert_not_called()
            program.best_effort_save.return_value = True
            with self.assertRaisesRegex(proof.Held, 'TRACK_CHILD_EVIDENCE_WRITE_UNCONFIRMED'):
                state.save()

    def test_context_first_failure_survives_close_failure(self):
        core, _, _ = fragments.load(self.material, lambda *_: None)
        owner = SimpleNamespace(program=SimpleNamespace(best_effort_save=lambda: True, _safe_failure_code=lambda code: code), report={})
        model = core.__new__(core)
        model.evidence = business.Evidence(owner, {'modeled': True})
        child = SimpleNamespace(begin=mock.Mock(side_effect=proof.Held('MODELED_PRIMARY')),
                                close=mock.Mock(side_effect=proof.Held('MODELED_SECONDARY')), closed=False)
        model.session = lambda _role: child
        with self.assertRaisesRegex(proof.Held, 'MODELED_PRIMARY'):
            model.commit('postgres', 'BEGIN; COMMIT;', 'modeled-primary')
        self.assertEqual(child.close.call_count, 1)
        self.assertEqual(model.evidence.value['first_failure'], 'MODELED_PRIMARY')


if __name__ == '__main__':
    unittest.main()
