# Workin Ants Context Map

This is the authoritative routing document for **which artifact owns which concern**. It records the Step 1 baseline and how agents must handle disagreement. It does not adjudicate architecture, replace registries, summarize Modules, or authorize implementation. All paths below are repository-relative when written as code; links resolve from this file. Filenames and directory spellings are preserved.

> Architecture defines what the system is allowed to be.
> Plans define the order in which that architecture is implemented.
> Progress records what has actually been completed.
> A plan or progress update may never silently redefine architecture.

# Artifact Baseline

- **Baseline date:** 2026-09-08, America/New_York.
- **Branch:** `master`.
- **Starting HEAD:** `c966c44b7676353e619a273d800d559d40a5e5e8`.
- **Starting working tree:** **DIRTY**. Existing changes were present before this task; none are adopted, reverted, or discarded by this map.
- **Freeze meaning:** identify the starting evidence, without immutability, backups, branch creation, staging, or commits. Git is the historical record.
- **Historical limitation:** `context/`, `docs/`, and `prisma/` are untracked at baseline. HEAD does **not** contain this artifact set. This map records the working-tree inventory; it cannot make uncommitted contents recoverable from HEAD. Preserve these files and include their baseline in a separately authorized Git checkpoint before later edits need historical comparison. No checkpoint was created in Step 1.
- **Content fingerprint:** 102 existing files; SHA-256 `34c3ba43fd15e8774e277a63ee27bdb7744271e2477ade8270e3bff033f53722`. Scope: every file under `context/`, `prisma/`, `docs/`, plus `AGENTS.md`, `CLAUDE.md`, `README.md`, and `prisma.config.ts`; excludes this new map. Sort repository-relative forward-slash paths ordinally; concatenate each path, a tab, lowercase SHA-256 of its raw bytes, and LF; hash the resulting UTF-8 text. This detects change; it is not a content backup.

Starting short Git status:

```text
 M AGENTS.md
 M README.md
 D app/favicon.ico
 D app/globals.css
 D app/layout.tsx
 D app/page.tsx
 M package-lock.json
 M package.json
 M tsconfig.json
?? components/
?? context/
?? docs/
?? features/
?? integrations/
?? lib/
?? pages/
?? prisma.config.ts
?? prisma/
?? scripts/
?? server/
?? types/
```

## Counts and missing artifacts

Counts are by document role and directory depth, corroborated by headers and registry IDs, **not exact generic basenames**.

| Artifact | Expected | Found | Baseline result |
| --- | --- | --- | --- |
| Cluster architecture | 10 | 10 | Complete inventory |
| Cluster build plan | 10 | 10 | Complete inventory |
| Module architecture | 34 | 33 | Missing `organization_hiring` |
| Module implementation plan | 34 | 33 | Missing `organization_hiring` |
| Canonical Shared Operations registry | 1 | 1 | 126 unique entry headings, SH-001 through SH-126, no gaps |

Both registries declare 34 Modules. CL-06 declares four, but only three Module directories exist. No `organization_hiring` Module directory or document pair was found elsewhere in the repository. Missing authority must remain missing; the Cluster document is supporting evidence, not a substitute Module contract.

Neither repository-root `architecture.md` / `build-plan.md` nor `context/architecture.md` / `context/build-plan.md` exists. The unversioned `context/project-overview.md` and dedicated `context/progress-tracker.md` are also absent. Overview references to `context/code-standards.md`, `context/library-docs.md`, `context/ui-tokens.md`, `context/ui-rules.md`, and `context/ui-registry.md` have no discovered files. These are gaps, not instructions to create them here.

## Root, shared, registry, glossary, compliance, and executable evidence

