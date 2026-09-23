# [CL-02] Cross-Cluster Reconciliation Handoff

Cluster: **Discovery, Classification & Visibility**. Evidence extracted **2026-09-19**; handoff completed **2026-09-20**.

This is an evidence handoff, not a new architectural ruling, implementation plan, or certification that all source documents agree. No source artifact is changed by this extraction. In plain English: this file lists what this team needs from other teams, what it gives them, and which questions still need answers.

## Scope, authority, and evidence

Membership is `taxonomy_classification`, `ai_taxonomy`, and `search_public_visibility` ([CR]). All eight required Cluster/Module architecture and plan files are present. Source documents were inspected for ownership, public contracts, unresolved/proposed material, jobs/events, integration gates, and cross-cutting rails. Relevant neighboring public-contract sections were also sampled to distinguish matching boundaries from one-sided expectations; this is not a complete audit of those Clusters or their implementations.

[CM] assigns authority **by concern**: Module architecture owns Module truth/lifecycle; Cluster architecture owns collaboration; the Shared Operations registry owns registered operation identity/status/boundary; Cluster and Module plans own their respective sequencing; Prisma describes current persisted structure. File depth and modification time are not precedence rules. This handoff records registry disagreements for the later refresh without deciding whether the registry or a consumer must change. Neither root architecture nor root build plan is available; no invented root phase is a prerequisite.

Evidence shorthand below resolves to real repository files. Section numbers and feature numbers in each entry provide stable navigation; quoted spellings are preserved even where directory/file names contain typos.

| Key | Evidence file |
| --- | --- |
| CM | [context-map.md](<../../context-map.md>) |
| SH | [shared-operations.md](<../../shared/shared-operations.md>) |
| CR | [clusters.json](<../../../prisma/clusters.json>) |
| DR | [deep modules and schemas.json](<../../../prisma/deep modules and schemas.json>) |
| SC | [schema.prisma](<../../../prisma/schema.prisma>) |
| CA | [discovery-classification-architecture.md](<../../clusters/discovery classification & taxonomy/discovery-classification-architecture.md>) |
| CP | [discovery-classification-build-plan.md](<../../clusters/discovery classification & taxonomy/discovery-classification-build-plan.md>) |
| TA | [taxonomy-classification-module-architecture.md](<../../clusters/discovery classification & taxonomy/Taxonomy Classification Module/taxonomy-classification-module-architecture.md>) |
| TP | [taxonomy-classification-module-implementation-plan.md](<../../clusters/discovery classification & taxonomy/Taxonomy Classification Module/taxonomy-classification-module-implementation-plan.md>) |
| AA | [ai-taxonomy-module-architecture.md](<../../clusters/discovery classification & taxonomy/AI Taxonomy module/ai-taxonomy-module-architecture.md>) |
| AP | [ai-taxonomy-module-implementation-plan.md](<../../clusters/discovery classification & taxonomy/AI Taxonomy module/ai-taxonomy-module-implementation-plan.md>) |
| SA | [search-public-visibility-module-architecture.md](<../../clusters/discovery classification & taxonomy/Search Public Visbility Module/search-public-visibility-module-architecture.md>) |
| SP | [search-public-visibility-module-implementation-plan.md](<../../clusters/discovery classification & taxonomy/Search Public Visbility Module/search-public-visibility-module-implementation-plan.md>) |
| TRACK | [track-subscription-entitlement-module-architecture.md](<../../clusters/identity, authority, & consent/Track Subscription & Entitlement Module/track-subscription-entitlement-module-architecture.md>) |
| CAND | [candidate-application-resume-privacy-module-architecture.md](<../../clusters/Organization Hiring & Candidate Pipeline/Candidate Application & Resume Privacy Module/candidate-application-resume-privacy-module-architecture.md>) |
| ORG | [organization-hiring-module-architecture.md](<../../clusters/Organization Hiring & Candidate Pipeline/Organization Hiring Module/organization-hiring-module-architecture.md>) |
| MARKET | [marketplace-supply-module-architecture.md](<../../clusters/professional supply & readiness/Marketplace Supply Module/marketplace-supply-module-architecture.md>) |
| PRO | [professional-eligbility-module-architecture.md](<../../clusters/professional supply & readiness/Professional Eligibility Module/professional-eligbility-module-architecture.md>) |
| GIG | [gig-demand-module-architecture.md](<../../clusters/customer demand, order, & resolution/gig demand module/gig-demand-module-architecture.md>) |
| TRUST | [trust-verification-screening-module-architecture.md](<../../clusters/professional supply & readiness/Trust verification Screening Module/trust-verification-screening-module-architecture.md>) |
| PRIV | [privacy-data-erasure-module-architecture.md](<../../clusters/Privacy & Location Safety/Privacy Data Erasure Module/privacy-data-erasure-module-architecture.md>) |
| LOC | [location-safety-module-architecture.md](<../../clusters/Privacy & Location Safety/Location Safety Module/location-safety-module-architecture.md>) |
| MOD | [content-moderation-legal-notice-module-architecture.md](<../../clusters/Moderation holds Audits and Ops/Content Moderation & Legal Notice Module/content-moderation-legal-notice-module-architecture.md>) |
| CP03 | [professional-supply-readiness-build-plan.md](<../../clusters/professional supply & readiness/professional-supply-readiness-build-plan.md>) |
| CP06 | [organization-hiring-candidate-pipeline-build-plan.md](<../../clusters/Organization Hiring & Candidate Pipeline/organization-hiring-candidate-pipeline-build-plan.md>) |

Prior adjudication evidence is the user-supplied **“Cluster Reconciliation Rulings — CL-02”** attachment in this task, originally at `C:\Users\elijr\.codex\attachments\97799c8b-dee3-4b5b-bfad-5e9dfd750fdc\pasted-text.txt`. Its `CL02-R001`–`CL02-R020` labels correspond to the audit's `CL-02-R001`–`CL-02-R020`. Section 8 below preserves the decision content needed by a future task; attachment availability is not required to interpret this handoff. Earlier application work does not prove that every current paragraph is reconciled: residual statements are explicitly recorded in section 7.

### Counting and status conventions

- `D###` counts one extracted question/dependency group, merging original IDs only when they ask the same question. Conditional future capabilities are marked conditional; inclusion does not approve or schedule them.
- `B###` counts one directed capability relationship. Explicitly named endpoint groups are one inventory row, not one count per potential caller. Return values belong to the same bridge; distinct executor-result obligations receive their own row where material.
- `E###` counts an event-boundary family. Multiple exact spellings in a family are enumerated, not counted as separate implemented subscriptions. Proposed and unnamed families are included. No event wire contract is certified as matched end to end by this extraction.
- The SH inventory counts **67 unique referenced operations**, including compressed ranges, conditional/non-used references, platform mechanisms, and local operations with cross-Cluster consequences. Scope is explicit; this is not a claim that all 67 are active inter-Cluster APIs.
- `ALIGNED` means the documented ownership/boundary agrees at the stated level, not that runtime code exists. `QUESTIONABLE` means detail or the matching side is not demonstrated. `UNRESOLVED` means explicitly gated. `CONFLICTING` marks incompatible recorded statements without adjudicating them.

## 1. Unresolved decisions and external prerequisites

The following questions remain open in the current evidence. Original resolved IDs are retained only as history or pointers to their remaining implementation prerequisites. Options are those documented in the sources; “not specified” means this extraction does not invent candidates.

### D001 — Join verified meaning

- **Question:** What approved contract/policy completes join verified meaning?
- **Affected Modules / Clusters:** Taxonomy; Professional, Marketplace, Gig, Organization, Candidate owners — CL-02/03/04/06.
- **Evidence:** CA §26 U-CL02-02; TA U-TAX-02; TP07.
- **Current options:** classification-review acceptance; provenance validation; legacy field or separately approved replacement.
- **Why still open / what it blocks:** No canonical meaning; blocks exposing or writing this metadata safely. It cannot mean Trust Verification passed.
- **Shared Operations impact:** SH-023/121/123.

### D002 — Confidence representation and accepted-join meaning

- **Question:** What approved contract/policy completes confidence representation and accepted-join meaning?
- **Affected Modules / Clusters:** AI, Taxonomy, contextual owners — CL-02/03/04/06.
- **Evidence:** CA U-CL02-02; TA U-TAX-03; AA U-AI-06/PR-AI-05.
- **Current options:** basis points; 0..1 float; bands; calibrated provider values; retain on proposals versus accepted joins.
- **Why still open / what it blocks:** Scale, eligible sources and provenance/persistence purpose are not approved; blocks confidence schema/output and join snapshots.
- **Shared Operations impact:** SH-066/023/121.

### D003 — Candidate-authored classification provenance

- **Question:** What approved contract/policy completes candidate-authored classification provenance?
- **Affected Modules / Clusters:** Taxonomy, Candidate — CL-02/06.
- **Evidence:** CA U-CL02-03; TA U-TAX-04; SC TagSource.
- **Current options:** use user; add candidate; another explicit actor rule.
- **Why still open / what it blocks:** candidate is commented out in the enum; blocks candidate self-tagging provenance, not ownership.
- **Shared Operations impact:** SH-023/121.

### D004 — AI records, exact fields, states and transition graph

- **Question:** What approved contract/policy completes aI records, exact fields, states and transition graph?
- **Affected Modules / Clusters:** AI; contextual acceptance consumers — CL-02/03/06; Privacy CL-08.
- **Evidence:** CA U-CL02-04; AA U-AI-04/PR-AI-02 §§8–9; AP01; R009.
- **Current options:** proposed two-model design and illustrative enums; exact approved alternative not supplied.
- **Why still open / what it blocks:** AiClassificationLog/AiSuggestion are absent from Prisma. Cancellation, supersession, target/purpose types and physical constraints remain unapproved; production persistence/worker/review is blocked.
- **Shared Operations impact:** SH-053/065/066/121.

### D005 — Additional taxonomy trigger representation

- **Question:** What approved contract/policy completes additional taxonomy trigger representation?
- **Affected Modules / Clusters:** Taxonomy, Trust, Healthcare, Location, Job Compliance — CL-02/03/08/06.
- **Evidence:** CA U-CL02-06; TA U-TAX-09/10; R010; SC TaxonomyCategory/Tag.
- **Current options:** future approved owner-bound mappings/fields; exact design not specified.
- **Why still open / what it blocks:** Only represented and approved trigger facts are usable. Tag healthcare/sensitivity, location/license/background expansion lacks complete mapping; blocks unsupported trigger coverage. DataSensitivity authority itself is settled.
- **Shared Operations impact:** SH-022/017/020/021/028.

### D006 — Deletion and effective activity through parents

- **Question:** What approved contract/policy completes deletion and effective activity through parents?
- **Affected Modules / Clusters:** Taxonomy; all classified owners and Search/AI — CL-02/03/04/06.
- **Evidence:** CA U-CL02-07; TA PR-TAX-02/03 §9; TP lifecycle gate; R002.
- **Current options:** proposed no normal hard delete; proposed ancestry-derived effectiveActive; neither proposal silently approved.
- **Why still open / what it blocks:** Current isActive/cascades do not settle policy; blocks dependent admin mutations, assignment/readiness semantics and destructive maintenance.
- **Shared Operations impact:** SH-023/024/079/094/122.

### D007 — Canonical merge, alias, retirement and reference migration

- **Question:** What approved contract/policy completes canonical merge, alias, retirement and reference migration?
- **Affected Modules / Clusters:** Taxonomy; contextual owners — CL-02/03/04/06.
- **Evidence:** CA U-CL02-07; TA U-TAX-07; TP11; SH-122.
- **Current options:** proposed owner-coordinated merge with alias/provenance/history; exact model not specified.
- **Why still open / what it blocks:** No approved merge/alias/history model; SH-122 remains proposed. Blocks production merges and foreign-reference migration.
- **Shared Operations impact:** SH-122/123/091/051.

### D008 — Taxonomy history/version evidence

- **Question:** What approved contract/policy completes taxonomy history/version evidence?
- **Affected Modules / Clusters:** Taxonomy; downstream compliance/source owners — CL-02/03/04/06; Audit CL-09.
- **Evidence:** TA U-TAX-11; CA U-CL02-07; TP12.
- **Current options:** updatedAt plus AuditEvent/outbox; dedicated immutable taxonomy version/change record.
- **Why still open / what it blocks:** Compliance-trigger historical proof not chosen; blocks any behavior requiring stronger historical semantics.
- **Shared Operations impact:** SH-029/046/109/110.

### D009 — Taxonomy reparenting

- **Question:** What approved contract/policy completes taxonomy reparenting?
- **Affected Modules / Clusters:** Taxonomy; contextual owners — CL-02/03/04/06.
- **Evidence:** TA U-TAX-12; CA U-CL02-07.
- **Current options:** normal edits keep parent IDs non-editable; separate migration policy not specified.
- **Why still open / what it blocks:** Reparenting can invalidate assignments; blocks Category-to-Domain/Tag-to-Category move commands.
- **Shared Operations impact:** SH-023/122/091.

### D010 — Cross-category Tag compatibility

- **Question:** What approved contract/policy completes cross-category Tag compatibility?
- **Affected Modules / Clusters:** Taxonomy; all classified owners — CL-02/03/04/06.
- **Evidence:** TA U-TAX-05; TP04/07.
- **Current options:** match primary Category; span Categories; typed compatibility policy.
- **Why still open / what it blocks:** Schema permits more than policy establishes. Unsupported combinations return taxonomy_cross_category_policy_unresolved; blocks affected assignments.
- **Shared Operations impact:** SH-023/121.

### D011 — Normalization, aliases, locale and rule versioning

- **Question:** What approved contract/policy completes normalization, aliases, locale and rule versioning?
- **Affected Modules / Clusters:** Taxonomy, AI and vocabulary consumers — CL-02/03/04/06.
- **Evidence:** TA U-TAX-06; TP02/10.
- **Current options:** Unicode/case/punctuation/whitespace/slug/locale and migration rules not selected.
- **Why still open / what it blocks:** SH-079 ownership is settled but exact policy is not; blocks normalization-dependent creation, seeds and maintenance.
- **Shared Operations impact:** SH-079/077/124.

### D012 — Optional shared slug adoption and local slug policy

- **Question:** What approved contract/policy completes optional shared slug adoption and local slug policy?
- **Affected Modules / Clusters:** Taxonomy; public-entity owners — CL-02/03/04/06; platform text primitive.
- **Evidence:** TA §15; SH-124; U-TAX-06.
- **Current options:** adopt proposed SH-124 only after approval; exact reservation/rename policy not specified.
- **Why still open / what it blocks:** Conditional shared primitive is proposed; does not authorize a taxonomy rename/redirect policy. Blocks only dependent adoption.
- **Shared Operations impact:** SH-124/079.

### D013 — Approved seed vocabulary/source

- **Question:** What approved contract/policy completes approved seed vocabulary/source?
- **Affected Modules / Clusters:** Taxonomy — CL-02; product/reference-data authority not assigned a Cluster.
- **Evidence:** TP02 dependencies and seed rules.
- **Current options:** approved initial seed data source required; alternatives not specified.
- **Why still open / what it blocks:** The plan requires evidence of the approved source; extraction does not certify it. Blocks production seed-content commitment, not a loader contract test.
- **Shared Operations impact:** SH-079/044.

