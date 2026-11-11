#!/usr/bin/env python3
"""Refresh current review-source fingerprints only. Never generate SQL or connect."""
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REC = ROOT / 'context/reconciliation'
path = REC / 'database-candidate-manifest.json'
manifest = json.loads(path.read_text(encoding='utf-8'))
manifest.update(
    directive='P0-C-02_OWNER_EXECUTION_AMENDMENT',
    original_candidate_commit='879336673f4c0408276ea8d31ddbc508fa8f0d9c',
    original_candidate_tree='8af073cb833bedb92524a1ffef4b9f10b07b08f0',
    correction_branch='codex/p0c-candidate-corrections-2026-10-31',
    correction_ids=['B010-01','B010-02','B010-03'],
    historical_validation_record='context/reconciliation/checkpoint-010-validation.json',
    historical_native_record='context/reconciliation/database-candidate-native-validation.json',
    current_native_record='context/reconciliation/database-candidate-corrections-native-validation.json',
    source_amendment_directive='P0-C-03A',
    targeted_review_base_commit='e363ad45dfad76d2a4ffbd0cd84ef0c01d24e966',
    current_review_directive='context/reconciliation/directives/brain-directive-p0-c-03a.md',
    current_sql_draft_manifest='context/reconciliation/foundation-sql-draft-manifest.json',
    scope='Candidate source packet; pre-generation flags belong to historical P0-C-02, not the separate current SQL draft stage.',
)
paths = set(manifest['files_sha256']) | {
    'context/reconciliation/database-candidate-corrections-first-replay-selection.json',
    'context/reconciliation/checkpoint-010-first-replay-selection.original.json',
    'context/reconciliation/phase0-foundation-status.json',
    'vercel.json',
    'scripts/check-handoff-adjudication.py',
    'scripts/check-phase0-negative.py',
    'context/reconciliation/database-candidate-corrections-validation-attempt-1.json',
    'context/reconciliation/database-candidate-corrections-validation-72e7673.json',
    'context/reconciliation/database-candidate-corrections-native-validation-72e7673.json',
    'context/reconciliation/directives/brain-review-72e7673-targeted-completion.md',
    'scripts/database-candidate-correction-rules.py',
    'scripts/refresh-database-candidate-fingerprints.py',
    'context/reconciliation/database-candidate-corrections.md',
    'context/reconciliation/database-candidate-corrections-native-validation.json',
    'context/reconciliation/database-candidate-corrections-native-validation-8917e20.json',
    'context/reconciliation/directives/brain-directive-p0-c-03a.md',
    'context/reconciliation/foundation-sql-verifier-access.json',
    'context/reconciliation/foundation-sql-scope-policy.json',
}
validation = 'context/reconciliation/database-candidate-corrections-validation.json'
if (ROOT / validation).exists():
    paths.add(validation)
manifest['files_sha256'] = {p:hashlib.sha256((ROOT/p).read_bytes()).hexdigest() for p in sorted(paths)}
path.write_text(json.dumps(manifest, indent=2)+'\n', encoding='utf-8', newline='\n')
print(json.dumps({'status':'REFRESHED_REVIEW_FINGERPRINTS','files':len(paths),'ddl_generated':False}))
