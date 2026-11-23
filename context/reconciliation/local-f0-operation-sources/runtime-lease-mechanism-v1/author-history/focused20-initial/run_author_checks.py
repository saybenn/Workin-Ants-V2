"""Private author runner; no production/service access."""
from pathlib import Path
import argparse, io, json, time, unittest
p=argparse.ArgumentParser();p.add_argument('name');p.add_argument('tests',nargs='*');a=p.parse_args()
out=Path(__file__).resolve().parent/'author-history'/a.name;out.mkdir()
for source in Path(__file__).resolve().parent.glob('*.py'):(out/source.name).write_bytes(source.read_bytes())
stream=io.StringIO();t=time.monotonic()
names=a.tests or ['check_local_f0_lease_mechanism_v1_operation.Case']
suite=unittest.TestSuite(unittest.defaultTestLoader.loadTestsFromName(n)for n in names)
r=unittest.TextTestRunner(stream=stream,verbosity=2).run(suite)
(out/'actual.log').write_text(stream.getvalue(),encoding='utf8',newline='\n')
v={'tests':r.testsRun,'failures':len(r.failures),'errors':len(r.errors),'seconds':time.monotonic()-t,'exit_code':0 if r.wasSuccessful()else 1}
(out/'outcome.json').write_text(json.dumps(v,indent=2)+'\n',encoding='utf8')
print(stream.getvalue());print(json.dumps(v));raise SystemExit(v['exit_code'])

