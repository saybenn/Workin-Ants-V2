"""Finite child for an independently admitted, still-open three-history owner."""

import re

import business_proof as proof


STAGE_RECORDS = {'source-customer': 'expected_source_records', 'schedule': 'expected_schedule_records',
                 'claim': 'expected_claim_records', 'retained-effect': 'expected_retained_records'}
OBSERVER_FIELDS = {'source-customer-observe': 'expected_source_observation',
                   'before-retained-observe': 'expected_before', 'after-retained-observe': 'expected_after'}
IDENTITY_KEYS = {'run_id', 'container_id', 'volume_created_at', 'source_commit', 'source_tree', 'packet_sha256'}
OBSERVATION_COUNT = 26


def check_identity(value):
    proof.need(type(value) is dict and set(value) == IDENTITY_KEYS and proof.canonical_uuid(value['run_id'])
               and all(type(value[k]) is str and proof.HASH.fullmatch(value[k]) for k in ('container_id', 'packet_sha256'))
               and all(type(value[k]) is str and re.fullmatch('[0-9a-f]{40}', value[k]) for k in ('source_commit', 'source_tree'))
               and type(value['volume_created_at']) is str and re.fullmatch('[0-9TZ:.+\\-]{20,64}', value['volume_created_at']),
               'TRACK_EXACT_BUSINESS_RESOURCE_CONTEXT')
    return dict(value)


