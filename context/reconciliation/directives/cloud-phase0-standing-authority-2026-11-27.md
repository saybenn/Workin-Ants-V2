You are the integration lead and implementation owner for the **Workin Ants Pro Development Project**.

**Repository:** `saybenn/Workin-Ants-V2`

## 1. Objective and working approach

Move development into a usable cloud execution environment and carry the project through **Phase 0 foundation qualification**, progressing from the current database work through the shared runtime, permissions, privacy, and integrated readiness checks.

Our larger goal is to reach the Workin Ants MVP. This assignment establishes the qualified foundation needed to begin the product-development milestones.

This is an implementation assignment. Inspect the current work, establish the cloud execution route, make the necessary changes, run actual tests, obtain independent reviews, publish checkpoints, and continue through the authorized scope.

A passing component test, a completed review, or a published checkpoint is a reason to continue to the next required task. Finish the assignment unless a consequential decision or an unavailable capability genuinely prevents further useful progress.

Use plain English in updates. Define technical terms when introducing them.

## 2. New owner authority for this assignment

This directive authorizes **sequential, synthetic-data, nonproduction cloud work through P0-C, P0-D, P0-E, P0-F, and P0-G**, subject to the actual prerequisites of each stage.

Within this scope, you may:

- Establish an isolated cloud development workspace and its reproducible setup.
- Port the existing qualification tooling to the actual cloud environment.
- Create, exercise, restore, and remove verified test-owned disposable PostgreSQL resources.
- Apply reviewed candidate migrations to those disposable databases as part of qualification.
- Implement the approved Phase 0 runtime, security, privacy, and integration capabilities.
- Investigate failures, correct defects, obtain independent review, and rerun affected checks.
- Record technical stage acceptance after independent review and sufficient actual evidence.
- Proceed into the next authorized Phase 0 stage when its prerequisites are satisfied.
- Create an isolated development branch, commit logical checkpoints, publish normally, and prepare draft pull requests.

**This replaces the earlier Windows-only execution restriction and mandatory return to Brain between these Phase 0 stages.** It also extends the earlier local P0-C standing authority to this bounded cloud Phase 0 assignment.

Record this as a new owner directive and reconcile the current instruction pointers. Preserve historical directives and their original meaning.

The change concerns execution environment and routine technical progression. Preserve the approved architecture, ownership rules, security requirements, migration history, evidence standards, and applicable external requirements.

Consequential product decisions, changes to approved security policy, new spending, production adoption, public release, and Step 20 product-feature activation remain outside this assignment. Platform and tool permissions continue to apply.

Use available included cloud capacity first. New paid services, unidentified existing database targets, or consequential account changes require a concrete decision identifying the target, purpose, cost, and smallest necessary access. Complete independent authorized work before raising that decision.

## 3. Project orientation and verified starting point

Workin Ants is a marketplace and work platform with distinct Identity, Customer, Professional, Candidate, Organization, Track, transaction, and supporting system owners.

The project already has:

- A reconciled architecture covering 10 Clusters and 34 Modules.
- Specifications for 132 Shared Operations.
- Root architecture and implementation plans.
- A context and execution harness.
- A clean application foundation with recorded P0-B toolchain and security qualification.

Preserve this work. Continue the approved architecture and clean application foundation.

The original roadmap’s Steps 1–17 established the architecture and plans. Step 19 prepared the execution context. Step 18’s actual foundation qualification is still underway. Step 20 is the subsequent product-feature development stage.

### Starting repository anchor

Last verified branch:

`codex/p0c-candidate-corrections-2026-10-31`

Last verified published commit:

`532445ed1f861211978dd8b2e9ae12d4b5e6e180`

This is an orientation anchor. Inspect current references, ancestry, working trees, open pull requests, and newer evidence. Continue from the appropriate compatible descendant.

Preserve the original Windows checkout and any unpublished work. Do not assume `main` contains the completed foundation work.

### Latest recorded qualification position

Current stage:

**P0-C — Database Foundation**

Current local qualification checkpoint:

**3.8 — Native integrity/concurrency checks**

Recorded assertion results:

- 695 PASS
- 35 PARTIAL
- 265 NOT_RUN
- 32 DEPENDENCY_BLOCKED
- 7 UNRESOLVED_SOURCE

