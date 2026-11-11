"""Pure source-review rules for P0-C-02. No SQL, connection or runtime adapter."""

BINDING_PROTOCOL = {
    'strategy': 'ISSUER_COMMITS_IMMUTABLE_TRANSACTION_TUPLE',
    'isolation': 'READ_COMMITTED_ONLY',
    'capture': ['session_user', 'pg_backend_pid()', 'pg_current_xact_id()::text'],
    'capture_before': 'ANY_BUSINESS_READ_OR_SOURCE_LOCK',
    'issuer_commit': 'SEPARATE_CREDENTIAL_AND_SEPARATE_TRANSACTION_BEFORE_BIND',
    'immutable_fields': ['databaseLoginRole', 'backendPid', 'transactionId'],
    'helper_grant_writes': [],
    'rollback_rule': 'OLD_GRANT_REMAINS_BOUND_TO_OLD_XID_AFTER_FULL_OR_SAVEPOINT_ROLLBACK',
    'retry': 'NEW_AUTHORIZATION_AND_NEW_GRANT_SAME_SEMANTIC_COMMAND_KEY',
    'not_implemented': True,
}

SQL02 = (
    'A custom actor-ID GUC is never authority. A 256-bit secret handle hashes to an '
    'issuer-written DatabaseActionGrant. Open a READ COMMITTED interactive transaction '
    'on one physical runtime/worker connection; before any business read or source lock, '
    'capture session_user, pg_backend_pid() and pg_current_xact_id()::text through the '
    'trusted server bridge, never client input. The separately credentialed issuer '
    'rechecks SH-001/SH-002/source-owner action, target, field and currentness authorization '
    'and commits a grant with that NONNULL immutable login/PID/xid8 tuple in its own '
    'separate transaction. Only after that issuer COMMIT may the source transaction bind '
    'the handle. The helper is read-only on the grant table: compare the full tuple and '
    'purpose/action/owner/target, subject-or-service XOR, expiry/revocation and current '
    'security/source generations; reject NULL binding or non-READ-COMMITTED isolation. '
    'No bind-time grant UPDATE, consumption flag or autonomous transaction is assumed. '
    'Full ROLLBACK, rollback to a SAVEPOINT containing the bind, failed bind, and commit '
    'cannot undo the separately committed tuple. An old token therefore cannot authorize '
    'a later transaction, even on the same pooled backend; a new transaction requires '
    'fresh authorization and a new grant. Rebinding within the same live transaction '
    'is idempotent and does not widen scope. SET LOCAL carries only the opaque handle. '
    'Current source/Consent/entitlement/Hold/proof, RLS USING/WITH CHECK and column/field '
    'guards remain required. There is no issuer/provider/network call while source locks '
    'are held. Revocation is irreversible; currentness is rechecked at protected effects '
    'and commit under the source-specific locking protocol.'
)

SQL06 = (
    'platform_private.bind_request_context(secret text) returns a grant ID only after '
    'validating the issuer-committed immutable login/backend/xid tuple against session_user, '
    'pg_backend_pid() and pg_current_xact_id()::text in READ COMMITTED. It SELECTs only the '
    'bounded grant columns and minimal Identity generations, then sets transaction-local '
    'transport; it never INSERTs, UPDATEs or DELETEs a grant. '
    'platform_private.context_allows(owner,action,kind,id,purpose) returns only a Boolean '
    'after the same tuple/currentness checks. Both SECURITY DEFINER helpers pin '
    'search_path=pg_catalog and qualify every application name. Their NOLOGIN/NOBYPASSRLS '
    'owner wa_private_helper_owner has bounded SELECT only, no grant-table write. '
    'REVOKE PUBLIC execution; only named runtime/worker (later separately approved privacy) '
    'roles receive EXECUTE, never direct grant-table privileges. wa_context_issuer alone '
    'may INSERT an already authorized fully bound grant, SELECT its own issued rows and '
    'UPDATE revokedAt from NULL to a timestamp; it cannot change any issued scope/tuple '
    'or DELETE. Runtime/worker cannot SET ROLE issuer/helper/owner. Issuer credentials '
    'remain separate and outside source/logs. Issuance commits after tuple capture and '
    'before business reads/source locks; no second connection is used under those locks.'
)

SQL05 = (
    'ConsentPresentation is an immutable per-user, per-action presentation: required '
    'userId references User; actionOwner/action and contextOwner/contextKind/contextId '
    'describe the exact authorized presentation, not a reusable public template. '
    'ConsentLog (presentationId, contentRevisionId, userId) has a restrictive composite '
    'FK to ConsentPresentation (id, contentRevisionId, userId), backed by the corresponding '
    'unique key. SQL checks also require equal actionOwner, action, contextOwner and '
    'contextKind, and contextId IS NOT DISTINCT FROM the presentation contextId; NULL '
    'is only allowed for a registered global context, not a wildcard. '
    'ConsentLog.presentationHash equals ConsentPresentation.renderedHash. The owner '
    'verifies the actually rendered bytes/hash and exact contentRevisionId, type/version, '
    'applicability and accepting authenticated User; an FK or submitted hash alone does '
    'not prove display or acceptance. Unique (userId, acceptanceKey); the fingerprint '
    'covers exact presentation ID/hash/content/user/action/context. Identical replay '
    'returns the original proof; changed meaning conflicts and intentional reacceptance '
    'uses a new key. Effective intervals are coherent; activated content, presentations '
    'and acceptance proofs are immutable. Draft/test-only policy never activates in '
    'production. Decline/withdrawal appends ConsentDisposition linked to the same user '
    'and presentation (and exact prior proof where supplied); it never erases old proof. '
    'No new IP, device, email or other personal metadata is required by this correction.'
)

GRANT_ACCESS = {
    'wa_context_issuer': ['INSERT_AUTHORIZED_IMMUTABLY_BOUND_GRANT', 'SELECT_OWN_ISSUED_GRANT', 'UPDATE_REVOKED_AT_NULL_TO_TIMESTAMP_ONLY'],
    'wa_private_helper_owner': ['SELECT_BOUNDED_GRANT_COLUMNS_VIA_DEFINER_ONLY'],
    'wa_app_runtime': ['EXECUTE_BIND_REQUEST_CONTEXT', 'CONTEXT_ALLOWS_BOOLEAN_VIA_POLICY'],
    'wa_worker': ['EXECUTE_BIND_REQUEST_CONTEXT', 'CONTEXT_ALLOWS_BOOLEAN_VIA_POLICY'],
}
DIRECT_GRANT_DENIALS = {
    'wa_app_runtime': ['SELECT', 'INSERT', 'UPDATE', 'DELETE', 'SET_ROLE_ISSUER_HELPER_OWNER'],
    'wa_worker': ['SELECT', 'INSERT', 'UPDATE', 'DELETE', 'SET_ROLE_ISSUER_HELPER_OWNER'],
    'wa_private_helper_owner': ['INSERT', 'UPDATE', 'DELETE', 'LOGIN'],
    'wa_context_issuer': ['UPDATE_IMMUTABLE_SCOPE_OR_TUPLE', 'DELETE', 'SOURCE_BUSINESS_WRITE'],
    'anon': ['SELECT', 'INSERT', 'UPDATE', 'DELETE', 'EXECUTE_HELPERS'],
    'authenticated': ['SELECT', 'INSERT', 'UPDATE', 'DELETE', 'EXECUTE_HELPERS'],
    'service_role': ['SELECT', 'INSERT', 'UPDATE', 'DELETE', 'EXECUTE_HELPERS'],
}