### D014 — Contextual assignment and affected-entity enumerator contracts

- **Question:** What approved contract/policy completes contextual assignment and affected-entity enumerator contracts?
- **Affected Modules / Clusters:** Taxonomy/Search; Professional, Marketplace, Gig, Organization, Candidate — CL-02/03/04/06.
- **Evidence:** R001/R007; TA U-TAX-08; TP07/09; CP07/12.
- **Current options:** owner-issued mutation/target validation and bounded enumerator contracts; DTO/cursor details not specified.
- **Why still open / what it blocks:** Ownership is resolved; matching foreign-owner implementation contracts and metadata semantics are prerequisites. Blocks each unsupported target integration, taxonomy fanout and merge migration.
- **Shared Operations impact:** SH-023/123/091/093/121.

### D015 — AI source DTOs and owner cursors

- **Question:** What approved contract/policy completes aI source DTOs and owner cursors?
- **Affected Modules / Clusters:** AI; Professional/Marketplace/Organization/Candidate; conditional Gig — CL-02/03/06/04.
- **Evidence:** AA U-AI-07; AP08–11; CP AI source-integration mapping.
- **Current options:** owner-approved target-specific safe fields, source versions, purpose/sensitivity and enumeration; exact DTOs not specified.
- **Why still open / what it blocks:** Rich AI inputs differ from minimal owner facts and Search projections; blocks each real source adapter and its backfill until supplied.
- **Shared Operations impact:** SH-123/003 proposed/078; SH-094 is not automatically the AI DTO.

### D016 — Search source versions, currentness and complete enumeration

- **Question:** What approved contract/policy completes search source versions, currentness and complete enumeration?
- **Affected Modules / Clusters:** Search; all searchable source/decision owners — CL-02/01/03/04/06/08/09.
- **Evidence:** SA §23 and §35.5; SP02/05/11; CP09/12.
- **Current options:** monotonic number; timestamp/version string; hash; opaque owner token with currentness query.
- **Why still open / what it blocks:** No universal ordering contract is selected. Partial enumeration is not proof of orphanhood; blocks unsafe stale-write suppression or destructive repair.
- **Shared Operations impact:** SH-024/094/091/093/052.

### D017 — Search durable-work physical representation

- **Question:** What approved contract/policy completes search durable-work physical representation?
- **Affected Modules / Clusters:** Search — CL-02; shared queue/platform, Ops CL-09.
- **Evidence:** CA U-CL02-08; SA PR-SPV-01/§35.1; SP01; R008.
- **Current options:** expand SearchUpsertEvent; another Search-owned representation.
- **Why still open / what it blocks:** Durable semantics are approved, Boolean is insufficient; exact fields/enums/migration remain open. Blocks production work persistence/worker.
- **Shared Operations impact:** SH-091/044/047/048/051/052.

### D018 — Typesense public layout, schema migration and query contract

- **Question:** What approved contract/policy completes typesense public layout, schema migration and query contract?
- **Affected Modules / Clusters:** Search; source owners — CL-02/03/04/06.
- **Evidence:** CA U-CL02-09; SA §35.2; SP03/06/11.
- **Current options:** multi-entity collection; per-entity collections/aliases; exact versions/facets/sorts/migration not selected.
- **Why still open / what it blocks:** Provider configuration is named but schema commitment unresolved; blocks production collection/query activation.
- **Shared Operations impact:** SH-092/093/094/115.

### D019 — Ranking weights and allowed quality/boost mapping

- **Question:** What approved contract/policy completes ranking weights and allowed quality/boost mapping?
- **Affected Modules / Clusters:** Search; Trust and Track — CL-02/03/01.
- **Evidence:** CA U-CL02-09; SA §35.6; §18 ranking.
- **Current options:** basic MVP relevance; exact trust/recency/taxonomy/boost weights not specified.
- **Why still open / what it blocks:** Policy tuning is open; eligibility-before-ranking is settled. Blocks unapproved advanced ranking, not the earliest vocabulary slice.
- **Shared Operations impact:** SH-005/024/092.

### D020 — Public Search transport and scoped key policy

- **Question:** What approved contract/policy completes public Search transport and scoped key policy?
- **Affected Modules / Clusters:** Search; Identity/security/platform — CL-02/01.
- **Evidence:** SA §35.12; SP06.
- **Current options:** server route/server component; approved scoped client Typesense key for anonymous public search.
- **Why still open / what it blocks:** No transport/key ruling; blocks dependent production API exposure. Admin credentials remain server-only.
- **Shared Operations impact:** SH-092; no new operation proposed.

### D021 — Protected Candidate collection/key isolation

- **Question:** What approved contract/policy completes protected Candidate collection/key isolation?
- **Affected Modules / Clusters:** Search, Candidate, Organization — CL-02/06; Identity CL-01.
- **Evidence:** SA §35.3; CA U-CL02-09/10; SP10.
- **Current options:** exact collection/key isolation; whether always server-mediated.
- **Why still open / what it blocks:** Public/protected separation is binding but physical/query layout unselected; blocks protected Search activation.
- **Shared Operations impact:** SH-001/002/024/094/092.

### D022 — Composite protected Candidate access

- **Question:** What approved contract/policy completes composite protected Candidate access?
- **Affected Modules / Clusters:** Search, Candidate, Organization, Role/Track; Hold/Moderation — CL-02/06/01/09.
- **Evidence:** CA U-CL02-10; CP10/11; SA §35; CAND §10/11.
- **Current options:** owner-issued privacy/projection, organization authority, applicable commercial/readiness/enforcement decisions; exact composition not specified.
- **Why still open / what it blocks:** Owners are known; action/field/decision agreement is incomplete. Blocks CP10 production exit.
- **Shared Operations impact:** SH-001/002/003 proposed/005/011/024/094.

### D023 — Organization commercial entitlement owner

- **Question:** What approved contract/policy completes organization commercial entitlement owner?
- **Affected Modules / Clusters:** Search, Organization, Track — CL-02/06/01.
- **Evidence:** SA §35.8; SH unresolved register; CA U-CL02-10.
- **Current options:** owner/model for organization ATS/search plan not confirmed.
- **Why still open / what it blocks:** Track User actor tracks do not by themselves establish Organization plans; blocks org-plan-gated Candidate Search if such plans are required.
- **Shared Operations impact:** SH-005.

### D024 — Candidate boost key/value, metering and count point

- **Question:** What approved contract/policy completes candidate boost key/value, metering and count point?
- **Affected Modules / Clusters:** Search, Track, Candidate — CL-02/01/06.
- **Evidence:** SA §35.7; SP10; TRACK §11.8/25.
- **Current options:** effective boost metadata only; approved metered usage; candidate_search_boost_applied timing undecided.
- **Why still open / what it blocks:** Exact commercial key and business count point not established; blocks metering/paid behavior that assumes them.
- **Shared Operations impact:** SH-005/006/091.

### D025 — Candidate Search sensitive-access audit scope

- **Question:** What approved contract/policy completes candidate Search sensitive-access audit scope?
- **Affected Modules / Clusters:** Search, Candidate, Audit — CL-02/06/09.
- **Evidence:** SA §35.9/27; SP10.
- **Current options:** every protected result/query; only designated detail/access operations.
- **Why still open / what it blocks:** Sensitivity/action matrix not agreed; blocks affected protected access, not public-hit logging. Candidate resume access proof is separate.
- **Shared Operations impact:** SH-030.

### D026 — Search work metadata retention/anonymization

- **Question:** What approved contract/policy completes search work metadata retention/anonymization?
- **Affected Modules / Clusters:** Search, Privacy — CL-02/08.
- **Evidence:** SA §35.10/28; CA §20; R017.
- **Current options:** retain; anonymize; erase subject-linked work metadata under approved policy.
- **Why still open / what it blocks:** No period or field map; blocks privacy-complete production handling of these records. No generic SH-098 use is approved by implication.
- **Shared Operations impact:** SH-095/096/097; SH-098 conditional.

### D027 — Reconciliation and maintenance cadence

- **Question:** What approved contract/policy completes reconciliation and maintenance cadence?
- **Affected Modules / Clusters:** Search/Taxonomy/AI; Ops/platform — CL-02/09.
- **Evidence:** SA §35.11/22; SP11; TA §22; AA §22.
- **Current options:** manual/admin callable first; scheduled frequency if separately approved.
- **Why still open / what it blocks:** No automatic Search cadence, periodic AI reclassification or intrinsic Taxonomy cron is confirmed; blocks only unapproved recurring execution.
- **Shared Operations impact:** SH-047/048/093.

### D028 — AI retention, minimum provenance and provider deletion policy

- **Question:** What approved contract/policy completes aI retention, minimum provenance and provider deletion policy?
- **Affected Modules / Clusters:** AI, Privacy; source/Healthcare owners — CL-02/08/03/06.
- **Evidence:** CA U-CL02-11; AA U-AI-03/§28; AP12.
- **Current options:** durations and minimum accepted-provenance fields not specified; deletion/anonymization/retention per approved owner facts.
- **Why still open / what it blocks:** Legal/provider/Privacy evidence missing; blocks production retention and sensitive AI use. Deleting a proposal does not delete separately accepted classification.
- **Shared Operations impact:** SH-095/096/097/098/070.

### D029 — Bedrock model, region, account, logging, fallback and retention

- **Question:** What approved contract/policy completes bedrock model, region, account, logging, fallback and retention?
- **Affected Modules / Clusters:** AI; source/Healthcare/Privacy; platform security — CL-02/03/06/08/01.
- **Evidence:** AA U-AI-02; AP04 provider preconditions.
- **Current options:** approved configuration per sensitivity lane; specific models/regions/fallback not selected.
- **Why still open / what it blocks:** Provider information/approval missing; blocks live sensitive lanes; deterministic fakes do not imply approval.
- **Shared Operations impact:** SH-065 proposed/061/070/078.

### D030 — Candidate raw-text provider use

- **Question:** What approved contract/policy completes candidate raw-text provider use?
- **Affected Modules / Clusters:** AI, Candidate, Privacy — CL-02/06/08.
- **Evidence:** AA U-AI-08; CA U-CL02-11; AP10.
- **Current options:** owner-normalized fields/skills only; narrowly approved raw resume/application text if ever allowed.
- **Why still open / what it blocks:** Purpose/legal/privacy permission unresolved; blocks raw-text transmission. Search raw-resume indexing remains forbidden.
- **Shared Operations impact:** SH-078/065.

### D031 — Healthcare-sensitive AI permission

- **Question:** What approved contract/policy completes healthcare-sensitive AI permission?
- **Affected Modules / Clusters:** AI, Healthcare and source owners — CL-02/03/06; Privacy CL-08.
- **Evidence:** AA U-AI-09/§19; CA §17/20.
- **Current options:** approved purpose/data-set allow, deny or review decision; exact owner contract not specified.
- **Why still open / what it blocks:** Healthcare/provider/BAA and sensitivity evidence required; blocks sensitive model calls, not classification-trigger truth.
- **Shared Operations impact:** SH-020/078/065.

### D032 — Shared foundation-model infrastructure placement

- **Question:** What approved contract/policy completes shared foundation-model infrastructure placement?
- **Affected Modules / Clusters:** AI; future AI capability owner/platform not assigned a Cluster.
- **Evidence:** CA U-CL02-12; AA PR-AI-06/08; SH-065.
- **Current options:** AI Taxonomy initially; broader infrastructure ownership when justified.
- **Why still open / what it blocks:** Registry explicitly proposed; no broader owner approved. Blocks dependent production adapter commitment/long-term reuse, not a port fake.
- **Shared Operations impact:** SH-065 proposed.

### D033 — Canonical events, actual consumers and payload versions

- **Question:** What approved contract/policy completes canonical events, actual consumers and payload versions?
- **Affected Modules / Clusters:** All CL-02 Modules; source/decision owners — CL-01/03/04/06/08/09; conditional CL-07.
- **Evidence:** CA U-CL02-13; AA U-AI-15/PR-AI-01; TA §12/21; SA §35.13.
- **Current options:** approved minimized event consumers; direct commands/queries where no event need exists.
- **Why still open / what it blocks:** Candidate vocabularies are not common wire contracts; Search outbound events have no proved consumer. Blocks asynchronous subscriptions, not direct SH-091.
- **Shared Operations impact:** SH-045/046/091.

### D034 — AI acceptance disposition transport

- **Question:** What approved contract/policy completes aI acceptance disposition transport?
- **Affected Modules / Clusters:** AI/Taxonomy and contextual mutation owners — CL-02/03/04/06.
- **Evidence:** AA U-AI-10/PR-AI-09; R003; AP07.
- **Current options:** transaction-aware direct recordSuggestionDisposition; versioned outbox fact.
- **Why still open / what it blocks:** Mutation-before-disposition and retry choreography are settled, transport/schema are not. Blocks dependent delivery implementation.
- **Shared Operations impact:** SH-121/044/045/046.

### D035 — Gig as AI classification target

- **Question:** What approved contract/policy completes gig as AI classification target?
- **Affected Modules / Clusters:** AI, Gig — CL-02/04.
- **Evidence:** CA U-CL02-14; AA U-AI-05; CR/DR discrepancy.
- **Current options:** MVP target; later target; excluded.
- **Why still open / what it blocks:** Cluster inbound inventory includes Gig; AI registry target references omit it. Blocks AI Gig feature only.
- **Shared Operations impact:** SH-065/123/121 if enabled.

### D036 — Novel term review-to-creation path

- **Question:** What approved contract/policy completes novel term review-to-creation path?
- **Affected Modules / Clusters:** Taxonomy, AI; classification consumers — CL-02/03/04/06.
- **Evidence:** CA U-CL02-15; R004; TP08.
- **Current options:** review-only novel proposals now; future controlled creation after dedupe/normalization/hierarchy/slug/compatibility/activation/merge rules.
- **Why still open / what it blocks:** Existing-ID-only initial acceptance is binding; reviewer approval alone does not authorize creation. Blocks future novel-term creation.
- **Shared Operations impact:** SH-121/079/023/122/124.

### D037 — User indexing scope

- **Question:** What approved contract/policy completes user indexing scope?
- **Affected Modules / Clusters:** Search, Identity, Privacy — CL-02/01/08.
- **Evidence:** CA U-CL02-16; SA §35.4; SC SearchEntityType.user.
- **Current options:** remove/deprecate; reserve internally; explicitly approved safe public use.
- **Why still open / what it blocks:** No User-safe projection/policy exists; default non-indexable. Blocks all User indexing.
- **Shared Operations impact:** SH-094/024/091.

### D038 — AI taxonomy reference storage

- **Question:** What approved contract/policy completes aI taxonomy reference storage?
- **Affected Modules / Clusters:** AI, Taxonomy — CL-02; external owners retain accepted assignments.
- **Evidence:** AA U-AI-11/PR-AI-04; AP01.
- **Current options:** logical UUID plus snapshot; foreign key.
- **Why still open / what it blocks:** Depends on deletion/merge policy; blocks AI schema reference design without selecting cascades.
- **Shared Operations impact:** SH-121/110.

