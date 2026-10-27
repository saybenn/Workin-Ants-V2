# WORKIN ANTS — BRAIN DIRECTIVE P0-C-01

## Prepare the Reviewed Database Candidate and Qualification Plan

### Governance decision

Checkpoint 009 is accepted for its **reported, scoped target-identity and empty-application-namespace evidence**.

It does not approve the physical schema, migration baseline, database security, runtime contracts or product development.

P0-B retains its prior recorded acceptance. P0-C remains posture D. No parallel implementation lanes or Step 20 feature development are authorized.

**Objective:** translate the established architecture into a concrete, traceable database candidate and a safe migration/security qualification plan. Do not restart completed architectural reconciliation.

## 1. Verify the current starting point

Repository: `saybenn/Workin-Ants-V2`

Reported Checkpoint 009 commit: `a067dd5`.

Its reported starting commit was Checkpoint 008:

`ee973d01cebf2d69f05ad0efb37366f9b08fb2e3`

Verify the full current commit, branch, ancestry and worktree state. Preserve any verified later work. Do not reset to an earlier checkpoint.

The intended fresh project is:

`lyalfdmfheevpahywuhv` — **Workin Ants MVP**

The preserved older project is:

`sdceenkakajslwpctbgl`

Do not contact or modify the older project under this directive.

Read the current root build plan, greenfield database strategy, Checkpoints 007–009, database observation manifest, provenance requirements, model/security inventory and governing owner contracts.

Carry forward the current P0-B security disposition from its actual evidence. Do not reopen an older dependency issue merely because a historical document still lists it.

**No new project, account creation or pasted credential is needed for this source-review assignment.**

## 2. Execution boundary

This directive authorizes:

- Read-only inspection of repository artifacts and existing observation evidence.
- Preparation of a review-only physical schema candidate.
- Necessary architecture-compatible technical decisions, recorded with rationale and affected owners.
- Offline schema validation, consistency checks and test specifications.
- A concrete migration, security, disposable-replay and adoption plan.

**This directive does not authorize live database changes, DDL generation, migration application, seeds, resets, test-table creation, provider configuration changes or broad runtime implementation.**

Preserve the checkpoint’s sequence: **candidate approval precedes migration generation and execution.**

Do not run tools that might contact, reset or use the fresh project as a shadow database while performing supposedly offline validation. Verify tool behavior and configuration first.

Operate autonomously through the complete candidate package. Return one meaningful review checkpoint—not a request for approval after each model.

## 3. Reconcile the physical schema against approved meaning

Use `schema.prisma` as evidence of the currently declared structure, not proof that every field, relationship or omission satisfies the later approved architecture.

Review all **177 inventoried models**, recomputing the count against the current source. Preserve coverage even if justified changes alter the final count.

For every model or proposed addition, establish:

- Its source owner and purpose.
- Whether it is authoritative truth, immutable evidence, a projection, compatibility data or shared infrastructure.
- Its identifiers, relationships, required constraints and deletion behavior.
- Its concurrency, currentness, idempotency and historical-proof needs.
- Its sensitive fields, intended access paths and privacy-execution responsibility.
- Whether it belongs in the initial foundation candidate, a later ordered migration or explicitly deferred scope.
- The authoritative ruling or contract supporting that disposition.

Every existing model must be accounted for. **Do not preserve a field as authoritative merely because it already exists, and do not remove it without traceable justification.**

Reconcile the **12 compatibility cases** individually. Preserve the distinction between actual physical compatibility fields and architecture-only concepts. Do not manufacture a table solely to make an inventory entry appear implemented.

Check architecture-required storage that may not yet appear in Prisma, including durable source/economic-effect identities, concurrency or generation records, shared-runtime persistence and Privacy execution evidence.

Produce an actual review-only candidate representation using the installed, pinned tooling where appropriate. Keep it clearly separate from an adopted production schema, with an explicit adoption path.

Where Prisma cannot represent a required database object or invariant, specify its exact purpose, owner and enforcement requirement in a companion register. Do not hide the gap in untyped JSON or a vague future-task note.

## 4. Resolve technical implementation choices without reopening product decisions

Apply current rulings before interpreting historical “Unresolved” sections.

