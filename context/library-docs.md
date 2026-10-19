# Provider and library evidence guide

This is an evidence-routing guide, not a claim that any vendor is production-qualified.

| Concern | Repository evidence | Required before implementation/activation |
|---|---|---|
| Next/React | package.json, package-lock.json, actual pages/ layout | Installed Next documentation required by AGENTS; validate actual version-specific APIs |
| TypeScript | tsconfig.json | Strict typechecking and runtime parsing of external data |
| Prisma/Postgres | prisma/schema.prisma, migrations/, prisma.config.ts | Database provenance decision, forward migration plan, disposable replay and privilege/constraint comparison |
| Supabase identity | Identity architecture, local provider mapping ruling | Qualified subject/account linkage, session/revocation and pre-account eligibility behavior |
| Payments/tax | Payment architecture and provider ports | Actual merchant/account/region scope, callback authentication, idempotency retention and ambiguous-effect recovery |
| Media/scanning/video | Media and Video architectures | Storage/access revocation, bounded grants, scanner stages, delivery evidence and applicable sensitive-content configuration |
| Search | Search architecture | Protected collection isolation, current-authority filtering, deletion/rebuild/reconciliation behavior |
| Messaging/notifications | Respective owner architectures | Channel eligibility, credentials, callback evidence strength, recipient privacy and actual provider limits |
| Screening/Healthcare | Trust/Healthcare architectures | Approved purpose/consent/legal policy and actual provider/account/region qualification; brand names alone do not qualify |

For each provider adapter keep a versioned qualification record: exact package/API version, official source link and retrieval date, account/region/configuration, supported operations, failure/idempotency/revocation behavior, data fields sent, approved retention, test evidence, owner and expiration/review trigger. Read current official documentation when selecting or changing an adapter; historical recommendations cannot substitute for this record. Do not include credentials or personal payloads in context artifacts.

Do not install speculative libraries during architecture reconciliation. Existing package declarations are repository facts; operational claims require current primary documentation and tests at implementation time.


## Directive 005 repository/toolchain evidence

Observed 2026-10-19: package.json declares Next 16.2.6, React 19.2.4, Prisma 7.8 range, Supabase JS 2.106 range and Tailwind 4; lockfile governs exact resolution. The available toolchain reports Node v24.19.0 / npm 11.9.0. `npm ci --offline --ignore-scripts --no-audit --no-fund` failed EUSAGE because lock resolution reports missing @emnapi/core/@emnapi/runtime entries. No successful dependency install, lint/typecheck/build, Prisma generation or provider qualification followed. A bounded lock repair attempt and exact outcome are in the Directive 005 validation record. Inspect actual lock diff and clean install with intended compatible package-manager before changing pinned versions.

Official general Next App Router references retrieved 2026-10-19:

- https://nextjs.org/docs/app/getting-started/layouts-and-pages — page/layout file placement under app/.
- https://nextjs.org/docs/app/api-reference/file-conventions/route — Route Handler file convention.

Those live pages describe current general conventions and do not certify the repository's pinned 16.2.6 implementation. The installed node_modules/next/dist/docs guide required by AGENTS remains unavailable until dependencies install. Do not write version-specific Next code from memory. WA-R090 resolves architecture intent versus the current App Router-style files under pages/; the code normalization remains P0-B work with actual route/build tests.

The contract schema fixture evaluator uses Python stdlib and explicitly supports only its declared JSON Schema assertion subset. It rejects unsupported assertion keywords and unregistered remote refs. Production TS parser/package selection is not implied; whichever adapter is implemented must pass the pinned wire/negative/consumer fixtures. No new runtime dependency is installed to generate contract documentation.

Versioned provider evidence must identify actual provider/account/region/model/configuration/fields/capability, authoritative source/version, positive/negative/recovery/currentness/deletion/revocation tests and legal/retention coverage. Schema examples/reference functions are not evidence of real provider behavior. No credentials or raw sensitive payloads belong in this file or logs.
