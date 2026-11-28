"""A Track terminal-hook overlay for a future committed, separately reviewed owner."""

import business_driver as driver
import business_proof as proof
import cloud_child as child


REQUIRED_CASES = ['retained-free', 'retained-paid-shape']
PASS = 'PASS_FINITE_TRACK_RETAINED_SELECTION_ONLY'
RESULT_SCHEMA = 'workinants.cloud-f0-track-retained-selection-business-result.v1'


class Evidence:
    def __init__(self, owner, identity):
        self.owner = owner
        self.value = {'identity': identity, 'status': 'IN_PROGRESS', 'operations': [], 'observations': [], 'assertion_promotions': 0}
        self.finalizing = False
        self.failed = False
        owner.report['track_business'] = self.value

    def stop(self, code):
        self.value.setdefault('first_failure', self.owner.program._safe_failure_code(code))
        self.value['status'] = 'STOPPED_PARTIAL_EVIDENCE_PRESERVED'
        return self.owner.program.best_effort_save()

    def save(self):
        if self.owner.program.best_effort_save() is not True:
            self.failed = True
            self.value.setdefault('first_failure', 'TRACK_CHILD_EVIDENCE_WRITE_UNCONFIRMED')
            self.value['status'] = 'STOPPED_PARTIAL_EVIDENCE_PRESERVED'
        if self.failed and not self.finalizing:
            raise proof.Held('TRACK_CHILD_EVIDENCE_WRITE_UNCONFIRMED')
        return not self.failed


def previous_artifact(program, filename):
    raw, _ = program.closed_bytes(program.OUT / filename, origin=program.STATE['origins'][filename])
    # These are single, indented artifacts. The inherited record splitter
    # applies only to line-delimited psql stdout.
    value = program.unique_json(raw)
    proof.need(type(value) is dict, 'TRACK_REQUIRED_INHERITED_ARTIFACT')
    return value, proof.sha(raw)


