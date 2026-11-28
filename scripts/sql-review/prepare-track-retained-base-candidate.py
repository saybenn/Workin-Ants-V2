#!/usr/bin/env python3
"""Render the held append-only Track receipt correction and expected catalog."""

import argparse
from copy import deepcopy
import hashlib
import json
from pathlib import Path
import re

from pglast import parse_plpgsql

import catalog_manifest as catalog
import runtime_lease_effective_catalog_v1 as source8


ROOT = Path(__file__).resolve().parents[2]
VERIFIER = 'track_atomic_valid'
TRIGGER = 'track_enrollment_commit'
BINDING = 'track_binding'
FUNCTIONS = {
    VERIFIER: ('pg_catalog.text,pg_catalog.jsonb,pg_catalog.jsonb',
               '6242c25eb0f4ec3d60e52100e8acb26d3f2a1a6d58469e88834ce4f07669d7f5'),
    TRIGGER: ('', 'f0bd21ea32a780d8b875b40eac92d3561c68792afa51304c5c489a210b55ddf0'),
    BINDING: ('', 'fc1ac7f07e3a1863ceafa3ecd18f43cf4f4d84eeaa8aa3bce06d41707c247d0e'),
}
SOURCE8_CATALOG = 'cfb1c1cc9855e72978eadcd9e4902174e2e97a39383d480a71133c1fb07360c4'
CANDIDATE_PHASE = 'append_track_retained_base_v1'
CLOUD_RESULTS = 'context/reconciliation/cloud-phase0-evidence/2026-11-27/two-2f71c365/acceptance.json'
CLOUD_RESULTS_SHA = '9ecf3628b388ef11c504def7422bf53c1d67926820a6662d60a44dbc0fe61d76'
CLOUD_PACKET = 'context/reconciliation/cloud-phase0-evidence/2026-11-27/two-2f71c365/operation.json'
TRACK_RESULT = 'urn:workinants:database-review:foundation-payloads:v1#/$defs/assignDefaultFreeTrackCustomerResult'

SELECTION_COLUMNS = ('b.id,b.user_id,b.track,b.customer_profile_id,b.revision,b.subscription_id,'
                     'b.mutation_transaction_id,b.source_generation,b.candidate_profile_id,b.professional_profile_id')
SUBSCRIPTION_COLUMNS = ('a.id,a.user_id,a.track,a.customer_profile_id,a.plan_id,a.status,a.provider,'
                        'a.ended_at,a.current_period_end,a.revision,a.mutation_transaction_id,'
                        'a.candidate_profile_id,a.professional_profile_id')


def require(condition, message):
    if not condition:
        raise ValueError(message)


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def replace_once(text, old, new):
    require(text.count(old) == 1, 'expected SQL boundary must occur once')
    return text.replace(old, new, 1)


def existing_definition(application, name):
    pattern = rf'^CREATE FUNCTION platform_private\.{name}\([^\n]*\n.*?^END \$wa\$;'
    matches = re.findall(pattern, application, re.MULTILINE | re.DOTALL)
    require(len(matches) == 1 and sha(matches[0].encode('utf8')) == FUNCTIONS[name][1],
            f'original definition drift for {name}')
    return matches[0]


