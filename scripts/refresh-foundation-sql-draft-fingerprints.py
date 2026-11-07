#!/usr/bin/env python3
"""Refresh P0-C-03A source fingerprints only. No SQL generator, driver or network.

Run candidate refresh first. Historical records are immutable inputs; this script
partitions their old input hashes into preserved and explicitly revised sources.
The validation record is separate to avoid circular self-fingerprinting.
"""
import hashlib
import json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
REC=ROOT/'context/reconciliation'
baseline=json.loads((REC/'foundation-sql-draft-manifest-8917e20.json').read_text())
def sha(p):return hashlib.sha256((ROOT/p).read_bytes()).hexdigest()
preserved={};revised={};changes={}
for p,old in baseline['preserved_reviewed_inputs_sha256'].items():
    current=sha(p)
    if old==current:preserved[p]=current
    else:
        revised[p]=current
        changes[p]={'reviewed_sha256':old,'corrected_sha256':current,'authority':'P0-C-03A source correction; see technical review and retained directive'}
sources=set(baseline['draft_source_sha256'])|{
    'scripts/refresh-foundation-sql-draft-fingerprints.py',
    'scripts/check-foundation-sql-corrections.py',
    'scripts/sql-review/foundation-service-authority.sql',
    'scripts/sql-review/foundation-verification.sql',
    'scripts/sql-review/foundation-bootstrap-finalize.sql',
    'context/reconciliation/foundation-sql-verifier-access.json',
    'context/reconciliation/foundation-sql-scope-policy.json',
    'context/reconciliation/directives/brain-directive-p0-c-03a.md',
    'context/reconciliation/foundation-sql-draft-manifest-8917e20.json',
    'context/reconciliation/foundation-sql-draft-validation-8917e20.json',
    'context/reconciliation/foundation-sql-generation-8917e20.json',
}
outputs=list(baseline['outputs_sha256'])+['review-output/foundation-bootstrap-finalize.review.sql']
manifest={
    'directive':'P0-C-03A',
    'reviewed_baseline':'8917e2035622017eccd14c99ad7fd2b55740163f',
    'original_drafting_input_baseline':baseline['reviewed_baseline'],
    'branch':baseline['branch'],
    'stage':'CORRECTED_SOURCE_AND_SQL_DRAFTS_PENDING_BRAIN_RE_REVIEW__EXECUTION_HELD',
    'source_corrections_authorized':True,'sql_draft_generated':True,
    'execution_approved':False,'database_contacted':False,'sql_executed':False,
    'adopted':False,'runtime_qualified':False,'database_posture':'D',
    'database_tests':'451_NOT_RUN','selected_replay_tests':'94_NOT_RUN',
    'source_candidate_manifest_scope':'Historical P0-C-02 candidate flags remain scoped to source review; this separate manifest records the current revised SQL drafts. Authorized input deltas are explicit, not called preserved.',
    'preserved_reviewed_inputs_sha256':dict(sorted(preserved.items())),
    'revised_inputs_sha256':dict(sorted(revised.items())),
    'authorized_input_changes':dict(sorted(changes.items())),
    'outputs_sha256':{p:sha(p) for p in outputs},
    'draft_source_sha256':{p:sha(p) for p in sorted(sources)},
    'physical_tables':{'candidate_model_tables':40,'private_sql_only_identity_tables':2},
    'migration_history':'ONE_FUTURE_PRISMA_APPLICATION_STREAM_NOT_ACTIVATED',
    'bootstrap':'SEPARATE_ENVIRONMENT_SCOPE; ORIGINAL_GRANTOR_FINALIZES_AFTER_SUCCESS_OR_FAILURE',
    'review_findings':{'DRAFT-01':'SOURCE_ADDRESSED_NOT_RUNTIME_QUALIFIED','DRAFT-02':'SOURCE_ADDRESSED_NOT_RUNTIME_QUALIFIED','DRAFT-03':'SOURCE_ADDRESSED_NOT_RUNTIME_QUALIFIED','first_write':'SOURCE_ADDRESSED','installation_authority':'SOURCE_ADDRESSED','authorization_and_consent_scope':'SOURCE_ADDRESSED','customer_messages_and_result_versions':'SOURCE_ADDRESSED','worker_completion_and_lease':'SOURCE_ADDRESSED','reservation_release':'SOURCE_ADDRESSED'},
    'remaining_gates':['Brain exact corrected-source approval','Separately authorized disposable identity/image/actions and actual installation/replay','Real Identity/issuer/owner/worker adapters and later P0-D/E/F qualification','Usage period/reconciliation and Privacy completion adapters remain denied'],
    'parser':baseline['parser'],
    'validation_record':'context/reconciliation/foundation-sql-draft-validation.json',
    'validation_scope':'Exact offline outputs separately retained; no circular manifest/report fingerprint or database claim.',
    'publication':'One corrected child on existing branch; Git/GitHub verification is reported separately after update. No main merge or force-push.'
}
(REC/'foundation-sql-draft-manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
print(json.dumps({'status':'REFRESHED_SOURCE_FINGERPRINTS','preserved':len(preserved),'revised':len(revised),'outputs':len(outputs),'database_contacted':False}))
