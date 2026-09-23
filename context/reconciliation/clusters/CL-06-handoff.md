# CL-06 — Cross-Cluster Reconciliation Handoff

**Cluster:** Organization, Hiring, & Candidate Pipeline
**Extraction date:** 2026-09-20 (America/New_York)
**Repository HEAD observed:** `ff71d8c`
**Status:** Extraction and handoff only. No new architecture ruling, policy approval, schema change or implementation authorization.

In plain English: this file lists what the hiring area needs from other areas, what it gives them, and which questions still need an answer. A listed option is not a chosen answer.

## 1. Scope, evidence and counting rules

The four registry members are `organization_hiring`, `job_compliance`, `candidate_application_resume_privacy`, and `job_interview`. All ten expected architecture/plan artifacts exist. “Candidate” below means Candidate Application & Resume Privacy; “Interview” means Job Interview. CL-06 coordinates; Modules own their truth.

Authority follows the concern in [MAP], not modification dates or depth. The current SH registry is recorded as evidence of canonical identity/status, **not assumed infallible**: disagreements and stale approval labels are carried forward for the later platform/SH refresh. No disagreement is resolved here. Schema observations describe repository structure, not a deployed database.

This handoff combines this task's two reconciliation application passes and approved CL-06-R001–R021 rulings with the current source files. Eighteen neighboring Module architectures were inspected for relevant producer/consumer boundaries; their complete implementation plans and runtime code were not audited. “ALIGNED” means the cited boundary agrees at the stated abstraction, not that code exists, every policy is approved, or event subscriptions are implemented.

| Inventory | Count | Definition |
| --- | --- | --- |
| Open/deferred decision entries | 70 | Includes residual approved rulings, proposed policy, deferred representation, external prerequisites and implementation choices; not 70 new architecture conflicts. |
| Cross-Cluster bridges | 61 | Logical directional boundary records, grouped where several CL-06 Modules consume the same rail. Includes indirect and conditional dependencies. |
| Cross-boundary event/trigger candidates | 57 | 50 named outbound candidates plus 7 unnamed inbound trigger families. No unverified subscriber is presented as confirmed. |
| Event inventory including local context | 61 | Also records 4 explicitly intra-Cluster business events; these are excluded from the 57 boundary candidates. |
| Shared Operation inventory | 88 | 59 IDs explicitly referenced locally plus 29 inferred/counterpart/conditional IDs. Some are shared mechanisms rather than a named Cluster API; SH-021 is primarily intra-Cluster with conditional Search consumption. |
| Sequencing records | 23 | Contract/capability prerequisites; no blanket FULL_CLUSTER_MATURITY requirement inferred. |
| Rail issues | 11 | Gaps/status/policy issues, distinct from the 24 rail coverage checks. |
| Indirect coupling observations | 26 | Structural, policy, currentness, privacy and failure dependencies requiring platform awareness. |

Handoff IDs `CL-06-U###`, `B###`, `E###`, `S##`, `RI##` and `IC##` are local inventory labels, **not new architecture-decision IDs or SH IDs**. Original decision IDs remain in each entry. Counts are records, not expanded combinations of Modules or event consumers.

### Source index

Evidence shorthand in entries resolves through this index; section/feature labels identify the relevant passages.

| Key | Artifact |
| --- | --- |
| CA | [Cluster architecture](<../../clusters/Organization Hiring & Candidate Pipeline/organization-hiring-candidate-piepline-architecture.md>) |
| CP | [Cluster build plan](<../../clusters/Organization Hiring & Candidate Pipeline/organization-hiring-candidate-pipeline-build-plan.md>) |
| NA | [Candidate Application & Resume Privacy architecture](<../../clusters/Organization Hiring & Candidate Pipeline/Candidate Application & Resume Privacy Module/candidate-application-resume-privacy-module-architecture.md>) |
| NP | [Candidate implementation plan](<../../clusters/Organization Hiring & Candidate Pipeline/Candidate Application & Resume Privacy Module/candidate-application-resume-privacy-module-implementation-plan.md>) |
| JA | [Job Compliance architecture](<../../clusters/Organization Hiring & Candidate Pipeline/Job Compliance Module/job-compliance-module-architecture.md>) |
| JP | [Job Compliance implementation plan](<../../clusters/Organization Hiring & Candidate Pipeline/Job Compliance Module/job-compliance-module-implementation-plan.md>) |
| IA | [Job Interview architecture](<../../clusters/Organization Hiring & Candidate Pipeline/Job Interview Module/job-interview-module-architecture.md>) |
| IP | [Job Interview implementation plan](<../../clusters/Organization Hiring & Candidate Pipeline/Job Interview Module/job-interview-module-implementation-plan.md>) |
| OA | [Organization Hiring architecture](<../../clusters/Organization Hiring & Candidate Pipeline/Organization Hiring Module/organization-hiring-module-architecture.md>) |
| OP | [Organization Hiring implementation plan](<../../clusters/Organization Hiring & Candidate Pipeline/Organization Hiring Module/organization-hiring-module-implementation-plan.md>) |
| MAP | [Authority/context map](<../../context-map.md>) |
| SH | [Shared Operations registry](<../../shared/shared-operations.md>) |
| ID | [ID source](<../../clusters/identity, authority, & consent/Identity & Access module/identity-access-module-architecture.md>) |
| ROLE | [ROLE source](<../../clusters/identity, authority, & consent/Role & Authority Module/role-authority-module-architecture.md>) |
| CONSENT | [CONSENT source](<../../clusters/identity, authority, & consent/Consent & Disclosure Module/consent-disclosure-module-architecture.md>) |
| TRACK | [TRACK source](<../../clusters/identity, authority, & consent/Track Subscription & Entitlement Module/track-subscription-entitlement-module-architecture.md>) |
| TAX | [TAX source](<../../clusters/discovery classification & taxonomy/Taxonomy Classification Module/taxonomy-classification-module-architecture.md>) |
| SEARCH | [SEARCH source](<../../clusters/discovery classification & taxonomy/Search Public Visbility Module/search-public-visibility-module-architecture.md>) |
| TRUST | [TRUST source](<../../clusters/professional supply & readiness/Trust verification Screening Module/trust-verification-screening-module-architecture.md>) |
| MEDIA | [MEDIA source](<../../clusters/scheduling, media, & digital delivery/media-asset-module/media-asset-module-architecture.md>) |
| VIDEO | [VIDEO source](<../../clusters/scheduling, media, & digital delivery/video-session-module/video-session-module-architecture.md>) |
| CAL | [CAL source](<../../clusters/scheduling, media, & digital delivery/booking-calendar-module/booking-calendar-module-architecture.md>) |
| MSG | [MSG source](<../../clusters/Messaging Notification Rail/Messaging Module/messaging-module-architecture.md>) |
| NOTIFY | [NOTIFY source](<../../clusters/Messaging Notification Rail/Notification Module/notification-module-architecture.md>) |
| PRIV | [PRIV source](<../../clusters/Privacy & Location Safety/Privacy Data Erasure Module/privacy-data-erasure-module-architecture.md>) |
| LOC | [LOC source](<../../clusters/Privacy & Location Safety/Location Safety Module/location-safety-module-architecture.md>) |
| HOLD | [HOLD source](<../../clusters/Moderation holds Audits and Ops/Admin Review & Compliance Hold Module/admin-review-compliance-hold-module-architecture.md>) |
| AUDIT | [AUDIT source](<../../clusters/Moderation holds Audits and Ops/Audit Event Ledger Module/audit-event-ledger-module-architecture.md>) |
| OPS | [OPS source](<../../clusters/Moderation holds Audits and Ops/Observability Ops Module/observability-ops-module-architecture.md>) |
| MOD | [MOD source](<../../clusters/Moderation holds Audits and Ops/Content Moderation & Legal Notice Module/content-moderation-legal-notice-module-architecture.md>) |
| REG | [REG source](<../../../prisma/deep modules and schemas.json>) |
| CLREG | [CLREG source](<../../../prisma/clusters.json>) |
| SCHEMA | [SCHEMA source](<../../../prisma/schema.prisma>) |

The attached adjudication and previous completion reports are conversation evidence summarized in §9 so a future task does not need the whole conversation. Existing neighboring handoff files were not treated as architecture authority.


## 2. Unresolved, proposed and deferred decisions

Resolved owners/invariants are stated inside residual entries to prevent accidentally reopening them. “Options” repeats documented alternatives or explicitly records that no alternative is approved; it is not a recommendation. External prerequisite bundles do not imply that an entire producer Cluster must be built first.

### CL-06-U001 — U-CL06-01 / R001

- **Question:** Who owns Organization business/representative verification and its proof/provider contract?
- **Affected Modules:** Organization Hiring; possible Trust/Identity involvement not assigned.
- **Affected Clusters:** CL-06; CL-01/03 potential.
- **Evidence:** [CA] §26; [OA] §35; Deep Registry organization_hiring notes.
- **Current options:** No approved owner/model; registry mentions business identity/Checkr requirements, not an ownership ruling.
- **Why open:** Required MVP facts lack an approved lifecycle/schema/provider-neutral contract.
- **Blocks:** Verified Organization activation and restricted hiring.
- **Shared Operations impact:** SH-017/018 may be relevant; they do not assign this owner.

### CL-06-U002 — U-CL06-02 / R001

- **Question:** Which versioned evidence establishes employment permissible purpose/FCRA Organization certification?
- **Affected Modules:** Organization Hiring, Consent, Trust.
- **Affected Clusters:** CL-06/01/03.
- **Evidence:** [CA] §26; [OA] §35; [TRUST] consent/FCRA sections.
- **Current options:** Consent acceptance proof plus a separately defined Organization authorization lifecycle; exact record is not selected.
- **Why open:** ConsentLog alone does not prove the full Organization-specific purpose/authorization lifecycle; legal input remains necessary.
- **Blocks:** Workflows legally dependent on certification.
- **Shared Operations impact:** SH-007/008/009/010 indirect; no new SH approved.

### CL-06-U003 — U-CL06-03 / R001

- **Question:** Which Organization owner representation is canonical, and how do transfer/removal preserve it?
- **Affected Modules:** Organization Hiring, Role / Authority.
- **Affected Clusters:** CL-06/01.
- **Evidence:** [OA] §8/35; [CA] §26; schema Organization/OrganizationMember.
- **Current options:** ownerUserId versus owner membership; precedence and invariant not chosen.
- **Why open:** Both structures exist; foreign keys do not establish lifecycle authority.
- **Blocks:** Ownership transfer and owner-sensitive membership removal.
- **Shared Operations impact:** SH-002/003/051/052.

### CL-06-U004 — U-CL06-04 / R001; U-CL01-33

- **Question:** Who owns OrganizationFeatureAccess/ATS commercial access and how does it relate to Track?
- **Affected Modules:** Organization Hiring, Candidate, Track, Search.
- **Affected Clusters:** CL-06/01/02.
- **Evidence:** [CA] §26; [OA]/[NA] §35; [TRACK] §35; [SEARCH] §35; [SH] unresolved register.
- **Current options:** Separate Organization commercial model versus another AccountTrack; neither selected.
- **Why open:** Current Track supports customer/candidate/professional; registry does not settle Organization policy.
- **Blocks:** Monetized ATS/resume viewer/protected Candidate Search, not an invented gate for basic free MVP.
- **Shared Operations impact:** SH-005/006; no new organization operation.

### CL-06-U005 — U-CL06-05 / PR-JC-01 / R003

- **Question:** What is publication precedence across checks, disclosure, review, summary, Holds, warning and technical failure?
- **Affected Modules:** Job Compliance, Organization Hiring, Holds, Search.
- **Affected Clusters:** CL-06/09/02.
- **Evidence:** [JA] §35; [CA]/[OA] §26/35; [JP] production gates.
- **Current options:** PR-JC-01 proposes owner evidence plus separate Hold gate and an Organization summary mirror; mapping remains proposed.
- **Why open:** The five public response values are approved, but that does not approve the policy matrix.
- **Blocks:** Production Job publication and Search eligibility composition.
- **Shared Operations impact:** SH-021/011/015; SH-015 remains Proposed ruling. SH-F02 records the registry's pass/warning/block/review shorthand against the approved five-value Module response; no mapping is inferred.

### CL-06-U006 — U-CL06-06 / residual R007 / PR-JC-02

- **Question:** How is mandatory immutable input/full applied-rule proof persisted and retained?
- **Affected Modules:** Job Compliance, Organization Hiring, Privacy.
- **Affected Clusters:** CL-06/08; platform persistence.
- **Evidence:** [JA] §8.6/35; [JP] Feature 02; schema JobComplianceCheck/Finding.
- **Current options:** Immutable canonical snapshot or immutable reconstructible source-version reference, plus hash/full applied rule versions; exact storage/retention not selected.
- **Why open:** Proof invariant is binding, including zero-finding approvals; current schema is insufficient.
- **Blocks:** Production reproducibility and Feature 02 exit.
- **Shared Operations impact:** SH-072/077/080/097.

### CL-06-U007 — U-CL06-07 / PR-JC-03 / R003

- **Question:** Who structurally owns CompensationPeriod, and what does EmploymentType.contract mean?
- **Affected Modules:** Organization Hiring, Job Compliance, terminology/legal owners.
- **Affected Clusters:** CL-06; platform vocabulary.
- **Evidence:** [JA] §35; [CA]/[OA] §26/35; Deep Registry; schema enums.
- **Current options:** PR-JC-03 proposes Organization ownership; contract could mean fixed-term employee or independent contractor.
- **Why open:** Registry currently assigns CompensationPeriod to Compliance; approved semantics are absent.
- **Blocks:** Final employment and compensation-compliance interpretation.
- **Shared Operations impact:** SH-021 consumes semantics; no new enum/SH chosen.

### CL-06-U008 — U-CL06-08 / R011; CL02-R001 cross-Cluster discrepancy

- **Question:** Who executes contextual taxonomy join writes, and has CL-06 adopted the CL-02 ruling?
- **Affected Modules:** Organization Hiring, Candidate, Taxonomy.
- **Affected Clusters:** CL-06/02.
- **Evidence:** [CA]/[OA]/[NA] unresolved sections; [TAX] §3/8/35; Deep Registry JobTag.
- **Current options:** CL-06 still leaves Taxonomy-versus-entity writer open; TAX says CL02-R001 approves entity owners for create/update/delete/privacy.
- **Why open:** Current artifacts differ in approval status; this extraction does not propagate the neighboring ruling.
- **Blocks:** Join repositories, attach/detach and privacy execution ownership alignment.
- **Shared Operations impact:** SH-023/090 not interchangeable; SH-095/096.

### CL-06-U009 — U-CL06-09 / residual R010

- **Question:** Remove, deprecate or retain non-authoritative resume/verification/logo fields?
- **Affected Modules:** Candidate, Organization Hiring, Media, Trust.
- **Affected Clusters:** CL-06/05/03.
- **Evidence:** [CA] §26; [OA]/[NA] §35; [NP] Feature 02; schema CandidateProfile/Organization.
- **Current options:** Remove; deprecate; retain as non-authoritative projection/cache.
- **Why open:** Non-authority is resolved; physical cleanup and compatibility are deferred.
- **Blocks:** Field cleanup/migration and legacy read-path rollout, not ownership.
- **Shared Operations impact:** SH-090/087/018; no cache may authorize verified workflows.

### CL-06-U010 — U-CL06-10 / residual R010

- **Question:** Which Candidate visibility state and participation/consent control Search?
- **Affected Modules:** Candidate, Search, Consent, Privacy.
- **Affected Clusters:** CL-06/02/01/08.
- **Evidence:** [NA] §9/25/35; [CA] §26; [NP] Feature 09.
- **Current options:** isVisible versus projection status precedence; explicit participation/consent requirement not decided.
- **Why open:** Multiple visibility inputs exist without approved precedence.
- **Blocks:** Candidate Search activation and privacy-safe rebuilds.
- **Shared Operations impact:** SH-094/091; consent SH-007/008 conditional.

### CL-06-U011 — U-CL06-11 / residual R010

- **Question:** What application status/stage graph, timestamps, reopen rules and history ledger are required?
- **Affected Modules:** Candidate, Organization Hiring, Interview.
- **Affected Clusters:** CL-06; CL-07/09 downstream.
- **Evidence:** [NA] §9/21/35; [NP] Features 05–07/10.
- **Current options:** Creation submitted/new_ is confirmed; full graph and JobApplicationEvent ledger versus existing proof remain open.
- **Why open:** Enums and outbox do not establish transitions or sufficient domain history.
- **Blocks:** Full recruiter pipeline, withdrawal subset, application/interview synchronization.
- **Shared Operations impact:** SH-053/052/031/046.

### CL-06-U012 — U-CL06-12 / residual R010

- **Question:** What qualifies as a view, and how do events update first-view/status summaries?
- **Affected Modules:** Candidate, Organization Hiring, Track, Audit.
- **Affected Clusters:** CL-06/01/09.
- **Evidence:** [NA] §9/27/35; [CP] Feature 06; [NP] Feature 07.
- **Current options:** Proposed append-only event per qualifying view, first-view viewedAt and status=viewed; not yet binding.
- **Why open:** Candidate ownership is confirmed; event qualification/summary semantics are not.
- **Blocks:** View tracking and entitlement-gated insights.
- **Shared Operations impact:** SH-125/030/076/005.

### CL-06-U013 — U-CL06-13 / residual R010

- **Question:** Does ResumeAccessLog prove issuance, actual read or both; how is raw parsed text encrypted/retained?
- **Affected Modules:** Candidate, Media, Audit, Privacy.
- **Affected Clusters:** CL-06/05/09/08.
- **Evidence:** [NA] §24/27/28/35; [NP] Features 04/08/11.
- **Current options:** Issuance versus read versus distinct evidence; text retention/encryption schedule unspecified.
- **Why open:** Separate Candidate/Media/Audit evidence exists but semantic correlation and legal duration remain open.
- **Blocks:** Compliance-grade resume evidence and production extractedText retention.
- **Shared Operations impact:** SH-125/030/087/088/097; SH-075 conditional.

### CL-06-U014 — U-CL06-14 / U-JI-01 / residual R012

- **Question:** How are participants removed/revoked, roles authorized, and candidate participation represented?
- **Affected Modules:** Interview, Organization Hiring, Candidate, Role, Messaging, Video.
- **Affected Clusters:** CL-06/01/07/05.
- **Evidence:** [IA] §8.3/9.3/35; [IP] Feature 04; [CA] §26.
- **Current options:** Delete versus revoke/cancel/separate history; required candidate row; non-member interviewer/coordinator/observer eligibility.
- **Why open:** Interview owns row/enums already; remaining behavior is not approved.
- **Blocks:** Participant mutations and downstream access revocation.
- **Shared Operations impact:** SH-002/003/113/068.

### CL-06-U015 — U-CL06-15 / U-JI-02 / residual R012

- **Question:** What Interview transition and reschedule topology/cardinality is legal?
- **Affected Modules:** Interview, Candidate, Calendar, Video, Messaging.
- **Affected Clusters:** CL-06/05/07.
- **Evidence:** [IA] §9/23/35; [IP] Feature 05; schema JobInterview self-relation.
- **Current options:** Mutate existing versus successor; proposed one effective active successor; reopen and draft-to-scheduled rules open.
- **Why open:** Proposed graph is non-binding; current schema permits multiple successors.
- **Blocks:** Advanced scheduling/rescheduling and downstream resource transfer.
- **Shared Operations impact:** SH-053/051/052/067/068.

### CL-06-U016 — U-CL06-16 / U-JI-03 / residual R013

- **Question:** What do Interview-local external event/provider/sync/error fields mean?
- **Affected Modules:** Interview, Booking & Calendar.
- **Affected Clusters:** CL-06/05.
- **Evidence:** [IA] §8/20/35; [IP] Feature 07; schema JobInterview.
- **Current options:** Approved local attachment/sync representation versus later relocation/deprecation; exact meaning undecided.
- **Why open:** Booking & Calendar provider ownership is resolved; local schema meaning is separate.
- **Blocks:** Production use of those fields/calendar persistence.
- **Shared Operations impact:** SH-067 confirmed; never reopen provider owner by implication.

### CL-06-U017 — R009

- **Question:** What project-level migration strategy reconciles schema with migration history?
- **Affected Modules:** All CL-06 owners; platform database authority.
- **Affected Clusters:** Platform-wide.
- **Evidence:** Thread R009; [CA] retired U-17 note; [MAP] schema/migrations; sole migration.
- **Current options:** Forward reconciliation, baseline/squash, reset or another explicitly approved strategy.
- **Why open:** Repository schema is not evidence of deployed state or migration approval.
- **Blocks:** Reliable migration rehearsal and production database rollout.
- **Shared Operations impact:** No operation directly; persistence prerequisites affect many SHs.

### CL-06-U018 — R008 deferred schema work

- **Question:** How/when is the extra Organization/view-event many-to-many relation removed or separately justified?
- **Affected Modules:** Candidate, Organization Hiring.
- **Affected Clusters:** CL-06.
- **Evidence:** [CA] §8; [NA] §8; schema JobApplicationViewEvent/Organization.
- **Current options:** Later removal unless distinct evidence establishes a different relationship.
- **Why open:** At-most-one Organization context is binding; physical correction was excluded from reconciliation edits.
- **Blocks:** Approved schema cleanup; current extra relation cannot supply truth.
- **Shared Operations impact:** SH-125/096 affected context; no new SH.

### CL-06-U019 — Residual R005

- **Question:** Which authoritative source fields supply all required compliance facts, including benefits/compensation?
- **Affected Modules:** Organization Hiring, Job Compliance.
- **Affected Clusters:** CL-06.
- **Evidence:** [OA] §11; [JA] §8/13; [OP] Feature 03; [CP] Features 01–02.
- **Current options:** Use actual Organization-owned fields; missing mappings remain unselected.
- **Why open:** Disclosure evidence cannot originate missing business facts.
- **Blocks:** Evaluation of rules requiring absent facts.
- **Shared Operations impact:** SH-021/077; owner-specific contracts do not approve SH-003.

### CL-06-U020 — OA additional Module decision

- **Question:** Are dedicated OrganizationEvent/JobEvent ledgers necessary?
- **Affected Modules:** Organization Hiring, Audit.
- **Affected Clusters:** CL-06/09.
- **Evidence:** [OA] §35; [OP] hardening/history.
- **Current options:** Existing outbox+generic audit versus separately approved owner ledger.
- **Why open:** Current architecture does not require new tables; history/replay requirements could.
- **Blocks:** Any implementation claiming stronger domain history than existing proof.
- **Shared Operations impact:** SH-031/046/029.

### CL-06-U021 — OA §9/22 local policy gaps

- **Question:** What are Job reopen, material-edit invalidation and closesAt rules?
- **Affected Modules:** Organization Hiring, Job Compliance, Search.
- **Affected Clusters:** CL-06/02.
- **Evidence:** [OA] §9/22; [OP] Features 05–06.
- **Current options:** Explicit reopen policy; final materiality policy; approved deadline eligibility; no complete alternatives approved.
- **Why open:** Existing commands are approved but these edge policies must be explicit.
- **Blocks:** Reopen, automatic deadline closure, safe approval invalidation.
- **Shared Operations impact:** SH-053/055/091/021.

### CL-06-U022 — NA §9 proposed CandidateProfile graph

- **Question:** Is the conservative profile graph approved, including archive restoration and suspension recovery?
- **Affected Modules:** Candidate, Trust, Holds.
- **Affected Clusters:** CL-06/03/09.
- **Evidence:** [NA] §9/36; [NP] Feature 02.
- **Current options:** Documented conservative draft/active/paused/suspended/archived graph; no approved restoration path.
- **Why open:** Shared enum is not the candidate-specific transition policy.
- **Blocks:** Profile transition subset beyond confirmed behavior.
- **Shared Operations impact:** SH-053/011/018.

### CL-06-U023 — NA §9 proposed CandidateSearchProjection lifecycle

- **Question:** What projection activation/hide/disable/erase transitions are approved?
- **Affected Modules:** Candidate, Search, Privacy.
- **Affected Clusters:** CL-06/02/08.
- **Evidence:** [NA] §9/36; [NP] Feature 09.
- **Current options:** Proposed draft→active after consent/privacy ruling; hidden/disabled; terminal erased.
- **Why open:** Lifecycle proposal depends on unresolved visibility policy.
- **Blocks:** Projection activation and privacy transition behavior.
- **Shared Operations impact:** SH-094/091/095.

### CL-06-U024 — U-CARP-01

- **Question:** Is there one current CandidateSearchProjection or a version/history model?
- **Affected Modules:** Candidate, Search.
- **Affected Clusters:** CL-06/02.
- **Evidence:** [NA] §8/35; schema CandidateSearchProjection.
- **Current options:** One row; immutable history; active row plus superseded history.
- **Why open:** candidateProfileId is indexed, not unique; no selection/currentness policy.
- **Blocks:** Uniqueness migration and unambiguous Search source.
- **Shared Operations impact:** SH-094/091/052.

### CL-06-U025 — U-CARP-02

- **Question:** Where does parse retry/attempt evidence live and may failed rows be reused?
- **Affected Modules:** Candidate, Ops/platform queue.
- **Affected Clusters:** CL-06/09; platform.
- **Evidence:** [NA] §9/23/35; [NP] Features 03–04.
- **Current options:** Shared Queue/Ops history versus owner proof ledger; retry same row versus approved attempt representation.
- **Why open:** One parse result per application/media pair lacks attempt ledger.
- **Blocks:** Retry implementation and claims of parse provenance.
- **Shared Operations impact:** SH-047/048/044/125 not a generic attempt owner.

### CL-06-U026 — U-CARP-03

- **Question:** What are controlled CandidateProfileMedia/JobApplicationMedia role values?
- **Affected Modules:** Candidate, Media.
- **Affected Clusters:** CL-06/05.
- **Evidence:** [NA] §35; [NP] Features 02–03; schema role strings.
- **Current options:** Approved local role vocabulary versus approved external context+DTO mapping.
- **Why open:** Free strings do not define a stable API vocabulary.
- **Blocks:** Production attach/parse APIs exposing roles.
- **Shared Operations impact:** SH-090/082.

### CL-06-U027 — NA §23 proposed application/Track protocol

- **Question:** How are application creation and quota consumption race-safe across owners?
- **Affected Modules:** Candidate, Track, platform persistence.
- **Affected Clusters:** CL-06/01.
- **Evidence:** [NA] §23; [NP] Feature 05; [CP] Feature 05.
- **Current options:** Approved shared transaction through owner participation versus explicit saga/reconciliation; shared semantic request identity.
- **Why open:** No root transaction protocol is approved; never pre-count locally.
- **Blocks:** Exactly-once logical usage and duplicate-free application under partial failure.
- **Shared Operations impact:** SH-006/044/051/052.

