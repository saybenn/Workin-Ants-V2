#!/usr/bin/env python3
"""Validate decision coverage without converting pending work into gate completion."""
import hashlib
import json
import re
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CLASSES = {'AI_RESOLVED', 'AI_RESOLVED_WITH_TRADEOFF', 'DEFERRED_IMPLEMENTATION_DETAIL',
           'EXTERNAL_REQUIREMENT', 'PRODUCT_OWNER_CHOICE'}


def source_ids(text):
    start = re.search(r'^## .*?[Uu]nresolved[^\n]*\n', text, re.M)
    if not start:
        raise ValueError('No unresolved-decision section')
    section = text[start.end():]
    end = re.search(r'^## ', section, re.M)
    if end:
        section = section[:end.start()]
    headings = list(re.finditer(r'^### ([^\n]+)', section, re.M))
    result = []
    for i, heading in enumerate(headings):
        body = section[heading.end():headings[i + 1].start() if i + 1 < len(headings) else len(section)]
        if '**Question' in body or '**Current options' in body:
            result.append(heading.group(1).split()[0].strip('`'))
    if not result:
        for line in section.splitlines():
            cells = [c.strip() for c in line.strip().strip('|').split('|')]
            if line.startswith('|') and re.match(r'^(?:CL-\d+-[UH]|U-)', cells[0]):
                result.append(cells[0].split()[0].strip('`'))
    return result


def inspect():
    errors = []
    records = json.loads((ROOT / 'context/reconciliation/handoff-adjudication.json').read_text())['records']
    expected = {}
    for path in sorted(ROOT.glob('context/reconciliation/clusters/CL-*-handoff.md')):
        source = str(path.relative_to(ROOT))
        cluster = path.name.removesuffix('-handoff.md')
        digest = hashlib.sha256(path.read_bytes()).hexdigest()
        for identifier in source_ids(path.read_text()):
            key = cluster + ':' + identifier
            if key in expected:
                errors.append(f'Duplicate source decision: {key}')
            expected[key] = (source, digest, identifier)
    if Counter(r['key'] for r in records) != Counter(expected.keys()):
        errors.append('Decision coverage differs from the ten source decision sections')
    rulings = (ROOT / 'context/reconciliation/platform-architecture-rulings.md').read_text()
    for r in records:
        if r['key'] not in expected:
            continue
        source, digest, identifier = expected[r['key']]
        if (r['source'], r['source_sha256'], r['id']) != (source, digest, identifier):
            errors.append(f"{r['key']}: source identity/fingerprint drift")
        status = r.get('review_status')
        if status not in {'PENDING', 'PARTIAL', 'ADJUDICATED'}:
            errors.append(f"{r['key']}: invalid review status")
        if status == 'PENDING' and r.get('dispositions'):
            errors.append(f"{r['key']}: pending record has a disposition")
        if status != 'PENDING' and not r.get('dispositions'):
            errors.append(f"{r['key']}: reviewed record lacks disposition")
        if status == 'PARTIAL' and not r.get('remaining'):
            errors.append(f"{r['key']}: partial record lacks remaining work")
        for d in r.get('dispositions', []):
            if d.get('classification') not in CLASSES or not d.get('decision') or not d.get('ruling'):
                errors.append(f"{r['key']}: invalid disposition")
            for ruling in re.findall(r'WA-R\d+', d.get('ruling', '')):
                if not re.search(r'^## '+re.escape(ruling)+r'\b', rulings, re.M):
                    errors.append(f"{r['key']}: missing ruling {ruling}")
            for reference in d.get('ruling', '').split('; '):
                if reference.endswith('.md') and not (ROOT / 'context/reconciliation' / reference).is_file():
                    errors.append(f"{r['key']}: missing reference {reference}")
    return {'errors': errors, 'source_decisions': len(expected),
            'review_statuses': dict(Counter(r['review_status'] for r in records)),
            'disposition_classes': dict(Counter(d['classification'] for r in records for d in r.get('dispositions', []))),
            'scope': 'Coverage and reference integrity only; ADJUDICATED includes open product/external gates, not implementation readiness.'}


if __name__ == '__main__':
    result = inspect()
    print(json.dumps(result, indent=2))
    raise SystemExit(bool(result['errors']))
