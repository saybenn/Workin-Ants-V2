BEGIN;
ALTER TABLE app.track_subscriptions DISABLE TRIGGER owner_commit;
ALTER TABLE app.track_base_selection DISABLE TRIGGER owner_commit;
INSERT INTO app.track_subscriptions (id,user_id,track,customer_profile_id,candidate_profile_id,professional_profile_id,plan_id,status,provider) VALUES ('af7c5ecc-edc0-5e20-902a-0e9b438623a6','4b860286-670b-5db0-b416-d44c384f936b','customer','c30510f5-b27a-5296-8749-c248c4d4724a',NULL,NULL,'d1ec3994-7360-5033-ae7a-632d8acda915','active','none');
INSERT INTO app.track_base_selection (id,user_id,track,customer_profile_id,candidate_profile_id,professional_profile_id,subscription_id,source_generation) VALUES ('5dd1c4ed-2628-56a4-b790-abefc3a7b37a','4b860286-670b-5db0-b416-d44c384f936b','customer','c30510f5-b27a-5296-8749-c248c4d4724a',NULL,NULL,'af7c5ecc-edc0-5e20-902a-0e9b438623a6',0);
SET CONSTRAINTS ALL IMMEDIATE;
ALTER TABLE app.track_base_selection ENABLE TRIGGER owner_commit;
ALTER TABLE app.track_subscriptions ENABLE TRIGGER owner_commit;
COMMIT;