Resolve ordinary physical implementation choices that follow from approved architecture. Record the decision before dependent candidate changes.

Distinguish:

**Already settled:** preserve and implement its physical consequences.

**Technical choice within approved boundaries:** choose, justify and document it.

**Genuine conflict or consequential new behavior:** isolate the issue and present a recommended resolution.

**Missing external policy or provider evidence:** keep the affected behavior gated; do not invent the answer.

In particular, examine whether the candidate supports:

- One owner per lifecycle and contextual relationship.
- Required uniqueness and coherent cross-record relationships.
- Durable protection against repeated financial or other business effects.
- Safe stale-write detection and current-generation checks.
- Source changes and required evidence/outbox records being committed together.
- Retention-safe relationships that do not accidentally cascade-delete protected history.
- Projections that cannot become alternate authorization or business truth.

Do not require all future product features to be implemented to finish this review. **Review their storage implications now and explicitly stage their implementation.**

## 5. Define the complete access model

Produce an object-and-access matrix covering application schemas, tables, views, sequences, functions and triggers.

Separate:

- Migration/DDL credentials.
- Application runtime connections.
- Background workers.
- Browser/API roles.
- Privileged support or administrative operations.

Do not confuse a business Module’s ownership with PostgreSQL object ownership. Do not create one database role per Module merely for symmetry.

Follow the approved schema/API strategy. Internal objects should not acquire browser access by accident. Any exposed surface needs an explicit purpose, permitted operations and appropriate protection.

For the intended Prisma connection path, establish how trusted actor context reaches the database and how it is cleared or isolated between pooled requests. Do not assume a direct database connection automatically carries a Supabase user’s identity.

Specify real, least-privileged runtime testing. Administrative catalog queries and privileged service access are not proof that end-user restrictions work.

Include positive access cases as well as denials: **a system that denies everything has not passed functional security qualification.**

### Carry forward Checkpoint 009’s specific findings

Address creator-specific default privileges, including privileges remaining after automatic exposure was disabled. Review the actual creation roles and inheritance paths rather than treating one role’s defaults as universal.

The observed automatic-RLS trigger covers newly created `public` tables only. The candidate must explicitly specify protection for application objects, including any `app` schema objects.

For the two warnings concerning `public.rls_auto_enable()`:

- Preserve the exact function type, ownership, privileges and trigger relationship.
- Distinguish an advisor finding from demonstrated RPC reachability or exploitability.
- Propose the narrowest justified disposition or remediation.
- Specify how legitimate trigger operation and denied unauthorized access will later be verified.
- Do not alter provider-managed objects or broadly revoke permissions merely to clear an advisor.

Review views, security-definer functions, search paths, role inheritance and RLS-bypass paths. Any privileged exception must have a documented purpose, restricted caller and test requirement.

Do not enable Data API exposure merely to make a test easier.

## 6. Design one reproducible migration and security history

Select and justify **one coordinated execution path** for application schema and security changes.

Account explicitly for the installed Prisma and Supabase tooling. Do not leave two independent migration histories capable of changing the same objects without a defined relationship.

The plan must explain:

- How the fresh application namespace is initialized.
- Which historical migrations remain preserved but are not executed against this target.
- How additional SQL-only objects, constraints, grants and policies are versioned.
- Which role creates and owns each category of object.
- How objects remain appropriately restricted during installation.
- How migration failure is detected and recovered.
- How later changes preserve applied migration checksums.
- How the full physical result—not just Prisma’s representation—is compared with the approved candidate.

**Do not replay the June migration by default. Do not mark migrations as applied when their required objects have not actually been established.**

Do not use schema push, reset, unreviewed introspection or regenerated history as a shortcut around a reviewed migration path.

Preserve Supabase-managed Auth, Storage, Realtime, extensions and other managed objects. Document required interactions without absorbing their ownership.

## 7. Prepare the executable qualification plan

Specify the next approved test environment and actions without performing them under this directive.

Prefer a clearly identified disposable environment containing only synthetic test data. Document relevant differences from the actual Supabase environment; local success alone must not be presented as hosted-provider parity.

The proposed tests must cover:

**Reproducible installation:** build from empty application state using only the reviewed history; prove repeat deployment behaves correctly and failures cannot be mistaken for success.

