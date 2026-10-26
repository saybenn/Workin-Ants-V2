# P0-B dependency security requalification — 26 October 2026

**PASS for the bounded foundation and known npm advisories at the recorded audit time.** The refreshed full-tree audit found 19 affected packages before remediation (1 critical, 14 high, 4 moderate). The October 19 omit-development audit found 15; date and scope differ. Both final audits exited zero with zero known vulnerabilities. This is not product-wide security certification or immunity to future advisories.

## Reviewed change

| Direct package | Before | After |
|---|---|---|
| Next.js | 16.2.6 | 16.4.3 |
| eslint-config-next | 16.2.6 | 16.4.3 |
| Prisma CLI | ^7.8.0, resolved 7.8.0 | 7.10.1, exact |
| Prisma Client | ^7.8.0, resolved 7.8.0 | 7.10.1, exact |

React/react-dom remain 19.2.4. Node 24.22.1/npm 11.9.0 are the final qualification pins. Node moved from 24.19.0 because the October 21 security release addresses runtime vulnerabilities outside npm audit; this remains Node 24. No audit fix, override, unrelated direct dependency or ORM major upgrade was used. Prisma 7.10.1's published internal engines-version package is 8.1.0-1; actual ORM client/CLI/engines remain7.10.1.

[The complete reviewed diff](phase0-security-file-changes.json) records83 existing version changes,50 added entries and9 removed entries, including required parent dependencies and optional OS binaries. [Coverage](dependency-remediation-coverage-2026-10-26.json) accounts for all19 prior affected packages and advisory references. Targeted compatible transitive updates resolve the remaining browser mapping/source-map-js/brace-expansion/browserslist/js-yaml/zod findings; Hono/node-server are no longer selected. Reachability is not used to waive a finding.

## Actual checks and recovery

Clean npm ci with lifecycle scripts,lint,route typegen/strict tsc,production build,installed dependency graph,offline Prisma validation and both audits passed. Final HTTP suite: **47/47**, retaining the original41 cases and adding image-source/scheme denial without contacting a local canary,diagnostic denial with spoofed internal-looking headers and exact AGENTS preservation. Windows-specific execution and dormant next/og/use-cache features are untested.

Next startup rewrites its managed AGENTS section. Previously nested database rules were removed during the first smoke run. Restored the exact block outside generated markers; subsequent dev/production/restart tests prove preservation. No product runtime source,UI classes/tokens,schema or historical migration changed.

An initial lock-only attempt used Node's bundled npm11.17.0 and produced an engine warning. Final resolution and qualification used npm 11.9.0. An initial package-only qualification under Node 24.19.0 was superseded after the runtime advisory review; all final checks repeat on Node 24.22.1. A help command without the offline Prisma config failed on missing DATABASE_URL; explicit offline-config help/validation passed. No connection string was supplied and no database was contacted. [Current evidence](phase0-security-requalification.json) retains failures/recovery separately from historical Checkpoint006.

The final runtime suite also checks the exact Node pin, rejection of DNS-only certificates for seven IP spellings, and matching-IP/DNS positive controls. These synthetic checks are not full TLS handshakes or exhaustive runtime exploit coverage.

## Primary sources

Accessed26 October2026; paraphrased findings,not application test results.

- [Node October 21 security release](https://nodejs.org/en/blog/vulnerability/october-2026-security-releases) and [Node 24.22.1 release](https://nodejs.org/en/blog/release/v24.22.1): runtime TLS/DNS/Brotli/HTTP/crypto/permission and bundled-library security fixes; final runtime downloaded from the official distribution and SHA-256 verified.
- [Next typed-array cache advisory](https://github.com/vercel/next.js/security/advisories/GHSA-673q-mjm6-r5xr): affected through16.4.0; patched16.4.1. An earlier16.3.x target misses this October notice.
- [Next SVG/image advisory](https://github.com/vercel/next.js/security/advisories/GHSA-2464-fhr4-w9xw): patched16.4.1; fixed sharp0.35.5,which the selected lock resolves.
- [Next16.4.3 release](https://github.com/vercel/next.js/releases/tag/v16.4.3): stable matched framework/lint update.
- [Prisma ORM7.10.1 release](https://github.com/prisma/orm/releases/tag/7.10.1): security dependency updates and nested-transaction option fix. Actual database transactions are not qualified here.
- [Prisma v7 dependency update](https://github.com/prisma/orm/pull/30189): upstream adoption of deepmerge-ts8.0.2;no local cross-major override.

Exact installed Next16.4.3 layouts,route handlers,not-found,environment,Turbopack,CLI,ESLint and image guidance were reviewed and fingerprinted. Prisma7.10.1 offline-config validation/migrate-diff help was inspected. No DDL was generated.

## Next gate

P0-C remains D with all12 actual provenance items not obtained. [The concrete handoff](database-provenance-handoff.md) states the next owner action and schema-only probe,which has not been executed. No replay,RLS,shared runtime,owner adapter,Privacy/provider qualification,contract freeze,parallel lane or public release follows from P0-B.
