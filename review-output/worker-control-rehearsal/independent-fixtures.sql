-- TRUSTED INDEPENDENT SYNTHETIC FACTS ONLY; never owner runtime/effect proof.
BEGIN;
ALTER TABLE app.users DISABLE TRIGGER owner_commit;
ALTER TABLE app.user_security_profiles DISABLE TRIGGER owner_commit;
ALTER TABLE app.track_plans DISABLE TRIGGER owner_commit;
ALTER TABLE app.track_entitlement_definitions DISABLE TRIGGER owner_commit;
ALTER TABLE app.track_plan_entitlements DISABLE TRIGGER owner_commit;
INSERT INTO app.users ("id","is_public","revision","privacy_generation","created_at","updated_at") VALUES ('e5ec0e3e-cbca-5cb1-9279-e45e4b59e148',false,0,0,clock_timestamp(),clock_timestamp());
INSERT INTO app.user_security_profiles ("id","user_id","revision","security_generation","created_at","updated_at") VALUES ('f1c7793c-65f6-596e-ab5a-58c7c8fd49f6','e5ec0e3e-cbca-5cb1-9279-e45e4b59e148',0,0,clock_timestamp(),clock_timestamp());
INSERT INTO app.track_plans ("id","track","key","name","status","billing_model","version","content_hash","updated_at") VALUES ('77d1bfb9-3b39-550c-b0cf-07863a173897','customer','worker-control-synthetic-free','Synthetic SQL test only','active','free','worker-control-synthetic.v1','a49b9655d7a26d743969acf3013d48cfe86a97f7cc4696333706f5d26daa5944',clock_timestamp());
INSERT INTO app.track_entitlement_definitions ("id","key","label","value_type","track","is_active","updated_at") VALUES ('80f13e9f-c853-5e29-8f8d-ed29c651f0f8','worker-control-synthetic-boolean','Synthetic SQL test only','boolean','customer',true,clock_timestamp());
INSERT INTO app.track_plan_entitlements ("id","plan_id","entitlement_id","value_type","boolean_value","updated_at") VALUES ('c717b670-f4d8-57d1-a159-710fb8f1abba','77d1bfb9-3b39-550c-b0cf-07863a173897','80f13e9f-c853-5e29-8f8d-ed29c651f0f8','boolean',true,clock_timestamp());
ALTER TABLE app.track_plan_entitlements ENABLE TRIGGER owner_commit;
ALTER TABLE app.track_entitlement_definitions ENABLE TRIGGER owner_commit;
ALTER TABLE app.track_plans ENABLE TRIGGER owner_commit;
ALTER TABLE app.user_security_profiles ENABLE TRIGGER owner_commit;
ALTER TABLE app.users ENABLE TRIGGER owner_commit;
COMMIT;