Recorded results across the 94 selected cases:

- 9 PASS
- 79 PARTIAL
- 6 NOT_RUN

These are historical, version-specific results to verify and preserve. They are not an MVP completion percentage or proof of the new cloud environment.

The earlier positive Customer COMMIT failure has been superseded by a later bounded passing Customer transaction. Resume from the latest checkpoint rather than restarting that earlier investigation.

The newest Customer stale-predecessor and two-history migration procedures have passed independent source and simulated checks. Their newest actual database runs remain unperformed in the recorded checkpoint.

## 4. Establish the current source of truth

First inspect Git state, repository instructions, current directives, and the latest evidence. Follow the repository’s required startup order:

1. `context/project-overview.md`, including its V3 routing.
2. `context/architecture.md`
3. `context/build-plan.md`
4. `context/code-standards.md`
5. `context/library-docs.md`
6. `context/ui-tokens.md`
7. `context/ui-rules.md`
8. `context/ui-registry.md`
9. The current section of `context/progress-tracker.md`

Read `AGENTS.md` and applicable nested instructions.

Then read:

- `context/phase0-roadmap.md`
- `context/reconciliation/launch-scope-baseline.md`
- `context/reconciliation/operating-policy.md`
- `context/reconciliation/directives/brain-directive-007-resumption.md`
- `context/reconciliation/directives/local-f0-standing-authority-2026-11-17.md`
- `context/reconciliation/phase0-foundation-report.md`
- Current Phase 0 status and readiness records.
- `context/reconciliation/local-f0-qualification-board.json`
- `context/reconciliation/local-f0-CSP-C-two-history-reviewed-source-progress-20261124.json`, or its verified successor.

Use the current progress records for the next action. Some older summary documents still describe already-completed rehearsals or earlier restrictions.

Use `context/context-map.md` to load the relevant owning and consuming Module/Cluster plans, connected workflows, and exact Shared Operation variants as each implementation slice requires them. Avoid recursively reading the entire historical archive.

Create a concise Phase 0 execution checklist mapping each required exit condition to:

- Existing evidence and its limits.
- Remaining implementation.
- Required real tests.
- Dependencies.
- The technical acceptance decision needed.

Keep this checklist finite. Add work when an actual requirement, changed dependency, or demonstrated defect justifies it.

## 5. Establish a working cloud execution route

The first cloud milestone is a working development and qualification environment.

Verify that the selected environment can actually:

- Check out the correct private repository and publish normal checkpoints.
- Install the pinned dependencies.
- Run the application and real PostgreSQL.
- Open independent database connections for simultaneous-operation tests.
- Run background processes and controlled crash/restart experiments.
- Protect credentials and temporary files.
- Perform the required migration and recovery tests.
- Retain reproducible source and evidence after the session ends.

Inspect the capabilities actually available through the connected tools and accounts. Choose the smallest suitable environment using existing included capacity.

Prefer disposable PostgreSQL inside the cloud execution environment where supported. A dedicated managed development target is acceptable only when its identity, isolation, capabilities, authority, and cost are established. Preserve Supabase/Postgres as the architectural source of truth.

Applying a reviewed candidate migration history to a verified disposable target is authorized for testing. Adopting a database as the continuing nonproduction development baseline requires the relevant qualification and recorded acceptance.

Keep existing hosted projects and retained data outside the experiment. Use synthetic records and explicitly owned resources.

If an essential capability is unavailable, identify the smallest workable alternative. Continue independent preparation and implementation. Report the exact missing capability and the concrete action needed to obtain it.

### Port the tooling deliberately

The current tooling contains Windows-specific assumptions, including Docker endpoint checks and Windows secret paths. Inspect the existing runner, guards, manifests, and their source generators.

One known example is:

`scripts/sql-review/local-f0-runtime-lease-history-v1-guard.mjs`

Create a separately versioned cloud execution profile with independently reviewed runner, guard, manifest, and environment checks.

Preserve the security properties the Windows checks were enforcing:

- Verified target identity and ownership.
- Demonstrable network isolation.
- Actual restricted database roles.
- Protected credentials.
- Exact source and fixture bindings.
- Controlled process termination.
- Verifiable cleanup.

