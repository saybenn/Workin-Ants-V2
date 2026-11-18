-- Independent synthetic Identity prerequisites, not owner mutation proof.
BEGIN;
ALTER TABLE app.users DISABLE TRIGGER owner_commit;
ALTER TABLE app.user_security_profiles DISABLE TRIGGER owner_commit;
INSERT INTO app.users ("id","is_public","revision","privacy_generation","created_at","updated_at") VALUES ('078052af-7e37-53e9-a1ae-462cceb06d30',false,0,0,clock_timestamp(),clock_timestamp());
INSERT INTO app.user_security_profiles ("id","user_id","revision","security_generation","created_at","updated_at") VALUES ('0ad89161-cd46-5bc5-b5d8-769ddb12c8a6','078052af-7e37-53e9-a1ae-462cceb06d30',0,0,clock_timestamp(),clock_timestamp());
ALTER TABLE app.user_security_profiles ENABLE TRIGGER owner_commit;
ALTER TABLE app.users ENABLE TRIGGER owner_commit;
COMMIT;
