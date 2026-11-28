"""Reproduce a held known-work child bundle from the exact reviewed source graph."""
import argparse
import hashlib
import json
from pathlib import Path
import re
import subprocess
import tarfile
from pglast import ast, parse_sql

WORK = "server/platform/runtime/work-leases.ts"
OWNER = "server/platform/persistence/owner-transaction.ts"
SMOKE = "scripts/sql-review/cloud-p0d-owner-transaction-v1/fixture.ts.txt"
APP = "review-output/app-write-two-guard-observation-v2"
LEASE = "review-output/lease-revoke-control-rehearsal"
ACL = "review-output/runtime-lease-branch-v1/worker-acl32.json"
PINS = {
    WORK: "c63d836f064616c54b9b44dbb6d350df7b973f3b1b23227c785b0fb95b9e75c4",
    OWNER: "fb94f8843d89d33bd3025eab49aeed498101efd392983f76b3db2b6b4fca2c84",
    f"{APP}/fixtures.json": "9a0b874d96fb621e20adfa5dcca5b1cc472f025507b171af056b58c9ff23c962",
    f"{APP}/genuine-sh004-effect-insert.sql": "f056d0efdf8fbe70302c291b7d1d644fa069fb99fd926b7ec06eb5f2bacd8273",
    f"{APP}/independent-user-fixtures.sql": "ce281631c3dcee36c6e1b8e24182cf8041bb86aae5b2caf8f8902d278bf0663a",
    f"{APP}/source-customer-observe.sql": "1e44be39b65dfa72d21c0ea8fec0c304332e66a5b888cde90683aa0808cbe89f",
    f"{APP}/complete-state-observe.sql": "a9250848d105577e4eeda0c68cddd158196186ffa5a1d6c2dfbf5f9f82e7e0ac",
    SMOKE: "a58c9282610121ced1de4605fd3f7621d9001bb23a0e1cc05308b8b435ff55d2",
    f"{LEASE}/fixtures.json": "fe59a9867093f1cbab01741fa7d4f1fd727090e410374e663bbbd0796903c7e5",
    f"{LEASE}/identity-worker-bootstrap.sql": "ec7afe38adcae4f5352048bd9fe1e5f0675b6851ab0734029719e309d158e452",
    ACL: "6909f3cd9e2a795d1f39379b7f81db4c24f9526e235e802deea5ce1a2da8e5a3",
    "node_modules/typescript/lib/typescript.js": "3ae902c92cc44dace175c0e69e13a4b0899f6983c6121d76b9ab8dd5795e7675",
    "node_modules/typescript/package.json": "822ef7ca6452205657b6288b066481ecf508bfbf43455d715cf7d3ec457561e6",
    "package-lock.json": "89ed7e1a71409fbab67118d310ffde9f6e76d1cea65992d234bdd08d7e1bc3de",
}
TOOL_SHA = "5a5deaff7aa721dd3b26be84f3ab1e9da1c1880ad902bced3be39dd5cc9e15f5"
TOOL_BYTES = 113920987
NODE_BYTES = 126879696
NODE_SHA = "e32e2d16081cf644f88392934288086e7662529d0d43277c34f7aad2207cfafb"
WORK_ID = "530db9d1-b945-53ec-bb0c-6d91c914b5fc"
MAP = {"database_login_role": "login", "owner_module_id": "owner", "service_principal": "servicePrincipal",
       "action": "action", "purpose": "purpose", "target_kind": "targetKind", "target_id": "targetId",
       "security_generation": "securityGeneration", "source_generation": "sourceGeneration", "allowed_fields": "allowedFields"}


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def metadata(raw):
    return {"bytes": len(raw), "sha256": sha(raw)}


def encode(value):
    return (json.dumps(value, sort_keys=True, indent=2, allow_nan=False) + "\n").encode()


def pin(root, name):
    path = root / name
    assert path.resolve(strict=True) == path
    raw = path.read_bytes()
    assert sha(raw) == PINS[name], name
    return raw


def worker_fixture(source, scope_acl):
    prior = json.loads(source)
    old = prior["work_ids"]["lease"]
    acl = {row["operation"]: set(row["fields"]) for row in scope_acl if row["model"] == "RuntimeWorkItem"}
    assert len(scope_acl) == 32
    prefix = f"RuntimeWorkItem/{WORK_ID}/"
    result = {}
    for name in ("claim-0", "claim-1", "renew-1"):
        template = prior["grants"][name]
        row = {out: template[key] for key, out in MAP.items()}
        assert row["targetId"] == old and row["servicePrincipal"] == "lease-revoke-worker.v1"
        assert row["login"] == "wa_worker" and row["securityGeneration"] == "0" and row["sourceGeneration"] == name[-1]
        row["targetId"] = WORK_ID
        row["allowedFields"] = [
            field.replace(f"RuntimeWorkItem/{old}/", prefix, 1)
            for field in row["allowedFields"]
        ]
        action = name.split("-")[0]
        assert row["action"] == f"runtime.{action}_work.v1" and row["purpose"] == f"work.{action}"
        update = {"leaseExpiresAt"} if action == "renew" else {"attemptCount", "fence", "leaseExpiresAt", "leaseTokenHash", "state"}
        assert update <= acl["UPDATE"]
        expected = [f"{prefix}SELECT/{field}" for field in acl["SELECT"]]
        expected += [f"{prefix}UPDATE/{field}" for field in update | {"@row"}]
        expected += [f"{prefix}revision/{name[-1]}"]
        assert row["allowedFields"] == sorted(set(expected))
        result[name] = row
    return {"schema": "workinants.p0d-known-work-worker-scope.v1", "grants": result}