### CL-06-U028 — Residual R020 — application token

- **Question:** What backs JobApplication concurrency and do child writes use parent tokens?
- **Affected Modules:** Candidate; Organization/Interview consumers.
- **Affected Clusters:** CL-06; platform.
- **Evidence:** [NA] §23; [NP] prerequisites; schema JobApplication.
- **Current options:** Owner-selected backing; no column/type chosen.
- **Why open:** No universal version/updatedAt exists on this aggregate.
- **Blocks:** Safe concurrent pipeline/withdraw/view mutations.
- **Shared Operations impact:** SH-052/051.

### CL-06-U029 — Residual R020 — Compliance token

- **Question:** What backs mutable finding/review concurrency and parent-child comparisons?
- **Affected Modules:** Job Compliance.
- **Affected Clusters:** CL-06; platform.
- **Evidence:** [JA] §23; [JP] prerequisites; schema JobComplianceFinding/Check.
- **Current options:** Owner-selected token/aggregate strategy; no column ordered.
- **Why open:** Finding/review structures differ and representation was deliberately deferred.
- **Blocks:** Stale review/override protection.
- **Shared Operations impact:** SH-052/051.

### CL-06-U030 — U-JI-08 / residual R020

- **Question:** What backs Interview and participant concurrency tokens?
- **Affected Modules:** Interview.
- **Affected Clusters:** CL-06; platform.
- **Evidence:** [IA] §23/35; [IP] Feature 02; schema JobInterview/Participant.
- **Current options:** Owner-selected backing including possible current updatedAt; parent-child choice unapproved.
- **Why open:** Opaque public contract is binding; storage selection is not.
- **Blocks:** Interview stale-write/participant races.
- **Shared Operations impact:** SH-052/051.

### CL-06-U031 — JA §35 finding-field duplication

- **Question:** Which finding fields are canonical?
- **Affected Modules:** Job Compliance, Privacy.
- **Affected Clusters:** CL-06/08.
- **Evidence:** [JA] §8/35; [JP] blockers; schema JobComplianceFinding.
- **Current options:** fieldName/sourceField; matchedText/matchedSnippetPreview; suggestedText/suggestedReplacement cleanup or distinct meaning.
- **Why open:** Both variants persist without final semantic ruling.
- **Blocks:** New code relying on both and safe exports/redaction.
- **Shared Operations impact:** SH-077/097/098.

### CL-06-U032 — JA §35 review history proof

- **Question:** Are Audit+outbox sufficient for immutable review/override evidence?
- **Affected Modules:** Job Compliance, Audit, Privacy.
- **Affected Clusters:** CL-06/09/08.
- **Evidence:** [JA] §35; [JP] blockers.
- **Current options:** Generic AuditEvent+outbox versus a dedicated immutable Compliance review/event record.
- **Why open:** Mutable review fields do not independently settle legal-grade history.
- **Blocks:** Review proof sufficiency.
- **Shared Operations impact:** SH-029/031/046/097.

### CL-06-U033 — JA §28/35 proposed retention/disposition

- **Question:** What retention schedule and redaction preserve Compliance proof?
- **Affected Modules:** Job Compliance, Privacy.
- **Affected Clusters:** CL-06/08.
- **Evidence:** [JA] §28/35; [JP] Feature 08.
- **Current options:** Proposed retain minimal rule/hash/context proof, scrub raw matches where lawful; exact duration/basis open.
- **Why open:** Legal schedule and immutable-proof/privacy reconciliation not supplied.
- **Blocks:** Destructive privacy and compliance-proof retention.
- **Shared Operations impact:** SH-095/097/098.

### CL-06-U034 — U-JI-04

- **Question:** What is externalMeetingUrl allowed to represent?
- **Affected Modules:** Interview, Video, Calendar.
- **Affected Clusters:** CL-06/05.
- **Evidence:** [IA] §35; [IP] Features 03/06/07.
- **Current options:** Organizer-supplied reference; temporary sensitive link; legacy field; permitted external-provider reference.
- **Why open:** Field presence does not approve reusable credentials.
- **Blocks:** Rendering/returning usable meeting URLs.
- **Shared Operations impact:** SH-068/067/030.

### CL-06-U035 — U-JI-05

- **Question:** How do application terminal changes affect interviews, and do interviews request stage advancement?
- **Affected Modules:** Interview, Candidate.
- **Affected Clusters:** CL-06; CL-05/07 effects.
- **Evidence:** [IA] §35; [IP] Feature 05; [NP] Feature 10.
- **Current options:** Owner-safe requests/events versus manual stage handling; exact withdrawal/reject/hire/close effects open.
- **Why open:** No shared lifecycle or cross-table writer is approved.
- **Blocks:** Full synchronization and provider/thread cleanup triggers.
- **Shared Operations impact:** SH-046/045/053.

### CL-06-U036 — U-JI-06

- **Question:** What Interview/participant/event retention overrides cascades?
- **Affected Modules:** Interview, Privacy, Audit.
- **Affected Clusters:** CL-06/08/09.
- **Evidence:** [IA] §28/35; [IP] Feature 08; schema cascading relations.
- **Current options:** Retain/anonymize/erase per approved legal basis; possible later cascade change.
- **Why open:** Cascade structure does not prove lawful evidence destruction.
- **Blocks:** Destructive privacy execution and parent deletion.
- **Shared Operations impact:** SH-095/096/097/098.

### CL-06-U037 — U-JI-07

- **Question:** Which Privacy target identifiers route Interview/participant/event work?
- **Affected Modules:** Interview, Privacy.
- **Affected Clusters:** CL-06/08.
- **Evidence:** [IA] §35; [IP] Feature 08; [PRIV] target protocol; schema DataErasureTargetType.
- **Current options:** Canonical typed targets or explicitly approved owner-qualified protocol; no ad hoc other mapping.
- **Why open:** Controlled schema lacks dedicated hiring variants; representation/routing remains open.
- **Blocks:** Durable privacy dispatch/replay for Interview data.
- **Shared Operations impact:** SH-095/096.

### CL-06-U038 — U-JI-09

- **Question:** Which interview.* names/schema versions become the approved event registry?
- **Affected Modules:** Interview and downstream consumers.
- **Affected Clusters:** CL-06/05/07/09.
- **Evidence:** [IA] §12/35; [IP] Feature 09; JobInterviewEvent.name.
- **Current options:** Proposed interview.* vocabulary; final approved registry not supplied.
- **Why open:** Free-text schema and preferred names are not bilateral consumer approval.
- **Blocks:** Frozen external event contracts.
- **Shared Operations impact:** SH-046/045/031.

### CL-06-U039 — U-JI-10

- **Question:** Do proposals expire automatically and how is no_response produced?
- **Affected Modules:** Interview, Notification/platform scheduler.
- **Affected Clusters:** CL-06/07; platform.
- **Evidence:** [IA] §22/35; [IP] Feature 02/04.
- **Current options:** Automatic deadline versus manual state; duration/representation unchosen.
- **Why open:** No expiration policy is approved.
- **Blocks:** Expiry/reminder worker and no_response transitions.
- **Shared Operations impact:** SH-055/047/041.

### CL-06-U040 — U-JI-11

- **Question:** How are sensitive meeting phone/location data revealed, retained and redacted?
- **Affected Modules:** Interview, Location Safety, Privacy, Notification, Calendar/Video.
- **Affected Clusters:** CL-06/08/07/05.
- **Evidence:** [IA] §35; [CP] Feature 11; [LOC] source applicability.
- **Current options:** Applicable Location Safety policy versus other explicit hiring treatment; exact fields/retention not selected.
- **Why open:** Hiring location target and precision policy not established.
- **Blocks:** Sensitive in-person/phone meeting output.
- **Shared Operations impact:** SH-027/028 conditional; SH-030/097.

### CL-06-U041 — R014 — SH-003

- **Question:** Is the shared owner-facts contract approved platform-wide?
- **Affected Modules:** All source owners, Role and CL-06 consumers.
- **Affected Clusters:** CL-06/01/02/03/05/07/08/09.
- **Evidence:** SH-003; all CL-06 [SH] governance sections.
- **Current options:** Approve/amend/reject shared shape; owner-specific DTOs can exist independently.
- **Why open:** Registry status remains Proposed ruling.
- **Blocks:** Cross-platform API/schema commitment, not local source-query definition.
- **Shared Operations impact:** SH-003 directly.

### CL-06-U042 — R014 — SH-015

- **Question:** Is the shared decision envelope approved platform-wide?
- **Affected Modules:** Decision-owning Modules.
- **Affected Clusters:** Platform-wide; CL-06 consumers.
- **Evidence:** SH-015; [CA] §10/11; [JA] §31.
- **Current options:** Separate SH approval/amendment; local five-outcome Compliance contract already approved.
- **Why open:** R004 did not approve SH-015.
- **Blocks:** Shared envelope commitment; local Compliance producer contract remains binding.
- **Shared Operations impact:** SH-015 directly.

### CL-06-U043 — R014 — SH-081

- **Question:** Who supplies the shared scanner mechanism and is its shared contract approved?
- **Affected Modules:** Job Compliance, possible Moderation/platform scanner owner.
- **Affected Clusters:** CL-06/09; owner not assigned.
- **Evidence:** SH-081; [JA] §6/15/20; [JP] scanner feature.
- **Current options:** Shared runtime after approval; owner-local mechanisms may meet local need without freezing the proposed shared API.
- **Why open:** Proposed ruling and unresolved neutral owner/policy boundary.
- **Blocks:** Shared scanner API/runtime commitment.
- **Shared Operations impact:** SH-081 directly.

### CL-06-U044 — R015 — SH-120

- **Question:** Who supplies normalized jurisdiction facts/evidence and what is its contract?
- **Affected Modules:** Job Compliance, Tax/payment, Location Safety.
- **Affected Clusters:** CL-06/03/08; neutral owner unresolved.
- **Evidence:** SH-120; [JA] §35; [JP] Feature 02; [CP] Feature 02.
- **Current options:** Owner/interface must be adjudicated; fixtures with explicitly normalized inputs only below production gate.
- **Why open:** Need is established, ownership/contract is not.
- **Blocks:** Jurisdiction-aware production Compliance; no local normalizer replacement.
- **Shared Operations impact:** SH-120 directly.

### CL-06-U045 — CL-09-R003 residual owner contract

- **Question:** Which Moderation effects/results are supported for Job/Organization?
- **Affected Modules:** Organization Hiring, Content Moderation.
- **Affected Clusters:** CL-06/09.
- **Evidence:** [OA] §10/13; [OP] Feature 06/integration; [MOD] owner executor section.
- **Current options:** Authorized supported effects; accepted/rejected/already-applied/retryable/terminal distinctions within SH-103 evidence; exact encoding open.
- **Why open:** Owner executor boundary is agreed, detailed effect mapping remains prerequisite.
- **Blocks:** Enabling each enforcement effect; acknowledgment is not completion.
- **Shared Operations impact:** SH-103/044/046.

### CL-06-U046 — Candidate moderation participation gap

- **Question:** Does Candidate expose the owner executor expected for candidate_profile moderation targets?
- **Affected Modules:** Candidate, Content Moderation, Holds.
- **Affected Clusters:** CL-06/09.
- **Evidence:** [MOD] target enum/provider table; [NA] §13/14/34; schema ModerationTargetType.
- **Current options:** No Candidate-specific effect contract confirmed in CL-06; investigate intended handler versus Hold-only paths.
- **Why open:** Neighbor advertises profile-owner handlers; CL-06 documents only Hiring's explicit SH-103 executor.
- **Blocks:** Any moderation effect needing Candidate-owned mutation.
- **Shared Operations impact:** SH-103 potential missing use; no handler invented.

### CL-06-U047 — CL-01 consent/security integration gaps

- **Question:** Which CL-06-specific consent proofs and sensitive actions require explicit checks?
- **Affected Modules:** Organization Hiring, Candidate, Interview, Consent, Identity, Role.
- **Affected Clusters:** CL-06/01; CL-03/05 indirect.
- **Evidence:** [CA] §14/15; [NA] §18/19; [IA] §18/19; [CONSENT]; [TRUST]/[CAL] consent boundaries.
- **Current options:** Screening consent through Trust; calendar consent through Calendar; Candidate discoverability/purpose and exact step-up actions remain conditional.
- **Why open:** No direct CL-06 consent API list or approved universal hiring step-up matrix.
- **Blocks:** Specific legally/sensitively gated flows, not every basic profile read.
- **Shared Operations impact:** SH-007/008/009/010/014 conditional.

### CL-06-U048 — Audit transaction/failure policy

- **Question:** Which audit failures block privileged writes or sensitive access, and what is atomic?
- **Affected Modules:** All CL-06 owners, Audit, Ops/platform.
- **Affected Clusters:** CL-06/09; platform.
- **Evidence:** [OA]/[NA]/[JA]/[IA] §13/27; [AUDIT] append/failure contracts.
- **Current options:** Owner write+durable audit intent/record under approved platform pattern; fail/ retry according to required evidence policy.
- **Why open:** Documents defer exact transaction/failure policy to missing root/security rules.
- **Blocks:** Claims of durable mandatory audit under outages.
- **Shared Operations impact:** SH-029/030/046/037.

### CL-06-U049 — U-CL01-29

- **Question:** What period, timezone and reversal policy governs application limits?
- **Affected Modules:** Candidate, Track.
- **Affected Clusters:** CL-06/01.
- **Evidence:** [TRACK] §35; [NA] §23; [NP] Features 05–06.
- **Current options:** Period bounds and withdrawal/refund/restore policy unselected.
- **Why open:** UsagePeriod enum alone is not product quota policy.
- **Blocks:** Production application quota and withdrawal usage behavior.
- **Shared Operations impact:** SH-005/006.

### CL-06-U050 — U-CL01-24/26/28 and U-TSE-03 dependency bundle

- **Question:** Which Track catalog/defaults/precedence/lifecycle/profile-binding rules support Candidate features?
- **Affected Modules:** Track, Candidate, Search.
- **Affected Clusters:** CL-01/06/02.
- **Evidence:** [TRACK] §35; [NP] Features 05/09.
- **Current options:** Free plan/grants; typed keys; grant precedence; approved subscription state/profile binding.
- **Why open:** Candidate plans assume effective entitlements but Track production policies remain gated.
- **Blocks:** Reliable quota, view insights and boosts; paid provider mechanics only if paid feature enabled.
- **Shared Operations impact:** SH-005/006; not FULL_CLUSTER_MATURITY.

### CL-06-U051 — U-TSE-04

- **Question:** What durable semantic idempotency backs TrackUsageEvent?
- **Affected Modules:** Track, Candidate.
- **Affected Clusters:** CL-01/06.
- **Evidence:** [TRACK] §35; [NA] §23; [NP] Feature 05.
- **Current options:** Owner-approved persistent replay key/representation; no new field chosen.
- **Why open:** Current usage event lacks settled persistent semantic key.
- **Blocks:** Exactly-once logical metering across retry and partial failure.
- **Shared Operations impact:** SH-006/044.

### CL-06-U052 — SEARCH §35 protected topology

- **Question:** How is protected Candidate Search isolated from anonymous Search?
- **Affected Modules:** Search, Candidate, Role, Track.
- **Affected Clusters:** CL-02/06/01.
- **Evidence:** [SEARCH] §18/35; [NA] §25; [CP] Feature 08.
- **Current options:** Collection/key separation and server mediation contract; exact topology open.
- **Why open:** Security boundary agreed; physical/query representation not final.
- **Blocks:** Protected candidate query activation.
- **Shared Operations impact:** SH-024/002/005/094.

### CL-06-U053 — SEARCH §35 source/currentness/work representation

- **Question:** How do owner source versions map to Search currentness and durable retry/rebuild work?
- **Affected Modules:** Search, Organization Hiring, Candidate.
- **Affected Clusters:** CL-02/06.
- **Evidence:** [SEARCH] §35; [NA] §23/25; [OA] §25.
- **Current options:** Opaque owner value plus currentness query versus other approved revision shape; Search work representation separately pending.
- **Why open:** Monotonicity and stale-removal protection need matching contracts; current schema does not settle work lifecycle.
- **Blocks:** Safe Search retries, reindex and privacy tombstones.
- **Shared Operations impact:** SH-091/092/093/094/052.

### CL-06-U054 — SEARCH §35 Candidate boost semantics

- **Question:** Which boost key/value is used and is application metered?
- **Affected Modules:** Track, Candidate, Search.
- **Affected Clusters:** CL-01/06/02.
- **Evidence:** [SEARCH] §35; [TRACK] §25; [NA] §25; [NP] Feature 09.
- **Current options:** Effective ranking metadata versus metered use; candidate_search_boost_applied timing unapproved.
- **Why open:** Commercial policy and Search effect must align without affecting eligibility.
- **Blocks:** Production boost behavior and usage accounting.
- **Shared Operations impact:** SH-005/006/091.

### CL-06-U055 — SEARCH §35 sensitive query logging

- **Question:** Must every protected Candidate query/result create sensitive-access proof?
- **Affected Modules:** Search, Candidate, Audit.
- **Affected Clusters:** CL-02/06/09.
- **Evidence:** [SEARCH] §27/35; [NA] §27.
- **Current options:** Every query/result versus selected detail/access operations per approved sensitivity policy.
- **Why open:** Resume proof does not independently settle Search access policy.
- **Blocks:** Protected Search audit coverage.
- **Shared Operations impact:** SH-030.

### CL-06-U056 — U-TAX-04 / join metadata meaning

- **Question:** What Candidate tag provenance/confidence values are valid?
- **Affected Modules:** Candidate, Taxonomy, Search.
- **Affected Clusters:** CL-06/02.
- **Evidence:** [TAX] §35; schema TagSource/CandidateTag; [NA] taxonomy sections.
- **Current options:** Use user, add candidate through approval, or another explicit actor rule; confidence meaning unresolved.
- **Why open:** TagSource.candidate is commented; join verified is not Trust truth.
- **Blocks:** Stable classification writes/projections and provenance.
- **Shared Operations impact:** SH-023/094; never SH-018 by inference.

### CL-06-U057 — Calendar bilateral contract coverage

- **Question:** Where is the hiring-capable SH-067 public port and its participant/connection contract?
- **Affected Modules:** Interview, Booking & Calendar.
- **Affected Clusters:** CL-06/05.
- **Evidence:** [IA] §13/20; [IP] Feature 07; [CAL] provider-facing interfaces.
- **Current options:** Provider-neutral hiring context under confirmed Calendar owner; exact bilateral API not fully shown.
- **Why open:** CL-06/SH cover hiring; CAL describes operations needed by Booking and explicitly names Booking event creation.
- **Blocks:** Contract freezing and production Interview calendar handoff.
- **Shared Operations impact:** SH-067/064/059–062; owner not reopened.

### CL-06-U058 — Video join timing/TTL dependency

- **Question:** What early-join and token expiry policy applies to Interview participants?
- **Affected Modules:** Interview, Video.
- **Affected Clusters:** CL-06/05.
- **Evidence:** [VIDEO] unresolved early-join/TTL question; [IA] §20; [IP] Feature 06.
- **Current options:** Bounded parent schedule context; exact early allowance/TTL still open.
- **Why open:** Video parent-facts boundary is confirmed; complete timing policy is not.
- **Blocks:** Production join credentials for interview roles.
- **Shared Operations impact:** SH-068/026/030.

### CL-06-U059 — Event contract finalization outside Interview

- **Question:** Which proposed/example event payload versions and consumers are frozen?
- **Affected Modules:** All CL-06 producers, Search/Notification/Media/Privacy/Trust/Track.
- **Affected Clusters:** CL-06/01/02/03/05/07/08/09.
- **Evidence:** [OA]/[NA]/[JA]/[IA] §12/21; all Module integration plans.
- **Current options:** Owner event facts versus explicit downstream commands; exact consumer subscriptions not universally enumerated.
- **Why open:** A local event list is not bilateral subscription evidence.
- **Blocks:** External consumer contract freeze and event-driven revocation/rebuild behavior.
- **Shared Operations impact:** SH-045/046/041/091.

### CL-06-U060 — Platform foundation representation/global sequence

- **Question:** Which approved root contracts locate shared persistence, queues, outbox, telemetry and global rollout?
- **Affected Modules:** All CL-06 owners; shared infrastructure.
- **Affected Clusters:** Platform-wide.
- **Evidence:** [MAP] missing root artifacts; [CP] prerequisites; all Module plans.
- **Current options:** Consume approved platform mechanisms; fixture contracts where allowed; no invented root phases.
- **Why open:** Root architecture/build plan/code standards absent at inspected inventory; no canonical infrastructure Cluster assignment.
- **Blocks:** Concrete shared implementation/transaction conventions; not a reason to build all Clusters first.
- **Shared Operations impact:** SH-031/044–055/072/076/077 and Ops rail.

### CL-06-U061 — Parser implementation selection

- **Question:** Which DOCX parser adapter and supported retry/upgrade policy are selected?
- **Affected Modules:** Candidate, Media/Ops.
- **Affected Clusters:** CL-06/05/09.
- **Evidence:** [NA] §20/22; [NP] Feature 04.
- **Current options:** PDF evidence names pdf-parse; DOCX library selected behind ResumeParserPort at implementation time.
- **Why open:** Implementation/provider detail deliberately deferred; parser is not decision authority.
- **Blocks:** DOCX execution and compatibility fixtures.
- **Shared Operations impact:** SH-047/048; no new parser SH.

### CL-06-U062 — Legal rule catalog and rescan policy

- **Question:** Which jurisdictions, legal sources, severity thresholds, input fields and rescan activation policy are approved?
- **Affected Modules:** Job Compliance, Organization Hiring, taxonomy/jurisdiction providers.
- **Affected Clusters:** CL-06/02; CL-03/08 normalization dependencies.
- **Evidence:** [JA] §8/9/20/22; [JP] Features 01–06; Deep Registry legal-gated checks.
- **Current options:** Versioned approved admin-managed rules; no automatic legal-feed poller confirmed.
- **Why open:** Libraries/registry examples are not legal authority; uncertain matches require approved review policy.
- **Blocks:** Production policy catalog, material edit and rule-change rescans.
- **Shared Operations impact:** SH-080/081/120/077/021.

### CL-06-U063 — R010/R012 deferred metadata

- **Question:** When are ownership inventories updated for view events and Interview participants?
- **Affected Modules:** Candidate, Interview, registry/glossary authority.
- **Affected Clusters:** CL-06; platform metadata.
- **Evidence:** Thread R010/R012; Deep Registry schemasOwnedResponsibleForOver; [IA] evidence notes.
- **Current options:** Later metadata pass; ownership itself already confirmed.
- **Why open:** Current Module Registry omits these confirmed owned records/enums; no registry edit authorized here.
- **Blocks:** Accurate platform ownership inventory, not a new owner decision.
- **Shared Operations impact:** SH-125/031 affected documentation only.

### CL-06-U064 — Organization/Job/Candidate retention and export mapping

- **Question:** What periods, field maps, export serializers and parent/child dispositions apply?
- **Affected Modules:** Organization Hiring, Candidate, Privacy, Media/Search.
- **Affected Clusters:** CL-06/08/05/02.
- **Evidence:** [CA] §20; [OA]/[NA] §28; [OP] Feature 08; [NP] Feature 11.
- **Current options:** Retain/anonymize/erase per owner facts and Privacy exemptions; exact legal field policy open.
- **Why open:** Raw text, hiring records, view/access proof and shared attachments have different obligations.
- **Blocks:** Production destructive privacy and complete exports.
- **Shared Operations impact:** SH-095/096/097/098/100 indirect.

### CL-06-U065 — JobMedia proposed contextual ownership

- **Question:** Is the proposed Organization Hiring JobMedia contextual responsibility formally approved/inventoried?
- **Affected Modules:** Organization Hiring, Media.
- **Affected Clusters:** CL-06/05.
- **Evidence:** [CA] §8/19; [OA] §3/8/24; [OP] Feature 04.
- **Current options:** Current text proposes Organization contextual meaning with Media asset mechanics; no competing owner selected.
- **Why open:** Both Cluster and Module still label JobMedia contextual ownership Proposed.
- **Blocks:** Any implementation relying on unapproved contextual join ownership.
- **Shared Operations impact:** SH-090.

### CL-06-U066 — Interview no-show detail representation

- **Question:** Where is absent-party detail recorded without sensitive free text?
- **Affected Modules:** Interview, Audit/Notification consumers.
- **Affected Clusters:** CL-06/09/07.
- **Evidence:** [IA] §10 markInterviewNoShow.
- **Current options:** Event metadata versus a future field through approval.
- **Why open:** Explicit Module question remains unruled.
- **Blocks:** Detailed no-show evidence/output beyond approved status.
- **Shared Operations impact:** SH-031/046/041.

### CL-06-U067 — Notification trigger/recipient product policy

- **Question:** Which hiring notices and participant changes require delivery and to whom?
- **Affected Modules:** CL-06 owners, Notification, Messaging.
- **Affected Clusters:** CL-06/07.
- **Evidence:** [NA] §26; [IA] §26; [OA] §26; [NOTIFY] recipient boundary.
- **Current options:** Owner-approved recipients/templates; completion/no-show and candidate view notices only if product/privacy/entitlement permits.
- **Why open:** Notification owns delivery, not hiring purpose; some notices and role effects remain conditional.
- **Blocks:** Enabling each conditional notice and participant-to-thread synchronization.
- **Shared Operations impact:** SH-041/043/113.

### CL-06-U068 — Hiring public/exact location applicability

- **Question:** Which Organization/Job/Candidate fields require Location Safety public precision or reveal?
- **Affected Modules:** Organization Hiring, Candidate, Interview, Location Safety, Search.
- **Affected Clusters:** CL-06/08/02.
- **Evidence:** [LOC] §14; [CA] §13/18; [IA] U-JI-11; [NA] projection field map.
- **Current options:** Location owner output for supported targets; no CL-06-local fuzzing; exact hiring mapping not established.
- **Why open:** Neighbor allows Hiring source applicability while CL-06 has no explicit SH-027/028 use.
- **Blocks:** Safe location projection/reveal for affected hiring surfaces.
- **Shared Operations impact:** SH-027/028 potential missing conditional use.

### CL-06-U069 — Generic review work claiming dependency

- **Question:** Is shared reviewer assignment/claim infrastructure needed by Job Compliance?
- **Affected Modules:** Job Compliance, Admin Review, Moderation/platform.
- **Affected Clusters:** CL-06/09.
- **Evidence:** [SH] unresolved generic manual-review infrastructure; [JA]/[JP] review feature.
- **Current options:** Owner-specific review workflow versus separately approved reusable claim/assignment machinery.
- **Why open:** Common need does not establish shared queue schema or owner.
- **Blocks:** Any implementation assuming a shared review case/claim table.
- **Shared Operations impact:** SH-054 candidate mechanism only; no new shared schema approved.

