# Physical model disposition ledger — review only

All 177 original models accounted for; 214 staged candidate models, 40 in the F0 parent-FK closure. Exact field/FK/index/change/evidence/access rows are in greenfield-model-security-inventory.json → physical_candidate_review. No SQL is generated or executed.

## admin_review_compliance_hold

### ComplianceHold

Independent protective source cause and release cycle, never payment dispatch.

- Object: `app.compliance_holds`. Class: AUTHORITATIVE_OWNER_STATE. Stage: LATER_OWNER_ORDERED_SLICE.
- Stable key: id. Foreign keys: user → User?, professionalProfile → ProfessionalProfile?, order → Order?, releasedByUser → User?.
- Physical changes: DB-C02: restrictive immutable-key FKs; Privacy deletes/anonymizes explicitly in reviewed order; DB-C03: UTC-capable timestamptz(6) physical instants; DB-C03: owner-local CAS revision; no global ordering; R059/R075: independent source cause and generation; release cannot waive another cause; SQL-08: server transaction identity for atomic source/evidence/message checks.
- Required SQL/access checks: SQL-01, SQL-02, SQL-03, SQL-04, SQL-08, SQL-16. Owner Privacy executor: admin_review_compliance_hold.

## audit_event_ledger

### AccessAuditLog

Durable protected-disclosure proof before secret delivery.

- Object: `app.access_audit_logs`. Class: IMMUTABLE_EVIDENCE_OR_RECEIPT. Stage: F0_FOUNDATION.
- Stable key: id. Foreign keys: actorUser → User?.
- Physical changes: DB-C02: restrictive immutable-key FKs; Privacy deletes/anonymizes explicitly in reviewed order; DB-C03: UTC-capable timestamptz(6) physical instants; SQL-08: server transaction identity for atomic source/evidence/message checks.
- Required SQL/access checks: SQL-01, SQL-02, SQL-03, SQL-04, SQL-08, SQL-16. Owner Privacy executor: audit_event_ledger.

### AuditEvent

Append-only bounded decision/effect audit intent and retained evidence.

- Object: `app.audit_events`. Class: IMMUTABLE_EVIDENCE_OR_RECEIPT. Stage: F0_FOUNDATION.
- Stable key: id. Foreign keys: none; typed registered descriptor scope is explicit in the SQL companion.
- Physical changes: DB-C03: UTC-capable timestamptz(6) physical instants; SQL-08: server transaction identity for atomic source/evidence/message checks.
- Required SQL/access checks: SQL-01, SQL-02, SQL-03, SQL-04, SQL-08, SQL-16. Owner Privacy executor: audit_event_ledger.

## booking_calendar

### BookingSlotLock

Exclusive interval reservation and authoritative hold-to-lock relation.

- Object: `app.booking_slot_locks`. Class: AUTHORITATIVE_OWNER_STATE. Stage: LATER_OWNER_ORDERED_SLICE.
- Stable key: id. Foreign keys: customerProfile → CustomerProfile, professionalProfile → ProfessionalProfile, buyerUser → User?, order → Order?, bookingHold → BookingHold?.
- Physical changes: DB-C02: restrictive immutable-key FKs; Privacy deletes/anonymizes explicitly in reviewed order; DB-C03: UTC-capable timestamptz(6) physical instants; DB-C03: owner-local CAS revision; no global ordering; DB-C06/R076: fresh buyer flows bind SH-004 Customer identity; old database untouched; DB-C06: coherent commercial buyer relation; DB-C07/R012: early release is a policy window, never request ordering; SQL-08: server transaction identity for atomic source/evidence/message checks.
- Required SQL/access checks: SQL-01, SQL-02, SQL-03, SQL-04, SQL-08, SQL-13, SQL-16. Owner Privacy executor: booking_calendar.

### CalendarConnection

Booking-owned scoped calendar consent/account capability and revocation generation.

- Object: `app.calendar_connections`. Class: AUTHORITATIVE_OWNER_STATE. Stage: LATER_OWNER_ORDERED_SLICE.
- Stable key: id. Foreign keys: professionalProfile → ProfessionalProfile, consentLog → ConsentLog?.
- Physical changes: DB-C02: restrictive immutable-key FKs; Privacy deletes/anonymizes explicitly in reviewed order; DB-C03: UTC-capable timestamptz(6) physical instants; DB-C03: owner-local CAS revision; no global ordering; SQL-08: server transaction identity for atomic source/evidence/message checks.
- Required SQL/access checks: SQL-01, SQL-02, SQL-03, SQL-04, SQL-08, SQL-13, SQL-16. Owner Privacy executor: booking_calendar.

### AvailabilityRule

Versioned timezone-aware availability input, not an eligibility grant.

- Object: `app.availability_rules`. Class: AUTHORITATIVE_OWNER_STATE. Stage: LATER_OWNER_ORDERED_SLICE.
- Stable key: id. Foreign keys: professionalProfile → ProfessionalProfile.
- Physical changes: DB-C02: restrictive immutable-key FKs; Privacy deletes/anonymizes explicitly in reviewed order; DB-C03: UTC-capable timestamptz(6) physical instants; DB-C03: owner-local CAS revision; no global ordering; SQL-08: server transaction identity for atomic source/evidence/message checks.
- Required SQL/access checks: SQL-01, SQL-02, SQL-03, SQL-04, SQL-08, SQL-13, SQL-16. Owner Privacy executor: booking_calendar.

### BusyWindow

Minimized provider busy-time projection, never private event content by default.

- Object: `app.busy_windows`. Class: AUTHORITATIVE_OWNER_STATE. Stage: LATER_OWNER_ORDERED_SLICE.
- Stable key: id. Foreign keys: professionalProfile → ProfessionalProfile, calendarConnection → CalendarConnection?.
- Physical changes: DB-C02: restrictive immutable-key FKs; Privacy deletes/anonymizes explicitly in reviewed order; DB-C03: UTC-capable timestamptz(6) physical instants; DB-C03: owner-local CAS revision; no global ordering; SQL-08: server transaction identity for atomic source/evidence/message checks.
- Required SQL/access checks: SQL-01, SQL-02, SQL-03, SQL-04, SQL-08, SQL-13, SQL-16. Owner Privacy executor: booking_calendar.

### BookingOrchestrationRun

Booking workflow projection over the single shared runner.

- Object: `app.booking_orchestration_runs`. Class: PROJECTION_NOT_AUTHORITY. Stage: LATER_OWNER_ORDERED_SLICE.
- Stable key: id. Foreign keys: booking → Booking, order → Order?, triggeredByUser → User?.
- Physical changes: DB-C02: restrictive immutable-key FKs; Privacy deletes/anonymizes explicitly in reviewed order; DB-C03: UTC-capable timestamptz(6) physical instants; DB-C03: owner-local CAS revision; no global ordering; SQL-08: server transaction identity for atomic source/evidence/message checks.
- Required SQL/access checks: SQL-01, SQL-02, SQL-03, SQL-04, SQL-08, SQL-13, SQL-16. Owner Privacy executor: booking_calendar.

### BookingOrchestrationStep

Source-specific desired effect/receipt reference; not another executable queue.

- Object: `app.booking_orchestration_steps`. Class: PROJECTION_NOT_AUTHORITY. Stage: LATER_OWNER_ORDERED_SLICE.
- Stable key: id. Foreign keys: run → BookingOrchestrationRun, booking → Booking.
- Physical changes: DB-C02: restrictive immutable-key FKs; Privacy deletes/anonymizes explicitly in reviewed order; DB-C03: UTC-capable timestamptz(6) physical instants; DB-C03: owner-local CAS revision; no global ordering; SQL-08: server transaction identity for atomic source/evidence/message checks.
- Required SQL/access checks: SQL-01, SQL-02, SQL-03, SQL-04, SQL-08, SQL-13, SQL-16. Owner Privacy executor: booking_calendar.

### Booking

Purchased appointment source with coherent buyer/order/session and parent revisions.

- Object: `app.bookings`. Class: AUTHORITATIVE_OWNER_STATE. Stage: LATER_OWNER_ORDERED_SLICE.
- Stable key: id. Foreign keys: customerProfile → CustomerProfile, order → Order, buyerUser → User, professionalProfile → ProfessionalProfile, rescheduledFromBooking → Booking?, calendarConnection → CalendarConnection?, bookingHold → BookingHold?, slotLock → BookingSlotLock?.
- Physical changes: DB-C02: restrictive immutable-key FKs; Privacy deletes/anonymizes explicitly in reviewed order; DB-C03: UTC-capable timestamptz(6) physical instants; DB-C03: owner-local CAS revision; no global ordering; DB-C06/R076: fresh buyer flows bind SH-004 Customer identity; old database untouched; DB-C06: coherent commercial buyer relation; DB-C07/R012: early release is a policy window, never request ordering; R042: retain one successor and current appointment audience; DB-C09: no unapproved numerical overtime/completion rule inferred from schema default; SQL-08: server transaction identity for atomic source/evidence/message checks.
- Required SQL/access checks: SQL-01, SQL-02, SQL-03, SQL-04, SQL-08, SQL-13, SQL-16. Owner Privacy executor: booking_calendar.

### BookingHold

Preliminary slot hold; lock relation comes from BookingSlotLock.

- Object: `app.booking_holds`. Class: AUTHORITATIVE_OWNER_STATE. Stage: LATER_OWNER_ORDERED_SLICE.
- Stable key: id. Foreign keys: customerProfile → CustomerProfile, order → Order?, buyerUser → User, professionalProfile → ProfessionalProfile.
- Physical changes: DB-C02: restrictive immutable-key FKs; Privacy deletes/anonymizes explicitly in reviewed order; DB-C03: UTC-capable timestamptz(6) physical instants; DB-C03: owner-local CAS revision; no global ordering; DB-C06/R076: fresh buyer flows bind SH-004 Customer identity; old database untouched; DB-C06: coherent commercial buyer relation; DB-C07/R076: BookingSlotLock.bookingHoldId is the single authoritative relation; DB-C07/R012: early release is a policy window, never request ordering; SQL-08: server transaction identity for atomic source/evidence/message checks.
- Required SQL/access checks: SQL-01, SQL-02, SQL-03, SQL-04, SQL-08, SQL-13, SQL-16. Owner Privacy executor: booking_calendar.

### BookingEvent

Retained Booking transition/outcome evidence; no-show is not money authority.

- Object: `app.booking_events`. Class: IMMUTABLE_EVIDENCE_OR_RECEIPT. Stage: LATER_OWNER_ORDERED_SLICE.
- Stable key: id. Foreign keys: booking → Booking.
- Physical changes: DB-C02: restrictive immutable-key FKs; Privacy deletes/anonymizes explicitly in reviewed order; DB-C03: UTC-capable timestamptz(6) physical instants; SQL-08: server transaction identity for atomic source/evidence/message checks.
- Required SQL/access checks: SQL-01, SQL-02, SQL-03, SQL-04, SQL-08, SQL-13, SQL-16. Owner Privacy executor: booking_calendar.

### ProcessedCalendarEvent

Verified account-scoped calendar event fingerprint and disposition.

- Object: `app.processed_calendar_events`. Class: IMMUTABLE_EVIDENCE_OR_RECEIPT. Stage: LATER_OWNER_ORDERED_SLICE.
- Stable key: id. Foreign keys: calendarConnection → CalendarConnection?, professionalProfile → ProfessionalProfile?, booking → Booking?.
- Physical changes: DB-C02: restrictive immutable-key FKs; Privacy deletes/anonymizes explicitly in reviewed order; DB-C03: UTC-capable timestamptz(6) physical instants; DB-C14/R018: verified provider/account/event identity and fingerprint; SQL-08: server transaction identity for atomic source/evidence/message checks.
- Required SQL/access checks: SQL-01, SQL-02, SQL-03, SQL-04, SQL-08, SQL-13, SQL-16. Owner Privacy executor: booking_calendar.

### CalendarDesiredMapping

Booking-owned desired/applied provider mapping bound to exactly one Booking or Interview parent generation.

- Object: `app.calendar_desired_mapping`. Class: AUTHORITATIVE_OWNER_STATE. Stage: LATER_OWNER_ORDERED_SLICE.
- Stable key: id. Foreign keys: booking → Booking?, interview → JobInterview?, connection → CalendarConnection.
- Physical changes: DB-C08; SQL-08: server transaction identity for atomic source/evidence/message checks.
- Required SQL/access checks: SQL-01, SQL-02, SQL-03, SQL-04, SQL-08, SQL-13, SQL-16. Owner Privacy executor: booking_calendar.

## candidate_application_resume_privacy

### CandidateProfile

One-to-one applicant identity with private resume and opt-in discovery.

- Object: `app.candidate_profiles`. Class: AUTHORITATIVE_OWNER_STATE. Stage: F0_FOUNDATION.
- Stable key: id. Foreign keys: user → User.
- Physical changes: DB-C02: restrictive immutable-key FKs; Privacy deletes/anonymizes explicitly in reviewed order; DB-C03: UTC-capable timestamptz(6) physical instants; DB-C03: owner-local CAS revision; no global ordering; DB-C05: owner erasure/restriction generation prevents resurrection; R045: discovery is opt-in; private by default; R045: affirmative participation and its source revision, not inferred visibility; R045/R050: protected resume bytes use explicit Media attachments, never a reusable URL field; SQL-08: server transaction identity for atomic source/evidence/message checks.
- Required SQL/access checks: SQL-01, SQL-02, SQL-03, SQL-04, SQL-08, SQL-16, SQL-18. Owner Privacy executor: candidate_application_resume_privacy.

### CandidateCategory

Candidate-owned selected category relationship.

- Object: `app.candidate_categories`. Class: AUTHORITATIVE_OWNER_STATE. Stage: LATER_OWNER_ORDERED_SLICE.
- Stable key: candidateProfileId, categoryId. Foreign keys: candidateProfile → CandidateProfile, category → TaxonomyCategory.
- Physical changes: DB-C02: restrictive immutable-key FKs; Privacy deletes/anonymizes explicitly in reviewed order; SQL-08: server transaction identity for atomic source/evidence/message checks.
- Required SQL/access checks: SQL-01, SQL-02, SQL-03, SQL-04, SQL-08, SQL-16, SQL-18. Owner Privacy executor: candidate_application_resume_privacy.

### CandidateTag

Candidate-owned controlled tag assignment and provenance.

- Object: `app.candidate_tags`. Class: AUTHORITATIVE_OWNER_STATE. Stage: LATER_OWNER_ORDERED_SLICE.
- Stable key: candidateProfileId, tagId. Foreign keys: candidateProfile → CandidateProfile, tag → TaxonomyTag.
- Physical changes: DB-C02: restrictive immutable-key FKs; Privacy deletes/anonymizes explicitly in reviewed order; DB-C03: UTC-capable timestamptz(6) physical instants; SQL-08: server transaction identity for atomic source/evidence/message checks.
- Required SQL/access checks: SQL-01, SQL-02, SQL-03, SQL-04, SQL-08, SQL-16, SQL-18. Owner Privacy executor: candidate_application_resume_privacy.

### JobApplication

Candidate-owned accepted application and stage; no automated ranking.

- Object: `app.job_applications`. Class: AUTHORITATIVE_OWNER_STATE. Stage: LATER_OWNER_ORDERED_SLICE.
- Stable key: id. Foreign keys: job → Job, candidateProfile → CandidateProfile.
- Physical changes: DB-C02: restrictive immutable-key FKs; Privacy deletes/anonymizes explicitly in reviewed order; DB-C03: UTC-capable timestamptz(6) physical instants; DB-C05: owner erasure/restriction generation prevents resurrection; SQL-08: server transaction identity for atomic source/evidence/message checks.
- Required SQL/access checks: SQL-01, SQL-02, SQL-03, SQL-04, SQL-08, SQL-16, SQL-18. Owner Privacy executor: candidate_application_resume_privacy.

### JobApplicationViewEvent

Immutable purpose-bound protected application-view evidence.

- Object: `app.job_application_view_events`. Class: IMMUTABLE_EVIDENCE_OR_RECEIPT. Stage: LATER_OWNER_ORDERED_SLICE.
- Stable key: id. Foreign keys: jobApplication → JobApplication, viewedByUser → User?, organization → Organization?.
- Physical changes: DB-C02: restrictive immutable-key FKs; Privacy deletes/anonymizes explicitly in reviewed order; DB-C03: UTC-capable timestamptz(6) physical instants; SQL-08: server transaction identity for atomic source/evidence/message checks.
- Required SQL/access checks: SQL-01, SQL-02, SQL-03, SQL-04, SQL-08, SQL-16, SQL-18. Owner Privacy executor: candidate_application_resume_privacy.

### JobApplicationMedia

Candidate-owned explicit application/resume attachment.

- Object: `app.job_application_media`. Class: AUTHORITATIVE_OWNER_STATE. Stage: LATER_OWNER_ORDERED_SLICE.
- Stable key: jobApplicationId, mediaId. Foreign keys: jobApplication → JobApplication, media → MediaAsset.
- Physical changes: DB-C02: restrictive immutable-key FKs; Privacy deletes/anonymizes explicitly in reviewed order; DB-C03: UTC-capable timestamptz(6) physical instants; SQL-08: server transaction identity for atomic source/evidence/message checks.
- Required SQL/access checks: SQL-01, SQL-02, SQL-03, SQL-04, SQL-08, SQL-16, SQL-18. Owner Privacy executor: candidate_application_resume_privacy.

### CandidateSearchProjection

Opt-in source-generation-bound minimized discovery projection.

- Object: `app.candidate_search_projections`. Class: PROJECTION_NOT_AUTHORITY. Stage: LATER_OWNER_ORDERED_SLICE.
- Stable key: id. Foreign keys: candidateProfile → CandidateProfile, resumeParseResult → ResumeParseResult?.
- Physical changes: DB-C02: restrictive immutable-key FKs; Privacy deletes/anonymizes explicitly in reviewed order; DB-C03: UTC-capable timestamptz(6) physical instants; DB-C03: owner-local CAS revision; no global ordering; DB-C05: owner erasure/restriction generation prevents resurrection; R045: stale extraction cannot republish withdrawn discovery; SQL-08: server transaction identity for atomic source/evidence/message checks.
- Required SQL/access checks: SQL-01, SQL-02, SQL-03, SQL-04, SQL-08, SQL-16, SQL-18. Owner Privacy executor: candidate_application_resume_privacy.

### ResumeParseResult

Protected source/generation-bound extraction only, not ranking or eligibility.

- Object: `app.resume_parse_results`. Class: AUTHORITATIVE_OWNER_STATE. Stage: LATER_OWNER_ORDERED_SLICE.
- Stable key: id. Foreign keys: jobApplication → JobApplication, media → MediaAsset, applicationMedia → JobApplicationMedia.
- Physical changes: DB-C02: restrictive immutable-key FKs; Privacy deletes/anonymizes explicitly in reviewed order; DB-C03: UTC-capable timestamptz(6) physical instants; DB-C03: owner-local CAS revision; no global ordering; SQL-08: server transaction identity for atomic source/evidence/message checks.
- Required SQL/access checks: SQL-01, SQL-02, SQL-03, SQL-04, SQL-08, SQL-16, SQL-18. Owner Privacy executor: candidate_application_resume_privacy.

### ResumeAccessLog

Durable authorized resume-delivery proof before credential issuance.

- Object: `app.resume_access_logs`. Class: IMMUTABLE_EVIDENCE_OR_RECEIPT. Stage: LATER_OWNER_ORDERED_SLICE.
- Stable key: id. Foreign keys: jobApplication → JobApplication, media → MediaAsset, viewerUser → User?, organization → Organization?.
- Physical changes: DB-C02: restrictive immutable-key FKs; Privacy deletes/anonymizes explicitly in reviewed order; DB-C03: UTC-capable timestamptz(6) physical instants; SQL-08: server transaction identity for atomic source/evidence/message checks.
- Required SQL/access checks: SQL-01, SQL-02, SQL-03, SQL-04, SQL-08, SQL-16, SQL-18. Owner Privacy executor: candidate_application_resume_privacy.

### CandidateProfileMedia

Candidate-owned explicit profile Media attachment.

- Object: `app.candidate_profile_media`. Class: AUTHORITATIVE_OWNER_STATE. Stage: LATER_OWNER_ORDERED_SLICE.
- Stable key: candidateProfileId, mediaId. Foreign keys: candidateProfile → CandidateProfile, media → MediaAsset.
- Physical changes: DB-C02: restrictive immutable-key FKs; Privacy deletes/anonymizes explicitly in reviewed order; SQL-08: server transaction identity for atomic source/evidence/message checks.
- Required SQL/access checks: SQL-01, SQL-02, SQL-03, SQL-04, SQL-08, SQL-16, SQL-18. Owner Privacy executor: candidate_application_resume_privacy.

## consent_disclosure

### ConsentLog

Immutable exact presented-content acceptance by subject, context and command identity.

- Object: `app.consent_logs`. Class: IMMUTABLE_EVIDENCE_OR_RECEIPT. Stage: F0_FOUNDATION.
- Stable key: id. Foreign keys: user → User, candidateContentRevisionId → ConsentContentRevision, candidatePresentationId → ConsentPresentation.
- Physical changes: DB-C02: restrictive immutable-key FKs; Privacy deletes/anonymizes explicitly in reviewed order; DB-C03: UTC-capable timestamptz(6) physical instants; DB-C01/R019: scoped repeatable acceptance; new intentional reacceptance has a new key; B010-02: exact accepting user/action/context and rendered presentation hash; DB-C16: typed contentRevisionId binding to canonical ConsentContentRevision; DB-C16: typed presentationId binding to canonical ConsentPresentation; B010-02: composite FK prevents cross-user or cross-content presentation acceptance; SQL-08: server transaction identity for atomic source/evidence/message checks.
- Required SQL/access checks: SQL-01, SQL-02, SQL-03, SQL-04, SQL-05, SQL-08, SQL-16. Owner Privacy executor: consent_disclosure.