### D039 — Prompt management persistence

- **Question:** What approved contract/policy completes prompt management persistence?
- **Affected Modules / Clusters:** AI; admin/platform governance — CL-02/09.
- **Evidence:** AA U-AI-12; AP02.
- **Current options:** immutable code/config templates; future database registry/admin publisher.
- **Why still open / what it blocks:** Product need and publishing governance not established; blocks database prompt registry/config workflow, not approved immutable provenance.
- **Shared Operations impact:** SH-065/072/029.

### D040 — Validated AI output persistence and raw-body exclusion approval

- **Question:** What approved contract/policy completes validated AI output persistence and raw-body exclusion approval?
- **Affected Modules / Clusters:** AI, Privacy and source owners — CL-02/08/03/06.
- **Evidence:** AA U-AI-13/PR-AI-11; AP01/12.
- **Current options:** full validated structured output; hash plus normalized suggestions; bounded diagnostic subset.
- **Why still open / what it blocks:** Payload/retention approval missing; blocks schema/content commitment. Raw source/provider-body persistence is not authorized by logs.
- **Shared Operations impact:** SH-066/072/078/095/098.

### D041 — First-class AI backfill lifecycle

- **Question:** What approved contract/policy completes first-class AI backfill lifecycle?
- **Affected Modules / Clusters:** AI; Ops/platform — CL-02/09.
- **Evidence:** AA U-AI-14/PR-AI-10; AP11.
- **Current options:** queue/per-target runs; separate AiBackfill if durable product pause/resume/progress/cancel/history requires it.
- **Why still open / what it blocks:** Product need not established; blocks adding a third business model by convenience, not bounded approved target runs.
- **Shared Operations impact:** SH-047/048/038.

### D042 — Rate, cost and public abuse-control policy

- **Question:** What approved contract/policy completes rate, cost and public abuse-control policy?
- **Affected Modules / Clusters:** AI/Search; platform security/Ops — CL-02/01/09.
- **Evidence:** AA U-AI-17; CA §22; SA §30.
- **Current options:** per-target/model/backfill limits and budgets; public Search quotas/mechanism not specified.
- **Why still open / what it blocks:** Platform/provider operational decisions missing; blocks unbounded production endpoints. No AI paid-plan requirement is currently established.
- **Shared Operations impact:** SH-036/038/065; no new rate-limit SH invented.

### D043 — AI review composition

- **Question:** What approved contract/policy completes aI review composition?
- **Affected Modules / Clusters:** AI, Taxonomy, Admin Review — CL-02/09.
- **Evidence:** AA U-AI-18.
- **Current options:** Taxonomy admin UI; shared Admin Review shell; AI route delegating acceptance.
- **Why still open / what it blocks:** Product/admin placement unselected; blocks only dependent review-shell integration. Low confidence is not automatically a Hold.
- **Shared Operations impact:** SH-121/002/054 proposed.

### D044 — Step-up action matrix

- **Question:** What approved contract/policy completes step-up action matrix?
- **Affected Modules / Clusters:** AI/Taxonomy/Search; Identity/Role — CL-02/01.
- **Evidence:** AA U-AI-01; CA §14; TA §18; SA backfill command.
- **Current options:** central designation of broad backfill/config/sensitive inspection actions; exact matrix not specified.
- **Why still open / what it blocks:** Fresh assurance requirements are conditional, not universal; blocks actions whose policy requires an unestablished assurance contract.
- **Shared Operations impact:** SH-014.

### D045 — Search restricted AI diagnostics

- **Question:** What approved contract/policy completes search restricted AI diagnostics?
- **Affected Modules / Clusters:** AI/Search; Admin/Ops — CL-02/09.
- **Evidence:** AA U-AI-16/PR-AI-07; DR Search consumer entry.
- **Current options:** accepted-source-only dependency; separately approved restricted diagnostic access.
- **Why still open / what it blocks:** No diagnostic consumer contract approved; blocks proposal diagnostic integration. Raw proposals never become Search truth.
- **Shared Operations impact:** SH-002/030; no direct indexing operation.

### D046 — Future notifications and recipient/trigger policy

- **Question:** What approved contract/policy completes future notifications and recipient/trigger policy?
- **Affected Modules / Clusters:** Taxonomy/AI/Search, Ops, Notification, source owners — CL-02/09/07/03/04/06.
- **Evidence:** TA/AA/SA §26.
- **Current options:** no baseline end-user notices; optional approved review/backfill/operator notices through Notification.
- **Why still open / what it blocks:** Conditional product requirement, recipient policy and templates not established; blocks only future notification activation.
- **Shared Operations impact:** SH-041; Notification retains SH-042/043 internally.

### D047 — Future provider callbacks

- **Question:** What approved contract/policy completes future provider callbacks?
- **Affected Modules / Clusters:** AI/Search; shared integration security/platform — CL-02/01/09.
- **Evidence:** CA §17; AA §20; SA provider boundary.
- **Current options:** none required now; verified/deduplicated callback if a future provider requires it.
- **Why still open / what it blocks:** No callback requirement or owner event ledger approved; blocks speculative callbacks/tables, not normal Bedrock/Typesense calls.
- **Shared Operations impact:** SH-059/060 conditional.

### D048 — Optional DecisionResult standardization

- **Question:** What approved contract/policy completes optional DecisionResult standardization?
- **Affected Modules / Clusters:** Taxonomy and decision consumers — CL-02/03/04/06; platform contract.
- **Evidence:** R016; TA §15/31; SH-015.
- **Current options:** documented local decision DTO; separately approved SH-015 adoption.
- **Why still open / what it blocks:** SH-015 remains proposed and cannot be a mandatory build gate. Blocks only dependent platform standardization.
- **Shared Operations impact:** SH-015 proposed.

### D049 — Shared manual-review claim capability

- **Question:** What approved contract/policy completes shared manual-review claim capability?
- **Affected Modules / Clusters:** AI/Taxonomy review; Admin Review/Ops/platform — CL-02/09.
- **Evidence:** CP06; SH-054 and unresolved register.
- **Current options:** approved shared claim/lease mechanism if needed; exact schemas/assignment/expiry not selected.
- **Why still open / what it blocks:** Generic review infrastructure remains proposed; blocks claim-based workflow activation, not basic protected proposal reads.
- **Shared Operations impact:** SH-054 proposed.

### D050 — Durable multi-step acceptance orchestration record

- **Question:** What approved contract/policy completes durable multi-step acceptance orchestration record?
- **Affected Modules / Clusters:** AI/Taxonomy/contextual owners — CL-02/03/04/06; platform workflow/Ops.
- **Evidence:** CA §16 workflow/saga boundaries.
- **Current options:** no generic Cluster saga by default; SH-049 mechanics if an approved durable record is required.
- **Why still open / what it blocks:** Need/record ownership beyond existing choreography is not approved; blocks inventing a saga store.
- **Shared Operations impact:** SH-049/121.

### D051 — Taxonomy maintenance run persistence

- **Question:** What approved contract/policy completes taxonomy maintenance run persistence?
- **Affected Modules / Clusters:** Taxonomy; shared queue/Ops — CL-02/09.
- **Evidence:** TP10 documentation gate; TA §22.
- **Current options:** shared QueueJob operational visibility; separately adjudicated Taxonomy-owned run if needed.
- **Why still open / what it blocks:** No extra business-run model approved; blocks adding one during normalization maintenance.
- **Shared Operations impact:** SH-047/038.

### D052 — Search query analytics/history

- **Question:** What approved contract/policy completes search query analytics/history?
- **Affected Modules / Clusters:** Search, Privacy — CL-02/08; product/Ops CL-09.
- **Evidence:** SP06 module-owned data.
- **Current options:** no current query-history model; future analytics only after architecture review.
- **Why still open / what it blocks:** No storage/retention/purpose approval; blocks recording personal query history by convenience.
- **Shared Operations impact:** SH-095/096/097 if future personal records; no new operation.

### D053 — Schema/migration foundation evidence

- **Question:** What approved contract/policy completes schema/migration foundation evidence?
- **Affected Modules / Clusters:** CL-02 owners; database/platform; Candidate CL-06.
- **Evidence:** R011; CM maturity register; SC; CP/TP/SP/AP preconditions.
- **Current options:** independently verify migration coverage before claiming clean-schema gates; no design choice made here.
- **Why still open / what it blocks:** Current schema and sole baseline migration differ; runtime/deployment parity not verified. Blocks relevant migration/production exit claims.
- **Shared Operations impact:** No new SH; affects persistence-backed contracts.

### D054 — Search privacy/enforcement completion receipt

- **Question:** What approved contract/policy completes search privacy/enforcement completion receipt?
- **Affected Modules / Clusters:** Search, Privacy, Moderation, Location — CL-02/08/09.
- **Evidence:** PRIV §17 at SH-091 completion boundary; SA §§10/28; MOD §12.
- **Current options:** durable receipt/correlation/acknowledgement representation not selected.
- **Why still open / what it blocks:** Queue acceptance is not completed deletion. Exact downstream completion contract remains unresolved; blocks truthful privacy completion and fully coordinated enforcement.
- **Shared Operations impact:** SH-091/095/103; SH-105 is a separate proposed related registry capability, not a new CL-02 dependency.

### D055 — Fuzzy location production policy and read-versus-generate integration

- **Question:** What approved contract/policy completes fuzzy location production policy and read-versus-generate integration?
- **Affected Modules / Clusters:** Search, Location, source owners — CL-02/08/03/04/06.
- **Evidence:** LOC §10 SH-028, §22 and U-08-17; SA §13; CA §13.
- **Current options:** consume getPublicLocationProjection; authorized generation via SH-028; exact freshness/expiry/regeneration policy remains owner-defined.
- **Why still open / what it blocks:** CL-02 describes SH-028 as returning safe fields; Location documents a persisting command with downstream refresh. Precise integration must avoid recursion and unsafe stale data; blocks unsupported production location surfaces.
- **Shared Operations impact:** SH-028/091; geocoder SH-069 remains outside CL-02 and proposed.

### D056 — Production shared foundation and audit-failure contracts

- **Question:** What approved contract/policy completes production shared foundation and audit-failure contracts?
- **Affected Modules / Clusters:** All CL-02 Modules; Identity/Role, Audit/Ops and platform — CL-01/09.
- **Evidence:** CP preconditions; TP preconditions; AA §13; SP preconditions; CM missing root artifacts.
- **Current options:** approved contract fakes for development; actual canonical capabilities before production; exact global audit failure policy not supplied.
- **Why still open / what it blocks:** Availability, runtime validation/config/secret boundary, mandatory-audit failure behavior and generic infrastructure cannot be inferred from missing root phases. Blocks affected production gates, not all early contract work.
- **Shared Operations impact:** SH-001/002/029/030/032–040/044–053/072/077/078.

### Resolved IDs that must not be reopened by extraction

`U-CL02-01` / `U-TAX-01` ownership is resolved (R001); `U-CL02-05` acceptance choreography is resolved (R003); `U-TAX-08` enumerator ownership is resolved (R007); `U-CL02-08` durable Search semantics are resolved but physical design is open (R008); `U-TAX-10` DataSensitivity meaning follows language/compliance authority (R010). D014, D017, D034 and D005 record only their remaining contracts/design. Existing-ID-only initial AI acceptance is binding (R004), even where old proposal headings remain. SA §35.14 is an outdated document-availability/revalidation note, recorded under I014 rather than counted as a new architecture decision.

## 2. Cross-Cluster bridge inventory

Producer means the owner sending the listed data/fact/instruction; consumer receives it. For a query, producer is the answering owner; for a command, producer is the requesting owner. A result travelling back is described in the contract profile. Platform infrastructure without a registered Module/Cluster is explicitly labelled **platform, unassigned**; it is not silently assigned to CL-09.

Each row inherits **producer output, consumer expectation, sequencing, failure behavior and privacy concerns** from its named profile below, specialized by the row's purpose/contract and evidence. This avoids repeating the same complete safety contract for every entity. `B###` rows are the countable bridges; provider-only paths are listed separately.

### Contract profiles (part of every referencing bridge record)

| Profile | Producer output → consumer expectation | Sequencing requirement | Failure behavior | Privacy / sensitivity |
| --- | --- | --- | --- | --- |
| AUTH | trusted actor/system identity and assurance → protected entry uses it, not browser identity claims | working CL-01 capability before production protected entry; contract fake for tests | unresolved/invalid actor denies protected action | minimal actor/session context; no credentials |
| DEC | owner-issued allow/deny/review with safe reason, evidence and source/policy version → consumer enforces its own named action | owner contract first; working decision before dependent production action | deny/review/unavailable does not become allow; no invented stale-decision TTL | only needed relationship/evidence facts; no raw checks or sensitive owner rows |
| VOC | canonical IDs, validity/normalization and triggered requirement facts → consuming owner validates classification without copying policy | taxonomy contract before source classification/readiness; unresolved term policies gate affected paths | invalid/unresolved compatibility fails closed; requirement trigger is not satisfaction | canonical vocabulary only; entity relationships stay with their owner |
| SRC | deterministic owner-safe projection, version/currentness and owner readiness → Search builds only allowed fields | CP09 per public target; CP11 prerequisite slice then CP10 for Candidate; no full producer Cluster prerequisite | malformed/unavailable source is not permission to index; reread current truth; no unapproved stale fallback | no raw resumes/private applications, exact coordinates or raw compliance evidence |
| AIIN | current owner-approved source DTO, target/version, allowed purpose/sensitivity → AI minimizes before invocation | CP09/AP08–09; CP10/AP10 Candidate; per-target prerequisite before CP06/AP11 backfill | owner deny/not-found/stale/unavailable prevents affected run; no client-text authority | source owner controls allowed fields; SH-078; sensitive/provider approval required |
| AIOUT | run/suggestion IDs and bounded provenance/status → source/review consumer treats them as advisory only | approved AI schema/lifecycle/provider and target adapter before real integration | failed/invalid output creates no accepted classification; duplicate calls have one persisted proposal effect | protected access and minimized diagnostics; no employment selection/ranking decisions |
| MUT | SH-121 validated acceptance/owner command with target, suggestion version, selected existing canonical IDs, reviewer/reason/idempotency/audit → contextual owner commits assignment and returns mutation reference | CP07 owner contract before CP08 acceptance; AI persistence prerequisites | failed owner mutation cannot mark AI accepted; lost acknowledgement retries same context without duplicate or reversal | proposal evidence scoped; accepted classification has separate privacy ownership |
| ENUM | owner-supplied affected/source IDs, bounded cursor and version/completeness context → CL-02 orchestrator refreshes/classifies only that scope | owner enumerator before CP12/TP09 fanout or AP11 enabled target | partial/unavailable enumeration checkpoints/retries; not proof of an orphan or completed backfill | no global cross-domain Prisma scan; IDs/cursors still subject-linked |
| REFRESH | canonical SH-091 request: entityType, entityId, action, reason, sourceVersion, requesterModule, idempotencyKey → Search acknowledges durable work, then converges through owner projection/readiness | source mutation commits first; CP02 contract harness; production persistence/provider gate before worker | source commit not rolled back by downstream outage; retry/outbox; duplicate fingerprint replays, changed fingerprint conflicts; stale work cannot resurrect data | IDs/versions/safe reasons only; no provider/source payload dump; acknowledgement is not deletion completion |
| PRIV | authorized target instruction or owner inventory/retention/export/result (row specifies direction) → Privacy coordinates, owner touches only owned truth and supplies actual completion evidence | owner protocol before affected data production; CP11/13 and AP12/TP12/SP09/12 integration | distinguish retained/skipped/pending/retryable/terminal outcomes; partial provider deletion never final success; D054 receipt unresolved | minimum fields, approved field maps/retention; proposal erasure is not accepted-classification erasure; source deletion differs from de-indexing |
| MOD | authorized case/action/target effect → Search applies hide/remove or reevaluates restoration and returns execution evidence | CP11 enforcement contract slice before CP10; reaction wiring later per R014 | accepted/queued is not completed; retry idempotently; restore never blindly republishes; no source lifecycle mutation | safe action refs, no case bodies/private evidence |
| OPS | sanitized material-action/access proof or operational evidence → canonical Audit/Ops owner records its own truth | baseline contracts before implementation; working mandatory proof/health/telemetry before production | audit failure policy where mandatory remains D056; operational failure visible, never substituted for domain outcome | SH-034 allowlists; no PHI, raw resume, model body, secrets, high-cardinality personal metrics |
| INFRA | common validated mechanism input/result: keys, fingerprints, leases, attempts, event envelopes, hashes or safe serialized input → owner retains domain semantics | contract/fake early; working capability before production work or provider use | bounded retry/dead-letter, explicit conflict/unknown/failure; no in-memory-only lock or local framework | payload minimal; policy and meaning remain with source/record owner; no implicit cross-domain transaction permission |
| MEDIA | source-owner-approved valid public media reference, or approved extracted input → Search/AI consumes only the permitted representation | Media/context access must be valid before source DTO includes it | inaccessible/revoked reference omitted or owner denies; no direct signing/downloading bypass | private file bodies/signed access cannot leak into index or AI logs |
| NOTICE | approved triggering fact, recipient context, template variables, sensitivity, priority, idempotency and route → Notification resolves delivery/routing | conditional future requirement only; no baseline dependency | canonical delivery retries/preferences; no local email/SMS/push or guessed recipients | minimized safe variables; sensitive content not notification body by default |
| QUERY | allowlisted public/protected results plus paging/safe exclusions → consuming product treats results as derived discovery, not current transaction authority | CP03 taxonomy; CP09 real sources; CP10 protected Candidate only after all gates | safe provider/dependency unavailable; never unfiltered DB fallback; protected denial before return | allowlisted facets/sorts, no exact location/private documents, protected surface isolated |

