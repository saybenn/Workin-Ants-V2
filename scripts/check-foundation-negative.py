#!/usr/bin/env python3
"""Adversarial architecture/consumer/schema/context mutations, never runtime provider tests."""
import copy
import json
import runpy
import shutil
import sys
import tempfile
from pathlib import Path
sys.dont_write_bytecode=True
ROOT=Path(__file__).resolve().parents[1]
CHECK=runpy.run_path(str(ROOT/'scripts/check-foundation.py'))['inspect']

def main():
    results=[]
    with tempfile.TemporaryDirectory(prefix='wa-foundation-negative-') as name:
        root=Path(name)
        for directory in ['context','contracts','tests','scripts','prisma','features','components','pages','app','legacy']:
            if (ROOT/directory).exists():shutil.copytree(ROOT/directory,root/directory,ignore=shutil.ignore_patterns('*.docx','*.bundle','__pycache__'))
        for file in ['AGENTS.md','CLAUDE.md','package.json','package-lock.json']:shutil.copy2(ROOT/file,root/file)
        baseline=CHECK(root)
        if baseline['errors']:raise SystemExit('Baseline failed: '+str(baseline['errors'][:4]))
        def jsoncase(label,path,mutator,expected):
            p=root/path;original=p.read_bytes();j=json.loads(original);mutator(j);p.write_text(json.dumps(j));found=CHECK(root)['errors'];p.write_bytes(original)
            passed=any(expected in e for e in found);results.append({'case':label,'expected':expected,'rejected':passed,'errors':found[:5]})
            if not passed:raise AssertionError('Mutation survived '+label+' '+str(found[:3]))
        catalog='context/shared/contracts/contract-catalog.json';wf='context/workflows/platform-workflows.json';lane='context/reconciliation/parallel-lane-manifest.json'
        jsoncase('missing SH identity',catalog,lambda j:j['contracts'].pop(),'identity/fixture coverage')
        jsoncase('duplicate SH identity',catalog,lambda j:j['contracts'].append(copy.deepcopy(j['contracts'][0])),'Missing/duplicated Shared Operation')
        jsoncase('canonical owner changed',catalog,lambda j:j['contracts'][0].update(canonical_owner='Consumer owns Identity'),'canonical owner/status drift')
        jsoncase('invented source owner',catalog,lambda j:j['contracts'][0]['source_truth'].update(owners=['unapproved_owner']),'unapproved source owner')
        jsoncase('silent Proposed promotion',catalog,lambda j:j['contracts'][2].update(registry_status='Confirmed'),'canonical owner/status drift')
        jsoncase('fake runtime qualification',catalog,lambda j:j['contracts'][0]['qualification'].update(runtime_implementation_qualification='QUALIFIED'),'runtime promotion')
        jsoncase('self-asserted freeze',catalog,lambda j:j['contracts'][0]['qualification'].update(final_disposition='FROZEN_FOR_IMPLEMENTATION',freeze_evidence={'assertion':'static pass'}),'qualification ledger/catalog mismatch')
        jsoncase('unexplained external gate',catalog,lambda j:j['contracts'][16]['qualification'].update(external_requirements=[]),'external gate lacks reason')
        jsoncase('broken workflow backlink',wf,lambda j:j['workflows'][0]['operations'].remove('SH-001'),'broken contract/workflow backlink')
        jsoncase('unregistered source event',wf,lambda j:j['workflows'][0]['registered_events'].append('role.permission_cache.v1'),'unregistered event')
        jsoncase('new synchronous contract cycle',catalog,lambda j:j['contracts'][76]['dependencies'].append({'operation':'SH-072','kind':'LOCAL_OR_PORT_CONTRACT','startup_wait':False,'qualification':'forbidden backedge'}),'synchronous dependency cycle')
        jsoncase('consumer requires absent result field','tests/contracts/shared/consumer-expectations.json',lambda j:j['bindings'][0]['consumer_requires_fields'].append('unprovidedAuthority'),'incompatible producer result')
        jsoncase('consumer expects incompatible field type','tests/contracts/shared/consumer-expectations.json',lambda j:j['bindings'][0]['consumer_response_schema']['properties']['value'].update(type='string'),'incompatible retained consumer response schema')
        jsoncase('unknown schema assertion silently ignored','contracts/shared/SH-001.v1.schema.json',lambda j:j['$defs']['request'].update(allowUnknownActor=True),'Unsupported schema keywords')
        jsoncase('unapproved concurrent lane',lane,lambda j:j['candidate_lanes'][0].update(authorized=True,status='ACTIVE'),'unapproved parallel activation')
        jsoncase('overlapping candidate file ownership',lane,lambda j:j['candidate_lanes'][1]['owned_file_roots'].append(j['candidate_lanes'][0]['owned_file_roots'][0]),'Parallel file ownership overlaps')
        jsoncase('candidate independently owns migrations',lane,lambda j:j['candidate_lanes'][0]['owned_file_roots'].append('prisma/'),'candidate owns shared integration path')
        def textcase(label,path,text,expected):
            p=root/path;original=p.read_bytes() if p.exists() else None;p.parent.mkdir(parents=True,exist_ok=True);p.write_text(text if original is None else original.decode()+text)
            found=CHECK(root)['errors']
            if original is None:p.unlink()
            else:p.write_bytes(original)
            passed=any(expected in e for e in found);results.append({'case':label,'expected':expected,'rejected':passed,'errors':found[:5]})
            if not passed:raise AssertionError('Mutation survived '+label+' '+str(found[:3]))
        textcase('foreign source repository','features/transaction_order/repository.ts','export const result = prisma.verificationCheck.findMany();','foreign source repository')
        textcase('cross-owner private import','features/transaction_order/foreign.ts','import x from "@/features/payment_payout_tax/infrastructure/repository";','cross-owner private import')
        textcase('consumer-local premium engine','features/transaction_order/premium.ts','export const isPremium = () => true;','duplicated local authority')
        textcase('unreviewed schema edit','prisma/schema.prisma','\n// unauthorized schema checkpoint\n','Protected source/schema/migration drift')
        textcase('broken current context link','context/ui-rules.md','\n[unavailable owner](missing-source.md)\n','broken current context link')
        jsoncase('invented implemented UI component','context/ui-registry.json',lambda j:j['components'][2].update(actual_path='components/ui/Unbuilt.tsx',status='COMPLETE'),'invented actual component')
        jsoncase('shared types changed without consumer review','contracts/shared/types.v1.schema.json',lambda j:j['$defs']['Key'].update(maxLength=256),'Shared types changed without retained consumer compatibility review')
        jsoncase('false production authorization','context/reconciliation/development-readiness-audit.json',lambda j:j.update(production_development_authorized=True),'Unproven production/runtime/database readiness promotion')
        jsoncase('inaccessible specified text contrast','context/ui-tokens.json',lambda j:j['themes']['light'].update(text='#ffffff'),'UI text contrast')
        if (root/'context/reconciliation/phase0-approved-file-changes.json').exists():
            jsoncase('existing dependency version changed','package-lock.json',lambda j:j['packages']['node_modules/next'].update(version='16.4.2'),'Unapproved existing dependency resolution')
            jsoncase('direct dependency silently added','package.json',lambda j:j['dependencies'].update(unapproved_parser='1.0.0'),'Unapproved direct dependency change')
            jsoncase('schema added to package exception','context/reconciliation/phase0-approved-file-changes.json',lambda j:j['files'].append({'path':'prisma/schema.prisma'}),'Unexpected Phase0 protected-file exception')
            jsoncase('reviewed package fingerprint weakened','context/reconciliation/phase0-approved-file-changes.json',lambda j:j['files'][0].update(reviewed_sha256='0'*64),'Protected source/schema/migration drift package.json')
    report={'status':'PASS' if all(r['rejected'] for r in results) else 'FAIL','total':len(results),'cases':results,'scope':'Negative static/wire/model checks only; injected fake feature files test detection. No real producer/provider/DB/RLS/runtime was exercised.'}
    print(json.dumps(report,indent=2));return not all(r['rejected'] for r in results)
if __name__=='__main__':raise SystemExit(main())