# The Customer-only first slice of WA-R078 / Track section 10.6, not a
# permission factory for all Track owners, catalog administrators or metering.
DEFAULT_FREE_HANDLER = 'assignDefaultFreeTrack.v1'


def _track_operation(verb, columns, row_scope, **guards):
    return {
        'handler': DEFAULT_FREE_HANDLER,
        'stage': 'F0_FOUNDATION',
        'track': 'customer',
        'operation': verb,
        'columns': columns.split(),
        'row_scope': row_scope,
        'guards': {
            'current_authorization_and_transaction_tuple': True,
            'current_customer_owner_binding': True,
            'original_semantic_enrollment_identity': True,
            'current_worker_fence': True,
            'server_stamps_mutation_transaction_id': True,
            **guards,
        },
    }


DEFAULT_FREE_TRACK_OPERATIONS = {
    'TrackPlan': [
        _track_operation('SELECT', 'id track key status billingModel version contentHash revision',
                         'APPROVED_FREE_REVISION_OR_CURRENT_SELECTED_PLAN',
                         new_free_plan_must_be_approved_active=True,
                         catalog_retirement_does_not_invalidate_existing_selection=True),
    ],
    'TrackEntitlementDefinition': [
        _track_operation('SELECT', 'id key valueType track isActive revision',
                         'DEFINITIONS_REFERENCED_BY_APPROVED_FREE_PLAN',
                         definitions_must_be_active_and_customer_applicable=True),
    ],
    'TrackPlanEntitlement': [
        _track_operation('SELECT', 'id planId entitlementId valueType booleanValue intValue decimalValue stringValue usagePeriod revision',
                         'MAPPINGS_OF_APPROVED_FREE_PLAN_REVISION',
                         exact_typed_approved_benefits_only=True,
                         json_value_remains_null_in_f0=True),
    ],
    'TrackSubscription': [
        _track_operation('SELECT', 'id userId planId track customerProfileId candidateProfileId professionalProfileId status provider currentPeriodStart currentPeriodEnd endedAt revision',
                         'EXACT_USER_CUSTOMER_TRACK_SELECTED_OR_NEW_ENROLLMENT'),
        _track_operation('INSERT', 'id userId planId track customerProfileId candidateProfileId professionalProfileId status provider',
                         'NEW_FREE_ENROLLMENT_FOR_EXACT_CUSTOMER',
                         only_if_no_valid_current_free_or_paid_selection=True,
                         approved_free_plan_revision=True,
                         provider_none_and_no_billing_identifiers=True,
                         customer_profile_only_other_profile_ids_null=True,
                         atomic_receipt_history_and_effect=True,
                         existing_subscriptions_unchanged=True),
    ],
    'TrackEntitlementGrant': [
        _track_operation('SELECT', 'id userId subscriptionId entitlementId track customerProfileId candidateProfileId professionalProfileId status valueType booleanValue intValue decimalValue stringValue startsAt expiresAt revokedAt sourcePlanId sourceEventId revision',
                         'EXACT_USER_CUSTOMER_ENROLLMENT_SUBSCRIPTION_GRANTS'),
        _track_operation('INSERT', 'id userId subscriptionId entitlementId track customerProfileId candidateProfileId professionalProfileId status valueType booleanValue intValue decimalValue stringValue startsAt sourcePlanId sourceEventId',
                         'NEW_GRANTS_OF_SAME_NEW_FREE_ENROLLMENT',
                         exact_typed_approved_benefits_only=True,
                         same_new_subscription_created_in_transaction=True,
                         no_duplicate_or_rewritten_existing_grants=True,
                         customer_profile_only_other_profile_ids_null=True,
                         atomic_receipt_history_and_effect=True,
                         json_value_remains_null_in_f0=True),
    ],
    'TrackBaseSelection': [
        _track_operation('SELECT', 'id userId track customerProfileId candidateProfileId professionalProfileId subscriptionId revision sourceGeneration',
                         'EXACT_USER_CUSTOMER_TRACK_SELECTION'),
        _track_operation('INSERT', 'id userId track customerProfileId candidateProfileId professionalProfileId subscriptionId sourceGeneration',
                         'MISSING_SELECTION_FOR_SAME_NEW_FREE_ENROLLMENT',
                         serialized_user_track_and_missing_selection=True,
                         same_new_subscription_created_in_transaction=True,
                         customer_profile_only_other_profile_ids_null=True,
                         atomic_receipt_history_and_effect=True),
        _track_operation('UPDATE', 'subscriptionId revision sourceGeneration',
                         'INVALID_SELECTION_CAS_TO_SAME_NEW_FREE_ENROLLMENT',
                         only_if_no_valid_current_free_or_paid_selection=True,
                         same_new_subscription_created_in_transaction=True,
                         cas_expected_selection_revision=True,
                         revision_increments_exactly_once=True,
                         user_track_and_profile_binding_immutable=True,
                         atomic_receipt_history_and_effect=True),
    ],
    'TrackEnrollmentReceipt': [
        _track_operation('SELECT', 'id userId track profileId sourceOwner sourceCreationRevision selectionId selectionRevision semanticKey fingerprint resultCode effectReceiptId',
                         'EXACT_ORIGINAL_SOURCE_PROFILE_SEMANTIC_KEY'),
        _track_operation('INSERT', 'id userId track profileId sourceOwner sourceCreationRevision selectionId selectionRevision semanticKey fingerprint resultCode effectReceiptId',
                         'MISSING_RECEIPT_FOR_ORIGINAL_ENROLLMENT_COMMAND',
                         insert_only_if_original_semantic_receipt_absent=True,
                         identical_replay_read_only_changed_fingerprint_conflicts=True,
                         preserve_valid_existing_free_or_paid_selection=True,
                         atomic_receipt_history_and_effect=True),
    ],
    'TrackSubscriptionEvent': [
        _track_operation('INSERT', 'id subscriptionId planId userId name fromStatus toStatus provider',
                         'NEW_HISTORY_OF_SAME_NEW_FREE_ENROLLMENT',
                         actual_new_enrollment_only_no_replay_event=True,
                         same_new_subscription_created_in_transaction=True,
                         existing_immutable_history_unchanged=True,
                         atomic_receipt_history_and_effect=True),
    ],
    # Enrollment does not meter, reset, repair or even query usage. An approved
    # test observer separately verifies these rows remain unchanged.
    'TrackUsageEvent': [],
    'TrackUsageCounter': [],
    'TrackUsageReservation': [],
}


