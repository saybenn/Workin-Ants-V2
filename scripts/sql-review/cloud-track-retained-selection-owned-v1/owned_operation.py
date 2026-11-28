"""Prepare and verify a separate Cloud Track retained-selection owner packet."""

import argparse
import ast
import os
from pathlib import Path
import re
import signal
import sys
from types import ModuleType
import uuid

import business_owner as business
import business_proof as proof
import cloud_child as child
import prior_machinery as prior


HERE = Path(__file__).resolve().parent
ROOT = proof.ROOT
INSTALLED = 'scripts/sql-review/cloud-track-retained-selection-owned-v1'
TRACK = prior.SOURCE_BASE
TRACK_PINS = {
    'candidate_profile.py': 'f4dc06e246b2c016585d72dad8165b0b6f41614f48574551e889bca27a280315',
    'three_proof.py': '6e1e185029e748f18ac57ea777427ea0f79975d9d15a242992670e366b2677a2',
    'operation.py': 'fa2b211aed19cd5f4fc30b7172f9b581b25504f3dedcfcea9a8a68a2362f78ef',
    'test_owned_operation.py': 'b9ed551039ecf34ed585e60457b13b75a4371bee3c0fe2d750d65af17fb4f216',
}
PACKAGE_FILES = ('owned_operation.py', 'prior_machinery.py', 'business_driver.py', 'business_owner.py',
                 'business_proof.py', 'cloud_child.py', 'reviewed_fragments.py', 'test_business.py',
                 'test_owned_operation.py', 'README.md', 'OPERATION.md')
ACCEPTANCE_PINS = {f'{TRACK}/{name}': digest for name, digest in TRACK_PINS.items()}
SCHEMA = child.OWNER_SCOPE
SOURCE_REVIEW = 'workinants.cloud-f0-track-retained-selection-source-review.v1'
LITERAL_REVIEW = 'workinants.cloud-f0-track-retained-selection-literal-review.v1'
EXECUTE = '--execute-reviewed-cloud-f0-track-retained-selection-owned-v1'
DRAFT = 'HELD_DRAFT_NO_EXECUTION_AUTHORITY'
COMMITTED = 'HELD_COMMITTED_PENDING_EXACT_BUSINESS_REVIEW'
SOURCE_SCOPES = ['accepted_physical_track_three_history_owner', 'exact_v4_recipe_capsule_and_candidate_catalog',
                 'scope_bounded_grants_fixtures_and_two_retained_cases', 'typed_work_full42_native_and_ledger_parity',
                 'first_failure_evidence_and_exclusive_cleanup']
LITERAL_SCOPES = ['verified_current_daemon_image_and_fresh_run_resources', 'exact_current_git_source_tool_and_recipe_digests',
                  'genuine_three_migration_status_noop_and_original_grantor', 'two_fixed_cases_eight_grants_and_bounded_fixture_restoration',
                  'independent_client_closure_and_owned_cleanup']


def mechanism():
    """Load the exact corrected Track owner without expanding its dispatch surface."""
    registered = []
    try:
        loaded = []
        for leaf in ('candidate_profile.py', 'three_proof.py', 'operation.py'):
            path = ROOT / TRACK / leaf
            raw = proof.path_hash(path, TRACK_PINS[leaf])
            name = '_cloud_track_business_inherited' if leaf == 'operation.py' else path.stem
            proof.need(name not in sys.modules, 'TRACK_BUSINESS_PINNED_IMPORT_COLLISION')
            module = ModuleType(name)
            module.__file__ = str(path)
            sys.modules[name] = module
            registered.append(name)
            exec(compile(raw, str(path), 'exec', dont_inherit=True), module.__dict__)
            loaded.append(module)
    finally:
        for name in registered:
            del sys.modules[name]
    return loaded[-1]


