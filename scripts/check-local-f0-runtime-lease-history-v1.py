"""Focused source-only suite. No Docker/database/network process is authorized."""
from pathlib import Path
import runpy,unittest
if __name__=='__main__':
    values=runpy.run_path(str(Path(__file__).parent/'sql-review/test_runtime_lease_effective_catalog_v1.py'))
    result=unittest.TextTestRunner(verbosity=2).run(unittest.defaultTestLoader.loadTestsFromTestCase(values['SourceChecks']))
    raise SystemExit(0 if result.wasSuccessful()else 1)
