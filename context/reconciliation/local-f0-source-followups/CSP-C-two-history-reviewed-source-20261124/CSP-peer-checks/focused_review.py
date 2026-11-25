from pathlib import Path
import sys,runpy,json,hashlib,unittest,time,traceback,ast,copy
sys.dont_write_bytecode=True
R=Path(__file__).resolve().parent;Q=R/'exclusive';forbidden=[]
def audit(event,args):
 if event.startswith(('subprocess.','socket.'))or event in('os.system','os.posix_spawn','os.spawn'):forbidden.append(event);raise AssertionError('UNMOCKED_EXTERNAL_EDGE_FORBIDDEN')
sys.addaudithook(audit)
M=runpy.run_path(str(Q/'check_local_f0_customer_stale_predecessor_v1_operation.py'));extra={}
def selected_auth(self):
 rows=[]
 for index in(2,18):
  code,g,m,_=self.run_case('auth:'+str(index)+':exception');self.assertEqual(code,1);self.assertTrue(m.auth_fault_seen);self.assertTrue(g['report']['transport_closure']['transport_closure_unconfirmed']);self.assertEqual(m.finalizer_sql_calls,m.auth_dispatches_at_fault);self.assertFalse(m.vm.processes);self.assertTrue(g['report']['cleanup_actions_confirmed']);self.assertFalse(m.containers or m.volumes)
  self.assertEqual(g['report']['primary_failure'],{'stage':'AUTH_HBA'if index==2 else'AUTH_WRONG_PASSWORD','code':'PROCESS_BOUNDARY_UNEXPECTED'})
  rows.append({'index':index,'primary':g['report']['primary_failure'],'finalizer_calls':m.finalizer_sql_calls,'unknown':True,'cleanup':True})
 extra['selected_auth_both_calls']=rows
M['WholeLifecycle'].test_peer_verifier_and_second_auth_no_exit=selected_auth
class Pure(unittest.TestCase):
 def test_inverse_auth_AST_and_finite_origin_source_codes(self):
  helper=(Q/'workinants-correction-pass/scripts/sql-review/run-first-rehearsal.py').read_bytes();st=ast.parse((Q/M['FIVE'][1]).read_bytes());old=next(n for n in ast.parse(helper).body if isinstance(n,ast.FunctionDef)and n.name=='authentication_preflight');new=copy.deepcopy(next(n for n in st.body if isinstance(n,ast.FunctionDef)and n.name=='csp_owned_authentication_preflight'));new.body=new.body[7:];new.name=old.name;new.args.args=new.args.args[:2]
  class Inverse(ast.NodeTransformer):
   def visit_Call(self,n):
    n=self.generic_visit(n)
    if isinstance(n.func,ast.Name)and n.func.id=='csp_auth_read':self.assert_api(n);n.func=ast.Name(id='run',ctx=ast.Load());n.args=n.args[1:]
    elif isinstance(n.func,ast.Name)and n.func.id=='csp_auth_process':n.func=ast.Attribute(value=ast.Name(id='subprocess',ctx=ast.Load()),attr='run',ctx=ast.Load())
    return n
   def assert_api(self,n):assert isinstance(n.args[0],ast.Name)and n.args[0].id=='api'
  new=Inverse().visit(new);self.assertEqual(ast.dump(new,include_attributes=False),ast.dump(old,include_attributes=False))
  helperAst=ast.parse((Q/'workinants-correction-pass/scripts/sql-review/run-local-f0-migrate.py').read_bytes());coreAst=ast.parse((Q/M['FIVE'][0]).read_bytes());sets={}
  for n in st.body:
   if isinstance(n,ast.Assign)and isinstance(n.targets[0],ast.Name)and n.targets[0].id in('_CSP_COORDINATOR_FAILURE_CODES','_CSP_OWNED_CORE_FAILURE_CODES'):sets[n.targets[0].id]=set(ast.literal_eval(n.value.args[0]))
  def source_codes(tree):
   codes=set()
   for n in ast.walk(tree):
    if isinstance(n,ast.Call)and isinstance(n.func,ast.Name):
     position=1 if n.func.id in('require','need')else 0 if n.func.id in('HeldFailure','Stop')else None
     if position is not None and len(n.args)>position and isinstance(n.args[position],ast.Constant)and type(n.args[position].value)is str:codes.add(n.args[position].value)
   return codes
  self.assertEqual(sets['_CSP_COORDINATOR_FAILURE_CODES'],source_codes(helperAst));self.assertEqual(sets['_CSP_OWNED_CORE_FAILURE_CODES'],source_codes(coreAst));extra['inverse_AST_and_origin_code_counts']={'helper':len(sets['_CSP_COORDINATOR_FAILURE_CODES']),'core':len(sets['_CSP_OWNED_CORE_FAILURE_CODES'])}
