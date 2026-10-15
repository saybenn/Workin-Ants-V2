# Workin Ants code standards

Read with context-map.md, the owning Module architecture and its implementation plan. This file governs implementation form; it does not grant feature scope or alter a lifecycle.

## Repository baseline

The repository declares Next 16.2.6, React 19.2.4, TypeScript strict mode with noUncheckedIndexedAccess/noImplicitOverride, Prisma 7 and Supabase. package-lock.json governs installed resolution; these declarations do not prove provider qualification. Before Next code changes read the installed node_modules/next/dist/docs guidance required by AGENTS.md. Preserve the actual pages/ routing layout unless a separately scoped migration is approved.

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
