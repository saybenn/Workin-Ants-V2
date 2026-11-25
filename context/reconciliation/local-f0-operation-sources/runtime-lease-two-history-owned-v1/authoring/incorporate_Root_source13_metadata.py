"""Copy only Root-issued exact36 admission into the exclusive private futureRoot."""
from pathlib import Path
import hashlib,json
OUT=Path(__file__).resolve().parent;TASK=OUT.parent;ROOT=TASK/'workinants-correction-pass';FUTURE=OUT/'future-root'
def sha(raw):return hashlib.sha256(raw).hexdigest()
p=TASK/'source13_FINAL_Root_source_admission_inventory_20261123.json';raw=p.read_bytes()
assert sha(raw)=='27c55abbbe58c1cdaca1cf035e578e87a4b02684deaa1ce43971591f6fd6ec21'
v=json.loads(raw);mapping=v['files_sha256'];assert len(mapping)==36 and mapping==v['Root_files_sha256']
for name,h in mapping.items():assert sha((ROOT/name).read_bytes())==h
for name,h in v['source_files_sha256'].items():assert sha((FUTURE/name).read_bytes())==h==sha((ROOT/name).read_bytes())
history=OUT/'author-history/Root-authorized-source13-metadata-admission';history.mkdir(parents=True,exist_ok=False)
delta={}
for name,h in mapping.items():
 source=(ROOT/name).read_bytes();target=FUTURE/name
 if target.exists()and target.read_bytes()==source:continue
 if target.exists():
  old=target.read_bytes();preserved=history/name;preserved.parent.mkdir(parents=True,exist_ok=True);preserved.write_bytes(old)
  assert name=='context/reconciliation/local-f0-runtime-lease-two-history-v1-source-validation.json'
  assert sha(old)=='2dab9d5f949046836594c8a7de171c88fa6fa0a48afc505315b3769adbfd025f'
  old_sha=sha(old)
 else:old_sha=None
 target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(source);delta[name]={'before':old_sha,'after':h}
assert len(delta)==7
for name,h in mapping.items():assert sha((FUTURE/name).read_bytes())==h
for name in('source13_FINAL_Root_source_admission_inventory_20261123.json','runtime_lease_two_history_v1_Root_SOURCE13_source_review_20261123.json'):
 (history/name).write_bytes((TASK/name).read_bytes())
record={'schema':'workinants.private-Root-source13-metadata-incorporation.v1','Root_inventory_sha256':sha(raw),'changes':delta,
 'all36source_and13code_unchanged':True,'owning_source_gates':'PENDING','runtime':'NOT_RUN','Posture':'D'}
(OUT/'Root-source13-incorporation.json').write_text(json.dumps(record,sort_keys=True,indent=2)+'\n',encoding='utf8')
print(json.dumps({'incorporated_exact_Root36':True,'metadata_delta_paths':len(delta),'owning_source_gates':'PENDING','runtime':'NOT_RUN'}))