### ConsentContentRevision

Immutable exact legal/disclosure content revision and applicability; legal approval never inferred.

- Object: `app.consent_content_revision`. Class: IMMUTABLE_EVIDENCE_OR_RECEIPT. Stage: F0_FOUNDATION.
- Stable key: id. Foreign keys: none; typed registered descriptor scope is explicit in the SQL companion.
- Physical changes: DB-C01; SQL-08: server transaction identity for atomic source/evidence/message checks.
- Required SQL/access checks: SQL-01, SQL-02, SQL-03, SQL-04, SQL-05, SQL-08, SQL-16. Owner Privacy executor: consent_disclosure.

### ConsentPresentation

Immutable actually rendered presentation and exact content/context binding.

- Object: `app.consent_presentation`. Class: IMMUTABLE_EVIDENCE_OR_RECEIPT. Stage: F0_FOUNDATION.
- Stable key: id. Foreign keys: content → ConsentContentRevision, subject → User.
- Physical changes: DB-C01; B010-02: immutable per-user action/context presentation and composite acceptance binding; SQL-08: server transaction identity for atomic source/evidence/message checks.
- Required SQL/access checks: SQL-01, SQL-02, SQL-03, SQL-04, SQL-05, SQL-08, SQL-16. Owner Privacy executor: consent_disclosure.

### ConsentDisposition

Append-only decline/withdrawal/reacceptance disposition without overwriting old acceptance.

- Object: `app.consent_disposition`. Class: IMMUTABLE_EVIDENCE_OR_RECEIPT. Stage: F0_FOUNDATION.
- Stable key: id. Foreign keys: proof → ConsentLog?, subject → User, presentation → ConsentPresentation.
- Physical changes: DB-C01; SQL-08: server transaction identity for atomic source/evidence/message checks.
- Required SQL/access checks: SQL-01, SQL-02, SQL-03, SQL-04, SQL-05, SQL-08, SQL-16. Owner Privacy executor: consent_disclosure.

## content_moderation_legal_notice

### Report

Retained source report and moderation intake, not a proved violation.

- Object: `app.reports`. Class: AUTHORITATIVE_OWNER_STATE. Stage: LATER_OWNER_ORDERED_SLICE.
- Stable key: id. Foreign keys: reporter → User?.
- Physical changes: DB-C02: restrictive immutable-key FKs; Privacy deletes/anonymizes explicitly in reviewed order; DB-C03: UTC-capable timestamptz(6) physical instants; DB-C03: owner-local CAS revision; no global ordering; SQL-08: server transaction identity for atomic source/evidence/message checks.
- Required SQL/access checks: SQL-01, SQL-02, SQL-03, SQL-04, SQL-08, SQL-16. Owner Privacy executor: content_moderation_legal_notice.

### LegalNotice

Protected legal intake and reviewed service/applicability evidence.

- Object: `app.legal_notices`. Class: AUTHORITATIVE_OWNER_STATE. Stage: LATER_OWNER_ORDERED_SLICE.
- Stable key: id. Foreign keys: moderationCase → ModerationCase?.
- Physical changes: DB-C02: restrictive immutable-key FKs; Privacy deletes/anonymizes explicitly in reviewed order; DB-C03: UTC-capable timestamptz(6) physical instants; DB-C03: owner-local CAS revision; no global ordering; SQL-08: server transaction identity for atomic source/evidence/message checks.
- Required SQL/access checks: SQL-01, SQL-02, SQL-03, SQL-04, SQL-08, SQL-16. Owner Privacy executor: content_moderation_legal_notice.

### ModerationCase

Authorized moderation case lifecycle and current decision cycle.

- Object: `app.moderation_cases`. Class: AUTHORITATIVE_OWNER_STATE. Stage: LATER_OWNER_ORDERED_SLICE.
- Stable key: id. Foreign keys: report → Report?, openedByUser → User?, assignedAdminUser → User?.
- Physical changes: DB-C02: restrictive immutable-key FKs; Privacy deletes/anonymizes explicitly in reviewed order; DB-C03: UTC-capable timestamptz(6) physical instants; DB-C03: owner-local CAS revision; no global ordering; SQL-08: server transaction identity for atomic source/evidence/message checks.
- Required SQL/access checks: SQL-01, SQL-02, SQL-03, SQL-04, SQL-08, SQL-16. Owner Privacy executor: content_moderation_legal_notice.

### ModerationAction

Immutable typed enforcement/restoration decision, not foreign source mutation.

- Object: `app.moderation_actions`. Class: AUTHORITATIVE_OWNER_STATE. Stage: LATER_OWNER_ORDERED_SLICE.
- Stable key: id. Foreign keys: moderationCase → ModerationCase, actorUser → User?.
- Physical changes: DB-C02: restrictive immutable-key FKs; Privacy deletes/anonymizes explicitly in reviewed order; DB-C03: UTC-capable timestamptz(6) physical instants; SQL-08: server transaction identity for atomic source/evidence/message checks.
- Required SQL/access checks: SQL-01, SQL-02, SQL-03, SQL-04, SQL-08, SQL-16. Owner Privacy executor: content_moderation_legal_notice.

## customer_buyer_profile

### CustomerProfile

One-to-one commercial buyer provisioned before buyer actions.

- Object: `app.customer_profiles`. Class: AUTHORITATIVE_OWNER_STATE. Stage: F0_FOUNDATION.
- Stable key: id. Foreign keys: user → User.
- Physical changes: DB-C02: restrictive immutable-key FKs; Privacy deletes/anonymizes explicitly in reviewed order; DB-C03: UTC-capable timestamptz(6) physical instants; DB-C03: owner-local CAS revision; no global ordering; DB-C05: owner erasure/restriction generation prevents resurrection; SQL-08: server transaction identity for atomic source/evidence/message checks.
- Required SQL/access checks: SQL-01, SQL-02, SQL-03, SQL-04, SQL-08, SQL-16. Owner Privacy executor: customer_buyer_profile.

### CustomerProfileLifecycleEvent

Exact Customer-owned retained lifecycle transition for the first P0-D slice.

- Object: `app.customer_profile_lifecycle_event`. Class: IMMUTABLE_EVIDENCE_OR_RECEIPT. Stage: F0_FOUNDATION.
- Stable key: id. Foreign keys: profile → CustomerProfile, command → RuntimeCommandReceipt, actor → User.
- Physical changes: DB-C16; SQL-08: server transaction identity for atomic source/evidence/message checks.
- Required SQL/access checks: SQL-01, SQL-02, SQL-03, SQL-04, SQL-08, SQL-16. Owner Privacy executor: customer_buyer_profile.

## digital_goods_access

### DigitalGoodsPolicy

Immutable purchase-disclosure/license policy; access never automatically bars refunds.

- Object: `app.digital_goods_policies`. Class: AUTHORITATIVE_OWNER_STATE. Stage: LATER_OWNER_ORDERED_SLICE.
- Stable key: id. Foreign keys: offering → Offering.
- Physical changes: DB-C02: restrictive immutable-key FKs; Privacy deletes/anonymizes explicitly in reviewed order; DB-C03: UTC-capable timestamptz(6) physical instants; DB-C03: owner-local CAS revision; no global ordering; DB-C09/P09: no automatic final-after-access default; policy remains unapproved/gated; DB-C01: retain multiple immutable policy revisions per Offering; DB-C01: exact historical policy with one reviewed current selection; DB-C09: optional tracking permission is never assumed from a policy default; SQL-08: server transaction identity for atomic source/evidence/message checks.
- Required SQL/access checks: SQL-01, SQL-02, SQL-03, SQL-04, SQL-05, SQL-08, SQL-15, SQL-16. Owner Privacy executor: digital_goods_access.

### DigitalGoodsTermsAcceptance

Exact historical purchase/policy/Consent binding.

- Object: `app.digital_goods_terms_acceptances`. Class: AUTHORITATIVE_OWNER_STATE. Stage: LATER_OWNER_ORDERED_SLICE.
- Stable key: id. Foreign keys: user → User, order → Order?, offering → Offering, digitalGoodsPolicy → DigitalGoodsPolicy?, consentLog → ConsentLog?.
- Physical changes: DB-C02: restrictive immutable-key FKs; Privacy deletes/anonymizes explicitly in reviewed order; DB-C03: UTC-capable timestamptz(6) physical instants; SQL-08: server transaction identity for atomic source/evidence/message checks.
- Required SQL/access checks: SQL-01, SQL-02, SQL-03, SQL-04, SQL-05, SQL-08, SQL-15, SQL-16. Owner Privacy executor: digital_goods_access.

### DigitalDownloadAsset

Qualified protected deliverable bound to Offering and exact Media object.

- Object: `app.digital_download_assets`. Class: AUTHORITATIVE_OWNER_STATE. Stage: LATER_OWNER_ORDERED_SLICE.
- Stable key: id. Foreign keys: offering → Offering, productDetails → ProductDetails?, courseDetails → CourseDetails?, mediaAsset → MediaAsset, createdByUser → User?.
- Physical changes: DB-C02: restrictive immutable-key FKs; Privacy deletes/anonymizes explicitly in reviewed order; DB-C03: UTC-capable timestamptz(6) physical instants; DB-C03: owner-local CAS revision; no global ordering; SQL-08: server transaction identity for atomic source/evidence/message checks.
- Required SQL/access checks: SQL-01, SQL-02, SQL-03, SQL-04, SQL-05, SQL-08, SQL-15, SQL-16. Owner Privacy executor: digital_goods_access.

### DigitalDownloadGrant

Current acquired-right/context/object-generation download credential evidence.

- Object: `app.digital_download_grants`. Class: AUTHORITATIVE_OWNER_STATE. Stage: LATER_OWNER_ORDERED_SLICE.
- Stable key: id. Foreign keys: digitalDownloadAsset → DigitalDownloadAsset, user → User, order → Order?.
- Physical changes: DB-C02: restrictive immutable-key FKs; Privacy deletes/anonymizes explicitly in reviewed order; DB-C03: UTC-capable timestamptz(6) physical instants; DB-C03: owner-local CAS revision; no global ordering; DB-C08: protected grant currentness and revocation binding; SQL-08: server transaction identity for atomic source/evidence/message checks.
- Required SQL/access checks: SQL-01, SQL-02, SQL-03, SQL-04, SQL-05, SQL-08, SQL-15, SQL-16. Owner Privacy executor: digital_goods_access.

### DigitalDownloadEvent

Actual download observation, not automatic refund finality.

- Object: `app.digital_download_events`. Class: IMMUTABLE_EVIDENCE_OR_RECEIPT. Stage: LATER_OWNER_ORDERED_SLICE.
- Stable key: id. Foreign keys: digitalDownloadAsset → DigitalDownloadAsset, digitalDownloadGrant → DigitalDownloadGrant?, user → User?, order → Order?.
- Physical changes: DB-C02: restrictive immutable-key FKs; Privacy deletes/anonymizes explicitly in reviewed order; DB-C03: UTC-capable timestamptz(6) physical instants; SQL-08: server transaction identity for atomic source/evidence/message checks.
- Required SQL/access checks: SQL-01, SQL-02, SQL-03, SQL-04, SQL-05, SQL-08, SQL-15, SQL-16. Owner Privacy executor: digital_goods_access.

### ChildDirectedContentDeclaration

Later-phase child-directed declaration; disabled at 18+ launch.

- Object: `app.child_directed_content_declarations`. Class: AUTHORITATIVE_OWNER_STATE. Stage: LATER_LAUNCH_DISABLED.
- Stable key: id. Foreign keys: offering → Offering, digitalGoodsPolicy → DigitalGoodsPolicy?, declaredByUser → User, reviewedByUser → User?.
- Physical changes: DB-C02: restrictive immutable-key FKs; Privacy deletes/anonymizes explicitly in reviewed order; DB-C03: UTC-capable timestamptz(6) physical instants; DB-C03: owner-local CAS revision; no global ordering; SQL-08: server transaction identity for atomic source/evidence/message checks.
- Required SQL/access checks: SQL-01, SQL-02, SQL-03, SQL-04, SQL-05, SQL-08, SQL-15, SQL-16. Owner Privacy executor: digital_goods_access.

### MinorPrivacyControl

Later-phase child-specific control; no minor-account workaround.

- Object: `app.minor_privacy_controls`. Class: AUTHORITATIVE_OWNER_STATE. Stage: LATER_LAUNCH_DISABLED.
- Stable key: id. Foreign keys: childDirectedDeclaration → ChildDirectedContentDeclaration?, offering → Offering?.
- Physical changes: DB-C02: restrictive immutable-key FKs; Privacy deletes/anonymizes explicitly in reviewed order; DB-C03: UTC-capable timestamptz(6) physical instants; DB-C03: owner-local CAS revision; no global ordering; SQL-08: server transaction identity for atomic source/evidence/message checks.
- Required SQL/access checks: SQL-01, SQL-02, SQL-03, SQL-04, SQL-05, SQL-08, SQL-15, SQL-16. Owner Privacy executor: digital_goods_access.

### CourseAccessibilityAsset

Qualified accessible course derivative bound to actual Media bytes.

- Object: `app.course_accessibility_assets`. Class: AUTHORITATIVE_OWNER_STATE. Stage: LATER_OWNER_ORDERED_SLICE.
- Stable key: id. Foreign keys: offering → Offering?, courseDetails → CourseDetails?, courseVideoAsset → CourseVideoAsset?, mediaAsset → MediaAsset?, uploadedByUser → User?, reviewedByUser → User?.
- Physical changes: DB-C02: restrictive immutable-key FKs; Privacy deletes/anonymizes explicitly in reviewed order; DB-C03: UTC-capable timestamptz(6) physical instants; DB-C03: owner-local CAS revision; no global ordering; SQL-08: server transaction identity for atomic source/evidence/message checks.
- Required SQL/access checks: SQL-01, SQL-02, SQL-03, SQL-04, SQL-05, SQL-08, SQL-15, SQL-16. Owner Privacy executor: digital_goods_access.

## gamification_rewards

### GamificationProgram

Versioned ordinary rewards program, distinct from prize competitions.

- Object: `app.gamification_programs`. Class: AUTHORITATIVE_OWNER_STATE. Stage: LATER_OWNER_ORDERED_SLICE.
- Stable key: id. Foreign keys: none; typed registered descriptor scope is explicit in the SQL companion.
- Physical changes: DB-C03: UTC-capable timestamptz(6) physical instants; DB-C03: owner-local CAS revision; no global ordering; SQL-08: server transaction identity for atomic source/evidence/message checks.
- Required SQL/access checks: SQL-01, SQL-02, SQL-03, SQL-04, SQL-08, SQL-16. Owner Privacy executor: gamification_rewards.

### GamificationRule

Versioned source-qualified reward rule; no unapproved earning event.

- Object: `app.gamification_rules`. Class: AUTHORITATIVE_OWNER_STATE. Stage: LATER_OWNER_ORDERED_SLICE.
- Stable key: id. Foreign keys: program → GamificationProgram.
- Physical changes: DB-C02: restrictive immutable-key FKs; Privacy deletes/anonymizes explicitly in reviewed order; DB-C03: UTC-capable timestamptz(6) physical instants; DB-C03: owner-local CAS revision; no global ordering; DB-C01: source-owned immutable activated policy/catalog revision; SQL-08: server transaction identity for atomic source/evidence/message checks.
- Required SQL/access checks: SQL-01, SQL-02, SQL-03, SQL-04, SQL-08, SQL-16. Owner Privacy executor: gamification_rewards.

### PointLedgerEntry

Signed immutable User-wide points effect; Professional is contextual only.

- Object: `app.point_ledger_entries`. Class: IMMUTABLE_EVIDENCE_OR_RECEIPT. Stage: LATER_OWNER_ORDERED_SLICE.
- Stable key: id. Foreign keys: user → User, professionalProfile → ProfessionalProfile?, program → GamificationProgram?, order → Order?, rewardRedemption → RewardRedemption?, candidateEffectReceiptId → RuntimeEffectReceipt, candidateReversesEntryId → PointLedgerEntry?.
- Physical changes: DB-C02: restrictive immutable-key FKs; Privacy deletes/anonymizes explicitly in reviewed order; DB-C03: UTC-capable timestamptz(6) physical instants; DB-C11: durable source/economic effect uniqueness, beyond transport deduplication; DB-C11: original source/rule and explicit compensating-entry lineage; DB-C16: typed effectReceiptId binding to canonical RuntimeEffectReceipt; DB-C16: typed reversesEntryId binding to canonical PointLedgerEntry; SQL-08: server transaction identity for atomic source/evidence/message checks.
- Required SQL/access checks: SQL-01, SQL-02, SQL-03, SQL-04, SQL-08, SQL-16. Owner Privacy executor: gamification_rewards.

### Challenge

Ordinary rewards challenge definition, not prize entry.

- Object: `app.challenges`. Class: AUTHORITATIVE_OWNER_STATE. Stage: LATER_OWNER_ORDERED_SLICE.
- Stable key: id. Foreign keys: program → GamificationProgram.
- Physical changes: DB-C02: restrictive immutable-key FKs; Privacy deletes/anonymizes explicitly in reviewed order; DB-C03: UTC-capable timestamptz(6) physical instants; DB-C03: owner-local CAS revision; no global ordering; SQL-08: server transaction identity for atomic source/evidence/message checks.
- Required SQL/access checks: SQL-01, SQL-02, SQL-03, SQL-04, SQL-08, SQL-16. Owner Privacy executor: gamification_rewards.

### ChallengeParticipant

User participation and source-qualified challenge completion.

- Object: `app.challenge_participants`. Class: AUTHORITATIVE_OWNER_STATE. Stage: LATER_OWNER_ORDERED_SLICE.
- Stable key: challengeId, userId. Foreign keys: challenge → Challenge, user → User, professionalProfile → ProfessionalProfile?.
- Physical changes: DB-C02: restrictive immutable-key FKs; Privacy deletes/anonymizes explicitly in reviewed order; DB-C03: UTC-capable timestamptz(6) physical instants; SQL-08: server transaction identity for atomic source/evidence/message checks.
- Required SQL/access checks: SQL-01, SQL-02, SQL-03, SQL-04, SQL-08, SQL-16. Owner Privacy executor: gamification_rewards.

### Leaderboard

Derived comparison definition; never balance or entitlement truth.

- Object: `app.leaderboards`. Class: AUTHORITATIVE_OWNER_STATE. Stage: LATER_OWNER_ORDERED_SLICE.
- Stable key: id. Foreign keys: program → GamificationProgram.
- Physical changes: DB-C02: restrictive immutable-key FKs; Privacy deletes/anonymizes explicitly in reviewed order; DB-C03: UTC-capable timestamptz(6) physical instants; DB-C03: owner-local CAS revision; no global ordering; SQL-08: server transaction identity for atomic source/evidence/message checks.
- Required SQL/access checks: SQL-01, SQL-02, SQL-03, SQL-04, SQL-08, SQL-16. Owner Privacy executor: gamification_rewards.

### LeaderboardEntry

Rebuildable derived ranking; cannot authorize a reward.

- Object: `app.leaderboard_entries`. Class: PROJECTION_NOT_AUTHORITY. Stage: LATER_OWNER_ORDERED_SLICE.
- Stable key: id. Foreign keys: leaderboard → Leaderboard, user → User, professionalProfile → ProfessionalProfile?.
- Physical changes: DB-C02: restrictive immutable-key FKs; Privacy deletes/anonymizes explicitly in reviewed order; DB-C03: UTC-capable timestamptz(6) physical instants; DB-C03: owner-local CAS revision; no global ordering; SQL-08: server transaction identity for atomic source/evidence/message checks.
- Required SQL/access checks: SQL-01, SQL-02, SQL-03, SQL-04, SQL-08, SQL-16. Owner Privacy executor: gamification_rewards.

### Reward

Versioned supported reward benefit and inventory definition.

- Object: `app.rewards`. Class: AUTHORITATIVE_OWNER_STATE. Stage: LATER_OWNER_ORDERED_SLICE.
- Stable key: id. Foreign keys: program → GamificationProgram?.
- Physical changes: DB-C02: restrictive immutable-key FKs; Privacy deletes/anonymizes explicitly in reviewed order; DB-C03: UTC-capable timestamptz(6) physical instants; DB-C03: owner-local CAS revision; no global ordering; SQL-08: server transaction identity for atomic source/evidence/message checks.
- Required SQL/access checks: SQL-01, SQL-02, SQL-03, SQL-04, SQL-08, SQL-16. Owner Privacy executor: gamification_rewards.

### RewardRedemption

Reserved supported benefit and actual fulfillment/reversal lifecycle.

- Object: `app.reward_redemptions`. Class: AUTHORITATIVE_OWNER_STATE. Stage: LATER_OWNER_ORDERED_SLICE.
- Stable key: id. Foreign keys: reward → Reward, user → User, professionalProfile → ProfessionalProfile?, blockedByHold → ComplianceHold?, taxProfile → TaxProfile?.
- Physical changes: DB-C02: restrictive immutable-key FKs; Privacy deletes/anonymizes explicitly in reviewed order; DB-C03: UTC-capable timestamptz(6) physical instants; DB-C03: owner-local CAS revision; no global ordering; SQL-08: server transaction identity for atomic source/evidence/message checks.
- Required SQL/access checks: SQL-01, SQL-02, SQL-03, SQL-04, SQL-08, SQL-16. Owner Privacy executor: gamification_rewards.

