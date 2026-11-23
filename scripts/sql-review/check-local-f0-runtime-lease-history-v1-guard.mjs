// Pure source API checks; the runner import starts no child process.
import assert from "node:assert/strict";
import fs from "node:fs";
import path from "node:path";
import {fileURLToPath} from "node:url";
import {strictJson,validateUrl,validateManifest,verifyInputs,sha256,SOURCE_ROOT,TOOLS_ROOT,PRIVATE_ROOT,URL_FILE,SCHEMA,HISTORY_MANIFEST,HISTORY,ORDERED,ORDERED_SHA,RUNTIME,IMAGE} from "./local-f0-runtime-lease-history-v1-guard.mjs";
import {prismaArguments,childEnvironment,summarizeProcess,main} from "./local-f0-runtime-lease-history-v1-runner.mjs";
const tools=Object.fromEntries(Array.from({length:10300},(_,i)=>["fixture-"+i,"a".repeat(64)]));
const id="2e4d7cc4-cef1-428e-8a1d-b9eeb7fc48c8";
const manifest={schema:"workinants.local-f0-runtime-lease-history-run.v1",purpose:"LOCAL_F0_RUNTIME_LEASE_TWO_MIGRATION_REHEARSAL",run_id:id,
 target:{container_name:"wa-p0c-2e4d7cc4-twohistory",volume_name:"wa-p0c-2e4d7cc4-twohistory-data",database:"wa_p0c_rehearsal",image:IMAGE,network:"none",
  labels:{"workinants.rehearsal":"p0c-local-f0","workinants.rehearsal.run":id},bootstrap_secret_host_path:"C:\\task\\private\\bootstrap-password"},
 history:{path:HISTORY,ordered:ORDERED},source:{initial_sql_sha256:ORDERED[0].sha256,append_sql_sha256:ORDERED[1].sha256,ordered_history_sha256:ORDERED_SHA,
  effective_expected_sha256:"b".repeat(64),foundation_schema_sha256:"de069b3beae07ab7f29167203efae11937f6a29c470cb1c95c2c143fdb623723",runtime_files_sha256:Object.fromEntries(RUNTIME.map(n=>[n,"c".repeat(64)]))},
 tools:{node_version:"v24.22.1",prisma_version:"7.10.1",engine_commit:"d1b3f377ca835d73fd50954a5e22128b9ebdd6b8",files_sha256:tools}};
let checks=0;const pass=f=>{f();checks++;};
pass(()=>assert.equal(validateManifest(manifest),manifest));
for(const raw of['{"x":1,"x":2}','{"x":NaN}','{"x":1e9999}','{"__proto__":1,"__proto__":2}','{"x":1}false'])pass(()=>assert.throws(()=>strictJson(Buffer.from(raw))));
pass(()=>assert.equal(strictJson(Buffer.from('{"x":[true,false,null,1,"z"]}')).x[3],1));
for(const operation of["resolve-rolled-back","resolve-applied","reset","db push","custom-sql"])pass(()=>assert.throws(()=>prismaArguments(operation,{})));
const local={cli:"/run/wa-f0-tools/node_modules/prisma/build/index.js",config:"/run/wa-f0-source/prisma.local-f0-runtime-lease-history-v1.config.mjs",engine:"/run/wa-f0-tools/schema-engine"};
for(const operation of["deploy","status"])pass(()=>assert.deepEqual(prismaArguments(operation,local),[local.cli,"migrate",operation,"--config",local.config]));
pass(()=>{const env=childEnvironment(local);assert.equal(env.PRISMA_SCHEMA_ENGINE_BINARY,local.engine);for(const name of["DATABASE_URL","NODE_OPTIONS","HTTP_PROXY","PGPASSWORD"])assert.equal(env[name],undefined);});
for(const url of["postgresql://wa_migrator:x@example.com:5432/wa_p0c_rehearsal?schema=public","postgresql://postgres:x@127.0.0.1:5432/wa_p0c_rehearsal?schema=public","postgresql://wa_migrator:x@127.0.0.1:5432/other?schema=public","postgresql://wa_migrator:x@127.0.0.1:5432/wa_p0c_rehearsal?schema=public&schema=public"])pass(()=>assert.throws(()=>validateUrl(url)));
for(const operation of["resolve-rolled-back","reset","custom-sql"])pass(()=>{let touched=false;assert.equal(main(["--execute-reviewed-local-f0-runtime-lease-history-v1","--operation",operation],{readStdin(){touched=true;throw Error();},emit(){}}),1);assert.equal(touched,false);});
pass(()=>{const bad=structuredClone(manifest);bad.history.ordered.reverse();assert.throws(()=>validateManifest(bad));});
pass(()=>{const bad=structuredClone(manifest);bad.schema="workinants.local-f0-run.v1";assert.throws(()=>validateManifest(bad));});

