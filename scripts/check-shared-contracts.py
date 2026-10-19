#!/usr/bin/env python3
"""Validate all Shared Operation schemas, wire fixtures and independent consumer field expectations."""
import copy
import hashlib
import json
import re
import sys
from collections import Counter
from pathlib import Path
sys.path.insert(0,str(Path(__file__).parent))
from contract_schema import Registry,SchemaError
ROOT=Path(__file__).resolve().parents[1]

def inspect(root=ROOT):
    errors=[];checks=Counter();read=lambda n:json.loads((root/n).read_text())
    catalog=read('context/shared/contracts/contract-catalog.json')['contracts'];fixtures=read('tests/contracts/shared/wire-fixtures.json')['fixtures'];bindings=read('tests/contracts/shared/consumer-expectations.json')['bindings']
    consumer_document=read('tests/contracts/shared/consumer-expectations.json')
    if consumer_document.get('shared_types_sha256')!=hashlib.sha256((root/'contracts/shared/types.v1.schema.json').read_bytes()).hexdigest():errors.append('Shared types changed without retained consumer compatibility review')
    reg=Registry(root);by={c['id']:c for c in catalog};fx={f['contract']:f for f in fixtures}
    expected={f'SH-{i:03}' for i in range(1,133)}
    if set(by)!=expected or len(catalog)!=132 or set(fx)!=expected or len(fixtures)!=132:errors.append('132-contract identity/fixture coverage mismatch')
    canonical=(root/'context/shared/shared-operations.md').read_text()
    module_paths=read('context/reconciliation/readiness-inventory.json')['module_paths']
    for c in catalog:
        source_owners=c['source_truth']['owners']
        if set(source_owners)-set(module_paths):errors.append(c['id']+': unapproved source owner')
        expected_paths=[module_paths[o]['files'][0] for o in source_owners if o in module_paths]
        if c['owner_architecture_refs']!=expected_paths:errors.append(c['id']+': source owner/artifact mismatch')
        sh=c['id'];pattern=r'^### '+sh+r' — `'+re.escape(c['name'])+r'`\n(.*?)(?=^### |^## |\Z)';match=re.search(pattern,canonical,re.M|re.S)
        if not match:errors.append(sh+': missing canonical identity');continue
        fields=dict(re.findall(r'^- \*\*([^*]+):\*\* (.+)$',match[1],re.M))
        if c['canonical_owner']!=fields['Owner'] or c['registry_status']!=fields['Status']:errors.append(sh+': canonical owner/status drift')
        f=fx[sh]
        for part,value in [('request',f['request']),('response',f['producer_result'])]+[('response',v) for v in f['rejected_results']]:
            found=reg.check(sh,part,value);checks['positive_wire_cases']+=1
            if found:errors.append(sh+': invalid positive '+part+' '+str(found[:2]))
        # Unknown fields, missing required fields and changed major cannot silently integrate.
        for part,seed in [('request',f['request']),('response',f['producer_result'])]:
            tests=[];v=copy.deepcopy(seed);v['unexpectedPrivatePayload']='prohibited';tests.append(v)
            v=copy.deepcopy(seed);v.pop('requestId');tests.append(v)
            v=copy.deepcopy(seed);v['contract']=sh+'.v2';tests.append(v)
            for v in tests:
                checks['negative_wire_cases']+=1
                if not reg.check(sh,part,v):errors.append(sh+': invalid/major-incompatible '+part+' accepted')
        cstatus=c['qualification']['final_disposition']
        if cstatus not in {'EVOLVABLE_COMPATIBLY','EXTERNALLY_GATED','UNSTABLE','FROZEN_FOR_IMPLEMENTATION'}:errors.append(sh+': invalid final disposition')
        if cstatus=='FROZEN_FOR_IMPLEMENTATION' and not c['qualification']['freeze_evidence']:errors.append(sh+': unsupported freeze')
        if cstatus=='UNSTABLE' and not (c['qualification'].get('specific_blocker') and c['qualification'].get('blocker_owner')):errors.append(sh+': unspecific instability')
        if cstatus=='EXTERNALLY_GATED' and not c['qualification']['external_requirements']:errors.append(sh+': external gate lacks reason')
        if c['qualification']['runtime_implementation_qualification']!='NOT_QUALIFIED':errors.append(sh+': runtime promotion lacks actual producer/provider evidence')
        if c['registry_status']=='Proposed ruling' and not c['proposal_review']['explicit_semantic_adoption']:errors.append(sh+': proposal silently promoted')
        for dep in c['dependencies']:
            if dep['operation'] not in expected or dep['startup_wait']:errors.append(sh+': invalid/unjustified whole startup dependency')
        for p in c['owner_architecture_refs']:
            if not (root/p).is_file():errors.append(sh+': missing actual owner file')
    for f in read('tests/contracts/shared/wire-fixtures.json').get('variant_fixtures',[]):
        for part,value in [('request',f['request']),('response',f['producer_result'])]:
            found=reg.check(f['contract'],part,value);checks['source_variant_wire_cases']+=1
            if found:errors.append(f['id']+': variant mismatch '+str(found[:2]))
    for b in bindings:
        sh=b['contract']
        if sh not in by:errors.append('Unknown consumer contract '+sh);continue
        doc=reg.documents['urn:workin-ants:'+sh+':v1']
        if reg.errors(fx[sh]['producer_result'],b['consumer_response_schema'],doc):errors.append(b['id']+': incompatible retained consumer response schema')
        actual=set(fx[sh]['producer_result']['value']);required=set(b['consumer_requires_fields']);checks['bilateral_expectation_checks']+=1
        if not required<=actual:errors.append(b['id']+': incompatible producer result/consumer requirement')
        if b['wire_version']!='v1':errors.append(b['id']+': unsupported consumer major')
        if b['id'] not in by[sh]['consumer_bindings']:errors.append(b['id']+': unregistered consumer')
        for p in ['owner_architecture','owner_plan']:
            if not (root/b[p]).is_file():errors.append(b['id']+': missing consumer authority')
    for c in catalog:
        if Counter(c['consumer_bindings'])!=Counter(b['id'] for b in bindings if b['contract']==c['id']):errors.append(c['id']+': missing/duplicate bilateral binding')
    for v in read('tests/contracts/shared/type-vectors.json')['vectors']:
        doc=reg.documents['urn:workin-ants:types:v1'];found=reg.errors(v['value'],doc['$defs'][v['type']],doc);checks['common_type_smoke_cases']+=1
        if found:errors.append(v['type']+': invalid type smoke vector '+str(found[:2]))
    for v in read('tests/contracts/shared/semantic-shape-vectors.json')['cases']:
        doc=reg.documents['urn:workin-ants:types:v1'];valid=not reg.errors(v['value'],doc['$defs'][v['type']],doc);checks['semantic_shape_cases']+=1
        if valid!=v['valid']:errors.append(v['id']+': semantic shape acceptance mismatch')
    for v in read('tests/contracts/shared/semantic-request-vectors.json')['cases']:
        valid=not reg.check(v['contract'],'request',v['request']);checks['cross_field_request_cases']+=1
        if valid!=v['valid']:errors.append(v['id']+': request coupling mismatch')
    # Validate every family/event definition resolves, and every registered R069 producer has a closed payload.
    defs=reg.documents['urn:workin-ants:types:v1']['$defs']
    events={e for m in read('context/reconciliation/authority-event-review.json')['modules'].values() for e in m['producer']}
    declared={s['properties']['eventName']['const'] for n,s in defs.items() if n.startswith('EventPayload_')}
    if declared!=events:errors.append('Source event payload coverage mismatch')
    return {'errors':errors,'metrics':{'contracts':len(catalog),'schemas':len(reg.documents),'consumer_bindings':len(bindings),'event_payloads':len(declared),**dict(checks),'dispositions':dict(Counter(c['qualification']['final_disposition'] for c in catalog))},'scope':'Executable schema/wire and declared consumer expectations. These are not tests of real owner implementations, database concurrency, RLS, providers or full Privacy field/action coverage.'}
if __name__=='__main__':
    result=inspect();print(json.dumps(result,indent=2));raise SystemExit(bool(result['errors']))