| Role | Actual location and baseline interpretation |
| --- | --- |
| Product overview | [project-overview-v3.md](project-overview-v3.md) and [project-overview-v2.md](project-overview-v2.md). V3 explicitly calls itself the context front door and names registry v2.3; use it as the entry point and retain V2 as foundational evidence. No explicit supersession adjudication was established; version numbers do not resolve substantive disagreements. |
| Root instructions/context | [AGENTS.md](../AGENTS.md), [CLAUDE.md](../CLAUDE.md), [README.md](../README.md). CLAUDE delegates to AGENTS; no nested AGENTS files found. README describes Phase 1 setup. |
| Shared registry | [context/shared/shared-operations.md](shared/shared-operations.md), the only file under `context/shared/`. Canonical by permanent SH ID. |
| Shared source synthesis | [Workin_Ants_Canonical_Shared_Operations_Architecture.docx](Workin_Ants_Canonical_Shared_Operations_Architecture.docx). Source synthesis of 34/34 extracts and 126 operations; supporting rationale, not a second ID registry. |
| Deep Module Registry | [prisma/deep modules and schemas.json](<../prisma/deep modules and schemas.json>), 34 entries; string IDs such as `identity_access`. Its location under Prisma does not turn proposed schemas into executable structure. |
| Cluster Registry | [prisma/clusters.json](../prisma/clusters.json), `v2.3-customer-subscription`; CL-01 through CL-10 with 34 declared memberships. |
| Glossary and compliance | [Ubiquitous Language Pack](<workin_ants_ubiquitous_language_pack_v2_2_full_compliance_schema_module (1).docx>). Includes “6. Canonical Glossary,” “7. Compliance Inventory / Legal Homework Map,” the “V2.2 Comprehensive Compliance, Module, Model, and Enum Refresh,” and “Appendix B - Complete Compliance Definitions Glossary.” No separate compliance inventory file found. Read relevant base entries and addenda; unresolved legal homework is not approved policy. |
| Executable schema | [prisma/schema.prisma](../prisma/schema.prisma), 177 models and 207 enums; [prisma.config.ts](../prisma.config.ts) provides configuration. Repository presence does not prove deployed state or approval history. |
| Migrations | [migration.sql](../prisma/migrations/20260602021702_phase_2_database_truth_layer/migration.sql) is the sole discovered SQL migration; [migration_lock.toml](../prisma/migrations/migration_lock.toml). It creates 53 tables and 31 enums. Schema/migration coverage alignment requires later review. |
| Progress evidence | [docs/phase-2-database-truth-layer.md](../docs/phase-2-database-truth-layer.md) records Phase 2 segment status and prior verification results. It is limited historical completion evidence, not a platform feature tracker or a fresh database check. |
| Implementation evidence | `pages/`, `components/`, `features/`, `integrations/`, `lib/`, `server/`, `types/`, [prisma/seed.ts](../prisma/seed.ts), [scripts/check-db-integrity.ts](../scripts/check-db-integrity.ts), migrations, and available tests. Directory existence and registry `buildStatus` values do not prove feature completion. |

## Cluster and Module path index

Cluster directories are directly under `context/clusters/`; Module directories are directly inside their Cluster. There is no discovered `context/modules/` hierarchy. Generic `architecture.md`, `module-architecture.md`, and plan names elsewhere in this map designate roles: resolve them through these exact links.

| Cluster | Actual directory under context/clusters | Architecture | Build plan | Module pairs |
| --- | --- | --- | --- | --- |
| CL-01 | [identity, authority, & consent](<clusters/identity, authority, & consent/>) | [architecture](<clusters/identity, authority, & consent/identity-authority-consent-architecture.md>) | [build plan](<clusters/identity, authority, & consent/identity-authority-consent-build-plan.md>) | 5 |
| CL-02 | [discovery classification & taxonomy](<clusters/discovery classification & taxonomy/>) | [architecture](<clusters/discovery classification & taxonomy/discovery-classification-architecture.md>) | [build plan](<clusters/discovery classification & taxonomy/discovery-classification-build-plan.md>) | 3 |
| CL-03 | [professional supply & readiness](<clusters/professional supply & readiness/>) | [architecture](<clusters/professional supply & readiness/professional-supply-readiness-architecture.md>) | [build plan](<clusters/professional supply & readiness/professional-supply-readiness-build-plan.md>) | 5 |
| CL-04 | [customer demand, order, & resolution](<clusters/customer demand, order, & resolution/>) | [architecture](<clusters/customer demand, order, & resolution/customer-demand-order-resolution-architecture.md>) | [build plan](<clusters/customer demand, order, & resolution/customer-demand-order-resolution-build-plan.md>) | 3 |
| CL-05 | [scheduling, media, & digital delivery](<clusters/scheduling, media, & digital delivery/>) | [architecture](<clusters/scheduling, media, & digital delivery/scheduling-media-digital-delivery-cluster-architecture.md>) | [build plan](<clusters/scheduling, media, & digital delivery/scheduling-media-digital-delivery-cluster-build-plan.md>) | 4 |
| CL-06 | [Organization Hiring & Candidate Pipeline](<clusters/Organization Hiring & Candidate Pipeline/>) | [architecture](<clusters/Organization Hiring & Candidate Pipeline/organization-hiring-candidate-piepline-architecture.md>) | [build plan](<clusters/Organization Hiring & Candidate Pipeline/organization-hiring-candidate-pipeline-build-plan.md>) | 3 |
| CL-07 | [Messaging Notification Rail](<clusters/Messaging Notification Rail/>) | [architecture](<clusters/Messaging Notification Rail/messaging-notification-rail-architecture.md>) | [build plan](<clusters/Messaging Notification Rail/messaging-notification-rail-build-plan.md>) | 2 |
| CL-08 | [Privacy & Location Safety](<clusters/Privacy & Location Safety/>) | [architecture](<clusters/Privacy & Location Safety/privacy-location-safety-architecture.md>) | [build plan](<clusters/Privacy & Location Safety/privacy-location-safety-build-plan.md>) | 2 |
| CL-09 | [Moderation holds Audits and Ops](<clusters/Moderation holds Audits and Ops/>) | [architecture](<clusters/Moderation holds Audits and Ops/moderation-holds-audit-ops-architecture.md>) | [build plan](<clusters/Moderation holds Audits and Ops/moderation-holds-audit-ops-build-plan.md>) | 4 |
| CL-10 | [incentives, rewards & prize economy](<clusters/incentives, rewards & prize economy/>) | [architecture](<clusters/incentives, rewards & prize economy/incentives-rewards-prize-economy-cluster-architecture.md>) | [build plan](<clusters/incentives, rewards & prize economy/incentives-rewards-prize-economy-cluster-build-plan.md>) | 2 |