### CL-06-U070 — TRACK SH-119 future temporary grants

- **Question:** If temporary Candidate boosts are enabled, who owns the grant and its precedence?
- **Affected Modules:** Track, Candidate, future grant-source owner; reward/prize involvement not established by CL-06.
- **Affected Clusters:** CL-01/06/02; future source Cluster unassigned here.
- **Evidence:** [TRACK] SH-119 section; SH-119 owner/status; [SEARCH] boost semantics.
- **Current options:** Track-owned temporary entitlement or affected feature-owner participation per later ruling; no Candidate boolean
- **Why open:** The registry leaves ownership partly unresolved and marks Proposed ruling; current CL-06 does not establish a direct CL-10 bridge.
- **Blocks:** Future temporary boosts only; not basic application or the entire rewards Cluster.
- **Shared Operations impact:** SH-119 applyTemporaryFeatureGrant (Proposed ruling); SH-005/091.

## 3. Cross-Cluster bridge inventory

Producer/consumer denote the direction of the payload described: a query owner produces its result; a command caller produces its request. Return/acknowledgment paths are described in the expectation/failure fields or separately where their semantics matter. “Platform/shared” preserves an unassigned Cluster rather than treating Ops as the owner of all infrastructure.

- `ALIGNED`: cited parties agree on the stated ownership/contract boundary; residual details can still be gated.
- `QUESTIONABLE`: partial, one-sided, differently labeled, or insufficiently specified evidence.
- `UNRESOLVED`: an explicit owner/policy/contract prerequisite remains open.
- `CONFLICTING`: incompatible requirements for the same circumstances; no bridge is promoted to this status merely because approval labels differ.

### CL-06-B001 — SH-001 resolveAuthenticatedActor

- **Producer Cluster / Module:** CL-01 Identity & Access.
- **Consumer Cluster / Module:** CL-06 all four Modules.
- **Purpose and boundary type:** query; Shared Operation. Use source actor; never treat User as CandidateProfile, org permission or entitlement
- **Contract/event/SH name:** SH-001 resolveAuthenticatedActor.
- **Producer output:** Trusted User/system actor and session assurance.
- **Consumer expectation:** Use source actor; never treat User as CandidateProfile, org permission or entitlement.
- **Sequencing requirement:** Before every protected feature; FOUNDATION_CAPABILITY.
- **Failure behavior:** Auth/dependency failure denies protected action.
- **Privacy/sensitivity:** Only minimal actor/security facts.
- **Evidence files:** [CA] §14; all Module §13/18; [ID] public actor contract.
- **Current status:** `ALIGNED`.

### CL-06-B002 — Owner DTOs; getOrganizationHiringContext; SH-003 queryOwnerFacts (Proposed ruling)

- **Producer Cluster / Module:** CL-06 Organization/Candidate/Interview owners.
- **Consumer Cluster / Module:** CL-01 Role / Authority.
- **Purpose and boundary type:** query; Shared Operation. Role interprets permission without owning membership/participant records
- **Contract/event/SH name:** Owner DTOs; getOrganizationHiringContext; SH-003 queryOwnerFacts (Proposed ruling).
- **Producer output:** Membership, resource ownership, application/interview relationships.
- **Consumer expectation:** Role interprets permission without owning membership/participant records.
- **Sequencing requirement:** CONTRACT_ONLY before corresponding action; runtime owner query required.
- **Failure behavior:** Missing/stale/unauthorized facts fail closed.
- **Privacy/sensitivity:** No resumes, application answers or private meetings in permission facts.
- **Evidence files:** [OA]/[NA]/[IA] §12–14; [ROLE] §3/13/35 still marks ownership split proposed.
- **Current status:** `QUESTIONABLE`.

### CL-06-B003 — SH-002 authorizeResourceAction

- **Producer Cluster / Module:** CL-01 Role / Authority.
- **Consumer Cluster / Module:** CL-06 all four Modules.
- **Purpose and boundary type:** query; policy/guardrail; Shared Operation. Server and RLS parity; entitlement/consent/compliance remain separate
- **Contract/event/SH name:** SH-002 authorizeResourceAction.
- **Producer output:** Action-specific permission decision/reasons.
- **Consumer expectation:** Server and RLS parity; entitlement/consent/compliance remain separate.
- **Sequencing requirement:** FOUNDATION_CAPABILITY before mutations/private reads.
- **Failure behavior:** No local role-string fallback.
- **Privacy/sensitivity:** Resource-scoped minimum identifiers.
- **Evidence files:** [CA] §14; all Module §18; [ROLE] public authorization/owner adapters.
- **Current status:** `ALIGNED`.

### CL-06-B004 — SH-014 requireStepUpForSensitiveAction

- **Producer Cluster / Module:** CL-01 Identity & Access.
- **Consumer Cluster / Module:** CL-06 approved sensitive/admin actions.
- **Purpose and boundary type:** query; policy/guardrail; Shared Operation. Only designated actions demand step-up; not an invented universal hiring rule
- **Contract/event/SH name:** SH-014 requireStepUpForSensitiveAction.
- **Producer output:** Fresh assurance scoped to approved action/context.
- **Consumer expectation:** Only designated actions demand step-up; not an invented universal hiring rule.
- **Sequencing requirement:** CONTRACT_ONLY matrix first; FOUNDATION_CAPABILITY when action enabled.
- **Failure behavior:** Missing/expired assurance blocks designated action.
- **Privacy/sensitivity:** No raw credentials/security secrets.
- **Evidence files:** [CA] §14; [IA] §18; [ID] sensitive-action matrix.
- **Current status:** `UNRESOLVED`.

### CL-06-B005 — SH-008 queryConsentProof; SH-010 presentStandaloneConsent; proof creation/version SH-007/009

- **Producer Cluster / Module:** CL-01 Consent & Disclosure.
- **Consumer Cluster / Module:** CL-03 Trust → CL-06 Organization/Candidate (indirect).
- **Purpose and boundary type:** query; policy/guardrail. Trust owns screening gate; CL-06 consumes readiness, not provider/legal truth
- **Contract/event/SH name:** SH-008 queryConsentProof; SH-010 presentStandaloneConsent; proof creation/version SH-007/009.
- **Producer output:** Standalone, versioned screening proof.
- **Consumer expectation:** Trust owns screening gate; CL-06 consumes readiness, not provider/legal truth.
- **Sequencing requirement:** Before legally gated screening; FOUNDATION_CAPABILITY in provider owner.
- **Failure behavior:** No valid proof means no protected screening.
- **Privacy/sensitivity:** Proof refs only; no screening report in hiring events.
- **Evidence files:** [CA] U-01/02; [TRUST] consent/FCRA gates; [CONSENT] public proof contracts.
- **Current status:** `UNRESOLVED`.

### CL-06-B006 — SH-007/008 calendar access disclosure/proof

- **Producer Cluster / Module:** CL-01 Consent & Disclosure.
- **Consumer Cluster / Module:** CL-05 Booking & Calendar → CL-06 Interview (indirect).
- **Purpose and boundary type:** query; policy/guardrail. Interview receives authorized provider-owner context; never infer consent from provider ID
- **Contract/event/SH name:** SH-007/008 calendar access disclosure/proof.
- **Producer output:** Authorized calendar connection/proof.
- **Consumer expectation:** Interview receives authorized provider-owner context; never infer consent from provider ID.
- **Sequencing requirement:** Before live calendar connection/use; FOUNDATION_CAPABILITY.
- **Failure behavior:** Connection/proof unavailable degrades sync without inventing source state.
- **Privacy/sensitivity:** Minimize participant/calendar data.
- **Evidence files:** [IP] Feature 07; [CAL] §13 calendar consent.
- **Current status:** `ALIGNED`.

### CL-06-B007 — Candidate discoverability consent/preferences; no approved operation binding

- **Producer Cluster / Module:** CL-01 Consent / CL-08 Privacy policy (exact responsibility unresolved).
- **Consumer Cluster / Module:** CL-06 Candidate / CL-02 Search.
- **Purpose and boundary type:** policy/guardrail. Fail-closed Candidate visibility and no raw resume indexing
- **Contract/event/SH name:** Candidate discoverability consent/preferences; no approved operation binding.
- **Producer output:** Approved participation/visibility evidence.
- **Consumer expectation:** Fail-closed Candidate visibility and no raw resume indexing.
- **Sequencing requirement:** CONTRACT_ONLY policy before CP08/NP09.
- **Failure behavior:** Unknown participation prevents activation.
- **Privacy/sensitivity:** Candidate data is protected, not anonymous public Search.
- **Evidence files:** [CA] U-10; [NA] §25/35; [SEARCH] protected candidate gate.
- **Current status:** `UNRESOLVED`.

### CL-06-B008 — SH-005 resolveEntitlement; checkCandidateApplicationAllowance composition

- **Producer Cluster / Module:** CL-01 Track.
- **Consumer Cluster / Module:** CL-06 Candidate.
- **Purpose and boundary type:** query; Shared Operation. No local premium flags/counters; effective policy is Track-owned
- **Contract/event/SH name:** SH-005 resolveEntitlement; checkCandidateApplicationAllowance composition.
- **Producer output:** Typed application limit, view-insight/boost value and evidence.
- **Consumer expectation:** No local premium flags/counters; effective policy is Track-owned.
- **Sequencing requirement:** CP05/06/08; FOUNDATION_CAPABILITY for live gates; fixtures earlier.
- **Failure behavior:** Unavailability cannot bypass quota or paid gates.
- **Privacy/sensitivity:** Safe allowance/evidence, not subscription internals.
- **Evidence files:** [NA] §13/19; NP05/09; [TRACK] §35 catalog/precedence.
- **Current status:** `UNRESOLVED`.

### CL-06-B009 — SH-006 consumeMeteredEntitlement

- **Producer Cluster / Module:** CL-06 Candidate.
- **Consumer Cluster / Module:** CL-01 Track.
- **Purpose and boundary type:** command; Shared Operation; background workflow. One usage receipt/counter effect for one accepted business use; reconcile partial outcome
- **Contract/event/SH name:** SH-006 consumeMeteredEntitlement.
- **Producer output:** Logical qualifying application-use request with actor/quantity/idempotency.
- **Consumer expectation:** One usage receipt/counter effect for one accepted business use; reconcile partial outcome.
- **Sequencing requirement:** CP05/NP05; CONTRACT_ONLY atomic/saga protocol then FOUNDATION_CAPABILITY.
- **Failure behavior:** No duplicate usage/application; rollback/reconcile through owners.
- **Privacy/sensitivity:** Application IDs, no answers/resume content.
- **Evidence files:** [NA] §23; NP05; [TRACK] U-CL01-29/U-TSE-04.
- **Current status:** `UNRESOLVED`.

### CL-06-B010 — evaluateCandidateSearchBoost; SH-005; entitlement-change trigger (name unconfirmed)

- **Producer Cluster / Module:** CL-01 Track.
- **Consumer Cluster / Module:** CL-06 Candidate and CL-02 Search.
- **Purpose and boundary type:** event; query; projection. Rebuild eligible Candidate projection/ranking; boost never grants visibility
- **Contract/event/SH name:** evaluateCandidateSearchBoost; SH-005; entitlement-change trigger (name unconfirmed).
- **Producer output:** Effective boost/perk values and currentness.
- **Consumer expectation:** Rebuild eligible Candidate projection/ranking; boost never grants visibility.
- **Sequencing requirement:** CP08/NP09 and Search protected feature; CONTRACT_ONLY then FOUNDATION_CAPABILITY.
- **Failure behavior:** Stale/unknown grant cannot become persistent premium truth.
- **Privacy/sensitivity:** Bounded ranking metadata only.
- **Evidence files:** [NA] §22/25; [TRACK] §25; [SEARCH] §35 boost semantics.
- **Current status:** `UNRESOLVED`.

### CL-06-B011 — OrganizationFeatureAccess/ATS entitlement; no approved owner contract

- **Producer Cluster / Module:** CL-01 Track or separately adjudicated owner.
- **Consumer Cluster / Module:** CL-06 Organization/Candidate; CL-02 Search.
- **Purpose and boundary type:** policy/guardrail. No extra AccountTrack/premium boolean selected locally
- **Contract/event/SH name:** OrganizationFeatureAccess/ATS entitlement; no approved owner contract.
- **Producer output:** Organization feature decision if monetized.
- **Consumer expectation:** No extra AccountTrack/premium boolean selected locally.
- **Sequencing requirement:** Only monetized features; CONTRACT_ONLY owner/policy prerequisite.
- **Failure behavior:** Keep dependent commercial feature gated.
- **Privacy/sensitivity:** Organization commercial context only.
- **Evidence files:** [CA] U-04; [OA]/[NA] §35; [TRACK] U-CL01-33; [SEARCH] §35.
- **Current status:** `UNRESOLVED`.

### CL-06-B012 — SH-023 validateTaxonomyAssignment

- **Producer Cluster / Module:** CL-02 Taxonomy.
- **Consumer Cluster / Module:** CL-06 Organization/Candidate/Job Compliance.
- **Purpose and boundary type:** query; Shared Operation. Owner keeps business attachment meaning; no local tags/term copies
- **Contract/event/SH name:** SH-023 validateTaxonomyAssignment.
- **Producer output:** Canonical IDs, hierarchy/active-state validation and errors.
- **Consumer expectation:** Owner keeps business attachment meaning; no local tags/term copies.
- **Sequencing requirement:** CP01/02; CONTRACT_ONLY DTO then FOUNDATION_CAPABILITY before assignment.
- **Failure behavior:** Invalid/unavailable classification blocks dependent operation.
- **Privacy/sensitivity:** Taxonomy IDs rather than private text.
- **Evidence files:** [OA]/[JA] §13; [NA] taxonomy section; [TAX] public validation.
- **Current status:** `ALIGNED`.

### CL-06-B013 — SH-022 resolveTaxonomyRequirements

- **Producer Cluster / Module:** CL-02 Taxonomy.
- **Consumer Cluster / Module:** CL-06 Organization/Job Compliance; indirectly Candidate/Trust.
- **Purpose and boundary type:** query; Shared Operation. Compliance/Trust interpret their policies; no hardcoded category law
- **Contract/event/SH name:** SH-022 resolveTaxonomyRequirements.
- **Producer output:** Requirement triggers for approved classification/context.
- **Consumer expectation:** Compliance/Trust interpret their policies; no hardcoded category law.
- **Sequencing requirement:** CP01–03 and verified-only gates; FOUNDATION_CAPABILITY.
- **Failure behavior:** Missing applicable requirement facts produces unavailable/review.
- **Privacy/sensitivity:** Controlled classification and safe context.
- **Evidence files:** [OA]/[JA] §13; [TAX] requirements; [TRUST] applicability.
- **Current status:** `ALIGNED`.

### CL-06-B014 — Contextual join persistence/impact enumeration

- **Producer Cluster / Module:** CL-06 classified entity owners (per CL-02 ruling; CL-06 still open).
- **Consumer Cluster / Module:** CL-02 Taxonomy workflows and CL-08 Privacy.
- **Purpose and boundary type:** command; query; policy/guardrail. Taxonomy validates; Privacy routes to actual writer; CL-06 adoption unresolved
- **Contract/event/SH name:** Contextual join persistence/impact enumeration.
- **Producer output:** Accepted entity-owned Candidate/Organization/Job classifications and impacts.
- **Consumer expectation:** Taxonomy validates; Privacy routes to actual writer; CL-06 adoption unresolved.
- **Sequencing requirement:** CONTRACT_ONLY owner alignment before repository/migration work.
- **Failure behavior:** No duplicate writers or ad hoc foreign-join cleanup.
- **Privacy/sensitivity:** Candidate joins may identify a person.
- **Evidence files:** [CA] U-08; [NA]/[OA] §35; [TAX] CL02-R001; Deep Registry JobTag.
- **Current status:** `QUESTIONABLE`.

### CL-06-B015 — Classification/requirement-change trigger; exact subscribed names unconfirmed

- **Producer Cluster / Module:** CL-02 Taxonomy.
- **Consumer Cluster / Module:** CL-06 classification/compliance/projection owners.
- **Purpose and boundary type:** event; background workflow. Owner invalidates/re-evaluates affected facts and requests own Search refresh
- **Contract/event/SH name:** Classification/requirement-change trigger; exact subscribed names unconfirmed.
- **Producer output:** Changed canonical term/requirement refs/version.
- **Consumer expectation:** Owner invalidates/re-evaluates affected facts and requests own Search refresh.
- **Sequencing requirement:** CONTRACT_ONLY impact/currentness contract before enabling propagation.
- **Failure behavior:** Retry safely; no stale accepted requirement masquerading as current.
- **Privacy/sensitivity:** No foreign source payload replication.
- **Evidence files:** [TAX] consumers/impact workflows; [OA]/[JA] classification gates; [CA] source currentness.
- **Current status:** `QUESTIONABLE`.

### CL-06-B016 — SH-017 resolveVerificationRequirements; SH-018 evaluateVerificationReadiness

- **Producer Cluster / Module:** CL-03 Trust Verification.
- **Consumer Cluster / Module:** CL-06 Organization/Candidate.
- **Purpose and boundary type:** query; Shared Operation. Verified-only gates use Trust truth, never Candidate caches/TrustBadge alone
- **Contract/event/SH name:** SH-017 resolveVerificationRequirements; SH-018 evaluateVerificationReadiness.
- **Producer output:** Requirement/readiness decision and evidence refs.
- **Consumer expectation:** Verified-only gates use Trust truth, never Candidate caches/TrustBadge alone.
- **Sequencing requirement:** CP03/05; CONTRACT_ONLY then FOUNDATION_CAPABILITY for verified-only path.
- **Failure behavior:** Unavailable/blocked readiness fails closed; no automatic hiring decision.
- **Privacy/sensitivity:** No raw Checkr/provider/screening reports.
- **Evidence files:** [OA]/[NA] §13; [CA] §15; [TRUST] Hiring consumer boundary.
- **Current status:** `ALIGNED`.

### CL-06-B017 — Owner-specific candidate/Job/organization/request facts

- **Producer Cluster / Module:** CL-06 Organization/Candidate.
- **Consumer Cluster / Module:** CL-03 Trust Verification.
- **Purpose and boundary type:** query; policy/guardrail. Trust validates target/purpose without taking over Job/application lifecycle
- **Contract/event/SH name:** Owner-specific candidate/Job/organization/request facts.
- **Producer output:** Identity bindings, target and authorized workflow context.
- **Consumer expectation:** Trust validates target/purpose without taking over Job/application lifecycle.
- **Sequencing requirement:** Before hiring screening; CONTRACT_ONLY; unresolved Organization purpose remains gate.
- **Failure behavior:** Missing/invalid purpose blocks affected screening.
- **Privacy/sensitivity:** Minimized identity/relationship facts.
- **Evidence files:** [TRUST] inbound Hiring facts; [OA] U-01/02; [NA] non-ownership.
- **Current status:** `UNRESOLVED`.

### CL-06-B018 — Readiness/hold change facts; exact subscribed names not agreed

- **Producer Cluster / Module:** CL-03 Trust / CL-09 Holds.
- **Consumer Cluster / Module:** CL-06 Organization/Candidate; indirectly CL-02 Search.
- **Purpose and boundary type:** event; policy/guardrail; background workflow. Re-evaluate owner eligibility and public projection; no provider status write into Job
- **Contract/event/SH name:** Readiness/hold change facts; exact subscribed names not agreed.
- **Producer output:** Changed authoritative evidence/current state.
- **Consumer expectation:** Re-evaluate owner eligibility and public projection; no provider status write into Job.
- **Sequencing requirement:** CONTRACT_ONLY revocation/currentness contract before enabled gate.
- **Failure behavior:** Late/duplicate events re-read current owner facts; fail closed on mandatory unknowns.
- **Privacy/sensitivity:** Only target/reason/evidence references.
- **Evidence files:** [OA] §9/25; [NA] §9/25; [TRUST]/[HOLD] consumer boundaries.
- **Current status:** `QUESTIONABLE`.

### CL-06-B019 — buildOrganizationSourceProjection; buildJobSourceProjection; SH-094 buildSourceProjection

- **Producer Cluster / Module:** CL-06 Organization Hiring.
- **Consumer Cluster / Module:** CL-02 Search.
- **Purpose and boundary type:** projection; query; Shared Operation. Search does not query raw Org/Job repositories or recompute compliance
- **Contract/event/SH name:** buildOrganizationSourceProjection; buildJobSourceProjection; SH-094 buildSourceProjection.
- **Producer output:** Allowlisted source DTO, lifecycle/readiness and source revision.
- **Consumer expectation:** Search does not query raw Org/Job repositories or recompute compliance.
- **Sequencing requirement:** CP03/OP06; CONTRACT_ONLY schema/currentness then FOUNDATION_CAPABILITY indexing.
- **Failure behavior:** Denied/stale source excludes/removes document; Search outage leaves source commit truthful.
- **Privacy/sensitivity:** No memberships/applicant data; safe location/media derivatives.
- **Evidence files:** [OA] §11/25; [CA] §18; [SEARCH] source projection table.
- **Current status:** `ALIGNED`.

### CL-06-B020 — getCandidateSearchProjection; SH-094 buildSourceProjection

- **Producer Cluster / Module:** CL-06 Candidate.
- **Consumer Cluster / Module:** CL-02 Search.
- **Purpose and boundary type:** projection; query; Shared Operation. Protected index only; no raw resume/answers reconstructed; enforce privacy first
- **Contract/event/SH name:** getCandidateSearchProjection; SH-094 buildSourceProjection.
- **Producer output:** Candidate-owned sanitized projection with visibility/currentness.
- **Consumer expectation:** Protected index only; no raw resume/answers reconstructed; enforce privacy first.
- **Sequencing requirement:** CP08/NP09; CONTRACT_ONLY plus unresolved visibility/cardinality/topology.
- **Failure behavior:** Unknown visibility excludes; stale rebuild cannot resurrect erased data.
- **Privacy/sensitivity:** Skills/title bands/state/approved metadata only.
- **Evidence files:** [NA] §8/25/35; [SEARCH] §25/35.
- **Current status:** `UNRESOLVED`.

### CL-06-B021 — SH-091 requestSearchProjectionRefresh

- **Producer Cluster / Module:** CL-06 Organization/Candidate.
- **Consumer Cluster / Module:** CL-02 Search.
- **Purpose and boundary type:** command; background workflow; Shared Operation. Search-owned work record/provider execution and retry
- **Contract/event/SH name:** SH-091 requestSearchProjectionRefresh.
- **Producer output:** Entity/action/reason/source version/idempotency request after owner commit.
- **Consumer expectation:** Search-owned work record/provider execution and retry.
- **Sequencing requirement:** CP03/08; FOUNDATION_CAPABILITY at live handoff.
- **Failure behavior:** Retry without source rollback; deletion/currentness wins over older upserts.
- **Privacy/sensitivity:** Minimized identifiers/projection inputs.
- **Evidence files:** [OA]/[NA] §25; CP03/08; [SEARCH] SH-091.
- **Current status:** `ALIGNED`.

### CL-06-B022 — Protected Candidate/public Job/Organization query contracts

- **Producer Cluster / Module:** CL-02 Search.
- **Consumer Cluster / Module:** CL-06 organization/candidate-facing surfaces.
- **Purpose and boundary type:** query; policy/guardrail. Owner privacy + Role + applicable entitlement; no resume access permission inferred
- **Contract/event/SH name:** Protected Candidate/public Job/Organization query contracts.
- **Producer output:** Authorized ranked safe results.
- **Consumer expectation:** Owner privacy + Role + applicable entitlement; no resume access permission inferred.
- **Sequencing requirement:** CP08 for Candidate; CONTRACT_ONLY query/security topology first.
- **Failure behavior:** Deny protected query when mandatory gate absent.
- **Privacy/sensitivity:** Separate protected collection/server authorization; sensitive-query audit still open.
- **Evidence files:** [SEARCH] protected candidate flow/§35; [NA] §25; [CA] §18.
- **Current status:** `UNRESOLVED`.

### CL-06-B023 — getJobPublicationComplianceDecision; SH-021 only if Search owner contract requires; SH-024 counterpart

- **Producer Cluster / Module:** CL-06 Job Compliance via Organization publication state.
- **Consumer Cluster / Module:** CL-02 Search.
- **Purpose and boundary type:** query; policy/guardrail. Organization applies lifecycle; Search projects current owner-approved readiness
- **Contract/event/SH name:** getJobPublicationComplianceDecision; SH-021 only if Search owner contract requires; SH-024 counterpart.
- **Producer output:** Current decision/evidence as readiness input, not a command to publish.
- **Consumer expectation:** Organization applies lifecycle; Search projects current owner-approved readiness.
- **Sequencing requirement:** CP02→03; CONTRACT_ONLY exact composition.
- **Failure behavior:** No publication on unavailable/stale compliance or unresolved mapping.
- **Privacy/sensitivity:** Evidence references; no matched text/rule payload.
- **Evidence files:** [JA] §11/14; [OA] publication; [SEARCH] public readiness; R021 applies Candidate, not arbitrary Search reads.
- **Current status:** `QUESTIONABLE`.

### CL-06-B024 — Upload APIs; SH-082 validateUploadedFile; SH-083 scanFileForMalware

- **Producer Cluster / Module:** CL-06 Organization/Candidate.
- **Consumer Cluster / Module:** CL-05 Media / File Access.
- **Purpose and boundary type:** command; Shared Operation. Media enforces byte/MIME/size/quarantine/scan/processing policy
- **Contract/event/SH name:** Upload APIs; SH-082 validateUploadedFile; SH-083 scanFileForMalware.
- **Producer output:** Organization logo/job graphic or private candidate resume/CV upload context.
- **Consumer expectation:** Media enforces byte/MIME/size/quarantine/scan/processing policy.
- **Sequencing requirement:** CP01/04; FOUNDATION_CAPABILITY for real uploads.
- **Failure behavior:** Invalid/unready/unsafe asset cannot attach/parse/read.
- **Privacy/sensitivity:** Org images use scrubbed derivatives; resumes private; 2MB image/5MB PDF-DOCX policy evidence.
- **Evidence files:** [OA]/[NA] §24; OP04/NP02–03; [MEDIA] contextual consumers.
- **Current status:** `ALIGNED`.

### CL-06-B025 — Ready/clean/context facts; SH-090 attachValidatedMedia

