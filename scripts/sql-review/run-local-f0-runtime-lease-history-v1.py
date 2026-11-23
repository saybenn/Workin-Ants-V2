"""Dormant local-only Prisma coordinator. Never provisions, pulls or resets.

This NEW config/history path is provisional rehearsal tooling. Before execution,
the integration operator supplies the reviewed source/run manifest, provisions
the pinned tool closure, and writes an owner-only migrator URL to private tmpfs.
The URL is never an argument, environment variable, captured log or evidence.
Importing this module, --help, and the offline checks contact no runtime.
"""
import argparse
import hashlib
import json
from pathlib import Path, PureWindowsPath
import re
import subprocess
import stat
from types import ModuleType

ROOT = Path(__file__).resolve().parents[2]
class HeldFailure(ValueError):
    def __init__(self,code):self.code=code;super().__init__(code)
def require(value,code):
    if not value:raise HeldFailure(code)
RUNTIME = ('prisma.local-f0-runtime-lease-history-v1.config.mjs',
 'scripts/sql-review/local-f0-runtime-lease-history-v1-guard.mjs',
 'scripts/sql-review/local-f0-runtime-lease-history-v1-runner.mjs')
VALIDATION='context/reconciliation/local-f0-runtime-lease-two-history-v1-source-validation.json'
PREPARER='scripts/prepare-local-f0-runtime-lease-history-v1.py'
NATIVE='scripts/prepare-native-runtime-lease-history-v1-review.py'
HISTORY='prisma/local-f0-runtime-lease-history-v1/migrations'
HISTORY_MANIFEST='prisma/local-f0-runtime-lease-history-v1/history-manifest.json'
REVIEW_PREFIX='context/reconciliation/local-f0-operation-sources/runtime-lease-two-history-v1/reviews/'
SOURCE8=('prisma/review/foundation-candidate.prisma',*RUNTIME,HISTORY+'/migration_lock.toml',
 HISTORY+'/20261117000100_f0_local_initial/migration.sql',
 HISTORY+'/20261120000100_f0_runtime_lease_branch_v1/migration.sql',HISTORY_MANIFEST)
ENDPOINT = "npipe:////./pipe/dockerDesktopLinuxEngine"
SOURCE_ROOT = "/run/wa-f0-source"
TOOLS_ROOT = "/run/wa-f0-tools"
PRIVATE_ROOT = "/run/wa-secrets"
PRISMA_CODES = set("P1000 P1001 P1002 P1003 P1008 P1010 P1011 P1012 P1013 P1014 P1015 P1016 P1017 P3000 P3001 P3002 P3003 P3004 P3005 P3006 P3007 P3008 P3009 P3010 P3011 P3012 P3013 P3014 P3015 P3016 P3017 P3018 P3019 P3020 P3021 P3022".split())
DIAGNOSTIC_FLAGS = {"text_valid", "sgr_stripped", "headers_valid", "prisma_header_present", "prisma_header_unique", "database_header_present", "database_header_unique"}
MOUNT_CHECKS = ('metadata_list','one_data_volume','one_bootstrap_bind','bootstrap_source','bootstrap_destination','bootstrap_readonly','only_declared_mounts','source_exact_windows','source_exact_desktop')


def bootstrap_source_comparison(actual, expected):
    """Only the exact planned Windows path or observed Desktop translation.

    No suffix/case folding, alternate host prefixes, URI decoding or general
    path normalization. The manifest's Windows path is validated first.
    """
    if type(expected)is not str or not re.fullmatch(r'[A-Za-z]:\\[^\x00-\x1f<>"|?*]+',expected) or '/'in expected or ':'in expected[2:]:return False,False
    if not all(p and p not in('.','..')and not p.endswith((' ','.'))for p in expected[3:].split('\\')):return False,False
    if type(actual) is not str:return False, False
    windows=PureWindowsPath(expected)
    desktop='/run/desktop/mnt/host/'+windows.drive[0].lower()+'/'+'/'.join(windows.parts[1:])
    return actual==expected, actual==desktop