The following lists directories and artifact pairs only; identity and membership remain owned by the registries.

| Module ID | Cluster | Actual Module directory within Cluster | Actual artifacts |
| --- | --- | --- | --- |
| `consent_disclosure` | CL-01 | [Consent & Disclosure Module](<clusters/identity, authority, & consent/Consent & Disclosure Module/>) | [architecture](<clusters/identity, authority, & consent/Consent & Disclosure Module/consent-disclosure-module-architecture.md>) / [plan](<clusters/identity, authority, & consent/Consent & Disclosure Module/consent-disclosure-implementation-plan.md>) |
| `customer_buyer_profile` | CL-01 | [Customer Buyer Profile Module](<clusters/identity, authority, & consent/Customer Buyer Profile Module/>) | [architecture](<clusters/identity, authority, & consent/Customer Buyer Profile Module/customer-buyer-profile-module-architecture.md>) / [plan](<clusters/identity, authority, & consent/Customer Buyer Profile Module/customer-buyer-profile-implementation-plan.md>) |
| `identity_access` | CL-01 | [Identity & Access module](<clusters/identity, authority, & consent/Identity & Access module/>) | [architecture](<clusters/identity, authority, & consent/Identity & Access module/identity-access-module-architecture.md>) / [plan](<clusters/identity, authority, & consent/Identity & Access module/identity-access-module-implementation-plan.md>) |
| `role_authority` | CL-01 | [Role & Authority Module](<clusters/identity, authority, & consent/Role & Authority Module/>) | [architecture](<clusters/identity, authority, & consent/Role & Authority Module/role-authority-module-architecture.md>) / [plan](<clusters/identity, authority, & consent/Role & Authority Module/role-authority-implementation-plan.md>) |
| `track_subscription_entitlement` | CL-01 | [Track Subscription & Entitlement Module](<clusters/identity, authority, & consent/Track Subscription & Entitlement Module/>) | [architecture](<clusters/identity, authority, & consent/Track Subscription & Entitlement Module/track-subscription-entitlement-module-architecture.md>) / [plan](<clusters/identity, authority, & consent/Track Subscription & Entitlement Module/track-subscription-entitlement-implementation-plan.md>) |
| `ai_taxonomy` | CL-02 | [AI Taxonomy module](<clusters/discovery classification & taxonomy/AI Taxonomy module/>) | [architecture](<clusters/discovery classification & taxonomy/AI Taxonomy module/ai-taxonomy-module-architecture.md>) / [plan](<clusters/discovery classification & taxonomy/AI Taxonomy module/ai-taxonomy-module-implementation-plan.md>) |
| `search_public_visibility` | CL-02 | [Search Public Visbility Module](<clusters/discovery classification & taxonomy/Search Public Visbility Module/>) | [architecture](<clusters/discovery classification & taxonomy/Search Public Visbility Module/search-public-visibility-module-architecture.md>) / [plan](<clusters/discovery classification & taxonomy/Search Public Visbility Module/search-public-visibility-module-implementation-plan.md>) |
| `taxonomy_classification` | CL-02 | [Taxonomy Classification Module](<clusters/discovery classification & taxonomy/Taxonomy Classification Module/>) | [architecture](<clusters/discovery classification & taxonomy/Taxonomy Classification Module/taxonomy-classification-module-architecture.md>) / [plan](<clusters/discovery classification & taxonomy/Taxonomy Classification Module/taxonomy-classification-module-implementation-plan.md>) |
| `healthcare_regulated_services` | CL-03 | [Healthcare Regulated Services module](<clusters/professional supply & readiness/Healthcare Regulated Services module/>) | [architecture](<clusters/professional supply & readiness/Healthcare Regulated Services module/healthcare-regulated-services-module-architecture.md>) / [plan](<clusters/professional supply & readiness/Healthcare Regulated Services module/healthcare-regulated-services-module-implementation-plan.md>) |
| `marketplace_supply` | CL-03 | [Marketplace Supply Module](<clusters/professional supply & readiness/Marketplace Supply Module/>) | [architecture](<clusters/professional supply & readiness/Marketplace Supply Module/marketplace-supply-module-architecture.md>) / [plan](<clusters/professional supply & readiness/Marketplace Supply Module/marketplace-supply-module-implementation-plan.md>) |
| `payment_payout_tax` | CL-03 | [Payment Payout & Tax Module](<clusters/professional supply & readiness/Payment Payout & Tax Module/>) | [architecture](<clusters/professional supply & readiness/Payment Payout & Tax Module/payment-payout-tax-module-architecture.md>) / [plan](<clusters/professional supply & readiness/Payment Payout & Tax Module/payment-payout-tax-module-implementation-plan.md>) |
| `professional_eligibility` | CL-03 | [Professional Eligibility Module](<clusters/professional supply & readiness/Professional Eligibility Module/>) | [architecture](<clusters/professional supply & readiness/Professional Eligibility Module/professional-eligbility-module-architecture.md>) / [plan](<clusters/professional supply & readiness/Professional Eligibility Module/professional-eligbility-module-implementation-plan.md>) |
| `trust_verification_screening` | CL-03 | [Trust verification Screening Module](<clusters/professional supply & readiness/Trust verification Screening Module/>) | [architecture](<clusters/professional supply & readiness/Trust verification Screening Module/trust-verification-screening-module-architecture.md>) / [plan](<clusters/professional supply & readiness/Trust verification Screening Module/trust-verification-screening-implementation-plan.md>) |
| `gig_demand` | CL-04 | [gig demand module](<clusters/customer demand, order, & resolution/gig demand module/>) | [architecture](<clusters/customer demand, order, & resolution/gig demand module/gig-demand-module-architecture.md>) / [plan](<clusters/customer demand, order, & resolution/gig demand module/gig-demand-implementation-plan.md>) |
| `review_dispute` | CL-04 | [review dispute module](<clusters/customer demand, order, & resolution/review dispute module/>) | [architecture](<clusters/customer demand, order, & resolution/review dispute module/review-dispute-module-architecture.md>) / [plan](<clusters/customer demand, order, & resolution/review dispute module/review-dispute-implementation-plan.md>) |
| `transaction_order` | CL-04 | [transaction order module](<clusters/customer demand, order, & resolution/transaction order module/>) | [architecture](<clusters/customer demand, order, & resolution/transaction order module/transaction_order-module-architecture.md>) / [plan](<clusters/customer demand, order, & resolution/transaction order module/transaction_order-implementation-plan.md>) |
| `booking_calendar` | CL-05 | [booking-calendar-module](<clusters/scheduling, media, & digital delivery/booking-calendar-module/>) | [architecture](<clusters/scheduling, media, & digital delivery/booking-calendar-module/booking-calendar-module-architecture.md>) / [plan](<clusters/scheduling, media, & digital delivery/booking-calendar-module/booking-calendar-module-implementation-plan.md>) |
| `digital_goods_access` | CL-05 | [digital-goods-access-module](<clusters/scheduling, media, & digital delivery/digital-goods-access-module/>) | [architecture](<clusters/scheduling, media, & digital delivery/digital-goods-access-module/digital-goods-access-module-architecture.md>) / [plan](<clusters/scheduling, media, & digital delivery/digital-goods-access-module/digital-goods-access-implementation-plan.md>) |
| `media_file_access` | CL-05 | [media-asset-module](<clusters/scheduling, media, & digital delivery/media-asset-module/>) | [architecture](<clusters/scheduling, media, & digital delivery/media-asset-module/media-asset-module-architecture.md>) / [plan](<clusters/scheduling, media, & digital delivery/media-asset-module/media-asset-module-implementation-plan.md>) |
| `video_session` | CL-05 | [video-session-module](<clusters/scheduling, media, & digital delivery/video-session-module/>) | [architecture](<clusters/scheduling, media, & digital delivery/video-session-module/video-session-module-architecture.md>) / [plan](<clusters/scheduling, media, & digital delivery/video-session-module/video-session-module-implementation-plan.md>) |
| `candidate_application_resume_privacy` | CL-06 | [Candidate Application & Resume Privacy Module](<clusters/Organization Hiring & Candidate Pipeline/Candidate Application & Resume Privacy Module/>) | [architecture](<clusters/Organization Hiring & Candidate Pipeline/Candidate Application & Resume Privacy Module/candidate-application-resume-privacy-module-architecture.md>) / [plan](<clusters/Organization Hiring & Candidate Pipeline/Candidate Application & Resume Privacy Module/candidate-application-resume-privacy-module-implementation-plan.md>) |
| `job_compliance` | CL-06 | [Job Compliance Module](<clusters/Organization Hiring & Candidate Pipeline/Job Compliance Module/>) | [architecture](<clusters/Organization Hiring & Candidate Pipeline/Job Compliance Module/job-compliance-module-architecture.md>) / [plan](<clusters/Organization Hiring & Candidate Pipeline/Job Compliance Module/job-compliance-module-implementation-plan.md>) |
| `job_interview` | CL-06 | [Job Interview Module](<clusters/Organization Hiring & Candidate Pipeline/Job Interview Module/>) | [architecture](<clusters/Organization Hiring & Candidate Pipeline/Job Interview Module/job-interview-module-architecture.md>) / [plan](<clusters/Organization Hiring & Candidate Pipeline/Job Interview Module/job-interview-module-implementation-plan.md>) |
| `messaging` | CL-07 | [Messaging Module](<clusters/Messaging Notification Rail/Messaging Module/>) | [architecture](<clusters/Messaging Notification Rail/Messaging Module/messaging-module-architecture.md>) / [plan](<clusters/Messaging Notification Rail/Messaging Module/messaging-module-implementation-plan.md>) |
| `notification` | CL-07 | [Notification Module](<clusters/Messaging Notification Rail/Notification Module/>) | [architecture](<clusters/Messaging Notification Rail/Notification Module/notification-module-architecture.md>) / [plan](<clusters/Messaging Notification Rail/Notification Module/notification-module-implementation-plan.md>) |
| `location_safety` | CL-08 | [Location Safety Module](<clusters/Privacy & Location Safety/Location Safety Module/>) | [architecture](<clusters/Privacy & Location Safety/Location Safety Module/location-safety-module-architecture.md>) / [plan](<clusters/Privacy & Location Safety/Location Safety Module/location-safety-module-implementation-plan.md>) |
| `privacy_data_erasure` | CL-08 | [Privacy Data Erasure Module](<clusters/Privacy & Location Safety/Privacy Data Erasure Module/>) | [architecture](<clusters/Privacy & Location Safety/Privacy Data Erasure Module/privacy-data-erasure-module-architecture.md>) / [plan](<clusters/Privacy & Location Safety/Privacy Data Erasure Module/privacy-data-erasure-module-implementation-plan.md>) |
| `admin_review_compliance_hold` | CL-09 | [Admin Review & Compliance Hold Module](<clusters/Moderation holds Audits and Ops/Admin Review & Compliance Hold Module/>) | [architecture](<clusters/Moderation holds Audits and Ops/Admin Review & Compliance Hold Module/admin-review-compliance-hold-module-architecture.md>) / [plan](<clusters/Moderation holds Audits and Ops/Admin Review & Compliance Hold Module/admin-review-compliance-hold-module-implementation-plan.md>) |
| `audit_event_ledger` | CL-09 | [Audit Event Ledger Module](<clusters/Moderation holds Audits and Ops/Audit Event Ledger Module/>) | [architecture](<clusters/Moderation holds Audits and Ops/Audit Event Ledger Module/audit-event-ledger-module-architecture.md>) / [plan](<clusters/Moderation holds Audits and Ops/Audit Event Ledger Module/audit-event-ledger-module-implementation-plan.md>) |
| `content_moderation_legal_notice` | CL-09 | [Content Moderation & Legal Notice Module](<clusters/Moderation holds Audits and Ops/Content Moderation & Legal Notice Module/>) | [architecture](<clusters/Moderation holds Audits and Ops/Content Moderation & Legal Notice Module/content-moderation-legal-notice-module-architecture.md>) / [plan](<clusters/Moderation holds Audits and Ops/Content Moderation & Legal Notice Module/content-moderation-legal-notice-module-implementation-plan.md>) |
| `observability_ops` | CL-09 | [Observability Ops Module](<clusters/Moderation holds Audits and Ops/Observability Ops Module/>) | [architecture](<clusters/Moderation holds Audits and Ops/Observability Ops Module/observability-ops-module-architecture.md>) / [plan](<clusters/Moderation holds Audits and Ops/Observability Ops Module/observability-ops-module-implementation-plan.md>) |
| `gamification_rewards` | CL-10 | [gamification-rewards-module](<clusters/incentives, rewards & prize economy/gamification-rewards-module/>) | [architecture](<clusters/incentives, rewards & prize economy/gamification-rewards-module/gamification-rewards-module-architecture(1).md>) / [plan](<clusters/incentives, rewards & prize economy/gamification-rewards-module/gamification-rewards-module-implementation-plan(1).md>) |
| `sweepstakes_prize` | CL-10 | [sweepstakes-module](<clusters/incentives, rewards & prize economy/sweepstakes-module/>) | [architecture](<clusters/incentives, rewards & prize economy/sweepstakes-module/sweepstakes-prize-module-architecture.md>) / [plan](<clusters/incentives, rewards & prize economy/sweepstakes-module/sweepstakes-prize-implementation-plan.md>) |
| `organization_hiring` | CL-06 | **MISSING** | Architecture and plan missing |

