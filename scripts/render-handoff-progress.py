#!/usr/bin/env python3
"""Render integration metrics from canonical ledgers; never infer interface freeze."""
import json
import re
from collections import Counter
from pathlib import Path
BASE = Path(__file__).resolve().parents[1] / 'context/reconciliation'
index = json.loads((BASE / 'handoff-families.json').read_text())
rows = json.loads((BASE / 'handoff-adjudication.json').read_text())['records']
families = index['families']
counts = Counter(r['review_status'] for r in rows)
unfinished = {f['canonical_family'] for f in families if f['integration_status'] not in {'APPLIED', 'CLOSED_BY_EXISTING_RULING'}}
scheduled = {f['canonical_family'] for f in families if f['canonical_family'] in unfinished and f.get('platform_convergence', {}).get('architecture_route') == 'RESOLVED'}
architectural = unfinished - scheduled
external = {f['canonical_family'] for f in families if f['classification'] == 'EXTERNAL_REQUIREMENT'}
rulings = re.findall(r'^## (WA-R\d+)\b', (BASE / 'platform-architecture-rulings.md').read_text(), re.M)
metrics = {
    'raw_pending': counts['PENDING'], 'raw_partial': counts['PARTIAL'],
    'family_candidates': len(families),
    'normalized_families': len({f['canonical_family'] for f in families}),
    'unresolved_architecture_families': len(architectural),
    'scheduled_readiness_families': len(scheduled),
    'external_requirement_families': len(external),
    'unresolved_families': len(unfinished | external),
    'closed_existing_ruling': sum(r.get('closure_basis') == 'EXISTING_RULING' and r['review_status'] == 'ADJUDICATED' for r in rows),
    'closed_deduplication': sum(r.get('closure_basis') == 'DEDUPLICATION' and r['review_status'] == 'ADJUDICATED' for r in rows),
    'new_rulings': sum(int(r.split('R')[1]) >= 40 for r in rulings),
    'ai_resolved_families': len({f['canonical_family'] for f in families if f['integration_status'] == 'APPLIED' and f['classification'] in {'AI_RESOLVED', 'AI_RESOLVED_WITH_TRADEOFF'}} - unfinished),
    'ai_resolved_with_product_judgment_families': len({f['canonical_family'] for f in families if f['integration_status'] == 'APPLIED' and f['classification'] == 'AI_RESOLVED_WITH_PRODUCT_JUDGMENT'} - unfinished),
    'duplicate_facets_collapsed': len(families) - len({f['canonical_family'] for f in families}),
    'product_questions': len({f['product_question'] for f in families if f.get('product_question')}),
}
(BASE / 'normalization-metrics.json').write_text(json.dumps(metrics, indent=2) + '\n')
text = '# Handoff adjudication coverage\n\nP01–P19 approved and binding. Canonical dispositions live in handoff-adjudication.json and applied rulings in platform-architecture-rulings.md. Grouping is not closure; ADJUDICATED includes scoped external requirements.\n\n## Current metrics\n\n'
text += '\n'.join(f'- {k}: {v}' for k,v in metrics.items())
text += f'\n\nFull ledger: {counts["ADJUDICATED"]} adjudicated, {counts["PARTIAL"]} partial, {counts["PENDING"]} pending ({len(rows)} total). New-ruling count is since the normalization baseline (WA-R040 onward). Original 323-record coverage is preserved. Deduplication means verified alias closure, not just merging concern groups.\n\n'
text += 'Scheduled readiness families retain partial source records for uncompleted plan/harness/runtime obligations; architectural route resolution is not implementation closure.\n\n'
text += '## Canonical family facets\n\n| Evidence family | Canonical concern | Records | Classification | Integration |\n|---|---|---:|---|---|\n'
for f in families:
    text += f'| {f["id"]} — {f["title"]} | {f["canonical_family"]} | {len(f["records"])} | {f["classification"]} | {f["integration_status"]} |\n'
text += '\n## Remaining work\n\n'
for f in families:
    if f['integration_status'] not in {'APPLIED','CLOSED_BY_EXISTING_RULING'}:
        text += f'- **{f["id"]}:** {f["remaining"]}\n'
text += '\nBridge evidence is separately inventoried in bridge-catalog.json/md; extraction does not imply bilateral reconciliation or freeze. No product implementation, external approval, provider qualification or deployment is certified here.\n'
(BASE / 'handoff-adjudication.md').write_text(text)
print(json.dumps(metrics, indent=2))