def default_free_operations(row):
    if row['stage'] != 'F0_FOUNDATION':
        return []
    return DEFAULT_FREE_TRACK_OPERATIONS.get(row['model'], [])


def default_free_denials(row):
    operations = default_free_operations(row)
    allowed = {op['operation'] for op in operations}
    return [verb for verb in ['SELECT', 'INSERT', 'UPDATE', 'DELETE'] if verb not in allowed]


def default_free_scope(row):
    return {
        'handler': DEFAULT_FREE_HANDLER,
        'stage': row['stage'],
        'track': 'customer',
        'catalog_preparation': 'SEPARATELY_AUTHORIZED_CATALOG_FIXTURE_STEP_NOT_ENROLLMENT_WORKER',
        'worker_may_prepare_catalog': False,
        'usage_observation': 'SEPARATE_AUTHORIZED_TEST_OBSERVER_NOT_ENROLLMENT_WORKER',
        'qualification': 'NOT_RUN',
        'authority': [
            'context/reconciliation/platform-architecture-rulings.md#wa-r078--default-free-enrollment-handoff-bf-035',
            'context/reconciliation/database-candidate-continuation.md',
            'context/clusters/identity, authority, & consent/Track Subscription & Entitlement Module/track-subscription-entitlement-module-architecture.md#106-assigndefaultfreetrack',
        ],
    }


def access_profile(row):
    """Explicit positive paths; these specify tests, not implemented privileges."""
    if row['model'] == 'DatabaseActionGrant':
        return {
            'operations_by_role': GRANT_ACCESS,
            'direct_denials_by_role': DIRECT_GRANT_DENIALS,
            'entry': 'ISSUER_OWN_ROW_POLICY_OR_NAMED_DEFINER_HELPER_ONLY',
        }
    immutable = row['classification'] == 'IMMUTABLE_EVIDENCE_OR_RECEIPT' or row['model'] in {
        'OwnerMutationEvidence', 'RuntimeEffectReceipt', 'RuntimeInboxReceipt',
        'RuntimeAttempt', 'RuntimeDeliveryAttempt',
    }
    runtime = ['SELECT_EXACT_AUTHORIZED_TARGET']
    worker = []
    if row['model'] not in {'CandidateProfile', 'ProfessionalProfile'} or row['stage'] != 'F0_FOUNDATION':
        runtime += ['INSERT_REGISTERED_OWNER_ACTION_WITH_ATOMIC_PROOF']
        if not immutable:
            runtime += ['UPDATE_REGISTERED_OWNER_FIELDS_WITH_CAS_AND_ATOMIC_PROOF']
    if row['source_owner'] == 'platform_integration_owner':
        worker = ['SELECT_REGISTERED_HANDLER_TARGET', 'INSERT_REGISTERED_HANDLER_EVIDENCE']
        if not immutable:
            worker += ['UPDATE_REGISTERED_HANDLER_FIELDS_WITH_CURRENT_LEASE_AND_FENCE']
    elif row['source_owner'] == 'track_subscription_entitlement':
        worker = default_free_operations(row)
    track_scope = row['source_owner'] == 'track_subscription_entitlement'
    helper = ['SELECT_SECURITY_GENERATION_COLUMNS_VIA_DEFINER_ONLY'] if row['model'] == 'UserSecurityProfile' else []
    profile = {
        'operations_by_role': {
            'wa_app_runtime': runtime,
            'wa_worker': worker,
            'wa_context_issuer': [],
            'wa_private_helper_owner': helper,
        },
        'direct_denials_by_role': {
            'anon': ['SELECT', 'INSERT', 'UPDATE', 'DELETE'],
            'authenticated': ['SELECT', 'INSERT', 'UPDATE', 'DELETE'],
            'service_role': ['SELECT', 'INSERT', 'UPDATE', 'DELETE'],
            'wa_context_issuer': ['SOURCE_BUSINESS_WRITE'],
        },
        'entry': 'NAMED_OWNER_ACTION_OR_REGISTERED_HANDLER_CURRENT_TARGET_FIELDS_AND_PROOF',
    }

    if track_scope:
        profile['worker_contract_scope'] = default_free_scope(row)
        profile['direct_denials_by_role']['wa_worker'] = default_free_denials(row)
    return profile