def recipe_capsule(track, *, draft):
    packet = proof.PACKET if draft else HERE / 'recipe-v4' / 'packet'
    material = proof.load(ROOT, packet)
    _, files, _, _ = material
    assets = {f'packet/{name}': raw for name, raw in files.items()}
    assets.update({'packet/MANIFEST.json': proof.path_hash(packet / 'MANIFEST.json', proof.MANIFEST_SHA),
                   'prepare.py': proof.path_hash(packet.parent / 'prepare.py', proof.GENERATOR_SHA),
                   'independent-source-review.json': proof.path_hash(packet.parent / 'independent-source-review.json', proof.REVIEW_SHA)})
    if not draft:
        # Committed source may have normal Git modes. Require its closed shape,
        # stable content and exact readback through the whole-source gate below.
        inventory = tuple(packet.parent.rglob('*'))
        track.S.require(all(not node.is_symlink() and (node.is_file() or node.is_dir()) for node in inventory)
                        and {node.relative_to(packet.parent).as_posix() for node in inventory if node.is_file()} == set(assets)
                        and {node.relative_to(packet.parent) for node in inventory if node.is_dir()}
                            == {parent for name in assets for parent in Path(name).parents if parent != Path('.')},
                        'TRACK_EXACT_COMMITTED_RECIPE_CAPSULE')
    return material, assets


def compose(tool_archive, run_id, *, draft=False, prior_path=None, prior_sha=None):
    proof.need((prior_path is None) == (prior_sha is None), 'TRACK_PRIOR_PATH_AND_SHA_REQUIRED_TOGETHER')
    if not draft:
        proof.need(prior_path is not None, 'TRACK_PRIOR_INDEPENDENT_MACHINERY_ACCEPTANCE_REQUIRED')
        proof.need(HERE == ROOT / INSTALLED, 'TRACK_BUSINESS_OWNER_MUST_BE_COMMITTED_IN_CHECKOUT')
        proof.need({path.name for path in HERE.iterdir()} == set(PACKAGE_FILES) | {'recipe-v4'},
                   'TRACK_BUSINESS_OWNER_EXACT_INSTALLED_TREE')
    track = mechanism()
    S, P = track.S, track.P
    admitted, past = (None, {}) if prior_path is None else prior.load(prior_path, prior_sha, ROOT, corrected_source_pins=ACCEPTANCE_PINS)
    prepared, two, steps, native = track.compose(tool_archive, run_id, draft=True)
    _, operation, blobs, inner, manifest, nested, sources, archive = prepared
    proof.need(all(S.sha(blobs[name]) == digest for name, digest in ACCEPTANCE_PINS.items()), 'TRACK_CORRECTED_CANONICAL_OWNER_SOURCE')
    material, recipe = recipe_capsule(track, draft=draft)
    _, leaves, borrowed, _ = material
    extra = {**borrowed, **past, **{f'{INSTALLED}/{leaf}': S.read(HERE / leaf) for leaf in PACKAGE_FILES},
             **{f'{INSTALLED}/recipe-v4/{leaf}': raw for leaf, raw in recipe.items()}}
    proof.need(all(name not in blobs or blobs[name] == raw for name, raw in extra.items()), 'TRACK_BUSINESS_SOURCE_COLLISION')
    blobs = {**blobs, **extra}
    pins = {path: S.sha(raw) for path, raw in blobs.items()}
    if admitted is not None:
        proof.need(admitted['run_id'] != run_id and admitted['daemon'] == operation['daemon'] and admitted['image'] == operation['image'],
                   'TRACK_FORMER_RUN_MUST_BE_DISTINCT_AND_CLOSED')
    directory = P.SCRATCH / f'wa-cloud-f0-track-retained-selection-owned-{run_id}'
    operation.update(schema=SCHEMA, status=DRAFT if draft else COMMITTED, source=None if draft else S.verify_committed(ROOT, blobs),
                     source_pins=pins, source_aggregate_sha256=S.aggregate(pins),
                     nested_manifest=P.bind(directory / 'run-manifest.json', nested), archive=P.bind(directory / 'source9.tar', archive),
                     track_business={
                        'recipe': child.RECEIPTS, 'leaves_sha256': {name: S.sha(raw) for name, raw in leaves.items()},
                        'capsule_sha256': S.aggregate({name: S.sha(raw) for name, raw in recipe.items()}),
                        'prior_independent_machinery_acceptance_sha256': prior_sha,
                        'prior_independent_machinery_acceptance_path': None if prior_path is None else prior_path.relative_to(ROOT).as_posix(),
                        'prior_closed_track_run': None if admitted is None else {name: admitted[name] for name in ('run_id', 'container_id', 'volume_created_at')},
                        'cases': dict.fromkeys(proof.CASES, 'NOT_RUN'), 'finite_grants': 8, 'fixture_normal_commits': 3,
                        'complete_state_tables': 42, 'externally_paid_proof': False, 'assertion_promotions': 0,
                     })
    return (directory, operation, blobs, inner, manifest, nested, sources, archive), track, two, steps, native, material, recipe