def verifier_definition(original):
    separator = " ELSIF table_name='track_enrollment_receipt' THEN\n"
    branch = f""" ELSIF table_name='track_enrollment_receipt' THEN
  IF n->>'result_code'='already_enrolled' THEN
   -- The guarded claim above has already locked the Customer and current plan.
   -- Do not acquire another plan lock after the User/track lock.
   PERFORM pg_advisory_xact_lock(hashtextextended('track:'||(o.payload->>'userId')||':customer',0));
  END IF;
  SELECT {SELECTION_COLUMNS} INTO sel
   FROM app.track_base_selection b WHERE b.id=(n->>'selection_id')::uuid;
  IF n->>'result_code'='enrolled' THEN
   selection_verified:=platform_private.worker_source_row_valid('TrackBaseSelection',sel.id::text);
  ELSIF n->>'result_code'='already_enrolled' THEN
   SELECT {SUBSCRIPTION_COLUMNS} INTO s
    FROM app.track_subscriptions a WHERE a.id=sel.subscription_id;
   selection_verified:=COALESCE(sel.id IS NOT NULL AND s.id IS NOT NULL
    AND sel.mutation_transaction_id<>pg_current_xact_id()::text
    AND s.mutation_transaction_id<>pg_current_xact_id()::text
    AND s.user_id=sel.user_id AND s.track=sel.track AND s.customer_profile_id=sel.customer_profile_id
    AND s.candidate_profile_id IS NULL AND s.professional_profile_id IS NULL
    AND sel.candidate_profile_id IS NULL AND sel.professional_profile_id IS NULL
    AND s.status IN ('active','trialing') AND s.ended_at IS NULL
    AND (s.current_period_end IS NULL OR s.current_period_end>clock_timestamp())
    AND platform_private.worker_row_capabilities('TrackBaseSelection',to_jsonb(sel),'SELECT')
    AND platform_private.worker_row_capabilities('TrackSubscription',to_jsonb(s),'SELECT'),false);
  ELSE
   RETURN false;
  END IF;
"""
    original = replace_once(original, 'w record; model_name text;', 'w record; model_name text; selection_verified boolean;')
    original = replace_once(original, separator +
        "  SELECT b.id,b.user_id,b.track,b.customer_profile_id,b.revision INTO sel FROM app.track_base_selection b WHERE b.id=(n->>'selection_id')::uuid;\n", branch)
    original = replace_once(original,
        "   AND platform_private.worker_source_row_valid('TrackBaseSelection',sel.id::text) AND platform_private.worker_effect_matches(w.id,e.id,true)",
        "   AND selection_verified AND platform_private.worker_effect_matches(w.id,e.id,true)")
    original = replace_once(original,
        "   AND e.fingerprint=o.payload_hash AND e.mutation_transaction_id=n->>'mutation_transaction_id'",
        "   AND n->>'fingerprint'=o.payload_hash::text AND e.fingerprint=o.payload_hash\n"
        "   AND e.mutation_transaction_id=n->>'mutation_transaction_id'")
    return original.replace('CREATE FUNCTION', 'CREATE OR REPLACE FUNCTION', 1)


def trigger_definition(original):
    # The restricted worker already has these two result columns. The private
    # verifier's independent column-limited grant does not need to change.
    return replace_once(original.replace('CREATE FUNCTION', 'CREATE OR REPLACE FUNCTION', 1),
        ' RETURN NULL;\nEND $wa$;', f""" IF TG_TABLE_NAME='track_enrollment_receipt' THEN
  SELECT c.result_body=jsonb_build_object('outcome',NEW.result_code,'selectionRevision',NEW.selection_revision::text,'receipt',NEW.id::text)
   AND c.result_digest=e.result_hash AND c.result_schema_id=e.result_schema_id
   AND e.result_schema_id='{TRACK_RESULT}'
   INTO result_matches
   FROM platform.runtime_effect_receipt e JOIN platform.runtime_command_receipt c ON c.id=e.command_receipt_id
   WHERE e.id=NEW.effect_receipt_id;
  IF result_matches IS DISTINCT FROM true THEN RAISE EXCEPTION 'Track result does not match enrollment receipt'; END IF;
 END IF;
 RETURN NULL;
END $wa$;""").replace('AS $wa$\nBEGIN', 'AS $wa$\nDECLARE result_matches boolean;\nBEGIN', 1)


def binding_definition(original):
    return replace_once(original.replace('CREATE FUNCTION', 'CREATE OR REPLACE FUNCTION', 1),
        " IF TG_TABLE_NAME='track_subscriptions' THEN\n  SELECT * INTO STRICT plan", """ IF TG_TABLE_NAME='track_subscriptions' THEN
  IF TG_OP='UPDATE' AND NEW.track='customer' THEN
   PERFORM pg_advisory_xact_lock(hashtextextended('track:'||NEW.user_id::text||':customer',0));
  END IF;
  SELECT * INTO STRICT plan""")


def migration(application):
    verifier = verifier_definition(existing_definition(application, VERIFIER))
    trigger = trigger_definition(existing_definition(application, TRIGGER))
    binding = binding_definition(existing_definition(application, BINDING))
    require(all(parse_plpgsql(definition) for definition in (verifier, trigger, binding)), 'invalid PL/pgSQL definition')
    return '\n'.join((
        'BEGIN;',
        'SET LOCAL ROLE wa_schema_owner;',
        trigger,
        binding,
        'GRANT CREATE ON SCHEMA platform_private TO wa_track_verifier;',
        'RESET ROLE;',
        'SET LOCAL ROLE wa_track_verifier;',
        verifier,
        'RESET ROLE;',
        'SET LOCAL ROLE wa_schema_owner;',
        'REVOKE CREATE ON SCHEMA platform_private FROM wa_track_verifier;',
        'RESET ROLE;',
        'COMMIT;',
        '',
    )).encode('utf8')


