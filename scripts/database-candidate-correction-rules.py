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
    'platform_private.context_allows(owner,kind,id,operation,purpose) returns only a Boolean '
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
        worker = ['SELECT_EXACT_DEFAULT_FREE_TARGET', 'INSERT_OR_UPDATE_DEFAULT_FREE_ONLY_WITH_CURRENT_CUSTOMER_FACT_AND_COMMAND_RECEIPT']
    helper = ['SELECT_SECURITY_GENERATION_COLUMNS_VIA_DEFINER_ONLY'] if row['model'] == 'UserSecurityProfile' else []
    return {
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


def table_cases(row, primary_key):
    profile = access_profile(row)
    setup = {
        'table': row['candidate_table'], 'owner': row['source_owner'], 'pk': primary_key,
        'operations_by_role': profile['operations_by_role'],
        'foreign_prerequisites': [f['attributes'] for f in row['foreign_relationships']],
        'context': 'Exact immutable issuer-bound transaction tuple, target/action/fields and current generations; no caller-supplied authority',
    }
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
    negative = {
        'table': row['candidate_table'],
        'direct_denials_by_role': profile['direct_denials_by_role'],
        'additional_denials': ['FOREIGN_RUNTIME_CONTEXT', 'UNREGISTERED_WORKER_ACTION', 'MISSING_OR_STALE_TUPLE_OR_GENERATION', 'OWNERSHIP_OR_IMMUTABLE_FIELD_REASSIGNMENT'],
        'fixture': 'Same synthetic concrete rows as the positive case',
    }
    return setup, positive, expected, negative