### Directed bridges

| ID | Producer Cluster / Module | Consumer Cluster / Module | Purpose / boundary type | Contract name and producer output specialization | Profile | Current status / evidence |
| --- | --- | --- | --- | --- | --- | --- |
| B001 | CL-01 / identity_access | CL-02 / all three | authentication and trusted worker actors; query | SH-001 resolveAuthenticatedActor | AUTH | ALIGNED — CA §14; TA/AA/SA §13; SH-001 |
| B002 | CL-01 / role_authority | CL-02 / all three | named resource/action authorization; policy/guardrail | SH-002 authorizeResourceAction; owner relationship facts | DEC | ALIGNED — CA §14; TA/AA/SA §18; SH-002 |
| B003 | CL-06 / organization_hiring | CL-02 / Search and AI; CL-01 Role interprets | organization membership/requester authority; query | owner-specific membership facts; SH-003 proposed only | DEC | UNRESOLVED — CA U-CL02-10; SA §13; AA §18; ORG §12; D022 |
| B004 | CL-01 / consent_disclosure via source owners | CL-02 / AI and Search | purpose/consent prerequisites carried indirectly by source decisions; policy/guardrail | upstream consent proof; no direct CL-02 consent operation established | DEC | QUESTIONABLE — CA §15 Consent; AA §19; D030/031; consent alone is not permission |
| B005 | CL-01 / identity_access | CL-02 / designated sensitive admin/backfill actions | fresh assurance; policy/guardrail | SH-014 requireStepUpForSensitiveAction, conditional | AUTH | UNRESOLVED — AA U-AI-01; CA §14; D044 |
| B006 | CL-01 / track_subscription_entitlement | CL-02 / Search | permitted boost or protected feature value; query | SH-005 resolveEntitlement; evaluateCandidateSearchBoost typed wrapper | DEC | UNRESOLVED — TRACK §11.8/25; SA §35.7–8; D023/024; boundary aligned, exact use gated |
| B007 | CL-02 / Search | CL-01 / track_subscription_entitlement | count an approved business usage point; command | SH-006 consumeMeteredEntitlement; usage receipt returned | INFRA | UNRESOLVED — SP10; SA §35.7; D024; not called for every query |
| B008 | CL-02 / Taxonomy | CL-03 / professional_eligibility, marketplace_supply | canonical classification vocabulary/validation; query | listTaxonomyTree/getTaxonomyTerm; SH-023/079 | VOC | ALIGNED — TA §14; PRO §13; MARKET §10/15; remaining metadata D001–011 |
| B009 | CL-02 / Taxonomy | CL-04 / gig_demand | canonical Gig classification; query | SH-022/023; canonical tree/term queries | VOC | ALIGNED — TA §14; GIG §15/19; D001–011 gate affected policy |
| B010 | CL-02 / Taxonomy | CL-06 / organization_hiring, candidate_application_resume_privacy | Organization/Job/Candidate classification; query | SH-023; canonical vocabulary and normalization | VOC | QUESTIONABLE — TA §14; ORG SH-023; CAND source projection; target-specific metadata/compatibility D003/010 |
| B011 | CL-02 / Taxonomy | CL-03 / professional_eligibility, trust_verification_screening, healthcare_regulated_services | classification-triggered requirements; query | SH-022 resolveTaxonomyRequirements; IDs/owners/severity/applicability | VOC | ALIGNED — CA Flow I/§13; TA §14; PRO §13; scope expansion remains D005 |
| B012 | CL-02 / Taxonomy | CL-06 / organization_hiring, job_compliance | accepted classification and job gate inputs; query | SH-022/023, source-owned readiness composition | VOC | ALIGNED — CA §13/15; ORG §13; SH-021/022; exact trigger expansion gated |
| B013 | CL-03 / trust_verification_screening | CL-02 / Taxonomy | expand approved verification requirement bindings; query | SH-017 resolveVerificationRequirements; no passed result | DEC | ALIGNED — TA §13/15; CA §13; SH-017 |
| B014 | CL-03/04/06 / each classified entity owner | CL-02 / Taxonomy and AI | target existence, version/status and relationship validity; query | SH-123 validateOwnedTargetReference; minimal SH-003 facts are separate | DEC | QUESTIONABLE — R001/R017; TA §13; AA §13; GIG §15; per-target contracts D014/015 |
| B015 | CL-02 / Taxonomy-led SH-121 workflow | CL-03/04/06 / each contextual assignment owner | apply an accepted existing-ID classification; command | owner assignment command name not yet specified; SH-121 choreography | MUT | CONFLICTING — R001/R003 and CA/TA flow versus CA §8 unresolved-owner rows and SH-121 final-mutation wording; I001/I002 |
| B016 | CL-03/04/06 / each contextual assignment owner | CL-02 / Taxonomy/Search fanout | enumerate entities affected by canonical term change; query | owner enumerator, exact operation/cursor unspecified | ENUM | UNRESOLVED — R007; TA U-TAX-08; TP09; CP12; D014 |
| B017 | CL-03 / professional_eligibility, marketplace_supply | CL-02 / AI | ProfessionalProfile/Offering classification input; query | owner safe classification DTO plus SH-123; distinct from SH-094 | AIIN | UNRESOLVED — AA U-AI-07; AP08; CP mapping; D015 |
| B018 | CL-06 / organization_hiring | CL-02 / AI | Organization/Job classification input; query | owner safe classification DTO plus SH-123 | AIIN | UNRESOLVED — AP09; CP09 mapping; D015 |
| B019 | CL-06 / candidate_application_resume_privacy | CL-02 / AI | privacy-safe Candidate skill/classification input; query | purpose-bound normalized fields/text DTO; SH-123 | AIIN | UNRESOLVED — AA U-AI-07/08; AP10; CP10; D015/030 |
| B020 | CL-04 / gig_demand | CL-02 / AI | possible future Gig classification input; query | target/DTO not approved | AIIN | UNRESOLVED — CA U-CL02-14; AA U-AI-05; CR/DR; D035 |
| B021 | CL-02 / AI | CL-03 / professional_eligibility, marketplace_supply | advisory suggestions for source editing; query | requestClassificationSuggestions result; getSuggestionsForTarget | AIOUT | QUESTIONABLE — AA §14; AP08; target/schema prerequisites D004/015 |
| B022 | CL-02 / AI | CL-06 / organization_hiring, candidate_application_resume_privacy | advisory organization/job/skill suggestions; query | requestClassificationSuggestions/getSuggestionsForTarget | AIOUT | QUESTIONABLE — AA §14; AP09/10; no hiring decision authority |
| B023 | CL-02 / AI | CL-09 / admin_review_compliance_hold and authorized Ops | restricted review/debug evidence; query | listSuggestionsForReview/getClassificationRun; optional shared review shell | AIOUT | UNRESOLVED — AA §14; U-AI-18; D043/049; low confidence is not automatic Hold |
| B024 | CL-03/06 / integrated source owners; CL-04 only if Gig approved | CL-02 / AI | backfill source enumeration; query | owner scope/cursor/current target versions | ENUM | UNRESOLVED — AA §22; AP11; CP06 target-specific gate; D014/015/035/041 |
| B025 | CL-03 / marketplace_supply | CL-02 / Search | Offering public projection/readiness; projection | SH-094 buildSourceProjection plus SH-024 | SRC | ALIGNED — CA §13; SA §13; MARKET §25; source lifecycle remains external |
| B026 | CL-04 / gig_demand | CL-02 / Search | Gig public projection/readiness; projection | SH-094/024, Gig visibility/lifecycle owner decision | SRC | ALIGNED — CA §13; SA §13; GIG §15/25 |
| B027 | CL-06 / organization_hiring | CL-02 / Search | Organization and Job public projection; projection | SH-094/024; SH-021 via Job owner composition | SRC | ALIGNED — CA §13; SA §13; ORG §13/25; final DTO/version detail D016 |
| B028 | CL-03 / professional_eligibility | CL-02 / Search | ProfessionalProfile projection/readiness; projection | SH-094/024; SH-016 evaluateProfessionalReadiness | SRC | ALIGNED — PRO §3.6/13; CA §13; SA §13 |
| B029 | CL-06 / candidate_application_resume_privacy | CL-02 / Search | protected Candidate source projection; projection | getCandidateSearchProjection / SH-094/024; active owner projection, rawResumeTextIndexed=false | SRC | UNRESOLVED — CAND §10/11/15; SA §13/25; D021/022 |
| B030 | CL-03 / trust_verification_screening | CL-02 / Search or composing source owner | safe TrustBadge and applicable readiness; query | public trust signal/version; SH-018 when needed | DEC | ALIGNED — CA §13; SA §13/25; TRUST events; no VerificationCheck reconstruction |
| B031 | CL-03 / healthcare_regulated_services | CL-02 / AI/Search or composing source owner | sensitive provider-input and public readiness permission; policy/guardrail | SH-020 evaluateHealthcareReadiness; exact purpose-bound input decision | DEC | UNRESOLVED — CA §13; AA §19; SA §13; D031 |
| B032 | CL-06 / job_compliance via organization_hiring | CL-02 / Search | Job public-feed compliance; policy/guardrail | SH-021 evaluateJobCompliance owner decision/evidence version | DEC | ALIGNED — CA §13/15; SA §13; ORG publication/source boundary; raw findings excluded |
| B033 | CL-03/04/06 / source and classification owners | CL-02 / Search | committed source/classification changes; command | SH-091 requestSearchProjectionRefresh; outbox event alternative in section 3 | REFRESH | QUESTIONABLE — CA §18; SA §21; MARKET/GIG/ORG/CAND; abbreviated neighbor envelopes require verification I004 |
| B034 | CL-01 / track_subscription_entitlement | CL-02 / Search | boost activation/expiration/revocation refresh; command | SH-091; TrackEntitlementGrantChanged illustrative event | REFRESH | QUESTIONABLE — TRACK §21/25 abbreviated fields; CA Flow H; I004; D024/033 |
| B035 | CL-08 / location_safety | CL-02 / Search | safe fuzzy location input; query | SH-028 applyFuzzyPublicLocation versus getPublicLocationProjection read | SRC | QUESTIONABLE — CA §13; LOC §10; D055/I008; source-approved input only |
| B036 | CL-08 / location_safety | CL-02 / Search | fuzzy projection change/invalidation; command | SH-091 after Location commit; proposed location.public_projection.* | REFRESH | QUESTIONABLE — LOC §§10/21/22; SA §25; D033/055 |
| B037 | CL-08 / privacy_data_erasure | CL-02 / AI, Search; Taxonomy only actual owned subject data | privacy erase/restrict/export/retain instruction; Shared Operation | SH-095 executePrivacyInstruction; authorized target/job/disposition | PRIV | UNRESOLVED — CA §20; AA/SA/TA §28; PRIV §17; D026/028/054 |
| B038 | CL-02 / AI, Search; Taxonomy only actual owned subject data | CL-08 / privacy_data_erasure | inventory, retention facts, export and completion proof; Shared Operation | SH-096/097; owner SH-095 result; safe export serializer | PRIV | UNRESOLVED — AA/SA/TA §28; PRIV §§13/17; no foreign join enumeration; D026/028/054 |
| B039 | CL-08 / Privacy or executing source owner | CL-02 / Search | de-index after privacy source mutation; command | SH-091; parent Privacy success waits for required completion evidence | REFRESH | UNRESOLVED — PRIV §17 completion ruling; SA §10/28; D054/I007 |
| B040 | CL-09 / content_moderation_legal_notice | CL-02 / Search | hide/remove/freeze/restore target effects; Shared Operation | SH-103 executeModerationDecision; SH-091 execution | MOD | QUESTIONABLE — MOD §12/25; SA §10; decision/executor split aligned, exact receipt/effect encoding D054 |
| B041 | CL-02 / Search | CL-09 / content_moderation_legal_notice | enforcement acknowledgement/completion/failure/restoration evidence; Shared Operation | SH-103 target result; no invented Search event | MOD | UNRESOLVED — SA §14; MOD §12; D054; queue acceptance not completion |
| B042 | CL-09 / admin_review_compliance_hold | CL-02 / Search; AI/Taxonomy only action-specific | applicable reusable stop sign; policy/guardrail | SH-011 evaluateComplianceHold | DEC | ALIGNED — CA §15; AA §19; SA §13; no universal AI hold or local blocked flag |
| B043 | CL-02 / approved domain workflow only | CL-09 / admin_review_compliance_hold | conditional justified Hold request; command | SH-012 requestComplianceHold; no automatic low-confidence trigger | DEC | UNRESOLVED — CP06 SH use; AA §14/19; source policy required, no baseline trigger |
| B044 | CL-02 / all three; sensitive access mainly AI/Search | CL-09 / audit_event_ledger | material-action and sensitive-access proof; command | SH-029 appendAuditEvent; SH-030 recordSensitiveAccess | OPS | ALIGNED — CA §21; TA/AA/SA §27; sensitive scope/audit failure D025/056 |
| B045 | CL-02 / all three | CL-09 / observability_ops | correlated logs, exceptions, metrics, failures, queues, health and incidents; Shared Operation | SH-032–040; owner health checks/results supplied to Ops | OPS | ALIGNED — CA §21; TA/AA/SA §29; domain outcome remains owner truth |
| B046 | platform, unassigned / application, event, queue and persistence mechanisms | CL-02 / all three | reliable commands, events, jobs, locks, state plumbing; background workflow | SH-044–053; SH-054 proposed review claim only | INFRA | QUESTIONABLE — CA §16; TA/AA/SA §§21–23; D049/050/056; no runtime availability proof |
| B047 | platform, unassigned / crypto, text, validation; external source policy owners | CL-02 / AI/Taxonomy/Search as used | safe canonical input, hash and validation; Shared Operation | SH-066/072/077/078; optional SH-015/124 | INFRA | ALIGNED — CA §11; AA §15; SH boundaries; adoption and exact local policy remain gated |
| B048 | CL-05 / media_file_access via source context owners | CL-02 / Search and AI | approved public references or owner-extracted input; provider handoff | owner DTO media/text fields; no direct Media download/signing contract | MEDIA | QUESTIONABLE — CA §19; AA/SA §24; indirect permission dependency, exact DTO D015/016 |
| B049 | CL-02 / approved Taxonomy/AI trigger or Search operator path via Ops | CL-07 / notification | future review/backfill/operator notice; command | SH-041 requestNotification, conditional | NOTICE | UNRESOLVED — TA/AA/SA §26; D046; no current end-user trigger |
| B050 | CL-02 / Search | CL-03/04/06 / public source discovery product surfaces | public discovery results; query | searchPublicDiscovery | QUERY | ALIGNED — CA §10/13; SA §14; exact provider/query settings D018/019/020 |
| B051 | CL-02 / Search | CL-06 / organization_hiring authorized product surface | protected Candidate search results; query | searchCandidatesForOrganization | QUERY | UNRESOLVED — CA Flow G; SA §10/35; CP10; D021–025 |
| B052 | CL-02 / Search | CL-09 / authorized Ops/admin tooling | projection diagnosis and safe rebuild control; query | inspectSearchProjection; runSearchBackfill/reconcileSearchProjection restricted commands | QUERY | QUESTIONABLE — SA §10/11/22; SP07/11; authorization/audit/cadence D027/044/056 |
| B053 | CL-03 / readiness owners; CL-06 Job Compliance; CL-09 enforcement owners | CL-02 / Search via source-owner composition | dependency-change reevaluation; event | semantic change signals → current SH-024 → SH-091; exact subscriptions unresolved | DEC | QUESTIONABLE — CA §18; SA §25; PRO §12 explicitly no assumed ProfessionalReadinessChanged event; E011–E021 |
| B054 | CL-02 / Taxonomy | CL-03/04/06 / classified entity owners and their readiness handlers | canonical term/trigger change fanout; event | proposed taxonomy.* facts identify changed terms; owners enumerate own entities | ENUM | UNRESOLVED — TA §12/21/22; R007; CP12; D014/033 |