# Authority by Concern

Authority follows the **question**, not directory depth, timestamp, version number, or filename. Supporting evidence can reveal a discrepancy without acquiring another artifact's authority. An explicit approved architecture decision may amend authority or ownership; an incidental statement cannot.

| Concern | Primary Authority | Supporting Evidence | Must Not Be Overridden By |
| --- | --- | --- | --- |
| Product orientation | Project overview; actual V3 entry point and V2 evidence above | Registries; glossary | Detailed plans redefining product scope; overview also cannot override a specific binding implementation rule |
| Terminology/domain meaning | Ubiquitous Language / Glossary, including relevant addenda | Compliance definitions; Module meaning | Casual renaming or redefinition in architectures, plans, code |
| Compliance obligations | Compliance Inventory/material and explicitly approved compliance architecture | Owner evidence contracts; glossary | Plans, convenience, or code weakening established obligations |
| Database structure | Current Prisma schema plus approved migrations | Database-truth report; schema-related architecture | JSON registries, prose, or plans pretending fields/constraints already exist |
| Module identity | Deep Module Registry | Module architecture's refinement | Plans or local architecture silently creating a different Module |
| Cluster membership | Cluster Registry | Cluster architecture | Folder names, plans, or local relocation claims |
| Module source truth | Owning Module architecture | Registry boundaries; schema; glossary | Cluster coordination, Shared Operation reuse, plans, progress |
| Module lifecycle | Owning Module architecture | Owned enums/transitions; compliance | Cluster services, consuming Modules, plans |
| Module commands/queries | Owning Module architecture | Public interfaces; SH registry for registered identity | Consumer-local substitutes or plan-defined ownership |
| Cluster collaboration | Applicable Cluster architecture | Member public interfaces; declared registry bridges | Plans or local integration shortcuts |
| Shared operations | Canonical `context/shared/shared-operations.md` by SH ID and entry status | Source DOCX; owner interfaces | Aliases, duplicate implementations, local names/owners/classifications in plans |
| Cluster sequencing | Applicable Cluster build plan | Cluster architecture; member plans | Independent Module resequencing or root plan duplicating Module truth |
| Module sequencing | Applicable Module implementation plan within Cluster sequence | Module architecture; feature exit gates | Ad hoc implementation order or competing plans |
| Global invariants | Root architecture **once reconciled/finalized; currently MISSING** | Confirmed lower-level rules; registries; AGENTS | Plans, accidental code drift, or unadjudicated root claims |
| Global rollout | Root build plan **once reconciled/finalized; currently MISSING** | Cluster plans; prerequisites; release evidence | Competing Module-level implementation truth |
| Implementation reality | Application code + migrations + tests as executable evidence | Recorded verification; deployment evidence when available | Planning/completion claims unsupported by implementation |
| Progress state | Explicit progress tracker **currently MISSING**; Phase 2 report only for its recorded scope | Exit-gate evidence; implementation history | Architecture prose, registry status labels, or planned features |

