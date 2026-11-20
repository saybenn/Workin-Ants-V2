SELECT 'WA_WR_BEFORE_VALID_CURRENT_FREE_SELECTION_SURVIVES_DUPLICATE_ATTEMPT';
INSERT INTO app.track_subscriptions ("id","user_id","track","customer_profile_id","candidate_profile_id","professional_profile_id","plan_id","status","provider") VALUES ('f149ef7f-2807-58be-afe7-668aefa2801d','1a00123e-aadd-5e3b-aa9b-797fda5b72cc','customer','51b0eaff-9164-508e-9cd9-c8fc679af06a',NULL,NULL,'91141536-7eb6-563b-8265-ee85eb4658dd','active','none');
SELECT 'WA_WR_AFTER_VALID_CURRENT_FREE_SELECTION_SURVIVES_DUPLICATE_ATTEMPT';
COMMIT;
