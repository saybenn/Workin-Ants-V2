#!/usr/bin/env python3
"""Mutation checks of platform evidence validators, not executable business-contract tests."""
import importlib.util
import json
import shutil
import tempfile
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('platform_check',ROOT/'scripts/check-platform-convergence.py')
check=importlib.util.module_from_spec(spec);spec.loader.exec_module(check)


def main():
    results=[]
    with tempfile.TemporaryDirectory(prefix='wa-platform-negative-') as name:
        root=Path(name)
        shutil.copytree(ROOT/'context',root/'context')
        shutil.copytree(ROOT/'prisma',root/'prisma')
        baseline=check.inspect(root)
        if baseline['errors']:raise SystemExit('Positive baseline failed: '+str(baseline['errors']))
        base=root/'context/reconciliation'
        def case(label,filename,mutate,expected):
            p=base/filename;original=p.read_bytes();data=json.loads(original)
            mutate(data);p.write_text(json.dumps(data))
            found=check.inspect(root)['errors'];p.write_bytes(original)
            passed=any(expected in e for e in found)
            results.append({'case':label,'expected_rejection':expected,'rejected':passed,'errors':found})
            if not passed:raise SystemExit('Mutation survived: '+label)
        case('missing owner action','platform-lifecycle-action-matrix.json',lambda j:j['actions'].pop(0),'Missing/duplicate owner')
        case('duplicate historical record','platform-lifecycle-action-matrix.json',lambda j:j['historical_record_coverage'].append(j['historical_record_coverage'][0]),'Historical record coverage changed')
        case('missing family','platform-lifecycle-action-matrix.json',lambda j:j['family_coverage'].pop(),'Family coverage missing')
        case('false DTO freeze','platform-lifecycle-action-matrix.json',lambda j:j['actions'][0].update(frozen=True,contract_status='FROZEN_FOR_IMPLEMENTATION'),'unsupported freeze')
        case('missing registered subscriber','platform-dependency-graph.json',lambda j:j['edges'].remove(next(e for e in j['edges'] if e['contract']=='order.outcome_changed.v1' and e['consumer']=='payment_payout_tax')),'producer/consumer edges differ')
        def recursive(j):
            j['synchronous_action_projection'].append({'edge_id':'malformed-fixture','from':'transaction_order::facts','to':'role_authority::decision','contract':'forbidden recursive fact gate'})
        case('recursive Role fact query','platform-dependency-graph.json',recursive,'Synchronous action recursion remains')
        case('startup waits on its own diagnostics','platform-dependency-graph.json',lambda j:j['startup_prerequisite_edges'].append(['optional_delivery_diagnostics','primitives']),'Startup deadlock')
        case('unfenced reservation release','platform-dependency-graph.json',lambda j:j['protocol_invariants'].update(fenced_noncommit_required_before_reservation_release=False),'invariant weakened')
        case('Privacy protocol falsely proves executor coverage','platform-dependency-graph.json',lambda j:j['protocol_invariants'].update(privacy_protocol_proves_field_executor_coverage=True),'invariant weakened')
        case('Hold release dispatches money','platform-dependency-graph.json',lambda j:j['protocol_invariants'].update(hold_release_dispatches_money=True),'invariant weakened')
        case('audit after protected disclosure','platform-dependency-graph.json',lambda j:j['protocol_invariants'].update(audit_acceptance_precedes_sensitive_disclosure=False),'invariant weakened')
        case('projection used as source truth','platform-dependency-graph.json',lambda j:j['edges'][0].update(source_of_truth_use='DOWNSTREAM_PROJECTION_AUTHORITATIVE'),'projection used as source')
        case('whole upstream maturity invented','platform-dependency-graph.json',lambda j:j['edges'][0].update(requires_full_upstream_maturity=True),'whole-upstream maturity')
        case('disabled facet enabled','platform-dependency-graph.json',lambda j:j['disabled_facets'][0].update(active_dependency=True),'disabled dependency enabled')
        def screening(j):
            e=next(e for e in j['edges'] if e['contract']=='createChargeableOrder')
            s=next(x for x in j['synchronous_action_projection'] if x['edge_id']==e['id'])
            s.update({'from':'trust_verification_screening::decision','to':'transaction_order::decision'})
        case('paid screening collapsed into seller eligibility','platform-dependency-graph.json',screening,'Synchronous action recursion remains')
        def cl01(j):
            e=next(e for e in j['edges'] if e['contract']=='executeModerationDecision');e['provider']='customer_buyer_profile'
        case('unregistered CL-01 moderation executor','platform-dependency-graph.json',cl01,'unregistered CL-01 generic moderation')
        case('unsupported database posture promotion','platform-schema-compatibility-review.json',lambda j:j.update(posture='A'),'Unproven database posture')
        case('open actual conflict','platform-convergence-review.json',lambda j:j['findings'][0].update(status='OPEN'),'Open AI-resolvable actual conflict')
        case('missing privacy rail','platform-convergence-review.json',lambda j:j.update(rail_review=[r for r in j['rail_review'] if r['id']!='CL-08']),'Incomplete cross-cutting rails')
        owner=next(iter(json.loads((base/'platform-convergence-review.json').read_text())['evidence_index']))
        p=root/owner;original=p.read_bytes();p.write_bytes(original+b'\nUNREVIEWED DRIFT\n')
        errors=check.inspect(root)['errors'];p.write_bytes(original)
        results.append({'case':'owner evidence drift','expected_rejection':'platform evidence drift','rejected':any('platform evidence drift' in e for e in errors),'errors':errors})
    report={'status':'PASS' if all(r['rejected'] for r in results) else 'FAIL','cases':results,'total':len(results),'scope':'Negative mutation evidence for static validators only. No production DTO, concurrent transaction, RLS, provider or Privacy executor was executed.'}
    print(json.dumps(report,indent=2));return not all(r['rejected'] for r in results)
if __name__=='__main__':raise SystemExit(main())