Use the cloud environment’s observed identities. Do not spoof Windows values, remove protective checks merely to make execution proceed, or copy Windows runtime passes into new cloud execution records.

Preserve the old Windows runner and evidence as historical versions.

The historical 372-file and 435-file preparation views identify the old packets. A changed cloud packet must have its own complete inventory and hashes.

### Preserve the approved toolchain

Read the actual repository pins and installed version-specific framework guidance. Use the existing package locks and approved runtime/database versions where compatible.

A necessary platform-specific binary or execution change requires its own identity and affected requalification. An environment move does not justify an opportunistic framework or database upgrade.

Recheck the environment-sensitive P0-B requirements in the cloud: clean dependency installation, lint, type checking, build, development/production route behavior, and production exclusion of debug routes.

Capture the outcome once and rerun affected checks when relevant source or environment changes.

## 6. Complete P0-C — Database Foundation

Resume the existing qualification board and selected-case register.

Inspect the two immediate source validations:

- `context/reconciliation/local-f0-customer-stale-predecessor-owned-v1-source-validation.json`
- `context/reconciliation/local-f0-runtime-lease-two-history-owned-v1-source-validation.json`

Follow their references to the actual operator sources, independent reviews, expected outcomes, and manifests.

Also load the relevant database-readiness, provenance, candidate migration, selected-test, SQL manifest, access-policy, and verifier records under `context/reconciliation/`.

### Immediate execution sequence

1. Prepare the reviewed cloud versions of the pending procedures.
2. Bind them to exact committed source or a complete recorded content snapshot.
3. Obtain independent operational review of the actual execution plans.
4. Verify the live target, runtime, image or installation, roles, resources, secrets, and cleanup plan.
5. Run the Customer stale-predecessor and two-history procedures sequentially.
6. Preserve their actual outcomes and verify cleanup.
7. Admit only the specific evidence each procedure establishes.
8. Continue corrected application and affected-worker qualification and the remaining attainable assertions.

The Customer predecessor test has a narrow stale-update scope. The two-history procedure proves migration-history machinery. Neither alone qualifies the complete application path or all of P0-C.

### Required database evidence

Complete the applicable existing requirements for:

- Safe disposable setup and correct/incorrect authentication.
- Successful and deliberately failed installation.
- Final removal of temporary installation privileges.
- Complete intended transactions and intended denied transactions.
- Genuine migration-ledger and checksum behavior.
- Repeated deployment with no unintended changes.
- Controlled migration failure and recovery.
- Full expected structure, constraints, indexes, functions, triggers, ownership, grants, default privileges, and row-level security.
- Actual permitted and denied operations under the intended restricted roles.
- Required invariants, simultaneous-operation behavior, and recovery.
- Applicable synthetic backup and restore.

Repair authoritative generators and regenerate their outputs together.

Preserve historical migration bytes and checksums. Use reviewed append-only corrections where an applied history requires them. Keep unsafe legacy database-write aliases blocked; use the verified target-specific execution route.

### Prevent a circular dependency

Account for all 94 selected cases at assertion level.

Some positive paths depend on P0-D, P0-E, or P0-F. Do not demand that those future dependencies already exist before beginning their properly sequenced implementation.

For each proposed transition:

- Identify the database prerequisites the next bounded stage actually requires.
- Prove those prerequisites independently.
- Record acceptance only for that supported scope.
- Retain PARTIAL and dependency-blocked statuses.
- Assign deferred obligations to their owning stages.
- Revisit those obligations when their real dependencies exist.

A failed mandatory prerequisite cannot be waived. A passing denial cannot substitute for an unavailable positive path. Keep the 451-case register distinct from this selected foundation scope.

## 7. Complete P0-D — Shared runtime

The shared runtime is the common machinery for processing commands, recording events, running background jobs, retrying failures, and recovering safely.

Implement the approved persistent command, inbox/outbox, job, lease, reservation, concurrency-control, and proof mechanisms behind their canonical owner interfaces.

Use the contract catalog and actual owner/consumer plans. Preserve one coordinated migration history and one integration owner for the shared implementation.

Required behavior includes:

