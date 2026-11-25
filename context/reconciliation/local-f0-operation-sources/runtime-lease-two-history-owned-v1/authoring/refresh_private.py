"""Refresh private archive/held data only. Never sets source approvals."""
from pathlib import Path
import hashlib,json,shutil
OUT=Path(__file__).resolve().parent;TASK=OUT.parent;ROOT=OUT/'future-root'
ARCHIVE='context/reconciliation/local-f0-operation-sources/runtime-lease-two-history-owned-v1'
VAL='context/reconciliation/local-f0-runtime-lease-two-history-owned-v1-source-validation.json'
FIVE=('execute_local_f0_runtime_lease_two_history_owned_v1_20261123.py','local_f0_runtime_lease_two_history_owned_v1_operation_steps.py','prepare_local_f0_runtime_lease_two_history_owned_v1_plan.py','check_local_f0_runtime_lease_two_history_owned_v1_operation.py','pin_local_f0_runtime_lease_two_history_owned_v1_plan_20261123.py')
def sha(b):return hashlib.sha256(b).hexdigest()
def enc(v):return(json.dumps(v,sort_keys=True,indent=2,allow_nan=False)+'\n').encode()
def write(path,raw):
 path=Path(path)
 if path.exists()and path.read_bytes()!=raw:
  h=OUT/'author-history'/('root-before-'+str(len(list((OUT/'author-history').glob('*')))))
  h.mkdir(parents=True);(h/path.name).write_bytes(path.read_bytes())
 path.parent.mkdir(parents=True,exist_ok=True);path.write_bytes(raw)
# The two accepted preflights were not in the original source13 graph. Capture
# their already-reviewed hashes before using them in this new owning graph.
extras={'scripts/sql-review/catalog-text-preflight.sql':'f1cab9adf94fe5aa2452f34213eea43cf4ecfe35c9ce5f5289486b7d4f859823','scripts/sql-review/catalog-acl-preflight.sql':'7018c8f415923533dc461b212a0df0f9a0f4144457e410c4505c9322df4647f4'}
for n,h in extras.items():
 raw=(TASK/'runtime-lease-two-history-owned-v1-FINAL-frozen-author-20261123/future-root'/n).read_bytes();assert sha(raw)==h
 p=OUT/'preserved-before-implementation/extra-reviewed'/n
 if not p.exists():p.parent.mkdir(parents=True,exist_ok=True);p.open('xb').write(raw)
 write(ROOT/n,raw)
archive=ROOT/ARCHIVE;archive.mkdir(parents=True,exist_ok=True)
fixtures={'native.json':('native-before.json','e2bc04014b3f3d57ac6669d3364cc15162d923f1fd29ccb782bdc809f7a861f8'),'oracle-results.json':('oracle-results.json','d7f91fb358b73d3f36acde73ec730c41259009c1e0f06931ded2a7d44510f995'),'acl-preflight.json':('acl-preflight.json','b1dffe67c99d83c46073c8db1f5e14bbda1b5dc0ed053be56d56a67a6018f3c8'),'text-preflight.json':('text-preflight.json','176676da1274c55ec6f8800089b61d1c5249c44ed52b3ecfbcf2c8edf6a3cda1'),'ledger.json':('ledger-observation.json','5a3d33491366fb9587bcc4a167efa4e38bda170b7b3291c022f28676dbdd94b3')}
for target,(name,h)in fixtures.items():
 raw=(archive/'unit-fixtures'/target).read_bytes();assert sha(raw)==h
 write(archive/'unit-fixtures'/target,raw)
write(archive/'unit-fixtures/SCOPE.json',enc({'scope':'UNIT_ONLY_CLOSED_HISTORICAL_OBSERVATION_FIXTURES_NOT_EXPECTATIONS','no_runtime_qualification':True,'new_expected_is_independently_source_compiled':True}))
for n in FIVE:write(archive/(n+'.txt'),(OUT/n).read_bytes())
for p in(OUT/'preserved-before-implementation/ACTUAL_PRIMITIVE').rglob('*'):
 if p.is_file():write(archive/'primitive11'/p.relative_to(OUT/'preserved-before-implementation/ACTUAL_PRIMITIVE'),p.read_bytes())