**Full structural comparison:** tables, columns, types, enums, relationships, constraints, indexes, owners, grants, policies, views, functions and triggers, with explicit treatment of managed objects and any comparison exclusions.

**Actual access behavior:** allowed and denied operations for the selected roles; cross-user and cross-organization attempts; forbidden ownership reassignment; privileged-call boundaries; direct/API access where applicable.

**Database-enforced invariants:** duplicate identities or effects, conflicting writes, retained-history protection and the other constraints required by the candidate.

**Recovery and preservation:** failure/forward-repair procedure, backup/restore coverage, target safeguards and the authorization required for destructive actions in a disposable environment.

Map each test to a requirement and expected outcome. Mark unexecuted tests as **NOT RUN**.

Separate P0-C database tests from the later P0-D worker/command tests and P0-E owner-adapter tests. Avoid creating a circular requirement that the entire runtime must already exist before its database can be qualified.

Do not claim runtime proof from static mutations or mocked database behavior.

## 8. Prepare the first P0-D implementation slice

Recommend—but do not implement under this directive—the smallest coherent shared-runtime slice supported by the candidate.

Its shape should be:

> Authorized owner command → durable idempotency handling → owner state and required evidence/outbox commit → worker processing → consumer deduplication → retry and recovery proof.

Choose the exact owner, contracts and files from the current build plan and architecture. Use synthetic fixtures without inventing a fake production business domain.

Specify tests for repeated identical requests, conflicting reuse of a request key, competing updates, transaction rollback, worker crash/reclaim, stale worker execution and downstream failure.

The acceptance goal is **no repeated committed business effect despite retries**, not an unsupported promise of exactly-once network delivery.

Identify the minimum security and Privacy prerequisites for that slice. Those protections must be present when needed, even though broader qualification continues in P0-E and P0-F.

## 9. Preserve launch scope and external gates

Carry forward the approved U.S., 18+ launch scope and the recorded exclusions.

Therapy, prescribing, child-directed features and prize competitions remain unavailable at launch. Their long-term architecture is preserved; schema presence is not activation permission.

Legal drafts are test material, not approved retention rules or production consent. Vendor capability evidence remains necessary when the relevant integration becomes a dependency.

Do not let missing future legal/provider evidence stop unrelated source reconciliation. Equally, do not encode an invented legal rule merely to complete the candidate.

UI design remains in its separate thread. No production screens or forms are part of this assignment.

## 10. Required outputs and acceptance

Extend existing authoritative artifacts rather than creating competing registers.

Return:

**A reconciled candidate package:** validated review-only schema, model disposition ledger, compatibility-case review and SQL-only object/invariant specifications.

**A security package:** object/role/access matrix, creator-default review, advisor dispositions and proposed positive/negative test coverage.

**A migration/replay package:** coordinated history strategy, disposable-target requirements, complete comparison method, recovery plan and exact action boundaries.

**A continuation package:** remaining DBP-01–12 evidence, the proposed first P0-D slice and a clear explanation of what would authorize the next step.

Candidate review is complete only when every inventoried model and compatibility case has a disposition, required storage is represented or explicitly gated, and no AI-resolvable physical-design contradiction remains silently open.

Run applicable offline validators, candidate schema checks, regression/mutation checks and diff hygiene. Report exact commands, results and limitations.

Maintain posture D until the actual adoption criteria are met. Do not freeze contracts or close runtime gates because the candidate passes static checks.

## 11. Git preservation and checkpoint

Verify Checkpoint 009’s complete commit identity and recoverability. Preserve logical commits on the current dedicated branch and report the actual remote state separately.

Use normal authenticated publication when available and safe; otherwise provide a verified full-history bundle, checksum, full HEAD/tree and restoration instructions. No force-push, `main` merge or substituted history.

The next checkpoint must answer:

1. What needed changing between the declared schema and the approved architecture?
2. Is the candidate ready for Brain review?
3. Which security findings have a justified proposed disposition?
4. What exact migration-generation and disposable-test actions are requested next?
5. What remains externally gated, and does it block the immediate foundation slice?
6. What was actually validated, and what was not run?

**Proceed autonomously through this bounded candidate review. Return before generating or applying database changes.**