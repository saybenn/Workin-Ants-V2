#!/usr/bin/env python3
"""Directive 005 deterministic architecture/context boundaries. Not production qualification."""
import hashlib
import json
import re
import runpy
import sys
from collections import Counter
from pathlib import Path
from urllib.parse import unquote
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(Path(__file__).parent))

def markdown_targets(text):
    text=re.sub(r'```.*?```','',text,flags=re.S)
    starts=re.finditer(r'\]\(',text)
    for match in starts:
        pos=match.end()
        if pos<len(text) and text[pos]=='<':
            end=text.find('>',pos+1)
            if end!=-1:yield text[pos+1:end]
            continue
        depth=1;chars=[]
        while pos<len(text) and depth:
            ch=text[pos]
            if ch=='(' :depth+=1
            if ch==')':
                depth-=1
                if not depth:break
            chars.append(ch);pos+=1
        if not depth:yield ''.join(chars).split(' "',1)[0]

def boundary_findings(root, manifest):
    findings=[];module_ids={m for l in manifest['candidate_lanes'] for m in l['modules']}
    modules=json.loads((root/'prisma/deep modules and schemas.json').read_text())
    schemas=(root/'prisma/schema.prisma').read_text();models=set(re.findall(r'^model (\w+) ',schemas,re.M))
    owners={model:m['id'] for m in modules for model in m['schemasOwnedResponsibleForOver'] if model in models}
    delegates={model[0].lower()+model[1:]:owner for model,owner in owners.items()}
    scanned=0
    for p in sorted((root/'features').rglob('*')):
        if p.suffix not in ['.ts','.tsx','.js','.jsx']:continue
        scanned+=1;rel=p.relative_to(root/'features');owner=rel.parts[0]
        if owner not in module_ids:findings.append(str(p.relative_to(root))+': unregistered feature owner');continue
        s=p.read_text()
        for foreign in re.findall(r'(?:from\s*|import\s*\()?[\'\"]@/features/([^/]+)/(?:infrastructure|repositories?|domain)(?:/|[\'\"])',s):
            if foreign!=owner:findings.append(str(p.relative_to(root))+': cross-owner private import '+foreign)
        for delegate in re.findall(r'\b(?:prisma|tx|db)\.(\w+)\.',s):
            if delegate in delegates and delegates[delegate]!=owner:findings.append(str(p.relative_to(root))+': foreign source repository '+delegate)
        if re.search(r'\b(?:prisma|tx|db)\s*\[',s):findings.append(str(p.relative_to(root))+': dynamic source dispatcher')
        if re.search(r'\b(?:function|const)\s+(?:isAdmin|isPremium|hasPremiumAccess|isBlocked|authorizeAnyResource|featureQueue)\b',s):findings.append(str(p.relative_to(root))+': duplicated local authority/entitlement/Hold/queue helper')
        if 'SUPABASE_SERVICE_ROLE_KEY'in s and ('"use client"'in s or "'use client'"in s):findings.append(str(p.relative_to(root))+': server credential in client feature')
    return findings,scanned

