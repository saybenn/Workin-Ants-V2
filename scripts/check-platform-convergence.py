#!/usr/bin/env python3
"""Static platform evidence and dependency-policy regressions. Never runtime certification."""
import hashlib
import json
import re
from collections import Counter, defaultdict
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]


def components(pairs):
    graph = defaultdict(set)
    for a, b in pairs:
        graph[a].add(b)
        graph.setdefault(b, set())
    index, low, stack, active, groups = {}, {}, [], set(), []
    def visit(v):
        index[v] = low[v] = len(index)
        stack.append(v); active.add(v)
        for w in sorted(graph[v]):
            if w not in index:
                visit(w); low[v] = min(low[v], low[w])
            elif w in active:
                low[v] = min(low[v], index[w])
        if low[v] == index[v]:
            group = []
            while True:
                w = stack.pop(); active.remove(w); group.append(w)
                if w == v: break
            if len(group) > 1 or v in graph[v]: groups.append(sorted(group))
    for v in sorted(graph):
        if v not in index: visit(v)
    return sorted(groups)


def inspect(root=ROOT):
    base = root / 'context/reconciliation'
    read = lambda name: json.loads((base / name).read_text())
    review = read('platform-convergence-review.json')
    matrix = read('platform-lifecycle-action-matrix.json')
    graph = read('platform-dependency-graph.json')
    schema = read('platform-schema-compatibility-review.json')
    bridge = read('bridge-review-complete.json')
    authority = read('authority-event-review.json')
    operations = read('shared-operation-contract-status.json')['contracts']
    modules = json.loads((root / 'prisma/deep modules and schemas.json').read_text())
    owners = {m['id'] for m in modules}
    errors = []
    checks = lambda condition, message: errors.append(message) if not condition else None
    primary = [a for a in matrix['actions'] if 'parent' not in a]
    checks(Counter(a['owner'] for a in primary) == Counter(owners), 'Missing/duplicate owner action review')
    action_ids = {a['id'] for a in matrix['actions']}
    checks(len(action_ids) == len(matrix['actions']), 'Duplicate action identity')
    for a in matrix['actions']:
        for field in ['authoritative_state_transition', 'required_incoming_facts', 'authorization_entitlement_consent_hold_checks', 'failure_recovery_and_consumer_obligations', 'ports', 'evidence']:
            checks(bool(a.get(field)), a['id'] + ': missing semantic field ' + field)
        checks(a['owner'] in owners, a['id'] + ': unknown source owner')
        checks(not a['frozen'] and a['contract_status'] == 'UNSTABLE', a['id'] + ': unsupported freeze')
        checks(a['emitted_events'] == authority['modules'][a['owner']]['producer'], a['id'] + ': producer mismatch')
        checks(a['consumed_events'] == authority['modules'][a['owner']]['consumer'], a['id'] + ': subscriber mismatch')
        for p in a['evidence']: checks((root / p).is_file(), a['id'] + ': missing owner evidence')
        if 'parent' in a: checks(a['parent'] in action_ids, a['id'] + ': missing owner row')
    for p, expected in review['evidence_index'].items():
        checks((root / p).is_file() and hashlib.sha256((root / p).read_bytes()).hexdigest() == expected, p + ': platform evidence drift')
    for s in matrix['source_surfaces']:
        text = (root / s['path']).read_text()
        actual = re.search(r'^## 12\..*?(?=^## |\Z)', text, re.M | re.S)[0]
        checks(hashlib.sha256(actual.encode()).hexdigest() == s['section_sha256'], s['owner'] + ': source surface drift')
    checks(matrix['historical_record_coverage'] == bridge['record_coverage'], 'Historical record coverage changed')
    expected_families = {f['id']: f for f in bridge['families']}
    checks(Counter(f['family_id'] for f in matrix['family_coverage']) == Counter(expected_families.keys()), 'Family coverage missing/duplicate')
    edge_ids = {e['id'] for e in graph['edges']}
    checks(len(edge_ids) == len(graph['edges']), 'Duplicate typed edge identity')
    disabled = {d['family_id'] for d in graph['disabled_facets']}
    for f in matrix['family_coverage']:
        old = expected_families.get(f['family_id'])
        if not old: continue
        checks(f['source_record_ids'] == old['source_record_ids'] and f['historical_directional_facets'] == old['historical_directional_facets'], f['family_id'] + ': changed source lineage')
        checks(set(f['owner_actions']) <= action_ids and bool(f['owner_actions']), f['family_id'] + ': missing owner review link')
        checks(set(f['typed_edge_refs']) <= edge_ids, f['family_id'] + ': invalid typed edge')
        checks(bool(f['typed_edge_refs']) or f['family_id'] in disabled, f['family_id'] + ': unscoped active dependency')
        checks(not f['frozen'], f['family_id'] + ': false freeze')
        if f['family_id'] in disabled: checks(not f['active_dependency'], f['family_id'] + ': disabled facet enabled')
    for d in graph['disabled_facets']: checks(d['active_dependency'] is False, d['family_id'] + ': disabled dependency enabled')
    checks(len(graph['shared_operations']) == 132, 'Shared Operation coverage incomplete')
    canonical = {c['id']: c for c in operations}
    for c in graph['shared_operations']:
        for key in ['name', 'owner', 'registry_status', 'parallel_status']:
            checks(c[key] == canonical[c['id']][key], c['id'] + ': permanent identity/status drift')
    allowed_kinds = {'SYNC_QUERY','SYNC_COMMAND','ASYNC_COMMAND','ASYNC_EVENT','PROJECTION_COMMAND','PROJECTION_READ','SHARED_MECHANISM','PROVIDER_HANDOFF','RECOVERY_QUERY'}
    for e in graph['edges']:
        checks(e['kind'] in allowed_kinds, e['id'] + ': untyped edge')
        checks(not e['requires_full_upstream_maturity'], e['id'] + ': unjustified whole-upstream maturity dependency')
        checks(e['development_dependency'] == 'CONTRACT_ONLY_ALLOWED', e['id'] + ': contract/implementation stages conflated')
        checks(e['source_of_truth_use'] == 'SOURCE_OWNER_FACT_OR_DECISION', e['id'] + ': downstream projection used as source truth')
        checks(e['status'] == 'ARCHITECTURE_AGREED_UNFROZEN', e['id'] + ': graph falsely frozen')
    required_protocol = {'fact_query_reenters_composed_gate':False,'fenced_noncommit_required_before_reservation_release':True,'screening_order_requires_professional_seller':False,'media_ready_equals_access_permission':False,'audit_acceptance_precedes_sensitive_disclosure':True,'privacy_protocol_proves_field_executor_coverage':False,'hold_release_dispatches_money':False,'notification_delivery_finishes_source':False,'scope_registry_required_for_conditional_edges':True,'full_upstream_maturity_inferred':False,'root_runtime_vendor_qualified':False}
    checks(graph.get('protocol_invariants') == required_protocol, 'Platform protocol invariant weakened')
    for e in graph['edges']:
        checks(not (e['contract']=='executeModerationDecision' and e['provider'] in ['identity_access','role_authority','consent_disclosure','track_subscription_entitlement','customer_buyer_profile']), e['id'] + ': unregistered CL-01 generic moderation effect')
    events = {(e['consumer'],e['provider'],e['contract']) for e in graph['edges'] if e['kind']=='ASYNC_EVENT'}
    prod = {event:o for o,m in authority['modules'].items() for event in m['producer']}
    expected = {(o,prod[event],event) for o,m in authority['modules'].items() for event in m['consumer']}
    checks(events == expected, 'Registered event producer/consumer edges differ')
    synchronous = graph['synchronous_action_projection']
    typed_sync = {e['id'] for e in graph['edges'] if e['kind'] in ['SYNC_QUERY','SYNC_COMMAND']}
    checks(Counter(e['edge_id'] for e in synchronous) == Counter(typed_sync), 'Synchronous action graph coverage differs')
    for e in synchronous:
        checks(not e['from'].endswith(('::facts','::proof_acceptance')), e['edge_id'] + ': leaf re-enters composed gate')
    action_cycles = components([(e['from'],e['to']) for e in synchronous + graph['internal_action_routes']])
    startup_cycles = components(graph['startup_prerequisite_edges'])
    checks(not action_cycles, 'Synchronous action recursion remains')
    checks(not startup_cycles, 'Startup deadlock remains')
    for c in graph['critical_cycles']:
        checks(c['status'] == 'ARCHITECTURALLY_RESOLVED_RUNTIME_TESTS_REQUIRED' and bool(c['disposition']) and bool(c['edge_ids']), c['id'] + ': unresolved critical cycle')
    checks({r['id'] for r in review['rail_review']} == {'CL-01','CL-07','CL-08','CL-09'}, 'Incomplete cross-cutting rails')
    for r in review['rail_review']:
        checks(bool(r['negative_cases']) and bool(r['qualification']) and bool(r['review']), r['id'] + ': incomplete rail judgment')
    checks(not [f for f in review['findings'] if f['classification']=='ACTUAL_CONFLICT' and f['status']!='CORRECTED'], 'Open AI-resolvable actual conflict')
    model_names = re.findall(r'^model (\w+) ', (root/'prisma/schema.prisma').read_text(), re.M)
    expected_coverage = [{'model':name,'owners':[m['id'] for m in modules if name in m['schemasOwnedResponsibleForOver']]} for name in model_names]
    checks(schema['model_owner_coverage'] == expected_coverage, 'Schema source-owner mapping drift')
    checks(all(len(m['owners'])==1 for m in expected_coverage), 'Missing/duplicate schema source owner')
    checks(schema['posture']=='D' and schema['migration_or_runtime_executed'] is False, 'Unproven database posture promoted')
    checks(review['runtime_qualification_claimed'] is False, 'False runtime qualification')
    for p in review['changed_owner_files']:
        text=(root/p).read_text()
        checks('WA-R085–087' in text, p + ': missing current architecture/plan integration')
    module_cycles = components([(e['consumer'],e['provider']) for e in graph['edges'] if e['consumer'] in owners and e['provider'] in owners])
    actual = {'modules':len(owners),'clusters':10,'shared_operations':len(operations),'historical_records':len(matrix['historical_record_coverage']),'families':len(matrix['family_coverage']),'action_rows':len(matrix['actions']),'explicit_action_slices':len(matrix['actions'])-len(primary),'typed_dependency_edges':len(graph['edges']),'registered_events':len(prod),'critical_cycle_reviews':len(graph['critical_cycles']),'model_owners':len(expected_coverage),'compatibility_mirror_cases':len(schema['compatibility_mirrors']),'open_ai_resolvable_actual_conflicts':0,'frozen_contracts':0,'owner_surface_operations':sum(len(r['ports']) for r in primary)}
    checks(review['metrics']==actual, 'Claimed platform metrics differ')
    return {'errors':errors,'metrics':actual,'module_level_sccs':module_cycles,'synchronous_action_cycles':action_cycles,'startup_cycles':startup_cycles,'scope':'Static coverage, source integrity and architectural dependency assertions only; not executable DTO/RLS/concurrency/provider/Privacy/runtime certification.'}

if __name__=='__main__':
    result=inspect();print(json.dumps(result,indent=2));raise SystemExit(bool(result['errors']))
