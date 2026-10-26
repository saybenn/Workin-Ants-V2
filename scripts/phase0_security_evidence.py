"""Verify the bounded dependency diff and recorded qualification; never a live audit."""
import hashlib
import json


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def inspect_change_review(root, previous):
    errors = []
    approved = {}
    try:
        record = json.loads((root/'context/reconciliation/phase0-security-file-changes.json').read_text())
        authority = 'context/reconciliation/directives/brain-directive-007-resumption.md'
        if record['authority'] != authority or digest(root/authority) != record['authority_sha256']:
            errors.append('Dependency remediation authority mismatch')
        if record['baseline_commit'] != '6261595e5e6daedf94bda5b6c7c5b19f736023d8':
            errors.append('Dependency remediation baseline mismatch')
        old_hashes = {f['path']: f['reviewed_sha256'] for f in previous['files']}
        historical = json.loads((root/'context/reconciliation/phase0-foundation-validation.json').read_text())
        old_hashes['.node-version'] = historical['foundation_source_sha256']['.node-version']
        if len(record['files']) != 3 or {f['path'] for f in record['files']} != {'package.json', 'package-lock.json', '.node-version'}:
            errors.append('Unexpected dependency remediation file exception')
        for f in record['files']:
            if f['path'] not in old_hashes or f['previous_sha256'] != old_hashes[f['path']]:
                errors.append('Dependency remediation previous file mismatch')
            elif digest(root/f['path']) != f['reviewed_sha256']:
                errors.append('Reviewed dependency file drift '+f['path'])
            else:
                approved[f['path']] = f['reviewed_sha256']
        package = json.loads((root/'package.json').read_text())
        original_text = record['previous_package_text']
        if hashlib.sha256(original_text.encode()).hexdigest() != old_hashes['package.json']:
            errors.append('Dependency remediation manifest preimage mismatch')
        original = json.loads(original_text)
        expected = {
            ('dependencies', 'next'): ('16.2.6', '16.4.3'),
            ('devDependencies', 'eslint-config-next'): ('16.2.6', '16.4.3'),
            ('dependencies', '@prisma/client'): ('^7.8.0', '7.10.1'),
            ('devDependencies', 'prisma'): ('^7.8.0', '7.10.1'),
        }
        revised = json.loads(json.dumps(original))
        for (section, name), (before, after) in expected.items():
            if original[section].get(name) != before:
                errors.append('Dependency remediation declaration baseline mismatch '+name)
            revised[section][name] = after
        revised['engines']['node'] = '24.22.x'
        if package != revised:
            errors.append('Unapproved direct dependency or package metadata change')
        lock = json.loads((root/'package-lock.json').read_text())['packages']
        for section in ['dependencies', 'devDependencies']:
            if lock[''][section] != package[section]:
                errors.append('Dependency remediation root lock mismatch '+section)
        if lock['']['engines'] != package['engines'] or (root/'.node-version').read_text().strip() != '24.22.1':
            errors.append('Dependency remediation runtime pin mismatch')
        for name, version in [('next','16.4.3'),('eslint-config-next','16.4.3'),('prisma','7.10.1'),('@prisma/client','7.10.1')]:
            if lock['node_modules/'+name]['version'] != version:
                errors.append('Dependency remediation installed resolution mismatch '+name)
        if not record['lock_changes']:
            errors.append('Missing reviewed dependency resolution diff')
        for change in record['lock_changes']:
            path = change['path']
            actual = lock.get(path)
            after = change['after']
            if (actual is None) != (after is None) or (actual is not None and actual != after):
                errors.append('Reviewed lock entry drift '+path)
    except (OSError, ValueError, KeyError, TypeError) as exc:
        errors.append('Invalid dependency remediation review: '+str(exc))
    return {'errors': errors, 'approved': approved if not errors else {}}


def inspect_qualification(root, evidence):
    errors = []
    try:
        commands = {c['id']: c for c in evidence['commands']}
        for name in ['clean_install','lint','typecheck','build','http_smoke','schema_validate','audit_full','audit_production','dependency_graph','runtime_security']:
            if commands.get(name, {}).get('exit_code') != 0:
                errors.append('Missing dependency requalification command '+name)
        if evidence['toolchain']['node'] != 'v24.22.1' or evidence['toolchain']['npm'] != '11.9.0':
            errors.append('Dependency requalification toolchain mismatch')
        if not evidence['clean_install_lifecycle_scripts_enabled']:
            errors.append('Dependency requalification lifecycle scripts disabled')
        if evidence['status'] != 'PASS' or evidence['dependency_security_gate'] != 'PASS_KNOWN_ADVISORIES_REMEDIATED':
            errors.append('Dependency requalification not passed')
        if evidence['http_smoke']['total'] < 47 or evidence['http_smoke']['status'] != 'PASS':
            errors.append('Missing affected HTTP/security regressions')
        for key in ['audit_full','audit_production']:
            file = root/evidence['audit_files'][key]['path']
            raw = file.read_bytes()
            audit = json.loads(raw)
            if hashlib.sha256(raw).hexdigest() != evidence['audit_files'][key]['sha256']:
                errors.append('Dependency audit fingerprint mismatch '+key)
            totals = audit.get('metadata',{}).get('vulnerabilities',{})
            if audit.get('error') or audit.get('vulnerabilities') != {} or totals.get('total') != 0 or any(v != 0 for v in totals.values()):
                errors.append('Dependency audit has findings or incomplete result '+key)
        if evidence.get('database_contacted') or evidence.get('runtime_shared_operations_qualified'):
            errors.append('Dependency audit cannot qualify database or owner runtime')
        if len(evidence.get('installed_guidance', [])) < 4:
            errors.append('Missing installed-version guidance review')
    except (OSError, ValueError, KeyError, TypeError) as exc:
        errors.append('Invalid dependency requalification evidence: '+str(exc))
    return errors
