import io,json,pathlib,runpy,sys,time,unittest
sys.dont_write_bytecode=True
A=pathlib.Path(__file__).parent
def audit(event,args):
 if event in('subprocess.Popen','os.system','os.posix_spawn','os.spawn','socket.connect','socket.bind','socket.getaddrinfo'):raise AssertionError('UNMOCKED_EXTERNAL_BOUNDARY_FORBIDDEN')
sys.addaudithook(audit)
class SafeResult(unittest.TestResult):
 def __init__(self):super().__init__();self.rows=[]
 def addSuccess(self,test):super().addSuccess(test);self.rows.append({'method':test.id(),'status':'PASS'})
 def addError(self,test,err):super().addError(test,err);self.rows.append({'method':test.id(),'status':'ERROR','exception_type':err[0].__name__})
 def addFailure(self,test,err):super().addFailure(test,err);self.rows.append({'method':test.id(),'status':'FAIL','exception_type':err[0].__name__})
tag=sys.argv[1]if len(sys.argv)>1 else'initial';start=time.monotonic();m=runpy.run_path(str(A/'check_local_f0_customer_stale_predecessor_v1_operation.py'));suite=unittest.TestSuite()
select=[('SourcePreservation','test_exact_original_115_and_guard_source'),('PendingAndProjection','test_actual_pending_entry_before_steps_or_processes'),('WholeLifecycle','test_actual_full_constructor_install_native_child_three_and_cleanup')]
if tag.startswith('failure-paths'):select=[('WholeLifecycle',n)for n in('test_wrong_guard_partial_prefix_stops_later_cases','test_persistent_parent_writer_failure_still_closes_and_cleans','test_late_closed_reference_drift_rejects_after_cleanup')]
if tag.startswith('transport'):select=[('BinaryTransport',n)for n in sorted(m['BinaryTransport'].__dict__)if n.startswith('test_')]
if tag.startswith('inherited'):select=[('InheritedTextTransport',n)for n in sorted(m['InheritedTextTransport'].__dict__)if n.startswith('test_')]
if tag.startswith('failure-paths'):select.append(('WholeLifecycle','test_uncaptured_client_failure_stays_unknown_after_global_zero'))
if tag.startswith('admission'):select=[('WholeLifecycle',n)for n in('test_pending_current_five_and_committed_drift_before_steps','test_manifest_extra_field_and_wrong_storage_reject_before_process')]
if tag.startswith('closure-owning'):select=[('WholeLifecycle',n)for n in('test_unknown_transport_then_global_zero_vetoes_finalizer_and_cleans','test_confirmed_closed_error_allows_otherwise_eligible_finalization','test_unknown_transport_latch_survives_persistent_IO_and_later_good_cleanup')]
if tag=='finalization-read-only':select=[('SourcePreservation','test_exact_original_115_and_guard_source'),('WholeLifecycle','test_actual_full_constructor_install_native_child_three_and_cleanup'),('WholeLifecycle','test_readonly_finalization_false_NULL_missing_unknown_noresponse_stop_before_child')]
if tag.startswith('source'):select=[('SourcePreservation','test_exact_original_115_and_guard_source'),('PendingAndProjection','test_changed_python_and_unchanged_packet_SQL_parse')]
if tag=='final-light':select=[('SourcePreservation','test_exact_original_115_and_guard_source')]+[(cls,n)for cls in('BinaryTransport','InheritedTextTransport','PendingAndProjection')for n in sorted(m[cls].__dict__)if n.startswith('test_')]+[('WholeLifecycle',n)for n in('test_pending_current_five_and_committed_drift_before_steps','test_manifest_extra_field_and_wrong_storage_reject_before_process')]
if tag=='final-all':select=[(cls,n)for cls in('SourcePreservation','BinaryTransport','InheritedTextTransport','PendingAndProjection','WholeLifecycle')for n in sorted(m[cls].__dict__)if n.startswith('test_')]
for cls,method in select:suite.addTest(m[cls](method))
if tag.startswith('source')or tag in('final-light','final-all'):
 for method in('test_source_and_three_exact_contracts','test_exact_capabilities_no_revision1_or_companion_write','test_reproduction_exact_all_prepared_bytes','test_setup_bypasses_only_two_identity_owner_guards_flush_then_restore','test_both_exact_source_diagnostics_and_unrelated_values','test_old_error_stop_restoration_rejects_before_rollback_ack','test_missing_rollback_is_not_manufactured_by_cleanup','test_unreceived_malformed_and_zero_row_bool_reject'):suite.addTest(m['child_tests']['Checks'](method))
result=SafeResult();suite.run(result)
report={'schema':'workinants.CSP1-private-focused-checks.v1','tag':tag,'status':'PASS'if result.wasSuccessful()else'FAILED_CHECKS_PRESERVED','tests_run':result.testsRun,'results':result.rows,'seconds':round(time.monotonic()-start,3),'runtime':'NOT_RUN','all_external_boundaries':'MOCKED_OR_AUDIT_FORBIDDEN','Posture':'D','unrestricted_output_retained':False,'safe_measured_payload_sizes':m.get('AUTHOR_MEASUREMENTS',{}),'operator_sources_sha256':{n:__import__('hashlib').sha256((A/n).read_bytes()).hexdigest()for n in m['FIVE']}}
folder=A/'author-checks';folder.mkdir(exist_ok=True);out=folder/(tag+'.json');assert not out.exists();out.write_text(json.dumps(report,indent=2)+'\n',encoding='utf8');print(json.dumps(report,indent=2))
for test,trace in result.errors+result.failures:print(test.id()+'\n'+trace[-5000:])
raise SystemExit(0 if result.wasSuccessful()else 1)