def operation_dispositions(row, profile):
    """Reviewed ACL ceilings are not proof of complete permitted operations."""
    model=row['model']
    privacy={'PrivacyTargetInstruction':'P0F_PRIVACY_INSTRUCTION_SCOPE_AND_FIELD_MAP',
             'PrivacyOwnerReceipt':'P0F_PRIVACY_OWNER_DISPOSITION_ACCOUNTING',
             'PrivacyRestoreMarker':'P0F_PRIVACY_RESTORE_GENERATION_PORT'}
    tracked=set(privacy)|{'PrivacyRequest','TrackUsageReservation','TrackUsageEvent','TrackUsageCounter','TrackSubscription','TrackEntitlementGrant','TrackBaseSelection','TrackSubscriptionEvent','TrackEnrollmentReceipt','RuntimeReservation','CustomerProfile'}
    if model not in tracked:return []
    results=[]
    for role,operations in profile['operations_by_role'].items():
        for op in operations:
            verb=op['operation'] if isinstance(op,dict) else op.split('_')[0]
            if verb not in ['SELECT','INSERT','UPDATE']:continue
            deps=[];reads=[]
            root=model;action='SH-003.v1';purpose='owner:queryOwnerFacts'
            if role=='wa_worker':
                root='RuntimeWorkItem';action='assignDefaultFreeTrack.v1';purpose='default_free_enrollment'
                reads=['Exact original Customer command/current source via bounded Boolean ports','Approved Free plan revision/version/content hash','Exact job/source row and verb/field/revision capabilities; current lease secret/fence']
                if model=='RuntimeReservation':deps=['NO_REGISTERED_WORKER_RESERVATION_ROUTE']
            else:
                if model in privacy:deps=[privacy[model]];reads=['Unregistered exact Privacy parent/generation/field-map/owner-disposition prerequisites']
                elif model=='TrackUsageReservation' or (model in ['TrackUsageEvent','TrackUsageCounter'] and verb!='SELECT'):deps=['P0D_TRACK_USAGE_PERIOD_RECONCILIATION'];reads=['Qualified UTC-period/reservation/reconciliation owner adapter; usage mutation currently raises 0A000']
                elif model in ['TrackSubscription','TrackEntitlementGrant'] and verb!='SELECT':deps=['P0E_TRACK_APP_PROFILE_AND_PLAN_FACT_PORT'];reads=['Typed Customer/Candidate/Professional user binding and exact Track plan/subscription: current root/owner scope does not authorize these prerequisite reads']
                elif model in ['TrackBaseSelection','TrackEnrollmentReceipt'] or (model=='TrackSubscriptionEvent' and verb!='SELECT'):deps=['F0_DEFAULT_FREE_WORKER_ONLY'];reads=['No application root path; history/receipt mutation explicitly requires wa_worker']
                if model=='RuntimeReservation':action='runtime.reservation.v1';purpose='reservation';reads=['Exact authorized command and terminal effect receipt; field effectReceiptId, immutable identity, fence and semantic key']
                if model=='CustomerProfile':action='SH-004.v1' if verb!='UPDATE' else 'updateCustomerProfileIdentity.v1';purpose='provision' if verb!='UPDATE' else 'profile_update';reads=['Required command/evidence/history/outbox SELECT and INSERT capabilities; root source verb remains separately bounded']
                if model=='PrivacyRequest' and verb!='SELECT':action='SH-049.v1';purpose='owner:orchestrateWorkflowSteps';reads=['Only open/noncompletion states; completed/partially_completed remains P0F_PRIVACY_OWNER_DISPOSITION_ACCOUNTING-gated']
                if deps and model in ['TrackUsageEvent','TrackUsageCounter'] and verb!='SELECT':action='SH-006.v1';purpose='owner:consumeMeteredEntitlement'
                if deps and model in ['TrackSubscription','TrackEntitlementGrant'] and verb!='SELECT':action='SH-053.v1';purpose='owner:transitionLifecycleState'
                if model=='TrackSubscriptionEvent' and verb!='SELECT':action='SH-053.v1';purpose='owner:transitionLifecycleState'
                if model in privacy or model in ['TrackUsageReservation','TrackBaseSelection','TrackEnrollmentReceipt']:
                    action='NO_REGISTERED_SCOPE';purpose='NO_REGISTERED_SCOPE'
            results.append({'role':role,'verb':verb,'source_owner':row['source_owner'],'action':action,'purpose':purpose,'root_kind':root,
                            'row_and_field_capabilities':'Exact model/id/verb/field tokens; no wildcard; prior revision and same-transaction successor convention where applicable',
                            'prerequisite_reads':reads,'atomic_proof':'Actual source/history/command/evidence/messages/terminal checks applicable to this operation; no standalone source write',
                            'source_admission':'DEPENDENCY_GATED' if deps else 'ATTAINABLE_WITH_SYNTHETIC_FIXTURE',
                            'dependency_ids':deps,'current_expected':'DENY_WHILE_DEPENDENCY_MISSING' if deps else 'ALLOW_ONLY_COMPLETE_PATH', 'status':'NOT_RUN'})
    if model=='PrivacyRequest':
        results.append({'role':'wa_app_runtime','verb':'UPDATE_COMPLETION_STATES','source_owner':row['source_owner'],'action':'SH-049.v1','purpose':'owner:orchestrateWorkflowSteps','root_kind':'PrivacyRequest','row_and_field_capabilities':'Exact request/generation/status caps','prerequisite_reads':['All qualified owner dispositions and complete accounting; source privacy_guard explicitly raises 0A000 until available'],'atomic_proof':'Actual completed/partially_completed accounting and exact source evidence','source_admission':'DEPENDENCY_GATED','dependency_ids':['P0F_PRIVACY_OWNER_DISPOSITION_ACCOUNTING'],'current_expected':'DENY_WHILE_DEPENDENCY_MISSING','status':'NOT_RUN'})
    return results


def table_cases(row, primary_key):
    profile = access_profile(row)
    setup = {
        'table': row['candidate_table'], 'owner': row['source_owner'], 'pk': primary_key,
        'operations_by_role': profile['operations_by_role'],
        'foreign_prerequisites': [f['attributes'] for f in row['foreign_relationships']],
        'context': 'Exact immutable issuer-bound transaction tuple, target/action/fields and current generations; no caller-supplied authority',
    }
    if 'worker_contract_scope' in profile:
        setup['worker_contract_scope'] = profile['worker_contract_scope']
    dispositions=operation_dispositions(row,profile)
    if dispositions:setup['operation_dispositions']=dispositions
    if row['model'] == 'DatabaseActionGrant':
        positive = ('Issuer login INSERTs a fully authorized immutable tuple grant, SELECTs its own row and exercises only one-way revocation. '
                    'Separate runtime and worker logins EXECUTE bind_request_context with their own issued tuples; '
                    'the NOLOGIN helper owner reads bounded columns only through the DEFINER call and returns an ID/Boolean. '
                    'Runtime and worker perform no direct grant-table SELECT or write. Use distinct fresh grants for revoked and live cases.')
        expected = 'Issuer-only issuance/revocation and both named helper paths succeed; no grant row/body is exposed to runtime/worker'
    else:
        positive = ('Run each exact nonempty operations_by_role path with its listed actual login and scoped synthetic context. '
                    'The helper owner is tested only through a named DEFINER call, never LOGIN/SET ROLE. '
                    'No operation is inferred for an empty role list. Immutable evidence admits append/select only; '
                    'FK-only Candidate/Professional prerequisites in F0 prove permitted SELECT without future feature mutations. '
                    'Registered source changes commit their required history/receipt/outbox; worker changes require the current fence.')
        expected = 'Each listed permitted row/effect succeeds only for its target/fields and stage, with all required atomic evidence'
        if dispositions:
            positive='Execute only ATTAINABLE_WITH_SYNTHETIC_FIXTURE operations with the complete listed login/scope/capability/prerequisite/proof path. ACL ceilings in operations_by_role are preserved. Separately exercise DEPENDENCY_GATED operations as expected denials; their future positive is not claimed attainable.'
            expected='Complete attainable paths commit; named gated paths deny. Privacy completion and usage mutation remain denied. All database/runtime statuses remain NOT_RUN.'
    negative = {
        'table': row['candidate_table'],
        'direct_denials_by_role': profile['direct_denials_by_role'],
        'additional_denials': ['FOREIGN_RUNTIME_CONTEXT', 'UNREGISTERED_WORKER_ACTION', 'MISSING_OR_STALE_TUPLE_OR_GENERATION', 'OWNERSHIP_OR_IMMUTABLE_FIELD_REASSIGNMENT'],
        'fixture': 'Same synthetic concrete rows as the positive case',
    }
    return setup, positive, expected, negative

# Brain P0-C-03A source-only amendments; no SQL is executed by these rules.
SQL02 += ' Current service authority is a private Identity-owned generation/revocation record bound to an immutable Identity receipt. Issuer cannot write or manufacture that source; absent/revoked/stale source denies. Actual action/purpose/root is enforced through protected_scope and context_allows, not just field tokens.'
SQL06 += ' Fixed Customer/Track Boolean ports use distinct NOLOGIN read-only roles and the exact columns in foundation-sql-verifier-access.json; direct worker grants remain unchanged. The private helper reads only current service generation/revocation in addition to its original Identity/grant leaves.'