### RewardFulfillmentReceipt

Actual supported reward benefit receipt and retained valuation; no reward from transport success.

- Object: `app.reward_fulfillment_receipt`. Class: IMMUTABLE_EVIDENCE_OR_RECEIPT. Stage: LATER_OWNER_ORDERED_SLICE.
- Stable key: id. Foreign keys: redemption → RewardRedemption, effect → RuntimeEffectReceipt.
- Physical changes: DB-C11; SQL-08: server transaction identity for atomic source/evidence/message checks.
- Required SQL/access checks: SQL-01, SQL-02, SQL-03, SQL-04, SQL-08, SQL-16. Owner Privacy executor: gamification_rewards.

## gig_demand

### Gig

Customer public paid request source; neither Job nor Offering.

- Object: `app.gigs`. Class: AUTHORITATIVE_OWNER_STATE. Stage: LATER_OWNER_ORDERED_SLICE.
- Stable key: id. Foreign keys: customerProfile → CustomerProfile?, poster → User, domain → TaxonomyDomain, category → TaxonomyCategory?.
- Physical changes: DB-C02: restrictive immutable-key FKs; Privacy deletes/anonymizes explicitly in reviewed order; DB-C03: UTC-capable timestamptz(6) physical instants; DB-C03: owner-local CAS revision; no global ordering; SQL-08: server transaction identity for atomic source/evidence/message checks.
- Required SQL/access checks: SQL-01, SQL-02, SQL-03, SQL-04, SQL-08, SQL-16. Owner Privacy executor: gig_demand.

### GigTag

Gig-owned controlled tag assignment and provenance.

- Object: `app.gig_tags`. Class: AUTHORITATIVE_OWNER_STATE. Stage: LATER_OWNER_ORDERED_SLICE.
- Stable key: gigId, tagId. Foreign keys: gig → Gig, tag → TaxonomyTag.
- Physical changes: DB-C02: restrictive immutable-key FKs; Privacy deletes/anonymizes explicitly in reviewed order; DB-C03: UTC-capable timestamptz(6) physical instants; SQL-08: server transaction identity for atomic source/evidence/message checks.
- Required SQL/access checks: SQL-01, SQL-02, SQL-03, SQL-04, SQL-08, SQL-16. Owner Privacy executor: gig_demand.

### GigResponse

Professional response and acceptance input for a Gig.

- Object: `app.gig_responses`. Class: AUTHORITATIVE_OWNER_STATE. Stage: LATER_OWNER_ORDERED_SLICE.
- Stable key: id. Foreign keys: gig → Gig, responderUser → User?, professionalProfile → ProfessionalProfile.
- Physical changes: DB-C02: restrictive immutable-key FKs; Privacy deletes/anonymizes explicitly in reviewed order; DB-C03: UTC-capable timestamptz(6) physical instants; DB-C03: owner-local CAS revision; no global ordering; SQL-08: server transaction identity for atomic source/evidence/message checks.
- Required SQL/access checks: SQL-01, SQL-02, SQL-03, SQL-04, SQL-08, SQL-16. Owner Privacy executor: gig_demand.

### GigAssignment

Retained accepted proposal/winner slot; Order outcome is a projection.

- Object: `app.gig_assignments`. Class: AUTHORITATIVE_OWNER_STATE. Stage: LATER_OWNER_ORDERED_SLICE.
- Stable key: id. Foreign keys: customerProfile → CustomerProfile?, gig → Gig, gigResponse → GigResponse?, professionalProfile → ProfessionalProfile.
- Physical changes: DB-C02: restrictive immutable-key FKs; Privacy deletes/anonymizes explicitly in reviewed order; DB-C03: UTC-capable timestamptz(6) physical instants; DB-C03: owner-local CAS revision; no global ordering; SQL-08: server transaction identity for atomic source/evidence/message checks.
- Required SQL/access checks: SQL-01, SQL-02, SQL-03, SQL-04, SQL-08, SQL-16. Owner Privacy executor: gig_demand.

### GigMedia

Gig-owned explicit Media attachment.

- Object: `app.gig_media`. Class: AUTHORITATIVE_OWNER_STATE. Stage: LATER_OWNER_ORDERED_SLICE.
- Stable key: gigId, mediaId. Foreign keys: gig → Gig, media → MediaAsset.
- Physical changes: DB-C02: restrictive immutable-key FKs; Privacy deletes/anonymizes explicitly in reviewed order; SQL-08: server transaction identity for atomic source/evidence/message checks.
- Required SQL/access checks: SQL-01, SQL-02, SQL-03, SQL-04, SQL-08, SQL-16. Owner Privacy executor: gig_demand.

## healthcare_regulated_services

### HealthcareComplianceProfile

Conditional regulated applicability/coverage, not a therapy launch permission.

- Object: `app.healthcare_compliance_profiles`. Class: AUTHORITATIVE_OWNER_STATE. Stage: LATER_OWNER_ORDERED_SLICE.
- Stable key: id. Foreign keys: professionalProfile → ProfessionalProfile.
- Physical changes: DB-C02: restrictive immutable-key FKs; Privacy deletes/anonymizes explicitly in reviewed order; DB-C03: UTC-capable timestamptz(6) physical instants; DB-C03: owner-local CAS revision; no global ordering; SQL-08: server transaction identity for atomic source/evidence/message checks.
- Required SQL/access checks: SQL-01, SQL-02, SQL-03, SQL-04, SQL-08, SQL-16. Owner Privacy executor: healthcare_regulated_services.

### BaaAgreement

Conditional reviewed agreement/account coverage evidence, not an executed-BAA assumption.

- Object: `app.baa_agreements`. Class: AUTHORITATIVE_OWNER_STATE. Stage: LATER_OWNER_ORDERED_SLICE.
- Stable key: id. Foreign keys: healthcareComplianceProfile → HealthcareComplianceProfile.
- Physical changes: DB-C02: restrictive immutable-key FKs; Privacy deletes/anonymizes explicitly in reviewed order; DB-C03: UTC-capable timestamptz(6) physical instants; DB-C03: owner-local CAS revision; no global ordering; SQL-08: server transaction identity for atomic source/evidence/message checks.
- Required SQL/access checks: SQL-01, SQL-02, SQL-03, SQL-04, SQL-08, SQL-16. Owner Privacy executor: healthcare_regulated_services.

### HealthcareDataBoundary

Context-specific regulated classification; no universal sensitivity ranking.

- Object: `app.healthcare_data_boundaries`. Class: AUTHORITATIVE_OWNER_STATE. Stage: LATER_OWNER_ORDERED_SLICE.
- Stable key: id. Foreign keys: none; typed registered descriptor scope is explicit in the SQL companion.
- Physical changes: DB-C03: UTC-capable timestamptz(6) physical instants; SQL-08: server transaction identity for atomic source/evidence/message checks.
- Required SQL/access checks: SQL-01, SQL-02, SQL-03, SQL-04, SQL-08, SQL-16. Owner Privacy executor: healthcare_regulated_services.

### HealthcareAdminAccessPolicy

Explicit regulated administrative purpose and access disposition.

- Object: `app.healthcare_admin_access_policies`. Class: AUTHORITATIVE_OWNER_STATE. Stage: LATER_OWNER_ORDERED_SLICE.
- Stable key: id. Foreign keys: none; typed registered descriptor scope is explicit in the SQL companion.
- Physical changes: DB-C03: UTC-capable timestamptz(6) physical instants; DB-C03: owner-local CAS revision; no global ordering; SQL-08: server transaction identity for atomic source/evidence/message checks.
- Required SQL/access checks: SQL-01, SQL-02, SQL-03, SQL-04, SQL-08, SQL-16. Owner Privacy executor: healthcare_regulated_services.

## identity_access

### AgeGateAttempt

Minimized Identity eligibility attempt, distinct from Consent acknowledgment.

- Object: `app.age_gate_attempts`. Class: AUTHORITATIVE_OWNER_STATE. Stage: F0_FOUNDATION.
- Stable key: id. Foreign keys: user → User?.
- Physical changes: DB-C02: restrictive immutable-key FKs; Privacy deletes/anonymizes explicitly in reviewed order; DB-C03: UTC-capable timestamptz(6) physical instants; SQL-08: server transaction identity for atomic source/evidence/message checks.
- Required SQL/access checks: SQL-01, SQL-02, SQL-03, SQL-04, SQL-08, SQL-16. Owner Privacy executor: identity_access.

### AgeGateBlock

Purpose-bound Identity abuse/rate restriction, not a minor account.

- Object: `app.age_gate_blocks`. Class: AUTHORITATIVE_OWNER_STATE. Stage: F0_FOUNDATION.
- Stable key: id. Foreign keys: none; typed registered descriptor scope is explicit in the SQL companion.
- Physical changes: DB-C03: UTC-capable timestamptz(6) physical instants; SQL-08: server transaction identity for atomic source/evidence/message checks.
- Required SQL/access checks: SQL-01, SQL-02, SQL-03, SQL-04, SQL-08, SQL-16. Owner Privacy executor: identity_access.

### User

Local account principal; not a seller or inferred commercial buyer.

- Object: `app.users`. Class: AUTHORITATIVE_OWNER_STATE. Stage: F0_FOUNDATION.
- Stable key: id. Foreign keys: none; typed registered descriptor scope is explicit in the SQL companion.
- Physical changes: DB-C03: UTC-capable timestamptz(6) physical instants; DB-C03: owner-local CAS revision; no global ordering; DB-C05: owner erasure/restriction generation prevents resurrection; SQL-08: server transaction identity for atomic source/evidence/message checks.
- Required SQL/access checks: SQL-01, SQL-02, SQL-03, SQL-04, SQL-08, SQL-16. Owner Privacy executor: identity_access.

### UserRole

Identity-owned platform role assignment; Role policy remains code-first.

- Object: `app.user_roles`. Class: AUTHORITATIVE_OWNER_STATE. Stage: F0_FOUNDATION.
- Stable key: userId, role. Foreign keys: user → User.
- Physical changes: DB-C02: restrictive immutable-key FKs; Privacy deletes/anonymizes explicitly in reviewed order; DB-C03: UTC-capable timestamptz(6) physical instants; DB-C03: owner-local CAS revision; no global ordering; SQL-08: server transaction identity for atomic source/evidence/message checks.
- Required SQL/access checks: SQL-01, SQL-02, SQL-03, SQL-04, SQL-08, SQL-16. Owner Privacy executor: identity_access.

### UserSecurityProfile

Current Identity security generation, restrictions and assurance prerequisites.

- Object: `app.user_security_profiles`. Class: AUTHORITATIVE_OWNER_STATE. Stage: F0_FOUNDATION.
- Stable key: id. Foreign keys: user → User.
- Physical changes: DB-C02: restrictive immutable-key FKs; Privacy deletes/anonymizes explicitly in reviewed order; DB-C03: UTC-capable timestamptz(6) physical instants; DB-C03: owner-local CAS revision; no global ordering; DB-C04: current security-generation binding; SQL-08: server transaction identity for atomic source/evidence/message checks.
- Required SQL/access checks: SQL-01, SQL-02, SQL-03, SQL-04, SQL-08, SQL-16. Owner Privacy executor: identity_access.

### AuthProviderAccount

Unique provider/account subject to local User binding.

- Object: `app.auth_provider_accounts`. Class: AUTHORITATIVE_OWNER_STATE. Stage: F0_FOUNDATION.
- Stable key: id. Foreign keys: user → User, securityProfile → UserSecurityProfile?.
- Physical changes: DB-C02: restrictive immutable-key FKs; Privacy deletes/anonymizes explicitly in reviewed order; DB-C03: UTC-capable timestamptz(6) physical instants; DB-C03: owner-local CAS revision; no global ordering; SQL-08: server transaction identity for atomic source/evidence/message checks.
- Required SQL/access checks: SQL-01, SQL-02, SQL-03, SQL-04, SQL-08, SQL-16. Owner Privacy executor: identity_access.

### PasskeyCredential

Protected public-key credential metadata; never raw biometric material.

- Object: `app.passkey_credentials`. Class: AUTHORITATIVE_OWNER_STATE. Stage: LATER_OWNER_ORDERED_SLICE.
- Stable key: id. Foreign keys: user → User, securityProfile → UserSecurityProfile?.
- Physical changes: DB-C02: restrictive immutable-key FKs; Privacy deletes/anonymizes explicitly in reviewed order; DB-C03: UTC-capable timestamptz(6) physical instants; DB-C03: owner-local CAS revision; no global ordering; SQL-08: server transaction identity for atomic source/evidence/message checks.
- Required SQL/access checks: SQL-01, SQL-02, SQL-03, SQL-04, SQL-08, SQL-16. Owner Privacy executor: identity_access.

### StepUpChallenge

Action/target/security-generation-bound challenge, not general elevated access.

- Object: `app.step_up_challenges`. Class: AUTHORITATIVE_OWNER_STATE. Stage: LATER_OWNER_ORDERED_SLICE.
- Stable key: id. Foreign keys: user → User, securityProfile → UserSecurityProfile?.
- Physical changes: DB-C02: restrictive immutable-key FKs; Privacy deletes/anonymizes explicitly in reviewed order; DB-C03: UTC-capable timestamptz(6) physical instants; DB-C03: owner-local CAS revision; no global ordering; SQL-08: server transaction identity for atomic source/evidence/message checks.
- Required SQL/access checks: SQL-01, SQL-02, SQL-03, SQL-04, SQL-08, SQL-16. Owner Privacy executor: identity_access.

### SensitiveActionSession

Bounded owner action assurance, never a universal admin session.

- Object: `app.sensitive_action_sessions`. Class: AUTHORITATIVE_OWNER_STATE. Stage: LATER_OWNER_ORDERED_SLICE.
- Stable key: id. Foreign keys: user → User, securityProfile → UserSecurityProfile?, stepUpChallenge → StepUpChallenge?.
- Physical changes: DB-C02: restrictive immutable-key FKs; Privacy deletes/anonymizes explicitly in reviewed order; DB-C03: UTC-capable timestamptz(6) physical instants; SQL-08: server transaction identity for atomic source/evidence/message checks.
- Required SQL/access checks: SQL-01, SQL-02, SQL-03, SQL-04, SQL-08, SQL-16. Owner Privacy executor: identity_access.

### AccountRecoveryRequest

Identity-owned recovery verification and revocation lifecycle.

- Object: `app.account_recovery_requests`. Class: AUTHORITATIVE_OWNER_STATE. Stage: LATER_OWNER_ORDERED_SLICE.
- Stable key: id. Foreign keys: user → User, securityProfile → UserSecurityProfile?.
- Physical changes: DB-C02: restrictive immutable-key FKs; Privacy deletes/anonymizes explicitly in reviewed order; DB-C03: UTC-capable timestamptz(6) physical instants; DB-C03: owner-local CAS revision; no global ordering; SQL-08: server transaction identity for atomic source/evidence/message checks.
- Required SQL/access checks: SQL-01, SQL-02, SQL-03, SQL-04, SQL-08, SQL-16. Owner Privacy executor: identity_access.

### UserSecurityEvent

Immutable Identity security/assignment/recovery change evidence.

- Object: `app.user_security_events`. Class: IMMUTABLE_EVIDENCE_OR_RECEIPT. Stage: LATER_OWNER_ORDERED_SLICE.
- Stable key: id. Foreign keys: user → User?, securityProfile → UserSecurityProfile?.
- Physical changes: DB-C02: restrictive immutable-key FKs; Privacy deletes/anonymizes explicitly in reviewed order; DB-C03: UTC-capable timestamptz(6) physical instants; SQL-08: server transaction identity for atomic source/evidence/message checks.
- Required SQL/access checks: SQL-01, SQL-02, SQL-03, SQL-04, SQL-08, SQL-16. Owner Privacy executor: identity_access.

## job_compliance

### JobCompensationDisclosure

Derived reviewed compensation disclosure bound to Hiring source/rules.

- Object: `app.job_compensation_disclosures`. Class: AUTHORITATIVE_OWNER_STATE. Stage: LATER_OWNER_ORDERED_SLICE.
- Stable key: id. Foreign keys: job → Job.
- Physical changes: DB-C02: restrictive immutable-key FKs; Privacy deletes/anonymizes explicitly in reviewed order; DB-C03: UTC-capable timestamptz(6) physical instants; DB-C03: owner-local CAS revision; no global ordering; SQL-08: server transaction identity for atomic source/evidence/message checks.
- Required SQL/access checks: SQL-01, SQL-02, SQL-03, SQL-04, SQL-08, SQL-16, SQL-18. Owner Privacy executor: job_compliance.

### JobComplianceCheck

Immutable Job-input/rule-version evaluation, with separate review decision.

- Object: `app.job_compliance_checks`. Class: AUTHORITATIVE_OWNER_STATE. Stage: LATER_OWNER_ORDERED_SLICE.
- Stable key: id. Foreign keys: job → Job, reviewedByUser → User?.
- Physical changes: DB-C02: restrictive immutable-key FKs; Privacy deletes/anonymizes explicitly in reviewed order; DB-C03: UTC-capable timestamptz(6) physical instants; DB-C03: owner-local CAS revision; no global ordering; R044: exact immutable Job input/rule-set binding; SQL-08: server transaction identity for atomic source/evidence/message checks.
- Required SQL/access checks: SQL-01, SQL-02, SQL-03, SQL-04, SQL-08, SQL-16, SQL-18. Owner Privacy executor: job_compliance.

### JobComplianceRule

Versioned jurisdiction rule supplied/approved externally; no statutory invention.

- Object: `app.job_compliance_rules`. Class: AUTHORITATIVE_OWNER_STATE. Stage: LATER_OWNER_ORDERED_SLICE.
- Stable key: id. Foreign keys: none; typed registered descriptor scope is explicit in the SQL companion.
- Physical changes: DB-C03: UTC-capable timestamptz(6) physical instants; DB-C03: owner-local CAS revision; no global ordering; SQL-08: server transaction identity for atomic source/evidence/message checks.
- Required SQL/access checks: SQL-01, SQL-02, SQL-03, SQL-04, SQL-08, SQL-16, SQL-18. Owner Privacy executor: job_compliance.

### JobComplianceFinding

Canonical bounded finding evidence; legacy aliases removed from fresh candidate.

- Object: `app.job_compliance_findings`. Class: AUTHORITATIVE_OWNER_STATE. Stage: LATER_OWNER_ORDERED_SLICE.
- Stable key: id. Foreign keys: check → JobComplianceCheck.
- Physical changes: DB-C02: restrictive immutable-key FKs; Privacy deletes/anonymizes explicitly in reviewed order; DB-C03: UTC-capable timestamptz(6) physical instants; DB-C07/R076: canonical bounded sourceField/preview/hash/replacement only; DB-C07: canonical finding field identity is required; SQL-08: server transaction identity for atomic source/evidence/message checks.
- Required SQL/access checks: SQL-01, SQL-02, SQL-03, SQL-04, SQL-08, SQL-16, SQL-18. Owner Privacy executor: job_compliance.

## job_interview

### JobInterview

Interview source parent/successor/schedule/participants, not Application status.

- Object: `app.job_interviews`. Class: AUTHORITATIVE_OWNER_STATE. Stage: LATER_OWNER_ORDERED_SLICE.
- Stable key: id. Foreign keys: jobApplication → JobApplication, organization → Organization, candidateProfile → CandidateProfile, scheduledByUser → User?, rescheduledFromInterview → JobInterview?.
- Physical changes: DB-C02: restrictive immutable-key FKs; Privacy deletes/anonymizes explicitly in reviewed order; DB-C03: UTC-capable timestamptz(6) physical instants; DB-C03: owner-local CAS revision; no global ordering; R046/R051: coherent current parent/audience and single successor chain; SQL-08: server transaction identity for atomic source/evidence/message checks.
- Required SQL/access checks: SQL-01, SQL-02, SQL-03, SQL-04, SQL-08, SQL-13, SQL-16, SQL-18. Owner Privacy executor: job_interview.

### JobInterviewParticipant

Current Interview audience membership and response state.

- Object: `app.job_interview_participants`. Class: AUTHORITATIVE_OWNER_STATE. Stage: LATER_OWNER_ORDERED_SLICE.
- Stable key: interviewId, userId. Foreign keys: interview → JobInterview, user → User.
- Physical changes: DB-C02: restrictive immutable-key FKs; Privacy deletes/anonymizes explicitly in reviewed order; DB-C03: UTC-capable timestamptz(6) physical instants; SQL-08: server transaction identity for atomic source/evidence/message checks.
- Required SQL/access checks: SQL-01, SQL-02, SQL-03, SQL-04, SQL-08, SQL-13, SQL-16, SQL-18. Owner Privacy executor: job_interview.

### JobInterviewEvent

Retained Interview transition/evidence history.

- Object: `app.job_interview_events`. Class: IMMUTABLE_EVIDENCE_OR_RECEIPT. Stage: LATER_OWNER_ORDERED_SLICE.
- Stable key: id. Foreign keys: interview → JobInterview.
- Physical changes: DB-C02: restrictive immutable-key FKs; Privacy deletes/anonymizes explicitly in reviewed order; DB-C03: UTC-capable timestamptz(6) physical instants; SQL-08: server transaction identity for atomic source/evidence/message checks.
- Required SQL/access checks: SQL-01, SQL-02, SQL-03, SQL-04, SQL-08, SQL-13, SQL-16, SQL-18. Owner Privacy executor: job_interview.

