BEGIN;
ALTER TABLE app.track_subscriptions DISABLE TRIGGER owner_commit;
ALTER TABLE app.track_base_selection DISABLE TRIGGER owner_commit;
INSERT INTO app.track_subscriptions (id,user_id,track,customer_profile_id,candidate_profile_id,professional_profile_id,plan_id,status,provider,current_period_start,current_period_end) VALUES ('b0ded3c1-d03c-5214-940f-6d434aac2789','075d7ed9-b5c3-5939-a807-9fa238c115ff','customer','aa50ee27-b66d-5fa9-b5f4-5144848088c9',NULL,NULL,'aeb3144a-8c21-5046-9582-a3bef344907d','active','manual',clock_timestamp()-interval '5 minutes',clock_timestamp()+interval '30 minutes');
INSERT INTO app.track_base_selection (id,user_id,track,customer_profile_id,candidate_profile_id,professional_profile_id,subscription_id,source_generation) VALUES ('e02f142e-a7a0-5048-9d1a-d420d3a69fe7','075d7ed9-b5c3-5939-a807-9fa238c115ff','customer','aa50ee27-b66d-5fa9-b5f4-5144848088c9',NULL,NULL,'b0ded3c1-d03c-5214-940f-6d434aac2789',0);
SET CONSTRAINTS ALL IMMEDIATE;
ALTER TABLE app.track_base_selection ENABLE TRIGGER owner_commit;
ALTER TABLE app.track_subscriptions ENABLE TRIGGER owner_commit;
COMMIT;
