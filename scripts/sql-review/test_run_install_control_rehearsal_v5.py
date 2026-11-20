"""Additional V4 namespace tripwires; no processes, databases or network."""
import ast,runpy,unittest
from pathlib import Path
R=Path(__file__).resolve().parents[2]
class BindingTests(unittest.TestCase):
 def test_new_transport_exact_five_and_old_tuple_rejects(self):
  old=runpy.run_path(str(R/'scripts/install_independent_review_protocol_v1.py'));new=runpy.run_path(str(R/'scripts/install_independent_review_protocol_v2.py'));self.assertEqual(len(new['OPERATORS']),5);self.assertTrue(all('owned_parity_v4'in n for n in new['OPERATORS']));self.assertFalse(set(old['OPERATORS'])&set(new['OPERATORS']))
  f=runpy.run_path(str(R/'scripts/test_install_independent_review_protocol_v2.py'));raws,_=f['fixture']();identity=new['decode'](raws[new['IDENTITY']],True);self.assertEqual(new['identity'](identity),identity);identity['operator_sources_sha256']={n:'d'*64 for n in old['OPERATORS']}
  with self.assertRaises(new['Held']):new['identity'](identity)
 def test_authority_and_deadlines_stay_frozen(self):
  p=runpy.run_path(str(R/'scripts/install_independent_review_protocol_v2.py'));w=runpy.run_path(str(R/'scripts/sql-review/watch-install-independent-review-v3.py'));self.assertEqual(p['TIMEOUT'],240);self.assertEqual(w['AUTHORITY_SHA'],'6c1474dc12a603b07346fff014c8ab8bd15dec5be0b972ec1d504342115ba48f');self.assertIn('220',(R/'scripts/sql-review/watch-install-independent-review-v3.py').read_text())
if __name__=='__main__':unittest.main(verbosity=2)