## location_safety

### FuzzyLocationCache

Derived fuzzy Location projection; never an exact-location fallback.

- Object: `app.fuzzy_location_cache`. Class: PROJECTION_NOT_AUTHORITY. Stage: LATER_OWNER_ORDERED_SLICE.
- Stable key: id. Foreign keys: none; typed registered descriptor scope is explicit in the SQL companion.
- Physical changes: DB-C03: UTC-capable timestamptz(6) physical instants; SQL-08: server transaction identity for atomic source/evidence/message checks.
- Required SQL/access checks: SQL-01, SQL-02, SQL-03, SQL-04, SQL-08, SQL-16. Owner Privacy executor: location_safety.

### LocationReveal

Purpose/parent/current-generation-bound exact-location reveal evidence.

- Object: `app.location_reveals`. Class: AUTHORITATIVE_OWNER_STATE. Stage: LATER_OWNER_ORDERED_SLICE.
- Stable key: id. Foreign keys: candidateInterviewId → JobInterview?, candidateBookingId → Booking?, candidateOrderId → Order?.
- Physical changes: DB-C03: UTC-capable timestamptz(6) physical instants; R071: separate Interview purpose and current parent/generation, no exact-location fallback; DB-C16: typed interviewId binding to canonical JobInterview; DB-C16: typed bookingId binding to canonical Booking; DB-C16: typed orderId binding to canonical Order; SQL-08: server transaction identity for atomic source/evidence/message checks.
- Required SQL/access checks: SQL-01, SQL-02, SQL-03, SQL-04, SQL-08, SQL-16. Owner Privacy executor: location_safety.

## marketplace_supply

### Offering

Professional-owned sellable supply and publication lifecycle.

- Object: `app.offerings`. Class: AUTHORITATIVE_OWNER_STATE. Stage: LATER_OWNER_ORDERED_SLICE.
- Stable key: id. Foreign keys: professionalProfile → ProfessionalProfile, domain → TaxonomyDomain, category → TaxonomyCategory?.
- Physical changes: DB-C02: restrictive immutable-key FKs; Privacy deletes/anonymizes explicitly in reviewed order; DB-C03: UTC-capable timestamptz(6) physical instants; DB-C03: owner-local CAS revision; no global ordering; DB-C01: policy history is one-to-many, not mutable single policy; SQL-08: server transaction identity for atomic source/evidence/message checks.
- Required SQL/access checks: SQL-01, SQL-02, SQL-03, SQL-04, SQL-08, SQL-16. Owner Privacy executor: marketplace_supply.

### ServiceDetails

Service-specific immutable-at-purchase Offering scope inputs.

- Object: `app.service_details`. Class: AUTHORITATIVE_OWNER_STATE. Stage: LATER_OWNER_ORDERED_SLICE.
- Stable key: offeringId. Foreign keys: offering → Offering.
- Physical changes: DB-C02: restrictive immutable-key FKs; Privacy deletes/anonymizes explicitly in reviewed order; SQL-08: server transaction identity for atomic source/evidence/message checks.
- Required SQL/access checks: SQL-01, SQL-02, SQL-03, SQL-04, SQL-08, SQL-16. Owner Privacy executor: marketplace_supply.

### ProductDetails

Product delivery definition; file access stays Media/Digital-owned.

- Object: `app.product_details`. Class: AUTHORITATIVE_OWNER_STATE. Stage: LATER_OWNER_ORDERED_SLICE.
- Stable key: offeringId. Foreign keys: offering → Offering, fileAsset → MediaAsset?.
- Physical changes: DB-C02: restrictive immutable-key FKs; Privacy deletes/anonymizes explicitly in reviewed order; SQL-08: server transaction identity for atomic source/evidence/message checks.
- Required SQL/access checks: SQL-01, SQL-02, SQL-03, SQL-04, SQL-08, SQL-16. Owner Privacy executor: marketplace_supply.

### CourseDetails

Course identity is Offering ID and defines purchased course scope.

- Object: `app.course_details`. Class: AUTHORITATIVE_OWNER_STATE. Stage: LATER_OWNER_ORDERED_SLICE.
- Stable key: offeringId. Foreign keys: offering → Offering.
- Physical changes: DB-C02: restrictive immutable-key FKs; Privacy deletes/anonymizes explicitly in reviewed order; DB-C03: UTC-capable timestamptz(6) physical instants; SQL-08: server transaction identity for atomic source/evidence/message checks.
- Required SQL/access checks: SQL-01, SQL-02, SQL-03, SQL-04, SQL-08, SQL-16. Owner Privacy executor: marketplace_supply.

### PricingTier

Source price definition selected into an immutable purchase revision.

- Object: `app.pricing_tiers`. Class: AUTHORITATIVE_OWNER_STATE. Stage: LATER_OWNER_ORDERED_SLICE.
- Stable key: id. Foreign keys: offering → Offering.
- Physical changes: DB-C02: restrictive immutable-key FKs; Privacy deletes/anonymizes explicitly in reviewed order; DB-C03: UTC-capable timestamptz(6) physical instants; DB-C03: owner-local CAS revision; no global ordering; SQL-08: server transaction identity for atomic source/evidence/message checks.
- Required SQL/access checks: SQL-01, SQL-02, SQL-03, SQL-04, SQL-08, SQL-16. Owner Privacy executor: marketplace_supply.

### OfferingMedia

Marketplace-owned explicit Media attachment; not Media ownership.

- Object: `app.offering_media`. Class: AUTHORITATIVE_OWNER_STATE. Stage: LATER_OWNER_ORDERED_SLICE.
- Stable key: offeringId, mediaId. Foreign keys: offering → Offering, media → MediaAsset.
- Physical changes: DB-C02: restrictive immutable-key FKs; Privacy deletes/anonymizes explicitly in reviewed order; SQL-08: server transaction identity for atomic source/evidence/message checks.
- Required SQL/access checks: SQL-01, SQL-02, SQL-03, SQL-04, SQL-08, SQL-16. Owner Privacy executor: marketplace_supply.

### OfferingTag

Marketplace-owned controlled tag assignment and provenance.

- Object: `app.offering_tags`. Class: AUTHORITATIVE_OWNER_STATE. Stage: LATER_OWNER_ORDERED_SLICE.
- Stable key: offeringId, tagId. Foreign keys: offering → Offering, tag → TaxonomyTag.
- Physical changes: DB-C02: restrictive immutable-key FKs; Privacy deletes/anonymizes explicitly in reviewed order; DB-C03: UTC-capable timestamptz(6) physical instants; SQL-08: server transaction identity for atomic source/evidence/message checks.
- Required SQL/access checks: SQL-01, SQL-02, SQL-03, SQL-04, SQL-08, SQL-16. Owner Privacy executor: marketplace_supply.

## media_file_access

### MediaAsset

Media identity and exact current object generation, never parent relationship ownership.

- Object: `app.media_assets`. Class: AUTHORITATIVE_OWNER_STATE. Stage: LATER_OWNER_ORDERED_SLICE.
- Stable key: id. Foreign keys: uploadedByUser → User?, sourceMediaAsset → MediaAsset?, candidateCurrentObjectVersionId → MediaObjectVersion?.
- Physical changes: DB-C02: restrictive immutable-key FKs; Privacy deletes/anonymizes explicitly in reviewed order; DB-C03: UTC-capable timestamptz(6) physical instants; DB-C05: owner erasure/restriction generation prevents resurrection; DB-C07: remove actual reverse relation for retired Agreement PDF mirror; DB-C16: typed currentObjectVersionId binding to canonical MediaObjectVersion; SQL-08: server transaction identity for atomic source/evidence/message checks.
- Required SQL/access checks: SQL-01, SQL-02, SQL-03, SQL-04, SQL-08, SQL-15, SQL-16. Owner Privacy executor: media_file_access.

### MediaUploadPolicy

Immutable activated policy revision and exact historical content.

- Object: `app.media_upload_policies`. Class: AUTHORITATIVE_OWNER_STATE. Stage: LATER_OWNER_ORDERED_SLICE.
- Stable key: id. Foreign keys: none; typed registered descriptor scope is explicit in the SQL companion.
- Physical changes: DB-C03: UTC-capable timestamptz(6) physical instants; DB-C03: owner-local CAS revision; no global ordering; DB-C10/R076: immutable activated policy identity/content; SQL-08: server transaction identity for atomic source/evidence/message checks.
- Required SQL/access checks: SQL-01, SQL-02, SQL-03, SQL-04, SQL-08, SQL-15, SQL-16. Owner Privacy executor: media_file_access.

### MediaUploadSession

Dedicated upload-attempt state linked to immutable policy revision.

- Object: `app.media_upload_sessions`. Class: AUTHORITATIVE_OWNER_STATE. Stage: LATER_OWNER_ORDERED_SLICE.
- Stable key: id. Foreign keys: policy → MediaUploadPolicy, mediaAsset → MediaAsset?, uploadedByUser → User?.
- Physical changes: DB-C02: restrictive immutable-key FKs; Privacy deletes/anonymizes explicitly in reviewed order; DB-C03: UTC-capable timestamptz(6) physical instants; DB-C03: owner-local CAS revision; no global ordering; DB-C10/R076: upload attempt lifecycle is distinct from MediaAsset; DB-C10: every new attempt binds an immutable policy revision; DB-C10: required immutable policy FK; SQL-08: server transaction identity for atomic source/evidence/message checks.
- Required SQL/access checks: SQL-01, SQL-02, SQL-03, SQL-04, SQL-08, SQL-15, SQL-16. Owner Privacy executor: media_file_access.

### MediaValidationResult

Exact input object/attempt inspection evidence, not URL readiness.

- Object: `app.media_validation_results`. Class: AUTHORITATIVE_OWNER_STATE. Stage: LATER_OWNER_ORDERED_SLICE.
- Stable key: id. Foreign keys: mediaAsset → MediaAsset?, uploadSession → MediaUploadSession?.
- Physical changes: DB-C02: restrictive immutable-key FKs; Privacy deletes/anonymizes explicitly in reviewed order; DB-C03: UTC-capable timestamptz(6) physical instants; SQL-08: server transaction identity for atomic source/evidence/message checks.
- Required SQL/access checks: SQL-01, SQL-02, SQL-03, SQL-04, SQL-08, SQL-15, SQL-16. Owner Privacy executor: media_file_access.

### MediaScanResult

Qualified scan result for exact object generation/checksum.

- Object: `app.media_scan_results`. Class: AUTHORITATIVE_OWNER_STATE. Stage: LATER_OWNER_ORDERED_SLICE.
- Stable key: id. Foreign keys: mediaAsset → MediaAsset?, uploadSession → MediaUploadSession?.
- Physical changes: DB-C02: restrictive immutable-key FKs; Privacy deletes/anonymizes explicitly in reviewed order; DB-C03: UTC-capable timestamptz(6) physical instants; SQL-08: server transaction identity for atomic source/evidence/message checks.
- Required SQL/access checks: SQL-01, SQL-02, SQL-03, SQL-04, SQL-08, SQL-15, SQL-16. Owner Privacy executor: media_file_access.

### MediaProcessingResult

Actual input/output bytes and metadata-removal evidence.

- Object: `app.media_processing_results`. Class: AUTHORITATIVE_OWNER_STATE. Stage: LATER_OWNER_ORDERED_SLICE.
- Stable key: id. Foreign keys: mediaAsset → MediaAsset?, uploadSession → MediaUploadSession?, derivedMediaAsset → MediaAsset?.
- Physical changes: DB-C02: restrictive immutable-key FKs; Privacy deletes/anonymizes explicitly in reviewed order; DB-C03: UTC-capable timestamptz(6) physical instants; SQL-08: server transaction identity for atomic source/evidence/message checks.
- Required SQL/access checks: SQL-01, SQL-02, SQL-03, SQL-04, SQL-08, SQL-15, SQL-16. Owner Privacy executor: media_file_access.

### MediaAccessGrant

Current contextual permission/proof bound to exact object version and operations.

- Object: `app.media_access_grants`. Class: AUTHORITATIVE_OWNER_STATE. Stage: LATER_OWNER_ORDERED_SLICE.
- Stable key: id. Foreign keys: mediaAsset → MediaAsset, user → User, candidateObjectVersionId → MediaObjectVersion.
- Physical changes: DB-C02: restrictive immutable-key FKs; Privacy deletes/anonymizes explicitly in reviewed order; DB-C03: UTC-capable timestamptz(6) physical instants; DB-C03: owner-local CAS revision; no global ordering; DB-C08: protected grant currentness and revocation binding; DB-C16: typed objectVersionId binding to canonical MediaObjectVersion; SQL-08: server transaction identity for atomic source/evidence/message checks.
- Required SQL/access checks: SQL-01, SQL-02, SQL-03, SQL-04, SQL-08, SQL-15, SQL-16. Owner Privacy executor: media_file_access.

### MediaAccessEvent

Append-only actual grant/byte access evidence; not proof of human consumption.

- Object: `app.media_access_events`. Class: IMMUTABLE_EVIDENCE_OR_RECEIPT. Stage: LATER_OWNER_ORDERED_SLICE.
- Stable key: id. Foreign keys: mediaAsset → MediaAsset, mediaAccessGrant → MediaAccessGrant?, user → User?.
- Physical changes: DB-C02: restrictive immutable-key FKs; Privacy deletes/anonymizes explicitly in reviewed order; DB-C03: UTC-capable timestamptz(6) physical instants; SQL-08: server transaction identity for atomic source/evidence/message checks.
- Required SQL/access checks: SQL-01, SQL-02, SQL-03, SQL-04, SQL-08, SQL-15, SQL-16. Owner Privacy executor: media_file_access.

### UserMedia

Identity-owned explicit User-profile Media attachment.

- Object: `app.user_media`. Class: AUTHORITATIVE_OWNER_STATE. Stage: LATER_OWNER_ORDERED_SLICE.
- Stable key: userId, mediaId. Foreign keys: user → User, media → MediaAsset.
- Physical changes: DB-C02: restrictive immutable-key FKs; Privacy deletes/anonymizes explicitly in reviewed order; SQL-08: server transaction identity for atomic source/evidence/message checks.
- Required SQL/access checks: SQL-01, SQL-02, SQL-03, SQL-04, SQL-08, SQL-15, SQL-16. Owner Privacy executor: media_file_access.

### MediaObjectVersion

Immutable exact stored bytes/object version bound to asset, digest and scan generation.

- Object: `app.media_object_version`. Class: IMMUTABLE_EVIDENCE_OR_RECEIPT. Stage: LATER_OWNER_ORDERED_SLICE.
- Stable key: id. Foreign keys: asset → MediaAsset.
- Physical changes: DB-C08; SQL-08: server transaction identity for atomic source/evidence/message checks.
- Required SQL/access checks: SQL-01, SQL-02, SQL-03, SQL-04, SQL-08, SQL-15, SQL-16. Owner Privacy executor: media_file_access.

## messaging

### Thread

Messaging source context with one matching concrete parent family.

- Object: `app.threads`. Class: AUTHORITATIVE_OWNER_STATE. Stage: LATER_OWNER_ORDERED_SLICE.
- Stable key: id. Foreign keys: order → Order?, gig → Gig?, gigResponse → GigResponse?, gigAssignment → GigAssignment?, jobApplication → JobApplication?, jobInterview → JobInterview?.
- Physical changes: DB-C02: restrictive immutable-key FKs; Privacy deletes/anonymizes explicitly in reviewed order; DB-C03: UTC-capable timestamptz(6) physical instants; DB-C03: owner-local CAS revision; no global ordering; SQL-08: server transaction identity for atomic source/evidence/message checks.
- Required SQL/access checks: SQL-01, SQL-02, SQL-03, SQL-04, SQL-08, SQL-16. Owner Privacy executor: messaging.

### ThreadParticipant

Current conversation audience; historical membership is not permission.

- Object: `app.thread_participants`. Class: AUTHORITATIVE_OWNER_STATE. Stage: LATER_OWNER_ORDERED_SLICE.
- Stable key: threadId, userId. Foreign keys: thread → Thread, user → User.
- Physical changes: DB-C02: restrictive immutable-key FKs; Privacy deletes/anonymizes explicitly in reviewed order; DB-C03: UTC-capable timestamptz(6) physical instants; DB-C03: owner-local CAS revision; no global ordering; SQL-08: server transaction identity for atomic source/evidence/message checks.
- Required SQL/access checks: SQL-01, SQL-02, SQL-03, SQL-04, SQL-08, SQL-16. Owner Privacy executor: messaging.

### Message

Contextual conversation source and owner-controlled edit/removal lifecycle.

- Object: `app.messages`. Class: AUTHORITATIVE_OWNER_STATE. Stage: LATER_OWNER_ORDERED_SLICE.
- Stable key: id. Foreign keys: thread → Thread, sender → User?.
- Physical changes: DB-C02: restrictive immutable-key FKs; Privacy deletes/anonymizes explicitly in reviewed order; DB-C03: UTC-capable timestamptz(6) physical instants; SQL-08: server transaction identity for atomic source/evidence/message checks.
- Required SQL/access checks: SQL-01, SQL-02, SQL-03, SQL-04, SQL-08, SQL-16. Owner Privacy executor: messaging.

### MessageMedia

Messaging-owned explicit Media attachment.

- Object: `app.message_media`. Class: AUTHORITATIVE_OWNER_STATE. Stage: LATER_OWNER_ORDERED_SLICE.
- Stable key: messageId, mediaId. Foreign keys: message → Message, media → MediaAsset.
- Physical changes: DB-C02: restrictive immutable-key FKs; Privacy deletes/anonymizes explicitly in reviewed order; SQL-08: server transaction identity for atomic source/evidence/message checks.
- Required SQL/access checks: SQL-01, SQL-02, SQL-03, SQL-04, SQL-08, SQL-16. Owner Privacy executor: messaging.

## notification

### Notification

Finite source-qualified safe recipient intent, not legal service/business completion.

- Object: `app.notifications`. Class: AUTHORITATIVE_OWNER_STATE. Stage: LATER_OWNER_ORDERED_SLICE.
- Stable key: id. Foreign keys: user → User?, organization → Organization?.
- Physical changes: DB-C02: restrictive immutable-key FKs; Privacy deletes/anonymizes explicitly in reviewed order; DB-C03: UTC-capable timestamptz(6) physical instants; SQL-08: server transaction identity for atomic source/evidence/message checks.
- Required SQL/access checks: SQL-01, SQL-02, SQL-03, SQL-04, SQL-08, SQL-16. Owner Privacy executor: notification.

### NotificationSubscription

Protected endpoint/device generation and permission; no plaintext tokens.

- Object: `app.notification_subscriptions`. Class: AUTHORITATIVE_OWNER_STATE. Stage: LATER_OWNER_ORDERED_SLICE.
- Stable key: id. Foreign keys: user → User.
- Physical changes: DB-C02: restrictive immutable-key FKs; Privacy deletes/anonymizes explicitly in reviewed order; DB-C03: UTC-capable timestamptz(6) physical instants; DB-C03: owner-local CAS revision; no global ordering; DB-C05: owner erasure/restriction generation prevents resurrection; DB-C15: remove raw endpoint/key mirrors; protected ciphertext plus scoped digest only; DB-C15: account/endpoint generation and active-recipient uniqueness specified in SQL register; SQL-08: server transaction identity for atomic source/evidence/message checks.
- Required SQL/access checks: SQL-01, SQL-02, SQL-03, SQL-04, SQL-08, SQL-16. Owner Privacy executor: notification.

### NotificationDelivery

One endpoint/source generation attempt and actual provider outcome.

- Object: `app.notification_deliveries`. Class: AUTHORITATIVE_OWNER_STATE. Stage: LATER_OWNER_ORDERED_SLICE.
- Stable key: id. Foreign keys: notification → Notification, subscription → NotificationSubscription?.
- Physical changes: DB-C02: restrictive immutable-key FKs; Privacy deletes/anonymizes explicitly in reviewed order; DB-C03: UTC-capable timestamptz(6) physical instants; SQL-08: server transaction identity for atomic source/evidence/message checks.
- Required SQL/access checks: SQL-01, SQL-02, SQL-03, SQL-04, SQL-08, SQL-16. Owner Privacy executor: notification.

### NotificationSubscriptionEvent

Immutable endpoint/permission/revocation generation evidence.

- Object: `app.notification_subscription_events`. Class: IMMUTABLE_EVIDENCE_OR_RECEIPT. Stage: LATER_OWNER_ORDERED_SLICE.
- Stable key: id. Foreign keys: subscription → NotificationSubscription?, user → User, notification → Notification?, delivery → NotificationDelivery?.
- Physical changes: DB-C02: restrictive immutable-key FKs; Privacy deletes/anonymizes explicitly in reviewed order; DB-C03: UTC-capable timestamptz(6) physical instants; SQL-08: server transaction identity for atomic source/evidence/message checks.
- Required SQL/access checks: SQL-01, SQL-02, SQL-03, SQL-04, SQL-08, SQL-16. Owner Privacy executor: notification.

## observability_ops

### OpsSystemEvent

Append-only safe operational observation, never domain proof or source completion.

