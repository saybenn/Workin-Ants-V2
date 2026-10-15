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
