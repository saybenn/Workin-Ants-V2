import { createHash } from "node:crypto";
import { mkdir, readFile, realpath, writeFile } from "node:fs/promises";
import { dirname, isAbsolute, relative, resolve, sep } from "node:path";
import { createRequire } from "node:module";

const sha = (raw) => createHash("sha256").update(raw).digest("hex");
const require = createRequire(import.meta.url);

function need(value) {
  if (!value) throw new Error("compile_input_or_output_mismatch");
}

function contained(root, path) {
  const name = relative(root, path);
  return name && !name.startsWith(".." + sep) && name !== ".." && !isAbsolute(name);
}

async function main() {
  const [rootArg, outputArg] = process.argv.slice(2);
  need(process.argv.length === 4 && isAbsolute(rootArg) && isAbsolute(outputArg));
  const root = await realpath(rootArg);
  const parent = await realpath(dirname(outputArg));
  const output = resolve(outputArg);
  need(root === rootArg && parent === dirname(output) && output === outputArg);
  need(contained("/workspace/scratch", output) && !contained(root, output));
  const manifest = JSON.parse(await readFile(new URL("./compile-inputs.json", import.meta.url), "utf8"));
  need(process.version === manifest.nodeVersion && manifest.version === "5.9.3");
  async function read(entry) {
    const path = resolve(root, entry.path);
    need(contained(root, path) && await realpath(path) === path);
    const raw = await readFile(path);
    need(raw.length === entry.bytes && sha(raw) === entry.sha256);
    return raw;
  }

  const lock = JSON.parse(await read(manifest.lock));
  const pkg = JSON.parse(await read(manifest.compilerPackage));
  const locked = lock.packages?.["node_modules/typescript"];
  need(pkg.name === "typescript" && pkg.version === manifest.version);
  need(locked?.version === manifest.version && locked.integrity === manifest.npmIntegrity);
  await read(manifest.compiler);
  const compiler = require(resolve(root, manifest.compiler.path));
  need(compiler.version === manifest.version);
  need(manifest.sources.length === 5);

  const emits = {};
  for (const source of manifest.sources) {
    const text = (await read(source)).toString("utf8");
    const result = compiler.transpileModule(text, {
      fileName: source.path,
      reportDiagnostics: true,
      compilerOptions: {
        module: compiler.ModuleKind.CommonJS,
        target: compiler.ScriptTarget.ES2022,
        newLine: compiler.NewLineKind.LineFeed,
        sourceMap: false,
        declaration: false,
        removeComments: false,
      },
    });
    need(result.diagnostics.length === 0 && source.path.endsWith(".ts"));
    const destination = source.path.replace(/\.ts$/, ".js");
    need(!Object.hasOwn(emits, destination) && contained(output, resolve(output, destination)));
    emits[destination] = Buffer.from(result.outputText, "utf8");
  }
  await read(manifest.compiler);
  await mkdir(output, {mode: 0o700});
  emits["package.json"] = Buffer.from('{"private":true,"type":"commonjs"}\n');
  const files = {};
  for (const name of Object.keys(emits).sort()) {
    const path = resolve(output, name);
    await mkdir(dirname(path), {recursive: true, mode: 0o700});
    await writeFile(path, emits[name], {flag: "wx", mode: 0o600});
    files[name] = {bytes: emits[name].length, sha256: sha(emits[name])};
  }
  const result = {schema: "workinants.p0d-customer-proof-compile-result.v1", compilerVersion: compiler.version,
                  compilerSha256: manifest.compiler.sha256, files};
  const text = JSON.stringify(result, null, 2) + "\n";
  await writeFile(resolve(output, "emit-manifest.json"), text, {flag: "wx", mode: 0o600});
  process.stdout.write(text);
}

try {
  await main();
} catch {
  process.exitCode = 1;
  process.stdout.write('{"status":"STOPPED","stage":"OFFLINE_COMPILE"}\n');
}
