<!-- BEGIN:nextjs-agent-rules -->

## This is NOT the Next.js you know

This version has breaking changes — APIs, conventions, and file structure may all differ from your training data. Read the relevant guide in `node_modules/next/dist/docs/` (resolved from this file's directory; in monorepos the `next` package may not be visible from the repo root) before writing any code. Heed deprecation notices.

This block is written and re-added by `next dev` — verify at `node_modules/next/dist/server/lib/generate-agent-files.js`. Removing it from a diff only re-creates the uncommitted change; committing it with your work keeps the tree clean.

<!-- END:nextjs-agent-rules -->

<!-- BEGIN:workinants-database-truth-rules -->
# WorkinAnts Database Truth Rules

Supabase/Postgres is the source of truth.

Prisma schema changes must preserve these object laws:

- Users are account holders and do not sell Offerings directly.
- ProfessionalProfiles are the seller identity. Offerings belong to ProfessionalProfiles.
- Organizations are hiring entities only. Organizations post Jobs and do not sell Offerings.
- CandidateProfiles apply to Jobs.
- Gigs are public paid requests posted by Users. Gigs are not Offerings.
- Jobs belong to Organizations. Jobs are not Gigs or Offerings.
- Orders are transaction truth. Existing marketplace Orders point to `buyerUserId` and `sellerProfessionalProfileId`; CustomerProfile is the commercial buyer identity. Approved platform-facilitated screening Orders require a separate source/participant representation with no fake Professional seller (WA-R003); that schema is not implemented yet.
- Media attachments use explicit join tables. Do not add polymorphic `ownerType` / `ownerId` media ownership.
- Taxonomy is controlled through `TaxonomyDomain`, `TaxonomyCategory`, and `TaxonomyTag`.
- `TaxonomyTag` is controlled L3 discovery vocabulary. AI may suggest/enrich tags, but AI is not authoritative.
- Do not build RLS, Stripe checkout, Typesense indexing, AI classification, or product UI unless the current task explicitly enters those phases.

Before changing Prisma schema, inspect existing migrations and avoid destructive resets unless explicitly approved.
<!-- END:workinants-database-truth-rules -->

## Directive006/006-A — current foundation scope and context loading

Current continuation is bounded by `context/reconciliation/directives/brain-directive-007-resumption.md`. Read `context/reconciliation/launch-scope-baseline.md` for approved launch decisions and `context/phase0-roadmap.md` for the preserved 20-step/P0-A–G sequence. Complete controlled dependency-security remediation/requalification before dependent foundation work; do not treat proposed legal terms, fees, retention periods or future-scope capabilities as approved launch policy. Existing database posture D and runtime/feature/parallel/release boundaries remain until actual evidence changes them.

At each session start read the nine foundational roles in order: `context/project-overview.md` (routing to V3), `context/architecture.md`, `context/build-plan.md`, `context/code-standards.md`, `context/library-docs.md`, `context/ui-tokens.md`, `context/ui-rules.md`, `context/ui-registry.md`, then the current section of `context/progress-tracker.md`. Also read `context/reconciliation/phase0-foundation-report.md` and the current Phase0 status/readiness boundary. Use `context/context-map.md` to selectively load the owning and consuming Module/Cluster architecture/plan, connected journey and exact SH variants required by the task. Do not recursively ingest every historical context artifact or import template example policies.

Current work is the single sequential foundation branch/worktree under Directive006-A. `app/` is a new minimal App Router foundation. The old `pages/` skeleton, utilities and original configurations are preserved byte-for-byte under `legacy/checkpoint-005/` and in Git, outside active compiler/linter/router inputs. It is not a behavioral migration. WA-R091 supersedes the old contents-preserving in-place P0-B implementation instruction while retaining WA-R090 App Router intent. Read installed pinned Next guidance before any framework code change.

Update `context/ui-registry.md` and its structured source after every implementation slice: actual path, API/classes/token usage, tests and limits versus planned-only components. Update progress and Phase0 evidence after every session. Actual foundation smoke qualification does not qualify any of the132 owner contracts, a whole product screen, the database or provider. All eight parallel lanes remain candidates; product implementation remains unapproved.

The preferred database evaluation target is a brand-new isolated development database. Posture D persists until actual identity/preservation/ledger/schema evidence and reviewed migration/RLS replay/security gates pass. Existing `db:migrate`, `db:seed` and `db:check` aliases are deliberately blocked; the old db:check contains SQL writes. Use `db:validate` for environment-free schema validation only. Never run old seed/integrity SQL or restore legacy files to bypass the gate. No live database/migration/provisioning is authorized by this checkpoint.

<!-- BEGIN:workinants-readiness-checkpoint -->
# Development readiness work in progress

Before feature work, read `context/context-map.md`, then
`context/reconciliation/development-readiness-status.md` and
`context/progress-tracker.md`. Resolve actual Module/Cluster paths through the map.
The current readiness checkpoint does **not** authorize product implementation or
parallel development lanes. Continue reconciliation without reopening product
choices already settled by `context/shared/shared-operations.md`.

Authority follows the concern, not file date or directory depth. Module owners
retain lifecycles; Cluster documents coordinate; Shared Operations owns permanent
SH identity/reuse boundaries; plans sequence; progress reports evidence. Apply
architecture changes before dependent plan changes, with a traceable ruling.
Never treat a historical handoff's unresolved label as newer than an applied ruling.

Run `python scripts/check-context.py` after context/registry changes. Passing is
structural evidence only, not readiness or implementation completion. Do not use
live database migration/seed/reset commands to reconcile static coverage. Read
`context/reconciliation/database-readiness.md` before schema/migration work.
Use one integration owner for migration sequencing; no competing canonical models.

No consumer-local authorization, entitlement, provider, queue, Search, Media or
lifecycle substitute may bypass its canonical owner. Missing contracts must be
resolved in that owner before dependent consumers implement them. Directive 005 authorizes a candidate parallel lane map; do not activate a lane
or mark a boundary frozen because documents merely exist.

When resuming, preserve current branch work; inspect Git status/HEAD, read the
rulings already applied, continue the earliest unfinished gate and record actual
validation results. No deployment, release, history rewrite or feature-completion
claim is authorized by this checkpoint.
<!-- END:workinants-readiness-checkpoint -->


## Readiness autonomy policy — 2026-10-12

Read `context/reconciliation/operating-policy.md` for the governing decision and stopping rules. Use `AI_RESOLVED_WITH_PRODUCT_JUDGMENT` for authorized reasonable product defaults and record evidence, reasoning, alternatives, reversibility and affected artifacts. Queue only consequential unresolved owner choices; batch at ten or the stated dependency/sweep limits. Scoped legal/provider/database gates do not stop unrelated work. Continue ordinary readiness gates autonomously. This supersedes earlier stop-on-question instructions; frozen rulings and publication/data safety boundaries remain.


## Directive 005 — mandatory implementation context

Read `context/reconciliation/development-readiness-report.md` for the current decision, then `context/architecture.md`, `context/build-plan.md` Phase 0 and `context/parallel-development-plan.md`. Use `context/context-map.md` for exact owner paths. Load the relevant journey from `context/workflows/platform-workflows.md`, its named SH resources in `context/shared/contracts/`, and both actual owner/consumer architectures and plans before implementing a dependent action.

All 132 Shared Operations have explicit specified architecture; the ledger distinguishes that from NOT_QUALIFIED runtime. EVOLVABLE_COMPATIBLY preserves exact v1 wire/security/failure semantics and does not authorize concurrent implementation. Canonical Confirmed/Proposed markers stay independent. Unknown fields/enums/variants reject; schema/reference fixtures do not prove real producers, consumers, database concurrency, RLS, Privacy fields or providers. No FROZEN_FOR_IMPLEMENTATION operation or active parallel lane is certified at this checkpoint.

Use the root code/library/UI standards. UI context must be read before substantial UI work; actual component states and paths are in ui-registry.md/json. WA-R090 selects App Router intent under app/; Directive006-A now uses a fresh app/ foundation and an inactive legacy archive under WA-R091; current Phase0 evidence records actual checks. Do not change framework code without that guide or invent a second routing model. Existing lock/toolchain failure is a qualification issue, not permission to upgrade dependencies blindly.

One integration owner controls canonical contracts/types, shared runtime, root context, Prisma/migrations and convergence. Candidate lane roots/model responsibilities are in the lane manifest; no lane activates itself. Keep owner repositories private; no feature-local authorization/entitlement/Hold/Media/Search/provider/queue substitutes. Source facts terminate under R085 and do not bypass trusted caller/action/field scope. A caller/actor/evidence ID in input or a fixture never supplies its own authority.

For context/contracts/boundary changes run `python scripts/check-foundation.py`; for actual implementation also run phase-specific real adapter/database/provider/framework tests and record blocked/unrun checks explicitly. Feature completion requires owning plan IDs, file/model/contract impact, positive/negative/compatibility evidence and applicable external qualification. Preserve D until real environment/provenance evidence; no migration/seed/reset, main merge, deployment or broad product implementation is authorized by this readiness directive.
