BEGIN READ ONLY;
SET LOCAL TIME ZONE 'UTC';
WITH fixture(label,profile_id,user_id,receipt_id,history_id,evidence_id,lifecycle_id,intent_id,decision_ref,
             semantic_key,request_id,correlation_id,fingerprint) AS (VALUES
  ('primary', 'cdfa190f-3235-5c98-b217-bf27a5d03d66'::uuid, '8136b2ae-cea6-5c8d-a04e-9bd70784c943'::uuid, 'ebc5b1de-0496-567d-820a-12499c92d32d'::uuid, 'd819bc18-7905-556e-bf07-4f21f62362a0'::uuid, '236df9dc-6084-5d71-8e7e-a97919fa2b21'::uuid, '5699ca7e-1df1-5d47-84d9-6bdabfb7c8f3'::uuid, '6be93914-5cc2-5cc0-a5b6-0906f8b4add1'::uuid, 'p0d-customer-proof-primary-decision', 'customer-controls-app-write-two-genuine-sh004', 'p0d-customer-proof-primary', 'p0d-customer-proof-primary-correlation', '7299619aea58ddc7969b1e92da224f65597c5fe70455bfdf3c7dbfffb3dce099'),
  ('rollback', 'a806260b-2295-579f-a3ec-3173582e0528'::uuid, '0c0ba942-ce1f-5fd4-aa1f-466be695de97'::uuid, '1704d3f1-aff9-5966-8f59-21133dc56fab'::uuid, '21a2dcae-1108-562d-ab32-949e3bfb89c6'::uuid, '349910bd-d824-5ef1-9002-f5af304e4cfb'::uuid, '1ec53d47-ba14-511f-bf2a-15f385897966'::uuid, 'e73fa313-1b3b-5da2-8e55-11d272d51d95'::uuid, 'p0d-customer-proof-rollback-decision', 'p0d-customer-proof-rollback-key', 'p0d-customer-proof-rollback', 'p0d-customer-proof-rollback-correlation', 'a3871ea88bb266979a0df532f42c69cc4ed42c5bf30a7d944490fb29919e99b2')
),
rows AS (
 SELECT f.label,'customer' AS kind,to_jsonb(c) AS body FROM fixture f JOIN app.customer_profiles c ON c.id=f.profile_id
 UNION ALL SELECT f.label,'command',to_jsonb(q) FROM fixture f
   JOIN platform.runtime_command_receipt q ON q.id=f.receipt_id
 UNION ALL SELECT f.label,'history',to_jsonb(h) FROM fixture f
   JOIN app.customer_profile_lifecycle_event h ON h.id=f.history_id
 UNION ALL SELECT f.label,'evidence',to_jsonb(e) FROM fixture f
   JOIN platform.owner_mutation_evidence e ON e.id=f.evidence_id
 UNION ALL SELECT f.label,'lifecycle',to_jsonb(o) FROM fixture f
   JOIN platform.runtime_outbox_message o ON o.id=f.lifecycle_id
 UNION ALL SELECT f.label,'intent',to_jsonb(o) FROM fixture f
   JOIN platform.runtime_outbox_message o ON o.id=f.intent_id
),
row_counts AS (
 SELECT label,count(*) AS total,min(body->>'mutation_transaction_id') AS app_xid,
   count(DISTINCT body->>'mutation_transaction_id') AS distinct_xids,
   encode(sha256(convert_to(jsonb_object_agg(kind,body)::text,'UTF8')),'hex') AS group_hash
 FROM rows GROUP BY label
),
coherent AS (
 SELECT f.label,q.result_digest::text AS result_digest,
   q.result_body #>> '{value,receipt,recordedAt}' AS recorded_at
 FROM fixture f
 JOIN app.customer_profiles c ON c.id=f.profile_id AND c.user_id=f.user_id
   AND c.status='active' AND c.revision=0 AND c.privacy_generation=0
   AND c.display_name IS NULL AND c.avatar_media_id IS NULL AND c.city IS NULL
   AND c.state IS NULL AND c.country IS NULL AND c.archived_at IS NULL
 JOIN platform.runtime_command_receipt q ON q.id=f.receipt_id AND q.owner_module_id='customer_buyer_profile'
   AND q.operation='SH-004.v1' AND q.subject_scope='CustomerProfile:'||f.profile_id::text
   AND q.semantic_key=f.semantic_key AND q.fingerprint=f.fingerprint
   AND q.state='committed' AND q.source_revision=0 AND q.result_schema_id='SH-004.v1#/$defs/response'
   AND q.result_schema_version='1' AND q.result_digest=encode(sha256(convert_to(q.result_body::text,'UTF8')),'hex')
   AND q.result_body=jsonb_build_object('contract','SH-004.v1','requestId',f.request_id,'status','ok','value',
     jsonb_build_object('customerProfileId',f.profile_id,'userId',f.user_id,'lifecycle','active','sourceToken','0','receipt',
       jsonb_build_object('owner','customer_buyer_profile','id',f.receipt_id,'semanticKey',f.semantic_key,
         'fingerprint',f.fingerprint,'sourceToken','0','recordedAt',q.result_body #>> '{value,receipt,recordedAt}')))
 JOIN app.customer_profile_lifecycle_event h ON h.id=f.history_id AND h.command_receipt_id=f.receipt_id
   AND h.customer_profile_id=f.profile_id AND h.source_revision=0 AND h.from_status IS NULL AND h.to_status='active'
   AND h.name='customer.lifecycle_changed.v1' AND h.actor_user_id=f.user_id
 JOIN platform.owner_mutation_evidence e ON e.id=f.evidence_id AND e.command_receipt_id=f.receipt_id
   AND e.owner_module_id=q.owner_module_id AND e.aggregate_kind='CustomerProfile' AND e.aggregate_id=f.profile_id::text
   AND e.previous_revision IS NULL AND e.committed_revision=0 AND e.action=q.operation AND e.decision_ref=f.decision_ref
   AND e.evidence_schema_id='urn:workinants:database-review:owner-evidence:v1#/$defs/CustomerProfile'
   AND e.evidence_schema_version='1' AND e.evidence_digest=encode(sha256(convert_to(e.evidence_body::text,'UTF8')),'hex')
   AND e.evidence_body=jsonb_build_object('schema','database-owner-evidence.v1','owner','customer_buyer_profile',
     'model','CustomerProfile','primaryKey',jsonb_build_object('id',f.profile_id),'prior',NULL,
     'committed',jsonb_build_object('id',f.profile_id,'userId',f.user_id,'status','active','revision','0','privacyGeneration','0'),
     'decisionRef',f.decision_ref)
 JOIN platform.runtime_outbox_message l ON l.id=f.lifecycle_id AND l.ordinal=0 AND l.kind='event'
   AND l.name='customer.lifecycle_changed.v1'
   AND l.payload_schema_id='urn:workin-ants:types:v1#/$defs/EventPayload_customer_lifecycle_changed_v1'
   AND l.payload=jsonb_build_object('eventName','customer.lifecycle_changed.v1','customerProfileId',f.profile_id,
     'userId',f.user_id,'lifecycleRevision','0','safeState','active')
 JOIN platform.runtime_outbox_message d ON d.id=f.intent_id AND d.ordinal=1 AND d.kind='command'
   AND d.name='assignDefaultFreeTrack.v1'
   AND d.payload_schema_id='urn:workinants:database-review:foundation-payloads:v1#/$defs/assignDefaultFreeTrackCustomerCommand'
   AND d.payload=jsonb_build_object('sourceOwner','customer_buyer_profile','userId',f.user_id,'track','customer',
     'customerProfileId',f.profile_id,'sourceCreationRevision','0','sourceCreationReceipt',f.receipt_id,
     'semanticKey','customer_buyer_profile/'||f.profile_id::text||'/default-free-enrollment/v1')
 WHERE l.occurred_at=d.occurred_at AND date_trunc('milliseconds',l.occurred_at) =
   (q.result_body #>> '{value,receipt,recordedAt}')::timestamptz
 AND NOT EXISTS (
  SELECT 1 FROM platform.runtime_outbox_message o WHERE o.id IN (f.lifecycle_id,f.intent_id) AND NOT (
    o.command_receipt_id=f.receipt_id AND o.producer_owner=q.owner_module_id
    AND o.aggregate_kind='CustomerProfile' AND o.aggregate_id=f.profile_id::text
    AND o.source_revision=0 AND o.source_generation=0 AND o.schema_version='1'
    AND o.correlation_id=f.correlation_id AND o.causation_id=f.receipt_id::text
    AND o.correction_of_id IS NULL AND o.occurred_at=o.effective_at
    AND o.payload_hash=encode(sha256(convert_to(o.payload::text,'UTF8')),'hex')
  )
 )
),
issued AS (
 SELECT backend_pid,transaction_id,mutation_transaction_id,token_hash,id,
   (database_login_role='wa_app_runtime' AND issuer_service='wa_context_issuer'
    AND owner_module_id='customer_buyer_profile' AND action='SH-004.v1' AND purpose='provision'
    AND target_kind='CustomerProfile' AND security_generation=0 AND source_generation=0
    AND service_principal IS NULL AND revoked_at IS NULL AND expires_at>created_at) AS metadata_exact,
   target_id,principal_user_id,
   encode(sha256(convert_to(array_to_string(allowed_fields,chr(10)),'UTF8')),'hex') AS fields_sha
 FROM platform.database_action_grant WHERE policy_version='wa-p0d-customer-proof.v1'
),
classified AS (
 SELECT CASE
   WHEN target_id='cdfa190f-3235-5c98-b217-bf27a5d03d66' AND principal_user_id='8136b2ae-cea6-5c8d-a04e-9bd70784c943' AND fields_sha='684bc408a16638003b12e3a6b19e5dc17e0da1d7f728d12af237c0e396e6f3ec' THEN 'primary'
   WHEN target_id='a806260b-2295-579f-a3ec-3173582e0528' AND principal_user_id='0c0ba942-ce1f-5fd4-aa1f-466be695de97' AND fields_sha='e6f65144276a71d4b077087be5962cbfba80ead34de996bf608d39ffb9d6d5a6' THEN 'rollback'
   WHEN target_id='a806260b-2295-579f-a3ec-3173582e0528' AND principal_user_id='0c0ba942-ce1f-5fd4-aa1f-466be695de97' AND fields_sha='6d029a15a9d745035d4fee53874d5188d3974d444bc5019bf1b73a4ca2dbf29e' THEN 'rollback_without_intent'
   ELSE 'unexpected' END AS capability_shape,
   backend_pid,transaction_id
 FROM issued
),
grant_groups AS (
 SELECT capability_shape,jsonb_agg(jsonb_build_object('pid',backend_pid,'xid',transaction_id)
     ORDER BY transaction_id COLLATE "C") AS value FROM classified GROUP BY capability_shape
)
SELECT jsonb_build_object(
  'scope_groups',(SELECT jsonb_object_agg(f.label,jsonb_build_object(
    'count',coalesce(r.total,0),'distinct_xids',coalesce(r.distinct_xids,0),
    'xid',r.app_xid,'rows_sha256',r.group_hash,'coherent',c.label IS NOT NULL,
    'result_digest',c.result_digest,'recorded_at',c.recorded_at))
    FROM fixture f LEFT JOIN row_counts r USING(label) LEFT JOIN coherent c USING(label)),
  'physical_counts',jsonb_build_object(
    'users',(SELECT count(*) FROM app.users),
    'security_profiles',(SELECT count(*) FROM app.user_security_profiles),
    'customers',(SELECT count(*) FROM app.customer_profiles),
    'receipts',(SELECT count(*) FROM platform.runtime_command_receipt),
    'history',(SELECT count(*) FROM app.customer_profile_lifecycle_event),
    'evidence',(SELECT count(*) FROM platform.owner_mutation_evidence),
    'outbox',(SELECT count(*) FROM platform.runtime_outbox_message),
    'work',(SELECT count(*) FROM platform.runtime_work_item),
    'effects',(SELECT count(*) FROM platform.runtime_effect_receipt),
    'grants',(SELECT count(*) FROM platform.database_action_grant)),
  'grants_ok',(SELECT coalesce(bool_and(metadata_exact),true) AND count(*)=count(DISTINCT token_hash)
    AND count(*)=count(DISTINCT mutation_transaction_id) AND count(*)=count(DISTINCT transaction_id)
    AND NOT EXISTS(SELECT 1 FROM issued a JOIN issued b ON a.transaction_id=b.mutation_transaction_id) FROM issued),
  'grant_groups',(SELECT coalesce(jsonb_object_agg(capability_shape,value),'{}'::jsonb) FROM grant_groups),
  'restricted_sessions',(SELECT count(*) FROM pg_stat_activity WHERE datname=current_database()
     AND usename IN('wa_app_runtime','wa_context_issuer'))
);
COMMIT;