def private_mount_comparison(target, mounts):
    checks=dict.fromkeys(MOUNT_CHECKS,False)
    if type(mounts) is not list or not all(type(m) is dict for m in mounts):return checks
    checks['metadata_list']=True
    data=[m for m in mounts if m.get('Type')=='volume' and m.get('Name')==target['volume_name'] and m.get('Destination')=='/var/lib/postgresql/data' and m.get('RW') is True]
    binds=[m for m in mounts if m.get('Type')=='bind']
    checks['one_data_volume']=len(data)==1;checks['one_bootstrap_bind']=len(binds)==1
    secret=[]
    if len(binds)==1:
        bind=binds[0]
        windows,desktop=bootstrap_source_comparison(bind.get('Source'),target['bootstrap_secret_host_path'])
        checks.update(source_exact_windows=windows,source_exact_desktop=desktop,bootstrap_source=windows or desktop,bootstrap_destination=bind.get('Destination')=='/run/bootstrap-password',bootstrap_readonly=bind.get('RW') is False)
        if checks['bootstrap_source'] and checks['bootstrap_destination'] and checks['bootstrap_readonly']:secret=[bind]
    checks['only_declared_mounts']=all(m in data or m in secret or m.get('Type')=='tmpfs' and m.get('Destination')==PRIVATE_ROOT for m in mounts)
    return checks


def mount_failure_comparison(error):
    value=getattr(error,'mount_comparison',None)
    return value if type(value) is dict and set(value)==set(MOUNT_CHECKS) and all(type(v) is bool for v in value.values()) else None


def unique_json(raw):
    def pairs(items):
        value={}
        for key,item in items:require(key not in value,'DUPLICATE_JSON');value[key]=item
        return value
    require(type(raw)in(str,bytes)and 0<len(raw)<=4*1024*1024,'BOUNDED_JSON')
    value=json.loads(raw,object_pairs_hook=pairs,parse_constant=lambda _:(_ for _ in()).throw(HeldFailure('NONFINITE_JSON')))
    def typed(v,depth=0):
        require(depth<=48,'JSON_DEPTH')
        if type(v)is dict:
            for x in v.values():typed(x,depth+1)
        elif type(v)is list:
            for x in v:typed(x,depth+1)
        else:require(v is None or type(v)in(str,bool,int),'STRICT_JSON_TYPES')
    typed(value);return value

def closed(root,name,wanted):
    root=Path(root).resolve();p=root/name
    require(type(name)is str and not Path(name).is_absolute()and ':'not in name and '\\\\'not in name and all(x not in('','.','..')for x in name.split('/')),'RELATIVE_SOURCE_PATH')
    require(p.resolve(strict=True).is_relative_to(root)and not any(x.is_symlink()for x in(p,*p.parents)if x.is_relative_to(root)),'SOURCE_PATH_CONFINEMENT')
    before=p.lstat();require(stat.S_ISREG(before.st_mode)and before.st_nlink==1 and 0<=before.st_size<=16*1024*1024,'REGULAR_BOUNDED_SOURCE')
    with p.open('rb')as stream:raw=stream.read(16*1024*1024+1)
    after=p.lstat()
    require((before.st_dev,before.st_ino,before.st_size,before.st_mtime_ns)==(after.st_dev,after.st_ino,after.st_size,after.st_mtime_ns)
      and len(raw)==before.st_size and hashlib.sha256(raw).hexdigest()==wanted,'SOURCE_BYTE_DRIFT')
    return raw

def load_sources(root,pins):
    require(type(pins)is dict and PREPARER in pins and NATIVE in pins and VALIDATION in pins,'COMPLETE_CLOSED_SOURCES_REQUIRED')
    validation=unique_json(closed(root,VALIDATION,pins[VALIDATION]))
    require(validation.get('review_gate')=='SOURCE_APPROVED','SOURCE_REVIEW_PENDING')
    source=validation.get('source_files_sha256')
    require(type(source)is dict and all(pins.get(n)==h for n,h in source.items()),'SOURCE_REVIEW_MAP')
    blobs={n:closed(root,n,h)for n,h in source.items()}
    for key in('independent_source_review','Root_source_review'):
        gate=validation.get(key)
        require(type(gate)is dict and gate.get('decision')=='SOURCE_APPROVED'and type(gate.get('path'))is str and gate['path'].startswith(REVIEW_PREFIX)
          and pins.get(gate['path'])==gate.get('sha256'),'SOURCE_REVIEW_RECORD')
        record=unique_json(closed(root,gate['path'],gate['sha256']))
        require(record.get('decision')=='SOURCE_APPROVED'and record.get('source_files_sha256')==source,'SOURCE_REVIEW_RECORD_BINDING')
    prep=ModuleType('_new_reviewed_two_history_preparer');prep.__file__=str(Path(root)/PREPARER)
    require(PREPARER in blobs,'CLOSED_PREPARER_REQUIRED')
    exec(compile(blobs[PREPARER],prep.__file__,'exec'),prep.__dict__)
    native=ModuleType('_new_reviewed_two_history_native');native.__file__=str(Path(root)/NATIVE)
    require(NATIVE in blobs,'CLOSED_NATIVE_REQUIRED')
    exec(compile(blobs[NATIVE],native.__file__,'exec'),native.__dict__)
    require(set(source)==set(native.REQUIRED_FILES),'EXACT_NEW_PROGRAM_SOURCE_GRAPH')
    require(validation.get('source_expected_sha256')is not None,'NEW_EXPECTED_SOURCE_HASH_REQUIRED')
    return prep,blobs,validation

