-- TRUSTED synthetic Identity prerequisites only; no Identity owner mutation proof.
BEGIN;
ALTER TABLE app.users DISABLE TRIGGER owner_commit;
ALTER TABLE app.user_security_profiles DISABLE TRIGGER owner_commit;
INSERT INTO app.users ("id","is_public","revision","privacy_generation","created_at","updated_at") VALUES ('21a01cd9-60db-5cac-b924-f682f19f20ba',false,0,0,clock_timestamp(),clock_timestamp());
INSERT INTO app.user_security_profiles ("id","user_id","revision","security_generation","created_at","updated_at") VALUES ('094cb783-ddd8-5346-b26a-165213e1a5eb','21a01cd9-60db-5cac-b924-f682f19f20ba',0,0,clock_timestamp(),clock_timestamp());
INSERT INTO app.users ("id","is_public","revision","privacy_generation","created_at","updated_at") VALUES ('28c6ee04-0d6e-5cc3-939e-ba10818c288c',false,0,0,clock_timestamp(),clock_timestamp());
INSERT INTO app.user_security_profiles ("id","user_id","revision","security_generation","created_at","updated_at") VALUES ('c461b26e-5eac-5191-80f0-b58ffa8eb67c','28c6ee04-0d6e-5cc3-939e-ba10818c288c',0,0,clock_timestamp(),clock_timestamp());
INSERT INTO app.users ("id","is_public","revision","privacy_generation","created_at","updated_at") VALUES ('62b5bcb6-911a-56b6-998a-d8210140e9ab',false,0,0,clock_timestamp(),clock_timestamp());
INSERT INTO app.user_security_profiles ("id","user_id","revision","security_generation","created_at","updated_at") VALUES ('397ed0ca-a8c1-5e4d-b9be-58715d93cff1','62b5bcb6-911a-56b6-998a-d8210140e9ab',0,0,clock_timestamp(),clock_timestamp());
INSERT INTO app.users ("id","is_public","revision","privacy_generation","created_at","updated_at") VALUES ('63ffc216-5055-5b5d-818d-e125e3aff027',false,0,0,clock_timestamp(),clock_timestamp());
INSERT INTO app.user_security_profiles ("id","user_id","revision","security_generation","created_at","updated_at") VALUES ('c937941a-02a4-5ca6-a372-73654989cde3','63ffc216-5055-5b5d-818d-e125e3aff027',0,0,clock_timestamp(),clock_timestamp());
INSERT INTO app.users ("id","is_public","revision","privacy_generation","created_at","updated_at") VALUES ('c15db2cb-2508-55b4-bff6-040aa84486bc',false,0,0,clock_timestamp(),clock_timestamp());
INSERT INTO app.user_security_profiles ("id","user_id","revision","security_generation","created_at","updated_at") VALUES ('b2fb3114-e524-5983-98d4-8676a0a4ad4d','c15db2cb-2508-55b4-bff6-040aa84486bc',0,0,clock_timestamp(),clock_timestamp());
INSERT INTO app.users ("id","is_public","revision","privacy_generation","created_at","updated_at") VALUES ('f52b38af-0d56-5526-b1dc-2ce636d8dcb7',false,0,0,clock_timestamp(),clock_timestamp());
INSERT INTO app.user_security_profiles ("id","user_id","revision","security_generation","created_at","updated_at") VALUES ('b99299bb-937b-5318-9c8b-bad7f0d23742','f52b38af-0d56-5526-b1dc-2ce636d8dcb7',0,0,clock_timestamp(),clock_timestamp());
ALTER TABLE app.user_security_profiles ENABLE TRIGGER owner_commit;
ALTER TABLE app.users ENABLE TRIGGER owner_commit;
COMMIT;
