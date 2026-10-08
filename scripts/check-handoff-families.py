#!/usr/bin/env python3
"""Verify normalization coverage and prevent grouping from impersonating closure."""
import json
from collections import Counter
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
def inspect():
    base = ROOT / 'context/reconciliation'
    index = json.loads((base / 'handoff-families.json').read_text())
    rows = json.loads((base / 'handoff-adjudication.json').read_text())['records']
    by_key = {r['key']: r for r in rows}
    families = index['families']
    keys = [k for f in families for k in f['records']]
    errors = []
    if len(keys) != index['baseline_pending'] + index['baseline_partial']:
        errors.append('Baseline family coverage count differs')
    if any(v != 1 for v in Counter(keys).values()):
        errors.append('Record occurs in multiple families')
    if len({f['id'] for f in families}) != len(families):
        errors.append('Duplicate family ID')
    for f in families:
        if not f['decision'] or not f['evidence']:
            errors.append(f"{f['id']}: missing decision/evidence")
        for key in f['records']:
            r = by_key.get(key)
            if not r or r.get('normalized_family') != f['id']:
                errors.append(f'{key}: family/record mapping mismatch')
            elif f['integration_status'] == 'CLOSED_BY_EXISTING_RULING':
                if r['review_status'] != 'ADJUDICATED' or r.get('closure_basis') != 'EXISTING_RULING':
                    errors.append(f'{key}: false existing-ruling closure')
    return {'errors': errors, 'covered_records': len(keys), 'families': len(families),
            'scope': 'Coverage only; proposed family decisions do not authorize implementation.'}
if __name__ == '__main__':
    result = inspect()
    print(json.dumps(result, indent=2))
    raise SystemExit(bool(result['errors']))