## Boundaries that make the table operational

**Orientation and meaning.** The overview owns broad purpose, actors, platform scope, and principles, not detailed implementation. The glossary owns business definitions and distinctions; compliance can further constrain meaning. A genuine terminology conflict requires reconciliation.

**Compliance.** Established legal constraints, evidence requirements, regulated boundaries, sensitivity classifications, and retention obligations constrain implementation. Read approval/status labels in the relevant compliance architecture. A working glossary or a proposed ruling is not proof of legal adjudication. Leave unresolved legal/compliance questions unresolved until explicitly adjudicated; plans may explain implementation but cannot weaken obligations.

**Structure versus meaning.** Supabase/Postgres is source truth. Prisma and approved migrations describe executable models, fields, enums, relations, indexes, and constraints represented or approved in the repository. A foreign key does not allocate business ownership. Do not infer that the current schema has been migrated into a live database. If schema and migration history diverge, or future Module intent differs from either, record the mismatch; do not rewrite one automatically.

**Identity versus owned truth.** The Deep Module Registry owns IDs, broad purpose, declared boundaries, and decomposition. The Cluster Registry owns IDs, purpose, membership, and declared cross-Cluster bridges. Within those boundaries, the owning Module architecture governs model meaning, owned enums, source truth, lifecycles/transitions, invariants, commands, queries, public interfaces, local policy, event truth, and explicit non-ownership. It answers “who owns this lifecycle?”, “what may this Module mutate?”, and “which command changes this truth?”. Refinement cannot silently change Module identity.

