# Remaining semantics review

Date: 2026-10-09. Scope: FH-08, COM-04/FH-26, FH-14 and FH-29. This is an integration proposal, not an applied owner amendment, wire freeze, runtime qualification or migration approval. Canonical authority remains the platform-rulings ledger and the corresponding owner architectures. Historical record text is evidence, not a reason to reopen approved decisions.

## Disposition summary

| Source facets | One underlying contract family | Existing decisions that close ownership/policy | Remaining architecture proposal | Activation gates |
|---|---|---|---|---|
| FH-08: CL-02:D014/D015; CL-06-U008 | Context-owned taxonomy assignment, affected-target enumeration and minimized AI inputs | WA-R033/034/043: contextual owners write joins; AI suggests; source owners enumerate; Candidate excludes raw resume/application content | The source descriptor and enumerator below | Per-target serializer/cursor fixtures, approved taxonomy seeds and qualified AI provider configuration |
| COM-04: CL04-U051/CL-05-U004; FH-26: CL-06-U040/U068 | CF-LOCATION: purpose-specific source facts and disclosure | WA-R025/047/049: Location decides; source owns facts; Booking caches do not authorize; hiring is a separate purpose | Typed source/facts catalog and revocation protocol below | Numerical fuzzy settings, jurisdiction/retention dispositions, qualified geocoder/key management, bilateral race fixtures |
| FH-14: CL-06-U009/U018/U063/U065 | Hiring stewardship and compatibility migration | WA-R007/008/043/045/046: retained compatibility is not authority; owner histories and contextual joins retain ownership | Registry correction now; staged forward migration below | Database posture D; actual schema/data inventory, preservation and replay proof |
| FH-29: CL-06-U058 | Interview parent-bound Video access timing | WA-R023/042/046/051: no early join without policy, current participant authorization, credential lifetime bounded by parent interval | Half-open interval and credential expiry calculation below | Video security TTL configuration and provider revocation/expiry qualification |

No new product-owner choice is required to adopt these architecture proposals. A request to expand launch scope (early interview joining, unrestricted candidate AI input, another exact-location recipient or an unsupported source) would be a new choice; it is not implied by an unfinished evidence row. Numerical settings already delegated by the existing rulings remain explicit configuration gates, not fabricated approved values.

## FH-08: concrete adapter contract

The CL-06 contextual join-write question is already resolved by WA-R043 and should close by that existing ruling. D014/D015 should not remain an abstract universal DTO discussion: adopt a versioned source descriptor per owner/type/purpose. The internal envelope is:

`descriptorVersion, sourceOwner, targetType, targetId, sourceToken, purpose, allowedFieldSetVersion, sensitivityCategories, policyVersions, fields`.

`sourceToken` is owner-issued opaque currentness evidence. `fields` is validated against the descriptor's closed schema; extra fields are rejected. IDs, policy evidence and actor context are internal routing/authorization metadata, not automatically provider payload. Source owner authorizes the specific purpose on current data; AI and Search do not obtain direct repository access. Candidate discovery opt-in is a Search participation fact, not consent for every AI processing purpose. No extraction permission is inferred from submitting an application.

Proposed launch AI field allowlist (semantic DTO names; physical field mapping belongs to each owner):

| Target | Owner-projected allowed provider fields | Explicitly excluded |
|---|---|---|
| ProfessionalProfile | `classificationText` derived from authorized professional bio; `acceptedCategoryIds`; `acceptedTagIds` | User/account identifiers, contact/address, licenses/background evidence, transactions, private messages |
| Offering | `title`, `summary`, `classificationText` derived from authorized offering description; `acceptedCategoryIds`; `acceptedTagIds` | Buyer or delivery facts, exact service address, prices/payment details, private attachments or client data |
| Organization | `classificationText` derived from authorized business description; `acceptedCategoryIds`; `acceptedTagIds` | EIN, representative identity, verification evidence, memberships, applicant records, exact address |
| Job | `title`, `classificationText` derived from authorized job description; `acceptedCategoryIds`; `acceptedTagIds` | Applications, recruiter notes, compensation/payment evidence, private interview details and credentials |
| CandidateProfile | `normalizedSkillLabels`, `normalizedExperienceCategories`; accepted canonical category/tag references where owned and relevant | Name/contact/address, employer-identifying narrative, raw resume, application/cover-letter text, parser raw output, recruiter decisions |

