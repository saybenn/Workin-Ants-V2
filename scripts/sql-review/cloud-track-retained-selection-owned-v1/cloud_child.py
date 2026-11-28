"""Owner-bound Cloud child transport. The held package has no operation entry point."""

from copy import deepcopy
import re
import secrets
import subprocess

import business_driver as driver
import business_proof as proof
import reviewed_fragments as fragments


OWNER_SCOPE = 'workinants.cloud-f0-track-retained-selection-owned-operation.v1'
NATIVE = 'scripts/sql-review/collect_native_catalog.sql'
INITIAL = 'review-output/foundation-application.review.sql'
RECEIPTS = {'manifest_sha256': proof.MANIFEST_SHA, 'proof_sha256': proof.PROOF_SHA, 'source_review_sha256': proof.REVIEW_SHA}
RESTORE_TARGETS = {
    'restore-user-plan-owner-commits.sql': {'app.users', 'app.user_security_profiles', 'app.track_plans'},
    'restore-prior-selection-owner-commits.sql': {'app.track_subscriptions', 'app.track_base_selection'},
}


def exact_fixture_restoration(baseline, live, targets):
    """Identify only the reviewed owner trigger flags on an otherwise exact native snapshot."""
    disabled = set()
    normalized = deepcopy(live)
    original = {}
    current = {}
    for catalog, selected in ((baseline, original), (normalized, current)):
        for row in catalog['triggers']:
            if row['table_name'] in targets and row['name'] == 'owner_commit':
                proof.need(row['table_name'] not in selected, 'TRACK_RESTORE_TRIGGER_IDENTITY')
                selected[row['table_name']] = row
    proof.need(set(original) == set(current) == set(targets), 'TRACK_RESTORE_TRIGGER_IDENTITY')
    for target in targets:
        expected, actual = original[target], current[target]
        proof.need(expected['internal'] is False and actual['internal'] is False and expected['enabled'] == 'O'
                   and actual['enabled'] in ('O', 'D'), 'TRACK_RESTORE_TRIGGER_ENABLED_DOMAIN')
        if actual['enabled'] == 'D':
            disabled.add(target)
            actual['enabled'] = 'O'
    proof.exact(normalized, baseline, 'TRACK_RESTORE_NATIVE_DRIFT')
    return disabled


def read_identity(owner):
    state = owner.observed_target()
    plan = owner.operation
    proof.need(state['container_id'] == owner.resources.cid and state['volume_created_at'] == owner.resources.volume_birth,
               'TRACK_ACTIVE_OWNED_IDENTITY')
    return driver.check_identity({'run_id': plan['run_id'], 'container_id': state['container_id'],
        'volume_created_at': state['volume_created_at'], 'source_commit': plan['source']['commit'],
        'source_tree': plan['source']['tree'], 'packet_sha256': proof.sha(owner.raw)})


def require_overlay_packet(owner, material):
    """Recognize only the prospective packet already verified by its owning entry point."""
    _, files, sources, _ = material
    plan = owner.operation
    proof.need(plan['schema'] == OWNER_SCOPE and plan['posture'] == 'D' and plan['source'] is not None
               and plan['native_expected_sha256'] == proof.CATALOG_SHA
               and [row['sha256'] for row in plan['ledger_expected']] == list(proof.MIGRATION_SHA),
               'TRACK_CURRENT_COMMITTED_BUSINESS_PACKET_REQUIRED')
    scope = plan['track_business']
    proof.need(scope['recipe'] == RECEIPTS and scope['leaves_sha256'] == {path: proof.sha(raw) for path, raw in files.items()}
               and type(scope['prior_independent_machinery_acceptance_sha256']) is str
               and proof.HASH.fullmatch(scope['prior_independent_machinery_acceptance_sha256'])
               and all(plan['source_pins'].get(name) == proof.sha(raw) for name, raw in sources.items())
               and all(type(owner.reviews.get(key)) is str and proof.HASH.fullmatch(owner.reviews[key]) for key in ('source', 'literal'))
               and not owner.transport.unknown and owner.program.STATE.get('three_applied_verified') is True
               and owner.program.STATE.get('finalization_verified') is True, 'TRACK_CURRENT_REVIEW_AND_MACHINERY_REQUIRED')


