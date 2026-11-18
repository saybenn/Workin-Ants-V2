"""Root-only future source pinning; importing this file invokes no process.

This does not approve execution. The complete pinned literal manifest must be
independently reviewed, with any source-review-pending packet resolved first.
"""
import argparse,hashlib,json,subprocess
from pathlib import Path
TASK=Path(__file__).resolve().parent;ROOT=TASK/'workinants-correction-pass'
def main(argv=None):
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('manifest',type=Path);args=parser.parse_args(argv)
    path=args.manifest.resolve();assert path.is_relative_to(TASK) and not path.is_relative_to(ROOT)
    master=json.loads(path.read_bytes());assert master['purpose']=='LOCAL_F0_RESTRICTED_CONTROLS_REHEARSAL' and master['review_status']=='PENDING_OPERATIONAL_REVIEW'
    def git(*args):return subprocess.check_output(['git','-c','core.longpaths=true',*args],cwd=ROOT)
    commit=git('rev-parse','HEAD').decode().strip();tree=git('rev-parse','HEAD^{tree}').decode().strip()
    for relative,expected in master['packet_files_sha256'].items():assert hashlib.sha256(git('show',commit+':'+relative)).hexdigest()==expected==hashlib.sha256((ROOT/relative).read_bytes()).hexdigest()
    assert hashlib.sha256((TASK/'restricted_controls_operator_20261118.py').read_bytes()).hexdigest()==master['wrapper_sha256']
    assert hashlib.sha256((TASK/'restricted_controls_operation_steps.py').read_bytes()).hexdigest()==master['steps_sha256']
    master.update(source_commit=commit,source_tree=tree)
    path.write_text(json.dumps(master,indent=2)+'\n',encoding='utf8',newline='\n')
    print(json.dumps({'source_commit':commit,'source_tree':tree,'packet_sha256':master['packet_sha256'],'manifest_sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'review_status':master['review_status'],'execution_approved':False}));return 0
if __name__=='__main__':raise SystemExit(main())
