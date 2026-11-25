"""CSP1 private focused checker under construction; no real process is allowed."""
import hashlib,json,pathlib,runpy,socket,subprocess,sys,unittest
from unittest.mock import patch
TASK=pathlib.Path(__file__).parent;ROOT=TASK/'workinants-correction-pass'
class SourcePreservation(unittest.TestCase):
 def test_fixed_source_and_two_identity_only(self):
  before=json.loads((TASK/'before-author-preservation.json').read_bytes())
  for n,h in before['child_current_files_sha256'].items():self.assertEqual(hashlib.sha256((ROOT/n).read_bytes()).hexdigest(),h)
  p=json.loads((ROOT/'review-output/customer-stale-predecessor-v1/fixtures.json').read_bytes())
  self.assertEqual({x['table']for x in p['fixture_bypasses']},{'app.users','app.user_security_profiles'})
  self.assertEqual(p['fixture_run_id'],'36e9cae1-53fc-44a7-b90f-b91fb6e8d2b5')
if __name__=='__main__':unittest.main()