def verify_source8(snapshot,manifest,manifest_bytes,prep):
    root=Path(snapshot).resolve(strict=True);require(not Path(snapshot).is_symlink(),'SOURCE8_ROOT_LINK')
    found=[]
    for p in root.rglob('*'):
        require(not p.is_symlink(),'SOURCE8_SYMLINK')
        if p.is_file():found.append(p.relative_to(root).as_posix())
    require(sorted(found)==sorted(SOURCE8),'EXACT_SOURCE8_CLOSURE')
    history_raw=(root/HISTORY_MANIFEST).read_bytes();history=unique_json(history_raw)
    require(history.get('schema')=='workinants.local-f0-runtime-lease-history.v1'and history.get('run_id')==manifest['run_id']
      and history.get('run_manifest_sha256')==hashlib.sha256(manifest_bytes).hexdigest(),'NEW_HISTORY_RUN_BINDING')
    declared=history.get('files_sha256');require(type(declared)is dict and set(declared)==set(SOURCE8)-{HISTORY_MANIFEST},'EXACT_DECLARED_SEVEN')
    out={n:closed(root,n,h)for n,h in declared.items()}
    emitted,expected=prep.prepare_plan(manifest,manifest_bytes,out[prep.ordered_rows()[0]['path']],out[prep.ordered_rows()[1]['path']],
      out[prep.SCHEMA],{n:out[n]for n in RUNTIME})
    require(history==expected and all(out[n]==b for n,b in emitted.items()),'SOURCE8_REPRODUCTION')
    out[HISTORY_MANIFEST]=history_raw;return out


def inspect_live(manifest, context, container, volume):
    """Pure metadata comparator; does not invoke Docker or contact Postgres."""
    target = manifest["target"]
    require(context.get("Name") == "desktop-linux" and
            context.get("Endpoints", {}).get("docker", {}).get("Host") == ENDPOINT,
            "LOCAL_DOCKER_ENDPOINT_REQUIRED")
    require(re.fullmatch(r"[0-9a-f]{64}", container.get("Id", "")), "CONTAINER_ID")
    require(container.get("Name") == "/" + target["container_name"] and
            container.get("Config", {}).get("Image") == target["image"] and
            container.get("Platform") == "linux" and container.get("State", {}).get("Running") is True,
            "LIVE_PINNED_CONTAINER_REQUIRED")
    labels = container.get("Config", {}).get("Labels", {})
    require(all(labels.get(key) == value for key, value in target["labels"].items()), "LIVE_RUN_LABELS")
    host = container.get("HostConfig", {})
    ports = container.get("NetworkSettings", {}).get("Ports") or {}
    require(host.get("NetworkMode") == "none" and not host.get("PortBindings") and
            type(ports) is dict and all(value is None for value in ports.values()) and
            host.get("Privileged") is False and not host.get("PidMode") and
            host.get("IpcMode") in ("", "private") and
            not host.get("Devices") and not host.get("CapAdd"), "PRIVATE_CONTAINER_REQUIRED")
    mounts = container.get("Mounts", [])
    checks=private_mount_comparison(target,mounts)
    if not all(checks[name] for name in MOUNT_CHECKS[:7]):
        error=HeldFailure('EXACT_PRIVATE_MOUNTS_REQUIRED');error.mount_comparison=checks
        raise error
    require(volume.get("Name") == target["volume_name"] and volume.get("Driver") == "local" and
            not volume.get("Options") and volume.get("Scope") == "local" and
            all(volume.get("Labels", {}).get(key) == value for key, value in target["labels"].items()), "RUN_OWNED_VOLUME_REQUIRED")
    tmpfs = host.get("Tmpfs", {})
    options = set(tmpfs.get(PRIVATE_ROOT, "").split(","))
    require(set(tmpfs) == {PRIVATE_ROOT} and {"noexec", "nosuid", "nodev"}.issubset(options) and
            bool(options.intersection({"mode=0700", "mode=700"})), "PRIVATE_SECRET_TMPFS_REQUIRED")
    return {"endpoint": ENDPOINT, "context": "desktop-linux", "container_id": container["Id"],
            "container_name": target["container_name"], "volume_name": target["volume_name"],
            "image": target["image"], "network": "none", "published_ports": False,
            "labels": target["labels"], "bootstrap_secret_host_path": target["bootstrap_secret_host_path"]}