class Driver:
    """Compare only typed observations delivered by the owner-bound coordinator."""

    def __init__(self, material, coordinator):
        self.spec, self.files, _, self.tables = material
        self.ops = coordinator
        self.identity = check_identity(self.ops.identity())
        self.current = None
        self.grants = set()
        self.results = []

    def exact_target(self):
        proof.exact(check_identity(self.ops.identity()), self.identity, 'TRACK_CROSS_RESOURCE_OBSERVER_DRIFT')

    def sql(self, leaf):
        return self.files[f'{leaf}.sql'].decode('utf-8')

    def observer(self, label, sql):
        self.exact_target()
        observed = self.ops.observe(label, sql)
        proof.need(type(observed) is dict and set(observed) == {'identity', 'raw', 'closed'} and observed['closed'] is True,
                   'TRACK_OBSERVER_OPERATION_CLOSURE')
        proof.exact(check_identity(observed['identity']), self.identity, 'TRACK_CROSS_RESOURCE_OBSERVER_DRIFT')
        return proof.unique_json(observed['raw'])

    def state(self, label):
        value = proof.full_state(self.observer(label, proof.read_only(self.sql('complete-state-observe'))), self.tables)
        self.ops.retain_observation(label, value, self.identity)
        return value

    def changed(self, step, label):
        value = self.state(label)
        proof.state_delta(self.current, value, self.tables, step)
        self.current = value

    def specific(self, case, name, *, final=False):
        expected = self.spec['cases'][case][OBSERVER_FIELDS[name]]
        label = f'{case}/final-{name}' if final else f'{case}/{name}'
        observed = self.observer(label, self.sql(f'{case}/{name}'))
        proof.exact(observed, expected, 'TRACK_EXACT_CASE_OBSERVER')
        self.ops.retain_observation(label, observed, self.identity)

    def restricted(self, case, step, lease=None, fence=None):
        self.exact_target()
        item = self.spec['cases'][case]
        grant = item['grants'][step]
        role, action, _ = proof.ROLE_GRANTS[step]
        proof.need(grant['database_login_role'] == role and grant['action'] == action, 'TRACK_EXACT_ACTION_SELECTOR')
        receipt = self.ops.restricted(case, step, grant, self.sql(f'{case}/{step}'), item[STAGE_RECORDS[step]], lease, fence)
        proof.need(type(receipt) is dict and set(receipt) == {'actual_login', 'xid', 'grant_id', 'committed', 'client_closed',
                   'same_tuple', 'stage_records_exact'} and receipt['actual_login'] == role
                   and all(receipt[name] is True for name in ('committed', 'client_closed', 'same_tuple', 'stage_records_exact'))
                   and type(receipt['xid']) is str and proof.XID.fullmatch(receipt['xid'])
                   and proof.canonical_uuid(receipt['grant_id']) and receipt['grant_id'] not in self.grants,
                   'TRACK_EXACT_RESTRICTED_RECEIPT')
        self.grants.add(receipt['grant_id'])
        return receipt

    def fixture(self, case=None):
        self.exact_target()
        step = 'prior-selection-fixture' if case else 'user-plan-fixtures'
        restore = 'restore-prior-selection-owner-commits' if case else 'restore-user-plan-owner-commits'
        targets = ('app.track_subscriptions', 'app.track_base_selection') if case else (
            'app.users', 'app.user_security_profiles', 'app.track_plans')
        leaf = f'{case}/{step}' if case else step
        self.ops.fixture(leaf, self.sql(leaf), self.sql(restore), targets)
        self.changed(step, leaf + '/full42')

    def one(self, case):
        item = self.spec['cases'][case]
        self.restricted(case, 'source-customer')
        self.specific(case, 'source-customer-observe')
        self.changed('source-customer', case + '/source-full42')
        self.fixture(case)
        self.restricted(case, 'schedule')
        self.changed('schedule', case + '/scheduled-full42')
        lease = self.ops.new_lease(case)
        proof.need(type(lease) is str and proof.HASH.fullmatch(lease), 'TRACK_PRIVATE_LEASE_SHAPE')
        lease_hash = proof.sha(bytes.fromhex(lease))
        claim = self.restricted(case, 'claim', lease, item['lease_claim_fence'])
        self.changed('claim', case + '/claimed-full42')
        self.specific(case, 'before-retained-observe')
        before = self.observer(case + '/before-projection', proof.projection_sql(item, None, lease_hash, claim['xid']))
        proof.validate_projection(before, item, after=False)
        self.ops.retain_observation(case + '/before-projection', before, self.identity)
        retained = self.restricted(case, 'retained-effect', lease, item['lease_effect_fence'])
        proof.need(retained['xid'] != claim['xid'], 'TRACK_NEW_EFFECT_TRANSACTION_REQUIRED')
        self.specific(case, 'after-retained-observe')
        after = self.observer(case + '/after-projection', proof.projection_sql(item, retained['grant_id'], lease_hash, retained['xid']))
        proof.validate_projection(after, item, after=True)
        self.ops.retain_observation(case + '/after-projection', after, self.identity)
        after_state = self.state(case + '/effect-full42')
        parity = proof.effect_pair(item, before, after, self.current, after_state, self.tables)
        self.current = after_state
        self.results.append({'case': case, 'result': 'already_enrolled', 'externally_paid_proof': False,
                             'before_and_after_clients_closed': True, 'complete_tables': 42, **parity})

    def run(self):
        self.current = self.state('pre-fixture-empty-full42')
        proof.need(all(row['count'] == 0 for row in self.current.values()), 'TRACK_FRESH_BUSINESS_DATA_REQUIRED')
        self.fixture()
        self.ops.identity_bootstrap(self.sql('identity-bootstrap'))
        self.changed('identity-bootstrap', 'identity-bootstrap/full42')
        for case in proof.CASES:
            self.one(case)
        for case in proof.CASES:
            self.specific(case, 'after-retained-observe', final=True)
        self.ops.retain_all_grants(self.grants)
        proof.need(len(self.grants) == 8 and {name: row['count'] for name, row in self.current.items()}
                   == proof.final_counts(self.tables), 'TRACK_COMPLETE_CASE_BUDGET')
        return {'identity': self.identity, 'status': 'FINITE_RETAINED_SELECTION_OBSERVED', 'results': self.results,
                'issued_grants': 8, 'expected_operational_commits': 20, 'complete_tables': 42,
                'final_full42_sha256': proof.sha(proof.canonical(self.current)), 'assertion_promotions': 0}, self.current
