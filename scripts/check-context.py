#!/usr/bin/env python3
"""Offline structural context checks. Passing is not architectural readiness."""
import argparse
import hashlib
import json
import re
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

def inspect():
    errors, warnings = [], []
    def read(path):
        return (ROOT / path).read_text(encoding='utf-8')
    modules = json.loads(read('prisma/deep modules and schemas.json'))
    registry = json.loads(read('prisma/clusters.json'))
    clusters = [c for group in registry['clustersByType'].values() for c in group]
    ids = [m['id'] for m in modules]
    memberships = [m for c in clusters for m in c['includedDeepModules']]
    if Counter(ids) != Counter(memberships) or any(n != 1 for n in Counter(memberships).values()):
        errors.append('Module identity/membership mismatch or duplicate membership')
    routing = read('context/context-map.md')
    # This table is an explicit path index; resolve actual links, not naming guesses.
    indexed = {}
    for line in routing.splitlines():
        match = re.match(r'\| `([^`]+)` \| (CL-\d+) \|', line)
        if match:
            links = re.findall(r'\]\(<([^>]+)>\)', line)
            files = [str(Path('context') / x) for x in links if x.endswith('.md')]
            indexed[match[1]] = {'cluster': match[2], 'files': files}
    for module in ids:
        item = indexed.get(module)
        if not item or len(item['files']) != 2:
            errors.append(f'{module}: architecture/plan pair not indexed')
            continue
        expected = next(c['clusterId'] for c in clusters if module in c['includedDeepModules'])
        if item['cluster'] != expected:
            errors.append(f'{module}: path index membership differs from registry')
        for path in item['files']:
            if not (ROOT / path).is_file():
                errors.append(f'{module}: missing {path}')
    cluster_files = sorted(ROOT.glob('context/clusters/*/*.md'))
    for c in clusters:
        members = c['includedDeepModules']
        dirs = {Path(indexed[m]['files'][0]).parent.parent for m in members if m in indexed}
        if len(dirs) != 1:
            errors.append(f"{c['clusterId']}: inconsistent indexed cluster directories")
            continue
        directory = ROOT / next(iter(dirs))
        files = list(directory.glob('*.md'))
        if sum('architecture' in f.name for f in files) != 1 or sum('build-plan' in f.name for f in files) != 1:
            errors.append(f"{c['clusterId']}: expected one cluster architecture and one build plan")
    shared = read('context/shared/shared-operations.md')
    entries = []
    for match in re.finditer(r'^### (SH-\d{3}) — `([^`]+)`\n(.*?)(?=^### |^## |\Z)', shared, re.M | re.S):
        sh, name, body = match.groups()
        fields = dict(re.findall(r'^- \*\*([^*]+):\*\* (.+)$', body, re.M))
        for field in ['Plain English', 'Owner', 'Classification', 'Status', 'Boundary', 'Build rule']:
            if field not in fields:
                errors.append(f'{sh}: missing {field}')
        entries.append({'id': sh, 'name': name, **fields})
    counts = Counter(e['id'] for e in entries)
    if any(n != 1 for n in counts.values()):
        errors.append('Duplicate canonical SH heading')
    if counts and set(counts) != {f'SH-{i:03}' for i in range(1, max(int(x[3:]) for x in counts)+1)}:
        errors.append('Gap in permanent SH identity sequence')
    canonical = {e['id']: e for e in entries}
    index = {}
    for line in shared.splitlines():
        match = re.match(r'\| (SH-\d{3}) \| `([^`]+)` \| (.*?) \| (.*?) \| (.*?) \|$', line)
        if match:
            sh, name, owner, classification, status = match.groups()
            index[sh] = (name, owner, classification, status)
    for e in entries:
        if index.get(e['id']) != (e['name'], e.get('Owner'), e.get('Classification'), e.get('Status')):
            errors.append(f"{e['id']}: compact index differs from canonical entry")
    source_files = sorted(ROOT.glob('context/clusters/**/*.md'))
    unknown = []
    for path in source_files:
        for sh in set(re.findall(r'\bSH-\d{3}\b', path.read_text())):
            if sh not in canonical:
                unknown.append({'path': str(path.relative_to(ROOT)), 'id': sh})
    if unknown:
        errors.append(f'{len(unknown)} nonexistent SH references in current Cluster/Module documents')
    schema = read('prisma/schema.prisma')
    model_names = set(re.findall(r'^model (\w+) ', schema, re.M))
    model_owners = {}
    for module in modules:
        for model in module['schemasOwnedResponsibleForOver']:
            if model in model_names:
                model_owners.setdefault(model, []).append(module['id'])
    for model, owners in model_owners.items():
        if len(owners) > 1:
            errors.append(f'{model}: competing registered model owners: {owners}')
    expected_handoffs = {c['clusterId'] + '-handoff.md' for c in clusters}
    actual_handoffs = {p.name for p in ROOT.glob('context/reconciliation/clusters/CL-*-handoff.md')}
    if expected_handoffs != actual_handoffs:
        errors.append('Cluster handoff set does not match registered Clusters')
    # Check explicit single-operation consumer names; grouped headings are positional.
    for path in source_files:
        for line_number, line in enumerate(path.read_text().splitlines(), 1):
            sh_ids = set(re.findall(r'SH-\d{3}', line))
            if len(sh_ids) != 1:
                continue
            match = re.search(r'(SH-\d{3})(?:\*\*)?(?:\s*[—–:]\s*|\s+)`([a-z][A-Za-z0-9]+)`', line)
            if not match:
                continue
            entry = canonical.get(match[1])
            if entry and match[2] != entry['name']:
                # Candidate aliases are recorded explicitly by the canonical registry.
                aliases = entry.get('Candidate aliases / narrower variants', '').split('; ')
                if match[2] not in aliases:
                    errors.append(f'{path.relative_to(ROOT)}:{line_number}: {match[1]} uses noncanonical name {match[2]}')
    migrations = sorted(ROOT.glob('prisma/migrations/*/migration.sql'))
    sql = '\n'.join(p.read_text() for p in migrations)
    created = set(re.findall(r'CREATE TABLE\s+"(\w+)"\."(\w+)"', sql))
    absent = []
    for name, body in re.findall(r'^model (\w+) \{(.*?)^\}', schema, re.M | re.S):
        table = re.search(r'@@map\("([^\"]+)"\)', body)
        namespace = re.search(r'@@schema\("([^\"]+)"\)', body)
        if (namespace.group(1) if namespace else 'public', table.group(1) if table else name) not in created:
            absent.append(name)
    if absent:
        warnings.append(f'{len(absent)} mapped Prisma models lack CREATE TABLE in checked-in migration SQL; this is static coverage, not a migration replay')
    artifacts = []
    for path in sorted(ROOT.glob('context/**/*')):
        if path.is_file() and 'readiness-inventory.json' != path.name:
            artifacts.append({'path': str(path.relative_to(ROOT)), 'sha256': hashlib.sha256(path.read_bytes()).hexdigest()})
    return {'scope': 'Structural evidence only; no semantic-readiness certification', 'errors': errors, 'warnings': warnings,
            'counts': {'clusters': len(clusters), 'modules': len(modules), 'cluster_documents': len(cluster_files), 'module_documents': len(source_files)-len(cluster_files), 'handoffs': len(list(ROOT.glob('context/reconciliation/clusters/CL-*-handoff.md'))), 'shared_operations': len(entries), 'shared_statuses': dict(Counter(e.get('Status') for e in entries)), 'prisma_models': len(re.findall(r'^model ',schema,re.M)), 'prisma_enums': len(re.findall(r'^enum ',schema,re.M)), 'sql_migrations': len(migrations), 'created_tables': len(created), 'created_enums': len(re.findall(r'CREATE TYPE',sql))},
            'module_paths': indexed, 'shared_operations': entries, 'unknown_shared_references': unknown, 'models_without_table_creation': absent, 'artifact_fingerprints': artifacts}

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--json', action='store_true')
    args = parser.parse_args()
    result = inspect()
    if args.json:
        print(json.dumps(result, indent=2))
    else:
        print(json.dumps(result['counts'], indent=2))
        for severity in ['errors', 'warnings']:
            for finding in result[severity]:
                print(f'{severity.upper()}: {finding}')
        print('Structural checks ' + ('FAILED' if result['errors'] else 'PASSED') + '; semantic readiness is a separate gate.')
    raise SystemExit(bool(result['errors']))
