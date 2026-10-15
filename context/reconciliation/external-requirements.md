# External requirements and activation gates

These gates remain open until evidence is recorded by the owning concern. They block the named activation, not unrelated contract design or reconciliation. No legal/provider/database approval is inferred.

## EXT-COM-10 — Privacy disposition and retention

Status: OPEN. Source family: COM-10.

Owner retention disposition precedes deletion; no FK cascade proves permission. Forward restrict/nullable attribution migration must preserve legally retained evidence.

Required evidence / remaining: Approved retention matrix and legal durations plus coordinated data migration proof; destructive processing blocked.

Affected source records: CL-04:CL04-U033, CL-04:CL04-U049, CL-05:CL-05-U010.

## EXT-COM-11 — Legal content and manual execution

Status: OPEN. Source family: COM-11.

Keep electronic/legal/manual-signature/child-directed/accessibility-waiver activation behind approved content, policy and provider evidence. Context architecture can record exact proof but cannot supply legal determinations.

Required evidence / remaining: Approved templates, manual verification procedure, child-directed rules and waiver authority before their affected production paths.

Affected source records: CL-04:CL04-U025, CL-04:CL04-U059, CL-05:CL-05-U006, CL-05:CL-05-U047, CL-05:CL-05-U048.

## EXT-COM-12 — Provider qualification

Status: OPEN. Source family: COM-12.

Use existing neutral Video/scanner/secret ports. Provider capability, healthcare agreements and encryption/key-management evidence must precede activation. Scanner callback model only if selected adapter actually requires callbacks.

Required evidence / remaining: Provider/security qualification; fail closed for required scans or sensitive transport; do not turn proposed Daily/ClamAV into approved vendors.

Affected source records: CL-05:CL-05-U001, CL-05:CL-05-U002, CL-05:CL-05-U037, CL-05:CL-05-U040, CL-05:CL-05-U044.

## EXT-FH-01 — Age eligibility provider and legal qualification

Status: OPEN. Source family: FH-01.

WA-R027 remains the age-gate protocol: no local User creation before applicable age-policy proof, single-use attempt/state binding, and callback revalidation. Qualification must exercise every enabled provider entry route (signup, social callback, retry, linking and provider provisioning trigger) and demonstrate that missing/expired/mismatched proof cannot create a local User or obtain an authorized local session. A provider shadow account is not platform membership. Identity records adapter/account/configuration version and qualification evidence; approved jurisdiction/threshold/proof-retention policy comes from the designated legal policy source. Missing external policy or provider evidence disables that signup route, not unrelated qualified routes. No external requirement is marked passed by this architecture.

Identity owns authenticated self-list and self-revoke of session/provider device registrations: accept resolved actor, opaque owned registration reference and expected security generation for revocation; return only safe device label, last-seen/status and local opaque identity. Provider session/device references and tokens are not returned. Unknown/unowned references are non-enumerating. Revocation advances Identity's security generation, records actor/reason and invalidates corresponding assurance/session use before success; provider cleanup may be pending and must report that honestly. Administrative revocation uses an explicit registered security action and fresh assurance, not the self port. Notification owns push endpoints, subscriptions, channel consent/preferences and delivery. A push endpoint is never an Identity session; logout/session revocation cannot silently mean unsubscribing every channel or deleting delivery history. If an endpoint is bound to a revoked session, Notification receives a minimal revocation fact and re-evaluates endpoint eligibility; it owns endpoint invalidation and receipt.

Identity emits security notification intent only to the affected local User with approved safe variables and an opaque authenticated-context link. Notification resolves current eligible verified delivery channel; no password, OTP, bearer recovery token, exact IP or sensitive factor details in general payload/log. Delivery request acceptance never proves delivery or security success.

CL-01 registers no generic SH-103 moderation executor at launch. A Moderation decision cannot directly rewrite Identity, Role, Consent, Track or Customer state. An explicitly authorized security restriction, Hold, entitlement grant/revocation or Customer lifecycle action must call its named owner command with current authority and purpose. Unsupported moderation target/effect returns unsupported with no mutation. Adding a new CL-01 effect requires an owner-specific allowlist, restoration semantics and evidence contract; existence of a profile row is insufficient.

Required evidence / remaining: External legal-policy approval and adapter/account/configuration qualification remain required before affected signup activation.

Affected source records: CL-01:U-CL01-04, CL-01:U-CL01-05, CL-01:U-IA-02, CL-01:U-IA-17.

## EXT-FH-10 — Employment legal purpose

Status: OPEN. Source family: FH-10.

Hiring supplies an immutable input snapshot and opaque source revision for each evaluation: Job and Organization identities, title/description, explicit work arrangement, required compensation amount/range/currency/period, benefit disclosures, geographic/jurisdiction facts, closing/publication facts and any additional field explicitly required by the selected rule. Missing mandatory facts produce unavailable/needs-changes rather than inferred values. Job Compliance stores the full immutable applied rule set (including zero-match rules), each key/version/scope, scanner/version, input snapshot/hash, evaluation identity and outcome. A text hash alone is insufficient. Sensitive text remains in protected owner evidence, not event/log payloads.