### Provider-only and negative boundaries

- **AWS Bedrock → CL-02 AI**: provider invocation/output at proposed SH-065, validated by SH-066, error mapping SH-061, deletion SH-070 only if durable retained resources exist. CL-03/06 source owners and CL-08/Healthcare policies indirectly constrain this handoff (B017–024/B031/B037). It is an external provider boundary, not a new Cluster or an independently counted B row. No webhook or provider reconciliation record is currently required.
- **CL-02 Search ↔ Typesense**: SH-092 owns write/delete/query/schema/version/health; SH-093 drift repair stays Search-owned. Source owners never receive provider clients. Typesense success/failure never changes source lifecycle. B025–041/B050–052 record the inter-Cluster consequences.
- **CL-05** has indirect Media dependence only; no evidenced direct Booking, Video or Digital Goods lifecycle dependency in CL-02.
- **CL-07 Messaging/Thread** is not used; no ensureContextThread dependency or delivery-trigger subscription is established.
- **CL-10** has no evidenced direct CL-02 contract. Future reward-sourced grants may reach Search only through the established Track entitlement boundary; no Gamification points, prize odds or reward table becomes Search truth.
- Transaction/Order, Review/Dispute and Payment may contribute upstream source readiness or approved public quality fields, but CL-02 does not directly consume their raw financial/transaction/dispute tables. Do not invent additional direct edges from broad registry labels.

## 3. Events crossing Cluster boundaries

**Shared ordering/idempotency rule E-BASE (applies to every row):** a fact follows its authoritative source commit; SH-046 transactional outbox when reliable asynchronous publication is required; stable event ID/type/schema version, source Module, aggregate/target ID and version, occurredAt, correlation/causation, trusted actor/system context and privacy classification. Consumers use SH-045 inbox identity plus handler/version and idempotent owner commands. No exactly-once transport assumption. Current owner decisions/source version must be rechecked before projection; older work cannot restore hidden/erased data. Exact subscriptions/envelopes are not established merely by naming an event. Direct SH-091 remains an approved alternative where described.

Payload columns below list **expectations to confirm**, not newly approved schemas. Raw source text, resumes, private application data, exact addresses/coordinates, provider bodies and secrets are excluded. A required *reaction* is distinct from a confirmed event of that name.

| ID | Event name / family and maturity | Owner / producer | Consumer and purpose | Payload expectations / special ordering | Do both sides agree? / evidence |
| --- | --- | --- | --- | --- | --- |
| E001 | taxonomy.domain.created / taxonomy.domain.updated / taxonomy.domain.activity_changed — proposed | CL-02 Taxonomy | CL-03/04/06 source owners; downstream Search fanout | term ID/type, changed categories, version and safe reason; effective activity only after D006 policy; E-BASE | Owner/fanout purpose agreed by R007; exact external subscriptions unconfirmed. TA §12/21; CA U-CL02-13 |
| E002 | taxonomy.category.created / taxonomy.category.updated / taxonomy.category.activity_changed — proposed | CL-02 Taxonomy | CL-03 readiness/source and CL-04/06 classification owners | Category/parent refs and approved trigger-change categories, version; owners enumerate own joins; E-BASE | Wire/payload not jointly approved. TA §12/21; CA §18; D014/033 |
| E003 | taxonomy.tag.created / taxonomy.tag.updated / taxonomy.tag.activity_changed — proposed | CL-02 Taxonomy | CL-03/04/06 classified owners; accepted facet/readiness refresh | Tag/Category refs, change/version/reason; no invented Tag healthcare trigger; E-BASE | Semantic need present; wire contract open. TA §12/21; R010 |
| E004 | taxonomy.ai_suggestion_applied — proposed | CL-02 Taxonomy canonical acceptance workflow; contextual mutation owner remains CL-03/04/06 as applicable | AI disposition inside CL-02; possible contextual-owner consumers outside CL-02 not confirmed | suggestion/target/decision/accepted mutation refs and versions, safe outcome; only after successful owner mutation; E-BASE | External use not proved; direct versus outbox handoff D034. TA §12; AA §21; R003 |
| E005 | accepted classification changed — no common wire name | CL-03/04/06 contextual assignment owner (CL-02 for canonical term changes only) | CL-02 Search; refresh accepted classification facets/eligibility | target and changed canonical refs, source version, safe reason; source owner requests SH-091; E-BASE | Ownership settled; per-owner event contracts incomplete. CA §16/18; R001/R007 |
| E006 | ai_taxonomy.classification_completed — proposed | CL-02 AI | CL-03/06 requesting workflows or CL-09 admin, only if an approved async consumer is established | run/target/purpose, safe status, source/config versions; no accepted-truth effect; E-BASE | No confirmed consumer/schema. AA §21/U-AI-15; D033 |
| E007 | ai_taxonomy.classification_failed — proposed | CL-02 AI | CL-09 review/Ops or requesting CL-03/06 workflow, consumer unconfirmed | run/target, safe failure category and version refs; no raw provider error; operational telemetry is separate; E-BASE | No confirmed external event; failures already observable through Ops. AA §21/29 |
| E008 | ai_taxonomy.suggestions_created — proposed | CL-02 AI | CL-03/06 source editor or CL-09 review if approved | suggestion/run IDs, target/purpose/config/source versions; no instruction to accept/index; E-BASE | No jointly confirmed event or Notification trigger. AA §12/21/26 |
| E009 | OfferingCreated / OfferingUpdated / OfferingClassificationChanged / OfferingPricingChanged / OfferingActivated / OfferingPaused / OfferingRestricted / OfferingRestored / OfferingArchived — proposed family | CL-03 Marketplace | CL-02 Search when projected fields/public eligibility change | Offering ref, source version, minimal changed-field/reason and correlation; reread public readiness; E-BASE | Producer family listed, Search semantic expectation matches; exact subscriptions not demonstrated. MARKET §3.5/21; SA §21/25 |
| E010 | GigCreated / GigPublished / GigUpdated / GigPaused / GigReopened / GigCancelled / GigExpired / GigArchived — proposed | CL-04 Gig | CL-02 Search for public Gig convergence | Gig identity/source version/visibility-affecting change; no raw response/assignment evidence; E-BASE | Family proposed; matching Search handler names not specified. GIG §12/25; SA §25. Other response/assignment events are not assumed CL-02 consumers. |
| E011 | ProfessionalProfile created / status changed / projection-relevant fields changed — wire names open | CL-03 Professional Eligibility | CL-02 Search for Professional source projection | profile identity/current source version and safe change category; source re-read; E-BASE | Owner event families and Search refresh agree semantically. PRO §§3.5/12/14; no exact wire agreement. |
| E012 | Professional readiness dependency change — no ProfessionalReadinessChanged event assumed | CL-03 Professional Eligibility and underlying readiness owners | CL-02 Search via owner reevaluation and SH-091 | dependency identity/version; new SH-016/024 evaluation rather than guessed persisted readiness delta; E-BASE if an event is used | QUESTIONABLE event assumption: CA/SA require reaction, PRO §12 explicitly does not assume an MVP ProfessionalReadinessChanged source event. D033/I009. |
| E013 | organization.created / organization.updated / organization.status_changed — owner-defined names | CL-06 Organization Hiring | CL-02 Search for Organization public projection | organization identity/version, changed public-field/status category; E-BASE | Producer names present; Search names/versions not matched. ORG §12; CA §18; SA §25 |
| E014 | job.created / job.updated / job.publication_requested / job.status_changed / job.published / job.paused / job.filled / job.closed / job.archived — owner-defined family | CL-06 Organization Hiring | CL-02 Search when public Job state changes | Job identity/version, safe lifecycle reason; publication_requested alone is not permission to index; SH-021/024 gate; E-BASE | Owner vocabulary present, exact Search subscriptions unconfirmed. ORG §12; CA §13/18 |
| E015 | candidate_projection.changed — owner-listed | CL-06 Candidate Application & Resume Privacy | CL-02 Search for protected projection refresh | Candidate/projection ref, status and owner version/allowed fields; rawResumeTextIndexed=false; E-BASE | Candidate query/SH-094 and Search expectation match; event version/subscription and activation remain gated. CAND §§11/12; SA §13/25 |
| E016 | candidate_profile.created / candidate_profile.updated / candidate_profile.status_changed; candidate_privacy_execution.completed — owner-listed, indirect | CL-06 Candidate | CL-02 Search only via current Candidate projection/privacy contract where affected | safe subject/target and source/execution refs; completion means Candidate-owned execution, not automatically Search deletion; E-BASE | Indirect reaction inferred, not confirmed subscriptions. CAND §12; SA §25/28; D054 |
| E017 | trust.verification_requirement.changed; trust.verification_check.status_changed / passed / failed_or_review_required / expired / revoked; trust.professional_license.status_changed; trust.trust_badge.status_changed; trust.verification_readiness.changed — recommended | CL-03 Trust | CL-03 readiness/source owners and CL-02 Search when public readiness/display changes | IDs, status/reason/version/correlation, safe expiry/public signal; never raw reports; re-evaluate owner policy; E-BASE | Recommended producer names, not matched wire contracts. TRUST §12; SA §25; unrelated started/adverse-action events are not assumed direct Search consumers. |
| E018 | healthcare/public-data-boundary decision changed — wire name unconfirmed | CL-03 Healthcare via source readiness owner | CL-02 Search; AI source gate reevaluation for future runs | safe decision/policy/source version refs; no PHI/BAA content; E-BASE | Semantic dependency only; exact event need and consumer contract absent. CA §13/18; AA §19; SA §25 |
| E019 | Job compliance/publication decision changed — wire name unconfirmed | CL-06 Job Compliance through Organization Hiring | CL-02 Search; re-evaluate approved public Job source | Job/check/decision version and safe outcome; no raw findings; E-BASE | Readiness collaboration defined, wire event not established here. CA §13/18; SA §13/25 |
| E020 | ComplianceHold created/changed/released/expired where discoverability is affected — no CL-02 wire name | CL-09 Admin Review / Compliance Hold | CL-02 Search or source composer; action-specific reevaluation | hold/target/action scope, safe reason and version/expiry; reread applicable hold; E-BASE | SH-011 boundary aligned; event mapping not matched. CA §15/18; SA §25 |
| E021 | moderation action/restriction/restoration facts — exact names unconfirmed | CL-09 Content Moderation & Legal Notice | CL-02 Search through SH-103/091 | authorized case/action/target/effect/version; restore reevaluates readiness; E-BASE | MOD explicitly leaves names/envelopes to finalization. SA expects reaction, not case-table reads. MOD §12; SA §10/25 |
| E022 | privacy erasure/restriction/correction facts and downstream completion — wire names unconfirmed | CL-08 Privacy and executing data owners; CL-02 Search returns its own effect result | CL-02 Search/AI; CL-08 consumes owner execution evidence | privacy job/target/instruction/result refs; actual required completion before parent success; E-BASE | Protocol alignment exists; receipt transport/representation open. PRIV §17; SA §28; D054 |
| E023 | location.public_projection.updated / location.public_projection.invalidated — proposed | CL-08 Location Safety | CL-02 Search | target, source/policy version, safe fuzzy projection ref/reason; no exact inputs; E-BASE | LOC requires root event registration; Search needs refresh but subscription unconfirmed. LOC §12/21; SA §25. Reveal events are not a CL-02 dependency. |
| E024 | TrackEntitlementGrantChanged — illustrative; effective boost activation/change/expiration/revocation family | CL-01 Track | CL-02 Search and Candidate owner as appropriate | actor track/profile, safe key/value/effective time/evidence version; no provider payload; re-resolve current entitlement; E-BASE | TRACK §21 illustrative name; §25 and CA Flow H align on refresh; exact event/key/version unresolved. D024/033 |
| E025 | organization.membership_added / organization.membership_role_changed / organization.membership_removed — owner-defined, indirect | CL-06 Organization Hiring | CL-01 Role and CL-02 protected-query authorization path | organization/member relationship version and safe identity refs; never trust old authorization solely because index is unchanged; E-BASE | Organization facts dependency exists; no CL-02 membership-event/cache-invalidation subscriber confirmed. ORG §12; CA §14; D022 |
| E026 | Search projection refresh requested / converged / removed — conceptual only | CL-02 Search | possible CL-08/09 completion consumer; no approved outbound event | work/target/source/projection versions and safe result if separately agreed; never raw Typesense response; E-BASE | No Search-specific domain event confirmed; satisfy existing executor contract without inventing one. CA §16; SA §12/21/35.13; D033/054 |