**Coordination versus ownership.** Cluster architecture governs intra-Cluster collaboration, data/control flow, interface use, integration topology, Cluster boundaries/invariants, and inbound/outbound bridges. It coordinates Module truth without acquiring lifecycle ownership. A conflicting owner named by Cluster and Module architecture is a reconciliation issue.

**Shared Operations.** The SH registry owns permanent identity, canonical name, plain-English meaning, owner, classification, confirmed/proposed/unresolved status, reusable boundary, build rule, aliases, prohibited duplicates, and shared-mechanism/separate-truth rules. Its 126 IDs are stable: never renumber or reuse them. Plans consume operations by SH reference and specify local usage; they cannot redefine operations or authorize duplicates. Shared mechanism does not transfer lifecycle truth. Confirmed entries constrain implementation; proposed rulings require explicit architecture approval before schema/API commitment; unresolved entries must not be silently implemented. This map does not approve any pending ruling or rename any operation.

**Sequencing.** Cluster build plans own Cluster phases, numbered features, cross-Module dependency order, integration milestones, and exit gates. Module plans own internal phases, numbered features, dependencies, scope, feature tests, and exit gates while participating in Cluster sequence. Neither owns architecture. A plan requiring forbidden ownership or behavior must be reconciled before that work proceeds.

**Global concerns.** Finalized root architecture will govern platform invariants, Cluster topology, shared infrastructure, system-wide integration, global security, and data flow. Finalized root build plan will synthesize build order, Cluster maturation, prerequisites, cross-Cluster milestones, controlled release, and integrated hardening gates. Neither exists here. If recovered root artifacts predate completed lower-level planning in the known project sequence, mark them `REQUIRES_RECONCILIATION`; do not automatically grant them authority over adjudicated ownership. Do not invent global decisions to fill missing files.

