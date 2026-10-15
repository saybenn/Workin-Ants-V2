#!/usr/bin/env python3
"""Check immutable bridge evidence coverage, not semantic compatibility."""
import hashlib
import json
from collections import Counter
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
def inspect():
    data = json.loads((ROOT / 'context/reconciliation/bridge-catalog.json').read_text())
    errors = []
    sources = {s['path']: s for s in data['sources']}
    texts = {}
    for path, source in sources.items():
        raw = (ROOT / path).read_bytes()
        texts[path] = raw.decode().splitlines(keepends=True)
        if hashlib.sha256(raw).hexdigest() != source['sha256']:
            errors.append(f'{path}: source fingerprint drift')
    ids = Counter(r['id'] for r in data['records'])
    if any(n != 1 for n in ids.values()):
        errors.append('Duplicate bridge identity')
    if len(ids) != data['coverage']['expected_records']:
        errors.append('Bridge coverage count differs')
    counts = Counter(r['source_path'] for r in data['records'])
    for path, source in sources.items():
        if counts[path] != source['expected_count']:
            errors.append(f'{path}: bridge count differs')
    profiles = {p['id'] for p in data['inherited_profiles']}
    for r in data['records']:
        raw = ''.join(texts[r['source_path']][r['source_start_line']-1:r['source_end_line']])
        if raw != r['raw_text'] or hashlib.sha256(raw.encode()).hexdigest() != r['raw_sha256']:
            errors.append(f'{r["id"]}: raw evidence drift')
        if set(r['inherited_profiles']) - profiles:
            errors.append(f'{r["id"]}: missing inherited profile')
        if r['frozen'] and not r.get('qualification_evidence'):
            errors.append(f'{r["id"]}: unsupported freeze')
    return {'errors':errors,'records':len(ids),'scope':'Source integrity only; not bilateral reconciliation.'}
if __name__ == '__main__':
    result=inspect()
    print(json.dumps(result,indent=2))
    raise SystemExit(bool(result['errors']))