// Actual reviewed SQL/schema/runtime bytes, but SYNTHETIC tool contents. This
// checks exported APIs and per-file hashing semantics, never real archive/tool
// qualification. Python's separate real coordinate trace binds the immutable
// production tool map before any modeled Docker reply. No hash function or
// production expected closure is replaced by this fixture.
const root=path.resolve(path.dirname(fileURLToPath(import.meta.url)),"../..");
const closure=JSON.parse(fs.readFileSync(path.join(root,"context/reconciliation/local-f0-tooling/prisma-tools-closure.json"),"utf8"));
const source=new Map();
source.set(SCHEMA,fs.readFileSync(path.join(root,SCHEMA)));
for(const n of RUNTIME)source.set(n,fs.readFileSync(path.join(root,n)));
source.set(ORDERED[0].path,fs.readFileSync(path.join(root,"review-output/foundation-application.review.sql")));
source.set(ORDERED[1].path,fs.readFileSync(path.join(root,"review-output/runtime-lease-branch-v1/history-source-artifact/migrations/20261120000100_f0_runtime_lease_branch_v1/migration.sql")));
source.set(HISTORY+"/migration_lock.toml",Buffer.from('provider = "postgresql"\n'));
const toolBytes=n=>n==="node_modules/prisma/package.json" ? Buffer.from('{"version":"7.10.1"}\n') : Buffer.from("UNIT_ONLY_SYNTHETIC_TOOL_BYTES:"+n+"\n");
const syntheticTools=Object.fromEntries(Object.keys(closure.tools_files_sha256).map(n=>[n,sha256(toolBytes(n))]));
const planned=structuredClone(manifest);
planned.source.runtime_files_sha256=Object.fromEntries(RUNTIME.map(n=>[n,sha256(source.get(n))]));
planned.tools.files_sha256=syntheticTools;
const runRaw=Buffer.from(JSON.stringify(planned));
const history={schema:"workinants.local-f0-runtime-lease-history.v1",scope:"PROVISIONAL_LOCAL_ONLY_NOT_HOSTED_ADOPTION",
 run_id:id,run_manifest_sha256:sha256(runRaw),migrations:HISTORY,ordered:ORDERED,ordered_history_sha256:ORDERED_SHA,
 effective_expected_sha256:planned.source.effective_expected_sha256,foundation_schema:SCHEMA,
 files_sha256:Object.fromEntries([...source].map(([n,b])=>[n,sha256(b)])),database_contacted:false,ledger_created_or_modified:false,
 raw_structure_applied_separately:false,public_source_archive_file_count:8,
 applied_history_rule:"Both exact applied checksums immutable; no resolve/baseline/direct ledger mutation in this family."};
source.set(HISTORY_MANIFEST,Buffer.from(JSON.stringify(history,null,2)+"\n"));
const observed={endpoint:"npipe:////./pipe/dockerDesktopLinuxEngine",context:"desktop-linux",container_id:"a".repeat(64),
 container_name:planned.target.container_name,volume_name:planned.target.volume_name,image:IMAGE,network:"none",published_ports:false,
 labels:planned.target.labels,bootstrap_secret_host_path:planned.target.bootstrap_secret_host_path};