`SearchUpsertEvent`, `AuditEvent`, `SystemEvent`, `IntegrationFailure`, `QueueJob` and `TrackUsageEvent` are persisted work/evidence/usage records, not interchangeable domain event wire contracts. Ops receives platform request/job/health/exception signals through SH-032–040 (B045), with owner-defined safe dimensions and correlation; those telemetry calls do not establish additional domain event subscriptions. `candidate_search_boost_applied` is an unresolved usage-event/count-point concept (D024), not a confirmed Search outbound domain event. Proposed taxonomy/AI names remain proposals despite appearing in feature test examples.

## 4. Shared Operations crossing boundaries

All **67** unique SH IDs referenced by the eight CL-02 source documents exist in the current registry. The table uses the registry's **exact current names, owners and statuses**, independently of local paraphrases. Six are `Proposed ruling`: SH-003, SH-015, SH-054, SH-065, SH-122 and SH-124. None is silently promoted here. No referenced operation is currently status `Unresolved`; several confirmed protocols still depend on unresolved local or cross-Cluster policies.

Source-column abbreviations identify every CL-02 file where the ID occurs, including compressed ranges/slash lists. Profile/bridge sections explain input/result, failure, sequencing and sensitivity. “Consumes platform” does not assign that platform mechanism to a new Module. Internal operations are included because the user requested every referenced provided/consumed/expected operation; their scope is not disguised as an external API.

| SH ID / canonical name | Current registry owner | Registry status | CL-02 provision/use and boundary scope | Source files |
| --- | --- | --- | --- | --- |
| SH-001 `resolveAuthenticatedActor` | Identity & Access | Confirmed | Consumes CL-01 actor resolution; B001. | AA, AP, CA, CP, SA, SP, TA, TP |
| SH-002 `authorizeResourceAction` | Role / Authority | Confirmed | Consumes CL-01 authorization; B002/003. | AA, AP, CA, CP, SA, SP, TA, TP |
| SH-003 `queryOwnerFacts` | Each source Module | Proposed ruling | Conditional minimal source-owner facts, proposed; not SH-123 eligibility or rich AI input; B003/014. | AA, AP, CA, CP, SA, SP |
| SH-005 `resolveEntitlement` | Track Subscription & Entitlement | Confirmed | Consumes CL-01 commercial decision; B006; org plan/boost details open. | AA, CA, CP, SA, SP |
| SH-006 `consumeMeteredEntitlement` | Track Subscription & Entitlement | Confirmed | Conditional command to CL-01 at approved usage point only; B007. | SA, SP |
| SH-011 `evaluateComplianceHold` | Admin Review / Compliance Hold | Confirmed | Consumes CL-09 applicable Hold decision; B042. | AA, CA, CP, SA, SP |
| SH-012 `requestComplianceHold` | Admin Review / Compliance Hold | Confirmed | Conditional request to CL-09; no universal AI or low-confidence trigger; B043. | CP |
| SH-014 `requireStepUpForSensitiveAction` | Identity & Access | Confirmed | Conditional CL-01 step-up; D044/B005. | AA, AP, CA, SA, TA, TP |
| SH-015 `returnDecisionResult` | Shared contract; policy owner varies | Proposed ruling | Optional shared DTO adoption; proposed, local documented results allowed; D048. | CP, SA, SP, TA, TP |
| SH-016 `evaluateProfessionalReadiness` | Professional Eligibility | Confirmed | Consumes CL-03 Professional readiness directly or in source composition; B028. | CA, CP, SA, SP |
| SH-017 `resolveVerificationRequirements` | Trust Verification / Screening | Confirmed | Consumes CL-03 Trust requirement bindings; B013. | CA, TA, TP |
| SH-018 `evaluateVerificationReadiness` | Trust Verification / Screening | Confirmed | Consumes CL-03 verification readiness only where required; never infer from badge; B030. | CA, CP, SA, SP, TA |
| SH-020 `evaluateHealthcareReadiness` | Healthcare / Regulated Services | Confirmed | Consumes CL-03 healthcare/provider/public boundary; B031. | CA, CP, SA, SP |
| SH-021 `evaluateJobCompliance` | Job Compliance | Confirmed | Consumes CL-06 Job decision preferably through source composition; B032. | CA, CP, SA, SP |
| SH-022 `resolveTaxonomyRequirements` | Taxonomy & Classification | Confirmed | Provides Taxonomy requirement triggers to CL-03/04/06; B009/011/012. | CA, CP, SA, TA, TP |
| SH-023 `validateTaxonomyAssignment` | Taxonomy & Classification | Confirmed | Provides canonical Taxonomy assignment validation to contextual owners; B008–015. | AA, AP, CA, CP, SA, TA, TP |
| SH-024 `evaluatePublicReadiness` | Source/compliance owner; Search composes | Confirmed | Provides for Taxonomy records; consumes other source/compliance owners; Search composes; B025–032. | CA, CP, SA, SP, TA, TP |
| SH-028 `applyFuzzyPublicLocation` | Location Safety | Confirmed | Consumes CL-08 fuzzy projection boundary; read/generate distinction D055/B035. | CA, CP, SA, SP |
| SH-029 `appendAuditEvent` | Audit / Event Ledger | Confirmed | Requests CL-09 generic proof; B044. | AA, AP, CA, CP, SA, SP, TA, TP |
| SH-030 `recordSensitiveAccess` | Audit / Event Ledger | Confirmed | Requests CL-09 sensitive-access proof conditionally; B044/D025. | AA, AP, CA, CP, SA, SP, TA, TP |
| SH-032 `createRequestContext` | Observability / platform infrastructure | Confirmed | Consumes/contributes CL-09 or platform telemetry, context and health; B045; no domain truth substitution. | AA, AP, CA, CP, SA, SP, TA, TP |
| SH-033 `writeStructuredLog` | Observability / Ops | Confirmed | Consumes/contributes CL-09 or platform telemetry, context and health; B045; no domain truth substitution. | AA, AP, CA, CP, SA, SP, TA, TP |
| SH-034 `sanitizeTelemetryMetadata` | Observability / Ops and Audit payload policy | Confirmed | Consumes/contributes CL-09 or platform telemetry, context and health; B045; no domain truth substitution. | AA, AP, CA, CP, SA, SP, TA, TP |
| SH-035 `captureException` | Observability / Ops | Confirmed | Consumes/contributes CL-09 or platform telemetry, context and health; B045; no domain truth substitution. | AA, AP, CA, CP, SA, SP, TP |
| SH-036 `emitMetric` | Observability / Ops | Confirmed | Consumes/contributes CL-09 or platform telemetry, context and health; B045; no domain truth substitution. | AA, AP, CA, CP, SA, SP, TA, TP |
| SH-037 `recordIntegrationFailure` | Observability / Ops | Confirmed | Consumes/contributes CL-09 or platform telemetry, context and health; B045; no domain truth substitution. | AA, AP, CA, CP, SA, SP, TA, TP |
| SH-038 `recordQueueTelemetry` | Observability / Ops / queue infrastructure | Confirmed | Consumes/contributes CL-09 or platform telemetry, context and health; B045; no domain truth substitution. | AA, AP, CA, CP, SA, SP, TA, TP |
| SH-039 `checkServiceHealth` | Observability / Ops coordinates; owner supplies check | Confirmed | Consumes/contributes CL-09 or platform telemetry, context and health; B045; no domain truth substitution. | AA, AP, CP, SA, SP |
| SH-040 `correlateOpsIncident` | Observability / Ops | Confirmed | Consumes/contributes CL-09 or platform telemetry, context and health; B045; no domain truth substitution. | CP |
| SH-041 `requestNotification` | Notification | Confirmed | Conditional future requests to CL-07; no baseline notifications; B049. | AA, SA, TA |
| SH-044 `executeIdempotentCommand` | Platform application infrastructure | Confirmed | Consumes platform idempotent command mechanism; B046. | AA, AP, CA, CP, SA, SP, TA, TP |
| SH-045 `deduplicateDomainEvent` | Platform event infrastructure; consumer owns inbox | Confirmed | Consumes platform inbox mechanism; consumer owns effect identity; B046/E-BASE. | AA, AP, CA, CP, SA, SP, TA, TP |
| SH-046 `publishDomainEvent` | Platform event/outbox infrastructure | Confirmed | Consumes platform outbox; source owns facts/payload; B046/E-BASE. | AA, AP, CA, CP, SA, SP, TA, TP |
| SH-047 `enqueueReliableJob` | Shared queue infrastructure | Confirmed | Consumes shared durable queue; CL-02 owns completion meaning; B046. | AA, AP, CA, CP, SA, SP, TA, TP |
| SH-048 `executeRetryWithBackoff` | Shared queue/platform infrastructure | Confirmed | Consumes shared bounded retry/dead-letter; owner classifies failures; B046. | AA, AP, CA, CP, SA, SP, TA, TP |
| SH-049 `orchestrateWorkflowSteps` | Workflow-owning Module using shared runner | Confirmed | Conditional workflow mechanics if approved acceptance workflow record is needed; D050. | AA, CA |
| SH-050 `reconcileWorkflowStatus` | Workflow owner using shared helper | Confirmed | Range-only reference in AA SH-044..053; no specific CL-02 reconciliation workflow contract is established and no new business record is implied. | AA |
| SH-051 `acquireAggregateLock` | Shared persistence infrastructure | Confirmed | Consumes aggregate locking; owner key/conflict policy; B046. | AA, AP, CA, CP, SA, SP, TA, TP |
| SH-052 `withOptimisticConcurrency` | Shared persistence infrastructure | Confirmed | Consumes optimistic concurrency; owner version policy; B046/D016. | AA, AP, CA, CP, SA, SP, TA, TP |
| SH-053 `transitionLifecycleState` | Shared mechanism; lifecycle owner supplies policy | Confirmed | Consumes lifecycle plumbing only after owner transition policy approval; B046. | AA, AP, CA, CP, TA |
| SH-054 `claimWorkItem` | Shared work-queue/locking capability | Proposed ruling | Proposed shared reviewer claim/lease, conditional; D049. | CP |
| SH-059 `verifyProviderWebhookSignature` | Shared integration-security shell; provider adapter supplies algorithm | Confirmed | Not used for current providers; conditional future callback verification; D047. | AA, CA, SP |
| SH-060 `deduplicateProviderEvent` | Provider-owning Module using shared primitive | Confirmed | Not used for current inference/Search; future provider-owner dedupe only; D047. | AA, CA, SP |
| SH-061 `translateProviderStatus` | Provider-owning adapter | Confirmed | Adapter-local AI/Search error/status translation; shared contract, separate meanings. | AA, AP, SA, SP |
| SH-065 `invokeFoundationModel` | AI Taxonomy initially; broader AI infrastructure ownership unresolved | Proposed ruling | AI provider boundary proposed; external Bedrock, broader platform owner unresolved; D029/032. | AA, AP, CA, CP, TA, TP |
| SH-066 `validateStructuredProviderOutput` | Shared validation primitive; consuming Module owns schema | Confirmed | Consumes shared output validator; AI owns schema/semantic validation; B047. | AA, AP, CA, CP |
| SH-070 `deleteProviderResource` | Provider-owning Module | Confirmed | Provider-owner deletion only if an applicable retained resource exists; D028/029. | AA |
| SH-072 `hashCanonicalPayload` | Shared security/cryptography capability | Confirmed | Consumes shared hash mechanism; owner defines what hash proves; B047. | AA, AP, CA, CP |
| SH-077 `buildCanonicalTextSnapshot` | Shared text canonicalization mechanism | Confirmed | Consumes shared deterministic text snapshot; source field choice separate; B047. | AA, AP, CA, CP |
| SH-078 `minimizeAndRedactProviderInput` | Source-data owner supplies policy; shared serializer enforces | Confirmed | Consumes source-policy-driven serializer before external AI call; B017–019/031/047. | AA, AP, CA, CP |
| SH-079 `normalizeControlledTerm` | Taxonomy & Classification policy over shared text primitive | Confirmed | Provides Taxonomy normalization policy over shared text; B008–012; D011. | AA, AP, CA, CP, TA, TP |
| SH-091 `requestSearchProjectionRefresh` | Search / Public Visibility | Confirmed | Provides Search refresh command to source/decision owners; B033/034/036/039/040. | AA, AP, CA, CP, SA, SP, TA, TP |
| SH-092 `writeSearchProjection` | Search / Public Visibility | Confirmed | Search-owned external provider adapter; internal to CL-02, no foreign Typesense clients. | CA, CP, SA, SP |
| SH-093 `reconcileSearchProjection` | Search / Public Visibility | Confirmed | Search internal reconciliation worker with external owner inputs/enumeration; B016/025–029. | CA, CP, SA, SP, TA |
| SH-094 `buildSourceProjection` | Each source Module | Confirmed | Taxonomy provides its source projection; Search consumes CL-03/04/06 owner projections; B025–029. AI DTO is separate. | CA, CP, SA, SP, TA, TP |
| SH-095 `executePrivacyInstruction` | Privacy orchestrates; each data owner executes | Confirmed | CL-02 owner executors receive CL-08 instructions and return results; B037/038. | AA, AP, CA, CP, SA, SP, TA, TP |
| SH-096 `enumerateSubjectData` | Each data-owning Module through Privacy-defined interface | Confirmed | CL-02 owners provide inventory to CL-08, not foreign-join scans; B038. | AA, AP, CA, CP, SA, SP, TA, TP |
| SH-097 `evaluateRetentionRequirement` | Data owner supplies facts; Privacy records exemption | Confirmed | CL-02 supplies retention facts, CL-08 records exemption; B038. | AA, AP, CA, CP, SA, SP, TA, TP |
| SH-098 `anonymizePersonalFields` | Shared primitive; record owner supplies mapping | Confirmed | Shared anonymization only with approved owner field map; Search has no unconditional dependency; D026/028. | AA, AP, CA, CP, SA, TA, TP |
| SH-103 `executeModerationDecision` | Moderation owns decision; each target owner executes | Confirmed | Search executes CL-09 decision and returns effect evidence; B040/041. | CA, CP, SA, SP |
| SH-109 `snapshotExternalDecision` | Consuming domain owner | Confirmed | Local consuming-owner snapshot pattern for external decision evidence; no copied policy. | TA |
| SH-110 `createDomainSnapshot` | Downstream lifecycle owner | Confirmed | Local owner snapshot pattern; AI reference/provenance design remains gated; D038/040. | TA |
| SH-115 `buildAggregateProjection` | Projection owner | Confirmed | Search-owned versioned projection/rebuild mechanism; no foreign lifecycle ownership. | CA, CP, SA, SP |
| SH-121 `applyAiSuggestion` | Workflow between AI Taxonomy and Taxonomy & Classification | Confirmed | CL-02 acceptance workflow extends to contextual CL-03/04/06 mutations; B015; registry wording discrepancy S01. | AA, AP, CA, CP, TA, TP |
| SH-122 `mergeCanonicalRecord` | Taxonomy & Classification for taxonomy terms | Proposed ruling | Proposed Taxonomy-internal merge; cross-owner reference migration remains gated; D007. | TA, TP |
| SH-123 `validateOwnedTargetReference` | Target owner | Confirmed | Consumes target-owner validity/version/relationship decision; B014; not generic Prisma access. | AA, AP, CA, CP, TA, TP |
| SH-124 `generateUniqueSlug` | Public entity owner using shared text primitive | Proposed ruling | Proposed shared slug primitive with Taxonomy-local policy; D012. | TA |

