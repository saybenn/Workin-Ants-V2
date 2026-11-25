from pathlib import Path
import sys,os,json,hashlib,runpy,time,unittest,traceback,contextlib,io,tempfile,copy
BASE=Path(__file__).resolve().parent
FREEZE=BASE/'freeze'
TASK=BASE.parent
os.environ['TEMP']=os.environ['TMP']=str(TASK/'test-tmp')
sys.path.insert(0,str(TASK/'offline-python'))
forbidden=[]
def audit(event,args):
    if event.startswith(('subprocess.','socket.')) or event in ('os.system','os.posix_spawn','os.spawn'):
        forbidden.append(event)
        raise RuntimeError('NESTED_RUNTIME_FORBIDDEN')
sys.addaudithook(audit)
sha=lambda b:hashlib.sha256(b).hexdigest()
mode=sys.argv[1]
path=BASE/(mode+'-checks.json')
assert not path.exists()
out={'schema':'workinants.two-history-independent-peer-bounded-checks.v1','mode':mode,'reviewer':'/root/two_history_successor_code_peer','results':[],'runtime':'NOT_RUN','Posture':'D'}
delivery=json.loads((TASK/'runtime_lease_two_history_owned_v1_HOLD_correction_FINAL_author_delivery_20261123.json').read_bytes())
pins={n:sha((FREEZE/n).read_bytes()) for n in delivery['external_five_sha256']}
assert pins==delivery['external_five_sha256']
out['operator_sources_sha256']=pins
def save():
    out['forbidden_edges_attempted']=list(forbidden)
    out['operator_sources_preserved']=pins=={n:sha((FREEZE/n).read_bytes()) for n in pins}
    path.write_text(json.dumps(out,sort_keys=True,indent=2)+'\n',encoding='utf8')
def failure(e):
    return {'status':'FAIL','error_type':type(e).__name__,'safe_code':getattr(e,'code',None) if getattr(e,'code',None) in {'PROCESS_DEADLINE_EXCEEDED','PENDING_SOURCE_REVIEW'} else None,'frames':[{'file':Path(f.filename).name,'line':f.lineno,'function':f.name} for f in traceback.extract_tb(e.__traceback__)]}
save()
if mode=='light':
    M=runpy.run_path(str(FREEZE/'check_local_f0_runtime_lease_two_history_owned_v1_operation.py'),run_name='_independent_checker_support')
    names=['test_binary_exact_bytes_nonzero_and_text_no_translation','test_control_overflow_strict_decoding_and_profile_refusals','test_each_measured_channel_cap_exact_and_plus_one','test_transport_worker_failures_and_safe_first_origin','test_invalid_UTF8_is_closed_failure_and_strict_input_rejected_before_spawn','test_strict_JSON_rejects_duplicates_nonfinite_depth_and_float','test_real_preparation_exact_source8_and_pending_before_process','test_whole_real_source_map_binary_Git_framing_and_batches','test_actual_pinner_whole_map_committed_mutants_and_currentness','test_closed_original_reference_rejects_rewrite_and_wrong_source8']
    class Result(unittest.TestResult):
        def startTest(self,test):super().startTest(test);self.started=time.monotonic()
        def addSuccess(self,test):super().addSuccess(test);out['results'].append({'test':test.id().split('.')[-1],'status':'PASS','seconds':round(time.monotonic()-self.started,3)});save();print(out['results'][-1],flush=True)
        def addError(self,test,err):super().addError(test,err);out['results'].append({'test':test.id().split('.')[-1],**failure(err[1])});save();print(out['results'][-1],flush=True)
        def addFailure(self,test,err):super().addFailure(test,err);out['results'].append({'test':test.id().split('.')[-1],**failure(err[1])});save();print(out['results'][-1],flush=True)
    result=Result()
    unittest.TestSuite(M['Checks'](n) for n in names).run(result)
elif mode in ('node','resource','forced','natural'):
    probe='hold_correction_probes.py' if mode in ('node','resource') else 'forced_remote_exec_probes.py'
    M=runpy.run_path(str(FREEZE/probe),run_name='_independent_focused_probe_support')
    cases=M[{'node':'NODE','resource':'RESOURCE','forced':'FORCED','natural':'NATURAL'}[mode]]
    for case in cases:
        started=time.monotonic()
        try:row=M['one'](case,'independent-peer-'+mode);row['independent_reexecution']=True
        except BaseException as e:row={'case':case,**failure(e)}
        row['seconds']=round(time.monotonic()-started,3)
        out['results'].append(row);save();print({'case':case,'status':row['status'],'seconds':row['seconds']},flush=True)
