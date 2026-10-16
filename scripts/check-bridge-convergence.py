#!/usr/bin/env python3
"""Validate reviewed bridge evidence/coverage; never certify runtime semantics."""
import hashlib
import json
import re
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def inspect(root=ROOT):
    base = root / 'context/reconciliation'
    read = lambda name: json.loads((base / name).read_text())
    review = read('bridge-review-complete.json')
    catalog = read('bridge-catalog.json')
    index = read('bridge-family-index.json')
    records = {r['id']: r for r in catalog['records']}
    families = {f['id']: f for f in index['families']}
    errors = []
    for key, name in [('catalog_sha256', 'bridge-catalog.json'),
                      ('family_index_sha256', 'bridge-family-index.json')]:
        if hashlib.sha256((base / name).read_bytes()).hexdigest() != review[key]:
            errors.append(name + ': immutable baseline differs')
    covered = Counter(t['record_id'] for t in review['record_coverage'])
    if set(covered) != set(records) or any(v != 1 for v in covered.values()):
        errors.append('Missing or duplicate primary source-record coverage')
    reviewed = Counter(f['id'] for f in review['families'])
    if set(reviewed) != set(families) or any(v != 1 for v in reviewed.values()):
        errors.append('Missing or duplicate family review')
    for row in review['record_coverage']:
        rec = records.get(row['record_id'])
        if not rec:
            continue
        if row['family_id'] != index['record_to_family'][rec['id']]:
            errors.append(rec['id'] + ': wrong family mapping')
        for k in ['source_path', 'source_start_line', 'source_end_line', 'inherited_profiles']:
            if row[k] != rec[k]:
                errors.append(rec['id'] + ': source provenance changed: ' + k)
        if row['source_sha256'] != rec['raw_sha256']:
            errors.append(rec['id'] + ': source hash differs')
    all_refs = []
    rulings = (base / 'platform-architecture-rulings.md').read_text()
    evidence = review['evidence_index']
    for path, expected in evidence.items():
        target = root / path
        if not target.is_file() or hashlib.sha256(target.read_bytes()).hexdigest() != expected['sha256']:
            errors.append(path + ': reviewed owner/consumer evidence drift')
    for f in review['families']:
        source = families.get(f['id'])
        if not source:
            continue
        ids = [r['record_id'] for r in source['records']]
        all_refs.extend(f['source_record_ids'])
        if f['source_record_ids'] != ids or f['historical_directional_facets'] != source['records']:
            errors.append(f['id'] + ': lost/changed directional source facet')
        if f['frozen'] or f['contract_status'] != 'UNSTABLE':
            errors.append(f['id'] + ': unsupported contract freeze/promotion')
        if not f['assessment'] or not f['contract'] or not f['rulings']:
            errors.append(f['id'] + ': missing semantic review/binding')
        if not f.get('producers') or not f.get('consumers'):
            errors.append(f['id'] + ': missing bilateral endpoint set')
        for rule in f['rulings']:
            if not re.search(r'^## ' + re.escape(rule) + r'\b', rulings, re.M):
                errors.append(f['id'] + ': unknown ruling ' + rule)
        for e in f['owner_consumer_evidence']:
            for kind in ['architecture', 'plan']:
                if e.get(kind) and e[kind] not in evidence:
                    errors.append(f['id'] + ': unbound owner/consumer evidence')
            if f['review_kind'] == 'DOMAIN' and 'prior_review' not in f and e.get('plan'):
                arch = (root / e['architecture']).read_text()
                plan = (root / e['plan']).read_text()
                if f['id'] not in arch.split('## WA-R081–083 — Gate 4 bridge obligations')[-1]:
                    errors.append(f['id'] + ': missing owner architecture adoption')
                if f['id'] not in plan.split('## WA-R081–083 — Bridge qualification sequence')[-1]:
                    errors.append(f['id'] + ': missing consumer sequence adoption')
    if Counter(all_refs) != Counter(records.keys()):
        errors.append('Family source coverage is not one-to-one')
    if review['inherited_profiles'] != catalog['inherited_profiles']:
        errors.append('Inherited source profiles differ')
    for rail in ['CL-01', 'CL-07', 'CL-08', 'CL-09']:
        rows = review['rail_matrices'].get(rail, [])
        if not rows or any(not r['truth_and_contract'] or not r['qualification'] or not r['families'] for r in rows):
            errors.append(rail + ': incomplete rail matrix')
        if any(fid not in families for r in rows for fid in r['families']):
            errors.append(rail + ': unknown family in rail matrix')
    m = review['metrics']
    actual = {'historical_records': len(records), 'unique_source_records': len(covered),
              'families': len(reviewed), 'domain_families': 0, 'rail_families': 0,
              'domain_records': 0, 'rail_records': 0, 'inherited_profiles': len(catalog['inherited_profiles']),
              'missing_source_records': len(set(records) - set(covered)),
              'duplicate_source_records': sum(v - 1 for v in covered.values() if v > 1),
              'unreviewed_families': len(set(families) - set(reviewed)),
              'frozen_contracts': sum(bool(f['frozen']) for f in review['families'])}
    for f in review['families']:
        kind = f['review_kind'].lower()
        actual[kind + '_families'] += 1
        actual[kind + '_records'] += len(f['source_record_ids'])
    if m != actual:
        errors.append('Claimed coverage metrics differ from evidence')
    text = (base / 'cross-cluster-bridge-inventory.md').read_text()
    rows = re.findall(r'^\| (CL-\d+-B\d+) \| (BF-\d+) \|', text, re.M)
    if Counter(r for r, _ in rows) != Counter(records.keys()):
        errors.append('Human inventory source coverage differs')
    if any(index['record_to_family'][r] != f for r, f in rows if r in records):
        errors.append('Human inventory source mapping differs')
    return {'errors': errors, 'metrics': actual,
            'scope': 'Static source preservation, reviewed bindings and evidence drift only; no semantic/runtime certification.'}


if __name__ == '__main__':
    result = inspect()
    print(json.dumps(result, indent=2))
    raise SystemExit(bool(result['errors']))