**Reality and progress.** Code, migrations, and tests answer “what is implemented right now?”; accidental drift does not become architecture. Record technical debt/reconciliation work rather than rewriting architecture to legitimize code. Progress records status and evidence, never architecture. The Phase 2 report's past checks are not checks rerun by this task.

# Conflict Handling Protocol

Agents must not guess when authoritative artifacts disagree. First distinguish an actual contradiction from a missing contract, stale reference, or harmless difference in detail.

| Classification | Meaning |
| --- | --- |
| `ACTUAL_CONFLICT` | Incompatible requirements for the same concern and circumstances. |
| `STALE_REFERENCE` | A path, dependency statement, or evidence-availability claim no longer matches the discovered artifacts. |
| `NAMING_DRIFT` | Different terms or identifiers appear to refer to the same concept; equivalence is not assumed. |
| `DIFFERENT_LEVEL_OF_ABSTRACTION` | Compatible statements express broader rules and narrower detail. |
| `MISSING_CONTRACT` | Required interface, owner boundary, or behavior agreement is unspecified. |
| `MISSING_DEPENDENCY` | A necessary prerequisite or integration dependency is absent from the relevant sequence or evidence. |
| `MISSING_FEATURE` | Required architectural behavior has no corresponding implementation feature. |
| `SCHEMA_ARCHITECTURE_MISMATCH` | Executable structure/migration evidence and architectural intent do not align. |
| `UNRESOLVED_ARCHITECTURE` | A necessary ruling is missing, proposed, disputed, or awaiting explicit approval. |
| `HARMLESS_OMISSION` | Detail is intentionally outside an artifact's concern and its absence changes no required behavior. |

For each apparent disagreement:

1. Identify the exact concern and circumstances.
2. Identify the artifact owning that concern using this map.
3. Capture the conflicting statement and its artifact, with paths and section/line references.
4. Do not automatically edit either file or implement the conflicting interpretation.
5. Record a reconciliation item for the later pass: classification, concern, both statements/references, approval/status evidence, affected implementation, and the decision or missing evidence required.
6. Preserve confirmed ownership unless an explicit architecture decision changes it. If both artifacts legitimately own the **same** concern and disagree, neither wins by directory depth, modification time, or filename.
7. If architecture must change, amend it first or in the same explicit architecture decision; only then update plans and implementation.

No dedicated reconciliation ledger was discovered. In Step 1, report potential candidates only in the completion report; do not create another file. Later work should use its explicitly designated issue/decision record. Pause the affected implementation while the required decision is unresolved; independent authorized work may continue.

A plan-versus-architecture conflict follows this same sequence: stop the conflicting interpretation, identify the conflict and concern, consult this map, create a reconciliation item, explicitly amend architecture if needed, then update plans and implementation. Existing document-local authority ladders are evidence to review, not permission to collapse this concern map into one global precedence chain.

# Specificity Without Precedence

A narrower artifact may add detail **inside its legitimate concern**. It may not contradict an invariant owned at a broader architectural level. These illustrative statements are complementary, not new rulings adopted here:

- Root architecture: “Search is projection, not source truth.”
- Cluster architecture: “CL-03 sends approved Offering projections to Search.”
- Module architecture: “Marketplace Supply owns Offering publication truth.”

The first constrains the platform, the second describes a bridge, and the third identifies source ownership. More detail does not mean more authority over every concern.

Similarly, a Cluster build plan refines **when** a Module capability must participate, and a Module plan refines its internal implementation sequence. Neither changes **who** owns the lifecycle. If their dependency sequences are incompatible, record the inconsistency rather than silently reordering either plan.

# Context-Loading Routes

Read relevant entries/sections rather than indiscriminately loading everything. Apply existing `AGENTS.md` instructions alongside these routes; `CLAUDE.md` points to that file. Resolve generic references through the path index, not invented standardized paths.

## Cluster architecture or build-plan task