- Object: `app.ops_system_event`. Class: IMMUTABLE_EVIDENCE_OR_RECEIPT. Stage: LATER_OWNER_ORDERED_SLICE.
- Stable key: id. Foreign keys: none; typed registered descriptor scope is explicit in the SQL companion.
- Physical changes: DB-C17; SQL-08: server transaction identity for atomic source/evidence/message checks.
- Required SQL/access checks: SQL-01, SQL-02, SQL-03, SQL-04, SQL-08, SQL-16, SQL-17. Owner Privacy executor: observability_ops.

### OpsIntegrationFailure

One actual failed integration occurrence; later retries are separate observations.

- Object: `app.ops_integration_failure`. Class: AUTHORITATIVE_OWNER_STATE. Stage: LATER_OWNER_ORDERED_SLICE.
- Stable key: id. Foreign keys: none; typed registered descriptor scope is explicit in the SQL companion.
- Physical changes: DB-C17; SQL-08: server transaction identity for atomic source/evidence/message checks.
- Required SQL/access checks: SQL-01, SQL-02, SQL-03, SQL-04, SQL-08, SQL-16, SQL-17. Owner Privacy executor: observability_ops.

### OpsIncident

Authorized operational incident state and explicit reopen history; never business repair authority.

- Object: `app.ops_incident`. Class: AUTHORITATIVE_OWNER_STATE. Stage: LATER_OWNER_ORDERED_SLICE.
- Stable key: id. Foreign keys: none; typed registered descriptor scope is explicit in the SQL companion.
- Physical changes: DB-C17; SQL-08: server transaction identity for atomic source/evidence/message checks.
- Required SQL/access checks: SQL-01, SQL-02, SQL-03, SQL-04, SQL-08, SQL-16, SQL-17. Owner Privacy executor: observability_ops.

### OpsIncidentEvent

Immutable incident triage/mitigation/resolution/reopen evidence.

- Object: `app.ops_incident_event`. Class: IMMUTABLE_EVIDENCE_OR_RECEIPT. Stage: LATER_OWNER_ORDERED_SLICE.
- Stable key: id. Foreign keys: incident → OpsIncident.
- Physical changes: DB-C17; SQL-08: server transaction identity for atomic source/evidence/message checks.
- Required SQL/access checks: SQL-01, SQL-02, SQL-03, SQL-04, SQL-08, SQL-16, SQL-17. Owner Privacy executor: observability_ops.

## organization_hiring

### Organization

Hiring entity and source identity; never an Offering seller.

- Object: `app.organizations`. Class: AUTHORITATIVE_OWNER_STATE. Stage: LATER_OWNER_ORDERED_SLICE.
- Stable key: id. Foreign keys: ownerUser → User?.
- Physical changes: DB-C02: restrictive immutable-key FKs; Privacy deletes/anonymizes explicitly in reviewed order; DB-C03: UTC-capable timestamptz(6) physical instants; DB-C03: owner-local CAS revision; no global ordering; SQL-08: server transaction identity for atomic source/evidence/message checks.
- Required SQL/access checks: SQL-01, SQL-02, SQL-03, SQL-04, SQL-08, SQL-16, SQL-18. Owner Privacy executor: organization_hiring.

### OrganizationMember

Current hiring membership and role; last-owner invariants remain Hiring-owned.

- Object: `app.organization_members`. Class: AUTHORITATIVE_OWNER_STATE. Stage: LATER_OWNER_ORDERED_SLICE.
- Stable key: organizationId, userId. Foreign keys: organization → Organization, user → User.
- Physical changes: DB-C02: restrictive immutable-key FKs; Privacy deletes/anonymizes explicitly in reviewed order; DB-C03: UTC-capable timestamptz(6) physical instants; DB-C03: owner-local CAS revision; no global ordering; SQL-08: server transaction identity for atomic source/evidence/message checks.
- Required SQL/access checks: SQL-01, SQL-02, SQL-03, SQL-04, SQL-08, SQL-16, SQL-18. Owner Privacy executor: organization_hiring.

### OrganizationCategory

Hiring-owned selected Organization category relationship.

- Object: `app.organization_categories`. Class: AUTHORITATIVE_OWNER_STATE. Stage: LATER_OWNER_ORDERED_SLICE.
- Stable key: organizationId, categoryId. Foreign keys: organization → Organization, category → TaxonomyCategory.
- Physical changes: DB-C02: restrictive immutable-key FKs; Privacy deletes/anonymizes explicitly in reviewed order; SQL-08: server transaction identity for atomic source/evidence/message checks.
- Required SQL/access checks: SQL-01, SQL-02, SQL-03, SQL-04, SQL-08, SQL-16, SQL-18. Owner Privacy executor: organization_hiring.

### OrganizationTag

Hiring-owned controlled Organization tag assignment and provenance.

- Object: `app.organization_tags`. Class: AUTHORITATIVE_OWNER_STATE. Stage: LATER_OWNER_ORDERED_SLICE.
- Stable key: organizationId, tagId. Foreign keys: organization → Organization, tag → TaxonomyTag.
- Physical changes: DB-C02: restrictive immutable-key FKs; Privacy deletes/anonymizes explicitly in reviewed order; DB-C03: UTC-capable timestamptz(6) physical instants; SQL-08: server transaction identity for atomic source/evidence/message checks.
- Required SQL/access checks: SQL-01, SQL-02, SQL-03, SQL-04, SQL-08, SQL-16, SQL-18. Owner Privacy executor: organization_hiring.

### Job

Organization-owned hiring source, compensation and publication revision.

- Object: `app.jobs`. Class: AUTHORITATIVE_OWNER_STATE. Stage: LATER_OWNER_ORDERED_SLICE.
- Stable key: id. Foreign keys: organization → Organization, domain → TaxonomyDomain, category → TaxonomyCategory?.
- Physical changes: DB-C02: restrictive immutable-key FKs; Privacy deletes/anonymizes explicitly in reviewed order; DB-C03: UTC-capable timestamptz(6) physical instants; DB-C03: owner-local CAS revision; no global ordering; SQL-08: server transaction identity for atomic source/evidence/message checks.
- Required SQL/access checks: SQL-01, SQL-02, SQL-03, SQL-04, SQL-08, SQL-16, SQL-18. Owner Privacy executor: organization_hiring.

### JobTag

Hiring-owned controlled Job tag assignment and provenance.

- Object: `app.job_tags`. Class: AUTHORITATIVE_OWNER_STATE. Stage: LATER_OWNER_ORDERED_SLICE.
- Stable key: jobId, tagId. Foreign keys: job → Job, tag → TaxonomyTag.
- Physical changes: DB-C02: restrictive immutable-key FKs; Privacy deletes/anonymizes explicitly in reviewed order; DB-C03: UTC-capable timestamptz(6) physical instants; SQL-08: server transaction identity for atomic source/evidence/message checks.
- Required SQL/access checks: SQL-01, SQL-02, SQL-03, SQL-04, SQL-08, SQL-16, SQL-18. Owner Privacy executor: organization_hiring.

### OrganizationMedia

Hiring-owned explicit Organization Media attachment.

- Object: `app.organization_media`. Class: AUTHORITATIVE_OWNER_STATE. Stage: LATER_OWNER_ORDERED_SLICE.
- Stable key: organizationId, mediaId. Foreign keys: organization → Organization, media → MediaAsset.
- Physical changes: DB-C02: restrictive immutable-key FKs; Privacy deletes/anonymizes explicitly in reviewed order; SQL-08: server transaction identity for atomic source/evidence/message checks.
- Required SQL/access checks: SQL-01, SQL-02, SQL-03, SQL-04, SQL-08, SQL-16, SQL-18. Owner Privacy executor: organization_hiring.

### JobMedia

Hiring-owned explicit Job Media attachment.

- Object: `app.job_media`. Class: AUTHORITATIVE_OWNER_STATE. Stage: LATER_OWNER_ORDERED_SLICE.
- Stable key: jobId, mediaId. Foreign keys: job → Job, media → MediaAsset.
- Physical changes: DB-C02: restrictive immutable-key FKs; Privacy deletes/anonymizes explicitly in reviewed order; SQL-08: server transaction identity for atomic source/evidence/message checks.
- Required SQL/access checks: SQL-01, SQL-02, SQL-03, SQL-04, SQL-08, SQL-16, SQL-18. Owner Privacy executor: organization_hiring.

### OrganizationNotificationSetting

Hiring-owned permitted Organization notification audience preference.

- Object: `app.organization_notification_settings`. Class: AUTHORITATIVE_OWNER_STATE. Stage: LATER_OWNER_ORDERED_SLICE.
- Stable key: id. Foreign keys: organization → Organization.
- Physical changes: DB-C02: restrictive immutable-key FKs; Privacy deletes/anonymizes explicitly in reviewed order; DB-C03: UTC-capable timestamptz(6) physical instants; DB-C03: owner-local CAS revision; no global ordering; SQL-08: server transaction identity for atomic source/evidence/message checks.
- Required SQL/access checks: SQL-01, SQL-02, SQL-03, SQL-04, SQL-08, SQL-16, SQL-18. Owner Privacy executor: organization_hiring.

## payment_payout_tax

### KycVerification

Payment provider verification mapping and currentness, not Professional readiness.

- Object: `app.kyc_verifications`. Class: AUTHORITATIVE_OWNER_STATE. Stage: LATER_OWNER_ORDERED_SLICE.
- Stable key: id. Foreign keys: user → User, professionalProfile → ProfessionalProfile?.
- Physical changes: DB-C02: restrictive immutable-key FKs; Privacy deletes/anonymizes explicitly in reviewed order; DB-C03: UTC-capable timestamptz(6) physical instants; DB-C03: owner-local CAS revision; no global ordering; SQL-08: server transaction identity for atomic source/evidence/message checks.
- Required SQL/access checks: SQL-01, SQL-02, SQL-03, SQL-04, SQL-07, SQL-08, SQL-11, SQL-16. Owner Privacy executor: payment_payout_tax.

### TaxProfile

Protected Payment tax-subject/provider verification reference.

- Object: `app.tax_profiles`. Class: AUTHORITATIVE_OWNER_STATE. Stage: LATER_OWNER_ORDERED_SLICE.
- Stable key: id. Foreign keys: user → User, professionalProfile → ProfessionalProfile?.
- Physical changes: DB-C02: restrictive immutable-key FKs; Privacy deletes/anonymizes explicitly in reviewed order; DB-C03: UTC-capable timestamptz(6) physical instants; DB-C03: owner-local CAS revision; no global ordering; SQL-08: server transaction identity for atomic source/evidence/message checks.
- Required SQL/access checks: SQL-01, SQL-02, SQL-03, SQL-04, SQL-07, SQL-08, SQL-11, SQL-16. Owner Privacy executor: payment_payout_tax.

### TaxDocument

Protected tax-document evidence associated with a tax profile.

- Object: `app.tax_documents`. Class: AUTHORITATIVE_OWNER_STATE. Stage: LATER_OWNER_ORDERED_SLICE.
- Stable key: id. Foreign keys: taxProfile → TaxProfile.
- Physical changes: DB-C02: restrictive immutable-key FKs; Privacy deletes/anonymizes explicitly in reviewed order; DB-C03: UTC-capable timestamptz(6) physical instants; SQL-08: server transaction identity for atomic source/evidence/message checks.
- Required SQL/access checks: SQL-01, SQL-02, SQL-03, SQL-04, SQL-07, SQL-08, SQL-11, SQL-16. Owner Privacy executor: payment_payout_tax.

### TaxYearEarningsSummary

Derived Payment aggregate partitioned by legal subject/year/currency/jurisdiction/regime.

- Object: `app.tax_year_earnings_summaries`. Class: AUTHORITATIVE_OWNER_STATE. Stage: LATER_OWNER_ORDERED_SLICE.
- Stable key: id. Foreign keys: user → User, professionalProfile → ProfessionalProfile?.
- Physical changes: DB-C02: restrictive immutable-key FKs; Privacy deletes/anonymizes explicitly in reviewed order; DB-C03: UTC-capable timestamptz(6) physical instants; DB-C03: owner-local CAS revision; no global ordering; DB-C13: legal fiscal aggregate dimensions remain distinct; DB-C13: explicit approved jurisdiction before tax activation; DB-C13: no aggregation across reporting regimes; SQL-08: server transaction identity for atomic source/evidence/message checks.
- Required SQL/access checks: SQL-01, SQL-02, SQL-03, SQL-04, SQL-07, SQL-08, SQL-11, SQL-16. Owner Privacy executor: payment_payout_tax.

### TaxReportingSubmission

Payment filing submission and provider outcome, externally gated.

- Object: `app.tax_reporting_submissions`. Class: AUTHORITATIVE_OWNER_STATE. Stage: LATER_OWNER_ORDERED_SLICE.
- Stable key: id. Foreign keys: none; typed registered descriptor scope is explicit in the SQL companion.
- Physical changes: DB-C03: UTC-capable timestamptz(6) physical instants; DB-C03: owner-local CAS revision; no global ordering; SQL-08: server transaction identity for atomic source/evidence/message checks.
- Required SQL/access checks: SQL-01, SQL-02, SQL-03, SQL-04, SQL-07, SQL-08, SQL-11, SQL-16. Owner Privacy executor: payment_payout_tax.

### TaxReportingRecipient

One submission recipient and retained filing amount/outcome evidence.

- Object: `app.tax_reporting_recipients`. Class: AUTHORITATIVE_OWNER_STATE. Stage: LATER_OWNER_ORDERED_SLICE.
- Stable key: id. Foreign keys: submission → TaxReportingSubmission.
- Physical changes: DB-C02: restrictive immutable-key FKs; Privacy deletes/anonymizes explicitly in reviewed order; DB-C03: UTC-capable timestamptz(6) physical instants; DB-C03: owner-local CAS revision; no global ordering; SQL-08: server transaction identity for atomic source/evidence/message checks.
- Required SQL/access checks: SQL-01, SQL-02, SQL-03, SQL-04, SQL-07, SQL-08, SQL-11, SQL-16. Owner Privacy executor: payment_payout_tax.

### PayoutAccount

Professional connected financial account and actual capability state.

- Object: `app.payout_accounts`. Class: AUTHORITATIVE_OWNER_STATE. Stage: LATER_OWNER_ORDERED_SLICE.
- Stable key: id. Foreign keys: professionalProfile → ProfessionalProfile.
- Physical changes: DB-C02: restrictive immutable-key FKs; Privacy deletes/anonymizes explicitly in reviewed order; DB-C03: UTC-capable timestamptz(6) physical instants; DB-C03: owner-local CAS revision; no global ordering; SQL-08: server transaction identity for atomic source/evidence/message checks.
- Required SQL/access checks: SQL-01, SQL-02, SQL-03, SQL-04, SQL-07, SQL-08, SQL-11, SQL-16. Owner Privacy executor: payment_payout_tax.

### ProviderRequirementSnapshot

Immutable provider/account requirement snapshot, not legal approval.

- Object: `app.provider_requirement_snapshots`. Class: IMMUTABLE_EVIDENCE_OR_RECEIPT. Stage: LATER_OWNER_ORDERED_SLICE.
- Stable key: id. Foreign keys: payoutAccount → PayoutAccount.
- Physical changes: DB-C02: restrictive immutable-key FKs; Privacy deletes/anonymizes explicitly in reviewed order; DB-C03: UTC-capable timestamptz(6) physical instants; SQL-08: server transaction identity for atomic source/evidence/message checks.
- Required SQL/access checks: SQL-01, SQL-02, SQL-03, SQL-04, SQL-07, SQL-08, SQL-11, SQL-16. Owner Privacy executor: payment_payout_tax.

### ProfessionalBalanceLedgerEntry

Signed append-only economic ledger under Payment effect identity.

- Object: `app.professional_balance_ledger_entries`. Class: IMMUTABLE_EVIDENCE_OR_RECEIPT. Stage: LATER_OWNER_ORDERED_SLICE.
- Stable key: id. Foreign keys: professionalProfile → ProfessionalProfile, user → User?, order → Order?, payoutRequest → PayoutRequest?, payoutTransfer → PayoutTransfer?, candidateEffectReceiptId → RuntimeEffectReceipt.
- Physical changes: DB-C02: restrictive immutable-key FKs; Privacy deletes/anonymizes explicitly in reviewed order; DB-C03: UTC-capable timestamptz(6) physical instants; DB-C11: durable source/economic effect uniqueness, beyond transport deduplication; DB-C16: typed effectReceiptId binding to canonical RuntimeEffectReceipt; SQL-08: server transaction identity for atomic source/evidence/message checks.
- Required SQL/access checks: SQL-01, SQL-02, SQL-03, SQL-04, SQL-07, SQL-08, SQL-11, SQL-16. Owner Privacy executor: payment_payout_tax.

### PayoutRequest

Authorized payout request and its current lifecycle, separate from external execution.

- Object: `app.payout_requests`. Class: AUTHORITATIVE_OWNER_STATE. Stage: LATER_OWNER_ORDERED_SLICE.
- Stable key: id. Foreign keys: user → User, professionalProfile → ProfessionalProfile, payoutAccount → PayoutAccount?, blockedByHold → ComplianceHold?.
- Physical changes: DB-C02: restrictive immutable-key FKs; Privacy deletes/anonymizes explicitly in reviewed order; DB-C03: UTC-capable timestamptz(6) physical instants; DB-C03: owner-local CAS revision; no global ordering; SQL-08: server transaction identity for atomic source/evidence/message checks.
- Required SQL/access checks: SQL-01, SQL-02, SQL-03, SQL-04, SQL-07, SQL-08, SQL-11, SQL-16. Owner Privacy executor: payment_payout_tax.

### PayoutTransfer

One reconciled external payout/transfer effect with durable semantic identity.

- Object: `app.payout_transfers`. Class: AUTHORITATIVE_OWNER_STATE. Stage: LATER_OWNER_ORDERED_SLICE.
- Stable key: id. Foreign keys: professionalProfile → ProfessionalProfile, payoutRequest → PayoutRequest?, payoutAccount → PayoutAccount?, order → Order?, blockedByHold → ComplianceHold?, candidateEffectReceiptId → RuntimeEffectReceipt.
- Physical changes: DB-C02: restrictive immutable-key FKs; Privacy deletes/anonymizes explicitly in reviewed order; DB-C03: UTC-capable timestamptz(6) physical instants; DB-C03: owner-local CAS revision; no global ordering; DB-C11: durable financial effect identity survives provider retry; DB-C16: typed effectReceiptId binding to canonical RuntimeEffectReceipt; SQL-08: server transaction identity for atomic source/evidence/message checks.
- Required SQL/access checks: SQL-01, SQL-02, SQL-03, SQL-04, SQL-07, SQL-08, SQL-11, SQL-16. Owner Privacy executor: payment_payout_tax.

### ProcessedStripeEvent

Verified account/event transport receipt; not an economic-effect ledger.

- Object: `app.processed_stripe_events`. Class: IMMUTABLE_EVIDENCE_OR_RECEIPT. Stage: LATER_OWNER_ORDERED_SLICE.
- Stable key: providerAccountScope, eventId. Foreign keys: none; typed registered descriptor scope is explicit in the SQL companion.
- Physical changes: DB-C03: UTC-capable timestamptz(6) physical instants; DB-C14/R018: verified provider/account/event identity and fingerprint; SQL-08: server transaction identity for atomic source/evidence/message checks.
- Required SQL/access checks: SQL-01, SQL-02, SQL-03, SQL-04, SQL-07, SQL-08, SQL-11, SQL-16. Owner Privacy executor: payment_payout_tax.

### SalesTaxCalculation

Payment tax calculation bound to immutable Order quote and private evidence.

- Object: `app.sales_tax_calculations`. Class: AUTHORITATIVE_OWNER_STATE. Stage: LATER_OWNER_ORDERED_SLICE.
- Stable key: id. Foreign keys: order → Order?, user → User?, candidateCheckoutEvidenceId → CheckoutTaxLocationEvidence?, candidatePurchaseRevisionId → OrderPurchaseRevision?.
- Physical changes: DB-C02: restrictive immutable-key FKs; Privacy deletes/anonymizes explicitly in reviewed order; DB-C03: UTC-capable timestamptz(6) physical instants; DB-C03: owner-local CAS revision; no global ordering; DB-C09/R037: tax liability is an explicit approved external policy, never a historical default; DB-C16: typed checkoutEvidenceId binding to canonical CheckoutTaxLocationEvidence; DB-C16: typed purchaseRevisionId binding to canonical OrderPurchaseRevision; SQL-08: server transaction identity for atomic source/evidence/message checks.
- Required SQL/access checks: SQL-01, SQL-02, SQL-03, SQL-04, SQL-07, SQL-08, SQL-11, SQL-16. Owner Privacy executor: payment_payout_tax.

### SalesTaxLineItem

Calculation line/jurisdiction result, not originating Offering price truth.

- Object: `app.sales_tax_line_items`. Class: AUTHORITATIVE_OWNER_STATE. Stage: LATER_OWNER_ORDERED_SLICE.
- Stable key: id. Foreign keys: salesTaxCalculation → SalesTaxCalculation, offering → Offering?, pricingTier → PricingTier?.
- Physical changes: DB-C02: restrictive immutable-key FKs; Privacy deletes/anonymizes explicitly in reviewed order; DB-C03: UTC-capable timestamptz(6) physical instants; SQL-08: server transaction identity for atomic source/evidence/message checks.
- Required SQL/access checks: SQL-01, SQL-02, SQL-03, SQL-04, SQL-07, SQL-08, SQL-11, SQL-16. Owner Privacy executor: payment_payout_tax.

### SalesTaxTransaction

Actual tax recording/reversal under approved liability policy.

