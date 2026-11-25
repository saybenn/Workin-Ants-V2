"""Exclusive successor preservation; all original834 bytes remain unchanged."""
from pathlib import Path
import hashlib,json,shutil
OUT=Path(__file__).resolve().parent;TASK=OUT.parent;OLD=TASK/'runtime-lease-two-history-owned-v1-FINAL-frozen-author-20261123'
def sha(raw):return hashlib.sha256(raw).hexdigest()
assert sha((OLD/'FREEZE-MANIFEST.json').read_bytes())=='6db06eeb2e618dd9786e0b33a6a86681a1cb98051bae29903b3316b5acf94477'
freeze=json.loads((OLD/'FREEZE-MANIFEST.json').read_bytes());assert len(freeze['files_sha256'])==834
for n,h in freeze['files_sha256'].items():assert sha((OLD/n).read_bytes())==h,n
pins={'runtime_lease_two_history_owned_v1_independent_code_security_HOLD_20261123.json':'486b5dcf17b196c428470536451fc7f2d6a92d5c0134d70b9e4cd3c280a16d7c',
'two_history_owning_HOLD_Root_bounded_correction_ruling_20261123.json':'73efbc0f5897e80788638d45f15251f88b7a4ad868c7a1c8cb8b44447f5cd910',
'two_history_prestart_API_Root_ruling_refinement_20261123.json':'faa9e55fed9796d861548635fd32333346f2d34eca12f51a49ebb2df54fbe486'}
for n,h in pins.items():assert sha((TASK/n).read_bytes())==h
assert not(OUT/'future-root').exists()
shutil.copytree(OLD/'future-root',OUT/'future-root')
(OUT/'support').mkdir();shutil.copyfile(OLD/'support/pinned-prisma-tools.tar.gz',OUT/'support/pinned-prisma-tools.tar.gz')
names=('execute_local_f0_runtime_lease_two_history_owned_v1_20261123.py','local_f0_runtime_lease_two_history_owned_v1_operation_steps.py','prepare_local_f0_runtime_lease_two_history_owned_v1_plan.py','check_local_f0_runtime_lease_two_history_owned_v1_operation.py','pin_local_f0_runtime_lease_two_history_owned_v1_plan_20261123.py','core_transport.py.txt','steps.py.txt','prepare.py.txt','checks.py.txt','pin.py.txt','build_private.py','refresh_private.py','run_checks.py','verify_private_final.py','prepare_final_held_packet.py')
for n in names:(OUT/n).open('xb').write((OLD/n).read_bytes())
(OUT/'author-history').mkdir();(OUT/'bindings').mkdir()
for n in pins:(OUT/'bindings'/n).open('xb').write((TASK/n).read_bytes())
for n in('before-preservation.json','Root-source13-incorporation.json','incorporate_Root_source13_metadata.py'):
 (OUT/n).open('xb').write((OLD/n).read_bytes())
record={'schema':'workinants.two-history-owning-successor-before-preservation.v1','original_freeze_root':str(OLD),'original_freeze_manifest_sha256':sha((OLD/'FREEZE-MANIFEST.json').read_bytes()),'original_frozen_files_verified':834,'copied_runtime_futureRoot':True,'original_preserved274_corpus':'EXACT_EXTERNAL_REFERENCE_NO_DUPLICATION','copied_genuine_archive_sha256':sha((OUT/'support/pinned-prisma-tools.tar.gz').read_bytes()),'Root_HOLD_ruling_bindings':pins,'original_five_sha256':{n:sha((OLD/n).read_bytes())for n in names[:5]},'source_gates':'PENDING','runtime':'NOT_RUN','Posture':'D'}
raw=(json.dumps(record,sort_keys=True,indent=2)+'\n').encode();(OUT/'successor-before-preservation.json').open('xb').write(raw)
print(json.dumps({'status':'SUCCESSOR_EXCLUSIVE_PRESERVATION_COMPLETE','sha256':sha(raw),'original834_verified':True,'Root_writes':False}))
