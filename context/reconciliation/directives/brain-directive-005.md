# WORKIN ANTS — BRAIN DIRECTIVE 005
## Full-Platform Contract Stabilization & Production-Ready Development Foundation

### Governance decision

The product owner has established a higher standard for Development Readiness.

**Our objective is the highest practical confidence in successful production development before handing implementation to autonomous Codex agents.**

The architecture must be coherent, contracts must be implementable, dependencies must be explicit, and the context system must give agents an integrated understanding of the platform.

This directive consolidates and supersedes Directives 004, 004-A and 004-B where they concern unfinished work. Preserve all completed work and approved architectural decisions.

### Starting state

Repository: `saybenn/Workin-Ants-V2`

Branch: `codex/development-readiness-2026-09-29`

Last verified published HEAD:

`f4e089902dcbcb303dc52976c4118f8903c135e5`

Verify current HEAD and preserve any verified later commits.

Gates 0–7 have completed their documented architectural scope, with Gate 6 retaining externally gated database posture D.

The platform contains:

- 10 Clusters and 34 Modules.
- 132 permanent canonical Shared Operations.
- 119 contracts previously classified UNSTABLE.
- 13 contracts previously classified EXTERNALLY_GATED.
- 563 reconciled historical bridge records.
- 268 reviewed bridge families.
- 828 typed dependency edges.
- 80 lifecycle/action rows.
- 47 registered source events.

These are checkpoint figures. Recompute before changing their status.

Development readiness remains uncertified.

---

## Objective 1 — Stabilize ALL 132 Shared Operations

Do not limit stabilization to the first implementation phase.

Review every canonical Shared Operation, whether currently Confirmed, Proposed ruling, UNSTABLE, or EXTERNALLY_GATED.

### Required contract specification

Each operation must explain:

**A. Purpose and platform value**

- Why this operation exists.
- What platform problem it solves.
- What capabilities it unlocks.
- What reusable leverage it provides.
- What duplication or architectural fragmentation it prevents.

**B. System context**

- Which end-to-end workflows use it.
- Which source lifecycles it supports.
- What happens immediately before and after it.
- How it interacts with other Shared Operations.
- Why its particular boundary matters.

**C. Ownership and responsibilities**

- Canonical SH ID and name.
- Owning Module or shared-runtime steward.
- Authoritative source truth.
- Producer and consumer responsibilities.
- Data it may read or mutate.
- Explicit non-ownership and prohibited shortcuts.

**D. Implementable interface**

- Operation classification and command/query/event/protocol semantics.
- Versioned input and output contracts.
- Required identifiers, revisions, evidence and correlation.
- Preconditions and postconditions.
- Authorization, entitlement, consent, hold and privacy guards where applicable.
- Expected errors, denial reasons and safe unknown behavior.
- Compatibility and versioning requirements.

Define concrete shapes where needed to remove implementation ambiguity. Do not prematurely commit to arbitrary internal implementation details.

**E. Cross-cutting relationships**

- Upstream dependencies and required facts.
- Downstream consumers and obligations.
- Other Shared Operations used.
- Cross-Cluster contract relationships.
- Relevant database models, events, projections and provider adapters.
- Sequencing constraints and circular-dependency safeguards.

**F. Implementation guidance**

Provide brief but valuable instructions describing how an implementation agent should build or integrate the operation.

Identify reusable infrastructure, important technical patterns, required transactional boundaries, concurrency mechanisms, versioning, security enforcement, provider separation and prohibited duplicate implementations.

The objective is not thousands of lines of speculative code. It is to provide the practical architectural knowledge that prevents Codex from making disconnected implementation decisions.

**G. Reliability and recovery**

Specify applicable:

- Idempotency and duplicate handling.
- Retries and terminal failures.
- Concurrency and stale-state protection.
- Partial completion and compensation.
- Event ordering and replay.
- Revocation and invalidation.
- Audit, telemetry and durable proof.
- Fail-closed behavior for incomplete evidence.

