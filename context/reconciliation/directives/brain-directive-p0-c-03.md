WORKIN ANTS — BRAIN DIRECTIVE P0-C-03
Prepare the Foundation SQL Draft; Do Not Execute It

GOVERNANCE DECISION

Brain has reviewed:
671ef58383580687ecf728036bf32c302aeb026c

The targeted Track-worker permission correction, independent
semantic regressions and P0C-CTX-02 ordering correction are
accepted at source-design level.

Earlier accepted grant-binding and consent designs remain accepted
at that same level.

The 40-model foundation candidate and its supporting specifications
are approved as inputs to SOURCE-ONLY SQL DRAFTING.

This replaces the pre-DDL-generation stop only for this bounded
drafting assignment. Database execution remains prohibited.
Posture D remains. Runtime qualification is not granted.

1. CONTINUE THE EXISTING PROJECT

Working folder:
C:\Users\elijr\source\WorkinAnts-Checkpoint010

Branch:
codex/p0c-candidate-corrections-2026-10-31

Verify the current state and ancestry. Preserve any later work;
do not reset to the reviewed commit or create duplicate workspaces.

Use 671ef58383580687ecf728036bf32c302aeb026c as the reviewed baseline.
Do not alter the old OneDrive checkout or recovery package.

2. GENERATE THE STRUCTURAL REVIEW DRAFT

Use the existing pinned Node/Prisma tooling and environment-free
foundation review configuration.

Confirm the installed CLI flags and source hashes before running
the source-only command recorded in the migration plan:

node node_modules/prisma/build/index.js migrate diff --from-empty --to-schema prisma/review/foundation-candidate.prisma --config prisma.foundation-review.config.ts --script --output review-output/foundation-structure.sql

Use only the 40-model foundation schema, not the full 214-model
candidate or historical June migration.

No datasource, shadow database, live introspection or migration
directory may become an input. Do not load credentials or .env
files. Do not pipe the output into an execution command.

Preserve the raw generated SQL and its fingerprint separately
from the edited, integrated review draft.

3. WRITE THE COMPLETE FOUNDATION SECURITY/ENFORCEMENT DRAFT

Produce actual review SQL—not another outline—for the requirements
applicable to the 40-model foundation.

Include the necessary role/namespace bootstrap draft, ownership,
default privileges, table and column grants, ENABLE/FORCE RLS,
policies, private helpers, constraints and triggers.

Preserve:
- Immutable issuer-committed transaction binding.
- Read-only, narrowly privileged context helpers.
- Exact consent subject/content/presentation/action/context proof.
- The reviewed per-model default-Free worker permissions.
- Immutable receipts and unchanged existing usage.
- Required atomic source/history/evidence/outbox obligations.
- Explicit JSON admission boundaries and nonrecursive bootstrap.

Resolve ordinary SQL implementation details from the approved
specifications. Do not broaden permissions to make a trigger,
helper or test convenient.

Map all 18 SQL requirement IDs to either their applicable F0
implementation or their explicitly deferred scope. Do not
implement later commerce, scheduling, hiring or disabled features
merely because their requirements appear in the full register.

Keep role/environment bootstrap separate from application object
ownership while retaining the selected single application
migration-history strategy.

Do not activate the migration execution path or remove the
existing database-write safeguards.

4. INSPECT THE DRAFT BEFORE RETURNING IT

Check installation order, dependencies, actual columns and types,
function signatures, ownership, search paths, default grants,
role membership, RLS recursion, allowed/denied operations and
transaction boundaries.

Verify that each required F0 invariant has concrete enforcement
or an explicitly identified owner-code dependency. Do not
substitute comments or permissive placeholders for enforcement.

Map the proposed first-replay tests to the draft controls,
including the corrected permission and revocation scenarios.

Use applicable offline checks and available static SQL analysis.
Do not claim SQL execution, catalog parity or runtime success.
A parser or linter pass is not a database test.

If drafting exposes a material conflict with the approved design,
record the exact conflict and recommended correction. Continue
independent safe work; do not silently change the design.

5. RECORD THE STAGE CHANGE HONESTLY

Record this bounded approval in the existing progress tracker
and review navigation.

Preserve the reviewed candidate and historical validation results.
Distinguish:
- Source candidate approved for F0 SQL drafting.
- SQL draft generated but not execution-approved.
- Database adoption and runtime qualification still pending.

Where existing validators deliberately enforce the historical
pre-generation state, retain that historical check and introduce
a separately scoped drafting-stage check. Do not simply disable
execution/adoption safeguards to obtain a passing result.

6. COMMIT, PUBLISH AND REPORT

Commit the review drafts and necessary evidence to the existing
branch. Publish normally to GitHub after checking secrets and
preserving the branch's deployment safeguards.

Verify the remote HEAD. No force-push or main merge.

Keep technical evidence inside the repository. Do not create
another bundle/ZIP or require a manual file-transfer cycle when
publication succeeds.

Return a short human-facing report:
- What scripts were prepared.
- What was checked and what remains untested.
- Any issue requiring Brain's decision.
- The published commit.
- “Ready for SQL review; no human setup action needed,”
  when applicable.

STOP BOUNDARY

No container starts, image pulls, database connections, SQL
execution, migration application, seed/reset, provider changes,
hosted Supabase actions or product-runtime implementation.

Do not run migrate dev, migrate deploy, db push, db execute or
equivalent database-writing commands.

Return the complete SQL draft for Brain review before execution.