Publication result precedence: active Hold or owner restriction denies; absent/stale/incomplete evaluation or technical failure is unavailable and cannot publish; blocking findings or required_missing/blocked disclosure deny; unresolved mandatory review/jurisdiction/rule requirement remains needs_review/unavailable; passed, or warning with no blocking rule/review/disclosure, permits publication subject to all other owner checks. Disclosure provided/not_required/exempt is nonblocking only when supported by current rule proof; provided_with_warning contributes warning. Hiring's complianceStatus is a summary of this decision, never policy truth. A stale approval cannot clear a newer restriction.

Original finding evidence is immutable. Canonical meanings are sourceField, matchedTextHash plus minimal matchedSnippetPreview, and suggestedReplacement. fieldName and suggestedText become compatibility aliases; matchedText is not a second authoritative field and is unavailable outside an explicitly retained protected input snapshot. Conflicting legacy duplicate values are quarantined for migration review. Override/resolution appends actor, reason, evidence, finding/check revisions and old/new decision to retained owner history. It does not rewrite original matched evidence. Review compares both parent check revision and child finding revision atomically; stale/double review conflicts. Audit and transactional outbox accompany the mutation but cannot replace retained owner review history. Re-evaluation creates a new check; current selector compares Job source revision and complete rule-set revision before changing.

Rule activation uses one effective version per key and scope at an instant; serialize activation for that scope and reject ambiguous overlapping versions. Scope precedence and legal content require an approved jurisdiction catalog rather than inference. Retired/disabled versions remain historical and cannot be rewritten. Versioned organization purpose/certification and Consent acknowledgment are distinct evidence: Consent does not establish employment permissible purpose. Legal content, jurisdiction coverage, severity thresholds, certification wording and retrospective rescan activation remain EXTERNAL_REQUIREMENT; affected regulated publication/screening stays disabled until qualification. This is an architectural evidence contract, not a legal conclusion.

Required evidence / remaining: Approved jurisdictions, certification/notice content, severity policy and rule-rescan activation evidence.

Affected source records: CL-06:CL-06-U002, CL-06:CL-06-U062.

## EXT-FH-24 — Hiring retention and privacy routing

Status: OPEN. Source family: FH-24.

Hiring's SH-103 executor allowlist is Job/Organization publication suppression and eligible restoration; Candidate's allowlist is Candidate search-projection suppression and eligible restoration. These are owner effects of an authorized Moderation decision, not replacement domain lifecycles. Bind decision ID, target, expected owner revision, effect key, actor and policy/evidence references; return applied/already-applied/unsupported/conflict/retryable/terminal with durable receipt and resulting revision. Restoration rechecks current participation, readiness, Holds, other restrictions and erasure; it cannot make an opted-out Candidate searchable. Identity/Track effects require their specific owner commands; no generic profile mutation is implied. Bilateral Moderation effect registration and fixtures remain prerequisites.

Privacy routes typed owner-qualified Organization, Job, CandidateProfile, JobApplication, JobInterview, participant and owner-event inventory; use the canonical Privacy executor protocol with owner target IDs and versions. Never use an ambiguous other bucket to authorize mutation. Inventory includes parent/child relationships and distinct raw resume/parse data, business/compliance history, access proof and provider attachment references. Active retention/exemption blocks destructive parent cascades; return retained/redacted/detached/erased outcomes and evidence instead of deleting retained children. Raw text can be redacted separately from retained minimal decision proof when approved policy permits it. Exact legal retention periods/bases, field disposition maps and export serializers remain qualification gates; no numeric schedule is invented.

Hiring's public Organization/Job/Candidate geography uses only purpose-approved coarse Location output, not raw candidate address or meeting detail. Exact Interview location/phone is disclosed only to currently authorized participants/support for the approved purpose after durable sensitive-access proof; recruitment role alone grants no blanket meeting-secret access. Notification payloads contain contextual links, not exact location/phone/meeting credentials. If Location lacks a supported hiring target/field policy, the affected exposure remains disabled; the active-service Booking reveal rule does not automatically apply to hiring. Location/Privacy field contracts and retention must be frozen bilaterally before that surface activates.

CL-06 sensitive actions register owner action/resource facts in Role: membership transfer/removal, Job publication, Compliance rule/review/override, Candidate search, application/resume detail access, Interview participant/schedule mutation and restricted export. Consent remains purpose-specific: Trust/Consent for screening; Calendar for its connections; P17 for Candidate participation. No universal hiring-consent checkbox is invented. Shared rails and missing root placement are synthesis dependencies; exact action DTOs, constants, schema constraints and provider fixtures remain implementation qualification, not ownership uncertainty.

Required evidence / remaining: Approved retention schedules/legal bases and export serializers required; schema routing extension is coordinated implementation work.

Affected source records: CL-06:CL-06-U033, CL-06:CL-06-U036, CL-06:CL-06-U037, CL-06:CL-06-U064.

## EXT-RAILS-04 — Communication provider activation

Status: OPEN. Source family: RAILS-04.

Notification intents and credential generations

Required evidence / remaining: Selected channel provider/configuration and verified delivery capability required.