**H. Qualification evidence**

Record:

- Current architectural maturity.
- Remaining ambiguity.
- Required fixtures and contract tests.
- Negative and compatibility tests.
- External requirements.
- Evidence supporting implementation freeze.
- Exact conditions required before activation.

### Stability standard

Resolve all AI-resolvable uncertainties across all 132 operations.

Every operation must receive an explicit final disposition:

- FROZEN_FOR_IMPLEMENTATION
- EVOLVABLE_COMPATIBLY
- EXTERNALLY_GATED
- UNSTABLE, with a specific unresolved blocker and owner

Aim to eliminate AI-resolvable UNSTABLE contracts before development authorization.

Do not falsely declare contracts frozen because documentation was written or a static validator passed.

Maintain two separate dimensions of evidence:

1. **Architectural contract readiness:** The specified interface and rules are coherent enough to implement.
2. **Runtime implementation qualification:** Real code, persistence, security and provider behavior have been tested.

Do not claim the second merely from the first.

Do not silently approve the canonical registry's Proposed ruling entries or alter permanent SH identities.

---

## Objective 2 — Connect the operations into one living platform

Do not produce 132 independent contract descriptions.

Create an interconnected platform workflow reference explaining how the operations cooperate to deliver real Workin Ants capabilities.

Cover major journeys including:

- Registration, identity and actor creation.
- Track enrollment, subscription and entitlements.
- Professional onboarding and readiness.
- Offering creation and publication.
- Gig response, acceptance and Order creation.
- Checkout, payment, settlement, refunds and payouts.
- Booking, cancellation, rescheduling and service delivery.
- Media, video and digital goods access.
- Organization hiring, applications and interviews.
- Messaging, notifications and public discovery.
- Privacy requests, erasure and export.
- Moderation, compliance holds, restoration and audit.
- Rewards, prize entries and fulfillment.

For each workflow, expose the sequence of source-state transitions, participating contracts, owner boundaries, security and compliance checks, downstream events, failure recovery and eventual consistency obligations.

Each contract should link to its applicable workflows. Each workflow should identify its contracts and authoritative owner architectures.

The result must teach an incoming Codex agent **how the platform works as a connected system**, not merely where hundreds of specifications are stored.

Avoid creating a competing source of architecture truth. Use the canonical registry, owner files and traceable companion resources.

---

## Objective 3 — Complete Gate 8: root development plan

Create or finalize:

- `context/build-plan.md`
- `context/parallel-development-plan.md`

Develop the implementation sequence using the root architecture, stabilized contracts, dependency graph and current Module/Cluster plans.

Include a mandatory **Phase 0 — Foundation Qualification**.

Phase 0 must address the technical prerequisites, reusable platform runtime, executable contract fixtures, migration strategy, authorization/RLS parity, concurrency safeguards, privacy execution prerequisites, and integration testing foundations needed to support later development.

Distinguish:

- Architectural dependencies.
- Contract-only dependencies.
- Actual implementation dependencies.
- Externally gated dependencies.

Create clear development phases, milestones, tests and convergence gates.

Derive candidate parallel lanes from proven boundaries, not simply different Modules or folders.

Every lane requires established file ownership, schema-change coordination, shared-contract versions, independent tests and merge checkpoints.

Do not authorize parallel implementation just because the plan contains a lane map.

Reconcile the root build plan again if full-platform contract stabilization changes a material prerequisite.

---

## Objective 4 — Complete ALL essential agent context

Complete Gate 9 by auditing, reconciling or creating the required Codex development context.

Include:

- `context/architecture.md`
- `context/build-plan.md`
- `context/code-standards.md`
- `context/library-docs.md`
- `context/ui-tokens.md`
- `context/ui-rules.md`
- `context/ui-registry.md`
- `context/progress-tracker.md`
- `context/context-map.md`
- `AGENTS.md`
- `CLAUDE.md`
- Shared Operation contract documentation.
- Cross-Cluster workflow/dependency documentation.
- Parallel development and migration coordination instructions.

