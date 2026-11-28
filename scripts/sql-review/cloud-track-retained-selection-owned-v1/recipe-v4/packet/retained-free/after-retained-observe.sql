BEGIN READ ONLY;
SELECT jsonb_build_object(
 'exact_current_prior',EXISTS(SELECT 1 FROM app.track_base_selection b
  JOIN app.track_subscriptions s ON s.id=b.subscription_id
  JOIN app.track_plans p ON p.id=s.plan_id
  WHERE b.id='5dd1c4ed-2628-56a4-b790-abefc3a7b37a' AND s.id='af7c5ecc-edc0-5e20-902a-0e9b438623a6' AND p.id='d1ec3994-7360-5033-ae7a-632d8acda915'
  AND b.user_id='4b860286-670b-5db0-b416-d44c384f936b' AND s.user_id=b.user_id AND b.track='customer' AND s.track=b.track AND p.track=b.track
  AND b.customer_profile_id='c30510f5-b27a-5296-8749-c248c4d4724a' AND s.customer_profile_id=b.customer_profile_id
  AND b.candidate_profile_id IS NULL AND b.professional_profile_id IS NULL
  AND s.candidate_profile_id IS NULL AND s.professional_profile_id IS NULL
  AND b.revision=0 AND s.revision=0 AND b.source_generation=0 AND b.mutation_transaction_id=s.mutation_transaction_id
  AND s.status='active' AND s.ended_at IS NULL AND s.provider='none'
  AND s.provider_customer_id IS NULL AND s.provider_subscription_id IS NULL AND s.provider_price_id IS NULL
  AND s.current_period_start IS NULL AND s.current_period_end IS NULL
  AND p.status='active' AND p.billing_model='free' AND p.version='worker-control-synthetic.v1'
  AND p.content_hash='a49b9655d7a26d743969acf3013d48cfe86a97f7cc4696333706f5d26daa5944' AND p.monthly_price_cents IS NULL),
 'exact_worker_result_and_prior_transaction',EXISTS(
  SELECT 1 FROM app.track_enrollment_receipt r
  JOIN app.track_base_selection b ON b.id=r.selection_id
  JOIN app.track_subscriptions s ON s.id=b.subscription_id
  JOIN platform.runtime_effect_receipt e ON e.id=r.effect_receipt_id
  JOIN platform.runtime_command_receipt c ON c.id=e.command_receipt_id
  JOIN platform.runtime_inbox_receipt i ON i.effect_receipt_id=e.id
  JOIN platform.runtime_work_item w ON w.effect_receipt_id=e.id
  JOIN platform.runtime_outbox_message m ON m.id=w.outbox_message_id AND m.id=i.outbox_message_id
  JOIN platform.runtime_attempt a ON a.work_item_id=w.id
  WHERE r.id='fa39454d-b041-5e10-9634-08d73ecfbaa4' AND r.user_id='4b860286-670b-5db0-b416-d44c384f936b' AND r.profile_id='c30510f5-b27a-5296-8749-c248c4d4724a' AND r.track='customer'
   AND b.id='5dd1c4ed-2628-56a4-b790-abefc3a7b37a' AND s.id='af7c5ecc-edc0-5e20-902a-0e9b438623a6' AND r.selection_revision=b.revision AND b.revision=0
   AND r.result_code='already_enrolled' AND r.source_owner='customer_buyer_profile' AND r.source_creation_revision=0
   AND e.id='b6046134-b6cc-5c4c-b6d9-38509aacc050' AND c.id='d2d3e770-43a0-5234-96b0-ce8ab83e6309' AND i.id='44faba2f-9c6b-53a6-84d4-cf11d210eb64' AND w.id='771e9030-3d83-5d15-873e-6bfa3bf4f389' AND m.id='add755d4-036e-5130-83f0-6ff538c68cc1'
   AND a.id='4d82988f-e504-50ae-8250-fdadf5193372' AND a.worker_id='worker-recovery-core-fixture.v1' AND a.attempt_number=1 AND a.fence=1 AND a.result='committed'
   AND w.state='leased' AND w.fence=1 AND w.attempt_count=1 AND e.state='committed' AND e.fence=w.fence AND c.state='committed'
   AND c.owner_module_id='track_subscription_entitlement' AND e.owner_module_id=c.owner_module_id
   AND c.operation='assignDefaultFreeTrack.v1' AND e.operation=c.operation AND w.handler_name=c.operation
   AND i.handler_name=c.operation AND i.consumer_owner=c.owner_module_id
   AND c.subject_scope='CustomerProfile:'||'c30510f5-b27a-5296-8749-c248c4d4724a' AND e.subject_scope=c.subject_scope
   AND w.semantic_work_key=r.semantic_key AND c.semantic_key=r.semantic_key AND e.semantic_effect_key=r.semantic_key
   AND r.fingerprint=m.payload_hash AND c.fingerprint=m.payload_hash AND e.fingerprint=m.payload_hash AND i.payload_hash=m.payload_hash
   AND c.result_body=jsonb_build_object('outcome','already_enrolled','selectionRevision','0','receipt','fa39454d-b041-5e10-9634-08d73ecfbaa4') AND c.result_digest=e.result_hash
   AND c.result_schema_id='urn:workinants:database-review:foundation-payloads:v1#/$defs/assignDefaultFreeTrackCustomerResult' AND e.result_schema_id=c.result_schema_id
   AND c.mutation_transaction_id=r.mutation_transaction_id AND e.mutation_transaction_id=r.mutation_transaction_id
   AND i.mutation_transaction_id=r.mutation_transaction_id AND w.mutation_transaction_id=r.mutation_transaction_id
   AND a.mutation_transaction_id=r.mutation_transaction_id AND b.mutation_transaction_id=s.mutation_transaction_id
   AND r.mutation_transaction_id<>b.mutation_transaction_id)
);
COMMIT;