- **Producer Cluster / Module:** CL-05 Media.
- **Consumer Cluster / Module:** CL-06 Organization/Candidate.
- **Purpose and boundary type:** query; Shared Operation. CL-06 writes explicit contextual joins only; Media owns asset truth
- **Contract/event/SH name:** Ready/clean/context facts; SH-090 attachValidatedMedia.
- **Producer output:** Validated MediaAsset state/authorized attachment context.
- **Consumer expectation:** CL-06 writes explicit contextual joins only; Media owns asset truth.
- **Sequencing requirement:** Before attachment and parse; CONTRACT_ONLY + FOUNDATION_CAPABILITY.
- **Failure behavior:** Recheck unsafe/missing state; replay returns existing join.
- **Privacy/sensitivity:** Explicit joins; no polymorphic media ownership/public resume URL.
- **Evidence files:** [OA]/[NA] commands; [MEDIA] contextual join boundary; JobMedia proposed meaning remains separate.
- **Current status:** `ALIGNED`.

### CL-06-B026 — authorizeContextualResumeAccess; SH-026 authorizeContextualResourceAccess pattern

- **Producer Cluster / Module:** CL-06 Candidate.
- **Consumer Cluster / Module:** CL-05 Media.
- **Purpose and boundary type:** query; policy/guardrail. Media grants mechanics only after Candidate business authorization
- **Contract/event/SH name:** authorizeContextualResumeAccess; SH-026 authorizeContextualResourceAccess pattern.
- **Producer output:** Actor/application/org/reason-bound allow/deny/evidence.
- **Consumer expectation:** Media grants mechanics only after Candidate business authorization.
- **Sequencing requirement:** CP07/NP08; CONTRACT_ONLY bilateral context/read semantics.
- **Failure behavior:** Deny cross-org/unavailable policy; no grant on failed context.
- **Privacy/sensitivity:** Resume purpose and minimal references, not resume content.
- **Evidence files:** [NA] §11/18/24; [MEDIA] resume boundary.
- **Current status:** `ALIGNED`.

### CL-06-B027 — SH-088 manageTemporaryAccessGrant; SH-087 issueSignedMediaUrl

- **Producer Cluster / Module:** CL-05 Media.
- **Consumer Cluster / Module:** CL-06 Candidate/resume UI and Interview review via Candidate.
- **Purpose and boundary type:** query; command; Shared Operation. Candidate appends ResumeAccessLog; generic Audit evidence remains separate
- **Contract/event/SH name:** SH-088 manageTemporaryAccessGrant; SH-087 issueSignedMediaUrl.
- **Producer output:** Short-lived scoped grant/URL and file-mechanics evidence.
- **Consumer expectation:** Candidate appends ResumeAccessLog; generic Audit evidence remains separate.
- **Sequencing requirement:** CP07/11; FOUNDATION_CAPABILITY; issuance-vs-read semantics unresolved.
- **Failure behavior:** No signed URL before allowed context/ready state; replay cannot extend access arbitrarily.
- **Privacy/sensitivity:** Short TTL, private inline delivery; exclude credentials from logs/events.
- **Evidence files:** [NA] §24/27; NP08; [MEDIA] grant/access contracts.
- **Current status:** `QUESTIONABLE`.

### CL-06-B028 — Scoped internal file-access/readiness interface

- **Producer Cluster / Module:** CL-05 Media.
- **Consumer Cluster / Module:** CL-06 Candidate parse worker.
- **Purpose and boundary type:** query; background workflow. Parse only after JobApplication plus matching JobApplicationMedia exists
- **Contract/event/SH name:** Scoped internal file-access/readiness interface.
- **Producer output:** Only authorized ready+clean application-linked bytes.
- **Consumer expectation:** Parse only after JobApplication plus matching JobApplicationMedia exists.
- **Sequencing requirement:** CP05 post-submission/NP05→03→04; FOUNDATION_CAPABILITY.
- **Failure behavior:** Corrupt permanent versus transient retry; no application rollback or hiring score.
- **Privacy/sensitivity:** Raw text/private bytes confined to parser; retention unresolved.
- **Evidence files:** [NA] §22; NP03/04; [MEDIA] private read boundary; schema ResumeParseResult.
- **Current status:** `ALIGNED`.

### CL-06-B029 — Normalized readiness/erasure/freeze/processing change; exact subscriptions not fixed

- **Producer Cluster / Module:** CL-05 Media.
- **Consumer Cluster / Module:** CL-06 contextual owners and CL-02 Search (indirect).
- **Purpose and boundary type:** event; background workflow. Stop parse/access and invalidate projections/attachments as owner policy requires
- **Contract/event/SH name:** Normalized readiness/erasure/freeze/processing change; exact subscriptions not fixed.
- **Producer output:** Current file availability/safety state.
- **Consumer expectation:** Stop parse/access and invalidate projections/attachments as owner policy requires.
- **Sequencing requirement:** CONTRACT_ONLY callback/event currentness before activation.
- **Failure behavior:** Recheck current state; duplicates cannot recreate unsafe access.
- **Privacy/sensitivity:** No raw file/provider payload in events.
- **Evidence files:** [MEDIA] events/consumers; [NA] worker recheck; [OA] processed projection rules.
- **Current status:** `QUESTIONABLE`.

### CL-06-B030 — Interview room provision/update/cancel/join contract; Video internally SH-068 invokeVideoProvider

- **Producer Cluster / Module:** CL-06 Interview.
- **Consumer Cluster / Module:** CL-05 Video Infrastructure.
- **Purpose and boundary type:** command; provider handoff. Video owns JobInterviewVideoRoom/provider credentials; Interview owns schedule
- **Contract/event/SH name:** Interview room provision/update/cancel/join contract; Video internally SH-068 invokeVideoProvider.
- **Producer output:** Interview ID, schedule, approved participant context and idempotency.
- **Consumer expectation:** Video owns JobInterviewVideoRoom/provider credentials; Interview owns schedule.
- **Sequencing requirement:** CP11/IP06; CONTRACT_ONLY then FOUNDATION_CAPABILITY for video feature.
- **Failure behavior:** Provider outage degrades room without rewriting Interview lifecycle.
- **Privacy/sensitivity:** Scoped credentials; no raw application/resume/meeting secrets in event.
- **Evidence files:** [IA] §13/20; [VIDEO] Interview room/join sections.
- **Current status:** `ALIGNED`.

### CL-06-B031 — Owner facts / counterpart SH-003 and SH-123 validateOwnedTargetReference

- **Producer Cluster / Module:** CL-06 Interview.
- **Consumer Cluster / Module:** CL-05 Video Infrastructure.
- **Purpose and boundary type:** query; policy/guardrail. Join authorized from current owner facts, not copied org permissions
- **Contract/event/SH name:** Owner facts / counterpart SH-003 and SH-123 validateOwnedTargetReference.
- **Producer output:** Current interview status/time/participant roles and target coherence.
- **Consumer expectation:** Join authorized from current owner facts, not copied org permissions.
- **Sequencing requirement:** CONTRACT_ONLY before video room/join; participant policy remains gated.
- **Failure behavior:** Revoked/missing participant facts deny credentials.
- **Privacy/sensitivity:** Minimal role/time identifiers; externalMeetingUrl not authority.
- **Evidence files:** [IA] owner facts; [VIDEO] §13/19; U-JI-01/04/08 and Video TTL gap.
- **Current status:** `QUESTIONABLE`.

### CL-06-B032 — Normalized room result/status handler; exact external event name not fixed

- **Producer Cluster / Module:** CL-05 Video Infrastructure.
- **Consumer Cluster / Module:** CL-06 Interview.
- **Purpose and boundary type:** event; provider handoff. Update only approved local handoff presentation; no provider-owned Interview transition
- **Contract/event/SH name:** Normalized room result/status handler; exact external event name not fixed.
- **Producer output:** Provider-neutral room state/receipt/error.
- **Consumer expectation:** Update only approved local handoff presentation; no provider-owned Interview transition.
- **Sequencing requirement:** CP11/IP06; CONTRACT_ONLY normalized response.
- **Failure behavior:** Retry/reconcile via Video; retain truthful parent status.
- **Privacy/sensitivity:** No durable reusable join secrets/raw callbacks.
- **Evidence files:** [IA] §12/20/22; [VIDEO] lifecycle/non-ownership.
- **Current status:** `ALIGNED`.

### CL-06-B033 — SH-067 invokeCalendarProvider via owner public calendar contract

- **Producer Cluster / Module:** CL-06 Interview.
- **Consumer Cluster / Module:** CL-05 Booking & Calendar.
- **Purpose and boundary type:** command; provider handoff; Shared Operation. Calendar owns connection/provider sync; no Booking/slot-lock conversion
- **Contract/event/SH name:** SH-067 invokeCalendarProvider via owner public calendar contract.
- **Producer output:** Committed schedule intent, safe participants, context/idempotency.
- **Consumer expectation:** Calendar owns connection/provider sync; no Booking/slot-lock conversion.
- **Sequencing requirement:** CP12/IP07; CONTRACT_ONLY hiring port; FOUNDATION_CAPABILITY for live sync.
- **Failure behavior:** Provider failure cannot roll back Interview truth; local sync-field mapping gated.
- **Privacy/sensitivity:** Minimized descriptions/participant data; consent in provider owner.
- **Evidence files:** [IA] §20; IP07; [CAL] provider-facing port wording; SH-067.
- **Current status:** `QUESTIONABLE`.

### CL-06-B034 — Normalized Calendar sync result and reconciliation query

- **Producer Cluster / Module:** CL-05 Booking & Calendar.
- **Consumer Cluster / Module:** CL-06 Interview.
- **Purpose and boundary type:** event; provider handoff; background workflow. Interview persists only approved local reference/sync/error semantics
- **Contract/event/SH name:** Normalized Calendar sync result and reconciliation query.
- **Producer output:** Verified/deduped normalized external event result/reference.
- **Consumer expectation:** Interview persists only approved local reference/sync/error semantics.
- **Sequencing requirement:** CP12/IP07; CONTRACT_ONLY local fields and normalized DTO first.
- **Failure behavior:** Reject stale results; provider owner verifies signatures/dedupes/reconciles.
- **Privacy/sensitivity:** No Cronofy payload/secrets/provider-event ledger in Interview.
- **Evidence files:** [IA] §12/20/35; CP12; [CAL] SH-059–062/067.
- **Current status:** `UNRESOLVED`.

### CL-06-B035 — SH-113 ensureContextThread

- **Producer Cluster / Module:** CL-06 Candidate/Interview; Organization where needed.
- **Consumer Cluster / Module:** CL-07 Messaging.
- **Purpose and boundary type:** command; Shared Operation. Messaging owns Thread/ThreadParticipant/uniqueness; one context converges under replay
- **Contract/event/SH name:** SH-113 ensureContextThread.
- **Producer output:** job_application/job_interview context ID and approved participants.
- **Consumer expectation:** Messaging owns Thread/ThreadParticipant/uniqueness; one context converges under replay.
- **Sequencing requirement:** Optional CP05; CP11/IP06; CONTRACT_ONLY then FOUNDATION_CAPABILITY if enabled.
- **Failure behavior:** Outage degrades conversation; no duplicate thread or source rollback.
- **Privacy/sensitivity:** No resume content in thread creation intent.
- **Evidence files:** [NA]/[IA] §13; [OA] §13; [MSG] context/SH-113; schema ThreadContextType.
- **Current status:** `ALIGNED`.

### CL-06-B036 — Source context/participant facts; membership/participant change events

- **Producer Cluster / Module:** CL-06 Organization/Candidate/Interview.
- **Consumer Cluster / Module:** CL-07 Messaging and CL-01 Role.
- **Purpose and boundary type:** query; event; policy/guardrail. Messaging/Role interpret their policies; membership ≠ automatic universal Thread access
- **Contract/event/SH name:** Source context/participant facts; membership/participant change events.
- **Producer output:** Current relationships and approved participation changes.
- **Consumer expectation:** Messaging/Role interpret their policies; membership ≠ automatic universal Thread access.
- **Sequencing requirement:** CONTRACT_ONLY revocation/update mapping; participant rules still gate.
- **Failure behavior:** Fail closed stale authority; retry change effects without cross-table writes.
- **Privacy/sensitivity:** Private thread authorization, no copied membership tables.
- **Evidence files:** [OA] events; [IA] participant policy; [MSG] authorization/contexts.
- **Current status:** `QUESTIONABLE`.

### CL-06-B037 — SH-041 requestNotification

- **Producer Cluster / Module:** CL-06 all four Modules.
- **Consumer Cluster / Module:** CL-07 Notification.
- **Purpose and boundary type:** command; Shared Operation. Notification persists/routes/delivers; source owns trigger meaning
- **Contract/event/SH name:** SH-041 requestNotification.
- **Producer output:** Recipients/template/safe variables/sensitivity/action route/idempotency.
- **Consumer expectation:** Notification persists/routes/delivers; source owns trigger meaning.
- **Sequencing requirement:** Owner commit first; CP03/05/06/09/11; FOUNDATION_CAPABILITY for actual delivery.
- **Failure behavior:** Retry/dead-letter; delivery failure does not undo hiring fact or prove legal completion.
- **Privacy/sensitivity:** No resume text, private answers, signed URLs or unnecessary PII.
- **Evidence files:** All Module §26; [NOTIFY] request/recipient contracts.
- **Current status:** `ALIGNED`.

### CL-06-B038 — resolveOrganizationNotificationRecipientFacts; SH-043 resolveNotificationRecipients

- **Producer Cluster / Module:** CL-06 Organization Hiring; Interview/Candidate for own context.
- **Consumer Cluster / Module:** CL-07 Notification.
- **Purpose and boundary type:** query; Shared Operation. Notification dedupes and applies reachability/channel eligibility; no OrganizationRole reconstruction
- **Contract/event/SH name:** resolveOrganizationNotificationRecipientFacts; SH-043 resolveNotificationRecipients.
- **Producer output:** Eligible concrete User IDs and safe routing facts.
- **Consumer expectation:** Notification dedupes and applies reachability/channel eligibility; no OrganizationRole reconstruction.
- **Sequencing requirement:** OP04 before related notifications; CONTRACT_ONLY owner query.
- **Failure behavior:** Empty eligible set valid; distinguish unauthorized/unavailable.
- **Privacy/sensitivity:** Minimal recipient IDs; source settings remain owner truth.
- **Evidence files:** [OA] §11; OP04; [NOTIFY] §13/recipient section; non-Org recipient policy remains conditional.
- **Current status:** `ALIGNED`.

### CL-06-B039 — SH-096 enumerateSubjectData

- **Producer Cluster / Module:** CL-06 all four owners.
- **Consumer Cluster / Module:** CL-08 Privacy.
- **Purpose and boundary type:** query; Shared Operation. Privacy orchestrates inventory; no direct foreign repository crawl
- **Contract/event/SH name:** SH-096 enumerateSubjectData.
- **Producer output:** Cursorable target descriptors, sensitivity, retention candidates, provider refs and export facts.
- **Consumer expectation:** Privacy orchestrates inventory; no direct foreign repository crawl.
- **Sequencing requirement:** CP13; CONTRACT_ONLY inventory/protocol earlier, FOUNDATION_CAPABILITY when executing.
- **Failure behavior:** Incomplete/failed enumeration cannot mean complete erasure.
- **Privacy/sensitivity:** Includes profile/applications/resumes/views/checks/meetings/joins.
- **Evidence files:** [CA] §20; all Module §28; [PRIV] owner protocol.
- **Current status:** `ALIGNED`.

### CL-06-B040 — SH-097 evaluateRetentionRequirement

- **Producer Cluster / Module:** CL-06 all four owners.
- **Consumer Cluster / Module:** CL-08 Privacy.
- **Purpose and boundary type:** query; policy/guardrail; Shared Operation. Privacy records exemption; owner supplies legal/domain facts
- **Contract/event/SH name:** SH-097 evaluateRetentionRequirement.
- **Producer output:** Reason/basis/minimum fields/retainUntil/anonymization/source refs.
- **Consumer expectation:** Privacy records exemption; owner supplies legal/domain facts.
- **Sequencing requirement:** Before any destructive instruction; CONTRACT_ONLY approved policy.
- **Failure behavior:** Unknown policy retained/manual-review; no invented duration.
- **Privacy/sensitivity:** Legal proof minimization and retained-data sensitivity.
- **Evidence files:** All Module §28; [JA]/[IA] §35; [PRIV] retention protocol.
- **Current status:** `UNRESOLVED`.

### CL-06-B041 — SH-095 executePrivacyInstruction; SH-098 anonymizePersonalFields where permitted

- **Producer Cluster / Module:** CL-08 Privacy.
- **Consumer Cluster / Module:** CL-06 all four owner executors.
- **Purpose and boundary type:** command; background workflow; Shared Operation. Owner mutates only own records and returns accurate per-target result
- **Contract/event/SH name:** SH-095 executePrivacyInstruction; SH-098 anonymizePersonalFields where permitted.
- **Producer output:** Authorized target/action/instruction/idempotency/retention context.
- **Consumer expectation:** Owner mutates only own records and returns accurate per-target result.
- **Sequencing requirement:** CP13; OP08/JP08/NP11/IP08; CONTRACT_ONLY target map then FOUNDATION_CAPABILITY.
- **Failure behavior:** Partial/retained/skipped/retryable/failed distinct; no fake completion.
- **Privacy/sensitivity:** No generic untyped other delete; target vocabulary and cascades remain gated.
- **Evidence files:** [CA] §20; Module privacy sections; [PRIV] controlled durable target protocol; schema enum.
- **Current status:** `UNRESOLVED`.

### CL-06-B042 — Owner export-safe serializers and execution receipts; indirect SH-100 createPrivacyExportArtifact

- **Producer Cluster / Module:** CL-06 all four owner executors.
- **Consumer Cluster / Module:** CL-08 Privacy (then CL-05 Media for export artifact).
- **Purpose and boundary type:** query; background workflow. Privacy owns orchestration/export lifecycle; Media stores artifact
- **Contract/event/SH name:** Owner export-safe serializers and execution receipts; indirect SH-100 createPrivacyExportArtifact.
- **Producer output:** Minimized export records/manifests and per-target disposition/provider receipts.
- **Consumer expectation:** Privacy owns orchestration/export lifecycle; Media stores artifact.
- **Sequencing requirement:** CP13; CONTRACT_ONLY serialization/target contracts; FOUNDATION_CAPABILITY for export.
- **Failure behavior:** Partial provider failure remains visible; retained target not silently erased.
- **Privacy/sensitivity:** Private expiring artifact; source rules redact hiring/legal/private data.
- **Evidence files:** Module §28; [PRIV] export/SH-100/Media boundary.
- **Current status:** `QUESTIONABLE`.

### CL-06-B043 — Delete/revoke owned attachment/asset request through Media/Privacy; SH-089 indirect

- **Producer Cluster / Module:** CL-06 Organization/Candidate through Privacy instruction.
- **Consumer Cluster / Module:** CL-05 Media.
- **Purpose and boundary type:** command; background workflow. Media decides file/resource mechanics and sharing-safe deletion
- **Contract/event/SH name:** Delete/revoke owned attachment/asset request through Media/Privacy; SH-089 indirect.
- **Producer output:** Approved contextual disposition and referenced assets/grants.
- **Consumer expectation:** Media decides file/resource mechanics and sharing-safe deletion.
- **Sequencing requirement:** CP13 after retention/ownership; CONTRACT_ONLY then FOUNDATION_CAPABILITY.
- **Failure behavior:** Partial deletion/revocation recorded; do not delete shared asset by cascade assumption.
- **Privacy/sensitivity:** Resumes/derivatives/private objects; no direct R2 delete.
- **Evidence files:** [OA]/[NA] §28; NP11; [MEDIA] Privacy/context boundaries.
- **Current status:** `ALIGNED`.

### CL-06-B044 — SH-091 removal plus Privacy/Search executor protocol

- **Producer Cluster / Module:** CL-06 Candidate/Organization and CL-08 Privacy.
- **Consumer Cluster / Module:** CL-02 Search.
- **Purpose and boundary type:** command; background workflow; projection. Remove public/protected projection and prevent stale rebuild resurrection
- **Contract/event/SH name:** SH-091 removal plus Privacy/Search executor protocol.
- **Producer output:** Owner privacy/source tombstone/currentness and deletion intent.
- **Consumer expectation:** Remove public/protected projection and prevent stale rebuild resurrection.
- **Sequencing requirement:** CP13; CONTRACT_ONLY deletion/currentness; FOUNDATION_CAPABILITY.
- **Failure behavior:** Retry/reconcile; erasure not complete just because local row changed.
- **Privacy/sensitivity:** Search metadata can remain personal; raw resume never indexed.
- **Evidence files:** [NA] §25/28; CP13; [SEARCH] privacy/removal.
- **Current status:** `ALIGNED`.

### CL-06-B045 — Owner deletion/revocation requests; indirect SH-070 deleteProviderResource

- **Producer Cluster / Module:** CL-06 Interview executing Privacy work.
- **Consumer Cluster / Module:** CL-05 Video/Booking & Calendar; CL-07 Messaging for its records.
- **Purpose and boundary type:** command; provider handoff; background workflow. Provider owners delete/revoke; Messaging handles own conversation data
- **Contract/event/SH name:** Owner deletion/revocation requests; indirect SH-070 deleteProviderResource.
- **Producer output:** Approved resource/context references and disposition.
- **Consumer expectation:** Provider owners delete/revoke; Messaging handles own conversation data.
- **Sequencing requirement:** CP13/IP08 after owner policy; CONTRACT_ONLY then FOUNDATION_CAPABILITY.
- **Failure behavior:** Provider retained/partial/failed visible to Privacy; no direct SDK cleanup.
- **Privacy/sensitivity:** Meeting rooms/logs/calendar participant data/threads may have distinct retention.
- **Evidence files:** [IA] §20/28; IP08; [VIDEO]/[CAL]/[MSG] privacy boundaries.
- **Current status:** `ALIGNED`.

### CL-06-B046 — SH-027 resolveLocationReveal; SH-028 applyFuzzyPublicLocation — applicability not locally bound

- **Producer Cluster / Module:** CL-08 Location Safety.
- **Consumer Cluster / Module:** CL-06 Organization/Job/Interview/Candidate; CL-02 Search indirectly.
- **Purpose and boundary type:** query; projection; policy/guardrail. No local coordinate fuzzing or exact meeting address disclosure by inference
- **Contract/event/SH name:** SH-027 resolveLocationReveal; SH-028 applyFuzzyPublicLocation — applicability not locally bound.
- **Producer output:** Approved public precision or actor/context-specific reveal proof.
- **Consumer expectation:** No local coordinate fuzzing or exact meeting address disclosure by inference.
- **Sequencing requirement:** CONTRACT_ONLY hiring target/applicability first; FOUNDATION_CAPABILITY if enabled.
- **Failure behavior:** Unknown precision/reveal policy fails closed.
- **Privacy/sensitivity:** Exact phone/address/location and free-text meetings require minimization.
- **Evidence files:** [IA] U-JI-11; [LOC] Hiring applicability; [CA] public projection rules.
- **Current status:** `UNRESOLVED`.

### CL-06-B047 — SH-011 evaluateComplianceHold

- **Producer Cluster / Module:** CL-09 Admin Review / Compliance Hold.
- **Consumer Cluster / Module:** CL-06 all applicable owner gates.
- **Purpose and boundary type:** query; policy/guardrail; Shared Operation. Local lifecycle owner composes stop sign; Hold is not Job/Application status truth
- **Contract/event/SH name:** SH-011 evaluateComplianceHold.
- **Producer output:** Active target/action stop-sign decision and hold refs.
- **Consumer expectation:** Local lifecycle owner composes stop sign; Hold is not Job/Application status truth.
- **Sequencing requirement:** Before enabled protected/publication/submission/interview action; FOUNDATION_CAPABILITY.
- **Failure behavior:** Required Hold service unavailable cannot permit action.
- **Privacy/sensitivity:** Safe reason/evidence references, not full case content.
- **Evidence files:** [CA] §15; all Module §13/19; [HOLD] public evaluation.
- **Current status:** `ALIGNED`.

### CL-06-B048 — SH-012 requestComplianceHold; SH-013 releaseComplianceHold only authorized scoped use

- **Producer Cluster / Module:** CL-06 Job Compliance/authorized owner workflow.
- **Consumer Cluster / Module:** CL-09 Admin Review / Compliance Hold.
- **Purpose and boundary type:** command; Shared Operation. Hold owner owns create/release lifecycle and policy; no direct hold rows
- **Contract/event/SH name:** SH-012 requestComplianceHold; SH-013 releaseComplianceHold only authorized scoped use.
- **Producer output:** Target/reason/scope/evidence request; approved release intent.
- **Consumer expectation:** Hold owner owns create/release lifecycle and policy; no direct hold rows.
- **Sequencing requirement:** CP02/review integrations; CONTRACT_ONLY then FOUNDATION_CAPABILITY when used.
- **Failure behavior:** Retry idempotently; no assumed release/clear on failure.
- **Privacy/sensitivity:** Minimize finding evidence; production mapping still U-05.
- **Evidence files:** [CA] Shared Ops; [JA] review/Hold sections; [HOLD] request/release contracts.
- **Current status:** `ALIGNED`.

### CL-06-B049 — Hold activation/release/expiry triggers; exact subscriptions unspecified

- **Producer Cluster / Module:** CL-09 Holds.
- **Consumer Cluster / Module:** CL-06 owners → CL-02 Search/CL-05 delivery/CL-07 collaboration indirectly.
- **Purpose and boundary type:** event; policy/guardrail; background workflow. Owners re-evaluate applicable gates; release ≠ automatic republish/reopen
- **Contract/event/SH name:** Hold activation/release/expiry triggers; exact subscriptions unspecified.
- **Producer output:** Changed stop-sign refs and current target state.
- **Consumer expectation:** Owners re-evaluate applicable gates; release ≠ automatic republish/reopen.
- **Sequencing requirement:** CONTRACT_ONLY revalidation contract before enabled effect.
- **Failure behavior:** Dedupe and current-state read; missed event cannot justify stale permissive cache.
- **Privacy/sensitivity:** No legal-case payload copied downstream.
- **Evidence files:** [OA] §9; [CA] gating; [HOLD] lifecycle/events/owner boundaries.
- **Current status:** `QUESTIONABLE`.

### CL-06-B050 — SH-103 executeModerationDecision

