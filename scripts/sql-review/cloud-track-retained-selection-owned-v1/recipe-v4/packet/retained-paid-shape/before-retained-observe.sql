BEGIN READ ONLY;
SELECT jsonb_build_object(
 'exact_current_prior',EXISTS(SELECT 1 FROM app.track_base_selection b
  JOIN app.track_subscriptions s ON s.id=b.subscription_id
  JOIN app.track_plans p ON p.id=s.plan_id
  WHERE b.id='e02f142e-a7a0-5048-9d1a-d420d3a69fe7' AND s.id='b0ded3c1-d03c-5214-940f-6d434aac2789' AND p.id='aeb3144a-8c21-5046-9582-a3bef344907d'
  AND b.user_id='075d7ed9-b5c3-5939-a807-9fa238c115ff' AND s.user_id=b.user_id AND b.track='customer' AND s.track=b.track AND p.track=b.track
  AND b.customer_profile_id='aa50ee27-b66d-5fa9-b5f4-5144848088c9' AND s.customer_profile_id=b.customer_profile_id
  AND b.candidate_profile_id IS NULL AND b.professional_profile_id IS NULL
  AND s.candidate_profile_id IS NULL AND s.professional_profile_id IS NULL
  AND b.revision=0 AND s.revision=0 AND b.source_generation=0 AND b.mutation_transaction_id=s.mutation_transaction_id
  AND s.status='active' AND s.ended_at IS NULL AND s.provider='manual'
  AND s.provider_customer_id IS NULL AND s.provider_subscription_id IS NULL AND s.provider_price_id IS NULL
  AND s.current_period_start<=clock_timestamp() AND s.current_period_end>clock_timestamp()
  AND p.status='active' AND p.billing_model='subscription' AND p.version='f0-retained-manual-shape.v1'
  AND p.content_hash='cfcb4d8891de392f0e8fad2136e9fd33baccc43e6651b74490bce931167fd3e4' AND p.monthly_price_cents=1 AND p.currency='USD'),
 'own_work_ready',EXISTS(SELECT 1 FROM platform.runtime_work_item w WHERE w.id='92533181-a521-5ea7-a17b-60c58661ee6f'
  AND w.outbox_message_id='36ec5ebd-4379-5885-9349-aea52771af7e' AND w.state='leased' AND w.fence=1 AND w.attempt_count=1
  AND w.effect_receipt_id IS NULL AND w.lease_expires_at>clock_timestamp()),
 'no_prior_operation_receipts',NOT EXISTS(SELECT 1 FROM platform.runtime_command_receipt WHERE id='2836fa7a-abd3-5dbf-b12d-be9c5ba14bc0')
  AND NOT EXISTS(SELECT 1 FROM platform.runtime_effect_receipt WHERE id='268baec6-4cb6-52b2-a238-10d8d9d09fad')
  AND NOT EXISTS(SELECT 1 FROM platform.runtime_inbox_receipt WHERE id='f2683a33-86f9-5f70-8040-78267f653441')
  AND NOT EXISTS(SELECT 1 FROM app.track_enrollment_receipt WHERE profile_id='aa50ee27-b66d-5fa9-b5f4-5144848088c9')
  AND NOT EXISTS(SELECT 1 FROM platform.runtime_attempt WHERE work_item_id='92533181-a521-5ea7-a17b-60c58661ee6f')
);
COMMIT;