def inspect(root=ROOT):
    read=lambda p:json.loads((root/p).read_text());errors=[];metrics={}
    try:
        wire=runpy.run_path(str(root/'scripts/check-shared-contracts.py'))['inspect'](root)
        errors.extend('Wire qualification: '+e for e in wire['errors'])
    except (ValueError,KeyError,TypeError) as exc:
        errors.append('Contract schema/fixture invalid: '+str(exc))
    c=read('context/shared/contracts/contract-catalog.json')['contracts'];by={x['id']:x for x in c};workflows=read('context/workflows/platform-workflows.json')['workflows'];wf={w['id']:w for w in workflows};lanes=read('context/reconciliation/parallel-lane-manifest.json');qual=read('context/reconciliation/shared-operation-contract-status.json')['contracts']
    if len(c)!=132 or len(by)!=132:errors.append('Missing/duplicated Shared Operation')
    for x in c:
        id=x['id']
        for w in x['workflows']:
            if w not in wf or id not in wf[w]['operations']:errors.append(id+': broken contract/workflow backlink')
        doc=root/'context/shared/contracts'/f'{id}.md'
        if not doc.is_file():errors.append(id+': missing individual specification')
        elif any(('## '+letter+'.') not in doc.read_text() for letter in 'ABCDEFGH'):errors.append(id+': incomplete A–H purpose/context/interface/recovery/qualification')
    eventnames={e for m in read('context/reconciliation/authority-event-review.json')['modules'].values() for e in m['producer']}
    for w in workflows:
        if len(w['steps'])!=3 or not w['guards'] or not w['failure_recovery']:errors.append(w['id']+': incomplete lifecycle workflow')
        for id in w['operations']:
            if id not in by or w['id'] not in by[id]['workflows']:errors.append(w['id']+': missing contract/backlink')
        if set(w['registered_events'])-eventnames:errors.append(w['id']+': unregistered event')
        if w['qualified_runtime']:errors.append(w['id']+': unproven runtime qualification')
        for p in w['owner_architectures']:
            if not (root/p).is_file():errors.append(w['id']+': missing source owner architecture')
    if set(wf)!={f'WF-{i:02}' for i in range(1,14)}:errors.append('Incomplete platform journey inventory')
    states={x['id']:x for x in qual}
    for x in c:
        id=x['id'];q=states.get(id,{})
        if q.get('parallel_status')!=x['qualification']['final_disposition']:errors.append(id+': qualification ledger/catalog mismatch')
        if q.get('runtime_implementation_qualification')!='NOT_QUALIFIED':errors.append(id+': unsupported runtime promotion')
        if q.get('parallel_status')=='FROZEN_FOR_IMPLEMENTATION':errors.append(id+': current evidence scope cannot authorize freeze')
        if not q.get('qualification_evidence'):errors.append(id+': missing qualification evidence')
    # Declared SH synchronous dependencies must terminate; async/recovery never become startup waits.
    components=runpy.run_path(str(root/'scripts/check-platform-convergence.py'))['components']
    pairs=[(x['id'],d['operation']) for x in c for d in x['dependencies'] if d['kind']=='LOCAL_OR_PORT_CONTRACT']
    cycles=components(pairs)
    if cycles:errors.append('Shared Operation synchronous dependency cycle '+str(cycles))
    # Canonical model/ID/source hashes stay fixed for this no-migration readiness pass.
    baseline=read('context/reconciliation/directive005-preserved-source-baseline.json')
    for p,sha in baseline['sha256'].items():
        if not (root/p).is_file() or hashlib.sha256((root/p).read_bytes()).hexdigest()!=sha:errors.append('Protected source/schema/migration drift '+p)
    all_modules={m['id'] for m in read('prisma/deep modules and schemas.json')};assigned=[m for l in lanes['candidate_lanes'] for m in l['modules']]
    if Counter(assigned)!=Counter(all_modules):errors.append('Candidate lanes missing/duplicate Module ownership')
    roots=[]
    for l in lanes['candidate_lanes']:
        if l['authorized'] or l['status']!='CANDIDATE_ONLY':errors.append(l['id']+': unapproved parallel activation')
        for p in l['owned_file_roots']:roots.append((l['id'],p))
        if not l['schema_policy'] or not l['shared_contract_policy'] or not l['independent_tests'] or not l['merge_checkpoint']:errors.append(l['id']+': incomplete lane qualification/migration guard')
    for i,(a,p) in enumerate(roots):
        if any(p.startswith(shared) or shared.startswith(p) for shared in lanes['integration_owned_roots']):errors.append(a+': candidate owns shared integration path '+p)
        for b,q in roots[i+1:]:
            if a!=b and (p.startswith(q) or q.startswith(p)):errors.append('Parallel file ownership overlaps '+a+' '+b+' '+p)
    if lanes['actual_concurrent_implementation_authorized']:errors.append('Unapproved concurrent implementation')
    findings,scanned=boundary_findings(root,lanes);errors+=findings
    required=['context/architecture.md','context/build-plan.md','context/parallel-development-plan.md','context/code-standards.md','context/library-docs.md','context/ui-tokens.md','context/ui-rules.md','context/ui-registry.md','context/progress-tracker.md','context/context-map.md','AGENTS.md','CLAUDE.md','context/reconciliation/development-readiness-report.md']
    current_docs=[root/p for p in required]+list((root/'context/shared/contracts').glob('*.md'))+list((root/'context/workflows').glob('*.md'))
    link_count=0
    for p in current_docs:
        if not p.is_file():errors.append('Missing essential context '+str(p.relative_to(root)));continue
        text=p.read_text()
        if p.name=='context-map.md':text=text.split('## Current inventory note')[0]
        for target in markdown_targets(text):
            if target.startswith(('https:','http:','mailto:','#','app:','sandbox:')):continue
            path=unquote(target.split('#')[0])
            if not path:continue
            link_count+=1
            if not (p.parent/path).resolve().exists():errors.append(str(p.relative_to(root))+': broken current context link '+target)
    audit_path=root/'context/reconciliation/development-readiness-audit.json'
    if audit_path.exists():
        audit=read('context/reconciliation/development-readiness-audit.json')
        if audit['production_development_authorized'] or audit['parallel_implementation_authorized'] or audit['runtime_qualified_contracts'] or audit['frozen_contracts'] or audit['database_posture']!='D':errors.append('Unproven production/runtime/database readiness promotion')
        if audit['classification']!='NOT_READY':errors.append('Current evidence cannot certify autonomous production readiness')
    ui=read('context/ui-registry.json')
    for comp in ui['components']:
        if comp['actual_path'] and not (root/comp['actual_path']).is_file():errors.append(comp['id']+': invented actual component')
        if comp['status']=='COMPLETE':errors.append(comp['id']+': unproven UI completion')
    if ui['substantial_ui_implementation_authorized']:errors.append('Substantial UI activation without qualification')
    cold=read('tests/context/cold-start-cases.json')['cases']
    for task in cold:
        if task['workflow'] not in wf or set(task['contracts'])-set(wf[task['workflow']]['operations']):errors.append(task['id']+': cold-start contract/workflow route mismatch')
        for file in task['required_context']:
            if not (root/file).is_file():errors.append(task['id']+': missing cold-start authority '+file)
        if not task['critical_constraint'] or 'production feature and parallel lane are blocked' not in task['expected_current_action']:errors.append(task['id']+': unsafe cold-start action')
    # Color arithmetic checks specified tokens only, not a rendered accessibility certification.
    tokens=read('context/ui-tokens.json')
    def luminance(h):
        rgb=[int(h[i:i+2],16)/255 for i in [1,3,5]];rgb=[v/12.92 if v<=.04045 else ((v+.055)/1.055)**2.4 for v in rgb];return sum(a*b for a,b in zip(rgb,[.2126,.7152,.0722]))
    contrast=[]
    for theme,colors in tokens['themes'].items():
        for fg,bg in tokens['required_contrast_pairs']:
            a,b=sorted([luminance(colors[fg]),luminance(colors[bg])]);ratio=(b+.05)/(a+.05);contrast.append({'theme':theme,'pair':[fg,bg],'ratio':round(ratio,2)})
            if ratio<tokens['minimum_normal_text_contrast']:errors.append(theme+': UI text contrast '+fg+'/'+bg)
    metrics={'contracts':len(c),'workflows':len(wf),'cold_start_routes':len(cold),'candidate_lanes':len(lanes['candidate_lanes']),'authorized_parallel_lanes':0,'synchronous_contract_cycles':cycles,'current_context_links_checked':link_count,'feature_source_files_scanned':scanned,'specified_token_contrast_pairs':len(contrast),'dispositions':dict(Counter(x['qualification']['final_disposition'] for x in c))}
    return {'errors':errors,'metrics':metrics,'token_contrast':contrast,'scope':'Static ownership/workflow/context/schema and executable wire/reference assertions. No real producer/consumer, framework, database, RLS, provider, Privacy executor or full rendered UI proof. Empty feature-source inventory is reported explicitly, not runtime boundary certification.'}

if __name__=='__main__':
    result=inspect();print(json.dumps(result,indent=2));raise SystemExit(bool(result['errors']))