- Object: `app.sales_tax_transactions`. Class: AUTHORITATIVE_OWNER_STATE. Stage: LATER_OWNER_ORDERED_SLICE.
- Stable key: id. Foreign keys: salesTaxCalculation → SalesTaxCalculation?, order → Order, user → User?.
- Physical changes: DB-C02: restrictive immutable-key FKs; Privacy deletes/anonymizes explicitly in reviewed order; DB-C03: UTC-capable timestamptz(6) physical instants; DB-C03: owner-local CAS revision; no global ordering; DB-C09/R037: tax liability is an explicit approved external policy, never a historical default; SQL-08: server transaction identity for atomic source/evidence/message checks.
- Required SQL/access checks: SQL-01, SQL-02, SQL-03, SQL-04, SQL-07, SQL-08, SQL-11, SQL-16. Owner Privacy executor: payment_payout_tax.

### PaymentEffect

Payment-owned normalized financial instruction/result, not an Order or runtime financial substitute.

- Object: `app.payment_effect`. Class: AUTHORITATIVE_OWNER_STATE. Stage: LATER_OWNER_ORDERED_SLICE.
- Stable key: id. Foreign keys: order → Order, purchase → OrderPurchaseRevision, runtime → RuntimeEffectReceipt.
- Physical changes: DB-C11; SQL-08: server transaction identity for atomic source/evidence/message checks.
- Required SQL/access checks: SQL-01, SQL-02, SQL-03, SQL-04, SQL-07, SQL-08, SQL-11, SQL-16. Owner Privacy executor: payment_payout_tax.

## platform_integration_owner

### DatabaseActionGrant

Ephemeral non-authorizing transport of already approved Role/Identity scope into one DB transaction; not a second policy catalog.

- Object: `platform.database_action_grant`. Class: SHARED_INFRASTRUCTURE. Stage: F0_FOUNDATION.
- Stable key: id. Foreign keys: none; typed registered descriptor scope is explicit in the SQL companion.
- Physical changes: DB-C04; B010-01: issuer commits immutable nonnullable transaction tuple before bind; helper never writes grant; SQL-08: server transaction identity for atomic source/evidence/message checks.
- Required SQL/access checks: SQL-01, SQL-02, SQL-03, SQL-04, SQL-06, SQL-07, SQL-08, SQL-09, SQL-16. Owner Privacy executor: platform executor for minimized infrastructure metadata; original owner retains domain payload disposition.

### RuntimeCommandReceipt

One shared scoped command identity/fingerprint/result receipt; owner retains semantic decisions.

- Object: `platform.runtime_command_receipt`. Class: SHARED_INFRASTRUCTURE. Stage: F0_FOUNDATION.
- Stable key: id. Foreign keys: none; typed registered descriptor scope is explicit in the SQL companion.
- Physical changes: DB-C11; SQL-08: server transaction identity for atomic source/evidence/message checks.
- Required SQL/access checks: SQL-01, SQL-02, SQL-03, SQL-04, SQL-06, SQL-07, SQL-08, SQL-09, SQL-16. Owner Privacy executor: platform executor for minimized infrastructure metadata; original owner retains domain payload disposition.

### RuntimeOutboxMessage

Source-transaction durable committed fact or registered command intent; no alternate owner lifecycle.

- Object: `platform.runtime_outbox_message`. Class: SHARED_INFRASTRUCTURE. Stage: F0_FOUNDATION.
- Stable key: id. Foreign keys: command → RuntimeCommandReceipt.
- Physical changes: DB-C11; SQL-08: server transaction identity for atomic source/evidence/message checks.
- Required SQL/access checks: SQL-01, SQL-02, SQL-03, SQL-04, SQL-06, SQL-07, SQL-08, SQL-09, SQL-16. Owner Privacy executor: platform executor for minimized infrastructure metadata; original owner retains domain payload disposition.

### RuntimeEffectReceipt

Durable owner-scoped semantic effect receipt, separate from event deduplication.

- Object: `platform.runtime_effect_receipt`. Class: SHARED_INFRASTRUCTURE. Stage: F0_FOUNDATION.
- Stable key: id. Foreign keys: command → RuntimeCommandReceipt?.
- Physical changes: DB-C11; SQL-08: server transaction identity for atomic source/evidence/message checks.
- Required SQL/access checks: SQL-01, SQL-02, SQL-03, SQL-04, SQL-06, SQL-07, SQL-08, SQL-09, SQL-16. Owner Privacy executor: platform executor for minimized infrastructure metadata; original owner retains domain payload disposition.

### RuntimeWorkItem

Single durable work/lease/fence source; QueueJob remains an Ops projection.

- Object: `platform.runtime_work_item`. Class: SHARED_INFRASTRUCTURE. Stage: F0_FOUNDATION.
- Stable key: id. Foreign keys: message → RuntimeOutboxMessage, effect → RuntimeEffectReceipt?.
- Physical changes: DB-C11; SQL-08: server transaction identity for atomic source/evidence/message checks.
- Required SQL/access checks: SQL-01, SQL-02, SQL-03, SQL-04, SQL-06, SQL-07, SQL-08, SQL-09, SQL-16. Owner Privacy executor: platform executor for minimized infrastructure metadata; original owner retains domain payload disposition.

### RuntimeAttempt

Append-only actual runner attempt and fenced outcome observation.

- Object: `platform.runtime_attempt`. Class: SHARED_INFRASTRUCTURE. Stage: F0_FOUNDATION.
- Stable key: id. Foreign keys: work → RuntimeWorkItem.
- Physical changes: DB-C11; SQL-08: server transaction identity for atomic source/evidence/message checks.
- Required SQL/access checks: SQL-01, SQL-02, SQL-03, SQL-04, SQL-06, SQL-07, SQL-08, SQL-09, SQL-16. Owner Privacy executor: platform executor for minimized infrastructure metadata; original owner retains domain payload disposition.

### RuntimeInboxReceipt

Consumer/event transport deduplication committed atomically with the consuming owner effect.

- Object: `platform.runtime_inbox_receipt`. Class: SHARED_INFRASTRUCTURE. Stage: F0_FOUNDATION.
- Stable key: id. Foreign keys: message → RuntimeOutboxMessage, effect → RuntimeEffectReceipt.
- Physical changes: DB-C11; SQL-08: server transaction identity for atomic source/evidence/message checks.
- Required SQL/access checks: SQL-01, SQL-02, SQL-03, SQL-04, SQL-06, SQL-07, SQL-08, SQL-09, SQL-16. Owner Privacy executor: platform executor for minimized infrastructure metadata; original owner retains domain payload disposition.

### RuntimeReservation

Execution reservation/fenced noncommit coordination; domain counts remain with their source owner.

- Object: `platform.runtime_reservation`. Class: SHARED_INFRASTRUCTURE. Stage: F0_FOUNDATION.
- Stable key: id. Foreign keys: command → RuntimeCommandReceipt, effect → RuntimeEffectReceipt?.
- Physical changes: DB-C11; SQL-08: server transaction identity for atomic source/evidence/message checks.
- Required SQL/access checks: SQL-01, SQL-02, SQL-03, SQL-04, SQL-06, SQL-07, SQL-08, SQL-09, SQL-16. Owner Privacy executor: platform executor for minimized infrastructure metadata; original owner retains domain payload disposition.

### OwnerMutationEvidence

Minimized immutable owner-transaction proof; source-specific histories and policy remain with each owner.

- Object: `platform.owner_mutation_evidence`. Class: SHARED_INFRASTRUCTURE. Stage: F0_FOUNDATION.
- Stable key: id. Foreign keys: command → RuntimeCommandReceipt.
- Physical changes: DB-C11; SQL-08: server transaction identity for atomic source/evidence/message checks.
- Required SQL/access checks: SQL-01, SQL-02, SQL-03, SQL-04, SQL-06, SQL-07, SQL-08, SQL-09, SQL-16. Owner Privacy executor: platform executor for minimized infrastructure metadata; original owner retains domain payload disposition.

## privacy_data_erasure

### PrivacyRequest

Verified data-rights request and orchestration state; no invented legal response timer.

- Object: `app.privacy_requests`. Class: AUTHORITATIVE_OWNER_STATE. Stage: F0_FOUNDATION.
- Stable key: id. Foreign keys: user → User.
- Physical changes: DB-C02: restrictive immutable-key FKs; Privacy deletes/anonymizes explicitly in reviewed order; DB-C03: UTC-capable timestamptz(6) physical instants; DB-C03: owner-local CAS revision; no global ordering; DB-C05: owner erasure/restriction generation prevents resurrection; DB-C05: new owner instructions invalidate old-generation completion; SQL-08: server transaction identity for atomic source/evidence/message checks.
- Required SQL/access checks: SQL-01, SQL-02, SQL-03, SQL-04, SQL-08, SQL-14, SQL-16. Owner Privacy executor: privacy_data_erasure.

### DataErasureJob

Privacy erasure orchestration projection over current instructions/receipts.

- Object: `app.data_erasure_jobs`. Class: AUTHORITATIVE_OWNER_STATE. Stage: LATER_OWNER_ORDERED_SLICE.
- Stable key: id. Foreign keys: privacyRequest → PrivacyRequest.
- Physical changes: DB-C02: restrictive immutable-key FKs; Privacy deletes/anonymizes explicitly in reviewed order; DB-C03: UTC-capable timestamptz(6) physical instants; DB-C03: owner-local CAS revision; no global ordering; DB-C05: exact request generation carried through orchestration; SQL-08: server transaction identity for atomic source/evidence/message checks.
- Required SQL/access checks: SQL-01, SQL-02, SQL-03, SQL-04, SQL-08, SQL-14, SQL-16. Owner Privacy executor: privacy_data_erasure.

### DataErasureTarget

Legacy target summary bound to a typed owner instruction; no cascade coverage inference.

- Object: `app.data_erasure_targets`. Class: AUTHORITATIVE_OWNER_STATE. Stage: LATER_OWNER_ORDERED_SLICE.
- Stable key: id. Foreign keys: erasureJob → DataErasureJob, candidateInstructionId → PrivacyTargetInstruction.
- Physical changes: DB-C02: restrictive immutable-key FKs; Privacy deletes/anonymizes explicitly in reviewed order; DB-C03: UTC-capable timestamptz(6) physical instants; DB-C16: typed instructionId binding to canonical PrivacyTargetInstruction; SQL-08: server transaction identity for atomic source/evidence/message checks.
- Required SQL/access checks: SQL-01, SQL-02, SQL-03, SQL-04, SQL-08, SQL-14, SQL-16. Owner Privacy executor: privacy_data_erasure.

### DataRetentionExemption

Reviewed lawful retained disposition and basis reference; no universal retention period.

- Object: `app.data_retention_exemptions`. Class: AUTHORITATIVE_OWNER_STATE. Stage: LATER_OWNER_ORDERED_SLICE.
- Stable key: id. Foreign keys: erasureTarget → DataErasureTarget.
- Physical changes: DB-C02: restrictive immutable-key FKs; Privacy deletes/anonymizes explicitly in reviewed order; DB-C03: UTC-capable timestamptz(6) physical instants; DB-C05: retained disposition needs approved basis, not a guessed timer; SQL-08: server transaction identity for atomic source/evidence/message checks.
- Required SQL/access checks: SQL-01, SQL-02, SQL-03, SQL-04, SQL-08, SQL-14, SQL-16. Owner Privacy executor: privacy_data_erasure.

### DataExportBundle

Export manifest bound to exact bytes, object version, digest and generation.

- Object: `app.data_export_bundles`. Class: AUTHORITATIVE_OWNER_STATE. Stage: LATER_OWNER_ORDERED_SLICE.
- Stable key: id. Foreign keys: privacyRequest → PrivacyRequest, candidateObjectVersionId → MediaObjectVersion?.
- Physical changes: DB-C02: restrictive immutable-key FKs; Privacy deletes/anonymizes explicitly in reviewed order; DB-C03: UTC-capable timestamptz(6) physical instants; DB-C03: owner-local CAS revision; no global ordering; DB-C05: export-ready requires complete accounting plus actual versioned bytes; DB-C16: typed objectVersionId binding to canonical MediaObjectVersion; SQL-08: server transaction identity for atomic source/evidence/message checks.
- Required SQL/access checks: SQL-01, SQL-02, SQL-03, SQL-04, SQL-08, SQL-14, SQL-16. Owner Privacy executor: privacy_data_erasure.

### PrivacyTargetInstruction

Versioned immutable owner/action/field-map instruction; no universal source crawler.

- Object: `app.privacy_target_instruction`. Class: IMMUTABLE_EVIDENCE_OR_RECEIPT. Stage: F0_FOUNDATION.
- Stable key: id. Foreign keys: request → PrivacyRequest.
- Physical changes: DB-C05; SQL-08: server transaction identity for atomic source/evidence/message checks.
- Required SQL/access checks: SQL-01, SQL-02, SQL-03, SQL-04, SQL-08, SQL-14, SQL-16. Owner Privacy executor: privacy_data_erasure.

### PrivacyOwnerReceipt

Actual completed/retained/omitted/failed/unknown owner disposition for one generation, not accepted-as-completed.

- Object: `app.privacy_owner_receipt`. Class: IMMUTABLE_EVIDENCE_OR_RECEIPT. Stage: F0_FOUNDATION.
- Stable key: id. Foreign keys: instruction → PrivacyTargetInstruction.
- Physical changes: DB-C05; SQL-08: server transaction identity for atomic source/evidence/message checks.
- Required SQL/access checks: SQL-01, SQL-02, SQL-03, SQL-04, SQL-08, SQL-14, SQL-16. Owner Privacy executor: privacy_data_erasure.

### PrivacyRestoreMarker

Owner erasure/restriction generation tombstone reapplied before restored data may be served.

- Object: `app.privacy_restore_marker`. Class: AUTHORITATIVE_OWNER_STATE. Stage: F0_FOUNDATION.
- Stable key: id. Foreign keys: receipt → PrivacyOwnerReceipt.
- Physical changes: DB-C05; SQL-08: server transaction identity for atomic source/evidence/message checks.
- Required SQL/access checks: SQL-01, SQL-02, SQL-03, SQL-04, SQL-08, SQL-14, SQL-16. Owner Privacy executor: privacy_data_erasure.

### PrivacyExportManifestItem

Complete per-owner retained/omitted/exported accounting for a bound export artifact.

- Object: `app.privacy_export_manifest_item`. Class: AUTHORITATIVE_OWNER_STATE. Stage: LATER_OWNER_ORDERED_SLICE.
- Stable key: id. Foreign keys: bundle → DataExportBundle, instruction → PrivacyTargetInstruction, receipt → PrivacyOwnerReceipt.
- Physical changes: DB-C05; SQL-08: server transaction identity for atomic source/evidence/message checks.
- Required SQL/access checks: SQL-01, SQL-02, SQL-03, SQL-04, SQL-08, SQL-14, SQL-16. Owner Privacy executor: privacy_data_erasure.

## professional_eligibility

### ProfessionalProfile

One-to-one seller identity and source lifecycle; readiness/reputation mirrors are non-authorizing.

- Object: `app.professional_profiles`. Class: AUTHORITATIVE_OWNER_STATE. Stage: F0_FOUNDATION.
- Stable key: id. Foreign keys: user → User.
- Physical changes: DB-C02: restrictive immutable-key FKs; Privacy deletes/anonymizes explicitly in reviewed order; DB-C03: UTC-capable timestamptz(6) physical instants; DB-C03: owner-local CAS revision; no global ordering; DB-C05: owner erasure/restriction generation prevents resurrection; SQL-08: server transaction identity for atomic source/evidence/message checks.
- Required SQL/access checks: SQL-01, SQL-02, SQL-03, SQL-04, SQL-08, SQL-16. Owner Privacy executor: professional_eligibility.

### ProfessionalCategory

Professional-owned selected category relationship.

- Object: `app.professional_categories`. Class: AUTHORITATIVE_OWNER_STATE. Stage: LATER_OWNER_ORDERED_SLICE.
- Stable key: professionalProfileId, categoryId. Foreign keys: professionalProfile → ProfessionalProfile, category → TaxonomyCategory.
- Physical changes: DB-C02: restrictive immutable-key FKs; Privacy deletes/anonymizes explicitly in reviewed order; SQL-08: server transaction identity for atomic source/evidence/message checks.
- Required SQL/access checks: SQL-01, SQL-02, SQL-03, SQL-04, SQL-08, SQL-16. Owner Privacy executor: professional_eligibility.

### ProfessionalTag

Professional-owned controlled tag assignment and provenance.

- Object: `app.professional_tags`. Class: AUTHORITATIVE_OWNER_STATE. Stage: LATER_OWNER_ORDERED_SLICE.
- Stable key: professionalProfileId, tagId. Foreign keys: professionalProfile → ProfessionalProfile, tag → TaxonomyTag.
- Physical changes: DB-C02: restrictive immutable-key FKs; Privacy deletes/anonymizes explicitly in reviewed order; DB-C03: UTC-capable timestamptz(6) physical instants; SQL-08: server transaction identity for atomic source/evidence/message checks.
- Required SQL/access checks: SQL-01, SQL-02, SQL-03, SQL-04, SQL-08, SQL-16. Owner Privacy executor: professional_eligibility.

### ProfessionalProfileMedia

Professional-owned explicit profile Media attachment.

- Object: `app.professional_profile_media`. Class: AUTHORITATIVE_OWNER_STATE. Stage: LATER_OWNER_ORDERED_SLICE.
- Stable key: professionalProfileId, mediaId. Foreign keys: professionalProfile → ProfessionalProfile, media → MediaAsset.
- Physical changes: DB-C02: restrictive immutable-key FKs; Privacy deletes/anonymizes explicitly in reviewed order; SQL-08: server transaction identity for atomic source/evidence/message checks.
- Required SQL/access checks: SQL-01, SQL-02, SQL-03, SQL-04, SQL-08, SQL-16. Owner Privacy executor: professional_eligibility.

## review_dispute

### Review

Order-linked genuine feedback/reputation source and reviewed publication state.

- Object: `app.reviews`. Class: AUTHORITATIVE_OWNER_STATE. Stage: LATER_OWNER_ORDERED_SLICE.
- Stable key: id. Foreign keys: order → Order, professionalProfile → ProfessionalProfile?.
- Physical changes: DB-C02: restrictive immutable-key FKs; Privacy deletes/anonymizes explicitly in reviewed order; DB-C03: UTC-capable timestamptz(6) physical instants; DB-C03: owner-local CAS revision; no global ordering; SQL-08: server transaction identity for atomic source/evidence/message checks.
- Required SQL/access checks: SQL-01, SQL-02, SQL-03, SQL-04, SQL-08, SQL-16, SQL-18. Owner Privacy executor: review_dispute.

### Dispute

Adjudication source; financial action goes through Order then Payment.

- Object: `app.disputes`. Class: AUTHORITATIVE_OWNER_STATE. Stage: LATER_OWNER_ORDERED_SLICE.
- Stable key: id. Foreign keys: order → Order.
- Physical changes: DB-C02: restrictive immutable-key FKs; Privacy deletes/anonymizes explicitly in reviewed order; DB-C03: UTC-capable timestamptz(6) physical instants; DB-C03: owner-local CAS revision; no global ordering; SQL-08: server transaction identity for atomic source/evidence/message checks.
- Required SQL/access checks: SQL-01, SQL-02, SQL-03, SQL-04, SQL-08, SQL-16, SQL-18. Owner Privacy executor: review_dispute.

## search_public_visibility

### SearchUpsertEvent

Search work projection with generation/effect receipt, not the runner or source truth.

- Object: `app.search_upsert_events`. Class: PROJECTION_NOT_AUTHORITY. Stage: LATER_OWNER_ORDERED_SLICE.
- Stable key: id. Foreign keys: none; typed registered descriptor scope is explicit in the SQL companion.
- Physical changes: DB-C03: UTC-capable timestamptz(6) physical instants; SQL-08: server transaction identity for atomic source/evidence/message checks.
- Required SQL/access checks: SQL-01, SQL-02, SQL-03, SQL-04, SQL-08, SQL-16. Owner Privacy executor: search_public_visibility.

## sweepstakes_prize

### PrizeDrawing

Later-phase prize definition; no launch activation.

- Object: `app.prize_drawings`. Class: AUTHORITATIVE_OWNER_STATE. Stage: LATER_LAUNCH_DISABLED.
- Stable key: id. Foreign keys: none; typed registered descriptor scope is explicit in the SQL companion.
- Physical changes: DB-C03: UTC-capable timestamptz(6) physical instants; DB-C03: owner-local CAS revision; no global ordering; SQL-08: server transaction identity for atomic source/evidence/message checks.
- Required SQL/access checks: SQL-01, SQL-02, SQL-03, SQL-04, SQL-08, SQL-16. Owner Privacy executor: sweepstakes_prize.

### SweepstakesEntryMethod

Later-phase official-rule entry method without paid odds advantage.

- Object: `app.sweepstakes_entry_methods`. Class: AUTHORITATIVE_OWNER_STATE. Stage: LATER_LAUNCH_DISABLED.
- Stable key: id. Foreign keys: drawing → PrizeDrawing.
- Physical changes: DB-C02: restrictive immutable-key FKs; Privacy deletes/anonymizes explicitly in reviewed order; DB-C03: UTC-capable timestamptz(6) physical instants; DB-C03: owner-local CAS revision; no global ordering; SQL-08: server transaction identity for atomic source/evidence/message checks.
- Required SQL/access checks: SQL-01, SQL-02, SQL-03, SQL-04, SQL-08, SQL-16. Owner Privacy executor: sweepstakes_prize.

### PrizeEntry