def project_source(sources):
    text = sources[SMOKE].decode()
    caps = re.search(r'"allowedFields": \[(.*?)\n    \]', text, re.S)
    high = json.loads("[" + caps[1] + "]")
    retained = [token for token in high if not token.startswith("RuntimeEffectReceipt/")]
    app = json.loads(sources[f"{APP}/fixtures.json"])
    assert len(high) == 208 and len(retained) == 179 and retained == app["source_customer"]["grant"]["allowed_fields"]
    sql = re.findall(r'  await query`([^`]+)`;', text)
    original = parse_sql(sources[f"{APP}/genuine-sh004-effect-insert.sql"].decode())
    inserts = [stmt.stmt for stmt in original if isinstance(stmt.stmt, ast.InsertStmt)]
    assert len(sql) == len(inserts) == 6
    assert all(parse_sql(raw)[0].stmt == expected for raw, expected in zip(sql, inserts, strict=True))
    pattern = r"^  return query`WITH changed AS \(INSERT INTO platform\.runtime_effect_receipt [^`]+`;$"
    effects = re.findall(pattern, text, flags=re.M)
    assert len(effects) == 1 and "RETURNING id" in effects[0]
    text = re.sub(pattern + r"\n", "", text, count=1, flags=re.M)
    field_text = "\n" + ",\n".join("      " + json.dumps(field) for field in retained)
    text = text[:caps.start(1)] + field_text + text[caps.end(1):]
    assert re.findall(r'  await query`([^`]+)`;', text) == sql
    return text.encode()

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source-root", type=Path, required=True, help="Absolute path to the pinned checkout")
    parser.add_argument("--tool-archive", type=Path, required=True, help="Absolute path to the pinned Prisma tools archive")
    parser.add_argument("destination", type=Path, help="New absolute directory beside this staged emitter")
    arguments = parser.parse_args()
    if not __debug__:
        parser.error("run with assertion checking enabled")
    here = Path(__file__).resolve().parent
    root, tool, destination = arguments.source_root, arguments.tool_archive, arguments.destination
    if not root.is_absolute() or not root.is_dir() or root.resolve(strict=True) != root:
        parser.error("--source-root requires an absolute canonical checkout directory")
    if not tool.is_absolute() or not tool.is_file() or tool.resolve(strict=True) != tool:
        parser.error("--tool-archive requires an absolute canonical archive path")
    if not destination.is_absolute() or destination.parent != here:
        parser.error("destination requires an absolute path beside the staged emitter")
    sources = {name: pin(root, name) for name in PINS}
    with tool.open("rb") as stream:
        if tool.stat().st_size != TOOL_BYTES or hashlib.file_digest(stream, "sha256").hexdigest() != TOOL_SHA:
            parser.error("tool archive bytes do not match the reviewed archive")
        stream.seek(0)
        with tarfile.open(fileobj=stream, mode="r:gz") as archive:
            member = archive.getmember("node/bin/node")
            if not member.isfile() or member.size != NODE_BYTES:
                parser.error("archived Node has an unexpected type or size")
            binary = archive.extractfile(member).read()
    if len(binary) != NODE_BYTES or sha(binary) != NODE_SHA:
        parser.error("archived Node bytes do not match the reviewed binary")
    destination.mkdir(mode=0o700)
    node = destination / "node"
    node.write_bytes(binary)
    node.chmod(0o700)
    assert subprocess.check_output([node, "--version"], timeout=5) == b"v24.22.1\n"
    projected = project_source(sources)
    projected_path = destination/"projected-source-fixture.ts"
    projected_path.write_bytes(projected)
    inputs = {"source": {WORK: WORK, OWNER: OWNER, str(projected_path): "fixture/fixture.ts"},
              "compiler": metadata(sources["node_modules/typescript/lib/typescript.js"])}
    emit = subprocess.check_output([node, here/"emit.cjs", root, destination/"compiled", json.dumps(inputs)], timeout=20)
    emit_manifest = json.loads(emit)
    fixture = encode(worker_fixture(sources[f"{LEASE}/fixtures.json"], json.loads(sources[ACL])))
    (destination/"worker-fixture.json").write_bytes(fixture)
    (destination/"known-work-child.mjs").write_bytes((here/"known-work-child.mjs").read_bytes())
    (destination/"identity-worker-bootstrap.sql").write_bytes(sources[f"{LEASE}/identity-worker-bootstrap.sql"])
    runtime = {name: metadata((destination/name).read_bytes()) for name in ("known-work-child.mjs", "worker-fixture.json")}
    runtime.update({f"compiled/{name}": info for name, info in emit_manifest["files"].items()})
    assert len(runtime) == 6
    support_names = ("prepare.py", "emit.cjs", "validate.py", "observe-work.sql", "observe-grants.sql",
                     "test-child.mjs", "test_validate.py", "README.md")
    support = {name: metadata((here/name).read_bytes()) for name in support_names}
    result = {"schema":"workinants.p0d-known-work-child-source-manifest.v1","author":"/root/pending_packets",
              "execution":"NOT_RUN","posture":"D","assertion_promotions":0,
              "source_pins":PINS,"rehearsal_tool_archive_sha256":TOOL_SHA,"node":metadata(binary),
              "runtime_files":runtime,"support_files":support,"compiled":emit_manifest,"worker_fixture":metadata(fixture),"projected_source_fixture":metadata(projected),
              "child":metadata((destination/"known-work-child.mjs").read_bytes())}
    (destination/"manifest.json").write_bytes(encode(result))
    print(sha(encode(result)))


if __name__ == "__main__":
    main()