# New vectors extend existing test IDs. They are specifications, never executions.
# Each pair requires a successful operation as well as a meaningful denial.
P0C03A_REPLAY_VECTORS = {
 'P0C-TABLE-ConsentLog-ALLOW': [
  ('CONSENT-SCOPE-CHAIN', 'SH-007 proof root reads its exact presentation/content using relationship and per-row/field capabilities, then appends coherent proof/evidence', 'Substitute an otherwise row-authorized foreign presentation/content, wrong root/purpose, or omit root-to-child capability', 'Only the exact subject/action/context/rendering chain is admitted; missing or foreign prerequisite scope denies')],
 'P0C-TABLE-ConsentLog-DENY': [
  ('CONSENT-SCOPE-DENY', 'Same exact prerequisite graph as authorized acceptance', 'Use SH-007 to INSERT a prerequisite or change purpose/root while preserving ordinary row/field caps', 'Prerequisite reads are SELECT-only and tied to the exact proof root; no acceptance grant creates its own presentation')],
 'P0C-TABLE-ConsentContentRevision-ALLOW': [
  ('CONSENT-CONTENT-SCOPE', 'Separately authorized publishConsentVersion.v1 / consent.publish_version appends one exact immutable root with required proof; SH-009 reads an exact revision', 'Use a query purpose to INSERT or supply a foreign content root', 'Named publisher admission succeeds; query write and foreign root deny; actual publisher/legal policy remains owner-adapter work')],
 'P0C-TABLE-ConsentPresentation-ALLOW': [
  ('CONSENT-PRESENTATION-SCOPE', 'recordConsentPresentation.v1 / consent.record_presentation appends current principal presentation and reads exact related content', 'Foreign principal/content or SH-010 presentation purpose attempts INSERT', 'Only the named append operation with exact subject/content admits the row; SH-010 remains SELECT-only')],
 'P0C-TABLE-ConsentDisposition-ALLOW': [
  ('CONSENT-DISPOSITION-SCOPE', 'recordConsentDisposition.v1 / consent.record_disposition appends exact same-subject presentation/proof disposition', 'Foreign proof/presentation, wrong purpose/root, missing relationship capability or UPDATE existing disposition', 'Exact immutable disposition appends; every foreign binding/rewrite denies')],
 'P0C-INSTALL-01': [
  ('INSTALL-CLEANUP', 'Bootstrap/application succeeds, then ORIGINAL grantor runs finalize in a separate connection', 'Inject application rollback, then the same grantor finalizes; wrong grantor cannot clean up', 'Both outcomes leave zero helper/verifier memberships on schema owner and zero CREATE on platform_private for leaf roles; runtime credentials stay inactive until verified')],
 'P0C-CATALOG-01': [
  ('CATALOG-LEAVES', 'Compare all 40 model tables plus two private Identity relations and exact column ACLs', 'Attempt issuer/current-source DML and verifier business DML or role assumption', 'Exact catalog/ACL/owner parity; no issuer self-attestation or verifier writes')],
 'P0C-CTX-01': [
  ('READ-PURPOSE-NO-WRITE', 'Canonical query/pure/result/presentation and projection/history/access-evidence source scopes admit only SELECT', 'Give SH-003 or another nonmutating purpose otherwise matching root UPDATE capabilities', 'Source writes deny; any independent append-only read proof needs an explicitly registered owner operation'),
  ('SERVICE-BOOTSTRAP', 'Identity writer commits bootstrap receipt and generation zero, then issuer binds a current service grant', 'Issuer/app/worker tries to manufacture service currentness, wrong tuple, or stale generation', 'Only independent Identity currentness authorizes service; issuer cannot write its own current source'),
  ('SCOPE-PURPOSE', 'Exact Customer action/purpose/root and otherwise valid row/field caps', 'Keep the same row/fields while substituting purpose, action or root', 'Protected operation succeeds only for its registered scope'),
  ('POOL-LIFETIME', 'New READ COMMITTED transaction on the same backend obtains a fresh separately committed grant', 'Reuse old handle after full/savepoint rollback or commit; use another backend or xid', 'Current tuple succeeds; all stale or foreign tuples deny')],
 'P0C-CTX-02': [
  ('SERVICE-REVOKE', 'Rotate/revoke/recover under separate Identity credentials and exact predecessor receipt', 'A binds; independent Identity writer commits revoke/rotate before A attempts action', 'Fresh current generation succeeds; old generation is denied; recovery needs new Identity receipt, never issuer assertion')],
 'P0C-PRIV-01': [
  ('BOOLEAN-PORTS', 'Worker calls fixed Boolean ports for its current source/job/approved plan/lease', 'Wrong customer, job, source receipt, plan revision or lease; attempt source-body SELECT via port', 'Only matching fixed facts return true; no source bodies, DML or broadened worker direct grant')],
 'P0C-BOOT-01': [
  ('FIRST-CUSTOMER', 'Trusted synthetic Identity/Consent/catalog setup; create Customer rev0/no predecessor, commit, then fresh scoped grant updates rev1 with exact predecessor0', 'Require predecessor on creation, supply predecessor on create, omit required history/proof, or use a stale predecessor on update', 'Valid create then update commits; invalid predecessor or absent grouped proof rolls back without recursive evidence-about-evidence')],
 'P0C-ATOMIC-01': [
  ('MESSAGE-REVERSE', 'Creation emits exactly event ordinal0 and Free command ordinal1, each linked to exact source/history/evidence/command', 'Beside a valid update event, emit an extra Free-enrollment command; substitute another source history or user', 'Exact creation/update message set commits; every extra or mismatched message rejects COMMIT'),
  ('RESULT-VERSION', 'Registered result schema version1 and closed payload', 'Same otherwise-valid result with another version', 'Only registered version is accepted')],
 'P0C-CAS-01': [
  ('OWNER-REVISIONS', 'TrackUsageReservation and PrivacyRestoreMarker update with exact OLD revision, +1 and closed prior/committed evidence', 'Stale predecessor, skipped revision, absent prior object or same-transaction second source update', 'One source revision/proof advances; stale/skipped/missing proof fails; later unqualified usage mutation remains blocked')],
 'P0C-IMMUTABLE-01': [
  ('AGE-APPEND', 'Append independently authorized AgeGateAttempt/Block with new semantic ID', 'UPDATE/DELETE old age evidence, including an attempted block extension in place', 'Append succeeds; retained age evidence cannot be rewritten'),
  ('CONSENT-EMPTY', 'Matching nonempty context; separately reviewed registry fixture may authorize one exact global tuple', 'NULL/empty context without exact registered global tuple, wrong action or context kind', 'Current production registry is empty and denies every empty context; equality alone conveys no global authority')],
 'P0C-TRACK-01': [
  ('LEASE-ATTACH', 'Current holder supplies 256-bit lease preimage; committed matching command/effect/inbox links null to exact effect once and completes in same transaction', 'Copy readable stored hash as secret, attach unrelated effect with identical fence, relink nonnull pointer, or use another job/customer/plan revision', 'Exact holder/link succeeds; copied hash or foreign/relinked evidence denies'),
  ('LEASE-RENEW', 'Fresh renew grant extends an unexpired same-fence lease with unchanged secret hash and attempt count', 'Renew after expiry, shorten expiry, change hash without reclaim, or let old holder act after concurrent higher-fence reclaim', 'Only current holder renews; reclaim increments fence/attempt once with future expiry; attempt-only changes deny; stale holder cannot commit'),
  ('LEASE-RECOVERY', 'Reclaimed current holder recognizes original exact already-committed effect/inbox and completes without another business mutation', 'Recognize same-fence receipt from a different semantic key/operation/customer or missing exact inbox', 'SELECT admits only the exact linked original committed outcome after reclaim; new effect INSERT requires current fence; foreign receipt cannot acknowledge work')],
 'P0C-TABLE-RuntimeReservation-ALLOW': [
  ('RESERVATION-RELEASE', 'Exact reservation/owner/command/operation/fingerprint/semantic key/fence has durable fenced_noncommit proof; attach that receipt once and release', 'Use receipt from another reservation/operation, NULL or foreign command, unresolved command, or elapsed lease alone', 'Exact proof releases; all foreign/unknown/time-only claims deny')],
 'P0C-TABLE-RuntimeReservation-DENY': [
  ('RESERVATION-BYPASS', 'active to unknown retains uncertain reservation; exact proof may release unknown', 'Try unknown to active to released, initial terminal state, unknown quantity reduction, terminal reversal, or later committed effect after noncommit', 'Unknown never returns to active; terminal command/effect/links cannot be reinterpreted')],
 'P0C-EVIDENCE-01': [
  ('WORKER-REVERSE-PROOF', 'Worker commits exact source snapshot/revision/transaction through fixed read-only Boolean port; base selection UPDATE has full verifier identity without wider direct grants', 'Wrong source/transaction/revision/snapshot or omitted UPDATE identity; keep direct worker source columns unchanged', 'Exact proof and legitimate base-selection update pass; all invented proof denies'),
  ('EVIDENCE-CODEC', 'Creation has JSON null prior and revision0; update exact prior object; Int JSON numbers and BigInt strings', 'Wrong predecessor/source/transaction, missing prior object, extra body keys or wrong numeric encoding', 'Closed minimized source/evidence agrees in both schemas and actual SQL snapshot expression')],
 'P0C-RESTORE-01': [
  ('SERVICE-RESTORE', 'Before any restored service connection, Identity independently revokes/advances every restored service epoch, rotates credentials and issues recovery receipt', 'Reuse a restored pre-crash service grant/generation or omit privacy restriction markers', 'Restored state remains unavailable until independent currentness/marker recovery; old grants fail')],
}

