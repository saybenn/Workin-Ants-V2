"""Correct only the probe's assumption that two backend SQL selectors differ."""
from pathlib import Path
import hashlib
TASK=Path(__file__).resolve().parent
old=TASK/'probe_nativebd4d_safety_resource_global_20261119.py';source=old.read_text()
needle="  selectors=[s for s in ('GLOBAL_BACKENDS','FINALIZATION_BACKENDS','ORIGINAL_GRANTOR_FINALIZATION','FINALIZATION_RESULT')if ns['_required_safety_text'](s)==input]\n  assert len(selectors)==1\n  selector=selectors[0];calls.append(selector)"
assert source.count(needle)==1
source=source.replace(needle,"  selector=('GLOBAL_BACKENDS','FINALIZATION_BACKENDS','ORIGINAL_GRANTOR_FINALIZATION','FINALIZATION_RESULT')[len(calls)]\n  assert ns['_required_safety_text'](selector)==input\n  calls.append(selector)")
source=source.replace("nativebd4d_safety_resource_global_source_probe_20261119.json","nativebd4d_safety_resource_global_source_probe_v2_20261119.json")
needle="raw=(json.dumps(record,indent=2)+'\\n').encode();path="
assert source.count(needle)==1
source=source.replace(needle,"record['initial_probe_harness_interruption']={'source_sha256':'"+hashlib.sha256(old.read_bytes()).hexdigest()+"','cause':'Probe wrongly required unique text across GLOBAL_BACKENDS and FINALIZATION_BACKENDS, which intentionally share identical SQL; corrected only mock selector dispatch ordering. Old three NameError reproductions completed before control assertion; no runtime/source file edited.'}\n"+needle)
exec(compile(source,str(old),'exec'),{'__name__':'__main__','__file__':str(__file__)})