`classificationText` is a source-owned, purpose-approved minimized projection, never an alias that permits forwarding an entire description unchanged without sensitivity review. Text lengths, array bounds and allowed language/output schema are explicit versioned serializer limits. Missing source authority, unqualified Healthcare context, unsupported target/purpose or unsafe text returns denied/unavailable; it must not broaden the allowlist. Gig remains unsupported for AI under WA-R033. Both `taxonomy_suggestion` and `skill_extraction` require explicit target-purpose registration; listing a target does not automatically enable both. No new model/table or forced collection of missing Candidate experience categories is required: unsupported input is omitted or the operation is unavailable.

Affected-target enumeration request:

`requestId, ownerScope, operationPurpose, termIdsWithExpectedVersions, descriptorVersion, snapshotToken?, cursor?, boundedPageSize`.

Response:

`ownerScope, snapshotToken, pageIdentity, targets[{targetType,targetId,sourceToken,assignmentToken}], nextCursor?, complete, checkpointEvidence`.

The first request establishes a snapshot/high-watermark; every page and cursor is bound to that scope, filter and snapshot. The owner enumerates its own joins, including currently nonpublic targets affected by a Taxonomy change when needed for owner revalidation; it does not expose arbitrary source content. Retries of a page are stable. Expired/incompatible cursor returns restart-required and does not masquerade as an empty page. `complete=true` plus a null continuation is explicit completion evidence, not a timeout interpretation. Concurrent changes require owner change-feed reconciliation or a new comparable snapshot; absence from an incomplete walk never proves deletion. Search/AI work deduplicates by target and source/assignment version. Taxonomy merge waits for required owner receipts rather than assuming enumerator dispatch completed the merge.

Assignment command is contextual-owner specific: `commandId, targetId, expectedSourceToken, expectedAssignmentToken, proposedTermIdsAndVersions, proposalReference?, actorAndReviewEvidence`. It rechecks Taxonomy effective activity/category compatibility and current owner authority, writes accepted joins plus immutable receipt/outbox atomically, then returns `applied|already_applied|conflict|denied|invalid_terms|unavailable` with resulting source/assignment token and receipt. Same key/different fingerprint conflicts. No consumer writes a foreign join. Physical DTO classes, cursor encoding and transport are deferred implementation details; the bounded schema, currentness/completion semantics and owner responsibilities are architectural requirements.

## COM-04 and FH-26: one Location contract, distinct purposes

The source registry is closed and purpose-qualified. Register `sourceOwner, targetType, permittedPurposes, sourceFactQueryVersion, projectionFieldSetVersion, sensitivityPolicyVersion`. Exact facts remain at the source owner; Location owns reveal/current decision/history and public precision. A target existing in Search or Prisma does not register it for location exposure.

Use these minimum owner-query responsibilities:

- Order supplies current Order revision, applicable service/session authorization identity, buyer and performing Professional identities, current cancellation/refund/dispute restrictions and source reference. It does not decide Location permission.
- Booking supplies current Booking revision, its consistent Order/session reference, current service-performance state, in-person mode, authorized start/end and explicitly approved overtime boundary, performing participant references and location source identity/revision. A reported completion/no-show remains distinguishable from adjudicated performance; no Location decision creates a financial or Review consequence. Missing evidence of an active authorized service denies new exact disclosure.
- The location source supplies source ID/revision, protected exact address/coordinate fields and purpose applicability. Location retains only the protected material required by its approved processing contract; no implied permanent duplicate address registry.
- Hiring supplies Organization/Job/Candidate public-projection eligibility and approved coarse source reference. Interview separately supplies current schedule revision, interval, participant/revocation facts, protected meeting-location/phone source references and approved interview purpose. Public candidate exposure additionally requires current P17 opt-in.

A service reveal request is `viewerUserId, purpose=service_performance, typedServiceContext, sourceReference, requestId`. Both attached Order and Booking must resolve consistently. Location obtains fresh owner tokens, Role/participant proof, applicable policy and current time; it applies WA-R025's performing-Professional/in-person/active-window predicate. Before returning exact fields, obtain WA-R023 durable access proof bound to viewer, purpose, source/service tokens, Location decision revision and field scope. A caller-provided source revision is a precondition, never the authoritative facts. Missing, conflicting or unqueryable facts deny disclosure.

The response contains only approved exact fields, decision/proof reference, bound versions and `validUntil` no later than the authorized service boundary or applicable proof/policy validity. It is not a bearer authorization for another viewer or future read. Query-time authorization is mandatory; event-only cache invalidation is insufficient. Source relocation, cancellation, disqualifying refund/dispute, service completion, participant change, policy change or Privacy restriction invalidates the current decision. Reschedule requires fresh evaluation. Owner change events carry source/context identity and new revision/change kind without exact coordinates, phone or address. Stale allow writes and replayed allow events cannot overtake revocation. Booking caches invalidate by matching source/revision and never reveal on their own.

