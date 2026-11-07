#!/usr/bin/env python3
"""Reproduce the review-only Prisma candidate and extend the existing model ledger.

Reads source/architecture files only. Never invokes Prisma, a shell or a database.
This is a physical review representation, not an adopted schema or SQL generator.
"""
import hashlib
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REC = ROOT / 'context/reconciliation'
OUT = ROOT / 'prisma/review'
BLOCK = re.compile(r'^(model|enum)\s+(\w+)\s*\{(.*?)^\}', re.M | re.S)
FIELD = re.compile(r'^\s*(\w+)\s+([\w\[\]?]+)(.*)$')


def sha(data):
    return hashlib.sha256(data).hexdigest()


def parse(text):
    return {name: {'kind': kind, 'body': body} for kind, name, body in BLOCK.findall(text)}


def fields(body):
    result = []
    for line in body.splitlines():
        m = FIELD.match(line)
        if m and not line.strip().startswith(('/', '*', '@')):
            result.append({'name': m[1], 'type': m[2], 'attributes': m[3].strip()})
    return result


def add(body, text):
    existing = {f['name'] for f in fields(body)}
    for line in text.strip().splitlines():
        m = FIELD.match(line)
        if m and m[1] in existing:
            continue
        body += '\n  ' + line.strip()
    return body + '\n'


def replace_field(body, field, replacement):
    pattern = r'^\s*' + re.escape(field) + r'\s+[^\n]+$'
    assert re.search(pattern, body, re.M), field
    return re.sub(pattern, '\n  ' + replacement if replacement else '', body, flags=re.M)


def remove_field(body, field):
    return replace_field(body, field, '')


def map_name(name):
    return re.sub(r'(?<!^)(?=[A-Z])', '_', name).lower()


