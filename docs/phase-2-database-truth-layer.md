# Phase 2 Database Truth Layer

Phase 2 establishes the normalized Postgres source-of-truth schema for WorkinAnts. It does not build auth flows, RLS policies, Stripe checkout, Typesense indexing, AI classification, UI flows, or full messaging behavior.

## Object Laws

`User` is the account holder. Users can buy offerings, post gigs, create profiles, belong to organizations, upload media, and send messages. Users do not sell offerings directly.

`ProfessionalProfile` is the seller identity. Offerings belong to professional profiles, and gig responses come from professional profiles.

`CandidateProfile` is the job-seeking identity. Candidate profiles apply to jobs.

`Organization` is a hiring entity. Organizations post jobs and manage members. Organizations do not sell offerings.

`Offering` is something a professional profile sells. Gigs are not offerings.

`Gig` is a public paid request posted by a user. The accepted flow is gig response, gig assignment, then order.

`Job` is a formal hiring post from an organization. Jobs are not gigs or offerings.

`Order` is transaction truth. Stripe is a payment rail only.

## Taxonomy

The controlled dictionary is:

```txt
TaxonomyDomain
TaxonomyCategory
TaxonomyTag
```

Profiles, organizations, offerings, gigs, and jobs use explicit join tables for category/tag assignment. Tag joins can carry provenance such as `source`, `confidence`, and `verified`.

The seed now loads the static WorkinAnts taxonomy: 12 active domains, 57 active categories, and 156 active tags. `TaxonomyTag` is the controlled L3 discovery vocabulary. Tags may be semantic phrases such as `Cloud Migration`, `Security Auditing`, or `Full-Stack Development`; future AI/search systems can tokenize, synonymize, and enrich those phrases, but should not create uncontrolled taxonomy rows without validation.

## Media

`MediaAsset` stores file metadata only. Ownership and attachment use explicit join tables such as `UserMedia`, `ProfessionalProfileMedia`, `OfferingMedia`, `GigMedia`, `JobMedia`, `OrderFile`, and `MessageMedia`.

Do not use polymorphic `ownerType` / `ownerId` media ownership.

`User.media` means media attached to the user profile. `User.uploadedMedia` means files uploaded by that user anywhere in the system.

## Prisma Config

This repo currently uses Prisma 7. The schema uses Prisma 7 datasource style:

```prisma
datasource db {
  provider = "postgresql"
  schemas  = ["public", "app"]
}
```

The datasource URL is configured in root-level `prisma.config.ts` from `DATABASE_URL`.

## Commands

```bash
npm run db:validate
npm run db:format
npm run db:migrate
```

Segment 1 validates and formats schema/config only. Migrations, seed data, and database integrity checks are handled in later Phase 2 segments.

## Segment 2 Migration Status

Prisma 7.8.0 is installed. The Phase 2 migration exists:

```txt
prisma/migrations/20260602021702_phase_2_database_truth_layer
```

`prisma migrate status` reports the configured Supabase database is up to date.

Scratch-apply verification has not been run because the configured database is Supabase, not a disposable local database. Do not reset or drop it for scratch verification.

## Segment 3 Seed Status

`prisma/seed.ts` creates representative Phase 2 data for:

- controlled taxonomy domains, categories, and tags
- account users
- professional and candidate profiles
- an organization and organization member
- service, product, and course offerings
- a public gig, response, assignment, and gig-sourced order
- an organization job and candidate application
- an offering-sourced order, order events, order file, agreement, and review
- explicit media attachments
- a minimal messaging shell
- notification, search upsert, processed Stripe event, and audit event shell records

The seed uses stable UUIDs and SQL `on conflict` handling so it can be rerun without duplicating seed-owned records.

Because this repo currently has Prisma 7's client engine mode and does not have a driver adapter such as `@prisma/adapter-pg` installed, the seed uses the installed `psql` client instead of Prisma Client queries. This avoids adding Phase 3 behavior and keeps the seed dependency-light.

Run:

```bash
npm run db:seed
```

The current script is:

```bash
node --experimental-strip-types prisma/seed.ts
```

Node may warn that the package has no `"type": "module"`; that warning does not block the seed.

## Segment 4 Integrity Status

`scripts/check-db-integrity.ts` verifies the seeded database relationships and selected schema laws:

- ProfessionalProfile has Offerings
- User has a posted Gig
- Gig has a GigResponse
- GigResponse connects to a GigAssignment
- GigAssignment connects to an Order
- Organization has a Job
- CandidateProfile has a JobApplication
- Offering connects to an Order
- media is attached through explicit join tables
- SearchUpsertEvent, ProcessedStripeEvent, and AuditEvent shell records exist
- duplicate GigResponse, JobApplication, and Offering slug constraints are enforced
- no user-owned or organization-owned offering columns exist
- no `gig_details` table exists
- no polymorphic media owner columns exist
- no `seller_org_id` order column exists

Run:

```bash
npm run db:check
```

The current script is:

```bash
node --experimental-strip-types scripts/check-db-integrity.ts
```

Final Phase 2 database verification passed:

```txt
prisma validate
prisma format
prisma validate
prisma migrate status
npm run db:seed
npm run db:check
```

Repository-wide `lint` passed. Repository-wide `typecheck` and `build` are currently blocked by stale generated Next route validator references to missing `app/` files after the working tree moved those files under `pages/`. That is separate from the Phase 2 database truth layer.