- The source change, required history, and required outgoing-message/proof intent commit together.
- External dispatch happens after the database commit.
- Database transactions do not remain open across external network calls.
- Repeating the same intended operation returns the established result without duplicating its effect.
- Reusing an operation identity with different meaning produces the required conflict.
- A timeout or interrupted connection does not imply that an external effect never happened.
- Recovery reconciles uncertain outcomes under their original effect identities.
- Retries are bounded; exhausted work remains visible and recoverable.
- Crashed or stale workers cannot complete work they no longer own.

Prove actual PostgreSQL behavior for success, failure, identical/conflicting replay, crash/reclaim, stale-worker rejection, competing reservations, relevant period/session/inventory races, and uncertain outcomes.

Verify startup and health reporting without creating a dependency cycle in which monitoring prevents the machinery supporting that monitoring from starting.

Reference models support reasoning; qualify the actual persistent implementation.

## 8. Complete P0-E — Permissions and real adapters

An adapter is the implementation connecting an owner’s actual behavior to the shared contract other components use.

Implement the minimum real owner and consumer interfaces required for the next bounded development scope. Follow the dependency map rather than requiring every surrounding Module to be completed first.

Required behavior includes:

- Trusted actor context is established by the server.
- Authority matches the exact owner, action, relationship, purpose, fields, assurance, and current state.
- Unsupported actions and unknown or stale required facts receive the specified refusal.
- Membership removal and permission revocation take effect as required.
- Private objects cannot be discovered through unauthorized lookups or error differences.
- Application permission checks and database row-level security agree.
- Required proof is durable before protected information is released.

Test permitted, denied, unknown, stale, revoked, and unavailable cases through actual adapters and restricted database connections.

Keep privileged setup and observation separate from business-operation proof. A broad service or administrator role cannot stand in for the restricted role being qualified.

Name the exact endpoints, operations, variants, and contract versions supported by the evidence.

## 9. Complete P0-F — Privacy and protected delivery

Inventory the actual implemented data owners, fields, actions, exports, provider transfers, media paths, and backup/restore behavior.

Implement privacy execution inside the owning Module. The central Privacy component coordinates work and records outcomes without becoming a second owner of other Modules’ data.

Required behavior includes:

- Privacy instructions and receipts are bound to the current version or generation of the relevant state.
- Old work cannot restore, disclose, or overwrite data contrary to a newer restriction.
- An accepted request is distinguished from a completed action.
- An uncertain external deletion is distinguished from verified deletion.
- Export manifests and checksums match the actual generated bytes and protected artifact.
- Media safety checks deny access when required safety evidence is unavailable.
- Restored backups receive current erasure/restriction handling before affected data is served.

Test the implemented scope’s success, stale instructions, failures, recovery, export-byte identity, protected delivery, and applicable provider outcomes.

Keep unsupported actions, unimplemented owners, unapproved retention rules, and unavailable provider capabilities explicit.

Use the approved launch baseline for synthetic development placeholders. Do not turn draft legal language, proposed retention periods, or a provider’s brand name into evidence of legal approval or actual capability.

A missing external requirement blocks the affected operation or activation. Continue other independent foundation work.

## 10. Complete P0-G — Integrated qualification and readiness decision

Combine the real components and exercise the producer/consumer paths required for the first bounded product-development milestone.

The first product milestone concerns a real registered actor and profile performing permitted source actions with current consent and authority.

P0-G must establish the actual foundation and interfaces that milestone needs. It does not require completing every future feature in all 34 Modules or automatically qualifying all 132 Shared Operations.

Required work:

- Exercise the real application, persistent runtime, database permissions, owner adapters, and applicable external test capabilities together.
- Test success, denial, staleness, revocation, replay, competing actions, failure, and recovery.
- Verify compatibility with retained consumer expectations.
- Revisit relevant P0-C assertions whose later dependencies now exist.
- Pin only the contract versions and variants that actually passed qualification.
- Reconcile changed owner architecture, contracts, consumer expectations, Cluster coordination, plans, implementation, and evidence.
- Obtain independent review of the final readiness decision.

Distinguish cloud PostgreSQL evidence from evidence about hosted authentication, managed storage, external providers, or production behavior.

