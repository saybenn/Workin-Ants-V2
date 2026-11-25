from pathlib import Path
import json,hashlib,sys
sys.dont_write_bytecode=True
T=Path(r'C:\Users\elijr\.codex\visualizations\2026\11\09\01a1be05-aeb3-7f42-b0f4-6c5e46dc669f');R=Path(__file__).resolve().parent;Q=R/'exclusive';A=T/'customer-stale-predecessor-owned-v1-first-code-private-20261123';O=T/'customer-stale-predecessor-owned-v1-private-20261123';Bdir=T/'customer-stale-predecessor-owned-v1-auth-closure-private-20261123';sha=lambda b:hashlib.sha256(b).hexdigest()
D=json.loads((A/'frozen-author-delivery.json').read_bytes());idx=json.loads((A/'frozen-index.json').read_bytes());before=json.loads((Q/'before-author-preservation.json').read_bytes())
scopes=[('author433',idx['files_sha256'],None),('copy433',{str(Path(n).relative_to(A)):h for n,h in idx['files_sha256'].items()},Q),('candidate159',D['Root_files_sha256'],Q/'workinants-correction-pass'),('prepared364',D['all_prepared_Root_files_sha256'],Q/'workinants-correction-pass'),('five',D['external_five_sha256'],Q),('child115',before['child_current_files_sha256'],Q/'workinants-correction-pass'),('original_basis1521',before['Root_files_sha256'],O/'workinants-correction-pass'),('Read13five',before['Read13_basis_five_sha256'],O/'preserved-read13-base'),('oldA374',json.loads((O/'frozen-index.json').read_bytes())['files_sha256'],None),('oldB402',json.loads((Bdir/'frozen-index.json').read_bytes())['files_sha256'],None)]
results={}
for label,m,base in scopes:
 bad=[]
 for n,h in m.items():
  try:
   if sha((Path(n)if base is None else base/n).read_bytes())!=h:bad.append(n)
  except OSError as e:bad.append({'path':n,'exception_class':type(e).__name__})
 results[label]={'files':len(m),'bad':bad}
assert all(not r['bad']for r in results.values()),results
report={'schema':'workinants.CSP1-C-independent-source-map-barrier.v1','entry433_author_and_copy_matched':True,'support_scope_correction':'Legacy Read13five not included in partial C copy; check original preserved basis instead. Initial path assumption preserved as check_source_maps_initial_scope.py; current433/159/364/115 all matched on first attempt.','current_check':results,'operator_sources_sha256':D['external_five_sha256'],'Root_LS_Git_gates_services_resources_untouched':True,'runtime':'NOT_RUN','Posture':'D'}
raw=(json.dumps(report,indent=2)+'\n').encode();p=R/'source-map-check.json';p.open('xb').write(raw);print(json.dumps({'status':'PASS','sha256':sha(raw),'maps':{k:r['files']for k,r in results.items()}}),flush=True)