- **Producer Cluster / Module:** CL-09 Content Moderation.
- **Consumer Cluster / Module:** CL-06 Organization Hiring.
- **Purpose and boundary type:** command; Shared Operation. Organization validates transition and performs own mutation only
- **Contract/event/SH name:** SH-103 executeModerationDecision.
- **Producer output:** Authorized case/action/Job-or-Organization target/supported effect/idempotency.
- **Consumer expectation:** Organization validates transition and performs own mutation only.
- **Sequencing requirement:** OP06 before CL-09 enabled Job/Org effects; CONTRACT_ONLY effect mapping.
- **Failure behavior:** Reject unsupported/invalid action; same replay no duplicate mutation.
- **Privacy/sensitivity:** Safe case/evidence refs only.
- **Evidence files:** [OA] §10/13; OP06; [MOD] CL-09-R003 executor.
- **Current status:** `ALIGNED`.

### CL-06-B051 — SH-103 correlated execution result

- **Producer Cluster / Module:** CL-06 Organization Hiring.
- **Consumer Cluster / Module:** CL-09 Content Moderation.
- **Purpose and boundary type:** event; command; Shared Operation. Moderation tracks actual execution; acceptance is not completion
- **Contract/event/SH name:** SH-103 correlated execution result.
- **Producer output:** Accepted/rejected/already-applied/retryable/terminal distinctions within canonical acknowledgment/completion/failure/restored evidence.
- **Consumer expectation:** Moderation tracks actual execution; acceptance is not completion.
- **Sequencing requirement:** Same owner handler/integration gate; CONTRACT_ONLY exact encoding.
- **Failure behavior:** Retries preserve logical effect identity; report partial/terminal outcomes.
- **Privacy/sensitivity:** No foreign mutation or sensitive source record dump.
- **Evidence files:** [OA] SH-103 result; [OP] integration; [MOD] corresponding contract; SH-103 exact encoding residual.
- **Current status:** `QUESTIONABLE`.

### CL-06-B052 — Potential SH-103 candidate_profile effect handler — not established locally

- **Producer Cluster / Module:** CL-09 Content Moderation.
- **Consumer Cluster / Module:** CL-06 Candidate.
- **Purpose and boundary type:** command; policy/guardrail. Candidate would retain lifecycle authority; current bilateral handler/effect semantics absent
- **Contract/event/SH name:** Potential SH-103 candidate_profile effect handler — not established locally.
- **Producer output:** Moderation profile target/action intent.
- **Consumer expectation:** Candidate would retain lifecycle authority; current bilateral handler/effect semantics absent.
- **Sequencing requirement:** CONTRACT_ONLY before any such effect.
- **Failure behavior:** Do not substitute direct Prisma writes or invent a handler.
- **Privacy/sensitivity:** Candidate/resume data remains protected.
- **Evidence files:** [MOD] enum/provider table; [NA] §13/14; schema ModerationTargetType.
- **Current status:** `UNRESOLVED`.

### CL-06-B053 — SH-029 appendAuditEvent

- **Producer Cluster / Module:** CL-06 all four Modules.
- **Consumer Cluster / Module:** CL-09 Audit / Event Ledger.
- **Purpose and boundary type:** command; Shared Operation. Generic immutable audit, separate from owner history/queue/provider proof
- **Contract/event/SH name:** SH-029 appendAuditEvent.
- **Producer output:** Actor/action/target/outcome/correlation and safe reason/evidence.
- **Consumer expectation:** Generic immutable audit, separate from owner history/queue/provider proof.
- **Sequencing requirement:** Before required audited action; CONTRACT_ONLY failure/atomicity, FOUNDATION_CAPABILITY.
- **Failure behavior:** Required proof cannot be silently skipped; exact transaction behavior remains policy-dependent.
- **Privacy/sensitivity:** No raw findings/resumes/provider payloads.
- **Evidence files:** All Module §27; [AUDIT] append/failure boundary.
- **Current status:** `QUESTIONABLE`.

### CL-06-B054 — SH-030 recordSensitiveAccess

- **Producer Cluster / Module:** CL-06 Candidate/Interview and designated reads.
- **Consumer Cluster / Module:** CL-09 Audit / Event Ledger.
- **Purpose and boundary type:** command; Shared Operation. Generic AccessAuditLog supplements ResumeAccessLog/MediaAccessEvent/Video proof
- **Contract/event/SH name:** SH-030 recordSensitiveAccess.
- **Producer output:** Sensitive target/action/decision/request context and minimized identifiers.
- **Consumer expectation:** Generic AccessAuditLog supplements ResumeAccessLog/MediaAccessEvent/Video proof.
- **Sequencing requirement:** CP07/11; FOUNDATION_CAPABILITY for required proof; policy contract first.
- **Failure behavior:** No successful-access claim without required proof; audit-failure response needs approved policy.
- **Privacy/sensitivity:** Resume/meeting sensitivity; hashed identifiers, no URLs/raw text.
- **Evidence files:** [NA]/[IA] §27; [AUDIT] sensitive-access contract; [SEARCH] query audit residual.
- **Current status:** `QUESTIONABLE`.

### CL-06-B055 — SH-037 recordIntegrationFailure; generic logging/metrics/queue/incident APIs

- **Producer Cluster / Module:** CL-06 all workers/interfaces.
- **Consumer Cluster / Module:** CL-09 Observability / Ops.
- **Purpose and boundary type:** command; background workflow; Shared Operation. Ops owns diagnostics only; business failure/status remains source-owned
- **Contract/event/SH name:** SH-037 recordIntegrationFailure; generic logging/metrics/queue/incident APIs.
- **Producer output:** Source/correlation refs, durations/counts, normalized error/retryability.
- **Consumer expectation:** Ops owns diagnostics only; business failure/status remains source-owned.
- **Sequencing requirement:** CP prerequisites and every async feature; FOUNDATION_CAPABILITY incrementally.
- **Failure behavior:** Bounded fallback/dead-letter; diagnostic outage cannot fabricate domain success.
- **Privacy/sensitivity:** Redact raw resume/matched text/tokens; avoid PII metric labels.
- **Evidence files:** All Module §22/29; [OPS] public diagnostics; implied [SH] list.
- **Current status:** `ALIGNED`.

### CL-06-B056 — SH-031/044/045/046/047/048/049/051/052/053/055/072/076/077/080/114/125

- **Producer Cluster / Module:** Platform/shared mechanism owners (no Cluster assigned by registry).
- **Consumer Cluster / Module:** CL-06 all Modules; downstream consumer inboxes.
- **Purpose and boundary type:** Shared Operation; background workflow. Separate owner truth/policy; no local generic frameworks or universal version column
- **Contract/event/SH name:** SH-031/044/045/046/047/048/049/051/052/053/055/072/076/077/080/114/125.
- **Producer output:** Durable claims/results, locks/tokens, outbox/inbox, jobs, canonical text/hash and append/provisioning mechanisms.
- **Consumer expectation:** Separate owner truth/policy; no local generic frameworks or universal version column.
- **Sequencing requirement:** CONTRACT_ONLY platform shape then FOUNDATION_CAPABILITY per slice.
- **Failure behavior:** Atomic/replay-safe writes, bounded retry/dead-letter; no process-local correctness locks.
- **Privacy/sensitivity:** Purpose-specific safe metadata and hashing; no shared data lake of private truth.
- **Evidence files:** [CP] prerequisites; Module concurrency/jobs/[SH] sections; [SH] owner metadata; missing root artifacts.
- **Current status:** `QUESTIONABLE`.

### CL-06-B057 — SH-120 normalizeJurisdictionContext

- **Producer Cluster / Module:** Unresolved shared jurisdiction owner.
- **Consumer Cluster / Module:** CL-06 Job Compliance; shared need with CL-03 Tax and CL-08 Location.
- **Purpose and boundary type:** query; Shared Operation; policy/guardrail. Compliance owns applicability; no raw-string legal inference/local platform substitute
- **Contract/event/SH name:** SH-120 normalizeJurisdictionContext.
- **Producer output:** Normalized country/state/city/remote facts with confidence/evidence/errors.
- **Consumer expectation:** Compliance owns applicability; no raw-string legal inference/local platform substitute.
- **Sequencing requirement:** CP02/JP02; CONTRACT_ONLY owner+interface before FOUNDATION_CAPABILITY production.
- **Failure behavior:** Unresolved owner/input yields unavailable/review; deterministic supplied fixtures below gate only.
- **Privacy/sensitivity:** No public exact-location leakage.
- **Evidence files:** SH-120; [JA] §13/35; JP02; CP02.
- **Current status:** `UNRESOLVED`.

### CL-06-B058 — SH-081 runPatternScanner (Proposed ruling)

- **Producer Cluster / Module:** Proposed shared scanner owner.
- **Consumer Cluster / Module:** CL-06 Job Compliance; possible CL-09 Moderation reuse.
- **Purpose and boundary type:** Shared Operation; background workflow. Compliance interprets legal meaning; scanner is not legal authority
- **Contract/event/SH name:** SH-081 runPatternScanner (Proposed ruling).
- **Producer output:** Deterministic matches/offsets/rule IDs/scanner version.
- **Consumer expectation:** Compliance interprets legal meaning; scanner is not legal authority.
- **Sequencing requirement:** CONTRACT_ONLY approval before shared API; FOUNDATION_CAPABILITY or owner-local permitted mechanism below boundary.
- **Failure behavior:** Technical error unavailable, not legal denial/pass.
- **Privacy/sensitivity:** Minimize text; matched snippets are sensitive evidence.
- **Evidence files:** SH-081; [JA] scanner boundary; [JP] Feature 04.
- **Current status:** `UNRESOLVED`.

### CL-06-B059 — getJobComplianceReport; review_required/review_resolved facts

- **Producer Cluster / Module:** CL-06 Job Compliance.
- **Consumer Cluster / Module:** CL-09 Admin Review/Holds/Audit and CL-07 Notification.
- **Purpose and boundary type:** query; event; policy/guardrail. Review/hold/audit/delivery owners do not acquire posting policy or Job status
- **Contract/event/SH name:** getJobComplianceReport; review_required/review_resolved facts.
- **Producer output:** Authorized findings/evidence/decision summaries.
- **Consumer expectation:** Review/hold/audit/delivery owners do not acquire posting policy or Job status.
- **Sequencing requirement:** CP02 and JP05/09; CONTRACT_ONLY reviewer/evidence contract.
- **Failure behavior:** Unavailable report not legal approval; replay no duplicate hold/audit/notice.
- **Privacy/sensitivity:** No public matched text/private review notes; source refs preferred.
- **Evidence files:** [JA] §11/14/21; JP05; [HOLD]/[MOD] reviewer separation; generic review infrastructure unresolved.
- **Current status:** `QUESTIONABLE`.

### CL-06-B060 — SH-107 createChargeableOrder and authoritative Order result, consumed by Trust

- **Producer Cluster / Module:** CL-04 Transaction / Order → CL-03 Trust Verification (payment rails behind Order).
- **Consumer Cluster / Module:** CL-06 verified-only hiring gates, indirectly.
- **Purpose and boundary type:** command; query; policy/guardrail. Payment permits ordering a check; it never proves a passed check or authorizes a hiring transition
- **Contract/event/SH name:** SH-107 createChargeableOrder and authoritative Order result, consumed by Trust.
- **Producer output:** Paid screening Order status where a fee applies, then independent Trust check/readiness.
- **Consumer expectation:** Payment permits ordering a check; it never proves a passed check or authorizes a hiring transition.
- **Sequencing requirement:** CONTRACT_ONLY fee/Order contract; FOUNDATION_CAPABILITY only for paid-screening path; no full CL-04 maturity requirement.
- **Failure behavior:** Unpaid/unavailable required fee blocks that check; no local checkout or permissive readiness.
- **Privacy/sensitivity:** Payment references/disclosure only; no screening report in Order.
- **Evidence files:** [TRUST] paid-screening inbound/interface/invariant sections; [OA]/[NA] Trust boundary; CL-04 side not inspected in this pass, so alignment is limited to Trust/CL-06 separation.
- **Current status:** `QUESTIONABLE`.

### CL-06-B061 — CandidateProfile owner binding facts; SH-003 queryOwnerFacts (Proposed ruling) pattern

- **Producer Cluster / Module:** CL-06 Candidate.
- **Consumer Cluster / Module:** CL-01 Track.
- **Purpose and boundary type:** query; policy/guardrail. Validate candidate track binding through source-owned facts, not a direct Candidate repository or User-only assumption
- **Contract/event/SH name:** CandidateProfile owner binding facts; SH-003 queryOwnerFacts (Proposed ruling) pattern.
- **Producer output:** CandidateProfile ID, User ownership and source status.
- **Consumer expectation:** Validate candidate track binding through source-owned facts, not a direct Candidate repository or User-only assumption.
- **Sequencing requirement:** CONTRACT_ONLY before profile-scoped entitlement/subscription use; runtime owner facts when enabled.
- **Failure behavior:** Unknown/mismatched binding blocks affected commercial operation.
- **Privacy/sensitivity:** No application history/resume/answers in billing/entitlement profile DTO.
- **Evidence files:** [TRACK] §13 Candidate/Profile owner row; [NA] getCandidateProfile/source truth; specific bilateral DTO not frozen.
- **Current status:** `QUESTIONABLE`.

## 4. Events crossing or potentially crossing Cluster boundaries

### Common envelope, ordering and replay expectations

All rows inherit the source-owner event rules in [OA]/[NA]/[JA]/[IA] §21 and SH-045/046:

- Publish facts after successful owner mutation through a durable transactional outbox; source write/outbox share a transaction where the approved persistence pattern permits.
- Carry event ID, name/schema version, source Module, aggregate ID, owner revision/concurrency context where available, occurredAt, correlation/causation and minimized actor/sensitivity metadata.
- No raw resumes, application answers, cover letters, matched Job text, private review notes, provider payloads, signed URLs, reusable tokens or unapproved exact locations.
- Consumers use inbox/idempotency keyed by event/handler identity, compare source currentness and tolerate duplicates/out-of-order delivery. Do not assume a universal integer version or global total order.
- A fact is not an imperative downstream command. SH-041 notifications, SH-091 refreshes, SH-113 thread requests, SH-095 privacy instructions and SH-103 enforcement requests remain their respective commands/protocols; do not invent an event name for them.
- Interview event names are explicitly proposed under U-JI-09. Several other names are local plan/example declarations. No exact literal among the 54 named CL-06 events was found in the 18 inspected neighboring architectures. This is **absence of bilateral named subscription evidence**, not proof that no consumer exists in code or that explicit command orchestration is wrong.
- Four rows are deliberately labeled INTRA_CLUSTER_ONLY and excluded from the boundary count. The other rows include conditional/indirect candidates, not asserted deployed subscriptions.

