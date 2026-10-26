# Workin Ants code standards

Read with context-map.md, the owning Module architecture and its implementation plan. This file governs implementation form; it does not grant feature scope or alter a lifecycle.

## Repository baseline

The repository declares Next 16.4.3, React 19.2.4, TypeScript strict mode with noUncheckedIndexedAccess/noImplicitOverride, Prisma 7.10.1 and Supabase. package-lock.json governs installed resolution; these declarations do not prove provider qualification. Before Next code changes read the installed node_modules/next/dist/docs guidance required by AGENTS.md. WA-R090 resolves the intended App Router convention under app/. Directive006-A/WA-R091 uses a new minimal app/ foundation in an isolated worktree; legacy/checkpoint-005/ preserves old application/configuration bytes outside active routing,lint and strict TypeScript inputs. Read current Phase0 evidence for actual qualified checks. Do not import the inactive archive or claim behavioral migration.

Domain code belongs under features/<canonical-module-id>/ with contracts, domain, application and infrastructure boundaries as needed. Do not reorganize the whole repository to create empty layers. server/ holds server-only execution capabilities; integrations/ holds provider adapters. lib/ is browser-safe shared utility space and cannot contain database credentials or private domain repositories. Thin routes validate transport and delegate to owner commands; UI never assigns domain status directly.

## Contracts and persistence

Export explicit request/result types and discriminated outcomes. Parse untrusted input at transport and adapter boundaries; TypeScript assertions are not validation. Treat owner revision tokens as opaque outside the owner. Reject unknown enum/action values. Use integer minor currency units and explicit currency; snapshots retain the applied policy/version.

Only an owner repository writes its aggregates and contextual joins. A same-database transaction does not authorize foreign repository access. Shared transaction plumbing coordinates explicitly approved participants; source owners retain validation and effects. Commit owner state, immutable evidence and outbox together where required. Network requests cannot be held inside database lock transactions. Provider ambiguity requires reconciliation; a timeout is not proof of non-execution.

Semantic idempotency binds owner, action, subject and payload fingerprint. Reusing a key with different meaning is a conflict. Persist financial and other durable effect receipts for their evidence lifetime; short-lived transport dedupe is insufficient. Concurrent mutation checks expected owner revision. Retained histories append correction evidence rather than overwriting prior decisions.

## Security and failure handling

Authenticate and authorize server-side using canonical Shared Operations. Client flags, Search projections, Consent acceptance and provider status are not independent authority. Follow the owner contract's unavailable/deny/retry distinctions. Do not return private existence or internal evidence in public errors. New tables/views/functions deny browser access until explicitly reviewed; RLS/server parity requires common allowed/denied fixtures.

Use allowlisted structured log metadata. Never log raw resumes, private documents, signed URLs, tokens, exact location, provider secrets or unrestricted payloads. Existing logger accepts arbitrary metadata, so callers must minimize it; its current interface is not a privacy filter. Request correlation is diagnostic, not an idempotency key or trusted actor claim.

## Validation and completion

Test observable invariants: competing commands, stale revisions, changed-payload replay, revoked authority, partial failure and recovery. Use owner-approved contract fakes only after the relevant interface is qualified; fakes cannot invent a missing contract. Provider tests separately prove actual callback/revocation/timeout semantics. A passing unit test does not prove legal approval or database deployment.

Run context checks for context changes. For code changes run the relevant unit/integration checks plus repository lint/typecheck/build where applicable; record actual commands and outcomes, including blocked checks. Do not report a feature complete without architecture/plan feature ID, changed owner files, contract/migration impact, negative-case evidence and integration checkpoint.

One integration owner sequences all Prisma/migration changes. Never rewrite applied migrations, reset a database or generate a replacement baseline from model counts. See reconciliation/database-readiness.md. Canonical context, shared registry and migration changes require integration review before parallel consumers continue.


## Directive 005 contract and agent discipline

Read the connected workflow, individual SH specification and actual owner architecture before implementation. `contracts/shared/` holds closed v1 interface schemas, not production handlers; `tests/contracts/` holds synthetic schema/consumer expectations and reference models. The stdlib schema evaluator is deliberately restricted/offline and is not the production runtime parser. An implementation agent must choose/qualify the actual parser against the same fixtures. Types and assertions are never untrusted-input validation.

Trusted actor/assurance/caller context is resolved by server middleware and supplied outside client request data. Actor IDs/evidence references declared in input never authenticate themselves. A `Secret` reference in fixtures describes a protected trusted-boundary value/handle; it does not mandate a new global vault/source database, authorize a caller, or permit returning handle/credential/raw data through an unreviewed public DTO. Actual secure transport/stream/delivery adapters must preserve the owner contract, field policy and proof-before-secret semantics and receive independent qualification.

Read architectural readiness separately from runtime qualification. EVOLVABLE_COMPATIBLY allows changes preserving exact v1 wire/security/failure meaning; closed fields/enums cannot be silently added. Actual producer/consumer compatibility, storage, RLS, provider and complete Privacy field/action proof precede freeze/activation. `ok` transport status can contain a denied/pending/unknown domain result. No mock/reference model is production evidence.

One integration owner controls common types/schemas, registry/rulings, shared runtime and migrations. Candidate file/model boundaries are in parallel-development-plan.md and its manifest. All lanes remain CANDIDATE_ONLY; an agent cannot activate itself. Modules own executor code; cross-cutting protocols never grant foreign repository writes. Shared schema proposals identify affected owners/consumers, forward/backfill/retention and concurrent invariants before the integrator authors a migration under proven posture.

For a bounded implementation patch load only necessary owner/consumer context plus root invariants, declare the file/model/contract scope and qualification entry conditions, and record exact tests/limits at completion. Run `python scripts/check-foundation.py` for context/contract/boundary changes. At actual application integration also run the pinned toolchain lint/typecheck/build and real adapter/database/provider/security checks required by that phase; missing tools/evidence remain failures or blocked checks, never a skipped-success report.


## Sequential foundation and slice completion

Keep strict TypeScript:use unknown with narrowing instead of any; preserve noUncheckedIndexedAccess/noImplicitOverride. Existing canonical feature folder IDs govern names; do not rename them to a generic template convention. Server Components are the default; use a client boundary only for actual interaction. No feature belongs in the process-only health/debug routes. Production diagnostics deny under NODE_ENV execution mode; NEXT_PUBLIC variables are browser-visible configuration and never an access guard.

Use the proven Node/npm pins and package lock. npm run typecheck generates exact route types before tsc; Next build is separate from ESLint. npm run test:foundation starts/stops loopback-only real dev/prod servers and checks mode denial/restart/secret-canary boundaries. A clean source clone must install from the lock without altering dependency resolutions. No force/legacy-peer/TLS-disable or ignored failure may substitute for qualification.

After each implementation slice update ui-registry.md/json with actual versus planned paths,API/classes/token use,tests and limits—even if no component changed,record that explicitly in the slice evidence. Update progress and Phase0 status,owned files,contract/schema impact,exact commands/failures/recovery and remaining gates. Only a bounded shell can be foundation-qualified; product components/screens need their full owner/security/accessibility qualification. Database write aliases remain blocked under D; the offline Prisma validation config reads no environment and opens no DB connection.
