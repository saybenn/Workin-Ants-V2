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
  WHERE r.id='cd887c14-6508-5059-a868-04886b984718' AND r.user_id='075d7ed9-b5c3-5939-a807-9fa238c115ff' AND r.profile_id='aa50ee27-b66d-5fa9-b5f4-5144848088c9' AND r.track='customer'
   AND b.id='e02f142e-a7a0-5048-9d1a-d420d3a69fe7' AND s.id='b0ded3c1-d03c-5214-940f-6d434aac2789' AND r.selection_revision=b.revision AND b.revision=0
   AND r.result_code='already_enrolled' AND r.source_owner='customer_buyer_profile' AND r.source_creation_revision=0
   AND e.id='268baec6-4cb6-52b2-a238-10d8d9d09fad' AND c.id='2836fa7a-abd3-5dbf-b12d-be9c5ba14bc0' AND i.id='f2683a33-86f9-5f70-8040-78267f653441' AND w.id='92533181-a521-5ea7-a17b-60c58661ee6f' AND m.id='36ec5ebd-4379-5885-9349-aea52771af7e'
   AND a.id='0e5aa3a1-d88b-5778-bee3-a34ada88dfce' AND a.worker_id='worker-recovery-core-fixture.v1' AND a.attempt_number=1 AND a.fence=1 AND a.result='committed'
   AND w.state='leased' AND w.fence=1 AND w.attempt_count=1 AND e.state='committed' AND e.fence=w.fence AND c.state='committed'
   AND c.owner_module_id='track_subscription_entitlement' AND e.owner_module_id=c.owner_module_id
   AND c.operation='assignDefaultFreeTrack.v1' AND e.operation=c.operation AND w.handler_name=c.operation
   AND i.handler_name=c.operation AND i.consumer_owner=c.owner_module_id
   AND c.subject_scope='CustomerProfile:'||'aa50ee27-b66d-5fa9-b5f4-5144848088c9' AND e.subject_scope=c.subject_scope
   AND w.semantic_work_key=r.semantic_key AND c.semantic_key=r.semantic_key AND e.semantic_effect_key=r.semantic_key
   AND r.fingerprint=m.payload_hash AND c.fingerprint=m.payload_hash AND e.fingerprint=m.payload_hash AND i.payload_hash=m.payload_hash
   AND c.result_body=jsonb_build_object('outcome','already_enrolled','selectionRevision','0','receipt','cd887c14-6508-5059-a868-04886b984718') AND c.result_digest=e.result_hash
   AND c.result_schema_id='urn:workinants:database-review:foundation-payloads:v1#/$defs/assignDefaultFreeTrackCustomerResult' AND e.result_schema_id=c.result_schema_id
   AND c.mutation_transaction_id=r.mutation_transaction_id AND e.mutation_transaction_id=r.mutation_transaction_id
   AND i.mutation_transaction_id=r.mutation_transaction_id AND w.mutation_transaction_id=r.mutation_transaction_id
   AND a.mutation_transaction_id=r.mutation_transaction_id AND b.mutation_transaction_id=s.mutation_transaction_id
   AND r.mutation_transaction_id<>b.mutation_transaction_id)
);
COMMIT;