def verify_image(manifest, container, image, helper, approved_manifest):
    proof=helper.validate_cached_image([image],approved_manifest)
    require(proof['reference']==manifest['target']['image']and container.get('Image')==proof['image_id'],'LIVE_CONTAINER_IMAGE_BINDING')
    return proof


def copied_entrypoint_preflight(manifest, observed, runtime_sources, process):
    """Use the trusted pinned-image utility BEFORE copied Node/JS can execute."""
    require(set(runtime_sources) == set(RUNTIME), "RUNTIME_SOURCE_FILES")
    reviewed = manifest["source"]["runtime_files_sha256"]
    require({name: hashlib.sha256(raw).hexdigest() for name, raw in runtime_sources.items()} == reviewed, "REVIEWED_RUNTIME_DRIFT")
    expected = {TOOLS_ROOT + "/node/bin/node": manifest["tools"]["files_sha256"]["node/bin/node"],
                **{SOURCE_ROOT + "/" + name: value for name, value in reviewed.items()}}
    result = process(["docker", "--context", "desktop-linux", "exec", observed["container_id"],
                      "/usr/bin/sha256sum", "--", *sorted(expected)],
                     text=True, capture_output=True, timeout=30, shell=False)
    require(result.returncode == 0, "COPIED_ENTRYPOINT_HASH_CHECK_FAILED")
    actual = {}
    for line in result.stdout.splitlines():
        match = re.fullmatch(r"([0-9a-f]{64})  (/run/wa-f0-(?:source|tools)/[^\r\n]+)", line)
        require(match is not None and match[2] not in actual, "COPIED_ENTRYPOINT_HASH_OUTPUT")
        actual[match[2]] = match[1]
    require(actual == expected, "COPIED_ENTRYPOINT_DRIFT")


def runner_succeeded(value):
    return value["exit_code"] == 0 and value["status"] == "CLI_COMPLETED_REQUIRES_INDEPENDENT_LEDGER_CATALOG_CHECKS"


