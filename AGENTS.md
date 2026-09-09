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
- Orders are transaction truth and point to `buyerUserId` and `sellerProfessionalProfileId`.
- Media attachments use explicit join tables. Do not add polymorphic `ownerType` / `ownerId` media ownership.
- Taxonomy is controlled through `TaxonomyDomain`, `TaxonomyCategory`, and `TaxonomyTag`.
- `TaxonomyTag` is controlled L3 discovery vocabulary. AI may suggest/enrich tags, but AI is not authoritative.
- Do not build RLS, Stripe checkout, Typesense indexing, AI classification, or product UI unless the current task explicitly enters those phases.

Before changing Prisma schema, inspect existing migrations and avoid destructive resets unless explicitly approved.
<!-- END:workinants-database-truth-rules -->
<!-- END:nextjs-agent-rules -->
