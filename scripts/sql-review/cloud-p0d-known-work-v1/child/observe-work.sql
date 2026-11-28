BEGIN READ ONLY;
SET LOCAL TIME ZONE 'UTC';
WITH clock_sample AS MATERIALIZED (
  SELECT floor(extract(epoch FROM clock_timestamp())*1000)::bigint AS now_ms
), source_rows AS (
  SELECT mutation_transaction_id FROM platform.runtime_command_receipt WHERE id='ebc5b1de-0496-567d-820a-12499c92d32d'
  UNION ALL SELECT mutation_transaction_id FROM app.customer_profiles WHERE id='cdfa190f-3235-5c98-b217-bf27a5d03d66'
  UNION ALL SELECT mutation_transaction_id FROM app.customer_profile_lifecycle_event WHERE command_receipt_id='ebc5b1de-0496-567d-820a-12499c92d32d'
  UNION ALL SELECT mutation_transaction_id FROM platform.owner_mutation_evidence WHERE command_receipt_id='ebc5b1de-0496-567d-820a-12499c92d32d'
  UNION ALL SELECT mutation_transaction_id FROM platform.runtime_outbox_message WHERE command_receipt_id='ebc5b1de-0496-567d-820a-12499c92d32d'
), input_row AS (
  SELECT w.*
  FROM platform.runtime_work_item w
  WHERE w.id = '530db9d1-b945-53ec-bb0c-6d91c914b5fc'
), projected AS (
  SELECT jsonb_build_object(
    'count', (SELECT count(*) FROM platform.runtime_work_item),
    'identity_exact',
       w.outbox_message_id = '6be93914-5cc2-5cc0-a5b6-0906f8b4add1'
       AND w.handler_name = 'assignDefaultFreeTrack.v1'
       AND w.semantic_work_key = 'customer_buyer_profile/cdfa190f-3235-5c98-b217-bf27a5d03d66/default-free-enrollment/v1'
       AND w.next_attempt_at IS NULL AND w.effect_receipt_id IS NULL
       AND EXISTS (
         SELECT 1 FROM platform.runtime_outbox_message m
         WHERE m.id=w.outbox_message_id AND m.kind='command' AND m.name=w.handler_name
           AND m.producer_owner='customer_buyer_profile' AND m.aggregate_kind='CustomerProfile'
           AND m.aggregate_id='cdfa190f-3235-5c98-b217-bf27a5d03d66'
           AND m.command_receipt_id='ebc5b1de-0496-567d-820a-12499c92d32d'
           AND m.source_revision=0 AND m.source_generation=0
           AND m.payload->>'semanticKey'=w.semantic_work_key
       ),
    'state', w.state, 'fence', w.fence, 'attempt', w.attempt_count,
    'deadline_ms', floor(extract(epoch FROM w.lease_expires_at)*1000)::bigint,
    'lease_digest_sha256', encode(sha256(convert_to(w.lease_token_hash::text,'UTF8')),'hex'),
    'mutation_xid', w.mutation_transaction_id,
    'row_sha256', encode(sha256(convert_to(to_jsonb(w)::text,'UTF8')),'hex'),
    'without_deadline_xid_sha256', encode(sha256(convert_to((to_jsonb(w)-ARRAY['lease_expires_at','mutation_transaction_id'])::text,'UTF8')),'hex'),
    'identity_sha256', encode(sha256(convert_to((to_jsonb(w)-ARRAY['state','fence','attempt_count','lease_token_hash',
            'lease_expires_at','mutation_transaction_id'])::text,'UTF8')),'hex')
  ) AS work
  FROM input_row w
)
SELECT jsonb_build_object(
  'server_ms',(SELECT now_ms FROM clock_sample),
  'source_count',(SELECT count(*) FROM source_rows),
  'source_distinct_xids',(SELECT count(DISTINCT mutation_transaction_id) FROM source_rows),
  'source_xid',(SELECT min(mutation_transaction_id) FROM source_rows),
  'work_total',(SELECT count(*) FROM platform.runtime_work_item),
  'work',(SELECT work FROM projected),
  'restricted_clients',(SELECT count(*) FROM pg_stat_activity
      WHERE datname=current_database() AND usename IN ('wa_app_runtime','wa_worker','wa_context_issuer')),
  'work_attempts',(SELECT count(*) FROM platform.runtime_attempt),
  'runtime_inbox',(SELECT count(*) FROM platform.runtime_inbox_receipt),
  'track_effects',(SELECT count(*) FROM platform.runtime_effect_receipt WHERE operation='assignDefaultFreeTrack.v1'),
  'track_enrollments',(SELECT count(*) FROM app.track_enrollment_receipt)
);
COMMIT;