1. `context/context-map.md`.
2. Project overview: V3 entry point; consult V2 if its statements or references are relevant.
3. Deep Module Registry: `prisma/deep modules and schemas.json`.
4. Cluster Registry: `prisma/clusters.json`.
5. Relevant schema and migrations.
6. Relevant Ubiquitous Language / Compliance entries and addenda; explicit approved compliance decisions where present.
7. `context/shared/shared-operations.md`, especially consumed SH entries and governance.
8. Target Cluster architecture and build plan through the index.
9. Relevant member Module architectures and implementation plans, plus bridge contracts where needed.

If a member artifact is missing, record the gap. Do not infer its complete contract from a neighbor.

## Module implementation task

1. `context/context-map.md`.
2. Root architecture: **missing at baseline**. Record any global-authority gap; do not pretend the overview replaces it.
3. Relevant Cluster architecture.
4. Relevant Cluster build plan.
5. Target Module architecture.
6. Target Module implementation plan.
7. `context/shared/shared-operations.md`: governance and directly consumed SH entries.
8. Directly dependent Modules' public-interface sections.
9. Relevant schema/migrations.
10. Progress tracker: **missing at baseline**; consult the Phase 2 report only for its recorded database work.

Also consult registries, glossary, and compliance for identity, meaning, or regulated behavior touched by the feature. If missing context prevents resolving a necessary concern, record the gap and stop that dependent work; do not choose an owner or invent a gate.

**Do not load all 34 Module plans for every feature unless the task genuinely requires a platform-wide audit.** Only 33 plans are present at this baseline.

# Current Maturity

These labels describe artifact role and evidence readiness, not recency, implementation completion, legal approval, or a completed consistency audit. `FOUNDATIONAL` means source/orientation material; `CANONICAL_CURRENT` means the current concern authority subject to explicit ruling statuses; `DERIVED_CURRENT` means current derived planning evidence; `REQUIRES_RECONCILIATION` means known alignment work remains; `HISTORICAL_REFERENCE` means recorded earlier-state evidence; `MISSING` means no artifact found.

| Artifact class | Maturity | Basis and limitation |
| --- | --- | --- |
| Project overview V2 and V3 | `FOUNDATIONAL` | Broad product orientation; V3 states its front-door role. No blanket supersession inferred. |
| Ubiquitous Language / Compliance pack | `FOUNDATIONAL` | Canonical vocabulary and obligation source with base text/addenda and explicit legal-homework posture. Pending legal questions remain pending. |
| Deep Module Registry | `CANONICAL_CURRENT` | 34 canonical Module IDs and declared decomposition. Does not prove all 34 document pairs exist. |
| Cluster Registry | `CANONICAL_CURRENT` | v2.3 declares 10 Clusters and 34 memberships. |
| Shared Operations Markdown | `CANONICAL_CURRENT` | Verified SH-001–SH-126; confirmed, proposed, and unresolved statuses retain their meanings. |
| Shared Operations source DOCX | `FOUNDATIONAL` | 34/34 extract synthesis and rationale underlying the canonical registry; source extracts themselves were not found as a separate artifact set. |
| 10 Cluster architectures / 33 Module architectures | `CANONICAL_CURRENT` | Current lower-level architecture evidence with confirmed/proposed/unresolved distinctions; not a platform-wide reconciliation certificate. |
| 10 Cluster plans / 33 Module plans | `DERIVED_CURRENT` | Current lower-level sequencing evidence; not proof of implementation or complete synchronization. |
| CL-02 Search and Taxonomy plans' Cluster-availability/root-sequence references | `REQUIRES_RECONCILIATION` | Both describe unavailable CL-02 documents now present and reference root phases without a discovered root plan. No sequencing corrected here. |
| Organization Hiring Module pair | `MISSING` | Registry member lacks its own directory, architecture, and plan. |
| Prisma schema / migration files | `CANONICAL_CURRENT` | Executable repository evidence for structure, not proof of deployed schema or every approval. |
| Schema-to-migration coverage | `REQUIRES_RECONCILIATION` | 177 models/207 enums versus sole migration's 53 tables/31 enums; migration coverage must be established later. |
| Root architecture / root build plan | `MISSING` | Absent at repository root and context root; no basis to label a discovered root document finalized or stale. A recovered pre-completion version requires reconciliation. |
| README / Phase 2 status report | `HISTORICAL_REFERENCE` | Phase 1 orientation and explicit Phase 2 verification history; different scopes, not a global completion tracker. |
| Dedicated progress tracker / referenced harness documents | `MISSING` | No dedicated progress, code standards, library docs, or UI context files at the referenced paths. |
| Existing AGENTS / CLAUDE | `CANONICAL_CURRENT` | Active repository instructions and delegation; this map does not amend them. |
| Application code, seed, checks, tests where present | `CANONICAL_CURRENT` | Evidence only of implementation reality; no architecture approval or product-completion inference. |

Step 1 ends with this map. Reconciliation, new architecture artifacts, context linting, AGENTS changes, schema changes, and implementation belong to later explicitly scoped work.

