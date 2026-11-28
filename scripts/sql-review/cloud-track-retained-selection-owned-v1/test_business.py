"""Offline checks of the real v4 packet, SQL projection and finite child."""

from copy import deepcopy
import itertools
import json
from pathlib import Path
from types import SimpleNamespace
import unittest
import uuid

from pglast import parse_sql

import business_driver as driver
import business_owner
import business_proof as proof
import cloud_child
import reviewed_fragments


class Model:
    def __init__(self, material, mutation=None):
        self.spec, _, _, tables = material
        self.mutation = mutation
        self.state = {name: {'count': 0, 'rows_sha256': proof.sha(b'[]')} for name in tables}
        self.serial = itertools.count(10)
        self.events = []
        self.grants = set()
        self.closed = True
        self.receipts = []

    def identity(self):
        return {'run_id': '10000000-0000-4000-8000-000000000001', 'container_id': 'c' * 64,
                'volume_created_at': '2026-11-28T00:00:00.123456789Z', 'source_commit': 'd' * 40,
                'source_tree': 'e' * 40, 'packet_sha256': 'f' * 64}

    def change(self, stage):
        for table, change in proof.STAGE_DELTAS[stage].items():
            row = self.state[table]
            row['count'] += change
            row['rows_sha256'] = proof.sha((table + str(next(self.serial))).encode())

    def fixture(self, label, text, restore, tables):
        assert self.closed and text.endswith('COMMIT;\n') and restore.endswith('COMMIT;\n')
        assert len(tables) == (2 if '/' in label else 3)
        self.events.append(label)
        self.change(label.split('/')[-1])

    def identity_bootstrap(self, source):
        assert 'synthetic-worker-fixture-authorization.v1' in source
        self.events.append('identity-bootstrap')
        self.change('identity-bootstrap')

    def new_lease(self, case):
        return ('a' if case == proof.CASES[0] else 'b') * 64

    def restricted(self, case, stage, grant, sql, records, lease, fence):
        assert self.closed and sql.rstrip().endswith('COMMIT;') and records
        assert fence == {'claim': 0, 'retained-effect': 1}.get(stage)
        assert (lease is not None) == (fence is not None)
        self.events.append(case + '/' + stage)
        self.before = deepcopy(self.state)
        self.change(stage)
        identity = str(uuid.UUID(int=next(self.serial), version=4))
        self.grants.add(identity)
        return {'actual_login': grant['database_login_role'], 'xid': str(next(self.serial)), 'grant_id': identity,
                'committed': True, 'client_closed': True, 'same_tuple': True, 'stage_records_exact': True}

    def projection(self, case, after):
        spec = self.spec['cases'][case]
        before = self.before if after else self.state
        header = {'database': proof.DATABASE, 'login': 'postgres', 'effective_login': 'postgres', 'read_only': True,
                  'server_version_num': 170011}
        work = {'id': spec['ids']['work'], 'state': 'leased', 'fence': 1, 'attempt_count': 1,
                'effect_pointer': spec['ids']['effect'] if after else None, 'exact_live_lease': True,
                'exact_transaction': True, 'stable_sha256': 'a' * 64}
        return {**header, 'work': work,
                'other_work': {'count': self.state[proof.WORK_TABLE]['count'] - 1, 'rows_sha256': 'b' * 64},
                'inserts': {table: {'own_count': int(after), 'unaffected': deepcopy(before[table])}
                            for table in (*proof.INSERTS, proof.GRANT_TABLE)}}

    def observe(self, label, sql):
        assert self.closed
        if label.endswith('-projection'):
            assert len(parse_sql(sql)) == 3 and 'REPEATABLE READ READ ONLY' in sql
            assert "to_jsonb(w)-ARRAY['effect_receipt_id','mutation_transaction_id']" in sql
            case, phase = label.split('/')
            raw = self.projection(case, phase.startswith('after'))
            if case == proof.CASES[1] and phase.startswith('after'):
                if self.mutation == 'other-work':
                    raw['other_work']['rows_sha256'] = 'a' * 64
                if self.mutation == 'own-work':
                    raw['work']['stable_sha256'] = 'b' * 64
                if self.mutation == 'prior-receipt':
                    raw['inserts']['platform.runtime_command_receipt']['unaffected']['rows_sha256'] = 'a' * 64
                if self.mutation == 'pointer':
                    raw['work']['effect_pointer'] = None
        elif label.split('/')[-1].removeprefix('final-') in driver.OBSERVER_FIELDS:
            case, phase = label.split('/')
            raw = self.spec['cases'][case][driver.OBSERVER_FIELDS[phase.removeprefix('final-')]]
        else:
            raw = deepcopy(self.state)
            if self.mutation == 'bool':
                raw['app.users']['count'] = False
            if self.mutation == 'float':
                raw['app.users']['count'] = 0.0
        identity = self.identity()
        if self.mutation == 'resource' and label == 'retained-paid-shape/after-projection':
            identity['container_id'] = '0' * 64
        return {'identity': identity, 'raw': json.dumps(raw), 'closed': self.mutation != 'unclosed'}

    def retain_observation(self, stage, validated, identity):
        assert identity == self.identity() and stage not in {row[0] for row in self.receipts}
        self.receipts.append((stage, proof.sha(proof.canonical(validated))))

    def retain_all_grants(self, observed):
        assert len(observed) == 8 and observed == self.grants


class Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.material = proof.load()

    def test_actual_material_and_deterministic_final_shape(self):
        _, files, pins, tables = self.material
        self.assertEqual((len(files), len(pins), len(tables)), (24, 24, 42))
        counts = proof.final_counts(tables)
        self.assertEqual((sum(counts.values()), sum(v > 0 for v in counts.values()), counts[proof.GRANT_TABLE]), (44, 18, 8))

    def test_projection_requires_closed_bind_types(self):
        case = self.material[0]['cases'][proof.CASES[0]]
        self.assertEqual(len(parse_sql(proof.projection_sql(case, None, 'a' * 64, '222'))), 3)
        for grant, token, xid in ((None, 'x' * 64, '222'), (None, 'a' * 64, "'; SELECT 1;"),
                                  ('broken', 'a' * 64, '222')):
            with self.assertRaisesRegex(proof.Held, 'TRACK_OBSERVER_BIND_TYPES'):
                proof.projection_sql(case, grant, token, xid)

    def test_exact_original_grant_fragments_and_closed_roles(self):
        core, session, protocol = reviewed_fragments.load(self.material, lambda *private: self.fail('unexpected credential'))
        self.assertTrue(callable(session.capture) and callable(core.finite_transaction) and callable(protocol['verdict']))
        created = str(uuid.UUID(int=100, version=4))
        issuer = {'login': 'wa_context_issuer', 'pid': '11', 'xid': '12', 'clock': '2026-11-28 00:00:00+00'}
        for case in self.material[0]['cases'].values():
            for template in case['grants'].values():
                role = template['database_login_role']
                backend = {'login': role, 'current_user': role, 'pid': '13', 'xid': '14'}
                result = core.grant_values(core.__new__(core), template, backend, issuer, created, 'a' * 64)
                self.assertEqual((len(result), result['backend_pid'], result['transaction_id']), (21, '13', "'14'"))
                with self.assertRaisesRegex(proof.Held, 'TRACK_EXACT_GRANT_HOLDER_LOGIN'):
                    core.grant_values(core.__new__(core), template, {**backend, 'login': 'postgres'}, issuer, created, 'a' * 64)

    def test_fixture_restore_permits_only_its_owner_trigger_flags(self):
        def trigger(table, name):
            return {'table_name': table, 'name': name, 'enabled': 'O', 'internal': False, 'body_sha256': 'a' * 64}

        targets = cloud_child.RESTORE_TARGETS['restore-prior-selection-owner-commits.sql']
        baseline = {'triggers': [trigger(table, name) for table in sorted(targets) for name in ('owner_commit', 'physical_guard')]}
        actual = deepcopy(baseline)
        actual['triggers'][0]['enabled'] = 'D'
        self.assertEqual(cloud_child.exact_fixture_restoration(baseline, actual, targets), {sorted(targets)[0]})
        actual['triggers'][1]['enabled'] = 'D'
        with self.assertRaisesRegex(proof.Held, 'TRACK_RESTORE_NATIVE_DRIFT'):
            cloud_child.exact_fixture_restoration(baseline, actual, targets)

    def test_existing_machinery_only_owner_cannot_admit_business(self):
        owner = SimpleNamespace(operation={'schema': 'workinants.cloud-f0-track-retained-base-owned-operation.v1'})
        with self.assertRaisesRegex(proof.Held, 'TRACK_CURRENT_COMMITTED_BUSINESS_PACKET_REQUIRED'):
            cloud_child.require_overlay_packet(owner, self.material)

    def test_inherited_multiline_artifact_and_terminal_hook_cannot_admit_base_packet(self):
        raw = b'{\n  "native_finite_cost": 100.0\n}\n'
        program = SimpleNamespace(OUT=Path('/modeled'), STATE={'origins': {'a.json': 'closed-origin'}}, unique_json=json.loads)
        program.closed_bytes = lambda path, *, origin: (raw, origin)
        opened, digest = business_owner.previous_artifact(program, 'a.json')
        self.assertEqual((opened, digest), ({'native_finite_cost': 100.0}, proof.sha(raw)))

        class OldOwner:
            operation = {'schema': 'workinants.cloud-f0-track-retained-base-owned-operation.v1'}
            program = SimpleNamespace()
            report = {}
            visited = False

            def track_terminal(self, *_):
                self.visited = True
                return {'existing_owned_machine_only': True}

        owner = business_owner.owner_adapter(OldOwner, self.material)()
        with self.assertRaisesRegex(proof.Held, 'TRACK_CURRENT_COMMITTED_BUSINESS_PACKET_REQUIRED'):
            owner.track_terminal(None, None, None)
        self.assertTrue(owner.visited)

    def test_exact_two_case_sequence(self):
        host = Model(self.material)
        value, state = driver.Driver(self.material, host).run()
        self.assertEqual(host.events, ['user-plan-fixtures', 'identity-bootstrap',
                                      *(case + '/' + step for case in proof.CASES for step in proof.STEPS)])
        self.assertEqual([row['case'] for row in value['results']], list(proof.CASES))
        self.assertEqual(value['assertion_promotions'], 0)
        self.assertEqual(value['expected_operational_commits'], 20)
        self.assertEqual(sum(row['count'] for row in state.values()), 44)
        self.assertEqual(len(host.receipts), driver.OBSERVATION_COUNT - 1)  # The owning postproof adds the last reading.

    def test_all_undeclared_row_and_identity_changes_stop(self):
        for mutation, error in {'other-work': 'TRACK_UNDECLARED_WORK_FIELD_OR_ROW_DRIFT',
                                'own-work': 'TRACK_UNDECLARED_WORK_FIELD_OR_ROW_DRIFT',
                                'prior-receipt': 'TRACK_UNDECLARED_EXISTING_ROW_DRIFT',
                                'pointer': 'TRACK_EXACT_WORK_RECEIPT',
                                'resource': 'TRACK_CROSS_RESOURCE_OBSERVER_DRIFT',
                                'unclosed': 'TRACK_OBSERVER_OPERATION_CLOSURE',
                                'bool': 'TRACK_STRICT_COUNT_HASH',
                                'float': 'TRACK_JSON_INTEGER_OR_BOOLEAN_REQUIRED'}.items():
            with self.subTest(mutation=mutation), self.assertRaisesRegex(proof.Held, error):
                driver.Driver(self.material, Model(self.material, mutation)).run()


if __name__ == '__main__':
    unittest.main()