| ID / event or trigger | Owner / producer | Consumer / purpose | Payload beyond common envelope | Scope / bilateral agreement | Evidence |
| --- | --- | --- | --- | --- | --- |
| CL-06-E001<br>organization.created | CL-06 Organization Hiring | CL-02 Search; CL-07 Notification when configured. Refresh public source/notify eligible actors after owner mutation | Organization ID, source revision, safe changed-state facts | Cross-Cluster candidate; exact subscription unconfirmed. Owner/rail boundaries agree at mechanism level; no matching literal subscription found in the 18 inspected neighboring Module architectures. This is not proof that the event is forbidden or required. | [OA] §21/25/26; [OP] event/features |
| CL-06-E002<br>organization.updated | CL-06 Organization Hiring | CL-02 Search; CL-07 Notification when configured. Refresh public source/notify eligible actors after owner mutation | Organization ID, source revision, safe changed-state facts | Cross-Cluster candidate; exact subscription unconfirmed. Owner/rail boundaries agree at mechanism level; no matching literal subscription found in the 18 inspected neighboring Module architectures. This is not proof that the event is forbidden or required. | [OA] §21/25/26; [OP] event/features |
| CL-06-E003<br>organization.status_changed | CL-06 Organization Hiring | CL-02 Search; CL-07 Notification when configured. Refresh public source/notify eligible actors after owner mutation | Organization ID, source revision, safe changed-state facts | Cross-Cluster candidate; exact subscription unconfirmed. Owner/rail boundaries agree at mechanism level; no matching literal subscription found in the 18 inspected neighboring Module architectures. This is not proof that the event is forbidden or required. | [OA] §21/25/26; [OP] event/features |
| CL-06-E004<br>organization.membership_added | CL-06 Organization Hiring | CL-01 Role and CL-07 Messaging/Notification where owner policies consume changes. Invalidate scoped permission/recipient/participation facts without foreign writes | Organization/member IDs, assigned role/change, safe source revision | Cross-Cluster candidate; exact subscription unconfirmed. Owner/rail boundaries agree at mechanism level; no matching literal subscription found in the 18 inspected neighboring Module architectures. This is not proof that the event is forbidden or required. | [OA] §21; [ROLE] owner facts; [MSG] membership boundary |
| CL-06-E005<br>organization.membership_role_changed | CL-06 Organization Hiring | CL-01 Role and CL-07 Messaging/Notification where owner policies consume changes. Invalidate scoped permission/recipient/participation facts without foreign writes | Organization/member IDs, assigned role/change, safe source revision | Cross-Cluster candidate; exact subscription unconfirmed. Owner/rail boundaries agree at mechanism level; no matching literal subscription found in the 18 inspected neighboring Module architectures. This is not proof that the event is forbidden or required. | [OA] §21; [ROLE] owner facts; [MSG] membership boundary |
| CL-06-E006<br>organization.membership_removed | CL-06 Organization Hiring | CL-01 Role and CL-07 Messaging/Notification where owner policies consume changes. Invalidate scoped permission/recipient/participation facts without foreign writes | Organization/member IDs, assigned role/change, safe source revision | Cross-Cluster candidate; exact subscription unconfirmed. Owner/rail boundaries agree at mechanism level; no matching literal subscription found in the 18 inspected neighboring Module architectures. This is not proof that the event is forbidden or required. | [OA] §21; [ROLE] owner facts; [MSG] membership boundary |
| CL-06-E007<br>organization.notification_setting_changed | CL-06 Organization Hiring | CL-07 Notification via refreshed owner recipient facts. Invalidate source routing inputs; delivery owner still controls channels | Organization/setting refs/version; no contact secrets | Cross-Cluster candidate; exact subscription unconfirmed. Owner/rail boundaries agree at mechanism level; no matching literal subscription found in the 18 inspected neighboring Module architectures. This is not proof that the event is forbidden or required. | [OA] §21/26; OP04; [NOTIFY] owner recipient query |
| CL-06-E008<br>job.created | CL-06 Organization Hiring | CL-02 Search; CL-07 Notification when product trigger applies. Rebuild/remove public Job and deliver owner-approved status intent | Job/org IDs, source version, status/reason; no applicant/private compliance text | Cross-Cluster candidate; exact subscription unconfirmed. Owner/rail boundaries agree at mechanism level; no matching literal subscription found in the 18 inspected neighboring Module architectures. This is not proof that the event is forbidden or required. | [OA] §21/25/26; OP05–06; CP03 |
| CL-06-E009<br>job.updated | CL-06 Organization Hiring | CL-02 Search; CL-07 Notification when product trigger applies. Rebuild/remove public Job and deliver owner-approved status intent | Job/org IDs, source version, status/reason; no applicant/private compliance text | Cross-Cluster candidate; exact subscription unconfirmed. Owner/rail boundaries agree at mechanism level; no matching literal subscription found in the 18 inspected neighboring Module architectures. This is not proof that the event is forbidden or required. | [OA] §21/25/26; OP05–06; CP03 |
| CL-06-E010<br>job.status_changed | CL-06 Organization Hiring | CL-02 Search; CL-07 Notification when product trigger applies. Rebuild/remove public Job and deliver owner-approved status intent | Job/org IDs, source version, status/reason; no applicant/private compliance text | Cross-Cluster candidate; exact subscription unconfirmed. Owner/rail boundaries agree at mechanism level; no matching literal subscription found in the 18 inspected neighboring Module architectures. This is not proof that the event is forbidden or required. | [OA] §21/25/26; OP05–06; CP03 |
| CL-06-E011<br>job.published | CL-06 Organization Hiring | CL-02 Search; CL-07 Notification when product trigger applies. Rebuild/remove public Job and deliver owner-approved status intent | Job/org IDs, source version, status/reason; no applicant/private compliance text | Cross-Cluster candidate; exact subscription unconfirmed. Owner/rail boundaries agree at mechanism level; no matching literal subscription found in the 18 inspected neighboring Module architectures. This is not proof that the event is forbidden or required. | [OA] §21/25/26; OP05–06; CP03 |
| CL-06-E012<br>job.paused | CL-06 Organization Hiring | CL-02 Search; CL-07 Notification when product trigger applies. Rebuild/remove public Job and deliver owner-approved status intent | Job/org IDs, source version, status/reason; no applicant/private compliance text | Cross-Cluster candidate; exact subscription unconfirmed. Owner/rail boundaries agree at mechanism level; no matching literal subscription found in the 18 inspected neighboring Module architectures. This is not proof that the event is forbidden or required. | [OA] §21/25/26; OP05–06; CP03 |
| CL-06-E013<br>job.filled | CL-06 Organization Hiring | CL-02 Search; CL-07 Notification when product trigger applies. Rebuild/remove public Job and deliver owner-approved status intent | Job/org IDs, source version, status/reason; no applicant/private compliance text | Cross-Cluster candidate; exact subscription unconfirmed. Owner/rail boundaries agree at mechanism level; no matching literal subscription found in the 18 inspected neighboring Module architectures. This is not proof that the event is forbidden or required. | [OA] §21/25/26; OP05–06; CP03 |
| CL-06-E014<br>job.closed | CL-06 Organization Hiring | CL-02 Search; CL-07 Notification when product trigger applies. Rebuild/remove public Job and deliver owner-approved status intent | Job/org IDs, source version, status/reason; no applicant/private compliance text | Cross-Cluster candidate; exact subscription unconfirmed. Owner/rail boundaries agree at mechanism level; no matching literal subscription found in the 18 inspected neighboring Module architectures. This is not proof that the event is forbidden or required. | [OA] §21/25/26; OP05–06; CP03 |
| CL-06-E015<br>job.archived | CL-06 Organization Hiring | CL-02 Search; CL-07 Notification when product trigger applies. Rebuild/remove public Job and deliver owner-approved status intent | Job/org IDs, source version, status/reason; no applicant/private compliance text | Cross-Cluster candidate; exact subscription unconfirmed. Owner/rail boundaries agree at mechanism level; no matching literal subscription found in the 18 inspected neighboring Module architectures. This is not proof that the event is forbidden or required. | [OA] §21/25/26; OP05–06; CP03 |
| CL-06-E016<br>job.publication_requested | CL-06 Organization Hiring | CL-06 Job Compliance; external event-bus infrastructure only proven. Start intra-Cluster publication evaluation; no external domain subscriber established | Job/source version, trigger/correlation | INTRA_CLUSTER_ONLY named business consumer; retained to prevent false cross-Cluster inference. Owner/rail boundaries agree at mechanism level; no matching literal subscription found in the 18 inspected neighboring Module architectures. This is not proof that the event is forbidden or required. | [OA] §21; OP05 |
| CL-06-E017<br>organization.media_changed | CL-06 Organization Hiring | CL-02 Search through owner refresh orchestration. Invalidate source projection after approved media relation change | Owner/media refs, source version; no file bytes | Plan-level Cross-Cluster candidate; architecture event-name confirmation needed. Owner/rail boundaries agree at mechanism level; no matching literal subscription found in the 18 inspected neighboring Module architectures. This is not proof that the event is forbidden or required. | OP04/06 (plan names; [OA] event list does not enumerate these) |
| CL-06-E018<br>job.media_changed | CL-06 Organization Hiring | CL-02 Search through owner refresh orchestration. Invalidate source projection after approved media relation change | Owner/media refs, source version; no file bytes | Plan-level Cross-Cluster candidate; architecture event-name confirmation needed. Owner/rail boundaries agree at mechanism level; no matching literal subscription found in the 18 inspected neighboring Module architectures. This is not proof that the event is forbidden or required. | OP04/06 (plan names; [OA] event list does not enumerate these) |
| CL-06-E019<br>candidate_profile.created | CL-06 Candidate | CL-01 Track binding and CL-02 Search only through approved owner projection; CL-07 notices if configured. Refresh binding/privacy-safe owner projection; never index raw profile/media blindly | Candidate ID/current source revision, safe change kind | Cross-Cluster candidate; media-attached/detached names appear in plan only. Owner/rail boundaries agree at mechanism level; no matching literal subscription found in the 18 inspected neighboring Module architectures. This is not proof that the event is forbidden or required. | [NA] §12/21/25; NP02; [TRACK] binding |
| CL-06-E020<br>candidate_profile.updated | CL-06 Candidate | CL-01 Track binding and CL-02 Search only through approved owner projection; CL-07 notices if configured. Refresh binding/privacy-safe owner projection; never index raw profile/media blindly | Candidate ID/current source revision, safe change kind | Cross-Cluster candidate; media-attached/detached names appear in plan only. Owner/rail boundaries agree at mechanism level; no matching literal subscription found in the 18 inspected neighboring Module architectures. This is not proof that the event is forbidden or required. | [NA] §12/21/25; NP02; [TRACK] binding |
| CL-06-E021<br>candidate_profile.status_changed | CL-06 Candidate | CL-01 Track binding and CL-02 Search only through approved owner projection; CL-07 notices if configured. Refresh binding/privacy-safe owner projection; never index raw profile/media blindly | Candidate ID/current source revision, safe change kind | Cross-Cluster candidate; media-attached/detached names appear in plan only. Owner/rail boundaries agree at mechanism level; no matching literal subscription found in the 18 inspected neighboring Module architectures. This is not proof that the event is forbidden or required. | [NA] §12/21/25; NP02; [TRACK] binding |
| CL-06-E022<br>candidate_profile.media_attached | CL-06 Candidate | CL-01 Track binding and CL-02 Search only through approved owner projection; CL-07 notices if configured. Refresh binding/privacy-safe owner projection; never index raw profile/media blindly | Candidate ID/current source revision, safe change kind | Cross-Cluster candidate; media-attached/detached names appear in plan only. Owner/rail boundaries agree at mechanism level; no matching literal subscription found in the 18 inspected neighboring Module architectures. This is not proof that the event is forbidden or required. | [NA] §12/21/25; NP02; [TRACK] binding |
| CL-06-E023<br>candidate_profile.media_detached | CL-06 Candidate | CL-01 Track binding and CL-02 Search only through approved owner projection; CL-07 notices if configured. Refresh binding/privacy-safe owner projection; never index raw profile/media blindly | Candidate ID/current source revision, safe change kind | Cross-Cluster candidate; media-attached/detached names appear in plan only. Owner/rail boundaries agree at mechanism level; no matching literal subscription found in the 18 inspected neighboring Module architectures. This is not proof that the event is forbidden or required. | [NA] §12/21/25; NP02; [TRACK] binding |
| CL-06-E024<br>application.submitted | CL-06 Candidate | CL-07 Notification/Messaging; CL-06 Interview is internal; Track usage is an explicit owner command. Communicate durable application facts; consumers request their own effects | Application/Job/Candidate/org IDs where allowed, state/source version; no answers/cover letter | Cross-Cluster candidate; exact subscription unconfirmed. Owner/rail boundaries agree at mechanism level; no matching literal subscription found in the 18 inspected neighboring Module architectures. This is not proof that the event is forbidden or required. | [NA] §12/21; NP05–07/10 |
| CL-06-E025<br>application.withdrawn | CL-06 Candidate | CL-07 Notification/Messaging; CL-06 Interview is internal; Track usage is an explicit owner command. Communicate durable application facts; consumers request their own effects | Application/Job/Candidate/org IDs where allowed, state/source version; no answers/cover letter | Cross-Cluster candidate; exact subscription unconfirmed. Owner/rail boundaries agree at mechanism level; no matching literal subscription found in the 18 inspected neighboring Module architectures. This is not proof that the event is forbidden or required. | [NA] §12/21; NP05–07/10 |
| CL-06-E026<br>application.status_changed | CL-06 Candidate | CL-07 Notification/Messaging; CL-06 Interview is internal; Track usage is an explicit owner command. Communicate durable application facts; consumers request their own effects | Application/Job/Candidate/org IDs where allowed, state/source version; no answers/cover letter | Cross-Cluster candidate; exact subscription unconfirmed. Owner/rail boundaries agree at mechanism level; no matching literal subscription found in the 18 inspected neighboring Module architectures. This is not proof that the event is forbidden or required. | [NA] §12/21; NP05–07/10 |
| CL-06-E027<br>application.stage_changed | CL-06 Candidate | CL-07 Notification/Messaging; CL-06 Interview is internal; Track usage is an explicit owner command. Communicate durable application facts; consumers request their own effects | Application/Job/Candidate/org IDs where allowed, state/source version; no answers/cover letter | Cross-Cluster candidate; exact subscription unconfirmed. Owner/rail boundaries agree at mechanism level; no matching literal subscription found in the 18 inspected neighboring Module architectures. This is not proof that the event is forbidden or required. | [NA] §12/21; NP05–07/10 |
| CL-06-E028<br>application.viewed | CL-06 Candidate | CL-07 Notification and CL-01 Track-gated insight surfaces if approved. Approved view notification/insight; view semantics remain U-12 | Application/view refs and minimized viewer context; no raw IP/resume | Conditional event; qualification and view summaries unapproved. Owner/rail boundaries agree at mechanism level; no matching literal subscription found in the 18 inspected neighboring Module architectures. This is not proof that the event is forbidden or required. | [NA] §12/35; NP07 |
| CL-06-E029<br>resume.parse_requested | CL-06 Candidate | CL-06 parse worker; platform queue only proven. Queue application-bound parse work | Application/media/parser policy identity; no raw text | INTRA_CLUSTER_ONLY business handler. Owner/rail boundaries agree at mechanism level; no matching literal subscription found in the 18 inspected neighboring Module architectures. This is not proof that the event is forbidden or required. | [NA] §12/22; NP03 |
| CL-06-E030<br>resume.parse_started | CL-06 Candidate | CL-06 parse workflow; Ops diagnostic intent separately. Optional processing fact | Parse/media IDs and safe state | INTRA_CLUSTER_ONLY; optional plan event. Owner/rail boundaries agree at mechanism level; no matching literal subscription found in the 18 inspected neighboring Module architectures. This is not proof that the event is forbidden or required. | NP04 optional internal event |
| CL-06-E031<br>resume.parse_completed | CL-06 Candidate | CL-06 projection builder, then CL-02 Search through projection/refresh. Extraction completes; raw result is not a Search payload | Parse/source refs/version; no extracted text | Indirect Cross-Cluster trigger; direct Search subscription not established. Owner/rail boundaries agree at mechanism level; no matching literal subscription found in the 18 inspected neighboring Module architectures. This is not proof that the event is forbidden or required. | [NA] §12/22/25; NP04/09 |
| CL-06-E032<br>resume.parse_failed | CL-06 Candidate | CL-07 Notification when candidate action needed; CL-09 Ops through diagnostic APIs. Surface owner failure while keeping technical diagnostics separate | Parse ref, safe error/retry classification; no raw document | Cross-Cluster candidate; exact subscription unconfirmed. Owner/rail boundaries agree at mechanism level; no matching literal subscription found in the 18 inspected neighboring Module architectures. This is not proof that the event is forbidden or required. | [NA] §12/22/26; NP04 |
| CL-06-E033<br>resume.accessed | CL-06 Candidate | CL-09 Audit through explicit access command; external event subscriber unconfirmed. Access-domain evidence; issuance/read distinction U-13 | Access/application/media/actor refs, approved reason/decision; no URL/raw bytes | Conditional semantics; appendAudit/recordSensitiveAccess are commands, not implied subscribers. Owner/rail boundaries agree at mechanism level; no matching literal subscription found in the 18 inspected neighboring Module architectures. This is not proof that the event is forbidden or required. | [NA] §12/24/27; NP08 |
| CL-06-E034<br>candidate_projection.changed | CL-06 Candidate | CL-02 Search through SH-091/SH-094. Refresh/remove authorized source projection | Projection/candidate refs/version/privacy state; no raw resume | Cross-Cluster candidate; exact subscription unconfirmed. Owner/rail boundaries agree at mechanism level; no matching literal subscription found in the 18 inspected neighboring Module architectures. This is not proof that the event is forbidden or required. | [NA] §12/25; NP09 |
| CL-06-E035<br>candidate_privacy_execution.completed | CL-06 Candidate | CL-08 Privacy (owner result protocol; event subscription not fixed). Signal accurately completed owner work, not whole-request completion | Instruction/target/result/evidence refs; retained/partial semantics per protocol | Cross-Cluster candidate; exact subscription unconfirmed. Owner/rail boundaries agree at mechanism level; no matching literal subscription found in the 18 inspected neighboring Module architectures. This is not proof that the event is forbidden or required. | [NA] §12/28; NP11 |
| CL-06-E036<br>job_compliance.evaluation_requested | CL-06 Job Compliance | CL-06 evaluation worker; shared queue only proven. Durable evaluation request | Job/source revision/trigger/correlation | INTRA_CLUSTER_ONLY business handler. Owner/rail boundaries agree at mechanism level; no matching literal subscription found in the 18 inspected neighboring Module architectures. This is not proof that the event is forbidden or required. | [CA] §16; [JA] public events |
| CL-06-E037<br>job_compliance.evaluated | CL-06 Job Compliance | CL-06 Organization primary; CL-02 Search only via approved readiness query/owner refresh. Publish current posting evidence; no external lifecycle command inferred | Job/source/check IDs, decision, reason summary, disclosure and full-rule proof refs/hash | Conditional external read-model/input; primary consumer is intra-Cluster. Owner/rail boundaries agree at mechanism level; no matching literal subscription found in the 18 inspected neighboring Module architectures. This is not proof that the event is forbidden or required. | [JA] §14/21; JP06–07 |
| CL-06-E038<br>job_compliance.decision_changed | CL-06 Job Compliance | CL-06 Organization primary; CL-02 Search only via approved readiness query/owner refresh. Publish current posting evidence; no external lifecycle command inferred | Job/source/check IDs, decision, reason summary, disclosure and full-rule proof refs/hash | Conditional external read-model/input; primary consumer is intra-Cluster. Owner/rail boundaries agree at mechanism level; no matching literal subscription found in the 18 inspected neighboring Module architectures. This is not proof that the event is forbidden or required. | [JA] §14/21; JP06–07 |
| CL-06-E039<br>job_compliance.review_required | CL-06 Job Compliance | CL-09 authorized review/Hold/Audit workflows; CL-07 Notification intent. Request owner-authorized human attention or signal completed review | Job/check/evidence refs, safe decision/reason; no private review notes | Cross-Cluster candidate; exact subscription unconfirmed. Owner/rail boundaries agree at mechanism level; no matching literal subscription found in the 18 inspected neighboring Module architectures. This is not proof that the event is forbidden or required. | [JA] §14/21; JP05/06 |
| CL-06-E040<br>job_compliance.review_resolved | CL-06 Job Compliance | CL-09 authorized review/Hold/Audit workflows; CL-07 Notification intent. Request owner-authorized human attention or signal completed review | Job/check/evidence refs, safe decision/reason; no private review notes | Cross-Cluster candidate; exact subscription unconfirmed. Owner/rail boundaries agree at mechanism level; no matching literal subscription found in the 18 inspected neighboring Module architectures. This is not proof that the event is forbidden or required. | [JA] §14/21; JP05/06 |
| CL-06-E041<br>job_compliance.evaluation_failed | CL-06 Job Compliance | CL-09 Ops via diagnostics; CL-07 notices if configured. Terminal failed/unavailable fact; never legal denial or pass | Job/check/source refs and safe failure category; full diagnostics stay Ops | Cross-Cluster candidate; exact subscription unconfirmed. Owner/rail boundaries agree at mechanism level; no matching literal subscription found in the 18 inspected neighboring Module architectures. This is not proof that the event is forbidden or required. | [JA] §21/22; JP06 |
| CL-06-E042<br>job_compliance.rule_activated | CL-06 Job Compliance | CL-06 rescan worker; CL-07 admin notice/CL-09 proof when configured. New evaluations for affected source revisions; preserve historical proof | Rule key/version/scope and transition ID/cursor context | Primary worker intra-Cluster; external notice/audit via explicit commands. Owner/rail boundaries agree at mechanism level; no matching literal subscription found in the 18 inspected neighboring Module architectures. This is not proof that the event is forbidden or required. | [JA] §21/22; JP01/06 |
| CL-06-E043<br>job_compliance.rule_retired | CL-06 Job Compliance | CL-06 rescan worker; CL-07 admin notice/CL-09 proof when configured. New evaluations for affected source revisions; preserve historical proof | Rule key/version/scope and transition ID/cursor context | Primary worker intra-Cluster; external notice/audit via explicit commands. Owner/rail boundaries agree at mechanism level; no matching literal subscription found in the 18 inspected neighboring Module architectures. This is not proof that the event is forbidden or required. | [JA] §21/22; JP01/06 |
| CL-06-E044<br>job_compliance.rule_disabled | CL-06 Job Compliance | CL-06 rescan worker; CL-07 admin notice/CL-09 proof when configured. New evaluations for affected source revisions; preserve historical proof | Rule key/version/scope and transition ID/cursor context | Primary worker intra-Cluster; external notice/audit via explicit commands. Owner/rail boundaries agree at mechanism level; no matching literal subscription found in the 18 inspected neighboring Module architectures. This is not proof that the event is forbidden or required. | [JA] §21/22; JP01/06 |
| CL-06-E045<br>interview.proposed | CL-06 Job Interview | CL-07 Notification/Messaging; CL-05 Video/Calendar via owner handoffs; CL-06 Candidate internal. Approved schedule/participant fact triggers owner-controlled collaboration/provider effects | Interview/application refs, safe schedule/state/location type/participant role context; no reusable meeting URLs/exact address by default | PROPOSED event registry U-JI-09; expiry/removal/product notices additionally gated. Owner/rail boundaries agree at mechanism level; no matching literal subscription found in the 18 inspected neighboring Module architectures. This is not proof that the event is forbidden or required. | [IA] §12/21/35; IP02/04–07 |
| CL-06-E046<br>interview.scheduled | CL-06 Job Interview | CL-07 Notification/Messaging; CL-05 Video/Calendar via owner handoffs; CL-06 Candidate internal. Approved schedule/participant fact triggers owner-controlled collaboration/provider effects | Interview/application refs, safe schedule/state/location type/participant role context; no reusable meeting URLs/exact address by default | PROPOSED event registry U-JI-09; expiry/removal/product notices additionally gated. Owner/rail boundaries agree at mechanism level; no matching literal subscription found in the 18 inspected neighboring Module architectures. This is not proof that the event is forbidden or required. | [IA] §12/21/35; IP02/04–07 |
| CL-06-E047<br>interview.rescheduled | CL-06 Job Interview | CL-07 Notification/Messaging; CL-05 Video/Calendar via owner handoffs; CL-06 Candidate internal. Approved schedule/participant fact triggers owner-controlled collaboration/provider effects | Interview/application refs, safe schedule/state/location type/participant role context; no reusable meeting URLs/exact address by default | PROPOSED event registry U-JI-09; expiry/removal/product notices additionally gated. Owner/rail boundaries agree at mechanism level; no matching literal subscription found in the 18 inspected neighboring Module architectures. This is not proof that the event is forbidden or required. | [IA] §12/21/35; IP02/04–07 |
| CL-06-E048<br>interview.cancelled | CL-06 Job Interview | CL-07 Notification/Messaging; CL-05 Video/Calendar via owner handoffs; CL-06 Candidate internal. Approved schedule/participant fact triggers owner-controlled collaboration/provider effects | Interview/application refs, safe schedule/state/location type/participant role context; no reusable meeting URLs/exact address by default | PROPOSED event registry U-JI-09; expiry/removal/product notices additionally gated. Owner/rail boundaries agree at mechanism level; no matching literal subscription found in the 18 inspected neighboring Module architectures. This is not proof that the event is forbidden or required. | [IA] §12/21/35; IP02/04–07 |
| CL-06-E049<br>interview.completed | CL-06 Job Interview | CL-07 Notification/Messaging; CL-05 Video/Calendar via owner handoffs; CL-06 Candidate internal. Approved schedule/participant fact triggers owner-controlled collaboration/provider effects | Interview/application refs, safe schedule/state/location type/participant role context; no reusable meeting URLs/exact address by default | PROPOSED event registry U-JI-09; expiry/removal/product notices additionally gated. Owner/rail boundaries agree at mechanism level; no matching literal subscription found in the 18 inspected neighboring Module architectures. This is not proof that the event is forbidden or required. | [IA] §12/21/35; IP02/04–07 |
| CL-06-E050<br>interview.no_show | CL-06 Job Interview | CL-07 Notification/Messaging; CL-05 Video/Calendar via owner handoffs; CL-06 Candidate internal. Approved schedule/participant fact triggers owner-controlled collaboration/provider effects | Interview/application refs, safe schedule/state/location type/participant role context; no reusable meeting URLs/exact address by default | PROPOSED event registry U-JI-09; expiry/removal/product notices additionally gated. Owner/rail boundaries agree at mechanism level; no matching literal subscription found in the 18 inspected neighboring Module architectures. This is not proof that the event is forbidden or required. | [IA] §12/21/35; IP02/04–07 |
| CL-06-E051<br>interview.expired | CL-06 Job Interview | CL-07 Notification/Messaging; CL-05 Video/Calendar via owner handoffs; CL-06 Candidate internal. Approved schedule/participant fact triggers owner-controlled collaboration/provider effects | Interview/application refs, safe schedule/state/location type/participant role context; no reusable meeting URLs/exact address by default | PROPOSED event registry U-JI-09; expiry/removal/product notices additionally gated. Owner/rail boundaries agree at mechanism level; no matching literal subscription found in the 18 inspected neighboring Module architectures. This is not proof that the event is forbidden or required. | [IA] §12/21/35; IP02/04–07 |
| CL-06-E052<br>interview.participant_invited | CL-06 Job Interview | CL-07 Notification/Messaging; CL-05 Video/Calendar via owner handoffs; CL-06 Candidate internal. Approved schedule/participant fact triggers owner-controlled collaboration/provider effects | Interview/application refs, safe schedule/state/location type/participant role context; no reusable meeting URLs/exact address by default | PROPOSED event registry U-JI-09; expiry/removal/product notices additionally gated. Owner/rail boundaries agree at mechanism level; no matching literal subscription found in the 18 inspected neighboring Module architectures. This is not proof that the event is forbidden or required. | [IA] §12/21/35; IP02/04–07 |
| CL-06-E053<br>interview.participant_removed | CL-06 Job Interview | CL-07 Notification/Messaging; CL-05 Video/Calendar via owner handoffs; CL-06 Candidate internal. Approved schedule/participant fact triggers owner-controlled collaboration/provider effects | Interview/application refs, safe schedule/state/location type/participant role context; no reusable meeting URLs/exact address by default | PROPOSED event registry U-JI-09; expiry/removal/product notices additionally gated. Owner/rail boundaries agree at mechanism level; no matching literal subscription found in the 18 inspected neighboring Module architectures. This is not proof that the event is forbidden or required. | [IA] §12/21/35; IP02/04–07 |
| CL-06-E054<br>interview.participant_responded | CL-06 Job Interview | CL-07 Notification/Messaging; CL-05 Video/Calendar via owner handoffs; CL-06 Candidate internal. Approved schedule/participant fact triggers owner-controlled collaboration/provider effects | Interview/application refs, safe schedule/state/location type/participant role context; no reusable meeting URLs/exact address by default | PROPOSED event registry U-JI-09; expiry/removal/product notices additionally gated. Owner/rail boundaries agree at mechanism level; no matching literal subscription found in the 18 inspected neighboring Module architectures. This is not proof that the event is forbidden or required. | [IA] §12/21/35; IP02/04–07 |
| CL-06-E055<br>Unspecified Track effective-entitlement/grant/usage-period change trigger | CL-01 Track | CL-06 Candidate projection/entitlement gates; CL-02 Search. Re-evaluate quota/perk/boost; current entitlement evidence wins | Actor/profile/key/source revision/effective-time refs | Inbound trigger family; exact event name/subscription not supplied. QUESTIONABLE: direction/currentness need is documented; bilateral named event binding not established. | [NA] §22/25; [TRACK] §25/35 |
| CL-06-E056<br>Unspecified Trust readiness/requirement change trigger | CL-03 Trust | CL-06 Organization/Candidate. Re-evaluate verified-only eligibility through owner query | Target/readiness/evidence refs; no report/provider payload | Inbound trigger family; exact event name/subscription not supplied. QUESTIONABLE: direction/currentness need is documented; bilateral named event binding not established. | [OA] §9/25; [NA] lifecycle; [TRUST] boundaries |
| CL-06-E057<br>Unspecified Hold change/release/expiry trigger | CL-09 Holds | CL-06 applicable owner gates. Re-evaluate stop signs; release does not automatically republish | Target/scope/hold refs/currentness | Inbound trigger family; exact event name/subscription not supplied. QUESTIONABLE: direction/currentness need is documented; bilateral named event binding not established. | [CA] gates; [OA] §9; [HOLD] lifecycle |
| CL-06-E058<br>Unspecified Media readiness/freeze/erasure/processing result trigger | CL-05 Media | CL-06 Organization/Candidate. Recheck attach/parse/read/projection eligibility | Media/context refs and safe normalized state/version | Inbound trigger family; exact event name/subscription not supplied. QUESTIONABLE: direction/currentness need is documented; bilateral named event binding not established. | [OA]/[NA] file rules; [MEDIA] events |
| CL-06-E059<br>Normalized Video room result handler; external event name not specified | CL-05 Video | CL-06 Interview. Reflect provider-owner outcome without changing Interview source lifecycle | Room/interview refs, normalized status/error; no credentials | Inbound trigger family; exact event name/subscription not supplied. QUESTIONABLE: direction/currentness need is documented; bilateral named event binding not established. | [IA] §12/20; [VIDEO] boundary |
| CL-06-E060<br>Normalized Calendar sync result handler; external event name not specified | CL-05 Booking & Calendar | CL-06 Interview. Apply only approved local reference/sync result | Interview/external ref/source token, normalized outcome; no raw callback | Inbound trigger family; exact event name/subscription not supplied. QUESTIONABLE: direction/currentness need is documented; bilateral named event binding not established. | [IA] §12/20; [CAL] provider port |
| CL-06-E061<br>Unspecified taxonomy classification/requirement-change trigger | CL-02 Taxonomy | CL-06 source/compliance/projection owners. Re-evaluate impacted facts through owner contracts | Canonical IDs/version/impact scope | Inbound trigger family; exact event name/subscription not supplied. QUESTIONABLE: direction/currentness need is documented; bilateral named event binding not established. | [TAX] impact/consumer boundary; [OA]/[JA] source requirements |


## 5. Shared Operations crossing Cluster boundaries

### Explicit local references (59 distinct IDs)

Names, owners, classification and status below are copied from the current [SH] registry. Direction describes the local use; it does not assign an unregistered Cluster to a generic infrastructure owner. The last column identifies the CL-06 files that explicitly reference the ID. The source boundary and implementation rule in [SH] remain part of the evidence; this table does not replace them.