# Owner-specific purpose statements supplement the exact field/FK/constraint ledger.
PURPOSES = '''
VerificationPackage|Versioned Trust screening package and commercial quote inputs; not clearance or Payment truth
VerificationPackageItem|One priced check component of a Trust package
ConsentLog|Immutable exact presented-content acceptance by subject, context and command identity
PrivacyRequest|Verified data-rights request and orchestration state; no invented legal response timer
AgeGateAttempt|Minimized Identity eligibility attempt, distinct from Consent acknowledgment
AgeGateBlock|Purpose-bound Identity abuse/rate restriction, not a minor account
FuzzyLocationCache|Derived fuzzy Location projection; never an exact-location fallback
LocationReveal|Purpose/parent/current-generation-bound exact-location reveal evidence
KycVerification|Payment provider verification mapping and currentness, not Professional readiness
TaxProfile|Protected Payment tax-subject/provider verification reference
TaxDocument|Protected tax-document evidence associated with a tax profile
TaxYearEarningsSummary|Derived Payment aggregate partitioned by legal subject/year/currency/jurisdiction/regime
TaxReportingSubmission|Payment filing submission and provider outcome, externally gated
TaxReportingRecipient|One submission recipient and retained filing amount/outcome evidence
PayoutAccount|Professional connected financial account and actual capability state
ProviderRequirementSnapshot|Immutable provider/account requirement snapshot, not legal approval
ProfessionalBalanceLedgerEntry|Signed append-only economic ledger under Payment effect identity
PayoutRequest|Authorized payout request and its current lifecycle, separate from external execution
PayoutTransfer|One reconciled external payout/transfer effect with durable semantic identity
ComplianceHold|Independent protective source cause and release cycle, never payment dispatch
DataErasureJob|Privacy erasure orchestration projection over current instructions/receipts
DataErasureTarget|Legacy target summary bound to a typed owner instruction; no cascade coverage inference
DataRetentionExemption|Reviewed lawful retained disposition and basis reference; no universal retention period
DataExportBundle|Export manifest bound to exact bytes, object version, digest and generation
Report|Retained source report and moderation intake, not a proved violation
LegalNotice|Protected legal intake and reviewed service/applicability evidence
ModerationCase|Authorized moderation case lifecycle and current decision cycle
ModerationAction|Immutable typed enforcement/restoration decision, not foreign source mutation
PrizeDrawing|Later-phase prize definition; no launch activation
SweepstakesEntryMethod|Later-phase official-rule entry method without paid odds advantage
PrizeEntry|Later-phase immutable source-qualified entry and eligibility snapshot
PrizeWinning|Later-phase winner/fulfillment state; drawing alone is not fulfillment
PrizeTaxYearSummary|Non-authorizing prize projection of Payment tax aggregation
HealthcareComplianceProfile|Conditional regulated applicability/coverage, not a therapy launch permission
BaaAgreement|Conditional reviewed agreement/account coverage evidence, not an executed-BAA assumption
HealthcareDataBoundary|Context-specific regulated classification; no universal sensitivity ranking
HealthcareAdminAccessPolicy|Explicit regulated administrative purpose and access disposition
AccessAuditLog|Durable protected-disclosure proof before secret delivery
GamificationProgram|Versioned ordinary rewards program, distinct from prize competitions
GamificationRule|Versioned source-qualified reward rule; no unapproved earning event
PointLedgerEntry|Signed immutable User-wide points effect; Professional is contextual only
Challenge|Ordinary rewards challenge definition, not prize entry
ChallengeParticipant|User participation and source-qualified challenge completion
Leaderboard|Derived comparison definition; never balance or entitlement truth
LeaderboardEntry|Rebuildable derived ranking; cannot authorize a reward
Reward|Versioned supported reward benefit and inventory definition
RewardRedemption|Reserved supported benefit and actual fulfillment/reversal lifecycle
VerificationRequirement|Versioned subject/source requirement; cannot invent screening applicability
VerificationConsent|Screening-specific subject/purpose authorization linked to exact Consent proof
VerificationCheck|Trust-owned provider check with original account/event/effect correlation
FcraAdverseActionWorkflow|Conditional reviewed notice/dispute sequence, not an invented statutory timer
ProfessionalLicenseCredential|Applicable professional credential scope, jurisdiction and currentness evidence
TrustBadge|Derived current verification display; never permission to perform a service
User|Local account principal; not a seller or inferred commercial buyer
UserRole|Identity-owned platform role assignment; Role policy remains code-first
Organization|Hiring entity and source identity; never an Offering seller
OrganizationMember|Current hiring membership and role; last-owner invariants remain Hiring-owned
OrganizationFeatureAccess|Track-owned Organization commercial projection; monetized ATS remains gated
ProfessionalProfile|One-to-one seller identity and source lifecycle; readiness/reputation mirrors are non-authorizing
CustomerProfile|One-to-one commercial buyer provisioned before buyer actions
CandidateProfile|One-to-one applicant identity with private resume and opt-in discovery
TaxonomyDomain|Controlled taxonomy domain dictionary
TaxonomyCategory|Controlled domain category and classification requirement inputs
TaxonomyTag|Controlled L3 discovery vocabulary; AI never writes authoritative vocabulary
ProfessionalCategory|Professional-owned selected category relationship
ProfessionalTag|Professional-owned controlled tag assignment and provenance
CandidateCategory|Candidate-owned selected category relationship
CandidateTag|Candidate-owned controlled tag assignment and provenance
OrganizationCategory|Hiring-owned selected Organization category relationship
OrganizationTag|Hiring-owned controlled Organization tag assignment and provenance
Offering|Professional-owned sellable supply and publication lifecycle
ServiceDetails|Service-specific immutable-at-purchase Offering scope inputs
ProductDetails|Product delivery definition; file access stays Media/Digital-owned
CourseDetails|Course identity is Offering ID and defines purchased course scope
PricingTier|Source price definition selected into an immutable purchase revision
OfferingMedia|Marketplace-owned explicit Media attachment; not Media ownership
OfferingTag|Marketplace-owned controlled tag assignment and provenance
Gig|Customer public paid request source; neither Job nor Offering
GigTag|Gig-owned controlled tag assignment and provenance
GigResponse|Professional response and acceptance input for a Gig
GigAssignment|Retained accepted proposal/winner slot; Order outcome is a projection
Job|Organization-owned hiring source, compensation and publication revision
JobCompensationDisclosure|Derived reviewed compensation disclosure bound to Hiring source/rules
JobApplication|Candidate-owned accepted application and stage; no automated ranking
JobApplicationViewEvent|Immutable purpose-bound protected application-view evidence
JobInterview|Interview source parent/successor/schedule/participants, not Application status
JobInterviewParticipant|Current Interview audience membership and response state
JobInterviewEvent|Retained Interview transition/evidence history
JobInterviewVideoRoom|Video desired/applied room generation bound to Interview revision
JobTag|Hiring-owned controlled Job tag assignment and provenance
JobComplianceCheck|Immutable Job-input/rule-version evaluation, with separate review decision
JobComplianceRule|Versioned jurisdiction rule supplied/approved externally; no statutory invention
JobComplianceFinding|Canonical bounded finding evidence; legacy aliases removed from fresh candidate
JobApplicationMedia|Candidate-owned explicit application/resume attachment
CandidateSearchProjection|Opt-in source-generation-bound minimized discovery projection
ResumeParseResult|Protected source/generation-bound extraction only, not ranking or eligibility
ResumeAccessLog|Durable authorized resume-delivery proof before credential issuance
Order|Transaction truth and one approved source family, not payment-provider state
OrderFile|Order-owned explicit attachment and purchased-context relationship
OrderEvent|Immutable Order lifecycle history under source revision and semantic effect
AgreementTemplate|Versioned reviewed immutable agreement template; draft is not legal approval
AgreementElectronicConsent|Exact execution-revision electronic delivery/consent proof
AgreementSignature|Signer and document proof for one immutable execution revision
AgreementDocumentSnapshot|Exact immutable rendered/signed document bytes and digest
AgreementEvent|Append-only agreement execution/correction history
AgreementAccessGrant|Current purpose/actor/execution-revision-bound document access
Agreement|Order-owned agreement lifecycle pointing to normalized immutable execution proof
Review|Order-linked genuine feedback/reputation source and reviewed publication state
Dispute|Adjudication source; financial action goes through Order then Payment
MediaAsset|Media identity and exact current object generation, never parent relationship ownership
MediaUploadPolicy|Immutable activated policy revision and exact historical content
MediaUploadSession|Dedicated upload-attempt state linked to immutable policy revision
MediaValidationResult|Exact input object/attempt inspection evidence, not URL readiness
MediaScanResult|Qualified scan result for exact object generation/checksum
MediaProcessingResult|Actual input/output bytes and metadata-removal evidence
MediaAccessGrant|Current contextual permission/proof bound to exact object version and operations
MediaAccessEvent|Append-only actual grant/byte access evidence; not proof of human consumption
GigMedia|Gig-owned explicit Media attachment
UserMedia|Identity-owned explicit User-profile Media attachment
ProfessionalProfileMedia|Professional-owned explicit profile Media attachment
CandidateProfileMedia|Candidate-owned explicit profile Media attachment
OrganizationMedia|Hiring-owned explicit Organization Media attachment
JobMedia|Hiring-owned explicit Job Media attachment
BookingSlotLock|Exclusive interval reservation and authoritative hold-to-lock relation
CalendarConnection|Booking-owned scoped calendar consent/account capability and revocation generation
AvailabilityRule|Versioned timezone-aware availability input, not an eligibility grant
BusyWindow|Minimized provider busy-time projection, never private event content by default
BookingOrchestrationRun|Booking workflow projection over the single shared runner
BookingOrchestrationStep|Source-specific desired effect/receipt reference; not another executable queue
Booking|Purchased appointment source with coherent buyer/order/session and parent revisions
BookingHold|Preliminary slot hold; lock relation comes from BookingSlotLock
BookingEvent|Retained Booking transition/outcome evidence; no-show is not money authority
BookingVideoRoom|Video desired/applied room generation bound to Booking revision
ProcessedCalendarEvent|Verified account-scoped calendar event fingerprint and disposition
Thread|Messaging source context with one matching concrete parent family
ThreadParticipant|Current conversation audience; historical membership is not permission
Message|Contextual conversation source and owner-controlled edit/removal lifecycle
MessageMedia|Messaging-owned explicit Media attachment
SearchUpsertEvent|Search work projection with generation/effect receipt, not the runner or source truth
ProcessedStripeEvent|Verified account/event transport receipt; not an economic-effect ledger
AuditEvent|Append-only bounded decision/effect audit intent and retained evidence
Notification|Finite source-qualified safe recipient intent, not legal service/business completion
NotificationSubscription|Protected endpoint/device generation and permission; no plaintext tokens
NotificationDelivery|One endpoint/source generation attempt and actual provider outcome
NotificationSubscriptionEvent|Immutable endpoint/permission/revocation generation evidence
OrganizationNotificationSetting|Hiring-owned permitted Organization notification audience preference
UserSecurityProfile|Current Identity security generation, restrictions and assurance prerequisites
AuthProviderAccount|Unique provider/account subject to local User binding
PasskeyCredential|Protected public-key credential metadata; never raw biometric material
StepUpChallenge|Action/target/security-generation-bound challenge, not general elevated access
SensitiveActionSession|Bounded owner action assurance, never a universal admin session
AccountRecoveryRequest|Identity-owned recovery verification and revocation lifecycle
UserSecurityEvent|Immutable Identity security/assignment/recovery change evidence
CourseVideoAsset|Video course asset; canonical courseDetailsId equals Offering identity
CourseVideoPlaybackGrant|Current acquired-right/context/object-generation playback credential evidence
CourseVideoPlaybackEvent|Actual playback observation for a bound grant; no automatic refund denial
ProcessedVideoProviderEvent|Verified account/event transport receipt with current parent generation
DigitalGoodsPolicy|Immutable purchase-disclosure/license policy; access never automatically bars refunds
DigitalGoodsTermsAcceptance|Exact historical purchase/policy/Consent binding
DigitalDownloadAsset|Qualified protected deliverable bound to Offering and exact Media object
DigitalDownloadGrant|Current acquired-right/context/object-generation download credential evidence
DigitalDownloadEvent|Actual download observation, not automatic refund finality
SalesTaxCalculation|Payment tax calculation bound to immutable Order quote and private evidence
SalesTaxLineItem|Calculation line/jurisdiction result, not originating Offering price truth
SalesTaxTransaction|Actual tax recording/reversal under approved liability policy
ChildDirectedContentDeclaration|Later-phase child-directed declaration; disabled at 18+ launch
MinorPrivacyControl|Later-phase child-specific control; no minor-account workaround
CourseAccessibilityAsset|Qualified accessible course derivative bound to actual Media bytes
TrackPlan|Versioned Track-owned base benefit catalog; no seeded commercial promise here
TrackPlanPrice|Qualified paid billing mapping; Free has no provider subscription
TrackEntitlementDefinition|Typed named benefit definition; no premium Boolean authority
TrackPlanEntitlement|Typed immutable plan benefit value selected under a catalog revision
TrackSubscription|Retained explicit provider-neutral enrollment/billing history
TrackEntitlementGrant|Current source-qualified typed grant and revocation interval
TrackUsageEvent|Immutable accepted usage/correction under semantic effect and UTC period
TrackUsageCounter|Rebuildable same-period aggregate; never destructive monthly reset truth
TrackSubscriptionEvent|Immutable enrollment/billing/selection transition evidence
'''
PURPOSE = dict(line.split('|', 1) for line in PURPOSES.strip().splitlines())


