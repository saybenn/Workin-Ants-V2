"""Preserve the exact held Fix2 bytes before the bounded Fix3 predicate edit."""
from pathlib import Path
from datetime import datetime,timezone
import json,hashlib
T=Path(__file__).resolve().parent;R=T/'workinants-correction-pass';D=T/'restore-v4-custom-namespace-fix3-before-author-20261120'
sha=lambda raw:hashlib.sha256(raw).hexdigest()
assert not D.exists()
delivery_path=T/'restore_bound_evidence_v4_frozen_source_plan_fix2_20261120.json';assert sha(delivery_path.read_bytes())=='27ee3bbf01edc244a62b69e4f9304cb8fe04c69deffce733f50ce7dcbe75e368';delivery=json.loads(delivery_path.read_bytes());fp=Path(delivery['freeze']['path']);assert sha(fp.read_bytes())=='04ee4701f12ffa6118b189e54123de734d2a36d71b46623de8cf8faa4c985578';freeze=json.loads(fp.read_bytes());assert len(freeze['snapshots_sha256'])==453
sources={}
for name,wanted in freeze['snapshots_sha256'].items():
 path=fp.parent/'files'/name;assert sha(path.read_bytes())==wanted;sources['prior453/'+name]=path
sources['prior453/freeze-manifest.json']=fp
for name,wanted in delivery['five_sha256'].items():assert sha((T/name).read_bytes())==wanted;sources['live-five/'+name]=T/name
V='context/reconciliation/local-f0-restore-bound-evidence-v4-source-validation.json';raw=(R/V).read_bytes();assert sha(raw)=='6bd02ec1cef344739a8f6f6929e76658bc3d18830e5a7054b6813f32a95b1f66';record=json.loads(raw);assert len(record['archive_files_sha256'])==270
for name,wanted in record['archive_files_sha256'].items():assert sha((R/name).read_bytes())==wanted;sources['original270/'+name]=R/name
sources['original270/'+V]=R/V
required={'restore_bound_evidence_v4_independent_source_review_fix2_20261120.json':'1c4f2e792bd6469a3ce34408aa87dfccf9cacf6f9b50296eb076b0a44be6f1cc','restore_v4_fix2_independent_classifier_probe_20261120.json':'78af420710aca8854b9380114a57716edc2816beb28f79e449bf1efd3f9b293c','restore_v4_fix2_independent_selected_checks_20261120.json':'f1d0a8dd1c42520a292c57a8d4139a22b2aca98eddf93110b78fba85427a43fd','restore_v4_fix2_custom_namespace_version_qualification_20261120.json':'3968145d18113648e71d0667dba297bacf8c7c75c097e6498937e682ba85d499','restore_v4_custom_namespace_fix3_Root_ACK_20261120.json':'0547cc8738050974ac6fc83d98b54a95779180614e2c68c511033cc7ac79239a'}
for name,wanted in required.items():assert sha((T/name).read_bytes())==wanted;sources['reviews/'+name]=T/name
for name in ('restore_bound_evidence_v4_frozen_source_plan_fix2_20261120.json','restore_bound_evidence_v4_source_author_review_fix2_20261120.json','restore_v4_fix2_independent_probe_20261120.py','check_restore_bound_evidence_v4_focused_20261120.py','check_restore_bound_evidence_v4_source_gates_20261120.py','check_restore_bound_evidence_v4_composed_20261120.py','restore_bound_v4_envelope_helpers.py.txt','restore_bound_v4_transaction_options_fix2_tests.py.txt','refresh_restore_bound_evidence_v4_source_20261120.py'):
 sources['reviews/'+name]=T/name
protected=json.loads((T/'restore-bound-evidence-v4-before-author-20261120/completed-preservation.json').read_bytes())
for path,wanted in protected['protected_files_sha256'].items():assert sha(Path(path).read_bytes())==wanted,('PROTECTED_SOURCE_DRIFT',path)
D.mkdir();snapshots={}
for name,path in sorted(sources.items()):
 raw=path.read_bytes();dest=D/name;dest.parent.mkdir(parents=True,exist_ok=True)
 with dest.open('xb') as stream:stream.write(raw)
 snapshots[name]=sha(raw)
value={'schema':'workinants.restore-v4-custom-namespace-fix3-before-author.v1','recorded_at_utc':datetime.now(timezone.utc).isoformat(),'snapshots_sha256':snapshots,'snapshots':len(snapshots),'prior453_verified':True,'original270_validation_livefive_verified':True,'protected1410_verified':True,'authority_sha256':required,'source_changes_before_preservation':False,'runtime':'NOT_RUN','Posture':'D'};raw=(json.dumps(value,indent=2)+'\n').encode()
with (D/'preservation.json').open('xb') as stream:stream.write(raw)
print(json.dumps({'path':str(D/'preservation.json'),'sha256':sha(raw),'snapshots':len(snapshots),'source_changes':False}))