elif mode in ('normal','normal-corrected'):
    M=runpy.run_path(str(FREEZE/'check_local_f0_runtime_lease_two_history_owned_v1_operation.py'),run_name='_independent_normal_support')
    started=time.monotonic()
    try:
        with tempfile.TemporaryDirectory(dir=FREEZE,prefix='independent-normal-') as d:
            base=Path(d)
            core,m,manifest=M['unit_fixture'](base)
            model=M['WholeModel'](core,m)
            pin=M['load'](M['PIN'],base)
            held=copy.deepcopy(m)
            held.update(review_status='PENDING_OPERATIONAL_REVIEW',source_commit='TO_BE_PINNED',source_tree='TO_BE_PINNED',packet_sha256='TO_BE_PINNED')
            heldraw=core.canonical_bytes(held)
            manifest.write_bytes(heldraw)
            proof=pin.pin(manifest,M['Boundary'](model.reply))
            pinned=json.loads(manifest.read_bytes())
            assert pinned['review_status']=='PENDING_OPERATIONAL_REVIEW'
            assert manifest.with_name('operation-manifest-before-source-pin.json').read_bytes()==heldraw
            assert proof['framed_bytes']>24_000_000 and proof['batches']>1 and proof['max_batch_bytes']<=16_777_216
            pinned['review_status']='APPROVED_LOCAL_F0_TWO_HISTORY_OWNED_ATTEMPT'
            manifest.write_bytes(core.canonical_bytes(pinned))
            driver=M['Boundary'](model.reply)
            captured=io.StringIO()
            with contextlib.redirect_stdout(captured):exit_code=core.launch(['--execute-reviewed-two-history-owned-v1','--manifest',str(manifest)],driver)
            report=core.report
            assert exit_code==0 and report['status']=='PASS_MACHINERY_SUBSET_ONLY'
            assert model.deploys==2 and len(model.attestation_bytes)==3 and model.oracle_calls==1 and model.native_calls==7
            assert model.finalizer_calls==1 and not model.created and not model.volume and report['cleanup_summary']['private_directory_absent']
            assert report['initial_two_rows']['rows']==2 and report['final_original_references_verified']
            assert not core.TRANSPORT.unknown and report.get('evidence_complete',True)
            assert not [p.error for p in driver.processes if p.error]
            for phase in ('initial','noop'):
                r=report['native_results'][phase]
                assert r['catalog_check_counts']=={'PASS':29089} and r['oracle_expressions']==416 and r['ledger_checks']==22 and r['applied_rows']==2
            assert report['native_results']['initial']['native_sha256']==report['native_results']['noop']['native_sha256']
            assert report['native_results']['noop']['oracle_proof']=='REUSED_INITIAL_AFTER_IDENTICAL_COMPLETE_NATIVE_NO_SECOND_ORACLE'
            raw=core.canonical_bytes(report)
            assert all(s.encode() not in raw and s not in captured.getvalue() for s in core.all_secrets)
            rp=BASE/'normal-memory-report.json';rp.write_bytes(raw)
            row={'case':'actual_fixture_prepare_pin_initialize_full_entry','status':'PASS','exit_code':exit_code,'pinner':proof,'deploys':model.deploys,'status_calls':len(model.attestation_bytes)-model.deploys,'native_calls':model.native_calls,'oracle_calls':model.oracle_calls,'finalizer_calls':model.finalizer_calls,'native':report['native_results'],'modeled_processes':len(driver.calls),'exact_cleanup':True,'no_secret_retained':True,'unknown':core.TRANSPORT.unknown,'report_sha256':sha(raw)}
    except BaseException as e:row={'case':'actual_fixture_prepare_pin_initialize_full_entry',**failure(e)}
    row['seconds']=round(time.monotonic()-started,3);out['results'].append(row);save();print(row,flush=True)
else:raise AssertionError('UNKNOWN_MODE')
out['successful']=all(r['status'] in ('PASS','PASS_UNIT_ONLY') for r in out['results']) and not forbidden and out['operator_sources_preserved']
save()
print(json.dumps({'mode':mode,'successful':out['successful'],'tests':len(out['results']),'receipt':str(path),'sha256':sha(path.read_bytes())}),flush=True)
raise SystemExit(0 if out['successful'] else 1)