Later-phase immutable source-qualified entry and eligibility snapshot.

- Object: `app.prize_entries`. Class: AUTHORITATIVE_OWNER_STATE. Stage: LATER_LAUNCH_DISABLED.
- Stable key: id. Foreign keys: drawing → PrizeDrawing, user → User, order → Order?, entryMethod → SweepstakesEntryMethod?.
- Physical changes: DB-C02: restrictive immutable-key FKs; Privacy deletes/anonymizes explicitly in reviewed order; DB-C03: UTC-capable timestamptz(6) physical instants; SQL-08: server transaction identity for atomic source/evidence/message checks.
- Required SQL/access checks: SQL-01, SQL-02, SQL-03, SQL-04, SQL-08, SQL-16. Owner Privacy executor: sweepstakes_prize.

### PrizeWinning

Later-phase winner/fulfillment state; drawing alone is not fulfillment.

- Object: `app.prize_winnings`. Class: AUTHORITATIVE_OWNER_STATE. Stage: LATER_LAUNCH_DISABLED.
- Stable key: id. Foreign keys: drawing → PrizeDrawing, user → User, blockedByHold → ComplianceHold?, taxProfile → TaxProfile?.
- Physical changes: DB-C02: restrictive immutable-key FKs; Privacy deletes/anonymizes explicitly in reviewed order; DB-C03: UTC-capable timestamptz(6) physical instants; DB-C03: owner-local CAS revision; no global ordering; SQL-08: server transaction identity for atomic source/evidence/message checks.
- Required SQL/access checks: SQL-01, SQL-02, SQL-03, SQL-04, SQL-08, SQL-16. Owner Privacy executor: sweepstakes_prize.

### PrizeTaxYearSummary

Non-authorizing prize projection of Payment tax aggregation.

- Object: `app.prize_tax_year_summaries`. Class: PROJECTION_NOT_AUTHORITY. Stage: LATER_LAUNCH_DISABLED.
- Stable key: id. Foreign keys: user → User, taxProfile → TaxProfile?.
- Physical changes: DB-C02: restrictive immutable-key FKs; Privacy deletes/anonymizes explicitly in reviewed order; DB-C03: UTC-capable timestamptz(6) physical instants; DB-C03: owner-local CAS revision; no global ordering; DB-C13: legal fiscal aggregate dimensions remain distinct; SQL-08: server transaction identity for atomic source/evidence/message checks.
- Required SQL/access checks: SQL-01, SQL-02, SQL-03, SQL-04, SQL-08, SQL-16. Owner Privacy executor: sweepstakes_prize.

### PrizeDrawingRun

Later-phase immutable official-rule/population/algorithm drawing run; no launch execution.

- Object: `app.prize_drawing_run`. Class: AUTHORITATIVE_OWNER_STATE. Stage: LATER_LAUNCH_DISABLED.
- Stable key: id. Foreign keys: drawing → PrizeDrawing, selectedEntry → PrizeEntry?.
- Physical changes: DB-C16; SQL-08: server transaction identity for atomic source/evidence/message checks.
- Required SQL/access checks: SQL-01, SQL-02, SQL-03, SQL-04, SQL-08, SQL-16. Owner Privacy executor: sweepstakes_prize.

### PrizePopulationMember

Later-phase immutable frozen eligible population; no silent redraw or paid odds change.

- Object: `app.prize_population_member`. Class: IMMUTABLE_EVIDENCE_OR_RECEIPT. Stage: LATER_LAUNCH_DISABLED.
- Stable key: id. Foreign keys: run → PrizeDrawingRun, entry → PrizeEntry.
- Physical changes: DB-C16; SQL-08: server transaction identity for atomic source/evidence/message checks.
- Required SQL/access checks: SQL-01, SQL-02, SQL-03, SQL-04, SQL-08, SQL-16. Owner Privacy executor: sweepstakes_prize.

### PrizeFulfillmentReceipt

Later-phase actual fulfillment/valuation receipt; winning does not establish taxable fulfillment.

- Object: `app.prize_fulfillment_receipt`. Class: IMMUTABLE_EVIDENCE_OR_RECEIPT. Stage: LATER_LAUNCH_DISABLED.
- Stable key: id. Foreign keys: winning → PrizeWinning, effect → RuntimeEffectReceipt.
- Physical changes: DB-C16; SQL-08: server transaction identity for atomic source/evidence/message checks.
- Required SQL/access checks: SQL-01, SQL-02, SQL-03, SQL-04, SQL-07, SQL-08, SQL-16. Owner Privacy executor: sweepstakes_prize.

## taxonomy_classification

### TaxonomyDomain

Controlled taxonomy domain dictionary.

- Object: `app.taxonomy_domains`. Class: AUTHORITATIVE_OWNER_STATE. Stage: LATER_OWNER_ORDERED_SLICE.
- Stable key: id. Foreign keys: none; typed registered descriptor scope is explicit in the SQL companion.
- Physical changes: DB-C03: UTC-capable timestamptz(6) physical instants; DB-C03: owner-local CAS revision; no global ordering; SQL-08: server transaction identity for atomic source/evidence/message checks.
- Required SQL/access checks: SQL-01, SQL-02, SQL-03, SQL-04, SQL-08, SQL-16. Owner Privacy executor: taxonomy_classification.

### TaxonomyCategory

Controlled domain category and classification requirement inputs.

- Object: `app.taxonomy_categories`. Class: AUTHORITATIVE_OWNER_STATE. Stage: LATER_OWNER_ORDERED_SLICE.
- Stable key: id. Foreign keys: domain → TaxonomyDomain.
- Physical changes: DB-C02: restrictive immutable-key FKs; Privacy deletes/anonymizes explicitly in reviewed order; DB-C03: UTC-capable timestamptz(6) physical instants; DB-C03: owner-local CAS revision; no global ordering; SQL-08: server transaction identity for atomic source/evidence/message checks.
- Required SQL/access checks: SQL-01, SQL-02, SQL-03, SQL-04, SQL-08, SQL-16. Owner Privacy executor: taxonomy_classification.

### TaxonomyTag

Controlled L3 discovery vocabulary; AI never writes authoritative vocabulary.

- Object: `app.taxonomy_tags`. Class: AUTHORITATIVE_OWNER_STATE. Stage: LATER_OWNER_ORDERED_SLICE.
- Stable key: id. Foreign keys: category → TaxonomyCategory.
- Physical changes: DB-C02: restrictive immutable-key FKs; Privacy deletes/anonymizes explicitly in reviewed order; DB-C03: UTC-capable timestamptz(6) physical instants; DB-C03: owner-local CAS revision; no global ordering; SQL-08: server transaction identity for atomic source/evidence/message checks.
- Required SQL/access checks: SQL-01, SQL-02, SQL-03, SQL-04, SQL-08, SQL-16. Owner Privacy executor: taxonomy_classification.

## track_subscription_entitlement

### OrganizationFeatureAccess

Track-owned Organization commercial projection; monetized ATS remains gated.

- Object: `app.organization_feature_access`. Class: AUTHORITATIVE_OWNER_STATE. Stage: LATER_OWNER_ORDERED_SLICE.
- Stable key: id. Foreign keys: organization → Organization.
- Physical changes: DB-C02: restrictive immutable-key FKs; Privacy deletes/anonymizes explicitly in reviewed order; DB-C03: UTC-capable timestamptz(6) physical instants; DB-C03: owner-local CAS revision; no global ordering; SQL-08: server transaction identity for atomic source/evidence/message checks.
- Required SQL/access checks: SQL-01, SQL-02, SQL-03, SQL-04, SQL-07, SQL-08, SQL-12, SQL-16. Owner Privacy executor: track_subscription_entitlement.

### TrackPlan

Versioned Track-owned base benefit catalog; no seeded commercial promise here.

- Object: `app.track_plans`. Class: AUTHORITATIVE_OWNER_STATE. Stage: F0_FOUNDATION.
- Stable key: id. Foreign keys: none; typed registered descriptor scope is explicit in the SQL companion.
- Physical changes: DB-C03: UTC-capable timestamptz(6) physical instants; DB-C03: owner-local CAS revision; no global ordering; DB-C01: source-owned immutable activated policy/catalog revision; SQL-08: server transaction identity for atomic source/evidence/message checks.
- Required SQL/access checks: SQL-01, SQL-02, SQL-03, SQL-04, SQL-07, SQL-08, SQL-12, SQL-16. Owner Privacy executor: track_subscription_entitlement.

### TrackPlanPrice

Qualified paid billing mapping; Free has no provider subscription.

- Object: `app.track_plan_prices`. Class: AUTHORITATIVE_OWNER_STATE. Stage: LATER_OWNER_ORDERED_SLICE.
- Stable key: id. Foreign keys: plan → TrackPlan.
- Physical changes: DB-C02: restrictive immutable-key FKs; Privacy deletes/anonymizes explicitly in reviewed order; DB-C03: UTC-capable timestamptz(6) physical instants; DB-C03: owner-local CAS revision; no global ordering; SQL-08: server transaction identity for atomic source/evidence/message checks.
- Required SQL/access checks: SQL-01, SQL-02, SQL-03, SQL-04, SQL-07, SQL-08, SQL-12, SQL-16. Owner Privacy executor: track_subscription_entitlement.

### TrackEntitlementDefinition

Typed named benefit definition; no premium Boolean authority.

- Object: `app.track_entitlement_definitions`. Class: AUTHORITATIVE_OWNER_STATE. Stage: F0_FOUNDATION.
- Stable key: id. Foreign keys: none; typed registered descriptor scope is explicit in the SQL companion.
- Physical changes: DB-C03: UTC-capable timestamptz(6) physical instants; DB-C03: owner-local CAS revision; no global ordering; SQL-08: server transaction identity for atomic source/evidence/message checks.
- Required SQL/access checks: SQL-01, SQL-02, SQL-03, SQL-04, SQL-07, SQL-08, SQL-12, SQL-16. Owner Privacy executor: track_subscription_entitlement.

### TrackPlanEntitlement

Typed immutable plan benefit value selected under a catalog revision.

- Object: `app.track_plan_entitlements`. Class: AUTHORITATIVE_OWNER_STATE. Stage: F0_FOUNDATION.
- Stable key: id. Foreign keys: plan → TrackPlan, entitlement → TrackEntitlementDefinition.
- Physical changes: DB-C02: restrictive immutable-key FKs; Privacy deletes/anonymizes explicitly in reviewed order; DB-C03: UTC-capable timestamptz(6) physical instants; DB-C03: owner-local CAS revision; no global ordering; SQL-08: server transaction identity for atomic source/evidence/message checks.
- Required SQL/access checks: SQL-01, SQL-02, SQL-03, SQL-04, SQL-07, SQL-08, SQL-12, SQL-16. Owner Privacy executor: track_subscription_entitlement.

### TrackSubscription

Retained explicit provider-neutral enrollment/billing history.

- Object: `app.track_subscriptions`. Class: AUTHORITATIVE_OWNER_STATE. Stage: F0_FOUNDATION.
- Stable key: id. Foreign keys: user → User, plan → TrackPlan, customerProfile → CustomerProfile?, candidateProfile → CandidateProfile?, professionalProfile → ProfessionalProfile?.
- Physical changes: DB-C02: restrictive immutable-key FKs; Privacy deletes/anonymizes explicitly in reviewed order; DB-C03: UTC-capable timestamptz(6) physical instants; DB-C03: owner-local CAS revision; no global ordering; DB-C12/R030: explicit provider-neutral Free enrollment, never a Stripe zero-price subscription; SQL-08: server transaction identity for atomic source/evidence/message checks.
- Required SQL/access checks: SQL-01, SQL-02, SQL-03, SQL-04, SQL-07, SQL-08, SQL-12, SQL-16. Owner Privacy executor: track_subscription_entitlement.

### TrackEntitlementGrant

Current source-qualified typed grant and revocation interval.

- Object: `app.track_entitlement_grants`. Class: AUTHORITATIVE_OWNER_STATE. Stage: F0_FOUNDATION.
- Stable key: id. Foreign keys: user → User, subscription → TrackSubscription?, entitlement → TrackEntitlementDefinition, customerProfile → CustomerProfile?, candidateProfile → CandidateProfile?, professionalProfile → ProfessionalProfile?.
- Physical changes: DB-C02: restrictive immutable-key FKs; Privacy deletes/anonymizes explicitly in reviewed order; DB-C03: UTC-capable timestamptz(6) physical instants; DB-C03: owner-local CAS revision; no global ordering; SQL-08: server transaction identity for atomic source/evidence/message checks.
- Required SQL/access checks: SQL-01, SQL-02, SQL-03, SQL-04, SQL-07, SQL-08, SQL-12, SQL-16. Owner Privacy executor: track_subscription_entitlement.

### TrackUsageEvent

Immutable accepted usage/correction under semantic effect and UTC period.

- Object: `app.track_usage_events`. Class: IMMUTABLE_EVIDENCE_OR_RECEIPT. Stage: F0_FOUNDATION.
- Stable key: id. Foreign keys: user → User, subscription → TrackSubscription?, entitlementGrant → TrackEntitlementGrant?, entitlement → TrackEntitlementDefinition?, customerProfile → CustomerProfile?, candidateProfile → CandidateProfile?, professionalProfile → ProfessionalProfile?, candidateEffectReceiptId → RuntimeEffectReceipt.
- Physical changes: DB-C02: restrictive immutable-key FKs; Privacy deletes/anonymizes explicitly in reviewed order; DB-C03: UTC-capable timestamptz(6) physical instants; DB-C11: durable source/economic effect uniqueness, beyond transport deduplication; DB-C12: retained usage source; counters cannot reset accepted history; DB-C12: accepted source time, not runner retry time, fixes UTC quota period; DB-C16: typed effectReceiptId binding to canonical RuntimeEffectReceipt; SQL-08: server transaction identity for atomic source/evidence/message checks.
- Required SQL/access checks: SQL-01, SQL-02, SQL-03, SQL-04, SQL-07, SQL-08, SQL-12, SQL-16. Owner Privacy executor: track_subscription_entitlement.

### TrackUsageCounter

Rebuildable same-period aggregate; never destructive monthly reset truth.

- Object: `app.track_usage_counters`. Class: PROJECTION_NOT_AUTHORITY. Stage: F0_FOUNDATION.
- Stable key: id. Foreign keys: user → User, subscription → TrackSubscription?, entitlementGrant → TrackEntitlementGrant?, entitlement → TrackEntitlementDefinition, customerProfile → CustomerProfile?, candidateProfile → CandidateProfile?, professionalProfile → ProfessionalProfile?.
- Physical changes: DB-C02: restrictive immutable-key FKs; Privacy deletes/anonymizes explicitly in reviewed order; DB-C03: UTC-capable timestamptz(6) physical instants; DB-C03: owner-local CAS revision; no global ordering; DB-C12: retained usage source; counters cannot reset accepted history; SQL-08: server transaction identity for atomic source/evidence/message checks.
- Required SQL/access checks: SQL-01, SQL-02, SQL-03, SQL-04, SQL-07, SQL-08, SQL-12, SQL-16. Owner Privacy executor: track_subscription_entitlement.

### TrackSubscriptionEvent

Immutable enrollment/billing/selection transition evidence.

- Object: `app.track_subscription_events`. Class: IMMUTABLE_EVIDENCE_OR_RECEIPT. Stage: F0_FOUNDATION.
- Stable key: id. Foreign keys: subscription → TrackSubscription?, plan → TrackPlan?, user → User.
- Physical changes: DB-C02: restrictive immutable-key FKs; Privacy deletes/anonymizes explicitly in reviewed order; DB-C03: UTC-capable timestamptz(6) physical instants; SQL-08: server transaction identity for atomic source/evidence/message checks.
- Required SQL/access checks: SQL-01, SQL-02, SQL-03, SQL-04, SQL-07, SQL-08, SQL-12, SQL-16. Owner Privacy executor: track_subscription_entitlement.

### TrackBaseSelection

Exactly one current base enrollment selection per User/track, including provider-neutral Free.

- Object: `app.track_base_selection`. Class: AUTHORITATIVE_OWNER_STATE. Stage: F0_FOUNDATION.
- Stable key: id. Foreign keys: user → User, enrollment → TrackSubscription, customer → CustomerProfile?, candidate → CandidateProfile?, professional → ProfessionalProfile?.
- Physical changes: DB-C12; SQL-08: server transaction identity for atomic source/evidence/message checks.
- Required SQL/access checks: SQL-01, SQL-02, SQL-03, SQL-04, SQL-07, SQL-08, SQL-12, SQL-16. Owner Privacy executor: track_subscription_entitlement.

### TrackEnrollmentReceipt

Immutable default-Free source/selection outcome; delayed Free cannot downgrade paid selection.

- Object: `app.track_enrollment_receipt`. Class: IMMUTABLE_EVIDENCE_OR_RECEIPT. Stage: F0_FOUNDATION.
- Stable key: id. Foreign keys: user → User, selection → TrackBaseSelection, effect → RuntimeEffectReceipt.
- Physical changes: DB-C12; SQL-08: server transaction identity for atomic source/evidence/message checks.
- Required SQL/access checks: SQL-01, SQL-02, SQL-03, SQL-04, SQL-07, SQL-08, SQL-12, SQL-16. Owner Privacy executor: track_subscription_entitlement.

### TrackUsageReservation

Owner quota/period reservation bound to accepted usage and fenced shared reservation.

- Object: `app.track_usage_reservation`. Class: AUTHORITATIVE_OWNER_STATE. Stage: F0_FOUNDATION.
- Stable key: id. Foreign keys: user → User, entitlement → TrackEntitlementDefinition, reservation → RuntimeReservation.
- Physical changes: DB-C12; SQL-08: server transaction identity for atomic source/evidence/message checks.
- Required SQL/access checks: SQL-01, SQL-02, SQL-03, SQL-04, SQL-07, SQL-08, SQL-12, SQL-16. Owner Privacy executor: track_subscription_entitlement.

## transaction_order

### Order

Transaction truth and one approved source family, not payment-provider state.

- Object: `app.orders`. Class: AUTHORITATIVE_OWNER_STATE. Stage: LATER_OWNER_ORDERED_SLICE.
- Stable key: id. Foreign keys: customerProfile → CustomerProfile, offering → Offering?, gigAssignment → GigAssignment?, buyerUser → User, sellerProfessionalProfile → ProfessionalProfile?.
- Physical changes: DB-C02: restrictive immutable-key FKs; Privacy deletes/anonymizes explicitly in reviewed order; DB-C03: UTC-capable timestamptz(6) physical instants; DB-C03: owner-local CAS revision; no global ordering; DB-C06/R003: screening seller is null; marketplace seller remains required by SQL invariant; DB-C06: optional FK only for approved screening source; DB-C06/R076: fresh buyer flows bind SH-004 Customer identity; old database untouched; DB-C06: coherent commercial buyer relation; DB-C07/R048: financial effect source is PaymentEffect/PayoutTransfer, not an Order mirror; SQL-08: server transaction identity for atomic source/evidence/message checks.
- Required SQL/access checks: SQL-01, SQL-02, SQL-03, SQL-04, SQL-08, SQL-10, SQL-11, SQL-13, SQL-16. Owner Privacy executor: transaction_order.

### OrderFile

Order-owned explicit attachment and purchased-context relationship.

- Object: `app.order_files`. Class: AUTHORITATIVE_OWNER_STATE. Stage: LATER_OWNER_ORDERED_SLICE.
- Stable key: id. Foreign keys: order → Order, media → MediaAsset.
- Physical changes: DB-C02: restrictive immutable-key FKs; Privacy deletes/anonymizes explicitly in reviewed order; DB-C03: UTC-capable timestamptz(6) physical instants; SQL-08: server transaction identity for atomic source/evidence/message checks.
- Required SQL/access checks: SQL-01, SQL-02, SQL-03, SQL-04, SQL-08, SQL-10, SQL-11, SQL-13, SQL-16. Owner Privacy executor: transaction_order.

### OrderEvent

Immutable Order lifecycle history under source revision and semantic effect.

- Object: `app.order_events`. Class: IMMUTABLE_EVIDENCE_OR_RECEIPT. Stage: LATER_OWNER_ORDERED_SLICE.
- Stable key: id. Foreign keys: order → Order.
- Physical changes: DB-C02: restrictive immutable-key FKs; Privacy deletes/anonymizes explicitly in reviewed order; DB-C03: UTC-capable timestamptz(6) physical instants; SQL-08: server transaction identity for atomic source/evidence/message checks.
- Required SQL/access checks: SQL-01, SQL-02, SQL-03, SQL-04, SQL-08, SQL-10, SQL-11, SQL-13, SQL-16. Owner Privacy executor: transaction_order.

### AgreementTemplate

Versioned reviewed immutable agreement template; draft is not legal approval.

- Object: `app.agreement_templates`. Class: AUTHORITATIVE_OWNER_STATE. Stage: LATER_OWNER_ORDERED_SLICE.
- Stable key: id. Foreign keys: templateMedia → MediaAsset?, createdByUser → User?, approvedByUser → User?.
- Physical changes: DB-C02: restrictive immutable-key FKs; Privacy deletes/anonymizes explicitly in reviewed order; DB-C03: UTC-capable timestamptz(6) physical instants; DB-C03: owner-local CAS revision; no global ordering; SQL-08: server transaction identity for atomic source/evidence/message checks.
- Required SQL/access checks: SQL-01, SQL-02, SQL-03, SQL-04, SQL-08, SQL-10, SQL-11, SQL-13, SQL-16. Owner Privacy executor: transaction_order.

