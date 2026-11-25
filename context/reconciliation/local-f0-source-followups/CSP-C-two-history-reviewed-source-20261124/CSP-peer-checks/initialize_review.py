from pathlib import Path
import json,hashlib,shutil,sys
sys.dont_write_bytecode=True
T=Path(r'C:\Users\elijr\.codex\visualizations\2026\11\09\01a1be05-aeb3-7f42-b0f4-6c5e46dc669f')
A=T/'customer-stale-predecessor-owned-v1-first-code-private-20261123';R=Path(__file__).resolve().parent;Q=R/'exclusive';sha=lambda b:hashlib.sha256(b).hexdigest()
D=json.loads((A/'frozen-author-delivery.json').read_bytes());I=json.loads((A/'frozen-index.json').read_bytes())
assert sha((A/'frozen-author-delivery.json').read_bytes())=='2258ea5f3edc040a86ca692197d3e8a31d721c04cc930d0c48a9ae03a2dc8dae'
assert sha((A/'frozen-index.json').read_bytes())=='385c346a205a8782af95fbaecdf53844b2de73b7f3e188fb0f648335128c4508'
bad=[n for n,h in I['files_sha256'].items()if sha(Path(n).read_bytes())!=h];assert not bad,bad
shutil.copytree(A,Q)
copybad=[]
for n,h in I['files_sha256'].items():
 relative=Path(n).relative_to(A)
 if sha((Q/relative).read_bytes())!=h:copybad.append(str(relative))
assert not copybad,copybad
report={'schema':'workinants.CSP1-C-independent-initial-freeze-check.v1','delivery_sha256':sha((A/'frozen-author-delivery.json').read_bytes()),'index_sha256':sha((A/'frozen-index.json').read_bytes()),'files':len(I['files_sha256']),'author_bad':bad,'copy_bad':copybad,'operator_sources_sha256':D['external_five_sha256'],'support_interruption':'Node/exec host replaced before R existed; no operation result reused. Recovered with explicit filesystem verification.','runtime':'NOT_RUN','Posture':'D'}
raw=(json.dumps(report,indent=2)+'\n').encode();(R/'initial-freeze-check.json').open('xb').write(raw);print(json.dumps({'files':len(I['files_sha256']),'copy':str(Q),'receipt_sha256':sha(raw),'delivery_keys':[k for k in D if k not in('Root_files_sha256','all_prepared_Root_files_sha256')]}),flush=True)