### Registry-refresh flags (recorded, not adjudicated)

- **S01 — SH-121 final mutation:** registry says Taxonomy owns “final mutation”; R001/R003 and current flow text assign contextual assignment persistence to the classified entity owner. It may be stale or narrower wording about canonical terms; this handoff does not choose that interpretation. Preserve ID/name and raise the boundary wording in the Shared Operations refresh. CA §8 also retains contradictory unresolved-owner rows (I001).
- **S02 — SH-094 scope:** CA §11 includes “AI when classification snapshot variant is approved”; R015/R017, AA/AP and CP's integration map distinguish rich AI classification DTOs from SH-094's Search-safe projection. Do not infer an approved generic AI source API from the registry pattern. Record a possible local scope overstatement, not an automatic registry error.
- **S03 — SH-022 coverage:** registry language broadly includes location/license/sensitivity; R010/current Prisma represent a narrower usable fact set. This is a capability boundary versus approved/represented coverage gap, not permission for hardcoded triggers or automatic evidence that the registry is wrong.
- **S04 — SH-028 read/generation semantics:** registry describes returning approximate location; LOC specifies a producing/persisting command and recommends `getPublicLocationProjection` for reads, while CL-02 often says “consume SH-028.” Verify call direction, freshness and refresh recursion; do not rename the operation (D055).
- **S05 — SH-091 abbreviated neighbor inputs:** TRACK §25, MOD §25 and several consumer tables list subsets of the canonical seven required fields. They may be summaries rather than incompatible minima. Later contract review must confirm requester/action/idempotency fields and version meaning, including Track version versus source entity version. Do not silently infer omissions are errors or invent a composite version.
- **S06 — statuses and aliases:** SH-003/015/054/065/122/124 remain proposed. SH-015 is optional, SH-054 conditional, SH-122 disabled until merge policy, SH-124 optional. `recordSuggestionDisposition` is AI-owned local integration, not an alternate SH-121. `evaluateCandidateSearchBoost` is a typed SH-005 wrapper, not a competing resolver. `runSearchBackfill` is a restricted local command, not an SH-093 rename. “SH-095–098 privacy protocol” does not mandate all four operations for every owner or authorize Search field scrubbing without a map.
- **S07 — no missing IDs or proved wrong canonical name found:** all 67 IDs resolve; uses of abbreviated groups and descriptive local interfaces are retained as such. Module tables need not repeat every reference appearing elsewhere in their architecture/plan. No new SH operation is proposed by this file.
- **S08 — mechanisms without a registered CL-02-specific SH:** rate limiting, exact owner enumerators/AI DTOs, completion receipts and secret/config management are dependencies, not invented SH IDs. Notification's SH-042/043, Location's proposed SH-069, and related proposed SH-105 are mentioned only as neighboring context; they are not additional confirmed CL-02 operation dependencies or part of the 67 count.

## 5. Sequencing dependencies

These dependencies name the **minimum capability**, not a demand to finish the producer Cluster. Approved fakes can prove contracts where plans permit them; production needs the actual capability. No evidenced dependency requires `FULL_CLUSTER_MATURITY`. The Candidate/Organization slice must supply real privacy-safe projection and access decisions, not every hiring/interview feature.

| ID | Producer / minimum prerequisite | Classification | CL-02 consumer and gate | Evidence / limitation |
| --- | --- | --- | --- | --- |
| Q01 | CL-01 actor, service-actor and resource/action interfaces | CONTRACT_ONLY | protected Module contract work | CP/TP/AP/SP preconditions; no local authentication substitute |
| Q02 | CL-01 working authentication/authorization and designated step-up | FOUNDATION_CAPABILITY | production admin, AI/review/backfill and protected Search | SH-001/002/014; D044/056 |
| Q03 | CL-09 Audit/Ops interfaces and safe payload contracts | CONTRACT_ONLY | early slices/worker tests | CP prerequisites; mandatory audit-failure policy D056 |
| Q04 | working Audit/Ops and platform idempotency, outbox/inbox, queue, retry, locks | FOUNDATION_CAPABILITY | production mutations/provider workers | TP03/06; AP05; SP04/05; CP02 begins as a harness. Do not assign all platform infrastructure to CL-09. |
| Q05 | independently verified database/migration baseline and approved owner physical schemas | FOUNDATION_CAPABILITY | CP01/02/04 and schema exit gates | D004/017/053; schema presence is not deployment proof |
| Q06 | CL-03/04/06 target validity and contextual assignment interfaces | CONTRACT_ONLY | CP07/08; TP07/08 | SH-123 plus SH-023; applicable metadata decisions first |
| Q07 | working contextual-owner assignment command for each enabled target | FOUNDATION_CAPABILITY | real manual/AI acceptance | mutation precedes AI accepted disposition; no foreign repository workaround |
| Q08 | CL-03 Professional/Offering safe AI input and target validation | CONTRACT_ONLY | AP08 mapped to CP09; enabled target CP06/AP11 backfill | distinct from SH-094; D015 |
| Q09 | CL-06 Organization/Job safe AI input and target validation | CONTRACT_ONLY | AP09 mapped to CP09 | no requirement for complete hiring UI/interviews |
| Q10 | CL-06 Candidate AI fields and purpose/privacy/retention permission | CONTRACT_ONLY | AP10 mapped to CP10 | D015/028/030; Search-safe data is not automatically AI-safe input |
| Q11 | working source adapter plus AI persistence, structured output and approved provider capability per target | FOUNDATION_CAPABILITY | that target's CP06/AP11 backfill | R013; one enabled target does not prove generalized multi-target completion |
| Q12 | CL-03/04/06 safe projection, readiness, currentness and bounded enumeration | CONTRACT_ONLY | CP09/SP02/08 and CP12 reconciliation | SH-024/094; D014/016; no global batch repository |
| Q13 | working public source/readiness and applicable Trust/Healthcare/Job decisions | FOUNDATION_CAPABILITY | production CP09 selected public targets | underlying producer capability may remain a limited approved slice |
| Q14 | Candidate privacy/projection, Organization/requester authority, applicable entitlement/readiness/Hold/Moderation interfaces | CONTRACT_ONLY | CP09 → CP11 prerequisite contracts → CP10; SP09 tests before SP10 | R014; D021–025 |
| Q15 | working CL-06/01/09 protected Candidate gates for enabled surface | FOUNDATION_CAPABILITY | protected Candidate production exit | org commercial ownership remains gated if plans are required; not full CL-06 maturity |
| Q16 | CL-08 safe location interface and freshness/production policy | CONTRACT_ONLY | Search location mapping/filter contract | SH-028 versus safe projection read; D055 |
| Q17 | working safe fuzzy location for targets requiring it | FOUNDATION_CAPABILITY | production affected projections | no exact-coordinate fallback |
| Q18 | CL-08 enumeration/execution/retention/export/completion protocol | CONTRACT_ONLY | CP11/13; TP12/AP12/SP09/12; design before affected data use | D026/028/054; queue acknowledgement is not completed deletion |
| Q19 | working Privacy orchestration, owner executors and applicable provider deletion proof | FOUNDATION_CAPABILITY | production privacy completion/sensitive AI use | target-specific legal/provider policy, not blanket erasure claims |
| Q20 | CL-09 authorized Moderation effects/current restriction and action-specific Holds | CONTRACT_ONLY | CP11 prerequisite slice before CP10 | SH-103/011; effect/result representation D054 |
| Q21 | working enforcement for enabled discovery surfaces | FOUNDATION_CAPABILITY | production visibility/restoration | restore reevaluates current source/readiness/Privacy |
| Q22 | contextual-owner affected-ID enumerators and approved events if asynchronous | CONTRACT_ONLY | CP12/TP09 fanout; conditional TP11 merge | R007; D014/033; no foreign join scan |
| Q23 | approved provider/secret/config and validation/hash/minimization mechanisms | FOUNDATION_CAPABILITY | Typesense CP03 and Bedrock CP05 production | fakes allowed earlier; D029/032/056 and local physical design gates |
| Q24 | CL-07 Notification trigger/recipient/template contract, only if adopted | CONTRACT_ONLY | no baseline CL-02 gate | D046; no full Messaging/Notification prerequisite |
| Q25 | CL-05 authorized media references/extracted input supplied through source owner | CONTRACT_ONLY | only DTOs containing those fields | B048; no direct CL-02 raw-file or signing capability |

Approved coordination: **CP01–09 → CP11 prerequisite-contract slice → CP10 → remaining CP11 reaction wiring → CP12–13**. SP03 establishes provider contract before SP05 production worker. Early fake-writer/taxonomy repair proof is not generalized reconciliation completion. AP08/09 map to CP09; AP10 maps to CP10. CP06 backfill is target-specific; Cluster completion does not imply TP10 internal normalization maintenance is complete.

**Stale sequence references:** AP preconditions still say Professional/Offering DTOs “until CL-03 Phase 5” and Organization/Job/Candidate DTOs “until CL-06 Phase 8.” Current CP03 Phase 5 is governance/privacy/enforcement; CP06 has only Phases 1–5 (Feature 08 is Candidate Search Projection). These references do not establish a valid capability-availability schedule. No replacement phase was decided here (I014).

## 6. Cross-cutting rail audit

`USED` includes documented indirect use, not proof of implementation. `NOT_USED` means no current dependency is established. `UNCLEAR` marks open policy/contract. No `SHOULD_USE_BUT_MISSING` finding is asserted merely because a Module table omits an operation documented elsewhere.

| Rail / check | Mark | Relationship, evidence and issue |
| --- | --- | --- |
| CL-01 authentication | USED | SH-001 protected/admin/trusted-system entry; separate anonymous public surface. CA §14; B001. |
| CL-01 authorization | USED | SH-002 with source/Organization relationship facts. CA §14; B002/003. Candidate composition RI02. |
| CL-01 actor/profile resolution | USED | User actor context; Professional/Candidate/Organization targets through owners/SH-123. No local profile resolver or inferred Customer commercial actor. CA §8/14; AA §13. |
| CL-01 consent | USED | Indirect upstream purpose/input policy. Consent proof alone permits neither transmission nor visibility. CA §15; AA §19; RI03. No additional direct consent SH is established. |
| CL-01 entitlement | USED | SH-005 boosts/protected features; no local premium flags. No current AI-plan gate. SA §13/35; AA §19; RI02. |
| CL-01 usage metering | UNCLEAR | SH-006 only after approved key/count point; candidate_search_boost_applied open. SP10; RI02. |
| CL-01 security / step-up | UNCLEAR | SH-014 mechanism known, action matrix open. AA U-AI-01; RI01. |
| CL-07 Thread / Messaging | NOT_USED | No current Thread, participation or Messaging command dependency. |
| CL-07 Notification requests | NOT_USED | No baseline notices; future SH-041 conditional. TA/AA/SA §26; D046. |
| CL-07 recipient resolution | NOT_USED | Future Notification retains routing/preferences; CL-02 supplies approved trigger facts only. |
| CL-07 delivery-trigger assumptions | NOT_USED | Search completion/AI failure does not automatically trigger email/SMS/push. Ops visibility is current path. |
| CL-08 personal-data ownership | USED | AI/source references and Search work/documents can identify subjects; contextual joins remain foreign-owned. TA/AA/SA §28. |
| CL-08 enumeration / execution | USED | SH-096/095 owner participation, no orchestration-table writes. B037–039; RI05 completion gap. |
| CL-08 retention | UNCLEAR | SH-097 facts and Privacy exemptions; AI/Search durations/minimum fields open. D026/028; RI04. |
| CL-08 export | USED | Safe owner serializers/inventory; Privacy bundle orchestration and Media file access. Exact field policy RI04. |
| CL-08 erasure / anonymization | USED | Owner executors/provider deletion; SH-098 only approved mappings, no generic Search map. RI04/05. |
| CL-08 exact / fuzzy location | USED | Owner-approved fuzzy public fields only. SH-028/read/freshness agreement RI06. |
| CL-08 location reveal | NOT_USED | No exact-location reveal through Search/AI; later context access separately authorized. CA §19; SA §25. |
| CL-09 ComplianceHold | USED | SH-011 action-specific stop signs; SH-012 only approved policy. No automatic low-confidence Hold. CA §15; AA §19. |
| CL-09 moderation enforcement | USED | SH-103/091; restoration rechecks eligibility. Exact ack/completion RI05. |
| CL-09 generic audit | USED | SH-029 material actions, not taxonomy/AI/Search lifecycle. Mandatory failure policy RI07. |
| CL-09 sensitive-access audit | UNCLEAR | SH-030 designated AI/Candidate/admin access; no per-hit public sensitive logging. Candidate action coverage RI07. |
| CL-09 observability | USED | SH-032–040 safe context, metrics and health; separate domain truth. Production availability RI08. |
| CL-09 operational failures | USED | IntegrationFailure/incidents; provider failure never changes source entity state. RI08. |
| CL-09 queue / worker visibility | USED | Shared retry/dead-letter/telemetry; Search/AI outcome remains owner-held. D017; RI08. |

### Rail issues for the platform audit (8 groups)

1. **RI01 — Step-up matrix:** CL-01 action-specific fresh-assurance requirements remain open (D044).
2. **RI02 — Protected/commercial/usage composition:** CL-01/06 Organization authority/commercial owner, Candidate privacy, boost key/value and count point need matched contracts (D021–024).
3. **RI03 — Sensitive AI permission:** source/consent/Healthcare/Privacy approval and provider purpose/fields must agree; consent proof alone is insufficient (D029–031).
4. **RI04 — Retention/export/field maps:** CL-08 and owners need exact inventory, durations, minimum provenance and allowed anonymization (D026/028/040).
5. **RI05 — Actual completion proof:** CL-08/09 cannot treat Search queue acceptance as completed deletion/enforcement (D054).
6. **RI06 — Fuzzy projection/freshness:** CL-08 production policy and producing-versus-reading interface need matching (D055).
7. **RI07 — Audit coverage/failure:** CL-09 Candidate query/detail sensitive-access scope and required audit failure policy remain open (D025/056).
8. **RI08 — Operational foundations:** documented shared queue/health/telemetry/idempotency are not proof of runtime availability; generic queue cannot replace Search currentness/outcome (D017/056).