const attestation={schema:"workinants.local-f0-runtime-lease-history-live-attestation.v1",planned,run_manifest_sha256:sha256(runRaw),observed};
const identity={platform:"linux",arch:"x64",node:"v24.22.1",hostname:observed.container_id.slice(0,12)};
const url="postgresql://wa_migrator:secret-canary@127.0.0.1:5432/wa_p0c_rehearsal?schema=public";
function fixtureIO(fault) {
  return {read(n){
    if(n.startsWith(SOURCE_ROOT+"/")){
      const relative=n.slice(SOURCE_ROOT.length+1);
      if(fault==="source" && relative===RUNTIME[0])return Buffer.from("changed-source-canary");
      if(fault==="old_history" && relative===HISTORY_MANIFEST){const bad=structuredClone(history);bad.schema="workinants.local-f0-history.v1";return Buffer.from(JSON.stringify(bad));}
      assert(source.has(relative),"unlisted source read");return source.get(relative);
    }
    assert(n.startsWith(TOOLS_ROOT+"/"),"unlisted filesystem read");
    const relative=n.slice(TOOLS_ROOT.length+1);assert(Object.hasOwn(syntheticTools,relative));
    if(fault==="tool" && relative==="node/bin/node")return Buffer.from("changed-tool-canary");
    return toolBytes(relative);
  },readPrivate(n){assert.equal(n,URL_FILE);return Buffer.from(fault==="url"?url.replace("127.0.0.1","example.com"):url);},
  listFiles(n){
    if(n===SOURCE_ROOT){const result=[...source.keys()];return fault==="old7"?result.filter(n=>n!==ORDERED[1].path):fault==="extra"?[...result,"extra.sql"]:result;}
    if(n===SOURCE_ROOT+"/"+HISTORY)return ["migration_lock.toml",...ORDERED.map(r=>r.id+"/migration.sql")];
    assert.equal(n,TOOLS_ROOT);const result=Object.keys(syntheticTools);return fault==="extra_tool"?[...result,"unlisted-tool"]:result;
  },mountInfo(){return fault==="mount"?"":"10 1 0:1 / "+PRIVATE_ROOT+" rw - tmpfs tmpfs rw\n";}};
}
const pureChecks=checks;
pass(()=>{const local=verifyInputs(attestation,fixtureIO(),identity);assert.equal(local.databaseUrl,url);assert.equal(local.migrations,SOURCE_ROOT+"/"+HISTORY);});
for(const fault of["source","old_history","tool","url","old7","extra","extra_tool","mount"])pass(()=>assert.throws(()=>verifyInputs(attestation,fixtureIO(fault),identity)));
for(const [key,value]of[["platform","win32"],["arch","arm64"],["node","v24.22.0"],["hostname","bbbbbbbbbbbb"]])pass(()=>assert.throws(()=>verifyInputs(attestation,fixtureIO(),{...identity,[key]:value})));
pass(()=>{const fixed=structuredClone(attestation);fixed.planned.tools.files_sha256=closure.tools_files_sha256;assert.throws(()=>verifyInputs(fixed,fixtureIO(),identity),/TOOL_FILE_DRIFT/);});
pass(()=>{assert.equal(Object.keys(syntheticTools).length,10300);assert.notDeepEqual(syntheticTools,closure.tools_files_sha256);assert.equal(source.size,8);});
for(const operation of["deploy","status"])pass(()=>{
  const trace=[];let emitted;
  const status=main(["--execute-reviewed-local-f0-runtime-lease-history-v1","--operation",operation],{
    readStdin(){trace.push("stdin");return Buffer.from(JSON.stringify(attestation));},
    store(raw,a){trace.push("private-store-boundary");assert.equal(sha256(raw),sha256(Buffer.from(JSON.stringify(attestation))));assert.deepEqual(a,strictJson(raw));},
    load(){trace.push("actual-verifyInputs");return verifyInputs(attestation,fixtureIO(),identity);},
    spawn(exe,args,options){trace.push("process-boundary");assert.equal(exe,TOOLS_ROOT+"/node/bin/node");
      assert.deepEqual(args,[TOOLS_ROOT+"/node_modules/prisma/build/index.js","migrate",operation,"--config",SOURCE_ROOT+"/"+RUNTIME[0]]);
      assert.equal(options.shell,false);assert.equal(options.cwd,SOURCE_ROOT);assert(!JSON.stringify({args,options}).includes("secret-canary"));
      assert.equal(Object.keys(options.env).length,11);return {status:0,stdout:operation==="deploy"?"No pending migrations to apply.\n":"",stderr:"raw-stderr-canary"};},
    emit(value){trace.push("safe-emit");emitted=value;}});
  assert.equal(status,0);assert.deepEqual(trace,["stdin","private-store-boundary","actual-verifyInputs","process-boundary","safe-emit"]);
  assert.equal(emitted.effective_expected_sha256,planned.source.effective_expected_sha256);assert.equal(emitted.database_qualification_claimed,false);
  assert.equal(emitted.no_pending_message_observed,operation==="deploy");
  for(const secret of["secret-canary","raw-stderr-canary","postgresql://","statement-body-canary"])assert(!JSON.stringify(emitted).includes(secret));
});
for(const argv of[["--execute-reviewed-local-f0-runtime-lease-history-v1","--operation","db push"],
 ["--execute-reviewed-local-f0-runtime-lease-history-v1","--operation","deploy","--config","other.mjs"],
 ["--execute-reviewed-local-f0-runtime-lease-history-v1","--operation","deploy","--url",url]])pass(()=>{
 let touched=false;assert.equal(main(argv,{readStdin(){touched=true;throw Error();},emit(){}}),1);assert.equal(touched,false);
});
pass(()=>{const names=["DATABASE_URL","NODE_OPTIONS","HTTP_PROXY","PGPASSWORD"];const saved=names.map(n=>process.env[n]);
 try{for(const n of names)process.env[n]="environment-secret-canary";const env=childEnvironment(local);
  assert(!JSON.stringify(env).includes("canary"));for(const n of names)assert.equal(env[n],undefined);
 }finally{names.forEach((n,i)=>{if(saved[i]===undefined)delete process.env[n];else process.env[n]=saved[i];});}
});
for(const fault of["source","tool","url"])pass(()=>{let spawned=false,emitted;assert.equal(main(["--execute-reviewed-local-f0-runtime-lease-history-v1","--operation","deploy"],{
 readStdin:()=>Buffer.from(JSON.stringify(attestation)),store(){},load(){return verifyInputs(attestation,fixtureIO(fault),identity);},spawn(){spawned=true;},emit(v){emitted=v;}}),1);
 assert.equal(spawned,false);assert.equal(emitted.status,"REFUSED_OR_INCOMPLETE");assert(!JSON.stringify(emitted).includes("secret-canary"));});