def prepare(tool_archive, *, draft=False, prior_path=None, prior_sha=None):
    prepared, track, _, _, native, _, recipe = compose(tool_archive, str(uuid.uuid4()), draft=draft, prior_path=prior_path, prior_sha=prior_sha)
    directory, operation, _, _, _, nested, sources, archive = prepared
    directory.mkdir(mode=0o700)
    for name, raw in {'operation.json': track.S.encode(operation), 'run-manifest.json': nested, 'source9.tar': archive}.items():
        track.P.write_new(directory / name, raw)
    track.P.write_source(directory / 'source9', sources)
    track.P.write_source(directory / 'native', native)
    track.P.write_source(directory / 'business-recipes', recipe)
    return directory / 'operation.json', operation


def read_closed(path, *, draft=False):
    track = mechanism()
    S, P = track.S, track.P
    proof.need(path.parent.parent == P.SCRATCH and path.name == 'operation.json', 'TRACK_BUSINESS_PACKET_EXACT_PATH')
    P.private_path(path.parent, file=False)
    raw = S.read(P.private_path(path, file=True))
    value = S.unique_json(raw)
    proof.need(value['schema'] == SCHEMA and value['status'] == (DRAFT if draft else COMMITTED),
               'TRACK_BUSINESS_COMMITTED_PACKET_REQUIRED')
    scope = value['track_business']
    prior_address = scope['prior_independent_machinery_acceptance_path']
    prior_path = None if prior_address is None else ROOT / prior_address
    composition = compose(Path(value['tools']['path']), value['run_id'], draft=draft, prior_path=prior_path,
                          prior_sha=scope['prior_independent_machinery_acceptance_sha256'])
    (directory, expected, _, _, _, nested, sources, archive), track, _, _, native, _, recipe = composition
    proof.need(path == directory / 'operation.json' and raw == S.encode(expected), 'TRACK_BUSINESS_PACKET_BYTE_DRIFT')
    track.compare_source9(directory, nested, sources, archive)
    track.exact_tree(directory / 'native', native)
    track.exact_tree(directory / 'business-recipes', recipe)
    return composition, raw


def bindings(track, operation, raw):
    scope = operation['track_business']
    return {**track.review_bindings(operation, raw), **scope['recipe'], 'recipe_capsule_sha256': scope['capsule_sha256'],
            'prior_independent_machinery_acceptance_sha256': scope['prior_independent_machinery_acceptance_sha256']}


def exact_reviews(track, directory, operation, raw):
    bound = bindings(track, operation, raw)
    source, source_hash = track.P.read_review(directory / 'source-review.json', schema=SOURCE_REVIEW, bindings=bound, scopes=SOURCE_SCOPES)
    literal, literal_hash = track.P.read_review(directory / 'literal-review.json', schema=LITERAL_REVIEW,
        bindings={**bound, 'source_review_sha256': source_hash}, scopes=LITERAL_SCOPES)
    proof.need(source['source_author'] == literal['source_author'], 'TRACK_BUSINESS_REVIEW_AUTHOR_MISMATCH')
    return {'source': source_hash, 'literal': literal_hash, 'source_reviewer': source['reviewer'], 'literal_reviewer': literal['reviewer']}


