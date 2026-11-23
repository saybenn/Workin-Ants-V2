// Local-only migration target guard. No database connection or child process.
import fs from "node:fs";
import crypto from "node:crypto";
import os from "node:os";
import path from "node:path";

export const SOURCE_ROOT = "/run/wa-f0-source";
export const TOOLS_ROOT = "/run/wa-f0-tools";
export const PRIVATE_ROOT = "/run/wa-secrets";
export const ATTESTATION = PRIVATE_ROOT + "/wa-runtime-lease-history-v1-attestation.json";
export const URL_FILE = PRIVATE_ROOT + "/wa-runtime-lease-history-v1-migrator-url";
export const IMAGE = "docker.io/library/postgres:17.11@sha256:996e9dc583ba9f0265a2c75547a9c95fb22c251e394749cab205a0a00e1856a1";
const HASH = /^[0-9a-f]{64}$/;

export class HeldFailure extends Error {
  constructor(code) { super(code); this.code = code; }
}
export function requireLocal(value, code) {
  if (!value) throw new HeldFailure(code);
}
export function sha256(value) { return crypto.createHash("sha256").update(value).digest("hex"); }


export const HISTORY = "prisma/local-f0-runtime-lease-history-v1/migrations";
export const HISTORY_MANIFEST = "prisma/local-f0-runtime-lease-history-v1/history-manifest.json";
export const SCHEMA = "prisma/review/foundation-candidate.prisma";
export const CONFIG = "prisma.local-f0-runtime-lease-history-v1.config.mjs";
export const RUNTIME = [CONFIG, "scripts/sql-review/local-f0-runtime-lease-history-v1-guard.mjs", "scripts/sql-review/local-f0-runtime-lease-history-v1-runner.mjs"];
export const INITIAL = "5ae39abf991f9c189e367eb6ab6968b0ad50836bf4220ac27ef8c18306ac26ad";
export const APPEND = "49c3345c281d8ef62355d5392d02085d5fdfa71f7193e7e0bd4264562c33cfb7";
export const ORDERED = [
  {id:"20261117000100_f0_local_initial",path:HISTORY+"/20261117000100_f0_local_initial/migration.sql",sha256:INITIAL},
  {id:"20261120000100_f0_runtime_lease_branch_v1",path:HISTORY+"/20261120000100_f0_runtime_lease_branch_v1/migration.sql",sha256:APPEND},
];
export const ORDERED_SHA = sha256(JSON.stringify(ORDERED.map(row => ({id:row.id,path:row.path,sha256:row.sha256}))));
const OLD_EXPECTED = "3be81a13d3bb2abb41bf03ef68398da6d92fbdbccffec3d74508e91dd455f433";
function keys(value, expected, code) {
  requireLocal(value !== null && typeof value === "object" && !Array.isArray(value) &&
    JSON.stringify(Object.keys(value).sort()) === JSON.stringify([...expected].sort()), code);
}
function equal(a,b) { return JSON.stringify(a) === JSON.stringify(b); }
// Strict raw parsing preserves duplicate-key, finite-number and bounded-depth
// requirements at the file boundary. A JSON.parse reviver cannot detect keys
// which the parser has already overwritten.
export function strictJson(raw) {
  requireLocal(Buffer.isBuffer(raw) && raw.length > 0 && raw.length <= 4*1024*1024 &&
    !(raw[0]===0xef && raw[1]===0xbb && raw[2]===0xbf), "JSON_SIZE_ENCODING");
  let text;
  try { text=new TextDecoder("utf-8",{fatal:true,ignoreBOM:true}).decode(raw); } catch { throw new HeldFailure("JSON_ENCODING"); }
  let i=0, budget=300000;
  function ws(){while(i<text.length && /[ \t\r\n]/.test(text[i]))i++;}
  function string(){
    requireLocal(text[i]==='"',"JSON_STRING"); const start=i++;
    while(i<text.length){
      const c=text[i++];
      if(c==='"'){try{return JSON.parse(text.slice(start,i));}catch{throw new HeldFailure("JSON_STRING");}}
      if(c==='\\'){requireLocal(i<text.length,"JSON_STRING");i++;}
      else requireLocal(c.charCodeAt(0)>=32,"JSON_STRING");
    }
    throw new HeldFailure("JSON_STRING");
  }
  function value(depth){
    requireLocal(depth<=48 && --budget>=0,"JSON_BOUNDS");ws();
    if(text[i]==='"')return string();
    if(text[i]==='{'){
      i++; const out=Object.create(null), seen=new Set();ws();
      if(text[i]==='}'){i++;return out;}
      while(true){
        ws();const k=string();requireLocal(!seen.has(k),"DUPLICATE_JSON");seen.add(k);ws();requireLocal(text[i++]===':',"JSON_OBJECT");
        out[k]=value(depth+1);ws();const c=text[i++];if(c==='}')return out;requireLocal(c===',',"JSON_OBJECT");
      }
    }
    if(text[i]==='['){
      i++;const out=[];ws();if(text[i]===']'){i++;return out;}
      while(true){out.push(value(depth+1));ws();const c=text[i++];if(c===']')return out;requireLocal(c===',',"JSON_ARRAY");}
    }
    for(const [token,result]of[["true",true],["false",false],["null",null]])if(text.startsWith(token,i)){i+=token.length;return result;}
    const number=text.slice(i).match(/^-?(?:0|[1-9][0-9]*)(?:\.[0-9]+)?(?:[eE][+-]?[0-9]+)?/);
    requireLocal(number!==null,"JSON_VALUE");i+=number[0].length;const result=Number(number[0]);requireLocal(Number.isFinite(result),"NONFINITE_JSON");
    return result;
  }
  const result=value(0);ws();requireLocal(i===text.length,"JSON_TRAILING");return result;
}
export function validateManifest(planned) {
  keys(planned,["schema","run_id","purpose","target","source","history","tools"],"RUN_FIELDS");
  requireLocal(planned.schema==="workinants.local-f0-runtime-lease-history-run.v1" &&
    planned.purpose==="LOCAL_F0_RUNTIME_LEASE_TWO_MIGRATION_REHEARSAL","NEW_RUN_MANIFEST");
  requireLocal(typeof planned.run_id==="string" && /^[0-9a-f]{8}-[0-9a-f]{4}-4[0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$/.test(planned.run_id),"UUID4_RUN_REQUIRED");
  const target=planned.target, source=planned.source;
  keys(target,["container_name","volume_name","database","image","network","labels","bootstrap_secret_host_path"],"TARGET_FIELDS");
  requireLocal(target.image===IMAGE && target.database==="wa_p0c_rehearsal" && target.network==="none","LOCAL_TARGET");
  for(const name of["container_name","volume_name"])requireLocal(typeof target[name]==="string" && /^wa-p0c-[a-z0-9][a-z0-9-]{0,110}$/.test(target[name]),"RESOURCE_NAME");
  requireLocal(typeof target.bootstrap_secret_host_path==="string" && /^[A-Za-z]:\\[^\x00-\x1f<>"|?*]+$/.test(target.bootstrap_secret_host_path) &&
    !target.bootstrap_secret_host_path.includes("/") && !target.bootstrap_secret_host_path.slice(2).includes(":") &&
    target.bootstrap_secret_host_path.slice(3).split("\\").every(x=>x && x!=="." && x!==".." && !/[ .]$/.test(x)),"ABSOLUTE_WINDOWS_SECRET_PATH_REQUIRED");
  keys(target.labels,["workinants.rehearsal","workinants.rehearsal.run"],"LABEL_FIELDS");
  requireLocal(target.labels["workinants.rehearsal"]==="p0c-local-f0" && target.labels["workinants.rehearsal.run"]===planned.run_id,"EXACT_RUN_LABELS");
  keys(planned.history,["path","ordered"],"HISTORY_FIELDS");
  requireLocal(planned.history.path===HISTORY && equal(planned.history.ordered,ORDERED),"EXACT_TWO_HISTORY_REQUIRED");
  keys(source,["initial_sql_sha256","append_sql_sha256","ordered_history_sha256","effective_expected_sha256","foundation_schema_sha256","runtime_files_sha256"],"SOURCE_FIELDS");
  requireLocal(source.initial_sql_sha256===INITIAL && source.append_sql_sha256===APPEND && source.ordered_history_sha256===ORDERED_SHA &&
    source.foundation_schema_sha256==="de069b3beae07ab7f29167203efae11937f6a29c470cb1c95c2c143fdb623723" &&
    typeof source.effective_expected_sha256==="string" && HASH.test(source.effective_expected_sha256) && source.effective_expected_sha256!==OLD_EXPECTED,"EXACT_TWO_SOURCE_PINS");
  keys(source.runtime_files_sha256,RUNTIME,"EXACT_RUNTIME3");
  requireLocal(RUNTIME.every(n=>typeof source.runtime_files_sha256[n]==="string" && HASH.test(source.runtime_files_sha256[n])),"RUNTIME_HASH_FIELDS");
  keys(planned.tools,["node_version","prisma_version","engine_commit","files_sha256"],"TOOLS_FIELDS");
  requireLocal(planned.tools.node_version==="v24.22.1" && planned.tools.prisma_version==="7.10.1" &&
    planned.tools.engine_commit==="d1b3f377ca835d73fd50954a5e22128b9ebdd6b8","PINNED_TOOLS");
  requireLocal(planned.tools.files_sha256 && typeof planned.tools.files_sha256==="object" && !Array.isArray(planned.tools.files_sha256) &&
    Object.keys(planned.tools.files_sha256).length===10300,"COMPLETE10300_TOOLS");
  return planned;
}
export function validateAttestation(value) {
  keys(value,["schema","planned","run_manifest_sha256","observed"],"ATTESTATION_FIELDS");
  requireLocal(value.schema==="workinants.local-f0-runtime-lease-history-live-attestation.v1","NEW_ATTESTATION_SCHEMA");
  const planned=validateManifest(value.planned), observed=value.observed;
  keys(observed,["endpoint","context","container_id","container_name","volume_name","image","network","published_ports","labels","bootstrap_secret_host_path"],"OBSERVATION_FIELDS");
  requireLocal(observed.endpoint==="npipe:////./pipe/dockerDesktopLinuxEngine" && observed.context==="desktop-linux","LOCAL_ENDPOINT");
  requireLocal(typeof observed.container_id==="string" && HASH.test(observed.container_id) && observed.container_name===planned.target.container_name && observed.volume_name===planned.target.volume_name,"LIVE_RESOURCE_IDENTITY");
  requireLocal(observed.image===IMAGE && observed.network==="none" && observed.published_ports===false,"LIVE_PRIVATE_TARGET");
  requireLocal(observed.bootstrap_secret_host_path===planned.target.bootstrap_secret_host_path,"LIVE_BOOTSTRAP_SECRET_BIND");
  requireLocal(equal(observed.labels,planned.target.labels),"LIVE_RUN_LABELS");
  requireLocal(typeof value.run_manifest_sha256==="string" && HASH.test(value.run_manifest_sha256),"RUN_MANIFEST_HASH");
  return value;
}

export function validateUrl(raw) {
  requireLocal(typeof raw === "string" && raw.length > 0 && raw.length < 4096 && raw === raw.trim(), "PRIVATE_URL_SHAPE");
  let url;
  try { url = new URL(raw); } catch { throw new HeldFailure("PRIVATE_URL_SHAPE"); }
  requireLocal(url.protocol === "postgresql:" && url.hostname === "127.0.0.1" && url.port === "5432", "LOOPBACK_ONLY");
  requireLocal(url.username === "wa_migrator" && url.password.length > 0 && url.pathname === "/wa_p0c_rehearsal" && !url.hash, "MIGRATOR_DATABASE_ONLY");
  const entries = [...url.searchParams];
  requireLocal(entries.length >= 1 && entries.length <= 2 && url.searchParams.getAll("schema").length === 1 && url.searchParams.get("schema") === "public", "PRIVATE_LEDGER_SCHEMA");
  requireLocal(entries.every(([key, value]) => key === "schema" && value === "public" || key === "sslmode" && value === "disable") && url.searchParams.getAll("sslmode").length <= 1, "URL_OPTIONS_DENIED");
  return raw;
}

export function readNoFollow(filename, privateFile = false) {
  let descriptor;
  try {
    descriptor = fs.openSync(filename, fs.constants.O_RDONLY | fs.constants.O_NOFOLLOW);
    const info = fs.fstatSync(descriptor);
    requireLocal(info.isFile() && info.nlink === 1 && info.size >= 0 && info.size <= 16*1024*1024 && info.uid === 0 && (info.mode & 0o022) === 0 && (!privateFile || (info.mode & 0o777) === 0o600), "FILE_OWNER_MODE");
    return fs.readFileSync(descriptor);
  } catch (error) {
    throw error instanceof HeldFailure ? error : new HeldFailure("FILE_UNAVAILABLE");
  } finally { if (descriptor !== undefined) fs.closeSync(descriptor); }
}

function listFiles(directory) {
  const result = [];
  function walk(current, relative) {
    const info = fs.lstatSync(current);
    requireLocal(info.uid === 0 && !info.isSymbolicLink() && (info.mode & 0o022) === 0, "TREE_OWNER_MODE");
    if (info.isFile()) result.push(relative);
    else {
      requireLocal(info.isDirectory(), "TREE_REGULAR_FILES_ONLY");
      for (const entry of fs.readdirSync(current)) walk(current + "/" + entry, relative ? relative + "/" + entry : entry);
    }
  }
  walk(directory, "");
  return result.sort();
}

function sourceFile(relative) {
  requireLocal(typeof relative === "string" && relative.length > 0 && !relative.includes("\\") && !relative.startsWith("/") && !relative.includes(":") && relative.split("/").every(part => part && part !== "." && part !== ".."), "RELATIVE_PATH");
  return relative;
}


export function verifyInputs(attestation,io,identity) {
  validateAttestation(attestation);
  requireLocal(identity.platform==="linux" && identity.arch==="x64" && identity.node==="v24.22.1","LINUX_PINNED_NODE_REQUIRED");
  requireLocal(identity.hostname===attestation.observed.container_id.slice(0,12),"CONTAINER_HOSTNAME");
  requireLocal(io.mountInfo().split("\n").some(line=>line.split(" ")[4]===PRIVATE_ROOT && line.includes(" - tmpfs ")),"PRIVATE_TMPFS_REQUIRED");
  const planned=attestation.planned, history=strictJson(io.read(SOURCE_ROOT+"/"+HISTORY_MANIFEST));
  keys(history,["schema","scope","run_id","run_manifest_sha256","migrations","ordered","ordered_history_sha256","effective_expected_sha256","foundation_schema","files_sha256","database_contacted","ledger_created_or_modified","raw_structure_applied_separately","public_source_archive_file_count","applied_history_rule"],"NEW_HISTORY_FIELDS");
  requireLocal(history.schema==="workinants.local-f0-runtime-lease-history.v1" && history.scope==="PROVISIONAL_LOCAL_ONLY_NOT_HOSTED_ADOPTION" &&
    history.run_id===planned.run_id && history.run_manifest_sha256===attestation.run_manifest_sha256,"HISTORY_RUN_IDENTITY");
  requireLocal(history.migrations===HISTORY && equal(history.ordered,ORDERED) && history.ordered_history_sha256===ORDERED_SHA,"EXACT_ORDERED_TWO_HISTORY");
  requireLocal(history.effective_expected_sha256===planned.source.effective_expected_sha256 &&
    history.foundation_schema===SCHEMA && history.database_contacted===false && history.ledger_created_or_modified===false &&
    history.raw_structure_applied_separately===false && history.public_source_archive_file_count===8 &&
    history.applied_history_rule==="Both exact applied checksums immutable; no resolve/baseline/direct ledger mutation in this family.","EXACT_NEW_HISTORY_PROVENANCE");
  const expected=[SCHEMA,...RUNTIME,HISTORY+"/migration_lock.toml",...ORDERED.map(r=>r.path)].sort(), files=history.files_sha256;
  keys(files,expected,"EXACT_SEVEN_DECLARED_SOURCES");
  requireLocal(files[SCHEMA]===planned.source.foundation_schema_sha256 && ORDERED.every(r=>files[r.path]===r.sha256) &&
    RUNTIME.every(n=>files[n]===planned.source.runtime_files_sha256[n]),"REVIEWED_RUNTIME_SQL_SCHEMA");
  requireLocal(equal(io.listFiles(SOURCE_ROOT).sort(),[...expected,HISTORY_MANIFEST].sort()),"EXACT_SOURCE8_CLOSURE");
  requireLocal(equal(io.listFiles(SOURCE_ROOT+"/"+HISTORY).sort(),["migration_lock.toml",...ORDERED.map(r=>r.id+"/migration.sql")].sort()),"UNLISTED_HISTORY_DENIED");
  for(const [relative,h]of Object.entries(files))requireLocal(typeof h==="string" && HASH.test(h) && sha256(io.read(SOURCE_ROOT+"/"+sourceFile(relative)))===h,"SOURCE_FILE_DRIFT");
  requireLocal(io.read(SOURCE_ROOT+"/"+HISTORY+"/migration_lock.toml").equals(Buffer.from('provider = "postgresql"\n')),"EXACT_PROVIDER_LOCK");
  const tools=planned.tools.files_sha256;
  for(const required of["node/bin/node","schema-engine","node_modules/prisma/build/index.js","node_modules/prisma/build/cli.js","node_modules/prisma/config.js","node_modules/prisma/package.json"])requireLocal(typeof tools[required]==="string" && HASH.test(tools[required]),"TOOL_FILE_MAP");
  requireLocal(equal(io.listFiles(TOOLS_ROOT).sort(),Object.keys(tools).sort()),"EXACT_TOOL_CLOSURE_REQUIRED");
  for(const [relative,h]of Object.entries(tools))requireLocal(typeof h==="string" && HASH.test(h) && sha256(io.read(TOOLS_ROOT+"/"+sourceFile(relative)))===h,"TOOL_FILE_DRIFT");
  requireLocal(strictJson(io.read(TOOLS_ROOT+"/node_modules/prisma/package.json")).version==="7.10.1","PRISMA_VERSION");
  const databaseUrl=validateUrl(io.readPrivate(URL_FILE).toString("utf8"));
  return {schema:SOURCE_ROOT+"/"+SCHEMA,migrations:SOURCE_ROOT+"/"+HISTORY,databaseUrl,orderedHistory:ORDERED,
    config:SOURCE_ROOT+"/"+CONFIG,cli:TOOLS_ROOT+"/node_modules/prisma/build/index.js",
    engine:TOOLS_ROOT+"/schema-engine",configLibrary:TOOLS_ROOT+"/node_modules/prisma/config.js"};
}

export function loadLocalF0Config() {
  try {
    const privateDirectory = fs.lstatSync(PRIVATE_ROOT);
    requireLocal(privateDirectory.isDirectory() && !privateDirectory.isSymbolicLink() && privateDirectory.uid === 0 && (privateDirectory.mode & 0o777) === 0o700, "PRIVATE_DIRECTORY_OWNER_MODE");
    const attestation = strictJson(readNoFollow(ATTESTATION, true));
    return verifyInputs(attestation,
      {read: filename => readNoFollow(filename), readPrivate: filename => readNoFollow(filename, true), listFiles, mountInfo: () => fs.readFileSync("/proc/self/mountinfo", "utf8")},
      {platform: process.platform, arch: process.arch, node: process.version, hostname: os.hostname()});
  } catch (error) { throw error instanceof HeldFailure ? error : new HeldFailure("INVALID_LOCAL_CONFIGURATION"); }
}