## 7. Indirect coupling and residual reconciliation evidence

These **16 review items** include documentary disagreements, unresolved contracts, and important existing constraints. They are not sixteen newly adjudicated architecture conflicts. Application code was not audited for direct Prisma access; the concerns below concern documented boundaries and future implementation.

| ID | Coupling / observation | Evidence | Consequence for later review |
| --- | --- | --- | --- |
| I001 | CA §8 still labels six groups of contextual joins “Unresolved lifecycle owner,” while settled rulings/other current sections assign entity-owner lifecycle. | CA §8 lines 490–495 versus §1/26/27; TA §3/35; DR; R001 | Preserve the existing R001 decision; do not reopen ownership from this stale table. Mapping in section 8. |
| I002 | SH-121 “final mutation” wording versus contextual-owner assignment persistence. | SH-121; R001/R003; CA §10; AA recordSuggestionDisposition | Examine canonical-term versus contextual-mutation wording in registry refresh; no ruling made here. |
| I003 | Some AA proposal prose attributes accepted-change Search refresh only to Taxonomy; current command/AP flow says owner of changed accepted truth. | AA PR-AI-07/§14/25 versus §10; AP07; R001/R003 | Distinguish term change from foreign assignment; avoid duplicate triggers or AI-generation indexing. |
| I004 | Track evidence version differs from entity source version; neighboring SH-091 summaries omit some canonical fields. | TRACK §25; MOD §25; CA §10; SA §23; SH-091 | Verify full seven-field envelope/currentness; abbreviation alone is not a proven conflict. No guessed composite version. |
| I005 | Shared enums/statuses do not transfer policy: Candidate projection draft/active/hidden/erased/disabled; rawResumeTextIndexed=false; Search user/trust_badge enum entries; commented TagSource.candidate. | SC; SA §9/25/33; TA U-TAX-04 | Candidate owns transition, Trust owns verification, User indexing stays gated; Search consumes decisions. |
| I006 | AI models absent; Search Boolean lacks approved durable semantics; schema/migration coverage unverified. | SC; CM maturity; R008/R009/R011 | Shared database presence neither authorizes missing schema nor proves migration/deployment parity. |
| I007 | Source erasure, provider deletion and orchestrator completion are separate facts. | PRIV §17; SA §10/28; MOD §12; D054 | Need completion correlation/retry evidence; enqueue cannot complete Privacy; restoration cannot resurrect forbidden data. |
| I008 | SH-028 generates cache and refreshes Search, while Search describes consuming it. | LOC §10/21/22; SA §13; CA §13 | Match read versus generation/freshness to avoid refresh loops or exact-location fallback. |
| I009 | Required readiness reaction does not imply a persisted readiness-changed event. | CA §18; SA §25; PRO §12/PE-PR-08 | Professional explicitly assumes no ProfessionalReadinessChanged MVP event; requery on legitimate dependency signals. |
| I010 | Candidate files/parsing, healthcare input and media validity are upstream DTO dependencies; AI erasure differs from accepted assignment erasure. | CA §19/20; AA/SA §24/28; CAND §11 | No raw resume fetch/signing, global privacy crawler or foreign executor; Privacy/Media retain export artifact responsibility. |
| I011 | Provider logging/retention may create deletion obligations; callbacks are not currently required. | AA §20/U-AI-02; CA §17; SA §20 | Do not assume provider deletion support or create callback ledgers; future SH-059/060 stays owner-specific. |
| I012 | Shared locking/idempotency is not shared lifecycle ownership. Acceptance/ack, provider write/completion and Privacy/backfill races cross boundaries. | R003/R008; AA/SA/TA §23 | Preserve owner version/lock scope; retry missing ack without duplicate mutation; queue status is not domain outcome; no generic saga approved. |
| I013 | Backfill/readiness gates are target- and feature-specific. | CP06/10/11/12 and integration mapping; AP08–11; R012–R015 | Do not require whole producer Clusters or claim production completion using fakes; TP10 maintenance is separate. |
| I014 | Residual doc-availability and phase references: SA waits for present CL-02 artifacts; CM retains older maturity note; AP names nonexistent CL-06 Phase 8 and CL-03 Phase 5 now governance. | SA §35/37; CM maturity; AP preconditions; CP03/CP06 headings | Reference cleanup remains for later work; missing root plans cannot supply binding phases. |
| I015 | CA conditionally mentions AI variant of SH-094 while current CP/AA/AP distinguish rich AI source contracts. | CA §11; CP integration map; AA §13; R015/R017; SH-094 | Search DTO/minimal SH-003 facts do not authorize model input or replace target validity. |
| I016 | Proposal text remains normative-looking: TA §36 items 5–6 describe PR-TAX-02/03 behavior; AA examples use proposed AI states. | TA §9/36; TP lifecycle gate; R002; AA §8–10; R009 | Keep deletion/ancestry/status details unapproved; illustrative plan/test text cannot approve them. |

## 8. Known reconciliation history

These are the supplied adjudication's **prior decisions**, not new rulings. Earlier application work targeted context/registry/language material and preserved schema/code boundaries. Residual statements in section 7 mean this handoff does not certify that every current paragraph is reconciled.

| Prior finding | Decision to preserve | Remaining boundary/gate |
| --- | --- | --- |
| CL02-R001 | Classified entity owner owns contextual join create/update/delete/privacy; Taxonomy owns canonical vocabulary, validity, normalization, compatibility and triggers. | U-CL02-01/U-TAX-01 resolved; no Taxonomy foreign join repository. Public contracts/metadata remain prerequisites. |
| CL02-R002 | PR-TAX-02/03 remain proposals, never defaults merely because no alternative was selected. | U-CL02-07 remains open; dependent deletion/ancestry/history/merge/reparenting behavior gated. |
| CL02-R003 | SH-121 acceptance uses suggestion ID/version, target, selected canonical term, reviewer, reason, idempotency and audit. Taxonomy validates; contextual owner commits; AI records acceptance only after success. | Proposal-only rejection/expiry/cancel/supersession remains AI-owned. Lost ack retries without duplicate/reversed classification; exact AI states and transport open. |
| CL02-R004 | Initial acceptance uses existing canonical IDs only; reviewer approval alone cannot create/activate a term. | U-CL02-15 future controlled creation open; novel proposals review-only. |
| CL02-R005 | Taxonomy provides owner SH-024 readiness and SH-094 safe projection. | Search cannot infer readiness from isActive/hierarchy; effective-activity-dependent policy gated. |
| CL02-R006 | SH-091 requires all seven canonical minimum fields. | No persisted columns or physical Search work representation selected. |
| CL02-R007 | Each contextual owner enumerates its own affected entity IDs; Taxonomy identifies changed terms. | Owner contracts/cursors and events remain prerequisites; no Taxonomy/Search foreign-join scans. |
| CL02-R008 | Search owns durable refresh identity/context, currentness, idempotency, requester/action, claimability, completion, retry/operator failure and stale/superseded outcomes. | Queue owns delivery/attempt/backoff/dead-letter. Boolean insufficient; expand/replace physical representation and exact fields/enums unchosen. |
| CL02-R009 | AiClassificationLog/AiSuggestion are AI-owned source records, not Audit/Queue substitutes. | Exact AI schema/status/transitions unresolved; no current correction or schema choice approved for this finding. |
| CL02-R010 | Only approved represented trigger facts: Category verification/healthcare/sensitivity; Tag verification plus approved bindings. Language/compliance owns DataSensitivity meaning. | No guessed Tag healthcare/location lists; triggers do not satisfy readiness. Future coverage open. |
| CL02-R011 | Independently verify schema/migration parity before relevant exit claims. | No schema or ownership decision; document/model presence is not clean-migration proof. |
| CL02-R012 | CP02 fake-writer harness differs from production worker; early taxonomy repair is not generalized SH-093. | No change required; SP03 provider contract before SP05 worker preserved. |
| CL02-R013 | CP06 backfill activates per target after persistence/provider/output, owner DTO, safe-input policy, SH-123 and applicable AP prerequisites. | Broader backfill waits for mapped integrations; no false multi-target completion. |
| CL02-R014 | CP09 → CP11 prerequisite contracts → CP10 → remaining CP11 reactions → CP12–13. | Candidate privacy/projection, org authority, applicable entitlement/readiness/Hold/Moderation and SP09 tests precede protected Candidate exit; exact composition open. |
| CL02-R015 | AP08 Professional/Offering and AP09 Organization/Job map to CP09; AP10 Candidate maps to CP10. | AI inputs differ from Search projections; no duplicate Cluster feature for TP10 maintenance. |
| CL02-R016 | SH-015 stays proposed/optional; documented local decision DTO permitted pending adoption. | No mandatory platform DTO dependency or local promotion to confirmed architecture. |
| CL02-R017 | SH-123 validates targets; SH-003 minimum facts cannot substitute. Search supplies SH-097 facts; SH-098 needs approved field map. SH-061/115 identify existing adapter/projection mechanisms. | Canonical IDs/names and separate local policy retained; no registry change or generic anonymization approved. |
| CL02-R018–R019 | Use real artifact paths/current feature coordination; unavailable root plans supply no enforceable phases. | Residual current references recorded in I014, not silently corrected or treated as sequencing authority. |
| CL02-R020 | Preserve all remaining metadata, provider, lifecycle, privacy, event, Candidate access/commercial and future-scope questions. | This extraction resolves none. |

### Contextual ownership mapping from R001

| Contextual rows | Lifecycle/privacy owner | Cluster |
| --- | --- | --- |
| ProfessionalCategory, ProfessionalTag | professional_eligibility | CL-03 |
| OfferingTag | marketplace_supply | CL-03 |
| GigTag | gig_demand | CL-04 |
| OrganizationCategory, OrganizationTag, JobTag | organization_hiring | CL-06 |
| CandidateCategory, CandidateTag | candidate_application_resume_privacy | CL-06 |

Taxonomy owns TaxonomyDomain/TaxonomyCategory/TaxonomyTag and TagSource semantics. CandidateSearchProjection remains Candidate-owned; Search owns provider projection and Search work. AI owns proposal provenance; accepted classification is separate truth. TrustBadge is display evidence, not VerificationCheck truth. ProfessionalProfile is seller identity; Organization is hiring identity. User indexing remains disabled without an approved safe contract.

## 9. Handoff totals and extraction checks

- **56** unresolved/conditional decision and external-prerequisite groups (`D001`–`D056`); resolved ownership/choreography portions are not recounted as open decisions.
- **54** directed bridge records (`B001`–`B054`), including explicitly scoped platform/conditional relationships; complete contract profiles form part of each record. Provider-only paths and negative boundaries are separate.
- **26** event-boundary families (`E001`–`E026`), including proposed/unnamed/indirect candidates; **zero** end-to-end confirmed wire subscriptions certified by this extraction.
- **67** unique referenced Shared Operation inventory entries; six proposed, all current IDs valid. Includes explicitly local/platform/conditional scopes, not 67 active inter-Cluster APIs.
- **8** rail issue groups (`RI01`–`RI08`); no current Messaging dependency or mandatory end-user Notification flow established.
- **16** indirect coupling/residual-evidence items (`I001`–`I016`); these are review points, not all actual conflicts.

Validation: all 50 local evidence links resolve; inventory IDs are unique and counts match; all 67 inventory names match the current SH registry; tables, fences and trailing whitespace checks pass. The 13 core source-file hashes are unchanged from extraction. `git diff --check` is clean; the untracked handoff also produces no whitespace diagnostics when compared with an empty file. Application/database checks were not run for this documentation-only extraction.

Only this handoff is created by this task. No architecture, plan, registry, Shared Operation, schema, migration or application code is changed. No unresolved policy is decided and no commit is made. The platform-wide pass can use the evidence inventory to match owner contracts, event versions, completion semantics and recorded disagreements under authority by concern.

[CM]: <../../context-map.md>
[SH]: <../../shared/shared-operations.md>
[CR]: <../../../prisma/clusters.json>
[DR]: <../../../prisma/deep modules and schemas.json>
[SC]: <../../../prisma/schema.prisma>
[CA]: <../../clusters/discovery classification & taxonomy/discovery-classification-architecture.md>
[CP]: <../../clusters/discovery classification & taxonomy/discovery-classification-build-plan.md>
[TA]: <../../clusters/discovery classification & taxonomy/Taxonomy Classification Module/taxonomy-classification-module-architecture.md>
[TP]: <../../clusters/discovery classification & taxonomy/Taxonomy Classification Module/taxonomy-classification-module-implementation-plan.md>
[AA]: <../../clusters/discovery classification & taxonomy/AI Taxonomy module/ai-taxonomy-module-architecture.md>
[AP]: <../../clusters/discovery classification & taxonomy/AI Taxonomy module/ai-taxonomy-module-implementation-plan.md>
[SA]: <../../clusters/discovery classification & taxonomy/Search Public Visbility Module/search-public-visibility-module-architecture.md>
[SP]: <../../clusters/discovery classification & taxonomy/Search Public Visbility Module/search-public-visibility-module-implementation-plan.md>
[TRACK]: <../../clusters/identity, authority, & consent/Track Subscription & Entitlement Module/track-subscription-entitlement-module-architecture.md>
[CAND]: <../../clusters/Organization Hiring & Candidate Pipeline/Candidate Application & Resume Privacy Module/candidate-application-resume-privacy-module-architecture.md>
[ORG]: <../../clusters/Organization Hiring & Candidate Pipeline/Organization Hiring Module/organization-hiring-module-architecture.md>
[MARKET]: <../../clusters/professional supply & readiness/Marketplace Supply Module/marketplace-supply-module-architecture.md>
[PRO]: <../../clusters/professional supply & readiness/Professional Eligibility Module/professional-eligbility-module-architecture.md>
[GIG]: <../../clusters/customer demand, order, & resolution/gig demand module/gig-demand-module-architecture.md>
[TRUST]: <../../clusters/professional supply & readiness/Trust verification Screening Module/trust-verification-screening-module-architecture.md>
[PRIV]: <../../clusters/Privacy & Location Safety/Privacy Data Erasure Module/privacy-data-erasure-module-architecture.md>
[LOC]: <../../clusters/Privacy & Location Safety/Location Safety Module/location-safety-module-architecture.md>
[MOD]: <../../clusters/Moderation holds Audits and Ops/Content Moderation & Legal Notice Module/content-moderation-legal-notice-module-architecture.md>
[CP03]: <../../clusters/professional supply & readiness/professional-supply-readiness-build-plan.md>
[CP06]: <../../clusters/Organization Hiring & Candidate Pipeline/organization-hiring-candidate-pipeline-build-plan.md>