| ID / canonical name | Canonical owner / classification | Registry status | CL-06 provision/consumption/expectation | Local evidence |
| --- | --- | --- | --- | --- |
| SH-001<br>`resolveAuthenticatedActor` | Identity & Access<br>Platform capability | Confirmed | Consumes actor resolution from CL-01; all protected operations. | [CA], [CP], [NA], [NP], [JA], [JP], [IA], [IP], [OA], [OP] |
| SH-002<br>`authorizeResourceAction` | Role / Authority<br>Cross-cutting capability | Confirmed | Consumes permission decision from CL-01; supplies owner relationship facts separately. | [CA], [CP], [NA], [NP], [JA], [JP], [IA], [IP], [OA], [OP] |
| SH-003<br>`queryOwnerFacts` | Each source Module<br>Shared contract; separate implementations | Proposed ruling | Provides owner-specific facts to CL-01 and neighbor context owners; consumes other owners' facts. Shared shape remains proposed. | [CA], [CP], [NA], [NP], [JA], [JP], [IA], [IP], [OA], [OP] |
| SH-005<br>`resolveEntitlement` | Track Subscription & Entitlement<br>Platform commercial-policy capability | Confirmed | Consumes CL-01 Track policy for Candidate quota/perks/boost; Organization ATS owner is still open. | [CA], [CP], [NA], [NP], [OP] |
| SH-006<br>`consumeMeteredEntitlement` | Track Subscription & Entitlement<br>Cross-cutting capability | Confirmed | Consumes CL-01 Track usage mechanism; Candidate decides when application counts. Cross-owner atomicity is open. | [CA], [CP], [NA], [NP] |
| SH-011<br>`evaluateComplianceHold` | Admin Review / Compliance Hold<br>Cross-cutting capability | Confirmed | Consumes CL-09 Hold stop-sign decisions at applicable owner gates. | [CA], [CP], [NA], [NP], [JA], [IA], [IP], [OA], [OP] |
| SH-012<br>`requestComplianceHold` | Admin Review / Compliance Hold<br>Cross-cutting capability | Confirmed | Requests CL-09 Hold where approved owner policy requires escalation; no local Hold lifecycle. | [CA], [CP], [JA], [JP] |
| SH-013<br>`releaseComplianceHold` | Admin Review / Compliance Hold<br>Cross-cutting capability | Confirmed | Requests CL-09 release after eligible owner decision; release is not automatic Job/application restoration. | [CA] |
| SH-014<br>`requireStepUpForSensitiveAction` | Identity & Access<br>Platform security capability | Confirmed | Consumes CL-01 step-up only for designated sensitive actions; matrix remains conditional. | [JA], [IA], [OA] |
| SH-015<br>`returnDecisionResult` | Shared contract; policy owner varies<br>Shared contract; separate policy | Proposed ruling | Expects a proposed shared result shape; does not transfer domain policy or approve a common enum. | [CA], [CP], [NA], [NP], [JA], [JP], [IA], [OA], [OP] |
| SH-017<br>`resolveVerificationRequirements` | Trust Verification / Screening<br>Module public interface | Confirmed | Consumes CL-03 verification requirements for enabled verified-only hiring gates. | [CA], [NA], [NP], [OA], [OP] |
| SH-018<br>`evaluateVerificationReadiness` | Trust Verification / Screening<br>Module public interface | Confirmed | Consumes CL-03 verification readiness; never infers pass from cached fields. | [CA], [NA], [NP], [OA], [OP] |
| SH-021<br>`evaluateJobCompliance` | Job Compliance<br>Module public interface | Confirmed | Provides Job Compliance decision chiefly to Organization inside CL-06. Search consumes owner readiness where required; no confirmed direct Search→Compliance call is inferred. | [CA], [CP], [JA], [JP], [OA], [OP] |
| SH-022<br>`resolveTaxonomyRequirements` | Taxonomy & Classification<br>Module public interface | Confirmed | Consumes CL-02 requirement triggers; Compliance interprets its own rules. | [JA], [OA], [OP] |
| SH-023<br>`validateTaxonomyAssignment` | Taxonomy & Classification<br>Module public interface | Confirmed | Consumes CL-02 controlled-term validation; contextual join writer approval differs across Clusters. | [JA], [OA], [OP] |
| SH-026<br>`authorizeContextualResourceAccess` | Relevant context owner<br>Shared contract; separate implementations | Confirmed | Provides Candidate/Interview/source contextual access facts for CL-05 Media/Video where applicable; separate from Role and delivery mechanics. | [IP] |
| SH-029<br>`appendAuditEvent` | Audit / Event Ledger<br>Platform audit capability | Confirmed | Consumes CL-09 generic audit append; owner ledgers remain separate. | [CA], [CP], [NA], [NP], [JA], [JP], [IA], [IP], [OA], [OP] |
| SH-030<br>`recordSensitiveAccess` | Audit / Event Ledger<br>Cross-cutting capability | Confirmed | Consumes CL-09 sensitive-access audit; resume/media/domain proof is not replaced. | [CA], [CP], [NA], [NP], [JA], [IA], [IP] |
| SH-031<br>`appendDomainLifecycleEvent` | Shared persistence mechanism; each domain owns truth<br>Shared mechanism; separate truth | Confirmed | Uses shared append mechanism for owner lifecycle records; no foreign lifecycle ownership or selected missing-ledger schema. | [CA], [CP], [IA], [IP] |
| SH-037<br>`recordIntegrationFailure` | Observability / Ops<br>Cross-cutting capability | Confirmed | Consumes CL-09 operational failure capture; owner writes any business failure result. | [IA], [IP] |
| SH-041<br>`requestNotification` | Notification<br>Platform notification capability | Confirmed | Requests CL-07 notifications after source commit; no direct email/SMS provider. | [CA], [CP], [NA], [NP], [JA], [JP], [IA], [IP], [OA], [OP] |
| SH-043<br>`resolveNotificationRecipients` | Source context owner plus Notification<br>Shared contract; separate policy | Confirmed | Provides source recipient facts to CL-07; Notification owns dedupe/channel preference/fan-out. | [CA], [IA], [IP], [OA], [OP] |
| SH-044<br>`executeIdempotentCommand` | Platform application infrastructure<br>Platform primitive | Confirmed | Uses shared infrastructure command replay mechanism; owner defines semantic identity. | [CA], [CP], [NA], [NP], [JA], [JP], [IA], [IP], [OA], [OP] |
| SH-045<br>`deduplicateDomainEvent` | Platform event infrastructure; consumer owns inbox<br>Platform primitive | Confirmed | Uses shared infrastructure event inbox dedupe; each consumer owns effects and currentness. | [CA], [NA], [NP], [JA], [JP], [IA], [IP], [OA], [OP] |
| SH-046<br>`publishDomainEvent` | Platform event/outbox infrastructure<br>Platform primitive | Confirmed | Uses platform outbox; CL-06 owns event meaning. Named bilateral subscriptions are unverified. | [CA], [CP], [NA], [NP], [JA], [JP], [IA], [IP], [OA], [OP] |
| SH-047<br>`enqueueReliableJob` | Shared queue infrastructure<br>Platform primitive | Confirmed | Uses shared reliable queue for parse, compliance rescan, projection, expiry and provider follow-up. | [CA], [CP], [NA], [NP], [JA], [JP], [IA], [IP], [OA], [OP] |
| SH-048<br>`executeRetryWithBackoff` | Shared queue/platform infrastructure<br>Platform primitive | Confirmed | Uses shared retry mechanics; business/provider owner defines retryability. | [CA], [CP], [NA], [NP], [JA], [JP], [IA], [IP], [OA], [OP] |
| SH-049<br>`orchestrateWorkflowSteps` | Workflow-owning Module using shared runner<br>Shared mechanism; separate workflow truth | Confirmed | Uses shared runner for applicable owner workflows; no parallel Privacy/Moderation orchestrator. | [CA], [IA] |
| SH-051<br>`acquireAggregateLock` | Shared persistence infrastructure<br>Platform primitive | Confirmed | Uses shared locking; owner chooses aggregate/conflicting commands. | [CA], [NA], [NP], [JA], [JP], [IA], [IP], [OA], [OP] |
| SH-052<br>`withOptimisticConcurrency` | Shared persistence infrastructure<br>Platform primitive | Confirmed | Uses shared compare-and-set mechanism with opaque owner token; backing remains open. | [CA], [CP], [NA], [NP], [JA], [JP], [IA], [IP], [OA], [OP] |
| SH-053<br>`transitionLifecycleState` | Shared mechanism; lifecycle owner supplies policy<br>Shared mechanism; separate truth | Confirmed | Uses shared transition mechanics; owner lifecycle graphs and policy remain separate. | [CA], [CP], [NA], [NP], [IA], [IP], [OA] |
| SH-055<br>`runDeadlineExpiration` | Shared scheduler/queue infrastructure<br>Cross-cutting capability | Confirmed | Uses shared deadline worker; Interview proposal/deadline and owner expiration semantics remain gated. | [CA], [IA], [IP], [OA], [OP] |
| SH-059<br>`verifyProviderWebhookSignature` | Shared integration-security shell; provider adapter supplies algorithm<br>Provider-adapter contract | Confirmed | Expects CL-05 provider owners to verify callbacks; no local hiring webhook verifier. | [CP], [IA], [IP] |
| SH-060<br>`deduplicateProviderEvent` | Provider-owning Module using shared primitive<br>Shared mechanism; separate truth | Confirmed | Expects CL-05 provider owners' replay ledger; Interview consumes normalized results. | [CP], [IA], [IP] |
| SH-061<br>`translateProviderStatus` | Provider-owning adapter<br>Provider-adapter contract | Confirmed | Expects CL-05 provider-owned normalization, not a hiring copy of provider status mapping. | [CP], [IA], [IP] |
| SH-062<br>`reconcileProviderState` | Each provider-owning Module using shared worker framework<br>Shared mechanism; separate policy | Confirmed | Expects CL-05 owner reconciliation; local Interview business state is separate. | [CP], [IA], [IP] |
| SH-067<br>`invokeCalendarProvider` | Booking & Calendar<br>Module provider interface | Confirmed | Consumes CL-05 Booking & Calendar provider mechanics; hiring method coverage/local sync fields still need alignment. | [CA], [CP], [IA], [IP] |
| SH-068<br>`invokeVideoProvider` | Video Infrastructure<br>Module provider interface | Confirmed | Consumes CL-05 Video provider mechanics; supplies Interview context, not room truth. | [CA], [CP], [IA], [IP] |
| SH-072<br>`hashCanonicalPayload` | Shared security/cryptography capability<br>Platform primitive | Confirmed | Uses shared hashing for owner-defined canonical proof; hash alone cannot reconstruct an evaluation. | [CA], [CP], [JA], [JP] |
| SH-076<br>`normalizeAndHashIdentifier` | Shared security/cryptography capability<br>Platform primitive | Confirmed | Uses shared identifier hashing with purpose/normalization/retention policy. | [CA], [CP], [NA], [NP] |
| SH-077<br>`buildCanonicalTextSnapshot` | Shared text canonicalization mechanism<br>Cross-cutting primitive | Confirmed | Uses shared canonical text mechanics; Compliance owns fields and meaning. | [CA], [CP], [JA], [JP] |
| SH-080<br>`manageVersionedRules` | Each policy Module using shared versioning mechanism<br>Shared mechanism; separate policy | Confirmed | Uses shared immutable-rule mechanism; Job Compliance owns employment rule policy. | [CA], [CP], [JA], [JP] |
| SH-081<br>`runPatternScanner` | Shared scanner mechanism; policy owner unresolved<br>Cross-cutting capability | Proposed ruling | Expects proposed shared scanning mechanism; shared runtime/owner commitment is not approved. | [CA], [CP], [JA], [JP] |
| SH-082<br>`validateUploadedFile` | Media / File Access<br>Cross-cutting media capability | Confirmed | Consumes CL-05 Media upload validation; source owner decides contextual suitability. | [CA], [CP], [NA], [NP], [OP] |
| SH-083<br>`scanFileForMalware` | Media / File Access<br>Cross-cutting media capability | Confirmed | Consumes CL-05 clean scan proof; no local scanner adapter. | [CA], [CP], [NA], [NP], [OP] |
| SH-087<br>`issueSignedMediaUrl` | Media / File Access<br>Cross-cutting media capability | Confirmed | Consumes CL-05 scoped media URL after source authorization; URL is not entitlement. | [CA], [NA], [NP] |
| SH-088<br>`manageTemporaryAccessGrant` | Shared grant mechanism; each domain owns its record<br>Shared mechanism; separate truth | Confirmed | Uses shared grant pattern through relevant owner, especially Media; no unified grant table. | [CA], [NA], [NP] |
| SH-090<br>`attachValidatedMedia` | Contextual domain Module; Media owns asset truth<br>Shared contract; separate contextual truth | Confirmed | Provides contextual attachment joins; consumes CL-05 ready/clean/upload-context facts. | [CA], [CP], [NA], [NP], [OA], [OP] |
| SH-091<br>`requestSearchProjectionRefresh` | Search / Public Visibility<br>Module public interface | Confirmed | Requests CL-02 projection refresh/removal; no direct Typesense/SearchUpsertEvent writes. | [CA], [CP], [NA], [NP], [OA], [OP] |
| SH-094<br>`buildSourceProjection` | Each source Module<br>Shared pattern; separate source projection | Confirmed | Provides allowlisted source projections to CL-02; Candidate owns CandidateSearchProjection. | [CA], [CP], [NA], [NP], [OA], [OP] |
| SH-095<br>`executePrivacyInstruction` | Privacy orchestrates; each data owner executes<br>Cross-cutting protocol | Confirmed | Consumes CL-08 owner instructions and returns replay-safe retained/skipped/completed/failure results. | [CA], [CP], [NA], [NP], [JA], [JP], [IA], [IP], [OA], [OP] |
| SH-096<br>`enumerateSubjectData` | Each data-owning Module through Privacy-defined interface<br>Cross-cutting protocol | Confirmed | Provides owner-scoped subject inventory to CL-08; stable target contract still required. | [CA], [CP], [NA], [NP], [JA], [JP], [IA], [IP], [OA], [OP] |
| SH-097<br>`evaluateRetentionRequirement` | Data owner supplies facts; Privacy records exemption<br>Cross-cutting protocol | Confirmed | Provides owner retention facts; CL-08 records exemption/workflow result. | [CA], [CP], [NA], [NP], [JA], [JP], [IA], [IP], [OA], [OP] |
| SH-098<br>`anonymizePersonalFields` | Shared primitive; record owner supplies mapping<br>Cross-cutting capability | Confirmed | Uses shared anonymization primitive under owner-approved field map. | [CP], [NA], [NP], [JA], [JP], [IA], [IP] |
| SH-103<br>`executeModerationDecision` | Moderation owns decision; each target owner executes<br>Cross-cutting protocol | Confirmed | Provides Organization/Job enforcement handler to CL-09; Candidate provider is not established locally. | [OA], [OP] |
| SH-113<br>`ensureContextThread` | Messaging<br>Module public interface | Confirmed | Requests CL-07 typed application/interview context thread; Messaging owns thread truth. | [CA], [CP], [NA], [NP], [IA], [IP], [OA] |
| SH-114<br>`provisionOneToOneProfile` | Each profile Module using shared provisioning mechanism<br>Shared mechanism; separate truth | Confirmed | Uses shared provisioning mechanism; Candidate owns CandidateProfile lifecycle. | [CA], [CP], [NA], [NP] |
| SH-120<br>`normalizeJurisdictionContext` | Shared commerce/location capability ownership unresolved<br>Cross-cutting capability | Unresolved | Expects normalized jurisdiction capability; owner/contract remains unresolved. | [CA], [CP], [JA], [JP] |
| SH-125<br>`recordDomainAccessEvent` | Domain owner<br>Shared append-only mechanism; separate truth | Confirmed | Uses shared append mechanism for Candidate domain access proof; Media/CL-09 proof remains separate. | [CA], [CP], [NA], [NP] |

### Indirect, omitted-reference and conditional dependencies (29 additional IDs)

These are separately marked because a neighbor may invoke the operation internally, the need may be conditional, or CL-06 may describe the capability without an explicit ID. **They are not 29 newly required direct CL-06 calls.** In particular, no unspecified feature is enabled by listing it here.

| ID / canonical name | Canonical owner / classification | Registry status | Relationship category and evidence of need | Evidence |
| --- | --- | --- | --- | --- |
| SH-007<br>`recordConsentProof` | Consent & Disclosure<br>Platform consent capability | Confirmed | Indirect/conditional. Consent creates versioned proof consumed through Trust/Calendar; direct Candidate participation proof is unresolved. | [CONSENT]; [TRUST]; [CAL]; [CA] U-02/10 |
| SH-008<br>`queryConsentProof` | Consent & Disclosure<br>Platform consent capability | Confirmed | Indirect/conditional. Trust/Calendar query proof; CL-06 must not substitute a local consent boolean. | [TRUST]/[CAL] inbound consent; [CA] U-02 |
| SH-009<br>`resolveActiveConsentVersion` | Consent & Disclosure<br>Cross-cutting capability | Confirmed | Indirect/conditional. Active consent version underlies valid screening/calendar proof; no direct CL-06 call asserted. | [CONSENT]; Trust/Calendar proof gates |
| SH-010<br>`presentStandaloneConsent` | Consent & Disclosure<br>Cross-cutting UI/application capability | Confirmed | Indirect/conditional. Standalone screening disclosure presentation through Trust; Organization purpose remains separate. | [TRUST] consent gate; [CA] U-02 |
| SH-024<br>`evaluatePublicReadiness` | Source/compliance owner; Search composes<br>Shared contract; separate policy | Confirmed | Counterpart-required reference. Search expects owner public-readiness input; CL-06 projection policy covers need without naming this SH. | [SEARCH] §13/15/19; [CA] §18; [OA]/[NA] §25 |
| SH-027<br>`resolveLocationReveal` | Location Safety<br>Module public interface | Confirmed | Applicability unresolved. Hiring exact-location/meeting reveal not mapped; do not infer target support. | [LOC] Hiring consumers; [IA] U-JI-11 |
| SH-028<br>`applyFuzzyPublicLocation` | Location Safety<br>Module public interface | Confirmed | Applicability unresolved. Public precision expected for supported source locations; CL-06 does not explicitly bind the operation. | [LOC] source projection; [CA] §18 |
| SH-032<br>`createRequestContext` | Observability / platform infrastructure<br>Platform primitive | Confirmed | Implied capability; local ID omitted. Canonical request/correlation context demanded throughout CL-06. | All Module §29; [OPS] |
| SH-033<br>`writeStructuredLog` | Observability / Ops<br>Platform capability | Confirmed | Implied capability; local ID omitted. Shared structured logging; no local generic logger. | All Module §29; [OPS] |
| SH-034<br>`sanitizeTelemetryMetadata` | Observability / Ops and Audit payload policy<br>Cross-cutting capability | Confirmed | Implied capability; local ID omitted. Telemetry minimization/redaction is explicit; use shared boundary rather than leaking hiring data. | All Module §29; [OPS] |
| SH-035<br>`captureException` | Observability / Ops<br>Provider adapter | Confirmed | Implied capability; local ID omitted. Exception capture requested generically, not by this ID. | [NA] §29; Ops integration |
| SH-036<br>`emitMetric` | Observability / Ops<br>Platform capability | Confirmed | Implied capability; local ID omitted. Metrics/durations/counts requested generically. | Module §29; [OPS] |
| SH-038<br>`recordQueueTelemetry` | Observability / Ops / queue infrastructure<br>Cross-cutting capability | Confirmed | Implied capability; local ID omitted. Worker attempts/retries/dead letters require queue telemetry. | Module §22/29; [OPS] |
| SH-039<br>`checkServiceHealth` | Observability / Ops coordinates; owner supplies check<br>Cross-cutting capability | Confirmed | Indirect operational support. Health dependency checks belong to shared Ops; not an additional hiring health service. | Hardening plans; [OPS]/[SH] |
| SH-040<br>`correlateOpsIncident` | Observability / Ops<br>Module-internal public ops interface | Confirmed | Indirect operational support. Integration-failure/dead-letter incident linkage through Ops; no hiring incident truth. | [IA] §22/29; hardening; [OPS] |
| SH-054<br>`claimWorkItem` | Shared work-queue/locking capability<br>Cross-cutting capability | Proposed ruling | Conditional shared need. Reviewer claim/assignment infrastructure is not confirmed as a generic schema; do not infer it from primitive availability. | [JA]/[JP] review; [SH] unresolved manual-review infrastructure |
| SH-064<br>`authorizeExternalProviderConnection` | Provider-owning Module<br>Provider-adapter capability | Confirmed | Indirect provider-owner use. Calendar connection authorization stays with Booking & Calendar before hiring sync. | [CAL] connection/provider port; IP07 |
| SH-070<br>`deleteProviderResource` | Provider-owning Module<br>Provider-adapter contract | Confirmed | Indirect provider-owner use. Provider deletion/revocation belongs to Video/Calendar after approved privacy instruction. | [IA] §20/28; [CAL]/[VIDEO] Privacy |
| SH-075<br>`encryptSensitiveValue` | Shared security/cryptography capability<br>Platform primitive | Confirmed | Conditional security mechanism. Encryption of extracted text/export artifact depends on retention/privacy design; no local implementation selected. | [NA] U-13; [PRIV] SH-100 cryptography |
| SH-078<br>`minimizeAndRedactProviderInput` | Source-data owner supplies policy; shared serializer enforces<br>Cross-cutting capability | Confirmed | Indirect provider-owner use. Minimize interview/calendar/video provider payloads through provider owners. | [IA] §20; [CAL] provider section |
| SH-084<br>`scrubFileMetadata` | Media / File Access<br>Cross-cutting media capability | Confirmed | Indirect Media-owner use. Organization public images require scrubbed derivatives; no CL-06 EXIF/GPS implementation. | [OA] §24; [MEDIA] processing |
| SH-089<br>`revokeTemporaryAccessGrant` | Each grant owner using shared primitive<br>Cross-cutting command pattern | Confirmed | Indirect Media-owner use. Resume/privacy grant revocation is requested through Media; no local grant truth. | [NA] privacy; [MEDIA] grant lifecycle |
| SH-092<br>`writeSearchProjection` | Search / Public Visibility<br>Provider adapter | Confirmed | Indirect Search-owner use. Search writes external projection after accepted refresh; CL-06 never does. | [OA]/[NA] §25; [SEARCH] |
| SH-093<br>`reconcileSearchProjection` | Search / Public Visibility<br>Module-internal worker using shared queue | Confirmed | Indirect Search-owner use. Search reconciliation/backfill cannot resurrect hidden/erased owner state. | [NA]/[CP] hardening; [SEARCH] |
| SH-099<br>`orchestratePrivacyFulfillment` | Privacy / Data Erasure<br>Module-internal orchestration with public interfaces | Confirmed | Indirect Privacy-owner use. Privacy owns aggregate fulfillment; CL-06 returns per-owner results. | All Module §28; [PRIV] |
| SH-100<br>`createPrivacyExportArtifact` | Privacy owns bundle; Media/storage owns object mechanics<br>Cluster-local capability | Confirmed | Indirect Privacy/Media use. CL-06 contributes export-safe data, Privacy owns artifact workflow, Media delivery. | [JA]/[NA]/[IA]/[OA] privacy; [PRIV] export |
| SH-107<br>`createChargeableOrder` | Transaction / Order<br>Cluster-local public interface | Confirmed | Indirect paid-screening dependency. Trust consumes authoritative fee Order only for paid checks; not CL-06 checkout. | [TRUST] paid screening; B060 |
| SH-119<br>`applyTemporaryFeatureGrant` | Track Subscription & Entitlement or affected feature owner<br>Cross-cutting public interface; ownership partly unresolved | Proposed ruling | Future conditional; Proposed ruling. Temporary Candidate boosts may use Track grants, but ownership/policy is unresolved and not locally referenced. | [TRACK] SH-119; U070 |
| SH-123<br>`validateOwnedTargetReference` | Target owner<br>Shared contract; separate implementations | Confirmed | Counterpart-required reference. Video/Media/source-owner target validation contracts imply narrow CL-06 facts; no generic foreign repository. | [VIDEO] §13; [IA] owner facts; [MEDIA] |

### Shared-operation refresh flags

| Flag | Observation carried forward | Disposition in this handoff |
| --- | --- | --- |
| SH-F01 — proposed/unresolved | SH-003 queryOwnerFacts, SH-015 returnDecisionResult and SH-081 runPatternScanner remain Proposed ruling; SH-120 normalizeJurisdictionContext remains Unresolved. The indirect future SH-119 applyTemporaryFeatureGrant also remains Proposed ruling. | No shared API/schema approval inferred. U041–044/U070 and relevant production gates remain open. |
| SH-F02 — result vocabulary | SH-021's registry implementation rule says “pass, warning, block, or review”; the approved CL-06-R004 Module response vocabulary is allowed, denied, warning, review_required, unavailable. | Record wording/result-shape disagreement for the later SH refresh. It may be summary shorthand or stale vocabulary; do not silently map values, reopen R004, or treat the registry wording as an overriding policy ruling. [SH] SH-021; [JA]/[OA] public interfaces; U005. |
| SH-F03 — Calendar coverage | SH-067 owner and canonical boundary include hiring; current [CAL] provider-facing methods are phrased for Booking. [IA]/[IP] expect the hiring-capable port. | Provider coverage is QUESTIONABLE, not a new ownership ruling. B033/U057. |
| SH-F04 — Candidate moderation | SH-103 is named locally for Organization/Job, while [MOD] includes candidate_profile and expects owner execution. [NA]/[NP] do not define an explicit Candidate handler/effect contract. | Missing/conditional provider contract, not permission to create one. B052/U046. |
| SH-F05 — omitted local references | Search public-readiness SH-024, shared Ops SH-032–036/038–040, and counterpart target validation SH-123 are described by need/counterpart more clearly than by local SH reference. | Carry as reference/contract coverage gaps; SH-039/040 and other inferred entries may remain indirect. |
| SH-F06 — applicability not established | SH-027/028 location, SH-054 generic review claims, SH-075 export/text encryption details, SH-119 temporary grants and other conditional entries lack complete CL-06 policy binding. | Do not turn generic capability existence into approved local semantics. |
| SH-F07 — aliases | SH-068 owner label is Video Infrastructure; registry Module identity is Video Session/video_session. Media / File Access denotes the Media Asset owner; Role / Authority and Search / Public Visibility are registry owner labels. Local prose/diagrams also use shortened labels. | Record aliases without renaming an operation or adding an owner. Canonical names/IDs in this table are preserved. |
| SH-F08 — primitive versus truth | SH-052 mentions versions/compare-and-set; R020 requires an opaque public owner token. SH-031/049/088/094/125 share mechanisms or patterns while preserving separate truth. | Different abstraction is not automatically conflict. No universal version field, workflow table, grant table, projection repository or audit replacement is selected. |
| SH-F09 — broader approval-status drift | [ROLE] still labels Organization membership ownership PR-CL01-02 Proposed; [TAX] says CL02-R001 approves contextual entity writers while CL-06 U-08 remains open. | These are source-document status disagreements, not wrong SH IDs/owners. Later platform adjudication must compare them; no registry refresh is applied here. |
| SH-F10 — identity/status checks | All 59 explicit local IDs exist; the explicit canonical name/status annotations match the current registry. No missing ID, renamed canonical operation or wrong canonical owner was established by this extraction. | This identity check does not erase the semantic/coverage discrepancies above and does not certify the registry as current architecture. |

SH-021 is counted as a locally referenced operation for completeness, although its confirmed normal caller is inside CL-06. Shared infrastructure entries are platform boundaries without a selected producer Cluster. Consequently the 88-entry inventory is a scope-qualified handoff count, not 88 confirmed external runtime endpoints.

## 6. Sequencing dependencies

`CONTRACT_ONLY` means the interface/policy agreement is needed before dependent implementation can be frozen; it does not authorize fixtures in production. `FOUNDATION_CAPABILITY` means the enabled feature needs a working shared capability. No evidence justifies requiring **FULL_CLUSTER_MATURITY** of an entire neighboring Cluster merely to obtain one listed service. Rows that begin with contract work state the later runtime gate explicitly.

| ID | Producer | Required capability/contract | Classification | When CL-06 needs it | Scope and activation limit | Evidence |
| --- | --- | --- | --- | --- | --- | --- |
| S01 | CL-01 Identity and Role | Actor, action authorization and owner-fact DTOs | CONTRACT_ONLY | Before all CL-06 public contracts; OA02/NA02/IA02/JA privileged actions | Fixture may establish contract; production uses actual service. PR-CL01-02 status mismatch remains for platform review. | [CP] prerequisites; all Module §13/18 |
| S02 | CL-01 Identity and Role | Working actor/authorization/RLS parity; designated step-up | FOUNDATION_CAPABILITY | CP01 onward; step-up only approved sensitive actions | No whole CL-01 maturity; consent/billing features unrelated to action need not precede basic drafts. | [CP] prerequisites; [OA]/[NA]/[IA]/[JA] plans |
| S03 | Platform persistence/events/queues; Ops CL-09 | Idempotency, transactions, locks/opaque tokens, outbox/inbox, reliable jobs, redacted telemetry | FOUNDATION_CAPABILITY | Source mutations/CP01; async Compliance/parse/provider work by relevant feature | Provider/worker runners and schema choices require approved contracts; generic infrastructure has no assigned Cluster in SH metadata. | [CP] prerequisites; Module concurrency/jobs |
| S04 | CL-02 Taxonomy | Validation/requirements DTOs and join-writer agreement | CONTRACT_ONLY | CP01/02; OP03; Candidate classifications | CL-06 U-08 and CL02-R001 status differ; no new writer selected here. | [OA]/[NA] U-08; [TAX] ruling; OP03 |
| S05 | CL-02 Taxonomy | Working controlled-term validation/requirements | FOUNDATION_CAPABILITY | Before real classified draft/publication; conditional Candidate assignment | No AI taxonomy/full Search maturity required for basic validation. | CP01/02; [OA]/[JA] §13 |
| S06 | Unresolved SH-120/scanner platform owner | Jurisdiction owner/interface and shared scanner approval if shared API used | CONTRACT_ONLY | CP02/JP02/04 production gate | Deterministic supplied normalized fixtures and permitted owner-local mechanics can precede live capability; not approval. | CP02; JP02/04; SH-081/120 |
| S07 | Jurisdiction capability; versioned legal policy; shared scanner if approved | Working jurisdiction/rule/check evaluation dependencies | FOUNDATION_CAPABILITY | Production CP02 and CP03 publication | Requires local U-05/07 policy and R007 implemented proof, not another whole Cluster. | CP02 exit; [JA] invariants |
| S08 | CL-02 Search | Projection schema/currentness/readiness/removal and protected-query contracts | CONTRACT_ONLY | CP03 for Job/Org; CP08 for Candidate; CP13 privacy | Fixtures allowed; Candidate privacy/topology/boost decisions block activation. | [OA]/[NA] §25; [SEARCH] §35 |
| S09 | CL-02 Search | Reliable indexing/deindexing/reconciliation and authorized protected query as enabled | FOUNDATION_CAPABILITY | CP03 public handoff; CP08 protected Candidate Search; CP13 removal | Basic public Search is sufficient for Job/Org; protected Candidate feature dependencies are separate. | CP03/08; [SEARCH] phased posture |
| S10 | CL-03 Trust (and CL-01 Consent indirectly) | Approved hiring target/readiness/consent contract and live readiness for verified-only gates | CONTRACT_ONLY | Before freezing CP03/05 verified-only subset | Then FOUNDATION_CAPABILITY required for enabled gate; unresolved legal/FCRA paths stay disabled. | [OA]/[NA] §13; [TRUST] hiring/consent gates |
| S11 | CL-04 Order via CL-03 Trust | Paid screening Order capability where fee required | FOUNDATION_CAPABILITY | Before paid check submission only | Not required for every application; payment never implies verification pass; no full CL-04 maturity. | [TRUST] SH-107; B060 |
| S12 | CL-05 Media | Upload/readiness/contextual attachment/private access and proof contract | CONTRACT_ONLY | CP04/NP02; CP05 parse; CP07 access; OP04 images | File-size/context/role and issuance/read semantics need correct owner contracts. | [MEDIA] boundary; [OA]/[NA] §24 |
| S13 | CL-05 Media | Ready+clean scanning, private storage, scoped read/grants/URLs | FOUNDATION_CAPABILITY | CP04 uploads; CP05 parser; CP07 resume viewer | Application+matching media pair precedes parse. No full Booking/Video capability needed. | CP04–05; [NP] actual 01→02→05→03→04 sequence |
| S14 | CL-01 Track | Quota period/reversal/catalog, Candidate binding and atomic application/usage contract | CONTRACT_ONLY | CP05/NP05; CP06/08 view insights/boost | U-CL01-29/U-TSE-04 and local cross-owner protocol unresolved. | [TRACK] §35; [NA] §23; NP05 |
| S15 | CL-01 Track | Working entitlement resolution and replay-safe consume for enabled Candidate gates | FOUNDATION_CAPABILITY | CP05 quota; CP08 boost/perks | No Organization plan assumed; paid provider maturity only if feature requires it. | CP05/08; NP05/09 |
| S16 | CL-07 Messaging/Notification | Typed contexts, recipient facts, notification intent and replay/error contracts | CONTRACT_ONLY | Optional CP05 conversation; CP03/05 alerts; CP11 collaboration | Working rail needed for actual delivery/thread creation; provider fixtures may prove source behavior earlier. | OP04/06; NP10; IP06; [MSG]/[NOTIFY] |
| S17 | CL-05 Video | Interview owner facts, participant policy, room/join API and exact join timing | CONTRACT_ONLY | CP11/IP06 | FOUNDATION_CAPABILITY for enabled room/join feature; no whole Video VOD/digital-goods maturity. | [IA]/[VIDEO] provider boundary; U-JI-01/04 |
| S18 | CL-05 Booking & Calendar | Hiring-capable SH-067 port, connection/consent and local sync-field agreement | CONTRACT_ONLY | CP12/IP07 | Provider capability required for live sync, but marketplace Booking/BookingHold/slot-lock lifecycle must not be prerequisite hiring truth. | [IA]/IP07; [CAL] provider interface coverage gap |
| S19 | CL-08 Privacy | Target routing, inventory/export serializers, retention/disposition/results protocol | CONTRACT_ONLY | Define during owner foundations; CP13 integration | Working orchestrator required for real requests; no destructive execution until owner retention and target maps approved. | All Module privacy sections; [PRIV] target protocol |
| S20 | CL-08 Location Safety | Hiring location target/applicability/public precision/exact reveal contract | CONTRACT_ONLY | Before publishing sensitive location or implementing U-JI-11-dependent behavior | Working precision/reveal only if applicable; no assumption entire Location Cluster blocks basic remote interviews. | [LOC] source consumers; [IA] U-JI-11 |
| S21 | CL-09 Holds/Audit/Ops | Working stop-sign decision, required audit/sensitive-access append, diagnostics | FOUNDATION_CAPABILITY | Applicable gates from CP01–07; every async feature | Contract/failure policy first; generic Ops/Audit never substitutes owner state. | Module §13/19/27/29 |
| S22 | CL-09 Moderation and CL-06 Organization provider | Exact SH-103 target/effect/result and owner execution contract | CONTRACT_ONLY | OP06 provides handler before CL-09 enables Job/Org effects; bilateral proof in integration | Candidate effect provider is unestablished. No new moderation transition inferred. | OP06/integration; [MOD] CL-09-R003 |
| S23 | All direct neighbor contracts relevant to enabled slice | Cross-owner contract proof and production failure/replay/privacy tests | FOUNDATION_CAPABILITY | CP14–15; OP09/JP09–10/NP12–13/IP09–10 | Requires enabled capabilities and test evidence, not blanket FULL_CLUSTER_MATURITY. | All implementation plans integration/hardening |