def safe_result(raw, manifest, observed, operation):
    value = unique_json(raw)
    require(type(value) is dict and value.get("schema") == "workinants.local-f0-runtime-lease-history-migrate-result.v1", "RUNNER_RESULT_SCHEMA")
    permitted = {"schema", "operation", "status", "exit_code", "prisma_codes", "sqlstates", "no_pending_message_observed",
                 "raw_output_discarded", "database_qualification_claimed", "run_id", "container_id", "initial_sql_sha256", "append_sql_sha256", "ordered_history_sha256", "effective_expected_sha256", "attestation_sha256", "diagnostic_format"}
    require(set(value) == permitted and value["operation"] == operation and
            value["run_id"] == manifest["run_id"] and value["container_id"] == observed["container_id"] and
            all(value[key] == manifest["source"][key] for key in ("initial_sql_sha256","append_sql_sha256","ordered_history_sha256","effective_expected_sha256")) and
            value["raw_output_discarded"] is True and value["database_qualification_claimed"] is False,
            "RUNNER_RESULT_IDENTITY")
    require(value["status"] in {"CLI_COMPLETED_REQUIRES_INDEPENDENT_LEDGER_CATALOG_CHECKS", "CLI_FAILED_STOP_AND_INSPECT", "CLI_OUTPUT_REJECTED_STOP_AND_INSPECT", "CLI_CLOSURE_UNCONFIRMED_STOP_AND_CLEAN_EXACT_RESOURCE"} and
            (value["exit_code"] is None or type(value["exit_code"]) is int and 0 <= value["exit_code"] <= 255) and
            type(value["no_pending_message_observed"]) is bool and
            type(value["prisma_codes"]) is list and len(value["prisma_codes"]) <= 1 and all(type(code) is str and code in PRISMA_CODES for code in value["prisma_codes"]) and
            type(value["sqlstates"]) is list and len(value["sqlstates"]) <= 1 and all(type(code) is str and code in {"42501", "42703", "22012", "P0001", "23503", "23505", "23514"} for code in value["sqlstates"]) and
            type(value["attestation_sha256"]) is str and re.fullmatch(r"[0-9a-f]{64}", value["attestation_sha256"]), "RUNNER_RESULT_VALUES")
    flags = value["diagnostic_format"]
    require(type(flags) is dict and set(flags) == DIAGNOSTIC_FLAGS and all(type(flag) is bool for flag in flags.values()), "RUNNER_DIAGNOSTIC_FLAGS")
    require((not flags["headers_valid"] or flags["text_valid"]) and
            all(not flags[family + "_unique"] or flags[family + "_present"] for family in ("prisma_header", "database_header")) and
            (flags["text_valid"] or not any(flags[key] for key in DIAGNOSTIC_FLAGS - {"text_valid", "sgr_stripped"})), "RUNNER_DIAGNOSTIC_CONSISTENCY")
    accepted = flags["text_valid"] and flags["headers_valid"] and all(not flags[family + "_present"] or flags[family + "_unique"] for family in ("prisma_header", "database_header"))
    require((not value["prisma_codes"] or accepted and flags["prisma_header_unique"]) and
            (not value["sqlstates"] or accepted and flags["database_header_unique"]) and
            (not value["no_pending_message_observed"] or accepted and operation == "deploy" and value["exit_code"] == 0 and not flags["prisma_header_present"] and not flags["database_header_present"]), "RUNNER_DIAGNOSTIC_CONSISTENCY")
    status = ("CLI_CLOSURE_UNCONFIRMED_STOP_AND_CLEAN_EXACT_RESOURCE" if value["exit_code"] is None else
              "CLI_OUTPUT_REJECTED_STOP_AND_INSPECT" if not accepted else
              "CLI_COMPLETED_REQUIRES_INDEPENDENT_LEDGER_CATALOG_CHECKS" if value["exit_code"] == 0 else "CLI_FAILED_STOP_AND_INSPECT")
    require(value["status"] == status, "RUNNER_STATUS_CONSISTENCY")
    return value


def docker_json(arguments, process):
    result = process(["docker", "--context", "desktop-linux", *arguments],
                     text=True, capture_output=True, timeout=30, shell=False)
    require(result.returncode == 0, "LOCAL_RUNTIME_INSPECTION_FAILED")
    value = unique_json(result.stdout)
    require(type(value) is list and len(value) == 1 and type(value[0]) is dict, "RUNTIME_INSPECTION_SCHEMA")
    return value[0]