def coordinator(owner, material, native, evidence):
    """Compose exact context and Worker fragments after the owning entry admits a new packet."""
    require_overlay_packet(owner, material)
    spec, files, sources, _ = material
    p = owner.program
    Core, Session, protocol = fragments.load(material, lambda *items: p.all_secrets.extend(items))

    class Coordinator(Core):
        def __init__(self):
            self.native, self.evidence, self.protocol = native, evidence, protocol
            self.packet = {'finite_caps': {'grant_instances_max': 8}, 'grants': {
                f'{case}/{step}': template for case in proof.CASES for step, template in spec['cases'][case]['grants'].items()}}
            self.application = sources[INITIAL].decode()
            self.instances, self.leases, self.sessions = {}, {}, []
            self.sequence = 0
            self.native_count = 0
            self.identity_attempted = self.identity_open = False

        def identity(self):
            self.socket_checked()
            return read_identity(owner)

        def text(self, name):
            proof.need(name in files and name.endswith('.sql'), 'TRACK_EXACT_CLOSED_SQL_LEAF')
            return files[name].decode()

        def psql(self, role):
            proof.need(role in fragments.ROLES, 'TRACK_EXACT_FINITE_ROLE')
            return owner.psql_args(owner.name, role)

        def socket_checked(self):
            proof.need(not owner.transport.unknown and owner.docker.socket_identity() == owner.docker.origin,
                       'TRACK_STICKY_TRANSPORT_OR_SOCKET')

        def uncertain(self, code):
            owner.transport.unknown = owner.docker.remote_unknown = True
            self.evidence.stop(code)

        def session(self, role):
            self.socket_checked()
            active = tuple(s.role for s in self.sessions if not s.closed)
            proof.need(role in fragments.ROLES and (not active or role == 'wa_context_issuer'
                       and active in (('wa_app_runtime',), ('wa_worker',)))
                       and (role != 'wa_identity_service_authority' or self.identity_open), 'TRACK_DIRECT_SESSION_CAP')
            result = Session(role, self)
            self.sessions.append(result)
            return result

        def spawn(self, role):
            self.socket_checked()
            return owner.transport.io.Popen(owner.docker.argv(*self.psql(role)), cwd=str(proof.ROOT), shell=False,
                stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, bufsize=0)

        def raw(self, role, text):
            proof.need(role in ('postgres', 'wa_context_issuer') and type(text) is str and len(text.encode()) <= 256 * 1024,
                       'TRACK_FIXED_CLOSED_RAW_OBSERVER')
            self.socket_checked()
            result = owner.command(self.psql(role), text, timeout=30)
            proof.need(result.returncode == 0 and result.stderr == '' and len(result.stdout.encode()) <= 256 * 1024,
                       'TRACK_FIXED_CLOSED_RAW_OBSERVER')
            return result.stdout.strip()

        def require_backend_absent(self, role, backend):
            proof.need(role == backend['login'] and role in fragments.ROLES
                       and re.fullmatch('[1-9][0-9]{0,9}', backend['pid'])
                       and re.fullmatch('[0-9T:+. \\-]{1,64}', backend['started']), 'TRACK_EXACT_CLIENT_TUPLE')
            query = (f"SELECT count(*) FROM pg_stat_activity WHERE pid={backend['pid']} AND backend_start="
                     f"'{backend['started']}'::timestamptz AND usename='{role}' AND datname='{proof.DATABASE}';")
            proof.need(self.raw('postgres', query) == '0', 'TRACK_EXACT_CLIENT_UNCLOSED')

        def global_closure(self):
            proof.need(not any(not session.closed for session in self.sessions), 'TRACK_OWN_SESSION_UNCLOSED')
            p.closed_backends(owner.name, 'TRACK_BUSINESS_GLOBAL_CLOSURE')

        def observe(self, label, text):
            owner.report['stage'] = 'TRACK_BUSINESS_OBSERVE'
            self.global_closure()
            prior = self.identity()
            raw = self.raw('postgres', text)
            self.global_closure()
            after = self.identity()
            proof.exact(prior, after, 'TRACK_CROSS_RESOURCE_OBSERVER_DRIFT')
            return {'identity': prior, 'raw': raw, 'closed': True}

        def retain_observation(self, label, validated_value, identity):
            rows = self.evidence.value['observations']
            raw = proof.canonical(validated_value)
            proof.need(len(rows) < driver.OBSERVATION_COUNT and all(row['stage'] != label for row in rows)
                       and 0 < len(raw) <= 16384 and type(label) is str and re.fullmatch('[a-z0-9/-]{1,90}', label),
                       'TRACK_CLOSED_OBSERVATION_RECEIPT_BOUNDS')
            proof.exact(identity, self.evidence.value['identity'], 'TRACK_CROSS_RESOURCE_OBSERVER_DRIFT')
            rows.append({'stage': label, 'sha256': proof.sha(raw), 'validated': validated_value,
                         'operation_closed': True, 'resource_identity_sha256': proof.sha(proof.canonical(identity))})
            self.evidence.save()

        def native_observation(self):
            self.global_closure()
            self.identity()
            proof.need(owner.blobs[NATIVE] == sources[NATIVE], 'TRACK_EXACT_NATIVE_COLLECTOR')
            self.native_count += 1
            native = p.collect_native(owner.name, 'NATIVE_TRACK_BUSINESS_FIXTURE',
                                      f'track-business-fixture-native-{self.native_count}.json')
            self.global_closure()
            proof.need(type(native) is dict, 'TRACK_CLOSED_NATIVE_READBACK')
            return native

        def fixture(self, leaf, text, restore, targets):
            owner.report['stage'] = 'TRACK_BUSINESS_FIXTURE'
            restoration = ('restore-user-plan-owner-commits.sql' if leaf == 'user-plan-fixtures'
                           else 'restore-prior-selection-owner-commits.sql')
            proof.need(leaf in {'user-plan-fixtures', *(f'{case}/prior-selection-fixture' for case in proof.CASES)}
                       and text == self.text(leaf + '.sql') and set(targets) == RESTORE_TARGETS[restoration]
                       and restore == self.text(restoration), 'TRACK_EXACT_FIXTURE_SCOPE')
            proof.exact(self.native_observation(), self.native, 'TRACK_PRE_FIXTURE_NATIVE_DRIFT')
            try:
                self.commit('postgres', text, 'TRACK_FIXTURE_' + leaf)
                proof.exact(self.native_observation(), self.native, 'TRACK_POST_FIXTURE_NATIVE_DRIFT')
            except BaseException as first:
                p._required_safety_first_exception(first, 'TRACK_BUSINESS_FIXTURE')
                if not owner.transport.unknown:
                    try:
                        if exact_fixture_restoration(self.native, self.native_observation(), targets):
                            self.commit('postgres', restore, 'TRACK_EXACT_FIXTURE_RESTORATION')
                            proof.exact(self.native_observation(), self.native, 'TRACK_POST_RESTORATION_NATIVE_DRIFT')
                    except BaseException as secondary:
                        p._required_safety_first_exception(secondary, 'TRACK_BUSINESS_FIXTURE_RESTORATION')
                raise

        def identity_bootstrap(self, text):
            owner.report['stage'] = 'TRACK_BUSINESS_IDENTITY'
            proof.need(not self.identity_attempted and text == self.text('identity-bootstrap.sql'), 'TRACK_ONE_IDENTITY_BOOTSTRAP')
            self.global_closure()
            self.identity_attempted = self.identity_open = True
            try:
                self.commit('wa_identity_service_authority', text, 'TRACK_SYNTHETIC_IDENTITY_BOOTSTRAP')
            finally:
                self.identity_open = False
            self.global_closure()

        def new_lease(self, case):
            proof.need(case in proof.CASES and case not in self.leases, 'TRACK_ONE_CASE_LEASE')
            token = secrets.token_hex(32)
            proof.need(token not in self.leases.values(), 'TRACK_DISJOINT_LEASES')
            self.leases[case] = token
            p.all_secrets.extend((token, proof.sha(bytes.fromhex(token))))
            return token

        def restricted(self, case, step, grant, sql, expected, lease, fence):
            owner.report['stage'] = 'TRACK_BUSINESS_RESTRICTED'
            proof.need(case in proof.CASES and step in proof.ROLE_GRANTS, 'TRACK_EXACT_RESTRICTED_SELECTOR')
            leaf = f'{case}/{step}'
            spec_case = spec['cases'][case]
            reserve = {'claim': 'lease_claim_fence', 'retained-effect': 'lease_effect_fence'}.get(step)
            proof.need(grant == self.packet['grants'][leaf] and sql == self.text(leaf + '.sql')
                       and expected == spec_case[driver.STAGE_RECORDS[step]] and
                       ((reserve is None and lease is None and fence is None) or
                        (reserve is not None and lease == self.leases[case] and type(fence) is int and fence == spec_case[reserve])),
                       'TRACK_RESTRICTED_LITERAL_SCOPE')
            self.global_closure()
            ordinal = self.sequence
            backend, outcome = self.finite_transaction(leaf, leaf, leaf + '.sql', expected, case if reserve else None, fence)
            proof.need(self.sequence == ordinal + 1 and outcome['complete_record_sequence_match'] is True, 'TRACK_ONE_ISSUER_AND_COMMIT')
            return {'actual_login': backend['login'], 'xid': backend['xid'], 'grant_id': self.instances[self.sequence]['id'],
                    'committed': True, 'client_closed': True, 'same_tuple': True, 'stage_records_exact': True}

        def retain_all_grants(self, actual_ids):
            self.global_closure()
            proof.need(actual_ids == {item['id'] for item in self.instances.values()} and len(actual_ids) == 8,
                       'TRACK_COMPLETE_ISSUER_INSTANCE_SET')
            self.retention(list(self.instances), unexpired=False)
            self.global_closure()

    return Coordinator()
