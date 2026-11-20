"""Exclusive before-edit preservation of the held V4 candidate and review."""
from pathlib import Path
from datetime import datetime,timezone
import json,hashlib
T=Path(__file__).resolve().parent;R=T/'workinants-correction-pass';D=T/'restore-v4-transaction-options-fix2-before-author-20261120'
sha=lambda raw:hashlib.sha256(raw).hexdigest()
assert not D.exists()
delivery=json.loads((T/'restore_bound_evidence_v4_frozen_source_plan_20261120.json').read_bytes());assert sha((T/'restore_bound_evidence_v4_frozen_source_plan_20261120.json').read_bytes())=='6935ff067a38c4eecda590a630c5b2c99237f45afe74ab9297abbc28d72759d8'
prior=Path(delivery['freeze']['path']);raw=prior.read_bytes();assert sha(raw)=='7e29837b6973b82fcda74fa916e6aad961b38a1aa66052a9d282671577478619';frozen=json.loads(raw);assert len(frozen['snapshots_sha256'])==312
sources={}
for relative,wanted in frozen['snapshots_sha256'].items():
 path=prior.parent/'files'/relative;raw=path.read_bytes();assert sha(raw)==wanted;sources['prior312/'+relative]=path
sources['prior312/freeze-manifest.json']=prior
for name,wanted in delivery['five_sha256'].items():
 path=T/name;assert sha(path.read_bytes())==wanted;sources['live-five/'+name]=path
V='context/reconciliation/local-f0-restore-bound-evidence-v4-source-validation.json';record=json.loads((R/V).read_bytes());assert sha((R/V).read_bytes())=='2b1a871644ba5bf704798da3f663d7851c55f3f1e30ac3e492533cc9f220ed3a';assert len(record['archive_files_sha256'])==129
for relative,wanted in record['archive_files_sha256'].items():
 path=R/relative;assert sha(path.read_bytes())==wanted;sources['original129/'+relative]=path
sources['original129/'+V]=R/V
required={
 'restore_bound_evidence_v4_independent_source_review_20261120.json':'23698acc74ce85e0095b339ff1de115c90c7235f3c4d2a055642e8843dce26e6',
 'restore_v4_independent_transaction_classifier_probe_20261120.json':'832e93e7659bb4132687c41bf1fadc1662c5184ab922f6a0f66f8d2630a7fa81',
 'restore_v4_independent_selected_checks_20261120.json':'fe5a93f3ea73b472831e7026c0501d55bc696a1d1a412cf04ddceb3e6720c08b',
 'restore_v4_transaction_options_fix2_Root_ACK_20261120.json':'6961dc75736afd7c3ae3fb47c465e520159eeab1d130cf0b6d61a79d6a2de55b'}
for name,wanted in required.items():assert sha((T/name).read_bytes())==wanted;sources['reviews/'+name]=T/name
for name in ('restore_bound_evidence_v4_frozen_source_plan_20261120.json','restore_bound_evidence_v4_source_author_review_20261120.json','restore_v4_independent_probe_v2_20261120.py','restore_v4_independent_probe_20261120.py','restore_v4_independent_probe_setup_stop_20261120.json','check_restore_bound_evidence_v4_focused_20261120.py','check_restore_bound_evidence_v4_source_gates_20261120.py','check_restore_bound_evidence_v4_composed_20261120.py','restore_bound_v4_envelope_helpers.py.txt','restore_bound_v4_envelope_tests.py.txt','restore_bound_v4_stateful_transport.py.txt','refresh_restore_bound_evidence_v4_source_20261120.py'):
 sources['reviews/'+name]=T/name
preservation=json.loads((T/'restore-bound-evidence-v4-before-author-20261120/completed-preservation.json').read_bytes())
for name,wanted in preservation['protected_files_sha256'].items():assert sha(Path(name).read_bytes())==wanted,('PROTECTED_SOURCE_DRIFT',name)
D.mkdir();snapshots={}
for name,path in sorted(sources.items()):
 raw=path.read_bytes();dest=D/name;dest.parent.mkdir(parents=True,exist_ok=True)
 with dest.open('xb') as stream:stream.write(raw)
 snapshots[name]=sha(raw)
value={'schema':'workinants.restore-v4-transaction-options-fix2-before-author.v1','recorded_at_utc':datetime.now(timezone.utc).isoformat(),'snapshots_sha256':snapshots,'snapshots':len(snapshots),'prior312_verified':True,'original129_and_validation_verified':True,'protected1410_verified':True,'authority_sha256':required,'source_changes_before_preservation':False,'runtime':'NOT_RUN','Posture':'D'}
raw=(json.dumps(value,indent=2)+'\n').encode()
with (D/'preservation.json').open('xb') as stream:stream.write(raw)
print(json.dumps({'preservation':str(D/'preservation.json'),'sha256':sha(raw),'snapshots':len(snapshots),'source_changes':False}))