# Follow-up of published e363ad4. Nested vectors preserve all 451 register IDs
# and the original 94 selections. Every behavioral case remains NOT_RUN.
for test_id, vectors in {
 'P0C-INSTALL-01':[('FUNCTION-ACL-AUTHORITY','Install as actual wa_migrator, SET LOCAL ROLE wa_schema_owner; exact function grants and managed-role revocations precede every transfer to NOINHERIT leaf owners','Move a grant/revocation after transfer without SET ROLE actual owner','Install commits with expected ACL; original grantor then removes every temporary membership and CREATE privilege')],
 'P0C-INSTALL-02':[('FUNCTION-ACL-FAILURE-CLEANUP','Original grantor finalizes after application ROLLBACK as well as COMMIT','Inject a failure after function setup but before application COMMIT; attempt runtime activation before independent cleanup verification','No application objects survive failed application transaction; zero temporary memberships/leaf CREATE after separate finalization')],
 'P0C-TRACK-01':[('DIRECT-TRACK-SNAPSHOT','Actual wa_worker directly calls every exposed Boolean branch with complete actual same-job/current-xid source snapshot, approved plan/version/hash and exact capabilities; repeat through intended source transaction','Complete foreign Customer; another ungranted source under same job; wrong job, plan/version/hash, xid, predecessor or required field/revision capability','Only complete same-job source returns true and legitimate transaction commits; direct and intended operations deny all substitutions')],
 'P0C-PRIV-01':[('DIRECT-PORT-CAPS','Invoke relationship, effect, atomic and reverse ports under the exact authorized job/source/field capabilities','Remove one required capability or change current Customer generation while keeping a valid job and complete foreign snapshots','No direct verifier oracle bypasses the intended policy path; internal actual-row ports cannot be directly executed by worker')],
 'P0C-TABLE-RuntimeReservation-ALLOW':[('RESERVATION-ROLE-REACHABILITY','Actual wa_app_runtime creates active reservation with null effect; with fresh exact reservation scope attaches committed receipt and commits; separately active -> unknown -> released with current durable fenced_noncommit proof','Use foreign receipt/reservation, different command/operation/semantic identity, replace existing link or try unknown -> active -> released','Actual UPDATE(effect_receipt_id) grant plus SELECT/RLS/field/revision/fence/exact-proof guards admit legitimate terminals; worker direct ACL stays unchanged and its reservation route remains denied')],
 'P0C-BOOT-01':[('FIRST-SMALL-REHEARSAL','Run only the separately approved small rehearsal below before expanding the 94 selected cases','Wrong-person Customer creation and missing-outbox COMMIT failure','Install/cleanup and one complete Customer transaction succeed; denial and rollback leave no partial business group')]
}.items():P0C03A_REPLAY_VECTORS.setdefault(test_id,[]).extend(vectors)

