<!-- BEGIN:nextjs-agent-rules -->
# This is NOT the Next.js you know

This version has breaking changes — APIs, conventions, and file structure may all differ from your training data. Read the relevant guide in `node_modules/next/dist/docs/` before writing any code. Heed deprecation notices.

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
<!-- END:nextjs-agent-rules -->

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
resolved in that owner before dependent consumers implement them. Do not invent a
parallel lane map or mark a boundary frozen because documents merely exist.

When resuming, preserve current branch work; inspect Git status/HEAD, read the
rulings already applied, continue the earliest unfinished gate and record actual
validation results. No deployment, release, history rewrite or feature-completion
claim is authorized by this checkpoint.
<!-- END:workinants-readiness-checkpoint -->
