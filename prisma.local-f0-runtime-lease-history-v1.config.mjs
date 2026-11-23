// Provisional local rehearsal only. No dotenv, root DATABASE_URL or shadow target.
import { createRequire } from "node:module";
import { loadLocalF0Config } from "./scripts/sql-review/local-f0-runtime-lease-history-v1-guard.mjs";

const local = loadLocalF0Config();
const { defineConfig } = createRequire(import.meta.url)(local.configLibrary);
export default defineConfig({
  schema: local.schema,
  migrations: { path: local.migrations },
  datasource: { url: local.databaseUrl },
});