def owner_adapter(base, material):
    """Supply the same owned lifecycle with one finite business seam."""
    class Owner(base):
        def configure_program(self):
            super().configure_program()
            self.program.SAFE_FAILURE_STAGES |= {
                'TRACK_BUSINESS', 'TRACK_BUSINESS_GLOBAL_CLOSURE', 'TRACK_BUSINESS_FIXTURE',
                'TRACK_BUSINESS_OBSERVE', 'TRACK_BUSINESS_IDENTITY', 'TRACK_BUSINESS_RESTRICTED',
                'TRACK_BUSINESS_FIXTURE_RESTORATION', 'NATIVE_TRACK_BUSINESS_FIXTURE',
                'NATIVE_TRACK_BUSINESS_AFTER', 'NATIVE_TRACK_BUSINESS_AFTER_LEDGER',
                'LEDGER_BUSINESS_AFTER', 'LEDGER_FINGERPRINT_track-business-after',
            }

        def track_terminal(self, installed, before, after):
            inherited = super().track_terminal(installed, before, after)
            p = self.program
            self.report['stage'] = 'TRACK_BUSINESS'
            child.require_overlay_packet(self, material)
            proof.need('track_business' not in self.report and self.report['targets'][self.name]['finalization'] == 'PASS',
                       'TRACK_SINGLE_BUSINESS_ENTRY_AFTER_FINALIZATION')
            p.closed_backends(self.name, 'TRACK_BUSINESS_GLOBAL_CLOSURE')
            identity = child.read_identity(self)
            native, native_file = previous_artifact(p, 'noop-native-before.json')
            catalog, catalog_file = previous_artifact(p, 'noop-catalog-comparison.json')
            ledger, ledger_file = previous_artifact(p, 'noop-ledger-observation.json')
            last_rows, ledger_rows_file = previous_artifact(p, 'initial-after-noop-fingerprints.json')
            proof.exact(last_rows, after, 'TRACK_INHERITED_LEDGER_BASELINE_DRIFT')
            proof.need(p.digest(native) == catalog['native_snapshot_sha256'] == self.report['native_results']['noop']['native_sha256']
                       and catalog['source_expected_sha256'] == proof.CATALOG_SHA and catalog['status'] == 'PASS'
                       and catalog['check_counts'] == {'PASS': 29089} and catalog['findings'] == [],
                       'TRACK_INHERITED_NATIVE_BASELINE_DRIFT')
            p.ARTIFACT_PREFIX = ''
            p.write_safe('track-business-machinery-baseline.json', {**identity, 'native_file_sha256': native_file,
                         'catalog_file_sha256': catalog_file, 'ledger_file_sha256': ledger_file,
                         'ledger_fingerprints_file_sha256': ledger_rows_file, 'source_expected_sha256': proof.CATALOG_SHA,
                         'original_grantor_finalized': True, 'current_three_history_noop_checked': True})
            evidence = Evidence(self, identity)
            proof.need(evidence.save() is True, 'TRACK_CHILD_FIRST_EVIDENCE_UNCONFIRMED')
            scope = child.coordinator(self, material, native, evidence)
            try:
                sequence = driver.Driver(material, scope)
                result, full42 = sequence.run()
                scope.global_closure()
                proof.exact(scope.identity(), identity, 'TRACK_CROSS_RESOURCE_OBSERVER_DRIFT')
                final = p.collect_native(self.name, 'NATIVE_TRACK_BUSINESS_AFTER', 'track-business-native-after.json')
                registration, ledger_after = p.ledger_observation(installed, 'BUSINESS_AFTER')
                final_again = p.collect_native(self.name, 'NATIVE_TRACK_BUSINESS_AFTER_LEDGER', 'track-business-native-after-ledger.json')
                proof.exact((final, final_again, ledger_after), (native, native, ledger), 'TRACK_POST_BUSINESS_NATIVE_OR_LEDGER_DRIFT')
                checked, ledger_evidence = p.compare_ledger(registration, ledger_after, final)
                oracle = p.CATALOG['tools']['catalog_expression_oracle'].validate_evidence(
                    p.CATALOG['expected'], final, p.STATE['initial_oracle_evidence'], database=proof.DATABASE, grantor='postgres', root=proof.ROOT)
                proof.need(len(oracle) == 416 and checked['status'] == 'PASS' and len(checked['checks']) == 22
                           and len(registration['history_expected']) == 3, 'TRACK_POST_BUSINESS_NATIVE_COUNTS')
                last_fingerprints = p.fingerprints('track-business-after')
                row_parity = p.CATALOG['two'].compare_noop(last_rows, last_fingerprints)
                proof.exact(sequence.state('post-business-native-ledger-full42'), full42, 'TRACK_POSTPROOF_FULL42_DRIFT')
                proof.exact(scope.identity(), identity, 'TRACK_CROSS_RESOURCE_OBSERVER_DRIFT')
                proof.need(not self.transport.unknown and [case['case'] for case in result['results']] == REQUIRED_CASES
                           and len(evidence.value['observations']) == driver.OBSERVATION_COUNT,
                           'TRACK_EXACT_TWO_RUNTIME_CASES')
                p.write_safe('track-business-ledger-evidence.json', ledger_evidence)
                artifact = p.write_safe('track-retained-selection-business-results.json', {**result, 'status': PASS, 'schema': RESULT_SCHEMA,
                    'recipe': child.RECEIPTS,
                    'post_native_snapshot_sha256': p.digest(final), 'post_ledger_checks': 22, 'post_oracle_expressions': 416,
                    'three_rows_full_columns_preserved': row_parity, 'postproof_full42_preserved': True,
                    'business_operations': evidence.value['operations'], 'closed_observations': evidence.value['observations']})
                evidence.value.update(status=PASS, result=artifact)
                proof.need(evidence.save() is True, 'TRACK_CHILD_FINAL_EVIDENCE_UNCONFIRMED')
            except BaseException as first:
                p._required_safety_first_exception(first, self.report.get('stage', 'TRACK_BUSINESS'))
                evidence.stop(p._safe_failure_code(getattr(first, 'code', 'TRACK_BOUNDED_CHILD_FAILURE')))
                raise
            return {**inherited, 'business_cases': PASS, 'business_result': artifact}

    return Owner