def scoped_codes(blobs):
    paths = [f'{INSTALLED}/{leaf}' for leaf in PACKAGE_FILES if leaf.endswith('.py') and not leaf.startswith('test_')]
    paths += ['scripts/sql-review/cloud-app-source8-v1/host_session.py', 'scripts/sql-review/run-context-control-rehearsal.py',
              'scripts/sql-review/run-worker-recovery-control-rehearsal.py', 'scripts/worker_recovery_control_protocol.py',
              'scripts/sql-review/run-scoped-read-companion-rehearsal.py']
    codes = {'TRACK_BOUNDED_CHILD_FAILURE'}
    for path in paths:
        for node in ast.walk(ast.parse(blobs[path], filename=path)):
            if not isinstance(node, ast.Call):
                continue
            name = getattr(node.func, 'id', None) or getattr(node.func, 'attr', None)
            if name in ('need', 'require') and len(node.args) > 1:
                value = node.args[1]
            elif name in ('Held', 'HeldFailure', 'SessionStop') and node.args:
                value = node.args[0]
            else:
                continue
            if isinstance(value, ast.Constant) and type(value.value) is str and re.fullmatch('[A-Z0-9_]{1,100}', value.value):
                codes.add(value.value)
    proof.need(0 < len(codes) <= 512, 'TRACK_FINITE_FAILURE_CODE_VOCABULARY')
    return codes


def owning_class(track, two, steps, native, material):
    inherited = business.owner_adapter(track.owner_type(two, steps, native), material)

    class Owner(inherited):
        def configure_program(self):
            super().configure_program()
            self.report['schema'] = 'workinants.cloud-f0-track-retained-selection-owned-run-evidence.v1'
            self.report['limits'].update(candidate_history_only=False, track_business_cases=list(proof.CASES))
            self.program.SAFE_FAILURE_CODES |= scoped_codes(self.blobs)

        def fresh(self, cid):
            earlier = self.operation['track_business']['prior_closed_track_run']
            proof.need(type(cid) is str and proof.HASH.fullmatch(cid) and cid != earlier['container_id']
                       and self.operation['run_id'] != earlier['run_id'], 'TRACK_FRESH_BUSINESS_TARGET_REQUIRED')

        def provision(self):
            super().provision()
            self.fresh(self.resources.cid)

        def observed_target(self):
            observed = super().observed_target()
            self.fresh(observed['container_id'])
            return observed

        def postchecks(self):
            composition, after = read_closed(self.directory / 'operation.json')
            restored, actual, *_ = composition
            proof.need(after == self.raw and restored[1] == self.operation
                       and exact_reviews(actual, self.directory, self.operation, after) == self.reviews
                       and actual.S.read(actual.P.private_path(self.directory / 'attempt.json', file=True))
                           == actual.attempt_receipt(self.operation, after, self.reviews), 'TRACK_BUSINESS_IMMUTABLE_POSTCHECK')
            self.report['immutable_source_postcheck'] = 'PASS'
            if self.transport.unknown:
                self.report['postcheck_remote_uncertainty_retained'] = True
            if self.report['status'] == track.PASS:
                proof.need(not self.transport.unknown and self.report['track_business']['status'] == business.PASS
                           and self.report['cleanup_full_container_identity_absent'] is True,
                           'TRACK_BUSINESS_CHILD_AND_CLOSURE_REQUIRED')
                evidence = self.report['track_business']
                expected = 'track-retained-selection-business-results.json'
                artifact = evidence['result']
                proof.need(artifact['path'] == expected, 'TRACK_BUSINESS_TERMINAL_RECEIPT')
                p = self.program
                raw, origin = p.closed_bytes(p.OUT / expected, origin=p.STATE['origins'][expected])
                facts = proof.unique_json(raw)
                proof.need(proof.sha(raw) == artifact['sha256'] == origin[0] and len(raw) == artifact['bytes']
                           and facts['identity'] == evidence['identity'] and facts['schema'] == business.RESULT_SCHEMA
                           and facts['status'] == business.PASS and facts['recipe'] == child.RECEIPTS
                           and facts['closed_observations'] == evidence['observations']
                           and [result['case'] for result in facts['results']] == list(proof.CASES)
                           and all(result['result'] == 'already_enrolled' and result['externally_paid_proof'] is False
                                   for result in facts['results'])
                           and type(facts['issued_grants']) is int and facts['issued_grants'] == 8
                           and len(facts['closed_observations']) == 26
                           and facts['postproof_full42_preserved'] is True and type(facts['assertion_promotions']) is int
                           and facts['assertion_promotions'] == 0,
                           'TRACK_BUSINESS_TERMINAL_RECEIPT')

    return Owner