def build():
    OUT.mkdir(parents=True, exist_ok=True)
    source = (ROOT / 'prisma/schema.prisma').read_text()
    original = parse(source)
    models = {n: v['body'] for n, v in original.items() if v['kind'] == 'model'}
    enums = {n: v['body'] for n, v in original.items() if v['kind'] == 'enum'}
    inventory_path = REC / 'greenfield-model-security-inventory.json'
    inventory = json.loads(inventory_path.read_text())
    owners = {x['model']: x['source_owner'] for x in inventory['models']}
    assert len(models) == 177 and set(models) == set(owners) == set(PURPOSE)
    changes = {n: [] for n in models}

    def add_to(n, text, why):
        models[n] = add(models[n], text)
        changes[n].append(why)

    def set_field(n, f, value, why):
        models[n] = replace_field(models[n], f, value)
        changes[n].append(why)

    def drop(n, f, why):
        if f in {x['name'] for x in fields(models[n])}:
            models[n] = remove_field(models[n], f)
            models[n] = re.sub(r'^\s*@@(?:index|unique)\(\[([^\]]+)\][^\n]*$', lambda m: '' if f in [x.strip() for x in m[1].split(',')] else m[0], models[n], flags=re.M)
            changes[n].append(why)

    # Explicitly retain historical source; only this separate representation changes.
    for n, body in models.items():
        lines = []
        for line in body.splitlines():
            if '@relation' in line and 'fields:' in line:
                line = re.sub(r'onDelete:\s*\w+', 'onDelete: Restrict', line)
                if 'onDelete:' not in line:
                    pos = line.index(')', line.index('@relation'))
                    line = line[:pos] + ', onDelete: Restrict' + line[pos:]
                if 'onUpdate:' not in line:
                    pos = line.index(')', line.index('@relation'))
                    line = line[:pos] + ', onUpdate: Restrict' + line[pos:]
            if re.match(r'\s*\w+\s+DateTime\??\b', line) and '@db.' not in line:
                line += ' @db.Timestamptz(6)'
            lines.append(line)
        models[n] = '\n'.join(lines) + '\n'
        if 'onDelete: Cascade' in body or ('@relation' in body and 'fields:' in body):
            changes[n].append('DB-C02: restrictive immutable-key FKs; Privacy deletes/anonymizes explicitly in reviewed order')
        if any(f['type'].startswith('DateTime') for f in fields(body)):
            changes[n].append('DB-C03: UTC-capable timestamptz(6) physical instants')
        if '@updatedAt' in body or n in {'Review', 'Dispute', 'ComplianceHold', 'OrganizationMember', 'UserRole', 'ThreadParticipant'}:
            add_to(n, 'revision BigInt @default(0) @map("revision")', 'DB-C03: owner-local CAS revision; no global ordering')

    # Brain P0-C-03A: immutable age attempts/blocks; no mutable zero-revision reuse.
    for n in ['AgeGateAttempt', 'AgeGateBlock']:
        changes[n].append('P0-C-03A/DRAFT-03: append-only Identity evidence; extension/retry is a new semantic row')

    add_to('UserSecurityProfile', 'securityGeneration BigInt @default(0) @map("security_generation")', 'DB-C04: current security-generation binding')
    for n in ['User', 'CustomerProfile', 'ProfessionalProfile', 'CandidateProfile', 'JobApplication', 'MediaAsset', 'CandidateSearchProjection', 'PrivacyRequest', 'NotificationSubscription']:
        add_to(n, 'privacyGeneration BigInt @default(0) @map("privacy_generation")', 'DB-C05: owner erasure/restriction generation prevents resurrection')
    set_field('CandidateProfile', 'isVisible', 'isVisible Boolean @default(false) @map("is_visible")', 'R045: discovery is opt-in; private by default')
    add_to('CandidateProfile', 'discoveryPreferenceRevision BigInt @default(0) @map("discovery_preference_revision")\ndiscoveryEnabledAt DateTime? @map("discovery_enabled_at") @db.Timestamptz(6)', 'R045: affirmative participation and its source revision, not inferred visibility')
    drop('CandidateProfile', 'resumeUrl', 'R045/R050: protected resume bytes use explicit Media attachments, never a reusable URL field')
    add_to('ConsentLog', 'acceptanceKey String @map("acceptance_key")\nfingerprint String @db.Char(64)\nactionOwner String @map("action_owner")\naction String\ncontextKind String @map("context_kind")\ncontextId String? @map("context_id")\n@@unique([userId, acceptanceKey])', 'DB-C01/R019: scoped repeatable acceptance; new intentional reacceptance has a new key')
    add_to('ConsentLog', 'contextOwner String @map("context_owner")\npresentationHash String @map("presentation_hash") @db.Char(64)', 'B010-02: exact accepting user/action/context and rendered presentation hash')
    set_field('VerificationPackage', 'platformFeeCents', 'platformFeeCents Int @map("platform_fee_cents")', 'DB-C09: legacy default amount is not adopted commercial approval')
    set_field('VerificationPackage', 'nonRefundable', 'nonRefundable Boolean @map("non_refundable")', 'DB-C09: exact approved policy must be supplied; no inferred legal finality')

    # R003/R076: a source discriminator without a fabricated seller.
    enums['OrderSourceType'] = '\n  platform_screening\n' + enums['OrderSourceType']
    set_field('Order', 'sellerProfessionalProfileId', 'sellerProfessionalProfileId String? @map("seller_professional_profile_id") @db.Uuid', 'DB-C06/R003: screening seller is null; marketplace seller remains required by SQL invariant')
    for f in fields(models['Order']):
        if f['type'] == 'ProfessionalProfile' and 'sellerProfessionalProfileId' in f['attributes']:
            set_field('Order', f['name'], f['name'] + ' ProfessionalProfile? ' + f['attributes'], 'DB-C06: optional FK only for approved screening source')
    for n in ['Order', 'Booking', 'BookingHold', 'BookingSlotLock']:
        set_field(n, 'customerProfileId', 'customerProfileId String @map("customer_profile_id") @db.Uuid', 'DB-C06/R076: fresh buyer flows bind SH-004 Customer identity; old database untouched')
        for f in fields(models[n]):
            if f['type'] == 'CustomerProfile?':
                set_field(n, f['name'], f['name'] + ' CustomerProfile ' + f['attributes'], 'DB-C06: coherent commercial buyer relation')
    drop('Order', 'stripeTransferId', 'DB-C07/R048: financial effect source is PaymentEffect/PayoutTransfer, not an Order mirror')
    for f in ['buyerSigUrl', 'professionalSigUrl', 'pdfMediaId', 'finalDocumentHash', 'pdfMedia']:
        drop('Agreement', f, 'DB-C07/R076: fresh candidate uses normalized execution/signature/document proof')
    drop('MediaAsset', 'agreements', 'DB-C07: remove reverse relation for retired Agreement PDF mirror')
    drop('MediaAsset', 'agreementPdfs', 'DB-C07: remove actual reverse relation for retired Agreement PDF mirror')
    drop('BookingHold', 'lockId', 'DB-C07/R076: BookingSlotLock.bookingHoldId is the single authoritative relation')
    for n in ['Booking', 'BookingHold', 'BookingSlotLock']:
        drop(n, 'priorityRank', 'DB-C07/R012: early release is a policy window, never request ordering')
    for n in ['BookingVideoRoom', 'JobInterviewVideoRoom']:
        for f in ['buyerJoinUrl', 'professionalJoinUrl', 'candidateJoinUrl', 'interviewerJoinUrl']:
            drop(n, f, 'DB-C08/R076: participant bearer credentials issued on demand, never reusable plaintext storage')
        add_to(n, 'parentRevision BigInt @map("parent_revision")\ngeneration BigInt @default(0)\naudienceGeneration BigInt @default(0) @map("audience_generation")', 'DB-C08: exact parent/audience/room generation binding')
    for f in ['fieldName', 'matchedText', 'suggestedText']:
        drop('JobComplianceFinding', f, 'DB-C07/R076: canonical bounded sourceField/preview/hash/replacement only')
    set_field('JobComplianceFinding', 'sourceField', 'sourceField String @map("source_field")', 'DB-C07: canonical finding field identity is required')
    add_to('JobComplianceCheck', 'jobSourceRevision BigInt @map("job_source_revision")\nruleSetHash String @map("rule_set_hash") @db.Char(64)', 'R044: exact immutable Job input/rule-set binding')
    add_to('CandidateSearchProjection', 'sourceRevision BigInt @map("source_revision")\nparticipationGeneration BigInt @map("participation_generation")', 'R045: stale extraction cannot republish withdrawn discovery')
    add_to('CourseVideoAsset', 'sourceRevision BigInt @map("source_revision")\ngeneration BigInt @default(0)', 'DB-C08: current exact video asset generation')
    set_field('DigitalGoodsPolicy', 'refundPolicyType', 'refundPolicyType DigitalGoodsRefundPolicyType @default(custom) @map("refund_policy_type")', 'DB-C09/P09: no automatic final-after-access default; policy remains unapproved/gated')
    set_field('DigitalGoodsPolicy', 'offeringId', 'offeringId String @map("offering_id") @db.Uuid', 'DB-C01: retain multiple immutable policy revisions per Offering')
    add_to('DigitalGoodsPolicy', 'policyVersion String @map("policy_version")\ncontentHash String @map("content_hash") @db.Char(64)\nreviewState ReviewPolicyState @default(draft) @map("review_state")\nisCurrent Boolean @default(false) @map("is_current")\n@@unique([offeringId, policyVersion])', 'DB-C01: exact historical policy with one reviewed current selection')
    for f in fields(models['Offering']):
        if f['type'] == 'DigitalGoodsPolicy?':
            set_field('Offering', f['name'], f['name'] + ' DigitalGoodsPolicy[] ' + f['attributes'], 'DB-C01: policy history is one-to-many, not mutable single policy')
    for f in ['trackingCookiesAllowed', 'targetedAdsAllowed']:
        set_field('DigitalGoodsPolicy', f, f + ' Boolean @default(false) @map("' + map_name(f) + '")', 'DB-C09: optional tracking permission is never assumed from a policy default')
    for n in ['DigitalDownloadGrant', 'CourseVideoPlaybackGrant', 'MediaAccessGrant', 'AgreementAccessGrant']:
        add_to(n, 'sourceRevision BigInt @map("source_revision")\nsourceGeneration BigInt @map("source_generation")\nauthorityGeneration BigInt @map("authority_generation")', 'DB-C08: protected grant currentness and revocation binding')

    add_to('MediaUploadPolicy', 'version String\ncontentHash String @map("content_hash") @db.Char(64)\neffectiveAt DateTime @map("effective_at") @db.Timestamptz(6)', 'DB-C10/R076: immutable activated policy identity/content')
    models['MediaUploadPolicy'] = re.sub(r'@@unique\(\[context, status\]\)', '@@unique([context, version])', models['MediaUploadPolicy'])
    enums['MediaUploadAttemptState'] = '\n  initiated\n  uploading\n  uploaded\n  validating\n  scanning\n  processing\n  completed\n  failed\n  rejected\n  cancelled\n  expired\n  @@map("media_upload_attempt_state")\n  @@schema("app")\n'
    set_field('MediaUploadSession', 'status', 'status MediaUploadAttemptState @default(initiated)', 'DB-C10/R076: upload attempt lifecycle is distinct from MediaAsset')
    set_field('MediaUploadSession', 'policyId', 'policyId String @map("policy_id") @db.Uuid', 'DB-C10: every new attempt binds an immutable policy revision')
    for f in fields(models['MediaUploadSession']):
        if f['type'] == 'MediaUploadPolicy?':
            set_field('MediaUploadSession', f['name'], f['name'] + ' MediaUploadPolicy ' + f['attributes'], 'DB-C10: required immutable policy FK')

    for n in ['PointLedgerEntry', 'ProfessionalBalanceLedgerEntry', 'TrackUsageEvent']:
        add_to(n, 'semanticEffectKey String @unique @map("semantic_effect_key")', 'DB-C11: durable source/economic effect uniqueness, beyond transport deduplication')
    add_to('PayoutTransfer', 'semanticEffectKey String @unique @map("semantic_effect_key")', 'DB-C11: durable financial effect identity survives provider retry')
    add_to('PointLedgerEntry', 'sourceOwner String @map("source_owner")\nsourceFactId String @map("source_fact_id")\nsourceFactRevision String @map("source_fact_revision")\nruleVersion String @map("rule_version")\nreversesEntryId String? @map("reverses_entry_id") @db.Uuid', 'DB-C11: original source/rule and explicit compensating-entry lineage')
    for n in ['TrackUsageEvent', 'TrackUsageCounter']:
        add_to(n, 'sourceRevision BigInt @map("source_revision")', 'DB-C12: retained usage source; counters cannot reset accepted history')
    add_to('TrackUsageEvent', 'sourceOwner String @map("source_owner")\nsourceId String @map("source_id")\nacceptedAt DateTime @map("accepted_at") @db.Timestamptz(6)\nperiodStart DateTime @map("period_start") @db.Timestamptz(6)\nperiodEnd DateTime @map("period_end") @db.Timestamptz(6)', 'DB-C12: accepted source time, not runner retry time, fixes UTC quota period')
    for n in ['TrackPlan', 'GamificationRule', 'VerificationPackage']:
        add_to(n, 'version String\ncontentHash String @map("content_hash") @db.Char(64)', 'DB-C01: source-owned immutable activated policy/catalog revision')
    models['TrackPlan'] = models['TrackPlan'].replace('@@unique([track, key])', '@@unique([track, key, version])')
    enums['TrackBillingProvider'] = '\n  none\n' + enums['TrackBillingProvider']
    set_field('TrackSubscription', 'provider', 'provider TrackBillingProvider @default(none)', 'DB-C12/R030: explicit provider-neutral Free enrollment, never a Stripe zero-price subscription')
    for n in ['TaxYearEarningsSummary', 'PrizeTaxYearSummary']:
        add_to(n, 'jurisdiction String\nreportingRegime TaxReportingRegime @map("reporting_regime")', 'DB-C13: legal fiscal aggregate dimensions remain distinct')
        if n == 'TaxYearEarningsSummary':
            set_field(n, 'jurisdiction', 'jurisdiction String', 'DB-C13: explicit approved jurisdiction before tax activation')
            set_field(n, 'reportingRegime', 'reportingRegime TaxReportingRegime @map("reporting_regime")', 'DB-C13: no aggregation across reporting regimes')
        models[n] = re.sub(r'@@unique\(\[userId, taxYear, currency\]\)', '@@unique([userId, taxYear, currency, jurisdiction, reportingRegime])', models[n])
    for n in ['SalesTaxCalculation', 'SalesTaxTransaction']:
        set_field(n, 'liabilityRole', 'liabilityRole SalesTaxLiabilityRole @map("liability_role")', 'DB-C09/R037: tax liability is an explicit approved external policy, never a historical default')
    for n in ['ProcessedStripeEvent', 'ProcessedCalendarEvent', 'ProcessedVideoProviderEvent']:
        add_to(n, 'providerAccountScope String @map("provider_account_scope")\npayloadFingerprint String @map("payload_fingerprint") @db.Char(64)\nverifiedAt DateTime @map("verified_at") @db.Timestamptz(6)', 'DB-C14/R018: verified provider/account/event identity and fingerprint')
        models[n] = models[n].replace('@@unique([provider, providerEventId])', '@@unique([provider, providerAccountScope, providerEventId])')
    models['ProcessedStripeEvent'] = models['ProcessedStripeEvent'].replace('eventId    String   @id', 'eventId    String')
    # Match formatting independently of source alignment.
    models['ProcessedStripeEvent'] = re.sub(r'(eventId\s+String)\s+@id', r'\1', models['ProcessedStripeEvent'])
    models['ProcessedStripeEvent'] += '\n  @@id([providerAccountScope, eventId])\n'
    for f in ['endpoint', 'token', 'p256dh', 'auth']:
        drop('NotificationSubscription', f, 'DB-C15: remove raw endpoint/key mirrors; protected ciphertext plus scoped digest only')
    models['NotificationSubscription'] = re.sub(r'^\s*@@unique\(\[provider, (endpoint|token)\]\).*$', '', models['NotificationSubscription'], flags=re.M)
    add_to('NotificationSubscription', 'providerAccountScope String @map("provider_account_scope")\ngeneration BigInt @default(0)\n@@unique([provider, providerAccountScope, endpointHash, generation], map: "notification_endpoint_generation_uq")\n@@unique([provider, providerAccountScope, tokenHash, generation], map: "notification_token_generation_uq")', 'DB-C15: account/endpoint generation and active-recipient uniqueness specified in SQL register')

    add_to('PrivacyRequest', 'instructionGeneration BigInt @default(0) @map("instruction_generation")', 'DB-C05: new owner instructions invalidate old-generation completion')
    add_to('DataErasureJob', 'generation BigInt', 'DB-C05: exact request generation carried through orchestration')
    add_to('DataExportBundle', 'generation BigInt\nmanifestHash String? @map("manifest_hash") @db.Char(64)\nbytesHash String? @map("bytes_hash") @db.Char(64)\nsizeBytes BigInt? @map("size_bytes")', 'DB-C05: export-ready requires complete accounting plus actual versioned bytes')
    add_to('DataRetentionExemption', 'legalBasisRef String @map("legal_basis_ref")\npolicyVersion String @map("policy_version")', 'DB-C05: retained disposition needs approved basis, not a guessed timer')
    add_to('LocationReveal', 'interviewId String? @map("interview_id") @db.Uuid\npurpose String\ncontextRevision BigInt @map("context_revision")\nsourceGeneration BigInt @map("source_generation")', 'R071: separate Interview purpose and current parent/generation, no exact-location fallback')
    add_to('JobInterview', 'applicationRevision BigInt @map("application_revision")\naudienceGeneration BigInt @default(0) @map("audience_generation")\n@@unique([rescheduledFromInterviewId])', 'R046/R051: coherent current parent/audience and single successor chain')
    add_to('Booking', 'audienceGeneration BigInt @default(0) @map("audience_generation")\n@@unique([rescheduledFromBookingId])', 'R042: retain one successor and current appointment audience')
    set_field('Booking', 'overtimeGraceMinutes', 'overtimeGraceMinutes Int? @map("overtime_grace_minutes")', 'DB-C09: no unapproved numerical overtime/completion rule inferred from schema default')
    add_to('ComplianceHold', 'sourceOwnerModuleId String @map("source_owner_module_id")\nsourceTargetKind String @map("source_target_kind")\nsourceTargetId String @map("source_target_id")\nsourceCauseRef String @map("source_cause_ref")\nsourceGeneration BigInt @map("source_generation")\nreleaseCycle BigInt @default(0) @map("release_cycle")\nsemanticCauseKey String @unique @map("semantic_cause_key")', 'R059/R075: independent source cause and generation; release cannot waive another cause')

    additions = json.loads((REC / 'database-candidate-additions.json').read_text())
    for name, values in additions['enums'].items():
        schema = 'platform' if name.startswith('Runtime') else 'app'
        enums[name] = '\n' + '\n'.join('  ' + x for x in values) + '\n  @@map("' + map_name(name) + '")\n  @@schema("' + schema + '")\n'
    for item in additions['models']:
        n = item['model']; assert n not in models
        body = '\n' + '\n'.join('  ' + l for l in item['fields']) + '\n'
        body += '\n'.join('  ' + a for a in item.get('attributes', [])) + '\n'
        body += '  @@map("' + item.get('table', map_name(n)) + '")\n  @@schema("' + item.get('schema', 'app') + '")\n'
        models[n] = body; owners[n] = item['owner']; PURPOSE[n] = item['purpose']; changes[n] = [item['decision']]
    for item in additions['models']:
        n = item['model']
        for fk in item.get('foreign_keys', []):
            field, target, local, remote = fk
            relation = 'C_' + n + '_' + field
            body_line = field + ' ' + target + ' @relation("' + relation + '", fields: [' + local + '], references: [' + remote + '], onDelete: Restrict, onUpdate: Restrict)'
            models[n] = add(models[n], body_line)
            target_name = target.rstrip('?')
            models[target_name] = add(models[target_name], 'candidate' + n + field.title() + ' ' + n + '[] @relation("' + relation + '")')

    # Add typed foreign references to existing source/evidence rows.
    links = additions['existing_links']
    for n, f, target, required in links:
        field_type = 'String' if required else 'String?'
        models[n] = add(models[n], f + ' ' + field_type + ' @map("' + map_name(f) + '") @db.Uuid')
        relation = 'C_' + n + '_' + f
        rel_field = 'candidate' + f[0].upper() + f[1:]
        models[n] = add(models[n], rel_field + ' ' + target + ('' if required else '?') + ' @relation("' + relation + '", fields: [' + f + '], references: [id], onDelete: Restrict, onUpdate: Restrict)')
        models[target] = add(models[target], 'candidate' + n + f.title() + ' ' + n + '[] @relation("' + relation + '")')
        changes[n].append('DB-C16: typed ' + f + ' binding to canonical ' + target)

    # B010-02: native user/content/presentation coherence; SQL-05 additionally
    # compares action/context and the acknowledged rendered hash, null-safely.
    set_field('ConsentLog', 'candidatePresentationId', 'candidatePresentationId ConsentPresentation @relation("C_ConsentLog_presentationId", fields: [presentationId, contentRevisionId, userId], references: [id, contentRevisionId, userId], onDelete: Restrict, onUpdate: Restrict)', 'B010-02: composite FK prevents cross-user or cross-content presentation acceptance')

    # PostgreSQL supplies the transaction identity. SQL triggers reject spoofing and
    # require source/evidence/outbox records from the same transaction where needed.
    for n in models:
        models[n] = add(models[n], 'mutationTransactionId String @default(dbgenerated("pg_current_xact_id()::text")) @map("mutation_transaction_id")')
        changes[n].append('SQL-08: server transaction identity for atomic source/evidence/message checks')

    # Review schema is full staged target; initial foundation cut is its parent-FK closure.
    foundation = set(additions['foundation_roots'])
    while True:
        expanded = foundation | {f['type'].rstrip('?[]') for n in foundation for f in fields(models[n]) if 'fields:' in f['attributes'] and '@relation' in f['attributes']}
        if expanded == foundation:
            break
        foundation = expanded
    assert foundation <= set(models)

    header = '// REVIEW ONLY — P0-C-01. NOT ADOPTED. NO SQL OR DATABASE EXECUTION AUTHORIZED.\n'
    header += 'datasource db {\n  provider = "postgresql"\n  schemas = ["app", "platform"]\n}\n\n'
    header += '// No client generator: this representation must not replace the live application client.\n\n'

    def render(selected, foundation_only=False):
        text = header
        used_enums = {f['type'].rstrip('?[]') for n in selected for f in fields(models[n]) if f['type'].rstrip('?[]') in enums}
        for n, body in enums.items():
            if foundation_only and n not in used_enums:
                continue
            text += 'enum ' + n + ' {' + body + '}\n\n'
        for n in models:
            if n not in selected:
                continue
            body = models[n]
            if foundation_only:
                kept = []
                for l in body.splitlines():
                    m = FIELD.match(l)
                    if m and m[2].rstrip('?[]') in models and m[2].rstrip('?[]') not in selected:
                        assert 'fields:' not in l, (n, l)
                        continue
                    kept.append(l)
                body = '\n'.join(kept) + '\n'
            text += '// Source owner: ' + owners[n] + '. ' + PURPOSE[n] + '\nmodel ' + n + ' {' + body + '}\n\n'
        return '\n'.join(line.rstrip() for line in text.splitlines()).rstrip() + '\n'

    full = render(set(models)); cut = render(foundation, True)
    (OUT / 'physical-candidate.prisma').write_text(full, encoding='utf-8', newline='\n')
    (OUT / 'foundation-candidate.prisma').write_text(cut, encoding='utf-8', newline='\n')

    contracts = json.loads((ROOT / 'context/shared/contracts/contract-catalog.json').read_text())['contracts']
    refs = {}
    for contract in contracts:
        for owner in contract['source_truth']['owners']:
            refs.setdefault(owner, set()).update(contract['owner_architecture_refs'])
    extra_by_name = {x['model']: x for x in additions['models']}
    deferred = {n for n in models if owners[n] == 'sweepstakes_prize'} | {'ChildDirectedContentDeclaration', 'MinorPrivacyControl'}
    projections = {'FuzzyLocationCache', 'CandidateSearchProjection', 'TrackUsageCounter', 'LeaderboardEntry', 'SearchUpsertEvent', 'PrizeTaxYearSummary', 'BookingOrchestrationRun', 'BookingOrchestrationStep', 'TrustBadge'}
    rows = []
    for n, body in models.items():
        fs = fields(body)
        exact_refs = sorted(refs.get(owners[n], set())) or ['context/architecture.md']
        scalar = [f for f in fs if f['type'].rstrip('?[]') not in models]
        fks = [f for f in fs if '@relation' in f['attributes'] and 'fields:' in f['attributes']]
        evidence = n.endswith(('Event', 'Log', 'LedgerEntry', 'Snapshot', 'Receipt')) or n in {'AgeGateAttempt', 'AgeGateBlock', 'ConsentLog', 'ConsentContentRevision', 'ConsentPresentation', 'ConsentDisposition', 'OwnerMutationEvidence', 'AgreementExecutionRevision', 'PrivacyTargetInstruction', 'MediaObjectVersion', 'OrderPurchaseRevision', 'OrderPurchasedUnit', 'PrizePopulationMember', 'CheckoutTaxLocationEvidence'}
        classification = 'PROJECTION_NOT_AUTHORITY' if n in projections else 'SHARED_INFRASTRUCTURE' if owners[n] == 'platform_integration_owner' else 'IMMUTABLE_EVIDENCE_OR_RECEIPT' if evidence else 'AUTHORITATIVE_OWNER_STATE'
        stage = 'F0_FOUNDATION' if n in foundation else 'LATER_LAUNCH_DISABLED' if n in deferred else 'LATER_OWNER_ORDERED_SLICE'
        sensitive = [f['name'] for f in scalar if re.search(r'user|profile|email|phone|address|location|lat|lng|resume|text|body|token|secret|credential|signature|document|tax|ipHash|device|endpoint|payload', f['name'], re.I)]
        row = {'model': n, 'existing_model': n in original, 'source_owner': owners[n], 'purpose': PURPOSE[n], 'classification': classification, 'stage': stage,
               'candidate_fields': fs, 'identifiers_and_indexes': [l.strip() for l in body.splitlines() if l.strip().startswith(('@@id', '@@unique', '@@index'))] + [f['name'] for f in scalar if '@id' in f['attributes'] or '@unique' in f['attributes']],
               'foreign_relationships': fks, 'deletion': 'RESTRICT all FK key changes/deletes; owner Privacy executor must explicitly erase/anonymize dependents only under reviewed field/action/legal disposition; no legal period inferred',
               'concurrency_currentness': [f['name'] for f in scalar if re.search(r'revision|generation|fence|semantic|fingerprint|effect|lease|command', f['name'], re.I)],
               'history_and_proof': 'Immutable owner action evidence/receipt plus source revision and required outbox in one transaction; later owner writes remain gated until their registered action/evidence schema is qualified',
               'sensitive_fields': sensitive, 'access': 'NO browser/Data API grants; only registered owner action under transaction-bound context, current source authorization and explicit row/field policies',
               'privacy_executor': owners[n] if owners[n] != 'platform_integration_owner' else 'platform executor for minimized infrastructure metadata; original owner retains domain payload disposition',
               'json_fields': [{'field': f['name'], 'rule': 'Closed registered schema/version/hash required; not authorization, lifecycle, idempotency or financial truth; inactive before owning stage serializer qualification', 'contract_candidates': [c['id'] for c in contracts if n in c.get('source_models', [])]} for f in scalar if f['type'].rstrip('?') == 'Json'],
               'disposition': 'RETAIN_RECONCILED_REVIEW_ONLY' if n in original else 'ADD_FOR_APPROVED_ARCHITECTURE_REVIEW_ONLY', 'changes': changes[n], 'authority': exact_refs,
               'rulings': extra_by_name[n]['rulings'] if n in extra_by_name else ['WA-R018', 'WA-R031', 'WA-R069', 'WA-R076', 'WA-R086'],
               'sql_companion': ['SQL-01', 'SQL-02', 'SQL-03', 'SQL-04'] + extra_by_name.get(n, {}).get('sql_requirements', [])}
        row['candidate_table'] = re.search(r'@@schema\("([^"]+)"\)', body)[1] + '.' + re.search(r'@@map\("([^"]+)"\)', body)[1]
        owner_requirements = {
            'consent_disclosure':['SQL-05'], 'platform_integration_owner':['SQL-06','SQL-07','SQL-09'],
            'transaction_order':['SQL-10','SQL-11','SQL-13'], 'payment_payout_tax':['SQL-07','SQL-11'],
            'track_subscription_entitlement':['SQL-07','SQL-12'], 'privacy_data_erasure':['SQL-14'],
            'booking_calendar':['SQL-13'], 'video_session':['SQL-13','SQL-15'], 'job_interview':['SQL-13','SQL-18'],
            'media_file_access':['SQL-15'], 'digital_goods_access':['SQL-05','SQL-15'],
            'organization_hiring':['SQL-18'], 'candidate_application_resume_privacy':['SQL-18'],
            'job_compliance':['SQL-18'], 'review_dispute':['SQL-18'], 'observability_ops':['SQL-17']}
        row['sql_companion'] = sorted(set(row['sql_companion'] + ['SQL-08','SQL-16'] + owner_requirements.get(owners[n], [])))
        if n in original:
            row['source_body_sha256'] = sha(original[n]['body'].encode())
            row['source_fields'] = fields(original[n]['body'])
            candidate_fields = {f['name']: f for f in fs}
            compatibility = {'ProfessionalProfile': ['ratingAverage','ratingCount','stripeAccountId','stripeReady','trustScore','verifiedAt','verificationExpiresAt'], 'CandidateProfile':['trustScore','verifiedAt','verificationExpiresAt'], 'Job':['complianceStatus'], 'Agreement':['buyerSignedAt','professionalSignedAt','finalHashAlgorithm'], 'Booking':['externalCalendarEventId','externalCalendarProvider','externalSyncStatus','externalSyncError','providerEventId','providerCalendarId','providerEventVersion'], 'JobInterview':['externalCalendarEventId','externalCalendarProvider','externalSyncStatus','externalSyncError'], 'Organization':['ownerUserId'], 'SearchUpsertEvent':['processed','processedAt'], 'TrackUsageCounter':['usedQuantity']}
            row['field_dispositions'] = [{'field': f['name'], 'disposition': 'REMOVE_FROM_FRESH_CANDIDATE_OLD_TARGET_UNCHANGED' if f['name'] not in candidate_fields else 'KEEP_NONAUTHORIZING_DERIVED_COMPATIBILITY' if f['name'] in compatibility.get(n,[]) else 'RECONCILE_PHYSICAL_TYPE_OR_CONSTRAINT' if f != candidate_fields[f['name']] else 'KEEP_OWNER_MEANING_WITH_STAGE_GATES', 'candidate': candidate_fields.get(f['name']), 'basis': changes[n] or ['Existing canonical owner shape retained; see per-object SQL/access requirements']} for f in row['source_fields']]
        rows.append(row)

    inventory['physical_candidate_review'] = {'directive': 'P0-C-01', 'status': 'REVIEW_ONLY_NOT_ADOPTED', 'source_schema_sha256': sha(source.encode()), 'full_schema': 'prisma/review/physical-candidate.prisma', 'full_schema_sha256': sha(full.encode()), 'foundation_schema': 'prisma/review/foundation-candidate.prisma', 'foundation_schema_sha256': sha(cut.encode()),
        'existing_models_reviewed': len([v for v in original.values() if v['kind'] == 'model']), 'existing_model_count': len([v for v in original.values() if v['kind'] == 'model']),
        'candidate_model_count': len(models), 'foundation_model_count': len(foundation), 'rows': rows,
        'compatibility_cases': additions['compatibility_cases'], 'architecture_only_cases': additions['architecture_only_cases'],
        'adopted': False, 'ddl_generated': False, 'database_contacted_by_review': False}
    # The pre-existing architectural inventory and its 12 compatibility rows stay unchanged.
    inventory['physical_candidate_review']['existing_models_reviewed'] = len([v for v in original.values() if v['kind'] == 'model'])
    inventory_path.write_text(json.dumps(inventory, indent=2) + '\n', encoding='utf-8', newline='\n')
    print(json.dumps({'existing_models': 177, 'candidate_models': len(models), 'foundation_models': len(foundation), 'enums': len(enums), 'scope': 'source generation only; no DDL, database or adoption'}, indent=2))


if __name__ == '__main__':
    build()
