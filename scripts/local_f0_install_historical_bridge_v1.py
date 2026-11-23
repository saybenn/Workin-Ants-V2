"""Validate the superseded INSTALL partial without adding it to current coverage."""
import hashlib,json
from pathlib import Path
from local_f0_read1161_evidence import _read as closed_read, EvidenceFailure as ReadFailure

PRIOR='context/reconciliation/local-f0-operation-sources/install-6850-precleanup-evidence-v1/prior671-ledger.json'
PRIOR_SHA='8b7cd04a5681dc7d2b2996c20b896dc352af67e88f968f1ccc9250f9bdda0d64'
OLD='context/reconciliation/local-f0-install-5f189aa-4b35e08b-qualified-evidence.json'
OLD_SHA='08f81059dfc828007cbf69ae08b224a6cbd82196800e30650058d128e83d8e39'
NEW='context/reconciliation/local-f0-install-0ff2a91-6850ee4c-precleanup-qualified-evidence.json'
KEY=('P0C-INSTALL-02','vector.FUNCTION-ACL-FAILURE-CLEANUP.adversarial')
ROW_SHA='0674eb3d2dca009da5eaa820d15662b608b80c9622f3c4630bc53355cb987d43'

class HistoricalInstallFailure(Exception):
    """Fixed rejection codes only."""

def need(value,code):
    if not value:raise HistoricalInstallFailure(code)

def canonical(value):
    return json.dumps(value,sort_keys=True,separators=(',',':'),ensure_ascii=False,allow_nan=False)

def validate_superseded_install_partial(root,current,execution,old_batch):
    """Keep the old closed batch complete; only the caller's current row counts."""
    try:
        need(old_batch is not None,'HISTORICAL_INSTALL_BATCH_REQUIRED')
        need(type(current)is dict and (current.get('case_id'),current.get('assertion_id'))==KEY and current.get('status')=='PASS'and current.get('evidence_path')==NEW and current.get('json_pointer')=='/claims/0','HISTORICAL_INSTALL_CURRENT_SCOPE')
        root=Path(root).resolve(strict=True)
        prior=json.loads(closed_read(root,PRIOR,PRIOR_SHA))
        need(type(prior)is dict and type(prior.get('assertions'))is list and len(prior['assertions'])==671,'HISTORICAL_INSTALL_ARCHIVED_LEDGER')
        previous=prior['assertions'][655]
        need(type(previous)is dict and (previous.get('case_id'),previous.get('assertion_id'))==KEY and previous.get('status')=='PARTIAL'and previous.get('evidence_path')==OLD and previous.get('evidence_sha256')==OLD_SHA and previous.get('json_pointer')=='/claims/14','HISTORICAL_INSTALL_PRIOR_SCOPE')
        need(hashlib.sha256(canonical(previous).encode()).hexdigest()==ROW_SHA,'HISTORICAL_INSTALL_PRIOR_HASH')
        need(type(current.get('previous_evidence'))is dict and canonical(current['previous_evidence'])==canonical(previous)and current.get('previous_evidence_sha256')==ROW_SHA and current.get('previous_evidence_preserved_at')==PRIOR,'HISTORICAL_INSTALL_EMBEDDED_HISTORY')
        need(type(execution)is dict and type(execution.get('claims'))is list and len(execution['claims'])==1,'HISTORICAL_INSTALL_NEW_CLAIM')
        claim=execution['claims'][0]
        need(type(claim)is dict and type(claim.get('prior_evidence'))is dict and canonical(claim['prior_evidence'])==canonical(previous)and claim.get('prior_evidence_sha256')==ROW_SHA,'HISTORICAL_INSTALL_NEW_HISTORY_BINDING')
        old_execution=json.loads(closed_read(root,OLD,OLD_SHA))
        old_batch.validate_claim(KEY[0],KEY[1],'PARTIAL',old_execution,root,json_pointer='/claims/14')
        return True
    except HistoricalInstallFailure:raise
    except ReadFailure:raise HistoricalInstallFailure('HISTORICAL_INSTALL_CLOSED_READ_REJECTED')from None
    except Exception:raise HistoricalInstallFailure('HISTORICAL_INSTALL_VALIDATION_REJECTED')from None