FIRST_REHEARSAL={
 'status':'PROPOSED_NOT_RUN_EXECUTION_HELD','reviewed_source':'e363ad45dfad76d2a4ffbd0cd84ef0c01d24e966',
 'environment':'Windows-connected session; Docker desktop-linux local named-pipe context. Read-only discovery 2026-11-10: CLI 29.6.2 present; daemon pipe absent, server/version/local image inventory unavailable. Do not start it during this source pass.',
 'image':{'reference':'docker.io/library/postgres:17.11@sha256:996e9dc583ba9f0265a2c75547a9c95fb22c251e394749cab205a0a00e1856a1','platform':'linux/amd64','version':'17.11','digest_kind':'PLATFORM_MANIFEST','config_digest':'sha256:eb0fb2377534e65aad04f37838956b3dfb888e1a3dd3c1acf957bc6557eb6c7d','read_only_verification':'docker manifest inspect --verbose docker.io/library/postgres:17.11; selected descriptor linux/amd64; OCI version17.11','official_source':'https://github.com/docker-library/postgres/tree/2603e26e245e558218728ee14e0a42dcb020dc7f/17/trixie','layers_pulled':False},
 'resources':{'success_container':'wa-p0c-first-20261110-ok','failure_container':'wa-p0c-first-20261110-fail','success_volume':'wa-p0c-first-20261110-ok-data','failure_volume':'wa-p0c-first-20261110-fail-data','database':'wa_p0c_rehearsal','label':'workinants.rehearsal=p0c-first-20261110','network':'--network none; no published host ports; docker exec psql uses container loopback TCP for actual restricted authentication','storage':'Only separately named disposable volumes at /var/lib/postgresql/data; no user/repository/hosted data mounts'},
 'credentials':'After execution approval generate independent cryptographically random bootstrap/migrator/issuer/Identity/app/worker passwords and context/lease secrets in memory. Owner-only temporary files outside Git; bootstrap POSTGRES_PASSWORD_FILE read-only mount; psql PGPASSFILE inside tmpfs /run/wa-secrets chmod0600. Never put plaintext in argv, SQL/source/reports, Docker environment values or transcripts. Set role passwords via controlled stdin with statement logging disabled. Remove exact test secret paths after cleanup.',
 'connections':['bootstrap postgres via separate privileged setup session','wa_migrator actual TCP login; application SQL performs SET LOCAL ROLE wa_schema_owner','wa_context_issuer actual separate TCP login/transaction before business locks','wa_identity_service_authority actual separate TCP login, prepared but not needed for the human Customer test','wa_app_runtime actual TCP login with human principal A/B','wa_worker actual separate TCP login, negative membership/privilege probes only in this first rehearsal; no worker loop'],
 'steps':[
  {'id':'FIRST-01','status':'NOT_RUN','action':'After separate Brain approval, verify Docker context endpoint remains local and server Linux/amd64 reachable; assert both exact container/volume names absent and image digest still resolves. Pull only the pinned reference if absent; record RepoDigests/image ID/config/version. Create the two labeled test-owned volumes and containers with --network none, no -p, POSTGRES_DB=wa_p0c_rehearsal, POSTGRES_PASSWORD_FILE and tmpfs /run/wa-secrets. Wait via pg_isready inside each exact container; no hosted connection.'},
  {'id':'FIRST-02','status':'NOT_RUN','action':'On each fresh target privileged bootstrap connection executes review-output/foundation-bootstrap.review.sql with psql -X -v ON_ERROR_STOP=1 -f. Create managed browser role simulation only if testing those names, label simulation. Bootstrap sets independent restricted-login SCRAM passwords and CONNECT only for needed roles; public CONNECT/TEMP are revoked for this isolated target.'},
  {'id':'FIRST-03','status':'NOT_RUN','action':'Actual wa_migrator TCP connection applies review-output/foundation-application.review.sql ONCE with ON_ERROR_STOP=1. It already contains the structure; do NOT apply foundation-structure.sql. Success target must COMMIT. Failure target uses a clearly retained test-only copy with SELECT 1/0 inserted immediately before final RESET ROLE/COMMIT; it must fail and ROLLBACK. Retain copy hash and error, never change canonical SQL.'},
  {'id':'FIRST-04','status':'NOT_RUN','action':'In a finally step on BOTH targets, original bootstrap grantor executes review-output/foundation-bootstrap-finalize.review.sql in a distinct connection after application connection exits. Independently SELECT pg_auth_members for roleid IN (wa_private_helper_owner,wa_customer_verifier,wa_track_verifier) and member wa_schema_owner: expect zero. Check has_schema_privilege(each leaf,platform_private,CREATE)=false. On failure target require absent app/platform application tables/functions and no dangling migration adoption. Runtime credentials inactive unless cleanup verification passes.'},
  {'id':'FIRST-05','status':'NOT_RUN','action':'Success target only: bootstrap-owned fixture transaction disables USER triggers ONLY on app.users and app.user_security_profiles, inserts synthetic Users A=10000000-0000-4000-8000-000000000001 and B=10000000-0000-4000-8000-000000000002 plus their security_generation0 rows, then reenables those same triggers before COMMIT; FK/CHECK constraints remain on. All optional personal/phone/secret/provider fields NULL; record privileged fixture provenance and enabled trigger catalog. This fixture seeding is not owner-runtime qualification.'},
  {'id':'FIRST-06','status':'NOT_RUN','action':'Open actual app READ COMMITTED transaction; before any business read/lock capture session_user,pg_backend_pid(),pg_current_xact_id()::text. Separate issuer transaction commits principal A grant: owner customer_buyer_profile, action SH-004.v1, purpose provision, root CustomerProfile/20000000-0000-4000-8000-000000000001, security/source generation0, hash of fresh256-bit handle, short expiry, exact row/revision/SELECT-field/INSERT-field capabilities for Customer + lifecycle history + command + evidence + two outbox messages. Query generated ACL map for every role-visible field needed by SELECT * trigger reads; do not use wildcard capabilities. The app binds via bind_request_context only after issuer COMMIT. No network call under source locks.'},
  {'id':'FIRST-07','status':'NOT_RUN','action':'Within that app transaction insert one command receipt (operation SH-004.v1, subject CustomerProfile:<id>, unique fixture semantic key/fingerprint, result schema1/valid SH004 closed result, state committed, source_revision0); Customer active/revision0/privacy_generation0 with display_name/avatar/city/state/country/archive NULL; lifecycle event from_status NULL/to_status active/source_revision0/actor A; OwnerMutationEvidence previous_revision NULL/committed_revision0/prior JSON null/exact generated Customer snapshot and decisionRef; exactly lifecycle event outbox ordinal0 and assignDefaultFreeTrack.v1 command ordinal1 with sourceCreationReceipt=command ID, revision0, semanticKey customer_buyer_profile/<id>/default-free-enrollment/v1. Payload/command digests use encode(sha256(convert_to(jsonb_value::text,UTF8)),hex), the actual SQL storage codec. All stamps/defaults remain server-owned. COMMIT must retain one coherent group; privileged read-only observer verifies exact counts, links, hashes and no worker enrollment yet.'},
  {'id':'FIRST-08','status':'NOT_RUN','action':'Use new IDs/semantic key and fresh app tuple/grant principal B, but attempt Customer.user_id=A with the same complete command/proof/messages path. Expect 42501/foreign Customer principal denial, ROLLBACK; independent privileged observer verifies zero group residue. Repeat with valid A but deliberately omit ordinal1 message: deferred COMMIT must fail; verify no command/Customer/history/evidence/outbox residue for that semantic key. Keep issuer grant (separately committed) bound to old xid; new transaction cannot reuse it.'},
  {'id':'FIRST-09','status':'NOT_RUN','action':'Retain source commit/tree and four SQL SHA256s, local context/server/image/digest, redacted command exit codes, schema-owner/leaf function ACL and membership catalogs, authenticated session_user for each connection, fixture IDs/counts, positive/negative/rollback receipts and cleanup evidence. No passwords/raw handles or personal bodies. Stop on any unexpected result; do not promote 94/451 cases from this small rehearsal.'},
  {'id':'FIRST-10','status':'NOT_RUN','action':'After evidence export and exact label/name verification, docker rm -f only wa-p0c-first-20261110-ok and wa-p0c-first-20261110-fail; docker volume rm only wa-p0c-first-20261110-ok-data and wa-p0c-first-20261110-fail-data. Delete only test-owned owner-only secret files. No prune, shared image removal, hosted cleanup or path-derived recursive delete. Independently confirm these exact test resources absent.'}
 ],
 'unresolved_prerequisites':['Brain approval of the corrected source and this exact rehearsal','Windows Docker Desktop local Linux daemon must be started by the authorized execution session; discovery found pipe absent','Concrete execution fixture/coordination script must follow the listed grant-field sets and closed current source shapes; review its exact bytes with the execution decision before running. This source pass supplies the protocol, IDs, outcomes and commands, not a tested DB harness.'],
 'expansion':'Only after FIRST-01..10 expected results and cleanup evidence pass, separately progress the staged94 with operation dependencies respected; remaining451 span later P0-C/D/E/F. Real auth/issuer adapters, pooling/worker loops/providers/hosted parity remain unqualified.',
 'database_posture':'D','database_connections_made':False,'sql_executed':False,'containers_started':False,'image_pulled':False
}
FIRST_REHEARSAL.update(
 fixture_source_generator='python -B scripts/prepare-first-rehearsal.py (environment-free; never calls Docker/SQL)',
 exact_fixture_packet='review-output/first-rehearsal/fixtures.json; generated source/observer SQL alongside it, exact per-row SELECT/INSERT capabilities and three distinct synthetic ID groups',
 dormant_coordinator='scripts/sql-review/run-first-rehearsal.py; refuses without --execute-approved-rehearsal before any Docker/DB call; same live app transaction, separate issuer COMMIT, raw secret only over controlled stdin, exact SQLSTATE/count checks',
 execution_command_after_separate_approval='python -B scripts/sql-review/run-first-rehearsal.py --execute-approved-rehearsal --evidence-directory "$env:TEMP/wa-p0c-first-20261110-evidence"',
 secret_setup='Bootstrap first sets ALTER DATABASE wa_p0c_rehearsal SET log_statement=none; ALTER DATABASE wa_p0c_rehearsal SET log_min_error_statement=panic, then in new controlled sessions provisions independent test role passwords and root-owned0600 /run/wa-secrets/pgpass over stdin. Coordinator verifies logging defaults before injecting a handle; no raw secret is retained or passed in argv.',
 unresolved_prerequisites=['Brain approval of the corrected source, exact generated fixture packet/coordinator and this rehearsal','Windows-connected authorized execution session starts Docker Desktop local Linux daemon; read-only discovery found pipe absent'],
)
FIRST_REHEARSAL['steps'][4]['action']='Success target only: privileged actual postgres TCP connection executes generated review-output/first-rehearsal/fixtures.sql. It disables USER triggers only on app.users/app.user_security_profiles in one fixture transaction, inserts synthetic A/B and security rows with explicit created_at/updated_at/mutation_transaction_id, reenables the same triggers before COMMIT, and preserves FK/CHECK enforcement. Retain the enabled-trigger catalog and privileged fixture provenance; not owner-runtime qualification.'
FIRST_REHEARSAL['steps'][5]['action']='Run the dormant coordinator only after approved install/finalization and private credential provisioning. It captures actual app login/PID/xid before business reads/locks, then commits the exact scenario grant through the separately authenticated issuer. Exact generated camelCase field arrays and UUIDs are in fixtures.json; no wildcard or deferred capability design. Only after issuer COMMIT does the same app connection bind its fresh handle. Native restricted logins use loopback TCP, not SET ROLE simulation.'
FIRST_REHEARSAL['steps'][6]['action']='Coordinator sends generated positive.sql into that same bound app transaction: command -> Customer -> exact history -> exact source evidence -> event ordinal0 + Free command ordinal1 -> COMMIT. It checks actual success plus generated privileged observer counts (1 command,1 source,1 history,1 evidence,2 outbox). Fixture digest provenance is explicit; JSON storage digests use Postgres jsonb::text. No worker enrollment is processed.'
FIRST_REHEARSAL['steps'][7]['action']='Coordinator uses fresh grant/tuple/IDs for wrong-person.sql: principalB tries userA and must fail42501 with zero generated group counts. It then uses still-unprovisioned valid userB/principalB for missing-outbox.sql, omits ordinal1 and requires P0001 at COMMIT plus zero group counts. This avoids Customer.user_id uniqueness masking the deferred rollback test. Separately committed grants remain bound to the old xid.'
FIRST_REHEARSAL['resource_commands_after_separate_approval']={
 'pull':'docker --context desktop-linux pull --platform linux/amd64 '+FIRST_REHEARSAL['image']['reference'],
 'volume_template':'docker --context desktop-linux volume create --label workinants.rehearsal=p0c-first-20261110 <exact success_volume or failure_volume above>',
 'container_template':'docker --context desktop-linux run -d --name <matching exact container> --label workinants.rehearsal=p0c-first-20261110 --network none --platform linux/amd64 --mount type=volume,src=<matching exact test volume>,dst=/var/lib/postgresql/data --mount type=bind,src=<owner-only test bootstrap password file outside Git>,dst=/run/bootstrap-password,readonly --tmpfs /run/wa-secrets:rw,nosuid,noexec,mode=0700 -e POSTGRES_DB=wa_p0c_rehearsal -e POSTGRES_PASSWORD_FILE=/run/bootstrap-password -e POSTGRES_HOST_AUTH_METHOD=scram-sha-256 '+FIRST_REHEARSAL['image']['reference']+' postgres -c log_statement=none -c log_min_error_statement=panic',
 'sql_transport_template':'Get-Content -Raw <reviewed SQL file> | docker --context desktop-linux exec -i -e PGPASSFILE=/run/wa-secrets/pgpass <exact target> psql -X -v ON_ERROR_STOP=1 -v VERBOSITY=sqlstate -h 127.0.0.1 -U <actual role> -d wa_p0c_rehearsal',
 'order':'bootstrap on each; provision independent passwords/private pgpass with statement logging disabled; application once as wa_migrator on success; explicit SELECT1/0 test copy before COMMIT on failure; original-grantor finalization in finally on BOTH; independent membership/CREATE/catalog observation; coordinator success-only; export evidence; exact-name/label cleanup from FIRST10'
}
# A final read-only snapshot arrived after the source correction was published.
# Preserve the initial observation; daemon availability is not execution consent.
FIRST_REHEARSAL['initial_docker_discovery']={'environment':FIRST_REHEARSAL['environment'],'unresolved_prerequisites':FIRST_REHEARSAL['unresolved_prerequisites']}
FIRST_REHEARSAL['latest_docker_readiness']={
 'observed_at':'2026-11-10T22:40:07-05:00','context':'desktop-linux',
 'endpoint':'npipe:////./pipe/dockerDesktopLinuxEngine','local':True,
 'client_version':'29.6.2','server_version':'29.6.2','desktop_version':'4.85.0 (235549)',
 'server_os':'linux','server_architecture':'amd64','daemon_reachable':True,
 'local_postgres_repository_images':0,'pinned_reference_present_locally':False,
 'image_inspect_exit_code':1,'image_pull_performed':False,
 'meaning':'Engine readiness gap resolved by the later observation. Registry image/version/digest remain established; exact pinned image must be pulled only after the separate execution decision. No database or container action was performed.'}
FIRST_REHEARSAL['environment']='Windows-connected local desktop-linux daemon is reachable at the final 22:40 read-only snapshot (Docker29.6.2, Desktop4.85.0, Linux/amd64). Initial pipe-absent observation is retained separately. No local postgres repository image or exact proposed pinned reference was present; no image was pulled.'
FIRST_REHEARSAL['unresolved_prerequisites']=['Brain approval of the corrected source, exact generated fixture packet/coordinator and specific rehearsal including the pinned image pull. Recheck local endpoint/resource absence/credentials at execution entry.']
