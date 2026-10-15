#!/usr/bin/env python3
"""Check the reviewed R068/R069 propagation, not runtime event delivery."""
import hashlib
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ARCH = '## WA-R068 / WA-R069 — Authority facts and committed event obligations'
PLAN = '## WA-R068 / WA-R069 — Authority/event qualification sequence'


def inspect(root=ROOT):
    base = root / 'context/reconciliation'
    review = json.loads((base / 'authority-event-review.json').read_text())
    registry = (base / 'authority-event-contracts.md').read_text()
    errors = []
    event_table = registry.split('## WA-R069 — Committed fact registry and subscribers')[1].split('## Reward qualification')[0]
    if hashlib.sha256(event_table.encode()).hexdigest() != review['registry_sha256']:
        errors.append('Registry changed: review producer/subscriber semantics before updating evidence')
    paths = re.findall(r'^- `([^`]+)`: `([^`]+)`; `([^`]+)`', registry, re.M)
    if {p[0] for p in paths} != set(review['modules']):
        errors.append('Review coverage differs from registered Modules')
    producers = {}
    for line in event_table.splitlines():
        if line.startswith('| ') and '.v1 |' in line:
            owner, names, _, _ = [v.strip() for v in line.split('|')[1:-1]]
            for event in names.split(' / '):
                if event in producers:
                    errors.append(f'Duplicate registered event: {event}')
                producers[event] = owner
    for owner, arch, plan in paths:
        source = (root / arch).read_text()
        sequence = (root / plan).read_text()
        if source.count(ARCH) != 1 or sequence.count(PLAN) != 1:
            errors.append(f'{owner}: missing or duplicated integrated appendix')
            continue
        block = source.split(ARCH)[1].split('\n## ')[0]
        actual = {'producer': [], 'consumer': []}
        mode = None
        for line in block.splitlines():
            if line == 'Producer obligations:':
                mode = 'producer'
            elif line == 'Consumer obligations:':
                mode = 'consumer'
            elif line.startswith('- `') and mode:
                actual[mode].extend(re.findall(r'[a-z_]+\.[a-z_]+\.v1', line.split('`')[1]))
        expected = review['modules'][owner]
        for role in actual:
            if sorted(actual[role]) != sorted(expected[role]):
                errors.append(f'{owner}: {role} registrations differ from reviewed routes')
        canonical = sorted(e for e, p in producers.items() if p == owner)
        if sorted(actual['producer']) != canonical:
            errors.append(f'{owner}: producer list differs from canonical registry')
        for event in actual['consumer']:
            if event not in producers:
                errors.append(f'{owner}: unknown event {event}')
        for required in ['source revision', 'missing/stale/unavailable', 'outbox', 'fingerprint', 'tombstones', 'correction', 'notification intents']:
            if required not in block:
                errors.append(f'{owner}: missing {required} obligation')
        if 'authority-event-contracts.md' not in sequence.split(PLAN)[1]:
            errors.append(f'{owner}: plan does not bind the canonical appendix')
    action_table = registry.split('## WA-R069 — Committed')[0]
    for line in action_table.splitlines():
        if not line.startswith('| ') or len(line.split('|')) != 7:
            continue
        owner, *fields = [v.strip() for v in line.split('|')[1:-1]]
        if owner not in review['modules']:
            continue
        arch = next(a for o, a, _ in paths if o == owner)
        block = (root / arch).read_text().split(ARCH)[1].split('\n## ')[0]
        for field in fields:
            if field not in block:
                errors.append(f'{owner}: R068 action/facts/assurance differs from registry')
    pending = json.loads((base / 'lane-reports/authority-events-pending-propagation.json').read_text())
    for appendix in pending['appendices']:
        heading = appendix['append'].strip().splitlines()[0]
        if (root / appendix['path']).read_text().count(heading) != 1:
            errors.append(f"Missing/duplicated transfer appendix: {appendix['path']}")
    return {'errors': errors, 'modules': len(paths), 'events': len(producers),
            'preserved_coordinated_appendices': len(pending['appendices']),
            'scope': 'Static reviewed registrations and authority propagation; no runtime, RLS, provider or interface-freeze claim.'}


if __name__ == '__main__':
    result = inspect()
    print(json.dumps(result, indent=2))
    raise SystemExit(bool(result['errors']))
