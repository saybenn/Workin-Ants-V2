// P0-C-03 pinned-engine compatibility; source-only exact command only.
const cp = require('node:child_process');
const path = require('node:path');
const expected = ['migrate','diff','--from-empty','--to-schema','prisma/review/foundation-candidate.prisma','--config','prisma.foundation-review.config.ts','--script','--output','review-output/foundation-structure.sql'];
if (JSON.stringify(process.argv.slice(2)) !== JSON.stringify(expected)) throw new Error('Source-only compatibility preload refuses other commands');
if (process.env.PRISMA_SCHEMA_ENGINE_BINARY || process.env.PRISMA_ENGINES_MIRROR) throw new Error('Unreviewed engine override');
const spawn = cp.spawn;
cp.spawn = function(file, args = [], options) {
 if (path.basename(String(file)) === 'schema-engine-windows.exe') {
  if (args.includes('--datasource')) throw new Error('Unexpected engine datasource');
  args = [...args, '--datasource', '{}'];
 }
 return spawn.call(this, file, args, options);
};