def execute(path, *, explicitly_reviewed):
    proof.need(explicitly_reviewed is True, 'EXPLICIT_TRACK_BUSINESS_OPERATION_REQUIRED')
    composition, raw = read_closed(path)
    prepared, track, two, steps, native, material, _ = composition
    directory, operation, *_ = prepared
    reviews = exact_reviews(track, directory, operation, raw)
    proof.need({entry.name for entry in directory.iterdir()} == track.BASE_ENTRIES | {'business-recipes', 'source-review.json', 'literal-review.json'},
               'TRACK_FRESH_BUSINESS_ATTEMPT_DIRECTORY_REQUIRED')
    os.umask(0o077)
    track.P.write_new(directory / 'attempt.json', track.attempt_receipt(operation, raw, reviews))
    signal.signal(signal.SIGTERM, two.interrupt)
    signal.signal(signal.SIGHUP, two.interrupt)
    return owning_class(track, two, steps, native, material)(prepared, raw, reviews).run()


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest='action', required=True)
    make = commands.add_parser('prepare')
    make.add_argument('--draft', action='store_true')
    make.add_argument('--tool-archive', type=Path, required=True)
    make.add_argument('--prior-acceptance', type=Path)
    make.add_argument('--prior-acceptance-sha256')
    examine = commands.add_parser('verify')
    examine.add_argument('--draft', action='store_true')
    examine.add_argument('--packet', type=Path, required=True)
    run = commands.add_parser('execute')
    run.add_argument(EXECUTE, dest='approved', action='store_true')
    run.add_argument('--packet', type=Path, required=True)
    args = parser.parse_args(argv)
    try:
        if args.action == 'execute':
            return execute(args.packet, explicitly_reviewed=args.approved)
        if args.action == 'prepare':
            path, value = prepare(args.tool_archive, draft=args.draft, prior_path=args.prior_acceptance,
                                  prior_sha=args.prior_acceptance_sha256)
            raw = mechanism().S.encode(value)
        else:
            path = args.packet
            composition, raw = read_closed(path, draft=args.draft)
            value = composition[0][1]
        print(proof.canonical({'packet': str(path), 'sha256': proof.sha(raw), 'state': value['status'],
                              'source_files': len(value['source_pins']), 'prisma_archive_files': len(value['source9']),
                              'case_recipe_files': len(value['track_business']['leaves_sha256']), 'runtime': 'NOT_RUN'}).decode())
        return 0
    except BaseException as error:
        code = getattr(error, 'code', None) or str(error)
        if type(code) is not str or not code.isascii() or not code.replace('_', '').isalnum() or not code.isupper() or len(code) > 100:
            code = 'TRACK_BUSINESS_OWNER_HELD'
        print(proof.canonical({'status': 'HELD_OR_STOPPED', 'code': code, 'runtime_pass_claimed': False}).decode())
        return 1


if __name__ == '__main__':
    sys.exit(main())