Affected source records: CL-07:U-CL07-15, CL-07:U-CL07-16, CL-07:U-CL07-17, CL-07:CL-07-H29.

## EXT-RAILS-09 — Retention and legal Privacy policy

Status: OPEN. Source family: RAILS-09.

Privacy owner inventory and private export handoff

Required evidence / remaining: Approved jurisdiction retention, exemptions, deadlines and final disposition required.

Affected source records: CL-07:U-CL07-08, CL-07:CL-07-H20, CL-08:U-08-06, CL-08:U-08-08, CL-08:U-08-09, CL-08:U-08-21, CL-08:CL-08-HU-07, CL-08:CL-08-HU-18, CL-08:CL-08-HU-20, CL-09:CL-09-D023, CL-09:CL-09-D033, CL-10:CL-10-HU032.

## EXT-RAILS-11 — Legal notification proof

Status: OPEN. Source family: RAILS-11.

Notification intents and credential generations

Required evidence / remaining: Source legal owner must approve notice requirements and sufficiency.

Affected source records: CL-07:CL-07-H22, CL-09:CL-09-D004, CL-09:CL-09-D006, CL-09:CL-09-D024, CL-09:CL-09-D028, CL-09:CL-09-D055, CL-09:CL-09-D058.

## EXT-RAILS-18 — Geocoder and KMS activation

Status: OPEN. Source family: RAILS-18.

Privacy owner inventory and private export handoff

Required evidence / remaining: Geocoder and key provider/account/purpose/capability qualification required.

Affected source records: CL-08:U-08-20.

## EXT-RAILS-27 — Prize legal policy and tax recognition

Status: OPEN. Source family: RAILS-27.

Sweepstakes owns immutable official-rules content/hash/version and binds Consent proof to the version actually accepted. Retain rule evidence through owner-authorized Media access; remote URL alone is insufficient. Each draw has one immutable run generation, frozen entry identities and eligibility/source revisions, algorithm/version, randomness provenance, actor/correlation, selection count, and selected-entry-to-winning linkage. Use referential integrity where retention permits; otherwise retain validated immutable evidence references. Freeze under serialized owner control, then execute once. Retry resumes/reconciles that run and cannot obtain a more favorable new random selection. Issuance/correction before freeze is audited; post-freeze change preserves the original population/run and requires a separately approved correction/redraw policy.

Ratify PrizeDrawing graph draft→active/cancelled; active→closed/cancelled; closed→drawing/cancelled; drawing→completed only with complete immutable run/winning evidence. completed/cancelled are ordinary terminal states. Failed or unknown execution remains recoverable within the same run; no automatic redraw. EntryMethod graph active↔paused; active/paused→retired; retired is terminal; changes remain subject to drawing freeze/rules.

PrizeWinning: pending_confirmation→pending_tax when tax evidence is required; pending_confirmation/pending_tax→approved only after applicable current confirmation, eligibility, tax and Hold gates. Any nonterminal prefulfillment state may become blocked on an applicable Hold; authorized reevaluation after release returns to pending_confirmation, pending_tax or approved according to current missing requirements, never directly fulfilled. approved→fulfilled requires actual effect receipt. cancelled/forfeited require explicit applicable official-rules authority and no unresolved delivery effect; no timer or notice-delivery inference supplies that authority. fulfilled/cancelled/forfeited remain ordinary terminal; a permitted correction is distinct retained evidence, not overwrite.

Payment owns tax-subject + jurisdiction + tax-year + currency aggregation and action-specific tax readiness. Prize/reward owners provide immutable actual value/fulfillment source facts and reconcile corrected facts by source identity/revision. Preserve jurisdiction; current user/year/currency-only summary uniqueness is insufficient and requires a coordinated migration before tax reporting. Approved external policy must still supply tax recognition moment, applicable thresholds, geographic/age eligibility, claim windows and redraw/forfeiture criteria. None are invented here. Randomness adapter proof, legal policy and provider validation are scoped activation prerequisites, not evidence that the architecture is implemented. Paid status, points spending and purchased entries must not improve odds; preserve P04/P05.

Required evidence / remaining: Approved tax recognition/jurisdiction/eligibility rules, redraw conditions, Payment contract and migration grain.

Affected source records: CL-10:U-CL10-11, CL-10:U-CL10-12, CL-10:U-GR-15, CL-10:CL-10-R009, CL-10:CL-10-HU028, CL-10:CL-10-HU047.

## EXT-DB — Canonical database provenance

Status: OPEN; posture D. Integration owner must obtain target database identity/environment, data-preservation constraints, deployed migration ledger and schema-only comparison against repository before selecting baseline/continuation/recovery. Static 177-model versus 53-created-table coverage is not evidence of deployed mismatch. No live credentials or user data belongs in this register. See database-readiness.md.

## Evidence completion protocol

Record owner, precise enabled path, approved policy/configuration version, environment/account/jurisdiction scope where applicable, authoritative evidence reference, verification date, restrictions and review trigger. Update affected contract qualification entries only after bilateral tests and actual capability evidence; an external gate being closed does not independently freeze an interface. Keep unsupported paths unavailable and retain unrelated qualified work.
