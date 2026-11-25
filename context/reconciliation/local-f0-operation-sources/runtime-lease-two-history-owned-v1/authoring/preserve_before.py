from pathlib import Path
import hashlib,json,shutil,sys
TASK=Path(__file__).resolve().parent.parent
OUT=Path(__file__).resolve().parent
ROOT=TASK/'workinants-correction-pass'
FROZEN=TASK/'runtime-lease-two-history-v1-FINAL-frozen-author-20261123'
def sha(b):return hashlib.sha256(b).hexdigest()
def enc(v):return (json.dumps(v,sort_keys=True,indent=2)+'\n').encode()
bindings={
 'runtime_lease_two_history_owned_v1_private_source_plan_20261123.json':'f3c7e018e5593e2274d418d53d554bf500d74410471967ea1f00a70fba6236a1',
 'runtime_lease_two_history_owned_v1_Root_plan_ACK_20261123.json':'31be63ec575d8b1de412996f275cd88b75ac2ccb82f19b5ad6263c3cdde5e4d3',
 'runtime_lease_two_history_owned_v1_transport_plan_addendum_20261123.json':'2d265dbac091b772f6ad78a65edd05a8d992b1dd7d069a9c1628c69d4c6df552',
 'runtime_lease_two_history_owned_v1_Root_transport_addendum_ACK_20261123.json':'93ba80adf5732a9e194a23248aef739e3fa8c33db09eade5e7f5bb7e5d1054e7',
 'runtime_lease_two_history_owned_v1_independent_transport_plan_HOLD_closure_20261123.json':'00caa856ad0d86f690d63d4cf8e34899cb4a5721c574af86ed1e64b7f144c028',
 'execute_local_f0_lease_mechanism_v1_20261120.py':'8e2c2529727fd8270f709737c3129c1ad650e09c6f70914dedd0ea46354250e9',
 'runtime_lease_two_history_v1_independent_code_security_source_review_20261123.json':'d00bd399ca295888bcad2b352a33ff65bb96156d6c42e1aa8066f9f5deb64e0a',
 'runtime_lease_two_history_v1_independent_actual_login_ACL_addendum_20261123.json':'c008864146000c1977f545322eda08d79d298a50f5b040cb9a47d659379334e3'}
basis=json.loads((TASK/'runtime_lease_two_history_owned_v1_private_plan_basis_20261123.json').read_bytes())
sources={}
def capture(kind,base,n,h):
 raw=(base/n).read_bytes();assert sha(raw)==h,(kind,n)
 dest=OUT/'preserved-before-implementation'/kind/n;dest.parent.mkdir(parents=True,exist_ok=True);dest.open('xb').write(raw)
 sources[kind+'/'+n]={'source':str(base/n),'sha256':h,'bytes':len(raw)}
for n,h in bindings.items():capture('TASK',TASK,n,h)
for family in basis['accepted_families'].values():
 for n,h in family['all_five_current_sources_sha256'].items():capture('TASK',TASK,n,h)
 v=json.loads((ROOT/family['validation_path']).read_bytes())
 capture('ROOT',ROOT,family['validation_path'],family['validation_sha256'])
 for n,h in v['archive_files_sha256'].items():capture('ROOT',ROOT,n,h)
for n,h in {**basis['fixed_source_inputs_sha256'],**basis['common_safety_fixed_source_map']}.items():
 if 'ROOT/'+n not in sources:capture('ROOT',ROOT,n,h)
freeze=json.loads((FROZEN/'FREEZE-MANIFEST.json').read_bytes())
assert len(freeze['files_sha256'])==655
for n,h in freeze['files_sha256'].items():
 assert sha((FROZEN/n).read_bytes())==h,n
for p in (FROZEN/'future-root').rglob('*'):
 if p.is_file():
  q=OUT/'future-root'/p.relative_to(FROZEN/'future-root');q.parent.mkdir(parents=True,exist_ok=True);q.open('xb').write(p.read_bytes())
# Copies of accepted closed source inputs, not edits/adoption of Root.
for key,item in sources.items():
 if key.startswith('ROOT/'):
  q=OUT/'future-root'/key[5:]
  if not q.exists():q.parent.mkdir(parents=True,exist_ok=True);q.open('xb').write(Path(item['source']).read_bytes())
archive=TASK/'local-f0-linux-tooling-20261117/pinned-prisma-tools.tar.gz'
assert sha(archive.read_bytes())=='481b68ef007cf8889045a50ca3545bb8bd2f6d7290dd40ee730adf12bfd198fb'
(OUT/'support').mkdir()
shutil.copyfile(archive,OUT/'support/pinned-prisma-tools.tar.gz')
# Real accepted immutable dependency receipts: these are closed, never active V9.
ack=json.loads((TASK/'runtime_lease_two_history_owned_v1_Root_plan_ACK_20261123.json').read_bytes())
audit_path=Path(ack['actual_primitive_dependency']['independent_actual_audit']['path'])
audit=json.loads(audit_path.read_bytes())
for n,h in audit['input_files_sha256'].items():
 capture('ACTUAL_PRIMITIVE',TASK,n,h)
capture('ACTUAL_PRIMITIVE',TASK,audit_path.name,'76b2911680a7eeb1a61c809981caedfedc36759386d7d15b40fdff739ccc3013')
receipt={'schema':'workinants.two-history-owned-private-before-preservation.v1','sources':sources,'preserved_files':len(sources),'frozen655_verified':True,'frozen655_aggregate':freeze['aggregate_sha256'],'tool_archive_sha256':'481b68ef007cf8889045a50ca3545bb8bd2f6d7290dd40ee730adf12bfd198fb','Root_writes':False,'runtime':'NOT_RUN','Posture':'D'}
(OUT/'before-preservation.json').open('xb').write(enc(receipt))
print(json.dumps({'status':'EXCLUSIVE_PRESERVATION_COMPLETE','files':len(sources),'sha256':sha(enc(receipt)),'future_root':str(OUT/'future-root')}))
