"""Preserve held Root bytes and prepare only the authorized Fix2 tests/history."""
from pathlib import Path
import hashlib,json
T=Path(__file__).resolve().parent;R=T/'workinants-correction-pass';D=T/'restore-v4-transaction-options-fix2-before-author-20261120';A='context/reconciliation/local-f0-operation-sources/restore-bound-evidence-v4';V='context/reconciliation/local-f0-restore-bound-evidence-v4-source-validation.json'
sha=lambda raw:hashlib.sha256(raw).hexdigest()
record=json.loads((D/'original129'/V).read_bytes());assert len(record['archive_files_sha256'])==129
for relative,wanted in record['archive_files_sha256'].items():
 raw=(D/'original129'/relative).read_bytes();assert sha(raw)==wanted;dest=R/A/'preserved-held-v4-fix1'/Path(relative).relative_to(A);dest.parent.mkdir(parents=True,exist_ok=True)
 if dest.exists():assert dest.read_bytes()==raw
 else:dest.write_bytes(raw)
dest=R/A/'preserved-held-v4-fix1/source-validation.json';raw=(D/'original129'/V).read_bytes()
if dest.exists():assert dest.read_bytes()==raw
else:dest.write_bytes(raw)
reviews={'independent-source-HOLD.json':'restore_bound_evidence_v4_independent_source_review_20261120.json','74-vector-probe.json':'restore_v4_independent_transaction_classifier_probe_20261120.json','independent17-checks.json':'restore_v4_independent_selected_checks_20261120.json','Root-ACK.json':'restore_v4_transaction_options_fix2_Root_ACK_20261120.json','before-author-preservation.json':None,'prior-delivery.json':'restore_bound_evidence_v4_frozen_source_plan_20261120.json','prior-author.json':'restore_bound_evidence_v4_source_author_review_20261120.json','prior-freeze-manifest.json':None}
for name,source in reviews.items():
 path=D/'preservation.json' if name=='before-author-preservation.json' else D/'prior312/freeze-manifest.json' if name=='prior-freeze-manifest.json' else D/'reviews'/source;raw=path.read_bytes();dest=R/A/'reviews/fix2'/name;dest.parent.mkdir(parents=True,exist_ok=True)
 if dest.exists():assert dest.read_bytes()==raw
 else:dest.write_bytes(raw)
path=T/'check_restore_bound_evidence_v4_focused_20261120.py';text=path.read_text(encoding='utf8');marker="if __name__=='__main__':unittest.main(verbosity=2)"
if 'class TransactionOptionsFix2Tests(' not in text:
 assert text.count(marker)==1;text=text.replace(marker,(T/'restore_bound_v4_transaction_options_fix2_tests.py.txt').read_text(encoding='utf8')+'\n'+marker);compile(text,str(path),'exec');path.write_text(text,encoding='utf8',newline='\n')
value=json.loads((R/V).read_bytes());value.update(source_version='bound-evidence-v4-fix2',status='TRANSACTION_OPTIONS_FIX2_PENDING_OFFLINE_AND_SAME_INDEPENDENT_ROOT_REVIEW',classifier_fix2={'finding':'RESTORE-V4-TRANSACTION-OPTIONS-01','Root_ACK_sha256':'6961dc75736afd7c3ae3fb47c465e520159eeab1d130cf0b6d61a79d6a2de55b','held_review_sha256':'23698acc74ce85e0095b339ff1de115c90c7235f3c4d2a055642e8843dce26e6','independent74_probe_sha256':'832e93e7659bb4132687c41bf1fadc1662c5184ab922f6a0f66f8d2630a7fa81','before_author_sha256':'c801840c3eefae738a2fe8f0f2d2d18dab41ed014031572f7a13c7657e2fe858','RESET_ALL_contract':'REJECT: resets transaction defaults as well as other parameters','semantic_function_analysis':False,'runtime_parser_dependency_added':False})
(R/V).write_text(json.dumps(value,indent=2)+'\n',encoding='utf8',newline='\n')
print('FIX2_TESTS_AND_IMMUTABLE_HELD_HISTORY_PREPARED_NO_TESTS_RUN')
