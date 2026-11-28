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
 'own_work_ready',EXISTS(SELECT 1 FROM platform.runtime_work_item w WHERE w.id='771e9030-3d83-5d15-873e-6bfa3bf4f389'
  AND w.outbox_message_id='add755d4-036e-5130-83f0-6ff538c68cc1' AND w.state='leased' AND w.fence=1 AND w.attempt_count=1
  AND w.effect_receipt_id IS NULL AND w.lease_expires_at>clock_timestamp()),
 'no_prior_operation_receipts',NOT EXISTS(SELECT 1 FROM platform.runtime_command_receipt WHERE id='d2d3e770-43a0-5234-96b0-ce8ab83e6309')
  AND NOT EXISTS(SELECT 1 FROM platform.runtime_effect_receipt WHERE id='b6046134-b6cc-5c4c-b6d9-38509aacc050')
  AND NOT EXISTS(SELECT 1 FROM platform.runtime_inbox_receipt WHERE id='44faba2f-9c6b-53a6-84d4-cf11d210eb64')
  AND NOT EXISTS(SELECT 1 FROM app.track_enrollment_receipt WHERE profile_id='c30510f5-b27a-5296-8749-c248c4d4724a')
  AND NOT EXISTS(SELECT 1 FROM platform.runtime_attempt WHERE work_item_id='771e9030-3d83-5d15-873e-6bfa3bf4f389')
);
COMMIT;
