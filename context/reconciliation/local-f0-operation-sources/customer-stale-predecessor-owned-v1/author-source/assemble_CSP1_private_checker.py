import ast,hashlib,json,pathlib,textwrap
A=pathlib.Path(__file__).parent;T=A.parent;P=A/'workinants-correction-pass';ARCH='context/reconciliation/local-f0-operation-sources/customer-stale-predecessor-owned-v1';sha=lambda b:hashlib.sha256(b).hexdigest()
source=T/'check_local_f0_app_write_two_owned_resource_v1_operation.py';raw=source.read_bytes();assert sha(raw)=='31fd7030921eb8ea43b59839968a88a0f76282152dacdbaacf73ba9df513c549'
node=next(n for n in ast.parse(raw).body if isinstance(n,ast.ClassDef)and n.name=='ProcessModel');methods=[n for n in node.body if isinstance(n,ast.FunctionDef)and n.name in('response','image_value','container','process','_process')]
body='class PrimitiveCommandModel:\n'+''.join(textwrap.indent(ast.unparse(n),' ')+'\n'for n in methods)
pins={'native-before':'24cf2f60e9c6a396d53b8f897b0aa6feea6b8498a1f231eb0241fc6e157d0eb0','ledger-observation':'5a3d33491366fb9587bcc4a167efa4e38bda170b7b3291c022f28676dbdd94b3','oracle-preflight':'e64b96e2f73e7a6d369d61c09301dc7c986c08bcd1cf95af06c6ab9756bcbe66','oracle-results':'d7f91fb358b73d3f36acde73ec730c41259009c1e0f06931ded2a7d44510f995','oracle-closure':'89067a06862e197fd49f3aed1e3f18bfc93d6a6c2035f9cdfc85a57036257ab9','acl-preflight':'b1dffe67c99d83c46073c8db1f5e14bbda1b5dc0ed053be56d56a67a6018f3c8','text-preflight':'176676da1274c55ec6f8800089b61d1c5249c44ed52b3ecfbcf2c8edf6a3cda1'}
for n,h in pins.items():
 src=T/'workinants-correction-pass/context/reconciliation/local-f0-run-assets/fcab2e9-read13-0b7c519e/evidence'/(n+'.json');data=src.read_bytes();assert sha(data)==h;dst=P/ARCH/'OFFLINE-model-inputs'/(n+'.json');dst.parent.mkdir(parents=True,exist_ok=True);dst.write_bytes(data)
head='''"""Focused CSP1 source/transport/whole-lifecycle mocks. No real external boundary."""
import ast,hashlib,io,json,os,queue,re,runpy,shutil,socket,subprocess,tempfile,threading,time,types,unittest
from pathlib import Path
from contextlib import ExitStack,redirect_stdout,redirect_stderr
from copy import deepcopy
from unittest.mock import patch,Mock
from pglast import ast as pgast,parse_sql,parser
TASK=Path(__file__).resolve().parent;ROOT=TASK/'workinants-correction-pass'
FIVE=('execute_local_f0_customer_stale_predecessor_v1_20261120.py','local_f0_customer_stale_predecessor_v1_operation_steps.py','prepare_local_f0_customer_stale_predecessor_v1_plan.py','check_local_f0_customer_stale_predecessor_v1_operation.py','pin_local_f0_customer_stale_predecessor_v1_plan_20261120.py')
ARCHIVE='context/reconciliation/local-f0-operation-sources/customer-stale-predecessor-owned-v1';VALIDATION='context/reconciliation/local-f0-customer-stale-predecessor-owned-v1-source-validation.json'
GATES=('independent_source_review','independent_owned_resource_review','independent_safety_sql_review','independent_binary_transport_review','Root_source_review')
FLAG='APPROVED_LOCAL_F0_CUSTOMER_STALE_PREDECESSOR_OWNED_V1_ATTEMPT';CID='a'*64;CANARY='CSP1_PRIVATE_PASSWORD_OPAQUE_HANDLE_STDERR_CANARY'
IMAGE='docker.io/library/postgres:17.11@sha256:996e9dc583ba9f0265a2c75547a9c95fb22c251e394749cab205a0a00e1856a1';CONFIG='sha256:eb0fb2377534e65aad04f37838956b3dfb888e1a3dd3c1acf957bc6557eb6c7d'
sha=lambda b:hashlib.sha256(b).hexdigest()
encoded=lambda v:(json.dumps(v,indent=2,allow_nan=False)+'\\n').encode()
ctx_protocol=runpy.run_path(str(ROOT/'scripts/sql-review/run-context-control-rehearsal.py'))
child_tests=runpy.run_path(str(ROOT/'scripts/check-customer-stale-predecessor-v1.py'))
ChildProcess=child_tests['Process'];ChildWorld=child_tests['World'];child_constant=child_tests['constant']
'''
head+='MODEL_CATALOG_PINS='+repr(pins)+'\n'
preserve='''
class SourcePreservation(unittest.TestCase):
 def test_exact_original_115_and_guard_source(self):
  before=json.loads((ROOT/ARCHIVE/'author-source/before-author-preservation.json').read_bytes())
  for n,h in before['child_current_files_sha256'].items():self.assertEqual(sha((ROOT/n).read_bytes()),h)
  packet=json.loads((ROOT/'review-output/customer-stale-predecessor-v1/fixtures.json').read_bytes());self.assertEqual({r['table']for r in packet['fixture_bypasses']},{'app.users','app.user_security_profiles'})
  self.assertEqual(sha((ROOT/'review-output/foundation-application.review.sql').read_bytes()),'5ae39abf991f9c189e367eb6ab6968b0ad50836bf4220ac27ef8c18306ac26ad');self.assertEqual(sha((ROOT/'context/reconciliation/foundation-sql-draft-access.json').read_bytes()),'f9d529a7fc481beea3fcb0b2307fce47c44d7168380a7e2dfab6b9be44831eea')
'''
text=head+body+'\n'+preserve+(A/'CSP1_checker_extension.py.txt').read_text()+"\nif __name__=='__main__':unittest.main()\n"
path=A/FIVE if False else A/'check_local_f0_customer_stale_predecessor_v1_operation.py';compile(text,str(path),'exec')
if path.exists()and path.read_bytes()!=text.encode():history=A/'author-history'/('checker-before-'+sha(path.read_bytes())[:12]);history.mkdir(parents=True,exist_ok=True);(history/path.name).write_bytes(path.read_bytes())
path.write_text(text,encoding='utf8',newline='\n')
print(json.dumps({'checker_sha256':sha(path.read_bytes()),'model_catalog_fixtures':len(pins)}))