CL-06-local ordering also constrains the bridges: Organization/Job foundations precede Compliance publication integration; ready clean resume upload/profile attachment may precede application, but submission plus matching JobApplicationMedia precedes parsing. The Candidate plan retains feature IDs and explicitly orders 01 → 02 → 05 → 03 → 04 → 06 onward. Interview lifecycle/participant policy precedes collaboration and provider integration; privacy contracts are designed with owner foundations, then exercised in the dedicated integration features. Cross-owner integration and hardening prove authorization, privacy, stale-result rejection, failure classification and replay rather than silently approving unresolved policy. Missing root plans/phases are not inferred from Cluster feature numbers.

## 7. Cross-cutting rail audit

`USED` records a documented boundary, not runtime completion. `UNCLEAR` records incomplete applicability/policy/contract binding. `SHOULD_USE_BUT_MISSING` identifies a neighboring contract expectation without a local provider; it does not authorize adding a feature. No entire requested rail is `NOT_USED`; conditional sub-capabilities remain explicitly qualified below.

| Rail | Concern | Coverage | Evidence-based assessment | Evidence |
| --- | --- | --- | --- | --- |
| CL-01 | Authentication | USED | SH-001 trusted actor for every protected CL-06 operation. | [ID]; [CA] §14; all Module §18 |
| CL-01 | Authorization | USED | SH-002 and owner facts; RLS parity. Role still calls PR-CL01-02 proposed while CL-06 ownership is binding; carry discrepancy. | [ROLE] §35; [OA]/[NA]/[IA] owner facts |
| CL-01 | Actor/profile resolution | USED | User actor and CandidateProfile remain distinct; Candidate owner supplies Track binding. No CL-06 customer actor/SH-004 dependency established. | [NA] §3/13; [TRACK] Candidate binding; [ID] |
| CL-01 | Consent | UNCLEAR | Indirect screening/calendar proof is used through provider owners. Organization purpose and Candidate discoverability proof are not fully bound to local APIs. | [CA] U-02/10; [TRUST]; [CAL]; [CONSENT] |
| CL-01 | Entitlements | USED | Track quota/perk/boost policy; Organization ATS commercial owner unresolved. | [CA] U-04; [NA] §19; [TRACK] §35 |
| CL-01 | Usage metering | USED | SH-006; quota period, reversal, persistent usage idempotency and application/usage protocol remain open. | [NA] §23; [TRACK] U-CL01-29/U-TSE-04 |
| CL-01 | Security/step-up | UNCLEAR | SH-014 conditional on approved sensitive-action matrix; CL-06 must not invent one. | [CA] §14; [IA] §18; [ID] security matrix |
| CL-07 | Thread/Messaging | USED | SH-113 optional application and enabled Interview contexts; typed FK uniqueness. Participant synchronization/removal remains policy-gated. | [MSG]; [NA]/[IA] §13; NP10/IP06 |
| CL-07 | Notification requests | USED | SH-041 after owner commit; durable retry; source state not rolled back by delivery. | All Module §26; [NOTIFY] |
| CL-07 | Recipient resolution | USED | Organization query is bilateral. Interview/Candidate exact conditional recipients depend on source policy; Notification owns reachability/fan-out. | [OA] query; [NOTIFY] recipient section; [IA]/[NA] §26 |
| CL-07 | Delivery-trigger assumptions | UNCLEAR | Conditional view/completion/no-show notices and exact event subscriptions are not frozen. Delivery receipt is not legal or business-state completion. | [IA]/[NA] §26; [JA] owner-facing publication split |
| CL-08 | Personal-data ownership | USED | Each CL-06 owner inventories only its records; no central foreign-table eraser. | [CA] §20; all Module §28; [PRIV] |
| CL-08 | Enumeration/execution | USED | SH-096/095; hiring target descriptors/routing not fully represented by current DataErasureTargetType. | [PRIV] target contract; [IA] U-JI-07; schema |
| CL-08 | Retention | USED | SH-097 facts then Privacy exemption; exact hiring/Compliance/resume/Interview schedules remain unresolved. | Module §28/35; [PRIV] |
| CL-08 | Export | USED | Owner-safe serializers → Privacy export → private Media artifact; complete field/target maps remain required. | [JA]/[NA]/[IA]/[OA] privacy; [PRIV] SH-100 |
| CL-08 | Erasure/anonymization | USED | SH-095/098, Search removal, Media/provider revocation; parent cascade ≠ proof of lawful completion. | [CA] §20; NP11/IP08; [PRIV] |
| CL-08 | Exact/fuzzy location and reveal | UNCLEAR | Location Safety acknowledges Hiring applicability; CL-06 lacks explicit SH-027/028 bindings and U-JI-11 remains open. | [LOC] §14; [IA] §35; [CA] §18 |
| CL-09 | ComplianceHold | USED | SH-011/012/013 where approved; stop sign remains separate from lifecycle and final posting precedence. | [CA] §15; [JA] U-05; [HOLD] |
| CL-09 | Organization/Job moderation enforcement | USED | SH-103 provider/consumer boundaries agree; exact effects/encoding remain gated. | [OA]/[OP] CL-09-R003; [MOD] |
| CL-09 | Candidate moderation enforcement | SHOULD_USE_BUT_MISSING | Counterpart advertises candidate_profile/owner enforcement, but no explicit Candidate SH-103 handler/effect contract appears in CL-06. Applies only if that effect is intended; no implementation directed. | [MOD] target/provider table; [NA] §13/14 |
| CL-09 | Generic audit | USED | SH-029; exact failure/atomicity requirements deferred to platform policy; does not replace domain history. | Module §27; [AUDIT] |
| CL-09 | Sensitive-access audit | USED | SH-030 supplements ResumeAccessLog/MediaAccessEvent; Search-query coverage and issuance/read correlation remain open. | [NA]/[IA] §27; [AUDIT]; [SEARCH] §35 |
| CL-09 | Observability/operational failures | USED | Shared logging/metrics/exceptions/SH-037; several canonical IDs are implied rather than referenced locally. | Module §29; [OPS] |
| CL-09 | Queue/worker visibility | USED | Shared queues, bounded retry/dead-letter, correlation and incidents; no local business approval from Ops state. | Module §22/29; [OPS]; [CP] prerequisites |

### Rail issues requiring platform review (11)

| ID | Rail | Coverage status | Issue | Related entries/evidence |
| --- | --- | --- | --- | --- |
| RI01 | CL-01 | UNCLEAR | Consent paths for Organization permissible purpose and Candidate discoverability are not fully contracted; indirect provider proof does not fill those gaps. | U002/U010/U047; B005–007 |
| RI02 | CL-01 | UNCLEAR | Sensitive-action/step-up matrix remains conditional. | U047; B004 |
| RI03 | CL-01 | USED | Track quota period/reversal/catalog and application/usage atomicity/replay are unresolved. | U027/U049–051; B008–010 |
| RI04 | CL-01 | USED | Role's PR-CL01-02 approval status differs from CL-06's confirmed Organization membership ownership. | B002; [ROLE] §35; R001 history |
| RI05 | CL-07 | UNCLEAR | Thread participant change/revocation and conditional notification recipients/triggers need exact owner contracts. | U014/U067; B035–038; event inventory |
| RI06 | CL-08 | USED | Hiring target routing, retention, serializer/disposition mapping and cascade handling block destructive production privacy. | U013/U033/U036–037/U064; B039–045 |
| RI07 | CL-08 | UNCLEAR | Hiring exact/fuzzy location and meeting-data policy lack explicit local Location Safety binding. | U040/U068; B046 |
| RI08 | CL-09 | SHOULD_USE_BUT_MISSING | Candidate profile moderation handler/effect contract is absent locally despite the neighboring owner-handler expectation. | U046; B052 |
| RI09 | CL-09 | USED | Organization moderation executor is paired but supported effect/result encoding is still a prerequisite. | U045; B050–051 |
| RI10 | CL-09 | USED | Required audit failure/transaction policy and protected Candidate Search audit coverage remain unresolved. | U048/U055; B053–054 |
| RI11 | CL-09 | USED | Ops mechanisms are used generically, but SH-032–036/038–040 are not explicit CL-06 references. This is a reference/contract inventory gap, not proof of missing runtime code. | B055; inferred [SH] table |

## 8. Indirect coupling inventory

These 26 observations include both safeguards already agreed and unresolved risks. They are not all defects, and none permits direct foreign-table access or a new shared operation.

| ID | Coupling | Why a later platform audit must account for it | Evidence |
| --- | --- | --- | --- |
| IC01 | Shared database is not shared ownership | Cross-Module Prisma reads/writes are prohibited as a default even when foreign keys make them convenient. Source DTOs and public commands remain required. | [CA] §7/24; Module repository boundaries; SH-003 |
| IC02 | Cross-owner application/quota commit | Unique JobApplication alone cannot guarantee Track usage is consumed exactly once. Atomic owner participation or explicit reconciliation is still needed. | [NA] §23; NP05; [TRACK] U-TSE-04 |
| IC03 | Parsing requires an application-media pair | ResumeParseResult FK/composite relation prevents pre-application parsing under current schema; upload and scan may precede submission. | R006; CP04/05; [NP] sequence; schema |
| IC04 | Single-Organization view versus extra M:N | Source policy forbids multiple Organization contexts; schema still permits the unexplained extra relation. Do not infer policy from joins. | R008; schema; [NA] §8 |
| IC05 | Owner representation and permission facts | ownerUserId, owner membership and Role interpretation must not diverge or grant cross-org authority. | U-CL06-03; [OA] §18; [ROLE] facts |
| IC06 | Classification writer approval drift | CL02-R001 says entity owners write joins; CL-06 still gates the writer. Privacy and impact enumeration inherit that mismatch. | [TAX] ruling; [CA]/[OA]/[NA] U-08 |
| IC07 | Shared enum does not define lifecycle | EmploymentType.contract, CompensationPeriod, ProfileStatus and application/interview status values need owner policy; no global state machine. | [CA] §9/26; [NA]/[IA] §9; [JA] U-07 |
| IC08 | Opaque concurrency versus schema fields | JobApplication has no general version/updatedAt; finding/participant rows differ. Shared SH-052 does not select their persistent token. | R020; schema; Module §23 |
| IC09 | Projection currentness and tombstones | Search and Candidate workers must not resurrect hidden/erased/closed data; source revision and currentness contracts are coupled. | [NA] §23/25; [SEARCH] §35; SH-091/094 |
| IC10 | Track boost cannot confer Search eligibility | Effective grant changes may trigger reindex but cannot override Candidate consent/privacy/source status. | [TRACK] §25; [SEARCH] protected gate; [NA] §25 |
| IC11 | Authoritative input versus Compliance evidence | Disclosure fields and a hash cannot originate missing Job facts or reconstruct historical zero-finding rule coverage. | R005/R007; [JA] §8.6; schema |
| IC12 | Normal application has no direct Compliance recheck | Compliance → Organization lifecycle/eligibility → Candidate; event/cache currentness must preserve the fail-closed owner path. | R021; [CA] §10; [NA] §19 |
| IC13 | Privacy targets versus enums/cascades | Hiring targets/children are not fully enumerated by DataErasureTargetType. Generic other is not permission for untyped deletion; cascades may destroy retained proof. | [PRIV] target protocol; [IA] U-JI-06/07; schema |
| IC14 | Three access-proof owners | ResumeAccessLog, MediaAccessEvent/Grant and AccessAuditLog carry different truth; issuance/actual read correlation is not settled. | [NA] §24/27; [MEDIA]/[AUDIT]; U-13 |
| IC15 | Provider callback isolation | Calendar/Video verify, dedupe and normalize provider callbacks; Interview handles only normalized owner results. No ProcessedInterviewCalendarEvent shortcut. | [IA] §20; SH-059–062/067/068 |
| IC16 | Calendar public-port coverage | SH and CL-06 cover hiring, while inspected Calendar provider methods are phrased for Booking. Need bilateral coverage without turning Interview into Booking. | B033; [CAL] provider-facing interface; R013 |
| IC17 | Participant truth versus delivery access | Interview participant changes affect Video claims, Messaging participation, Calendar payload and Notification recipients; none may own participant lifecycle. | [IA] U-JI-01/02; [VIDEO]/[MSG]/[NOTIFY] |
| IC18 | Notification transaction boundary | Owner facts commit first; notification failure retries without reversing applications/jobs/interviews. Delivery is not legal notice proof by itself. | Module §21/26; [NOTIFY]; [TRUST] FCRA gates |
| IC19 | Hold release and Moderation acknowledgment | Released hold is not automatic lifecycle restoration; accepted enforcement is not completed enforcement. Owners apply legal transitions and return evidence. | [CA] gates; [OA] SH-103; [MOD]/[HOLD] |
| IC20 | Provider/Media credential leakage | resumeUrl, logoUrl, externalMeetingUrl and stored provider references cannot silently become durable authorization. Short-lived grants belong to the delivery owner. | R010/R013; [OA]/[NA]/[IA] media/provider sections |
| IC21 | Source proof, audit and diagnostics stay separate | Generic audit does not replace JobInterviewEvent or required future owner ledgers; QueueJob/IntegrationFailure cannot be business result truth. | R007; [OA] ledger question; [IA] §21; [AUDIT]/[OPS] |
| IC22 | Indirect legal consent/payment dependencies | Verified-only readiness may depend on versioned screening consent and a paid Order before a check. Paid ≠ passed; CL-06 cannot skip or recreate those owners. | [TRUST] SH-008/010/107; B005/B060 |
| IC23 | Unassigned infrastructure is not CL-09 ownership | Generic locks/queue/outbox/crypto are platform/shared owners in SH metadata; Ops observes them but does not gain domain or platform ownership. | [SH] metadata; [CP] prerequisites; B056 |
| IC24 | Conditional Candidate moderation | candidate_profile target vocabulary plus generic owner handler expectation creates a potential missing provider; no direct Candidate enforcement contract is documented. | [MOD] target table; [NA] dependencies; B052 |
| IC25 | Absent named subscriptions | The inspected neighboring architectures name compatible command/query rails but contain none of the 54 exact local event literals. Event subscription agreement remains unproven; do not convert commands into events to hide the gap. | Event extraction and counterpart scan; Module §21 |
| IC26 | Inventory approval lag | Deep Module Registry still omits confirmed Candidate view-event and Interview participant ownership; current schema/registry are supporting evidence, not new lifecycle rulings. | R010/R012; Deep Registry; [IA] evidence notes |

## 9. Known reconciliation history

The approved attached CL-06 adjudication is the history source for R001–R021. The first application pass and requested second pass brought the local documents into those rulings. The second pass corrected residual wording/references, including parse order, the five-value Compliance response, immutable evaluation proof and owner concurrency tokens; it did not approve new architecture. Concurrent Notification recipient and Organization Moderation work was preserved and is now inspected as current evidence.

| Original finding | Binding decision or intentional non-decision to preserve |
| --- | --- |
| R001 | Organization/member/Job ownership and Role interpretation preserved; Organization verification, purpose proof, owner representation and commercial model left open. |
| R002 | Plans explicitly cover pauseJob, markJobFilled, closeJob and archiveJob; owner transition precedes Search effects. |
| R003 | Publication policy precedence and employment/compensation vocabulary remain unresolved; technical failure is not legal approval/rejection. |
| R004 | Job Compliance owns allowed / denied / warning / review_required / unavailable. Organization consumes it; remediation is metadata; SH-015 not approved. |
| R005 | Organization owns exact/versioned Compliance input snapshot and scoped/cursor rescan enumeration; no direct Compliance read of Organization repositories; missing source fields remain open. |
| R006 | Upload/scan/profile attachment may precede application. ResumeParseResult/job requires existing JobApplication plus matching JobApplicationMedia. Candidate feature IDs retained but execution is 01→02→05→03→04→06 onward. |
| R007 | Immutable exact input or reconstructible immutable version plus hash, complete applied rules including zero-finding approvals, scanner/time/jurisdiction proof are mandatory. Storage/retention remains deferred. |
| R008 | JobApplicationViewEvent has at most one optional Organization context. Extra many-to-many relation is not truth and is for later schema correction unless separately justified. |
| R009 | Migration baseline strategy is project-level and deliberately undecided; no reset/schema/migration work authorized. |
| R010 | Candidate owns JobApplicationViewEvent and CandidateSearchProjection. resumeUrl is not canonical; trustScore/verifiedAt/verificationExpiresAt are non-authoritative caches only. Remaining view/visibility/lifecycle/access/retention questions remain open. |
| R011 | Classification writer was preserved unresolved in this task. Later/current CL-02 approval now requires cross-Cluster reconciliation; do not silently propagate it from this handoff. |
| R012 | Interview owns JobInterviewParticipant and its role/status enums. Removal, eligibility, synchronization, reschedule, event, expiry and privacy policies were not approved. |
| R013 | Confirmed SH-067 assigns hiring calendar provider mechanics to Booking & Calendar. Only Interview-local sync/reference field semantics remain open; JobInterview is never Booking. |
| R014 | SH-003/015/081 remain Proposed ruling. Owner-specific interfaces may exist; shared API/schema commitment needs separate approval. |
| R015 | Unresolved SH-120 is a production prerequisite for jurisdiction-aware Compliance. Supplied deterministic normalized fixtures may precede production; no local replacement approved. |
| R016 | Candidate provision/access append/identifier hashing references use confirmed SH-114/125/076; source policy remains Candidate-owned. |
| R017 | Canonical SH IDs/names/statuses were inserted across all ten documents. This did not refresh or approve the Shared Operations registry. |
| R018 | Retired out-of-model relation-placement claim U-CL06-17. Actual fields are inside braces. R008 meaning mismatch and R009 migration baseline are separate. |
| R019 | Corrected verified paths/inventory and phase/feature pointers; preserved historical source filenames as provenance. Missing root artifacts were not invented. |
| R020 | Public mutation contracts use owner-issued opaque expectedConcurrencyToken, atomic compare and stale rejection via SH-052. Aggregate backing/parent-child token choices remain unselected. |
| R021 | Normal Candidate submission consumes Organization's fail-closed application-eligibility context, not a fresh direct Compliance read/evaluation; later decisions flow through Organization owner state/events. |

A future platform task must not reopen already-approved ownership merely because the supporting inventory or a neighboring approval label is stale. Conversely, an approved local owner/interface does not approve unresolved policy, schema representation, root sequencing, a proposed SH shape or a neighbor's unadopted ruling. The later taxonomy writer ruling is recorded as a cross-Cluster discrepancy, not silently applied to CL-06.

## 10. Extraction limits and use of this handoff

- This file is an inventory for platform-wide reconciliation. It changes no source architecture, plan, Module membership, registry, Shared Operation, schema, migration or application code.
- All ten CL-06 architecture/plan artifacts, context-map, current Shared Operations registry, relevant registries/schema and 18 neighboring architectures were used. Neighbor implementation plans, deployed database state and runtime subscriptions were not exhaustively audited.
- Event consumers/payloads are documented intent or minimal contract expectations at the level stated. Rows marked conditional/unconfirmed are not evidence of a subscribed handler, a frozen DTO or an approved notification policy.
- “Options” and implementation prerequisites reproduce unresolved material; they are not recommendations. Missing target mappings, provider methods, transaction protocols and owner assignments remain missing/open.
- Source filenames retain their current spelling, including `piepline` and `Visbility`; working paths are not normalized into nonexistent files. Reference links below point to current artifacts.
- No architectural decision was made by this extraction. Open questions and disagreements are handed forward, including those that may require a Shared Operations refresh.

[CA]: <../../clusters/Organization Hiring & Candidate Pipeline/organization-hiring-candidate-piepline-architecture.md>
[CP]: <../../clusters/Organization Hiring & Candidate Pipeline/organization-hiring-candidate-pipeline-build-plan.md>
[NA]: <../../clusters/Organization Hiring & Candidate Pipeline/Candidate Application & Resume Privacy Module/candidate-application-resume-privacy-module-architecture.md>
[NP]: <../../clusters/Organization Hiring & Candidate Pipeline/Candidate Application & Resume Privacy Module/candidate-application-resume-privacy-module-implementation-plan.md>
[JA]: <../../clusters/Organization Hiring & Candidate Pipeline/Job Compliance Module/job-compliance-module-architecture.md>
[JP]: <../../clusters/Organization Hiring & Candidate Pipeline/Job Compliance Module/job-compliance-module-implementation-plan.md>
[IA]: <../../clusters/Organization Hiring & Candidate Pipeline/Job Interview Module/job-interview-module-architecture.md>
[IP]: <../../clusters/Organization Hiring & Candidate Pipeline/Job Interview Module/job-interview-module-implementation-plan.md>
[OA]: <../../clusters/Organization Hiring & Candidate Pipeline/Organization Hiring Module/organization-hiring-module-architecture.md>
[OP]: <../../clusters/Organization Hiring & Candidate Pipeline/Organization Hiring Module/organization-hiring-module-implementation-plan.md>
[MAP]: <../../context-map.md>
[SH]: <../../shared/shared-operations.md>
[ID]: <../../clusters/identity, authority, & consent/Identity & Access module/identity-access-module-architecture.md>
[ROLE]: <../../clusters/identity, authority, & consent/Role & Authority Module/role-authority-module-architecture.md>
[CONSENT]: <../../clusters/identity, authority, & consent/Consent & Disclosure Module/consent-disclosure-module-architecture.md>
[TRACK]: <../../clusters/identity, authority, & consent/Track Subscription & Entitlement Module/track-subscription-entitlement-module-architecture.md>
[TAX]: <../../clusters/discovery classification & taxonomy/Taxonomy Classification Module/taxonomy-classification-module-architecture.md>
[SEARCH]: <../../clusters/discovery classification & taxonomy/Search Public Visbility Module/search-public-visibility-module-architecture.md>
[TRUST]: <../../clusters/professional supply & readiness/Trust verification Screening Module/trust-verification-screening-module-architecture.md>
[MEDIA]: <../../clusters/scheduling, media, & digital delivery/media-asset-module/media-asset-module-architecture.md>
[VIDEO]: <../../clusters/scheduling, media, & digital delivery/video-session-module/video-session-module-architecture.md>
[CAL]: <../../clusters/scheduling, media, & digital delivery/booking-calendar-module/booking-calendar-module-architecture.md>
[MSG]: <../../clusters/Messaging Notification Rail/Messaging Module/messaging-module-architecture.md>
[NOTIFY]: <../../clusters/Messaging Notification Rail/Notification Module/notification-module-architecture.md>
[PRIV]: <../../clusters/Privacy & Location Safety/Privacy Data Erasure Module/privacy-data-erasure-module-architecture.md>
[LOC]: <../../clusters/Privacy & Location Safety/Location Safety Module/location-safety-module-architecture.md>
[HOLD]: <../../clusters/Moderation holds Audits and Ops/Admin Review & Compliance Hold Module/admin-review-compliance-hold-module-architecture.md>
[AUDIT]: <../../clusters/Moderation holds Audits and Ops/Audit Event Ledger Module/audit-event-ledger-module-architecture.md>
[OPS]: <../../clusters/Moderation holds Audits and Ops/Observability Ops Module/observability-ops-module-architecture.md>
[MOD]: <../../clusters/Moderation holds Audits and Ops/Content Moderation & Legal Notice Module/content-moderation-legal-notice-module-architecture.md>
[REG]: <../../../prisma/deep modules and schemas.json>
[CLREG]: <../../../prisma/clusters.json>
[SCHEMA]: <../../../prisma/schema.prisma>