def coordinate(manifest_bytes, operation, *, source8_root, source_pins, root=ROOT, process=subprocess.run):
    require(operation in('deploy','status'),'OPERATION_DENIED')
    prep,blobs,validation=load_sources(root,source_pins)
    manifest=prep.validate_manifest(unique_json(manifest_bytes))
    require(manifest['source']['effective_expected_sha256']==validation['source_expected_sha256'],'EXACT_NEW_EXPECTED_SOURCE')
    tool_closure=unique_json(blobs['context/reconciliation/local-f0-tooling/prisma-tools-closure.json'])
    require(manifest['tools']['files_sha256']==tool_closure['tools_files_sha256']and tool_closure['file_count']==10300,'EXACT_PINNED_TOOL_CLOSURE')
    snapshot=verify_source8(source8_root,manifest,manifest_bytes,prep)
    runtime_sources={n:blobs[n]for n in RUNTIME}
    require({n:hashlib.sha256(b).hexdigest()for n,b in runtime_sources.items()}==manifest['source']['runtime_files_sha256'],'RUNTIME_SOURCE_MAP')
    context=docker_json(['context','inspect','desktop-linux'],process)
    container=docker_json(['inspect',manifest['target']['container_name']],process)
    volume=docker_json(['volume','inspect',manifest['target']['volume_name']],process)
    observed=inspect_live(manifest,context,container,volume)
    image=docker_json(['image','inspect',manifest['target']['image']],process)
    identity=ModuleType('_reviewed_manifest_config_identity');identity.__file__=str(Path(root)/'scripts/sql-review/local_image_identity.py')
    exec(compile(blobs['scripts/sql-review/local_image_identity.py'],identity.__file__,'exec'),identity.__dict__)
    verify_image(manifest,container,image,identity,blobs['scripts/sql-review/fixtures/postgres-17.11-approved-manifest.json'])
    # Hash and length verification of all eight mounted sources precedes Node.
    expected={SOURCE_ROOT+'/'+n:hashlib.sha256(b).hexdigest()for n,b in snapshot.items()}
    expected[TOOLS_ROOT+'/node/bin/node']=manifest['tools']['files_sha256']['node/bin/node']
    result=process(['docker','--context','desktop-linux','exec',observed['container_id'],'/usr/bin/sha256sum','--',*sorted(expected)],text=True,capture_output=True,timeout=30,shell=False)
    require(result.returncode==0,'COPIED_SOURCE_HASH_CHECK')
    parsed={}
    for line in result.stdout.splitlines():
        m=re.fullmatch(r'([0-9a-f]{64})  (/run/wa-f0-(?:source|tools)/[^\r\n]+)',line)
        require(m is not None and m[2]not in parsed,'COPIED_SOURCE_HASH_OUTPUT');parsed[m[2]]=m[1]
    require(parsed==expected,'COPIED_SOURCE_DRIFT')
    lengths={SOURCE_ROOT+'/'+n:len(b)for n,b in snapshot.items()}
    result=process(['docker','--context','desktop-linux','exec',observed['container_id'],'/usr/bin/stat','--format=%s','--',*sorted(lengths)],text=True,capture_output=True,timeout=30,shell=False)
    require(result.returncode==0 and result.stdout.splitlines()==[str(lengths[n])for n in sorted(lengths)],'COPIED_SOURCE_LENGTHS')
    attestation={'schema':'workinants.local-f0-runtime-lease-history-live-attestation.v1','planned':manifest,
      'run_manifest_sha256':hashlib.sha256(manifest_bytes).hexdigest(),'observed':observed}
    raw=json.dumps(attestation,separators=(',',':'))
    result=process(['docker','--context','desktop-linux','exec','-i',observed['container_id'],TOOLS_ROOT+'/node/bin/node',
      SOURCE_ROOT+'/scripts/sql-review/local-f0-runtime-lease-history-v1-runner.mjs',
      '--execute-reviewed-local-f0-runtime-lease-history-v1','--operation',operation],
      input=raw,text=True,capture_output=True,timeout=150,shell=False)
    value=safe_result(result.stdout,manifest,observed,operation)
    require(value['attestation_sha256']==hashlib.sha256(raw.encode()).hexdigest(),'ATTESTATION_RESULT_MISMATCH')
    require(result.returncode==(0 if runner_succeeded(value)else 1),'RUNNER_EXIT_MISMATCH')
    again=verify_source8(source8_root,manifest,manifest_bytes,prep)
    require(again==snapshot,'SOURCE8_CHANGED_DURING_OPERATION')
    for n,b in blobs.items():require(closed(root,n,source_pins[n])==b,'PROGRAM_SOURCE_CHANGED_DURING_OPERATION')
    return value

def main(argv=None,process=subprocess.run):
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--execute-reviewed-two-history',action='store_true')
    parser.add_argument('--run-manifest',type=Path)
    parser.add_argument('--operation',choices=('deploy','status'))
    parser.add_argument('--source-pins',type=Path)
    parser.add_argument('--source8-root',type=Path)
    parser.add_argument('--evidence-file',type=Path)
    args=parser.parse_args(argv)
    try:
        require(args.execute_reviewed_two_history and all(x is not None for x in(args.run_manifest,args.operation,args.source_pins,args.source8_root)),'EXPLICIT_NEW_EXECUTION_REQUIRED')
        if args.evidence_file:
            p=args.evidence_file.resolve()
            require(p.is_relative_to(ROOT.parent.resolve())and not p.is_relative_to(ROOT.resolve())and not p.exists(),'FRESH_TASK_EXTERNAL_EVIDENCE')
        value=coordinate(args.run_manifest.read_bytes(),args.operation,source8_root=args.source8_root,source_pins=unique_json(args.source_pins.read_bytes()),process=process)
        if args.evidence_file:
            with args.evidence_file.open('x',encoding='utf8',newline='\n')as f:f.write(json.dumps(value,indent=2)+'\n')
        print(json.dumps(value));return 0 if runner_succeeded(value)else 1
    except BaseException as error:
        print(json.dumps({'schema':'workinants.local-f0-runtime-lease-history-migrate-result.v1','status':'REFUSED_OR_INCOMPLETE',
          'code':error.code if isinstance(error,HeldFailure)else'NEW_INPUT_IO_OR_UNCONFIRMED_PROCESS','raw_output_discarded':True,'database_qualification_claimed':False}));return 1

if __name__=='__main__':raise SystemExit(main())