### AgreementElectronicConsent

Exact execution-revision electronic delivery/consent proof.

- Object: `app.agreement_electronic_consents`. Class: AUTHORITATIVE_OWNER_STATE. Stage: LATER_OWNER_ORDERED_SLICE.
- Stable key: id. Foreign keys: agreement → Agreement, user → User, consentLog → ConsentLog?, candidateExecutionRevisionId → AgreementExecutionRevision.
- Physical changes: DB-C02: restrictive immutable-key FKs; Privacy deletes/anonymizes explicitly in reviewed order; DB-C03: UTC-capable timestamptz(6) physical instants; DB-C03: owner-local CAS revision; no global ordering; DB-C16: typed executionRevisionId binding to canonical AgreementExecutionRevision; SQL-08: server transaction identity for atomic source/evidence/message checks.
- Required SQL/access checks: SQL-01, SQL-02, SQL-03, SQL-04, SQL-08, SQL-10, SQL-11, SQL-13, SQL-16. Owner Privacy executor: transaction_order.

### AgreementSignature

Signer and document proof for one immutable execution revision.

- Object: `app.agreement_signatures`. Class: AUTHORITATIVE_OWNER_STATE. Stage: LATER_OWNER_ORDERED_SLICE.
- Stable key: id. Foreign keys: agreement → Agreement, user → User?, consent → AgreementElectronicConsent?, signatureImageMedia → MediaAsset?, signedDocumentSnapshot → AgreementDocumentSnapshot?, candidateExecutionRevisionId → AgreementExecutionRevision.
- Physical changes: DB-C02: restrictive immutable-key FKs; Privacy deletes/anonymizes explicitly in reviewed order; DB-C03: UTC-capable timestamptz(6) physical instants; DB-C03: owner-local CAS revision; no global ordering; DB-C16: typed executionRevisionId binding to canonical AgreementExecutionRevision; SQL-08: server transaction identity for atomic source/evidence/message checks.
- Required SQL/access checks: SQL-01, SQL-02, SQL-03, SQL-04, SQL-08, SQL-10, SQL-11, SQL-13, SQL-16. Owner Privacy executor: transaction_order.

### AgreementDocumentSnapshot

Exact immutable rendered/signed document bytes and digest.

- Object: `app.agreement_document_snapshots`. Class: IMMUTABLE_EVIDENCE_OR_RECEIPT. Stage: LATER_OWNER_ORDERED_SLICE.
- Stable key: id. Foreign keys: agreement → Agreement, mediaAsset → MediaAsset, generatedByUser → User?, candidateExecutionRevisionId → AgreementExecutionRevision.
- Physical changes: DB-C02: restrictive immutable-key FKs; Privacy deletes/anonymizes explicitly in reviewed order; DB-C03: UTC-capable timestamptz(6) physical instants; DB-C16: typed executionRevisionId binding to canonical AgreementExecutionRevision; SQL-08: server transaction identity for atomic source/evidence/message checks.
- Required SQL/access checks: SQL-01, SQL-02, SQL-03, SQL-04, SQL-08, SQL-10, SQL-11, SQL-13, SQL-16. Owner Privacy executor: transaction_order.

### AgreementEvent

Append-only agreement execution/correction history.

- Object: `app.agreement_events`. Class: IMMUTABLE_EVIDENCE_OR_RECEIPT. Stage: LATER_OWNER_ORDERED_SLICE.
- Stable key: id. Foreign keys: agreement → Agreement, actorUser → User?.
- Physical changes: DB-C02: restrictive immutable-key FKs; Privacy deletes/anonymizes explicitly in reviewed order; DB-C03: UTC-capable timestamptz(6) physical instants; SQL-08: server transaction identity for atomic source/evidence/message checks.
- Required SQL/access checks: SQL-01, SQL-02, SQL-03, SQL-04, SQL-08, SQL-10, SQL-11, SQL-13, SQL-16. Owner Privacy executor: transaction_order.

### AgreementAccessGrant

Current purpose/actor/execution-revision-bound document access.

- Object: `app.agreement_access_grants`. Class: AUTHORITATIVE_OWNER_STATE. Stage: LATER_OWNER_ORDERED_SLICE.
- Stable key: id. Foreign keys: agreement → Agreement, user → User, documentSnapshot → AgreementDocumentSnapshot?.
- Physical changes: DB-C02: restrictive immutable-key FKs; Privacy deletes/anonymizes explicitly in reviewed order; DB-C03: UTC-capable timestamptz(6) physical instants; DB-C03: owner-local CAS revision; no global ordering; DB-C08: protected grant currentness and revocation binding; SQL-08: server transaction identity for atomic source/evidence/message checks.
- Required SQL/access checks: SQL-01, SQL-02, SQL-03, SQL-04, SQL-08, SQL-10, SQL-11, SQL-13, SQL-16. Owner Privacy executor: transaction_order.

### Agreement

Order-owned agreement lifecycle pointing to normalized immutable execution proof.

- Object: `app.agreements`. Class: AUTHORITATIVE_OWNER_STATE. Stage: LATER_OWNER_ORDERED_SLICE.
- Stable key: id. Foreign keys: order → Order, template → AgreementTemplate?, supersededByAgreement → Agreement?.
- Physical changes: DB-C02: restrictive immutable-key FKs; Privacy deletes/anonymizes explicitly in reviewed order; DB-C03: UTC-capable timestamptz(6) physical instants; DB-C03: owner-local CAS revision; no global ordering; DB-C07/R076: fresh candidate uses normalized execution/signature/document proof; SQL-08: server transaction identity for atomic source/evidence/message checks.
- Required SQL/access checks: SQL-01, SQL-02, SQL-03, SQL-04, SQL-08, SQL-10, SQL-11, SQL-13, SQL-16. Owner Privacy executor: transaction_order.

### OrderScreeningSource

Trust package/quote and self-paid subject for the approved screening Order family.

- Object: `app.order_screening_source`. Class: AUTHORITATIVE_OWNER_STATE. Stage: LATER_OWNER_ORDERED_SLICE.
- Stable key: id. Foreign keys: order → Order, package → VerificationPackage, subject → User, professional → ProfessionalProfile?, candidate → CandidateProfile?.
- Physical changes: DB-C06; SQL-08: server transaction identity for atomic source/evidence/message checks.
- Required SQL/access checks: SQL-01, SQL-02, SQL-03, SQL-04, SQL-08, SQL-10, SQL-11, SQL-13, SQL-16. Owner Privacy executor: transaction_order.

### AgreementExecutionRevision

Immutable normalized execution scope, parties, template and document revision.

- Object: `app.agreement_execution_revision`. Class: IMMUTABLE_EVIDENCE_OR_RECEIPT. Stage: LATER_OWNER_ORDERED_SLICE.
- Stable key: id. Foreign keys: agreement → Agreement, purchase → OrderPurchaseRevision.
- Physical changes: DB-C07; SQL-08: server transaction identity for atomic source/evidence/message checks.
- Required SQL/access checks: SQL-01, SQL-02, SQL-03, SQL-04, SQL-08, SQL-10, SQL-11, SQL-13, SQL-16. Owner Privacy executor: transaction_order.

### OrderPurchaseRevision

Frozen purchased scope and price/fee/rights snapshot; later Track changes never reprice it.

- Object: `app.order_purchase_revision`. Class: IMMUTABLE_EVIDENCE_OR_RECEIPT. Stage: LATER_OWNER_ORDERED_SLICE.
- Stable key: id. Foreign keys: order → Order.
- Physical changes: DB-C06; SQL-08: server transaction identity for atomic source/evidence/message checks.
- Required SQL/access checks: SQL-01, SQL-02, SQL-03, SQL-04, SQL-08, SQL-10, SQL-11, SQL-13, SQL-16. Owner Privacy executor: transaction_order.

### OrderSessionReservation

Purchased session/unit reservation, distinct from Booking interval lock.

- Object: `app.order_session_reservation`. Class: AUTHORITATIVE_OWNER_STATE. Stage: LATER_OWNER_ORDERED_SLICE.
- Stable key: id. Foreign keys: purchase → OrderPurchaseRevision, booking → Booking?, reservation → RuntimeReservation, unit → OrderPurchasedUnit.
- Physical changes: DB-C11; SQL-08: server transaction identity for atomic source/evidence/message checks.
- Required SQL/access checks: SQL-01, SQL-02, SQL-03, SQL-04, SQL-08, SQL-10, SQL-11, SQL-13, SQL-16. Owner Privacy executor: transaction_order.

### OrderPurchasedUnit

Immutable named deliverable/session/access unit of one purchased revision; reservations consume this exact unit.

- Object: `app.order_purchased_unit`. Class: IMMUTABLE_EVIDENCE_OR_RECEIPT. Stage: LATER_OWNER_ORDERED_SLICE.
- Stable key: id. Foreign keys: purchase → OrderPurchaseRevision.
- Physical changes: DB-C06; SQL-08: server transaction identity for atomic source/evidence/message checks.
- Required SQL/access checks: SQL-01, SQL-02, SQL-03, SQL-04, SQL-08, SQL-10, SQL-11, SQL-13, SQL-16. Owner Privacy executor: transaction_order.

### CheckoutTaxLocationEvidence

Immutable private buyer/quote evidence descriptor and encrypted closed-schema fields; tax legality/provider validation remains external.

- Object: `app.checkout_tax_location_evidence`. Class: IMMUTABLE_EVIDENCE_OR_RECEIPT. Stage: LATER_OWNER_ORDERED_SLICE.
- Stable key: id. Foreign keys: order → Order, purchase → OrderPurchaseRevision, buyer → User, customer → CustomerProfile.
- Physical changes: DB-C16; SQL-08: server transaction identity for atomic source/evidence/message checks.
- Required SQL/access checks: SQL-01, SQL-02, SQL-03, SQL-04, SQL-08, SQL-10, SQL-11, SQL-13, SQL-16. Owner Privacy executor: transaction_order.

## trust_verification_screening

### VerificationPackage

Versioned Trust screening package and commercial quote inputs; not clearance or Payment truth.

- Object: `app.verification_packages`. Class: AUTHORITATIVE_OWNER_STATE. Stage: LATER_OWNER_ORDERED_SLICE.
- Stable key: id. Foreign keys: none; typed registered descriptor scope is explicit in the SQL companion.
- Physical changes: DB-C03: UTC-capable timestamptz(6) physical instants; DB-C03: owner-local CAS revision; no global ordering; DB-C09: legacy default amount is not adopted commercial approval; DB-C09: exact approved policy must be supplied; no inferred legal finality; DB-C01: source-owned immutable activated policy/catalog revision; SQL-08: server transaction identity for atomic source/evidence/message checks.
- Required SQL/access checks: SQL-01, SQL-02, SQL-03, SQL-04, SQL-08, SQL-16. Owner Privacy executor: trust_verification_screening.

### VerificationPackageItem

One priced check component of a Trust package.

- Object: `app.verification_package_items`. Class: AUTHORITATIVE_OWNER_STATE. Stage: LATER_OWNER_ORDERED_SLICE.
- Stable key: id. Foreign keys: package → VerificationPackage.
- Physical changes: DB-C02: restrictive immutable-key FKs; Privacy deletes/anonymizes explicitly in reviewed order; SQL-08: server transaction identity for atomic source/evidence/message checks.
- Required SQL/access checks: SQL-01, SQL-02, SQL-03, SQL-04, SQL-08, SQL-16. Owner Privacy executor: trust_verification_screening.

### VerificationRequirement

Versioned subject/source requirement; cannot invent screening applicability.

- Object: `app.verification_requirements`. Class: AUTHORITATIVE_OWNER_STATE. Stage: LATER_OWNER_ORDERED_SLICE.
- Stable key: id. Foreign keys: verificationPackage → VerificationPackage?.
- Physical changes: DB-C02: restrictive immutable-key FKs; Privacy deletes/anonymizes explicitly in reviewed order; DB-C03: UTC-capable timestamptz(6) physical instants; DB-C03: owner-local CAS revision; no global ordering; SQL-08: server transaction identity for atomic source/evidence/message checks.
- Required SQL/access checks: SQL-01, SQL-02, SQL-03, SQL-04, SQL-08, SQL-16. Owner Privacy executor: trust_verification_screening.

### VerificationConsent

Screening-specific subject/purpose authorization linked to exact Consent proof.

- Object: `app.verification_consents`. Class: AUTHORITATIVE_OWNER_STATE. Stage: LATER_OWNER_ORDERED_SLICE.
- Stable key: id. Foreign keys: user → User, consentLog → ConsentLog?.
- Physical changes: DB-C02: restrictive immutable-key FKs; Privacy deletes/anonymizes explicitly in reviewed order; DB-C03: UTC-capable timestamptz(6) physical instants; SQL-08: server transaction identity for atomic source/evidence/message checks.
- Required SQL/access checks: SQL-01, SQL-02, SQL-03, SQL-04, SQL-08, SQL-16. Owner Privacy executor: trust_verification_screening.

### VerificationCheck

Trust-owned provider check with original account/event/effect correlation.

- Object: `app.verification_checks`. Class: AUTHORITATIVE_OWNER_STATE. Stage: LATER_OWNER_ORDERED_SLICE.
- Stable key: id. Foreign keys: user → User, professionalProfile → ProfessionalProfile?, candidateProfile → CandidateProfile?, requirement → VerificationRequirement?, consentLog → ConsentLog?, verificationPackage → VerificationPackage?, screeningFeeOrder → Order?.
- Physical changes: DB-C02: restrictive immutable-key FKs; Privacy deletes/anonymizes explicitly in reviewed order; DB-C03: UTC-capable timestamptz(6) physical instants; DB-C03: owner-local CAS revision; no global ordering; SQL-08: server transaction identity for atomic source/evidence/message checks.
- Required SQL/access checks: SQL-01, SQL-02, SQL-03, SQL-04, SQL-08, SQL-16. Owner Privacy executor: trust_verification_screening.

### FcraAdverseActionWorkflow

Conditional reviewed notice/dispute sequence, not an invented statutory timer.

- Object: `app.fcra_adverse_action_workflows`. Class: AUTHORITATIVE_OWNER_STATE. Stage: LATER_OWNER_ORDERED_SLICE.
- Stable key: id. Foreign keys: verificationCheck → VerificationCheck.
- Physical changes: DB-C02: restrictive immutable-key FKs; Privacy deletes/anonymizes explicitly in reviewed order; DB-C03: UTC-capable timestamptz(6) physical instants; DB-C03: owner-local CAS revision; no global ordering; SQL-08: server transaction identity for atomic source/evidence/message checks.
- Required SQL/access checks: SQL-01, SQL-02, SQL-03, SQL-04, SQL-08, SQL-16. Owner Privacy executor: trust_verification_screening.

### ProfessionalLicenseCredential

Applicable professional credential scope, jurisdiction and currentness evidence.

- Object: `app.professional_license_credentials`. Class: AUTHORITATIVE_OWNER_STATE. Stage: LATER_OWNER_ORDERED_SLICE.
- Stable key: id. Foreign keys: user → User, professionalProfile → ProfessionalProfile?.
- Physical changes: DB-C02: restrictive immutable-key FKs; Privacy deletes/anonymizes explicitly in reviewed order; DB-C03: UTC-capable timestamptz(6) physical instants; DB-C03: owner-local CAS revision; no global ordering; SQL-08: server transaction identity for atomic source/evidence/message checks.
- Required SQL/access checks: SQL-01, SQL-02, SQL-03, SQL-04, SQL-08, SQL-16. Owner Privacy executor: trust_verification_screening.

### TrustBadge

Derived current verification display; never permission to perform a service.

- Object: `app.trust_badges`. Class: PROJECTION_NOT_AUTHORITY. Stage: LATER_OWNER_ORDERED_SLICE.
- Stable key: id. Foreign keys: user → User, professionalProfile → ProfessionalProfile?, candidateProfile → CandidateProfile?, verificationCheck → VerificationCheck?.
- Physical changes: DB-C02: restrictive immutable-key FKs; Privacy deletes/anonymizes explicitly in reviewed order; DB-C03: UTC-capable timestamptz(6) physical instants; SQL-08: server transaction identity for atomic source/evidence/message checks.
- Required SQL/access checks: SQL-01, SQL-02, SQL-03, SQL-04, SQL-08, SQL-16. Owner Privacy executor: trust_verification_screening.

## video_session

### JobInterviewVideoRoom

Video desired/applied room generation bound to Interview revision.

- Object: `app.job_interview_video_rooms`. Class: AUTHORITATIVE_OWNER_STATE. Stage: LATER_OWNER_ORDERED_SLICE.
- Stable key: id. Foreign keys: interview → JobInterview.
- Physical changes: DB-C02: restrictive immutable-key FKs; Privacy deletes/anonymizes explicitly in reviewed order; DB-C03: UTC-capable timestamptz(6) physical instants; DB-C03: owner-local CAS revision; no global ordering; DB-C08/R076: participant bearer credentials issued on demand, never reusable plaintext storage; DB-C08: exact parent/audience/room generation binding; SQL-08: server transaction identity for atomic source/evidence/message checks.
- Required SQL/access checks: SQL-01, SQL-02, SQL-03, SQL-04, SQL-08, SQL-13, SQL-15, SQL-16. Owner Privacy executor: video_session.

### BookingVideoRoom

Video desired/applied room generation bound to Booking revision.

- Object: `app.booking_video_rooms`. Class: AUTHORITATIVE_OWNER_STATE. Stage: LATER_OWNER_ORDERED_SLICE.
- Stable key: id. Foreign keys: booking → Booking.
- Physical changes: DB-C02: restrictive immutable-key FKs; Privacy deletes/anonymizes explicitly in reviewed order; DB-C03: UTC-capable timestamptz(6) physical instants; DB-C03: owner-local CAS revision; no global ordering; DB-C08/R076: participant bearer credentials issued on demand, never reusable plaintext storage; DB-C08: exact parent/audience/room generation binding; SQL-08: server transaction identity for atomic source/evidence/message checks.
- Required SQL/access checks: SQL-01, SQL-02, SQL-03, SQL-04, SQL-08, SQL-13, SQL-15, SQL-16. Owner Privacy executor: video_session.

### CourseVideoAsset

Video course asset; canonical courseDetailsId equals Offering identity.

- Object: `app.course_video_assets`. Class: AUTHORITATIVE_OWNER_STATE. Stage: LATER_OWNER_ORDERED_SLICE.
- Stable key: id. Foreign keys: courseDetails → CourseDetails, sourceMediaAsset → MediaAsset?, createdByUser → User?.
- Physical changes: DB-C02: restrictive immutable-key FKs; Privacy deletes/anonymizes explicitly in reviewed order; DB-C03: UTC-capable timestamptz(6) physical instants; DB-C03: owner-local CAS revision; no global ordering; DB-C08: current exact video asset generation; SQL-08: server transaction identity for atomic source/evidence/message checks.
- Required SQL/access checks: SQL-01, SQL-02, SQL-03, SQL-04, SQL-08, SQL-13, SQL-15, SQL-16. Owner Privacy executor: video_session.

### CourseVideoPlaybackGrant

Current acquired-right/context/object-generation playback credential evidence.

- Object: `app.course_video_playback_grants`. Class: AUTHORITATIVE_OWNER_STATE. Stage: LATER_OWNER_ORDERED_SLICE.
- Stable key: id. Foreign keys: courseVideoAsset → CourseVideoAsset, user → User, order → Order?.
- Physical changes: DB-C02: restrictive immutable-key FKs; Privacy deletes/anonymizes explicitly in reviewed order; DB-C03: UTC-capable timestamptz(6) physical instants; DB-C08: protected grant currentness and revocation binding; SQL-08: server transaction identity for atomic source/evidence/message checks.
- Required SQL/access checks: SQL-01, SQL-02, SQL-03, SQL-04, SQL-08, SQL-13, SQL-15, SQL-16. Owner Privacy executor: video_session.

### CourseVideoPlaybackEvent

Actual playback observation for a bound grant; no automatic refund denial.

- Object: `app.course_video_playback_events`. Class: IMMUTABLE_EVIDENCE_OR_RECEIPT. Stage: LATER_OWNER_ORDERED_SLICE.
- Stable key: id. Foreign keys: courseVideoAsset → CourseVideoAsset, playbackGrant → CourseVideoPlaybackGrant?, user → User?, order → Order?.
- Physical changes: DB-C02: restrictive immutable-key FKs; Privacy deletes/anonymizes explicitly in reviewed order; DB-C03: UTC-capable timestamptz(6) physical instants; SQL-08: server transaction identity for atomic source/evidence/message checks.
- Required SQL/access checks: SQL-01, SQL-02, SQL-03, SQL-04, SQL-08, SQL-13, SQL-15, SQL-16. Owner Privacy executor: video_session.

### ProcessedVideoProviderEvent

Verified account/event transport receipt with current parent generation.

- Object: `app.processed_video_provider_events`. Class: IMMUTABLE_EVIDENCE_OR_RECEIPT. Stage: LATER_OWNER_ORDERED_SLICE.
- Stable key: id. Foreign keys: none; typed registered descriptor scope is explicit in the SQL companion.
- Physical changes: DB-C03: UTC-capable timestamptz(6) physical instants; DB-C14/R018: verified provider/account/event identity and fingerprint; SQL-08: server transaction identity for atomic source/evidence/message checks.
- Required SQL/access checks: SQL-01, SQL-02, SQL-03, SQL-04, SQL-08, SQL-13, SQL-15, SQL-16. Owner Privacy executor: video_session.
