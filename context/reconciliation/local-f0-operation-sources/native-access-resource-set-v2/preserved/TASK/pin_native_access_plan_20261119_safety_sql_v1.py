"""Pin a held native-access plan to exact committed sources; no execution."""
from pathlib import Path
import argparse,hashlib,json,subprocess
TASK=Path(__file__).resolve().parent;ROOT=TASK/'workinants-correction-pass'
SOURCE_ROOT='context/reconciliation/local-f0-operation-sources/native-access-safety-sql-v1'
SOURCE_FILES={name:name+'.txt' for name in ('execute_local_f0_native_access_20261119_safety_sql_v1.py','local_f0_native_access_operation_steps_safety_sql_v1.py','prepare_local_f0_native_access_plan_safety_sql_v1.py','check_native_access_operation_safety_sql_v1.py','pin_native_access_plan_20261119_safety_sql_v1.py')}
def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('manifest',type=Path);args=parser.parse_args()
    path=args.manifest.resolve();assert path.is_relative_to(TASK) and not path.is_relative_to(ROOT)
    raw=path.read_bytes();v=json.loads(raw)
    assert v['purpose']=='LOCAL_F0_NATIVE_ACCESS_REHEARSAL' and v['review_status']=='PENDING_OPERATIONAL_REVIEW'
    assert v['native_access']['packet_sha256']=='8044d43f25c4a449f662bbb467183aac86d6a619836aae0988458098d59e0b69'
    def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
    def git(*argv):return subprocess.check_output(['git','-c','core.longpaths=true',*argv],cwd=ROOT)
    files=dict(v['packet_files_sha256'])
    assert hashlib.sha256(''.join(p+'\0'+files[p]+'\n' for p in sorted(files)).encode()).hexdigest()==v['prepared_source_files_aggregate_sha256']
    for external,snapshot in SOURCE_FILES.items():
        relative=SOURCE_ROOT+'/'+snapshot;assert relative in files and sha(TASK/external)==files[relative]==sha(ROOT/relative)
    review='context/reconciliation/local-f0-native-access-safety-sql-v1-source-validation.json';assert review in files and files[review]==sha(ROOT/review)
    assert json.loads((ROOT/review).read_bytes())['independent_safety_sql_review']['decision']=='SOURCE_APPROVED'
    assert set(v['operator_sources_sha256'])==set(SOURCE_FILES)
    for relative,digest in files.items():assert sha(ROOT/relative)==digest,relative
    commit=git('rev-parse','HEAD').decode().strip();tree=git('rev-parse','HEAD^{tree}').decode().strip()
    for relative,digest in files.items():
        assert digest==hashlib.sha256(git('show',commit+':'+relative)).hexdigest(),relative
    for external,digest in v['operator_sources_sha256'].items():assert sha(TASK/external)==digest
    with path.with_name('operation-manifest-before-source-pin.json').open('xb') as out:out.write(raw)
    v.update(source_commit=commit,source_tree=tree,packet_files_sha256=dict(sorted(files.items())),packet_sha256=hashlib.sha256(''.join(p+'\0'+files[p]+'\n' for p in sorted(files)).encode()).hexdigest())
    path.write_bytes((json.dumps(v,indent=2)+'\n').encode())
    print(json.dumps({'source_commit':commit,'source_tree':tree,'manifest_sha256':sha(path),'packet_sha256':v['packet_sha256'],'packet_files':len(files),'runtime_approved':False}))
if __name__=='__main__':main()
