"""Read-only full-current plus committed-blob pinner; no Git mutation."""
from pathlib import Path
import hashlib
import json
import subprocess
import types
import argparse

PREP='prepare_local_f0_lease_mechanism_v1_plan.py'

def manifest_json(raw):
    def refused():raise ValueError('PINNER_MANIFEST_JSON')
    def pairs(items):
        value={}
        for k,v in items:
            if k in value:refused()
            value[k]=v
        return value
    if type(raw)is not bytes or not 0<len(raw)<=8*1024*1024:refused()
    try:value=json.loads(raw,object_pairs_hook=pairs,parse_float=lambda _:refused(),parse_constant=lambda _:refused())
    except (ValueError,UnicodeError,RecursionError):refused()
    if type(value)is not dict:refused()
    return value

def validate(manifest,root,external,require_literal=True):
    # This code itself is part of the literal-reviewed external five. The
    # helper is read as closed bytes and verified before execution.
    p=Path(external)/PREP;raw=p.read_bytes()
    if hashlib.sha256(raw).hexdigest()!=manifest.get('external_files_sha256',{}).get(PREP):raise ValueError('PINNER_PREP_HASH')
    m=types.ModuleType('_lease_mechanism_prep');m.__file__=str(p);exec(compile(raw,str(p),'exec'),m.__dict__)
    files,blobs,five=m.shape(manifest,root,external,True,require_literal)
    def git(args):
        r=subprocess.run(['git','-C',str(root),*args],capture_output=True,timeout=30)
        m.need(type(r.returncode)is int and r.returncode==0 and type(r.stdout)is bytes and r.stderr==b'','COMMITTED_SOURCE_READ_FAILED');return r.stdout
    commit=manifest['source_commit'];tree=manifest['source_tree']
    m.need(git(['rev-parse',commit+'^{commit}']).strip().decode('ascii')==commit and git(['rev-parse',commit+'^{tree}']).strip().decode('ascii')==tree,'COMMIT_TREE_BINDING')
    for name,wanted in files.items():m.need(m.sha(git(['cat-file','blob',commit+':'+name]))==wanted,'COMMITTED_SOURCE_DRIFT')
    # A fresh current-byte barrier closes the span consumed by Git reads.
    for name,wanted in files.items():m.root_read(root,name,wanted)
    for name,wanted in five.items():m.need(m.sha(m.closed(Path(external)/name))==wanted,'EXTERNAL_FIVE_DRIFT')
    return {'packet_sha256':m.aggregate(files),'files':len(files),'current_and_committed':True}

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--manifest',required=True);p.add_argument('--root',required=True);p.add_argument('--require-literal',action='store_true');a=p.parse_args()
    # Root supplies the published full commit/tree in the candidate manifest;
    # this verifier never alters those bindings or any review/approval flag.
    value=manifest_json(Path(a.manifest).read_bytes())
    print(json.dumps(validate(value,a.root,Path(__file__).resolve().parent,a.require_literal)))