for n in ('runtime_lease_two_history_owned_v1_private_source_plan_20261123.json','runtime_lease_two_history_owned_v1_Root_plan_ACK_20261123.json','runtime_lease_two_history_owned_v1_transport_plan_addendum_20261123.json','runtime_lease_two_history_owned_v1_Root_transport_addendum_ACK_20261123.json','runtime_lease_two_history_owned_v1_independent_transport_plan_HOLD_closure_20261123.json','runtime_lease_two_history_v1_independent_code_security_source_review_20261123.json','runtime_lease_two_history_v1_independent_actual_login_ACL_addendum_20261123.json'):
 write(archive/'plan-bindings'/n,(TASK/n).read_bytes())
for p in OUT.glob('*.txt'):write(archive/'authoring'/p.name,p.read_bytes())
for n in('build_private.py','refresh_private.py','preserve_successor.py','successor-before-preservation.json','before-preservation.json','incorporate_Root_source13_metadata.py','Root-source13-incorporation.json'):write(archive/'authoring'/n,(OUT/n).read_bytes())
for n in('bounded-correction-addendum.json','no-receipt-aligned-addendum.json','forced-remote-exec-addendum.json','direct-auth-deadline-inspection.json'):write(archive/'hold-correction'/n,(OUT/n).read_bytes())
write(archive/'hold-correction/hold_correction_probes.py.txt',(OUT/'hold_correction_probes.py').read_bytes())
write(archive/'hold-correction/forced_remote_exec_probes.py.txt',(OUT/'forced_remote_exec_probes.py').read_bytes())
write(archive/'hold-correction/historical_direct_auth_deadline_inspection_probe.py.txt',(OUT/'direct_auth_deadline_inspection_probe.py').read_bytes())
for p in(OUT/'bindings').glob('*.json'):write(archive/'hold-correction'/p.name,p.read_bytes())
old=TASK/'runtime-lease-two-history-owned-v1-FINAL-frozen-author-20261123'
write(archive/'hold-correction/original834-freeze-reference.json',enc({'schema':'workinants.original834-immutable-reference.v1','root':str(old),'manifest_sha256':sha((old/'FREEZE-MANIFEST.json').read_bytes()),'author_delivery_sha256':'e69889e4c13de2ec26edae1176059d3f5eb78166b461df272619db859c069c3d','files':834,'original_source_and_all_checks_preserved':True,'duplicate_preserved_corpus_copied':False}))
base={p.relative_to(ROOT).as_posix():sha(p.read_bytes())for p in ROOT.rglob('*')if p.is_file()and not p.relative_to(ROOT).as_posix().startswith(('node_modules/',ARCHIVE+'/'))and p.relative_to(ROOT).as_posix()!=VAL and '__pycache__'not in p.parts}
write(archive/'source-inputs.json',enc({'schema':'workinants.two-history-owned-source-inputs.v1','files_sha256':dict(sorted(base.items())),'source_gates':'PENDING','runtime':'NOT_RUN'}))
files={p.relative_to(ROOT).as_posix():sha(p.read_bytes())for p in archive.rglob('*')if p.is_file()}
runtime={**base,**{ARCHIVE+'/'+n+'.txt':sha((OUT/n).read_bytes())for n in FIVE}}
value={'schema':'workinants.two-history-owned-source-validation.v1','status':'INACTIVE_SOURCE_AWAITING_DISTINCT_REVIEW','operator_sources_sha256':{n:sha((OUT/n).read_bytes())for n in FIVE},'source_files_sha256':dict(sorted(runtime.items())),'archive_files_sha256':dict(sorted(files.items())),'independent_source_review':{'decision':'PENDING'},'Root_source_review':{'decision':'PENDING'},'runtime':'NOT_RUN','Posture':'D','business_assertions_qualified':0}
write(ROOT/VAL,enc(value))
print(json.dumps({'status':'PRIVATE_PENDING_GRAPH_REFRESHED','source_inputs':len(base),'archive_files':len(files),'runtime_sources':len(runtime),'five':len(FIVE),'source_gates':'PENDING','runtime':'NOT_RUN'}))
