-- Privileged synthetic fixture preparation only; never owner-runtime proof.
BEGIN;
ALTER TABLE app.users DISABLE TRIGGER USER;
ALTER TABLE app.user_security_profiles DISABLE TRIGGER USER;
INSERT INTO app.users ("id","is_public","revision","privacy_generation","created_at","updated_at","mutation_transaction_id") VALUES ('10000000-0000-4000-8000-000000000001',false,0,0,clock_timestamp(),clock_timestamp(),pg_current_xact_id()::text);
INSERT INTO app.user_security_profiles ("id","user_id","revision","security_generation","created_at","updated_at","mutation_transaction_id") VALUES ('90000000-0000-4000-8000-000000000001','10000000-0000-4000-8000-000000000001',0,0,clock_timestamp(),clock_timestamp(),pg_current_xact_id()::text);
INSERT INTO app.users ("id","is_public","revision","privacy_generation","created_at","updated_at","mutation_transaction_id") VALUES ('10000000-0000-4000-8000-000000000002',false,0,0,clock_timestamp(),clock_timestamp(),pg_current_xact_id()::text);
INSERT INTO app.user_security_profiles ("id","user_id","revision","security_generation","created_at","updated_at","mutation_transaction_id") VALUES ('90000000-0000-4000-8000-000000000002','10000000-0000-4000-8000-000000000002',0,0,clock_timestamp(),clock_timestamp(),pg_current_xact_id()::text);
ALTER TABLE app.user_security_profiles ENABLE TRIGGER USER;
ALTER TABLE app.users ENABLE TRIGGER USER;
COMMIT;
