BEGIN READ ONLY;
SET LOCAL TIME ZONE 'UTC';
SELECT jsonb_build_object(
  'count',count(*),
  'distinct_hashes',count(DISTINCT token_hash),
  'grants',coalesce(jsonb_agg(jsonb_build_object(
    'id',id,
    'issuer_service',issuer_service,
    'role',database_login_role,
    'owner',owner_module_id,
    'action',action,
    'purpose',purpose,
    'target_kind',target_kind,
    'target_id',target_id,
    'security_generation',security_generation,
    'source_generation',source_generation,
    'policy',policy_version,
    'pid',backend_pid,
    'runtime_xid',transaction_id,
    'issuer_xid',mutation_transaction_id,
    'fields_sha256',encode(sha256(convert_to(array_to_string(allowed_fields,chr(10)),'UTF8')),'hex'),
    'identity_exact',CASE WHEN database_login_role='wa_app_runtime'
      THEN principal_user_id='8136b2ae-cea6-5c8d-a04e-9bd70784c943' AND service_principal IS NULL
      WHEN database_login_role='wa_worker'
      THEN principal_user_id IS NULL AND service_principal='lease-revoke-worker.v1' ELSE false END,
    'metadata_exact',expires_at>created_at AND expires_at<=created_at+interval '125 seconds'
      AND revoked_at IS NULL AND token_hash::text ~ '^[0-9a-f]{64}$',
    'row_sha256',encode(sha256(convert_to(to_jsonb(g)::text,'UTF8')),'hex')
  ) ORDER BY id),'[]'::jsonb)
) FROM platform.database_action_grant g;
COMMIT;