def build(root=ROOT):
    # The accepted TWO manifest pins each unchanged catalog input and the two
    # source8 migration bytes. The expected catalog remains entirely offline.
    prior_bytes = (root / CLOUD_RESULTS).read_bytes()
    require(sha(prior_bytes) == CLOUD_RESULTS_SHA, 'accepted source8 receipt drift')
    prior = json.loads(prior_bytes)
    require(prior['decision'] == 'ACCEPT_EXACT_DISPOSABLE_MIGRATION_MACHINERY'
            and prior['actual_evidence']['immutable_source8_history'] == [source8.INITIAL, source8.PATCH],
            'accepted source8 migration basis required')
    catalog_paths = (*catalog.INPUTS, source8.PATCH_PATH)
    blobs = {path: (root / path).read_bytes() for path in catalog_paths}
    pins = {path: sha(raw) for path, raw in blobs.items()}
    packet_bytes = (root / CLOUD_PACKET).read_bytes()
    require(sha(packet_bytes) == prior['files_sha256']['operation.json'], 'accepted source8 packet drift')
    packet_pins = json.loads(packet_bytes)['source_pins']
    require(all(packet_pins.get(path) == digest for path, digest in pins.items()),
            'accepted source8 catalog input drift')
    base = source8.build_manifest(catalog, blobs, pins)
    require(base['expected_sha256'] == SOURCE8_CATALOG, 'source8 catalog drift')
    bootstrap, application, finalize = (blobs[path].decode('utf8') for path in catalog.INPUTS[:3])
    append = migration(application)
    compiler = catalog.ManifestCompiler()
    for text, phase in ((bootstrap, 'bootstrap'), (application, 'application'),
                        (blobs[source8.PATCH_PATH].decode('utf8'), 'append_runtime_lease_v1')):
        compiler.consume(text, phase)
    acl_position = len(compiler.acl_events)
    compiler.consume(append.decode('utf8'), CANDIDATE_PHASE)
    compiler.consume(finalize, 'finalize')
    expected = compiler.result()
    expected['model_register'] = base['expected']['model_register']
    expected['prisma_declarations'] = base['expected']['prisma_declarations']
    adjusted = deepcopy(expected)
    statement_counts = adjusted['statement_counts'].pop(CANDIDATE_PHASE)
    require(statement_counts == {'TransactionStmt': 2, 'VariableSetStmt': 6, 'CreateFunctionStmt': 3, 'GrantStmt': 2},
            'candidate envelope drift')
    temporary_acl = adjusted['acl_source_operations'][acl_position:acl_position + 2]
    require([event.get('is_grant', False) for event in temporary_acl] == [True, False]
            and all(event['execution_role'] == 'wa_schema_owner'
                    and event['object_grantors'] == {'platform_private': 'wa_schema_owner'} for event in temporary_acl),
            'temporary Track verifier schema CREATE operations drift')
    del adjusted['acl_source_operations'][acl_position:acl_position + 2]
    changed = source8.delta(base['expected'], adjusted)
    wanted = sorted(f'/functions/platform_private.{name}({arguments})/{key}'
                    for name, (arguments, _) in FUNCTIONS.items() for key in ('body_sha256', 'definition_ast_sha256'))
    require(changed == wanted, f'candidate alters additional expected catalog facts: {changed}')
    return append, {
        'schema': 'workinants.track-retained-base-append-candidate.v1',
        'status': 'SOURCE_ONLY_PENDING_REVIEW_AND_ACTUAL_PARITY',
        'database_posture': 'D',
        'source8_catalog_sha256': SOURCE8_CATALOG,
        'ordered_migration_sha256': [source8.INITIAL, source8.PATCH, sha(append)],
        'expected_catalog_sha256': catalog.digest(expected),
        'changed_expected_fields': changed,
        'source_files_sha256': {**pins, CLOUD_RESULTS: CLOUD_RESULTS_SHA, CLOUD_PACKET: sha(packet_bytes)},
        'expected': expected,
    }


def main():
    cli = argparse.ArgumentParser(description=__doc__)
    cli.add_argument('--output', type=Path, required=True, help='New directory for the held candidate artifacts')
    args = cli.parse_args()
    append, manifest = build()
    args.output.mkdir(mode=0o700)
    with (args.output / 'migration.sql').open('xb') as output:
        output.write(append)
    with (args.output / 'expected-catalog.json').open('x', encoding='utf8', newline='\n') as output:
        json.dump(manifest, output, indent=2, sort_keys=True, allow_nan=False)
        output.write('\n')
    print(json.dumps({key: manifest[key] for key in ('status', 'ordered_migration_sha256', 'expected_catalog_sha256')}))


if __name__ == '__main__':
    main()