Interview exact meeting location/phone uses a distinct `interview_participation` field policy: current authorized participants or purpose-authorized support, fresh Interview/Role facts, WA-R023 proof and the owning restriction/retention rules under WA-R047. It never inherits the service-Professional-only predicate or grants all recruiters access. Its supported field map is `meetingLocation` and/or `meetingPhone`, individually authorized; invitation notifications contain a secure contextual link, not those values. Public Organization/Job/Candidate output is limited to Location-approved coarse locality/region/country and optional fuzzy coordinates under a configured policy. Names of locality fields do not promise a minimum anonymity radius. Unsupported target/purpose or unset numerical policy returns unavailable; Search cannot compute a substitute.

Keep real gates: fuzzy radius/precision/refresh/expiry configuration per purpose and source; approved legal retention/disposition for source fields and reveal history; geocoder account/region/processing terms; key lifecycle qualification; bilateral concurrency/denial fixtures. These are not new independent owner assignments. COM-04 and FH-26 must remain linked to CF-LOCATION and share its contract/version evidence.

## FH-14: correct inventory now, migrate only on evidence

Close contextual JobMedia stewardship and history ownership against WA-R043/045/046 when the canonical inventory states: Hiring owns JobMedia and Organization/Job history; Candidate owns Candidate/Application media joins and application-view/access events; Interview owns its participant/current-selection and invitation/response history. Media still owns bytes/readiness/access. Correct the registry without pretending that a schema migration ran.

For legacy resume URL, Organization logo/verification summaries and redundant Organization/view-event links: retain read-only compatibility or quarantined historical values; stop new authority reads/writes. Introduce explicit canonical reference/history selection, shadow-compare/backfill from proven owner IDs with reconciliation receipts, and quarantine ambiguous historical ownership. Do not infer an Organization from name, current recruiter membership or the first relation in a many-to-many collection. View evidence must preserve the Organization/actor context actually bound at the time; current memberships do not rewrite history. A redundant link may remain inert pending provenance analysis. Removal requires proven completeness, preserved required history and no remaining authoritative consumers.

Sequence: owner schema proposal and all affected contracts → integration-owned static diff and provenance inventory → forward additive constraints/history/reference support → idempotent backfill and ambiguity report → owner-read cutover with parity evidence → separately reviewed removal only after retention/preservation proof. Database posture D blocks choosing/applying a baseline or deployment migration until target identity, preservation requirements, migration ledger and schema comparison are available. This is EXTERNAL_REQUIREMENT for migration activation, not an unresolved product question and not a reason to leave registry stewardship undecided. Exact tables/indexes and batch mechanics are deferred to the coordinated migration owner. No destructive script is authorized here.

## FH-29: timing can close without inventing a TTL

Apply the existing no-early-join launch rule as `startsAt <= serverNow < endsAt`, for the current scheduled Interview revision and accepted, nonrevoked participant. There is no implicit post-end or pre-start grace. Invitation acceptance still requires a future slot under P18; that is distinct from joining an already accepted current slot. Application terminal/restricted status, Interview cancellation/reschedule or participant revocation immediately blocks new credential issuance despite a previously accepted invitation.

Video resolves its current session generation and parent facts at issuance. Set `expiresAt = min(serverNow + configuredSecurityTTL, interview.endsAt, currentAuthorityEvidenceExpiry, applicableProviderMaximumExpiry)` using only applicable finite limits. Missing/invalid TTL or provider inability to honor the required bound disables issuance. The credential binds viewer, typed Interview ID, schedule revision, session generation and audience; never reuse predecessor credentials after reschedule. Clock tolerance may only make denial more conservative unless an explicit approved policy permits otherwise. Provider callbacks cannot extend parent authority.

Provider revocation/expiry capability and disconnect semantics must be qualified; a short TTL alone must not be falsely represented as immediate revocation of an already connected session. Unsupported mandatory revocation remains a provider activation gate. Numerical security TTL, provider clock handling and maximum session limits belong to Video security configuration and evidence, not a new product vote. Any future early-join interval requires an explicit policy version and does not reopen P18's no timer invitation expiry.

## Verification required before integration closure

Apply accepted text to actual owners and consumers first, then record the existing/new ruling references in the canonical handoff ledger. Verify allowlist exclusion and unsupported purpose, interrupted/cursor-stale enumeration, assignment receipt retry/conflict, stale location allow after revocation, mismatched Order/Booking, Candidate opt-out, support scope, exact-data absence from public/notification payloads, migration ambiguity quarantine, interval boundary and reschedule/participant-revocation races. These are required future contract fixtures; this review did not run product/provider/database tests or claim any Shared Operation frozen.
