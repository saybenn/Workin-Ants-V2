"""Mechanism-only frozen actual INSTALL V5 main/reader, no domain proof."""
from pathlib import Path
from contextlib import redirect_stdout
import hashlib,io,json,os,runpy,sys,tempfile,time
T=Path(__file__).resolve().parent;R=T/'workinants-correction-pass'
CORE=T/'execute_local_f0_install_controls_20261120_source_phase_v5.py'
STEPS=T/'local_f0_install_controls_operation_steps_source_phase_v5.py'
H=lambda raw:hashlib.sha256(raw).hexdigest()
def deny(event,args):
    if event in {'subprocess.Popen','os.system','os.posix_spawn','socket.connect','socket.connect_ex','socket.bind','socket.getaddrinfo'}:raise AssertionError('ACTUAL_PROCESS_NETWORK_FORBIDDEN')
sys.addaudithook(deny)
def main():
    start=time.monotonic();assert H(CORE.read_bytes())=='bd50b44a48b5cdbf37736fa90b758419a0e44dbb76d9b3989c235f096a79593e';assert H(STEPS.read_bytes())=='ed6be9d0d62890ef25782bf6e566395d08b8572e1e0dbe76d4ebde181e22121e';rows=[]
    with tempfile.TemporaryDirectory(prefix='install-v5-parent-reference-catalog-',dir=T)as directory:
        base=Path(directory)
        for phase in ('none','late-native','cleanup','tool-postcheck'):
            n=runpy.run_path(str(CORE))['initialize'].__globals__;exec(compile(STEPS.read_bytes(),str(STEPS),'exec'),n)
            out=base/phase;fixed=out/'install-controls/install-controls-results.json';events=[];before=b'{"safe":1}\n';after=b'{"safe":2}\n';source='scripts/sql-review/local_image_identity.py'
            n.update(TASK=T,ROOT=R,OUT=out,PRIVATE=out/'private',MANIFEST={'review_status':'APPROVED_LOCAL_F0_INSTALL_OWNED_ATTEMPT','operator_sources_sha256':{}},TARGETS=[],report={'stage':'MECHANISM_ONLY','status':'IN_PROGRESS','steps':{},'targets':{},'events':[],'unexpected':[],'install':{'native':{}},'source_verification':{'files_sha256':{source:H((R/source).read_bytes())}}},INSTALL={},bootstrap_attempted=set(),all_secrets=[],save=lambda:None,event=lambda*a,**kw:None)
            for name in ('verify_packet','preflight','ensure_image','create_resources','prepare_install_credentials_and_baselines','provision_migration_tools','install_cross_target_semantic_parity','secret_scan','verify_external_input_preservation'):
                n[name]=lambda name=name:events.append(name)
            def mutate():
                st=fixed.stat();fixed.write_bytes(after);os.utime(fixed,ns=(st.st_atime_ns,st.st_mtime_ns));events.append('SAME_SIZE_MTIME_RESTORED_MUTATION')
            def component():
                fixed.parent.mkdir();fixed.write_bytes(before);n['retain_install_reference']();events.append('ACTUAL_INITIAL_READER')
            def native(*a):
                events.append('later-native-proof')
                if phase=='late-native'and fixed.read_bytes()==before:mutate()
            def cleanup():
                events.append('cleanup');n['report']['cleanup_actions_confirmed']=True
                if phase=='cleanup':mutate()
            def post():
                events.append('tool-postcheck')
                if phase=='tool-postcheck':mutate()
            n.update(install_coordinator_experiment=component,qualify_install_catalog=native,cleanup=cleanup,verify_tool_data=post,write_safe=lambda*a:None)
            with redirect_stdout(io.StringIO()):code=n['main']()
            ref=n['report']['install']['coordinator_reference'];row={'mutation_phase':phase,'exit_code':code,'status':n['report']['status'],'reference_sha256':ref['sha256'],'retained_file_sha256':H(fixed.read_bytes()),'reference_qualified':ref['reference_qualified'],'same_size':len(before)==len(after),'all_inputs_preserved':n['report']['all_source_and_external_inputs_preserved_after_run'],'cleanup_attempted':'cleanup'in events,'events':events};rows.append(row)
            assert code==0 and row['reference_qualified']is True
            assert (row['reference_sha256']==row['retained_file_sha256'])==(phase=='none')
    value={'schema':'workinants.install-v5-parent-reference-order-independent-probe.v1','decision':'CONFIRMED_NO_FRESH_PARENT_REFERENCE_BARRIER_BEFORE_FINAL_PASS','source_core_sha256':H(CORE.read_bytes()),'source_steps_sha256':H(STEPS.read_bytes()),'vectors':rows,'scope':'Actual frozen owning main and initial retain_install_reference. Source/domain/resource qualification bodies deliberately isolated to test ordering only; no genuine/full mocked database qualification or runtime result claimed.','actual_process_network_forbidden':True,'source_or_gate_edits':False,'seconds':round(time.monotonic()-start,3)}
    raw=(json.dumps(value,indent=2)+'\n').encode();path=T/'install_v5_parent_reference_order_independent_probe_20261120.json'
    with path.open('xb')as handle:handle.write(raw)
    print(json.dumps({'path':str(path),'sha256':H(raw),'decision':value['decision'],'seconds':value['seconds']}))
if __name__=='__main__':main()