State exactly which next development slice can begin, the prerequisites it satisfies, and which operations remain disabled or blocked.

Keep the approved launch restrictions: adults 18 and older, the approved U.S. scope, and the existing distinction between ordinary rewards and deferred prize competitions. Preserve the deferral of therapy, prescribing, and child-directed capabilities.

Finish this assignment at the Phase 0 boundary with a concrete Step 20/M1 handoff. Product lanes activate through their subsequent authorization.

## 11. Execution, review, evidence, and continuity

Maintain one integration owner for shared contracts, schema/migrations, shared runtime, root context, and convergence.

Use additional agents or independent review facilities for investigation, review, and genuinely separate work. Preserve the dependency sequence and avoid competing canonical changes.

For a substantive defect:

1. Preserve the failed attempt and its source/environment identity.
2. Establish a testable explanation.
3. Make the smallest coherent correction.
4. Update affected generated artifacts and identities.
5. Obtain review from someone or an independent review facility that did not author the change.
6. Resolve substantive findings.
7. Run focused checks and required regressions.
8. Execute the reviewed replacement experiment.
9. Record the actual result, confirm resource state, and continue.

A failed experiment stops that experiment and dependent cases. It does not end the assignment. Diagnose and correct before retrying.

If independent review is unavailable, continue safe preparation and report that exact limitation. Do not label self-review as independent.

Preserve expected business and security behavior when repairing tests. Maintain independently established expected results rather than regenerating expectations to match defective code.

### Keep the work finite

Every added test should address:

- An open acceptance requirement.
- A changed source or environment dependency.
- A demonstrated defect.

Run meaningful regressions. Preserve unaffected historical evidence without rerunning it after every small edit. Stop optional verification once the relevant criteria are satisfied and move to the next required task.

### Evidence and publication

Record exact source, environment, packet, fixture, role, reviewer, result, and resource identities.

Keep passing, failed, partial, dependency-blocked, unresolved, and not-run results distinct. Preserve raw historical outcomes and explain later interpretations separately.

Protect secrets in files, logs, errors, and repository history. Keep useful sanitized diagnostics sufficient to identify failure origins.

Verify exact ownership before deleting resources. Use controlled cleanup for test resources and an explicit retention record for the continuing development environment.

Run applicable repository context and foundation checks after relevant changes. These structural checks supplement actual implementation tests.

Publish logical checkpoints on the appropriate isolated cloud branch. Verify remote publication and preserve the existing deployment-suppression boundaries. Prepare a draft PR against the correct prerequisite branch when useful.

Persist enough information in the repository that a fresh cloud session can continue without the Windows checkout or private machine-specific wrapper paths.

### Progress updates and escalation

Each meaningful update should state:

- What now works.
- Which phase and checkpoint are current.
- What remains unproved.
- The next action.
- Any actual decision or access requirement.

Ask for input only when it changes a consequential decision, supplies genuinely unavailable access, resolves a substantive authority conflict, or approves necessary spending.

Before escalating, complete the independent work and prepare the concrete decision, evidence, attempted remedies, and recommendation.

## 12. Required completion package

Deliver:

1. **A reproducible cloud development setup** with exact environment assumptions and usable setup/run instructions.
2. **Published implementation checkpoints** and the appropriate review branch or draft PR.
3. **Updated Phase 0 records** showing the actual status of P0-C through P0-G and the limits of each acceptance.
4. **The qualification evidence**, including applicable migrations, permissions, runtime behavior, privacy, integration, recovery, and cleanup.
5. **A precise unresolved-requirements list**, identifying owners, dependencies, and the exact scope each limitation blocks.
6. **A first-M1 handoff** naming the next implementation slice, required files and contracts, acceptance criteria, and remaining external decisions.
7. **A plain-English report** explaining what was completed, what can start next, and anything that still prevents that next scope.

Claim Phase 0 readiness only for the scope the evidence supports. If an indispensable prerequisite remains unavailable, complete everything else and state that blocker precisely.

Begin by verifying the current repository state, recording this owner directive, establishing the real cloud execution route, and continuing the earliest unfinished prerequisite. Carry the work through the authorized Phase 0 sequence without waiting for another routine assignment.