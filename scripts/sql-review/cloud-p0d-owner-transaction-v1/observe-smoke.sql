BEGIN READ ONLY;
SET LOCAL TIME ZONE 'UTC';
WITH source_group AS (
  SELECT mutation_transaction_id FROM platform.runtime_command_receipt WHERE id = 'ebc5b1de-0496-567d-820a-12499c92d32d'
  UNION ALL SELECT mutation_transaction_id FROM app.customer_profiles WHERE id = 'cdfa190f-3235-5c98-b217-bf27a5d03d66'
  UNION ALL SELECT mutation_transaction_id FROM app.customer_profile_lifecycle_event WHERE command_receipt_id = 'ebc5b1de-0496-567d-820a-12499c92d32d'
  UNION ALL SELECT mutation_transaction_id FROM platform.owner_mutation_evidence WHERE command_receipt_id = 'ebc5b1de-0496-567d-820a-12499c92d32d'
  UNION ALL SELECT mutation_transaction_id FROM platform.runtime_outbox_message WHERE command_receipt_id = 'ebc5b1de-0496-567d-820a-12499c92d32d'
  UNION ALL SELECT mutation_transaction_id FROM platform.runtime_effect_receipt WHERE command_receipt_id = 'ebc5b1de-0496-567d-820a-12499c92d32d'
),
work AS (
  SELECT jsonb_build_object(
    'full_row_sha256',encode(sha256(convert_to(to_jsonb(w)::text,'UTF8')),'hex'),
    'scheduled_xid',w.mutation_transaction_id,
    'known_pending_original',
      w.outbox_message_id = '6be93914-5cc2-5cc0-a5b6-0906f8b4add1'
      AND w.handler_name = 'assignDefaultFreeTrack.v1'
      AND w.semantic_work_key = 'customer_buyer_profile/cdfa190f-3235-5c98-b217-bf27a5d03d66/default-free-enrollment/v1'
      AND w.state = 'pending' AND w.fence = 0 AND w.attempt_count = 0 AND w.next_attempt_at IS NULL
      AND w.lease_token_hash IS NULL AND w.lease_expires_at IS NULL AND w.effect_receipt_id IS NULL
  ) AS result
  FROM platform.runtime_work_item w WHERE w.id = '530db9d1-b945-53ec-bb0c-6d91c914b5fc'
),
issued AS (
  SELECT id, token_hash, issuer_service, principal_user_id, service_principal, database_login_role,
    owner_module_id, action, purpose, target_kind, target_id, security_generation, source_generation,
    backend_pid, transaction_id, expires_at, revoked_at, created_at, mutation_transaction_id,
    encode(sha256(convert_to(array_to_string(allowed_fields,chr(10)),'UTF8')),'hex') AS fields_sha256
  FROM platform.database_action_grant
  WHERE policy_version = 'wa-p0d-owner-smoke.v1'
),
classified AS (
  SELECT transaction_id, CASE
    WHEN owner_module_id = 'customer_buyer_profile' AND action = 'SH-004.v1' AND purpose = 'provision'
      AND target_kind = 'CustomerProfile' AND target_id = 'cdfa190f-3235-5c98-b217-bf27a5d03d66' AND security_generation = 0
      AND fields_sha256 = '10901bb4fccfd450f2049df71a74f2d41d0d537f09e33fc5dd1a1f8ee9cb90ea' THEN 'source'
    WHEN owner_module_id = 'platform_integration_owner' AND action = 'runtime.schedule_work.v1' AND purpose = 'work.schedule'
      AND target_kind = 'RuntimeWorkItem' AND target_id = '530db9d1-b945-53ec-bb0c-6d91c914b5fc' AND security_generation = 0
      AND fields_sha256 = '6fcd1458f8cdf7f054e097f8cd3a39c81dded57b9c687268a52986ab9e7d5dbc' THEN 'schedule'
    WHEN owner_module_id = 'customer_buyer_profile' AND action = 'SH-004.v1' AND purpose = 'provision'
      AND target_kind = 'CustomerProfile' AND target_id = 'cdfa190f-3235-5c98-b217-bf27a5d03d66' AND security_generation = 0
      AND fields_sha256 = '565b67ce3ba6e40ff30d4b77f27b8982bb5ee27aa67784a3190fc369aaeaac4d' THEN 'complete'
    WHEN owner_module_id = 'customer_buyer_profile' AND action = 'SH-004.v1' AND purpose = 'provision'
      AND target_kind = 'CustomerProfile' AND target_id = 'cdfa190f-3235-5c98-b217-bf27a5d03d66' AND security_generation = 1
      AND fields_sha256 = '565b67ce3ba6e40ff30d4b77f27b8982bb5ee27aa67784a3190fc369aaeaac4d' THEN 'stale'
    WHEN owner_module_id = 'customer_buyer_profile' AND action = 'SH-004.v1' AND purpose = 'provision'
      AND target_kind = 'CustomerProfile' AND target_id = 'cdfa190f-3235-5c98-b217-bf27a5d03d66' AND security_generation = 0
      AND fields_sha256 = '82836dcd2e1e076c2f43d5f5ce0813aa5377f772cdb2ae0b8803253919c00456' THEN 'missing_revision'
    WHEN owner_module_id = 'platform_integration_owner' AND action = 'runtime.schedule_work.v1' AND purpose = 'work.schedule'
      AND target_kind = 'RuntimeWorkItem' AND target_id = '530db9d1-b945-53ec-bb0c-6d91c914b5fc' AND security_generation = 0
      AND fields_sha256 = '0f8083d7fa9409e06e3e6be8b4b96cc05ebf161822d1c3c54643b097efd89755' THEN 'work_update'
    ELSE 'unexpected'
  END AS grant_shape
  FROM issued
),
shapes AS (
  SELECT grant_shape, jsonb_agg(transaction_id ORDER BY transaction_id COLLATE "C") AS xids
  FROM classified GROUP BY grant_shape
)
SELECT jsonb_build_object(
  'source_count',(SELECT count(*) FROM source_group),
  'source_distinct_xids',(SELECT count(DISTINCT mutation_transaction_id) FROM source_group),
  'source_xid',(SELECT min(mutation_transaction_id) FROM source_group),
  'work',(SELECT result FROM work),
  'work_count',(SELECT count(*) FROM work),
  'restricted_sessions',(SELECT count(*) FROM pg_stat_activity
    WHERE datname = current_database() AND usename IN ('wa_app_runtime','wa_context_issuer')),
  'grant_total',(SELECT count(*) FROM platform.database_action_grant),
  'grant_count',(SELECT count(*) FROM issued),
  'runtime_pid',(SELECT min(backend_pid) FROM issued),
  'runtime_pids',(SELECT count(DISTINCT backend_pid) FROM issued),
  'separate_issuer_transactions',(SELECT count(DISTINCT mutation_transaction_id) FROM issued),
  'grant_ids_distinct',(SELECT count(DISTINCT id) = count(*) FROM issued),
  'grant_hashes_distinct',(SELECT count(DISTINCT token_hash) = count(*) FROM issued),
  'grant_runtime_xids_distinct',(SELECT count(DISTINCT transaction_id) FROM issued),
  'issuer_and_runtime_xids_disjoint',(SELECT NOT EXISTS (
    SELECT 1 FROM issued a JOIN issued b ON a.mutation_transaction_id = b.transaction_id)),
  'grant_metadata_exact',(SELECT coalesce(bool_and(
    issuer_service = 'wa_context_issuer' AND database_login_role = 'wa_app_runtime'
    AND principal_user_id = '8136b2ae-cea6-5c8d-a04e-9bd70784c943' AND service_principal IS NULL
    AND source_generation = 0 AND expires_at > created_at AND revoked_at IS NULL
  ),false) FROM issued),
  'grant_shapes',(SELECT jsonb_object_agg(grant_shape,xids) FROM shapes)
);
COMMIT;
