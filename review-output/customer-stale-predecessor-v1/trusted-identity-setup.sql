-- Trusted Identity seed only. All Customer physical/deferred guards stay enabled.
BEGIN;
ALTER TABLE app.users DISABLE TRIGGER owner_commit;
ALTER TABLE app.user_security_profiles DISABLE TRIGGER owner_commit;
INSERT INTO app.users(id,is_public,revision,privacy_generation,created_at,updated_at,mutation_transaction_id) VALUES('00e9603c-2f57-5978-8df5-fbff48cddc0d',false,0,0,clock_timestamp(),clock_timestamp(),pg_current_xact_id()::text);
INSERT INTO app.user_security_profiles(id,user_id,revision,security_generation,created_at,updated_at,mutation_transaction_id) VALUES('e2592d48-0df7-5f55-8202-f6c2f829648f','00e9603c-2f57-5978-8df5-fbff48cddc0d',0,0,clock_timestamp(),clock_timestamp(),pg_current_xact_id()::text);
SET CONSTRAINTS ALL IMMEDIATE;
ALTER TABLE app.user_security_profiles ENABLE TRIGGER owner_commit;
ALTER TABLE app.users ENABLE TRIGGER owner_commit;
SET CONSTRAINTS ALL DEFERRED;
COMMIT;