class Result(unittest.TestResult):
 def __init__(self):super().__init__();self.rows=[];self.starts={}
 def startTest(self,t):super().startTest(t);self.starts[t.id()]=time.monotonic()
 def row(self,t,status,e=None):
  v={'method':t.id(),'status':status,'seconds':round(time.monotonic()-self.starts.get(t.id(),time.monotonic()),3)}
  if e:v.update(exception_type=e[0].__name__,frames=[{'file':Path(f.filename).name,'line':f.lineno,'function':f.name}for f in traceback.extract_tb(e[2])])
  self.rows.append(v);print(json.dumps(v),flush=True)
 def addSuccess(self,t):super().addSuccess(t);self.row(t,'PASS')
 def addError(self,t,e):super().addError(t,e);self.row(t,'ERROR',e)
 def addFailure(self,t,e):super().addFailure(t,e);self.row(t,'FAIL',e)
phase=sys.argv[1];selection=[]
if phase=='light':
 selection=[('SourcePreservation','test_exact_original_115_and_guard_source'),('PendingAndProjection','test_actual_pending_entry_before_steps_or_processes'),('PendingAndProjection','test_changed_python_and_unchanged_packet_SQL_parse')]+[('BinaryTransport',n)for n in sorted(M['BinaryTransport'].__dict__)if n.startswith('test_')]+[('pure','test_inverse_auth_AST_and_finite_origin_source_codes')]
if phase=='affected':
 selection=[('WholeLifecycle',n)for n in('test_actual_full_constructor_install_native_child_three_and_cleanup','test_original_source_code_before_closure_consequence','test_forced_remote_exec_vs_natural_return','test_inner_validated_and_preNode_contrasts','test_auth_unknown_persistent_IO_secondary_close','test_auth_completed_and_confirmed_closed_contrasts','test_peer_verifier_and_second_auth_no_exit','test_pending_current_five_and_committed_drift_before_steps')]
suite=unittest.TestSuite((Pure if c=='pure'else M[c])(n)for c,n in selection);result=Result();start=time.monotonic();suite.run(result)
report={'schema':'workinants.CSP1-C-independent-focused-same-peer-checks.v1','phase':phase,'reviewer':'/root/lease_v2_code_review','status':'PASS'if result.wasSuccessful()else'CHECK_FAILURES_PRESERVED','methods':result.testsRun,'results':result.rows,'seconds':round(time.monotonic()-start,3),'extra':extra,'measurements':M['AUTHOR_MEASUREMENTS'],'operator_sources_sha256':{n:hashlib.sha256((Q/n).read_bytes()).hexdigest()for n in M['FIVE']},'forbidden_edges_attempted':forbidden,'all_nested_process_DB_network_edges':'MOCKED_OR_AUDIT_FORBIDDEN','runtime':'NOT_RUN','Posture':'D'}
raw=(json.dumps(report,sort_keys=True,indent=2)+'\n').encode();out=R/(phase+'-checks.json');out.open('xb').write(raw);print(json.dumps({'receipt':str(out),'sha256':hashlib.sha256(raw).hexdigest(),'status':report['status'],'methods':result.testsRun}),flush=True);raise SystemExit(0 if result.wasSuccessful()else 1)
