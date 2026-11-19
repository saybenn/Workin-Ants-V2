BEGIN;
ALTER TABLE app.track_plan_entitlements ENABLE TRIGGER owner_commit;
ALTER TABLE app.track_entitlement_definitions ENABLE TRIGGER owner_commit;
ALTER TABLE app.track_plans ENABLE TRIGGER owner_commit;
ALTER TABLE app.user_security_profiles ENABLE TRIGGER owner_commit;
ALTER TABLE app.users ENABLE TRIGGER owner_commit;
COMMIT;