for(const result of[{status:null,signal:"SIGTERM",stdout:"password-canary"},{status:null,error:Error("password-canary"),stderr:"password-canary"},
 {status:1,stderr:"Error code: P3018\nDatabase error code: 42501\nraw-statement-canary"},
 {status:0,stdout:"Error code: P3018\nError code: P3018\nNo pending migrations to apply."},
 {status:0,stdout:"No pending migrations to apply.\u0000password-canary"}])pass(()=>{
 const value=summarizeProcess(result,"deploy");assert(!JSON.stringify(value).includes("canary"));assert.equal(value.database_qualification_claimed,false);
 if(result.status===null)assert.equal(value.status,"CLI_CLOSURE_UNCONFIRMED_STOP_AND_CLEAN_EXACT_RESOURCE");
 else if(result.status===1){assert.deepEqual(value.prisma_codes,["P3018"]);assert.deepEqual(value.sqlstates,["42501"]);}
 else assert.equal(value.status,"CLI_OUTPUT_REJECTED_STOP_AND_INSPECT");
});
console.log(JSON.stringify({schema:"workinants.two-history-v1-guard-focused-checks.v1",checks,pure_shape_checks:pureChecks,
 actual_source8_API_synthetic_tools_checks:checks-pureChecks,status:"PASS_ENVIRONMENT_FREE_API_ONLY",source_files:source.size,
 synthetic_tool_members:10300,real_10300_tool_files_cryptographically_validated:false,real_process_spawned:false,database_contacted:false,Posture:"D"}));
