"""Static Fix3 test/history preparation only; no suite or external process."""
from pathlib import Path
import hashlib,json
T=Path(__file__).resolve().parent;R=T/'workinants-correction-pass';D=T/'restore-v4-custom-namespace-fix3-before-author-20261120';A='context/reconciliation/local-f0-operation-sources/restore-bound-evidence-v4';V='context/reconciliation/local-f0-restore-bound-evidence-v4-source-validation.json'
sha=lambda raw:hashlib.sha256(raw).hexdigest()
old=json.loads((D/'original270'/V).read_bytes());assert len(old['archive_files_sha256'])==270
for relative,wanted in old['archive_files_sha256'].items():
 raw=(D/'original270'/relative).read_bytes();assert sha(raw)==wanted;dest=R/A/'preserved-held-v4-fix2'/Path(relative).relative_to(A);dest.parent.mkdir(parents=True,exist_ok=True)
 if dest.exists():assert dest.read_bytes()==raw
 else:dest.write_bytes(raw)
dest=R/A/'preserved-held-v4-fix2/source-validation.json';raw=(D/'original270'/V).read_bytes()
if dest.exists():assert dest.read_bytes()==raw
else:dest.write_bytes(raw)
reviews={'independent-source-HOLD.json':'restore_bound_evidence_v4_independent_source_review_fix2_20261120.json','45-custom-probe.json':'restore_v4_fix2_independent_classifier_probe_20261120.json','independent-checks.json':'restore_v4_fix2_independent_selected_checks_20261120.json','version-qualification.json':'restore_v4_fix2_custom_namespace_version_qualification_20261120.json','Root-ACK.json':'restore_v4_custom_namespace_fix3_Root_ACK_20261120.json','before-author-preservation.json':None,'prior-delivery.json':'restore_bound_evidence_v4_frozen_source_plan_fix2_20261120.json','prior-author.json':'restore_bound_evidence_v4_source_author_review_fix2_20261120.json','prior-freeze-manifest.json':None}
for name,source in reviews.items():
 path=D/'preservation.json' if name=='before-author-preservation.json' else D/'prior453/freeze-manifest.json' if name=='prior-freeze-manifest.json' else D/'reviews'/source;raw=path.read_bytes();dest=R/A/'reviews/fix3'/name;dest.parent.mkdir(parents=True,exist_ok=True)
 if dest.exists():assert dest.read_bytes()==raw
 else:dest.write_bytes(raw)
path=T/'check_restore_bound_evidence_v4_focused_20261120.py';text=path.read_text(encoding='utf8');marker="if __name__=='__main__':unittest.main(verbosity=2)"
if 'class CustomNamespaceFix3Tests(' not in text:
 assert text.count(marker)==1;text=text.replace(marker,(T/'restore_bound_v4_custom_namespace_fix3_tests.py.txt').read_text(encoding='utf8')+'\n'+marker);compile(text,str(path),'exec');path.write_text(text,encoding='utf8',newline='\n')
record=json.loads((R/V).read_bytes());record.update(source_version='bound-evidence-v4-fix3',status='CUSTOM_NAMESPACE_FIX3_PENDING_OFFLINE_AND_SAME_INDEPENDENT_ROOT_REVIEW',classifier_fix3={'finding':'RESTORE-V4-CUSTOM-GUC-NAMESPACE-02','Root_ACK_sha256':'0547cc8738050974ac6fc83d98b54a95779180614e2c68c511033cc7ac79239a','held_review_sha256':'1c4f2e792bd6469a3ce34408aa87dfccf9cacf6f9b50296eb076b0a44be6f1cc','custom45_probe_sha256':'78af420710aca8854b9380114a57716edc2816beb28f79e449bf1efd3f9b293c','before_author_sha256':'5c4c42cf1254956650a8e55538eab525b49f0a614f95a78c149571fdebf90950','bounded_delta':'Require complete unqualified transaction name before keyword control classification; all other predicates unchanged','runtime_parser_dependency_added':False})
(R/V).write_text(json.dumps(record,indent=2)+'\n',encoding='utf8',newline='\n');print('FIX3_STATIC_TEST_HISTORY_PREPARED_NO_TESTS_RUN')