Inspect before creating or replacing existing files.

**UI context must be completed before substantial UI implementation.**

Derive visual and interaction guidance from established product intent, approved design choices and actual technology conventions. Use coherent, reversible defaults where permitted. Do not invent consequential product behavior.

The development context must provide:

1. Product and platform orientation.
2. Authoritative ownership and context-loading instructions.
3. Architecture and implementation sequencing.
4. Connected Shared Operation contracts.
5. Approved implementation patterns and reusable libraries.
6. Visual/UI conventions and reusable component boundaries.
7. Source-truth and privacy/security protections.
8. Contract tests, quality expectations and completion rules.
9. Agent file ownership and parallel development safeguards.
10. Progress, traceability and integration checkpoints.

Ensure these resources reinforce one another rather than becoming inconsistent instructions.

---

## Objective 5 — Build automated architectural safeguards

Improve or create deterministic checks that verify:

- All 132 contract identities and qualification records.
- Contract-to-owner and contract-to-workflow traceability.
- Producer/consumer compatibility.
- Dependency registration and cycle constraints.
- Missing or duplicated Shared Operations.
- Unapproved source-truth ownership.
- Cross-domain repository shortcuts.
- Local authorization or entitlement duplication.
- Invalid contract status promotions.
- Incompatible parallel-lane ownership.
- Schema/migration coordination conflicts.
- Broken context links or stale architectural references.

Use positive, negative and compatibility fixtures wherever meaningful.

Avoid equating successful static validation with production runtime proof.

Preserve schema/migration posture D pending real database provenance.

---

## Objective 6 — Complete Gate 10 under the stronger standard

After root planning, contract stabilization and context alignment, perform a comprehensive final Development Readiness audit.

The report must answer:

1. Are all 132 operations individually understood, architecturally resolved where possible, and integrated into system workflows?
2. Are their producer/consumer relationships compatible?
3. Are all critical architectural dependencies stable?
4. Are external uncertainties isolated behind explicit activation gates?
5. Is the root architecture coherent with the implementation plan?
6. Does Codex have complete, reliable and noncontradictory operating context?
7. Are shared schema, migration, security and provider responsibilities clear?
8. Are required tests and integration checkpoints specified?
9. Is the first bounded implementation phase actually authorized by available evidence?
10. Can candidate parallel lanes begin without independently redefining shared contracts?

Produce `context/reconciliation/development-readiness-report.md` with the master roadmap's authorized classification.

If readiness cannot be certified, identify precisely what remains and the smallest actions required to resolve it.

Do not lower the certification standard merely to advance the roadmap.

### Operating policy

Continue autonomously through evidence-supported work.

Resolve technical decisions using authority-by-concern and existing approved rulings.

Escalate only genuine consequential product choices or missing external evidence requiring owner action. Batch such requests whenever possible.

Preserve P01–P19, all approved rulings, historical source records and canonical SH IDs.

Do not deploy, merge main, execute destructive migrations or begin broad product feature implementation.

Maintain logical commits and verified recovery bundles. Verify GitHub publication independently.

### Checkpoint requirement

Return a substantive checkpoint after the complete contract stabilization and development-context alignment, or earlier only when a genuine blocker prevents meaningful progress.

Report:

- Number of SH contracts qualified by final disposition.
- Remaining unstable or externally gated contracts and precise reasons.
- Completed workflow relationships and traceability.
- Root build plan and context-file completion.
- Tests and negative regressions.
- First proposed development phase.
- Candidate versus authorized parallel lanes.
- Remaining technical/external risks.
- Full commit HEAD and publication status.
- Recommended final Codex readiness decision.

**Success means an incoming implementation agent can understand what to build, why it exists, how the moving parts cooperate, what must never be violated, and how correctness will be verified.**

Do not mistake completed documentation for a proven runtime system.

Proceed autonomously toward the strongest practical foundation before Codex implementation.